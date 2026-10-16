#!/usr/bin/env python3
"""Connect Sootopolis's differently sized interior Dive maps; preserve terrain."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys
r=Path.cwd();p=r/'tools/hoenn_import/patches'
pairs=[
 ('Underwater_SootopolisCity','MAP_SOOTOPOLIS_CITY',31,54,
  'a9e6ac9a919b821dd76091cfbe25c532c90336ed7a3d7cb965d99c492c68619f'),
 ('SootopolisCity','MAP_UNDERWATER_SOOTOPOLIS_CITY',9,6,
  '620c9c896617640b73595ea98d32d68b8eb0e850ea681c7b2f51f30b8f43fe49')]
pending={};originals=set();terrain={}
for m,dest,x,y,expected in pairs:
 mp=r/'data/maps'/m/'map.json'
 md=json.loads(mp.read_text())
 layout=next(z for z in json.loads((r/'data/layouts/layouts.json').read_text())['layouts']
             if z.get('id')==md['layout'])
 binary=r/layout['blockdata_filepath']
 assert hashlib.sha256(binary.read_bytes()).hexdigest()==expected,('terrain changed',m)
 terrain[str(binary.relative_to(r))]=expected
 assert md['connections'] is None,('unexpected interior connection',m)
 label=m+'_NativeDiveWarp'
 line='\tmap_script MAP_SCRIPT_ON_DIVE_WARP, '+label+'\n'
 sc=p/(m+'.scripts.inc');mc=p/(m+'.mapscripts')
 oldscript=sc.read_text() if sc.exists() else ''
 oldmaps=mc.read_text() if mc.exists() else ''
 actual=(r/'data/maps'/m/'scripts.inc').read_text()
 block=label+'::\n\tsetdivewarp '+dest+', '+str(x)+', '+str(y)+'\n\tend\n'
 if label+'::' in oldscript:
  assert block in oldscript,('existing canonical Dive differs',m)
 else:
  assert label+'::' not in actual,('untracked generated Dive hook',m)
  oldscript=oldscript.rstrip()+'\n\n@ Thunder Yellow Sootopolis Dive v1\n'+block
 if 'MAP_SCRIPT_ON_DIVE_WARP' in oldmaps:
  assert oldmaps.count('MAP_SCRIPT_ON_DIVE_WARP')==1 and line in oldmaps,m
 else:
  assert 'MAP_SCRIPT_ON_DIVE_WARP' not in actual,('untracked Dive mapscript',m)
  oldmaps=oldmaps.rstrip()+'\n'+line
 pending[sc]=oldscript.lstrip('\n');pending[mc]=oldmaps.lstrip('\n')
 originals.update([sc,mc]+[r/'data/maps'/m/f for f in ['map.json','scripts.inc','text.inc']])
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=r/'work/sootopolis-dive-v1-backups'/stamp
manifest={}
for f in originals:
 key=str(f.relative_to(r))
 if f.exists():
  manifest[key]=hashlib.sha256(f.read_bytes()).hexdigest()
  target=backup/key;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
 else:manifest[key]=None
backup.mkdir(parents=True,exist_ok=True)
for f,v in pending.items():f.parent.mkdir(parents=True,exist_ok=True);f.write_text(v,encoding='utf-8')
subprocess.run([sys.executable,'tools/hoenn_import/apply_patches.py']+[z[0] for z in pairs],check=True)
for f,h in terrain.items():assert hashlib.sha256((r/f).read_bytes()).hexdigest()==h,f
receipt={'maps':[z[0] for z in pairs],'terrain_unchanged':True,'save_layout_changed':False,
 'native_runtime_validated':False,'original_files':manifest,
 'canonical_files':{str(f.relative_to(r)):hashlib.sha256(f.read_bytes()).hexdigest() for f in pending}}
(backup/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'backup':str(backup),'maps':receipt['maps'],'runtime_validated':False}))
