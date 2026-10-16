"""Read-only SAV forensic scan: independent sector and encrypted-mon checks.

Writes JSON evidence only to this script's directory. Never changes a SAV or ROM.
Audits both complete generations, plus authentic record matches in local SAVs.
QA-generated saves are labelled and cannot authenticate a recovery donor.
"""
import hashlib
import json
import struct
from collections import defaultdict
from pathlib import Path

ROOT = Path('C:/Users/seren/Documents/Codex/2026-10-01/https-effective-meme-v6pxvx5qx6vghwj56-github-dev')
OUT = Path(__file__).resolve().parent
CURRENT = ROOT / 'outputs/save-pp15-20261013/pokemonthyl_v1.25-items99-iv2x-pp15.sav'
EXPECTED = '917c24715ca1dd78b22d6350182648fa81f307b771fa5524595d157a0b6a6604'
SIZES = [3876, 3968, 3968, 3968, 3816] + [3968] * 8 + [2000]
ORDER = ('GAEM GAME GEAM GEMA GMAE GMEA AGEM AGME AEGM AEMG AMGE AMEG '
         'EGAM EGMA EAGM EAMG EMGA EMAG MGAE MGEA MAGE MAEG MEGA MEAG').split()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def parse_banks(raw):
    assert len(raw) == 131072, 'requires exact FLASH1M battery save'
    result = []
    for bank in (0, 1):
        sectors, counters, problems = {}, set(), []
        for physical in range(bank * 14, (bank + 1) * 14):
            start = physical * 4096
            sid, stored, signature, counter = struct.unpack_from('<HHII', raw, start + 4084)
            if signature != 0x08012025 or sid >= 14 or sid in sectors:
                problems.append(dict(physical=physical, section=sid, signature=signature))
                continue
            payload = raw[start:start + SIZES[sid]]
            total = sum(struct.unpack('<%dI' % (len(payload) // 4), payload)) & 0xffffffff
            computed = (total + (total >> 16)) & 65535
            if stored != computed:
                problems.append(dict(physical=physical, section=sid, stored=stored, computed=computed))
            counters.add(counter)
            sectors[sid] = payload
        valid = len(sectors) == 14 and len(counters) == 1 and not problems
        item = dict(bank=bank, valid=valid, counters=sorted(counters), sector_errors=problems)
        if valid:
            item['counter'] = next(iter(counters))
            item['sb2'] = sectors[0]
            item['sb1'] = b''.join(sectors[s] for s in range(1, 5))
            item['storage'] = b''.join(sectors[s] for s in range(5, 14))
            assert tuple(map(len, (item['sb2'], item['sb1'], item['storage']))) == (3876, 15720, 33744)
        result.append(item)
    return result

def decode(raw):
    assert len(raw) == 80
    pid, ot = struct.unpack_from('<II', raw)
    plain = b''.join(struct.pack('<I', word ^ pid ^ ot) for word in struct.unpack('<12I', raw[32:]))
    computed = sum(struct.unpack('<24H', plain)) & 65535
    stored = struct.unpack_from('<H', raw, 28)[0]
    chunks = {letter: bytearray(plain[i * 12:(i + 1) * 12]) for i, letter in enumerate(ORDER[pid % 24])}
    species = struct.unpack_from('<H', chunks['G'])[0]
    egg_word = struct.unpack_from('<I', chunks['M'], 4)[0]
    cleared = bytearray(chunks['M'])
    struct.pack_into('<I', cleared, 4, egg_word & ~(1 << 30))
    clear_sum = sum(struct.unpack('<24H', b''.join(bytes(cleared if letter == 'M' else chunks[letter]) for letter in ORDER[pid % 24]))) & 65535
    identity = (pid, ot, raw[8:18], raw[20:27], raw[18])
    return dict(pid=pid, ot_id=ot, nickname_hex=raw[8:18].hex(), ot_name_hex=raw[20:27].hex(),
                language=raw[18], header_flags=raw[19], header_BadEgg=bool(raw[19] & 1),
                header_egg=bool(raw[19] & 4), secure_egg=bool(egg_word & (1 << 30)),
                stored_checksum=stored, computed_checksum=computed, checksum_ok=stored == computed,
                species_untrusted_if_bad=species, exp_untrusted_if_bad=struct.unpack_from('<I', chunks['G'], 4)[0],
                moves_untrusted_if_bad=list(struct.unpack_from('<4H', chunks['A'])),
                hypothetical_checksum_after_clearing_secure_egg=clear_sum,
                hypothetical_residual=(clear_sum - stored) & 65535,
                record_sha256=sha(raw), _identity=identity, _raw=raw)

def records(bank):
    if not bank['valid']:
        return []
    rows = []
    party_count = bank['sb1'][52]
    assert party_count <= 6, 'party count out of range'
    for slot in range(party_count):
        rows.append(dict(location='party', slot_1based=slot + 1, **decode(bank['sb1'][56 + 100 * slot:136 + 100 * slot])))
    for slot in range(420):
        raw = bank['storage'][4 + slot * 80:84 + slot * 80]
        if not any(raw):
            continue
        rows.append(dict(location='PC', box_1based=slot // 30 + 1, cell_1based=slot % 30 + 1, **decode(raw)))
    # Include daycare donor identities; stride 140 comes from archived global.h:
    # 80 BoxPokemon + 56 DayCareMail + 4 steps, two DaycareMon records.
    for slot in range(2):
        raw = bank['sb1'][12160 + 140 * slot:12240 + 140 * slot]
        if any(raw):
            rows.append(dict(location='daycare', slot_1based=slot + 1, **decode(raw)))
    return rows

def public(row):
    return {key: value for key, value in row.items() if not key.startswith('_')}

def main():
    before = CURRENT.read_bytes()
    assert sha(before) == EXPECTED, 'unexpected current save'
    metadata = json.loads((ROOT / 'work/save-sort-v1_1/metadata.json').read_text())
    assert metadata['offsets']['storage.boxes'] == 4
    assert metadata['offsets']['sb1.playerParty'] == 56
    assert metadata['offsets']['sb1.daycare'] == 12160
    build = json.loads((ROOT / 'outputs/misty-profile-20261014/build-validation.json').read_text())
    abi = {row['name']: row['candidate']['size'] for row in build['ram']['save_abi']}
    assert [abi[key] for key in ('gSaveBlock2', 'gSaveBlock1', 'gPokemonStorage')] == [3876, 15720, 33744]
    banks = parse_banks(before)
    current = []
    for bank in banks:
        current.append(dict(bank=bank['bank'], valid=bank['valid'], counter=bank.get('counter'),
                            sector_errors=bank['sector_errors'],
                            occupied_records=len(records(bank)),
                            bad_records=[public(row) for row in records(bank) if not row['checksum_ok'] or row['header_BadEgg']]))
    targets = {row['_identity']: row for bank in banks for row in records(bank) if not row['checksum_ok'] or row['header_BadEgg']}
    matches, scanned, failures = defaultdict(list), [], []
    paths = sorted(set((ROOT / 'work').rglob('*.sav')) | set((ROOT / 'outputs').rglob('*.sav')))
    hashes = {}
    for path in paths:
        raw = path.read_bytes()
        hashes[str(path)] = sha(raw)
        relative = str(path.relative_to(ROOT)).replace('\\', '/')
        fixture = any(word in relative.lower() for word in ('qa-only', 'preboot', 'component-tests', 'runtime-results', 'candidate'))
        try:
            parsed = parse_banks(raw)
        except AssertionError as error:
            failures.append(dict(path=relative, reason=str(error), bytes=len(raw)))
            continue
        scanned.append(dict(path=relative, sha256=sha(raw), fixture_or_derived=fixture,
                            banks=[dict(bank=b['bank'], valid=b['valid'], counter=b.get('counter'), sector_errors=b['sector_errors']) for b in parsed]))
        for bank in parsed:
            for row in records(bank):
                if row['_identity'] in targets:
                    matches[row['_identity']].append(dict(path=relative, sav_sha256=sha(raw),
                                                         fixture_or_derived=fixture, bank=bank['bank'], counter=bank['counter'], **public(row)))
    recovery = []
    for identity, target in targets.items():
        rows = matches[identity]
        healthy = [row for row in rows if row['checksum_ok'] and not row['header_BadEgg'] and not row['fixture_or_derived']]
        recovery.append(dict(target=public(target), identity_match_count=len(rows), matching_records=rows,
                             healthy_nonfixture_record_hashes=sorted({row['record_sha256'] for row in healthy}),
                             authenticated_recovery_available=bool(healthy),
                             reconstruction_or_checksum_rewrite_performed=False))
    unchanged = sha(CURRENT.read_bytes()) == EXPECTED and all(sha(Path(path).read_bytes()) == digest for path, digest in hashes.items())
    assert unchanged
    result = dict(schema='thunder-yellow-read-only-save-forensics-v1',
                  current_save_path=str(CURRENT), current_save_sha256=EXPECTED,
                  current_banks=current, local_scanned_files=scanned, skipped_files=failures,
                  target_recovery=recovery, all_scanned_inputs_unchanged=True,
                  changed_SAV_files=0, ROM_changes=0, emulator_execution=False,
                  limitations=['Only local SAV copies were scanned; remote complete inventory must be joined by SHA before claiming exhaustive recovery search.',
                               'This is a battery-save audit, not a DELTA Save State audit or a physical-device performance measurement.',
                               'A matching PID/OT/name/language plus valid checksum is a recovery lead; original donor provenance and byte deltas must still be independently checked.',
                               'Corrupt decoded species/EXP/moves are identification hints and not trustworthy original values.'])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'current-save-forensics.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(current_banks=current, unique_targets=len(targets), local_files_scanned=len(scanned),
                          healthy_donors_found=sum(bool(r['authenticated_recovery_available']) for r in recovery),
                          all_inputs_unchanged=True), ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
