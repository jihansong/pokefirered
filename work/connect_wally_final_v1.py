#!/usr/bin/env python3
"""Restore Wally's original Emerald final team without changing SAV layout."""
import argparse,hashlib,json,re,shutil,struct
from datetime import datetime,timezone
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--apply',action='store_true');a=P.parse_args()
ROOT=Path.cwd();MARK='THYL_WALLY_FINAL_V1';M='HoennVictoryRoad_1F'
T='TRAINER_HOENN_WALLY_VICTORY_ROAD_FINAL'
sha=lambda b:hashlib.sha256(b).hexdigest()
PREIMAGES={
 "include/constants/opponents_hoenn_story.h": "6c02c7818796ff8cb8f1e03d3497a4f387aa37cf668c791253bcf47c6f0827e6",
 "src/data/trainers_hoenn_story.h": "6ffd5e4d3e269ec23dee18d0138dad5e1141fe59120506de32871a15bc48a20f",
 "src/data/trainer_parties_hoenn_story.h": "8495c36b60106ca4ea6aa637ccefceb56e9d8ca4cfc8b188921258f32eeadb8f",
 "data/maps/HoennVictoryRoad_1F/map.json": "21877f07eec421be551c24532b1d2090bb643300e8c92cd3e44e07a93264c104",
 "data/maps/HoennVictoryRoad_1F/scripts.inc": "a9ea40629ea348bce99005402569f7d3e477facddeb06791db3eba2c677304ba",
 "data/maps/HoennVictoryRoad_1F/text.inc": "bd24b8e7e108fa91640e842b777e79ad8d22cc23e6f1a4cd26fa7ee6023ece55",
 "wally_party_original_block": "856e7bb410eb846042d549ac50673e8fdb2cf9d135d4947b2c1d6baa30a55855",
 "wally_trainer_original_block": "0095e5b694c5472d59712368d6a217cfaf8d835fcba28757815938ec8cb9778d"
}
paths=[p for p in PREIMAGES if not p.startswith('wally_')]
old={p:(ROOT/p).read_bytes() for p in paths}
def patched(p,b):return (M+'_EventScript_TYWallyFinal' if p.endswith('/map.json') else MARK).encode() in b
if all(patched(p,old[p]) for p in paths):
 print(json.dumps({'pass':True,'already_applied':True,'writes':0}));raise SystemExit
assert not any(patched(p,old[p]) for p in paths),'partial Wally final patch'
for p in paths:assert sha(old[p])==PREIMAGES[p],('preimage changed',p,sha(old[p]))
# Names and trainer bits use existing allocations. No SaveBlock is resized.
op=(ROOT/'include/constants/opponents.h').read_text()
assert re.search(r'#define\s+TRAINER_HOENN_WALLY_MAUVILLE\s+\(HOENN_TRAINERS_START\s*\+\s*506\)',op)
assert T not in op and T not in old[paths[0]].decode()
assert not re.search(r'\(HOENN_TRAINERS_START\s*\+\s*538\)',op+'\n'+old['include/constants/opponents_hoenn_story.h'].decode())
assert 'TRAINER_CLASS_RIVAL_LATE' in (ROOT/'include/constants/trainers.h').read_text()
assert re.search(r'#define\s+OBJ_EVENT_GFX_WALLY\s+179\b',(ROOT/'include/constants/event_objects.h').read_text())
assert re.search(r'#define\s+HOENN_STORY_FLAGS_USED\s+113\b',(ROOT/'include/constants/flags_hoenn_story.h').read_text())
def initializer(source,tag):
 matches=list(re.finditer(re.escape(tag),source));assert len(matches)==1,(tag,len(matches))
 start=matches[0].start();n=source.index('{',start)+1;depth=1
 while depth:
  depth+=(source[n]=='{')-(source[n]=='}');n+=1
 while n<len(source) and source[n] in ' ;,\r\n':n+=1
 return source[start:n].rstrip()+'\n'
party=initializer(Path('/root/src/pokeemerald/src/data/trainer_parties.h').read_text(),
 'static const struct TrainerMonNoItemCustomMoves sParty_WallyVR1[]')
trainer=initializer(Path('/root/src/pokeemerald/src/data/trainers.h').read_text(),
 '[TRAINER_WALLY_VR_1] =')
assert sha(party.encode())==PREIMAGES['wally_party_original_block']
assert sha(trainer.encode())==PREIMAGES['wally_trainer_original_block']
assert re.findall(r'\.species\s*=\s*(\w+)',party)==[
 'SPECIES_ALTARIA','SPECIES_DELCATTY','SPECIES_ROSELIA','SPECIES_MAGNETON','SPECIES_GARDEVOIR']
assert re.findall(r'\.lvl\s*=\s*(\d+)',party)==['44','43','44','41','45']
party=party.replace('sParty_WallyVR1','sHoennParty_WallyVictoryRoadFinal')
trainer=trainer.replace('TRAINER_WALLY_VR_1',T).replace('TRAINER_CLASS_RIVAL,','TRAINER_CLASS_RIVAL_LATE,').replace('sParty_WallyVR1','sHoennParty_WallyVictoryRoadFinal')
updated={p:b.decode() for p,b in old.items()}
h='include/constants/opponents_hoenn_story.h'
tail='#endif  // GUARD_CONSTANTS_OPPONENTS_HOENN_STORY_H\n';assert updated[h].count(tail)==1
updated[h]=updated[h].replace(tail,'// '+MARK+'\n#define '+T+' (HOENN_TRAINERS_START + 538)\n'+tail)
updated['src/data/trainers_hoenn_story.h']+='\n// '+MARK+'\n    '+trainer
updated['src/data/trainer_parties_hoenn_story.h']+='\n// '+MARK+'\n'+party
map_path='data/maps/'+M+'/map.json';j=json.loads(updated[map_path])
original_objects=j['object_events'][:];original_warps=j['warp_events'][:]
assert len(original_objects)==7 and not j['coord_events']
assert not any((o['x'],o['y'])==(16,39) for o in original_objects+original_warps+j['bg_events'])
layout_path=ROOT/'data/layouts/HoennVictoryRoad_1F/map.bin'
terrain=layout_path.read_bytes()
assert sha(terrain)=='b100693756672442b3f583a8886950d07b68bac1b6eafe07a2b5fe721d1c484e'
assert struct.unpack_from('<H',terrain,2*(39*46+16))[0]==0x3201,'Wally tile/elevation changed'
j['object_events'].append({
 'type':'object','graphics_id':'OBJ_EVENT_GFX_WALLY','x':16,'y':39,'elevation':3,
 'movement_type':'MOVEMENT_TYPE_FACE_LEFT','movement_range_x':0,'movement_range_y':0,
 'trainer_type':'TRAINER_TYPE_NONE','trainer_sight_or_berry_tree_id':'0',
 'script':M+'_EventScript_TYWallyFinal','flag':'0'})
assert j['object_events'][:-1]==original_objects and j['warp_events']==original_warps
updated[map_path]=json.dumps(j,indent=2)+'\n'
script=r'''
@ THYL_WALLY_FINAL_V1: an optional native challenge; existing League gates stay intact.
HoennVictoryRoad_1F_EventScript_TYWallyFinal::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_LEAGUE_CLEAR, HoennVictoryRoad_1F_EventScript_TYWallyLegacy
	goto_if_unset FLAG_HOENN_BADGE08_GET, HoennVictoryRoad_1F_EventScript_TYWallyEarly
	goto_if_defeated TRAINER_HOENN_WALLY_VICTORY_ROAD_FINAL, HoennVictoryRoad_1F_EventScript_TYWallyPost
	goto_if_not_defeated TRAINER_HOENN_WALLY_MAUVILLE, HoennVictoryRoad_1F_EventScript_TYWallyFirstMeeting
	msgbox HoennVictoryRoad_1F_Text_TYWallyRemember, MSGBOX_YESNO
	goto HoennVictoryRoad_1F_EventScript_TYWallyAnswer

HoennVictoryRoad_1F_EventScript_TYWallyFirstMeeting::
	msgbox HoennVictoryRoad_1F_Text_TYWallyFirstMeeting, MSGBOX_YESNO

HoennVictoryRoad_1F_EventScript_TYWallyAnswer::
	goto_if_eq VAR_RESULT, NO, HoennVictoryRoad_1F_EventScript_TYWallyDeclined
	trainerbattle_single TRAINER_HOENN_WALLY_VICTORY_ROAD_FINAL, HoennVictoryRoad_1F_Text_TYWallyBattle, HoennVictoryRoad_1F_Text_TYWallyDefeat, HoennVictoryRoad_1F_EventScript_TYWallyFinish
	goto HoennVictoryRoad_1F_EventScript_TYWallyFinish

HoennVictoryRoad_1F_EventScript_TYWallyFinish::
	goto_if_not_defeated TRAINER_HOENN_WALLY_VICTORY_ROAD_FINAL, HoennVictoryRoad_1F_EventScript_TYWallyDone

HoennVictoryRoad_1F_EventScript_TYWallyPost::
	msgbox HoennVictoryRoad_1F_Text_TYWallyPost, MSGBOX_DEFAULT
	goto HoennVictoryRoad_1F_EventScript_TYWallyDone

HoennVictoryRoad_1F_EventScript_TYWallyLegacy::
	msgbox HoennVictoryRoad_1F_Text_TYWallyLegacy, MSGBOX_DEFAULT
	goto HoennVictoryRoad_1F_EventScript_TYWallyDone

HoennVictoryRoad_1F_EventScript_TYWallyEarly::
	msgbox HoennVictoryRoad_1F_Text_TYWallyEarly, MSGBOX_DEFAULT
	goto HoennVictoryRoad_1F_EventScript_TYWallyDone

HoennVictoryRoad_1F_EventScript_TYWallyDeclined::
	msgbox HoennVictoryRoad_1F_Text_TYWallyDeclined, MSGBOX_DEFAULT

HoennVictoryRoad_1F_EventScript_TYWallyDone::
	release
	end
'''
text=r'''
@ THYL_WALLY_FINAL_V1: branches do not invent a past battle for legacy saves.
HoennVictoryRoad_1F_Text_TYWallyRemember:
	.string "WALLY: Hi, {PLAYER}!\p"
	.string "After our battle in MAUVILLE, I kept\n"
	.string "training with my POKéMON.\p"
	.string "Now we've reached VICTORY ROAD!\n"
	.string "May I challenge you before the LEAGUE?$"

HoennVictoryRoad_1F_Text_TYWallyFirstMeeting:
	.string "WALLY: I'm WALLY, from VERDANTURF.\n"
	.string "My partners and I have come this far.\p"
	.string "The storm is over, and the path to\n"
	.string "the POKéMON LEAGUE is open again.\p"
	.string "May I challenge you before we go on?$"

HoennVictoryRoad_1F_Text_TYWallyBattle:
	.string "WALLY: I'm going to give this my all!\n"
	.string "For the POKéMON who gave me courage!$"

HoennVictoryRoad_1F_Text_TYWallyDefeat:
	.string "Wow!\n"
	.string "{PLAYER}, you are strong, after all!$"

HoennVictoryRoad_1F_Text_TYWallyPost:
	.string "WALLY: I couldn't beat you today,\n"
	.string "but I'll keep training with my team.\p"
	.string "One day, we'll challenge the LEAGUE,\n"
	.string "just like you!$"

HoennVictoryRoad_1F_Text_TYWallyLegacy:
	.string "WALLY: You've become HOENN's CHAMPION!\p"
	.string "I'm still training with my POKéMON.\n"
	.string "I'll keep working toward the LEAGUE!$"

HoennVictoryRoad_1F_Text_TYWallyEarly:
	.string "WALLY: Before you climb the waterfall,\n"
	.string "visit JUAN's GYM in SOOTOPOLIS.\p"
	.string "The RAINBADGE proves you're ready\n"
	.string "for this road and its strong TRAINERS.$"

HoennVictoryRoad_1F_Text_TYWallyDeclined:
	.string "WALLY: All right. I'll be training\n"
	.string "here when you're ready.$"
'''
updated['data/maps/'+M+'/scripts.inc']+=script
updated['data/maps/'+M+'/text.inc']+=text
for p,s in updated.items():assert patched(p,s.encode())
protected={p:sha(p.read_bytes()) for p in (ROOT/'saves').rglob('*.sav')}
receipt={'pass':True,'apply':a.apply,'trainer':T,'trainer_slot':538,
 'party_source':'original Emerald Wally VR1, exact levels/IV/moves/items',
 'new_save_flags':0,'save_layout_changes':0,'old_map_objects_preserved':True,
 'warps_preserved':True,'terrain_sha256':sha(terrain),
 'files':[{'path':p,'before':sha(old[p]),'after':sha(s.encode())} for p,s in updated.items()]}
if a.apply:
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 backup=ROOT/'work'/'backups'/('wally-final-v1-'+stamp)
 assert not backup.exists()
 for p,b in old.items():
  q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
 for p,s in updated.items():(ROOT/p).write_text(s)
 assert layout_path.read_bytes()==terrain
 assert protected=={p:sha(p.read_bytes()) for p in protected}
 receipt['backup']=str(backup)
print(json.dumps(receipt,indent=2))
