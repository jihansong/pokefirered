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
 s=_original_fixture(path,'FALKNER',False)
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

cases=[]
def add(name,where,marker,**kw):cases.append(dict(name=name,where=where,marker=marker,**kw))
FLORIST=('GoldenrodCity_NorthGate',4,7)
PATRON=('EcruteakCity_DanceTheater',9,12)
MORTY=('EcruteakCity_Gym',6,5)
kimono={n:True for n in KIMONO}
add('gate_badge3_closed',('GoldenrodCity_NorthGate',7,3),'GoldenrodCity_NorthGate_Text_Stop',flags={G:False},step=True,location=(7,3))
add('gate_badge3_open',('GoldenrodCity_NorthGate',7,3),None,step=True,location=(7,2))
add('florist_before_badge','PLACE','GoldenrodCity_NorthGate_Text_FloristBefore',flags={G:False},expect_flags={W:False})
cases[-1]['where']=FLORIST
add('florist_lends_once',FLORIST,'GoldenrodCity_NorthGate_Text_FloristLend',expect_flags={W:True})
add('florist_lending_repeat',FLORIST,'GoldenrodCity_NorthGate_Text_FloristAfter',flags={W:True})
add('sudowoodo_needs_water',('JohtoRoute36',25,9),'JohtoRoute36_Text_NeedWater',expect_flags={O:False},object=(1,25,8))
add('silver_needs_badge3',('BurnedTower_1F',13,12),'BurnedTower_1F_Text_Before',flags={G:False})
add('tower_cannot_awaken_before_silver',('BurnedTower_B1F',13,11),None,step=True,expect_flags={Z:False},location=(13,10))
add('tower_native_awakening',('BurnedTower_B1F',13,11),'BurnedTower_B1F_Text_Escaped',flags={S:True},step=True,expect_flags={Z:True},seen_added=['RAIKOU','ENTEI','SUICUNE'])
add('tower_awakened_not_repeated',('BurnedTower_B1F',13,11),None,flags={S:True,Z:True},step=True)
add('morty_below_before',('BurnedTower_B1F',13,10),'BurnedTower_B1F_Text_MortyBefore')
add('morty_below_after',('BurnedTower_B1F',13,10),'BurnedTower_B1F_Text_MortyReady',flags={S:True,Z:True})
for absent in KIMONO:
 trainers=dict(kimono);trainers[absent]=False
 add('patron_requires_'+absent.lower(),PATRON,'EcruteakCity_DanceTheater_Text_PatronBefore',trainers=trainers,expect_flags={H3:False})
add('patron_first_surf_hm',PATRON,'EcruteakCity_DanceTheater_Text_Surf',trainers=kimono,expect_flags={H3:True},delta={'ITEM_HM03':1})
add('patron_bag_hm_alternate',PATRON,'EcruteakCity_DanceTheater_Text_Alternate',trainers=kimono,items={'ITEM_HM03':1},expect_flags={H3:True},delta={'ITEM_TM35':1})
add('patron_pc_hm_alternate',PATRON,'EcruteakCity_DanceTheater_Text_Alternate',trainers=kimono,pc_hm3=1,expect_flags={H3:True},delta={'ITEM_TM35':1})
add('patron_history_hm_alternate',PATRON,'EcruteakCity_DanceTheater_Text_Alternate',trainers=kimono,surf_history=True,expect_flags={H3:True},delta={'ITEM_TM35':1})
add('patron_learned_surf_not_history',PATRON,'EcruteakCity_DanceTheater_Text_Surf',trainers=kimono,party_surf=True,expect_flags={H3:True},delta={'ITEM_HM03':1})
add('patron_alternate_full_stack',PATRON,'EcruteakCity_DanceTheater_Text_BagFull',trainers=kimono,surf_history=True,items={'ITEM_TM35':999},expect_flags={H3:False})
add('patron_alternate_retry_space',PATRON,'EcruteakCity_DanceTheater_Text_Alternate',trainers=kimono,surf_history=True,items={'ITEM_TM35':998},expect_flags={H3:True},delta={'ITEM_TM35':1})
add('patron_reward_not_reissued',PATRON,'EcruteakCity_DanceTheater_Text_PatronAfter',flags={H3:True},trainers=kimono)
add('patron_tmcase_created',PATRON,'EcruteakCity_DanceTheater_Text_Surf',trainers=kimono,tm_case=0,expect_flags={H3:True},delta={'ITEM_HM03':1})
add('morty_badge3_gate',MORTY,'EcruteakCity_Gym_Text_NotReady',flags={G:False,Z:True})
add('morty_tower_gate',MORTY,'EcruteakCity_Gym_Text_NotReady')
add('morty_tm_full_keeps_badge',MORTY,'EcruteakCity_Gym_Text_BagFull',flags={D:True},items={'ITEM_TM30':999},expect_flags={D:True,Y:False})
add('morty_tm_retry',MORTY,'EcruteakCity_Gym_Text_TM',flags={D:True},items={'ITEM_TM30':998},expect_flags={Y:True},delta={'ITEM_TM30':1})
add('morty_tm_not_reissued',MORTY,'EcruteakCity_Gym_Text_After',flags={D:True,Y:True})
assert len(cases)==31
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='ecruteak-native-events-') as td:
  for c in cases:
   path=Path(td)/(c['name']+'.sav');prepared=fixture(path,c)
   with ReadOnlyEmu(str(rom),str(path),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    interaction(e,c);after=snapshot(e)
    flags=dict(before['flags']);flags.update(c.get('expect_flags',{}))
    assert after['flags']==flags,(c['name'],'flags',after['flags'],flags)
    assert after['trainers']==before['trainers'],(c['name'],'unexpected battle record')
    for item in ITEMS:assert after['items'][item]==before['items'][item]+c.get('delta',{}).get(item,0)
    for field in ['pc','party','party_count','pc_hm','pc_hm3']:assert after[field]==before[field],(c['name'],'preservation',field)
    allowed={struct.unpack('<H',r.at(syms['sSpeciesToNationalPokedexNum']+(const('SPECIES_'+x)-1)*2,2))[0] for x in c.get('seen_added',[])}
    for dex,(old,new) in enumerate(zip(before['dex'],after['dex']),1):
     assert old[0]==new[0],(c['name'],'caught changed',dex)
     assert new[1:]==(True,True,True) if dex in allowed else new==old,(c['name'],'seen changed',dex,old,new)
    if c.get('location'):assert tuple(e.location()[2:])==c['location'],(c['name'],e.location())
    if c.get('object'):follower_map_object(e,*c['object'])
    assert after['pc']==bytes(prepared.blocks['storage'])
    e.shot(str(out/(c['name']+'.png')),scale=3);saved=flash_reload(e,c['name'])
    if c.get('object'):follower_map_object(e,*c['object'])
    row={'case':c['name'],'native_dialogue':c['marker'],'save':saved,'pc_party_preserved':True,
     'seen_only_added':c.get('seen_added',[]),'forced_memory_writes':0,'forced_battle_outcomes':0}
    results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sha in originals.items():assert digest(path.read_bytes())==sha,('original changed',str(path))
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,
 'original_files_unchanged':True,'forced_memory_writes':0,'forced_battle_outcomes':0},indent=2))
