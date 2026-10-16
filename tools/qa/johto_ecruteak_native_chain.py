#!/usr/bin/env python3
"""Ecruteak chapter continuity. QA position warps only; no progress forcing after setup."""
from pathlib import Path
import ast,hashlib,sys
root=Path('/workspaces/pokefirered')
battles=root/'tools/qa/johto_ecruteak_native_battles.py'
wild=root/'tools/qa/johto_ecruteak_native_wild.py'
battle_src=battles.read_text();wild_src=wild.read_text()
assert hashlib.sha256(battle_src.encode()).hexdigest()=='cdeb7df13e0dd45cbb0ba0dc2d865c378382fc03610466b93deda9fb9f311508'
assert hashlib.sha256(wild_src.encode()).hexdigest()=='37e99b9ca7b60933c149a52c97814028ef25cc71aae4dfbfea4119fd5d36f19e'
assert battle_src.count('\nresults=[]\n')==1
exec(compile(battle_src.split('\nresults=[]\n')[0],str(battles),'exec'),globals())
# Reuse wild inputs without executing its separate-case bootstrap/fixture loop.
import re,gamedata as gd
gd.FIELDS['pokemon.level']=('Pokemon','level');gd._OFFSETS=None
bit=re.search(r'^#define\s+BATTLE_TYPE_TRAINER\s+\(1\s*<<\s*(\d+)\)',Path('include/constants/battle.h').read_text(),re.M)
assert bit;TRAINER_BATTLE_BIT=1<<int(bit.group(1))
nodes=[n for n in ast.parse(wild_src).body if isinstance(n,ast.FunctionDef) and n.name in ('start_wild','attempt')]
assert len(nodes)==2
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(wild),'exec'),globals())
rows=[];warps=0
critical=[W,O,S,Z,D,Y]
def keep(row):
 path=Path(row['save']['qa_save']);assert path.is_file()
 rows.append(row);print(json.dumps({'chapter_chain':row}),flush=True);return path
try:
 with tempfile.TemporaryDirectory(prefix='ecruteak-continuity-') as td:
  td=Path(td);initial=td/'initial-after-badge3.sav'
  prepared=fixture(initial,{'where':('GoldenrodCity_NorthGate',4,7),'flags':{G:True}})
  prepared.set_var('VAR_HAPPINESS_STEP_COUNTER',0);prepared.save(str(initial))
  start=SaveFile(str(initial));pc=bytes(start.blocks['storage']);initialdex=[start.dex_state(i) for i in range(1,387)]
  assert start.flag(G) and all(not start.flag(f) for f in critical)
  assert all(not start.trainer_beaten('TRAINER_JOHTO_'+n) for n in ['SILVER_BURNED_TOWER','MORTY'])
  saved=dialog_progress(initial,td/'flower-position.sav',('GoldenrodCity_NorthGate',4,7),
   {'name':'chain_waterbottle','marker':'GoldenrodCity_NorthGate_Text_FloristLend','expect_flags':{W:True}})
  warps+=1;previous=keep({'case':'waterbottle','save':saved,'forced_progress_after_setup':0})
  target=td/'sudowoodo-position.sav';prepared=warp_native_result(previous,target,('JohtoRoute36',25,9));warps+=1
  assert prepared.flag(W) and not prepared.flag(O)
  with ReadOnlyEmu(str(rom),str(target),sym='') as e:row=attempt(e,'win',prepared,'chain_sudowoodo_win')
  previous=keep(row)
  target=td/'silver-position.sav';prepared=warp_native_result(previous,target,POSITIONS['SILVER_BURNED_TOWER']);warps+=1
  assert prepared.flag(O) and not prepared.flag(S)
  with ReadOnlyEmu(str(rom),str(target),sym='') as e:row=battle(e,'SILVER_BURNED_TOWER',False,prepared,'chain_silver_win')
  previous=keep(row)
  target=td/'tower-position.sav';prepared=warp_native_result(previous,target,('BurnedTower_B1F',13,11));warps+=1
  assert prepared.flag(S) and not prepared.flag(Z)
  with ReadOnlyEmu(str(rom),str(target),sym='') as e:
   e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
   interaction(e,{'name':'chain_three_beasts','marker':'BurnedTower_B1F_Text_Escaped','step':True})
   after=snapshot(e);flags=dict(before['flags']);flags[Z]=True
   assert after['flags']==flags
   for field in ['trainers','pc','party','party_count','items','pc_hm','pc_hm3']:assert after[field]==before[field],('awakening preservation',field)
   allowed={struct.unpack('<H',r.at(syms['sSpeciesToNationalPokedexNum']+(const('SPECIES_'+x)-1)*2,2))[0] for x in ['RAIKOU','ENTEI','SUICUNE']}
   for dex,(old,new) in enumerate(zip(before['dex'],after['dex']),1):
    assert old[0]==new[0]
    assert new[1:]==(True,True,True) if dex in allowed else new==old,('awakening seen',dex,old,new)
   assert after['pc']==pc
   e.shot(str(out/'chain_three_beasts.png'),scale=3);saved=flash_reload(e,'chain_three_beasts')
  previous=keep({'case':'three_beasts','save':saved,'seen_only_added':['RAIKOU','ENTEI','SUICUNE'],'forced_progress_after_setup':0})
  target=td/'morty-position.sav';prepared=warp_native_result(previous,target,POSITIONS['MORTY']);warps+=1
  assert prepared.flag(G) and prepared.flag(Z) and not prepared.flag(D)
  with ReadOnlyEmu(str(rom),str(target),sym='') as e:row=battle(e,'MORTY',False,prepared,'chain_morty_win')
  previous=keep(row)
  final=SaveFile(str(previous));assert final.flag(G) and all(final.flag(f) for f in critical)
  assert all(final.trainer_beaten('TRAINER_JOHTO_'+n) for n in ['SILVER_BURNED_TOWER','MORTY'])
  assert bytes(final.blocks['storage'])==pc
  for i in range(1,387):
   old=initialdex[i-1];new=final.dex_state(i);assert new[0]==old[0] and all(not a or b for a,b in zip(old,new)),('final dex',i)
  assert warps==5 and len(rows)==5
finally:
 for path,sha in originals.items():assert digest(path.read_bytes())==sha,('original changed',str(path))
result={'pass_all':True,'rom_sha256':digest(rom.read_bytes()),'sequence':rows,'final_qa_save':str(previous),'native_save_cold_reopens':5,
 'qa_position_only_warps':warps,'forced_story_flags_after_setup':0,'forced_trainer_flags_after_setup':0,
 'forced_memory_writes':0,'forced_battle_outcomes':0,'initial_fixture':'winning battle fixture after Johto Badge3; temporary setup only',
 'full_natural_walking_tested':False,'kimono_five_wins_repeated':False,'full_campaign_tested':False,'original_files_unchanged':True}
(out/'chapter-chain-result.json').write_text(json.dumps(result,indent=2));print(json.dumps({'chapter_chain_result':result}),flush=True)
