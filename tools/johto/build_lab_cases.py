#!/usr/bin/env python3

def lab_cases(r,base):
    """Generate expectations from the actual supplied QA save; never mutate it."""
    import sys,copy
    sys.path.insert(0,str(r/"tools/qa"))
    from savefile import SaveFile
    from gamedata import const
    s=SaveFile(str(base))
    boxed=sum(1 for m in s.box_mons()if m.has_species()and m.species()==155 and not m.is_egg())
    first=next(i for i,m in enumerate(s.box_mons())if m.has_species()and not m.is_egg())
    assert s.party_count()>=1
    prefix=["warp NewBarkTown_ElmsLab 5 6","noquestlog","party 1","mon 0 PIKACHU 50",
            "flag FLAG_GOT_CYNDAQUIL_FROM_AIDE 0","flag FLAG_GOT_CHIKORITA_FROM_AIDE 1","flag FLAG_GOT_TOTODILE_FROM_AIDE 0"]
    offer=["UP","A","mashtext NewBarkTown_ElmsLab_Text_CyndaquilOffer 60","wait 120","A"]
    accept=offer+["mashtext Text_GiveNicknameToThisMon 60","wait 120","B","mash 180","expect overworld"]
    receipt=["expect flag FLAG_GOT_CYNDAQUIL_FROM_AIDE = 1","expect flag FLAG_GOT_CHIKORITA_FROM_AIDE = 1",
             "expect flag FLAG_GOT_TOTODILE_FROM_AIDE = 0",f"expect count CYNDAQUIL = {boxed+1}"]
    cases=[]
    def add(name,edits,steps,xf=False):
        c=dict(name="j1_lab_"+name,base=str(base),edit=prefix+edits,steps=steps)
        if xf:c["xfail"]=True
        cases.append(c)
    add("gift_party",[],accept+receipt+["expect mon CYNDAQUIL metloc=MAPSEC_NEW_BARK_TOWN metlvl=5 where=party",
                                       "shot received_party","A","mash 150",f"expect count CYNDAQUIL = {boxed+1}"])
    add("decline",[],offer[:-1]+["B","mash 100","expect overworld","expect flag FLAG_GOT_CYNDAQUIL_FROM_AIDE = 0",f"expect count CYNDAQUIL = {boxed}"])
    fullparty=[]
    for i in range(1,6):fullparty +=[f"frombox {first} {i}",f"mon {i} PIKACHU 50"]
    assert any(not m.has_species()for m in s.box_mons()),"Need one free PC slot for PC delivery case"
    add("gift_pc",fullparty,accept+receipt+["expect mon CYNDAQUIL metloc=MAPSEC_NEW_BARK_TOWN metlvl=5 where=box","shot received_pc"])
    add("no_room_retry_pending",fullparty+["fillboxes"],offer+["mash 160","expect overworld","expect flag FLAG_GOT_CYNDAQUIL_FROM_AIDE = 0",f"expect count CYNDAQUIL = {boxed}","shot no_room"])
    add("party_room_pc_full",["fillboxes"],accept+receipt+["expect mon CYNDAQUIL metloc=MAPSEC_NEW_BARK_TOWN metlvl=5 where=party"])
    add("legacy_receipt_even_after_release",["flag FLAG_GOT_CYNDAQUIL_FROM_AIDE 1"],["UP","A","mash 160","expect overworld",f"expect count CYNDAQUIL = {boxed}","expect flag FLAG_GOT_CYNDAQUIL_FROM_AIDE = 1","shot legacy_receipt"])
    add("negative_duplicate",["flag FLAG_GOT_CYNDAQUIL_FROM_AIDE 1"],["UP","A","mash 160",f"expect count CYNDAQUIL = {boxed+1}"],True)
    add("negative_full_consumed",fullparty+["fillboxes"],offer+["mash 160","expect flag FLAG_GOT_CYNDAQUIL_FROM_AIDE = 1"],True)
    return cases

def main():
    import argparse,hashlib,json,pathlib
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=pathlib.Path,default=pathlib.Path("/workspaces/pokefirered"))
    ap.add_argument("--base",type=pathlib.Path,default=pathlib.Path("saves/hoenn.sav"))
    ap.add_argument("--output",type=pathlib.Path,default=pathlib.Path("tools/qa/cases/johto_lab.jsonl"))
    a=ap.parse_args();r=a.root.resolve()
    base=a.base.resolve()if a.base.is_absolute()else(r/a.base).resolve()
    dest=a.output.resolve()if a.output.is_absolute()else(r/a.output).resolve()
    assert dest!=base and r in dest.parents
    before=hashlib.sha256(base.read_bytes()).hexdigest()
    rows=lab_cases(r,base)
    data="# Generated expectations; runtime NOT RUN.\n"+''.join(json.dumps(c)+"\n"for c in rows)
    if dest.exists():assert dest.read_text()==data,"Different existing QA file; preserve and inspect it"
    else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(data)
    assert hashlib.sha256(base.read_bytes()).hexdigest()==before
    print(json.dumps({"cases":len(rows),"original_save_unchanged":True,"base_sha256":before,"runtime":"NOT RUN"}))
if __name__=="__main__":main()
