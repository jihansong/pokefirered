#!/usr/bin/env python3
"""Apply/check only the canonical original Hoenn bike attribute words.

Unlike map patches, these records target tileset attributes. No layout, map,
graphics, border or unrelated attribute is written. Already applied inputs
are left byte-for-byte and mtime unchanged.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct


def sha(data):
    return hashlib.sha256(data).hexdigest()


def apply(source_root, check_only=False):
    source_root = source_root.resolve()
    canonical = source_root / 'tools/hoenn_import/bike_terrain_patches.json'
    patch = json.loads(canonical.read_text(encoding='utf-8'))
    assert patch['schema'] == 'hoenn-bike-terrain-v1'
    prepared = []
    for record in patch['files']:
        relative = Path(record['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        assert relative.as_posix().startswith('data/tilesets/')
        assert relative.name == 'metatile_attributes.bin'
        path = source_root / relative
        original = path.read_bytes()
        assert len(original) == record['bytes'] and len(original) % 4 == 0
        # Accept only the frozen source or the exact canonical result. This
        # catches an unrelated attribute edit instead of overwriting it.
        assert sha(original) in (record['before_sha256'], record['after_sha256']), str(relative)
        result = bytearray(original)
        indices = set()
        for word in record['words']:
            index = word['index']
            assert index not in indices and 0 <= index < len(result) // 4
            indices.add(index)
            before, after = word['before'], word['after']
            assert (before ^ after) & ~0xff == 0
            assert 0xea <= (after & 0xff) <= 0xef
            current = struct.unpack_from('<I', result, index * 4)[0]
            assert current in (before, after), (str(relative), index)
            struct.pack_into('<I', result, index * 4, after)
        assert sha(result) == record['after_sha256']
        prepared.append((path, original, bytes(result), len(indices)))
    # Validate every input before the first write.
    changed = 0
    for path, original, result, count in prepared:
        if original != result:
            if check_only:
                raise AssertionError('Bike terrain patch not yet applied: ' + str(path))
            path.write_bytes(result)
            changed += 1
        print(('checked ' if check_only else 'patched ') + str(path.relative_to(source_root))
              + ' (' + str(count) + ' canonical words)')
    print('files changed: ' + str(changed))
    return changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    apply(args.source_root, args.check)
