from pathlib import Path
p=Path('tools/qa/hoenn_gauntlet_save_qa.py').read_text().split('tmp=None; e=None\ntry:',1)[0].replace('len(p)>=6','len(p)>=5')
exec(compile(p,'<native-QA-definitions>','exec'))
report.update(mode='native-airplane-johto-transition',fixture='temporary champion flag and starting position fixture; original party and PC retained')
def yesno(e):
 return any(e.u8(syms['gTasks']+40*i+4) and (e.u32(syms['gTasks']+40*i)&~1) in sets['Task_YesNoMenu_HandleInput'] for i in range(16))
e=None
try:
 with tempfile.TemporaryDirectory(prefix='johto-flight-native-') as td:
  s=SaveFile(str(sav))
  for f in ['FLAG_SYS_GAME_CLEAR','FLAG_MISTY_COMPANION_DECLINED','FLAG_HIDE_MISTY_PALLET',*['FLAG_BADGE%02d_GET'%i for i in range(1,9)]]:s.set_flag(f,True)
  s.set_flag('FLAG_MISTY_COMPANION_JOINED',False)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.sb2[off('sb2.specialSaveWarpFlags')]&=~1;s.warp('KantoAirport',10,6)
  tmp=Path(td)/'fixture.sav';s.save(str(tmp))
  expected_party=bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
  e=ReadOnlyEmu(str(rom),str(tmp),sym='');e.syms=syms;e.boot_continue();settle(e);photo(e,'kanto-before-flight')
  assert loc_is(e,'KantoAirport');e.press('UP',hold=1,after=20);e.press('A',hold=3,after=20)
  for _ in range(360):
   safe(e)
   if yesno(e):break
   e.press('A',hold=2,after=10)
  else:raise AssertionError('Flight ticket YESNO missing')
  assert e.u16(syms['gSpecialVar_LastTalked'])==2
  e.run(40);e.press('A',hold=3,after=25)
  start=e.frame();report['transition_samples']=[]
  for i in range(1200):
   safe(e);assert not e.in_battle()
   if loc_is(e,'JohtoCherrygroveAirstrip') and e.field_idle():break
   if i in [0,20,40,80]:photo(e,'flight-phase-'+str(i));report['transition_samples'].append({'step':i,'frame':e.frame(),'location':e.location(),'callback':hex(e.callback2())})
   e.press('A',hold=1,after=15)
  else:raise AssertionError('Actual airplane never reached idle Johto airstrip')
  e.run(120);photo(e,'johto-arrived-after-actual-flight')
  assert pc(e)==source_pc and e.read(e.ptr('gSaveBlock1Ptr')+off('sb1.playerParty'),600)==expected_party
  assert digest_dex(blocks(e))==digest_dex(source)

  report['walk_stages']=[]
  def shotstage(tag):
   photo(e,tag);report['walk_stages'].append({'stage':tag,'location':e.location(),'frame':e.frame()})
  def step(direction):
   safe(e);assert not e.in_battle()
   e.press(direction,hold=8,after=24)
   for _ in range(180):
    safe(e);assert not e.in_battle()
    if e.field_idle():return
    e.run(1)
   raise AssertionError(('step not idle',e.location()))
  def axis(name,idx,target):
   for _ in range(128):
    assert loc_is(e,name),(name,e.location())
    pos=e.location()
    if pos[idx]==target:return
    step(('RIGHT' if pos[idx]<target else 'LEFT') if idx==2 else ('DOWN' if pos[idx]<target else 'UP'))
    assert e.location()!=pos,('blocked axis',name,idx,target,pos)
   raise AssertionError(('axis timeout',name,e.location()))
  def cross(old,new):
   for _ in range(8):
    if loc_is(e,new):shotstage(new+'-actual-connection');return
    assert loc_is(e,old),(old,new,e.location())
    step('RIGHT')
   raise AssertionError(('east connection failed',old,new,e.location()))
  assert e.location()==(76,0,22,12)
  shotstage('airstrip-actual-arrival')
  axis('JohtoCherrygroveAirstrip',2,31);cross('JohtoCherrygroveAirstrip','JohtoRoute29')
  axis('JohtoRoute29',2,39);cross('JohtoRoute29','NewBarkTown')
  axis('NewBarkTown',2,11);axis('NewBarkTown',3,9);shotstage('NewBarkTown-lab-door')
  for _ in range(4):
   if loc_is(e,'NewBarkTown_ElmsLab'):break
   assert loc_is(e,'NewBarkTown');step('UP')
  assert loc_is(e,'NewBarkTown_ElmsLab'),('lab warp failed',e.location())
  shotstage('ElmsLab-actual-door-entry')
  axis('NewBarkTown_ElmsLab',2,7);axis('NewBarkTown_ElmsLab',3,9)
  e.press('UP',hold=1,after=20);e.press('A',hold=3,after=40)
  assert e.u16(syms['gSpecialVar_LastTalked'])==2
  shotstage('ElmsLab-professor-actual-dialogue')
  for _ in range(600):
   safe(e);assert not e.in_battle()
   if e.field_idle():break
   e.press('A',hold=2,after=10)
  else:raise AssertionError('Professor conversation locked')
  assert pc(e)==source_pc and e.read(e.ptr('gSaveBlock1Ptr')+off('sb1.playerParty'),600)==expected_party
  assert digest_dex(blocks(e))==digest_dex(source)
  report.update(continuous_flight_airstrip_route29_newbark_lab=True,actual_professor_A=True,party_pc_dex_unchanged=True)

  report['pass']=True;report.update(arrival=e.location(),flight_frames=e.frame()-start,native_inputs_only=True,party_pc_dex_unchanged=True)
except Exception as ex:
 report.update(error=repr(ex),traceback=traceback.format_exc())
 if e and e.h:photo(e,'failure')
finally:
 if e:e.close()
 report['original_saves_unchanged']=before=={p:sha(Path(p).read_bytes()) for p in before}
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
