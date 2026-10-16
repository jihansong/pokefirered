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
TEAMS={'CHUCK':['PRIMEAPE','POLIWRATH'],'JASMINE':['MAGNEMITE','MAGNEMITE','STEELIX']}
POSITIONS={'CHUCK':('CianwoodCity_Gym',6,5),'JASMINE':('OlivineCity_Gym',6,5)}
def battle_fixture(path,name,loss):
 c={'where':POSITIONS[name],'loss':loss}
 if name=='JASMINE':c['flags']={REQ:True,MED:True,CURED:True,B5:True}
 return fixture(path,c)
def battle(e,name,loss,prepared,tag):
 e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
 e.walk('UP',1);e.run(30);e.press('A',hold=3,after=12);mash_until(e,e.in_battle,300);assert menu(e)
 assert e.u16(e.sym('gTrainerBattleOpponent_A'))==const('TRAINER_JOHTO_'+name)
 raw=e.read(syms['gEnemyParty'],600);actual=[Mon(bytearray(raw),i*100).species() for i in range(6) if Mon(bytearray(raw),i*100).has_species()]
 assert actual==[const('SPECIES_'+v) for v in TEAMS[name]],(name,actual)
 turns=0
 while menu(e):
  assert turns<90,'battle did not finish';fight_one_turn(e,loss=loss);turns+=1
 outcome=e.u8(e.sym('gBattleOutcome'));assert outcome==(2 if loss else 1)
 settle(e);after=snapshot(e);flags=dict(before['flags']);trainers=dict(before['trainers']);trainers[name]=not loss;delta={}
 if not loss:
  flags.update({B5:True,CTM:True} if name=='CHUCK' else {B6:True,JTM:True});delta['ITEM_TM01' if name=='CHUCK' else 'ITEM_TM23']=1
 assert after['flags']==flags,(tag,'flags',after['flags'],flags)
 assert after['trainers']==trainers,(tag,'trainer result')
 assert after['pc']==before['pc']==bytes(prepared.blocks['storage']) and after['party_count']==before['party_count']
 for item in ITEMS:assert after['items'][item]==before['items'][item]+delta.get(item,0),(tag,item)
 for key in ['pc_hm','pc_hm3','pc_hm02','pc_hm04']:assert after[key]==before[key],(tag,key)
 for old,new in zip(before['dex'],after['dex']):assert old[0]==new[0] and all(not a or b for a,b in zip(old,new)),(tag,'caught/seen')
 e.shot(str(out/(tag+'.png')),scale=3);saved=flash_reload(e,tag)
 return {'case':tag,'turns':turns,'native_outcome':outcome,'enemies':actual,'save':saved,'pc_preserved':True,'forced_memory_writes':0,'forced_battle_outcomes':0}
def warp_native_result(source,target,where):
 s=SaveFile(str(source));party=bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
 pc=bytes(s.blocks['storage']);dex=[s.dex_state(i) for i in range(1,387)]
 flag_bytes=bytes(s.sb1[off('sb1.flags'):off('sb1.vars')])
 trainers={n:s.trainer_beaten('TRAINER_JOHTO_'+n) for n in ACTORS}
 s.warp(*where);s.save(str(target));check=SaveFile(str(target))
 assert party==bytes(check.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
 assert pc==bytes(check.blocks['storage']) and dex==[check.dex_state(i) for i in range(1,387)]
 assert flag_bytes==bytes(check.sb1[off('sb1.flags'):off('sb1.vars')]),'position-only QA warp changed story flags'
 assert trainers=={n:check.trainer_beaten('TRAINER_JOHTO_'+n) for n in ACTORS}
 return check
def dialog_stage(source,target,where,c):
 assert not target.exists();prepared=warp_native_result(source,target,where)
 with ReadOnlyEmu(str(rom),str(target),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
  interaction(e,c);after=snapshot(e);flags=dict(before['flags']);flags.update(c.get('expect_flags',{}))
  assert after['flags']==flags,(c['name'],'story flags')
  for item in ITEMS:assert after['items'][item]==before['items'][item]+c.get('delta',{}).get(item,0),(c['name'],item)
  for field in ['pc','party','party_count','dex','pc_hm','pc_hm3','pc_hm02','pc_hm04','trainers']:
   assert after[field]==before[field],(c['name'],'unexpected native state change',field)
  if c.get('absent_object'):object_absent(e,c['absent_object'])
  e.shot(str(out/(c['name']+'.png')),scale=3);saved=flash_reload(e,c['name'])
  if c.get('absent_object'):object_absent(e,c['absent_object'])
  return {'case':c['name'],'native_dialogue':c['marker'],'save':saved,'forced_story_flags':0,'forced_memory_writes':0}
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='olivine-same-save-chain-') as td:
  td=Path(td);first=td/'badge4-complete-initial-fixture.sav'
  prepared=fixture(first,{'where':('OlivineLighthouse_6F',12,10),'party_surf':True})
  assert prepared.flag(D) and all(not prepared.flag(f) for f in [REQ,MED,CURED,B5,B6,CTM,JTM,FLY,STR])
  steps=[
   ('dialog',('OlivineLighthouse_6F',12,10),{'name':'chain_jasmine_requests_medicine','marker':'OlivineLighthouse_6F_Text_Request','expect_flags':{REQ:True}}),
   ('dialog',('CianwoodCity_Pharmacy',5,4),{'name':'chain_pharmacy_reserved_dose','marker':'CianwoodCity_Pharmacy_Text_Give','expect_flags':{MED:True}}),
   ('battle',POSITIONS['CHUCK'],'CHUCK'),
   ('dialog',('CianwoodCity',15,11),{'name':'chain_chuck_wife_fly','marker':'CianwoodCity_Text_FlyGiftHM','expect_flags':{FLY:True,'FLAG_GOT_HM02':True},'delta':{'ITEM_HM02':1}}),
   ('dialog',('OlivineLighthouse_6F',12,10),{'name':'chain_medicine_cures_amphy','marker':'OlivineLighthouse_6F_Text_Return','expect_flags':{CURED:True,HIDE:False},'absent_object':1}),
   ('battle',POSITIONS['JASMINE'],'JASMINE'),
   ('dialog',('OlivineCity_Cafe',5,4),{'name':'chain_sailor_strength','marker':'OlivineCity_Cafe_Text_StrengthGiftHM','expect_flags':{STR:True,'FLAG_GOT_HM04':True},'delta':{'ITEM_HM04':1}})]
  previous=first
  for i,(kind,where,c) in enumerate(steps):
   target=td/('step-'+str(i+1)+'.sav')
   if kind=='dialog':row=dialog_stage(previous,target,where,c)
   else:
    prepared=warp_native_result(previous,target,where)
    assert not prepared.trainer_beaten('TRAINER_JOHTO_'+c)
    if c=='JASMINE':assert prepared.flag(CURED) and prepared.flag(B5) and not prepared.flag(HIDE)
    with ReadOnlyEmu(str(rom),str(target),sym='') as e:row=battle(e,c,False,prepared,'chain_actual_'+c.lower()+'_win')
   previous=Path(row['save']['qa_save']);results.append(row);print(json.dumps(row),flush=True)
  final=SaveFile(str(previous));assert all(final.flag(f) for f in [REQ,MED,CURED,B5,B6,CTM,JTM,FLY,STR])
  assert not final.flag(HIDE)
  for name in ['CHUCK','JASMINE']:assert final.trainer_beaten('TRAINER_JOHTO_'+name)
  for item in ['ITEM_HM02','ITEM_HM04','ITEM_TM01','ITEM_TM23']:assert final.item_count(item)==1,(item,final.item_count(item))
finally:
 for path,sha in originals.items():assert digest(path.read_bytes())==sha,('original changed',str(path))
assert len(results)==7
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'initial_fixture':'Completed Morty badge4, unstarted medicine/gyms5-6','stages':results,'all_pass':True,'same_native_save_chain':True,'qa_position_only_warps':7,'forced_story_flags_after_initial_fixture':0,'forced_trainer_flags_after_initial_fixture':0,'forced_memory_writes':0,'forced_battle_outcomes':0,'original_files_unchanged':True},indent=2))
