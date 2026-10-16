#!/usr/bin/env python3
"""Keep original scripted PC services distinct from walkable stairs."""
import argparse,ast,datetime,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--apply',action='store_true');a=p.parse_args()
path=a.root/'tools/johto/build_mahogany.py';old=path.read_text()
assert hashlib.sha256(old.encode()).hexdigest()=='44e82b3551b3cdc3698320a980ab81443ce7c824c186a08120b3c1527ad7ef66'
edits=[["if n not in maps:continue\n  def walk(x,y):","if n not in maps:continue\n  inherited_portals=[]\n  if n.endswith('PokemonCenter_2F'):\n   old_pc=s.json('data/maps/OlivineCity_PokemonCenter_2F/map.json')\n   assert m['layout']==old_pc['layout']\n   old_layout=ls[old_pc['layout']]\n   assert raw==s.read(old_layout['blockdata_filepath']),'native link-room geometry changed'\n   expected_objects=json.loads(json.dumps(old_pc['object_events']).replace('OLIVINE_CITY','MAHOGANY_TOWN').replace('OLIVINE','MAHOGANY').replace('OlivineCity','MahoganyTown'))\n   assert m['object_events']==expected_objects,'native link-room service objects/scripts changed'\n   inherited_portals=[p for p in old_pc['warp_events'] if p['dest_map'] in ('MAP_UNION_ROOM','MAP_TRADE_CENTER')]\n   assert len(inherited_portals)==2 and all(p in m['warp_events'] for p in inherited_portals)\n  def walk(x,y):"],["assert z in seen,(n,'unreachable native warp',wp,z)","assert z in seen or wp in inherited_portals,(n,'unreachable native warp',wp,z)"],["if gfx=='OBJ_EVENT_GFX_CLERK':continue\n   assert walk(x,y)","if gfx=='OBJ_EVENT_GFX_CLERK':continue\n   if gfx=='OBJ_EVENT_GFX_CABLE_CLUB_RECEPTIONIST' and inherited_portals:\n    assert behavior(l,a[(y+1)*w+x])==values['MB_COUNTER'] and (x,y+2) in seen,(n,'unreachable native service counter',o)\n    continue\n   assert walk(x,y)"]]
new=old
for before,after in edits:
 assert new.count(before)==1
 new=new.replace(before,after,1)
assert hashlib.sha256(new.encode()).hexdigest()=='044ca7fc150e7973efc7f80848d5bbf951b6052a9b91e1a9ee63ce63416a14f8'
ast.parse(new)
if a.apply:
 backup=a.root/'outputs'/('mahogany-native-link-services-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));backup.mkdir(parents=True,exist_ok=False)
 (backup/'build_mahogany.before.py').write_bytes(path.read_bytes())
 assert path.read_text()==old
 tmp=path.with_suffix('.link-service-check.tmp');tmp.write_bytes(new.encode());tmp.replace(path)
print('NATIVE_LINK_SERVICE_CHECKER_PASS',len(new.encode()),hashlib.sha256(new.encode()).hexdigest(),'applied',a.apply)
