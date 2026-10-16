#!/usr/bin/env python3
"""Native Johto League gates and retained/restarted challenge state."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_league_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='474c1ff4a38f7c8b77b8ef4bc826b9762a5a92ba09977a7616ffda6ad5aec136'
exec(compile(_boot_text,str(_boot),'exec'),globals())


cases=[
 {'name':'kanto_badge1_missing_east_gate','where':('JohtoRoute27',0,20),'direction':'RIGHT','step':True,
  'marker':'JohtoRoute27_Text_NotReady','flags':{'FLAG_BADGE01_GET':False}},
 {'name':'kanto_badge1_missing_reception','where':('JohtoLeague_PokemonCenter_1F',4,8),
  'marker':'JohtoLeague_PokemonCenter_1F_Text_NotReady','flags':{SILVER_L:True,'FLAG_BADGE01_GET':False}},
 {'name':'kanto_badge1_missing_hof','where':('JohtoLeague_HallOfFame',6,6),
  'marker':'JohtoLeague_HallOfFame_Text_NotReady','flags':{**{f:True for f in ELITE_FLAGS},'FLAG_BADGE01_GET':False}}]
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='native-kanto-badge1-negative-')as td:
  for c in cases:
   target=Path(td)/(c['name']+'.sav');prepared=fixture(target,c)
   assert prepared.flag(SYS)and not prepared.flag('FLAG_BADGE01_GET'),'does not model SYS set after a different region'
   with ReadOnlyEmu(str(rom),str(target),sym='')as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    interaction(e,c);after=snapshot(e)
    assert after==before,(c['name'],'denied entry changed gameplay progress')
    info=map_info(c['where'][0]);assert e.location()[:2]==(info['group'],info['num'])
    assert not after['flags'][L_CLEAR],'invalid Kanto prerequisites fabricated Johto HOF'
    e.shot(str(out/(c['name']+'.png')),scale=3);saved=flash_reload(e,c['name'])
    row={'case':c['name'],'save':saved,'SYS_GAME_CLEAR_fixture':True,'kanto_badge1_fixture':False,
     'native_denied_dialogue':c['marker'],'party_pc_dex_all_progress_preserved':True,'forced_memory_writes':0}
   results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==3
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,
 'scope':'Three actual League gates deny missing original Kanto badge1 despite global SYS clear',
 'original_files_unchanged':True,'forced_memory_writes':0},indent=2))
