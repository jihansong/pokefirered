from pathlib import Path
import json,re,struct,hashlib,datetime,subprocess,argparse
parser=argparse.ArgumentParser();parser.add_argument('--root',default='/workspaces/pokefirered');parser.add_argument('--apply',action='store_true');args=parser.parse_args()
R=Path(args.root)
assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='hoenn-z3'
assert R.is_dir()
def sha(b):return hashlib.sha256(b).hexdigest()
names=['data/maps/VermilionCity/map.json','data/maps/VermilionCity/scripts.inc','data/maps/SSAnne_Exterior/map.json','data/maps/SSAnne_Exterior/scripts.inc','data/layouts/SSAnne_Exterior/map.bin']
original={p:(R/p).read_bytes() for p in names}
vc=json.loads(original[names[0]]);ss=json.loads(original[names[2]])
v=original[names[1]].decode().replace('\r\n','\n');s=original[names[3]].decode().replace('\r\n','\n')
if 'SSAnne_Exterior_EventScript_DockTruck::' in s:
 assert 'walk_in_place_normal_left' not in s,'Older invalid movement macro'
 assert 'seteventmon SPECIES_MEW, 30' in s,'Missing fateful encounter creation'
 proofs=[]
 for f in R.glob('.qa-dock-mew-*/manifest.json'):
  m=json.loads(f.read_text())
  if all(m.get('after',{}).get(p)==sha(b) for p,b in original.items()):proofs.append(str(f))
 assert proofs,'Installed files differ from dock backup manifest; inspect before overwrite'
 print(json.dumps({'changed':[],'already_applied':True,'verified_manifests':proofs,'runtime_qa':'NOT_ASSERTED'}));raise SystemExit(0)
assert sha(original[names[4]])=='41affa56fb4673824704a7e31e8006ec73c6b44b28f50daa3bb6c487ee0d76bc','Dock layout changed'
assert len(original[names[4]])==70*32*2
assert vc['object_events'][9]['local_id']=='LOCALID_VERMILION_TRUCK'
assert vc['object_events'][9]['graphics_id']=='OBJ_EVENT_GFX_TRUCK'
assert vc['object_events'][10]['local_id']=='LOCALID_VERMILION_MEW'
assert len(ss['object_events'])==1 and ss['object_events'][0]['local_id']=='LOCALID_SS_ANNE'
vc_other=json.dumps(vc['object_events'][:9]+vc['object_events'][10:],sort_keys=True)
vc['object_events'][9]['flag']='FLAG_HIDE_VERMILION_CITY_MEW';vc['object_events'][9]['movement_type']='MOVEMENT_TYPE_INVISIBLE';vc['object_events'][9]['script']='0x0'
assert vc_other==json.dumps(vc['object_events'][:9]+vc['object_events'][10:],sort_keys=True)
def one(text,old,new):
 assert text.count(old)==1,repr(old)
 return text.replace(old,new,1)
v=one(v,'VermilionCity_OnResume::\n','VermilionCity_OnResume::\n\t@ Keep legacy local IDs stable; hide the obsolete roadside truck on old saves too.\n\tsetflag FLAG_HIDE_VERMILION_CITY_MEW\n\tremoveobject LOCALID_VERMILION_TRUCK\n\tremoveobject LOCALID_VERMILION_MEW\n')
for direction,title in [('SOUTH','South'),('NORTH','North'),('WEST','West'),('EAST','East')]:v=one(v,'\tcall_if_eq VAR_VERMILION_CITY_TRUCK_PUSHED, DIR_'+direction+', VermilionCity_EventScript_TruckPushed'+title+'\n','')
a=v.index('VermilionCity_EventScript_TruckPushedSouth::');b=v.index('VermilionCity_EventScript_AirportSign::',a);legacy=v[a:b]
assert 'setwildbattle SPECIES_MEW, 30' in legacy and 'FLAG_GOT_MEW_EGG' in legacy
v=v[:a]+'@ The truck encounter now belongs to the original S.S. ANNE dock truck.\n\n'+v[b:]
ss['object_events'].append({'local_id':'LOCALID_SSANNE_DOCK_MEW','type':'object','graphics_id':'OBJ_EVENT_GFX_MEW','x':57,'y':3,'elevation':3,'movement_type':'MOVEMENT_TYPE_FACE_RIGHT','movement_range_x':0,'movement_range_y':0,'trainer_type':'TRAINER_TYPE_NONE','trainer_sight_or_berry_tree_id':'0','script':'0x0','flag':'FLAG_HIDE_VERMILION_CITY_MEW'})
ss['bg_events'].append({'type':'sign','x':57,'y':3,'elevation':3,'player_facing_dir':'BG_EVENT_PLAYER_FACING_WEST','script':'SSAnne_Exterior_EventScript_DockTruck'})
s=one(s,'\tmap_script MAP_SCRIPT_ON_FRAME_TABLE, SSAnne_Exterior_OnFrame\n','\tmap_script MAP_SCRIPT_ON_FRAME_TABLE, SSAnne_Exterior_OnFrame\n\tmap_script MAP_SCRIPT_ON_RESUME, SSAnne_Exterior_DockOnResume\n')
s=one(s,'SSAnne_Exterior_OnLoad::\n','SSAnne_Exterior_OnLoad::\n\tsetflag FLAG_HIDE_VERMILION_CITY_MEW\n\tcall_if_ne VAR_VERMILION_CITY_TRUCK_PUSHED, 0, SSAnne_Exterior_DockTruckShifted\n')
s=one(s,'SSAnne_Exterior_OnTransition::\n','SSAnne_Exterior_OnTransition::\n\tsetflag FLAG_HIDE_VERMILION_CITY_MEW\n')
blocks=[['DockOnResume','setflag FLAG_HIDE_VERMILION_CITY_MEW|removeobject LOCALID_SSANNE_DOCK_MEW|call_if_ne VAR_VERMILION_CITY_TRUCK_PUSHED, 0, @DockTruckShifted|end'],['EventScript_DockTruck','goto_if_questlog EventScript_ReleaseEnd|lockall|goto_if_set FLAG_GOT_MEW_EGG, @DockMewGone|goto_if_set FLAG_FOUGHT_MEW, @DockMewGone|goto_if_ne VAR_VERMILION_CITY_TRUCK_PUSHED, 0, @DockMewGone|goto_if_lt VAR_MAP_SCENE_VERMILION_CITY, 3, @DockTruckWontBudge|checkpartymove MOVE_STRENGTH|goto_if_eq VAR_RESULT, PARTY_SIZE, @DockTruckWontBudge|setfieldeffectargument 0, VAR_RESULT|msgbox VermilionCity_Text_TruckLooksHeavy, MSGBOX_YESNO|goto_if_eq VAR_RESULT, NO, @DockDeclined|closemessage|special QuestLog_CutRecording|dofieldeffect FLDEFF_USE_STRENGTH|waitstate|playse SE_M_STRENGTH|setvar VAR_0x8004, 0|setvar VAR_0x8005, 2|setvar VAR_0x8006, 8|setvar VAR_0x8007, 2|special ShakeScreen|applymovement LOCALID_PLAYER, @DockPushMovement|waitmovement 0|call @DockTruckShifted|special DrawWholeMapView|setvar VAR_VERMILION_CITY_TRUCK_PUSHED, DIR_WEST|delay 16|addobject LOCALID_SSANNE_DOCK_MEW|applymovement LOCALID_SSANNE_DOCK_MEW, @DockMewJump|waitmovement 0|applymovement LOCALID_SSANNE_DOCK_MEW, Common_Movement_ExclamationMark|waitmovement 0|waitse|playmoncry SPECIES_MEW, CRY_MODE_ENCOUNTER|waitmoncry|delay 20|setflag FLAG_FOUGHT_MEW|seteventmon SPECIES_MEW, 30|setflag FLAG_SYS_SPECIAL_WILD_BATTLE|special StartLegendaryBattle|waitstate|clearflag FLAG_SYS_SPECIAL_WILD_BATTLE|specialvar VAR_RESULT, GetBattleOutcome|goto_if_eq VAR_RESULT, B_OUTCOME_RAN, @DockMewFled|goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, @DockMewFled|goto_if_eq VAR_RESULT, B_OUTCOME_MON_FLED, @DockMewFled|fadescreen FADE_TO_BLACK|removeobject LOCALID_SSANNE_DOCK_MEW|fadescreen FADE_FROM_BLACK|releaseall|end'],['DockMewFled','fadescreen FADE_TO_BLACK|removeobject LOCALID_SSANNE_DOCK_MEW|fadescreen FADE_FROM_BLACK|bufferspeciesname STR_VAR_1, SPECIES_MEW|msgbox Text_MonFlewAway|releaseall|end'],['DockMewGone','msgbox VermilionCity_Text_TruckPinkHair|releaseall|end'],['DockTruckWontBudge','msgbox VermilionCity_Text_TruckWontBudge|releaseall|end'],['DockDeclined','closemessage|releaseall|end'],['DockPushMovement','walk_in_place_left|walk_in_place_left|step_end'],['DockMewJump','jump_in_place_right|step_end'],['DockTruckShifted','setmetatile 54, 1, 0x313, TRUE|setmetatile 55, 1, 0x314, TRUE|setmetatile 56, 1, 0x12B, TRUE|setmetatile 54, 2, 0x315, TRUE|setmetatile 55, 2, 0x316, TRUE|setmetatile 56, 2, 0x317, TRUE|setmetatile 57, 2, 0x31B, FALSE|setmetatile 54, 3, 0x318, TRUE|setmetatile 55, 3, 0x319, TRUE|setmetatile 56, 3, 0x31A, TRUE|setmetatile 57, 3, 0x1C1, FALSE|return']]
for label,commands in blocks:s+='\nSSAnne_Exterior_'+label+'::\n'+''.join('\t'+c.replace('@','SSAnne_Exterior_')+'\n' for c in commands.split('|'))
tile=bytearray(original[names[4]])
for y in (2,3):
 for x in (55,56,57):
  offset=(y*70+x)*2;old=struct.unpack_from('<H',tile,offset)[0]
  assert old>>12==0 and (old&0xC00)==0x400
  struct.pack_into('<H',tile,offset,(old&0xFFF)|0x3000)
changed={names[0]:(json.dumps(vc,indent=2)+'\n').encode(),names[1]:v.encode(),names[2]:(json.dumps(ss,indent=2)+'\n').encode(),names[3]:s.encode(),names[4]:bytes(tile)}
assert all((a&0xFFF)==(b&0xFFF) for (a,),(b,) in zip(struct.iter_unpack('<H',original[names[4]]),struct.iter_unpack('<H',changed[names[4]])))
assert vc['object_events'][10]['script']=='0x0'
assert (vc['object_events'][9]['x'],vc['object_events'][9]['y'])==(27,29)
assert not any(e.get('x')==57 and e.get('y')==3 for e in json.loads(original[names[2]])['bg_events'])
assert re.search(r'create_movement_action\s+walk_in_place_left,',(R/'asm/macros/movement.inc').read_text())
assert re.search(r'\.macro\s+seteventmon\b',(R/'asm/macros/event.inc').read_text())
for data in (v,s):
 labels=re.findall(r'^(\w+)::?',data,re.M);assert len(labels)==len(set(labels))
for label in re.findall(r'^(VermilionCity_\w+)::',legacy,re.M):assert not re.search(r'\b'+re.escape(label)+r'\b',v+s),'Legacy label still referenced'
for label in ('TruckLooksHeavy','TruckPinkHair','TruckWontBudge'):assert 'VermilionCity_Text_'+label+'::' in (R/'data/maps/VermilionCity/text.inc').read_text()
report={'before':{p:sha(b) for p,b in original.items()},'after':{p:sha(b) for p,b in changed.items()},'save_layout_changed':False,'truck_pixels_preserved':True,'runtime_qa':'NOT_RUN'}
if not args.apply:print(json.dumps({'preflight':'PASS',**report},indent=2));raise SystemExit(0)
assert all((R/p).read_bytes()==b for p,b in original.items()),'Concurrent source change'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup=R/('.qa-dock-mew-'+stamp);backup.mkdir(exist_ok=False)
for p,b in original.items():q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
manifest={'utc':stamp,'branch':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'before':{p:sha(b) for p,b in original.items()},'after':{p:sha(b) for p,b in changed.items()},'save_layout_changes':False,'requires_runtime_qa':True}
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for p,b in changed.items():(R/p).write_bytes(b)
print(json.dumps({'applied':list(changed),'backup':str(backup),'after':manifest['after']},indent=2))
