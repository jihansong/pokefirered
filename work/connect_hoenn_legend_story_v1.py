#!/usr/bin/env python3
"""Connect the native Seafloor/Sootopolis/Sky Pillar chapter; keep save layouts."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,sys
r=Path.cwd();p=r/'tools/hoenn_import/patches'
maps=['SeafloorCavern_Room9','SootopolisCity','SkyPillar_Top','SootopolisCity_Gym_1F']
first='FLAG_HOENN_SEAFLOOR_CLEARED';second='FLAG_HOENN_RAYQUAZA_AWAKENED'
pending={};originals=set();terrain={}
def sha(b):return hashlib.sha256(b).hexdigest()
def append(name,kind,block):
 f=p/(name+'.'+kind);old=f.read_text() if f.exists() else ''
 assert '@ Thunder Yellow Hoenn sea-sky chapter v1' not in old,('already applied',f)
 pending[f]=(old.rstrip()+'\n\n@ Thunder Yellow Hoenn sea-sky chapter v1\n'+block).lstrip('\n')
 originals.add(f)
def obj(gfx,x,y,el,move,script,flag):
 return dict(type='object',graphics_id=gfx,x=x,y=y,elevation=el,movement_type=move,
             movement_range_x=0,movement_range_y=0,trainer_type='TRAINER_TYPE_NONE',
             trainer_sight_or_berry_tree_id='0',script=script,flag=flag)
def append_objects(name,objects):
 f=p/(name+'.json');extra=json.loads(f.read_text()) if f.exists() else {}
 current=json.loads((r/'data/maps'/name/'map.json').read_text())
 scripts={o['script'] for o in objects}
 assert not scripts.intersection(o.get('script') for o in current['object_events'])
 assert not scripts.intersection(o.get('script') for o in extra.get('object_events',[]))
 extra['object_events']=extra.get('object_events',[])+objects
 pending[f]=json.dumps(extra,indent=2)+'\n';originals.add(f)
 # apply_patches de-duplicates existing canonical object lists before appending.
 remaining=[o for o in current['object_events'] if o.get('script') not in
            {o['script'] for o in extra['object_events']}]
 ids={o['script']:i+1 for i,o in enumerate(remaining+extra['object_events'])}
 for o in objects:
  assert not any((a['x'],a['y'])==(o['x'],o['y']) for a in current['object_events'])
 assert len(remaining+extra['object_events'])<=14,('NPC slots including follower',name)
 return ids
layouts={z['id']:z for z in json.loads((r/'data/layouts/layouts.json').read_text())['layouts'] if z.get('id')}
for name,expected in [
 ('SeafloorCavern_Room9','1a4ea2ca4afc9d6b4b2fee1d4304cf7eb653a36cf8984d6b082732b618604cb3'),
 ('SootopolisCity','620c9c896617640b73595ea98d32d68b8eb0e850ea681c7b2f51f30b8f43fe49'),
 ('SkyPillar_Top','80bbe44563def5477c420586c2fa94e7657aae25903729ba4de12cedc208b577')]:
 md=json.loads((r/'data/maps'/name/'map.json').read_text());l=layouts[md['layout']]
 f=r/l['blockdata_filepath'];b=f.read_bytes()
 assert sha(b)==expected,('terrain changed',name)
 terrain[str(f.relative_to(r))]=expected
 def cell(x,y):return int.from_bytes(b[2*(y*l['width']+x):2*(y*l['width']+x)+2],'little')
 coords={'SeafloorCavern_Room9':[(13,42,0x3211),(14,42,0x3223),(17,39,0x1170)],
  'SootopolisCity':[(28,33,0x3001),(28,34,0x3001)],
  'SkyPillar_Top':[(13,9,0x3234)]}[name]
 for x,y,w in coords:assert cell(x,y)==w,(name,x,y,hex(cell(x,y)),hex(w))
for name in maps:
 for filename in ['map.json','scripts.inc','text.inc']:originals.add(r/'data/maps'/name/filename)
flags=r/'include/constants/flags_hoenn_story.h';fs=flags.read_text()
assert first not in fs and second not in fs
assert not re.search(r'HOENN_STORY_FLAGS_START\s*\+\s*11[01]\s*\)',fs),'flag slot used'
used=re.search(r'#define HOENN_STORY_FLAGS_USED\s+(\d+)',fs)
assert used and int(used.group(1))==110,('unexpected current Hoenn flags',used.group(0) if used else None)
fs=fs[:used.start()]+fs[used.start():].replace(used.group(0),
 '#define '+first+' (HOENN_STORY_FLAGS_START + 110)\n'
 '#define '+second+' (HOENN_STORY_FLAGS_START + 111)\n\n#define HOENN_STORY_FLAGS_USED 112',1)
pending[flags]=fs;originals.add(flags)
# Genuine native frames must be imported first, rather than recolored placeholders.
gi=(r/'src/data/object_events/object_event_graphics_info.h').read_text()
for kind in ['Kyogre','Rayquaza']:
 body=re.search(r'const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_'+kind+r'\s*=\s*\{(.*?)\};',gi,re.S)
 assert body and '.images = sPicTable_ThunderLegend' in body.group(1),('original legend frames absent',kind)
room='SeafloorCavern_Room9';archie=room+'_EventScript_TY_Archie';ky=room+'_EventScript_TY_Kyogre'
ids=append_objects(room,[
 obj('OBJ_EVENT_GFX_ARCHIE',14,42,3,'MOVEMENT_TYPE_FACE_LEFT',archie,first),
 obj('OBJ_EVENT_GFX_KYOGRE',17,39,1,'MOVEMENT_TYPE_FACE_DOWN',ky,first)])
archid=ids[archie];kyid=ids[ky]
append(room,'scripts.inc',f"""{archie}::
	goto_if_questlog EventScript_ReleaseEnd
	goto_if_set {first}, {room}_TY_Done
	goto_if_unset FLAG_HOENN_SPACE_CENTER_SECURED, {room}_TY_NotReady
	goto_if_unset FLAG_HOENN_BADGE07_GET, {room}_TY_NotReady
	goto_if_defeated TRAINER_HOENN_ARCHIE, {room}_TY_AfterBattle
	trainerbattle_single TRAINER_HOENN_ARCHIE, {room}_Text_TY_Intro, {room}_Text_TY_Defeat, {room}_TY_AfterBattle
	goto {room}_TY_AfterBattle

{room}_TY_AfterBattle::
	lockall
	msgbox {room}_Text_TY_Awake, MSGBOX_DEFAULT
	playmoncry SPECIES_KYOGRE, CRY_MODE_NORMAL
	waitmoncry
	applymovement {kyid}, {room}_Movement_TY_Escape
	waitmovement 0
	removeobject {kyid}
	msgbox {room}_Text_TY_Storm, MSGBOX_DEFAULT
	setflag {first}
	removeobject {archid}
	releaseall
	end

{room}_TY_NotReady::
	msgbox {room}_Text_TY_NotReady, MSGBOX_NPC
	end

{room}_TY_Done::
	end

{ky}::
	goto_if_questlog EventScript_ReleaseEnd
	msgbox {room}_Text_TY_Sleep, MSGBOX_NPC
	end

{room}_Movement_TY_Escape::
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end
""")
append(room,'text.inc',f"""{room}_Text_TY_Intro::
	.string "ARCHIE: Back at the museum,\\n"
	.string "you defied TEAM AQUA.\\p"
	.string "Now the ancient sea POKEMON\\n"
	.string "will reshape these waters!$"

{room}_Text_TY_Defeat::
	.string "Even here, you stop me...$"

{room}_Text_TY_Awake::
	.string "ARCHIE: The cavern is shaking!\\n"
	.string "KYOGRE is waking up!$"

{room}_Text_TY_Storm::
	.string "ARCHIE: KYOGRE escaped!\\n"
	.string "That storm is beyond control.\\p"
	.string "The seas link HOENN, JOHTO,\\n"
	.string "and KANTO. All coasts are at risk.\\p"
	.string "Go to SOOTOPOLIS. WALLACE\\n"
	.string "studies the ancient legends.$"

{room}_Text_TY_NotReady::
	.string "Finish helping STEVEN at\\n"
	.string "MOSSDEEP's SPACE CENTER first.\\p"
	.string "You'll need the MIND BADGE\\n"
	.string "to investigate these waters.$"

{room}_Text_TY_Sleep::
	.string "An ancient POKEMON sleeps\\n"
	.string "beneath the cavern's still waters.$"
""")
city='SootopolisCity';wallace=city+'_EventScript_TY_Wallace'
append_objects(city,[obj('OBJ_EVENT_GFX_WALLACE',28,33,3,'MOVEMENT_TYPE_FACE_DOWN',wallace,'0')])
append(city,'scripts.inc',f"""{city}_OnTransition::
	setflag FLAG_HOENN_WORLD_MAP_SOOTOPOLIS_CITY
	goto_if_set FLAG_HOENN_BADGE08_GET, {city}_TY_Calm
	goto_if_unset {first}, {city}_TY_Calm
	goto_if_set {second}, {city}_TY_Calm
	setweather WEATHER_RAIN_THUNDERSTORM
	doweather
	end

{city}_TY_Calm::
	setweather WEATHER_SUNNY
	doweather
	end

{wallace}::
	goto_if_set FLAG_HOENN_BADGE08_GET, {city}_TY_WallaceLegacy
	goto_if_set {second}, {city}_TY_WallaceCalm
	goto_if_set {first}, {city}_TY_WallaceStorm
	msgbox {city}_Text_TY_WallaceBefore, MSGBOX_NPC
	end

{city}_TY_WallaceStorm::
	msgbox {city}_Text_TY_WallaceStorm, MSGBOX_NPC
	end

{city}_TY_WallaceCalm::
	msgbox {city}_Text_TY_WallaceCalm, MSGBOX_NPC
	end

{city}_TY_WallaceLegacy::
	msgbox {city}_Text_TY_WallaceLegacy, MSGBOX_NPC
	end
""")
append(city,'text.inc',f"""{city}_Text_TY_WallaceBefore::
	.string "WALLACE: I study how our sea\\n"
	.string "and sky legends keep balance.\\p"
	.string "STEVEN is investigating TEAM\\n"
	.string "AQUA's activity near ROUTE 128.\\p"
	.string "Help him at MOSSDEEP, then\\n"
	.string "explore SEAFLOOR CAVERN.$"

{city}_Text_TY_WallaceStorm::
	.string "WALLACE: KYOGRE's storm is\\n"
	.string "spreading beyond HOENN.\\p"
	.string "The legend of RAYQUAZA speaks\\n"
	.string "of restoring the sea and sky.\\p"
	.string "SKY PILLAR rises near ROUTE 131.\\n"
	.string "Awaken RAYQUAZA at its summit.$"

{city}_Text_TY_WallaceCalm::
	.string "WALLACE: The storm has ended!\\n"
	.string "RAYQUAZA restored the balance.\\p"
	.string "JUAN can resume your GYM test.\\n"
	.string "Thank you for protecting our sea.$"

{city}_Text_TY_WallaceLegacy::
	.string "WALLACE: You already earned\\n"
	.string "JUAN's RAIN BADGE.\\p"
	.string "Your earlier journey stands.\\n"
	.string "The GYM remains open to you.$"
""")
sky='SkyPillar_Top';ray=sky+'_EventScript_TY_Rayquaza'
ids=append_objects(sky,[obj('OBJ_EVENT_GFX_RAYQUAZA',13,9,3,'MOVEMENT_TYPE_FACE_DOWN',ray,second)])
rayid=ids[ray]
append(sky,'scripts.inc',f"""{ray}::
	goto_if_questlog EventScript_ReleaseEnd
	goto_if_set {second}, {sky}_TY_Done
	goto_if_set FLAG_HOENN_BADGE08_GET, {sky}_TY_Wake
	goto_if_unset {first}, {sky}_TY_Sleep
{sky}_TY_Wake::
	lockall
	msgbox {sky}_Text_TY_Wake, MSGBOX_DEFAULT
	applymovement {rayid}, {sky}_Movement_TY_Awake
	waitmovement 0
	playmoncry SPECIES_RAYQUAZA, CRY_MODE_NORMAL
	waitmoncry
	applymovement {rayid}, {sky}_Movement_TY_Call
	waitmovement 0
	delay 30
	applymovement {rayid}, {sky}_Movement_TY_Rise
	waitmovement 0
	removeobject {rayid}
	setflag {second}
	msgbox {sky}_Text_TY_After, MSGBOX_DEFAULT
	releaseall
	end

{sky}_TY_Sleep::
	msgbox {sky}_Text_TY_Sleep, MSGBOX_NPC
	end

{sky}_TY_Done::
	end

{sky}_Movement_TY_Awake::
	walk_in_place_fast_left
	step_end

{sky}_Movement_TY_Call::
	walk_in_place_left
	step_end

{sky}_Movement_TY_Rise::
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end
""")
append(sky,'text.inc',f"""{sky}_Text_TY_Sleep::
	.string "RAYQUAZA is sleeping.\\n"
	.string "WALLACE may know its legend.$"

{sky}_Text_TY_Wake::
	.string "The sea and sky are unsettled.\\n"
	.string "RAYQUAZA opens its eyes!$"

{sky}_Text_TY_After::
	.string "RAYQUAZA flies toward the storm!\\p"
	.string "Return to WALLACE in SOOTOPOLIS\\n"
	.string "and check whether the sea is calm.$"
""")
gym='SootopolisCity_Gym_1F';gs=(r/'data/maps'/gym/'scripts.inc').read_text()
h0=gym+'_EventScript_H0';boss=gym+'_TY_Boss'
h0old=re.search(r'^'+h0+r'::\n(?:[ \t].*\n)+',gs,re.M)
assert h0old and h0old.group(0)==h0+'::\n\tgoto '+boss+'\n',('unexpected Juan entry',h0old.group(0) if h0old else None)
rewards={label:body for label,body in re.findall(r'^('+gym+r'_TY_\w+)::\n((?:[ \t].*\n)+)',gs,re.M)}
assert boss in rewards and any('ITEM_TM03' in b for b in rewards.values())
f=p/(gym+'.scripts.inc');old=f.read_text() if f.exists() else ''
newentry=f"""{h0}::
	goto_if_set FLAG_HOENN_BADGE08_GET, {boss}
	goto_if_set {second}, {boss}
	msgbox {gym}_Text_TY_StormGate, MSGBOX_NPC
	end
"""
if h0+'::' in old:
 old,n=re.subn(r'^'+h0+r'::\n(?:[ \t].*\n)+\n?',lambda m:newentry+'\n',old,flags=re.M)
 assert n==1
else:old=old.rstrip()+'\n\n'+newentry
pending[f]=(old.rstrip()+'\n\n@ Thunder Yellow Hoenn sea-sky chapter v1\n').lstrip('\n');originals.add(f)
append(gym,'text.inc',f"""{gym}_Text_TY_StormGate::
	.string "JUAN: This storm endangers\\n"
	.string "SOOTOPOLIS and the distant coasts.\\p"
	.string "Speak to WALLACE outside the GYM.\\n"
	.string "The test must wait until it's calm.$"
""")
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=r/'work/hoenn-sea-sky-v1-backups'/stamp
manifest={}
for f in originals:
 key=str(f.relative_to(r))
 manifest[key]=sha(f.read_bytes()) if f.exists() else None
 if f.exists():
  target=backup/key;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
backup.mkdir(parents=True,exist_ok=True)
for f,txt in pending.items():f.parent.mkdir(parents=True,exist_ok=True);f.write_text(txt,encoding='utf-8')
subprocess.run([sys.executable,'tools/hoenn_import/apply_patches.py']+maps,check=True)
for f,h in terrain.items():assert sha((r/f).read_bytes())==h,f
after=(r/'data/maps'/gym/'scripts.inc').read_text()
for label,body in rewards.items():assert label+'::\n'+body in after,('Juan reward path changed',label)
for name in maps:
 generated=(r/'data/maps'/name/'scripts.inc').read_text()
 labels=re.findall(r'^(\w+)::',generated,re.M)
 assert len(labels)==len(set(labels)),('duplicate map label',name)
receipt={'chapter':'Seafloor Archie -> Sootopolis storm -> Sky Pillar -> Juan',
 'new_flags':[first,second],'terrain_unchanged':True,'juan_reward_paths_unchanged':True,
 'legacy_rain_badge_bypass':True,'native_runtime_validated':False,'save_layout_changed':False,
 'original_files':manifest,'canonical_files':{str(f.relative_to(r)):sha(f.read_bytes()) for f in pending}}
(backup/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'backup':str(backup),'maps':maps,'runtime_validated':False}))
