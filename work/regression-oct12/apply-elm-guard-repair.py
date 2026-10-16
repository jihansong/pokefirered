from pathlib import Path
import json,ast,hashlib,copy,re
r=Path('/workspaces/pokefirered');sha=lambda b:hashlib.sha256(b).hexdigest()
changes=[]
p=r/'tools/johto/build_entry.py';old=p.read_bytes()
assert sha(old)=='834034c710c98c2eaa0fdf62f5be26e743acc2c7f8ee536022e16967a0525f39'
a='''def build(r):
    # CHERRYGROVE_EXTENSION_GUARD
    _jg = json.loads((r / "data/maps/map_groups.json").read_bytes()).get("gMapGroup_JohtoEntry", [])
    if any(_name not in NAMES for _name in _jg):
        raise RuntimeError("Johto has additional maps; use tools/johto/build_cherrygrove.py; do not overwrite the extension")
 out={}
'''
b='\n'.join(line[3:] if line.startswith('    ') else line for line in a.split('\n'))
s=old.decode();assert s.count(a)==1;new=s.replace(a,b,1).encode();ast.parse(new);changes.append((p,old,new))
p=r/'data/maps/NewBarkTown_ElmsLab/map.json';old=p.read_bytes();m=json.loads(old)
assert len(m['object_events'])==1 and m['object_events'][0]['script']=='NewBarkTown_ElmsLab_Researcher'
original_events=copy.deepcopy(m['object_events']);ls=json.loads((r/'data/layouts/layouts.json').read_text())['layouts'];l=next(x for x in ls if x.get('id')==m['layout']);block=(r/l['blockdata_filepath']).read_bytes()
occupied={(o['x'],o['y']) for k in ['object_events','warp_events','coord_events','bg_events'] for o in m.get(k,[]) if isinstance(o.get('x'),int)}
floor=[]
for x,y in [(7,8),(8,9),(4,8)]:
 raw=int.from_bytes(block[(y*l['width']+x)*2:(y*l['width']+x)*2+2],'little')
 if (raw>>10)&3==0 and (raw>>12)==3 and (x,y) not in occupied:floor.append((x,y,raw))
assert floor,'No verified empty walking floor';x,y,raw=floor[0]
elm=copy.deepcopy(original_events[0]);elm.update(local_id='2',x=x,y=y,graphics_id='OBJ_EVENT_GFX_SCIENTIST',script='NewBarkTown_ElmsLab_ProfessorElm',flag='0');m['object_events'].append(elm)
assert m['object_events'][:1]==original_events
changes.append((p,old,(json.dumps(m,indent=2,ensure_ascii=False)+'\n').encode()))
p=r/'data/maps/NewBarkTown_ElmsLab/scripts.inc';old=p.read_bytes()
script='''
@ Named professor uses a temporary native research sprite; dedicated Elm art pending.
NewBarkTown_ElmsLab_ProfessorElm::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_MR_POKEMON_BRIEFED, NewBarkTown_ElmsLab_ProfessorElmIntroduction
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, NewBarkTown_ElmsLab_ProfessorElmComplete
    msgbox NewBarkTown_ElmsLab_Text_ProfessorElmReport, MSGBOX_DEFAULT
    setflag FLAG_JOHTO_ELM_REPORT_DELIVERED
    release
    end

NewBarkTown_ElmsLab_ProfessorElmIntroduction::
    msgbox NewBarkTown_ElmsLab_Text_ProfessorElm, MSGBOX_DEFAULT
    release
    end

NewBarkTown_ElmsLab_ProfessorElmComplete::
    msgbox NewBarkTown_ElmsLab_Text_ProfessorElmComplete, MSGBOX_DEFAULT
    release
    end
'''
assert 'NewBarkTown_ElmsLab_ProfessorElm::' not in old.decode();changes.append((p,old,old+script.encode()))
p=r/'data/maps/NewBarkTown_ElmsLab/text.inc';old=p.read_bytes()
text=r'''
NewBarkTown_ElmsLab_Text_ProfessorElm::
    .string "ELM: Welcome to NEW BARK TOWN!\n"
    .string "I am PROF. ELM, JOHTO's\l"
    .string "POKeMON researcher.\p"
    .string "OAK told me about KANTO's\n"
    .string "new CHAMPION. I would like\l"
    .string "your help with our research.\p"
    .string "OAK, BIRCH, and I compare\n"
    .string "findings across our regions.\l"
    .string "Your POKeDEX links that work.\p"
    .string "Speak to my assistant about\n"
    .string "our CYNDAQUIL partner study.\p"
    .string "MR. POKeMON lives on ROUTE 30.\n"
    .string "Go west to CHERRYGROVE,\l"
    .string "then follow ROUTE 30 north.\p"
    .string "Speak to him, then return\n"
    .string "here with his research report.$"

NewBarkTown_ElmsLab_Text_ProfessorElmReport::
    .string "ELM: MR. POKeMON's findings!\n"
    .string "Thank you for bringing them.\p"
    .string "They build on OAK's KANTO work\n"
    .string "and BIRCH's HOENN research.\p"
    .string "Continue to VIOLET CITY.\n"
    .string "The GUIDE GENT in CHERRYGROVE\l"
    .string "can explain the route.$"

NewBarkTown_ElmsLab_Text_ProfessorElmComplete::
    .string "ELM: We have your report.\n"
    .string "Our regional records are linked.\p"
    .string "Continue to VIOLET CITY and\n"
    .string "learn at the SPROUT TOWER.\p"
    .string "I look forward to hearing\n"
    .string "about your JOHTO partners.$"
'''.replace('POKe','POK')
assert 'NewBarkTown_ElmsLab_Text_ProfessorElm::' not in old.decode();changes.append((p,old,old+text.encode()))
backup=r/'work/regression-oct12/backups';backup.mkdir(parents=True,exist_ok=True)
for p,o,n in changes:
 dest=backup/(p.name+'.pre-elm-guard-'+sha(o)[:12])
 if dest.exists():assert dest.read_bytes()==o
 else:dest.write_bytes(o)
 assert p.read_bytes()==o
for p,o,n in changes:p.write_bytes(n)
receipt={'source_applied':True,'new_save_fields':0,'original_assistant_event_preserved':True,'professor_coordinate':[x,y],'floor_raw':hex(raw),'professor_graphics':'Temporary OBJ_EVENT_GFX_SCIENTIST, not completed dedicated Elm art','generator_executed':False,'changes':[{'path':str(p),'before_sha256':sha(o),'after_sha256':sha(n)} for p,o,n in changes]}
(r/'work/regression-oct12/elm-guard-repair-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
