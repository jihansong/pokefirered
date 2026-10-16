from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re
N="LittlerootTown_ProfessorBirchsLab";P="tools/hoenn_import/patches/"+N;G="data/maps/"+N
PIN={P+".scripts.inc":"1e738c356ea19010f2834b28831435f382c612f27f4b5e2485dda04f31ce8203",P+".text.inc":"570de2c6d2b4aeca18e5a4eb19fd93592e9f834c4ed2b347d22be01c7d975c30",G+"/map.json":"d31e359af884c163083afbfc3266a97383fadf039be75e2c10bfe660f9c5d337"}
F="FLAG_JOHTO_MET_LAB_ASSISTANT";L=N+"_EventScript_JohtoReferral";T=N+"_Text_JohtoReferral"
ADD="\n"+L+"::\n\tmsgbox "+T+"\n\treturn\n"
TEXT="\n"+T+'::\n    .string "ELM\'s assistant told me about\\n"\n    .string "your visit to the JOHTO LAB.\\p"\n    .string "Here in HOENN, I study POKéMON\\n"\n    .string "in the wild. Welcome to my LAB!$"\n'
BEGIN="@ BEGIN PATCH (tools/hoenn_import/patches)\n";END="@ END PATCH\n"
def sha(b):return hashlib.sha256(b).hexdigest()
def merge(cur,patch):
 cur=re.sub(re.escape(BEGIN)+".*?"+re.escape(END),"",cur,flags=re.S).rstrip("\n")+"\n"
 for label in re.findall(r"^(\w+)::",patch,re.M):
  cur=re.sub(r"^"+re.escape(label)+r"::\n(?:[ \t].*\n)+\n?","",cur,flags=re.M)
 return cur.rstrip("\n")+"\n\n"+BEGIN+patch.rstrip("\n")+"\n"+END
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--generated-scripts-sha",required=True);ap.add_argument("--generated-text-sha",required=True);ap.add_argument("--write",action="store_true");a=ap.parse_args()
 pins={**PIN,G+"/scripts.inc":a.generated_scripts_sha,G+"/text.inc":a.generated_text_sha}
 before={p:Path(p).read_bytes()for p in pins}
 assert all(sha(b)==pins[p]for p,b in before.items()),"Fresh source hash mismatch"
 text={p:b.decode("utf-8")for p,b in before.items()}
 assert any(F in p.read_text(encoding="utf-8")for p in Path("include/constants").glob("flags*.h")),"Johto meeting flag missing"
 for ext in["scripts.inc","text.inc"]:
  assert merge(text[G+"/"+ext],text[P+"."+ext])==text[G+"/"+ext],"Canonical baseline differs"
 scripts=text[P+".scripts.inc"]
 anchor=r"^(?P<label>\w+)::\n(?P<lock>[ \t]+lock\n)(?P<face>[ \t]+faceplayer\n)(?=[ \t]+goto_if_eq VAR_HOENN_SCENE_BIRCH, 1, \w+)"
 matches=list(re.finditer(anchor,scripts,re.M));assert len(matches)==1,"Birch entry changed"
 m=matches[0];indent=re.match(r"[ \t]+",m["face"]).group()
 assert L+"::"not in scripts and T+"::"not in text[P+".text.inc"],"New label already exists"
 new=scripts[:m.end()]+indent+"call_if_set "+F+", "+L+"\n"+scripts[m.end():]+ADD
 restored=new[:-len(ADD)].replace(indent+"call_if_set "+F+", "+L+"\n","",1)
 assert restored==scripts
 after={P+".scripts.inc":new.encode(),P+".text.inc":(text[P+".text.inc"]+TEXT).encode()}
 for ext in["scripts.inc","text.inc"]:
  patch=after[P+"."+ext].decode()
  merged=merge(text[G+"/"+ext],patch)
  assert merge(merged,patch)==merged
  after[G+"/"+ext]=merged.encode()
 report={"applied":False,"changed":list(after),"before":{p:sha(b)for p,b in before.items()},"after":{p:sha(b)for p,b in after.items()},"existing_script_restored_exactly":True,"new_save_fields":False,"new_flags":False,"runtime_verified":False}
 if a.write:
  backup=Path("work/birch-johto-bridge-backup")/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ");backup.mkdir(parents=True,exist_ok=False)
  for p in after:
   q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[p])
  (backup/"manifest.json").write_text(json.dumps(report,indent=2))
  assert all(Path(p).read_bytes()==b for p,b in before.items()),"Concurrent source change"
  for p,b in after.items():Path(p).write_bytes(b)
  assert all(Path(p).read_bytes()==b for p,b in after.items()),"Write verification failed"
  report.update(applied=True,backup=str(backup))
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
