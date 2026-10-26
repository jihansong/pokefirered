#!/usr/bin/env python3
"""Normal joypad/read-only-SYM controller for a public synthetic space fixture.

The preboot fixture is disclosed separately. No runtime script, RAM write,
warp, save-state or callable-game-function interface exists in this controller.
"""
import argparse
from collections import deque
import hashlib
import json
import os
from pathlib import Path
import re
import select
import struct
import subprocess
import traceback

KEYS = {'A': 1, 'B': 2, 'START': 8, 'E': 16, 'W': 32, 'N': 64, 'S': 128}
DELTA = {'E': (1, 0), 'W': (-1, 0), 'N': (0, -1), 'S': (0, 1)}
REVERSE = {'E': 'W', 'W': 'E', 'N': 'S', 'S': 'N'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Guest:
    def __init__(self, args, seed, directory, name):
        self.directory = directory
        directory.mkdir(mode=0o700)
        self.trace = (directory/'protocol.jsonl').open('x', encoding='utf8')
        self.errors = (directory/'stderr.log').open('x', encoding='utf8')
        self.encoder = None
        self.encoder_errors = None
        self.video_path = directory/'ship-walkthrough.mp4'
        self.schema = json.loads(args.schema.read_text())
        self.values = self.schema['values']
        self.sym = {}
        for line in args.symbols.read_text().splitlines():
            match = re.fullmatch(r'([0-9a-fA-F]{8})\s+\S+\s+([0-9a-fA-F]{8})\s+(\S+)', line.strip())
            if match:
                address, size, symbol = match.groups()
                self.sym[symbol] = int(address, 16)
        for required in ('gMain', 'gSaveBlock1Ptr', 'gPlayerAvatar', 'gObjectEvents',
                         'sLockFieldControls', 'sStartMenuCallback', 'StartCB_HandleInput'):
            assert required in self.sym, ('Missing fresh symbol', required)
        self.proc = None
        try:
            video_args, passed = [], ()
            if args.video and name == 'normal-save.sav':
                assert not self.video_path.exists()
                self.encoder_errors = (directory/'ffmpeg.log').open('x', encoding='utf8')
                self.encoder = subprocess.Popen(['ffmpeg', '-nostdin', '-n', '-hide_banner', '-loglevel', 'warning',
                    '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', '240x160', '-framerate', '60',
                    '-i', 'pipe:0', '-an', '-vf', 'scale=960:640:flags=neighbor', '-c:v', 'libx264',
                    '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(self.video_path)],
                    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=self.encoder_errors)
                fd = self.encoder.stdin.fileno()
                video_args, passed = ['--video-fd', str(fd)], (fd,)
            self.proc = subprocess.Popen([str(args.host), '--rom', str(args.rom), '--seed', str(seed),
                                          '--artifact-dir', str(directory), '--output', name, *video_args],
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         stderr=self.errors, text=True, bufsize=1, pass_fds=passed)
            self.initial = self.receive()
            self.last_status = self.initial
        except Exception:
            self.stop_failed_process()
            self.trace.close()
            self.errors.close()
            raise

    def stop_failed_process(self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=10)
        for pipe in ((self.proc.stdin, self.proc.stdout) if self.proc is not None else ()):
            if pipe and not pipe.closed:
                pipe.close()
        if self.encoder is not None:
            if self.encoder.stdin and not self.encoder.stdin.closed:
                self.encoder.stdin.close()
            try:
                self.encoder.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.encoder.kill()
                self.encoder.wait(timeout=10)
            self.encoder = None
        if self.encoder_errors and not self.encoder_errors.closed:
            self.encoder_errors.close()

    def finish_video(self):
        assert self.encoder is not None
        state = self.command('video finish')
        assert not state['video_error'] and state['video_frames'] > 0, state
        self.encoder.stdin.close()
        code = self.encoder.wait(timeout=30)
        assert code == 0, ('Video encoder failed', code)
        self.encoder = None
        self.encoder_errors.close()
        metadata = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                              '-show_format', '-of', 'json', str(self.video_path)], text=True))
        stream = metadata['streams'][0]
        assert stream['codec_name'] == 'h264' and stream['width'] == 960 and stream['height'] == 640
        assert stream['avg_frame_rate'] == '60/1' and int(stream['nb_frames']) == state['video_frames']
        return {'file': self.video_path.name, 'frames': state['video_frames'], 'fps': 60,
                'duration_seconds': float(metadata['format']['duration']), 'sha256': digest(self.video_path),
                'capture': 'Every rendered core frame during the continuous normal-key tour; silent; 4x nearest-neighbor display scale'}

    def receive(self):
        ready, _, _ = select.select([self.proc.stdout], [], [], 45)
        if not ready:
            raise TimeoutError('Guest protocol response timeout')
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError('Guest exited; inspect stderr.log')
        response = json.loads(line)
        self.trace.write(json.dumps({'response': response})+'\n')
        self.trace.flush()
        return response

    def command(self, text):
        self.trace.write(json.dumps({'command': text})+'\n')
        self.proc.stdin.write(text+'\n')
        self.proc.stdin.flush()
        return self.receive()

    def read(self, address, length):
        result = bytearray()
        for offset in range(0, length, 4096):
            part = self.command('read %x %x' % (address+offset, min(4096, length-offset)))
            result.extend(bytes.fromhex(part['hex']))
        assert len(result) == length
        return bytes(result)

    def number(self, symbol, length=4):
        return int.from_bytes(self.read(self.sym[symbol], length), 'little')

    def step(self, keys=0, frames=24):
        result = self.command('step %d %d' % (keys, frames))
        assert result['complete'] and result['actual'] == frames, result
        assert result['keys'] == 0
        self.last_status = result
        return result

    def tap(self, key, settle=20):
        self.step(KEYS[key], 4)
        self.step(0, settle)

    def snapshot(self):
        v = self.values
        pointer = self.number('gSaveBlock1Ptr')
        cb = int.from_bytes(self.read(self.sym['gMain']+v['offset.Main.callback2'], 4), 'little')
        result = {'callback2': cb, 'map': None, 'xy': None}
        if not 0x02000000 <= pointer < 0x02040000:
            return result
        warp = self.read(pointer+v['offset.SaveBlock1.location'], v['sizes.WarpData'])
        group = warp[v['offset.WarpData.mapGroup']]
        number = warp[v['offset.WarpData.mapNum']]
        avatar = self.read(self.sym['gPlayerAvatar'], v['sizes.PlayerAvatar'])
        index = avatar[v['offset.PlayerAvatar.objectEventId']]
        result['map'] = [group, number]
        if index < 16:
            offset = self.sym['gObjectEvents']+index*v['sizes.ObjectEvent']+v['offset.ObjectEvent.currentCoords']
            xy = struct.unpack('<hh', self.read(offset, 4))
            result['xy'] = [xy[0]-v['constant.MAP_OFFSET'], xy[1]-v['constant.MAP_OFFSET']]
        result['save_counter'] = self.number('gSaveCounter')
        result['script_locked'] = self.number('sLockFieldControls', 1)
        return result

    def field(self, snap):
        return (snap['callback2'] & ~1) == (self.sym['CB2_Overworld'] & ~1) and snap['xy'] is not None and snap['xy'][0] >= 0

    def boot(self):
        for i in range(700):
            snap = self.snapshot()
            if self.field(snap):
                self.step(0, 90)
                snap = self.snapshot()
                if self.field(snap) and snap['map'][0] == 69 and not snap['script_locked']:
                    return snap
            self.tap('START' if i % 3 == 0 else 'A', settle=28)
        raise AssertionError('No normal Continue field within boot bound')

    def picture(self, name):
        self.command('ppm '+name+'.ppm')

    def close(self):
        try:
            code = self.proc.poll()
            if code is None:
                self.command('quit')
                self.proc.stdin.close()
                code = self.proc.wait(timeout=10)
            assert code == 0, ('Guest must exit normally', code)
        finally:
            self.stop_failed_process()
            self.trace.close()
            self.errors.close()


class Tour:
    def __init__(self, guest, source):
        self.g = guest
        self.source = source
        self.maps = {}
        constants = (source/'include/constants/map_groups.h').read_text()
        self.ids = {name: [int(group), int(number)] for name, number, group in
                    re.findall(r'#define\s+(MAP_\w+)\s+\((\d+)\s*\|\s*\((\d+)\s*<<\s*8\)\)', constants)}
        layout_list = json.loads((source/'data/layouts/layouts.json').read_text())['layouts']
        self.layouts = {x['id']: x for x in layout_list if 'id' in x}
        for directory in sorted((source/'data/maps').glob('HoennSpacecraft*')):
            self.add_map(directory)
        self.add_map(source/'data/maps/HoennOrbitalObservatory')
        assert len(self.maps) == 17
        self.crossings = []
        self.visited = set()
        self.chapters = []

    def add_map(self, directory):
        definition = json.loads((directory/'map.json').read_text())
        layout = self.layouts[definition['layout']]
        path = self.source/layout['blockdata_filepath']
        data = path.read_bytes()
        w, h = layout['width'], layout['height']
        assert len(data) == w*h*2
        grid = struct.unpack('<'+'H'*(w*h), data)
        floor = {(i % w, i // w) for i, cell in enumerate(grid) if cell & 0x0c00 == 0}
        # Treat all source NPC positions as obstacles, even if a story flag hides
        # one. This conservative tour does not claim to test those interactions.
        floor -= {(x['x'], x['y']) for x in definition['object_events']}
        self.maps[directory.name] = dict(definition=definition, w=w, h=h, floor=floor)

    def name(self, snap=None):
        snap = snap or self.g.snapshot()
        for name, row in self.maps.items():
            if self.ids[row['definition']['id']] == snap['map']:
                return name
        raise AssertionError(('Not a ship room', snap))

    def path(self, name, start, goal):
        floor = self.maps[name]['floor'] | {start}
        assert goal in floor, (name, goal, 'target not walkable')
        q = deque([start]); previous = {start: None}
        while q:
            p = q.popleft()
            if p == goal:
                result = []
                while previous[p] is not None:
                    before, direction = previous[p]
                    result.append(direction); p = before
                return list(reversed(result))
            for direction, (dx, dy) in DELTA.items():
                dest = p[0]+dx, p[1]+dy
                if dest in floor and dest not in previous:
                    previous[dest] = (p, direction); q.append(dest)
        raise AssertionError(('No floor route', name, start, goal))

    def move(self, direction):
        before = self.g.snapshot()
        for _ in range(45):
            self.g.step(KEYS[direction], 1)
            after = self.g.snapshot()
            if after['map'] != before['map'] or after['xy'] != before['xy']:
                self.g.step(0, 24)
                return self.g.snapshot()
        raise AssertionError(('Movement blocked', direction, before))

    def walk(self, name, goal, allowed_destination=None):
        for _ in range(400):
            before = self.g.snapshot()
            here = self.name(before)
            if here != name:
                assert here == allowed_destination, (name, here, goal)
                return here
            if tuple(before['xy']) == goal:
                return here
            steps = self.path(name, tuple(before['xy']), goal)
            assert steps
            self.move(steps[0])
        raise AssertionError(('Walking bound exceeded', name, goal))

    def crossing(self, name, index):
        warp = self.maps[name]['definition']['warp_events'][index]
        destination = next(n for n, r in self.maps.items() if r['definition']['id'] == warp['dest_map'])
        room = self.maps[name]
        x, y = warp['x'], warp['y']
        direction = min(((x, 'W'), (room['w']-1-x, 'E'), (y, 'N'), (room['h']-1-y, 'S')))[1]
        reached = self.walk(name, (x, y), destination)
        if reached == name:
            self.move(direction)
        for _ in range(15):
            self.g.step(0, 24)
            snap = self.g.snapshot()
            if self.g.field(snap) and not snap['script_locked'] and self.name(snap) == destination:
                break
        else:
            raise AssertionError(('Door transition failed', name, index, self.g.snapshot()))
        self.crossings.append({'from': name, 'warp': index, 'to': destination,
                               'destination_warp': int(warp['dest_warp_id']), 'snapshot': snap})
        landing = self.maps[destination]['definition']['warp_events'][int(warp['dest_warp_id'])]
        target_room = self.maps[destination]
        lx, ly = landing['x'], landing['y']
        outward = min(((lx, 'W'), (target_room['w']-1-lx, 'E'),
                       (ly, 'N'), (target_room['h']-1-ly, 'S')))[1]
        dx, dy = DELTA[REVERSE[outward]]
        assert tuple(snap['xy']) in {(lx, ly), (lx+dx, ly+dy)}, ('Wrong destination door landing', snap, landing)
        return destination, int(warp['dest_warp_id'])

    def dfs(self, name):
        self.visited.add(name)
        self.chapters.append({'room': name, 'video_frame': self.g.last_status.get('video_frames', 0)})
        self.g.picture('room-'+name)
        self.g.step(0, 90)
        # Turn and settle through four ordinary directions at a safe standing tile.
        # This tour records rendered rooms; exhaustive per-pixel models are separate.
        for index, warp in enumerate(self.maps[name]['definition']['warp_events']):
            target = next((n for n, r in self.maps.items() if r['definition']['id'] == warp['dest_map']), None)
            if target is None or target in self.visited:
                continue
            reached, back = self.crossing(name, index)
            self.dfs(reached)
            old, _ = self.crossing(reached, back)
            assert old == name

    def run(self):
        origin = self.name()
        self.dfs(origin)
        assert len(self.visited) == 17 and len(self.crossings) == 32
        expected = {(name, i) for name, row in self.maps.items()
                    for i, warp in enumerate(row['definition']['warp_events'])
                    if any(r['definition']['id'] == warp['dest_map'] for r in self.maps.values())}
        actual = {(x['from'], x['warp']) for x in self.crossings}
        assert actual == expected and len(actual) == len(self.crossings), ('Directed door coverage mismatch', actual ^ expected)
        return {'visited_rooms': sorted(self.visited), 'directional_crossings': self.crossings,
                'video_chapters': self.chapters,
                'scope': 'One continuous synthetic-fixture tour with normal keys; no NPC battles or facility use claimed'}


def normal_save(g):
    before = g.snapshot()
    assert g.field(before)
    assert not before['script_locked']
    g.tap('START', settle=40)
    assert g.snapshot()['script_locked']
    assert g.number('sStartMenuCallback') & ~1 == g.sym['StartCB_HandleInput'] & ~1
    count = g.number('sNumStartMenuItems', 1)
    order = list(g.read(g.sym['sStartMenuOrder'], count))
    assert 4 in order and 0 < count <= 9, order
    for _ in range(count):
        cursor = g.number('sStartMenuCursorPos', 1)
        if order[cursor] == 4:
            break
        g.tap('S')
    else:
        raise AssertionError('SAVE menu selection failed')
    g.tap('A', settle=24)
    callbacks = []
    inverse = {value & ~1: name for name, value in g.sym.items() if name.startswith('SaveDialogCB_')}
    success_seen = False
    for i in range(400):
        callback = g.number('sSaveDialogCB') & ~1
        name = inverse.get(callback, hex(callback))
        if not callbacks or callbacks[-1] != name:
            callbacks.append(name)
        assert 'Error' not in name, callbacks
        success_seen |= name == 'SaveDialogCB_ReturnSuccess'
        after = g.snapshot()
        if success_seen and after['save_counter'] == before['save_counter']+1 and not after.get('script_locked', 1):
            break
        g.step(KEYS['A'] if i % 4 == 0 else 0, 8)
    else:
        raise AssertionError(('Normal SAVE completion not observed', callbacks, g.snapshot()))
    g.step(0, 60)
    g.picture('normal-save-complete')
    answer = g.command('battery normal-save-complete')
    assert answer['battery'] and answer['bytes'] == 131072
    return {'before': before, 'after': g.snapshot(), 'callbacks': callbacks,
            'normal_ui_success_seen': success_seen, 'export': answer}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('host', 'source', 'schema', 'rom', 'symbols', 'seed', 'artifact-dir'):
        parser.add_argument('--'+key, type=Path, required=True)
    parser.add_argument('--scenario', choices=['boot-save', 'tour-save'], default='boot-save')
    parser.add_argument('--video', action='store_true', help='Record actual rendered frames through a dedicated ffmpeg pipe')
    a = parser.parse_args()
    for key in ('host', 'source', 'schema', 'rom', 'symbols', 'seed'):
        setattr(a, key.replace('-', '_'), getattr(a, key.replace('-', '_')).resolve(strict=True))
    assert not a.artifact_dir.exists()
    a.artifact_dir.mkdir(mode=0o700)
    a.artifact_dir = a.artifact_dir.resolve()
    seed_hash = digest(a.seed)
    result = {'status': 'STARTED_NOT_PASS', 'scenario': a.scenario,
              'rom_sha256': digest(a.rom), 'sym_sha256': digest(a.symbols),
              'schema_sha256': digest(a.schema), 'seed_sha256': seed_hash,
              'host_sha256': digest(a.host), 'runtime_memory_writes': 0,
              'scope': 'Official pinned GBA core with a public synthetic preboot fixture; not installed iOS Delta'}
    guest = None
    try:
        guest = Guest(a, a.seed, a.artifact_dir/'warm', 'normal-save.sav')
        result['boot'] = guest.boot()
        guest.picture('continued-field')
        if a.video:
            guest.command('video on')
            guest.step(0, 120)
        if a.scenario == 'tour-save':
            result['tour'] = Tour(guest, a.source).run()
        if a.video:
            guest.step(0, 120)
            result['video'] = guest.finish_video()
        result['save'] = normal_save(guest)
        disk = guest.directory/'normal-save.sav'
        result['saved_sha256'] = digest(disk)
        from make_ty28_fixture import validate_ty28
        result['saved_sector_validation'] = validate_ty28(disk.read_bytes(), guest.schema)
        assert result['saved_sector_validation']['counter'] == result['save']['after']['save_counter']
        guest.close(); guest = None
        # New OS process, no quickstate or in-memory reset.
        guest = Guest(a, disk, a.artifact_dir/'cold', 'unused-no-export.sav')
        result['cold'] = guest.boot()
        assert result['cold']['map'] == result['save']['after']['map']
        assert result['cold']['xy'] == result['save']['after']['xy']
        assert result['cold']['save_counter'] == result['save']['after']['save_counter']
        guest.picture('cold-continued-field')
        assert not guest.snapshot()['script_locked']
        guest.tap('START', settle=40)
        assert guest.number('sNumStartMenuItems', 1) > 0
        assert guest.snapshot()['script_locked']
        assert guest.number('sStartMenuCallback') & ~1 == guest.sym['StartCB_HandleInput'] & ~1
        guest.picture('cold-opened-start-menu')
        guest.tap('B')
        assert guest.field(guest.snapshot()) and not guest.snapshot()['script_locked']
        guest.picture('cold-closed-start-menu')
        result['cold_menu_controls'] = True
        guest.close(); guest = None
        assert digest(a.seed) == seed_hash and digest(disk) == result['saved_sha256']
        result['status'] = 'PASS_SYNTHETIC_NORMAL_SAVE_COLD_CORE'
    except Exception:
        result['status'] = 'FAIL_NOT_VERIFIED'
        result['error'] = traceback.format_exc()
        if guest:
            try:
                guest.picture('failure-final-frame')
                result['failure_snapshot'] = guest.snapshot()
            except Exception:
                pass
        raise
    finally:
        if guest:
            try:
                guest.close()
            except Exception:
                result['status'] = 'FAIL_NOT_VERIFIED'
                result['close_error'] = traceback.format_exc()
        (a.artifact_dir/'result.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps({'status': result['status'], 'scenario': a.scenario}))


if __name__ == '__main__':
    main()
