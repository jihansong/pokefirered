#!/usr/bin/env python3
"""Native Dive menu/A-key/teaching/round-trip QA. Temporary fixture only."""
from pathlib import Path
head=Path('tools/qa/hoenn_weather_space_native_qa.py').read_text().split('e=None\ntry:',1)[0]
head=head.replace("choices=['weather-party','weather-pc','space']","choices=['route','teach','no-badge','hoenn-only','legacy','invalid','land','no-move']")
exec(compile(head,'tools/qa/hoenn_weather_space_native_qa.py','exec'))
assert not a.loss
report.update(mode='native-dive-'+a.case,fixture='temporary level-50 LAPRAS; original PC and source SAV unchanged',stages=[])
R='Route128';U='Underwater_Route128';C='Underwater_SeafloorCavern';E='SeafloorCavern_Entrance'
DIVE=const('MOVE_DIVE'); SURF=const('PLAYER_AVATAR_FLAG_SURFING'); UW=const('PLAYER_AVATAR_FLAG_UNDERWATER')
def await_state(pred,limit=2000,key=None):
 for i in range(limit):
  if pred():return
  safe(e)
  if key and i%8==0:e.press(key,hold=1,after=1)
  else:e.run(1)
 raise AssertionError(('state timeout',e.location(),hex(e.callback2())))
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
def close_ui():
 await_state(e.field_idle,2400,'B')
def native_moves():
 m=Mon(bytearray(e.read(syms['gPlayerParty'],100)),0)
 return list(struct.unpack_from('<4H',m.subs()['A'],0))
def menu_dive(expect_transition=True):
 start_option(1)
 await_state(lambda:active_task(e,'Task_HandleChooseMonInput'))
 e.press('A',hold=3,after=20)
 await_state(lambda:active_task(e,'Task_HandleSelectionMenuInput'))
 p=e.ptr('sPartyMenuInternal')
 actions=list(e.read(p+15,e.u8(p+23)))
 # Native PartyMenuInternal head: two pointers, u32 bitfield, 3 windows, 8 actions.
 assert 30 in actions,('DIVE action missing',actions,native_moves())
 assert struct.unpack('<I',r.at(syms['sCursorOptions']+30*8,4))[0]==syms['gMoveNames']+DIVE*13
 idx=actions.index(30)
 for _ in range(idx):e.press('DOWN',hold=3,after=12)
 photo(e,'party-dive-menu-'+str(len(report['stages'])))
 e.press('A',hold=3,after=20)
 if not expect_transition:
  e.run(60);photo(e,'party-dive-rejected')
  close_ui()
def a_dive():
 e.press('A',hold=3,after=20)
 await_state(lambda:active_task(e,'Task_YesNoMenu_HandleInput'),2000,'A')
 e.run(10);e.press('UP',hold=2,after=5);e.press('A',hold=2,after=5)
def reach(name,x,y,flag):
 await_state(lambda:loc_is(e,name) and e.field_idle(),2400,'A')
 assert e.location()[2:]==(x,y),(name,e.location(),x,y)
 bits=e.u8(syms['gPlayerAvatar'])
 assert bits&flag and not(bits&(UW if flag==SURF else SURF)),('avatar flags',bits,flag)
 assert not e.u8(syms['gPlayerAvatar']+6),'movement stayed locked'
 photo(e,'native-'+name+'-'+str(len(report['stages'])))
 report['stages'].append({'map':name,'xy':[x,y],'avatar_flags':bits,'frame':e.frame()})
def teach():
 assert DIVE not in native_moves()
 start_option(2)
 await_state(lambda:active_task(e,'Task_BagMenu_HandleInput'))
 for _ in range(4):
  if e.u16(syms['gBagMenuState']+6)==1:break
  e.press('RIGHT',hold=3,after=45)
 assert e.u16(syms['gBagMenuState']+6)==1
 # TM CASE is first in the fixture key-item pocket.
 for _ in range(70):e.press('UP',hold=2,after=3)
 e.press('A',hold=3,after=20)
 await_state(lambda:bool(e.ptr('sTMCaseDynamicResources')) and active_task(e,'Task_HandleListInput'),1600,'A')
 assert blocks(e).item_count('ITEM_HM08')==1
 photo(e,'hm08-native-tm-case')
 e.press('A',hold=3,after=20)
 await_state(lambda:active_task(e,'Task_ContextMenu_HandleInput'))
 assert e.u16(syms['gSpecialVar_ItemId'])==const('ITEM_HM08')
 e.press('A',hold=3,after=20)
 await_state(lambda:active_task(e,'Task_HandleChooseMonInput'))
 e.press('A',hold=3,after=20)
 await_state(lambda:DIVE in native_moves(),2400,'A')
 photo(e,'hm08-native-learned')
 close_ui()
 assert blocks(e).item_count('ITEM_HM08')==1,'HM was consumed'
 report['native_hm08_teaching']={'move_after':native_moves(),'hm_quantity_after':1}

e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-dive-qa-') as td:
  s=SaveFile(str(sav));s.fast_battles();s.keep_party(1)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False)
  s.set_flag('FLAG_HOENN_BADGE07_GET',a.case not in ('no-badge','legacy'))
  for i in range(1,9):s.set_flag('FLAG_BADGE%02d_GET'%i,a.case=='no-badge')
  s.set_item('ITEM_HM08',1)
  if a.case=='legacy':s.warp(C,6,6)
  elif a.case=='land':s.warp(S,15,7)
  elif a.case=='invalid':s.warp(R,39,25)
  else:s.warp(R,38,27)
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  m=s.party_mon(0);m.set_otid(owner);m.set_starter_bit(False);m.set_snagged(False)
  m.set_species(const('SPECIES_LAPRAS'),rom=r)
  sub=m.subs();sub['E'][:6]=bytes(6);sub['A'][:]=bytes(12)
  move_names=['MOVE_SURF','MOVE_TACKLE'] if a.case in ('teach','no-move') else ['MOVE_SURF','MOVE_DIVE']
  for i,name in enumerate(move_names):
   mid=const(name);struct.pack_into('<H',sub['A'],i*2,mid)
   sub['A'][8+i]=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  struct.pack_into('<I',sub['M'],4,struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30))
  m.put_subs(sub);m.blk[m.o+19]=(m.blk[m.o+19]&~5)|2;m.set_held(0);m.make_strong(50,rom=r)
  if a.case=='teach':
   key=s._key()&65535
   for o in s._slots('ITEM_HM08'):struct.pack_into('<HH',s.sb1,o,0,key)
   s.set_item('ITEM_HM08',1);s.put_item_first('ITEM_TM_CASE',1)
  assert bytes(s.blocks['storage'][boxoff:boxoff+cs])==source_pc
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  initial=e.location()
  expected_badges=[blocks(e).flag('FLAG_BADGE%02d_GET'%i) for i in range(1,9)]
  expected_hoenn=blocks(e).flag('FLAG_HOENN_BADGE07_GET')
  if a.case=='teach':teach()
  if a.case in ('route','teach','hoenn-only'):
   assert e.u8(syms['gPlayerAvatar'])&SURF
   if a.case=='route':a_dive()
   else:menu_dive()
   reach(U,38,27,UW)
   native_save_reopen(e,source_pc);reach(U,38,27,UW)
   # Enter the native underwater cave warp, then emerge through its fixed hook.
   e.walk('UP');await_state(lambda:loc_is(e,C) and e.field_idle(),1800)
   assert e.location()[2:]==(6,7),e.location()
   e.walk('UP');assert e.location()[2:]==(6,6),e.location()
   a_dive();reach(E,10,16,SURF)
   # Native menu returns into the cave instead of onto its exit warp.
   menu_dive();reach(C,6,6,UW)
   e.walk('DOWN');await_state(lambda:loc_is(e,U) and e.field_idle(),1800)
   assert e.location()[2:]==(38,26),e.location()
   e.walk('DOWN');assert e.location()[2:]==(38,27)
   menu_dive();reach(R,38,27,SURF)
   report['native_roundtrip']=True
  elif a.case=='legacy':
   assert not expected_hoenn
   a_dive();reach(E,10,16,SURF)
   report['legacy_emerge_without_badge']=True
  elif a.case in ('no-badge','invalid','land'):
   menu_dive(False)
   assert e.location()==initial
   if a.case=='no-badge':
    e.press('A',hold=3,after=20);quiet_finish(e)
    assert e.location()==initial
   report['native_rejection']=True
  elif a.case=='no-move':
   e.press('A',hold=3,after=20);quiet_finish(e)
   assert e.location()==initial and DIVE not in native_moves()
   report['no_dive_mon_rejected']=True
  assert pc(e)==source_pc
  assert blocks(e).flag('FLAG_HOENN_BADGE07_GET')==expected_hoenn
  assert [blocks(e).flag('FLAG_BADGE%02d_GET'%i) for i in range(1,9)]==expected_badges
  native_save_reopen(e,source_pc)
  report['pass']=True
except Exception as ex:
 report['error']=repr(ex);report['traceback']=traceback.format_exc()
 if e and e.h:
  report['failure_location']=e.location();report['failure_callback2']=hex(e.callback2());photo(e,'failure')
finally:
 if e:e.close()
 after={p:sha(Path(p).read_bytes()) for p in before}
 report['original_saves_unchanged']=before==after
 if before!=after:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='traceback'}),flush=True)
sys.exit(0 if report['pass'] else 1)
