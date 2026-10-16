#!/usr/bin/env python3
"""Native A-join/NO/cold-Continue regression. No fake-party or forced script calls."""
from pathlib import Path
import ast,hashlib,json,struct,sys
basic=Path('tools/qa/native_misty_basic_qa.py').read_text()
assert hashlib.sha256(basic.encode()).hexdigest()=='ba5c17ca3fd4a167ce1efe6379357a08b464586a5cf21391e05bbc5e7e7ccd1e'
assert basic.count('results=[];rows=[]\n')==1
exec(compile(basic.split('results=[];rows=[]\n')[0],'<verified-misty-definitions-only>','exec'))
# Extend the original snapshot oracle; retain its checksum/BadEgg/SAVE implementation.
old_snapshot=snapshot
flags_len=off('sb1.vars')-off('sb1.flags');hf_len=(const('HOENN_FLAGS_COUNT')+7)//8
assert 0<flags_len<4096 and 0<hf_len<4096
extra_flags=[join,hide,'FLAG_SYS_GAME_CLEAR',*K]
def snapshot(e):
 s=old_snapshot(e);b=blocks(e)
 s['flags'].update({f:b.flag(f) for f in extra_flags})
 s['raw_story_flags']=bytes(b.sb1[off('sb1.flags'):off('sb1.vars')])
 s['raw_hoenn_flags']=bytes(b.sb2[off('sb2.hoennFlags'):off('sb2.hoennFlags')+hf_len])
 s['raw_hoenn_trainers']=bytes(b.sb2[off('sb2.hoennTrainerFlags'):off('sb2.hoennFlags')])
 return s
rows=[];checks=[]
def task(e,name):
 assert name in syms
 return [i for i in range(16) if e.u8(e.sym('gTasks')+40*i+4) and e.u32(e.sym('gTasks')+40*i)&~1==syms[name]&~1]
def answer(e,yes):
 e.press('DOWN',hold=1,after=10);assert e.location()[2:]==(8,9),'did not face static Misty'
 assert len(object_rows(e,4))==1
 e.press('A',hold=3,after=20)
 for _ in range(240):
  safe(e)
  if task(e,'Task_YesNoMenu_HandleInput'):break
  assert not e.in_battle();e.press('A',hold=2,after=10)
 else:raise AssertionError('A interaction did not open join YES/NO')
 e.run(40)
 if not yes:e.press('DOWN',hold=3,after=15)
 e.press('A',hold=3,after=25)
 for _ in range(360):
  safe(e);assert not e.in_battle()
  if e.field_idle():break
  e.press('A',hold=2,after=10)
 else:raise AssertionError('join dialogue did not end')
 settle(e);e.run(30)
 assert blocks(e).flag(join)==yes
 assert len(object_rows(e,4))==(0 if yes else 1)
 assert len(object_rows(e,253))==(1 if yes else 0)
 assert blocks(e).var('VAR_TEMP_7')==0
 if not yes:
  e.run(240);assert e.field_idle() and not task(e,'Task_YesNoMenu_HandleInput') and not blocks(e).flag(join),'NO automatically prompted again'
 return dict(answer='YES' if yes else 'NO',joined=blocks(e).flag(join),static_npc=len(object_rows(e,4)),runtime_misty=len(object_rows(e,253)),pass_all=True)
try:
 with Emu(str(rom),str(sav),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30)
  source=record(e);assert e.location()[2:]==(8,9) and not blocks(e).flag(join)
  assert not object_rows(e,4), 'ineligible old Continue exposed Misty'
  saved=flash_reload(e,'base-pallet-saved')
  same_records(e,source);checks.append(dict(case='ineligible_continue_and_native_save',save=saved,pass_all=True))
 # Use actual native Pallet mapView and battery image, not an old remote-map cache.
 positive=out/'eligible-hidden-old-continue.sav';assert not positive.exists();s=SaveFile(saved['qa_save'])
 s.set_flag('FLAG_SYS_GAME_CLEAR',True)
 for f in K:s.set_flag(f,True)
 s.set_flag(join,False);s.set_flag(hide,True);s.set_var('VAR_TEMP_7',0)
 s.sb2[off('sb2.specialSaveWarpFlags')]&=~1
 assert bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])==source['party'] and bytes(s.blocks['storage'])==source['pc']
 s.save(str(positive))
 with Emu(str(rom),str(positive),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(60)
  same_records(e,source);eligible_flags=snapshot(e)
  # This specifically catches clearing HIDE without respawning an old-save NPC.
  npc=object_rows(e,4);checks.append(dict(case='eligible_hidden_old_continue',native_static_count=len(npc),hide_flag=blocks(e).flag(hide),position=e.location()))
  assert not blocks(e).flag(hide) and len(npc)==1,'eligible cold Continue lacks talkable static Misty'
  checks.append(dict(case='join_decline_actual_A',**answer(e,False)))
  same_records(e,source)
  assert snapshot(e)['raw_story_flags']==eligible_flags['raw_story_flags']
  checks.append(dict(case='join_accept_actual_A',**answer(e,True)))
  same_records(e,source)
  for j in range(3):one_tile(e,'LEFT');trail(e,'accepted-walk-left-'+str(j),need_visible=j>=2)
  joined_flags=snapshot(e)
  cold=flash_reload(e,'joined-native-save')
  same_records(e,source);assert blocks(e).flag(join) and not object_rows(e,4) and len(object_rows(e,253))==1
  for j in range(3):one_tile(e,'RIGHT');trail(e,'cold-walk-right-'+str(j),need_visible=j>=2)
  assert snapshot(e)['raw_story_flags']==joined_flags['raw_story_flags']
  checks.append(dict(case='joined_native_save_cold_trail',save=cold,pass_all=True))
finally:
 for f,h in originals.items():assert digest(f.read_bytes())==h,('original file changed',str(f))
 (out/'join-progress.json').write_text(json.dumps(dict(checks=checks,trail_samples=rows,original_sav_unchanged=True),indent=2))
(out/'join-result.json').write_text(json.dumps(dict(all_pass=True,rom_sha256=digest(rom.read_bytes()),checks=checks,original_party_pc_dex_preserved=True,actual_A_join_tested=True,native_battery_save_and_cold=True,friendly_duel_tested=False,water_routes_tested=False,actual_device_fps_measured=False),indent=2))
