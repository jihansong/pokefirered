#!/usr/bin/env python3
"""Weather/Space native battles, gift and save QA; temporary SAV only."""
from pathlib import Path
helper=Path('tools/qa/hoenn_gauntlet_save_qa.py').read_text()
prefix=helper.split('tmp=None; e=None\ntry:',1)[0]
assert prefix!=helper
prefix=prefix.replace("P.add_argument('--loss',", "P.add_argument('--case',choices=['weather-party','weather-pc','space'],required=True)\nP.add_argument('--loss',",1)
# Include assembler globals even if objdump omits its type column.
prefix=prefix.replace('len(p)>=6','len(p)>=5')
exec(compile(prefix,str(Path('tools/qa/hoenn_gauntlet_save_qa.py')),'exec'))
report.update(mode=a.case+('-loss' if a.loss else '-wins'),stages=[])
W='Route119_WeatherInstitute_2F'; S='MossdeepCity_SpaceCenter_2F'
WF='FLAG_HOENN_WEATHER_RESCUED'; CF='FLAG_HOENN_GOT_WEATHER_CASTFORM'
SF='FLAG_HOENN_SPACE_CENTER_SECURED'; HF='FLAG_HOENN_GOT_HM08_FROM_STEVEN'
WT='TRAINER_HOENN_SHELLY_WEATHER_INSTITUTE'
TT='TRAINER_HOENN_TABITHA_SPACE_CENTER'; MT='TRAINER_HOENN_MAXIE_SPACE_CENTER'
flags=[WF,CF,SF,HF]
def active_task(e,name):
 want=sets.get(name,set())
 return any(e.u8(syms['gTasks']+i*40+4) and
  (e.u32(syms['gTasks']+i*40)&~1) in want for i in range(16))
def native_battle(e,trainer,enemy_count):
 mash_until(e,e.in_battle,400)
 assert e.u16(syms['gTrainerBattleOpponent_A'])==const(trainer)
 assert menu(e),'native battle did not reach action menu'
 enemy=e.read(syms['gEnemyParty'],600)
 species=[Mon(bytearray(enemy),i*100).species() for i in range(6)]
 assert sum(bool(x) for x in species)==enemy_count,(trainer,species)
 row={'trainer':trainer,'enemy_species':species,'start_frame':e.frame(),'moves':[]}
 photo(e,trainer+'-start')
 for turn in range(90):
  if not menu(e):break
  row['moves'].append(fight_one_turn(e,a.loss))
 else:raise AssertionError('more than 90 selected turns')
 settle(e); row['end_frame']=e.frame()
 assert blocks(e).trainer_beaten(trainer)==(not a.loss)
 assert pc(e)==source_pc,'battle changed PC'
 photo(e,trainer+'-result')
 report['stages'].append(row)
 print(json.dumps({'trainer':trainer,'turns':len(row['moves']),'native_outcome':'loss' if a.loss else 'win'}),flush=True)
def talk(e,direction):
 e.press(direction,hold=2,after=12)
 e.press('A',hold=3,after=20)
def quiet_finish(e,key='A'):
 for _ in range(500):
  assert not e.in_battle(),'repeat dialogue started another battle'
  if e.field_idle():return
  safe(e);e.press(key,hold=2,after=14)
 raise AssertionError('dialogue did not finish')
def choose_offer(e):
 for _ in range(1000):
  if active_task(e,'Task_YesNoMenu_HandleInput'):
   e.run(10);e.press('UP',hold=2,after=5);e.press('A',hold=2,after=5);return
  safe(e);e.press('A',hold=1,after=5)
 raise AssertionError('gift yes/no menu missing')
def gift(e):
 before_party=e.u8(syms['gPlayerPartyCount']); before_pc=pc(e)
 go(e,18,7);talk(e,'UP');choose_offer(e)
 # B advances the gift text and declines the native nickname prompt.
 quiet_finish(e,'B')
 assert blocks(e).flag(CF)
 after_party=e.u8(syms['gPlayerPartyCount']);after_pc=pc(e)
 if a.case=='weather-party':
  assert before_party==1 and after_party==2 and after_pc==before_pc
  mon=Mon(bytearray(e.read(syms['gPlayerParty'],600)),100)
  assert mon.species()==const('SPECIES_CASTFORM')
  assert mon.blk[mon.o+84]==25
  delta=[]
 else:
  assert before_party==after_party==6
  delta=[i for i in range(420) if before_pc[i*80:(i+1)*80]!=after_pc[i*80:(i+1)*80]]
  assert len(delta)==1,delta
  i=delta[0]
  old=Mon(bytearray(before_pc),i*80);new=Mon(bytearray(after_pc),i*80)
  assert old.species()==0 and new.species()==const('SPECIES_CASTFORM')
  assert after_pc[51*80:52*80]==source_pc[51*80:52*80],'existing Bad Egg changed'
 report['gift']={'party_before':before_party,'party_after':after_party,'changed_pc_slots':delta}
 repeat_party=e.read(syms['gPlayerParty'],600);repeat_pc=pc(e)
 talk(e,'UP');quiet_finish(e)
 assert e.read(syms['gPlayerParty'],600)==repeat_party and pc(e)==repeat_pc,'gift duplicated'
 return after_pc
def native_save_reopen(e,expected_pc):
 b=blocks(e);expected_flags={f:b.flag(f) for f in flags}
 expected_trainers={t:b.trainer_beaten(t) for t in [WT,TT,MT]}
 expected_dex=digest_dex(b);count=e.u8(syms['gPlayerPartyCount'])
 party=e.read(syms['gPlayerParty'],count*100);party_valid(party,count)
 hm=b.item_count('ITEM_HM08');counter=e.u32(syms['gSaveCounter'])
 e.press('START',hold=3,after=60)
 n=e.u8(syms['sNumStartMenuItems']);order=list(e.read(syms['sStartMenuOrder'],n))
 assert 4 in order,('native SAVE option missing',order)
 target=order.index(4)
 for _ in range(n+1):
  if e.u8(syms['sStartMenuCursorPos'])==target:break
  e.press('DOWN',hold=3,after=12)
 assert e.u8(syms['sStartMenuCursorPos'])==target
 e.press('A',hold=3,after=20)
 for _ in range(900):
  if e.field_idle() and e.u32(syms['gSaveCounter'])>counter:break
  safe(e);e.press('A',hold=2,after=14)
 else:raise AssertionError('native SAVE never completed')
 assert e.u16(syms['gSaveAttemptStatus'])==1
 assert Path(e.sav_path).resolve()!=sav
 e.run(30);e.lib.qa_close(e.h);e.h=None
 saved=SaveFile(e.sav_path);check_sectors(saved)
 assert saved.counter>counter
 assert {f:saved.flag(f) for f in flags}==expected_flags
 assert {t:saved.trainer_beaten(t) for t in [WT,TT,MT]}==expected_trainers
 assert bytes(saved.blocks['storage'][boxoff:boxoff+cs])==expected_pc
 po=off('sb1.playerParty')
 assert bytes(saved.sb1[po:po+count*100])==party
 assert digest_dex(saved)==expected_dex and saved.item_count('ITEM_HM08')==hm
 written=Path(e.sav_path).read_bytes();(out/'qa-only-native-save.sav').write_bytes(written)
 e.h=e.lib.qa_open(str(rom).encode(),str(e.sav_path).encode());assert e.h
 e.boot_continue();settle(e);b=blocks(e)
 assert {f:b.flag(f) for f in flags}==expected_flags
 assert {t:b.trainer_beaten(t) for t in [WT,TT,MT]}==expected_trainers
 assert pc(e)==expected_pc and e.read(syms['gPlayerParty'],count*100)==party
 assert digest_dex(b)==expected_dex and b.item_count('ITEM_HM08')==hm
 report['native_save']={'counter_before':counter,'counter_after':saved.counter,'valid_sectors':14,
  'cold_reopen':True,'flags':expected_flags,'trainers':expected_trainers,'hm08':hm,'sha256':sha(written)}
 photo(e,'native-save-reopened')
e=None
try:
 with tempfile.TemporaryDirectory(prefix='weather-space-qa-') as td:
  s=SaveFile(str(sav));s.fast_battles()
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  for f in flags:s.set_flag(f,False)
  for t in [WT,TT,MT]:s.set_trainer_beaten(t,False)
  s.set_flag('FLAG_HOENN_BADGE07_GET',True);s.set_item('ITEM_HM08',0)
  if a.case=='space':
   s.set_flag(WF,True);s.set_trainer_beaten(WT,True);s.warp(S,14,7)
  else:s.warp(W,17,7)
  if a.case=='weather-pc' and not a.loss:
   while s.party_count()<6:s.copy_box_mon_to_party(0,s.party_count(),rom=r)
  else:s.keep_party(1)
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  moves=['MOVE_SPLASH'] if a.loss else ['MOVE_AERIAL_ACE','MOVE_THUNDERBOLT','MOVE_ICE_BEAM','MOVE_SHADOW_BALL']
  for i in range(s.party_count()):
   m=s.party_mon(i);m.set_otid(owner);m.set_starter_bit(False);m.set_snagged(False)
   m.set_species(const('SPECIES_MAGIKARP' if a.loss else 'SPECIES_MEWTWO'),rom=r)
   subs=m.subs();subs['E'][:6]=bytes(6);subs['G'][8]=0 if a.loss else 255;subs['A'][:]=bytes(12)
   for j,name in enumerate(moves):
    mid=const(name);struct.pack_into('<H',subs['A'],2*j,mid)
    raw=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))
    subs['A'][8+j]=raw[4] if a.loss else raw[4]*8//5
   struct.pack_into('<I',subs['M'],4,struct.unpack_from('<I',subs['M'],4)[0]&~(1<<30))
   m.put_subs(subs);m.blk[m.o+19]=(m.blk[m.o+19]&~5)|2
   m.set_held(const('ITEM_NONE' if a.loss else 'ITEM_LEFTOVERS'))
   m.make_strong(1 if a.loss else 100,rom=r)
  assert bytes(s.blocks['storage'][boxoff:boxoff+cs])==source_pc
  tmp=Path(td)/'fixture.sav';s.save(str(tmp));check_sectors(SaveFile(str(tmp)))
  e=ReadOnlyEmu(str(rom),str(tmp),sym='');e.syms=syms;e.boot_continue();settle(e)
  kanto=[blocks(e).flag('FLAG_BADGE%02d_GET'%i) for i in range(1,9)]
  expected_pc=source_pc
  if a.case.startswith('weather'):
   assert loc_is(e,W);talk(e,'UP');native_battle(e,WT,2)
   if a.loss:
    assert not loc_is(e,W) and not blocks(e).flag(WF) and not blocks(e).flag(CF)
   else:
    assert loc_is(e,W) and blocks(e).flag(WF) and not blocks(e).flag(CF)
    expected_pc=gift(e)
  else:
   assert loc_is(e,S);talk(e,'LEFT');native_battle(e,TT,4)
   if a.loss:
    assert not loc_is(e,S) and not blocks(e).flag(SF) and not blocks(e).flag(HF)
   else:
    assert not blocks(e).flag(SF);talk(e,'LEFT');quiet_finish(e)
    talk(e,'DOWN');native_battle(e,MT,3)
    assert blocks(e).flag(SF) and not blocks(e).flag(HF)
    talk(e,'UP');quiet_finish(e)
    assert blocks(e).flag(HF) and blocks(e).item_count('ITEM_HM08')==1
    talk(e,'UP');quiet_finish(e)
    assert blocks(e).item_count('ITEM_HM08')==1
  assert [blocks(e).flag('FLAG_BADGE%02d_GET'%i) for i in range(1,9)]==kanto
  assert pc(e)==expected_pc
  native_save_reopen(e,expected_pc)
  report['pass']=True
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

