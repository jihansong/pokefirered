from pathlib import Path
import hashlib,json,traceback
q=Path('tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<verified-native-definitions>','exec'))
mr='FLAG_JOHTO_MR_POKEMON_BRIEFED';delivered='FLAG_JOHTO_ELM_REPORT_DELIVERED'
checks=[];status={'all_pass':False,'ram_writes':0,'direct_script_calls':0}
try:
 for tag,brief,done in [('introduction',False,False),('report_delivery',True,False),('completed_report',True,True)]:
  f=out/(tag+'-fixture.sav');assert not f.exists();s=SaveFile(str(sav))
  s.set_flag(mr,brief);s.set_flag(delivered,done);s.set_flag('FLAG_SYS_GAME_CLEAR',True)
  for flagname in K:s.set_flag(flagname,True)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.sb2[off('sb2.specialSaveWarpFlags')]&=~1;s.warp('NewBarkTown_ElmsLab',7,9);s.save(str(f))
  with ReadOnlyEmu(str(rom),str(f),sym='') as e:
   e.syms=syms;e.boot_continue();settle(e);before=record(e)
   e.press('UP',hold=1,after=20);assert e.location()[2:]==(7,9)
   e.press('A',hold=3,after=40);assert e.u16(e.sym('gSpecialVar_LastTalked'))==2
   e.shot(str(out/(tag+'-professor-name.png')),scale=3)
   for _ in range(600):
    safe(e);assert not e.in_battle()
    if e.field_idle():break
    e.press('A',hold=2,after=10)
   else:raise AssertionError('Professor dialog did not release field')
   same_records(e,before);assert blocks(e).flag(delivered)==brief
   if tag=='report_delivery':
    for repeat in range(2):
     e.press('A',hold=3,after=20);settle(e);same_records(e,before)
     assert blocks(e).flag(delivered)
   checks.append({'case':tag,'actual_professor_NPC_2':True,'report_delivered_after':blocks(e).flag(delivered),'party_PC_dex_preserved':True,'pass':True})
 status['all_pass']=len(checks)==3
except Exception as ex:status.update(error=repr(ex),traceback=traceback.format_exc())
finally:
 status.update(checks=checks,original_inputs_unchanged=all(digest(p.read_bytes())==h for p,h in originals.items()),rom_sha256=digest(rom.read_bytes()),professor_art='Temporary native scientist sprite; dedicated Elm drawing pending')
 (out/'validation.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status),flush=True)
