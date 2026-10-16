#!/usr/bin/env python3
"""Give the real Silver victory continuation the guarded native callback label."""
from pathlib import Path
import ast,hashlib,json,sys
p=Path('tools/johto/build_johto_league.py');old=p.read_bytes()
assert hashlib.sha256(old).hexdigest()=='cb9ba7049d9dc0fb66a5e4079626f7742f849509c9cff006e2986a71246d70be'
t=old.decode();a='{silver}_SilverVictory';b='{silver}_Silver_Victory'
assert t.count(a)==3 and b not in t;t=t.replace(a,b);new=t.encode();ast.parse(new)
assert hashlib.sha256(new).hexdigest()=='ba96cc75de8002aa4e41d6e463bdf5943c05b098a9fed15d67d802d9f4a41bf8'
print(json.dumps({'path':str(p),'bytes':len(new),'sha256':hashlib.sha256(new).hexdigest(),
 'callback_references_renamed':3,'trainer_and_flags_unchanged':True,'native_callback_guard_unchanged':True}))
if '--apply' in sys.argv:
 backup=p.with_name(p.name+'.before-silver-victory-label');assert not backup.exists();backup.write_bytes(old);p.write_bytes(new)
