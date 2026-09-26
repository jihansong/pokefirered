#!/usr/bin/env python3
"""Measure and check the game's songs (sound/songs/midi/*.mid). Standard library only.

    python3 tools/music/songinfo.py mus_route1            # summary + engine check
    python3 tools/music/songinfo.py mus_route1 --json     # every number, as JSON
    python3 tools/music/songinfo.py --all > songs.json    # all mus_* songs

What it reads: the MIDI file, its line in sound/songs/midi/midi.cfg (-G -V -R -P),
and the voicegroup it names in sound/voice_groups.inc (plus the included
sound/voicegroups/*.inc), so program numbers resolve to the real instruments.

What it reports (no melodies, only numbers): tempo, time signatures, an estimated
key (Krumhansl-Schmuckler, only a guess), bars, intro/loop/total seconds from the
[ and ] loop markers, tracks, programs and the instrument each resolves to,
drum notes, and the two channel numbers the music team checks:

  max_held_ds     most DirectSound (sample) notes held down at once. The game
                  mixes at most 5 sample voices for music, sound effects and
                  cries together (src/m4a.c m4aSoundInit), so new songs keep <= 4.
  held_ds_steals  held sample notes that would be cut because 5 were already
                  sounding (released notes still ringing are taken first).

The check (exit code 1 on failure) is the music team's rule for new songs:
a midi.cfg line, 24 ticks per quarter note, -R50, at most 9 tracks with notes
(the BGM player has 10, sound/music_player_table.inc), max_held_ds <= 4,
held_ds_steals == 0, and [ ] loop markers unless --one-shot is given.
See docs/music/research/02-engine-limits.md.
"""
import collections
import json
import math
import os
import re
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
MIDI_DIR = os.path.join(ROOT, 'sound/songs/midi')
MAX_DS = 5          # src/m4a.c: m4aSoundInit, 5 << SOUND_MODE_MAXCHN_SHIFT
FRAME_HZ = 59.7275

# ---------------------------------------------------------------- voicegroups
ENTRIES = []   # every voice entry in memory order: (macro, [args])
LABELS = {}    # label -> index into ENTRIES


def _parse_voices(path):
    for raw in open(path):
        line = raw.split('@')[0].strip()
        if not line:
            continue
        m = re.match(r'(\w+)::$', line)
        if m:
            LABELS[m.group(1)] = len(ENTRIES)
            continue
        m = re.match(r'\.include\s+"([^"]+)"', line)
        if m:
            if 'voicegroups' in m.group(1):
                _parse_voices(os.path.join(ROOT, m.group(1)))
            continue
        m = re.match(r'voice_group\s+(\w+)(?:\s*,\s*(\d+))?', line)
        if m:   # asm/macros/m4a.inc: a starting note moves the label back
            LABELS['voicegroup_' + m.group(1)] = len(ENTRIES) - int(m.group(2) or 0)
            continue
        m = re.match(r'(voice_\w+)\s*(.*)', line)
        if m:
            ENTRIES.append((m.group(1), [a.strip() for a in m.group(2).split(',')]))


_parse_voices(os.path.join(ROOT, 'sound/voice_groups.inc'))

KEYSPLITS = {}


def _parse_keysplits():
    cur, n = None, 0
    for raw in open(os.path.join(ROOT, 'sound/keysplit_tables.inc')):
        s = raw.split('@')[0].strip()
        m = re.match(r'\.set\s+(\w+),\s*\.\s*-\s*(\d+)', s)
        if m:
            cur, n = m.group(1), int(m.group(2))
            KEYSPLITS[cur] = {}
            continue
        m = re.match(r'\.byte\s+(\d+)', s)
        if m and cur:
            KEYSPLITS[cur][n] = int(m.group(1))
            n += 1
    p = os.path.join(ROOT, 'sound/hoenn_keysplit_tables.inc')
    if os.path.exists(p):
        cur, last = None, 0
        for raw in open(p):
            s = raw.split('@')[0].strip()
            m = re.match(r'keysplit\s+(\w+)(?:\s*,\s*(\d+))?', s)
            if m:
                cur, last = 'keysplit_' + m.group(1), int(m.group(2) or 0)
                KEYSPLITS[cur] = {}
                continue
            m = re.match(r'split\s+(\d+)\s*,\s*(\d+)', s)
            if m and cur:
                for k in range(last, int(m.group(2))):
                    KEYSPLITS[cur][k] = int(m.group(1))
                last = int(m.group(2))


_parse_keysplits()


def vg_label(g):
    """-G132 -> voicegroup132, -G_littleroot -> voicegroup_littleroot."""
    return 'voicegroup%03d' % int(g) if g.isdigit() else 'voicegroup' + g


def voice(g, prog):
    lab = vg_label(g)
    if lab not in LABELS or LABELS[lab] + prog >= len(ENTRIES):
        return ('?', [])
    return ENTRIES[LABELS[lab] + prog]


def resolve(g, prog, note):
    """The voice that actually sounds for (program, note), and the key it plays at."""
    kind, args = voice(g, prog)
    if kind.startswith('voice_keysplit_all'):      # drum kit: the note picks the drum
        kind, args = ENTRIES[LABELS[args[0]] + note]
        return kind, args, int(args[0]) if args and args[0].isdigit() else 60
    if kind.startswith('voice_keysplit'):
        idx = KEYSPLITS.get(args[1], {}).get(note, 0)
        kind, args = ENTRIES[LABELS[args[0]] + idx]
    return kind, args, note


def family(kind, args):
    if kind.startswith('voice_keysplit_all'):
        return 'drumkit'
    if kind.startswith('voice_keysplit'):
        return 'keysplit:' + args[0]
    if kind.startswith('voice_square_1'):
        return 'square1'
    if kind.startswith('voice_square_2'):
        return 'square2'
    if kind.startswith('voice_programmable_wave'):
        return 'wave'
    if kind.startswith('voice_noise'):
        return 'noise'
    if kind.startswith('voice_directsound'):
        return 'ds:' + args[2].replace('DirectSoundWaveData_', '')
    return kind


def is_ds(kind):
    return kind.startswith('voice_directsound')


# ---------------------------------------------------------------- midi.cfg
def read_cfg():
    cfg = {}
    for line in open(os.path.join(MIDI_DIR, 'midi.cfg')):
        m = re.match(r'(\S+)\.mid:\s*(.*)', line)
        if m:
            cfg[m.group(1)] = dict(re.findall(r'-([A-Z])(\S*)', m.group(2)))
    return cfg


# ---------------------------------------------------------------- MIDI
def _vlq(d, i):
    v = 0
    while True:
        b = d[i]
        i += 1
        v = (v << 7) | (b & 0x7F)
        if not b & 0x80:
            return v, i


def parse_midi(path):
    """-> (ticks per quarter, [track events]); an event is (tick, 'meta'|'ch', type/status, bytes)."""
    d = open(path, 'rb').read()
    if d[:4] != b'MThd':
        raise ValueError('%s: not a MIDI file' % path)
    _fmt, ntrk, div = struct.unpack('>HHH', d[8:14])
    i = 8 + struct.unpack('>I', d[4:8])[0]
    tracks = []
    while i < len(d) and len(tracks) < ntrk and d[i:i + 4] == b'MTrk':
        ln = struct.unpack('>I', d[i + 4:i + 8])[0]
        j, end, t, run, ev = i + 8, i + 8 + ln, 0, None, []
        while j < end:
            dt, j = _vlq(d, j)
            t += dt
            st = d[j]
            if st == 0xFF:
                typ = d[j + 1]
                n, j = _vlq(d, j + 2)
                ev.append((t, 'meta', typ, d[j:j + n]))
                j += n
            elif st in (0xF0, 0xF7):
                n, j = _vlq(d, j + 1)
                j += n
            else:
                if st & 0x80:
                    run = st
                    j += 1
                n = 1 if run & 0xF0 in (0xC0, 0xD0) else 2
                ev.append((t, 'ch', run, bytes(d[j:j + n])))
                j += n
        tracks.append(ev)
        i = end
    return div, tracks


class Song:
    """One song: MIDI + cfg, with a tempo map and the loop markers."""

    def __init__(self, name, cfg=None, midi_path=None):
        self.name = name
        self.cfg = (cfg if cfg is not None else read_cfg()).get(name, {})
        self.path = midi_path or os.path.join(MIDI_DIR, name + '.mid')
        self.div, self.tracks = parse_midi(self.path)
        self.g = self.cfg.get('G', '0')
        self.tempos = sorted((t, 60000000 / int.from_bytes(b, 'big'))
                             for tr in self.tracks for t, k, a, b in tr if k == 'meta' and a == 0x51)
        self.markers = sorted((t, b.decode('latin1').strip()) for tr in self.tracks for t, k, a, b in tr
                              if k == 'meta' and 1 <= a <= 7 and b.decode('latin1').strip() in ('[', ']', '][', ':'))
        self.loop_start = next((t for t, x in self.markers if x == '['), None)
        self.loop_end = next((t for t, x in self.markers if x == ']'), None)
        self.end = max((ev[-1][0] for ev in self.tracks if ev), default=0)

    def seconds(self, a, b=None):
        """Seconds from tick a to tick b (or from 0 to a)."""
        if b is None:
            a, b = 0, a
        bpm = 120.0
        for tt, bb in self.tempos:
            if tt <= a:
                bpm = bb
        sec, cur = 0.0, a
        for tt, bb in self.tempos:
            if a < tt < b:
                sec += (tt - cur) / self.div * 60 / bpm
                cur, bpm = tt, bb
        return sec + (b - cur) / self.div * 60 / bpm

    def notes(self, loops=1):
        """Notes with the loop unrolled loops times:
        (start_s, end_s, track, channel, note, velocity, volume, pan, program)."""
        le = self.loop_end if self.loop_end is not None else self.end
        segs = [(0, le)]
        if self.loop_start is not None:
            segs += [(self.loop_start, le)] * (loops - 1)
        offs, acc = [], 0.0
        for a, b in segs:
            offs.append(acc)
            acc += self.seconds(a, b)
        self.unrolled_seconds = acc
        out = []
        for ti, tr in enumerate(self.tracks):
            for (a, b), off in zip(segs, offs):
                prog, vol, pan, on = {}, {}, {}, {}
                for t, k, st, dd in tr:
                    if k != 'ch':
                        continue
                    hi, ch = st & 0xF0, st & 0x0F
                    if hi == 0xC0:
                        prog[ch] = dd[0]
                    elif hi == 0xB0 and dd[0] == 7:
                        vol[ch] = dd[1]
                    elif hi == 0xB0 and dd[0] == 10:
                        pan[ch] = dd[1]
                    if t < a or t >= b:
                        continue
                    ts = off + self.seconds(a, t)
                    if hi == 0x90 and dd[1] > 0:
                        on[(ch, dd[0])] = (ts, dd[1], vol.get(ch, 127), pan.get(ch, 64), prog.get(ch, 0))
                    elif (hi == 0x80 or hi == 0x90) and (ch, dd[0]) in on:
                        s0, v, vo, pa, pr = on.pop((ch, dd[0]))
                        out.append((s0, ts, ti, ch, dd[0], v, vo, pa, pr))
                end_s = off + self.seconds(a, b)   # notes still held at the loop end stop there
                for (ch, n), (s0, v, vo, pa, pr) in on.items():
                    out.append((s0, end_s, ti, ch, n, v, vo, pa, pr))
        out.sort()
        return out


def release_tail(args):
    """Seconds a DirectSound note keeps ringing after note-off (m4a multiplies the
    envelope by release/256 each frame; stop counting below 1%)."""
    r = int(args[6]) if len(args) > 6 and args[6].isdigit() else 0
    if r < 128:
        return 0.02
    return min(1.5, math.log(0.01) / math.log(r / 256) / FRAME_HZ)


def channel_plan(song, notes, limit=True):
    """Simulate voice allocation: at most MAX_DS DirectSound notes (a new note takes a
    released-but-ringing voice first, then the oldest held one) and one note per CGB
    channel. Returns (cut: {note index: time it is cut}, max_held_ds, held_ds_steals)."""
    active, cgb_last, cut = [], {}, {}
    maxheld = steals = 0
    for i, (s0, s1, ti, ch, note, vel, vol, pan, prog) in enumerate(notes):
        kind, args, _key = resolve(song.g, prog, note)
        if is_ds(kind):
            active = [x for x in active if x[0] > s0]
            if limit and len(active) >= MAX_DS:
                victim = min(active, key=lambda x: (x[2] > s0, x[1]))
                active.remove(victim)
                cut[victim[3]] = s0
                if victim[2] > s0:
                    steals += 1
            active.append((s1 + release_tail(args), s0, s1, i))
            maxheld = max(maxheld, sum(1 for x in active if x[2] > s0))
        elif kind != '?':
            cg = family(kind, args)
            if cg in cgb_last and notes[cgb_last[cg]][1] > s0:
                cut[cgb_last[cg]] = s0
            cgb_last[cg] = i
    return cut, maxheld, steals


MAJ = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MIN = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def _corr(a, b):
    ma, mb = sum(a) / 12, sum(b) / 12
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return num / den if den else 0


def estimate_key(hist):
    best = (-2, None)
    for r in range(12):
        for mode, prof in (('major', MAJ), ('minor', MIN)):
            rot = prof[-r:] + prof[:-r] if r else prof
            c = _corr(hist, rot)
            if c > best[0]:
                best = (c, '%s %s' % (NAMES[r], mode))
    return best


def measure(name, cfg=None, midi_path=None):
    s = Song(name, cfg, midi_path)
    bar = s.div * 4
    tsigs = sorted({'%d/%d' % (b[0], 2 ** b[1]) for tr in s.tracks for t, k, a, b in tr if k == 'meta' and a == 0x58})
    first_ts = next((b for tr in s.tracks for t, k, a, b in sorted(tr, key=lambda e: e[0]) if k == 'meta' and a == 0x58), None)
    if first_ts:
        bar = s.div * 4 * first_ts[0] // (2 ** first_ts[1])
    notes = s.notes(1)
    hist = [0.0] * 12
    per_track = collections.OrderedDict()
    drums = collections.Counter()
    for s0, s1, ti, ch, note, vel, vol, pan, prog in notes:
        kind, args = voice(s.g, prog)
        fam = family(kind, args)
        t = per_track.setdefault(ti, dict(track=ti, notes=0, programs={}, lo=None, hi=None, drum=False))
        t['notes'] += 1
        t['programs'][prog] = fam
        if fam == 'drumkit':
            t['drum'] = True
            dk, da, _ = resolve(s.g, prog, note)
            drums[(note, family(dk, da))] += 1
        else:
            t['lo'] = note if t['lo'] is None else min(t['lo'], note)
            t['hi'] = note if t['hi'] is None else max(t['hi'], note)
            hist[note % 12] += s1 - s0
    _cut, maxheld, steals = channel_plan(s, notes)
    conf, key = estimate_key(hist) if sum(hist) else (None, None)
    ls, le = s.loop_start, s.loop_end
    return dict(
        name=name, cfg=s.cfg, voicegroup=s.g, ticks_per_quarter=s.div,
        tracks_with_notes=len(per_track),
        tempo_first=round(s.tempos[0][1], 1) if s.tempos else None,
        tempo_min=round(min(b for _, b in s.tempos), 1) if s.tempos else None,
        tempo_max=round(max(b for _, b in s.tempos), 1) if s.tempos else None,
        tempo_changes=len(s.tempos), time_signatures=tsigs,
        key_estimate=key, key_confidence=round(conf, 2) if conf is not None else None,
        bars_total=round(s.end / bar, 2),
        seconds_total=round(s.seconds(s.end), 1),
        frames_total=round(s.seconds(s.end) * FRAME_HZ),
        loop_start_bar=round(ls / bar, 2) if ls is not None else None,
        loop_end_bar=round(le / bar, 2) if le is not None else None,
        intro_seconds=round(s.seconds(ls), 1) if ls is not None else None,
        loop_seconds=round(s.seconds(ls, le), 1) if ls is not None and le is not None else None,
        max_held_ds=maxheld, held_ds_steals=steals,
        tracks=list(per_track.values()),
        drums={'%d:%s' % k: v for k, v in sorted(drums.items())},
    )


def check(info, one_shot=False):
    """The music team's rules for a new song. Returns a list of problems."""
    p = []
    if not info['cfg']:
        p.append('no line in sound/songs/midi/midi.cfg')
    elif info['cfg'].get('R') != '50':
        p.append('midi.cfg should use -R50 (every song does)')
    if info['ticks_per_quarter'] != 24:
        p.append('MIDI resolution %d, the songs use 24 ticks per quarter note' % info['ticks_per_quarter'])
    if info['tracks_with_notes'] > 9:
        p.append('%d tracks with notes; keep <= 9 (BGM player has 10)' % info['tracks_with_notes'])
    if info['max_held_ds'] > 4:
        p.append('max_held_ds %d; keep <= 4 sample notes at once' % info['max_held_ds'])
    if info['held_ds_steals']:
        p.append('%d held sample notes cut by the 5-voice limit' % info['held_ds_steals'])
    if not one_shot and info['loop_start_bar'] is None:
        p.append('no [ ] loop markers (pass --one-shot for fanfares and jingles)')
    if any('?' in f for t in info['tracks'] for f in t['programs'].values()):
        p.append('a program resolves to no voice in voicegroup %s' % info['voicegroup'])
    return p


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    cfg = read_cfg()
    if '--all' in argv:
        names = sorted(f[:-4] for f in os.listdir(MIDI_DIR) if f.startswith('mus_') and f.endswith('.mid'))
        json.dump([measure(n, cfg) for n in names], sys.stdout, indent=1)
        return 0
    if not args:
        print(__doc__)
        return 2
    bad = 0
    for name in args:
        name = os.path.splitext(os.path.basename(name))[0]
        info = measure(name, cfg)
        if '--json' in argv:
            print(json.dumps(info, indent=1))
        else:
            print('%s  VG %s  %s BPM  %s  key~%s (%s)  %d tracks  %.1f s total (%d frames)' % (
                name, info['voicegroup'], info['tempo_first'], ','.join(info['time_signatures']) or '-',
                info['key_estimate'], info['key_confidence'], info['tracks_with_notes'],
                info['seconds_total'], info['frames_total']))
            if info['loop_start_bar'] is not None:
                print('  intro %.1f s, loop %.1f s (bars %s-%s)' % (info['intro_seconds'], info['loop_seconds'] or 0,
                                                                    info['loop_start_bar'], info['loop_end_bar']))
            else:
                print('  one-shot (no loop markers)')
            print('  max_held_ds %d, held_ds_steals %d' % (info['max_held_ds'], info['held_ds_steals']))
        problems = check(info, '--one-shot' in argv)
        for pr in problems:
            print('  CHECK: ' + pr)
        if not problems:
            print('  check: ok')
        bad |= bool(problems)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
