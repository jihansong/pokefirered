#!/usr/bin/env python3
"""Map smoke test: put the player on every map, continue the save, walk a
little and look for trouble.

Each map gets its own copy of a base save warped to the map (at its first
warp, else an object or sign, else the middle), CONTINUE is pressed, and the
player walks a few steps. Further spawns follow until every object of the map
has been on screen once (an object with a bad movement type resets the game
the moment it appears); --quick keeps only the first. The map's result is the
worst of its spawns:

    OK       overworld on the right map, screen not black
    BATTLE   a wild or trainer battle started (usually harmless; listed)
    MOVED    the game put the player on another map (a map script did)
    BLACK    over 97% of the screen stayed black
    RESET    the game fell back to the intro/title (a crash reset)
    TIMEOUT  the overworld never came up
    ERROR    the harness itself failed on this map

    tools/qa/mapsmoke.py                        # all maps, base saves/hoenn.sav
    tools/qa/mapsmoke.py Route110 MAP_MAUVILLE_CITY --shots /tmp/ms
    tools/qa/mapsmoke.py --grep HOENN -j 4
"""

import argparse
import json
import multiprocessing
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emu import Emu, GameReset                     # noqa: E402
from gamedata import REPO, maps, map_info          # noqa: E402
from savefile import SaveFile                      # noqa: E402

_LAYOUTS = None


def layout_size(name):
    global _LAYOUTS
    if _LAYOUTS is None:
        with open(os.path.join(REPO, 'data', 'layouts', 'layouts.json')) as f:
            _LAYOUTS = {l['id']: (l.get('width', 0), l.get('height', 0))
                        for l in json.load(f)['layouts'] if 'id' in l}
    return _LAYOUTS.get(name, (0, 0))


def spawn_point(m):
    j = m['json']
    for key in ('warp_events', 'object_events', 'bg_events', 'coord_events'):
        for ev in j.get(key) or []:
            if 'x' in ev and 'y' in ev:
                return ev['x'], ev['y']
    w, h = layout_size(m['layout'])
    return w // 2, h // 2


def cover_points(m):
    """Spawn points so that every object of the map comes on screen at least
    once (the screen shows about 15x10 tiles around the player): the usual
    spawn first, then one point per still-unseen object, greedily."""
    pts = [spawn_point(m)]
    seen = lambda o, p: abs(o[0] - p[0]) <= 7 and abs(o[1] - p[1]) <= 4
    objs = [(o['x'], o['y']) for o in m['json'].get('object_events') or [] if 'x' in o]
    for o in objs:
        if not any(seen(o, p) for p in pts):
            pts.append(o)
    return pts


PRIORITY = ['ERROR', 'RESET', 'TIMEOUT', 'BLACK', 'MOVED', 'BATTLE', 'OK']


def smoke(job):
    mapid, rom, base, frames, shots, quick = job
    m = map_info(mapid)
    worst = (mapid, 'OK', '')
    for i, (x, y) in enumerate(cover_points(m)[:1] if quick else cover_points(m)):
        r = smoke_at(mapid, m, x, y, rom, base, frames, shots, i)
        if PRIORITY.index(r[1]) < PRIORITY.index(worst[1]):
            worst = (mapid, r[1], ('at (%d,%d) ' % (x, y) if i else '') + r[2])
    return worst


def smoke_at(mapid, m, x, y, rom, base, frames, shots, idx):
    tmp = tempfile.mkdtemp(prefix='ms-')
    sav = os.path.join(tmp, 'm.sav')
    try:
        s = SaveFile(base)
        s.warp(mapid, x, y)
        s.set_var('VAR_REPEL_STEP_COUNT', 250)   # no wild battles while walking about
        s.save(sav)
        with Emu(rom, sav) as e:
            try:
                e.boot_continue(timeout=2400)
            except GameReset:
                return mapid, 'RESET', 'while entering the map'
            except TimeoutError:
                return mapid, 'TIMEOUT', ''
            # Where CONTINUE put us, before any walking can take a door out.
            e.run(frames)
            result, note = 'OK', ''
            g, n, _, _ = e.location()
            if e.in_battle():
                result = 'BATTLE'
            elif (g, n) != (m['group'], m['num']):
                result, note = 'MOVED', 'now on %d.%d' % (g, n)
            elif e.black_fraction() > 0.97:
                result = 'BLACK'
            if shots and (result != 'OK' or shots_all):
                e.shot(os.path.join(shots, '%s_%d_%s.png' % (m['dir'], idx, result)))
            if result != 'OK':
                return mapid, result, note
            # Then walk about so the camera brings more objects on screen (an
            # object with a bad movement type resets the game when it appears).
            for step in ['DOWN', 'UP', 'LEFT', 'RIGHT'] * 2:
                e.walk(step, 2)
                if e.reset_seen():
                    result, note = 'RESET', 'while walking'
                    break
                if e.in_battle():
                    result = 'BATTLE'
                    break
            else:
                e.run(30)
                if e.reset_seen():
                    result, note = 'RESET', 'while walking'
            if shots and (result != 'OK' or shots_all):
                e.shot(os.path.join(shots, '%s_%d_%s.png' % (m['dir'], idx, result)))
            return mapid, result, note
    except Exception as ex:          # keep going; one bad map must not stop the sweep
        return mapid, 'ERROR', repr(ex)
    finally:
        for f in os.listdir(tmp):
            os.remove(os.path.join(tmp, f))
        os.rmdir(tmp)


shots_all = False


def main():
    global shots_all
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('maps', nargs='*', help='maps to test (default: all)')
    ap.add_argument('--rom', default=os.path.join(REPO, 'pokemonthyl.gba'))
    ap.add_argument('--base', default=os.path.join(REPO, 'saves', 'hoenn.sav'))
    ap.add_argument('--grep', help='only maps whose MAP_ id contains this')
    ap.add_argument('--frames', type=int, default=120, help='frames to wait after CONTINUE before judging the map')
    ap.add_argument('-j', type=int, default=os.cpu_count(), help='parallel emulators')
    ap.add_argument('--shots', help='directory for screenshots of non-OK maps')
    ap.add_argument('--shots-all', action='store_true', help='screenshot every map')
    ap.add_argument('--quick', action='store_true', help='one spawn per map instead of covering every object')
    a = ap.parse_args()
    shots_all = a.shots_all
    ids = [map_info(n)['id'] for n in a.maps] if a.maps else sorted(maps())
    if a.grep:
        ids = [i for i in ids if a.grep.upper() in i]
    if a.shots:
        os.makedirs(a.shots, exist_ok=True)
    jobs = [(i, a.rom, a.base, a.frames, a.shots, a.quick) for i in ids]
    counts = {}
    bad = []
    with multiprocessing.Pool(a.j) as pool:
        for n, (mapid, result, note) in enumerate(pool.imap_unordered(smoke, jobs), 1):
            counts[result] = counts.get(result, 0) + 1
            if result != 'OK':
                bad.append((mapid, result, note))
                print('%-8s %s %s' % (result, mapid, note), flush=True)
            if n % 50 == 0:
                print('... %d/%d' % (n, len(jobs)), file=sys.stderr, flush=True)
    print('%d maps: %s' % (len(jobs), ', '.join('%s %d' % kv for kv in sorted(counts.items()))))
    return 1 if any(r in ('RESET', 'TIMEOUT', 'ERROR', 'BLACK') for _, r, _ in bad) else 0


if __name__ == '__main__':
    sys.exit(main())
