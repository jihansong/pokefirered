"""Portable, read-only preflight for root's private Codespaces execution.

Run from the repository with explicit latest filename and expected SHA:
python3 remote_v14_preflight.py saves/pokemonthyl_v1.4.sav EXPECTED_SHA
Needs scan_current_save.py beside this script; imports only independent parsing.
No output file and no candidate: prints a bounded JSON evidence report to stdout.
"""
import base64
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from scan_current_save import decode, parse_banks, public, records, sha

source = Path(sys.argv[1]).resolve()
expected = sys.argv[2]
repo = Path.cwd().resolve()
assert source.is_relative_to(repo / 'saves')
raw = source.read_bytes()
assert sha(raw) == expected
banks = parse_banks(raw)
assert all(bank['valid'] for bank in banks), 'both save generations must be complete and checksummed'
assert all(bank['counter'] % 2 == bank['bank'] for bank in banks)
assert max(bank['counter'] for bank in banks) < 0xfffffff0, 'counter wrap requires explicit comparator'
latest = max(banks, key=lambda bank: bank['counter'])
target_ids = {row['_identity'] for bank in banks for row in records(bank) if not row['checksum_ok'] or row['header_BadEgg']}
inventory, donor_matches = [], []
protected = {}
for path in sorted((repo / 'saves').rglob('*.sav')):
    data = path.read_bytes()
    digest = sha(data)
    protected[path] = digest
    entry = dict(path=str(path.relative_to(repo)), sha256=digest, bytes=len(data))
    try:
        parsed = parse_banks(data)
        entry['banks'] = [dict(bank=b['bank'], valid=b['valid'], counter=b.get('counter'), errors=b['sector_errors']) for b in parsed]
        for bank in parsed:
            for row in records(bank):
                if row['_identity'] in target_ids:
                    candidate = dict(path=entry['path'], sav_sha256=digest, bank=bank['bank'], counter=bank['counter'], **public(row))
                    if row['checksum_ok'] and not row['header_BadEgg']:
                        candidate['healthy_exact_record_base64'] = base64.b64encode(row['_raw']).decode()
                    donor_matches.append(candidate)
    except AssertionError as error:
        entry['parse_error'] = str(error)
    inventory.append(entry)

party_rows = []
for row in records(latest):
    if row['location'] not in ('party', 'PC'):
        continue
    clean = public(row)
    if row['checksum_ok']:
        data = row['_raw']
        pid, ot = struct.unpack_from('<II', data)
        plain = b''.join(struct.pack('<I', word ^ pid ^ ot) for word in struct.unpack('<12I', data[32:80]))
        from scan_current_save import ORDER
        chunks = {letter: plain[i * 12:(i + 1) * 12] for i, letter in enumerate(ORDER[pid % 24])}
        ivword = struct.unpack_from('<I', chunks['M'], 4)[0]
        clean['IVs_HP_ATK_DEF_SPD_SPATK_SPDEF'] = [(ivword >> (5 * n)) & 31 for n in range(6)]
        clean['EVs_HP_ATK_DEF_SPD_SPATK_SPDEF'] = list(chunks['E'][:6])
        clean['current_PP'] = list(chunks['A'][8:12])
        clean['PP_Up_stages'] = [(chunks['G'][8] >> (2 * n)) & 3 for n in range(4)]
    if row['location'] == 'party' or row['species_untrusted_if_bad'] in (3, 6, 9, 148, 149) or not row['checksum_ok']:
        party_rows.append(clean)

key = struct.unpack_from('<I', latest['sb2'], 3872)[0] & 65535
pockets = [('ITEMS', 784, 42), ('KEY', 952, 30), ('BALLS', 1072, 13), ('TMHM', 1124, 58), ('BERRIES', 1356, 43)]
item_rows = []
for name, offset, count in pockets:
    for slot in range(count):
        item, encrypted = struct.unpack_from('<HH', latest['sb1'], offset + 4 * slot)
        if item:
            item_rows.append(dict(pocket=name, slot_0based=slot, item=item, quantity=encrypted ^ key))
source_paths = ['src/pokemon.c', 'src/save.c', 'src/load_save.c', 'src/pokemon_storage_system.c',
                'src/snag.c', 'include/global.h', 'include/pokemon.h', 'include/pokemon_storage_system.h',
                'include/constants/items.h', 'src/data/pokemon/evolution.h',
                'src/data/pokemon/species_info.h', 'src/data/pokemon/experience_tables.h',
                'src/data/pokemon/pokedex_orders.h']
sources = []
for relative in source_paths:
    path = repo / relative
    sources.append(dict(path=relative, exists=path.is_file(), sha256=sha(path.read_bytes()) if path.is_file() else None))
ledgers = []
for base in ('work', 'outputs'):
    for path in (repo / base).rglob('*.json'):
        if not any(word in str(path).lower() for word in ('save', 'iv', 'inventory')):
            continue
        if path.stat().st_size > 500000:
            continue
        text = path.read_text(errors='replace')
        if ('IV' in text or 'iv' in text) and ('before' in text or 'after' in text) and ('2x' in text or 'double' in text or 'doubl' in text):
            ledgers.append(dict(path=str(path.relative_to(repo)), sha256=sha(path.read_bytes()), bytes=path.stat().st_size))
assert sha(source.read_bytes()) == expected
assert all(sha(path.read_bytes()) == digest for path, digest in protected.items())
print(json.dumps(dict(schema='thunder-yellow-v14-read-only-preflight-v1', source=str(source), source_sha256=expected,
                      active_bank=latest['bank'], save_counter=latest['counter'],
                      inventory=inventory, party_and_target_records=party_rows,
                      current_bad_records=[public(row) for row in records(latest) if not row['checksum_ok'] or row['header_BadEgg']],
                      identity_donor_search=donor_matches, item_inventory=item_rows,
                      current_source_hashes=sources, prior_IV_ledger_candidates=ledgers,
                      all_original_saves_unchanged=True, write_operations=0), ensure_ascii=False, indent=2))
