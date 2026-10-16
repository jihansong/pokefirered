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
gd.FIELDS['pokemon.level']=('Pokemon','level');gd._OFFSETS=None
_trainer_bit=re.search(r'^#define\s+BATTLE_TYPE_TRAINER\s+\(1\s*<<\s*(\d+)\)',Path('include/constants/battle.h').read_text(),re.M)
assert _trainer_bit,'native trainer-battle flag macro changed'
TRAINER_BATTLE_BIT=1<<int(_trainer_bit.group(1))
# Only the native bag-input controller is reused; it does not write game memory.
node=next(n for n in ast.parse(Path('tools/qa/eventcheck.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='throw_ball')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<native-ball-input>','exec'),globals())
wait_action_menu=lambda e,rom:menu(e)
live_blocks=blocks
item_name=gd.item_name

STATIC={'gyarados':dict(where=('LakeOfRage',20,19),species='GYARADOS',level=30,flag=RED,local_id=1,object_xy=(20,17),shiny=True),
 'electrode1':dict(where=('JohtoRocketHQ_B3F',10,14),species='ELECTRODE',level=23,flag=E1,local_id=1,object_xy=(10,12),shiny=False),
 'electrode2':dict(where=('JohtoRocketHQ_B3F',16,14),species='ELECTRODE',level=23,flag=E2,local_id=2,object_xy=(16,12),shiny=False),
 'electrode3':dict(where=('JohtoRocketHQ_B3F',22,14),species='ELECTRODE',level=23,flag=E3,local_id=3,object_xy=(22,12),shiny=False)}
def wild_fixture(path,key,loss=False):
 v=STATIC[key];c={'where':v['where'],'loss':loss,'party_surf':key=='gyarados'}
 if key!='gyarados':c.update(flags={RED:True,JOIN:True,SCALE:True,MOVED:True},trainers={'PETREL':True,'ARIANA':True})
 s=fixture(path,c);s.set_item('ITEM_MASTER_BALL',1);s.save(str(path));return s
def mon_shiny(raw):
 pid,ot=struct.unpack_from('<II',raw)
 return ((pid&0xffff)^(pid>>16)^(ot&0xffff)^(ot>>16))<8
def assert_mon_legal(raw,label):
 m=Mon(bytearray(raw),0);subs=m.subs()
 decrypted=b''.join(bytes(v) for v in subs.values())
 assert len(decrypted)==48
 checksum=sum(v for (v,) in struct.iter_unpack('<H',decrypted))&0xffff
 assert checksum==struct.unpack_from('<H',raw,28)[0],(label,'encrypted Pokemon checksum mismatch')
 assert m.has_species() and raw[19]&1==0 and not m.is_egg(),(label,'invalid new Pokemon/Bad Egg flag')
 return m
def start_wild(e,key):
 v=STATIC[key];native_step(e,'UP');e.press('A',hold=3,after=12)
 mash_until(e,e.in_battle,300);assert menu(e)
 assert not(e.u32(syms['gBattleTypeFlags'])&TRAINER_BATTLE_BIT)
 raw=e.read(syms['gEnemyParty'],600);mon=assert_mon_legal(raw[:100],key+' scripted enemy')
 actual=[Mon(bytearray(raw),i*100).species() for i in range(6) if Mon(bytearray(raw),i*100).has_species()]
 assert actual==[const('SPECIES_'+v['species'])],(key,actual)
 assert raw[off('pokemon.level')]==v['level'],(key,'level')
 if v['shiny']:assert mon_shiny(raw),(key,'scripted opponent is not legitimately shiny')
 return raw[:100]
def attempt(e,key,mode,prepared,tag):
 v=STATIC[key];e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
 beforeball=blocks(e).item_count('ITEM_MASTER_BALL')
 if key=='gyarados':assert e.u8(syms['gPlayerAvatar'])&8,'lake fixture did not cold-load native Surf'
 enemy=start_wild(e,key);turns=0
 if mode=='catch':assert throw_ball(e,str(rom),'ITEM_MASTER_BALL',None) is None
 elif mode=='run':
  for button in ('DOWN','RIGHT','A'):e.press(button,hold=3,after=12)
 else:
  while menu(e):
   assert turns<90,'static battle did not finish'
   fight_one_turn(e,loss=mode=='loss');turns+=1
 settle(e);outcome=e.u8(e.sym('gBattleOutcome'));after=snapshot(e)
 assert outcome=={'win':1,'loss':2,'run':4,'catch':7}[mode],(tag,outcome)
 flags=dict(before['flags']);flags[v['flag']]=mode in ('win','catch')
 assert after['flags']==flags,(tag,'story/outcome flags',after['flags'],flags)
 assert not blocks(e).flag('FLAG_SYS_SPECIAL_WILD_BATTLE')
 assert after['trainers']==before['trainers']
 assert after['pc']==before['pc']==bytes(prepared.blocks['storage'])
 for field in ['items','pc_hm','pc_hm3','pc_hm02','pc_hm04']:assert after[field]==before[field],(tag,field)
 assert blocks(e).item_count('ITEM_MASTER_BALL')==beforeball-(1 if mode=='catch' else 0)
 species=const('SPECIES_'+v['species'])
 dex=struct.unpack('<H',r.at(syms['sSpeciesToNationalPokedexNum']+(species-1)*2,2))[0]
 for i,(old,new) in enumerate(zip(before['dex'],after['dex']),1):
  wanted=(True,True,True,True) if mode=='catch' and i==dex else ((old[0],True,True,True) if i==dex else old)
  assert new==wanted,(tag,'Dex delta',i,old,new,wanted)
 if mode=='catch':
  assert before['party_count']<6 and after['party_count']==before['party_count']+1
  assert after['party'][:before['party_count']*100]==before['party'][:before['party_count']*100]
  caught=after['party'][before['party_count']*100:(before['party_count']+1)*100]
  cm=assert_mon_legal(caught,tag+' native capture');assert cm.species()==species
  assert caught[:8]==enemy[:8],(tag,'PID/OT changed during capture')
  assert caught[19]&1==0,(tag,'new Bad Egg flag')
  if v['shiny']:assert mon_shiny(caught),(tag,'captured Gyarados is not shiny')
 else:assert after['party_count']==before['party_count']
 if mode in ('win','catch'):object_absent(e,v['local_id'])
 elif mode=='run':follower_map_object(e,v['local_id'],*v['object_xy'])
 e.shot(str(out/(tag+'.png')),scale=3);saved=flash_reload(e,tag)
 if mode in ('win','catch'):object_absent(e,v['local_id'])
 elif mode=='run':follower_map_object(e,v['local_id'],*v['object_xy'])
 return {'case':tag,'turns':turns,'outcome':outcome,'species_internal':species,'national_dex':dex,'scripted_shiny_verified':v['shiny'],'save':saved,'pc_preserved':True,'legal_capture_checksum_verified':mode=='catch','forced_memory_writes':0,'forced_battle_outcomes':0}
def retry_from_saved(source,target,key):
 s=SaveFile(str(source));pc=bytes(s.blocks['storage'])
 flags=bytes(s.sb1[off('sb1.flags'):off('sb1.vars')])
 party=bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
 dex=[s.dex_state(i) for i in range(1,387)]
 s.warp(*STATIC[key]['where']);s.save(str(target));check=SaveFile(str(target))
 assert pc==bytes(check.blocks['storage']) and flags==bytes(check.sb1[off('sb1.flags'):off('sb1.vars')])
 assert party==bytes(check.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
 assert dex==[check.dex_state(i) for i in range(1,387)]
 assert not check.flag(STATIC[key]['flag'])
 return check
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='mahogany-native-static-') as td:
  td=Path(td);escaped={}
  modes=[(key,mode) for key in ['gyarados','electrode1'] for mode in ['win','loss','run','catch']]+[('electrode2','catch'),('electrode3','win')]
  for key,mode in modes:
   tag=key+'_'+mode;path=td/(tag+'.sav')
   prepared=retry_from_saved(escaped[key],path,key) if mode=='catch' and key in escaped else wild_fixture(path,key,mode=='loss')
   with ReadOnlyEmu(str(rom),str(path),sym='') as e:row=attempt(e,key,mode,prepared,tag)
   if mode=='run':escaped[key]=Path(row['save']['qa_save'])
   results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==10
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,'native_flee_save_cold_retry':True,'original_files_unchanged':True,'forced_memory_writes':0,'forced_battle_outcomes':0},indent=2))
