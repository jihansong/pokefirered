#!/usr/bin/env python3
"""Capture actual airport door animation on a disposable copy of a base save."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import tempfile

from emu import Emu
from gamedata import REPO
import savedit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--base', type=Path, default=Path(REPO) / 'saves/hoenn.sav')
    ap.add_argument('--rom', default=str(Path(REPO) / 'pokemonthyl.gba'))
    ap.add_argument('--x', type=int, default=35)
    ap.add_argument('--y', type=int, default=13)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    original_sha = hashlib.sha256(args.base.read_bytes()).hexdigest()
    frames = []
    with tempfile.TemporaryDirectory(prefix='airport-door-qa-') as folder:
        save = str(Path(folder) / 'case.sav')
        assert savedit.run([str(args.base), '-o', save, 'warp', 'VermilionCity', str(args.x), str(args.y), 'noquestlog']) == 0
        with Emu(args.rom, save) as e:
            e.boot_continue()
            initial_map = e.location()[:2]
            e.shot(str(args.out / 'door-closed.png'))
            function = e.sym('Task_AnimateDoor') & ~1
            e.hold('UP')
            for tick in range(1, 181):
                e.run(1)
                if tick == 24:
                    e.hold()
                # struct Task: function at 0, isActive at 4, total size 40.
                tasks = e.read(e.sym('gTasks'), 16 * 40)
                active = any(tasks[i + 4] and (struct.unpack_from('<I', tasks, i)[0] & ~1) == function
                             for i in range(0, len(tasks), 40))
                if active or tick % 12 == 0:
                    name = f'door-frame-{tick:03d}.png'
                    e.shot(str(args.out / name))
                    frames.append({'frame': tick, 'door_task_active': active,
                                   'location': list(e.location()), 'image': name})
                if e.location()[:2] != initial_map and e.field_idle():
                    break
            e.hold()
            assert e.location()[:2] != initial_map, 'Door did not warp to another map'
            assert sum(row['door_task_active'] for row in frames) >= 3, 'No multi-frame door task was observed'
    assert hashlib.sha256(args.base.read_bytes()).hexdigest() == original_sha
    (args.out / 'frames.json').write_text(json.dumps({'frames': frames, 'base_save_unchanged': True,
                                                    'visual_review_required': True}, indent=2), encoding='utf8')
    print('PASS: door task ran across multiple frames and entry warped; inspect captured alignment frames')


if __name__ == '__main__':
    main()
