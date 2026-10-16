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
def wild_fixture(path,loss=False):
 s=fixture(path,{'where':('JohtoRoute36',25,9),'loss':loss,'flags':{W:True}})
 s.set_item('ITEM_MASTER_BALL',1);s.save(str(path));return s
def object_absent(e,local_id):
 group,num,_,_=e.location();raw=e.read(syms['gObjectEvents'],36*const('OBJECT_EVENTS_COUNT'))
 for i in range(0,len(raw),36):
  row=raw[i:i+36]
  assert not (row[0]&1 and row[8]==local_id and row[9]==num and row[10]==group)
def start_wild(e):
 e.walk('UP',1);e.run(30);e.press('A',hold=3,after=12)
 mash_until(e,e.in_battle,300);assert menu(e)
 assert not (e.u32(e.sym('gBattleTypeFlags'))&TRAINER_BATTLE_BIT)
 raw=e.read(syms['gEnemyParty'],600)
 actual=[Mon(bytearray(raw),i*100).species() for i in range(6) if Mon(bytearray(raw),i*100).has_species()]
 assert actual==[const('SPECIES_SUDOWOODO')],actual
 assert raw[off('pokemon.level')]==20
def attempt(e,mode,prepared,tag):
 e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e);beforeball=blocks(e).item_count('ITEM_MASTER_BALL')
 start_wild(e);turns=0
 if mode=='catch':
  assert throw_ball(e,str(rom),'ITEM_MASTER_BALL',None) is None
 elif mode=='run':
  for key in ('DOWN','RIGHT','A'):e.press(key,hold=3,after=12)
 else:
  while menu(e):
   assert turns<90
   fight_one_turn(e,loss=mode=='loss');turns+=1
 settle(e);outcome=e.u8(e.sym('gBattleOutcome'));after=snapshot(e)
 assert outcome=={'win':1,'loss':2,'run':4,'catch':7}[mode],(tag,outcome)
 flags=dict(before['flags']);flags[O]=mode in ('win','catch')
 assert after['flags']==flags,(tag,after['flags'],flags)
 assert after['trainers']==before['trainers']
 assert after['pc']==before['pc']==bytes(prepared.blocks['storage'])
 assert after['items']==before['items'] and after['pc_hm']==before['pc_hm'] and after['pc_hm3']==before['pc_hm3']
 assert blocks(e).item_count('ITEM_MASTER_BALL')==beforeball-(1 if mode=='catch' else 0)
 assert not blocks(e).flag('FLAG_SYS_SPECIAL_WILD_BATTLE')
 dex=struct.unpack('<H',r.at(syms['sSpeciesToNationalPokedexNum']+(const('SPECIES_SUDOWOODO')-1)*2,2))[0]
 for i,(old,new) in enumerate(zip(before['dex'],after['dex']),1):
  assert new==((True,True,True,True) if mode=='catch' and i==dex else ((old[0],True,True,True) if i==dex else old)),(tag,'dex',i,old,new)
 if mode=='catch':
  assert after['party_count']==before['party_count']+1
  for i in range(after['party_count']):
   m=Mon(bytearray(after['party']),i*100)
   if i==after['party_count']-1:assert m.species()==const('SPECIES_SUDOWOODO')
 else:assert after['party_count']==before['party_count']
 if mode in ('win','catch'):object_absent(e,1)
 elif mode=='run':follower_map_object(e,1,25,8)
 e.shot(str(out/(tag+'.png')),scale=3);saved=flash_reload(e,tag)
 if mode in ('win','catch'):object_absent(e,1)
 elif mode=='run':follower_map_object(e,1,25,8)
 return {'case':tag,'turns':turns,'outcome':outcome,'save':saved,'pc_preserved':True,'native_capture':mode=='catch',
  'forced_memory_writes':0,'forced_battle_outcomes':0}
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='ecruteak-native-wild-') as td:
  escaped=None
  for mode in ['win','loss','run','catch']:
   tag='sudowoodo_'+mode;path=Path(td)/(tag+'.sav')
   if mode=='catch':
    # Retry from the actual run-away save; only the QA position changes.
    s=SaveFile(str(escaped));beforepc=bytes(s.blocks['storage']);beforeflags={f:s.flag(f) for f in STORY}
    s.warp('JohtoRoute36',25,9);s.save(str(path));prepared=SaveFile(str(path))
    assert bytes(prepared.blocks['storage'])==beforepc and {f:prepared.flag(f) for f in STORY}==beforeflags
    assert not prepared.flag(O)
   else:prepared=wild_fixture(path,mode=='loss')
   with ReadOnlyEmu(str(rom),str(path),sym='') as e:row=attempt(e,mode,prepared,tag)
   if mode=='run':escaped=Path(row['save']['qa_save'])
   results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sha in originals.items():assert digest(path.read_bytes())==sha,('original changed',str(path))
assert len(results)==4
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,
 'original_files_unchanged':True,'forced_memory_writes':0,'forced_battle_outcomes':0},indent=2))
