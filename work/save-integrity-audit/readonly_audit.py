"""Read-only Gen3 save audit. Reads explicit files; emits JSON to stdout only."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,json,struct
ORDERS=("GAEM","GAME","GEAM","GEMA","GMAE","GMEA","AGEM","AGME","AEGM","AEMG","AMGE","AMEG","EGAM","EGMA","EAGM","EAMG","EMGA","EMAG","MGAE","MGEA","MAGE","MAEG","MEGA","MEAG")
SECTOR=4096;DATA=3968;FOOTER=4084;SIGNATURE=0x08012025
OFF={"sb1":15720,"sb2":3876,"storage":33744,"storage.boxes":4,"boxmon":80,"pokemon":100,"sb1.playerParty":56,"sb1.playerPartyCount":52}
SIZES=[3876,3968,3968,3968,3816]+[3968]*8+[2000]
def sha(data):return hashlib.sha256(data).hexdigest()
def u16(data,o=0):return struct.unpack_from("<H",data,o)[0]
def u32(data,o=0):return struct.unpack_from("<I",data,o)[0]
def sector_sum(data):
 total=sum(x[0]for x in struct.iter_unpack("<I",data))&0xffffffff
 return (total+(total>>16))&65535
def difference(a,b):
 return [{"offset":i,"before":x,"after":y,"xor":x^y,"bits":[j for j in range(8)if (x^y)>>j&1]}for i,(x,y)in enumerate(zip(a,b))if x!=y]
def inspect_mon(raw,meta=None):
 assert len(raw)==80
 pid,ot=struct.unpack_from("<II",raw);key=pid^ot
 decrypted=b"".join(struct.pack("<I",v[0]^key)for v in struct.iter_unpack("<I",raw[32:]))
 order=ORDERS[pid%24];sub={k:decrypted[j*12:(j+1)*12]for j,k in enumerate(order)}
 species,item,exp=struct.unpack_from("<HHI",sub["G"]);ivs=u32(sub["M"],4);flags=raw[19]
 stored=u16(raw,28);computed=sum(struct.unpack("<24H",decrypted))&65535
 occupied=bool(species or flags&7);errors=[]
 if flags&1:errors.append("bad_egg_flag")
 if stored!=computed:errors.append("mon_checksum")
 if bool(flags&4)!=bool(ivs&(1<<30)):errors.append("egg_flag_disagreement")
 if bool(flags&2)!=bool(species):errors.append("has_species_disagreement")
 annotation=None
 if occupied and meta:
  info=meta["species"].get(str(species))
  if not info:errors.append("species_not_in_metadata")
  else:
   table=meta["experience"][info["growth"]]
   level=max([i for i in range(1,101)if table[i]<=exp],default=0)
   annotation={"source":"provided metadata; not inferred from save","name":info["name"],"national":info["national"],"level_if_exp_valid":level,"exp_above_max":exp>table[100]}
   if exp>table[100]:errors.append("experience_above_level100")
 without_egg=bytearray(decrypted);mpos=order.index("M")*12+4
 struct.pack_into("<I",without_egg,mpos,ivs&~(1<<30))
 projected=sum(struct.unpack("<24H",without_egg))&65535
 result={"pid_ot":f"{pid:08x}:{ot:08x}","identity_names_sha256":sha(raw[:19]+raw[20:27]),"origin_ivs_sha256":sha(raw[:8]+raw[18:19]+raw[20:27]+sub["M"][:4]+struct.pack("<I",ivs&~(1<<30))),"raw_sha256":sha(raw),"flags":flags,"bad_egg":bool(flags&1),"header_egg":bool(flags&4),"secure_egg":bool(ivs&(1<<30)),"checksum_stored":stored,"checksum_computed":computed,"checksum_valid":stored==computed,"occupied":occupied,"errors":errors,"decoded":{"trusted_checksum":stored==computed,"species":species,"item":item,"experience":exp,"friendship":sub["G"][9],"moves":list(struct.unpack_from("<4H",sub["A"])),"pp":list(sub["A"][8:]),"order":order},"annotation":annotation,"hypothetical_without_secure_egg_checksum":projected,"hypothetical_residual_mod65536":(projected-stored)&65535}
 return result,sub
def spans(where,base,start,length):
 result=[];pos=start;end=start+length
 while pos<end:
  chunk,inside=divmod(pos,DATA);sid=base+chunk;n=min(end-pos,DATA-inside)
  result.append({"logical_sector":sid,"physical_sector":where[sid],"file_offset":where[sid]*SECTOR+inside,"bytes":n})
  pos+=n
 assert sum(v["bytes"]for v in result)==length
 return result
def slot_audit(raw,index,meta):
 sectors=[];seen=defaultdict(list)
 for relative in range(14):
  physical=index*14+relative;start=physical*SECTOR;sid,stored,signature,counter=struct.unpack_from("<HHII",raw,start+FOOTER)
  length=SIZES[sid]if sid<14 else None
  computed=sector_sum(raw[start:start+length])if length is not None else None
  row={"physical":physical,"relative":relative,"id":sid,"counter":counter,"signature_valid":signature==SIGNATURE,"stored_checksum":stored,"computed_checksum":computed,"checksum_valid":stored==computed,"checksum_bytes":length,"rotation":(relative-sid)%14 if sid<14 else None}
  sectors.append(row);seen[sid].append(row)
 coherent=set(seen)==set(range(14))and all(len(v)==1 for v in seen.values())and all(v["signature_valid"]for v in sectors)
 counters=sorted({v["counter"]for v in sectors});rotations=sorted({v["rotation"]for v in sectors if v["rotation"]is not None})
 errors=[]
 for name,okay in [("sector_ids_or_signatures",coherent),("sector_checksum",all(v["checksum_valid"]for v in sectors)),("mixed_counters",len(counters)==1),("rotation",len(rotations)==1),("counter_parity",all(v["counter"]%2==index for v in sectors))]:
  if not okay:errors.append(name)
 accepted=[v for v in sectors if v["signature_valid"]and v["checksum_valid"]and v["id"]<14]
 mask=0
 for v in accepted:mask|=1<<v["id"]
 engine={"defined":all(v["id"]<14 for v in sectors if v["signature_valid"]),"accepted_id_mask":mask,"slot_ok":mask==0x3fff,"last_valid_physical_counter":accepted[-1]["counter"]if accepted else None}
 result={"engine":engine,"slot":index,"counter":counters[0]if len(counters)==1 else None,"rotation":rotations[0]if len(rotations)==1 else None,"strict_valid":not errors,"errors":errors,"sectors":sectors,"records":[]}
 if not coherent:return result,[]
 where={sid:seen[sid][0]["physical"]for sid in range(14)}
 chunks=[raw[where[i]*SECTOR:where[i]*SECTOR+SIZES[i]]for i in range(14)]
 sb1=b"".join(chunks[1:5]);storage=b"".join(chunks[5:]);assert len(sb1)==15720 and len(storage)==33744
 party_count=sb1[52];result["party_count"]=party_count;result["party_count_valid"]=party_count<=6
 result["pc_bounds"]={"records_begin":4,"records_end_exclusive":33604,"storage_size":len(storage),"tail_bytes":len(storage)-33604,"current_box":storage[0],"current_box_valid":storage[0]<14,"prefix_sha256":sha(storage[:4]),"names_wallpapers_sha256":sha(storage[33604:]),"storage_sha256":sha(storage)}
 locations=[("pc",i,storage[4+i*80:4+(i+1)*80],spans(where,5,4+i*80,80))for i in range(420)]
 locations += [("party"if i<party_count else"party_unused",i,sb1[56+i*100:56+i*100+80],spans(where,1,56+i*100,80))for i in range(6)]
 internals=[];summary=Counter()
 for area,i,record,parts in locations:
  mon,subs=inspect_mon(record,meta);summary[area+"_slots_scanned"]+=1
  if mon["occupied"]:summary[area+"_occupied"]+=1
  if mon["errors"]:summary[area+"_anomalies"]+=1
  if not mon["occupied"]and not mon["errors"]:continue
  mon.update(area=area,index=i,physical_spans=parts,slot_bytes_trusted=not errors,live_member=area!="party_unused")
  if area=="pc":mon.update(box=i//30+1,cell=i%30+1,crosses_sector_boundary=len(parts)>1)
  result["records"].append(mon);internals.append((mon,record,subs))
 result["summary"]=dict(summary)
 result["pc_crossing_indices"]=[i for i in range(420)if len(spans(where,5,4+i*80,80))>1]
 return result,internals
def select_slot(slots):
 good=[s for s in slots if s["strict_valid"]];strict=None;reason="no_strict_valid_slot";delta=None
 if len(good)==1:strict=good[0]["slot"];reason="one_strict_valid_slot"
 elif len(good)==2:
  a,b=slots[0]["counter"],slots[1]["counter"];delta=(b-a)&0xffffffff
  strict=None if delta in (0,0x80000000)else int(delta<0x80000000)
  reason="ambiguous_counter"if strict is None else"unsigned_serial_order"
 engine_good=[s for s in slots if s["engine"]["slot_ok"]];engine_counter=None
 engine_defined=all(s["engine"]["defined"]for s in slots)
 if engine_defined and engine_good:
  engine_counter=engine_good[0]["engine"]["last_valid_physical_counter"]
  if len(engine_good)==2:
   a,b=[s["engine"]["last_valid_physical_counter"]for s in slots]
   engine_counter=0 if {a,b}=={0xffffffff,0}else max(a,b)
 engine_slot=None if engine_counter is None else engine_counter%2
 return {"strict_slot":strict,"reason":reason,"counter_delta_1_minus_0":delta,"engine_model_defined":engine_defined,"engine_model_counter":engine_counter,"engine_model_slot":engine_slot,"model_disagreement":strict!=engine_slot,"engine_model_source_sha256":"24f0b70d72cc83c50f7b2d6d73cb211c9b1272ab5fa40dc1d553ad48d1f4511c","engine_runtime_load_tested":False}
def audit(inputs,meta=None):
 report={"schema":"thunder-yellow-readonly-save-audit-v1","offset_assumptions":OFF,"slots_per_file":2,"sector_checksum_sizes":SIZES,"save_files_written":False,"repairs_performed":False,"root_cause_proven":False,"files":[],"identity_groups":[],"active_file_comparisons":[]}
 groups=defaultdict(list);snapshots=[];paths_before={}
 for fileid,(path,expected)in enumerate(inputs):
  path=Path(path).resolve();raw=path.read_bytes();digest=sha(raw)
  if expected and digest!=expected:raise ValueError("Input SHA changed: "+str(path))
  paths_before[path]=digest
  entry={"file_id":fileid,"path":str(path),"bytes":len(raw),"sha256":digest,"expected_sha256":expected,"slots":[]}
  report["files"].append(entry)
  if len(raw)!=131072:entry["error"]="expected_exact_128KiB_FLASH; no guessed truncation";snapshots.append({});continue
  pending=[]
  for index in (0,1):
   s,records=slot_audit(raw,index,meta);entry["slots"].append(s)
   pending += [(index,m,r,d)for m,r,d in records]
  selection=select_slot(entry["slots"]);entry["selection"]=selection
  entry["special_sectors"]=[{"physical":i,"sha256":sha(raw[i*SECTOR:(i+1)*SECTOR]),"validation":"not interpreted as normal save slot; HOF/eReader separate format"}for i in range(28,32)]
  live=defaultdict(list)
  for slot,m,r,d in pending:
   m["ref"]={"file_id":fileid,"slot":slot,"active":slot==selection["strict_slot"],"area":m["area"],"index":m["index"]}
   groups[m["pid_ot"]].append((m,r,d))
   if m["ref"]["active"]and m["live_member"]and m["occupied"]:live[m["pid_ot"]].append(m)
  snapshots.append(live)
 for identity,rows in sorted(groups.items()):
  if not any(m["errors"]for m,r,d in rows):continue
  variants=defaultdict(list)
  for m,r,d in rows:variants[sha(r)].append((m,r,d))
  result={"pid_ot":identity,"candidate_identity_only_not_unique_proof":True,"occurrences":[m["ref"]for m,r,d in rows],"variants":[],"differences":[],"duplicate_pid_ot_within_slot":[]}
  locations=Counter((m["ref"]["file_id"],m["ref"]["slot"])for m,r,d in rows if m["occupied"]and m["live_member"])
  result["duplicate_pid_ot_within_slot"]=[{"file_id":f,"slot":s,"count":n}for(f,s),n in locations.items()if n>1]
  for digest,vr in variants.items():
   m,r,d=vr[0];result["variants"].append({"raw_sha256":digest,"raw_hex":r.hex(),"canonical_substructures":{k:v.hex()for k,v in d.items()},"errors":m["errors"],"trusted_donor_occurrences":[x["ref"]for x,_,_ in vr if not x["errors"]and x["slot_bytes_trusted"]and x["live_member"]],"identity_names_sha256":m["identity_names_sha256"],"origin_ivs_sha256":m["origin_ivs_sha256"]})
  representatives=[min(vr,key=lambda row:(bool(row[0]["errors"]),not row[0]["slot_bytes_trusted"],not row[0]["live_member"]))for vr in variants.values()]
  for j,(bad,braw,bsub)in enumerate(representatives):
   if not bad["errors"]:continue
   healthy=[(m,r,d)for m,r,d in representatives if not m["errors"]and m["slot_bytes_trusted"]and m["live_member"]]
   for good,graw,gsub in healthy:
    result["differences"].append({"from_healthy":good["raw_sha256"],"to_anomalous":bad["raw_sha256"],"same_names_language":good["identity_names_sha256"]==bad["identity_names_sha256"],"same_origin_ivs":good["origin_ivs_sha256"]==bad["origin_ivs_sha256"],"raw_bytes":difference(graw,braw),"canonical_bytes":{k:difference(gsub[k],bsub[k])for k in "GAEM"if gsub[k]!=bsub[k]},"exact_original_restoration_authorized":False})
  report["identity_groups"].append(result)
 for a in range(len(inputs)):
  for b in range(a+1,len(inputs)):
   left,right=snapshots[a],snapshots[b];common=set(left)&set(right);changes=[]
   for identity in sorted(common):
    x,y=left[identity],right[identity];mx=Counter(m["raw_sha256"]for m in x);my=Counter(m["raw_sha256"]for m in y)
    if mx!=my:changes.append({"pid_ot":identity,"left":dict(mx),"right":dict(my),"pairing_ambiguous":len(x)!=1 or len(y)!=1,"left_anomalies":sum(bool(m["errors"])for m in x),"right_anomalies":sum(bool(m["errors"])for m in y)})
   report["active_file_comparisons"].append({"left_file_id":a,"right_file_id":b,"chronological_order_not_assumed":True,"shared_pid_ot":len(common),"only_left":sorted(set(left)-set(right)),"only_right":sorted(set(right)-set(left)),"changed_record_groups":changes})
 report["all_inputs_unchanged"]=all(sha(p.read_bytes())==d for p,d in paths_before.items())
 if not report["all_inputs_unchanged"]:raise RuntimeError("An input changed during read-only scan")
 report["limitations"]=["PID/OT collisions, duplicated Pokemon and legitimate edits must be reviewed; no automatic donor replacement.","Invalid-checksum decoded fields are clues, not authenticated original values.","Sector-valid/mon-invalid means the invalid bytes were committed with valid outer checksums; it does not identify the producer or root cause.","Party unused entries are reported separately and are not treated as live party Pokemon.","No global chronology inferred from save names, mtime, or counters from different save lineages.","Static checksum audit does not reproduce DELTA runtime corruption; no ROM compatibility claim without matching source offsets."]
 return report
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--save",nargs=2,action="append",metavar=("PATH","SHA256"),required=True);ap.add_argument("--metadata",type=Path);ap.add_argument("--rom",nargs=2,metavar=("PATH","SHA256"));args=ap.parse_args()
 for path,digest in args.save:
  if len(digest)!=64 or any(c not in"0123456789abcdef"for c in digest):raise ValueError("Expected lowercase SHA256 for "+path)
 meta=None
 if args.metadata:
  raw=args.metadata.read_bytes();meta=json.loads(raw)
  assert all(meta["offsets"].get(k)==v for k,v in OFF.items()),"Metadata layout differs; review before reading"
  assert meta["constants"]["TOTAL_BOXES_COUNT"]==14 and meta["constants"]["IN_BOX_COUNT"]==30
 result=audit(args.save,meta)
 if meta:result["metadata"]={"path":str(args.metadata.resolve()),"sha256":sha(raw),"rom_sha256":meta.get("rom_sha256"),"source_head":meta.get("head"),"fresh_rom_match_claimed":False}
 if args.rom:
  rp=Path(args.rom[0]);rb=rp.read_bytes();rs=sha(rb)
  assert rs==args.rom[1],"ROM SHA changed"
  assert len(rb)>=192 and len(rb)<=32*1024*1024,"Unexpected GBA size"
  result["rom"]={"path":str(rp.resolve()),"bytes":len(rb),"sha256":rs,"game_code_hex":rb[172:176].hex(),"header_checksum_valid":((-sum(rb[160:189])-25)&255)==rb[189],"metadata_rom_exact_match":bool(meta and meta.get("rom_sha256")==rs),"save_contains_no_binding_to_this_rom_hash":True}
  assert sha(rp.read_bytes())==rs,"ROM changed during inspection"
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
