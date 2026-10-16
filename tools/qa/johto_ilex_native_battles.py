#!/usr/bin/env python3
"""Native Ilex story/reward fixtures and menu-save/cold-load checks.
Usage: SCRIPT VERIFIED_VIOLET_QA --rom ROM --elf ELF --sav SAV --out NEWDIR
Uses temporary SAV fixtures, native inputs, and no game-memory writes.
"""
from pathlib import Path
import hashlib,sys
base=Path(sys.argv.pop(1));text=base.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='83c4557b96c344b241fc6f79e9b17722acfc0b0e81e0f9e6d649ff5d8b1c84bb'
assert text.count('\nresults=[]\n')==1
exec(compile(text.split('\nresults=[]\n')[0],str(base),'exec'),globals())
_original_fixture=fixture
_original_snapshot=snapshot
P='FLAG_JOHTO_SILVER_AZALEA_DEFEATED'
F='FLAG_JOHTO_ILEX_FARFETCHD_RETURNED'
C='FLAG_JOHTO_ILEX_CUT_BRIEFED'
G='FLAG_JOHTO_BADGE03_GET'
Q='FLAG_JOHTO_ILEX_HELP_REQUESTED'
R='FLAG_JOHTO_GOLDENROD_RESEARCH_REGISTERED'
N='FLAG_JOHTO_WHITNEY_ENCOURAGED'
U='FLAG_JOHTO_GOT_TM45_FROM_WHITNEY'
J='FLAG_JOHTO_BADGE02_GET'
STORY=[P,F,C,G,Q,R,N,U,J]
ACTORS=['SILVER_AZALEA','WHITNEY']
ITEMS=['ITEM_HM01','ITEM_TM48','ITEM_TM45']
def pc_item(s,item,qty):
 iid=const(item);start=off('sb1.pcItems');slots=[start+i*4 for i in range(const('PC_ITEMS_COUNT'))]
 for pos in slots:
  old,n=struct.unpack_from('<HH',s.sb1,pos)
  if old==iid:
   struct.pack_into('<HH',s.sb1,pos,iid if qty else 0,qty);return
 if not qty:return
 for pos in slots:
  if struct.unpack_from('<H',s.sb1,pos)[0]==0:
   struct.pack_into('<HH',s.sb1,pos,iid,qty);return
 raise AssertionError('QA fixture has no free PC-item slot')
def pc_count(b,item):
 iid=const(item);start=off('sb1.pcItems')
 return sum(n for old,n in struct.iter_unpack('<HH',bytes(b.sb1[start:start+const('PC_ITEMS_COUNT')*4])) if old==iid)
def fixture(path,c):
 s=_original_fixture(path,'FALKNER',False)
 for f in [T,H,B,M,J]:s.set_flag(f,True)
 for tr in ['LI','FALKNER','BUGSY']:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,True)
 for f in STORY:s.set_flag(f,False)
 s.set_flag(J,True);s.set_flag(P,True)
 for f,v in c.get('flags',{}).items():s.set_flag(f,v)
 for tr in ACTORS:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,c.get('trainers',{}).get(tr,False))
 s.set_flag('FLAG_GOT_HM01',c.get('history',False))
 for item in ITEMS:s.set_item(item,c.get('items',{}).get(item,0))
 s.set_item('ITEM_TM_CASE',c.get('tm_case',1));pc_item(s,'ITEM_HM01',c.get('pc_hm',0))
 if c.get('party_cut'):
  m=s.party_mon(0);sub=m.subs();struct.pack_into('<H',sub['A'],0,const('MOVE_CUT'));sub['A'][8]=30;m.put_subs(sub)
 s.set_var('VAR_REPEL_STEP_COUNT',250)
 s.warp(*c['where']);s.save(str(path));return s
def snapshot(e):
 d=_original_snapshot(e);b=blocks(e)
 d['flags'].update({f:b.flag(f) for f in STORY+['FLAG_GOT_HM01']})
 d['trainers'].update({n:b.trainer_beaten('TRAINER_JOHTO_'+n) for n in ACTORS})
 d['items']={n:b.item_count(n) for n in ITEMS}
 d['pc_hm']=pc_count(b,'ITEM_HM01')
 return d
def interaction(e,c):
 marker=syms[c['marker']]
 token=e.read(marker,24).split(b'\xff')[0]
 assert len(token)>=8
 seen=[False];oldrun=e.run
 def watch_run(frames=1):
  oldrun(frames)
  if token in e.sym_read('gStringVar4',256):seen[0]=True
 e.run=watch_run
 try:
  e.walk(c.get('direction','UP'),1);e.run(30);e.press('A',hold=3,after=12);settle(e)
 finally:e.run=oldrun
 assert seen[0],('dialogue branch not seen',c['name'],c['marker'])
 assert e.in_overworld() and not e.in_battle()
def follower_map_object(e,local_id,x,y):
 group,num,_,_=e.location();obj=e.read(syms['gObjectEvents'],36*const('OBJECT_EVENTS_COUNT'))
 found=[]
 for i in range(0,len(obj),36):
  row=obj[i:i+36]
  if row[0]&1 and row[8]==local_id and row[9]==num and row[10]==group:
   found.append(struct.unpack_from('<hh',row,16))
 assert found==[(x+7,y+7)],('native object position',found,(x,y))
TEAMS={'SILVER_AZALEA':['GASTLY','ZUBAT','CROCONAW'],'WHITNEY':['CLEFAIRY','MILTANK']}
POSITIONS={'SILVER_AZALEA':('IlexForest_AzaleaGate',7,6),'WHITNEY':('GoldenrodCity_Gym',6,5)}
def battle_fixture(path,name,loss):
 s=_original_fixture(path,'FALKNER',loss)
 for f in [T,H,B,M,J]:s.set_flag(f,True)
 for tr in ['LI','FALKNER','BUGSY']:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,True)
 for f in STORY:s.set_flag(f,False)
 s.set_flag(J,True)
 if name=='WHITNEY':s.set_flag(P,True);s.set_flag(F,True);s.set_flag(C,True);s.set_flag(R,True)
 for tr in ACTORS:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,False)
 for item in ITEMS:s.set_item(item,0)
 s.set_item('ITEM_TM_CASE',1);pc_item(s,'ITEM_HM01',0)
 s.set_var('VAR_REPEL_STEP_COUNT',250);s.warp(*POSITIONS[name]);s.save(str(path));return s
def object_absent(e,local_id):
 group,num,_,_=e.location();raw=e.read(syms['gObjectEvents'],36*const('OBJECT_EVENTS_COUNT'))
 for i in range(0,len(raw),36):
  row=raw[i:i+36]
  assert not (row[0]&1 and row[8]==local_id and row[9]==num and row[10]==group),'event object returned after save'
def warp_native_result(source,target,where):
 s=SaveFile(str(source))
 before={'party':bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]),
  'pc':bytes(s.blocks['storage']),'dex':[s.dex_state(i) for i in range(1,387)],
  'flags':{f:s.flag(f) for f in STORY+[A,L,E,T,H,B,M]+K},
  'trainers':{n:s.trainer_beaten('TRAINER_JOHTO_'+n) for n in ACTORS}}
 s.warp(*where);s.save(str(target));check=SaveFile(str(target))
 assert before['party']==bytes(check.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
 assert before['pc']==bytes(check.blocks['storage'])
 assert before['dex']==[check.dex_state(i) for i in range(1,387)]
 assert before['flags']=={f:check.flag(f) for f in before['flags']}
 assert before['trainers']=={n:check.trainer_beaten('TRAINER_JOHTO_'+n) for n in ACTORS}
 return check
def dialog_progress(source,target,where,c):
 assert not target.exists();prepared=warp_native_result(source,target,where)
 with ReadOnlyEmu(str(rom),str(target),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
  interaction(e,c);after=snapshot(e)
  flags=dict(before['flags']);flags.update(c.get('expect_flags',{}))
  assert after['flags']==flags,(c['name'],after['flags'],flags)
  for item in ITEMS:assert after['items'][item]==before['items'][item]+c.get('delta',{}).get(item,0)
  for field in ['pc','party','party_count','dex','pc_hm','trainers']:assert after[field]==before[field],(c['name'],field)
  assert after['pc']==bytes(prepared.blocks['storage'])
  e.shot(str(out/(c['name']+'.png')),scale=3)
  return flash_reload(e,c['name'])
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='ilex-native-battles-') as td:
  for name in ACTORS:
   for loss in [False,True]:
    tag=name.lower()+('_loss' if loss else '_win');target=Path(td)/(tag+'.sav')
    prepared=battle_fixture(target,name,loss)
    expected=[const('SPECIES_'+n) for n in TEAMS[name]]
    with ReadOnlyEmu(str(rom),str(target),sym='') as e:
     e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
     e.walk('UP',1);e.run(30);e.press('A',hold=3,after=12)
     mash_until(e,e.in_battle,300);assert menu(e)
     assert e.u16(e.sym('gTrainerBattleOpponent_A'))==const('TRAINER_JOHTO_'+name)
     raw=e.read(syms['gEnemyParty'],600)
     actual=[Mon(bytearray(raw),i*100).species() for i in range(6) if Mon(bytearray(raw),i*100).has_species()]
     assert actual==expected,(name,actual,expected)
     turns=0
     while menu(e):
      assert turns<90,'battle did not finish'
      fight_one_turn(e,loss=loss);turns+=1
     outcome=e.u8(e.sym('gBattleOutcome'));assert outcome==(2 if loss else 1)
     settle(e);after=snapshot(e)
     wantflags=dict(before['flags']);wanttrainers=dict(before['trainers'])
     wanttrainers[name]=not loss
     if name=='SILVER_AZALEA' and not loss:wantflags[P]=True
     assert after['flags']==wantflags,(tag,after['flags'],wantflags)
     assert after['trainers']==wanttrainers
     assert after['pc']==before['pc']==bytes(prepared.blocks['storage'])
     assert after['items']==before['items'] and after['pc_hm']==before['pc_hm']
     for old,new in zip(before['dex'],after['dex']):
      assert old[0]==new[0] and all(not x or y for x,y in zip(old,new))
     if name=='SILVER_AZALEA' and not loss:object_absent(e,1)
     e.shot(str(out/(tag+'.png')),scale=3);saved=flash_reload(e,tag)
     if name=='SILVER_AZALEA' and not loss:object_absent(e,1)
     row={'case':tag,'turns':turns,'native_outcome':outcome,'enemies':actual,
      'save':saved,'pc_preserved':True,'forced_memory_writes':0,'forced_battle_outcomes':0}
    if name=='WHITNEY' and not loss:
     # Each continuation copies the save produced by the actual preceding native interaction.
     # Only the QA position changes; no story flag, trainer flag, item, party, PC, or dex is edited.
     upset=dialog_progress(Path(saved['qa_save']),Path(td)/(tag+'-upset.sav'),POSITIONS[name],
      {'name':tag+'_upset_revisit','marker':'GoldenrodCity_Gym_Text_Upset','expect_flags':{G:False,N:False,U:False}})
     encourage=dialog_progress(Path(upset['qa_save']),Path(td)/(tag+'-assistant.sav'),('GoldenrodCity_Gym',7,17),
      {'name':tag+'_native_assistant','marker':'GoldenrodCity_Gym_Text_AssistantEncourage','expect_flags':{G:False,N:True,U:False}})
     badge=dialog_progress(Path(encourage['qa_save']),Path(td)/(tag+'-badge.sav'),POSITIONS[name],
      {'name':tag+'_native_badge_reward','marker':'GoldenrodCity_Gym_Text_TM','expect_flags':{G:True,N:True,U:True},'delta':{'ITEM_TM45':1}})
     row['native_reward_sequence']={'upset_without_badge':upset,'assistant_without_badge':encourage,'revisit_badge_and_tm':badge,
      'qa_position_only_warps':3,'forced_story_flags':0}
    results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sha in originals.items():assert digest(path.read_bytes())==sha,('original changed',str(path))
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),
 'helper_sha256':digest(text.encode()),'input_sav_sha256':originals[sav],
 'case_count':len(results),'all_pass':len(results)==4,'cases':results},indent=2))
