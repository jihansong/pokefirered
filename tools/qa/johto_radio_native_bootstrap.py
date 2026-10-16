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
 raw=e.read(syms[marker],512).split(b'\xff')[0] if marker else b''
 parts=raw.split(b'\xfb');index=c.get('marker_para',0)
 assert not marker or index<len(parts),('missing native dialogue paragraph',marker,index)
 token=parts[index][:24] if marker else b''
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

_maho_fixture=fixture
_maho_snapshot=snapshot
ACCESS='FLAG_JOHTO_RADIO_BASEMENT_ACCESS'
DIRECTOR='FLAG_JOHTO_RADIO_DIRECTOR_RESCUED'
RTM='FLAG_JOHTO_RADIO_GOT_TM11'
HSILVER='FLAG_HIDE_JOHTO_RADIO_SILVER'
HPETREL='FLAG_HIDE_JOHTO_RADIO_PETREL'
ELM='FLAG_JOHTO_ELM_REPORT_DELIVERED'
SEA='FLAG_HOENN_SEAFLOOR_CLEARED'
RAY='FLAG_HOENN_RAYQUAZA_AWAKENED'
RADIO_FLAGS=[ACCESS,DIRECTOR,RTM,HSILVER,HPETREL]
RADIO_ACTORS=['RADIO_GRUNT_A','RADIO_GRUNT_B','RADIO_SCIENTIST','PETREL_RADIO','SILVER_UNDERGROUND',
 'WAREHOUSE_GRUNT_A','WAREHOUSE_GRUNT_B','WAREHOUSE_SCIENTIST','ARIANA_RADIO','ARCHER']
STORY+=RADIO_FLAGS
ACTORS+=RADIO_ACTORS
ITEMS+=['ITEM_TM11']
def fixture(path,c):
 context=dict(c)
 context['flags']={f:True for f in MAHO_FLAGS if f!=RADIO}
 context['flags'][RADIO]=False;context['flags'].update(c.get('flags',{}))
 context['trainers']={n:True for n in MAHO_ACTORS};context['trainers'].update(c.get('trainers',{}))
 s=_maho_fixture(path,context)
 for f in RADIO_FLAGS:s.set_flag(f,c.get('flags',{}).get(f,False))
 for n in RADIO_ACTORS:s.set_trainer_beaten('TRAINER_JOHTO_'+n,c.get('trainers',{}).get(n,False))
 # Preserve the original Hoenn progress unless a specific dialogue boundary is tested.
 for f in [ELM,SEA,RAY]:
  if f in c.get('flags',{}):s.set_flag(f,c['flags'][f])
 s.set_var('VAR_TEMP_0',0);s.warp(*c['where']);s.save(str(path));return s
def snapshot(e):
 d=_maho_snapshot(e);live=blocks(e)
 for f in [ELM,SEA,RAY]:d['flags'][f]=live.flag(f)
 return d
def assert_preserved(before,after,tag):
 for field in PRESERVE:assert before[field]==after[field],(tag,'preservation',field)
def existing_flags(before,c):
 expected=dict(before['flags']);expected.update(c.get('expect_flags',{}));return expected
def cross(e,c):
 target=map_info(c['dest'])
 for tap in range(5):
  e.hold(c['key']);e.run(1);e.hold();e.run(120)
  if e.location()[:2]==(target['group'],target['num']):settle(e);return tap+1
  assert e.in_overworld() and not e.in_battle(),(c['name'],'unexpected battle/callback')
 raise AssertionError((c['name'],'native inverse transition failed',e.location(),c['dest']))
