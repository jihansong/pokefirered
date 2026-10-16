#!/usr/bin/env python3
"""Native duplicate-HM08/TM49 rewards, failure retries and battery save QA."""
from pathlib import Path
head=Path('tools/qa/hoenn_weather_space_native_qa.py').read_text().split('e=None\ntry:',1)[0]
cases=['absent','bag','pc','bag-full','pc-full','done-bag','done-pc','done-missing']
head=head.replace("choices=['weather-party','weather-pc','space']","choices="+repr(cases))
exec(compile(head,'tools/qa/hoenn_weather_space_native_qa.py','exec'))
assert not a.loss
report.update(mode='hm08-alternate-'+a.case,stages=[],native_saves=[])
def pcitems(b):
 start=off('sb1.pcItems')
 return bytes(b.sb1[start:start+const('PC_ITEMS_COUNT')*4])
def pcquantity(b,item):
 return sum(n for i,n in struct.iter_unpack('<HH',pcitems(b)) if i==const(item))
def verify(expected_flag,hm,tm):
 b=blocks(e)
 assert b.flag(HF)==expected_flag,(a.case,'receipt flag',b.flag(HF),expected_flag)
 assert b.item_count('ITEM_HM08')==hm,(a.case,'HM quantity',b.item_count('ITEM_HM08'),hm)
 assert b.item_count('ITEM_TM49')==tm,(a.case,'TM quantity',b.item_count('ITEM_TM49'),tm)
 assert pcitems(b)==expected_items,'PC item storage changed'
 assert pc(e)==source_pc,'stored Pokemon changed'
 assert e.read(syms['gPlayerParty'],party_count*100)==expected_party,'party or learned moves changed'
def claim():
 talk(e,'LEFT');quiet_finish(e)
def saved(expected_flag,hm,tm):
 native_save_reopen(e,source_pc)
 report['native_saves'].append(report['native_save'])
 verify(expected_flag,hm,tm)
e=None
try:
 with tempfile.TemporaryDirectory(prefix='hm08-alternate-qa-') as td:
  s=SaveFile(str(sav));s.fast_battles()
  for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  done=a.case.startswith('done-');in_pc=a.case in ('pc','pc-full','done-pc')
  in_bag=a.case in ('bag','bag-full','done-bag');full=a.case.endswith('-full')
  s.warp(S,15,6);s.set_flag(SF,True);s.set_flag(HF,done)
  s.set_item('ITEM_HM08',1 if in_bag else 0)
  s.set_item('ITEM_TM49',999 if full else 7)
  start=off('sb1.pcItems');capacity=const('PC_ITEMS_COUNT')
  for i in range(capacity):
   o=start+i*4
   if struct.unpack_from('<H',s.sb1,o)[0]==const('ITEM_HM08'):
    struct.pack_into('<HH',s.sb1,o,0,0)
  if in_pc:
   slots=[start+i*4 for i in range(capacity) if struct.unpack_from('<H',s.sb1,start+i*4)[0]==0]
   assert slots,'temporary PC-item fixture has no free slot'
   struct.pack_into('<HH',s.sb1,slots[0],const('ITEM_HM08'),1)
  expected_items=pcitems(s);party_count=s.party_count()
  expected_party=bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+party_count*100])
  assert bytes(s.blocks['storage'][boxoff:boxoff+cs])==source_pc
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  assert pcquantity(blocks(e),'ITEM_HM08')==int(in_pc)
  claim()
  if full:
   verify(False,int(in_bag),999)
   photo(e,'full-no-receipt')
   saved(False,int(in_bag),999)
   claim();verify(False,int(in_bag),999)
   # Make a separate retry fixture from the actual native failed-gift save.
   # Only its TM stack is lowered; no emulator RAM or original SAV is changed.
   retry=SaveFile(str(out/'qa-only-native-save.sav'));retry.set_item('ITEM_TM49',998)
   retry_path=Path(td)/'retry.sav';retry.save(str(retry_path));check_sectors(SaveFile(str(retry_path)))
   e.close();e=None
   e=ReadOnlyEmu(str(rom),str(retry_path),sym='');e.syms=syms;e.boot_continue();settle(e)
   claim();verify(True,int(in_bag),999)
   report['retry_from_native_failed_save']=True
   final_hm,final_tm=int(in_bag),999
  else:
   final_hm=1 if a.case=='absent' else int(in_bag)
   final_tm=8 if (in_bag or in_pc) and not done else 7
   verify(True,final_hm,final_tm)
  photo(e,'reward-final')
  claim();verify(True,final_hm,final_tm)
  saved(True,final_hm,final_tm)
  claim();verify(True,final_hm,final_tm)
  report.update(pass_=True,bag_hm08=final_hm,bag_tm49=final_tm,pc_hm08=int(in_pc),
   party_and_learned_moves_preserved=True,original_pc_pokemon_preserved=True,
   repeat_and_cold_reload_no_duplicate=True)
  report['pass']=True
except Exception as ex:
 report['error']=repr(ex);report['traceback']=traceback.format_exc()
 if e and e.h:photo(e,'failure')
finally:
 if e:e.close()
 after={p:sha(Path(p).read_bytes()) for p in before}
 report['original_saves_unchanged']=before==after
 if before!=after:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='traceback'}),flush=True)
sys.exit(0 if report['pass'] else 1)
