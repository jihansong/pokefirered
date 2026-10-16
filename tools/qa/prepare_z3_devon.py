#!/usr/bin/env python3
"""Make disposable Devon key-item capacity fixtures; never rewrite a user save.

Run from the repository root before cases/z3_devon.jsonl. The battle cases use
the ordinary save; these two fixtures cover the KEY ITEMS pocket, which the
existing savedit fillitems command does not fill.
"""
from pathlib import Path
import hashlib
import json
import struct

from gamedata import REPO, const, items, off
from savefile import SaveFile


def main():
    source = Path(REPO) / 'saves/hoenn.sav'
    out = Path(REPO) / 'tools/qa/.cache/z3_devon'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    out.mkdir(parents=True, exist_ok=True)
    candidates = sorted({const(name): name for name, pocket in items().items()
                         if pocket == 'POCKET_KEY_ITEMS' and name != 'ITEM_DEVON_GOODS'}.items())
    capacity = const('BAG_KEYITEMS_COUNT')
    assert len(candidates) >= capacity, 'Not enough distinct real key items for this fixture'
    records = []
    for empty, filename in ((0, 'key-items-full.sav'), (1, 'key-items-one-free.sav')):
        save = SaveFile(str(source))
        offset = off('sb1.bagPocket_KeyItems')
        key = struct.unpack_from('<I', save.sb2, off('sb2.encryptionKey'))[0] & 0xFFFF
        for index in range(capacity):
            iid = candidates[index][0] if index < capacity - empty else 0
            struct.pack_into('<HH', save.sb1, offset + index * 4, iid, (1 if iid else 0) ^ key)
        assert save.item_count('ITEM_DEVON_GOODS') == 0
        target = out / filename
        save.save(str(target))
        reloaded = SaveFile(str(target))
        free = sum(struct.unpack_from('<H', reloaded.sb1, offset + index * 4)[0] == 0
                   for index in range(capacity))
        assert free == empty
        records.append({'file': target.relative_to(REPO).as_posix(), 'free_key_item_slots': free,
                        'devon_goods': reloaded.item_count('ITEM_DEVON_GOODS'),
                        'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    result = {'source': 'saves/hoenn.sav', 'source_sha256': digest, 'source_unchanged': True,
              'capacity': capacity, 'filled_with_distinct_key_items': [n for _, n in candidates[:capacity]],
              'fixtures': records}
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
