#!/usr/bin/env python3
"""Hoenn HM03/04/05 rewards follow actual chapter prerequisites, sharing existing HMs."""
import argparse,datetime,hashlib,json,re,subprocess
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--apply',action='store_true');a=P.parse_args()
R=Path.cwd();sha=lambda b:hashlib.sha256(b).hexdigest()
ROWS=[{"map":"VerdanturfTown_WandasHouse","hm":"ITEM_HM04","tm":"ITEM_TM26","history":"FLAG_GOT_HM04","receipt":"FLAG_HOENN_GOT_WANDA_SHARED_HM_REWARD","oldsha":"aebf2e0bbca2d92cea53aff574ba3db8a48cba0a2a383fe8f32abde2e2d533fa","mapsha":"f8ce862cea5198965209c2d686760dca43e916114941f43d7ce64f219b0b21d9","target":"VerdanturfTown_WandasHouse_EventScript_ReunionDone","old":"VerdanturfTown_WandasHouse_EventScript_ReunionDone::\n\trelease\n\tend\n","npcScript":"VerdanturfTown_WandasHouse_EventScript_Wanda","npc":[6,4],"layout":"HoennVerdanturfTown_WandasHouse","terrain":"cfc9d2a0923025f21d5feacbdbd0665f10bb781a34b9ed17f28ee7f9e918f738","script":"VerdanturfTown_WandasHouse_EventScript_ReunionDone::\n\tgoto_if_unset FLAG_HOENN_RUSTURF_OPEN, VerdanturfTown_WandasHouse_TYSharedHM_Done\n\tgoto_if_set FLAG_HOENN_GOT_WANDA_SHARED_HM_REWARD, VerdanturfTown_WandasHouse_TYSharedHM_Done\n\tgoto_if_set FLAG_GOT_HM04, VerdanturfTown_WandasHouse_TYSharedHM_Known\n\tcheckitem ITEM_HM04\n\tgoto_if_eq VAR_RESULT, TRUE, VerdanturfTown_WandasHouse_TYSharedHM_Known\n\tcheckpcitem ITEM_HM04\n\tgoto_if_eq VAR_RESULT, TRUE, VerdanturfTown_WandasHouse_TYSharedHM_Known\n\tmsgbox VerdanturfTown_WandasHouse_TYSharedHM_FreshText\n\tcheckitemspace ITEM_HM04\n\tgoto_if_eq VAR_RESULT, FALSE, VerdanturfTown_WandasHouse_TYSharedHM_Full\n\tgiveitem ITEM_HM04\n\tgoto_if_eq VAR_RESULT, FALSE, VerdanturfTown_WandasHouse_TYSharedHM_Full\n\tsetflag FLAG_HOENN_GOT_WANDA_SHARED_HM_REWARD\n\tmsgbox VerdanturfTown_WandasHouse_TYSharedHM_FreshThanks\n\trelease\n\tend\n\nVerdanturfTown_WandasHouse_TYSharedHM_Known::\n\tmsgbox VerdanturfTown_WandasHouse_TYSharedHM_KnownText\n\tcheckitemspace ITEM_TM26\n\tgoto_if_eq VAR_RESULT, FALSE, VerdanturfTown_WandasHouse_TYSharedHM_Full\n\tgiveitem ITEM_TM26\n\tgoto_if_eq VAR_RESULT, FALSE, VerdanturfTown_WandasHouse_TYSharedHM_Full\n\tsetflag FLAG_HOENN_GOT_WANDA_SHARED_HM_REWARD\n\tmsgbox VerdanturfTown_WandasHouse_TYSharedHM_TechniqueText\n\trelease\n\tend\n\nVerdanturfTown_WandasHouse_TYSharedHM_Full::\n\tmsgbox VerdanturfTown_WandasHouse_TYSharedHM_FullText\n\trelease\n\tend\n\nVerdanturfTown_WandasHouse_TYSharedHM_Done::\n\trelease\n\tend\n","text":"VerdanturfTown_WandasHouse_TYSharedHM_FreshText::\n\t.string \"Thanks to you, the tunnel is open.\\p\"\n\t.string \"My partner left this HM for you.\\n\"\n\t.string \"It teaches STRENGTH.$\"\n\nVerdanturfTown_WandasHouse_TYSharedHM_FreshThanks::\n\t.string \"With FLANNERY's BADGE, you can\\n\"\n\t.string \"use STRENGTH on HOENN boulders.$\"\n\nVerdanturfTown_WandasHouse_TYSharedHM_KnownText::\n\t.string \"You already have STRENGTH.\\p\"\n\t.string \"The same HM works across regions.\\n\"\n\t.string \"Take this different technique.$\"\n\nVerdanturfTown_WandasHouse_TYSharedHM_TechniqueText::\n\t.string \"The TM teaches EARTHQUAKE.\\n\"\n\t.string \"Put it to good use in HOENN!$\"\n\nVerdanturfTown_WandasHouse_TYSharedHM_FullText::\n\t.string \"Your BAG has no room.\\p\"\n\t.string \"Make some space, then return.\\n\"\n\t.string \"I will keep your reward ready.$\"\n"},{"map":"PetalburgCity_WallysHouse","hm":"ITEM_HM03","tm":"ITEM_TM13","history":"FLAG_GOT_HM03","receipt":"FLAG_HOENN_GOT_WALLY_DAD_SHARED_HM_REWARD","oldsha":"c10762d63fe3770089ba366889310fa83403fcd2a703f04c20b4790397e34048","mapsha":"61b125b97eade6b91d1cb2a097b9d6d0ffac11d9061b5e114d3e621c373477dd","target":"PetalburgCity_WallysHouse_EventScript_DadAfter","old":"PetalburgCity_WallysHouse_EventScript_DadAfter::\n\tmsgbox PetalburgCity_WallysHouse_Text_DadAfter\n\trelease\n\tend\n","npcScript":"PetalburgCity_WallysHouse_EventScript_H0","npc":[3,4],"layout":"HoennHouse2","terrain":"abbbb3ae0dde23f48f41faac137e9533b6095a9f3c69ce2817f459d4dad0fe50","script":"PetalburgCity_WallysHouse_EventScript_DadAfter::\n\tmsgbox PetalburgCity_WallysHouse_Text_DadAfter\n\tgoto_if_unset FLAG_HOENN_BADGE05_GET, PetalburgCity_WallysHouse_TYSharedHM_Done\n\tgoto_if_not_defeated TRAINER_HOENN_NORMAN_1, PetalburgCity_WallysHouse_TYSharedHM_Done\n\tgoto_if_set FLAG_HOENN_GOT_WALLY_DAD_SHARED_HM_REWARD, PetalburgCity_WallysHouse_TYSharedHM_Done\n\tgoto_if_set FLAG_GOT_HM03, PetalburgCity_WallysHouse_TYSharedHM_Known\n\tcheckitem ITEM_HM03\n\tgoto_if_eq VAR_RESULT, TRUE, PetalburgCity_WallysHouse_TYSharedHM_Known\n\tcheckpcitem ITEM_HM03\n\tgoto_if_eq VAR_RESULT, TRUE, PetalburgCity_WallysHouse_TYSharedHM_Known\n\tmsgbox PetalburgCity_WallysHouse_TYSharedHM_FreshText\n\tcheckitemspace ITEM_HM03\n\tgoto_if_eq VAR_RESULT, FALSE, PetalburgCity_WallysHouse_TYSharedHM_Full\n\tgiveitem ITEM_HM03\n\tgoto_if_eq VAR_RESULT, FALSE, PetalburgCity_WallysHouse_TYSharedHM_Full\n\tsetflag FLAG_HOENN_GOT_WALLY_DAD_SHARED_HM_REWARD\n\tmsgbox PetalburgCity_WallysHouse_TYSharedHM_FreshThanks\n\trelease\n\tend\n\nPetalburgCity_WallysHouse_TYSharedHM_Known::\n\tmsgbox PetalburgCity_WallysHouse_TYSharedHM_KnownText\n\tcheckitemspace ITEM_TM13\n\tgoto_if_eq VAR_RESULT, FALSE, PetalburgCity_WallysHouse_TYSharedHM_Full\n\tgiveitem ITEM_TM13\n\tgoto_if_eq VAR_RESULT, FALSE, PetalburgCity_WallysHouse_TYSharedHM_Full\n\tsetflag FLAG_HOENN_GOT_WALLY_DAD_SHARED_HM_REWARD\n\tmsgbox PetalburgCity_WallysHouse_TYSharedHM_TechniqueText\n\trelease\n\tend\n\nPetalburgCity_WallysHouse_TYSharedHM_Full::\n\tmsgbox PetalburgCity_WallysHouse_TYSharedHM_FullText\n\trelease\n\tend\n\nPetalburgCity_WallysHouse_TYSharedHM_Done::\n\trelease\n\tend\n","text":"PetalburgCity_WallysHouse_TYSharedHM_FreshText::\n\t.string \"You earned NORMAN's BADGE.\\p\"\n\t.string \"Let me help you reach the places\\n\"\n\t.string \"beyond HOENN's seas. Take SURF!$\"\n\nPetalburgCity_WallysHouse_TYSharedHM_FreshThanks::\n\t.string \"Your local BADGE lets you SURF\\n\"\n\t.string \"across HOENN's waters.$\"\n\nPetalburgCity_WallysHouse_TYSharedHM_KnownText::\n\t.string \"You already have SURF.\\p\"\n\t.string \"Your local BADGE works with it.\\n\"\n\t.string \"Here is another useful technique.$\"\n\nPetalburgCity_WallysHouse_TYSharedHM_TechniqueText::\n\t.string \"The TM teaches ICE BEAM.\\n\"\n\t.string \"Put it to good use in HOENN!$\"\n\nPetalburgCity_WallysHouse_TYSharedHM_FullText::\n\t.string \"Your BAG has no room.\\p\"\n\t.string \"Make some space, then return.\\n\"\n\t.string \"I will keep your reward ready.$\"\n"},{"map":"GraniteCave_1F","hm":"ITEM_HM05","tm":"ITEM_TM29","history":"FLAG_GOT_HM05","receipt":"FLAG_HOENN_GOT_GRANITE_SHARED_HM_REWARD","oldsha":"6d245e9eb050542692ce1696ec79cb9ccf780be41f42108d7e03b4e8229b4c83","mapsha":"902c84870a4655ed0b8bccf760f738bd4a4927aa4a14bb4803f99d792c9659c5","target":"GraniteCave_1F_EventScript_H0","old":"GraniteCave_1F_EventScript_H0::\n\tmsgbox GraniteCave_1F_Text_H0, MSGBOX_NPC\n\tend\n","npcScript":"GraniteCave_1F_EventScript_H0","npc":[36,9],"layout":"HoennGraniteCave_1F","terrain":"6e8e5420747a9e2c18c9ecc04e43e028cac70e6030a8015a52edcac739459bbf","script":"GraniteCave_1F_EventScript_H0::\n\tlock\n\tfaceplayer\n\tgoto_if_set FLAG_HOENN_GOT_GRANITE_SHARED_HM_REWARD, GraniteCave_1F_TYSharedHM_Done\n\tgoto_if_set FLAG_GOT_HM05, GraniteCave_1F_TYSharedHM_Known\n\tcheckitem ITEM_HM05\n\tgoto_if_eq VAR_RESULT, TRUE, GraniteCave_1F_TYSharedHM_Known\n\tcheckpcitem ITEM_HM05\n\tgoto_if_eq VAR_RESULT, TRUE, GraniteCave_1F_TYSharedHM_Known\n\tmsgbox GraniteCave_1F_TYSharedHM_FreshText\n\tcheckitemspace ITEM_HM05\n\tgoto_if_eq VAR_RESULT, FALSE, GraniteCave_1F_TYSharedHM_Full\n\tgiveitem ITEM_HM05\n\tgoto_if_eq VAR_RESULT, FALSE, GraniteCave_1F_TYSharedHM_Full\n\tsetflag FLAG_HOENN_GOT_GRANITE_SHARED_HM_REWARD\n\tmsgbox GraniteCave_1F_TYSharedHM_FreshThanks\n\trelease\n\tend\n\nGraniteCave_1F_TYSharedHM_Known::\n\tmsgbox GraniteCave_1F_TYSharedHM_KnownText\n\tcheckitemspace ITEM_TM29\n\tgoto_if_eq VAR_RESULT, FALSE, GraniteCave_1F_TYSharedHM_Full\n\tgiveitem ITEM_TM29\n\tgoto_if_eq VAR_RESULT, FALSE, GraniteCave_1F_TYSharedHM_Full\n\tsetflag FLAG_HOENN_GOT_GRANITE_SHARED_HM_REWARD\n\tmsgbox GraniteCave_1F_TYSharedHM_TechniqueText\n\trelease\n\tend\n\nGraniteCave_1F_TYSharedHM_Full::\n\tmsgbox GraniteCave_1F_TYSharedHM_FullText\n\trelease\n\tend\n\nGraniteCave_1F_TYSharedHM_Done::\n\tmsgbox GraniteCave_1F_TYSharedHM_DoneText\n\trelease\n\tend\n","text":"GraniteCave_1F_TYSharedHM_FreshText::\n\t.string \"It gets pitch-black further in.\\p\"\n\t.string \"STEVEN went down ahead of you.\\n\"\n\t.string \"Take this HM to light the way.$\"\n\nGraniteCave_1F_TYSharedHM_FreshThanks::\n\t.string \"With BRAWLY's BADGE, FLASH can\\n\"\n\t.string \"light up HOENN's dark caves.$\"\n\nGraniteCave_1F_TYSharedHM_KnownText::\n\t.string \"You already have FLASH.\\p\"\n\t.string \"That HM will still light the way.\\n\"\n\t.string \"Try this different technique, too.$\"\n\nGraniteCave_1F_TYSharedHM_TechniqueText::\n\t.string \"The TM teaches PSYCHIC.\\n\"\n\t.string \"Put it to good use in HOENN!$\"\n\nGraniteCave_1F_TYSharedHM_FullText::\n\t.string \"Your BAG has no room.\\p\"\n\t.string \"Make some space, then return.\\n\"\n\t.string \"I will keep your reward ready.$\"\n\nGraniteCave_1F_TYSharedHM_DoneText::\n\t.string \"Use your gifts to find a safe path.\\n\"\n\t.string \"Good luck looking for STEVEN!$\"\n"}]
MARK='TY_HOENN_SHARED_HM_STORY_V1'
BEGIN='@ BEGIN PATCH (tools/hoenn_import/patches)\n';END='@ END PATCH\n'
assert subprocess.check_output(['git','branch','--show-current'],text=True).strip()=='hoenn-z3'
paths=['include/constants/flags_hoenn_story.h']
for row in ROWS:
 for kind in ('scripts.inc','text.inc'):
  paths+=['data/maps/'+row['map']+'/'+kind,'tools/hoenn_import/patches/'+row['map']+'.'+kind]
before={p:(R/p).read_bytes() if (R/p).exists() else None for p in paths};out={}
flagpath=paths[0];f=before[flagpath].decode()
for row in ROWS:
 for name,header in [(row['history'],'flags.h'),(row['hm'],'items.h'),(row['tm'],'items.h')]:
  assert re.search(r'^#define\s+'+name+r'\b',(R/'include/constants'/header).read_text(),re.M),('missing original constant',name)
existing=[bool(re.search(r'^#define\s+'+row['receipt']+r'\b',f,re.M)) for row in ROWS]
if any(existing):assert all(existing),('partial reward flags',existing)
else:
 used=re.search(r'^#define\s+HOENN_STORY_FLAGS_USED\s+(\d+)\b',f,re.M)
 assert used,('story flag bound missing')
 start=int(used.group(1));assert start+len(ROWS)<=512
 numbers=[int(x) for x in re.findall(r'\(HOENN_STORY_FLAGS_START\s*\+\s*(\d+)\)',f)]
 assert numbers and max(numbers)<start,('flag allocation bound is stale',start,max(numbers))
 decl='\n// Chapter-bound shared HM gifts; the same receipt covers either reward.\n'
 for i,row in enumerate(ROWS):decl+='#define '+row['receipt']+' (HOENN_STORY_FLAGS_START + '+str(start+i)+')\n'
 f=f[:used.start()]+decl+'#define HOENN_STORY_FLAGS_USED '+str(start+len(ROWS))+f[used.end():]
out[flagpath]=f.encode()
maps_before={};terrain_before={}
for row in ROWS:
 M=row['map'];stem='tools/hoenn_import/patches/'+M
 sp='data/maps/'+M+'/scripts.inc';mp=stem+'.scripts.inc'
 tp='data/maps/'+M+'/text.inc';mt=stem+'.text.inc'
 old=row['old'];replacement='@ '+MARK+'\n'+row['script']
 s=before[sp].decode()
 if row['script'] in s:assert s.count(row['script'])==1
 else:
  assert sha(before[sp])==row['oldsha'] and s.count(old)==1,('NPC source changed',sp)
  assert not re.search(r'^'+M+r'_TYSharedHM_\w+::',s,re.M),('partial new script labels',sp)
  s=s.replace(old,replacement,1)
 out[sp]=s.encode()
 mirror=(before[mp] or b'').decode()
 if row['script'] not in mirror:
  if mirror.strip():
   assert mirror.count(old)==1,('mirror target must be reviewed',mp)
   assert not re.search(r'^'+M+r'_TYSharedHM_\w+::',mirror,re.M)
   mirror=mirror.replace(old,replacement,1)
  else:mirror=replacement
 else:assert mirror.count(row['script'])==1
 out[mp]=mirror.encode()
 t=before[tp].decode()
 if row['text'] not in t:
  assert not re.search(r'^'+M+r'_TYSharedHM_\w+::',t,re.M),('partial new text labels',tp)
  if END in t:
   assert t.count(END)==1;t=t.replace(END,row['text']+END,1)
  else:t=t.rstrip()+'\n\n'+BEGIN+row['text']+END
 out[tp]=t.encode()
 mirror=(before[mt] or b'').decode()
 if row['text'] not in mirror:
  assert not re.search(r'^'+M+r'_TYSharedHM_\w+::',mirror,re.M),('partial mirror text',mt)
  mirror=mirror.rstrip()+'\n\n'+row['text']
 out[mt]=mirror.encode()
 for name in re.findall(r'^(\w+)::',row['script']+row['text'],re.M):
  count=out[sp].decode().count(name+'::')+out[tp].decode().count(name+'::')
  assert count==1,('duplicate script/text label',M,name,count)
 map_path=R/'data/maps'/M/'map.json'
 assert sha(map_path.read_bytes())==row['mapsha'],('original NPC map changed',M)
 maps_before[str(map_path)]=sha(map_path.read_bytes())
 objects=json.loads(map_path.read_text())['object_events']
 chosen=[o for o in objects if o.get('script')==row['npcScript']]
 assert len(chosen)==1 and [chosen[0]['x'],chosen[0]['y']]==row['npc'] and chosen[0]['flag']=='0'
 assert chosen[0]['trainer_type']=='TRAINER_TYPE_NONE'
 terrain_path=R/'data/layouts'/row['layout']/'map.bin'
 assert sha(terrain_path.read_bytes())==row['terrain'],('original NPC terrain changed',M)
 terrain_before[str(terrain_path)]=sha(terrain_path.read_bytes())
 assert 'checkpcitem '+row['hm'] in row['script']
 assert row['script'].count('setflag '+row['receipt'])==2
 assert row['script'].count('goto_if_eq VAR_RESULT, FALSE, '+M+'_TYSharedHM_Full')==4
 assert re.findall(r'^\tsetflag\s+(\w+)',row['script'],re.M)==[row['receipt']]*2
 assert not re.search(r'^\t(?:settrainerflag|setvar|clearflag|setorcopyvar)\b',row['script'],re.M)
changed={p:b for p,b in out.items() if b!=before[p]}
saves={str(p):sha(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}
receipt={'apply':a.apply,'changed':list(changed),'native_shared_hm_cases':'NOT_RUN',
 'save_layout_changed':False,'original_npc_positions_warps_or_terrain_changed':False,
 'chapter_gates':{'Wanda':'RUSTURF_OPEN; preserve the existing Wally/referral dialogue',
  'WallyDad':'Wally scene >=2 AND Hoenn Badge05 AND actual Norman trainer victory',
  'Hiker':'Original immediate HM05 gift; Flash usage has its separate badge gate'},
 'rare_tm':{row['map']:{'hm':row['hm'],'duplicate_tm':row['tm'],'receipt':row['receipt']} for row in ROWS},
 'files':{p:{'before':sha(before[p]) if before[p] is not None else None,'after':sha(out[p])} for p in out},
 'original_map_sha256':maps_before,'original_terrain_sha256':terrain_before,'original_save_sha256':saves}
if a.apply and changed:
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=R/'work/backups'/('hoenn-shared-hm-story-v1-'+stamp)
 for p,b in before.items():assert ((R/p).read_bytes() if (R/p).exists() else None)==b,('concurrent source edit',p)
 for p in changed:
  if before[p] is not None:
   q=dest/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[p])
 for p,b in changed.items():
  q=R/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
 receipt['backup']=str(dest.relative_to(R))
assert {str(p):sha(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}==saves
assert {p:sha(Path(p).read_bytes()) for p in maps_before}==maps_before
assert {p:sha(Path(p).read_bytes()) for p in terrain_before}==terrain_before
print(json.dumps(receipt,indent=2))
