from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, re, subprocess, sys
sys.dont_write_bytecode=True
R=Path.cwd().resolve()
PIN={
"data/maps/JohtoCherrygroveAirstrip/scripts.inc":"980e61e641a1f367a73018f8aba050433b7ccc9ebfbd9cae90edb65bf37509c1",
"data/maps/JohtoCherrygroveAirstrip/text.inc":"0b8d8643684237cd1d1c61ef48ec9404b0815c1eccf8ee665df8862e57e443ac",
"data/maps/NewBarkTown_ElmsLab/scripts.inc":"eb4a38ea935c04e586c7d9521353f95819b5635de2adfcb09fc2043de87d7a18",
"data/maps/NewBarkTown_ElmsLab/text.inc":"fe95f5cce305358c294d723dc215925c20060059bbb9b3d46970dbe6818f7475",
}
HEADER="""#ifndef GUARD_CONSTANTS_FLAGS_JOHTO_STORY_H
#define GUARD_CONSTANTS_FLAGS_JOHTO_STORY_H
// Existing hoennFlags reservation. No SaveBlock fields or offsets change.
#define JOHTO_STORY_FLAGS_START (HOENN_FLAGS_START + 0x500)
#define FLAG_JOHTO_ARRIVAL_BRIEFED (JOHTO_STORY_FLAGS_START + 0)
#define FLAG_JOHTO_MET_LAB_ASSISTANT (JOHTO_STORY_FLAGS_START + 1)
#if JOHTO_STORY_FLAGS_START + 1 > HOENN_FLAGS_END
#error Johto story flags exceed the existing Hoenn flag array
#endif
#endif
"""
ARRIVAL="\n@ A first-visit research referral. This is not a regional clear condition.\nJohtoCherrygroveAirstrip_OnFrame::\n\tmap_script_2 VAR_TEMP_0, 0, JohtoCherrygroveAirstrip_ResearchArrival\n\t.2byte 0\n\nJohtoCherrygroveAirstrip_ResearchArrival::\n\tsetvar VAR_TEMP_0, 1\n\tgoto_if_set FLAG_JOHTO_ARRIVAL_BRIEFED, JohtoCherrygroveAirstrip_ResearchArrivalDone\n\tgoto_if_set FLAG_JOHTO_MET_LAB_ASSISTANT, JohtoCherrygroveAirstrip_ResearchArrivalRecord\n\tlockall\n\tmsgbox JohtoCherrygroveAirstrip_Text_ResearchArrival\n\treleaseall\nJohtoCherrygroveAirstrip_ResearchArrivalRecord::\n\tsetflag FLAG_JOHTO_ARRIVAL_BRIEFED\nJohtoCherrygroveAirstrip_ResearchArrivalDone::\n\tend\n"
TEXT="\nJohtoCherrygroveAirstrip_Text_ResearchArrival::\n    .string \"AIRPORT ANNOUNCEMENT:\\n\"\n    .string \"Welcome to the CHERRYGROVE coast!\\p\"\n    .string \"PROF. ELM's assistant is waiting\\n\"\n    .string \"for the champion from KANTO.\\p\"\n    .string \"Take ROUTE 29 east to NEW BARK.\\n\"\n    .string \"Please visit the LAB before\\l\"\n    .string \"setting out across JOHTO.$\"\n"
def sha(b):return hashlib.sha256(b).hexdigest()
def match(pattern,text):
 m=list(re.finditer(pattern,text,re.M))
 if len(m)!=1:raise ValueError("Expected unique current source anchor: "+pattern)
 return m[0]
def airstrip(text):
 if "VAR_TEMP_0" in text or "JohtoCherrygroveAirstrip_ResearchArrival" in text:
  raise ValueError("Airstrip temp variable or story labels already used")
 m=match(r"^JohtoCherrygroveAirstrip_MapScripts::(?P<n>\r?\n)(?P<i>[ \t]+)\.byte[ \t]+0[ \t]*(?P=n)",text)
 n,i=m["n"],m["i"]
 start="JohtoCherrygroveAirstrip_MapScripts::"+n+i+"map_script MAP_SCRIPT_ON_FRAME_TABLE, JohtoCherrygroveAirstrip_OnFrame"+n+i+".byte 0"+n
 return text[:m.start()]+start+text[m.end():]+ARRIVAL.replace("\n",n)
def lab(text):
 if "FLAG_JOHTO_MET_LAB_ASSISTANT" in text:raise ValueError("Lab already changed")
 m=match(r"^NewBarkTown_ElmsLab_Researcher::(?P<n>\r?\n)(?P<i>[ \t]+)lock[ \t]*(?P=n)[ \t]+faceplayer[ \t]*(?P=n)",text)
 return text[:m.end()]+m["i"]+"setflag FLAG_JOHTO_MET_LAB_ASSISTANT"+m["n"]+text[m.end():]
def builder(text):
 if '"tools/johto/patches/JohtoCherrygroveAirstrip/' in text:
  raise ValueError("Airstrip canonical hook already exists")
 m=match(r"^(?P<i>[ \t]+)return out,dict\(maps=maps,grids=blobs,old_groups=oldgroups,old_layouts=oldlayout\)[ \t]*(?P<n>\r?\n)",text)
 hook="".join(m["i"]+'put("data/maps/JohtoCherrygroveAirstrip/'+part+'", (r/"tools/johto/patches/JohtoCherrygroveAirstrip/'+part+'").read_bytes())'+m["n"] for part in ["scripts.inc","text.inc"])
 changed=text[:m.start()]+hook+text[m.start():]
 compile(changed,"tools/johto/build_entry.py","exec")
 return changed
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--flags-sha",required=True);ap.add_argument("--builder-sha",required=True);ap.add_argument("--write",action="store_true")
 args=ap.parse_args()
 pins={**PIN,"include/constants/flags.h":args.flags_sha,"tools/johto/build_entry.py":args.builder_sha}
 before={p:(R/p).read_bytes() for p in pins}
 if any(sha(b)!=pins[p] for p,b in before.items()):raise ValueError("Fresh input hash mismatch")
 for part in ["scripts.inc","text.inc"]:
  p="tools/johto/patches/NewBarkTown_ElmsLab/"+part
  before[p]=(R/p).read_bytes()
  if before[p]!=before["data/maps/NewBarkTown_ElmsLab/"+part]:
   raise ValueError("Lab canonical/generated differ: "+part)
 for p in ["include/constants/flags_johto_story.h"]+["tools/johto/patches/JohtoCherrygroveAirstrip/"+x for x in ["scripts.inc","text.inc"]]:
  if (R/p).exists():raise FileExistsError(p)
 sys.path.insert(0,str(R/"tools/qa"))
 from gamedata import consts
 proc=subprocess.run(["cc","-dM","-E","-w","-iquote","include","-DLEAFGREEN","-DREVISION=0","-DENGLISH","-DMODERN=1","-x","c","-"],input='#include "global.h"\n#include "constants/flags.h"\n',text=True,capture_output=True,check=True)
 names=sorted(set(re.findall(r"^#define (FLAG_[A-Za-z0-9_]+)[ \t]+[^\n]+",proc.stdout,re.M)))
 occupied={k:v for k,v in consts(names).items() if v in [0x1500,0x1501]}
 if occupied:raise ValueError("Reserved bits already named: "+json.dumps(occupied))
 after=dict(before)
 after["include/constants/flags_johto_story.h"]=HEADER.encode()
 h=before["include/constants/flags.h"].decode()
 anchor='#include "constants/flags_hoenn_story.h"'
 if h.count(anchor)!=1 or 'flags_johto_story.h' in h:raise ValueError("Flags include structure changed")
 n="\r\n" if "\r\n" in h else "\n"
 after["include/constants/flags.h"]=h.replace(anchor,anchor+n+'#include "constants/flags_johto_story.h"',1).encode()
 after["tools/johto/build_entry.py"]=builder(before["tools/johto/build_entry.py"].decode()).encode()
 for region,fn in [("JohtoCherrygroveAirstrip",airstrip),("NewBarkTown_ElmsLab",lab)]:
  content=fn(before["data/maps/"+region+"/scripts.inc"].decode()).encode()
  after["data/maps/"+region+"/scripts.inc"]=content
  after["tools/johto/patches/"+region+"/scripts.inc"]=content
 text=before["data/maps/JohtoCherrygroveAirstrip/text.inc"].decode()
 if "JohtoCherrygroveAirstrip_Text_ResearchArrival" in text:raise ValueError("Text label collision")
 n="\r\n" if "\r\n" in text else "\n"
 content=(text+TEXT.replace("\n",n)).encode()
 after["data/maps/JohtoCherrygroveAirstrip/text.inc"]=content
 after["tools/johto/patches/JohtoCherrygroveAirstrip/text.inc"]=content
 spec=importlib.util.spec_from_file_location("johto_bridge_base",R/"tools/johto/build_entry.py")
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 out,meta=module.build(R)
 targets=["data/maps/"+region+"/"+part for region in ["JohtoCherrygroveAirstrip","NewBarkTown_ElmsLab"] for part in ["scripts.inc","text.inc"]]
 for p in targets:out[p]=after[p]
 module.verify(R,out,meta)
 changed=[p for p in after if before.get(p)!=after[p]]
 report={"changed":changed,"before":{p:sha(b) for p,b in before.items()},"after":{p:sha(after[p]) for p in changed},"applied":False,"save_layout_changed":False,"regional_clear_implemented":False,"build_or_emulator_verified":False}
 if args.write:
  backup=R/"work/johto-research-bridge-backup"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
  backup.mkdir(parents=True,exist_ok=False)
  for p in changed:
   if p in before:
    q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[p])
  (backup/"manifest.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
  if any((R/p).read_bytes()!=b for p,b in before.items()):raise ValueError("Sources changed before apply")
  if any((R/p).exists() for p in after if p not in before):raise ValueError("New destination appeared")
  for p in changed:
   q=R/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after[p])
  if any((R/p).read_bytes()!=after[p] for p in changed):raise ValueError("Write verification failed")
  scope={"__name__":"johto_bridge_new","__file__":str(R/"tools/johto/build_entry.py")}
  exec(compile(after["tools/johto/build_entry.py"],scope["__file__"],"exec"),scope)
  regenerated,metadata=scope["build"](R);scope["verify"](R,regenerated,metadata)
  if any(regenerated[p]!=after[p] for p in targets):raise ValueError("Canonical regeneration mismatch")
  report.update(applied=True,backup=str(backup),canonical_regeneration_verified=True)
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
