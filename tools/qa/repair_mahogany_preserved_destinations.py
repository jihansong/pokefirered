#!/usr/bin/env python3
"""Validate preserved destination metadata instead of rejecting native PC link rooms."""
import argparse,ast,datetime,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--apply',action='store_true');a=p.parse_args()
path=a.root/'tools/johto/build_mahogany.py';old=path.read_text()
assert hashlib.sha256(old.encode()).hexdigest()=='4713a36c36660344ce1d6f92e8b65ed6aa6f1c6377d16d1c5457ea64745c488f'
before="if dst_name is None:\n    assert wp['dest_map']=='MAP_ECRUTEAK_CITY'\n    dst=behavior_maps['EcruteakCity']\n   else:dst=maps[dst_name]"
after="if dst_name is None:\n    # Preserve and validate the old city's six exits and the native PC link rooms.\n    allowed=OLD if n=='EcruteakCity' else (['UnionRoom','TradeCenter'] if n.endswith('PokemonCenter_2F') else ['EcruteakCity'])\n    matches=[]\n    for name in allowed:\n     candidate=final.json('data/maps/'+name+'/map.json')\n     if candidate['id']==wp['dest_map']:matches.append(candidate)\n    assert len(matches)==1,(n,'unknown or ambiguous preserved destination',wp)\n    dst=matches[0]\n   else:dst=maps[dst_name]"
assert old.count(before)==1
new=old.replace(before,after,1)
assert hashlib.sha256(new.encode()).hexdigest()=='44e82b3551b3cdc3698320a980ab81443ce7c824c186a08120b3c1527ad7ef66'
ast.parse(new)
if a.apply:
 backup=a.root/'outputs'/('mahogany-preserved-warps-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));backup.mkdir(parents=True,exist_ok=False)
 (backup/'build_mahogany.before.py').write_bytes(path.read_bytes())
 assert path.read_text()==old
 tmp=path.with_suffix('.warp-check.tmp');tmp.write_bytes(new.encode());tmp.replace(path)
print('PRESERVED_DESTINATION_CHECKER_PASS',len(new.encode()),hashlib.sha256(new.encode()).hexdigest(),'applied',a.apply)
