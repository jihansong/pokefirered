#!/usr/bin/env python3
"""Preview a song as a WAV without building the ROM: an approximate m4a renderer.

    python3 tools/music/render.py mus_route1 /tmp/route1.wav           # loop played twice
    python3 tools/music/render.py mus_route1 /tmp/route1.wav --loops 3
    python3 tools/music/render.py path/to/new.mid /tmp/new.wav --cfg "-E -R50 -G133 -V090"
    python3 tools/music/render.py mus_route1 /tmp/r.wav --no-limit     # hear it without the 5-voice cut

Needs numpy (installed by .devcontainer/setup.sh); tools/music/songinfo.py does the
parsing with the standard library.

Uses the game's own instruments: the song's voicegroup from midi.cfg, keysplit
tables, and the real samples in sound/direct_sound_samples/*.wav (their smpl loop
points, root key 60 and native rate), the programmable wave samples, and square /
noise PSG voices. Applies VOL, PAN, velocity, -V, the [ ] loop, a per-frame
attack/decay/sustain/release, and the engine's 5 DirectSound voices with stealing
plus one note per CGB channel (tools/music/songinfo.py channel_plan).

Not modelled: reverb (-R50), MOD/LFO vibrato, pitch bend, square sweep, exact CGB
envelopes, the m4a resampler, and sound effects or cries competing for voices. It
runs a little brighter than the game. For the final check record the ROM itself
with tools/qa/audiocap.py (docs/music/research/05-preview-tools.md).
"""
import argparse
import os
import re
import struct
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import songinfo as S  # noqa: E402

SR = 13379 * 2           # twice the game's mixing rate
FRAME = SR / S.FRAME_HZ

_samples = {}


def ds_sample(ptr):
    name = ptr.replace('DirectSoundWaveData_', '')
    if name not in _samples:
        d = open(os.path.join(S.ROOT, 'sound/direct_sound_samples', name + '.wav'), 'rb').read()
        i, rate, loop, data = 12, 13379, None, b''
        while i + 8 <= len(d):
            cid, ln = d[i:i + 4], struct.unpack('<I', d[i + 4:i + 8])[0]
            if cid == b'fmt ':
                rate = struct.unpack('<I', d[i + 12:i + 16])[0]
            elif cid == b'smpl' and struct.unpack('<I', d[i + 36:i + 40])[0]:
                loop = struct.unpack('<6I', d[i + 44:i + 68])[2]
            elif cid == b'data':
                data = d[i + 8:i + 8 + ln]
            i += 8 + ln + (ln & 1)
        arr = (np.frombuffer(data, dtype=np.uint8).astype(np.float32) - 128) / 128
        _samples[name] = (arr, rate, loop)
    return _samples[name]


_waves = {}


def prog_wave(ptr):
    if ptr not in _waves:
        n = int(re.search(r'_(\d+)$', ptr).group(1))
        b = open(os.path.join(S.ROOT, 'sound/programmable_wave_samples/%02d.pcm' % n), 'rb').read()[:16]
        _waves[ptr] = (np.array([v for x in b for v in (x >> 4, x & 15)], dtype=np.float32) - 7.5) / 7.5
    return _waves[ptr]


def ds_envelope(n_on, n_total, a, d, s, r):
    """m4a DirectSound envelope, stepped once a frame (values 0..255)."""
    frames = int(n_total / FRAME) + 2
    on_f = n_on / FRAME
    e, out, phase = 0.0, [], 'a'
    for f in range(frames):
        if f >= on_f:
            phase = 'r'
        if phase == 'a':
            e += a
            if e >= 255:
                e, phase = 255, 'd'
        elif phase == 'd':
            e = e * d / 256
            if e <= s:
                e, phase = s, 's'
        elif phase == 'r':
            e = e * r / 256
        out.append(e / 255)
    return np.interp(np.arange(n_total) / FRAME, np.arange(frames), out).astype(np.float32)


def render(song, loops=2, limit=True):
    notes = song.notes(loops)
    cut, maxheld, steals = S.channel_plan(song, notes, limit)
    mvl = int(song.cfg.get('V', '127')) / 127
    out = np.zeros((int((song.unrolled_seconds + 2) * SR) + 1, 2), dtype=np.float32)
    for i, (s0, s1, ti, ch, note, vel, vol, pan, prog) in enumerate(notes):
        kind, args, key = S.resolve(song.g, prog, note)
        if kind == '?':
            continue
        amp = (vel / 127) * (vol / 127) * mvl
        p = (pan - 64) / 64
        gl, gr = min(1, 1 - p), min(1, 1 + p)
        n0, non = int(s0 * SR), max(1, int((s1 - s0) * SR))
        stop = cut.get(i)
        if S.is_ds(kind):
            arr, rate, loop = ds_sample(args[2])
            a_, d_, s_, r_ = (int(x) for x in args[3:7])
            fixed = 'no_resample' in kind
            step = (rate if fixed else rate * 2 ** ((key - 60) / 12)) / SR
            ntot = non + int(S.release_tail(args) * SR)
            if stop is not None:
                ntot = max(1, min(ntot, int((stop - s0) * SR)))
            pos = np.arange(ntot) * step
            if loop is not None and len(arr) > loop:
                pos = np.where(pos >= len(arr), loop + np.mod(pos - loop, len(arr) - loop), pos)
                sig = arr[np.minimum(pos.astype(int), len(arr) - 1)]
            else:
                sig = np.where(pos < len(arr) - 1, arr[np.minimum(pos.astype(int), len(arr) - 1)], 0)
            y = sig * ds_envelope(non, ntot, a_, d_, s_, r_) * amp * 0.5
        else:
            f = 440 * 2 ** ((note - 69) / 12)
            ntot = non + int(0.03 * SR)
            if stop is not None:
                ntot = max(1, min(ntot, int((stop - s0) * SR)))
            t = np.arange(ntot) / SR
            if 'square' in kind:
                duty = [0.125, 0.25, 0.5, 0.75][int(args[4] if 'square_1' in kind else args[2]) & 3]
                sig = np.where(np.mod(t * f, 1) < duty, 1.0, -1.0)
            elif 'wave' in kind:
                sig = prog_wave(args[2])[(np.mod(t * f, 1) * 32).astype(int)]
            else:
                sig = np.random.default_rng(note).choice([-1.0, 1.0], ntot)
            env = np.full(ntot, max(int(args[-2]) / 15, 0.3), dtype=np.float32)
            if ntot > non:
                env[non:] *= np.linspace(1, 0, ntot - non)
            y = sig * env * amp * 0.25
        e = min(len(out), n0 + len(y))
        out[n0:e, 0] += y[:e - n0] * gl
        out[n0:e, 1] += y[:e - n0] * gr
    peak = float(np.abs(out).max()) or 1.0
    return out / peak * 0.9, dict(notes=len(notes), seconds=round(song.unrolled_seconds, 1),
                                  max_held_ds=maxheld, held_ds_steals=steals)


def write_wav(path, audio, rate=SR):
    w = wave.open(path, 'wb')
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(rate)
    w.writeframes((np.clip(audio, -1, 1) * 32767).astype('<i2').tobytes())
    w.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('song', help='mus_name (from sound/songs/midi) or a path to a .mid')
    ap.add_argument('out', help='output .wav')
    ap.add_argument('--loops', type=int, default=2, help='times through the loop (default 2)')
    ap.add_argument('--cfg', help='midi.cfg options for a .mid that has no cfg line yet, e.g. "-E -R50 -G133 -V090"')
    ap.add_argument('--no-limit', action='store_true', help='do not apply the 5 sample voice limit')
    a = ap.parse_args()
    name = os.path.splitext(os.path.basename(a.song))[0]
    path = a.song if a.song.endswith('.mid') else None
    cfg = S.read_cfg()
    if a.cfg:
        cfg[name] = dict(re.findall(r'-([A-Z])(\S*)', a.cfg))
    song = S.Song(name, cfg, path)
    audio, stats = render(song, a.loops, not a.no_limit)
    write_wav(a.out, audio)
    print(a.out, stats)


if __name__ == '__main__':
    main()
