"""Headless GBA emulator for the QA scripts (libmgba through tools/qa/libqa.so).

    from emu import Emu
    with Emu('pokemonthyl.gba', 'saves/hoenn.sav') as e:
        e.boot_continue()           # title screen -> CONTINUE -> overworld
        e.press('A'); e.run(60)
        e.shot('/tmp/x.png')
        print(e.sym_read('gSaveBlock1Ptr', 4))

The save is copied to a temporary file first, so the game can write to it
without touching the original. Symbols come from the ROM's .sym file
(pokemonthyl.gba -> pokemonthyl.sym) when one sits next to it.
"""

import ctypes
import os
import shutil
import struct
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, 'libqa.so')

KEYS = {'A': 0, 'B': 1, 'SELECT': 2, 'START': 3, 'RIGHT': 4, 'LEFT': 5,
        'UP': 6, 'DOWN': 7, 'R': 8, 'L': 9}
W, H = 240, 160


def _lib():
    if not os.path.exists(LIB) or os.path.getmtime(LIB) < os.path.getmtime(os.path.join(HERE, 'libqa.c')):
        subprocess.check_call([os.path.join(HERE, 'build.sh')])
    lib = ctypes.CDLL(LIB)
    lib.qa_open.restype = ctypes.c_void_p
    lib.qa_open.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    for name in ('qa_close', 'qa_reset'):
        getattr(lib, name).argtypes = [ctypes.c_void_p]
    lib.qa_set_keys.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    lib.qa_run.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.qa_frame.argtypes = [ctypes.c_void_p]
    lib.qa_frame.restype = ctypes.c_uint
    lib.qa_read.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_char_p, ctypes.c_int]
    lib.qa_write.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_char_p, ctypes.c_int]
    lib.qa_screen.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.qa_state_size.argtypes = [ctypes.c_void_p]
    lib.qa_state_size.restype = ctypes.c_uint
    lib.qa_save_state.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.qa_load_state.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    return lib


_LIBQA = None


def fresh_syms(rom):
    """Path of the .sym for rom, rebuilt from the .elf when it is older than
    the ROM (`make leafgreen` does not refresh it; only `make syms` does)."""
    base = os.path.splitext(rom)[0]
    sym, elf = base + '.sym', base + '.elf'
    if os.path.exists(elf) and (not os.path.exists(sym) or os.path.getmtime(sym) < os.path.getmtime(rom)):
        dka = os.environ.get('DEVKITARM', '/opt/devkitpro/devkitARM')
        out = subprocess.check_output([os.path.join(dka, 'bin', 'arm-none-eabi-objdump'), '-t', elf], text=True)
        lines = set()
        for line in out.splitlines():
            # 08000000 g     F .text\t000000f0 AgbMain  ->  08000000 g 000000f0 AgbMain
            if line[:1] in '0' and line[1:2] in '2389':
                head, _, tail = line.partition('\t')
                p = tail.split()
                if len(p) >= 2:
                    lines.add('%s %s %s %s' % (head[:8], head[9], p[0], p[-1]))
        with open(sym, 'w') as f:
            f.write('\n'.join(sorted(lines)) + '\n')
    return sym


def load_syms(path):
    syms = {}
    if path and os.path.exists(path):
        with open(path) as f:
            for line in f:
                p = line.split()
                if len(p) >= 4:
                    syms[p[3]] = int(p[0], 16)
    return syms


class GameReset(RuntimeError):
    """The game fell back to the copyright/intro screens (a crash reset)."""


BOOT_CALLBACKS = ('CB2_InitCopyrightScreenAfterBootup', 'CB2_InitCopyrightScreenAfterTitleScreen',
                  'CB2_WaitFadeBeforeSetUpIntro', 'CB2_SetUpIntro', 'CB2_Intro', 'CB2_CopyrightScreen')


class Emu:
    def __init__(self, rom, sav=None, sym=None):
        global _LIBQA
        if _LIBQA is None:
            _LIBQA = _lib()
        self.lib = _LIBQA
        self.tmp = tempfile.mkdtemp(prefix='qa-')
        tsav = None
        if sav:
            tsav = os.path.join(self.tmp, 'game.sav')
            shutil.copyfile(sav, tsav)
        self.sav_path = tsav
        self.h = self.lib.qa_open(rom.encode(), tsav.encode() if tsav else None)
        if not self.h:
            raise RuntimeError('mGBA could not open %s' % rom)
        if sym is None:
            sym = fresh_syms(rom)
        self.syms = load_syms(sym)

    # -- lifetime
    def close(self):
        if self.h:
            self.lib.qa_close(self.h)
            self.h = None
        shutil.rmtree(self.tmp, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    # -- time and input
    def run(self, frames=1):
        self.lib.qa_run(self.h, int(frames))

    def frame(self):
        return self.lib.qa_frame(self.h)

    def hold(self, *keys):
        mask = 0
        for k in keys:
            mask |= 1 << KEYS[k.upper()]
        self.lib.qa_set_keys(self.h, mask)

    def press(self, key, hold=3, after=10):
        """Press and release a key (or 'A+B' for several), then wait."""
        self.hold(*[k for k in key.split('+') if k])
        self.run(hold)
        self.hold()
        self.run(after)

    def walk(self, direction, tiles=1):
        """Walk tiles on foot (16 frames a tile, plus turn time)."""
        self.hold(direction)
        self.run(16 * tiles + 2)
        self.hold()
        self.run(8)

    # -- memory
    def read(self, addr, n):
        buf = ctypes.create_string_buffer(n)
        self.lib.qa_read(self.h, addr, buf, n)
        return buf.raw

    def write(self, addr, data):
        self.lib.qa_write(self.h, addr, bytes(data), len(data))

    def u8(self, addr):
        return self.read(addr, 1)[0]

    def u16(self, addr):
        return struct.unpack('<H', self.read(addr, 2))[0]

    def u32(self, addr):
        return struct.unpack('<I', self.read(addr, 4))[0]

    def sym(self, name):
        return self.syms[name]

    def sym_read(self, name, n):
        return self.read(self.syms[name], n)

    def ptr(self, name):
        return self.u32(self.syms[name])

    # -- game state helpers (pokefirered symbols)
    def callback2(self):
        return self.u32(self.syms['gMain'] + 4)

    def in_overworld(self):
        return (self.callback2() & ~1) == self.syms.get('CB2_Overworld', -1)

    def in_battle(self):
        return (self.callback2() & ~1) == self.syms.get('BattleMainCB2', -1)

    def field_idle(self):
        """In the overworld with no script running and the player free to
        move (script.c: sGlobalScriptContextStatus CONTEXT_SHUTDOWN, controls
        unlocked)."""
        if not self.in_overworld():
            return False
        status = self.syms.get('sGlobalScriptContextStatus')
        lock = self.syms.get('sLockFieldControls')
        return (status is None or self.u8(status) == 2) and (lock is None or not self.u8(lock))

    def quest_log_playing(self):
        return bool(self.u8(self.syms['gQuestLogState']) or self.u8(self.syms['gQuestLogPlaybackState']))

    def location(self):
        """(mapGroup, mapNum, x, y) of the live SaveBlock1."""
        sb1 = self.ptr('gSaveBlock1Ptr')
        g, n = struct.unpack('<bb', self.read(sb1 + 4, 2))
        x, y = struct.unpack('<hh', self.read(sb1, 4))
        return g, n, x, y

    def reset_seen(self):
        """True when the game is on its power-on screens (or has no callback),
        which after CONTINUE means it crashed and reset."""
        cb = self.callback2() & ~1
        return cb == 0 or cb in {self.syms.get(n) for n in BOOT_CALLBACKS}

    def boot_continue(self, timeout=3600):
        """From power-on, mash through the intro and title and pick CONTINUE.
        Returns the frame count at which the overworld came up; raises
        GameReset if the game resets after leaving the main menu."""
        start = self.frame()
        menu = self.syms.get('CB2_MainMenu')
        seen_menu = left_menu = False
        while self.frame() - start < timeout:
            cb = self.callback2() & ~1
            if left_menu and self.reset_seen():
                raise GameReset('reset after CONTINUE (callback2=%08x)' % self.callback2())
            if cb == menu:
                seen_menu = True
            elif seen_menu:
                left_menu = True
            if self.quest_log_playing():
                # "Previously on your quest..." replays old scenes on the
                # old maps; B skips to the end and the real map loads after.
                self.press('B', hold=2, after=14)
                continue
            if self.in_overworld():
                self.run(30)
                if self.in_overworld() and not self.quest_log_playing():
                    return self.frame() - start
                continue
            self.press('A', hold=2, after=14)
        raise TimeoutError('never reached the overworld (callback2=%08x)' % self.callback2())

    # -- video
    def screen(self):
        buf = ctypes.create_string_buffer(W * H * 3)
        self.lib.qa_screen(self.h, buf)
        return buf.raw

    def shot(self, path, scale=1):
        from PIL import Image
        img = Image.frombytes('RGB', (W, H), self.screen())
        if scale != 1:
            img = img.resize((W * scale, H * scale), Image.NEAREST)
        img.save(path)
        return path

    def black_fraction(self, threshold=24):
        s = self.screen()
        dark = sum(1 for i in range(0, len(s), 3) if s[i] < threshold and s[i + 1] < threshold and s[i + 2] < threshold)
        return dark / (W * H)

    # -- states
    def save_state(self):
        buf = ctypes.create_string_buffer(self.lib.qa_state_size(self.h))
        self.lib.qa_save_state(self.h, buf)
        return buf.raw

    def load_state(self, blob):
        self.lib.qa_load_state(self.h, blob)
