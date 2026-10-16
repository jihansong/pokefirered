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
MASTER=('IlexForest',29,36)
GATE=('IlexForest_AzaleaGate',7,6)
RADIO=('GoldenrodCity_RadioTower_1F',9,4)
WHITNEY=('GoldenrodCity_Gym',6,5)
ASSISTANT=('GoldenrodCity_Gym',7,17)
cases=[]
def add(name,where,marker,**kw):
 cases.append(dict(name=name,where=where,marker=marker,**kw))
def master(name,marker,**kw):
 add('master_'+name,MASTER,'IlexForest_Text_'+marker,**kw)
master('before_return','MasterBefore',expect_flags={C:False})
master('first_hm','MasterCut',flags={F:True},expect_flags={C:True},delta={'ITEM_HM01':1})
master('bag_hm_alternate','MasterAlternate',flags={F:True},items={'ITEM_HM01':1},expect_flags={C:True},delta={'ITEM_TM48':1})
master('pc_hm_alternate','MasterAlternate',flags={F:True},pc_hm=1,expect_flags={C:True},delta={'ITEM_TM48':1})
master('history_only_alternate','MasterAlternate',flags={F:True},history=True,expect_flags={C:True},delta={'ITEM_TM48':1})
master('party_cut_is_not_hm_history','MasterCut',flags={F:True},party_cut=True,expect_flags={C:True},delta={'ITEM_HM01':1})
master('alternate_full_stack','MasterBagFull',flags={F:True},history=True,items={'ITEM_TM48':999},expect_flags={C:False})
master('alternate_retry_has_space','MasterAlternate',flags={F:True},history=True,items={'ITEM_TM48':998},expect_flags={C:True},delta={'ITEM_TM48':1})
master('already_done_no_reissue','MasterAfter',flags={F:True,C:True},expect_flags={C:True})
master('tm_case_auto_created','MasterCut',flags={F:True},tm_case=0,expect_flags={C:True},delta={'ITEM_HM01':1})
add('farfetchd_before_request',('IlexForest',34,14),'IlexForest_Text_FarfetchdShy')
add('apprentice_first_request',('IlexForest',25,36),'IlexForest_Text_ApprenticeRequest',expect_flags={Q:True})
add('apprentice_repeat_request',('IlexForest',25,36),'IlexForest_Text_ApprenticeWait',flags={Q:True},expect_flags={Q:True})
add('farfetchd_native_return',('IlexForest',34,14),'IlexForest_Text_FarfetchdBack',flags={Q:True},expect_flags={F:True},object=(2,26,35))
add('farfetchd_home_cold_load',('IlexForest',26,36),'IlexForest_Text_FarfetchdHome',flags={Q:True,F:True},object=(2,26,35))
add('radio_before_elm',RADIO,'GoldenrodCity_RadioTower_1F_Text_BeforeElm',flags={E:False},expect_flags={R:False})
add('radio_register',RADIO,'GoldenrodCity_RadioTower_1F_Text_Register',expect_flags={R:True})
add('radio_registered_repeat',RADIO,'GoldenrodCity_RadioTower_1F_Text_Registered',flags={R:True},expect_flags={R:True})
add('silver_needs_johto_badge2',GATE,'IlexForest_AzaleaGate_Text_SilverNotReady',flags={P:False,J:False},expect_flags={P:False})
add('whitney_badge2_gate',WHITNEY,'GoldenrodCity_Gym_Text_NotReady',flags={R:True,J:False},expect_flags={G:False,U:False})
add('whitney_research_gate',WHITNEY,'GoldenrodCity_Gym_Text_NotReady',flags={R:False},expect_flags={G:False,U:False})
add('assistant_before_win',ASSISTANT,'GoldenrodCity_Gym_Text_AssistantBefore',expect_flags={N:False})
add('assistant_encourages_after_win',ASSISTANT,'GoldenrodCity_Gym_Text_AssistantEncourage',trainers={'WHITNEY':True},expect_flags={N:True,G:False,U:False})
add('whitney_upset_before_encouragement',WHITNEY,'GoldenrodCity_Gym_Text_Upset',flags={R:True},trainers={'WHITNEY':True},expect_flags={G:False,U:False})
add('whitney_badge_then_tm',WHITNEY,'GoldenrodCity_Gym_Text_TM',flags={R:True,N:True},trainers={'WHITNEY':True},expect_flags={G:True,U:True},delta={'ITEM_TM45':1})
add('whitney_tm_full_stack_keeps_badge',WHITNEY,'GoldenrodCity_Gym_Text_BagFull',flags={R:True,N:True},trainers={'WHITNEY':True},items={'ITEM_TM45':999},expect_flags={G:True,U:False})
add('whitney_tm_retry_has_space',WHITNEY,'GoldenrodCity_Gym_Text_TM',flags={G:True},trainers={'WHITNEY':True},items={'ITEM_TM45':998},expect_flags={U:True},delta={'ITEM_TM45':1})
add('whitney_claimed_tm_not_reissued',WHITNEY,'GoldenrodCity_Gym_Text_After',flags={G:True,U:True},trainers={'WHITNEY':True})
assert len(cases)==28
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='ilex-native-events-') as td:
  for c in cases:
   path=Path(td)/(c['name']+'.sav');prepared=fixture(path,c)
   with ReadOnlyEmu(str(rom),str(path),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    interaction(e,c);after=snapshot(e)
    flags=dict(before['flags']);flags.update(c.get('expect_flags',{}))
    assert after['flags']==flags,(c['name'],'flags',after['flags'],flags)
    assert after['trainers']==before['trainers'],(c['name'],'unexpected battle record')
    for item in ITEMS:
     assert after['items'][item]==before['items'][item]+c.get('delta',{}).get(item,0),(c['name'],item,after['items'])
    for field in ['pc','party','party_count','dex','pc_hm']:
     assert after[field]==before[field],(c['name'],'preservation',field)
    assert after['pc']==bytes(prepared.blocks['storage'])
    if c.get('object') and c['name']!='farfetchd_native_return':follower_map_object(e,*c['object'])
    e.shot(str(out/(c['name']+'.png')),scale=3)
    saved=flash_reload(e,c['name'])
    if c.get('object') and c['name']!='farfetchd_native_return':follower_map_object(e,*c['object'])
    row={'case':c['name'],'native_dialogue':c['marker'],'menu_save_cold_load':saved,
     'pc_party_dex_preserved':True,'forced_memory_writes':0,'forced_battle_outcomes':0}
   if c['name']=='farfetchd_native_return':
    # The home position is outside the player's camera after the return.
    # Inspect it by cold-loading the genuine native result with a position-only QA warp.
    source=SaveFile(saved['qa_save']);target=Path(td)/(c['name']+'-home.sav')
    native_pc=bytes(source.blocks['storage'])
    native_party=bytes(source.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
    native_flags={f:source.flag(f) for f in before['flags']}
    assert native_flags[F]
    source.warp('IlexForest',26,36);source.save(str(target))
    check=SaveFile(str(target))
    assert bytes(check.blocks['storage'])==native_pc
    assert bytes(check.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])==native_party
    assert {f:check.flag(f) for f in native_flags}==native_flags
    with ReadOnlyEmu(str(rom),str(target),sym='') as home:
     home.syms=syms;home.boot_continue();settle(home);home.run(60)
     follower_map_object(home,2,26,35);live=snapshot(home)
     assert live['pc']==native_pc and live['party']==native_party
     assert live['flags']==native_flags
     home.shot(str(out/(c['name']+'-native-home.png')),scale=3)
     row['returned_home_native_cold_load']={'forced_story_flags':0,'qa_position_only_warps':1}
   results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sha in originals.items():assert digest(path.read_bytes())==sha,('original changed',str(path))
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),
 'helper_sha256':digest(text.encode()),'input_sav_sha256':originals[sav],
 'case_count':len(results),'all_pass':len(results)==len(cases),'cases':results},indent=2))
