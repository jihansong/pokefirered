#!/usr/bin/env python3
"""Open one safe Sky Pillar stair tile as part of the sea/sky story."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys
r=Path.cwd();p=r/'tools/hoenn_import/patches';m='SkyPillar_4F'
sha=lambda b:hashlib.sha256(b).hexdigest()
binfile=r/'data/layouts/HoennSkyPillar_4F/map.bin'
expected='692325a3215a820b6f5d3716c16426eb3819e57d818d274e864e3c065efee4c4'
b=binfile.read_bytes();assert sha(b)==expected
assert int.from_bytes(b[2*(2*14+8):2*(2*14+8)+2],'little')==0x3607
assert int.from_bytes(b[2*(2*14+7):2*(2*14+7)+2],'little')==0x3235
flags=(r/'include/constants/flags_hoenn_story.h').read_text()
assert 'FLAG_HOENN_SEAFLOOR_CLEARED' in flags
sc=p/(m+'.scripts.inc');mc=p/(m+'.mapscripts')
oldsc=sc.read_text() if sc.exists() else '';oldmc=mc.read_text() if mc.exists() else ''
actual=(r/'data/maps'/m/'scripts.inc').read_text()
assert 'MAP_SCRIPT_ON_LOAD' not in oldmc and 'MAP_SCRIPT_ON_LOAD' not in actual
label=m+'_TY_ClearLooseStones'
assert label+'::' not in oldsc and label+'::' not in actual
script=f"""{label}::
	goto_if_set FLAG_HOENN_SEAFLOOR_CLEARED, {m}_TY_OpenStairs
	goto_if_set FLAG_HOENN_BADGE08_GET, {m}_TY_OpenStairs
	end

{m}_TY_OpenStairs::
	setmetatile 8, 2, 0x235, FALSE
	end
"""
pending={sc:(oldsc.rstrip()+'\n\n@ Thunder Yellow Sky Pillar safe ascent v1\n'+script).lstrip('\n'),
 mc:(oldmc.rstrip()+'\n\tmap_script MAP_SCRIPT_ON_LOAD, '+label+'\n').lstrip('\n')}
town=p/'SootopolisCity.text.inc';text=town.read_text()
old='\t.string "Awaken RAYQUAZA at its summit.$"'
new='\t.string "Awaken RAYQUAZA at its summit.\\p"\n\t.string "Use the cleared upper stairs.\\n"\n\t.string "Loose stones were removed.$"'
assert text.count(old)==1
pending[town]=text.replace(old,new)
files=set(pending)|{r/'data/maps'/n/f for n in [m,'SootopolisCity'] for f in ['map.json','scripts.inc','text.inc']}
backup=r/'work/sky-pillar-safe-ascent-v1-backups'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
manifest={}
for f in files:
 key=str(f.relative_to(r));manifest[key]=sha(f.read_bytes()) if f.exists() else None
 if f.exists():
  dest=backup/key;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
backup.mkdir(parents=True,exist_ok=True)
for f,v in pending.items():f.parent.mkdir(parents=True,exist_ok=True);f.write_text(v,encoding='utf-8')
subprocess.run([sys.executable,'tools/hoenn_import/apply_patches.py',m,'SootopolisCity'],check=True)
assert sha(binfile.read_bytes())==expected,'source terrain changed'
receipt={'changed_runtime_tile':[8,2],'runtime_tile_from':'0x3607','runtime_tile_to':'0x3235',
 'map_ids_warp_ids_unchanged':True,'source_terrain_unchanged':True,'save_layout_changed':False,
 'legacy_rain_badge_bypass':True,'native_runtime_validated':False,'original_files':manifest}
(backup/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'backup':str(backup),'runtime_validated':False}))
