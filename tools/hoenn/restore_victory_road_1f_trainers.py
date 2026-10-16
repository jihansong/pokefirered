#!/usr/bin/env python3
"""Restore the five original Emerald Victory Road 1F trainer encounters."""
import argparse,hashlib,json,re,struct
from datetime import datetime,timezone
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--apply',action='store_true');a=P.parse_args()
ROOT=Path.cwd();M='HoennVictoryRoad_1F';MARK='THYL_VICTORY_ROAD_1F_TRAINERS_V1'
sha=lambda b:hashlib.sha256(b).hexdigest()
PREIMAGES={
 "include/constants/opponents_hoenn_story.h": "3fdbdef3b124c8f348a5ad625e73959f6a0c7404a3f6af1cb4d74924d4174ca9",
 "src/data/trainers_hoenn_story.h": "5a574d06891a43dfc2766f42373da2670510860bd3479de088cfe6c8158db255",
 "src/data/trainer_parties_hoenn_story.h": "a17372ada84acab9a559b5e6a60d2a8d21799ac93f6dea3ee5ac81ebebf529ef",
 "data/maps/HoennVictoryRoad_1F/map.json": "9020d1b93c963420b77aa92cfd365e4d08448c9f88a18de2a98855a8079b4191",
 "data/maps/HoennVictoryRoad_1F/scripts.inc": "35c17a06bec19481698d6bb26ae571f97fd01140b9807217b5577d77c5c58bc4",
 "data/maps/HoennVictoryRoad_1F/text.inc": "34f86ef82dfc67f1f58320457bc8d2d8770b7836d4388169e6ded01c55da93ef"
}
ORIGINAL_HASHES=[
 [
  "Edgar",
  "6ac9872cbc4d0bf4b18dc6d92c77f5943867665b2e02a97338ee0281792be1c2",
  "c32cac2697bd446cd90a23cda4d2ffd30212f7c02fbcb1f7199f42c41c12e378"
 ],
 [
  "Hope",
  "8055a621d2e5dfb30008a617f182f01879d1fc794702a63851252b8b2efd7e16",
  "c04d60e0c24b2d7b643c3c8714f64798f3cb41b99508e277bf3fe587cb1cc3eb"
 ],
 [
  "Albert",
  "5d0269dd53c9f2ca327a984ee023dcd305c9b525c2254f9e914a8b05ac064571",
  "82a4d35e8ecf89e76b1e36e7684c7b16c873e7b363b25d5032660fbf98dde7fb"
 ],
 [
  "Katelynn",
  "758bd6ea01933251dd826b378bae1bd0f7f783ee35f22d0eb7c93069e5f86378",
  "85cbefb2e15dcb3aed6ad1879868b458097d214eb8a0520fc4f38073565553fa"
 ],
 [
  "Quincy",
  "9df883572060b2980b7836fbaa818bb336af160042a2d58207407cd80feddca1",
  "915f319d4f51731ddf50b04d6a7f7b92d0302011baf3da9aa47b4efe36379e9d"
 ]
]
DATA=[
 ('Edgar',0,539,33,22,3,'MOVEMENT_TYPE_FACE_DOWN',3),
 ('Hope',1,540,6,15,4,'MOVEMENT_TYPE_FACE_LEFT',4),
 ('Albert',2,541,27,34,3,'MOVEMENT_TYPE_FACE_DOWN_AND_RIGHT',3),
 ('Katelynn',3,542,29,17,3,'MOVEMENT_TYPE_FACE_RIGHT',2),
 ('Quincy',4,543,32,17,3,'MOVEMENT_TYPE_FACE_LEFT',2)]
paths=list(PREIMAGES);old={p:(ROOT/p).read_bytes() for p in paths}
# Map completion is identified by original NORMAL trainer types and sight ranges.
def patched(p,b):
 if not p.endswith('/map.json'):return MARK.encode() in b
 j=json.loads(b);return all(any(o.get('script')==M+'_EventScript_H'+str(h) and
  o.get('trainer_type')=='TRAINER_TYPE_NORMAL' and str(o.get('trainer_sight_or_berry_tree_id'))==str(sight)
  for o in j['object_events']) for name,h,slot,x,y,elev,movement,sight in DATA)
if all(patched(p,b) for p,b in old.items()):
 print(json.dumps({'pass':True,'already_applied':True,'writes':0}));raise SystemExit
assert not any(patched(p,b) for p,b in old.items()),'partial VR1F trainer patch'
for p,b in old.items():assert sha(b)==PREIMAGES[p],('preimage changed',p,sha(b))
assert all('THYL_WALLY_FINAL_V1' in old[p].decode() for p in paths if not p.endswith('/map.json'))
terrain_path=ROOT/'data/layouts/HoennVictoryRoad_1F/map.bin'
terrain=terrain_path.read_bytes()
assert sha(terrain)=='b100693756672442b3f583a8886950d07b68bac1b6eafe07a2b5fe721d1c484e'
all_opponents='\n'.join(p.read_text() for p in (ROOT/'include/constants').glob('opponents*.h'))
for name,h,slot,*rest in DATA:
 assert not re.search(r'\(HOENN_TRAINERS_START\s*\+\s*'+str(slot)+r'\)',all_opponents),('trainer slot in use',slot)
 assert 'TRAINER_HOENN_'+name.upper()+'_VICTORY_ROAD' not in all_opponents
assert re.search(r'#define\s+HOENN_STORY_FLAGS_USED\s+113\b',(ROOT/'include/constants/flags_hoenn_story.h').read_text())
tc=(ROOT/'include/constants/trainers.h').read_text()
for c in ['TRAINER_CLASS_COOLTRAINER','TRAINER_PIC_COOLTRAINER_M','TRAINER_PIC_COOLTRAINER_F']:
 assert c in tc,c
emerald=Path('/root/src/pokeemerald')
trainer_source=(emerald/'src/data/trainers.h').read_text()
party_source=(emerald/'src/data/trainer_parties.h').read_text()
original_scripts=(emerald/'data/maps/VictoryRoad_1F/scripts.inc').read_text()
original_map=json.loads((emerald/'data/maps/VictoryRoad_1F/map.json').read_text())
def initializer(source,tag):
 matches=list(re.finditer(re.escape(tag),source));assert len(matches)==1,(tag,len(matches))
 start=matches[0].start();n=source.index('{',start)+1;depth=1
 while depth:
  depth+=(source[n]=='{')-(source[n]=='}');n+=1
 while n<len(source) and source[n] in ' ;,\r\n':n+=1
 return source[start:n].rstrip()+'\n'
def text_block(label):
 m=re.search(r'^'+re.escape(label)+r':\n.*?(?=\n\n|\Z)',original_scripts,re.M|re.S)
 assert m,label
 return m.group()+'\n'
new={p:b.decode() for p,b in old.items()}
op='include/constants/opponents_hoenn_story.h'
tail='#endif  // GUARD_CONSTANTS_OPPONENTS_HOENN_STORY_H\n'
assert new[op].count(tail)==1
defs='// '+MARK+'\n'
trainers='\n// '+MARK+'\n';parties='\n// '+MARK+'\n'
scripts='\n@ '+MARK+': original teams, defeat bits and automatic sight encounters.\n'
texts='\n@ '+MARK+': original Emerald intro and defeat dialogue.\n'
map_path='data/maps/'+M+'/map.json';j=json.loads(new[map_path])
before_objects=json.loads(json.dumps(j['object_events']));before_map=json.loads(json.dumps(j))
assert len(j['object_events'])==8 and j['object_events'][-1]['script']==M+'_EventScript_TYWallyFinal'
expected_species=[['SPECIES_CACTURNE','SPECIES_PELIPPER'],['SPECIES_ROSELIA'],
 ['SPECIES_MAGNETON','SPECIES_MUK'],['SPECIES_GARDEVOIR','SPECIES_SLAKING'],
 ['SPECIES_SLAKING','SPECIES_DUSCLOPS']]
for idx,(name,h,slot,x,y,elev,movement,sight) in enumerate(DATA):
 trainer=initializer(trainer_source,'[TRAINER_'+name.upper()+'] =')
 kind='Custom' if name in ('Katelynn','Quincy') else 'Default'
 party=initializer(party_source,'static const struct TrainerMonNoItem'+kind+'Moves sParty_'+name+'[]')
 _,th,ph=ORIGINAL_HASHES[idx]
 assert sha(trainer.encode())==th,(name,'trainer original changed')
 assert sha(party.encode())==ph,(name,'party original changed')
 assert re.findall(r'\.species\s*=\s*(\w+)',party)==expected_species[idx]
 assert re.findall(r'\.iv\s*=\s*(\d+)',party)==['100']*len(expected_species[idx])
 assert '.items = {ITEM_FULL_RESTORE, ITEM_NONE, ITEM_NONE, ITEM_NONE}' in trainer
 new_name='TRAINER_HOENN_'+name.upper()+'_VICTORY_ROAD'
 party_name='sHoennParty_'+name+'VictoryRoad'
 defs+='#define '+new_name+' (HOENN_TRAINERS_START + '+str(slot)+')\n'
 trainers+='    '+trainer.replace('TRAINER_'+name.upper(),new_name).replace('sParty_'+name,party_name)
 parties+=party.replace('sParty_'+name,party_name)
 label=M+'_EventScript_H'+str(h)
 old_script=label+'::\n\tmsgbox '+M+'_Text_H'+str(h)+', MSGBOX_NPC\n\tend\n'
 assert new['data/maps/'+M+'/scripts.inc'].count(old_script)==1
 new_script=label+'::\n\ttrainerbattle_single '+new_name+', '+M+'_Text_TY'+name+'Intro, '+M+'_Text_TY'+name+'Defeat\n\tmsgbox '+M+'_Text_H'+str(h)+', MSGBOX_AUTOCLOSE\n\tend\n'
 new['data/maps/'+M+'/scripts.inc']=new['data/maps/'+M+'/scripts.inc'].replace(old_script,new_script)
 for suffix in ('Intro','Defeat'):
  b=text_block('VictoryRoad_1F_Text_'+name+suffix)
  texts+=b.replace('VictoryRoad_1F_Text_'+name+suffix,M+'_Text_TY'+name+suffix)+'\n'
 matches=[o for o in j['object_events'] if o['script']==label];assert len(matches)==1
 o=matches[0]
 assert (o['x'],o['y'],o['elevation'],o['movement_type'],o['trainer_type'],o['flag'])==(x,y,elev,movement,'TRAINER_TYPE_NONE','0')
 originals=[q for q in original_map['object_events'] if q.get('script')=='VictoryRoad_1F_EventScript_'+name]
 assert len(originals)==1,name
 original=originals[0]
 assert (original['x'],original['y'],original['elevation'],original['movement_type'],original['trainer_type'],str(original['trainer_sight_or_berry_tree_id']),original['flag'])==(x,y,elev,movement,'TRAINER_TYPE_NORMAL',str(sight),'0')
 assert (original['movement_range_x'],original['movement_range_y'])==(o['movement_range_x'],o['movement_range_y'])
 o['trainer_type']='TRAINER_TYPE_NORMAL';o['trainer_sight_or_berry_tree_id']=str(sight)
new[op]=new[op].replace(tail,defs+tail)
new['src/data/trainers_hoenn_story.h']+=trainers
new['src/data/trainer_parties_hoenn_story.h']+=parties
new['data/maps/'+M+'/scripts.inc']+=scripts
new['data/maps/'+M+'/text.inc']+=texts
new[map_path]=json.dumps(j,indent=2)+'\n'
# Only type and native sight range may change on the existing five objects.
for old_o,new_o in zip(before_objects,j['object_events']):
 for k in old_o:
  if k not in ('trainer_type','trainer_sight_or_berry_tree_id'):assert old_o[k]==new_o[k],k
for k in before_map:
 if k!='object_events':assert before_map[k]==j[k],k
assert j['object_events'][-1]==before_objects[-1],'Wally changed'
for p,s in new.items():assert patched(p,s.encode()),p
protected={p:sha(p.read_bytes()) for p in (ROOT/'saves').rglob('*.sav')}
receipt={'pass':True,'apply':a.apply,'trainers':[{'name':n,'slot':s} for n,h,s,*_ in DATA],
 'save_layout_changes':0,'original_sight_and_teams':True,'existing_wally_items_warps_preserved':True,
 'terrain_sha256':sha(terrain),
 'files':[{'path':p,'before':sha(old[p]),'after':sha(s.encode())} for p,s in new.items()]}
if a.apply:
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 backup=ROOT/'work'/'backups'/('victory-road-1f-trainers-v1-'+stamp)
 assert not backup.exists()
 for p,b in old.items():
  q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
 for p,s in new.items():(ROOT/p).write_text(s)
 assert terrain_path.read_bytes()==terrain
 assert protected=={p:sha(p.read_bytes()) for p in protected}
 receipt['backup']=str(backup)
print(json.dumps(receipt,indent=2))
