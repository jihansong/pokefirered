#!/usr/bin/env python3
"""Ordinary PIKA A retains emotion; explicit Misty YES/NO and native SAVE/cold."""
from pathlib import Path
import hashlib,json
q=Path('tools/qa/native_misty_join_qa.py').read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='e054487caefcacbb398349e88bce8660932093b1e0daee4824e98e436b9bc5a0'
anchor='\ntry:\n with Emu(str(rom),str(sav),sym=\'\') as e:';assert q.count(anchor)==1
exec(compile(q.split(anchor)[0],'<verified-Misty-join-definitions-only>','exec'))
proof_path=sav.parent/'join-result.json';proof=json.loads(proof_path.read_text())
assert proof['all_pass'] and proof['actual_A_join_tested'] and proof['native_battery_save_and_cold']
assert Path(next(v['save']['qa_save'] for v in proof['checks'] if v['case']=='joined_native_save_cold_trail')).resolve()==sav.resolve()
proof_before=digest(proof_path.read_bytes());checks=[];rows=[]
def turn_only(e,key):
 position=e.location();e.press(key,hold=1,after=30)
 assert e.location()==position,'real turn input stepped: no fake coordinates'
def finish_dialogue(e):
 for _ in range(400):
  safe(e);assert not e.in_battle(),'declined dialogue unexpectedly started a battle'
  if e.field_idle():break
  e.press('A',hold=2,after=10)
 else:raise AssertionError('dialogue did not finish')
 settle(e);e.run(30)
def open_pika_A(e,question):
 e.press('A',hold=3,after=20)
 assert e.u16(e.sym('gSpecialVar_LastTalked'))==254 and task(e,'Task_StarterPikachuEmotion'),'original PIKA emotion A was lost'
 for _ in range(1200):
  safe(e);assert not e.in_battle()
  if not task(e,'Task_StarterPikachuEmotion'):break
  e.run(1)
 else:raise AssertionError('original PIKA emotion did not finish')
 if question:
  for _ in range(240):
   safe(e);assert not e.in_battle()
   if task(e,'Task_YesNoMenu_HandleInput'):break
   e.press('A',hold=2,after=10)
  else:raise AssertionError('ordinary PIKA A has no explicit Misty choice')
  assert e.u16(e.sym('gSpecialVar_LastTalked'))==254
 else:
  for _ in range(80):
   assert not task(e,'Task_YesNoMenu_HandleInput'),'unjoined PIKA emotion gained an unwanted choice'
   if e.field_idle():break
   e.run(1)
  else:raise AssertionError('unjoined original PIKA A did not release')
  finish_dialogue(e)
def answer_choice(e,yes):
 assert task(e,'Task_YesNoMenu_HandleInput');e.run(40)
 if not yes:e.press('DOWN',hold=3,after=15)
 e.press('A',hold=3,after=20)
def talk_misty_without_battle(e):
 # Select the new companion choice, then decline the existing training question.
 answer_choice(e,True)
 for _ in range(240):
  safe(e);assert not e.in_battle(),'Misty training began before its own choice'
  if task(e,'Task_YesNoMenu_HandleInput') and e.u16(e.sym('gSpecialVar_LastTalked'))==253:break
  e.press('A',hold=2,after=10)
 else:raise AssertionError('Misty ordinary A access did not select runtime object253')
 assert e.u8(e.sym('gSelectedObjectEvent'))==object_rows(e,253)[0]['slot']
 answer_choice(e,False);finish_dialogue(e)
 assert e.u16(e.sym('gSpecialVar_LastTalked'))==253
try:
 with Emu(str(rom),str(sav),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30)
  assert blocks(e).flag(join) and e.location()[2:]==(5,9)
  reference=record(e)
  for j in range(4):one_tile(e,'RIGHT');trail(e,'ordinary-A-base-'+str(j),need_visible=j>=2)
  baseline=e.save_state();turn_only(e,'LEFT')
  # Negative control changes one flag in RAM only; original party PIKA stays intact.
  flag(e,join,False);e.run(30);assert not object_rows(e,253)
  negative=snapshot(e);open_pika_A(e,False);same_records(e,reference)
  assert snapshot(e)['raw_story_flags']==negative['raw_story_flags']
  checks.append(dict(case='unjoined_original_PIKA_A',pika_emotion=True,extra_question=False,temporary_join_flag_control=True,pass_all=True))
  e.load_state(baseline);turn_only(e,'LEFT');joined=snapshot(e)
  open_pika_A(e,True);answer_choice(e,False);finish_dialogue(e);same_records(e,reference)
  assert e.u16(e.sym('gSpecialVar_LastTalked'))==254 and snapshot(e)['raw_story_flags']==joined['raw_story_flags']
  checks.append(dict(case='joined_Misty_choice_NO',pika_emotion=True,original_PIKA_selected=True,no_training_started=True,pass_all=True))
  e.load_state(baseline);turn_only(e,'LEFT');open_pika_A(e,True);talk_misty_without_battle(e);same_records(e,reference)
  assert snapshot(e)['raw_story_flags']==joined['raw_story_flags']
  checks.append(dict(case='joined_Misty_choice_YES_then_training_NO',pika_emotion=True,runtime_misty_selected=253,actual_A_access=True,no_script_entry_hook=True,no_training_started=True,pass_all=True))
  saved=flash_reload(e,'ordinary-pika-Misty-A');same_records(e,reference)
  for j in range(3):one_tile(e,'LEFT');trail(e,'cold-A-trail-'+str(j),need_visible=j>=2)
  turn_only(e,'RIGHT');open_pika_A(e,True);talk_misty_without_battle(e);same_records(e,reference)
  assert blocks(e).flag(join) and snapshot(e)['raw_story_flags']==joined['raw_story_flags']
  checks.append(dict(case='native_SAVE_cold_then_actual_A',save=saved,actual_A_access=True,pika_and_misty_trail_visible=True,pass_all=True))
finally:
 for f,h in originals.items():assert digest(f.read_bytes())==h,('original input changed',str(f))
 assert digest(proof_path.read_bytes())==proof_before,'join proof changed'
 (out/'A-dialogue-progress.json').write_text(json.dumps(dict(checks=checks,trail_samples=rows),indent=2))
(out/'A-dialogue-result.json').write_text(json.dumps(dict(all_pass=True,rom_sha256=digest(rom.read_bytes()),joined_native_source_rom_sha256=proof['rom_sha256'],original_PIKA_emotion_preserved=True,ordinary_two_follower_A_access=True,actual_A_and_yesno_only=True,companion_coordinates_never_poked=True,temporary_negative_join_flag_control=True,party_pc_dex_preserved=True,story_flags_preserved=True,native_save_and_cold=True,friendly_battle_in_this_test=False,actual_device_fps_measured=False,checks=checks),indent=2))
