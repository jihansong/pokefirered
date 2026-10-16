#!/usr/bin/env python3
"""Real native Misty mode-9 training; script hook is explicitly not an A-access proof."""
from pathlib import Path
import ast,hashlib,json,os,struct,sys
q=Path('tools/qa/native_misty_join_qa.py').read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='502adf6ca87daa10d64b5e20d0f99d34ce18b35de4d4fc43c32fe6767725c5ec'
anchor='\ntry:\n with Emu(str(rom),str(sav),sym=\'\') as e:';assert q.count(anchor)==1
exec(compile(q.split(anchor)[0],'<verified-misty-join-definitions-only>','exec'))
gd.FIELDS.update({'misty_partymenu.slot':('PartyMenu','slotId')});gd._OFFSETS=None
mode=os.environ.get('MISTY_DUEL_MODE','win-repeat');assert mode in ('win-repeat','loss')
original=SaveFile(str(sav));assert original.flag(join) and original.party_count()==6
base_party=bytes(original.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]);base_id=identity(base_party,6);base_pc=bytes(original.blocks['storage']);base_dex=[original.dex_state(i) for i in range(1,387)]
fixture=out/'training-fixture-only.sav';assert not fixture.exists()
s=SaveFile(str(sav))
for i,f in enumerate(growth):s.set_flag(f,mode=='loss' and i==3)
if mode=='loss':
 # Legal negative-test copy: keep six creatures/PID/OT/species/order, HP=1/PP=0 only.
 # Never claim source PIKACHU raw100 is unchanged in this controlled-loss fixture.
 for i in range(6):
  m=s.party_mon(i);subs=m.subs();subs['A'][8:12]=bytes(4);m.put_subs(subs);struct.pack_into('<H',s.sb1,m.o+86,1)
s.set_var('VAR_HAPPINESS_STEP_COUNTER',0);s.save(str(fixture))
assert identity(bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]),6)==base_id and bytes(s.blocks['storage'])==base_pc
assert [s.dex_state(i) for i in range(1,387)]==base_dex
checks=[];rows=[];seen_allowed=set()
def identity_guard(e):
 n=e.u8(e.sym('gPlayerPartyCount'));p=e.read(e.sym('gPlayerParty'),600);assert n==6 and identity(p,n)==base_id
 assert e.read(e.ptr('gPokemonStoragePtr'),33744)==base_pc
 dex=[blocks(e).dex_state(i) for i in range(1,387)]
 for no,(old,new) in enumerate(zip(base_dex,dex),1):
  assert new[0]==old[0],('owned Dex changed',no)
  assert tuple(new[1:])==tuple(bool(v or no in seen_allowed) for v in old[1:]),('unexpected native seen change',no,old,new,seen_allowed)
 return p

def select_alive(e):
 slot_off=off('misty_partymenu.slot');assert 0<=slot_off<32
 for _ in range(20):
  sid=struct.unpack('<b',e.read(e.sym('gPartyMenu')+slot_off,1))[0]
  if 0<=sid<6:
   p=e.sym('gPlayerParty')+sid*100
   current=e.u16(e.sym('gBattlerPartyIndexes'))
   if sid!=current and e.u16(p+86)>0 and not Mon(bytearray(e.read(p,100)),0).is_egg():
    e.press('A',hold=3,after=25)
    # The real party action submenu has SEND OUT as its first action.
    for _ in range(90):
     if task(e,'Task_HandleSelectionMenuInput'):e.press('A',hold=3,after=30);return
     if not task(e,'Task_HandleChooseMonInput'):return
     e.run(1)
    raise AssertionError('native party SEND OUT submenu did not open')
  e.press('DOWN',hold=3,after=12)
 raise AssertionError('no native selectable healthy bench creature')

def begin_training(e):
 call(e,'ScriptContext_SetupScript',syms['EventScript_TalkToMistyCompanion']);e.run(15)
 for _ in range(180):
  safe(e)
  if task(e,'Task_YesNoMenu_HandleInput'):break
  e.press('A',hold=2,after=12)
 else:raise AssertionError('friendly dialogue has no YES/NO')
 e.run(40);e.press('A',hold=3,after=20)
 for _ in range(240):
  safe(e)
  if e.in_battle():break
  e.press('A',hold=2,after=12)
 else:raise AssertionError('actual friendly trainer battle did not start')
 stage=4 if mode=='loss' else 0;trainer=const('TRAINER_MISTY_COMPANION_STAGE%d'%stage)
 assert e.u16(e.sym('gTrainerBattleOpponent_A'))==trainer
 assert e.u16(e.sym('sTrainerBattleMode'))==9 and e.u16(e.sym('sRivalBattleFlags'))&const('RIVAL_BATTLE_HEAL_AFTER')
 enemy=e.read(e.sym('gEnemyParty'),600);count=0
 for i in range(6):
  m=Mon(bytearray(enemy),100*i)
  if m.has_species():
   count+=1
 assert count==(6 if stage==4 else 3)
 return trainer,count,{Mon(bytearray(enemy),i*100).species() for i in range(count)}
def native_enemy_seen(e,roster):
 if e.u8(e.sym('gBattlersCount'))>=2:
  sp=e.u16(e.sym('gBattleMons')+off('battlemon'))
  if sp in roster:
   no=struct.unpack('<H',r.at(syms['sSpeciesToNationalPokedexNum']+(sp-1)*2,2))[0]
   assert 1<=no<=386;seen_allowed.add(no)
def loss_turn(e):
 # All PP=0 invokes native Struggle directly; no forced turn/outcome writes.
 for key in ('UP','LEFT','A'):e.press(key,hold=3,after=12)
 for _ in range(180):
  if not e.in_battle():return
  if ctrl(e,0,'HandleInputChooseMove'):
   for key in ('UP','LEFT','A'):e.press(key,hold=3,after=10)
   return
  if ctrl(e,0,'HandleInputChooseAction'):return
  e.press('B',hold=2,after=10)
try:
 with Emu(str(rom),str(fixture),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30)
  assert blocks(e).flag(join);origin=e.location();identity_guard(e);story=snapshot(e)
  repeats=2 if mode=='win-repeat' else 1
  for attempt in range(repeats):
   trainer,count,roster=begin_training(e);turns=0;switches=0
   for frame in range(80000):
    safe(e);native_enemy_seen(e,roster)
    if e.callback2()&~1==syms.get('CB2_WhiteOut',0)&~1:raise AssertionError('friendly loss entered WhiteOut')
    if not e.in_battle():break
    if task(e,'Task_HandleChooseMonInput'):select_alive(e);switches+=1;continue
    if ctrl(e,0,'HandleInputChooseAction'):
     e.run(20)
     if mode=='loss':loss_turn(e)
     else:fight_one_turn(e)
     turns+=1;assert turns<160
    else:e.press('B',hold=2,after=12)
   else:raise AssertionError('friendly native battle did not finish')
   outcome=e.u8(e.sym('gBattleOutcome'));assert outcome==(const('B_OUTCOME_LOST') if mode=='loss' else const('B_OUTCOME_WON')),('wrong actual outcome',outcome)
   settle(e);e.run(30);assert e.location()==origin,'friendly battle warped the player'
   p=identity_guard(e)
   for i in range(6):assert struct.unpack_from('<H',p,100*i+86)[0]==struct.unpack_from('<H',p,100*i+88)[0] and struct.unpack_from('<I',p,100*i+80)[0]==0,'post-training heal missing'
   for i in range(6):
    subs=Mon(bytearray(p),100*i).subs();moves=struct.unpack('<4H',subs['A'][:8])
    for j,mv in enumerate(moves):
     assert subs['A'][8+j]==call(e,'CalculatePPWithBonus',mv,subs['G'][8],j),'post-training PP heal missing'
   current=snapshot(e);assert current['raw_story_flags']==story['raw_story_flags'] and current['raw_hoenn_flags']==story['raw_hoenn_flags'],'friendly battle changed story milestones'
   # Native trainer-beaten bit is expected, but it must never prevent this repeat.
   expected=bytearray(story['raw_hoenn_trainers']);index=trainer-const('HOENN_TRAINERS_START');expected[index//8]|=1<<(index%8)
   assert current['raw_hoenn_trainers']==bytes(expected),'unrelated trainer flag changed'
   saved=flash_reload(e,'training-%s-%d'%(mode,attempt));identity_guard(e)
   assert e.location()==origin and blocks(e).flag(join) and len(object_rows(e,253))==1
   checks.append(dict(attempt=attempt,outcome=outcome,trainer=trainer,team_count=count,turns=turns,native_switches=switches,save=saved,mode9=True,heal_after=True,pass_all=True))
finally:
 for f,h in originals.items():assert digest(f.read_bytes())==h,('original file changed',str(f))
 (out/'training-progress.json').write_text(json.dumps(dict(checks=checks,mode=mode,source_sav_unchanged=True),indent=2))
(out/'training-result.json').write_text(json.dumps(dict(all_pass=True,mode=mode,rom_sha256=digest(rom.read_bytes()),input_sav_sha256=originals[sav],native_script_hook=True,actual_A_companion_access_verified=False,no_forced_battle_outcomes=True,source_original_party_count_identity_preserved=True,loss_copy_HP1_PP0=mode=='loss',native_save_cold=True,player_party_temporarily_replaced=False,actual_device_fps_measured=False,checks=checks),indent=2))
