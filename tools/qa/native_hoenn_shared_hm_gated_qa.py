#!/usr/bin/env python3
"""Chapter-bound HM03/04/05 sharing, permanent retries and preserved original six-party save."""
from pathlib import Path
import hashlib,re
qa=Path('tools/qa/native_strength_rock_puzzle_qa.py');text=qa.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='ab57a60e8f4961c318c0b975863c0ac36075f3e7556f363ae508b702928a3841'
prefix=text.split('e=None\ntry:',1)[0];assert prefix!=text
cases=[who+'-'+state for who in ('wanda','dad','flash') for state in ('fresh','bag','pc','history','done','full-retry')]
cases+=['wanda-before-open','wanda-referral','dad-before-wally','dad-before-norman','dad-badge-only','dad-trainer-only']
prefix,n=re.subn(r'cases=\[.*?\]\nassert head.count','cases='+repr(cases)+'\nassert head.count',prefix,count=1,flags=re.S);assert n==1
exec(compile(prefix,str(qa),'exec'))
protected_before=dict(before)
who,state=a.case.split('-',1)
C={
 "wanda":["VerdanturfTown_WandasHouse","ITEM_HM04","ITEM_TM26","FLAG_GOT_HM04","FLAG_HOENN_GOT_WANDA_SHARED_HM_REWARD",[6,4],"HoennVerdanturfTown_WandasHouse","cfc9d2a0923025f21d5feacbdbd0665f10bb781a34b9ed17f28ee7f9e918f738","VerdanturfTown_WandasHouse_EventScript_Wanda"],
 "dad":["PetalburgCity_WallysHouse","ITEM_HM03","ITEM_TM13","FLAG_GOT_HM03","FLAG_HOENN_GOT_WALLY_DAD_SHARED_HM_REWARD",[3,4],"HoennHouse2","abbbb3ae0dde23f48f41faac137e9533b6095a9f3c69ce2817f459d4dad0fe50","PetalburgCity_WallysHouse_EventScript_H0"],
 "flash":["GraniteCave_1F","ITEM_HM05","ITEM_TM29","FLAG_GOT_HM05","FLAG_HOENN_GOT_GRANITE_SHARED_HM_REWARD",[36,9],"HoennGraniteCave_1F","6e8e5420747a9e2c18c9ecc04e43e028cac70e6030a8015a52edcac739459bbf","GraniteCave_1F_EventScript_H0"],
}
M,HM,TM,HISTORY,RECEIPT,NPC,LAYOUT,TERRAIN,NPC_SCRIPT=C[who]
NPC=tuple(NPC)
WT=TT=MT='TRAINER_HOENN_NORMAN_1'
NEGATIVE=state in ('before-open','before-wally','before-norman','badge-only','trainer-only')
htext=Path('include/constants/flags_hoenn_story.h').read_text()
hf=re.findall(r'^#define\s+(FLAG_(?:HIDE_)?HOENN_\w+)\b',htext,re.M)
flags=list(dict.fromkeys(storyflags+hf+[HISTORY,RECEIPT]))
report.update(mode='native-hoenn-shared-hm-story-'+a.case,stages=[],
 fixture='original six-mon party, PC and genuine starter Pika are unchanged in temporary save',
 scope='Only chapter-bound Wanda HM04/TM26, Wally Dad HM03/TM13 and Hiker HM05/TM29; not a complete Hoenn playthrough')
original_party=bytes(source.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
original_count=source.party_count();assert original_count==6
original_pika=original_starter_copy(source)
assert original_party[100:200]==original_pika
assert sha(Path('data/layouts/'+LAYOUT+'/map.bin').read_bytes())==TERRAIN
j=map_info(M)['json'];rows=[o for o in j['object_events'] if o['script']==NPC_SCRIPT]
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
 allowed={RECEIPT}
 if state=='referral':allowed.add('FLAG_HOENN_MET_WANDA')
 assert {f:blocks(e).flag(f) for f in initial if f not in allowed}=={
  f:v for f,v in initial.items() if f not in allowed},'unrelated story or Kanto HM history changed'
 b=blocks(e)
 assert {v:b.var(v) for v in protected_vars}==initial_vars,'chapter progress variables changed'
 assert b.trainer_beaten(WT)==initial_norman,'Norman victory history changed'
 if state=='referral':assert b.flag('FLAG_HOENN_MET_WANDA')
def reward_counts(hm,tm):
 b=blocks(e);assert b.item_count(HM)==hm and b.item_count(TM)==tm,(HM,b.item_count(HM),hm,TM,b.item_count(TM),tm)
def repel_guard(reference):
 # Exact candidate ARM tables; no species, order or level edits.
 assert hashlib.sha256(r.data).digest()==hashlib.sha256(Path(rom).read_bytes()).digest()
 lead=None
 for slot in range(reference.party_count()):
  m=reference.party_mon(slot);raw=bytes(m.blk[m.o:m.o+100])
  if struct.unpack_from('<H',raw,86)[0]>0 and not m.is_egg():
   assert not raw[19]&1,'native Repel lead is Bad Egg'
   checksum=sum(struct.unpack('<24H',b''.join(m.subs()[k] for k in 'GAEM')))&65535
   assert checksum==struct.unpack_from('<H',raw,28)[0],'native Repel lead checksum mismatch'
   lead={'slot':slot,'level':raw[84],'personality':m.personality,'otid':m.otid};break
 assert lead and lead['level']>0,'no healthy original Repel lead'
 mi=map_info(M);pair=(mi['group'],mi['num']);encounters=[]
 for table in ('gWildMonHeaders','gWildMonHeadersMorning','gWildMonHeadersNight'):
  assert table in syms and table in r.syms and syms[table]==r.syms[table],('candidate encounter symbol mismatch',table)
  found=[];ended=False
  for i in range(1024):
   raw=r.at(syms[table]+i*20,20);assert len(raw)==20
   g,n=raw[:2]
   if (g,n)==(255,255):ended=True;break
   if (g,n)!=pair:continue
   land=struct.unpack_from('<I',raw,4)[0];assert land and land%4==0
   info=r.at(land,8);assert len(info)==8 and info[0]>0
   mons=struct.unpack_from('<I',info,4)[0];assert mons and mons%2==0
   slots=r.at(mons,12*4);assert len(slots)==48
   assert all(0<slots[j*4]<=slots[j*4+1]<=100 for j in range(12))
   found.append({'table':table,'maximum_level':max(slots[j*4+1] for j in range(12)),'native_rate':info[0]})
  assert ended and len(found)==1,('native cave wild header must be unique',table,found)
  encounters.extend(found)
 assert all(lead['level']>v['maximum_level'] for v in encounters),'original lead level does not guarantee Repel; do not edit party'
 report['native_repel_guard']={'original_lead':lead,'actual_candidate_encounters':encounters,'temporary_repel_steps':250}
def normalize_continue_object_flags(s):
 # These three targets use the default Briney and Wanda map branches.
 assert M in ('VerdanturfTown_WandasHouse','PetalburgCity_WallysHouse','GraniteCave_1F')
 c=Path('src/field_specials.c').read_text()
 expected_lines=[
  'SetHideFlag(FLAG_HIDE_HOENN_BIRCH_LAB, birch == 0);',
  'SetHideFlag(FLAG_HIDE_HOENN_RIVAL_ROUTE103, birch != 2);',
  'SetHideFlag(FLAG_HIDE_HOENN_RIVAL_LAB, birch < 3);',
  'SetHideFlag(FLAG_HIDE_HOENN_RUSTBORO_THIEF, !(devon == 1 && FlagGet(FLAG_HOENN_BADGE01_GET)));',
  'SetHideFlag(FLAG_HIDE_HOENN_RUSTURF_GRUNT, devon != 2);',
  'SetHideFlag(FLAG_HIDE_HOENN_RUSTURF_PEEKO, devon != 2 || peeko);',
  'SetHideFlag(FLAG_HIDE_HOENN_BRINEY, !peeko);',
  'SetHideFlag(FLAG_HIDE_HOENN_WALLY_PETALBURG, wally != 1);',
  'SetHideFlag(FLAG_HIDE_HOENN_WALLY_VERDANTURF, wally < 2);',
  'SetHideFlag(FLAG_HIDE_HOENN_WANDA_BOYFRIEND, !FlagGet(FLAG_HOENN_RUSTURF_OPEN));']
 assert all(c.count(line)==1 for line in expected_lines),'continue object formulas changed'
 assert 'SetHideFlag(FLAG_HIDE_HOENN_ROCKET_WOODS, FlagGet(FLAG_HOENN_ROCKET_WOODS)' in c
 assert '|| !HasTrainerBeenFought(TRAINER_HOENN_GRUNT_PETALBURG_WOODS));' in c
 birch=s.var('VAR_HOENN_SCENE_BIRCH');devon=s.var('VAR_HOENN_SCENE_DEVON');wally=s.var('VAR_HOENN_SCENE_WALLY')
 peeko=s.flag('FLAG_HOENN_PEEKO_RESCUED')
 values={
  'FLAG_HIDE_HOENN_BIRCH_LAB':birch==0,
  'FLAG_HIDE_HOENN_RIVAL_ROUTE103':birch!=2,
  'FLAG_HIDE_HOENN_RUSTBORO_THIEF':not(devon==1 and s.flag('FLAG_HOENN_BADGE01_GET')),
  'FLAG_HIDE_HOENN_RUSTURF_GRUNT':devon!=2,
  'FLAG_HIDE_HOENN_RUSTURF_PEEKO':devon!=2 or peeko,
  'FLAG_HIDE_HOENN_BRINEY':not peeko,
  'FLAG_HIDE_HOENN_WALLY_PETALBURG':wally!=1,
  'FLAG_HIDE_HOENN_WALLY_VERDANTURF':wally<2,
  'FLAG_HIDE_HOENN_WANDA_BOYFRIEND':not s.flag('FLAG_HOENN_RUSTURF_OPEN'),
  'FLAG_HIDE_HOENN_ROCKET_WOODS':s.flag('FLAG_HOENN_ROCKET_WOODS') or not s.trainer_beaten('TRAINER_HOENN_GRUNT_PETALBURG_WOODS'),
  'FLAG_HIDE_HOENN_RIVAL_LAB':birch<3}
 for flag,value in values.items():s.set_flag(flag,value)
 report['temporary_continue_object_fixture']={'actual_source_formulas':True,'flags':values,
  'original_source_save_changed':False,'native_save_assertions_unchanged':True}
 return values
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-hoenn-shared-hm-story-') as td:
  s=SaveFile(str(sav))
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
  s.set_var('VAR_HAPPINESS_STEP_COUNTER',0);s.set_var('VAR_REPEL_STEP_COUNT',250)
  if who=='flash':repel_guard(s)
  s.set_var('VAR_HOENN_SCENE_WALLY',1 if state=='before-wally' else 2)
  if who=='wanda':
   s.set_flag('FLAG_HOENN_RUSTURF_OPEN',state!='before-open')
   s.set_flag('FLAG_HOENN_MET_WANDA',state!='referral')
   s.set_flag('FLAG_HOENN_DEFEATED_MAUVILLE_GYM',True)
  if who=='dad':
   s.set_flag('FLAG_HOENN_BADGE05_GET',state not in ('before-norman','trainer-only'))
   s.set_trainer_beaten(WT,state not in ('before-norman','badge-only'))
  s.set_flag(RECEIPT,state=='done');s.set_flag(HISTORY,state in ('history','full-retry'))
  s.set_item(HM,1 if state in ('bag','done') else 0)
  s.set_item(TM,999 if state=='full-retry' else 2 if state=='done' else 0)
  set_pc_hm(s,1 if state=='pc' else 0);fixture_pc_items=itempc(s)
  normalized_hide=normalize_continue_object_flags(s)
  hm_before=s.item_count(HM);tm_before=s.item_count(TM);s.warp(M,*START)
  fixture=Path(td)/'shared-hm.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  invariants();assert loc_is(e,M) and e.location()[2:]==START
  initial_story={f:blocks(e).flag(f) for f in flags}
  assert {f:initial_story[f] for f in normalized_hide}==normalized_hide,'first boot changed derived object formulas'
  protected_vars=['VAR_HOENN_SCENE_WALLY','VAR_HOENN_STAGE1_PROGRESS']
  initial_vars={v:blocks(e).var(v) for v in protected_vars}
  initial_norman=blocks(e).trainer_beaten(WT)
  if who=='dad':
   assert (initial_vars['VAR_HOENN_SCENE_WALLY']>=2 and initial_story['FLAG_HOENN_BADGE05_GET'] and initial_norman)==(not NEGATIVE)
  if who=='wanda':
   assert initial_story['FLAG_HOENN_RUSTURF_OPEN']==(not NEGATIVE)
   assert initial_story['FLAG_HOENN_MET_WANDA']==(state!='referral')
  probe_companion('shared-hm-before',('DOWN','UP'))
  talk_reward()
  if state=='full-retry':
   assert not blocks(e).flag(RECEIPT)
   reward_counts(hm_before,999);unchanged_story(initial_story)
   native_save_reopen(e,source_pc);invariants()
   assert not blocks(e).flag(RECEIPT);reward_counts(hm_before,999)
   e.close();e=None
   released=SaveFile(str(out/'qa-only-native-save.sav'));assert not released.flag(RECEIPT)
   released.set_item(TM,998)
   retry=Path(td)/'capacity-released-fixture.sav';released.save(str(retry));check_sectors(SaveFile(str(retry)))
   e=ReadOnlyEmu(str(rom),str(retry),sym='');e.syms=syms;e.boot_continue();settle(e)
   invariants();reward_counts(hm_before,998)
   report['capacity_release']={'temporary_fixture_only':True,'native_bag_toss_tested':False,'before':999,'after':998}
   talk_reward();reward_counts(hm_before,999)
   expected_hm=hm_before;expected_tm=999
  elif state in ('fresh','referral'):
   expected_hm=hm_before+1;expected_tm=tm_before;reward_counts(expected_hm,expected_tm)
  elif state=='done':
   expected_hm=hm_before;expected_tm=tm_before;reward_counts(expected_hm,expected_tm)
  elif NEGATIVE:
   expected_hm=hm_before;expected_tm=tm_before;reward_counts(expected_hm,expected_tm)
  else:
   expected_hm=hm_before;expected_tm=tm_before+1;reward_counts(expected_hm,expected_tm)
  if NEGATIVE:
   expected_hm=hm_before;expected_tm=tm_before
   assert not blocks(e).flag(RECEIPT);reward_counts(expected_hm,expected_tm)
  else:assert blocks(e).flag(RECEIPT)
  talk_reward();reward_counts(expected_hm,expected_tm)
  invariants();unchanged_story(initial_story)
  native_save_reopen(e,source_pc);invariants()
  assert loc_is(e,M) and e.location()[2:]==START
  assert blocks(e).flag(RECEIPT)==(not NEGATIVE)
  reward_counts(expected_hm,expected_tm)
  probe_companion('shared-hm-cold',('DOWN','UP'));invariants();unchanged_story(initial_story)
  report['stages'].append({'label':'native-no-premature-gift' if NEGATIVE else 'native-one-shared-hm-or-rare-tm',
   'state':state,'hm':HM,'hm_quantity':expected_hm,'alternate_tm':TM,'tm_quantity':expected_tm,
   'receipt':RECEIPT,'received':not NEGATIVE,'chapter_gate_preserved':True,'item_pc_unchanged':True,'cold':True})
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
