#!/usr/bin/env python3
"""Native Johto League gates and retained/restarted challenge state."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_league_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='474c1ff4a38f7c8b77b8ef4bc826b9762a5a92ba09977a7616ffda6ad5aec136'
exec(compile(_boot_text,str(_boot),'exec'),globals())

import ast
_chain_path=Path(__file__).with_name('johto_blackthorn_native_chain.py')
_chain_text=_chain_path.read_text()
assert hashlib.sha256(_chain_text.encode()).hexdigest()=='8c073ac862bb28cca4278d65f0a4ca2db81456372692bdc87c40ce07252c524c'
_nodes=[n for n in ast.parse(_chain_text).body if isinstance(n,ast.FunctionDef)and n.name in ('warp_native_result','dialog_stage')]
assert len(_nodes)==2
exec(compile(ast.Module(body=_nodes,type_ignores=[]),str(_chain_path),'exec'),globals())
_event_path=Path(__file__).with_name('johto_league_native_events.py')
_event_text=_event_path.read_text()
assert hashlib.sha256(_event_text.encode()).hexdigest()=='e76a2acad8776380b9d755cbfcbe7d99530ff24f3bbc68e7240bf1b10367d493'
_nodes=[n for n in ast.parse(_event_text).body if isinstance(n,ast.FunctionDef)and n.name=='interaction']
assert len(_nodes)==1
_league_base_interaction=interaction
exec(compile(ast.Module(body=_nodes,type_ignores=[]),str(_event_path),'exec'),globals())
_hof_path=Path(__file__).with_name('johto_league_native_hof.py');_hof_text=_hof_path.read_text()
assert hashlib.sha256(_hof_text.encode()).hexdigest()=='244277c45e4e2f03f198850901f4d39adacd5b6d0dba1642b2675437172c0000'
_names={'hof_compiled_oracles','hof_party','native_hof'}
_nodes=[n for n in ast.parse(_hof_text).body if isinstance(n,ast.FunctionDef)and n.name in _names]
assert {n.name for n in _nodes}==_names
exec(compile(ast.Module(body=_nodes,type_ignores=[]),str(_hof_path),'exec'),globals())
gd.FIELDS.update({'pokemon.hp':('Pokemon','hp'),'pokemon.maxHP':('Pokemon','maxHP'),'pokemon.status':('Pokemon','status')})
gd._OFFSETS=None
def eligible_initial_copy(target):
 initial=SaveFile(str(sav))
 assert all(initial.flag(f)for f in ['FLAG_JOHTO_BADGE%02d_GET'%i for i in range(1,9)])
 assert initial.flag(RADIO) and all(initial.flag(f)for f in BLACK_FLAGS),'requires actual q8 Blackthorn completion SAVE'
 assert all(initial.trainer_beaten('TRAINER_JOHTO_'+n)for n in BLACK_ACTORS)
 assert all(initial.flag(f)for f in K),'initial Kanto badges unavailable'
 assert all(not initial.flag(f)for f in LEAGUE_FLAGS),'League chapter must begin unstarted'
 assert all(not initial.trainer_beaten('TRAINER_JOHTO_'+n)for n in LEAGUE_ACTORS)
 party=bytes(initial.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]);pc=bytes(initial.blocks['storage'])
 dex=[initial.dex_state(i)for i in range(1,387)];oldflags={f:initial.flag(f)for f in STORY};sys_before=initial.flag(SYS)
 # q8's verified chapter chain has SYS_GAME_CLEAR false. This isolated eligibility fixture records that one deliberate change.
 initial.set_flag(SYS,True)
 initial.set_var('VAR_REPEL_STEP_COUNT',250);initial.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
 initial.warp('JohtoRoute27',0,20);initial.save(str(target))
 saved=SaveFile(str(target))
 assert bytes(saved.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])==party
 assert bytes(saved.blocks['storage'])==pc and [saved.dex_state(i)for i in range(1,387)]==dex
 assert all(saved.flag(f)==(True if f==SYS else v)for f,v in oldflags.items())
 return {'source_kanto_clear':sys_before,'fixture_kanto_clear':True,
  'explicit_story_flag_initialization':[SYS] if not sys_before else [],
  'source_sha256':digest(sav.read_bytes()),'party_pc_dex_preserved':True}
def nurse():
 return ('dialog',('JohtoLeague_PokemonCenter_1F',7,4),
  {'name':'chain_native_heal_before_elite_challenge','marker':'Text_RestoredPkmnToFullHealth','face_only':True,'heal':True})
steps=[
 ('dialog',('JohtoRoute27',0,20),{'name':'chain_eligible_league_road_opens','marker':None,'step':True,'direction':'RIGHT'}),
 ('battle',POSITIONS['SILVER_VICTORY_ROAD'],'SILVER_VICTORY_ROAD'),
 ('dialog',('JohtoVictoryRoad_1F',15,4),{'name':'chain_silver_opens_plateau_arrival','marker':None,'step':True,
  'dest':'JohtoIndigoPlateau','expect_flags':{L_ARRIVED:True}}),
 nurse(),
 ('dialog',('JohtoLeague_PokemonCenter_1F',4,8),{'name':'chain_reception_starts_new_challenge','marker':None,
   'answer':'YES','question':'JohtoLeague_PokemonCenter_1F_Text_Challenge','dest':ROOMS['WILL']})]
for i,name in enumerate(ELITE_ACTORS):
 steps.append(('battle',POSITIONS[name],name))
 dest=ROOMS[ELITE_ACTORS[i+1]] if i+1<len(ELITE_ACTORS) else 'JohtoLeague_HallOfFame'
 steps.append(('dialog',(ROOMS[name],6,3),{'name':'chain_'+name.lower()+'_victory_opens_next_room','marker':None,'step':True,'dest':dest}))
steps.append(('hof',('JohtoLeague_HallOfFame',6,6),'chain_actual_johto_champion_hof'))
assert len(steps)==16
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='johto-league-same-save-chain-') as td:
  td=Path(td);previous=td/'explicit-kanto-eligible-initial-QA-only.sav';initialization=eligible_initial_copy(previous)
  initial=SaveFile(str(previous));initial_pc=bytes(initial.blocks['storage'])
  cross_history={f:initial.flag(f)for f in [SEA,RAY,HWATER,KWATER,SYS]}
  for i,(kind,where,c) in enumerate(steps):
   target=td/('step-'+str(i+1)+'.sav')
   if kind=='dialog':row=dialog_stage(previous,target,where,c)
   else:
    prepared=warp_native_result(previous,target,where)
    with ReadOnlyEmu(str(rom),str(target),sym='') as e:
     if kind=='battle':
      assert not prepared.trainer_beaten('TRAINER_JOHTO_'+c)
      row=battle_attempt(e,c,False,prepared,'chain_actual_'+c.lower()+'_win')
     else:row=native_hof(e,c);row['save']={'qa_save':row['qa_save'],'counter':row['native_hof_counter']}
   previous=Path(row['save']['qa_save']);results.append(row);print(json.dumps(row),flush=True)
  final=SaveFile(str(previous))
  assert all(final.flag(f)for f in LEAGUE_FLAGS)
  assert all(final.trainer_beaten('TRAINER_JOHTO_'+n)for n in LEAGUE_ACTORS)
  assert bytes(final.blocks['storage'])==initial_pc
  assert all(final.flag(f)==v for f,v in cross_history.items()),'League fabricated cross-region event history'
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==16
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'initial_save':str(sav),
 'initial_context':'Actual q8 Blackthorn completion save copied with explicit Kanto champion test eligibility',
 'initialization':initialization,'stages':results,'all_pass':True,'same_native_save_chain':True,
 'native_nurse_heals':1,'qa_position_only_warps_after_initialization':16,'forced_story_flags_after_initial_fixture':0,
 'forced_trainer_flags_after_initial_fixture':0,'forced_memory_writes':0,'forced_battle_outcomes':0,
 'actual_silver_six_and_five_elite_battles':True,'actual_hof_save_and_credits_dispatch':True,
 'full_kanto_to_johto_campaign_walk_claimed':False,'original_files_unchanged':True},indent=2))
