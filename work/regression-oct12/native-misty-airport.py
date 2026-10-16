from pathlib import Path
import hashlib,json,traceback
q=Path('tools/qa/native_misty_basic_qa.py').read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
anchor='\nresults=[];rows=[]\n';assert q.count(anchor)==1
exec(compile(q.split(anchor)[0],'<verified-Misty-basic-definitions-only>','exec'))
declined='FLAG_MISTY_COMPANION_DECLINED';old_snapshot=snapshot
def snapshot(e):
 d=old_snapshot(e);d['flags'].update({f:blocks(e).flag(f) for f in [join,hide,declined,'FLAG_SYS_GAME_CLEAR',*K]})
 d['raw_story_flags']=bytes(blocks(e).sb1[off('sb1.flags'):off('sb1.vars')]);return d
def yesno(e):
 return any(e.u8(e.sym('gTasks')+40*i+4) and (e.u32(e.sym('gTasks')+40*i)&~1)==(syms['Task_YesNoMenu_HandleInput']&~1) for i in range(16))
def await_yesno(e):
 for _ in range(360):
  safe(e);assert not e.in_battle()
  if yesno(e):e.run(40);return
  e.press('A',hold=2,after=10)
 raise AssertionError('Expected airport YES/NO did not appear')
def answer(e,yes):
 assert yesno(e)
 if not yes:e.press('DOWN',hold=3,after=15)
 e.press('A',hold=3,after=25)
def finish_field(e):
 for _ in range(600):
  safe(e);assert not e.in_battle();assert not yesno(e),'Unexpected extra YES/NO'
  if e.field_idle():settle(e);e.run(30);return
  e.press('A',hold=2,after=10)
 raise AssertionError('Airport dialog did not release field')
def open_clerk(e,local):
 before=e.location();e.press('UP',hold=1,after=20);assert e.location()==before
 e.press('A',hold=3,after=20);await_yesno(e)
 assert e.u16(e.sym('gSpecialVar_LastTalked'))==local
def decline_flight(e):
 assert yesno(e);e.press('B',hold=3,after=25);finish_field(e)
def repeated_clerk(e,local):
 before=snapshot(e);open_clerk(e,local);decline_flight(e);assert snapshot(e)==before
def make_fixture(tag,x,no_pika):
 path=out/(tag+'-fixture.sav');assert not path.exists()
 s=SaveFile(str(sav));party=bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]);pc=bytes(s.blocks['storage'])
 s.set_flag('FLAG_SYS_GAME_CLEAR',True)
 for f in K:s.set_flag(f,True)
 s.set_flag(join,False);s.set_flag(declined,False);s.set_flag(hide,True)
 if no_pika:s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',False)
 s.set_var('VAR_TEMP_7',0);s.sb2[off('sb2.specialSaveWarpFlags')]&=~1
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 s.warp('KantoAirport',x,6)
 assert bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])==party and bytes(s.blocks['storage'])==pc
 s.save(str(path));return path
checks=[];status={'all_pass':False,'ram_writes':0,'direct_MistyJoin_calls':0}
try:
 for tag,x,local,accept,no_pika in [('johto_yes',10,2,True,False),('johto_no',10,2,False,False),('hoenn_yes_starter_follower_disabled',6,1,True,True),('hoenn_no',6,1,False,False)]:
  f=make_fixture(tag,x,no_pika)
  with ReadOnlyEmu(str(rom),str(f),sym='') as e:
   e.syms=syms;e.boot_continue();settle(e);e.run(30)
   assert e.location()[2:]==(x,6) and not blocks(e).flag(join) and not blocks(e).flag(declined)
   before=record(e);initial=snapshot(e);pikachu_before=object_rows(e,254)
   if no_pika:assert not pikachu_before
   open_clerk(e,local);answer(e,accept);await_yesno(e)
   assert blocks(e).flag(join)==accept and blocks(e).flag(declined)==(not accept)
   assert len(object_rows(e,253))==(1 if accept else 0)
   e.shot(str(out/(tag+'-flight-after-companion.png')),scale=3)
   decline_flight(e);same_records(e,before);post=snapshot(e)
   changed=[(i,a^b) for i,(a,b) in enumerate(zip(initial['raw_story_flags'],post['raw_story_flags'])) if a!=b]
   assert changed==([(68,8)] if accept else [(69,1)]),('Unexpected story flag changes',changed)
   repeated_clerk(e,local);cold=flash_reload(e,tag);same_records(e,before);assert snapshot(e)==post
   assert blocks(e).flag(join)==accept and blocks(e).flag(declined)==(not accept)
   if not accept:
    e.run(600);assert e.field_idle() and not yesno(e) and not object_rows(e,253)
    repeated_clerk(e,local)
   else:
    assert len(object_rows(e,253))==1
    for _ in range(3):one_tile(e,'DOWN')
    ms=object_rows(e,253);assert len(ms)==1 and ms[0]['visible']
    if no_pika:assert not object_rows(e,254)
    same_records(e,before);e.shot(str(out/(tag+'-cold-trail.png')),scale=3)
   checks.append(dict(case=tag,actual_clerk_A=True,actual_yesno=True,native_menu_SAVE=cold,no_RAM_writes=True,no_direct_MistyJoin=True,party_pc_dex_preserved=True,pikachu_at_start=len(pikachu_before),received_starter_flag_cold_control=no_pika,pass_all=True))
   print(json.dumps(checks[-1]),flush=True)
 status.update(all_pass=len(checks)==4)
except Exception as ex:status.update(error=repr(ex),traceback=traceback.format_exc())
finally:
 unchanged=all(digest(f.read_bytes())==h for f,h in originals.items());status.update(checks=checks,original_inputs_unchanged=unchanged,rom_sha256=digest(rom.read_bytes()),automatic_Pallet_Oak_flow_tested=False,actual_device_DELTA_tested=False)
 if not unchanged:status['all_pass']=False
 (out/'misty-airport-result.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status),flush=True)
