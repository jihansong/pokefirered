from pathlib import Path
import argparse,hashlib,json,sys
ap=argparse.ArgumentParser()
ap.add_argument("--harbor-cases",type=Path,required=True)
ap.add_argument("--output",type=Path,required=True)
ap.add_argument("--rom",default="pokemonthyl.gba")
ap.add_argument("--run",action="store_true")
a=ap.parse_args();sys.path.insert(0,str(Path("tools/qa").resolve()))
from eventcheck import run_case
old={c["name"]:c for line in a.harbor_cases.read_text().splitlines() if line.strip() for c in [json.loads(line)]}
L="FLAG_JOHTO_MET_LAB_ASSISTANT";G="FLAG_GOT_CYNDAQUIL_FROM_AIDE"
T="SlateportCity_Harbor_Text_JohtoReferral";cases=[]
for met in [0,1]:
 for lab in [0,1]:
  for progress in [0,7]:
   c=json.loads(json.dumps(old[f"harbor_scene0_met{met}_progress{progress}"]))
   assert not c.get("xfail",False)
   c["name"]=f"harbor_johto_met{met}_lab{lab}_progress{progress}"
   c["edit"] += [f"flag {L} {lab}",f"flag {G} {lab}"]
   c["steps"].insert(0,"watch "+T)
   c["steps"] += [f"expect saw {T} = {int(not met and lab)}",f"expect flag {L} = {lab}",f"expect flag {G} = {lab}"]
   cases.append(c)
for index,value in [(2,0),(6,1)]:
 c=json.loads(json.dumps(cases[index]));c["name"]+="_negative_control"
 c["xfail"]=True;c["steps"].append(f"expect saw {T} = {value}");cases.append(c)
assert len(cases)==10
sources={Path(c.get("base","saves/hoenn.sav")).resolve()for c in cases}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={p:sha(p)for p in sources}
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open("x",encoding="utf-8")as f:
 for c in cases:f.write(json.dumps(c)+"\n")
report={"executed":False,"positive":8,"negative_controls":2,"results":[]}
try:
 if a.run:
  report["executed"]=True
  for c in cases:
   try:ok,fails=run_case(c,a.rom,str(a.output.parent/"referral-shots"))
   except Exception as ex:ok,fails=False,[type(ex).__name__+": "+str(ex)]
   passed=(not ok and len(fails)==1 and fails[0].startswith(c["steps"][-1]+":"))if c.get("xfail")else ok
   r={"name":c["name"],"pass":passed,"failures":fails};report["results"].append(r);print(json.dumps(r),flush=True)
finally:
 report["source_saves_unchanged"]=all(sha(p)==h for p,h in before.items())
 report["all_pass"]=a.run and len(report["results"])==10 and all(r["pass"]for r in report["results"])
 a.output.with_suffix(".report.json").write_text(json.dumps(report,indent=2))
 assert report["source_saves_unchanged"],"Source save changed"
if a.run and not report["all_pass"]:raise SystemExit(1)
