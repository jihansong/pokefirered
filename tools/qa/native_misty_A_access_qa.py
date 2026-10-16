#!/usr/bin/env python3
"""Actual A interaction in the ordinary two-companion trail; no fake coordinates."""
from pathlib import Path
import hashlib,json
q=Path('tools/qa/native_misty_join_qa.py').read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='e054487caefcacbb398349e88bce8660932093b1e0daee4824e98e436b9bc5a0'
anchor='\ntry:\n with Emu(str(rom),str(sav),sym=\'\') as e:';assert q.count(anchor)==1
exec(compile(q.split(anchor)[0],'<verified-misty-join-definitions-only>','exec'))
checks=[];rows=[]
def turn_only(e,direction):
 position=e.location();e.press(direction,hold=1,after=30)
 assert e.location()==position,'turn-only input stepped; do not fake coordinates to make this pass'
def finish_dialogue(e):
 for i in range(400):
  safe(e);assert not e.in_battle()
  if e.field_idle():break
  e.press('A',hold=2,after=10)
 else:raise AssertionError('native dialogue did not finish')
 settle(e);e.run(30)
try:
 with Emu(str(rom),str(sav),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30)
  assert blocks(e).flag(join) and e.location()[2:]==(5,9)
  original_state=e.save_state();reference=record(e)
  for j in range(4):one_tile(e,'RIGHT');trail(e,'normal-A-trail-'+str(j),need_visible=j>=2)
  row=trail(e,'normal-A-before-turn',need_visible=True)
  gap=sum(abs(a-b) for a,b in zip(row['misty'][0]['xy'],row['player']['xy']))
  assert gap==2,'ordinary trail does not have the expected two-tile spacing'
  turn_only(e,'LEFT');e.press('A',hold=3,after=20)
  emotion=bool(task(e,'Task_StarterPikachuEmotion'));talked=e.u16(e.sym('gSpecialVar_LastTalked'))
  assert talked==254 and emotion,'ordinary Pikachu A emotion did not execute'
  assert not task(e,'Task_YesNoMenu_HandleInput'),'Misty prompt appeared through an unreviewed path'
  finish_dialogue(e);same_records(e,reference)
  checks.append(dict(case='ordinary_trail_actual_A',misty_visible=True,misty_player_tile_distance=gap,last_talked=talked,original_pika_emotion_preserved=True,misty_direct_A_reached=False,scope='This normal trail pose, not proof that every possible movement timing is unreachable'))
  # Control case: remove the runtime Pika only with a temporary flag, keep its real party bytes.
  flag(e,'FLAG_RECEIVED_STARTER_PIKACHU',False);e.run(30);assert not object_rows(e,254)
  for j in range(2):one_tile(e,'RIGHT');trail(e,'without-Pika-A-trail-'+str(j),need_visible=j>=1)
  row=trail(e,'without-Pika-A-before-turn',need_visible=True)
  gap=sum(abs(a-b) for a,b in zip(row['misty'][0]['xy'],row['player']['xy']));assert gap==1
  turn_only(e,'LEFT');e.press('A',hold=3,after=20)
  for _ in range(180):
   safe(e)
   if task(e,'Task_YesNoMenu_HandleInput'):break
   e.press('A',hold=2,after=10)
  else:raise AssertionError('Misty actual A did not open its dialogue')
  assert e.u16(e.sym('gSpecialVar_LastTalked'))==253
  e.run(40);e.press('DOWN',hold=3,after=15);e.press('A',hold=3,after=20);finish_dialogue(e)
  same_records(e,reference);checks.append(dict(case='no-runtime-Pika_control_actual_A',temporary_received_starter_flag=False,real_pika100_and_party600_preserved=True,last_talked=253,misty_direct_A_reached=True))
  e.load_state(original_state);same_records(e,reference)
finally:
 for f,h in originals.items():assert digest(f.read_bytes())==h,('original file changed',str(f))
 (out/'A-access-progress.json').write_text(json.dumps(dict(checks=checks,trail_samples=rows),indent=2))
(out/'A-access-result.json').write_text(json.dumps(dict(test_execution_pass=True,normal_two_follower_direct_Misty_A_available=False,conditional_no_runtime_Pika_A_available=True,source_original_sav_unchanged=True,coordinates_never_poked=True,temporary_native_flag_control=True,actual_device_fps_measured=False,checks=checks),indent=2))
