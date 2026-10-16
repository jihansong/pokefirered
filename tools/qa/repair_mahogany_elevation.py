#!/usr/bin/env python3
"""Repair source-only static elevation traversal; no canonical maps are modified."""
import argparse,ast,datetime,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--apply',action='store_true');a=p.parse_args()
path=a.root/'tools/johto/build_mahogany.py';old=path.read_text()
assert hashlib.sha256(old.encode()).hexdigest()=='607f4269f462bfb974b1618d44e52beb3b2ac92b50f1dbc10479b1dac909a32c'
replacements=[["return (t>>10)&3==0 and ((t>>12)==3 or behavior(l,t) in water_b)","return (t>>10)&3==0 and ((t>>12)!=1 or behavior(l,t) in water_b)"],["q=deque([start]);seen={start}\n  while q:\n   x,y=q.popleft()\n   for z in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:\n    if z not in seen and walk(*z):seen.add(z);q.append(z)","# Match native IsElevationMismatchAt/ObjectEventUpdateElevation:\n  # elevation0 allows a change; elevation15 retains the previous elevation.\n  # Outdoor water additionally admits the native Surf/dismount transition.\n  initial_elevation=a[start[1]*w+start[0]]>>12\n  if initial_elevation==15:initial_elevation=3\n  q=deque([(start[0],start[1],initial_elevation)])\n  states=set(q);seen={start}\n  while q:\n   x,y,current_elevation=q.popleft()\n   for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:\n    if not walk(xx,yy):continue\n    raw=a[yy*w+xx];target_elevation=raw>>12\n    water_transition=(behavior(l,raw) in water_b or behavior(l,a[y*w+x]) in water_b) and {current_elevation,target_elevation}<={0,1,3}\n    if current_elevation!=0 and target_elevation not in (0,15,current_elevation) and not water_transition:continue\n    next_elevation=current_elevation if target_elevation==15 else target_elevation\n    state=(xx,yy,next_elevation)\n    if state not in states:states.add(state);seen.add((xx,yy));q.append(state)"]]
new=old
for before,after in replacements:
 assert new.count(before)==1
 new=new.replace(before,after,1)
assert hashlib.sha256(new.encode()).hexdigest()=='4713a36c36660344ce1d6f92e8b65ed6aa6f1c6377d16d1c5457ea64745c488f'
ast.parse(new)
if a.apply:
 backup=a.root/'outputs'/('mahogany-checker-elevation-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));backup.mkdir(parents=True,exist_ok=False)
 (backup/'build_mahogany.before.py').write_bytes(path.read_bytes())
 assert path.read_text()==old
 tmp=path.with_suffix('.elevation.tmp');tmp.write_bytes(new.encode());tmp.replace(path)
print('SOURCE_CHECKER_PASS',len(new.encode()),hashlib.sha256(new.encode()).hexdigest(),'applied',a.apply)
