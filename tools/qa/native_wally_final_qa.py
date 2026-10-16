#!/usr/bin/env python3
"""Native Wally final battle/choices/legacy QA on temporary SAV fixtures."""
from pathlib import Path
head=Path('tools/qa/hoenn_weather_space_native_qa.py').read_text().split('e=None\ntry:',1)[0]
old="choices=['weather-party','weather-pc','space']";assert head.count(old)==1
head=head.replace(old,"choices=['first','remember','loss','decline','early','done','legacy']",1)
exec(compile(head,'tools/qa/hoenn_weather_space_native_qa.py','exec'))
assert a.loss==(a.case=='loss'),'--loss is required only for loss case'
T='TRAINER_HOENN_WALLY_VICTORY_ROAD_FINAL';PREV='TRAINER_HOENN_WALLY_MAUVILLE'
WT=T;TT=PREV;MT=T
M='HoennVictoryRoad_1F';B='FLAG_HOENN_BADGE08_GET';L='FLAG_HOENN_LEAGUE_CLEAR'
flags=[B,L]
wally_script=Path('data/maps/HoennVictoryRoad_1F/scripts.inc').read_text()
assert 'goto_if_not_defeated '+PREV+', '+M+'_EventScript_TYWallyFirstMeeting' in wally_script
assert not re.search(r'checktrainerflag[^\n]*\n\s*goto_if_\w+\s+VAR_RESULT',wally_script),'trainer condition incorrectly depends on VAR_RESULT'
report.update(mode='native-wally-final-'+a.case,
 fixture='temporary native battle fixture; original SAV, PC and existing dex records preserved',
 native_story_not_entire_regions=True,stages=[])
source_storage=bytes(source.blocks['storage'][:off('storage')])
def dex_bytes(b):
 n=off('dex.seen')-off('dex.owned')
 assert 49<=n<=64
 return [bytes(b.sb2[off('sb2.pokedex')+off('dex.owned'):off('sb2.pokedex')+off('dex.owned')+n]),
  bytes(b.sb2[off('sb2.pokedex')+off('dex.seen'):off('sb2.pokedex')+off('dex.seen')+n]),
  bytes(b.sb1[off('sb1.seen1'):off('sb1.seen1')+n]),bytes(b.sb1[off('sb1.seen2'):off('sb1.seen2')+n])]
original_dex=dex_bytes(source)
def invariants(allow_seen=False):
 assert e.read(e.ptr('gPokemonStoragePtr'),off('storage'))==source_storage,'full PC storage changed'
 assert pc(e)==source_pc
 count=e.u8(syms['gPlayerPartyCount']);assert count==1
 party_valid(e.read(syms['gPlayerParty'],600),count)
 current=dex_bytes(blocks(e))
 assert current[0]==original_dex[0],'owned dex records changed'
 if allow_seen:
  for before,after in zip(original_dex[1:],current[1:]):
   assert all((a&b)==a for a,b in zip(before,after)),'old seen dex record lost'
 else:assert current==original_dex,'nonbattle dialogue changed dex'
 assert blocks(e).trainer_beaten(PREV)==previous_defeated,'Mauville history changed'
 assert {f:blocks(e).flag(f) for f in flags}==initial_flags,'Wally dialogue changed region/badge flags'
def await_native(pred,limit=2500,key=None):
 for i in range(limit):
  if pred():return
  safe(e)
  if key and i%8==0:e.press(key,hold=1,after=1)
  else:e.run(1)
 raise AssertionError(('Wally native timeout',a.case,e.location(),hex(e.callback2())))
def check_dialogue(label):
 addr=syms[M+'_Text_TYWally'+label]
 expected=r.at(addr,10);got=e.read(syms['gStringVar4'],10)
 assert got==expected,('wrong Wally dialogue branch',label,got.hex(),expected.hex())
 report['dialogue_branch']=label
 photo(e,'wally-'+label)
def begin_dialogue():
 initial=e.location();assert loc_is(e,M) and initial[2:]==(15,39)
 # The adjacent Wally blocks the step but turns the player east.
 e.press('RIGHT',hold=1,after=20);assert e.location()==initial
 e.press('A',hold=3,after=20)
def answer_challenge(yes):
 await_native(lambda:active_task(e,'Task_YesNoMenu_HandleInput'),2500,'A')
 check_dialogue('Remember' if a.case=='remember' else 'FirstMeeting')
 e.run(10);e.press('UP' if yes else 'DOWN',hold=2,after=10)
 e.press('A',hold=2,after=20)
def check_original_enemy():
 mash_until(e,e.in_battle,400);assert menu(e)
 assert e.u16(syms['gTrainerBattleOpponent_A'])==const(T)
 data=e.read(syms['gEnemyParty'],600)
 expected=[
 ('SPECIES_ALTARIA',44,['MOVE_AERIAL_ACE','MOVE_SAFEGUARD','MOVE_DRAGON_BREATH','MOVE_DRAGON_DANCE']),
 ('SPECIES_DELCATTY',43,['MOVE_SING','MOVE_ASSIST','MOVE_CHARM','MOVE_FAINT_ATTACK']),
 ('SPECIES_ROSELIA',44,['MOVE_MAGICAL_LEAF','MOVE_LEECH_SEED','MOVE_GIGA_DRAIN','MOVE_TOXIC']),
 ('SPECIES_MAGNETON',41,['MOVE_SUPERSONIC','MOVE_THUNDERBOLT','MOVE_TRI_ATTACK','MOVE_SCREECH']),
 ('SPECIES_GARDEVOIR',45,['MOVE_DOUBLE_TEAM','MOVE_CALM_MIND','MOVE_PSYCHIC','MOVE_FUTURE_SIGHT'])]
 for i,(species,level,moves) in enumerate(expected):
  mon=Mon(bytearray(data),i*100)
  assert mon.species()==const(species) and data[i*100+84]==level,(i,species,level)
  assert list(struct.unpack_from('<4H',mon.subs()['A']))==[const(name) for name in moves],('original enemy moves changed',i)
 assert Mon(bytearray(data),500).species()==0
 report['original_emerald_vr1_enemy_team_verified']=True
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-wally-final-qa-') as td:
  s=SaveFile(str(sav));s.fast_battles();s.keep_party(1)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_var('VAR_REPEL_STEP_COUNT',250);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  s.set_flag('FLAG_SYS_CRUISE_MODE',False)
  s.set_flag(B,a.case!='early');s.set_flag(L,a.case=='legacy')
  previous_defeated=a.case=='remember'
  s.set_trainer_beaten(PREV,previous_defeated);s.set_trainer_beaten(T,a.case=='done')
  s.warp(M,15,39)
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
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  initial_flags={f:blocks(e).flag(f) for f in flags}
  report['initial_native_var_result']=e.u16(syms['gSpecialVar_Result'])
  assert loc_is(e,M) and e.location()[2:]==(15,39)
  invariants();begin_dialogue()
  if a.case in ('first','remember','loss'):
   answer_challenge(True);check_original_enemy();native_battle(e,T,5)
   if a.loss:
    assert not loc_is(e,M),'native blackout did not leave Victory Road'
    assert not blocks(e).trainer_beaten(T)
    invariants(True);native_save_reopen(e,source_pc);invariants(True)
    assert not blocks(e).trainer_beaten(T)
    report['native_loss_not_completed']=True
   else:
    assert loc_is(e,M) and blocks(e).trainer_beaten(T)
    invariants(True);native_save_reopen(e,source_pc);invariants(True)
    begin_dialogue();quiet_finish(e);check_dialogue('Post')
    assert blocks(e).trainer_beaten(T)
    report['native_win_saved_without_repeat']=True
  elif a.case=='decline':
   answer_challenge(False);quiet_finish(e);check_dialogue('Declined')
   assert not blocks(e).trainer_beaten(T)
   invariants();native_save_reopen(e,source_pc);invariants()
   begin_dialogue()
   await_native(lambda:active_task(e,'Task_YesNoMenu_HandleInput'),2500,'A')
   e.run(10);e.press('DOWN',hold=2,after=10);e.press('A',hold=2,after=20)
   quiet_finish(e);assert not blocks(e).trainer_beaten(T)
   report['native_decline_then_reoffer']=True
  else:
   quiet_finish(e);check_dialogue({'early':'Early','done':'Post','legacy':'Legacy'}[a.case])
   assert blocks(e).trainer_beaten(T)==(a.case=='done')
   invariants();native_save_reopen(e,source_pc);invariants()
   begin_dialogue();quiet_finish(e)
   assert blocks(e).trainer_beaten(T)==(a.case=='done')
   report['native_nonbattle_branch_saved']=True
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
