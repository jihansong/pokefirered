#!/usr/bin/env python3
"""Restore only the fourteen original Victory Road B1F field obstacles."""
import argparse,hashlib,json,re,struct
from datetime import datetime,timezone
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--apply',action='store_true');a=P.parse_args()
ROOT=Path.cwd();M='VictoryRoad_B1F';PTH='data/maps/'+M+'/map.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
OLD_SHA='d8fbf7720d0caa38f404955b28ad5e4c2e8bbb62a676bd641ba1d6935902dc43'
TERRAIN_SHA='574316b10f2989df34eb3a53c3fc4bd946bb0e67bb679e15dfc91997cb47d684'
ORIGINAL_OBSTACLES_SHA='708fad442c50a6661dddadab2c5797451eebf3c0b4ee0f0ecb8401f8466e40c3'
original=json.loads(Path('/root/src/pokeemerald/data/maps/VictoryRoad_B1F/map.json').read_text())
obstacles=[o for o in original['object_events'] if o.get('graphics_id') in
 ('OBJ_EVENT_GFX_PUSHABLE_BOULDER','OBJ_EVENT_GFX_BREAKABLE_ROCK')]
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
assert len(obstacles)==14 and sha(canon(obstacles))==ORIGINAL_OBSTACLES_SHA,'original obstacle source changed'
assert sum(o['script']=='EventScript_StrengthBoulder' for o in obstacles)==8
assert sum(o['script']=='EventScript_RockSmash' for o in obstacles)==6
translated=[]
for o in obstacles:
 q={'type':'object',**o}
 if q['graphics_id']=='OBJ_EVENT_GFX_BREAKABLE_ROCK':q['graphics_id']='OBJ_EVENT_GFX_ROCK_SMASH_ROCK'
 assert q['movement_type']=='MOVEMENT_TYPE_LOOK_AROUND' and q['elevation']==3
 assert q['trainer_type']=='TRAINER_TYPE_NONE'
 assert re.fullmatch(r'FLAG_TEMP_1[1-9A-F]',q['flag']),q['flag']
 translated.append(q)
assert len({o['flag'] for o in translated})==14
old=(ROOT/PTH).read_bytes();j=json.loads(old)
if len(j['object_events'])==21 and j['object_events'][7:]==translated:
 print(json.dumps({'pass':True,'already_applied':True,'writes':0}));raise SystemExit
assert sha(old)==OLD_SHA,('preimage changed',PTH,sha(old))
assert len(j['object_events'])==7,'unexpected existing objects'
assert sum(o['trainer_type']=='TRAINER_TYPE_NORMAL' for o in j['object_events'])==5
assert sum(o['graphics_id']=='OBJ_EVENT_GFX_ITEM_BALL' for o in j['object_events'])==2
assert not any(o['graphics_id'] in('OBJ_EVENT_GFX_PUSHABLE_BOULDER','OBJ_EVENT_GFX_ROCK_SMASH_ROCK') for o in j['object_events'])
before=json.loads(json.dumps(j));terrain_path=ROOT/'data/layouts/HoennVictoryRoad_B1F/map.bin'
terrain=terrain_path.read_bytes();assert sha(terrain)==TERRAIN_SHA and len(terrain)==46*31*2
for o in translated:
 assert not any((q['x'],q['y'])==(o['x'],o['y']) for q in j['object_events']+j['warp_events'])
 assert struct.unpack_from('<H',terrain,2*(o['y']*46+o['x']))[0]==0x3201,'original obstacle floor/elevation changed'
global_constants=(ROOT/'include/constants/global.h').read_text()
assert re.search(r'#define\s+OBJECT_EVENTS_COUNT\s+16\b',global_constants)
assert re.search(r'#define\s+OBJECT_EVENT_TEMPLATES_COUNT\s+64\b',global_constants)
gfx=(ROOT/'include/constants/event_objects.h').read_text()
for name,value in [('OBJ_EVENT_GFX_ROCK_SMASH_ROCK',96),('OBJ_EVENT_GFX_PUSHABLE_BOULDER',97)]:
 assert re.search(r'#define\s+'+name+r'\s+'+str(value)+r'\b',gfx),name
scripts=(ROOT/'data/scripts/field_moves.inc').read_text()
for label in ('EventScript_StrengthBoulder::','EventScript_RockSmash::'):
 assert label in scripts,label
flags=(ROOT/'include/constants/flags.h').read_text()
for o in translated:assert re.search(r'#define\s+'+o['flag']+r'\s+',flags),o['flag']
j['object_events'].extend(translated)
assert len(j['object_events'])==21<=64
assert j['object_events'][:7]==before['object_events'],'old local IDs/objects changed'
for k in before:
 if k!='object_events':assert before[k]==j[k],('non-object map data changed',k)
new=(json.dumps(j,indent=2)+'\n').encode()
# Templates are spawned in view; 21 templates do not mean 21 active objects.
# This conservative static estimate includes declared movement ranges. Native
# player+Pikachu/spawn/cold-load and boulder relocation QA remain required.
dense=[]
for y in range(31):
 for x in range(46):
  if struct.unpack_from('<H',terrain,2*(y*46+x))[0]!=0x3201:continue
  if any(o['x']==x and o['y']==y for o in j['object_events']):continue
  seen=[o for o in j['object_events'] if
   x-9-o['movement_range_x']<=o['x']<=x+10+o['movement_range_x'] and
   y-7-o['movement_range_y']<=o['y']<=y+9+o['movement_range_y']]
  dense.append((len(seen),x,y))
max_templates=max(n for n,x,y in dense)
assert max_templates+2<=16,'static spawn budget exceeds player plus follower capacity'
protected={p:sha(p.read_bytes()) for p in (ROOT/'saves').rglob('*.sav')}
receipt={'pass':True,'apply':a.apply,'path':PTH,'before':sha(old),'after':sha(new),
 'original_obstacles_sha256':sha(canon(obstacles)),'added_boulders':8,'added_smash_rocks':6,
 'template_count':21,'template_capacity':64,'active_object_capacity':16,
 'conservative_static_max_templates':max_templates,'player_and_follower_static_budget':max_templates+2,
 'safe_dense_probe_xy':[[25,7],[26,7]],'native_spawn_and_puzzle_qa_still_required':True,
 'new_local_ids':list(range(8,22)),'temp_flags':[o['flag'] for o in translated],
 'existing_7_objects_warps_items_preserved':True,'save_layout_changes':0,'terrain_sha256':sha(terrain)}
if a.apply:
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 backup=ROOT/'work'/'backups'/('victory-road-b1-obstacles-v1-'+stamp)
 assert not backup.exists()
 q=backup/PTH;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(old)
 (ROOT/PTH).write_bytes(new)
 assert terrain_path.read_bytes()==terrain
 assert protected=={p:sha(p.read_bytes()) for p in protected}
 receipt['backup']=str(backup)
print(json.dumps(receipt,indent=2))
