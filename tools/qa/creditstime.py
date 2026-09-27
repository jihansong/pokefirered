#!/usr/bin/env python3
"""Time the ending credits against MUS_CREDITS, in this ROM and a reference.

    tools/qa/creditstime.py [--rom pokemonthyl.gba] [--ref qa-base/v0.8.0/pokemonthyl.gba]
                            [--base saves/hoenn.sav] [--tolerance 30] [--wav DIR]

The real post-champion flow, as measured in
docs/music/research/06-kanto-credits-timeline.md: the save is put on INDIGO
PLATEAU (11,6) with VAR_MAP_SCENE_INDIGO_PLATEAU_EXTERIOR 1 and the quest
log empty, and at the main menu gDisableMapMusicChangeOnMapLoad is set to 2
and FLAG_DONT_SHOW_MAP_NAME_POPUP on (what SetWarpsToRollCredits does). CONTINUE then loads the map through CB2_LoadMap, so ON_TRANSITION's
playbgm MUS_CREDITS really plays, and ON_FRAME walks the rival out and rolls
the credits.

Every frame it reads gMPlayInfo_BGM (song header and track bits) and the
credits script command (sCreditsMgr+6), and records the sound. Frames are
counted from F0, the first frame MUS_CREDITS plays. It prints, for each ROM:
the credits screen, the copyright page, THE END (the frame its command
starts, i.e. the fade), the song's end (its last track stops) and where the
sound falls under -50 dBFS (tools/qa/audiocap.py's measure).

Exit status 1 unless MUS_CREDITS played in both and THE END starts within
--tolerance frames of the reference's.
"""

import argparse
import os
import struct
import sys
import tempfile
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audiocap import FPS, loud_span              # noqa: E402
from emu import Emu                              # noqa: E402
from gamedata import REPO                        # noqa: E402
import savedit                                   # noqa: E402

CMD_WAITBUTTON = 5      # CREDITSSCRCMD_WAITBUTTON (src/credits.c)
RATE = 32768
EDITS = ['warp', 'IndigoPlateau_Exterior', '11', '6', 'var', 'VAR_MAP_SCENE_INDIGO_PLATEAU_EXTERIOR', '1',
         'noquestlog']


def measure(rom, sav, wav=None, limit=20000):
    with Emu(rom, sav) as e:
        menu = e.sym('CB2_MainMenu')
        credits_cb = e.sym('CB2_Credits')
        song = e.sym('mus_credits')
        bgm = e.sym('gMPlayInfo_BGM')
        script = e.sym('sCreditsScript')
        wait_idx = 0
        while e.u8(script + wait_idx * 4) != CMD_WAITBUTTON:
            wait_idx += 1
        # sCreditsMgr+6 holds N+1 while command N is on screen
        the_end, copyright = wait_idx, wait_idx - 1

        for _ in range(400):
            if (e.callback2() & ~1) == menu:
                break
            e.press('A', hold=2, after=18)
        else:
            raise RuntimeError('%s: never reached the main menu' % rom)
        e.run(60)
        e.write(e.sym('gDisableMapMusicChangeOnMapLoad'), b'\x02')
        # FLAG_DONT_SHOW_MAP_NAME_POPUP, the first special (RAM) flag
        flags = e.sym('sSpecialFlags')
        e.write(flags, bytes([e.u8(flags) | 1]))

        e.audio_start(RATE)
        pcm = []
        t = {}
        f = 0
        while f < limit:
            if (e.callback2() & ~1) == menu and f % 20 == 0:
                e.hold('A')
            elif f % 20 == 2:
                e.hold()
            pcm.append(e.run_audio(1))
            f += 1
            header, status = struct.unpack('<II', e.read(bgm, 8))
            playing = header == song and status & 0xFFFF
            if playing and 'song' not in t:
                t['song'] = f
            if 'song' in t and 'song_end' not in t and not playing:
                t['song_end'] = f
            cb = e.callback2() & ~1
            if cb == credits_cb:
                t.setdefault('credits', f)
                mgr = e.ptr('sCreditsMgr')
                idx = e.u16(mgr + 6) if mgr else 0
                if idx == copyright + 1:
                    t.setdefault('copyright', f)
                if idx == the_end + 1:
                    t.setdefault('the_end', f)
                if idx == wait_idx + 1 and 'song_end' in t:
                    break
        pcm = b''.join(pcm)
    if 'song' not in t:
        return None
    f0 = t['song']
    per_frame = len(pcm) / f
    after = pcm[int(f0 * per_frame) // 4 * 4:]
    span = loud_span(after, RATE, 2)
    rel = {k: v - f0 for k, v in t.items()}
    rel['sound_end'] = round(span[1] * FPS) if span else None
    if wav:
        w = wave.open(wav, 'wb')
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(after)
        w.close()
    return rel


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--rom', default=os.path.join(REPO, 'pokemonthyl.gba'))
    ap.add_argument('--ref', default=os.path.join(REPO, 'qa-base', 'v0.8.0', 'pokemonthyl.gba'))
    ap.add_argument('--base', default=os.path.join(REPO, 'saves', 'hoenn.sav'))
    ap.add_argument('--tolerance', type=int, default=30)
    ap.add_argument('--wav', help='directory for the recordings (from F0)')
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        sav = os.path.join(tmp, 'credits.sav')
        with open(os.devnull, 'w') as quiet:
            old, sys.stdout = sys.stdout, quiet
            try:
                rc = savedit.run([a.base, '-o', sav] + EDITS)
            finally:
                sys.stdout = old
        if rc:
            print('savedit failed')
            return 1
        res = {}
        for name, rom in (('this', a.rom), ('ref', a.ref)):
            wav = os.path.join(a.wav, 'credits_%s.wav' % name) if a.wav else None
            res[name] = measure(rom, sav, wav)

    keys = ['credits', 'copyright', 'the_end', 'song_end', 'sound_end']
    print('frames from F0 (MUS_CREDITS starts)   ' + ''.join('%11s' % k for k in keys))
    ok = True
    for name, rom in (('this', a.rom), ('ref', a.ref)):
        r = res[name]
        if r is None:
            print('%-38s MUS_CREDITS never played' % os.path.relpath(rom, REPO))
            ok = False
            continue
        print('%-38s' % os.path.relpath(rom, REPO) + ''.join('%11s' % r.get(k) for k in keys))
    if ok:
        mine, ref = res['this'], res['ref']
        diff = mine['the_end'] - ref['the_end']
        print('THE END: %+d frames against the reference (tolerance %d); %+d from the song\'s end (reference %+d)' % (
            diff, a.tolerance, mine['the_end'] - mine['song_end'], ref['the_end'] - ref['song_end']))
        ok = abs(diff) <= a.tolerance
    print('OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
