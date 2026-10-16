#!/usr/bin/env python3
"""Remaining original VR south puzzle, central 1F exit, League approach and cold save."""
from pathlib import Path
import hashlib,re
qa=Path('tools/qa/native_strength_rock_puzzle_qa.py')
text=qa.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='ab57a60e8f4961c318c0b975863c0ac36075f3e7556f363ae508b702928a3841'
prefix=text.split('e=None\ntry:',1)[0];assert prefix!=text
prefix,n=re.subn(r"cases=\[.*?\]\nassert head.count",
 "cases=['strength-vr-league-route']\nassert head.count",prefix,count=1,flags=re.S)
assert n==1
assert prefix.count("'Task_YesNoMenu_HandleInput']")==1
prefix=prefix.replace("'Task_YesNoMenu_HandleInput']",
 "'Task_YesNoMenu_HandleInput','Task_RunTrainerSeeFuncList']",1)
exec(compile(prefix,str(qa),'exec'))
protected_before=dict(before)
report.update(mode='native-original-vr-league-approach',route_steps=[],
 scope='Checkpoint after passed B2F: B1F south puzzle through central 1F to League lobby; not all regions or optional item platforms')
HALLE='TRAINER_HOENN_HALLE';EDGAR='TRAINER_HOENN_EDGAR_VICTORY_ROAD'
WT=HALLE;TT=MT=EDGAR
trainer_species={
 HALLE:('SPECIES_SABLEYE','SPECIES_ABSOL'),
 EDGAR:('SPECIES_CACTURNE','SPECIES_PELIPPER')}
battle_done=set();expected_party=None
for name,expected in [
 ('HoennVictoryRoad_B1F','574316b10f2989df34eb3a53c3fc4bd946bb0e67bb679e15dfc91997cb47d684'),
 ('HoennVictoryRoad_1F','b100693756672442b3f583a8886950d07b68bac1b6eafe07a2b5fe721d1c484e'),
 ('HoennEverGrandeCity','65fe6682e18c1befab20f007b86811bc5cde2346ded25dd908cc15757ce17d1c')]:
 f=Path('data/layouts')/name/'map.bin';assert sha(f.read_bytes())==expected,('original terrain changed',str(f))
 report.setdefault('original_terrain_sha256',{})[name]=expected
for name,script,expected in [
 ('VictoryRoad_B1F','VictoryRoad_B1F_EventScript_H4',
  (14,20,3,'MOVEMENT_TYPE_FACE_UP_AND_RIGHT','TRAINER_TYPE_NORMAL','3')),
 ('HoennVictoryRoad_1F','HoennVictoryRoad_1F_EventScript_H0',
  (33,22,3,'MOVEMENT_TYPE_FACE_DOWN','TRAINER_TYPE_NORMAL','3'))]:
 rows=[q for q in map_info(name)['json']['object_events'] if q.get('script')==script]
 assert len(rows)==1,('original route trainer missing',name,script)
 q=rows[0]
 got=(q['x'],q['y'],q['elevation'],q['movement_type'],q['trainer_type'],str(q['trainer_sight_or_berry_tree_id']))
 assert got==expected,('original trainer sight differs',name,got,expected)
def raw_dex_arrays(b):
 n=off('dex.seen')-off('dex.owned');assert 49<=n<=64
 p=off('sb2.pokedex')
 return tuple(bytes(x) for x in [
  b.sb2[p+off('dex.owned'):p+off('dex.owned')+n],
  b.sb2[p+off('dex.seen'):p+off('dex.seen')+n],
  b.sb1[off('sb1.seen1'):off('sb1.seen1')+n],
  b.sb1[off('sb1.seen2'):off('sb1.seen2')+n]])
baseline_dex_bytes=raw_dex_arrays(source)
tables=[n for n in ('sSpeciesToNationalPokedexNum','gSpeciesToNationalPokedexNum') if n in syms]
assert len(tables)==1,tables
national={
 trainer:tuple(struct.unpack('<H',r.at(syms[tables[0]]+2*(const(name)-1),2))[0] for name in species)
 for trainer,species in trainer_species.items()}
assert national[HALLE]==(302,359) and national[EDGAR]==(332,279),national
def guard_route_dex():
 now=raw_dex_arrays(blocks(e));assert now[0]==baseline_dex_bytes[0],'caught dex changed on trainer route'
 allowed=sorted({number for trainer in battle_done for number in national[trainer]});added=[]
 for i in range(1,4):
  expected=bytearray(baseline_dex_bytes[i])
  for number in allowed:
   bit=number-1;expected[bit//8]|=1<<(bit%8)
  assert now[i]==bytes(expected),('seen dex changed beyond actually fought original trainers',i,allowed)
  added.append([bit+1 for bit in range(len(expected)*8)
   if (now[i][bit//8]&~baseline_dex_bytes[i][bit//8])&(1<<(bit%8))])
 report['dex_guard']={'caught_bytes_unchanged':True,'old_seen_preserved':True,
  'only_seen_allowed_national':allowed,'seen_added_per_replica':added}
def route_invariants():
 assert e.read(e.ptr('gPokemonStoragePtr'),off('storage'))==source_storage,'full original storage changed'
 assert pc(e)==source_pc and e.u8(syms['gPlayerPartyCount'])==2
 now=e.read(syms['gPlayerParty'],600);party_valid(now,2)
 assert now[100:200]==original_pika,'genuine original Pika edited through route'
 assert Mon(bytearray(now),0).species()==const('SPECIES_LAPRAS')
 guard_route_dex()
def run_sight_battle(trainer):
 assert trainer not in battle_done,('completed trainer battled twice',trainer)
 sight=False
 for _ in range(180):
  sight|=active_task(e,'Task_RunTrainerSeeFuncList')
  if e.u16(syms['gTrainerBattleOpponent_A'])==const(trainer) and not e.field_idle():break
  safe(e);e.run(1)
 else:raise AssertionError(('expected native sight never started without A',trainer,e.location()))
 assert sight,('native sight task not observed before A',trainer)
 photo(e,'native-sight-'+trainer)
 report.setdefault('native_sight_no_a',[]).append(trainer)
 native_battle(e,trainer,len(trainer_species[trainer]))
 row=report['stages'][-1]
 assert row['enemy_species'][:len(trainer_species[trainer])]==[const(x) for x in trainer_species[trainer]]
 battle_done.add(trainer)
 assert blocks(e).trainer_beaten(trainer)
 route_invariants()
def route_step(key,expected_sight=None):
 previous=e.location();e.hold(key)
 try:
  for _ in range(100):
   safe(e);assert not e.in_battle(),'step started in unexpected battle';e.run(1)
   if e.location()!=previous:break
  else:raise AssertionError(('original route blocked',key,previous))
 finally:e.hold()
 e.run(40)
 sight_now=active_task(e,'Task_RunTrainerSeeFuncList')
 pending=(not e.field_idle() and expected_sight is not None
          and e.u16(syms['gTrainerBattleOpponent_A'])==const(expected_sight))
 if sight_now or e.in_battle() or pending:
  assert expected_sight is not None,('unexpected trainer or wild event',key,e.location())
  assert expected_sight not in battle_done
  run_sight_battle(expected_sight)
 for _ in range(2000):
  safe(e)
  if e.in_battle():
   assert expected_sight is not None and expected_sight not in battle_done
   run_sight_battle(expected_sight)
  if e.field_idle():break
  e.run(1)
 else:raise AssertionError(('route did not settle',key,e.location(),hex(e.callback2())))
 report['route_steps'].append({'key':key,'before':previous,'after':e.location()})
 route_invariants();return previous
def walk_many(sequence,expected_sight=None):
 for key,count in sequence:
  for _ in range(count):route_step(key,expected_sight)
def turn_blocked(key):
 prior=e.location();e.press(key,hold=1,after=20);assert e.location()==prior
def push_one(key,localid,oldxy,newxy,playerxy,label):
 assert object_by_id(localid)['xy']==oldxy
 prior=route_step(key)
 assert e.location()[2:]==playerxy and object_by_id(localid)['xy']==newxy
 check_companion_visible(prior[2:],label);no_player_overlap()
 report['stages'].append({'label':label,'before':oldxy,'after':newxy,'native_push':True})
def smash_one(key,localid,xy,flag,label):
 assert object_by_id(localid)['xy']==xy
 turn_blocked(key);use_a();quiet_finish(e)
 object_by_id(localid,False);assert blocks(e).flag(flag)
 route_invariants();report['stages'].append({'label':label,'native_removed':True,'flag':flag})
def check_map_warp(from_map,index,to_map,arrival,label):
 w=map_info(from_map)['json']['warp_events'][index]
 q=map_info(to_map)['json']['warp_events'][int(w['dest_warp_id'])]
 assert w['dest_map']==map_info(to_map)['json']['id'] and (q['x'],q['y'])==arrival
 assert loc_is(e,to_map) and e.location()[2:]==arrival,(label,e.location(),arrival)
 report['stages'].append({'label':label,'from_map':from_map,'to_map':to_map,'arrival':list(arrival)})
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-vr-league-route-') as td:
  s=SaveFile(str(sav));original_pika=original_starter_copy(s)
  assert Mon(bytearray(original_pika),0).subs()['G'][9]==255,'long-route 100-byte Pika guard requires the actual original friendship cap'
  report['original_pika_friendship']=255
  s.fast_battles();s.keep_party(1);s.set_var('VAR_REPEL_STEP_COUNT',250)
  s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);set_badges(s)
  for i in range(1,9):s.set_flag('FLAG_HOENN_BADGE%02d_GET'%i,True)
  s.set_trainer_beaten(HALLE,False);s.set_trainer_beaten(EDGAR,False)
  # This checkpoint was reached and saved natively in the independent B2F
  # PASS. This case tests the remaining path and does not re-test that floor.
  s.warp(M,18,16)
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  mon=s.party_mon(0);mon.set_otid(owner);mon.set_starter_bit(False);mon.set_snagged(False)
  mon.set_species(const('SPECIES_LAPRAS'),rom=r)
  subs=mon.subs();subs['E'][:6]=bytes(6);subs['A'][:]=bytes(12)
  for i,name in enumerate(['MOVE_STRENGTH','MOVE_ROCK_SMASH','MOVE_SURF','MOVE_ICE_BEAM']):
   mid=const(name);struct.pack_into('<H',subs['A'],2*i,mid)
   subs['A'][8+i]=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  struct.pack_into('<I',subs['M'],4,struct.unpack_from('<I',subs['M'],4)[0]&~(1<<30))
  mon.put_subs(subs);mon.blk[mon.o+19]=(mon.blk[mon.o+19]&~5)|2
  mon.set_held(0);mon.make_strong(100,rom=r)
  po=off('sb1.playerParty');s.sb1[po+100:po+200]=original_pika
  s.sb1[off('sb1.playerPartyCount')]=2
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  assert loc_is(e,M) and e.location()[2:]==(18,16)
  route_invariants();initial_story={f:blocks(e).flag(f) for f in storyflags}
  # Approach the adjacent sight tile from the north. At distance one the
  # trainer does not walk into the south passage while approaching the player.
  walk_many([('DOWN',1),('LEFT',2),('DOWN',2),('LEFT',1),('DOWN',1)],HALLE)
  assert e.location()[2:]==(15,20)
  # Original UP/RIGHT facing remains untouched. Retry actual UP/DOWN steps
  # into the adjacent RIGHT sight tile; no A or facing/RAM/template edits.
  for _ in range(24):
   if HALLE in battle_done:break
   route_step('UP',HALLE);assert e.location()[2:]==(15,19)
   e.run(8);route_step('DOWN',HALLE);assert e.location()[2:]==(15,20)
  assert HALLE in battle_done,'original Halle sight did not trigger within actual native step retries'
  assert object_by_id(7)['xy']==(14,20),'adjacent trainer approach moved Halle into the route'
  walk_many([('DOWN',5),('RIGHT',4)]);assert e.location()[2:]==(19,25)
  smash_one('RIGHT',18,(20,25),'FLAG_TEMP_1C','original-south-rock-one')
  prior=route_step('RIGHT');assert e.location()[2:]==(20,25)
  check_companion_visible(prior[2:],'south-first-rock-passage')
  turn_blocked('DOWN');use_a();quiet_finish(e);assert blocks(e).flag(ST)
  push_one('DOWN',12,(20,26),(20,27),(20,26),'original-south-boulder')
  smash_one('RIGHT',19,(21,26),'FLAG_TEMP_1D','original-south-rock-two')
  walk_many([('RIGHT',2),('UP',5),('LEFT',1)])
  assert e.location()[2:]==(21,21)
  route_step('LEFT');settle(e)
  check_map_warp(M,5,'HoennVictoryRoad_1F',(21,32),'original-central-ladder-to-1f')
  assert not blocks(e).flag(ST) and all(not blocks(e).flag(f) for f in TEMP)
  # Original central stairs and high bridge lead to the north half of 1F.
  walk_many([('UP',4),('RIGHT',12),('DOWN',3),('RIGHT',3),
             ('UP',7),('LEFT',3)],EDGAR)
  assert e.location()[2:]==(33,24) and EDGAR in battle_done,'original Edgar no-A sight battle missing'
  walk_many([('LEFT',1),('UP',6),('RIGHT',1),('UP',3),
             ('LEFT',1),('UP',10),('RIGHT',6)])
  assert e.location()[2:]==(38,5)
  route_step('RIGHT');settle(e)
  assert loc_is(e,'HoennVictoryRoad_1F') and e.location()[2:]==(39,5)
  # Original MB_SOUTH_ARROW_WARP requires DOWN while standing on the tile.
  route_step('DOWN');settle(e)
  assert loc_is(e,'EverGrandeCity') and e.location()[2]==18 and 27<=e.location()[3]<=29,('original cave exit',e.location())
  report['stages'].append({'label':'original-vr-north-city-exit','arrival':list(e.location()[2:])})
  # A door exit may finish on its warp tile or after the native south step.
  # Move to the same two-tiles-south outdoor tile using actual DOWN input.
  while e.location()[3]<29:route_step('DOWN')
  assert e.location()[2:]==(18,29)
  walk_many([('UP',1),('RIGHT',3),('UP',1),('RIGHT',4),('UP',11),
             ('LEFT',5),('UP',10),('LEFT',2)])
  assert e.location()[2:]==(18,6)
  route_step('UP');settle(e)
  assert loc_is(e,'EverGrandeCity_PokemonLeague_1F'),('original League entrance did not warp',e.location())
  q=map_info('EverGrandeCity_PokemonLeague_1F')['json']['warp_events'][0]
  assert q['dest_map']=='MAP_EVER_GRANDE_CITY' and int(q['dest_warp_id'])==0
  assert e.location()[2]==q['x'] and q['y']-2<=e.location()[3]<=q['y'],('League entrance landing',e.location(),q)
  # Stay in the lobby, avoiding the already tested Elite Four challenge.
  while e.location()[3]>9:route_step('UP')
  assert e.location()[2:]==(9,9)
  report['stages'].append({'label':'original-vr-to-league-lobby','arrival':[9,9],
                          'elite_four_existing_checks_not_repeated':True})
  route_invariants();check_story_unchanged(initial_story)
  native_save_reopen(e,source_pc);route_invariants()
  assert loc_is(e,'EverGrandeCity_PokemonLeague_1F') and e.location()[2:]==(9,9)
  probe_companion('original-league-approach-cold',('RIGHT','LEFT'))
  route_invariants();check_story_unchanged(initial_story)
  assert battle_done=={HALLE,EDGAR}
  report['ram_writes']=0;report['pass']=True;report['full_original_storage_unchanged']=True
except Exception as ex:
 report['error']=repr(ex);report['traceback']=traceback.format_exc()
 if e and e.h:report['failure_location']=e.location();photo(e,'failure')
finally:
 if e:e.close()
 after={p:sha(Path(p).read_bytes()) for p in protected_before}
 report['original_saves_unchanged']=protected_before==after
 if protected_before!=after:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='traceback'}),flush=True)
sys.exit(0 if report['pass'] else 1)
