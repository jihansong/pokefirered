#!/usr/bin/env python3
"""Directly validate native scripted/captured Pokemon encryption checksums."""
import argparse,ast,datetime,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--apply',action='store_true');a=p.parse_args()
files=[('tools/qa/johto_mahogany_native_static.py','e311453dc96cb0cbab350473439e558236a3814f4e8c2fc09cbb9602837e7949','7da8efbc2747d17d17e0cba2c68a75d0c0456c271c202173804b707e6c3ab052'),('tools/qa/johto_mahogany_native_chain.py','bd3128affafc286e223ecfbc8799accb603686d8a5532d77a542a3653b82a2b1','85614b72738f99c4b42b5806b5c568a62ccf20645ee46e668dbd9e0d7e045ddf')]
edits=[["def start_wild(e,key):","def assert_mon_legal(raw,label):\n m=Mon(bytearray(raw),0);subs=m.subs()\n decrypted=b''.join(bytes(v) for v in subs.values())\n assert len(decrypted)==48\n checksum=sum(v for (v,) in struct.iter_unpack('<H',decrypted))&0xffff\n assert checksum==struct.unpack_from('<H',raw,28)[0],(label,'encrypted Pokemon checksum mismatch')\n assert m.has_species() and raw[19]&1==0 and not m.is_egg(),(label,'invalid new Pokemon/Bad Egg flag')\n return m\ndef start_wild(e,key):"],["raw=e.read(syms['gEnemyParty'],600);mon=Mon(bytearray(raw),0)\n mon.subs()","raw=e.read(syms['gEnemyParty'],600);mon=assert_mon_legal(raw[:100],key+' scripted enemy')"],["cm=Mon(bytearray(caught),0);cm.subs();assert cm.species()==species and cm.has_species()","cm=assert_mon_legal(caught,tag+' native capture');assert cm.species()==species"]]
pending=[]
for name,before_sha,after_sha in files:
 path=a.root/name;old=path.read_text();assert hashlib.sha256(old.encode()).hexdigest()==before_sha,(name,'source differs')
 new=old
 for before,after in edits:
  assert new.count(before)==1,(name,'source anchor count')
  new=new.replace(before,after,1)
 assert hashlib.sha256(new.encode()).hexdigest()==after_sha,(name,'result hash')
 ast.parse(new);pending.append((path,old,new))
if a.apply:
 backup=a.root/'outputs'/('mahogany-native-mon-checksum-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));backup.mkdir(parents=True,exist_ok=False)
 for path,old,new in pending:
  assert path.read_text()==old
  (backup/(path.name+'.before')).write_bytes(old.encode())
 for path,old,new in pending:
  tmp=path.with_suffix('.checksum.tmp');tmp.write_bytes(new.encode());tmp.replace(path)
for path,old,new in pending:print(path,len(new.encode()),hashlib.sha256(new.encode()).hexdigest(),'applied',a.apply)
