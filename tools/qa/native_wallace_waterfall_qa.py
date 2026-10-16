#!/usr/bin/env python3
"""Native Wallace HM07 / rare-TM reward and successful-only receipt QA."""
from pathlib import Path
q=Path('tools/qa/native_hoenn_sea_sky_qa.py').read_text()
head=q.split('e=None\ntry:',1)[0]
old="choices=\"['seafloor','seafloor-early','seafloor-no-badge','sky','sky-early','city-storm','city-calm','gym-locked','gym-legacy','gym']\""
assert head.count(old)==1
head=head.replace(old,"choices=\"['first','bag','pc','history','done','early','storm','legacy','full-retry']\"",1)
head=head.replace('wo=weather_offsets()','wo={}')
exec(compile(head,'tools/qa/native_hoenn_sea_sky_qa.py','exec'))
assert not a.loss
F='FLAG_HOENN_GOT_WALLACE_WATERFALL_REWARD'
KH='FLAG_HIDE_FOUR_ISLAND_ICEFALL_CAVE_1F_HM07'
flags=[SEA,RAY,B7,B8,F,KH]
report.update(mode='native-wallace-waterfall-'+a.case,
 fixture='temporary story/item fixture; original source SAV and full Pokemon storage unchanged',
 stages=[],native_story_not_entire_regions=True)
source_storage=bytes(source.blocks['storage'][:off('storage')])
original_dex=digest_dex(source);po=off('sb1.playerParty')
expected_party=None;expected_count=source.party_count()
def pc_item_count(b,item):
 iid=const(item);o=off('sb1.pcItems');n=const('PC_ITEMS_COUNT')
 return sum(struct.unpack_from('<H',b.sb1,o+4*i+2)[0]
            for i in range(n) if struct.unpack_from('<H',b.sb1,o+4*i)[0]==iid)
def set_pc_item(b,item,qty):
 iid=const(item);o=off('sb1.pcItems');n=const('PC_ITEMS_COUNT')
 for i in range(n):
  if struct.unpack_from('<H',b.sb1,o+4*i)[0]==iid:
   struct.pack_into('<HH',b.sb1,o+4*i,0,0)
 if qty:
  for i in range(n):
   if struct.unpack_from('<H',b.sb1,o+4*i)[0]==0:
    struct.pack_into('<HH',b.sb1,o+4*i,iid,qty);return
  raise AssertionError('no temporary PC item slot')
def invariants():
 assert e.read(e.ptr('gPokemonStoragePtr'),off('storage'))==source_storage,'full Pokemon storage changed'
 assert pc(e)==source_pc
 assert e.u8(syms['gPlayerPartyCount'])==expected_count
 now=e.read(syms['gPlayerParty'],600);party_valid(now,expected_count)
 assert now==expected_party,'party changed beyond intentional native held-TM test'
 assert digest_dex(blocks(e))==original_dex
def await_state(pred,limit=2000,key=None):
 for i in range(limit):
  if pred():return
  safe(e);assert not e.in_battle(),'reward entered a battle'
  if key and i%8==0:e.press(key,hold=1,after=1)
  else:e.run(1)
 raise AssertionError(('UI timeout',e.location(),hex(e.callback2())))
def one_step(key):
 initial=e.location();e.hold(key)
 try:
  for _ in range(80):
   safe(e);assert not e.in_battle(),'unexpected approach battle'
   e.run(1)
   if e.location()!=initial:break
  else:raise AssertionError(('one approach step blocked',key,initial))
 finally:e.hold()
 e.run(40);settle(e)
 dx,dy={'UP':(0,-1),'DOWN':(0,1),'LEFT':(-1,0),'RIGHT':(1,0)}[key]
 assert e.location()==(initial[0],initial[1],initial[2]+dx,initial[3]+dy),('approach step size',key,initial,e.location())
 report.setdefault('wallace_approach',[]).append({'key':key,'from':initial,'to':e.location()})
def start_option(option):
 assert e.field_idle()
 e.press('START',hold=3,after=60)
 n=e.u8(syms['sNumStartMenuItems']);order=list(e.read(syms['sStartMenuOrder'],n))
 assert option in order,(option,order)
 target=order.index(option)
 for _ in range(n+1):
  if e.u8(syms['sStartMenuCursorPos'])==target:break
  e.press('DOWN',hold=3,after=12)
 assert e.u8(syms['sStartMenuCursorPos'])==target
 e.press('A',hold=3,after=20)
def native_give_tm26():
 global expected_party
 assert blocks(e).item_count('ITEM_TM26')==999
 start_option(2)
 await_state(lambda:active_task(e,'Task_BagMenu_HandleInput'))
 for _ in range(4):
  if e.u16(syms['gBagMenuState']+6)==1:break
  e.press('RIGHT',hold=3,after=45)
 assert e.u16(syms['gBagMenuState']+6)==1
 for _ in range(70):e.press('UP',hold=2,after=3)
 e.press('A',hold=3,after=20)
 await_state(lambda:bool(e.ptr('sTMCaseDynamicResources')) and active_task(e,'Task_HandleListInput'),1600,'A')
 for _ in range(70):e.press('UP',hold=2,after=3)
 # Native TM CASE sorts the one HM07 first, then TM26.
 e.press('DOWN',hold=3,after=12)
 e.press('A',hold=3,after=20)
 await_state(lambda:active_task(e,'Task_ContextMenu_HandleInput'))
 assert e.u16(syms['gSpecialVar_ItemId'])==const('ITEM_TM26')
 # FRLG field TM context order is USE, GIVE, EXIT.
 e.press('DOWN',hold=3,after=12);e.press('A',hold=3,after=20)
 await_state(lambda:active_task(e,'Task_HandleChooseMonInput'))
 e.press('A',hold=3,after=20)
 await_state(lambda:blocks(e).item_count('ITEM_TM26')==998,2400,'A')
 await_state(e.field_idle,2400,'B')
 expected_party=bytearray(expected_party)
 Mon(expected_party,0).set_held(const('ITEM_TM26'));expected_party=bytes(expected_party)
 invariants()
 report['native_make_room']={'method':'Give TM26 to first party Pokemon through native TM CASE',
  'quantity_before':999,'quantity_after':998,'held_item':const('ITEM_TM26')}
def reward():
 talk(e,'UP');quiet_finish(e)
 b=blocks(e)
 report['stages'].append({'frame':e.frame(),'receipt':b.flag(F),'hm07':b.item_count('ITEM_HM07'),
  'tm26':b.item_count('ITEM_TM26'),'pc_hm07':pc_item_count(b,'ITEM_HM07')})
 photo(e,'native-wallace-'+str(len(report['stages'])))
 return b
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-wallace-waterfall-qa-') as td:
  s=SaveFile(str(sav));s.fast_battles();s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False)
  for f in flags:s.set_flag(f,False)
  s.set_flag(B7,True);s.set_flag(SEA,a.case!='early')
  s.set_flag(RAY,a.case not in ('early','storm'))
  if a.case=='legacy':
   s.set_flag(SEA,False);s.set_flag(RAY,False);s.set_flag(B8,True)
  if a.case=='history':s.set_flag(KH,True)
  if a.case=='done':s.set_flag(F,True)
  set_pc_item(s,'ITEM_HM07',1 if a.case=='pc' else 0)
  s.set_item('ITEM_HM07',1 if a.case in ('bag','full-retry') else 0)
  s.set_item('ITEM_TM26',999 if a.case=='full-retry' else 0)
  if a.case=='full-retry':
   # Only the tested TM and HM remain in the temporary TM pocket, making
   # the native list selection exact; no user save is edited.
   key=s._key()&65535
   for o in s._slots('ITEM_TM26'):struct.pack_into('<HH',s.sb1,o,0,key)
   s.set_item('ITEM_TM26',999);s.set_item('ITEM_HM07',1)
   s.put_item_first('ITEM_TM_CASE',1)
   s.party_mon(0).set_held(0)
  # Gym south exit runs the real City OnTransition before talking to Wallace.
  s.warp('SootopolisCity_Gym_1F',8,24)
  expected_party=bytes(s.sb1[po:po+600]);party_valid(expected_party,expected_count)
  assert bytes(s.blocks['storage'][:off('storage')])==source_storage
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  e.walk('DOWN');settle(e);assert loc_is(e,'SootopolisCity')
  # Release keys at the first changed coordinate; a fixed 18-frame walk
  # can travel two tiles at the current native walking speed.
  assert e.location()[2:]==(31,33),('Gym south exit',e.location())
  one_step('DOWN')
  for _ in range(3):one_step('LEFT')
  assert e.location()[2:]==(28,34),('Wallace south approach',e.location())
  invariants()
  kanto=[blocks(e).flag('FLAG_BADGE%02d_GET'%i) for i in range(1,9)]
  initial={f:blocks(e).flag(f) for f in flags}
  first=reward()
  if a.case in ('early','storm'):
   assert not first.flag(F) and first.item_count('ITEM_HM07')==0 and first.item_count('ITEM_TM26')==0
  elif a.case=='done':
   assert first.flag(F) and first.item_count('ITEM_HM07')==0 and first.item_count('ITEM_TM26')==0
  elif a.case=='full-retry':
   assert not first.flag(F) and first.item_count('ITEM_HM07')==1 and first.item_count('ITEM_TM26')==999
   native_save_reopen(e,source_pc);invariants()
   assert not blocks(e).flag(F),'failed receipt survived as success'
   native_give_tm26();retry=reward()
   assert retry.flag(F) and retry.item_count('ITEM_TM26')==999 and retry.item_count('ITEM_HM07')==1
  elif a.case in ('bag','pc','history'):
   assert first.flag(F) and first.item_count('ITEM_TM26')==1
   assert first.item_count('ITEM_HM07')==(1 if a.case=='bag' else 0)
   assert pc_item_count(first,'ITEM_HM07')==(1 if a.case=='pc' else 0)
  else:
   assert first.flag(F) and first.item_count('ITEM_HM07')==1 and first.item_count('ITEM_TM26')==0
  invariants()
  saved_items=(blocks(e).item_count('ITEM_HM07'),blocks(e).item_count('ITEM_TM26'),pc_item_count(blocks(e),'ITEM_HM07'))
  repeat=reward()
  assert (repeat.item_count('ITEM_HM07'),repeat.item_count('ITEM_TM26'),pc_item_count(repeat,'ITEM_HM07'))==saved_items,'repeat reward duplicated'
  assert [repeat.flag('FLAG_BADGE%02d_GET'%i) for i in range(1,9)]==kanto
  assert all(repeat.flag(f)==initial[f] for f in flags if f!=F),'unrelated story flag changed'
  native_save_reopen(e,source_pc);invariants()
  cold=blocks(e)
  assert (cold.item_count('ITEM_HM07'),cold.item_count('ITEM_TM26'),pc_item_count(cold,'ITEM_HM07'))==saved_items
  report['pass']=True;report['full_original_pokemon_storage_unchanged']=True
except Exception as ex:
 report['error']=repr(ex);report['traceback']=traceback.format_exc()
 if e and e.h:report['failure_location']=e.location();photo(e,'failure')
finally:
 if e:e.close()
 after={p:sha(Path(p).read_bytes()) for p in before}
 report['original_saves_unchanged']=before==after
 if before!=after:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='traceback'}),flush=True)
sys.exit(0 if report['pass'] else 1)
