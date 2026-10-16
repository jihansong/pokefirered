from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re
PIN={"tools/hoenn_import/patches/SlateportCity_Harbor.scripts.inc":"d7529ae1dd6840f3e215480d8f0ff5c1ca3a1c42065e205ef36b29e5027cc881","data/maps/SlateportCity_Harbor/scripts.inc":"0c1c53b1c4d7c5faa39e1fb5725eb3888417601551abeea2bd459a3a3da243b7","tools/hoenn_import/patches/SlateportCity_Harbor.text.inc":"0a6495ae49a260202c6cffb827693e9de9d70d89aea7c1d2bfbe8d97c4461b61","data/maps/SlateportCity_Harbor/text.inc":"645f8a9f0c40bab655af1cbc0993ba3a6f1a492eb183882010e6284f1d925465"}
TEXT="SlateportCity_Harbor_Text_JohtoReferral::\n    .string \"ELM's assistant sent word, too.\\p\"\n    .string \"You met the research team\\n\"\n    .string \"at ELM's lab in JOHTO.\\p\"\n    .string \"BIRCH studies how POKéMON live\\n\"\n    .string \"here in HOENN.\\p\"\n    .string \"Once you have seen SLATEPORT,\\n\"\n    .string \"look for his lab in LITTLEROOT.$\"\n"
P="tools/hoenn_import/patches/SlateportCity_Harbor"
G="data/maps/SlateportCity_Harbor"
L="SlateportCity_Harbor_EventScript_JohtoReferral"
BEGIN="@ BEGIN PATCH (tools/hoenn_import/patches)\n";END="@ END PATCH\n"
def sha(b):return hashlib.sha256(b).hexdigest()
def merge(cur,patch):
 cur=re.sub(re.escape(BEGIN)+".*?"+re.escape(END),"",cur,flags=re.S)
 for label in re.findall(r"^(\w+)::",patch,re.M):
  cur=re.sub(r"^"+re.escape(label)+r"::\n(?:[ \t].*\n)+\n?","",cur,flags=re.M)
 return cur.rstrip("\n")+"\n\n"+BEGIN+patch.rstrip("\n")+"\n"+END
def update(before):
 text={p:b.decode() for p,b in before.items()}
 sc=text[P+".scripts.inc"]
 assert L not in sc
 pat=r"(?m)^(?P<i>[ \t]+)msgbox SlateportCity_Harbor_Text_SternArrival[ \t]*\n"
 hits=list(re.finditer(pat,sc))
 if len(hits)!=1:raise ValueError("Expected one arrival introduction")
 m=hits[0]
 start=sc.index("SlateportCity_Harbor_EventScript_ArrivalScene::")
 resume=sc.index("SlateportCity_Harbor_EventScript_ResumeArrival::")
 assert start<m.start()<resume
 assert "goto_if_set FLAG_HOENN_MET_STERN, SlateportCity_Harbor_EventScript_ResumeArrival" in sc[start:m.start()]
 call=m["i"]+"call_if_set FLAG_JOHTO_MET_LAB_ASSISTANT, "+L+"\n"
 sc=sc[:m.end()]+call+sc[m.end():]
 sc+="\n"+L+"::\n\tmsgbox SlateportCity_Harbor_Text_JohtoReferral\n\treturn\n"
 assert "SlateportCity_Harbor_Text_JohtoReferral::" not in text[P+".text.inc"]
 after={P+".scripts.inc":sc.encode(),P+".text.inc":(text[P+".text.inc"]+"\n"+TEXT).encode()}
 for ext in ["scripts.inc","text.inc"]:
  assert merge(text[G+"/"+ext],text[P+"."+ext])==text[G+"/"+ext],"Canonical baseline differs"
  p=G+"/"+ext;patched=merge(text[p],after[P+"."+ext].decode())
  assert merge(patched,after[P+"."+ext].decode())==patched
  after[p]=patched.encode()
 return after
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--write",action="store_true");a=ap.parse_args()
 before={p:Path(p).read_bytes() for p in PIN}
 assert all(sha(b)==PIN[p] for p,b in before.items()),"Fresh source SHA mismatch"
 header=Path("include/constants/flags_johto_story.h").read_text()
 assert "FLAG_JOHTO_MET_LAB_ASSISTANT" in header
 after=update(before)
 report={"before":{p:sha(b) for p,b in before.items()},"after":{p:sha(b) for p,b in after.items()},
  "applied":False,"new_flags":0,"save_layout_changed":False,"regional_clear_unlocked":False,
  "scope":"Optional first-arrival acknowledgment of the actual Johto lab visit only"}
 if a.write:
  d=Path("work/region-bridge-backup")/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
  d.mkdir(parents=True)
  for p,b in before.items():
   q=d/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
  (d/"manifest.json").write_text(json.dumps(report,indent=2))
  assert all(Path(p).read_bytes()==b for p,b in before.items()),"Concurrent source change"
  for p,b in after.items():Path(p).write_bytes(b)
  assert all(Path(p).read_bytes()==b for p,b in after.items())
  report.update(applied=True,backup=str(d))
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
