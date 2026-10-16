#!/usr/bin/env python3
"""Legacy Brawly/Wattson win bits recover Hoenn badges and reward receipts."""
from pathlib import Path
import hashlib,re
q=Path('tools/qa/native_strength_rock_puzzle_qa.py');text=q.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='ab57a60e8f4961c318c0b975863c0ac36075f3e7556f363ae508b702928a3841'
prefix=text.split('e=None\ntry:',1)[0];assert prefix!=text
cases=[name+'-'+state for name in ('brawly','wattson') for state in ('legacy','receipt','full-retry')]
prefix,n=re.subn(r'cases=\[.*?\]\nassert head.count','cases='+repr(cases)+'\nassert head.count',prefix,count=1,flags=re.S);assert n==1
exec(compile(prefix,str(q),'exec'))
protected_before=dict(before)
name,state=a.case.split('-',1)
C={
 'brawly':('DewfordTown_Gym','DewfordTown_Gym_EventScript_Brawly','TRAINER_HOENN_BRAWLY_1',
  'FLAG_HOENN_BADGE02_GET','FLAG_HOENN_GOT_TM08_FROM_BRAWLY','ITEM_TM08',3,(4,3),
  'HoennDewfordTown_Gym','b4b06558fc3ada623e51389ea679dae72c17cf8111b6054c7b2436a4dff09d9e'),
 'wattson':('MauvilleCity_Gym','MauvilleCity_Gym_EventScript_Wattson','TRAINER_HOENN_WATTSON_1',
  'FLAG_HOENN_BADGE03_GET','FLAG_HOENN_GOT_TM34_FROM_WATTSON','ITEM_TM34',6,(5,2),
  'HoennMauvilleCity_Gym','bde3a68a66cd1633838d4361d8439c155532d1666d4e8d33c065c2add372944f')}
M,L,TR,BADGE,GOT,TM,PROGRESS,NPC,LAYOUT,TERRAIN=C[name]
WT=TT=MT=TR
extras=['FLAG_HOENN_PIKACHU_GYM_SEEN','FLAG_HOENN_WATTSON_ERRAND',
 'FLAG_HOENN_NEW_MAUVILLE_DONE','FLAG_HOENN_DEFEATED_MAUVILLE_GYM']
flags=list(dict.fromkeys(storyflags+extras+[BADGE,GOT]))
report.update(mode='native-hoenn-legacy-badge-'+a.case,stages=[],
 fixture='temporary legacy trainer win, entire original six-mon party and genuine Pika unchanged',
 scope='Only the previously won leader with a missing badge; not a fresh gym battle or full Hoenn completion')
original_party=bytes(source.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
original_count=source.party_count();assert original_count==6
original_pika=original_starter_copy(source)
assert original_party[100:200]==original_pika
assert sha(Path('data/layouts/'+LAYOUT+'/map.bin').read_bytes())==TERRAIN,'original gym terrain changed'
j=map_info(M)['json'];leaders=[o for o in j['object_events'] if o['script']==L]
assert len(leaders)==1 and (leaders[0]['x'],leaders[0]['y'])==NPC
assert leaders[0]['trainer_type']=='TRAINER_TYPE_NONE'
START=(NPC[0],NPC[1]+1)
PROG='VAR_HOENN_STAGE1_PROGRESS'
def invariants():
 now=e.read(syms['gPlayerParty'],600)
 assert e.u8(syms['gPlayerPartyCount'])==original_count and now==original_party,'original party changed'
 party_valid(now,original_count)
 assert e.read(e.ptr('gPokemonStoragePtr'),off('storage'))==source_storage
 assert pc(e)==source_pc and digest_dex(blocks(e))==original_dex
 assert now[100:200]==original_pika,'genuine Pika changed'
def talk_leader():
 prior=e.location();e.press('UP',hold=1,after=20);assert e.location()==prior
 e.press('A',hold=3,after=20);quiet_finish(e);invariants()
 assert not e.in_battle() and blocks(e).trainer_beaten(TR),'old win rematched or cleared'
 assert loc_is(e,M) and e.location()[2:]==START,'reward moved player'
def unchanged_story(initial):
 excluded={BADGE,GOT}
 if name=='wattson':excluded.add('FLAG_HOENN_DEFEATED_MAUVILLE_GYM')
 assert {f:blocks(e).flag(f) for f in initial if f not in excluded}=={
  f:v for f,v in initial.items() if f not in excluded},'unrelated story flags changed'
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-hoenn-legacy-badge-') as td:
  s=SaveFile(str(sav));assert bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])==original_party
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
  s.set_trainer_beaten(TR,True);s.set_flag(BADGE,False);s.set_flag(GOT,state=='receipt')
  s.set_flag('FLAG_HOENN_PIKACHU_GYM_SEEN',True)
  s.set_flag('FLAG_HOENN_WATTSON_ERRAND',True)
  s.set_flag('FLAG_HOENN_NEW_MAUVILLE_DONE',False)
  s.set_flag('FLAG_HOENN_DEFEATED_MAUVILLE_GYM',False)
  s.set_var('VAR_HOENN_NEW_MAUVILLE_STATE',0)
  s.set_var(PROG,PROGRESS-1);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  # 999 is the actual TMs/Items stack limit; releasing one unit is a
  # temporary save fixture change, not an untested native bag toss.
  s.set_item(TM,999 if state=='full-retry' else 2 if state=='receipt' else 0)
  before_qty=s.item_count(TM);s.warp(M,*START)
  fixture=Path(td)/'legacy.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  invariants();assert loc_is(e,M) and e.location()[2:]==START
  assert blocks(e).trainer_beaten(TR) and not blocks(e).flag(BADGE)
  initial_story={f:blocks(e).flag(f) for f in flags}
  probe_companion('legacy-before',('DOWN','UP'))
  talk_leader();b=blocks(e)
  assert b.flag(BADGE),'old trainer win did not recover its own Hoenn badge'
  assert b.var(PROG)==PROGRESS,('legacy progress did not advance without decrement',b.var(PROG),PROGRESS)
  if name=='wattson':assert b.flag('FLAG_HOENN_DEFEATED_MAUVILLE_GYM')
  if state=='full-retry':
   assert not b.flag(GOT) and b.item_count(TM)==999,'full stack incorrectly committed or grew'
   report['stages'].append({'label':'native-legacy-badge-full-stack-refusal','badge':True,'receipt':False,'quantity':999})
   unchanged_story(initial_story);native_save_reopen(e,source_pc);invariants()
   assert blocks(e).flag(BADGE) and not blocks(e).flag(GOT)
   assert blocks(e).item_count(TM)==999 and blocks(e).var(PROG)==PROGRESS
   e.close();e=None
   released=SaveFile(str(fixture));assert released.flag(BADGE) and not released.flag(GOT)
   released.set_item(TM,998)
   retry=Path(td)/'capacity-released-fixture.sav';released.save(str(retry));check_sectors(SaveFile(str(retry)))
   e=ReadOnlyEmu(str(rom),str(retry),sym='');e.syms=syms;e.boot_continue();settle(e)
   invariants();assert blocks(e).item_count(TM)==998
   report['capacity_release']={'qa_only_fixture':True,'native_bag_toss_tested':False,'before':999,'after':998}
   talk_leader();assert blocks(e).item_count(TM)==999 and blocks(e).flag(GOT)
  elif state=='receipt':
   assert b.flag(GOT) and b.item_count(TM)==before_qty,'received reward was duplicated'
  else:assert b.flag(GOT) and b.item_count(TM)==before_qty+1,'unreceived reward not given once'
  snapshot=e.read(syms['gPlayerParty'],600);qty=blocks(e).item_count(TM)
  talk_leader();assert blocks(e).item_count(TM)==qty and blocks(e).flag(GOT),'repeat gift duplicated'
  assert e.read(syms['gPlayerParty'],600)==snapshot
  invariants();unchanged_story(initial_story)
  native_save_reopen(e,source_pc);invariants()
  assert loc_is(e,M) and e.location()[2:]==START
  assert blocks(e).flag(BADGE) and blocks(e).flag(GOT) and blocks(e).trainer_beaten(TR)
  assert blocks(e).var(PROG)==PROGRESS and blocks(e).item_count(TM)==qty
  probe_companion('legacy-cold',('DOWN','UP'));invariants();unchanged_story(initial_story)
  report['stages'].append({'label':'native-old-win-badge-resumed-no-rematch',
   'trainer':TR,'badge':BADGE,'reward_receipt':GOT,'reward':TM,'quantity':qty,'cold':True})
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
