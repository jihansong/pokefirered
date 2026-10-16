#!/usr/bin/env python3
"""Apply this source-only candidate after all fresh hashes match; preserve backup."""
from pathlib import Path
import argparse, hashlib, json, os

p = argparse.ArgumentParser()
p.add_argument('--root', type=Path, required=True)
p.add_argument('--bundle', type=Path, default=Path(__file__).parent)
p.add_argument('--backup', type=Path, required=True)
p.add_argument('--apply', action='store_true')
a = p.parse_args()
root, bundle, backup = a.root.resolve(), a.bundle.resolve(), a.backup.resolve()
manifest = json.loads((bundle/'manifest.json').read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
rows = manifest['files']
assert backup.is_relative_to(root/'work') and not backup.exists()
payload = {}
for name, row in rows.items():
    dest = (root/name).resolve()
    assert dest.is_relative_to(root) and not dest.is_symlink()
    raw = (bundle/'candidate'/name).read_bytes()
    assert sha(raw) == row['after_sha256'], ('candidate mismatch', name)
    if row['before_sha256'] is None:
        assert not dest.exists(), ('new file already exists', name)
    else:
        assert dest.is_file() and sha(dest.read_bytes()) == row['before_sha256'], ('fresh source changed', name)
    payload[name] = raw
print(json.dumps({'checked_source_files': len(rows), 'apply_requested': a.apply}), flush=True)
if not a.apply:
    raise SystemExit(0)
backup.mkdir(parents=True)
for name, row in rows.items():
    if row['before_sha256'] is not None:
        target = backup/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((root/name).read_bytes())
(backup/'source-manifest.json').write_text(json.dumps(manifest, indent=2))
applied = []
try:
    for name, raw in payload.items():
        dest = root/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        temp = dest.with_name(dest.name+'.misty-story-tmp')
        assert not temp.exists()
        with temp.open('xb') as f:
            f.write(raw)
        os.replace(temp, dest)
        assert sha(dest.read_bytes()) == rows[name]['after_sha256']
        applied.append(name)
except BaseException:
    # Only roll back our own exact writes. A concurrent edit is never overwritten.
    for name in reversed(applied):
        dest = root/name
        assert sha(dest.read_bytes()) == rows[name]['after_sha256'], ('concurrent change during rollback', name)
        if rows[name]['before_sha256'] is None:
            dest.unlink()
        else:
            dest.write_bytes((backup/name).read_bytes())
    raise
(backup/'applied-receipt.json').write_text(json.dumps({'source_applied': True, 'files': rows,
              'rom_rebuilt': False, 'saves_modified': False}, indent=2))
print(json.dumps({'source_applied': True, 'source_files': len(rows), 'backup': str(backup),
                   'rom_rebuilt': False, 'saves_modified': False}), flush=True)
