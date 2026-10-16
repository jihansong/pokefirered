LAB_SCRIPT = r"""NewBarkTown_ElmsLab_MapScripts::
    .byte 0

@ ELM's native assistant; the separate Silver story is still pending.
NewBarkTown_ElmsLab_Researcher::
    lock
    faceplayer
    goto_if_set FLAG_GOT_CYNDAQUIL_FROM_AIDE, NewBarkTown_ElmsLab_AlreadyReceived
    msgbox NewBarkTown_ElmsLab_Text_ResearchRequest
    showmonpic SPECIES_CYNDAQUIL, 10, 3
    playmoncry SPECIES_CYNDAQUIL, 0
    waitmoncry
    msgbox NewBarkTown_ElmsLab_Text_CyndaquilOffer, MSGBOX_YESNO
    hidemonpic
    goto_if_eq VAR_RESULT, NO, NewBarkTown_ElmsLab_Decline
    setvar VAR_TEMP_1, SPECIES_CYNDAQUIL
    call EventScript_GiveGiftMonLv5
    goto_if_eq VAR_RESULT, FALSE, EventScript_ReleaseEnd
    setflag FLAG_GOT_CYNDAQUIL_FROM_AIDE
    msgbox NewBarkTown_ElmsLab_Text_Received
    release
    end

NewBarkTown_ElmsLab_AlreadyReceived::
    msgbox NewBarkTown_ElmsLab_Text_AlreadyReceived
    release
    end

NewBarkTown_ElmsLab_Decline::
    msgbox NewBarkTown_ElmsLab_Text_Decline
    release
    end
"""
LAB_TEXT = r"""NewBarkTown_ElmsLab_Text_ResearchRequest::
    .string "I'm one of PROF. ELM's assistants.\p"
    .string "He asked us to study how a new\n"
    .string "partner grows with a TRAINER.\p"
    .string "Your journey with a KANTO partner\n"
    .string "could help with that research.$"

NewBarkTown_ElmsLab_Text_CyndaquilOffer::
    .string "This CYNDAQUIL is ready to travel.\n"
    .string "Will you take it along?$"

NewBarkTown_ElmsLab_Text_Received::
    .string "Thank you! CYNDAQUIL is still\n"
    .string "young, so help it grow at its pace.\p"
    .string "Try walking together and sharing\n"
    .string "the sights of JOHTO.$"

NewBarkTown_ElmsLab_Text_AlreadyReceived::
    .string "ELM already entrusted CYNDAQUIL\n"
    .string "to you for his research.\p"
    .string "A partner from OAK's aide counts,\n"
    .string "too. We share those records.\p"
    .string "Every journey with a partner\n"
    .string "teaches us something new.$"

NewBarkTown_ElmsLab_Text_Decline::
    .string "That's fine. We'll care for\n"
    .string "CYNDAQUIL until you're ready.$"
"""
import argparse,ast,datetime,hashlib,json,pathlib,re,subprocess
p=argparse.ArgumentParser();p.add_argument("--apply",action="store_true");a=p.parse_args()
r=pathlib.Path("/workspaces/pokefirered");sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(["git","branch","--show-current"],cwd=r,text=True).strip()=="hoenn-z3"
n="NewBarkTown_ElmsLab";dp="data/maps/"+n+"/";cp="tools/johto/patches/"+n+"/"
expected={"scripts.inc":"fa2a2c9ca600dd8302da407658446260c3000e69d71d7d89e28fd88d479397c3","text.inc":"b1cb41aa16ee61e61f45893e1c306a7fe28a44b8ef140691234a32999356e1b9"}
assert sha((r/"data/scripts/gift_mon.inc").read_bytes())=="335fa02468b2fd5eff47f912e41c33816c0b9b8fd2428f5de3c3fced0fe71a77"
assert sha((r/"data/layouts/NewBarkTown_ElmsLab/map.bin").read_bytes())=="a1ca472215cd91f5128360af49880035be67b82fb43120758826a21e6a8d803f"
assert re.search(r"#define\s+FLAG_GOT_CYNDAQUIL_FROM_AIDE\s+0x0CE\b",(r/"include/constants/flags.h").read_text())
obj=json.loads((r/(dp+"map.json")).read_text())["object_events"]
assert len(obj)==1 and(obj[0]["x"],obj[0]["y"],obj[0]["script"])==(5,5,n+"_Researcher")
out={}
for f,t in[("scripts.inc",LAB_SCRIPT),("text.inc",LAB_TEXT)]:
    old=(r/(dp+f)).read_bytes();new=t.encode()
    assert sha(old)==expected[f]or old==new,("Changed lab source",f,sha(old))
    if(r/(cp+f)).exists():assert(r/(cp+f)).read_bytes()==new,("Existing different canonical",f)
    out[cp+f]=out[dp+f]=new
ep="tools/johto/build_entry.py";entry=(r/ep).read_text()
for f in("scripts.inc","text.inc"):
    new='put("'+dp+f+'",(r/"'+cp+f+'").read_bytes())'
    if new in entry:assert entry.count(new)==1;continue
    if f=="scripts.inc":
        old='script(3,npc(3,"Researcher"))';assert entry.count(old)==1,"Entry script anchor changed";entry=entry.replace(old,new,1)
    else:
        pattern=r'(?m)^([ \t]+)text\(3,dict\(Researcher=.*\)\)$'
        entry,count=re.subn(pattern,lambda m:m.group(1)+new,entry);assert count==1,"Entry text anchor changed"
ast.parse(entry);out[ep]=entry.encode()
before={f:(r/f).read_bytes()if(r/f).exists()else None for f in out}
changed={f:b for f,b in out.items()if before[f]!=b}
print(json.dumps({"changed":list(changed),"apply":a.apply,"runtime":"NOT RUN"},indent=2))
if a.apply and changed:
    backup=r/(".qa-lab-mini-"+datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"));backup.mkdir(exist_ok=False)
    for f in changed:
        if before[f]is not None:
            q=backup/f;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[f])
    (backup/"manifest.json").write_text(json.dumps({f:{"before":sha(before[f])if before[f]is not None else None,"after":sha(changed[f])}for f in changed},indent=2))
    for f,b in changed.items():
        q=r/f;assert(q.read_bytes()if q.exists()else None)==before[f],("Concurrent change",f)
        q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
    assert all((r/f).read_bytes()==b for f,b in out.items())
    print("APPLIED 5 files; build and 8 game cases still required")
