from pathlib import Path
import hashlib,json,traceback,sys
mode=sys.argv.pop(1);assert mode in ('baseline','fixed')
q=Path('tools/qa/native_misty_basic_qa.py').read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<verified-native-definitions>','exec'))
L='FLAG_JOHTO_MET_LAB_ASSISTANT';G='FLAG_JOHTO_MET_CHERRYGROVE_GUIDE';MR='FLAG_JOHTO_MR_POKEMON_BRIEFED';D='FLAG_JOHTO_ELM_REPORT_DELIVERED';C='FLAG_GOT_CYNDAQUIL_FROM_AIDE'
protected={p:digest(p.read_bytes()) for p in Path('saves').rglob('*.sav')}
checks=[];status={'all_pass':False,'mode':mode,'arbitrary_RAM_writes':0,'direct_script_calls':0,'native_inputs_only':True,'scope':'Separate immutable temporary preboot NPC fixtures; not a continuous full campaign walk'}
def fixture(tag,mapname,x,y,lab=False,done=False):
 f=out/(tag+'-fixture.sav');assert not f.exists();s=SaveFile(str(sav))
 for flagname,value in [(L,lab),(G,False),(MR,False),(D,done),(C,False),('FLAG_SYS_GAME_CLEAR',True)]:s.set_flag(flagname,value)
 for flagname in K:s.set_flag(flagname,True)
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 s.sb2[off('sb2.specialSaveWarpFlags')]&=~1;s.warp(mapname,x,y);s.save(str(f));return f
def opened(e,local):
 before=e.location();e.press('UP',hold=1,after=20);assert e.location()==before;e.press('A',hold=3,after=40)
 assert e.u16(e.sym('gSpecialVar_LastTalked'))==local
def assert_text(e,label):
 expected=r.at(syms[label],1024).split(b'\xff',1)[0]
 actual=e.read(syms['gStringVar4'],1024).split(b'\xff',1)[0]
 assert actual==expected,('Wrong native expanded text',label,actual.hex()[:80],expected.hex()[:80])
 return digest(actual)
def finish(e):
 for _ in range(600):
  safe(e);assert not e.in_battle()
  if e.field_idle():return
  e.press('A',hold=2,after=10)
 raise AssertionError('NPC dialog did not release')
def yesno(e):
 return any(e.u8(e.sym('gTasks')+40*i+4) and (e.u32(e.sym('gTasks')+40*i)&~1)==(syms['Task_YesNoMenu_HandleInput']&~1) for i in range(16))
try:
 f=fixture('professor-first','NewBarkTown_ElmsLab',7,9)
 with ReadOnlyEmu(str(rom),str(f),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);before=record(e);assert not blocks(e).flag(L)
  opened(e,2);h=assert_text(e,'NewBarkTown_ElmsLab_Text_ProfessorElm');e.shot(str(out/'professor-first-dialogue.png'),scale=3);finish(e)
  labafter=blocks(e).flag(L);assert labafter==(mode=='fixed');assert not blocks(e).flag(C) and not blocks(e).flag(D);same_records(e,before)
  checks.append({'case':'professor_first','lab_visit_after':labafter,'gift_received_after':False,'report_delivered_after':False,'native_text_sha256':h,'party_PC_Dex_preserved':True})
 f=fixture('guide-after-professor','CherrygroveCity',31,15,lab=labafter)
 with ReadOnlyEmu(str(rom),str(f),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);before=record(e);opened(e,1)
  h=assert_text(e,'CherrygroveCity_Text_GuideRequest' if mode=='fixed' else 'CherrygroveCity_Text_GuideBeforeLab');e.shot(str(out/'guide-after-professor-dialogue.png'),scale=3);finish(e)
  assert blocks(e).flag(G)==(mode=='fixed');same_records(e,before)
  checks.append({'case':'guide_after_professor_separate_fixture','guide_registered':blocks(e).flag(G),'native_text_sha256':h,'party_PC_Dex_preserved':True})
 for done in [False,True]:
  tag='visitor-report-'+str(int(done));f=fixture(tag,'SproutTower_1F',9,13,done=done)
  with ReadOnlyEmu(str(rom),str(f),sym='') as e:
   e.syms=syms;e.boot_continue();settle(e);before=record(e);opened(e,2)
   label='SproutTower_1F_Text_VisitorBeforeElmReport' if mode=='fixed' and not done else 'SproutTower_1F_Text_Visitor'
   h=assert_text(e,label);e.shot(str(out/(tag+'-dialogue.png')),scale=3);finish(e)
   assert blocks(e).flag(D)==done;same_records(e,before)
   checks.append({'case':tag,'native_text_label':label,'report_flag_unchanged':True,'native_text_sha256':h,'party_PC_Dex_preserved':True})
 if mode=='fixed':
  f=fixture('assistant-gift-still-offered','NewBarkTown_ElmsLab',3,7,lab=True)
  with ReadOnlyEmu(str(rom),str(f),sym='') as e:
   e.syms=syms;e.boot_continue();settle(e);before=record(e);opened(e,1)
   for _ in range(360):
    safe(e)
    if yesno(e):break
    e.press('A',hold=2,after=10)
   else:raise AssertionError('Gift YES/NO did not appear')
   e.run(40);e.shot(str(out/'assistant-gift-offer.png'),scale=3);e.press('B',hold=3,after=25);finish(e)
   assert blocks(e).flag(L) and not blocks(e).flag(C);same_records(e,before)
   checks.append({'case':'assistant_gift_still_offered_declined','actual_native_yesno':True,'gift_flag_not_set':True,'party_PC_Dex_preserved':True})
 status['all_pass']=len(checks)==(5 if mode=='fixed' else 4)
except Exception as ex:status.update(error=repr(ex),traceback=traceback.format_exc())
finally:
 status.update(checks=checks,rom_sha256=digest(rom.read_bytes()),original_inputs_unchanged=all(digest(p.read_bytes())==h for p,h in originals.items()),original_all_SAVs_unchanged=all(digest(p.read_bytes())==h for p,h in protected.items()))
 (out/'validation.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status),flush=True)
