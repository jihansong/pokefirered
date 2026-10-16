#!/usr/bin/env python3
"""Reapply only the canonical Johto Route 29 table; --write is explicit."""
from pathlib import Path
import argparse,hashlib,json
def build(root):
 p=root/"src/data/wild_encounters.json"
 old=json.loads(p.read_text())
 data=json.loads(json.dumps(old))
 entry=json.loads((root/"tools/johto/route29_wild.json").read_text())
 assert entry["map"]=="MAP_JOHTO_ROUTE29" and entry["base_label"]=="sJohtoRoute29"
 groups=[g for g in data["wild_encounter_groups"] if g["label"]=="gWildMonHeaders"]
 assert len(groups)==1 and groups[0]["for_maps"]
 rows=groups[0]["encounters"]
 hits=[i for i,e in enumerate(rows) if e["map"]==entry["map"] or e["base_label"]==entry["base_label"]]
 assert len(hits)<=1,"Duplicate or colliding Route 29 headers"
 if hits:
  assert rows[hits[0]]["map"]==entry["map"] and rows[hits[0]]["base_label"]==entry["base_label"]
  rows[hits[0]]=entry
 else:rows.append(entry)
 return (json.dumps(data,ensure_ascii=False,indent=2)+"\n").encode()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--write",action="store_true");a=ap.parse_args()
 root=Path(__file__).resolve().parents[2];p=root/"src/data/wild_encounters.json";old=p.read_bytes();new=build(root)
 if a.write and new!=old:
  from datetime import datetime,timezone
  dest=root/"work/johto-wild-backups"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
  dest.mkdir(parents=True);(dest/"wild_encounters.json").write_bytes(old);p.write_bytes(new)
 print(json.dumps({"changed":old!=new,"written":bool(a.write and old!=new),"sha256":hashlib.sha256(new).hexdigest()}))
if __name__=="__main__":main()
