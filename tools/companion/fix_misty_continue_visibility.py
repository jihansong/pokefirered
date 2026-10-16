#!/usr/bin/env python3
"""Exact native-confirmed Misty Continue visibility fix. Dry unless --apply."""
from pathlib import Path
import argparse,datetime,hashlib,json
ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');a=ap.parse_args()
root=Path('/workspaces/pokefirered').resolve();H=lambda b:hashlib.sha256(b).hexdigest()
old='        if (FlagGet(FLAG_HIDE_MISTY_PALLET)) FlagClear(FLAG_HIDE_MISTY_PALLET);';new='        if (FlagGet(FLAG_HIDE_MISTY_PALLET))\n        {\n            FlagClear(FLAG_HIDE_MISTY_PALLET);\n            // Continue can omit OnTransition and already skipped this hidden NPC.\n            // Spawn only the newly revealed static NPC, once on this flag edge.\n            TrySpawnObjectEvent(LOCALID_PALLET_MISTY,\n                gSaveBlock1Ptr->location.mapNum, gSaveBlock1Ptr->location.mapGroup);\n        }'
cp=root/'src/companion_misty.c';pp=root/'tools/companion/misty_source_payload.json';sp=root/'outputs/misty-companion-v1/applied-state.json'
source=cp.read_bytes();payload=pp.read_bytes();state=sp.read_bytes();s=source.decode();p=payload.decode();st=json.loads(state)
assert H(source)=='6f5b1fda8545b54441a632cac2e73b93d5a73a3af7f9c0407755c9acb29a8e4c' and H(payload)=='a68da6b2cd968888c410556e57e0ee0afd416b9a42f64caa2341db81e8bafcd7'
assert st['hashes']['src/companion_misty.c']==H(source)
assert H((root/'include/event_object_movement.h').read_bytes())=='ecc4e09bfcb981fdab022c2da77ffb0e734e9dfcdacc8ab8f54667dd656aad44'
assert H((root/'src/event_object_movement.c').read_bytes())=='241a15df4e9977c0fb3a8e84507623476470f18de0a1862a8457bb96fbf6a420'
assert 'u8 TrySpawnObjectEvent(u8 localId, u8 mapNum, u8 mapGroup);' in (root/'include/event_object_movement.h').read_text()
assert s.count(old)==1;s2=s.replace(old,new)
escape=lambda t:json.dumps(t)[1:-1]
assert p.count(escape(old))==1;p2=p.replace(escape(old),escape(new))
assert json.loads(p2)['files']['src/companion_misty.c']==s2
assert H(s2.encode())=='dfaa0fa32d1dd0128132e6d4d7ac986c874a02fded2c06b9d6a1a3f226f9b402' and H(p2.encode())=='8f04e68b18afe2930e03d8c304616d090e73bd4e94c8da78b144e88ae3fdc8c6'
st['hashes']['src/companion_misty.c']=H(s2.encode())
report=dict(dry_pass=True,applied=False,product_sha256=H(s2.encode()),payload_sha256=H(p2.encode()),new_RAM_or_save_fields=0,automatic_prompt_rearmed=False,native_fix_retest_pending=True)
if a.apply:
 utc=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup=root/'outputs/misty-companion-v1/continue-fix-backups'/utc;backup.mkdir(parents=True,exist_ok=False)
 for path,data in [(cp,source),(pp,payload),(sp,state)]:
  assert path.resolve().is_relative_to(root);dest=backup/path.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 cp.write_text(s2);pp.write_text(p2);sp.write_text(json.dumps(st,indent=2)+'\n');report['applied']=True;report['backup']=str(backup)
print(json.dumps(report,indent=2))
