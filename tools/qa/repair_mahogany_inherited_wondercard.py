#!/usr/bin/env python3
"""Verify exact inherited optional Wonder Card service instead of ordinary NPC access."""
import argparse,ast,datetime,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--apply',action='store_true');a=p.parse_args()
path=a.root/'tools/johto/build_mahogany.py';old=path.read_text()
assert hashlib.sha256(old.encode()).hexdigest()=='044ca7fc150e7973efc7f80848d5bbf951b6052a9b91e1a9ee63ce63416a14f8'
before="assert any(z in seen for z in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),(n,'NPC cannot be faced',o)"
after="if gfx=='OBJ_EVENT_GFX_MG_DELIVERYMAN' and inherited_portals:\n    # This original optional service is activated by saved Wonder Cards.\n    assert o in expected_objects and (x,y)==(1,2) and o['script']=='CableClub_EventScript_MysteryGiftMan'\n    assert o['flag']=='FLAG_HIDE_MG_DELIVERYMEN'\n    prior_script=s.text('data/maps/OlivineCity_PokemonCenter_2F/scripts.inc')\n    expected_script=prior_script.replace('OLIVINE_CITY','MAHOGANY_TOWN').replace('OLIVINE','MAHOGANY').replace('OlivineCity','MahoganyTown')\n    assert final.text('data/maps/'+n+'/scripts.inc')==expected_script,'original CableClub map callbacks changed'\n    assert 'CableClub_OnTransition' in expected_script\n    cable=s.text('data/scripts/cable_club.inc')\n    assert all(token in cable for token in ['call CableClub_EventScript_HideOrShowMysteryGiftMan','specialvar VAR_RESULT, ValidateSavedWonderCard','setflag FLAG_HIDE_MG_DELIVERYMEN','clearflag FLAG_HIDE_MG_DELIVERYMEN','trywondercardscript'])\n    continue\n   assert any(z in seen for z in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),(n,'NPC cannot be faced',o)"
assert old.count(before)==1
new=old.replace(before,after,1)
assert hashlib.sha256(new.encode()).hexdigest()=='0e6e6d174025fd4d0ac208c4a780737a5ce045e5c710b0d80f494adf8fc129b9'
ast.parse(new)
if a.apply:
 backup=a.root/'outputs'/('mahogany-inherited-wondercard-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));backup.mkdir(parents=True,exist_ok=False)
 (backup/'build_mahogany.before.py').write_bytes(path.read_bytes())
 assert path.read_text()==old
 tmp=path.with_suffix('.gift-service-check.tmp');tmp.write_bytes(new.encode());tmp.replace(path)
print('WONDERCARD_SERVICE_PRESERVATION_PASS',len(new.encode()),hashlib.sha256(new.encode()).hexdigest(),'applied',a.apply)
