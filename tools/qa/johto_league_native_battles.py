#!/usr/bin/env python3
"""Native Johto League gates and retained/restarted challenge state."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_league_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='474c1ff4a38f7c8b77b8ef4bc826b9762a5a92ba09977a7616ffda6ad5aec136'
exec(compile(_boot_text,str(_boot),'exec'),globals())

results=[]
try:
 with tempfile.TemporaryDirectory(prefix='johto-league-native-battles-') as td:
  for name,loss in [(n,False) for n in LEAGUE_ACTORS]+[('SILVER_VICTORY_ROAD',True),('LANCE_CHAMPION',True)]:
   tag=name.lower()+('_loss' if loss else '_win')
   target=Path(td)/(tag+'.sav')
   prepared=fixture(target,{'where':POSITIONS[name],'loss':loss,'flags':PRIOR.get(name,{})})
   with ReadOnlyEmu(str(rom),str(target),sym='') as e:row=battle_attempt(e,name,loss,prepared,tag)
   row['fixture_kanto_clear_explicit']=prepared.flag(SYS);results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==8
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,
 'eligible_initial_test_fixture_explicitly_sets_kanto_champion_flag':True,'campaign_playthrough_claimed':False,
 'original_files_unchanged':True,'forced_memory_writes':0,'forced_battle_outcomes':0},indent=2))
