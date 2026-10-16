#!/usr/bin/env python3
"""Restore the original Route119 Aqua bridge blockade after the native rival patch."""
import argparse,datetime,hashlib,json,re,subprocess
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--apply',action='store_true');a=P.parse_args()
R=Path.cwd();sha=lambda b:hashlib.sha256(b).hexdigest()
M='Route119';MARK='TY_HOENN_WEATHER_BRIDGE_V1'
END='@ END PATCH\n'
MAP_SHA='48eb38d968e0c1dbab7bb1eff0ed89304e2d02b26e74f7106cec4f2a499939b1'
SCRIPT_SHA='5df47a91199555d0bc6ee6c5c5ff3216162cd606c066d95e133e19cb4e7074f0'
TERRAIN_SHA='f6c948a0fb90925afce408b4bf1742ba56e9e6c95ffb899a348d563d1ba5f47d'
C_ANCHOR="    if (IsPlayerOnMap(MAP_ROUTE103) || IsPlayerOnMap(MAP_LITTLEROOT_TOWN_PROFESSOR_BIRCHS_LAB)\n        || IsPlayerOnMap(MAP_ROUTE110) || IsPlayerOnMap(MAP_ROUTE119))\n        VarSet(VAR_OBJ_GFX_ID_0, GetHoennRivalGfx());\n\n    // These map-local flags are reset by normal map loading; only the current\n    // chapter owns TEMP_11 / TEMP_0. No saved coordinates or save layout change.\n    if (IsPlayerOnMap(MAP_ROUTE110))\n    {\n        bool8 hidden = birch < 3 || FlagGet(FLAG_HOENN_GOT_RIVAL110_GIFT);\n        SetHideFlag(FLAG_TEMP_11, hidden);\n        VarSet(VAR_TEMP_0, hidden ? 1 : 0);\n    }\n    else if (IsPlayerOnMap(MAP_ROUTE119))\n    {\n        bool8 earlierBattle = gSaveBlock2Ptr->playerGender == FEMALE\n            ? HasTrainerBeenFought(TRAINER_HOENN_BRENDAN_ROUTE_110_TORCHIC)\n            : HasTrainerBeenFought(TRAINER_HOENN_MAY_ROUTE_110_TORCHIC);\n        bool8 hidden = birch < 3\n            || !FlagGet(FLAG_HOENN_GOT_RIVAL110_GIFT)\n            || !earlierBattle\n            || !FlagGet(FLAG_HOENN_WEATHER_RESCUED)\n            || FlagGet(FLAG_HOENN_GOT_RIVAL_FLY_REWARD);\n        SetHideFlag(FLAG_TEMP_11, hidden);\n        VarSet(VAR_TEMP_0, hidden ? 1 : 0);\n    }"
C_ADD="    // Restore the original two Aqua bridge lookouts without trapping\n    // earlier saves whose Fortree Gym progression is already complete.\n    if (IsPlayerOnMap(MAP_ROUTE119))\n    {\n        bool8 bridgeClear = FlagGet(FLAG_HOENN_WEATHER_RESCUED)\n            || FlagGet(FLAG_HOENN_BADGE06_GET)\n            || HasTrainerBeenFought(TRAINER_HOENN_WINONA_1);\n        SetHideFlag(FLAG_TEMP_12, bridgeClear);\n        SetHideFlag(FLAG_TEMP_13, bridgeClear);\n    }\n"
SCRIPT='''@ TY_HOENN_WEATHER_BRIDGE_V1
Route119_TYWeather_BridgeGuard1::
\tmsgbox Route119_TYWeather_BlockadeText1, MSGBOX_NPC
\tend

Route119_TYWeather_BridgeGuard2::
\tmsgbox Route119_TYWeather_BlockadeText2, MSGBOX_NPC
\tend

'''
TEXT='''Route119_TYWeather_BlockadeText1::
\t.string "TEAM AQUA: The bridge is closed.\\p"
\t.string "Our crew is working inside the\\n"
\t.string "WEATHER INSTITUTE. Stay back!$"

Route119_TYWeather_BlockadeText2::
\t.string "TEAM AQUA: No crossing this bridge!\\p"
\t.string "Don't interfere with our research\\n"
\t.string "at the WEATHER INSTITUTE!$"

'''
guards=[]
for i,y in enumerate((33,34),1):
 guards.append({'type':'object','graphics_id':'OBJ_EVENT_GFX_AQUA_MEMBER_M','x':13,'y':y,
  'elevation':4,'movement_type':'MOVEMENT_TYPE_FACE_RIGHT','movement_range_x':0,
  'movement_range_y':0,'trainer_type':'TRAINER_TYPE_NONE','trainer_sight_or_berry_tree_id':'0',
  'script':M+'_TYWeather_BridgeGuard'+str(i),'flag':'FLAG_TEMP_'+str(11+i)})
paths=['src/field_specials.c','data/maps/Route119/map.json','tools/hoenn_import/patches/Route119.json',
 'data/maps/Route119/scripts.inc','tools/hoenn_import/patches/Route119.scripts.inc',
 'data/maps/Route119/text.inc','tools/hoenn_import/patches/Route119.text.inc']
assert subprocess.check_output(['git','branch','--show-current'],text=True).strip()=='hoenn-z3'
before={p:(R/p).read_bytes() for p in paths};out={}
terrain=R/'data/layouts/HoennRoute119/map.bin';terrain_before=terrain.read_bytes()
assert sha(terrain_before)==TERRAIN_SHA
saves={str(p):sha(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}
c=before[paths[0]].decode()
assert c.count(C_ANCHOR)==1,'native rival controller must be installed first'
if C_ADD not in c:
 assert 'bool8 bridgeClear' not in c,'partial bridge controller'
 c=c.replace(C_ANCHOR,C_ANCHOR+'\n'+C_ADD,1)
else:assert c.count(C_ADD)==1
out[paths[0]]=c.encode()
j=json.loads(before[paths[1]]);oldj=json.loads(before[paths[1]])
own=[o for o in j['object_events'] if o.get('script','').startswith(M+'_TYWeather_')]
if not own:
 assert sha(before[paths[1]])==MAP_SHA and len(j['object_events'])==30,'Route119 post-rival map preimage changed'
 assert j['object_events'][29]['script']=='Route119_TYRival_Interact'
 assert not any(o['flag'] in ('FLAG_TEMP_12','FLAG_TEMP_13') for o in j['object_events'])
 assert not any((o['x'],o['y']) in ((13,33),(13,34)) for o in j['object_events'])
 j['object_events']+=guards
else:
 assert own==guards and j['object_events'][-2:]==guards and len(j['object_events'])==32,'partial or reordered bridge objects'
assert j['object_events'][:30]==oldj['object_events'][:30]
assert all(j[k]==oldj[k] for k in oldj if k!='object_events'),'terrain/header/warps/events changed'
assert len(j['object_events'])<=64
out[paths[1]]=(json.dumps(j,indent=2,ensure_ascii=False)+'\n').encode()
patch=json.loads(before[paths[2]]);oldpatch=json.loads(before[paths[2]])
patchown=[o for o in patch.get('object_events',[]) if o.get('script','').startswith(M+'_TYWeather_')]
if not patchown:
 patch.setdefault('object_events',[]).extend(guards)
else:assert patchown==guards
assert all(patch[k]==oldpatch[k] for k in oldpatch if k!='object_events')
assert patch['object_events'][:len(oldpatch.get('object_events',[]))]==oldpatch.get('object_events',[])
out[paths[2]]=(json.dumps(patch,indent=2,ensure_ascii=False)+'\n').encode()
for canonical,mirror,payload in [(paths[3],paths[4],SCRIPT),(paths[5],paths[6],TEXT)]:
 s=before[canonical].decode();x=before[mirror].decode()
 if payload not in s:
  assert not re.search(r'^'+M+r'_TYWeather_\w+::',s,re.M),'partial canonical blockade'
  if payload==SCRIPT:assert sha(before[canonical])==SCRIPT_SHA and '.equ LOCALID_ROUTE119_TY_RIVAL, 30' in s
  assert s.count(END)==1,'expected existing patch enclosure'
  s=s.replace(END,payload+END,1)
 else:assert s.count(payload)==1
 if payload not in x:
  assert not re.search(r'^'+M+r'_TYWeather_\w+::',x,re.M),'partial mirror blockade'
  assert '@ TY_HOENN_RIVAL_110_119_V1' in x if payload==SCRIPT else 'Route119_TYRival_MayIntro::' in x
  x=x.rstrip()+'\n\n'+payload
 else:assert x.count(payload)==1
 out[canonical]=s.encode();out[mirror]=x.encode()
for label in re.findall(r'^(\w+)::',SCRIPT+TEXT,re.M):
 assert out[paths[3]].decode().count(label+'::')+out[paths[5]].decode().count(label+'::')==1
fh=(R/'include/constants/flags_hoenn_story.h').read_text();th=(R/'include/constants/opponents.h').read_text()
for name in ('FLAG_HOENN_WEATHER_RESCUED','FLAG_HOENN_BADGE06_GET'):
 assert re.search(r'^#define\s+'+name+r'\b',fh,re.M)
# Native importer uses a dedicated opponents header included from opponents.h.
trainer_headers=[th]+[p.read_text() for p in (R/'include/constants').glob('*hoenn*.h')]
assert any(re.search(r'^#define\s+TRAINER_HOENN_WINONA_1\b',h,re.M) for h in trainer_headers)
gfx=(R/'include/constants/event_objects.h').read_text()
assert re.search(r'^#define\s+OBJ_EVENT_GFX_AQUA_MEMBER_M\s+171\b',gfx,re.M)
assert not re.search(r'^\s*(?:setflag|clearflag|settrainerflag|setvar)\b',SCRIPT,re.M)
changed={p:b for p,b in out.items() if b!=before[p]}
receipt={'apply':a.apply,'scope':'original Route119 bridge guards only; rival generation required',
 'native_cases':'NOT_RUN','save_layout_changed':False,'persistent_flags_added':0,
 'guard_local_ids':[31,32],'original_route_objects_kept':30,
 'bridge_clear_condition':'Weather rescued OR existing Hoenn badge6 OR actual Winona victory',
 'legacy_completed_progress_rewritten':False,'original_terrain_sha256':sha(terrain_before),
 'files':{p:{'before':sha(before[p]),'after':sha(out[p])} for p in out},
 'changed':list(changed),'original_save_sha256':saves}
if a.apply and changed:
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=R/'work/backups'/('hoenn-weather-bridge-v1-'+stamp)
 for p,b in before.items():assert (R/p).read_bytes()==b,('concurrent source edit',p)
 for p in changed:
  q=dest/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[p])
 for p,b in changed.items():q=R/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
 receipt['backup']=str(dest.relative_to(R))
assert terrain.read_bytes()==terrain_before
assert {str(p):sha(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}==saves
print(json.dumps(receipt,indent=2))
