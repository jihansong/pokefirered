#!/usr/bin/env python3
"""Blackthorn native QA; original SAV read-only and native inputs only."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_blackthorn_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='2a96b6d26b6f0abbb7a6cc2444ef887cf5e709d8f2373bd2698b086e3d17d032'
exec(compile(_boot_text,str(_boot),'exec'),globals())

cases=[]
def link(tag,where,key,dest):cases.append(dict(name=tag,where=where,key=key,dest=dest))
R44='JohtoRoute44';I1='IcePath_1F';IB='IcePath_B1F';I2='IcePath_B2F';CITY='BlackthornCity'
PC1=CITY+'_PokemonCenter_1F';PC2=CITY+'_PokemonCenter_2F';MART=CITY+'_Mart';GYM=CITY+'_Gym';DEN='DragonDen_1F';SHRINE='DragonDen_Shrine'
link('mahogany_into_route44',('MahoganyTown',30,16),'RIGHT',R44)
link('route44_back_mahogany',(R44,1,16),'LEFT','MahoganyTown')
link('route44_into_ice_path',(R44,40,6),'UP',I1)
link('ice_path_back_route44',(I1,4,21),'DOWN',R44)
link('ice_path_first_descends',(I1,22,4),'UP',IB)
link('ice_path_basement_returns',(IB,22,4),'UP',I1)
link('ice_path_basement_descends',(IB,4,19),'DOWN',I2)
link('ice_path_deep_returns',(I2,22,4),'UP',IB)
link('ice_path_into_blackthorn',(I2,4,21),'DOWN',CITY)
link('blackthorn_back_ice_path',(CITY,4,27),'UP',I2)
link('blackthorn_center_enters',(CITY,7,23),'UP',PC1)
link('blackthorn_center_exits',(PC1,7,8),'DOWN',CITY)
link('blackthorn_center_native_stair_up',(PC1,2,6),'LEFT',PC2)
link('blackthorn_center_native_stair_down',(PC2,2,6),'LEFT',PC1)
link('blackthorn_mart_enters',(CITY,24,22),'UP',MART)
link('blackthorn_mart_exits',(MART,4,7),'DOWN',CITY)
link('blackthorn_gym_enters',(CITY,23,13),'UP',GYM)
link('blackthorn_gym_exits',(GYM,7,21),'DOWN',CITY)
link('blackthorn_dragon_den_enters',(CITY,14,6),'UP',DEN)
link('dragon_den_back_blackthorn',(DEN,15,23),'DOWN',CITY)
link('dragon_den_elder_shrine_enters',(DEN,15,6),'UP',SHRINE)
link('elder_shrine_back_den',(SHRINE,4,9),'DOWN',DEN)
assert len(cases)==22
gd.FIELDS['pokemon.hp']=('Pokemon','hp')
gd._OFFSETS=None
def safe_link_fixture(path,c):
 prepared=fixture(path,dict(c,flags={CLAIR:True}))
 lead=next((prepared.party_mon(i) for i in range(prepared.party_count()) if prepared.party_mon(i).has_species() and not prepared.party_mon(i).is_egg() and struct.unpack_from('<H',prepared.party_mon(i).blk,prepared.party_mon(i).o+off('pokemon.hp'))[0]>0),None)
 assert lead is not None and lead.level()>=31,'Native Repel needs the first healthy non-egg lead above wild max30'
 prepared.set_var('VAR_REPEL_STEP_COUNT',250);prepared.save(str(path));return prepared
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='blackthorn-native-links-') as td:
  for c in cases:
   target=Path(td)/(c['name']+'.sav');prepared=safe_link_fixture(target,c)
   with ReadOnlyEmu(str(rom),str(target),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    taps=cross(e,c);after=snapshot(e)
    for field in ['flags','trainers','items']+PRESERVE:assert after[field]==before[field],(c['name'],'state preservation',field)
    e.shot(str(out/(c['name']+'.png')),scale=3)
    row={'case':c['name'],'from':c['where'],'to':c['dest'],'key':c['key'],'actual_location':e.location(),'fresh_native_taps':taps,
     'party_pc_dex_flags_preserved':True,'forced_memory_writes':0}
    results.append(row);print(json.dumps(row),flush=True)
  for tag,where,key,dest in [('ice_strip_east',(I1,6,11),'RIGHT',(21,11)),('ice_strip_west',(IB,21,11),'LEFT',(6,11))]:
   target=Path(td)/(tag+'.sav');prepared=safe_link_fixture(target,{'name':tag,'where':where})
   with ReadOnlyEmu(str(rom),str(target),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    for _ in range(2):
     e.hold(key);e.run(1);e.hold();e.run(600)
     if e.location()[2:]==dest:break
    assert e.location()[2:]==dest and e.in_overworld() and not e.in_battle(),('native solid ice slide',tag,e.location(),dest)
    after=snapshot(e)
    for field in ['flags','trainers','items']+PRESERVE:assert after[field]==before[field],(tag,'state preservation',field)
    saved=flash_reload(e,tag)
    row={'case':tag,'native_slide_end':dest,'save':saved,'party_pc_dex_flags_preserved':True,'forced_memory_writes':0}
    results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==24
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,'original_files_unchanged':True,
 'forced_memory_writes':0,'wild_events_prevented_by_native_repel_with_healthy_lead_above30':True},indent=2))
