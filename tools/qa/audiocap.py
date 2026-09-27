#!/usr/bin/env python3
"""Record what the ROM plays to a WAV file (headless mGBA, tools/qa/emu.py).

    # power on with no save and record the first 1500 frames (logo, intro)
    python3 tools/qa/audiocap.py pokemonthyl.gba /tmp/intro.wav --frames 1500

    # a save: CONTINUE into the overworld, then press A at 30 frames and record 40 s
    python3 tools/qa/audiocap.py pokemonthyl.gba /tmp/scene.wav --sav saves/x.sav \\
        --continue --press A@30 --seconds 40

    # skip 1465 frames unrecorded (reach the title screen), then record 60 s
    python3 tools/qa/audiocap.py preview.gba /tmp/title.wav --skip 1465 --seconds 60

    # one song from its first tick, whether or not the game plays it anywhere yet
    python3 tools/qa/audiocap.py pokemonthyl.gba /tmp/help.wav --sav saves/hoenn.sav \\
        --song MUS_HELP --seconds 16.5 --small

--song MUS_X records a song of the built ROM that nothing plays yet (a port or
a new cue before it is wired in): it runs a copy of the ROM whose song table
points every music id (256 and up) at that song, picks CONTINUE on --sav, and
cuts the recording at the frame the BGM player starts the song (clock 0), so
the WAV opens on its first tick. The song data is the ROM's own, byte for byte.

--press KEY@FRAME (repeatable) presses a key (A B SELECT START RIGHT LEFT UP DOWN
R L, or A+B) for --hold frames at FRAME counted from the start of the recording.
Frames are the GBA's 59.73 a second. Output is 16-bit stereo at --rate Hz
(32768 by default); --small writes 22050 Hz mono instead, a quarter of the size,
for sending previews.

Afterwards it prints the length and where the sound starts and ends (the first
and last 50 ms window louder than -50 dBFS), which is how the music team
measures a cue against a scene's length. --continue needs the ROM's .sym file
beside it (make syms, or copy pokemonthyl.sym with the ROM).

Use a copy of the ROM when someone else is using the one in the tree; the ROM
is only read, and the save is copied to a temporary file (emu.py).
"""
import argparse
import array
import math
import os
import re
import shutil
import sys
import tempfile
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu import Emu, KEYS, fresh_syms, load_syms  # noqa: E402

FPS = 59.7275


def parse_press(spec):
    key, _, frame = spec.partition('@')
    keys = [k.upper() for k in key.split('+') if k]
    for k in keys:
        if k not in KEYS:
            raise argparse.ArgumentTypeError('unknown key %r' % k)
    return int(frame or 0), keys


def loud_span(pcm, rate, channels, win=0.05, db=-50.0):
    """(first, last) seconds of the windows louder than db, or None if silent."""
    a = array.array('h', pcm)
    if sys.byteorder != 'little':
        a.byteswap()
    step = max(1, int(win * rate)) * channels
    thresh = 32768 * 10 ** (db / 20)
    loud = []
    for i in range(0, len(a) - step + 1, step):
        seg = a[i:i + step:4] or a[i:i + step]
        rms = math.sqrt(sum(x * x for x in seg) / len(seg))
        if rms > thresh:
            loud.append(i // channels / rate)
    return (loud[0], loud[-1] + win) if loud else None


def to_small(pcm, rate):
    """16-bit stereo at rate -> 16-bit mono at 22050 Hz (linear interpolation)."""
    a = array.array('h', pcm)
    if sys.byteorder != 'little':
        a.byteswap()
    mono = [(a[i] + a[i + 1]) / 2 for i in range(0, len(a) - 1, 2)]
    out = array.array('h')
    ratio = rate / 22050
    n = int(len(mono) / ratio)
    for j in range(n):
        x = j * ratio
        i = int(x)
        f = x - i
        v = mono[i] if i + 1 >= len(mono) else mono[i] * (1 - f) + mono[i + 1] * f
        out.append(int(v))
    if sys.byteorder != 'little':
        out.byteswap()
    return out.tobytes()


def song_rom(rom, const, out):
    """Copy rom to out with every music entry (ids 256..) of gSongTable
    pointing at const's entry. Returns (sym path, song header address)."""
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
    songs = dict((n, int(v)) for n, v in re.findall(
        r'#define (MUS_\w+)\s+(\d+)', open(os.path.join(root, 'include/constants/songs.h')).read()))
    if const not in songs:
        sys.exit('unknown song %s' % const)
    sym = fresh_syms(rom)
    table = load_syms(sym)['gSongTable'] - 0x08000000
    d = bytearray(open(rom, 'rb').read())
    entry = bytes(d[table + 8 * songs[const]:table + 8 * songs[const] + 8])
    for i in range(256, max(songs.values()) + 1):
        d[table + 8 * i:table + 8 * i + 8] = entry
    open(out, 'wb').write(d)
    return sym, int.from_bytes(entry[:4], 'little')


def record_song(rom, sav, const, frames, rate):
    """PCM of const from its first tick, frames long (see --song)."""
    tmp = tempfile.mkdtemp(prefix='songcap-')
    try:
        prom = os.path.join(tmp, 'song.gba')
        sym, header = song_rom(rom, const, prom)
        with Emu(prom, sav, sym=sym) as e:
            bgm = e.syms['gMPlayInfo_BGM']
            e.boot_continue(leave_menu_only=True)
            e.audio_start(rate)
            chunks, start, prev, pressing = [], None, None, 0
            for _ in range(frames + 20000):
                # every frame is recorded, the ones spent pressing B too
                if pressing == 0 and e.quest_log_playing():
                    chunks, start, prev = [], None, None
                    e.hold('B')
                    pressing = 16
                chunks.append(e.run_audio(1))
                if pressing:
                    pressing -= 1
                    if pressing == 14:
                        e.hold()
                h, clock = e.u32(bgm), e.u32(bgm + 12)    # songHeader, clock
                if h == header and (prev is None or clock < prev):
                    start = len(chunks) - 1                  # (re)started this frame
                prev = clock if h == header else None
                if start is not None and len(chunks) - start >= frames:
                    break
            if start is None or e.u32(bgm) != header:
                sys.exit('%s did not play through the recording' % const)
            return b''.join(chunks[start:start + frames])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument('rom')
    ap.add_argument('out', help='output .wav')
    ap.add_argument('--sav', help='128K flash save to start from (copied, never written)')
    ap.add_argument('--continue', dest='cont', action='store_true',
                    help='mash through the title and pick CONTINUE before recording (needs --sav)')
    ap.add_argument('--skip', type=int, default=0, help='frames to run, unrecorded, before recording')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--frames', type=int, help='frames to record')
    g.add_argument('--seconds', type=float, help='seconds to record')
    ap.add_argument('--press', type=parse_press, action='append', default=[], metavar='KEY@FRAME')
    ap.add_argument('--hold', type=int, default=3, help='frames a --press key is held (default 3)')
    ap.add_argument('--rate', type=int, default=32768)
    ap.add_argument('--small', action='store_true', help='write 22050 Hz mono')
    ap.add_argument('--song', metavar='MUS_X',
                    help='record this song from its first tick (needs --sav; see below)')
    a = ap.parse_args()
    frames = a.frames if a.frames is not None else int(round((a.seconds or 30) * FPS))
    if a.song and not a.sav:
        ap.error('--song needs --sav')

    if a.song:
        pcm = record_song(a.rom, a.sav, a.song, frames, a.rate)
    else:
        pcm = record(a, frames)
    write_wav(a, pcm, frames)


def record(a, frames):
    with Emu(a.rom, a.sav) as e:
        if a.cont:
            e.boot_continue()
        if a.skip:
            e.run(a.skip)
        e.audio_start(a.rate)
        events = []
        for f, keys in a.press:
            events += [(f, keys), (f + a.hold, [])]
        events.sort(key=lambda x: x[0])
        pcm, t = [], 0
        for f, keys in events + [(frames, None)]:
            f = min(f, frames)
            if f > t:
                pcm.append(e.run_audio(f - t))
                t = f
            if keys is None:
                break
            e.hold(*keys)
        return b''.join(pcm)


def write_wav(a, pcm, frames):
    span = loud_span(pcm, a.rate, 2)
    rate, channels = a.rate, 2
    if a.small:
        pcm, rate, channels = to_small(pcm, a.rate), 22050, 1
    w = wave.open(a.out, 'wb')
    w.setnchannels(channels)
    w.setsampwidth(2)
    w.setframerate(rate)
    w.writeframes(pcm)
    w.close()
    secs = len(pcm) / (2 * channels) / rate
    print('%s: %.2f s (%d frames)' % (a.out, secs, frames))
    if span:
        print('sound from %.2f s (frame %d) to %.2f s (frame %d)' % (
            span[0], round(span[0] * FPS), span[1], round(span[1] * FPS)))
    else:
        print('silent')


if __name__ == '__main__':
    main()
