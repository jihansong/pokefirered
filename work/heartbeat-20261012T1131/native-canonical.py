from pathlib import Path
import hashlib,json,traceback,struct
q=Path('tools/qa/native_misty_basic_qa.py').read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<verified-readonly-definitions>','exec'))
F='FLAG_HOENN_ROUTE114_TM05_RECEIVED';TM='ITEM_TM05';J='FLAG_JOHTO_LEAGUE_CLEARED'
assert const(F)==0x1278 and const(TM)==293
protected={p:digest(p.read_bytes()) for p in Path('saves').rglob('*.sav')};main_before=digest(Path('pokemonthyl.gba').read_bytes())
assert main_before=='b46fb32bb67f89d5a48dfbfdf41ddd4977cc4a2d60dbbe6c72e1bc0281c5606d'
checks=[];status={'all_pass':False,'arbitrary_RAM_writes':0,'direct_script_calls':0,'scope':'Seven separate preboot native NPC fixtures; not continuous campaign proof'}
def msg(e,label):
 a=e.read(e.sym('gStringVar4'),1024).split(b'\xff',1)[0]
 expected=r.at(syms[label],1024).split(b'\xff',1)[0]
 return a==expected
def yesno(e):
 return any(e.u8(e.sym('gTasks')+40*i+4) and (e.u32(e.sym('gTasks')+40*i)&~1)==(syms['Task_YesNoMenu_HandleInput']&~1) for i in range(16))
def inventory(e):
 b=blocks(e);slots=set()
 for item in ['ITEM_POTION','ITEM_BICYCLE','ITEM_MASTER_BALL','ITEM_TM05','ITEM_ORAN_BERRY']:slots.update(b._slots(item))
 d={}
 for o in slots:
  iid,qty=struct.unpack_from('<HH',b.sb1,o)
  if iid:d[iid]=d.get(iid,0)+(qty^(b._key()&65535))
 return d
def fixture(tag,mapname,x,y,flags,qty=None):
 s=SaveFile(str(sav));oldparty=bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]);oldpc=bytes(s.blocks['storage'])
 for f,v in flags.items():s.set_flag(f,v)
 if qty is not None:
  assert s.item_count('ITEM_TM_CASE')>=1;s.set_item(TM,qty)
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 s.sb2[off('sb2.specialSaveWarpFlags')]&=~1;s.warp(mapname,x,y)
 assert bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])==oldparty and bytes(s.blocks['storage'])==oldpc
 f=out/(tag+'-fixture.sav');assert not f.exists();s.save(str(f));return f
def open_npc(e,face,local):
 before=e.location();e.press(face,hold=1,after=20);assert e.location()==before
 e.press('A',hold=3,after=30);assert not e.field_idle()
 assert e.u16(e.sym('gSpecialVar_LastTalked'))==local
def finish_gift(e,failed):
 sawroar=sawfail=False
 for _ in range(600):
  safe(e);assert not e.in_battle()
  sawroar|=msg(e,'Route114_Text_H5Roar');sawfail|=msg(e,'Route114_Text_H5NoRoom')
  if e.field_idle():
   assert sawfail==failed and (failed or sawroar),(failed,sawroar,sawfail)
   return {'roar_dialogue':sawroar,'no_room_dialogue':sawfail}
  e.press('A',hold=2,after=10)
 raise AssertionError('Gift script did not release')
def finish(e):
 for _ in range(600):
  safe(e)
  if e.field_idle():return
  e.press('A',hold=2,after=10)
 raise AssertionError('Dialog did not release')
try:
 for tag,qty,claimed,finalqty,finalclaim,failed in [('fresh',0,False,1,True,False),('owns_two',2,False,3,True,False),('full_stack',999,False,999,False,True),('space_ready_retry_fixture',998,False,999,True,False),('consumed_after_receipt',0,True,0,True,False)]:
  f=fixture(tag,'Route114',20,11,{F:claimed},qty)
  with ReadOnlyEmu(str(rom),str(f),sym='') as e:
   e.syms=syms;e.boot_continue();settle(e);e.run(30);before=record(e);inv=inventory(e)
   assert blocks(e).flag(F)==claimed and blocks(e).item_count(TM)==qty
   expected=dict(inv)
   if finalqty:expected[const(TM)]=finalqty
   else:expected.pop(const(TM),None)
   talks=[]
   for _ in range(2):
    open_npc(e,'LEFT',8);talks.append(finish_gift(e,failed))
    assert inventory(e)==expected and blocks(e).flag(F)==finalclaim;same_records(e,before)
   e.shot(str(out/(tag+'-after-talk.png')),scale=3);cold=flash_reload(e,'route114-'+tag)
   assert inventory(e)==expected and blocks(e).flag(F)==finalclaim;same_records(e,before)
   open_npc(e,'LEFT',8);talks.append(finish_gift(e,failed))
   assert inventory(e)==expected and blocks(e).flag(F)==finalclaim;same_records(e,before)
   e.shot(str(out/(tag+'-cold-repeat.png')),scale=3)
   row={'case':tag,'quantity':[qty,finalqty],'claim':[claimed,finalclaim],'dialogs':talks,'native_SAVE_cold':cold,'all_bag_quantities_checked':True,'party_full_PC_Dex_preserved':True,'retry_is_separate_fixture':tag=='space_ready_retry_fixture','pass':True}
   checks.append(row);print(json.dumps(row),flush=True)
 for cleared in [False,True]:
  tag='return-after-league-'+str(int(cleared));f=fixture(tag,'JohtoCherrygroveAirstrip',22,11,{J:cleared,'FLAG_JOHTO_ARRIVAL_BRIEFED':True})
  with ReadOnlyEmu(str(rom),str(f),sym='') as e:
   e.syms=syms;e.boot_continue();settle(e);e.run(30);before=record(e);inv=inventory(e);open_npc(e,'UP',1)
   if cleared:
    assert msg(e,'JohtoCherrygroveAirstrip_Text_PostLeagueResearch') and not yesno(e)
    e.shot(str(out/'post-league-research-guidance.png'),scale=3)
   for _ in range(400):
    safe(e)
    if yesno(e):break
    e.press('A',hold=2,after=10)
   else:raise AssertionError('Native return YESNO absent')
   assert msg(e,'JohtoCherrygroveAirstrip_Text_Return');e.run(40)
   if not cleared:
    e.press('B',hold=3,after=25);finish(e);assert e.location()[2:]==(22,11) and e.location()[:2]==(map_info('JohtoCherrygroveAirstrip')['group'],map_info('JohtoCherrygroveAirstrip')['num'])
   else:
    e.press('A',hold=3,after=12)
    for _ in range(2400):
     safe(e)
     if e.field_idle() and e.location()[:2]==(map_info('KantoAirport')['group'],map_info('KantoAirport')['num']):break
     e.run(1)
    else:raise AssertionError('Native airplane never reached Kanto')
    assert e.location()[2:]==(12,7),e.location()
   same_records(e,before);assert inventory(e)==inv and blocks(e).flag(J)==cleared
   e.shot(str(out/(tag+'-after.png')),scale=3)
   row={'case':tag,'first_guidance':cleared,'choice':'YES' if cleared else 'NO','native_flight':cleared,'destination':e.location(),'party_full_PC_Dex_preserved':True,'bag_quantities_preserved':True,'pass':True}
   checks.append(row);print(json.dumps(row),flush=True)
 status['all_pass']=len(checks)==7
except Exception as ex:status.update(error=repr(ex),traceback=traceback.format_exc())
finally:
 status.update(checks=checks,rom_sha256=digest(rom.read_bytes()),original_inputs_unchanged=all(digest(p.read_bytes())==v for p,v in originals.items()),all_14_original_SAVs_unchanged=all(digest(p.read_bytes())==v for p,v in protected.items()),main_ROM_unchanged=digest(Path('pokemonthyl.gba').read_bytes())==main_before)
 (out/'validation.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status),flush=True)
