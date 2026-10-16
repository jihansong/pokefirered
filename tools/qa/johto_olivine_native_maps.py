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
cases=[]
def link(tag,where,key,dest,surf=False):
 cases.append(dict(name=tag,where=where,key=key,dest=dest,surf=surf))
link('ecruteak_west_into_gate',('EcruteakCity',1,21),'UP','EcruteakCity_WestGate')
link('west_gate_back_ecruteak',('EcruteakCity_WestGate',7,9),'DOWN','EcruteakCity')
link('west_gate_into_route38',('EcruteakCity_WestGate',7,2),'UP','JohtoRoute38')
link('route38_back_west_gate',('JohtoRoute38',34,10),'UP','EcruteakCity_WestGate')
link('route38_left_to_route39',('JohtoRoute38',0,11),'LEFT','JohtoRoute39')
link('route39_right_to_route38',('JohtoRoute39',23,15),'RIGHT','JohtoRoute38')
link('route39_down_to_olivine',('JohtoRoute39',9,31),'DOWN','OlivineCity')
link('olivine_up_to_route39',('OlivineCity',19,0),'UP','JohtoRoute39')
link('olivine_left_to_route40',('OlivineCity',0,25),'LEFT','JohtoRoute40')
link('route40_right_to_olivine',('JohtoRoute40',23,17),'RIGHT','OlivineCity')
link('route40_surf_down_to_route41',('JohtoRoute40',5,35),'DOWN','JohtoRoute41',True)
link('route41_surf_up_to_route40',('JohtoRoute41',5,0),'UP','JohtoRoute40',True)
link('route41_surf_left_to_cianwood',('JohtoRoute41',0,15),'LEFT','CianwoodCity',True)
link('cianwood_surf_right_to_route41',('CianwoodCity',27,23),'RIGHT','JohtoRoute41',True)
for city,entries in [('OlivineCity',[('PokemonCenter_1F',7,19,7,7),('Mart',15,18,4,6),('Gym',28,7,6,13),('Cafe',6,8,4,6),('LIGHTHOUSE',32,26,11,17)]),
 ('CianwoodCity',[('PokemonCenter_1F',5,24,7,7),('Pharmacy',15,23,4,6),('Gym',9,7,6,13)])]:
 for suffix,x,y,ex,ey in entries:
  interior='OlivineLighthouse_1F' if suffix=='LIGHTHOUSE' else city+'_'+suffix
  link(city.lower()+'_enter_'+suffix.lower(),(city,x,y+1),'UP',interior)
  link(city.lower()+'_exit_'+suffix.lower(),(interior,ex,ey),'DOWN',city)
for city in ['OlivineCity','CianwoodCity']:
 link(city.lower()+'_center_upstairs',(city+'_PokemonCenter_1F',2,6),'LEFT',city+'_PokemonCenter_2F')
 link(city.lower()+'_center_downstairs',(city+'_PokemonCenter_2F',2,6),'LEFT',city+'_PokemonCenter_1F')
stairs=[
 ('OlivineLighthouse_1F',17,9,'RIGHT','OlivineLighthouse_2F'),
 ('OlivineLighthouse_2F',17,10,'RIGHT','OlivineLighthouse_1F'),
 ('OlivineLighthouse_2F',5,10,'LEFT','OlivineLighthouse_3F'),
 ('OlivineLighthouse_3F',5,10,'LEFT','OlivineLighthouse_2F'),
 ('OlivineLighthouse_3F',17,10,'RIGHT','OlivineLighthouse_4F'),
 ('OlivineLighthouse_4F',17,10,'RIGHT','OlivineLighthouse_3F'),
 ('OlivineLighthouse_4F',5,10,'LEFT','OlivineLighthouse_5F'),
 ('OlivineLighthouse_5F',5,10,'LEFT','OlivineLighthouse_4F'),
 ('OlivineLighthouse_5F',17,10,'RIGHT','OlivineLighthouse_6F'),
 ('OlivineLighthouse_6F',12,16,'LEFT','OlivineLighthouse_5F')]
for i,(n,x,y,key,dest) in enumerate(stairs):link('lighthouse_inverse_stair_'+str(i+1),(n,x,y),key,dest)
assert len(cases)==44
def cross(e,c):
 target=map_info(c['dest'])
 for tap in range(5):
  e.hold(c['key']);e.run(1);e.hold();e.run(120)
  if e.location()[:2]==(target['group'],target['num']):
   settle(e);return tap+1
  assert e.in_overworld() and not e.in_battle(),(c['name'],'unexpected battle or callback')
 raise AssertionError((c['name'],'inverse link did not transition',e.location(),c['dest']))
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='olivine-native-links-') as td:
  for c in cases:
   target=Path(td)/(c['name']+'.sav');prepared=fixture(target,c)
   for n in ['CHAD','DEREK','PRESTON','HUEY','ERNEST','RANDALL','DENISE','YOSHI','CHUCK','JASMINE']:
    prepared.set_trainer_beaten('TRAINER_JOHTO_'+n,True)
   prepared.set_flag('FLAG_SYS_CRUISE_MODE',False);prepared.save(str(target))
   with ReadOnlyEmu(str(rom),str(target),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    if c['surf']:assert e.u8(syms['gPlayerAvatar'])&8,(c['name'],'water fixture did not boot into native Surf')
    taps=cross(e,c);after=snapshot(e)
    for field in ['flags','trainers','items','pc','party','party_count','dex','pc_hm','pc_hm3','pc_hm02','pc_hm04']:
     assert after[field]==before[field],(c['name'],'unexpected source state change',field)
    if c['surf']:assert e.u8(syms['gPlayerAvatar'])&8,(c['name'],'native Surf lost at sea connection')
    e.shot(str(out/(c['name']+'.png')),scale=3)
    row={'case':c['name'],'from':c['where'],'key':c['key'],'to':c['dest'],'actual_location':e.location(),'fresh_native_taps':taps,'surf':c['surf'],'party_pc_dex_flags_preserved':True,'forced_memory_writes':0}
    results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sha in originals.items():assert digest(path.read_bytes())==sha,('original changed',str(path))
assert len(results)==44
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,'original_files_unchanged':True,'forced_memory_writes':0},indent=2))
