from pathlib import Path
import hashlib,json,traceback
q=Path('tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
anchor='\nresults=[];rows=[]\n';exec(compile(q.split(anchor)[0],'<Misty-native-definitions>','exec'))
declined='FLAG_MISTY_COMPANION_DECLINED';oakvar='VAR_MAP_SCENE_PALLET_TOWN_OAK';labvar='VAR_MAP_SCENE_PALLET_TOWN_PROFESSOR_OAKS_LAB';old_snapshot=snapshot
def snapshot(e):
 d=old_snapshot(e);b=blocks(e);d['flags'].update({f:b.flag(f) for f in [join,hide,declined,'FLAG_SYS_GAME_CLEAR',*K]});d['raw_story_flags']=bytes(b.sb1[off('sb1.flags'):off('sb1.vars')]);return d
def yesno(e):
 return any(e.u8(e.sym('gTasks')+40*i+4) and (e.u32(e.sym('gTasks')+40*i)&~1)==(syms['Task_YesNoMenu_HandleInput']&~1) for i in range(16))
def answer(e,yes):
 assert yesno(e);e.run(40)
 if not yes:e.press('DOWN',hold=3,after=15)
 e.press('A',hold=3,after=25)
def finish(e):
 for _ in range(600):
  safe(e);assert not e.in_battle();assert not yesno(e),'Repeat invitation'
  if e.field_idle():settle(e);e.run(30);return
  e.press('A',hold=2,after=10)
 raise AssertionError('Dialog did not end')
def diff(a,b):return [(i,x^y) for i,(x,y) in enumerate(zip(a['raw_story_flags'],b['raw_story_flags'])) if x!=y]
def walk_axis(e,axis,target):
 for _ in range(40):
  xy=e.location()[2:];idx=0 if axis=='x' else 1
  if xy[idx]==target:return
  one_tile(e,('RIGHT' if target>xy[0] else 'LEFT') if axis=='x' else ('DOWN' if target>xy[1] else 'UP'))
 raise AssertionError(('walking blocked',e.location(),axis,target))
checks=[];traces=[];status={'all_pass':False,'ram_writes':0,'direct_Join_calls':0,'actual_Champion_battle_replayed':False}
try:
 for branch,oneisland in [('no_one_island',False),('national_lab_return',True)]:
  f=out/(branch+'-fixture.sav');assert not f.exists();s=SaveFile(str(sav))
  s.set_flag('FLAG_SYS_GAME_CLEAR',True)
  for name in K:s.set_flag(name,True)
  s.set_flag(join,False);s.set_flag(declined,False);s.set_flag(hide,True);s.set_flag('FLAG_WORLD_MAP_ONE_ISLAND',oneisland)
  s.set_var(oakvar,2);s.set_var('VAR_TEMP_7',0);s.sb2[off('sb2.specialSaveWarpFlags')]&=~1
  for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.warp('PalletTown',6,8);s.save(str(f))
  with ReadOnlyEmu(str(rom),str(f),sym='') as e:
   e.syms=syms;e.boot_continue(leave_menu_only=True)
   for _ in range(3600):
    if e.in_overworld():break
    e.run(1)
   else:raise AssertionError('Continue did not enter overworld')
   before=record(e);pallet=e.location()[:2];last=None;trace=[];lab_seen=False;lab_finished=False;returned=False
   for n in range(3000):
    safe(e);assert not e.in_battle();b=blocks(e);where=e.location();state=(b.var(oakvar),b.var('VAR_TEMP_7'),b.var(labvar),where,yesno(e))
    if state!=last:trace.append(dict(sample=n,oak=state[0],queued=state[1],lab_scene=state[2],location=where,yesno=state[4]));last=state
    if where[:2]!=pallet:lab_seen=True
    if yesno(e):
     assert b.var(oakvar)==3 and not b.flag(join) and not b.flag(declined)
     assert any(t['oak']==2 and t['queued']==1 for t in trace)
     if oneisland:assert lab_seen and lab_finished and returned,'National-Lab branch not entered'
     break
    if oneisland and lab_seen and not lab_finished and where[:2]!=pallet and b.var(labvar)==8 and e.field_idle():
     lab_finished=True;same_records(e,before);e.shot(str(out/(branch+'-lab-complete.png')),scale=3)
     walk_axis(e,'x',6);walk_axis(e,'y',11);e.hold('DOWN')
     try:
      for _ in range(720):
       e.run(1)
       if e.location()[:2]==pallet:break
      else:raise AssertionError('Lab exit did not warp to Pallet')
     finally:e.hold()
     returned=True;e.run(30);continue
    e.press('A',hold=2,after=10)
   else:raise AssertionError('Oak sequence did not yield Misty prompt')
   traces.append({'branch':branch,'trace':trace});same_records(e,before);e.shot(str(out/(branch+'-auto-prompt.png')),scale=3)
   before_no=snapshot(e);answer(e,False);finish(e);same_records(e,before);after_no=snapshot(e)
   assert diff(before_no,after_no)==[(69,1)];assert not blocks(e).flag(join) and blocks(e).flag(declined)
   e.run(600);assert e.field_idle() and not yesno(e) and not object_rows(e,253)
   cold_no=flash_reload(e,branch+'-no');same_records(e,before);assert snapshot(e)==after_no
   e.run(600);assert e.field_idle() and not yesno(e) and len(object_rows(e,4))==1
   walk_axis(e,'x',7);walk_axis(e,'y',9);walk_axis(e,'x',8)
   pos=e.location();e.press('DOWN',hold=1,after=20);assert e.location()==pos;e.press('A',hold=3,after=20)
   for _ in range(360):
    safe(e)
    if yesno(e):break
    e.press('A',hold=2,after=10)
   else:raise AssertionError('Manual Misty join prompt missing')
   assert e.u16(e.sym('gSpecialVar_LastTalked'))==4
   before_yes=snapshot(e);answer(e,True);finish(e);same_records(e,before);after_yes=snapshot(e)
   assert blocks(e).flag(join) and not blocks(e).flag(declined);assert diff(before_yes,after_yes)==[(68,24),(69,1)]
   cold_yes=flash_reload(e,branch+'-yes');same_records(e,before);assert snapshot(e)==after_yes
   for _ in range(3):one_tile(e,'LEFT')
   assert len(object_rows(e,253))==1 and object_rows(e,253)[0]['visible'];same_records(e,before)
   e.shot(str(out/(branch+'-cold-trail.png')),scale=3)
   checks.append({'branch':branch,'native_no_SAVE_cold':cold_no,'native_manual_yes_SAVE_cold':cold_yes,'queued_behind_Oak':True,'actual_Lab_exit':returned,'party_PC_dex_preserved':True,'pass':True})
   print(json.dumps(checks[-1]),flush=True)
 status['all_pass']=len(checks)==2
except Exception as ex:status.update(error=repr(ex),traceback=traceback.format_exc())
finally:
 status.update(checks=checks,traces=traces,original_inputs_unchanged=all(digest(p.read_bytes())==h for p,h in originals.items()),rom_sha256=digest(rom.read_bytes()))
 (out/'validation.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status),flush=True)
