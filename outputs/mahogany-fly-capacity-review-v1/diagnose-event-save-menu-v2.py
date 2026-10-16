#!/usr/bin/env python3
"""Native Ilex story/reward fixtures and menu-save/cold-load checks.
Usage: SCRIPT VERIFIED_VIOLET_QA --rom ROM --elf ELF --sav SAV --out NEWDIR
Uses temporary SAV fixtures, native inputs, and no game-memory writes.
"""
from pathlib import Path
import hashlib,sys
base=Path(sys.argv.pop(1));text=base.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='83c4557b96c344b241fc6f79e9b17722acfc0b0e81e0f9e6d649ff5d8b1c84bb'
assert text.count('\nresults=[]\n')==1
exec(compile(text.split('\nresults=[]\n')[0],str(base),'exec'),globals())
_original_fixture=fixture
_original_snapshot=snapshot
P='FLAG_JOHTO_SILVER_AZALEA_DEFEATED'
F='FLAG_JOHTO_ILEX_FARFETCHD_RETURNED'
C='FLAG_JOHTO_ILEX_CUT_BRIEFED'
G='FLAG_JOHTO_BADGE03_GET'
Q='FLAG_JOHTO_ILEX_HELP_REQUESTED'
R='FLAG_JOHTO_GOLDENROD_RESEARCH_REGISTERED'
N='FLAG_JOHTO_WHITNEY_ENCOURAGED'
U='FLAG_JOHTO_GOT_TM45_FROM_WHITNEY'
J='FLAG_JOHTO_BADGE02_GET'
STORY=[P,F,C,G,Q,R,N,U,J]
ACTORS=['SILVER_AZALEA','WHITNEY']
ITEMS=['ITEM_HM01','ITEM_TM48','ITEM_TM45']
def pc_item(s,item,qty):
 iid=const(item);start=off('sb1.pcItems');slots=[start+i*4 for i in range(const('PC_ITEMS_COUNT'))]
 for pos in slots:
  old,n=struct.unpack_from('<HH',s.sb1,pos)
  if old==iid:
   struct.pack_into('<HH',s.sb1,pos,iid if qty else 0,qty);return
 if not qty:return
 for pos in slots:
  if struct.unpack_from('<H',s.sb1,pos)[0]==0:
   struct.pack_into('<HH',s.sb1,pos,iid,qty);return
 raise AssertionError('QA fixture has no free PC-item slot')
def pc_count(b,item):
 iid=const(item);start=off('sb1.pcItems')
 return sum(n for old,n in struct.iter_unpack('<HH',bytes(b.sb1[start:start+const('PC_ITEMS_COUNT')*4])) if old==iid)
def fixture(path,c):
 s=_original_fixture(path,'FALKNER',c.get('loss',False))
 for f in [T,H,B,M,J]:s.set_flag(f,True)
 for tr in ['LI','FALKNER','BUGSY']:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,True)
 for f in STORY:s.set_flag(f,False)
 s.set_flag(J,True);s.set_flag(P,True)
 for f,v in c.get('flags',{}).items():s.set_flag(f,v)
 for tr in ACTORS:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,c.get('trainers',{}).get(tr,False))
 s.set_flag('FLAG_GOT_HM01',c.get('history',False))
 for item in ITEMS:s.set_item(item,c.get('items',{}).get(item,0))
 s.set_item('ITEM_TM_CASE',c.get('tm_case',1));pc_item(s,'ITEM_HM01',c.get('pc_hm',0))
 if c.get('party_cut'):
  m=s.party_mon(0);sub=m.subs();struct.pack_into('<H',sub['A'],0,const('MOVE_CUT'));sub['A'][8]=30;m.put_subs(sub)
 s.set_var('VAR_REPEL_STEP_COUNT',250)
 s.warp(*c['where']);s.save(str(path));return s
def snapshot(e):
 d=_original_snapshot(e);b=blocks(e)
 d['flags'].update({f:b.flag(f) for f in STORY+['FLAG_GOT_HM01']})
 d['trainers'].update({n:b.trainer_beaten('TRAINER_JOHTO_'+n) for n in ACTORS})
 d['items']={n:b.item_count(n) for n in ITEMS}
 d['pc_hm']=pc_count(b,'ITEM_HM01')
 return d
def interaction(e,c):
 marker=syms[c['marker']]
 token=e.read(marker,24).split(b'\xff')[0]
 assert len(token)>=8
 seen=[False];oldrun=e.run
 def watch_run(frames=1):
  oldrun(frames)
  if token in e.sym_read('gStringVar4',256):seen[0]=True
 e.run=watch_run
 try:
  e.walk(c.get('direction','UP'),1);e.run(30);e.press('A',hold=3,after=12);settle(e)
 finally:e.run=oldrun
 assert seen[0],('dialogue branch not seen',c['name'],c['marker'])
 assert e.in_overworld() and not e.in_battle()
def follower_map_object(e,local_id,x,y):
 group,num,_,_=e.location();obj=e.read(syms['gObjectEvents'],36*const('OBJECT_EVENTS_COUNT'))
 found=[]
 for i in range(0,len(obj),36):
  row=obj[i:i+36]
  if row[0]&1 and row[8]==local_id and row[9]==num and row[10]==group:
   found.append(struct.unpack_from('<hh',row,16))
 assert found==[(x+7,y+7)],('native object position',found,(x,y))
_ilex_fixture=fixture
_ilex_snapshot=snapshot
BASE_STORY=STORY[:];BASE_ACTORS=ACTORS[:];BASE_ITEMS=ITEMS[:]
D='FLAG_JOHTO_BADGE04_GET'
W='FLAG_JOHTO_SQUIRTBOTTLE_RECEIVED'
O='FLAG_JOHTO_SUDOWOODO_CLEARED'
Z='FLAG_JOHTO_BURNED_TOWER_INVESTIGATED'
S='FLAG_JOHTO_SILVER_BURNED_TOWER_DEFEATED'
Y='FLAG_JOHTO_GOT_TM30_FROM_MORTY'
H3='FLAG_JOHTO_DANCE_SURF_REWARDED'
KIMONO=['KIMONO_'+x for x in ['NAOKO','SAYO','ZUKI','KUNI','MIKI']]
STORY=BASE_STORY+[D,W,O,Z,S,Y,H3]
ACTORS=BASE_ACTORS+KIMONO+['SILVER_BURNED_TOWER','MORTY']
ITEMS=BASE_ITEMS+['ITEM_HM03','ITEM_TM35','ITEM_TM30']
def fixture(path,c):
 s=_ilex_fixture(path,c)
 for f in [F,C,G,Q,R,N,U]:s.set_flag(f,True)
 for tr in BASE_ACTORS:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,True)
 for f in [D,W,O,Z,S,Y,H3]:s.set_flag(f,False)
 for tr in KIMONO+['SILVER_BURNED_TOWER','MORTY']:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,False)
 for f,v in c.get('flags',{}).items():s.set_flag(f,v)
 for tr,v in c.get('trainers',{}).items():s.set_trainer_beaten('TRAINER_JOHTO_'+tr,v)
 s.set_flag('FLAG_GOT_HM03',c.get('surf_history',False))
 pc_item(s,'ITEM_HM03',c.get('pc_hm3',0))
 if c.get('party_surf'):
  m=s.party_mon(0);sub=m.subs();struct.pack_into('<H',sub['A'],0,const('MOVE_SURF'));sub['A'][8]=15;m.put_subs(sub)
 s.set_var('VAR_TEMP_0',0);s.warp(*c['where']);s.save(str(path));return s
def snapshot(e):
 d=_ilex_snapshot(e);b=blocks(e)
 d['flags']['FLAG_GOT_HM03']=b.flag('FLAG_GOT_HM03')
 d['pc_hm3']=pc_count(b,'ITEM_HM03')
 return d
def native_step(e,key):
 start=e.location();dx,dy={'UP':(0,-1),'DOWN':(0,1),'LEFT':(-1,0),'RIGHT':(1,0)}[key]
 target=(start[2]+dx,start[3]+dy)
 # The first tap may only turn the player; the next tap must move exactly one square.
 for _ in range(2):
  e.hold(key);e.run(1);e.hold();e.run(24)
  now=e.location()
  if now[2:]!=start[2:]:
   assert now[:2]==start[:2] and now[2:]==target,('native single step',start,now,target)
   return
 raise AssertionError(('native step did not move',start,e.location(),key))
def interaction(e,c):
 marker=c.get('marker');seen=[False];oldrun=e.run
 token=e.read(syms[marker],24).split(b'\xff')[0] if marker else b''
 if marker:assert len(token)>=8
 def watch_run(frames=1):
  oldrun(frames)
  if marker and token in e.sym_read('gStringVar4',256):seen[0]=True
 e.run=watch_run
 try:
  if c.get('step'):
   native_step(e,c.get('direction','UP'))
   settle(e)
  else:
   e.walk(c.get('direction','UP'),1);e.run(30);e.press('A',hold=3,after=12);settle(e)
 finally:e.run=oldrun
 if marker:assert seen[0],('dialogue branch not seen',c['name'],marker,e.location())
 assert e.in_overworld() and not e.in_battle()

_ecru_fixture=fixture
_ecru_snapshot=snapshot
B5='FLAG_JOHTO_BADGE05_GET'
B6='FLAG_JOHTO_BADGE06_GET'
REQ='FLAG_JOHTO_LIGHTHOUSE_MEDICINE_REQUESTED'
MED='FLAG_JOHTO_CIANWOOD_MEDICINE_RECEIVED'
CURED='FLAG_JOHTO_AMPHY_CURED'
CTM='FLAG_JOHTO_GOT_TM01_FROM_CHUCK'
FLY='FLAG_JOHTO_FLY_REWARDED'
JTM='FLAG_JOHTO_GOT_TM23_FROM_JASMINE'
HIDE='FLAG_HIDE_JOHTO_JASMINE_GYM'
STR='FLAG_JOHTO_STRENGTH_REWARDED'
NEW_STORY=[B5,B6,REQ,MED,CURED,CTM,FLY,JTM,HIDE,STR]
STORY+=NEW_STORY
ACTORS+=['CHUCK','JASMINE']
ITEMS+=['ITEM_HM02','ITEM_TM02','ITEM_HM04','ITEM_TM08','ITEM_TM01','ITEM_TM23']
def fixture(path,c):
 s=_ecru_fixture(path,c)
 for f in [D,W,O,Z,S,Y,H3]:s.set_flag(f,True)
 for tr in KIMONO+['SILVER_BURNED_TOWER','MORTY']:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,True)
 for f in NEW_STORY:s.set_flag(f,f==HIDE)
 for f,v in c.get('flags',{}).items():s.set_flag(f,v)
 for tr in ['CHUCK','JASMINE']:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,c.get('trainers',{}).get(tr,False))
 for num in ['02','04']:
  s.set_flag('FLAG_GOT_HM'+num,c.get('hm'+num+'_history',False))
  pc_item(s,'ITEM_HM'+num,c.get('pc_hm'+num,0))
 s.set_var('VAR_TEMP_0',0);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
 s.warp(*c['where']);s.save(str(path));return s
def snapshot(e):
 d=_ecru_snapshot(e);b=blocks(e)
 for num in ['02','04']:
  d['flags']['FLAG_GOT_HM'+num]=b.flag('FLAG_GOT_HM'+num)
  d['pc_hm'+num]=pc_count(b,'ITEM_HM'+num)
 return d
def object_absent(e,local_id):
 group,num,_,_=e.location();raw=e.read(syms['gObjectEvents'],36*const('OBJECT_EVENTS_COUNT'))
 assert not any(row[0]&1 and row[8]==local_id and row[9]==num and row[10]==group for row in [raw[i:i+36] for i in range(0,len(raw),36)]),'hidden Jasmine still present'

_olivine_fixture=fixture
_olivine_snapshot=snapshot
B7='FLAG_JOHTO_BADGE07_GET'
RED='FLAG_JOHTO_RED_GYARADOS_RESOLVED'
JOIN='FLAG_JOHTO_LANCE_INVESTIGATION_JOINED'
SCALE='FLAG_JOHTO_RED_SCALE_RECEIVED'
E1='FLAG_JOHTO_HQ_ELECTRODE1_CLEARED'
E2='FLAG_JOHTO_HQ_ELECTRODE2_CLEARED'
E3='FLAG_JOHTO_HQ_ELECTRODE3_CLEARED'
HQ='FLAG_JOHTO_ROCKET_HQ_CLEARED'
LTM='FLAG_JOHTO_LANCE_TM24_RECEIVED'
PTM='FLAG_JOHTO_PRYCE_TM13_RECEIVED'
RADIO='FLAG_JOHTO_RADIO_TOWER_CLEARED'
MOVED='FLAG_JOHTO_LANCE_MOVED_TO_HQ'
MAHO_FLAGS=[B7,RED,JOIN,SCALE,E1,E2,E3,HQ,LTM,PTM,RADIO,MOVED]
MAHO_ACTORS=['HARRISON','MARKUS','TIFFANY','HQ_GUARD_A','HQ_GUARD_B','HQ_SCIENTIST','PETREL','ARIANA','PRYCE']
STORY+=MAHO_FLAGS
ACTORS+=MAHO_ACTORS
ITEMS+=['ITEM_RED_SCALE','ITEM_TM24','ITEM_TM13']
def fixture(path,c):
 context=dict(c)
 context['flags']={B5:True,B6:True,REQ:True,MED:True,CURED:True,CTM:True,FLY:True,JTM:True,HIDE:False,STR:True}
 context['flags'].update(c.get('flags',{}))
 context['trainers']={'CHUCK':True,'JASMINE':True}
 context['trainers'].update(c.get('trainers',{}))
 s=_olivine_fixture(path,context)
 for f in MAHO_FLAGS:s.set_flag(f,False)
 for f,v in c.get('flags',{}).items():s.set_flag(f,v)
 for n in MAHO_ACTORS:s.set_trainer_beaten('TRAINER_JOHTO_'+n,c.get('trainers',{}).get(n,False))
 s.set_flag('FLAG_SYS_SPECIAL_WILD_BATTLE',False)
 s.set_flag('FLAG_SYS_CRUISE_MODE',False)
 s.set_var('VAR_TEMP_0',0)
 s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
 s.warp(*c['where']);s.save(str(path));return s
def snapshot(e):
 d=_olivine_snapshot(e)
 d['flags']['FLAG_SYS_SPECIAL_WILD_BATTLE']=blocks(e).flag('FLAG_SYS_SPECIAL_WILD_BATTLE')
 return d
PRESERVE=['pc','party','party_count','dex','pc_hm','pc_hm3','pc_hm02','pc_hm04']
def native_face(e,key):
 e.hold(key);e.run(1);e.hold();e.run(24)
def interaction(e,c):
 marker=c.get('marker');seen=[False];oldrun=e.run
 token=e.read(syms[marker],24).split(b'\xff')[0] if marker else b''
 if marker:assert len(token)>=8
 def watch_run(frames=1):
  oldrun(frames)
  if marker and token in e.sym_read('gStringVar4',256):seen[0]=True
 e.run=watch_run
 try:
  if c.get('step'):
   native_step(e,c.get('direction','UP'));settle(e)
  else:
   if not c.get('face_only'):native_step(e,c.get('direction','UP'))
   else:native_face(e,c.get('direction','UP'))
   e.press('A',hold=3,after=12);settle(e)
 finally:e.run=oldrun
 if marker:assert seen[0],('native dialogue not observed',c['name'],marker,e.location())
 assert e.in_overworld() and not e.in_battle()

cases=[]
def add(name,where,marker,**kw):cases.append(dict(name=name,where=where,marker=marker,**kw))
GATE=('EcruteakCity_EastGate',7,4)
LANCE=('LakeOfRage',22,29)
SHOP=('MahoganyTown_Shop',3,5)
STEPS=('MahoganyTown_Shop',7,3)
POWER=('JohtoRocketHQ_B3F',8,10)
GYM=('MahoganyTown_Gym',6,7)
basepower={RED:True,JOIN:True,SCALE:True,E1:True,E2:True,E3:True,MOVED:True}
add('east_gate_requires_badge6',GATE,'EcruteakCity_EastGate_Text_Before',step=True,flags={B6:False})
add('east_gate_opens_with_badge6',GATE,None,step=True)
add('lance_requires_gyarados_resolution',LANCE,'LakeOfRage_Text_LanceBefore')
add('lance_joins_and_gives_scale',LANCE,'LakeOfRage_Text_LanceJoined',flags={RED:True},expect_flags={JOIN:True,SCALE:True},delta={'ITEM_RED_SCALE':1})
add('lance_join_does_not_duplicate_scale',LANCE,'LakeOfRage_Text_LanceJoined',flags={RED:True,JOIN:True,SCALE:True})
add('lance_full_scale_still_joins',LANCE,'LakeOfRage_Text_LanceFull',flags={RED:True},items={'ITEM_RED_SCALE':999},expect_flags={JOIN:True,SCALE:False})
add('lance_scale_retry',LANCE,'LakeOfRage_Text_LanceJoined',flags={RED:True,JOIN:True},items={'ITEM_RED_SCALE':998},expect_flags={SCALE:True},delta={'ITEM_RED_SCALE':1})
add('shop_clerk_requires_lance',SHOP,'MahoganyTown_Shop_Text_Before')
add('shop_stair_requires_lance',STEPS,'MahoganyTown_Shop_Text_Before',step=True)
add('shop_stair_opens_with_investigation',STEPS,None,step=True,flags={JOIN:True},expect_flags={MOVED:True},dest='JohtoRocketHQ_B1F')
add('shop_clerk_native_warp',SHOP,'MahoganyTown_Shop_Text_Entry',flags={JOIN:True},expect_flags={MOVED:True},dest='JohtoRocketHQ_B1F',xy=(6,17))
add('hq_security_requires_petrel',('JohtoRocketHQ_B2F',28,3),'JohtoRocketHQ_B2F_Text_Closed',step=True,flags={JOIN:True})
add('hq_security_opens_after_petrel',('JohtoRocketHQ_B2F',28,3),None,step=True,flags={JOIN:True},trainers={'PETREL':True},dest='JohtoRocketHQ_B3F')
for i,x in enumerate([10,16,22],1):
 add('electrode'+str(i)+'_requires_ariana',('JohtoRocketHQ_B3F',x,14),'JohtoRocketHQ_B3F_Text_ExecutiveFirst',flags={JOIN:True})
for f in [E1,E2,E3]:
 flags=dict(basepower);flags[f]=False
 add('lance_requires_'+f.split('_')[-2].lower(),POWER,'JohtoRocketHQ_B3F_Text_NotReady',flags=flags)
add('lance_stops_signal_and_rewards',POWER,'JohtoRocketHQ_B3F_Text_After',flags=basepower,expect_flags={HQ:True,LTM:True},delta={'ITEM_TM24':1})
add('lance_tm_full_does_not_block_story',POWER,'JohtoRocketHQ_B3F_Text_Full',flags=basepower,items={'ITEM_TM24':999},expect_flags={HQ:True})
add('lance_tm_retry',POWER,'JohtoRocketHQ_B3F_Text_After',flags=dict(basepower,**{HQ:True}),items={'ITEM_TM24':998},expect_flags={LTM:True},delta={'ITEM_TM24':1})
add('lance_reward_not_reissued',POWER,'JohtoRocketHQ_B3F_Text_After',flags=dict(basepower,**{HQ:True,LTM:True}))
retry=dict(basepower);retry[SCALE]=False
add('moved_lance_unclaimed_scale_full',POWER,'JohtoRocketHQ_B3F_Text_ScaleFull',flags=retry,items={'ITEM_RED_SCALE':999},expect_flags={HQ:True})
add('moved_lance_unclaimed_scale_retry',POWER,'JohtoRocketHQ_B3F_Text_After',flags=retry,items={'ITEM_RED_SCALE':998},expect_flags={HQ:True,SCALE:True,LTM:True},delta={'ITEM_RED_SCALE':1,'ITEM_TM24':1})
add('pryce_requires_signal_shutdown',GYM,'MahoganyTown_Gym_Text_Before')
add('pryce_requires_badge6',GYM,'MahoganyTown_Gym_Text_Before',flags={HQ:True,B6:False})
add('pryce_remembers_win_badge_on_full_tm',GYM,'MahoganyTown_Gym_Text_Full',flags={HQ:True},trainers={'PRYCE':True},items={'ITEM_TM13':999},expect_flags={B7:True})
add('pryce_tm_retry',GYM,'MahoganyTown_Gym_Text_After',flags={HQ:True,B7:True},trainers={'PRYCE':True},items={'ITEM_TM13':998},expect_flags={PTM:True},delta={'ITEM_TM13':1})
add('pryce_reward_not_reissued',GYM,'MahoganyTown_Gym_Text_After',flags={HQ:True,B7:True,PTM:True},trainers={'PRYCE':True})
add('mahogany_radio_handoff_after_badge7',('MahoganyTown',26,18),'MahoganyTown_Text_RadioNews',flags={B7:True})
add('mahogany_resident_after_hq',('MahoganyTown',12,19),'MahoganyTown_Text_ResidentAfter',flags={HQ:True})
assert len(cases)==32,len(cases)
cases=[c for c in cases if c['name']=='east_gate_opens_with_badge6']
_original_native_save=native_save
def native_save(e):
 def state():
  count=e.u8(e.sym('sNumStartMenuItems'))
  names=['sGlobalScriptContextStatus','sGlobalScriptContext','sLockFieldControls','gQuestLogState','gPlayerAvatar','gMain','gScriptContext1','gScriptContext2','gScriptContext2Enabled','sStartMenuCallback','gNewKeys','gHeldKeys']
  return {'count':count,'order':list(e.read(e.sym('sStartMenuOrder'),min(count,16))),'cursor':e.u8(e.sym('sStartMenuCursorPos')),'field_idle':e.field_idle(),'in_overworld':e.in_overworld(),'tasks_hex':e.read(e.sym('gTasks'),640).hex(),'state_hex':{n:e.read(e.sym(n),24).hex() for n in names if n in syms}}
 trace={'before':state()}
 e.run(180);trace['after_quiet']=state()
 try:
  result=_original_native_save(e);trace['after']=state();return result
 except Exception as error:
  trace.update(error=repr(error),after=state());e.shot(str(out/'save-menu-failure.png'),scale=3);raise
 finally:
  (out/'save-menu-debug.json').write_text(json.dumps(trace,indent=2))
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='mahogany-native-events-') as td:
  for c in cases:
   path=Path(td)/(c['name']+'.sav');prepared=fixture(path,c)
   with ReadOnlyEmu(str(rom),str(path),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    interaction(e,c);after=snapshot(e)
    flags=dict(before['flags']);flags.update(c.get('expect_flags',{}))
    assert after['flags']==flags,(c['name'],'story flags',after['flags'],flags)
    assert after['trainers']==before['trainers'],(c['name'],'trainer records changed without battle')
    for item in ITEMS:assert after['items'][item]==before['items'][item]+c.get('delta',{}).get(item,0),(c['name'],item)
    for field in PRESERVE:assert after[field]==before[field],(c['name'],'preservation',field)
    assert after['pc']==bytes(prepared.blocks['storage'])
    if c.get('dest'):
     m=map_info(c['dest']);assert e.location()[:2]==(m['group'],m['num']),(c['name'],'wrong native warp',e.location())
    if c.get('xy'):assert e.location()[2:]==c['xy'],(c['name'],'coordinate warp ignored',e.location())
    e.shot(str(out/(c['name']+'.png')),scale=3);saved=flash_reload(e,c['name'])
    row={'case':c['name'],'dialogue':c['marker'],'save':saved,'party_pc_dex_preserved':True,'forced_memory_writes':0,'forced_outcomes':0}
    results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==len(cases)
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,'original_files_unchanged':True,'forced_memory_writes':0,'forced_outcomes':0},indent=2))
