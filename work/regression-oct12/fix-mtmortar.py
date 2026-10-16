from pathlib import Path
import json,re,hashlib,datetime,os,tempfile,copy
r=Path('/workspaces/pokefirered');bp=r/'tools/johto/build_mahogany.py';lp=r/'data/layouts/layouts.json'
b0=bp.read_bytes();l0=lp.read_bytes();s=b0.decode();d=json.loads(l0)
m=json.loads((r/'data/maps/MtMortar_1F/map.json').read_text());target_id=m['layout']
target=[x for x in d['layouts'] if x.get('id')==target_id]
donor=[x for x in d['layouts'] if x.get('id')=='LAYOUT_ROCK_TUNNEL_1F']
assert len(target)==len(donor)==1
assert donor[0]['primary_tileset']=='gTileset_General' and donor[0]['secondary_tileset']=='gTileset_RockTunnel'
assert target[0]['secondary_tileset']=='gTileset_RockTunnel'
assert target[0]['primary_tileset'] in ('gTileset_Building','gTileset_General')
pat=r'''(["']MtMortar_1F["']\s*:\s*\(\s*["'])(Building|General)(["']\s*,\s*["']RockTunnel["']\s*,\s*["']LAYOUT_ROCK_TUNNEL_1F["']\s*\))'''
assert len(list(re.finditer(pat,s)))==1
b1=re.sub(pat,lambda q:q[1]+'General'+q[3],s).encode()
text=l0.decode();blockpat=r'\{[^{}]*"id"\s*:\s*"'+re.escape(target_id)+r'"[^{}]*\}'
matches=list(re.finditer(blockpat,text));assert len(matches)==1
old=matches[0][0];new=old.replace('"gTileset_Building"','"gTileset_General"')
l1=text.replace(old,new,1).encode()
expected=copy.deepcopy(d);next(x for x in expected['layouts'] if x.get('id')==target_id)['primary_tileset']='gTileset_General'
assert json.loads(l1)==expected
changes=[(p,o,n) for p,o,n in [(bp,b0,b1),(lp,l0,l1)] if o!=n]
backup=r/'work/regression-oct12/backups';backup.mkdir(parents=True,exist_ok=True)
prepared=[]
try:
 for p,o,n in changes:
  h=hashlib.sha256(o).hexdigest();dest=backup/(p.name+'.pre-mtmortar-'+h[:12])
  if dest.exists():assert dest.read_bytes()==o
  else:dest.write_bytes(o)
  assert p.read_bytes()==o
  fd,tmp=tempfile.mkstemp(prefix='.mtmortar-',dir=p.parent)
  with os.fdopen(fd,'wb') as f:f.write(n)
  prepared.append((p,Path(tmp),o))
 for p,tmp,o in prepared:os.replace(tmp,p)
except BaseException:
 for p,tmp,o in prepared:
  if tmp.exists():tmp.unlink()
  if p.read_bytes()!=o:p.write_bytes(o)
 raise
receipt={'status':'source repaired; rebuild and native visual validation pending','layout':target_id,'changes':[{'path':str(p),'before_sha256':hashlib.sha256(o).hexdigest(),'after_sha256':hashlib.sha256(n).hexdigest()} for p,o,n in changes]}
(r/'work/regression-oct12/mtmortar-repair-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
