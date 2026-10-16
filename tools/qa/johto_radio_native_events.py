#!/usr/bin/env python3
"""Radio Tower native QA; original SAV remains read-only and all outcomes use game inputs."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_radio_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='bbb842feb5d4cd98813d057411e440d45fb8838126a5a550ff2e1be46f1993ed'
exec(compile(_boot_text,str(_boot),'exec'),globals())

cases=[]
def add(name,where,marker,**kw):cases.append(dict(name=name,where=where,marker=marker,**kw))
F1='GoldenrodCity_RadioTower_1F'
F2='GoldenrodCity_RadioTower_2F'
F3='GoldenrodCity_RadioTower_3F'
F4='GoldenrodCity_RadioTower_4F'
F5='GoldenrodCity_RadioTower_5F'
UG='GoldenrodUnderground'
UB='GoldenrodUnderground_Basement'
WH='GoldenrodWarehouse'
clerk=(F1,3,10)
research=(F1,9,5)
petrel=(F3,16,10)
director=(WH,16,18)
archer=(F5,16,10)
add('lobby_research_before_elm',research,F1+'_Text_BeforeElm',flags={ELM:False,R:False})
add('lobby_research_registration',research,F1+'_Text_Register',flags={ELM:True,R:False},expect_flags={R:True})
add('lobby_research_not_registered_twice',research,F1+'_Text_Registered',flags={ELM:True,R:True})
add('lobby_before_pryce',clerk,F1+'_Text_BroadcastClerkBefore',flags={B7:False})
add('lobby_radio_alarm_after_pryce',clerk,F1+'_Text_BroadcastClerkAlarm')
add('lobby_normal_after_rescue',clerk,F1+'_Text_BroadcastClerkAfter',flags={RADIO:True})
add('lobby_studios_locked_before_badge7',(F1,13,3),F1+'_Text_UpperGateClosed',direction='LEFT',step=True,flags={B7:False})
add('lobby_studios_open_after_badge7',(F1,13,3),None,direction='LEFT',step=True,dest=F2)
add('petrel_not_ready_before_badge7',petrel,F3+'_Text_PetrelBefore',flags={B7:False})
add('petrel_saved_win_grants_access',petrel,F3+'_Text_PetrelAfter',trainers={'PETREL_RADIO':True},expect_flags={ACCESS:True,HPETREL:True})
add('upper_studio_locked_before_director',(F3,29,2),F3+'_Text_UpperGateClosed',direction='RIGHT',step=True)
add('upper_studio_opens_after_director',(F3,29,2),None,direction='RIGHT',step=True,flags={DIRECTOR:True},dest=F4)
for name,flags,marker in [('before_code',{},'WorkerBefore'),('with_code',{ACCESS:True},'WorkerCode'),('after_clear',{RADIO:True},'WorkerAfter')]:
 add('underground_worker_'+name,(UG,10,10),UG+'_Text_'+marker,flags=flags)
add('underground_gate_requires_access',(UG,30,2),UG+'_Text_BasementGateClosed',direction='RIGHT',step=True)
add('underground_gate_accepts_access',(UG,30,2),None,direction='RIGHT',step=True,flags={ACCESS:True},dest=UB)
add('silver_requires_access',(UB,16,10),UB+'_Text_SilverBefore')
add('warehouse_requires_silver_win',(UB,29,2),UB+'_Text_WarehouseGateClosed',direction='LEFT',step=True,flags={ACCESS:True})
add('warehouse_opens_after_silver',(UB,29,2),None,direction='LEFT',step=True,flags={ACCESS:True},trainers={'SILVER_UNDERGROUND':True},dest=WH)
guards=['WAREHOUSE_GRUNT_A','WAREHOUSE_GRUNT_B','WAREHOUSE_SCIENTIST']
for missing in guards:
 add('director_requires_'+missing.lower(),director,WH+'_Text_DirectorBefore',flags={ACCESS:True},trainers={n:n!=missing for n in guards})
add('director_rescued_after_three_guards',director,WH+'_Text_DirectorRescued',flags={ACCESS:True},trainers={n:True for n in guards},expect_flags={DIRECTOR:True})
add('director_waits_for_final_broadcast',director,WH+'_Text_DirectorWaiting',flags={ACCESS:True,DIRECTOR:True})
add('director_full_tm_does_not_revoke_rescue',director,WH+'_Text_DirectorFull',flags={RADIO:True,DIRECTOR:True},items={'ITEM_TM11':999})
add('director_tm_retry_after_full_bag',director,WH+'_Text_DirectorAfter',marker_para=1,flags={RADIO:True,DIRECTOR:True,SEA:False,RAY:False},items={'ITEM_TM11':998},expect_flags={RTM:True},delta={'ITEM_TM11':1})
add('director_tm_not_reissued',director,WH+'_Text_DirectorAfter',marker_para=1,flags={RADIO:True,DIRECTOR:True,RTM:True,SEA:False,RAY:False})
add('director_reports_unresolved_hoenn_storm',director,WH+'_Text_DirectorHoennStorm',marker_para=1,flags={RADIO:True,DIRECTOR:True,RTM:True,SEA:True,RAY:False})
add('director_acknowledges_actual_ray_rescue',director,WH+'_Text_DirectorHoennCalm',marker_para=1,flags={RADIO:True,DIRECTOR:True,RTM:True,SEA:True,RAY:True})
add('final_studio_requires_ariana',(F4,29,2),F4+'_Text_UpperGateClosed',direction='LEFT',step=True,flags={DIRECTOR:True})
add('final_studio_opens_after_ariana',(F4,29,2),None,direction='LEFT',step=True,flags={DIRECTOR:True},trainers={'ARIANA_RADIO':True},dest=F5)
add('archer_requires_real_director',archer,F5+'_Text_ArcherBefore',trainers={'ARIANA_RADIO':True})
add('archer_requires_ariana',archer,F5+'_Text_ArcherBefore',flags={DIRECTOR:True})
add('archer_saved_win_stops_signal',archer,F5+'_Text_ArcherAfter',flags={DIRECTOR:True},trainers={'ARIANA_RADIO':True,'ARCHER':True},expect_flags={RADIO:True})
assert len(cases)==35,len(cases)
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='radio-native-events-') as td:
  for c in cases:
   path=Path(td)/(c['name']+'.sav');prepared=fixture(path,c)
   with ReadOnlyEmu(str(rom),str(path),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    interaction(e,c);after=snapshot(e)
    assert after['flags']==existing_flags(before,c),(c['name'],'story flags',after['flags'],existing_flags(before,c))
    assert after['trainers']==before['trainers'],(c['name'],'trainer records changed without battle')
    for item in ITEMS:assert after['items'][item]==before['items'][item]+c.get('delta',{}).get(item,0),(c['name'],item)
    assert_preserved(before,after,c['name'])
    assert after['pc']==bytes(prepared.blocks['storage'])
    if c.get('dest'):
     m=map_info(c['dest']);assert e.location()[:2]==(m['group'],m['num']),(c['name'],'wrong native warp',e.location())
    e.shot(str(out/(c['name']+'.png')),scale=3)
    saved=flash_reload(e,c['name'])
    row={'case':c['name'],'dialogue':c['marker'],'save':saved,'party_pc_dex_preserved':True,'forced_memory_writes':0,'forced_outcomes':0}
    results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==len(cases)
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,'original_files_unchanged':True,'forced_memory_writes':0,'forced_outcomes':0},indent=2))
