#!/usr/bin/env python3
"""Original B2F sight battle, Surf/waterfalls, B1F ladder and native save/cold."""
from pathlib import Path
import hashlib
qa=Path('tools/qa/native_victory_road_b1f_route_qa.py')
text=qa.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='201dca861305286b5798291922943367117e56063b6d8a054a00a7f419e88c70','passed B1F route dependency changed'
prefix=text.split('e=None\ntry:',1)[0]
assert prefix!=text
# Keep the proven UI/task/byte-preservation helpers. Narrowly adapt only this
# floor's native sight event and its actual original three trainer species.
changes=[
 ("'strength-b1f-route'","'strength-b2f-route'"),
 ("mode='native-original-vr-b1f-route'","mode='native-original-vr-b2f-route'"),
 ("scope='B1F west ladder to original B2F ladder; not entire Hoenn or complete Victory Road'",
  "scope='Original B2F entry through Julie, Surf and both waterfalls to B1F; not complete Victory Road or entire Hoenn'"),
 ('SAMUEL','JULIE'),('Samuel','Julie'),('samuel','julie'),
 ('SPECIES_SWELLOW','SPECIES_SANDSLASH'),('SPECIES_MAWILE','SPECIES_NINETALES'),
 ('SPECIES_KADABRA','SPECIES_TROPIUS'),
 ('(277,303,64)','(28,38,357)'),('(34,12)','(33,22)')]
for old,new in changes:
 assert old in prefix,('missing passed dependency anchor',old)
 prefix=prefix.replace(old,new)
exec(compile(prefix,str(qa),'exec'))
protected_before=dict(before)
M='VictoryRoad_B2F'
WATERFALL=const('MOVE_WATERFALL')
FORCED=1<<avatar_states.index('PLAYER_AVATAR_STATE_FORCED')
assert 'Task_UseWaterfall' not in qa_task_names
for line in tab.splitlines():
 p=line.split()
 if len(p)>=6 and re.fullmatch('[0-9a-fA-F]{8}',p[0]) and p[-1]=='Task_UseWaterfall':
  sets.setdefault('Task_UseWaterfall',set()).add(int(p[0],16)&~1)
assert sets.get('Task_UseWaterfall'),'native Waterfall task missing'
# These are the imported original Emerald maps. No proposed terrain edits.
for name,expected in [
 ('HoennVictoryRoad_B1F','574316b10f2989df34eb3a53c3fc4bd946bb0e67bb679e15dfc91997cb47d684'),
 ('HoennVictoryRoad_B2F','60f525ef9b6e374604f4dcfd96ef1091b6b9bdaac2b73860b345eb75476c00c0')]:
 f=Path('data/layouts')/name/'map.bin'
 assert sha(f.read_bytes())==expected,('original route terrain changed',str(f))
 report.setdefault('original_terrain_sha256',{})[name]=expected
b2_json=map_info(M)['json']
julie_objects=[q for q in b2_json['object_events'] if q.get('script')=='VictoryRoad_B2F_EventScript_H3']
assert len(julie_objects)==1,julie_objects
jo=julie_objects[0]
assert (jo['x'],jo['y'],jo['elevation'],jo['movement_type'],jo['trainer_type'],
        str(jo['trainer_sight_or_berry_tree_id']))==(
 35,22,3,'MOVEMENT_TYPE_FACE_LEFT','TRAINER_TYPE_NORMAL','2'),('original Julie sight object changed',jo)
w=b2_json['warp_events']
assert (w[2]['x'],w[2]['y'],w[2]['dest_map'],str(w[2]['dest_warp_id']))==(
 19,12,'MAP_VICTORY_ROAD_B1F','1'),('original B2F to B1F ladder changed',w[2])
report['original_julie_object']=jo
report['original_ladder_event']=w[2]
def check_follower_mode(previous,label,surf):
 b,sp=companion_state()
 xy=struct.unpack_from('<hh',b,16)
 assert xy==(previous[0]+7,previous[1]+7),('original Pika lost previous tile',label,xy,previous)
 assert not(int.from_bytes(b[:4],'little')&((1<<13)|(1<<14))),('Pika hidden or offscreen',label)
 assert not(e.u8(sp+0x3e)&4),('Pika sprite invisible',label)
 avatar=e.u8(syms['gPlayerAvatar'])
 assert bool(avatar&SURF)==surf,('wrong native avatar state',label,avatar,surf)
 assert e.read(syms['gPlayerParty']+100,100)==original_pika,'genuine Pika edited during field transition'
 photo(e,'follower-'+label+'-'+str(len(report['follower_checks'])))
 report['follower_checks'].append({'label':label,'map':e.location()[:2],
  'player_xy':e.location()[2:],'follower_xy':[xy[0]-7,xy[1]-7],
  'visible':True,'native_sprite_active':True,'avatar_flags':avatar})
 route_invariants()
def surf_from_coast(key,expected,label):
 before=e.location()
 assert not(e.u8(syms['gPlayerAvatar'])&SURF),('Surf must start on original land',label,before)
 turn_blocked(key)
 use_a();quiet_finish(e);e.run(40)
 assert loc_is(e,M) and e.location()[2:]==expected,('native Surf coast failed',label,e.location(),expected)
 check_follower_mode(before[2:],label,True)
 report['stages'].append({'label':label,'before':before,'after':e.location(),'native_surf_a':True})
def forced_to(expected,label,previous,require_task=False):
 last=e.location();steps=[{'frame':e.frame(),'xy':list(last[2:])}];seen_task=False
 for frame_index in range(5000):
  safe(e);assert not e.in_battle(),('unexpected battle during original waterfall',label)
  now=e.location()
  if now!=last:steps.append({'frame':e.frame(),'xy':list(now[2:])});last=now
  seen_task|=active_task(e,'Task_UseWaterfall')
  if (loc_is(e,M) and now[2:]==expected and e.field_idle()
      and not active_task(e,'Task_UseWaterfall') and not e.u8(syms['gPlayerAvatar']+6)):
   e.run(40);break
  # The original A script shows a normal used-WATERFALL message after
  # YES; advance that native text exactly as in the passed waterfall QA.
  if require_task and frame_index%8==0:e.press('A',hold=1,after=1)
  else:e.run(1)
 else:raise AssertionError(('original B2F waterfall timeout',label,e.location(),steps[-12:]))
 if require_task:assert seen_task,'ascent skipped native Waterfall task'
 assert not(e.u8(syms['gPlayerAvatar'])&FORCED),'waterfall forced movement stayed set'
 assert len(steps)>=4,('original waterfall did not traverse intermediate tiles',label,steps)
 check_follower_mode(previous,label,True)
 report['stages'].append({'label':label,'steps':steps,'native_waterfall_task_seen':seen_task})
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-vr-b2-route-') as td:
  s=SaveFile(str(sav));original_pika=original_starter_copy(s)
  s.fast_battles();s.keep_party(1);s.set_var('VAR_REPEL_STEP_COUNT',250)
  s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);set_badges(s)
  for i in (3,4,5,8):s.set_flag('FLAG_HOENN_BADGE%02d_GET'%i,True)
  s.set_trainer_beaten(JULIE,False)
  # A TEMPORARY save fixture only: native entry coordinates reached by the
  # independently passed B1F route, with no product or source-save mutation.
  s.warp(M,30,25)
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  mon=s.party_mon(0);mon.set_otid(owner);mon.set_starter_bit(False);mon.set_snagged(False)
  mon.set_species(const('SPECIES_LAPRAS'),rom=r)
  subs=mon.subs();subs['E'][:6]=bytes(6);subs['A'][:]=bytes(12)
  for i,name in enumerate(['MOVE_SURF','MOVE_WATERFALL','MOVE_ICE_BEAM','MOVE_PSYCHIC']):
   mid=const(name);struct.pack_into('<H',subs['A'],2*i,mid)
   subs['A'][8+i]=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  struct.pack_into('<I',subs['M'],4,struct.unpack_from('<I',subs['M'],4)[0]&~(1<<30))
  mon.put_subs(subs);mon.blk[mon.o+19]=(mon.blk[mon.o+19]&~5)|2
  mon.set_held(0);mon.make_strong(100,rom=r)
  po=off('sb1.playerParty');s.sb1[po+100:po+200]=original_pika
  s.sb1[off('sb1.playerPartyCount')]=2
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  assert loc_is(e,M) and e.location()[2:]==(30,25)
  route_invariants();initial_story={f:blocks(e).flag(f) for f in storyflags}
  walk_many([('RIGHT',3),('UP',3)],True)
  assert e.location()[2:]==(33,22) and route_battle_done,'original Julie no-A sight battle missing'
  assert report['native_julie_sight_no_a'] and report['original_julie_sight_battle']
  walk_many([('UP',5)]);assert e.location()[2:]==(33,17)
  surf_from_coast('UP',(33,16),'original-lower-surf')
  lower_water_prev=route_step('UP');check_follower_mode(lower_water_prev[2:],'lower-water-step',True)
  walk_many([('UP',2)]);assert e.location()[2:]==(33,13)
  check_follower_mode((33,14),'original-island-landing',False)
  route_step('UP');assert e.location()[2:]==(33,12)
  surf_from_coast('LEFT',(32,12),'original-island-surf')
  walk_many([('LEFT',5)]);assert e.location()[2:]==(27,12)
  turn_blocked('UP');use_a()
  forced_to((27,8),'original-waterfall-ascent',(27,9),True)
  walk_many([('UP',4),('LEFT',18),('DOWN',6)])
  assert e.location()[2:]==(9,10)
  # The original downward waterfall current needs only a native DOWN step.
  descent_origin=e.location();e.hold('DOWN')
  try:
   for _ in range(100):
    safe(e);assert not e.in_battle();e.run(1)
    if e.location()!=descent_origin:break
   else:raise AssertionError('original downward waterfall step blocked')
  finally:e.hold()
  forced_to((9,14),'original-waterfall-descent',(9,13))
  walk_many([('RIGHT',6),('UP',2),('RIGHT',3)])
  assert e.location()[2:]==(18,12)
  check_follower_mode((17,12),'original-west-landing',False)
  route_step('RIGHT');settle(e)
  assert loc_is(e,'VictoryRoad_B1F') and e.location()[2:]==(17,16),'original B2F to B1F ladder warp failed'
  report['original_ladder_transition']={'from_map':M,'to_map':'VictoryRoad_B1F','arrival':[17,16]}
  assert not(e.u8(syms['gPlayerAvatar'])&SURF),'Surf persisted on dry B1F ladder'
  assert not blocks(e).flag(ST)
  assert all(not blocks(e).flag(f) for f in TEMP),'temporary obstacle flags persisted across actual floor warp'
  # 18,16 is the single east landing floor; 19,16 is a wall. The DOWN/UP
  # probe stays off the ladder and cannot legitimately warp back to B2F.
  route_step('RIGHT');assert e.location()[2:]==(18,16)
  route_invariants();check_story_unchanged(initial_story)
  native_save_reopen(e,source_pc);route_invariants()
  assert loc_is(e,'VictoryRoad_B1F') and e.location()[2:]==(18,16)
  probe_companion('original-b2f-route-b1f-cold',('DOWN','UP'))
  route_invariants();check_story_unchanged(initial_story)
  assert blocks(e).trainer_beaten(JULIE)
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
