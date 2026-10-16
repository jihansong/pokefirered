#!/usr/bin/env python3
"""Focused native checkpoint QA; copied saves only, no RAM writes."""
from pathlib import Path
helper=Path('tools/qa/hoenn_gauntlet_save_qa.py').read_text()
marker='tmp=None; e=None\ntry:'
assert helper.count(marker)==1
exec(compile(helper.split(marker)[0],'<gauntlet-helpers>','exec'),globals())
gd.FIELDS.update({'sb1.lastHealLocation':('SaveBlock1','lastHealLocation')})
gd._OFFSETS=None
healoff=off('sb1.lastHealLocation')
report['mode']='native_checkpoint_regression'
report['fixture']='two native center transitions and genuine Sidney losses; HOF precondition fixture does not repeat five wins'
report['checkpoints']=[]
city=map_info('EverGrandeCity')
def point(e):
 data=blocks(e).sb1[healoff:healoff+8]
 group,num,warp_id,pad,x,y=struct.unpack('<bbBBhh',data)
 return (group,num,x,y)
def clean(s):
 s.fast_battles()
 for j in range(const('QUEST_LOG_SCENE_COUNT')):
  s.sb1[off('sb1.questLog')+j*off('questlogscene')]=0
 for f in badges:s.set_flag(f,True)
 return s
def start(s,path):
 s.save(str(path));check_sectors(SaveFile(str(path)))
 em=ReadOnlyEmu(str(rom),str(path),sym='');em.syms=syms;em.boot_continue();settle(em)
 return em
def weak(s):
 s.keep_party(1)
 m=s.party_mon(0)
 owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
 m.set_otid(owner);m.set_starter_bit(False);m.set_snagged(False)
 m.set_species(const('SPECIES_MAGIKARP'),rom=r)
 sub=m.subs();sub['E'][:6]=bytes(6);sub['A'][:]=bytes(12)
 struct.pack_into('<H',sub['A'],0,const('MOVE_SPLASH'));sub['A'][8]=40
 sub['G'][8]=0
 struct.pack_into('<I',sub['M'],4,struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30))
 m.put_subs(sub);m.blk[m.o+19]=(m.blk[m.o+19]&~5)|2
 m.set_held(const('ITEM_NONE'));m.make_strong(1,rom=r)
 return s
e=None
try:
 with tempfile.TemporaryDirectory(prefix='hoenn-checkpoint-') as td:
  td=Path(td)
  for name,center,xy,healxy,reset in [
   ('south','EverGrandeCity_PokemonCenter_1F',(7,4),(27,49),False),
   ('north',lobby,(3,4),(18,6),True)]:
   s=clean(SaveFile(str(sav)))
   s.set_flag(cleared,True);s.set_var(progress,7)
   for t in trainers:s.set_trainer_beaten(t,True)
   s.warp(center,*xy);e=start(s,td/(name+'-center.sav'))
   expected=(city['group'],city['num'],*healxy)
   assert point(e)==expected,(name,'native checkpoint',point(e),expected)
   b=blocks(e)
   assert b.flag(cleared)
   if reset:
    assert b.var(progress)==0 and all(not b.trainer_beaten(t) for t in trainers)
   assert pc(e)==source_pc
   checkpoint=bytes(b.sb1[healoff:healoff+8])
   photo(e,name+'-center');e.close();e=None
   # Pre-boot battle fixture inherits the checkpoint read from a real center entry.
   s=weak(clean(SaveFile(str(sav))))
   s.sb1[healoff:healoff+8]=checkpoint
   s.set_flag(cleared,True);s.set_var(progress,1)
   for t in trainers:s.set_trainer_beaten(t,False)
   s.warp(rooms[0],6,6);e=start(s,td/(name+'-loss.sav'))
   assert point(e)==expected
   facing_up(e);e.press('A',hold=3,after=20)
   mash_until(e,e.in_battle,300);assert menu(e)
   assert e.u16(e.sym('gTrainerBattleOpponent_A'))==const(trainers[0])
   raw=e.read(e.sym('gEnemyParty'),600)
   assert sum(Mon(raw,j*100).species()!=const('SPECIES_NONE') for j in range(6))==5
   turns=0
   for j in range(30):
    if not menu(e):break
    fight_one_turn(e,True);turns+=1
   else:raise AssertionError('loss fixture did not finish')
   settle(e);b=blocks(e)
   assert loc_is(e,center) and e.location()[2:]==xy,(name,'whiteout destination',e.location())
   assert point(e)==expected and b.flag(cleared)
   assert not b.trainer_beaten(trainers[0])
   if reset:assert b.var(progress)==0 and all(not b.trainer_beaten(t) for t in trainers)
   party=e.read(e.sym('gPlayerParty'),100)
   assert struct.unpack_from('<H',party,86)[0]==struct.unpack_from('<H',party,88)[0]>0
   assert pc(e)==source_pc
   photo(e,name+'-native-blackout')
   report['checkpoints'].append({'name':name,'checkpoint':expected,'respawn':e.location(),'native_loss_turns':turns,'permanent_clear_preserved':True})
   e.close();e=None
  # Checkpoint-only HOF fixture: genuine native HOF save and reopen, not a five-win claim.
  s=clean(SaveFile(str(sav)))
  for t in trainers:s.set_trainer_beaten(t,True)
  s.set_var(progress,6);s.set_flag(cleared,False);s.warp('EverGrandeCity_HallOfFame',7,10)
  path=td/'hof.sav';s.save(str(path));counter=s.counter
  e=ReadOnlyEmu(str(rom),str(path),sym='');e.syms=syms
  e.boot_continue(leave_menu_only=True)
  mash_until(e,lambda:(e.callback2()&~1)==syms['CB2_Credits'],1200)
  e.run(60);b=blocks(e)
  assert e.ptr('sCreditsMgr') and e.u8(e.ptr('sCreditsMgr')+16)==2
  assert b.flag(cleared) and b.var(progress)==7 and all(b.trainer_beaten(t) for t in trainers)
  live_count=e.u8(e.sym('gPlayerPartyCount'));live_party=e.read(e.sym('gPlayerParty'),live_count*100)
  party_valid(live_party,live_count);live_dex=digest_dex(b)
  assert pc(e)==source_pc
  e.run(30);e.lib.qa_close(e.h);e.h=None
  written=Path(e.sav_path).read_bytes();flushed=SaveFile(e.sav_path);check_sectors(flushed)
  assert flushed.counter>counter and flushed.flag(cleared) and flushed.var(progress)==7
  assert all(flushed.trainer_beaten(t) for t in trainers)
  assert bytes(flushed.blocks['storage'][boxoff:boxoff+cs])==source_pc
  po=off('sb1.playerParty')
  assert bytes(flushed.sb1[po:po+len(live_party)])==live_party and digest_dex(flushed)==live_dex
  (out/'qa-only-native-hof-checkpoint.sav').write_bytes(written)
  report['native_hof_save']={'counter_before':counter,'counter_after':flushed.counter,'valid_sectors':14,'save_sha256':sha(written)}
  e.h=e.lib.qa_open(str(rom).encode(),str(e.sav_path).encode());assert e.h
  e.boot_continue();settle(e);b=blocks(e)
  assert loc_is(e,'EverGrandeCity') and e.location()[2:]==(18,6),('HOF continue',e.location())
  assert b.flag(cleared) and b.var(progress)==7 and all(b.trainer_beaten(t) for t in trainers)
  assert pc(e)==source_pc and e.read(e.sym('gPlayerParty'),len(live_party))==live_party and digest_dex(b)==live_dex
  photo(e,'hof-reopened-outside')
  e.walk('UP');mash_until(e,lambda:loc_is(e,lobby) and e.field_idle(),400);b=blocks(e)
  assert b.flag(cleared) and b.var(progress)==0 and all(not b.trainer_beaten(t) for t in trainers)
  assert point(e)==(city['group'],city['num'],18,6)
  assert pc(e)==source_pc and e.read(e.sym('gPlayerParty'),len(live_party))==live_party and digest_dex(b)==live_dex
  photo(e,'hof-reentered-lobby')
  report['native_hof_continue_and_rematch_reset']=True;report['pass']=True
except Exception as ex:
 report['error']=repr(ex);report['traceback']=traceback.format_exc()
 if e and e.h:
  report['failure_location']=e.location();photo(e,'failure')
finally:
 if e:e.close()
 report['original_saves_unchanged']=before=={p:sha(Path(p).read_bytes()) for p in before}
 if not report['original_saves_unchanged']:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='traceback'}),flush=True)
sys.exit(0 if report['pass'] else 1)
