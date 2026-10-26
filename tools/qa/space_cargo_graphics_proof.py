"""Prove a fixed Cargo graphic delta by restoring public inputs in memory only."""
import hashlib
from pathlib import Path, PurePosixPath
import subprocess


PREFIX = 'data/tilesets/secondary/ty_space_v4_cargohold/'
SYMBOLS = {
    PREFIX+'tiles.4bpp': ('sgTileset_TYSpaceDeckV4CargoHoldTiles', 16384),
    PREFIX+'metatiles.bin': ('sgTileset_TYSpaceDeckV4CargoHoldMetatiles', 8192),
    PREFIX+'palettes.gbapal': ('sgTileset_TYSpaceDeckV4CargoHoldPalettes', 416),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify_cargo_graphics(source, rom, elf, contract, baseline_source=None):
    assert contract['schema'] == 'TY_CARGO_GRAPHICS_ONLY_PROOF_V1'
    assert len(rom) == contract['rom_bytes'] == 33554432
    assert sha(rom) == contract['expected_candidate_rom_sha256']
    rows = contract['ranges']
    assert len(rows) == 3 and {r['source'] for r in rows} == set(SYMBOLS)
    base = contract['baseline_commit']
    assert len(base) == 40 and all(c in '0123456789abcdef' for c in base)
    restored = bytearray(rom)
    intervals = []
    evidence = []
    for row in rows:
        relative = row['source']
        pure = PurePosixPath(relative)
        assert not pure.is_absolute() and '..' not in pure.parts
        symbol, length = SYMBOLS[relative]
        assert row['symbol'] == symbol and row['bytes'] == length
        actual = elf.one(symbol)
        assert actual['value'] == row['address'] and actual['size'] == length
        offset = actual['value']-0x08000000
        assert 0 <= offset < offset+length <= len(rom)
        intervals.append((offset, offset+length))
        new = (source/relative).read_bytes()
        assert len(new) == length and sha(new) == row['candidate_sha256']
        assert rom[offset:offset+length] == elf.at(row['address'], length) == new
        if baseline_source is not None:
            old = (Path(baseline_source)/relative).read_bytes()
        else:
            old = subprocess.check_output(['git', '-c', 'safe.directory='+str(source),
                                           'show', base+':'+relative], cwd=source)
        assert len(old) == length and sha(old) == row['previous_sha256']
        assert hashlib.sha1(b'blob '+str(length).encode()+b'\0'+old).hexdigest() == row['previous_git_blob']
        restored[offset:offset+length] = old
        evidence.append({'source': relative, 'symbol': symbol, 'address': row['address'],
                         'bytes': length, 'new_sha256': sha(new), 'old_sha256': sha(old),
                         'differing_bytes': sum(a != b for a, b in zip(new, old))})
    intervals.sort()
    assert all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:]))
    assert sha(restored) == contract['baseline_rom_sha256'], 'Change exists outside approved Cargo graphics'
    return {'status': 'PASS_ONLY_THREE_FIXED_CARGO_GRAPHIC_RANGES_CHANGED',
            'baseline_rom_sha256': contract['baseline_rom_sha256'],
            'candidate_rom_sha256': sha(rom), 'restored_memory_sha256': sha(restored),
            'ranges': evidence, 'code_and_pointer_bytes_outside_ranges_identical': True,
            'symbol_addresses_and_sizes_unchanged': True,
            'ROM_file_writes': 0, 'source_writes': 0, 'restoration_is_memory_only': True}
