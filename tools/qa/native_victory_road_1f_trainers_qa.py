#!/usr/bin/env python3
"""Native original Victory Road 1F teams, sight encounters and cold saves."""
from pathlib import Path
head=Path('tools/qa/hoenn_weather_space_native_qa.py').read_text().split('e=None\ntry:',1)[0]
old="choices=['weather-party','weather-pc','space']";assert head.count(old)==1
head=head.replace(old,"choices=['edgar','hope','albert','katelynn','quincy','edgar-sight','quincy-done']",1)
exec(compile(head,'tools/qa/hoenn_weather_space_native_qa.py','exec'))
assert not a.loss or a.case in ('edgar','hope','albert','katelynn','quincy'),'invalid loss case'
M='HoennVictoryRoad_1F';B='FLAG_HOENN_BADGE08_GET';L='FLAG_HOENN_LEAGUE_CLEAR'
names=['Edgar','Hope','Albert','Katelynn','Quincy']
trainers=['TRAINER_HOENN_'+n.upper()+'_VICTORY_ROAD' for n in names]
choice=a.case.split('-')[0];index=[n.lower() for n in names].index(choice);T=trainers[index]
WALLY='TRAINER_HOENN_WALLY_VICTORY_ROAD_FINAL'
WT=T;TT=WALLY;MT=T;flags=[B,L]
positions=[(33,21),(6,14),(27,33),(29,16),(32,16)]
expected_teams=[
 [('SPECIES_CACTURNE',43,None),('SPECIES_PELIPPER',43,None)],
 [('SPECIES_ROSELIA',45,None)],
 [('SPECIES_MAGNETON',43,None),('SPECIES_MUK',43,None)],
 [('SPECIES_GARDEVOIR',43,['MOVE_SKILL_SWAP','MOVE_PSYCHIC','MOVE_THUNDERBOLT','MOVE_CALM_MIND']),
  ('SPECIES_SLAKING',43,['MOVE_EARTHQUAKE','MOVE_SHADOW_BALL','MOVE_AERIAL_ACE','MOVE_BRICK_BREAK'])],
 [('SPECIES_SLAKING',43,['MOVE_ATTRACT','MOVE_ICE_BEAM','MOVE_THUNDERBOLT','MOVE_FLAMETHROWER']),
  ('SPECIES_DUSCLOPS',43,['MOVE_SKILL_SWAP','MOVE_PROTECT','MOVE_WILL_O_WISP','MOVE_TOXIC'])]]
script=Path('data/maps/'+M+'/scripts.inc').read_text()
assert 'THYL_VICTORY_ROAD_1F_TRAINERS_V1' in script
for i,t in enumerate(trainers):
 assert 'trainerbattle_single '+t+', '+M+'_Text_TY'+names[i]+'Intro' in script
 assert '_EventScript_TYWallyFinal' in script
j=json.loads(Path('data/maps/'+M+'/map.json').read_text())
for i,sight in enumerate([3,4,3,2,2]):
 o=[o for o in j['object_events'] if o['script']==M+'_EventScript_H'+str(i)]
 assert len(o)==1 and o[0]['trainer_type']=='TRAINER_TYPE_NORMAL'
 assert str(o[0]['trainer_sight_or_berry_tree_id'])==str(sight)
assert len(j['object_events'])==8
# Resolve the approach task from the actual candidate; no manually assigned callback.
assert 'Task_RunTrainerSeeFuncList' in syms
sets.setdefault('Task_RunTrainerSeeFuncList',set()).add(syms['Task_RunTrainerSeeFuncList']&~1)
report.update(mode='native-vr1f-trainers-'+a.case+('-loss' if a.loss else '-win'),
 fixture='temporary native battle fixture; user SAV/PC and old dex records preserved',
 native_story_not_entire_regions=True,stages=[])
gd.FIELDS.update({'vr_object':('ObjectEvent',None),'vr_object.localid':('ObjectEvent','localId'),
 'vr_object.current':('ObjectEvent','currentCoords')})
gd._OFFSETS=None  # the inherited head initialized its offset cache before these fields were added
source_storage=bytes(source.blocks['storage'][:off('storage')])
trainer_size=off('sb2.hoennFlags')-off('sb2.hoennTrainerFlags');assert trainer_size==128
def dex_bytes(b):
 n=off('dex.seen')-off('dex.owned');assert 49<=n<=64
 return [bytes(b.sb2[off('sb2.pokedex')+off('dex.owned'):off('sb2.pokedex')+off('dex.owned')+n]),
  bytes(b.sb2[off('sb2.pokedex')+off('dex.seen'):off('sb2.pokedex')+off('dex.seen')+n]),
  bytes(b.sb1[off('sb1.seen1'):off('sb1.seen1')+n]),bytes(b.sb1[off('sb1.seen2'):off('sb1.seen2')+n])]
original_dex=dex_bytes(source)
def trainer_bits(b):return bytes(b.sb2[off('sb2.hoennTrainerFlags'):off('sb2.hoennTrainerFlags')+trainer_size])
def invariants(allow_seen=False,won=False):
 assert e.read(e.ptr('gPokemonStoragePtr'),off('storage'))==source_storage,'full storage changed'
 assert pc(e)==source_pc and e.u8(syms['gPlayerPartyCount'])==1
 party_valid(e.read(syms['gPlayerParty'],600),1)
 current=dex_bytes(blocks(e))
 assert current[0]==original_dex[0],'owned dex records changed'
 if allow_seen:
  for before,after in zip(original_dex[1:],current[1:]):
   assert all((x&y)==x for x,y in zip(before,after)),'old seen record lost'
 else:assert current==original_dex,'nonbattle dialogue changed dex'
 expected=bytearray(initial_trainer_bits)
 bit=const(T)-const('HOENN_TRAINERS_START')
 if won:expected[bit//8]|=1<<(bit%8)
 assert trainer_bits(blocks(e))==bytes(expected),'another Hoenn trainer bit changed'
 assert {f:blocks(e).flag(f) for f in flags}==initial_flags,'region/badge flags changed'
def default_moves(species,level):
 # Exact native level-up table from this candidate ROM. Duplicate moves are
 # ignored, and a fifth known move displaces the oldest, as pokemon.c does.
 p=struct.unpack('<I',r.at(syms['gLevelUpLearnsets']+4*species,4))[0]
 moves=[]
 for i in range(256):
  entry=struct.unpack('<H',r.at(p+2*i,2))[0]
  if entry==0xFFFF or entry>>9>level:break
  move=entry&0x1FF
  if move not in moves:
   if len(moves)==4:moves.pop(0)
   moves.append(move)
 else:raise AssertionError('unterminated native learnset')
 return moves+[const('MOVE_NONE')]*(4-len(moves))
def check_original_enemy():
 mash_until(e,e.in_battle,400);assert menu(e)
 assert e.u16(syms['gTrainerBattleOpponent_A'])==const(T)
 data=e.read(syms['gEnemyParty'],600)
 team=expected_teams[index];actual=[]
 for i,(species,level,moves) in enumerate(team):
  mon=Mon(bytearray(data),i*100);species_id=const(species)
  assert mon.species()==species_id and data[i*100+84]==level,(i,species,level)
  expected=[const(n) for n in moves] if moves else default_moves(species_id,level)
  got=list(struct.unpack_from('<4H',mon.subs()['A']))
  assert got==expected,('original enemy moves changed',names[index],i,got,expected)
  actual.append({'species':species,'level':level,'moves':got})
 assert all(Mon(bytearray(data),i*100).species()==0 for i in range(len(team),6))
 report['original_enemy_team']=actual
def begin_dialogue():
 initial=e.location();assert loc_is(e,M)
 e.press('DOWN',hold=1,after=20);assert e.location()==initial
 e.press('A',hold=3,after=20)
def post_dialogue():
 quiet_finish(e)
 expected=r.at(syms[M+'_Text_H'+str(index)],10)
 assert e.read(syms['gStringVar4'],10)==expected,'wrong post-battle dialogue'
 photo(e,'trainer-post-dialogue')
def approach_without_a():
 assert a.case=='edgar-sight' and e.location()[2:]==(32,25)
 e.hold('RIGHT')
 seen=False
 for i in range(60):
  e.run(1)
  if e.location()[2:]==(33,25):
   e.hold()
   seen=active_task(e,'Task_RunTrainerSeeFuncList')
   break
 else:raise AssertionError(('sight approach did not reach tile',e.location()))
 for _ in range(100):
  if active_task(e,'Task_RunTrainerSeeFuncList'):seen=True
  if e.u16(syms['gTrainerBattleOpponent_A'])==const(T) and not e.field_idle():break
  safe(e);e.run(1)
 else:raise AssertionError('trainer sight did not start native event without A')
 assert seen,'native sight approach task not observed'
 report['native_sight_no_a']=True
 photo(e,'edgar-native-sight')
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-vr1f-trainers-qa-') as td:
  s=SaveFile(str(sav));s.fast_battles();s.keep_party(1)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_var('VAR_REPEL_STEP_COUNT',250);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);s.set_flag(B,True);s.set_flag(L,False)
  for t in trainers:s.set_trainer_beaten(t,False)
  s.set_trainer_beaten(WALLY,True)
  if a.case=='quincy-done':s.set_trainer_beaten(T,True)
  initial_trainer_bits=trainer_bits(s)
  xy=(32,25) if a.case=='edgar-sight' else positions[index]
  s.warp(M,*xy)
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  m=s.party_mon(0);m.set_otid(owner);m.set_starter_bit(False);m.set_snagged(False)
  m.set_species(const('SPECIES_MAGIKARP' if a.loss else 'SPECIES_MEWTWO'),rom=r)
  sub=m.subs();sub['E'][:6]=bytes(6);sub['G'][8]=0 if a.loss else 255;sub['A'][:]=bytes(12)
  moves=['MOVE_SPLASH'] if a.loss else ['MOVE_AERIAL_ACE','MOVE_THUNDERBOLT','MOVE_ICE_BEAM','MOVE_SHADOW_BALL']
  for i,name in enumerate(moves):
   mid=const(name);struct.pack_into('<H',sub['A'],i*2,mid)
   pp=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
   sub['A'][8+i]=pp if a.loss else pp*8//5
  struct.pack_into('<I',sub['M'],4,struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30))
  m.put_subs(sub);m.blk[m.o+19]=(m.blk[m.o+19]&~5)|2
  m.set_held(const('ITEM_NONE' if a.loss else 'ITEM_LEFTOVERS'));m.make_strong(1 if a.loss else 100,rom=r)
  assert bytes(s.blocks['storage'][:off('storage')])==source_storage
  tmp=Path(td)/'fixture.sav';s.save(str(tmp));check_sectors(SaveFile(str(tmp)))
  e=ReadOnlyEmu(str(rom),str(tmp),sym='');e.syms=syms;e.boot_continue();settle(e)
  initial_flags={f:blocks(e).flag(f) for f in flags}
  assert loc_is(e,M) and e.location()[2:]==xy
  invariants()
  if a.case=='quincy-done':
   begin_dialogue();post_dialogue();assert not e.in_battle()
   invariants();native_save_reopen(e,source_pc);invariants()
   begin_dialogue();post_dialogue();assert not e.in_battle()
   report['legacy_defeated_skips_battle']=True
  else:
   if a.case=='edgar-sight':approach_without_a()
   else:begin_dialogue()
   check_original_enemy();native_battle(e,T,len(expected_teams[index]))
   if a.loss:
    assert not loc_is(e,M),'native blackout did not leave Victory Road'
    assert not blocks(e).trainer_beaten(T)
    invariants(True);native_save_reopen(e,source_pc);invariants(True)
    report['native_loss_not_completed']=True
   else:
    assert loc_is(e,M) and blocks(e).trainer_beaten(T)
    invariants(True,True);native_save_reopen(e,source_pc);invariants(True,True)
    # Saved map objects can change facing or position after a sight approach.
    # Return by actual key walking before retalking the defeated trainer.
    if a.case=='edgar-sight':
     o=None
     objsize=off('vr_object')
     for slot in range(16):
      q=syms['gObjectEvents']+slot*objsize
      if e.u8(q+off('vr_object.localid'))==1 and e.u32(q)&1:
       o=struct.unpack('<hh',e.read(q+off('vr_object.current'),4));break
     assert o is not None,'Edgar object missing after save'
     report['sight_post_object_xy']=o
     # The cold-load may preserve the approached NPC or restore its template.
     # Read its actual position and walk to its southern adjacent floor tile.
     npc_xy=(o[0]-7,o[1]-7)
     assert npc_xy[0]==33 and 22<=npc_xy[1]<=24,npc_xy
     go(e,npc_xy[0],npc_xy[1]+1)
     initial=e.location();e.press('UP',hold=1,after=20)
     assert e.location()==initial,'Edgar not adjacent after native walking'
     e.press('A',hold=3,after=20)
    else:begin_dialogue()
    post_dialogue();assert not e.in_battle()
    invariants(True,True);report['native_win_saved_without_repeat']=True
  report['pass']=True;report['full_original_storage_unchanged']=True
  report['old_owned_and_seen_dex_bits_preserved']=True
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
