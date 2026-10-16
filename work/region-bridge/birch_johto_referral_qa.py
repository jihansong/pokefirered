from pathlib import Path
import argparse,contextlib,hashlib,io,json,sys
ap=argparse.ArgumentParser();ap.add_argument("--base",type=Path,default=Path("saves/hoenn.sav"));ap.add_argument("--output",type=Path,required=True);ap.add_argument("--rom",default="pokemonthyl.gba");ap.add_argument("--run",action="store_true");a=ap.parse_args()
sys.path.insert(0,str(Path("tools/qa").resolve()))
import savedit
from eventcheck import run_case
from savefile import SaveFile
from gamedata import const
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a.base=a.base.resolve();original=sha(a.base)
assert SaveFile(str(a.base)).party_count()==6,"Use the reviewed six-mon hoenn.sav base"
a.output.mkdir(parents=True,exist_ok=False)
N="LittlerootTown_ProfessorBirchsLab"
S="VAR_HOENN_SCENE_BIRCH";L="FLAG_JOHTO_MET_LAB_ASSISTANT";G="FLAG_GOT_CYNDAQUIL_FROM_AIDE"
B="FLAG_HOENN_GOT_TORCHIC_FROM_BIRCH";C="FLAG_GOT_TORCHIC_FROM_CELIO";T=N+"_Text_JohtoReferral"
rows=[("new_gift_no_visit",1,0,0,0,False),("new_gift_declined_cyndaquil",1,1,0,0,False),("new_gift_after_celio",1,1,1,1,False),("no_room_keeps_pending",1,1,0,0,True)]
rows += [(f"received_visit{l}_cyndaquil{g}",2,l,g,0,False)for l in[0,1]for g in[0,1]]
rows += [(f"after_rival_visit{l}",3,l,1,0,False)for l in[0,1]]
cases=[];report={"executed":False,"results":[]}
try:
 for name,scene,lab,gift,celio,full in rows:
  fixture=a.output/(name+".sav")
  edits=[f"warp {N} 6 5","noquestlog",f"var {S} {scene}",f"flag {L} {lab}",f"flag {G} {gift}",f"flag {B} {int(scene!=1)}",f"flag {C} {celio}","flag FLAG_HOENN_BIRCH_RESCUED 1"]
  edits += ["fillboxes"]if full else(["party 5"]if scene==1 else[])
  argv=[str(a.base),"-o",str(fixture)]
  for line in edits:argv+=line.split()
  with contextlib.redirect_stdout(io.StringIO()):rc=savedit.run(argv)
  assert rc==0
  save=SaveFile(str(fixture))
  mons=[save.party_mon(i)for i in range(save.party_count())]+save.box_mons()
  count=sum(m.has_species()and not m.is_egg()and m.species()==const("SPECIES_TORCHIC")for m in mons)
  awarded=scene==1 and not full
  expect=[f"expect saw {T} = {lab}",f"expect flag {L} = {lab}",f"expect flag {G} = {gift}",f"expect flag {C} = {celio}",f"expect flag {B} = {int(scene!=1 or awarded)}",f"expect mons TORCHIC = {count+awarded}"]
  if scene<=2:expect += [f"expect var {S} = {2 if awarded else scene}"]
  if awarded:expect += [f"expect species {save.party_count()} TORCHIC"]
  start=[f"watch {T}","UP","A"]+(["mashtext Text_GiveNicknameToThisMon 180","B"]if awarded else[])
  steps=start+["mash 220","expect overworld","expect sym sLockFieldControls = 0"]+expect+["wait 180","mash 20","expect presses <= 0"]
  if not full:steps += ["A","mash 220","expect overworld"]+expect
  cases.append({"name":"birch_bridge_"+name,"base":str(fixture.resolve()),"steps":steps})
 for index,want in[(0,1),(1,0)]:
  c=json.loads(json.dumps(cases[index]));c["name"]+="_negative_control";c["xfail"]=True;c["steps"].append(f"expect saw {T} = {want}");cases.append(c)
 assert len(cases)==12
 (a.output/"cases.jsonl").write_text("\n".join(json.dumps(c)for c in cases)+"\n")
 protected={Path(c["base"]):sha(Path(c["base"]))for c in cases}
 if a.run:
  report["executed"]=True
  for c in cases:
   try:ok,fails=run_case(c,a.rom,str(a.output/"shots"))
   except Exception as ex:ok,fails=False,[type(ex).__name__+": "+str(ex)]
   passed=(not ok and len(fails)==1 and fails[0].startswith(c["steps"][-1]+":"))if c.get("xfail")else ok
   r={"name":c["name"],"pass":passed,"failures":fails};report["results"].append(r);print(json.dumps(r),flush=True)
 report["fixtures_unchanged"]=all(sha(p)==h for p,h in protected.items())
finally:
 report["original_save_unchanged"]=sha(a.base)==original
 report["all_pass"]=a.run and len(report["results"])==12 and all(r["pass"]for r in report["results"])and report.get("fixtures_unchanged",False)and report["original_save_unchanged"]
 (a.output/"report.json").write_text(json.dumps(report,indent=2))
 assert report["original_save_unchanged"],"Original save changed"
if a.run and not report["all_pass"]:raise SystemExit(1)
