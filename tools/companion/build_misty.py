#!/usr/bin/env python3
"""Dry by default. Integrate Misty as a second transient field companion."""
import argparse,datetime,hashlib,json,pathlib,re,struct
ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');a=ap.parse_args()
root=pathlib.Path('/workspaces/pokefirered').resolve();payload=json.loads((root/'tools/companion/misty_source_payload.json').read_text())
H=lambda b:hashlib.sha256(b).hexdigest()
state=root/'outputs/misty-companion-v1/applied-state.json'
previous=json.loads(state.read_text()) if state.is_file() else {}
old={};wanted={}
def read(p):
 q=(root/p).resolve();assert q.is_relative_to(root),('path outside workspace',p)
 assert q.is_file(),('missing existing source',p)
 if p not in old:old[p]=q.read_bytes()
 return old[p].decode('utf-8')
for p,h in payload['preimages'].items():
 t=read(p);actual=H(old[p]);assert actual in [h,previous.get('hashes',{}).get(p)],('source preimage changed',p,actual)
for row in payload['recipes']:
 p=row['path'];t=wanted.get(p,read(p))
 if 'append' in row:
  if row['append'] not in t:t+=row['append']
  assert t.count(row['append'])==1,('append duplicate',p)
 else:
  before,after=row['old'],row['new']
  if before in t:
   assert t.count(before)==1,('ambiguous source anchor',p);t=t.replace(before,after,1)
  else:assert t.count(after)==1,('missing source anchor',p)
 wanted[p]=t
# Preserve every pre-existing map event; append one flagged static NPC only.
p='data/maps/PalletTown/map.json';meta=json.loads(read(p));original=payload['pallet_original_map'];npc=payload['pallet_object']
if meta==original:
 assert all((int(v['x']),int(v['y']))!=(8,10) for k in ['object_events','warp_events','coord_events','bg_events'] for v in meta.get(k,[]))
 meta['object_events'].append(npc)
else:
 assert meta.get('object_events',[])[-1]==npc
 check=dict(meta);check['object_events']=meta['object_events'][:-1];assert check==original,'Pallet original map events changed'
assert len(meta['object_events'])==len(original['object_events'])+1
layouts=json.loads((root/'data/layouts/layouts.json').read_text())['layouts']
rows=[v for v in layouts if v.get('id')==meta['layout']];assert len(rows)==1
layout=rows[0];w,h=layout['width'],layout['height'];raw=(root/layout['blockdata_filepath']).read_bytes();assert len(raw)==w*h*2
word=struct.unpack_from('<H',raw,2*(10*w+8))[0]
assert not word&0xc00 and word>>12==3,('Misty Pallet NPC tile is not walkable elevation3',hex(word))
wanted[p]=json.dumps(meta,indent=2)+'\n'
# New ROM data has no player party or save layout mutation. Reserved offsets must fit.
import sys
sys.path.insert(0,str(root/'tools/qa'))
from gamedata import const,off
assert const('FLAG_0x223')==0x223 and const('FLAG_0x224')==0x224
assert const('HOENN_TRAINERS_START')>0 and const('HOENN_TRAINERS_START')+855<65536
trainer_bytes=off('sb2.hoennFlags')-off('sb2.hoennTrainerFlags');assert trainer_bytes>0 and trainer_bytes*8>855
for flag in ['FLAG_SYS_GAME_CLEAR','FLAG_BADGE01_GET','FLAG_BADGE08_GET','FLAG_HOENN_BADGE07_GET','FLAG_HOENN_BIRCH_RESCUED','FLAG_JOHTO_BADGE06_GET','FLAG_JOHTO_BADGE02_GET']:
 assert const(flag)>0,('missing existing story predicate',flag)
assert const('FLAG_BADGE08_GET')-const('FLAG_BADGE01_GET')==7
for p,s in payload['files'].items():
 q=(root/p).resolve();assert q.is_relative_to(root)
 if q.is_file():assert q.read_text()==s,('new file already contains different work',p)
 wanted[p]=s
# Friendly mode9 must still return after losses and must not enable the tutorial flag1.
setup=(root/'src/battle_setup.c').read_text()
assert 'if (sTrainerBattleMode == TRAINER_BATTLE_EARLY_RIVAL)' in setup
assert 'if (sRivalBattleFlags & RIVAL_BATTLE_HEAL_AFTER)' in setup
assert '(GetRivalBattleFlags() & RIVAL_BATTLE_TUTORIAL) == RIVAL_BATTLE_TUTORIAL' in setup
macro=(root/'asm/macros/event.inc').read_text()
assert '.macro trainerbattle_earlyrival trainer:req, flags:req, defeat_text:req, victory_text:req' in macro
assert 'trainerbattle TRAINER_BATTLE_EARLY_RIVAL, \\trainer, \\flags, \\defeat_text, \\victory_text' in macro
# Preserve ordinary trainer415 and all prior trainer/party ROM source byte-for-byte.
for p in ['src/data/trainers_hoenn.h','src/data/trainer_parties_hoenn.h']:
 assert wanted[p].startswith(old[p].decode('utf-8'))
# These checks keep the approved PIKACHU water/dive policy and its one-task budget.
def body(s,name):
 x=s.index(name);l=s.index('{',x);n=1;r=l+1
 while n:n+=(s[r]=='{')-(s[r]=='}');r+=1
 return s[l:r]
f0=read('src/follower_pikachu.c');f1=wanted['src/follower_pikachu.c']
assert body(f0,'static bool8 ShouldFollowerExist')==body(f1,'static bool8 ShouldFollowerExist')
assert body(f0,'static u8 GetFollowSpeed')==body(f1,'static u8 GetFollowSpeed')
assert f1.count('CreateTask(Task_FollowerPikachu, 80)')==1
assert 'CreateTask(' not in wanted['src/companion_misty.c']
assert wanted['src/companion_misty.c'].count('EWRAM_DATA')==1
assert 'gPlayerParty[' not in wanted['src/companion_misty.c']
changed={p:s for p,s in wanted.items() if not (root/p).is_file() or (root/p).read_bytes()!=s.encode()}
report={'dry_pass':True,'applied':False,'files':len(wanted),'changed':list(changed),'team_counts':payload['team_counts'],'team_levels':payload['team_levels'],'new_static_ewram_bytes':1,'save_fields_added':0,'same_priority80_task':True,'pikachu_water_predicate_preserved':True,'pallet_geometry_word':hex(word),'original_pallet_objects_preserved':True,'trainer_offset_range':[851,855],'trainer_flag_capacity_bits':trainer_bytes*8,'native_executed':False,'ally_battle_implemented':False}
if a.apply:
 utc=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 backup=root/'outputs/misty-companion-v1/backups'/utc;backup.mkdir(parents=True,exist_ok=False)
 for p in changed:
  if p in old:
   q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(old[p])
 for p,s in changed.items():
  q=root/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(s.encode())
 report['applied']=True;report['backup']=str(backup);report['hashes']={p:H(s.encode()) for p,s in wanted.items()}
 state.parent.mkdir(parents=True,exist_ok=True);state.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
