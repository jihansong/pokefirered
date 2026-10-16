#!/usr/bin/env python3
"""Disable the passed East Gate coord trigger before returning field control."""
from pathlib import Path
import argparse,ast,hashlib,json,datetime
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('/workspaces/pokefirered'));p.add_argument('--apply',action='store_true');a=p.parse_args()
H=lambda b:hashlib.sha256(b).hexdigest()
generator={'9361ee5aad75cc22ae8425cc7c3a45f89008f423189b02474b42ac66d69ee519':'fe667caf94807c5b3e0e22af071da8dcc6a8fa3e77224b4297eddef2c9eabc86','828a130a25531ed0db77131b135f7043cfda86862b4a2e8a968dd69ba97f0a4a':'7e39576f02bdd4eadfa9522c1a2e7de7d3bbc5f2c8e9afda13a9dcfd1eaf17a3'}
rows=[('tools/johto/build_mahogany.py',generator),('data/maps/EcruteakCity_EastGate/scripts.inc',{'0920676beef6451b70f2b56977bb404e8147ecafc974d142ba10f7ee1b4ddbd7':'3880aacbab124fe65dfbea9896483880b294b20e58fc52f32c97282fecf4f8af'})]
OLD="EcruteakCity_EastGate_Allow::\n    end"
NEW="EcruteakCity_EastGate_Allow::\n    setvar VAR_TEMP_0, 1\n    end"
writes=[]
for name,pairs in rows:
 path=a.root/name;before=path.read_bytes();oldsha=H(before);assert oldsha in pairs,(name,'source changed',oldsha)
 text=before.decode();assert text.count(OLD)==1,(name,'pass-branch anchor changed')
 after=text.replace(OLD,NEW,1).encode();assert H(after)==pairs[oldsha]
 if name.endswith('.py'):ast.parse(after.decode(),filename=name)
 writes.append((path,before,after))
if a.apply:
 backup=a.root/'outputs'/('mahogany-east-gate-once-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));backup.mkdir(parents=True,exist_ok=False)
 for path,before,after in writes:
  assert path.read_bytes()==before;rel=path.relative_to(a.root);dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(before)
 for path,before,after in writes:
  assert path.read_bytes()==before
  tmp=path.with_suffix(path.suffix+'.gate.tmp');tmp.write_bytes(after);tmp.replace(path)
print(json.dumps({'applied':a.apply,'files':[{'path':str(p),'bytes':len(n),'sha256':H(n)} for p,b,n in writes],'existing_flag_and_save_layout_changed':False}))
