from pathlib import Path
import sys,json,hashlib,struct,traceback,datetime
root=Path('/workspaces/pokefirered');w=root/'work/hoenn-devon-native-20261013';out=w/'native-v4';out.mkdir(parents=True)
rom=root/'pokemonthyl.gba';elf=root/'pokemonthyl.elf';sav=root/'saves/pokemonthyl_v1.25-items99-iv2x.sav'
sys.argv=['devon','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
q=(root/'tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split(chr(10)+'results=[];rows=[]'+chr(10))[0],'<verified-definitions-only>','exec'))
report={'pass':False,'status':'running','ROM_sha256':digest(rom.read_bytes()),'RAM_writes':0,'direct_script_calls':0,'forced_battle_outcomes':0,'cases':[],'stages':[],'scope':'Preboot eligible fixtures; actual Roxanne battle and continuous Gym exit to Devon coord; not whole campaign'}
protected={f:digest(f.read_bytes()) for f in list((root/'saves').glob('*.sav'))+[rom,elf]}
status_file=root/'outputs/regional-starters-20261013/devon-native-status.json'
e=None
F=['FLAG_HOENN_BADGE01_GET','FLAG_HOENN_DEFEATED_RUSTBORO_GYM','FLAG_HOENN_GOT_TM39_FROM_ROXANNE','FLAG_HIDE_HOENN_RUSTBORO_THIEF','FLAG_HOENN_WOODS_RESEARCHER_SAVED']
def emit():
 text=json.dumps(report,indent=2);(out/'validation.json').write_text(text);status_file.write_text(text)
def state():
 b=blocks(e);return {'position':e.location(),'devon_scene':b.var('VAR_HOENN_SCENE_DEVON'),'flags':{f:b.flag(f) for f in F},'roxanne_beaten':b.trainer_beaten('TRAINER_HOENN_ROXANNE_1'),'idle':bool(e.field_idle())}
def stage(tag):
 report['stages'].append({'stage':tag,**state()});emit()
def idle():
 for _ in range(1500):
  safe(e)
  if e.field_idle():return
  assert not e.in_battle(),'unexpected battle while dismissing event'
  e.press('B',hold=2,after=14)
 raise AssertionError(('event did not finish',state()))
def step(k,warp=False):
 start=e.location();dx,dy={'UP':(0,-1),'DOWN':(0,1),'LEFT':(-1,0),'RIGHT':(1,0)}[k];want=(*start[:2],start[2]+dx,start[3]+dy)
 e.hold(k)
 try:
  for _ in range(120):
   e.run(1)
   if e.location()!=start:break
  else:raise AssertionError(('step blocked',start,k))
 finally:e.hold()
 if not warp:assert e.location()==want,('step overshot',start,k,e.location())
 idle();e.run(20)
 if not warp:assert e.location()==want
 return e.location()
def partyprofiles(raw,n):
 v=[]
 for i in range(n):
  a=raw[i*100:i*100+100];m=Mon(bytearray(a),0);subs=m.subs();assert not a[19]&1
  assert sum(x[0] for s in subs.values() for x in struct.iter_unpack('<H',s))&65535==struct.unpack_from('<H',a,28)[0]
  v.append((a,m,subs))
 return v
def preserve(before):
 after=snapshot(e);assert after['pc']==before['pc'];assert after['party_count']==before['party_count']
 ledger=[]
 for i,(old,new) in enumerate(zip(partyprofiles(before['party'],before['party_count']),partyprofiles(after['party'],after['party_count']))):
  a,m,s=old;b,n,t=new
  assert (m.personality,m.otid,m.species())==(n.personality,n.otid,n.species())
  assert a[:28]==b[:28] and s['M']==t['M']
  assert s['G'][:4]==t['G'][:4] and s['G'][8:9]==t['G'][8:9] and s['G'][10:]==t['G'][10:]
  assert s['A'][:8]==t['A'][:8] and s['E'][6:]==t['E'][6:]
  ledger.append({'slot':i,'pid':m.personality,'species':m.species(),'EXP_before_after':[struct.unpack_from('<I',s['G'],4)[0],struct.unpack_from('<I',t['G'],4)[0]],'friendship_before_after':[s['G'][9],t['G'][9]],'EV_before_after':[list(s['E'][:6]),list(t['E'][:6])],'PP_before_after':[list(s['A'][8:]),list(t['A'][8:])],'party_cache_changed':a[80:]!=b[80:],'checksum_ok':True,'IV_and_origin_preserved':True})
 for a,b in zip(before['dex'],after['dex']):assert all(not x or y for x,y in zip(a,b)),'lost dex bits'
 return ledger
def fixture(scene):
 s=SaveFile(str(sav));s.fast_battles();s.set_flag('FLAG_SYS_GAME_CLEAR',True)
 s.set_flag('FLAG_HOENN_BIRCH_RESCUED',True);s.set_var('VAR_HOENN_SCENE_BIRCH',3);s.set_var('VAR_HOENN_SCENE_DEVON',scene)
 s.set_flag('FLAG_HOENN_ROCKET_WOODS',True);s.set_trainer_beaten('TRAINER_HOENN_GRUNT_PETALBURG_WOODS',True)
 s.set_flag('FLAG_HOENN_WOODS_RESEARCHER_SAVED',scene==1)
 for f in F[:3]:s.set_flag(f,False)
 s.set_trainer_beaten('TRAINER_HOENN_ROXANNE_1',False)
 for t in ['TRAINER_HOENN_JOSH','TRAINER_HOENN_TOMMY','TRAINER_HOENN_MARC']:s.set_trainer_beaten(t,True)
 s.set_item('ITEM_TM39',0);s.set_item('ITEM_TM_CASE',1)
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 s.set_var('VAR_REPEL_STEP_COUNT',250);s.warp('RustboroCity_Gym',5,3)
 f=out/('scene'+str(scene)+'-before-QA-only.sav');s.save(str(f));return f
try:
 assert report['ROM_sha256']=='63904802b37dc5e922ec616361c0be3388f1030e5b2c1a0b7a2949f2a33c1f7c'
 for scene in [1,0]:
  f=fixture(scene);e=ReadOnlyEmu(str(rom),str(f),sym='');e.syms=syms;e.boot_continue();settle(e);e.run(30);before=snapshot(e);stage('scene%d-Gym-start'%scene)
  report['objects_before_talk']=object_rows(e,1);report['active_objects']=[{'i':i,'local':e.u8(syms['gObjectEvents']+36*i+off('misty_obj.local')),'flags':e.u32(syms['gObjectEvents']+36*i),'xy':list(struct.unpack('<hh',e.read(syms['gObjectEvents']+36*i+off('misty_obj.coords'),4))),'face':e.u8(syms['gObjectEvents']+36*i+24)} for i in range(16) if e.u8(syms['gObjectEvents']+36*i)&1];emit();e.shot(str(out/'gym-before.png'),scale=3);e.press('UP',hold=4,after=30);assert e.location()[2:]==(5,3)
  e.press('A',hold=3,after=12);mash_until(e,e.in_battle,300);assert menu(e)
  assert e.u16(syms['gTrainerBattleOpponent_A'])==const('TRAINER_HOENN_ROXANNE_1')
  turns=0
  while menu(e):
   assert turns<60,'Roxanne did not finish';fight_one_turn(e,loss=False);turns+=1
  report['after_battle_before_dismiss']=state();report['outcome_before_dismiss']=e.u8(syms['gBattleOutcome']);emit();e.shot(str(out/'after-battle.png'),scale=3);idle();assert blocks(e).trainer_beaten('TRAINER_HOENN_ROXANNE_1')
  assert e.u8(syms['gBattleOutcome'])==const('B_OUTCOME_WON')
  assert all(blocks(e).flag(f) for f in F[:3]) and blocks(e).item_count('ITEM_TM39')==1
  stage('scene%d-Roxanne-win'%scene);e.shot(str(out/('scene%d-gym.png'%scene)),scale=3)
  step('RIGHT')
  for _ in range(15):step('DOWN')
  step('LEFT');step('DOWN',warp=True)
  city=map_info('RustboroCity');assert e.location()[:2]==(city['group'],city['num']),e.location()
  stage('scene%d-Gym-exit'%scene)
  x,y=e.location()[2:]
  while x>23:step('LEFT');x,y=e.location()[2:]
  assert e.location()[2]==23 and 20<=e.location()[3]<=24,e.location()
  idle();stage('scene%d-Devon-coord-complete'%scene)
  assert blocks(e).var('VAR_HOENN_SCENE_DEVON')==(2 if scene==1 else 0)
  assert blocks(e).flag('FLAG_HIDE_HOENN_RUSTBORO_THIEF')
  ledger=preserve(before);e.shot(str(out/('scene%d-city.png'%scene)),scale=3)
  saved_state=state();save=flash_reload(e,'scene%d-Devon'%scene);assert state()==saved_state
  preserve(before);stage('scene%d-native-SAVE-cold'%scene)
  report['cases'].append({'scene_at_boot':scene,'pass':True,'actual_Roxanne_win':True,'turns':turns,'continuous_Gym_exit_and_City_coord':True,'expected_theft':scene==1,'SAVE_cold':save,'party_changes':ledger,'PC_33744_bytes_preserved':True,'existing_damaged_PC_record_preserved':True});emit();e.close();e=None
 report['pass']=len(report['cases'])==2;report['status']='complete'
except Exception as err:
 report['error']=repr(err);report['traceback']=traceback.format_exc();report['status']='failed';report['failure_state']=state() if e is not None else {};report['script_context_raw']=e.read(syms['gScriptContext1'],160).hex() if e is not None else '';report['battle_outcome_failure']=e.u8(syms['gBattleOutcome']) if e is not None else -1;e.shot(str(root/'outputs/regional-starters-20261013/devon-failure.png'),scale=3) if e is not None else None
finally:
 if e is not None:e.close()
 report['protected_original_inputs_unchanged']=all(digest(f.read_bytes())==h for f,h in protected.items());emit()
print(json.dumps({'pass':report['pass'],'status':report['status'],'cases':len(report['cases']),'error':report.get('error')}),flush=True)
