#!/usr/bin/env python3
"""Actual original B1F Strength/Rock Smash route, trainer sight battle and B2F cold save."""
from pathlib import Path
import hashlib,re
qa=Path('tools/qa/native_strength_rock_puzzle_qa.py')
text=qa.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='ab57a60e8f4961c318c0b975863c0ac36075f3e7556f363ae508b702928a3841','puzzle QA dependency changed; inspect it first'
prefix=text.split('e=None\ntry:',1)[0]
assert prefix!=text
prefix,n=re.subn(r"cases=\[.*?\]\nassert head.count", "cases=['strength-b1f-route']\nassert head.count",prefix,count=1,flags=re.S)
assert n==1
assert prefix.count("'Task_YesNoMenu_HandleInput']")==1
prefix=prefix.replace("'Task_YesNoMenu_HandleInput']", "'Task_YesNoMenu_HandleInput','Task_RunTrainerSeeFuncList']",1)
exec(compile(prefix,str(qa),'exec'))
report.update(mode='native-original-vr-b1f-route',route_steps=[],
 scope='B1F west ladder to original B2F ladder; not entire Hoenn or complete Victory Road')
SAMUEL='TRAINER_HOENN_SAMUEL';WT=TT=MT=SAMUEL
route_battle_done=False;expected_party=None
def raw_dex_arrays(b):
 n=off('dex.seen')-off('dex.owned')
 assert 49<=n<=64
 p=off('sb2.pokedex')
 return tuple(bytes(x) for x in [
  b.sb2[p+off('dex.owned'):p+off('dex.owned')+n],
  b.sb2[p+off('dex.seen'):p+off('dex.seen')+n],
  b.sb1[off('sb1.seen1'):off('sb1.seen1')+n],
  b.sb1[off('sb1.seen2'):off('sb1.seen2')+n]])
baseline_dex_bytes=raw_dex_arrays(source)
# Resolve the actual compiled species-to-national table, not an enum through
# the macro-only constant parser or an assumption about Hoenn internal IDs.
national_tables=[n for n in ('sSpeciesToNationalPokedexNum','gSpeciesToNationalPokedexNum') if n in syms]
assert len(national_tables)==1,('candidate species-to-national table missing or ambiguous',national_tables)
national_table=syms[national_tables[0]]
samuel_national=tuple(struct.unpack('<H',r.at(national_table+2*(const(name)-1),2))[0]
 for name in ('SPECIES_SWELLOW','SPECIES_MAWILE','SPECIES_KADABRA'))
assert samuel_national==(277,303,64),('original Samuel national mapping differs',samuel_national)
def guard_route_dex():
 now=raw_dex_arrays(blocks(e))
 assert now[0]==baseline_dex_bytes[0],'caught dex changed during trainer-only route'
 added=[]
 for i in range(1,4):
  expected=bytearray(baseline_dex_bytes[i])
  if route_battle_done:
   for number in samuel_national:
    bit=number-1;expected[bit//8]|=1<<(bit%8)
  assert now[i]==bytes(expected),('seen dex differs beyond original Samuel species',i,
   [bit+1 for bit in range(len(expected)*8)
    if (now[i][bit//8]^expected[bit//8])&(1<<(bit%8))])
  added.append([bit+1 for bit in range(len(expected)*8)
   if (now[i][bit//8]&~baseline_dex_bytes[i][bit//8])&(1<<(bit%8))])
 report['dex_guard']={'caught_bytes_unchanged':True,'all_old_seen_bits_preserved':True,
  'only_seen_allowed_national':list(samuel_national) if route_battle_done else [],
  'seen_added_per_replica':added}
def route_invariants():
 assert e.read(e.ptr('gPokemonStoragePtr'),off('storage'))==source_storage
 assert pc(e)==source_pc and e.u8(syms['gPlayerPartyCount'])==2
 now=e.read(syms['gPlayerParty'],600);party_valid(now,2)
 assert now[100:200]==original_pika,'unedited genuine starter changed through route'
 assert Mon(bytearray(now),0).species()==const('SPECIES_LAPRAS')
 guard_route_dex()
def route_step(key,allow_samuel=False):
 global route_battle_done
 previous=e.location();e.hold(key)
 try:
  for _ in range(100):
   safe(e);e.run(1)
   if e.location()!=previous:break
  else:raise AssertionError(('actual original route blocked',key,previous))
 finally:e.hold()
 e.run(40)
 if allow_samuel and loc_is(e,M) and e.location()[2:]==(34,12):
  # Observe the real sight task and native opponent before any A input.
  sight_seen=False
  for _ in range(120):
   if active_task(e,'Task_RunTrainerSeeFuncList'):sight_seen=True
   if e.u16(syms['gTrainerBattleOpponent_A'])==const(SAMUEL) and not e.field_idle():break
   safe(e);e.run(1)
  else:raise AssertionError('Samuel native sight event did not start without A')
  assert sight_seen,'Samuel native sight approach task not observed'
  report['native_samuel_sight_no_a']=True
  photo(e,'samuel-native-sight')
  native_battle(e,SAMUEL,3);route_battle_done=True
  row=report['stages'][-1]
  assert row['enemy_species'][:3]==[const('SPECIES_SWELLOW'),const('SPECIES_MAWILE'),const('SPECIES_KADABRA')]
  report['original_samuel_sight_battle']=True
 for _ in range(1800):
  safe(e)
  if e.in_battle():
   assert allow_samuel and not route_battle_done,('unexpected route battle',key,e.location())
   assert e.u16(syms['gTrainerBattleOpponent_A'])==const(SAMUEL)
   native_battle(e,SAMUEL,3);route_battle_done=True
   row=report['stages'][-1]
   assert row['enemy_species'][:3]==[const('SPECIES_SWELLOW'),const('SPECIES_MAWILE'),const('SPECIES_KADABRA')]
   report['original_samuel_sight_battle']=True
   break
  if e.field_idle():break
  e.run(1)
 else:raise AssertionError(('actual route field did not settle',key,e.location(),hex(e.callback2())))
 report['route_steps'].append({'key':key,'before':previous,'after':e.location()})
 route_invariants()
 return previous
def walk_many(sequence,allow_samuel=False):
 for key,count in sequence:
  for _ in range(count):route_step(key,allow_samuel)
def turn_blocked(key):
 previous=e.location();e.press(key,hold=1,after=20)
 assert e.location()==previous
def push_expected(key,localid,oldxy,newxy,playerxy,label):
 assert object_by_id(localid)['xy']==oldxy
 previous=route_step(key)
 assert e.location()[2:]==playerxy and object_by_id(localid)['xy']==newxy
 check_companion_visible(previous[2:],label)
 no_player_overlap()
 report['stages'].append({'label':label,'local_id':localid,'before':oldxy,'after':newxy})
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-vr-b1-route-') as td:
  s=SaveFile(str(sav));original_pika=original_starter_copy(s)
  s.fast_battles();s.keep_party(1);s.set_var('VAR_REPEL_STEP_COUNT',250)
  s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);set_badges(s)
  s.set_flag('FLAG_HOENN_BADGE03_GET',True)
  s.set_trainer_beaten(SAMUEL,False)
  assert len(map_info(M)['json']['object_events'])==21
  s.warp(M,8,3)
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  mon=s.party_mon(0);mon.set_otid(owner);mon.set_starter_bit(False);mon.set_snagged(False)
  mon.set_species(const('SPECIES_LAPRAS'),rom=r)
  subs=mon.subs();subs['E'][:6]=bytes(6);subs['A'][:]=bytes(12)
  for i,name in enumerate(['MOVE_STRENGTH','MOVE_ROCK_SMASH','MOVE_SURF','MOVE_TACKLE']):
   mid=const(name);struct.pack_into('<H',subs['A'],2*i,mid)
   subs['A'][8+i]=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  struct.pack_into('<I',subs['M'],4,struct.unpack_from('<I',subs['M'],4)[0]&~(1<<30))
  mon.put_subs(subs);mon.blk[mon.o+19]=(mon.blk[mon.o+19]&~5)|2
  mon.set_held(0);mon.make_strong(100,rom=r)
  po=off('sb1.playerParty');s.sb1[po+100:po+200]=original_pika
  s.sb1[off('sb1.playerPartyCount')]=2
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  assert loc_is(e,M) and e.location()[2:]==(8,3)
  route_invariants();initial_story={f:blocks(e).flag(f) for f in storyflags}
  walk_many([('DOWN',1),('RIGHT',1),('DOWN',3),('LEFT',4)])
  assert e.location()[2:]==(5,7);turn_blocked('LEFT');use_a();quiet_finish(e)
  assert blocks(e).flag(ST)
  push_expected('LEFT',10,(4,7),(3,7),(4,7),'actual-original-boulder-one')
  walk_many([('DOWN',3),('RIGHT',4)])
  assert e.location()[2:]==(8,10)
  push_expected('RIGHT',11,(9,10),(10,10),(9,10),'actual-original-boulder-two')
  walk_many([('DOWN',3),('RIGHT',6),('UP',1),('RIGHT',2)])
  assert e.location()[2:]==(17,12)
  assert object_by_id(17)['xy']==(18,12)
  turn_blocked('RIGHT');use_a();quiet_finish(e)
  object_by_id(17,False);assert blocks(e).flag('FLAG_TEMP_1B')
  previous=route_step('RIGHT');assert e.location()[2:]==(18,12)
  check_companion_visible(previous[2:],'actual-original-rock-route')
  walk_many([('RIGHT',3),('UP',3),('RIGHT',11),('DOWN',3)])
  assert e.location()[2:]==(32,12)
  walk_many([('RIGHT',2)],True)
  assert e.location()[2:]==(34,12) and route_battle_done,'original Samuel automatic sight battle missing'
  walk_many([('DOWN',1),('RIGHT',3),('DOWN',12),('LEFT',1),('DOWN',1),('LEFT',5),('UP',1)])
  assert e.location()[2:]==(31,25)
  route_step('LEFT');settle(e)
  assert loc_is(e,'VictoryRoad_B2F') and e.location()[2:]==(30,25),'original B1F to B2F ladder warp failed'
  report['original_ladder_transition']={'from_map':M,'to_map':'VictoryRoad_B2F','arrival':[30,25]}
  assert not blocks(e).flag(ST),'Strength should reset on an actual floor map change'
  assert all(not blocks(e).flag(f) for f in TEMP),'temporary obstacle flags should reset on actual floor change'
  # Walk away from the ladder before the native save and follower probe so
  # returning to it cannot legitimately warp the player back during the probe.
  walk_many([('RIGHT',2)]);assert e.location()[2:]==(32,25)
  route_invariants();check_story_unchanged(initial_story)
  native_save_reopen(e,source_pc);route_invariants()
  assert loc_is(e,'VictoryRoad_B2F') and e.location()[2:]==(32,25)
  probe_companion('original-b1f-route-b2f-cold',('RIGHT','LEFT'))
  route_invariants();check_story_unchanged(initial_story)
  assert blocks(e).trainer_beaten(SAMUEL)
  report['ram_writes']=0;report['pass']=True;report['full_original_storage_unchanged']=True
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
