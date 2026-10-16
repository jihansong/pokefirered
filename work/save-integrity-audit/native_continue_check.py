"""Normal CONTINUE only: read native RAM and compare with untouched save bytes."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct,sys
sys.dont_write_bytecode=True
AUDIT_SHA="3656fc7c3a90fe731d199e64d028787fdc35d4d60f91e59d2b1af222bedcb1fb"
EMU_SHA="c8d3ba672d7ecc84dcefab513d84223f410e9d8cb43081cee4b37555e1378e69"
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,msg):
 if not ok:raise AssertionError(msg)
def baseline(A,raw):
 require(len(raw)==131072,"Save size")
 slots=[A.slot_audit(raw,i,None)[0]for i in (0,1)]
 require(all(s["strict_valid"]for s in slots),"Both original slots must pass strict audit")
 selected=A.select_slot(slots);i=selected["strict_slot"]
 require(i is not None and i==selected["engine_model_slot"],"Ambiguous or disagreeing slot selector")
 where={s["id"]:s["physical"]for s in slots[i]["sectors"]}
 chunks=[raw[where[k]*4096:where[k]*4096+A.SIZES[k]]for k in range(14)]
 sb1=b"".join(chunks[1:5]);storage=b"".join(chunks[5:]);count=sb1[52]
 require(len(storage)==33744 and count<=6,"Storage or party bounds")
 party=[sb1[56+k*100:56+k*100+80]for k in range(count)]
 for record in [storage[4+k*80:4+(k+1)*80]for k in range(420)]+party:
  require(not A.inspect_mon(record)[0]["errors"],"Original contains an anomalous mon")
 return {"slot":i,"counter":slots[i]["counter"],"storage":storage,"party":party,"party_count":count}
def ram_address(p,n):
 return (0x02000000<=p and p+n<=0x02040000)or(0x03000000<=p and p+n<=0x03008000)
def party_differences(A,expected,native):
 result=[]
 for i in range(max(len(expected),len(native))):
  old=expected[i]if i<len(expected)else None;new=native[i]if i<len(native)else None
  if old==new:continue
  row={"index":i,"expected_present":old is not None,"native_present":new is not None,"before_means":"original save active slot","after_means":"native RAM in this snapshot"}
  if old is not None and new is not None:
   om,osub=A.inspect_mon(old);nm,nsub=A.inspect_mon(new);diff=A.difference(old,new)
   row.update(expected_sha256=sha(old),native_sha256=sha(new),header_byte_differences=[v for v in diff if v["offset"]<32],encrypted_byte_differences=[v for v in diff if v["offset"]>=32],canonical_byte_differences={k:A.difference(osub[k],nsub[k])for k in "GAEM"if osub[k]!=nsub[k]},expected_mon=om,native_mon=nm)
   flags=["isBadEgg","hasSpecies","isEgg","blockBoxRS","isStarterPikachu","isSnagged","unused6","unused7"]
   row["header_flag_changes"]=[{"bit":b,"name":name,"before":bool(old[19]&(1<<b)),"after":bool(new[19]&(1<<b))}for b,name in enumerate(flags)if (old[19]^new[19])&(1<<b)]
  result.append(row)
 return result
def snapshot(e,A,base):
 require(e.in_overworld()and not e.quest_log_playing()and not e.reset_seen(),"Not in continued overworld")
 storage_ptr=e.ptr("gPokemonStoragePtr");party_ptr=e.sym("gPlayerParty")
 require(ram_address(storage_ptr,33744)and ram_address(party_ptr,600),"RAM pointer outside GBA RAM")
 storage=e.read(storage_ptr,33744);count=e.sym_read("gPlayerPartyCount",1)[0]
 require(count<=6,"Native party count overflow")
 party_raw=e.read(party_ptr,600);party=[party_raw[k*100:k*100+80]for k in range(count)]
 pc=[A.inspect_mon(storage[4+k*80:4+(k+1)*80])[0]for k in range(420)]
 mons=[A.inspect_mon(m)[0]for m in party]
 original_order=[A.inspect_mon(m)[0]["pid_ot"]for m in base["party"]]
 order=[m["pid_ot"]for m in mons]
 checks={"pc_all_33744_bytes_equal":storage==base["storage"],"pc_all_420_mon_checksums_flags_valid":all(not m["errors"]for m in pc),"party_count_equal":count==base["party_count"],"party_raw80_sequence_equal":party==base["party"],"party_pid_ot_order_equal":order==original_order,"party_all_checksums_flags_valid":all(not m["errors"]for m in mons)}
 mismatches=[{"index":k,"box":k//30+1,"cell":k%30+1,"expected_sha256":sha(base["storage"][4+k*80:4+(k+1)*80]),"native_sha256":sha(storage[4+k*80:4+(k+1)*80]),"errors":pc[k]["errors"]}for k in range(420)if storage[4+k*80:4+(k+1)*80]!=base["storage"][4+k*80:4+(k+1)*80]or pc[k]["errors"]]
 return {"frame":e.frame(),"callback2":e.callback2(),"location":e.location(),"storage_pointer":storage_ptr,"storage_sha256":sha(storage),"party_count":count,"party_raw80_sha256":[sha(m)for m in party],"party_pid_ot_order":order,"party_errors":[m["errors"]for m in mons],"party_mismatches":party_differences(A,base["party"],party),"checks":checks,"pc_mismatches":mismatches,"pc_prefix_equal":storage[:4]==base["storage"][:4],"pc_names_wallpapers_equal":storage[33604:]==base["storage"][33604:],"first_storage_diff_offsets":[i for i,(x,y)in enumerate(zip(storage,base["storage"]))if x!=y][:32],"pass":all(checks.values())}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--rom",nargs=2,required=True,metavar=("PATH","SHA256"));ap.add_argument("--sym",nargs=2,required=True,metavar=("PATH","SHA256"));ap.add_argument("--save",nargs=2,action="append",required=True,metavar=("PATH","SHA256"));ap.add_argument("--audit",type=Path,required=True);ap.add_argument("--qa-dir",type=Path,default=Path("tools/qa"));ap.add_argument("--timeout",type=int,default=6000);a=ap.parse_args()
 rom=Path(a.rom[0]).resolve();sym=Path(a.sym[0]).resolve();qa=a.qa_dir.resolve();aud=a.audit.resolve()
 protected={rom:a.rom[1],sym:a.sym[1],aud:AUDIT_SHA,qa/"emu.py":EMU_SHA}
 for path,h in a.save:protected[Path(path).resolve()]=h
 for path,h in protected.items():require(digest(path)==h,"SHA mismatch: "+str(path))
 require(sym.stat().st_mtime>=rom.stat().st_mtime,"Run make syms for this ROM before QA")
 lib=qa/"libqa.so";libc=qa/"libqa.c"
 require(lib.is_file()and libc.is_file()and lib.stat().st_mtime>=libc.stat().st_mtime,"Prebuild libqa.so; harness must not trigger a build")
 protected[lib]=digest(lib)
 spec=importlib.util.spec_from_file_location("readonly_save_audit",aud);A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
 require(A.OFF=={"sb1":15720,"sb2":3876,"storage":33744,"storage.boxes":4,"boxmon":80,"pokemon":100,"sb1.playerParty":56,"sb1.playerPartyCount":52},"Auditor layout")
 sys.path.insert(0,str(qa))
 from emu import Emu
 report={"schema":"thunder-yellow-normal-continue-load-v1","rom_sha256":a.rom[1],"sym_sha256":a.sym[1],"input_save_count":len(a.save),"code_injection":False,"memory_writes":False,"binary_patch":False,"save_mutation_requested":False,"saves":[]}
 for path,expected in a.save:
  source=Path(path).resolve();case={"path":str(source),"original_sha256":expected,"pass":False}
  try:
   require(digest(source)==expected and digest(rom)==a.rom[1]and digest(sym)==a.sym[1],"Input changed before case")
   base=baseline(A,source.read_bytes());case.update(active_slot=base["slot"],counter=base["counter"],expected_storage_sha256=sha(base["storage"]))
   with Emu(str(rom),str(source),sym=str(sym))as e:
    required=("gPokemonStoragePtr","gPlayerParty","gPlayerPartyCount","gMain","CB2_MainMenu","CB2_Overworld","gQuestLogState","gQuestLogPlaybackState")
    require(all(n in e.syms for n in required),"Required symbols absent")
    require(Path(e.sav_path).resolve()!=source and digest(e.sav_path)==expected,"Emulator save is not an exact temporary copy")
    case["temporary_save_copy_verified"]=True;case["boot_frames"]=e.boot_continue(timeout=a.timeout)
    case["after_continue"]=snapshot(e,A,base)
    e.hold();e.run(180)
    case["after_idle_180"]=snapshot(e,A,base)
    case["pass"]=case["after_continue"]["pass"]and case["after_idle_180"]["pass"]
  except Exception as err:case["error"]=type(err).__name__+": "+str(err)
  case["source_unchanged"]=digest(source)==expected
  case["pass"]=case["pass"]and case["source_unchanged"];report["saves"].append(case)
 report["protected_inputs_unchanged"]={str(p):digest(p)==h for p,h in protected.items()}
 report["all_pass"]=all(c["pass"]for c in report["saves"])and all(report["protected_inputs_unchanged"].values())
 report["limits"]=["Normal boot and 180 idle frames only; does not reproduce every gameplay/save/load path or DELTA.","PC comparison includes box names/wallpapers. Party comparison uses each exact encrypted 80-byte BoxPokemon in original order; runtime HP/status bytes are outside this comparison.","No in-game save is requested and no original save is replaced."]
 print(json.dumps(report,indent=2))
 return 0 if report["all_pass"]else 1
if __name__=="__main__":sys.exit(main())
