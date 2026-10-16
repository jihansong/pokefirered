#!/usr/bin/env python3
"""Two permanent Hoenn NPCs share existing HMs and substitute rare TMs."""
from pathlib import Path
import hashlib,re
qa=Path('tools/qa/native_strength_rock_puzzle_qa.py');text=qa.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='ab57a60e8f4961c318c0b975863c0ac36075f3e7556f363ae508b702928a3841'
prefix=text.split('e=None\ntry:',1)[0];assert prefix!=text
cases=[who+'-'+state for who in ('cutter','smash') for state in ('fresh','bag','pc','history','done','full-retry')]
prefix,n=re.subn(r'cases=\[.*?\]\nassert head.count','cases='+repr(cases)+'\nassert head.count',prefix,count=1,flags=re.S);assert n==1
exec(compile(prefix,str(qa),'exec'))
protected_before=dict(before)
who,state=a.case.split('-',1)
C={
 'cutter':('RustboroCity_CuttersHouse','ITEM_HM01','ITEM_TM31','FLAG_GOT_HM01',
  'FLAG_HOENN_GOT_CUTTER_SHARED_HM_REWARD',(7,5),'HoennRustboroCity_CuttersHouse',
  '0473ea5f7bfc8f5ff9f62ee6427c10c6f749b650484efb5c6615428904abd915'),
 'smash':('MauvilleCity_House1','ITEM_HM06','ITEM_TM23','FLAG_GOT_HM06',
  'FLAG_HOENN_GOT_ROCK_SMASH_SHARED_HM_REWARD',(4,4),'HoennHouse2',
  'abbbb3ae0dde23f48f41faac137e9533b6095a9f3c69ce2817f459d4dad0fe50')}
M,HM,TM,HISTORY,RECEIPT,NPC,LAYOUT,TERRAIN=C[who]
WT=TT=MT='TRAINER_HOENN_ROXANNE_1'
htext=Path('include/constants/flags_hoenn_story.h').read_text()
hf=re.findall(r'^#define\s+(FLAG_(?:HIDE_)?HOENN_\w+)\b',htext,re.M)
flags=list(dict.fromkeys(storyflags+hf+[HISTORY,RECEIPT]))
report.update(mode='native-hoenn-shared-hm-'+a.case,stages=[],
 fixture='original six-mon party, PC and genuine starter Pika are unchanged in temporary save',
 scope='Only Cutter HM01/TM31 and Mauville HM06/TM23; not all shared HM recipients or complete Hoenn story')
original_party=bytes(source.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
original_count=source.party_count();assert original_count==6
original_pika=original_starter_copy(source)
assert original_party[100:200]==original_pika
assert sha(Path('data/layouts/'+LAYOUT+'/map.bin').read_bytes())==TERRAIN
j=map_info(M)['json'];rows=[o for o in j['object_events'] if o['script']==M+'_EventScript_H0']
assert len(rows)==1 and (rows[0]['x'],rows[0]['y'])==NPC
assert rows[0]['trainer_type']=='TRAINER_TYPE_NONE'
START=(NPC[0],NPC[1]+1);PO=off('sb1.pcItems');PN=const('PC_ITEMS_COUNT')
assert 1<=PN<=256
def itempc(s):return bytes(s.sb1[PO:PO+4*PN])
def set_pc_hm(s,count):
 # PC item quantity has no bag XOR; only this HM is changed in the fixture.
 mid=const(HM)
 for i in range(PN):
  pos=PO+4*i
  if struct.unpack_from('<H',s.sb1,pos)[0]==mid:struct.pack_into('<HH',s.sb1,pos,0,0)
 if count:
  empty=[PO+4*i for i in range(PN) if not struct.unpack_from('<H',s.sb1,PO+4*i)[0]]
  assert empty,'temporary PC fixture has no empty item slot'
  struct.pack_into('<HH',s.sb1,empty[0],mid,count)
def invariants():
 now=e.read(syms['gPlayerParty'],600)
 assert e.u8(syms['gPlayerPartyCount'])==original_count and now==original_party
 party_valid(now,original_count)
 assert now[100:200]==original_pika
 assert pc(e)==source_pc and e.read(e.ptr('gPokemonStoragePtr'),off('storage'))==source_storage
 assert digest_dex(blocks(e))==original_dex
 assert itempc(blocks(e))==fixture_pc_items,'PC items changed by a bag reward'
def talk_reward():
 prior=e.location();e.press('UP',hold=1,after=20);assert e.location()==prior
 e.press('A',hold=3,after=20);quiet_finish(e);invariants()
 assert not e.in_battle() and loc_is(e,M) and e.location()[2:]==START
def unchanged_story(initial):
 assert {f:blocks(e).flag(f) for f in initial if f!=RECEIPT}=={
  f:v for f,v in initial.items() if f!=RECEIPT},'unrelated story or Kanto HM history changed'
def reward_counts(hm,tm):
 b=blocks(e);assert b.item_count(HM)==hm and b.item_count(TM)==tm,(HM,b.item_count(HM),hm,TM,b.item_count(TM),tm)

# Preserve assertions, log exact flags and native counter around cold continue.
_helper=Path('tools/qa/hoenn_weather_space_native_qa.py').read_text()
_helper=_helper[_helper.index('def native_save_reopen('):_helper.index('\ne=None\ntry:')]
_old=" assert {f:b.flag(f) for f in flags}==expected_flags"
_new=" report['cold_counter_diagnostic']={'saved':saved.counter,'cold':e.u32(syms['gSaveCounter'])}\n report['cold_flag_differences']={f:{'warm':expected_flags[f],'saved':saved.flag(f),'cold':b.flag(f)} for f in flags if b.flag(f)!=expected_flags[f]}\n print('COLD_FLAG_DIFF',json.dumps({'counter':report['cold_counter_diagnostic'],'flags':report['cold_flag_differences']}),flush=True)\n"+_old
assert _helper.count(_old)==1
exec(compile(_helper.replace(_old,_new),'diagnostic-save-helper','exec'))

e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-hoenn-shared-hm-') as td:
  s=SaveFile(str(sav))
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
  s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  s.set_flag(RECEIPT,state=='done');s.set_flag(HISTORY,state in ('history','full-retry'))
  s.set_item(HM,1 if state in ('bag','done') else 0)
  s.set_item(TM,999 if state=='full-retry' else 2 if state=='done' else 0)
  set_pc_hm(s,1 if state=='pc' else 0);fixture_pc_items=itempc(s)
  hm_before=s.item_count(HM);tm_before=s.item_count(TM);s.warp(M,*START)
  fixture=Path(td)/'shared-hm.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  invariants();assert loc_is(e,M) and e.location()[2:]==START
  initial_story={f:blocks(e).flag(f) for f in flags}
  probe_companion('shared-hm-before',('DOWN','UP'))
  talk_reward()
  if state=='full-retry':
   assert not blocks(e).flag(RECEIPT)
   reward_counts(hm_before,999);unchanged_story(initial_story)
   native_save_reopen(e,source_pc);invariants()
   assert not blocks(e).flag(RECEIPT);reward_counts(hm_before,999)
   e.close();e=None
   released=SaveFile(str(fixture));assert not released.flag(RECEIPT)
   released.set_item(TM,998)
   retry=Path(td)/'capacity-released-fixture.sav';released.save(str(retry));check_sectors(SaveFile(str(retry)))
   e=ReadOnlyEmu(str(rom),str(retry),sym='');e.syms=syms;e.boot_continue();settle(e)
   invariants();reward_counts(hm_before,998)
   report['capacity_release']={'temporary_fixture_only':True,'native_bag_toss_tested':False,'before':999,'after':998}
   talk_reward();reward_counts(hm_before,999)
   expected_hm=hm_before;expected_tm=999
  elif state=='fresh':
   expected_hm=hm_before+1;expected_tm=tm_before;reward_counts(expected_hm,expected_tm)
  elif state=='done':
   expected_hm=hm_before;expected_tm=tm_before;reward_counts(expected_hm,expected_tm)
  else:
   expected_hm=hm_before;expected_tm=tm_before+1;reward_counts(expected_hm,expected_tm)
  assert blocks(e).flag(RECEIPT)
  talk_reward();reward_counts(expected_hm,expected_tm)
  invariants();unchanged_story(initial_story)
  native_save_reopen(e,source_pc);invariants()
  assert loc_is(e,M) and e.location()[2:]==START and blocks(e).flag(RECEIPT)
  reward_counts(expected_hm,expected_tm)
  probe_companion('shared-hm-cold',('DOWN','UP'));invariants();unchanged_story(initial_story)
  report['stages'].append({'label':'native-one-shared-hm-or-rare-tm',
   'state':state,'hm':HM,'hm_quantity':expected_hm,'alternate_tm':TM,'tm_quantity':expected_tm,
   'receipt':RECEIPT,'item_pc_unchanged':True,'cold':True})
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
