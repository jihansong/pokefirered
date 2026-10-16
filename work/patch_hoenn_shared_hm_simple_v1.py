#!/usr/bin/env python3
"""Shared HM01/HM06 or rare TM rewards at two original permanent Hoenn NPCs."""
import argparse,datetime,hashlib,json,re,subprocess
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--apply',action='store_true');a=P.parse_args()
R=Path.cwd();sha=lambda b:hashlib.sha256(b).hexdigest()
ROWS=[{"map":"RustboroCity_CuttersHouse","hm":"ITEM_HM01","tm":"ITEM_TM31","history":"FLAG_GOT_HM01","receipt":"FLAG_HOENN_GOT_CUTTER_SHARED_HM_REWARD","known":"CUT","technique":"BRICK BREAK","oldsha":"64ee0d6ce58fa31b17fce78e207b9bd06c5c6cec15382484cb71dcdf58018ad7","script":"RustboroCity_CuttersHouse_EventScript_H0::\n\tlock\n\tfaceplayer\n\tgoto_if_set FLAG_HOENN_GOT_CUTTER_SHARED_HM_REWARD, RustboroCity_CuttersHouse_TYSharedHM_Done\n\tgoto_if_set FLAG_GOT_HM01, RustboroCity_CuttersHouse_TYSharedHM_Known\n\tcheckitem ITEM_HM01\n\tgoto_if_eq VAR_RESULT, TRUE, RustboroCity_CuttersHouse_TYSharedHM_Known\n\tcheckpcitem ITEM_HM01\n\tgoto_if_eq VAR_RESULT, TRUE, RustboroCity_CuttersHouse_TYSharedHM_Known\n\tmsgbox RustboroCity_CuttersHouse_TYSharedHM_FreshText\n\tcheckitemspace ITEM_HM01\n\tgoto_if_eq VAR_RESULT, FALSE, RustboroCity_CuttersHouse_TYSharedHM_Full\n\tgiveitem ITEM_HM01\n\tgoto_if_eq VAR_RESULT, FALSE, RustboroCity_CuttersHouse_TYSharedHM_Full\n\tsetflag FLAG_HOENN_GOT_CUTTER_SHARED_HM_REWARD\n\tmsgbox RustboroCity_CuttersHouse_TYSharedHM_FreshThanks\n\trelease\n\tend\n\nRustboroCity_CuttersHouse_TYSharedHM_Known::\n\tmsgbox RustboroCity_CuttersHouse_TYSharedHM_KnownText\n\tcheckitemspace ITEM_TM31\n\tgoto_if_eq VAR_RESULT, FALSE, RustboroCity_CuttersHouse_TYSharedHM_Full\n\tgiveitem ITEM_TM31\n\tgoto_if_eq VAR_RESULT, FALSE, RustboroCity_CuttersHouse_TYSharedHM_Full\n\tsetflag FLAG_HOENN_GOT_CUTTER_SHARED_HM_REWARD\n\tmsgbox RustboroCity_CuttersHouse_TYSharedHM_TechniqueText\n\trelease\n\tend\n\nRustboroCity_CuttersHouse_TYSharedHM_Full::\n\tmsgbox RustboroCity_CuttersHouse_TYSharedHM_FullText\n\trelease\n\tend\n\nRustboroCity_CuttersHouse_TYSharedHM_Done::\n\tmsgbox RustboroCity_CuttersHouse_TYSharedHM_DoneText\n\trelease\n\tend\n","text":"RustboroCity_CuttersHouse_TYSharedHM_FreshText::\n\t.string \"A new region has new challenges.\\p\"\n\t.string \"Take this HM for CUT.$\"\n\nRustboroCity_CuttersHouse_TYSharedHM_FreshThanks::\n\t.string \"You can use CUT here when\\n\"\n\t.string \"you earn the local BADGE.$\"\n\nRustboroCity_CuttersHouse_TYSharedHM_KnownText::\n\t.string \"You already have CUT.\\p\"\n\t.string \"Your technique still works here.\\n\"\n\t.string \"Try this different move, too.$\"\n\nRustboroCity_CuttersHouse_TYSharedHM_TechniqueText::\n\t.string \"The TM teaches BRICK BREAK.\\n\"\n\t.string \"Put it to good use in HOENN!$\"\n\nRustboroCity_CuttersHouse_TYSharedHM_FullText::\n\t.string \"Your BAG has no room.\\p\"\n\t.string \"Make some space, then return.\\n\"\n\t.string \"I will keep your reward ready.$\"\n\nRustboroCity_CuttersHouse_TYSharedHM_DoneText::\n\t.string \"That gift is yours to keep.\\n\"\n\t.string \"Good luck on your journey!$\"\n"},{"map":"MauvilleCity_House1","hm":"ITEM_HM06","tm":"ITEM_TM23","history":"FLAG_GOT_HM06","receipt":"FLAG_HOENN_GOT_ROCK_SMASH_SHARED_HM_REWARD","known":"ROCK SMASH","technique":"IRON TAIL","oldsha":"2c66babb343cea9033b8716f88e04f07959ddbf02a367a0bf64998981afaf93e","script":"MauvilleCity_House1_EventScript_H0::\n\tlock\n\tfaceplayer\n\tgoto_if_set FLAG_HOENN_GOT_ROCK_SMASH_SHARED_HM_REWARD, MauvilleCity_House1_TYSharedHM_Done\n\tgoto_if_set FLAG_GOT_HM06, MauvilleCity_House1_TYSharedHM_Known\n\tcheckitem ITEM_HM06\n\tgoto_if_eq VAR_RESULT, TRUE, MauvilleCity_House1_TYSharedHM_Known\n\tcheckpcitem ITEM_HM06\n\tgoto_if_eq VAR_RESULT, TRUE, MauvilleCity_House1_TYSharedHM_Known\n\tmsgbox MauvilleCity_House1_TYSharedHM_FreshText\n\tcheckitemspace ITEM_HM06\n\tgoto_if_eq VAR_RESULT, FALSE, MauvilleCity_House1_TYSharedHM_Full\n\tgiveitem ITEM_HM06\n\tgoto_if_eq VAR_RESULT, FALSE, MauvilleCity_House1_TYSharedHM_Full\n\tsetflag FLAG_HOENN_GOT_ROCK_SMASH_SHARED_HM_REWARD\n\tmsgbox MauvilleCity_House1_TYSharedHM_FreshThanks\n\trelease\n\tend\n\nMauvilleCity_House1_TYSharedHM_Known::\n\tmsgbox MauvilleCity_House1_TYSharedHM_KnownText\n\tcheckitemspace ITEM_TM23\n\tgoto_if_eq VAR_RESULT, FALSE, MauvilleCity_House1_TYSharedHM_Full\n\tgiveitem ITEM_TM23\n\tgoto_if_eq VAR_RESULT, FALSE, MauvilleCity_House1_TYSharedHM_Full\n\tsetflag FLAG_HOENN_GOT_ROCK_SMASH_SHARED_HM_REWARD\n\tmsgbox MauvilleCity_House1_TYSharedHM_TechniqueText\n\trelease\n\tend\n\nMauvilleCity_House1_TYSharedHM_Full::\n\tmsgbox MauvilleCity_House1_TYSharedHM_FullText\n\trelease\n\tend\n\nMauvilleCity_House1_TYSharedHM_Done::\n\tmsgbox MauvilleCity_House1_TYSharedHM_DoneText\n\trelease\n\tend\n","text":"MauvilleCity_House1_TYSharedHM_FreshText::\n\t.string \"A new region has new challenges.\\p\"\n\t.string \"Take this HM for ROCK SMASH.$\"\n\nMauvilleCity_House1_TYSharedHM_FreshThanks::\n\t.string \"You can use ROCK SMASH here when\\n\"\n\t.string \"you earn the local BADGE.$\"\n\nMauvilleCity_House1_TYSharedHM_KnownText::\n\t.string \"You already have ROCK SMASH.\\p\"\n\t.string \"Your technique still works here.\\n\"\n\t.string \"Try this different move, too.$\"\n\nMauvilleCity_House1_TYSharedHM_TechniqueText::\n\t.string \"The TM teaches IRON TAIL.\\n\"\n\t.string \"Put it to good use in HOENN!$\"\n\nMauvilleCity_House1_TYSharedHM_FullText::\n\t.string \"Your BAG has no room.\\p\"\n\t.string \"Make some space, then return.\\n\"\n\t.string \"I will keep your reward ready.$\"\n\nMauvilleCity_House1_TYSharedHM_DoneText::\n\t.string \"That gift is yours to keep.\\n\"\n\t.string \"Good luck on your journey!$\"\n"}]
MARK='TY_HOENN_SHARED_HM_SIMPLE_V1'
BEGIN='@ BEGIN PATCH (tools/hoenn_import/patches)\n';END='@ END PATCH\n'
assert subprocess.check_output(['git','branch','--show-current'],text=True).strip()=='hoenn-z3'
paths=['include/constants/flags_hoenn_story.h']
for row in ROWS:
 for kind in ('scripts.inc','text.inc'):
  paths+=['data/maps/'+row['map']+'/'+kind,'tools/hoenn_import/patches/'+row['map']+'.'+kind]
before={p:(R/p).read_bytes() if (R/p).exists() else None for p in paths};out={}
flagpath=paths[0];f=before[flagpath].decode()
for row in ROWS:
 for n in [row['history'],row['hm'],row['tm']]:
  headers='flags.h' if n.startswith('FLAG_') else 'items.h'
  assert re.search(r'^#define\s+'+n+r'\b',(R/'include/constants'/headers).read_text(),re.M),('missing original constant',n)
existing=[bool(re.search(r'^#define\s+'+row['receipt']+r'\b',f,re.M)) for row in ROWS]
if any(existing):assert all(existing),('partial reward flags',existing)
else:
 used=re.search(r'^#define\s+HOENN_STORY_FLAGS_USED\s+(\d+)\b',f,re.M)
 assert used,('story flag bound missing')
 start=int(used.group(1));assert start+len(ROWS)<=512
 numbers=[int(x) for x in re.findall(r'\(HOENN_STORY_FLAGS_START\s*\+\s*(\d+)\)',f)]
 assert numbers and max(numbers)<start,('flag allocation bound is stale',start,max(numbers))
 decl='\n// Shared Hoenn HM gifts; one receipt regardless of HM or alternate TM.\n'
 for i,row in enumerate(ROWS):decl+='#define '+row['receipt']+' (HOENN_STORY_FLAGS_START + '+str(start+i)+')\n'
 f=f[:used.start()]+decl+'#define HOENN_STORY_FLAGS_USED '+str(start+len(ROWS))+f[used.end():]
out[flagpath]=f.encode()
maps_before={};original_blocks={}
for row in ROWS:
 M=row['map'];stem='tools/hoenn_import/patches/'+M
 sp='data/maps/'+M+'/scripts.inc';mp=stem+'.scripts.inc'
 tp='data/maps/'+M+'/text.inc';mt=stem+'.text.inc'
 old=M+'_EventScript_H0::\n\tmsgbox '+M+'_Text_H0, MSGBOX_NPC\n\tend\n'
 s=before[sp].decode();patch='@ '+MARK+'\n'+row['script']
 if row['script'] in s:assert s.count(row['script'])==1
 else:
  assert sha(before[sp])==row['oldsha'] and s.count(old)==1,('NPC current source changed',sp)
  s=s.replace(old,'',1).rstrip()+'\n\n'+BEGIN+patch+END
 out[sp]=s.encode()
 if before[mp] is not None:
  assert before[mp].decode().strip()==patch.strip(),('existing mirror must be reviewed',mp)
 out[mp]=patch.encode()
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
 map_path=R/'data/maps'/M/'map.json';maps_before[str(map_path)]=sha(map_path.read_bytes())
 objects=json.loads(map_path.read_text())['object_events']
 assert sum(o.get('script')==M+'_EventScript_H0' for o in objects)==1
 assert 'checkpcitem '+row['hm'] in row['script']
 assert row['script'].count('setflag '+row['receipt'])==2
 assert row['script'].count('goto_if_eq VAR_RESULT, FALSE, '+M+'_TYSharedHM_Full')==4
changed={p:b for p,b in out.items() if b!=before[p]}
saves={str(p):sha(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}
receipt={'apply':a.apply,'changed':list(changed),'native_shared_hm_cases':'NOT_RUN',
 'save_layout_changed':False,'original_npc_positions_warps_or_terrain_changed':False,
 'rare_tm':{row['map']:{'hm':row['hm'],'duplicate_tm':row['tm'],'receipt':row['receipt']} for row in ROWS},
 'files':{p:{'before':sha(before[p]) if before[p] is not None else None,'after':sha(out[p])} for p in out},
 'original_map_sha256':maps_before,'original_save_sha256':saves}
if a.apply and changed:
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=R/'work/backups'/('hoenn-shared-hm-simple-v1-'+stamp)
 for p,b in before.items():assert ((R/p).read_bytes() if (R/p).exists() else None)==b,('concurrent source edit',p)
 for p in changed:
  if before[p] is not None:
   q=dest/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[p])
 for p,b in changed.items():
  q=R/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
 receipt['backup']=str(dest.relative_to(R))
assert {str(p):sha(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}==saves
assert {p:sha(Path(p).read_bytes()) for p in maps_before}==maps_before
print(json.dumps(receipt,indent=2))
