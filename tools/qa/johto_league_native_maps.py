#!/usr/bin/env python3
"""Native Johto League gates and retained/restarted challenge state."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_league_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='474c1ff4a38f7c8b77b8ef4bc826b9762a5a92ba09977a7616ffda6ad5aec136'
exec(compile(_boot_text,str(_boot),'exec'),globals())

cases=[]
def link(name,where,key,dest,**kw):cases.append(dict(name=name,where=where,key=key,dest=dest,**kw))
R27='JohtoRoute27';FALLS='TohjoFalls';R26='JohtoRoute26';VR='JohtoVictoryRoad_1F'
PLATEAU='JohtoIndigoPlateau';PC='JohtoLeague_PokemonCenter_1F';HOF='JohtoLeague_HallOfFame'
link('new_bark_water_connection_enters_route27',('NewBarkTown',35,20),'RIGHT',R27)
link('route27_cave_enters_tohjo_falls',(R27,33,6),'UP',FALLS)
link('tohjo_south_returns_route27',(FALLS,10,17),'DOWN',R27)
link('tohjo_north_enters_route26',(FALLS,10,4),'UP',R26)
link('route26_south_returns_tohjo',(R26,10,31),'DOWN',FALLS)
link('route26_cave_enters_victory_road',(R26,25,6),'UP',VR)
link('victory_road_returns_route26',(VR,15,24),'DOWN',R26)
link('victory_road_opens_plateau',(VR,15,4),'UP',PLATEAU,expect_flags={L_ARRIVED:True})
link('plateau_returns_victory_road',(PLATEAU,11,17),'DOWN',VR)
link('plateau_center_enters',(PLATEAU,11,7),'UP',PC)
link('league_center_exits',(PC,7,8),'DOWN',PLATEAU,expect_flags={L_ARRIVED:True})
for n in ELITE_ACTORS:link(n.lower()+'_south_exit_returns_reception',(ROOMS[n],6,10),'DOWN',PC)
link('hof_returns_lance_room',(HOF,5,11),'DOWN',ROOMS['LANCE_CHAMPION'])
assert len(cases)==17
gd.FIELDS['pokemon.hp']=('Pokemon','hp');gd._OFFSETS=None
def safe_fixture(path,c):
 prepared=fixture(path,dict(c,flags={SILVER_L:True,**{f:True for f in ELITE_FLAGS}}))
 healthy=[]
 for i in range(prepared.party_count()):
  m=prepared.party_mon(i)
  if m.has_species() and not m.is_egg() and struct.unpack_from('<H',m.blk,m.o+off('pokemon.hp'))[0]>0:healthy.append(m)
 assert healthy and healthy[0].level()>=38,'Native Repel needs first healthy lead above league wild max37'
 prepared.set_var('VAR_REPEL_STEP_COUNT',250);prepared.save(str(path));return prepared
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='johto-league-native-links-') as td:
  for c in cases:
   target=Path(td)/(c['name']+'.sav');prepared=safe_fixture(target,c)
   with ReadOnlyEmu(str(rom),str(target),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    taps=cross(e,c);after=snapshot(e)
    assert after['flags']==existing_flags(before,c),(c['name'],'native arrival story flags')
    for field in ['trainers','items']+PRESERVE:assert after[field]==before[field],(c['name'],'preservation',field)
    e.shot(str(out/(c['name']+'.png')),scale=3)
    row={'case':c['name'],'from':c['where'],'to':c['dest'],'native_location':e.location(),'fresh_native_taps':taps,
     'party_pc_dex_preserved':True,'forced_memory_writes':0}
    results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==17
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,
 'original_files_unchanged':True,'forced_memory_writes':0,'wild_events_prevented_by_native_repel_with_healthy_lead_above37':True,
 'new_bark_reverse_surf_prompt_and_tohjo_waterfall_full_path_tested_separately':True},indent=2))
