#!/usr/bin/env python3
"""Create separate Misty QA inputs; preserve original party/storage/Dex bytes."""
from pathlib import Path
import argparse,hashlib,json,struct,sys
sys.path.insert(0,str(Path.cwd()/'tools/qa'))
from savefile import SaveFile,Mon
from gamedata import const,off
ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
base=Path(a.base).resolve();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
H=lambda b:hashlib.sha256(b).hexdigest()
original=base.read_bytes();s=SaveFile(str(base));po=off('sb1.playerParty');party=bytes(s.sb1[po:po+600]);count=s.party_count();storage=bytes(s.blocks['storage'])
assert count==6 and len(storage)==33744
assert s.flag('FLAG_SYS_B_DASH'),'source has no running shoes; do not claim native RUN tested'
assert sum(s.party_mon(i).species()==const('SPECIES_PIKACHU') for i in range(count))==1
for i in range(count):
 m=s.party_mon(i);raw=party[i*100:(i+1)*100];assert not raw[19]&1
 assert sum(v[0] for b in m.subs().values() for v in struct.iter_unpack('<H',b))&65535==struct.unpack_from('<H',raw,28)[0]
dex=tuple(s.dex_state(i) for i in range(1,387))
meta=json.loads(Path('data/maps/PalletTown/map.json').read_text());layouts=json.loads(Path('data/layouts/layouts.json').read_text())['layouts'];ls=[v for v in layouts if v.get('id')==meta['layout']];assert len(ls)==1
l=ls[0];w,h=l['width'],l['height'];terrain=Path(l['blockdata_filepath']).read_bytes();assert len(terrain)==w*h*2
# These tested paths avoid the sign woman range and every source event/NPC tile.
for x in range(5,11):
 raw=struct.unpack_from('<H',terrain,2*(9*w+x))[0];assert raw==0x3296,(x,raw)
assert not any(v.get('y')==9 and 5<=v.get('x',-1)<=10 for k in ('warp_events','coord_events','bg_events','object_events') for v in meta[k])
rows=[]
for name,x in [('basic',5),('join-base',8)]:
 s=SaveFile(str(base));s.warp('PalletTown',x,9)
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 s.set_flag('FLAG_SYS_GAME_CLEAR',False);s.set_flag('FLAG_MISTY_COMPANION_JOINED',False);s.set_flag('FLAG_HIDE_MISTY_PALLET',True)
 s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
 s.set_var('VAR_MAP_SCENE_PALLET_TOWN_OAK',3);s.set_var('VAR_TEMP_7',0);s.set_var('VAR_REPEL_STEP_COUNT',250);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
 assert bytes(s.sb1[po:po+600])==party and s.party_count()==count and bytes(s.blocks['storage'])==storage and tuple(s.dex_state(i) for i in range(1,387))==dex
 target=out/(name+'.sav');assert not target.exists();s.save(str(target));t=SaveFile(str(target))
 assert bytes(t.sb1[po:po+600])==party and bytes(t.blocks['storage'])==storage and tuple(t.dex_state(i) for i in range(1,387))==dex
 rows.append(dict(name=name,path=str(target),sha256=H(target.read_bytes()),party600_preserved=True,storage33744_preserved=True,dex4_preserved=True,story_fixture_edits=['SYS_GAME_CLEAR=false','JOINED=false','HIDE_PALLET=true','RECEIVED_STARTER_PIKACHU=true','OakScene=3','questlog cleared'],original_save_modified=False))
assert base.read_bytes()==original
(out/'fixture-manifest.json').write_text(json.dumps(dict(original_path=str(base),original_sha256=H(original),source_pallet_terrain_sha256=H(terrain),source_geometry_checked=True,candidate_native_movement_not_yet_tested=True,fixtures=rows),indent=2))
print(json.dumps(rows,indent=2))
