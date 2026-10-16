#!/usr/bin/env python3
"""Blackthorn native QA; original SAV read-only and native inputs only."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_blackthorn_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='2a96b6d26b6f0abbb7a6cc2444ef887cf5e709d8f2373bd2698b086e3d17d032'
exec(compile(_boot_text,str(_boot),'exec'),globals())

cases=[]
def add(name,where,marker,**kw):cases.append(dict(name=name,where=where,marker=marker,**kw))
R44='JohtoRoute44';B2='IcePath_B2F';GYM='BlackthornCity_Gym';DEN='DragonDen_1F';SHRINE='DragonDen_Shrine'
keeper=(B2,10,18);clair=(GYM,7,7);elder=(SHRINE,6,7)
add('route44_closed_before_radio',(R44,0,16),R44+'_Text_WestGateClosed',direction='RIGHT',step=True,flags={RADIO:False})
add('route44_open_consumes_coord_event',(R44,0,16),None,direction='RIGHT',step=True,open_gate=True)
add('waterfall_keeper_requires_radio',keeper,B2+'_Text_WaterfallBefore',face_only=True,flags={RADIO:False})
add('waterfall_first_gift_is_hm07',keeper,B2+'_Text_WaterfallNew',face_only=True,expect_flags={WF:True},delta={'ITEM_HM07':1})
add('waterfall_duplicate_in_bag_is_tm50',keeper,B2+'_Text_WaterfallAlternate',face_only=True,items={'ITEM_HM07':1},expect_flags={WF:True},delta={'ITEM_TM50':1})
add('waterfall_duplicate_in_pc_is_tm50',keeper,B2+'_Text_WaterfallAlternate',face_only=True,pc_hm07=1,expect_flags={WF:True},delta={'ITEM_TM50':1})
add('waterfall_kanto_receipt_is_tm50',keeper,B2+'_Text_WaterfallAlternate',face_only=True,kanto_waterfall_history=True,expect_flags={WF:True},delta={'ITEM_TM50':1})
add('waterfall_hoenn_receipt_is_tm50',keeper,B2+'_Text_WaterfallAlternate',face_only=True,hoenn_waterfall_history=True,expect_flags={WF:True},delta={'ITEM_TM50':1})
add('waterfall_owned_hm_and_full_alternate_keeps_receipt',keeper,B2+'_Text_WaterfallFull',face_only=True,items={'ITEM_HM07':999,'ITEM_TM50':999})
add('waterfall_alternate_full_then_retryable',keeper,B2+'_Text_WaterfallFull',face_only=True,kanto_waterfall_history=True,items={'ITEM_TM50':999})
add('waterfall_alternate_retry_after_full',keeper,B2+'_Text_WaterfallAlternate',face_only=True,kanto_waterfall_history=True,items={'ITEM_TM50':998},expect_flags={WF:True},delta={'ITEM_TM50':1})
add('waterfall_reward_not_reissued',keeper,B2+'_Text_WaterfallAfter',face_only=True,flags={WF:True})
add('clair_requires_pryce_badge',clair,GYM+'_Text_ClairBefore',flags={B7:False})
add('clair_requires_radio_rescue',clair,GYM+'_Text_ClairBefore',flags={RADIO:False})
add('clair_saved_win_grants_trial_only',clair,GYM+'_Text_ClairTrial',trainers={'CLAIR':True},expect_flags={CLAIR:True})
add('clair_waits_for_elder_trial',clair,GYM+'_Text_ClairTrial',flags={CLAIR:True})
add('clair_acknowledges_final_badge',clair,GYM+'_Text_ClairAfter',flags={CLAIR:True,TRIAL:True,B8:True})
add('dragon_den_requires_clair',(DEN,15,6),DEN+'_Text_TrialGateClosed',step=True)
add('dragon_den_opens_after_actual_clair',(DEN,15,6),None,step=True,flags={CLAIR:True},dest=SHRINE)
add('elder_requires_clair_victory',elder,SHRINE+'_Text_DragonMasterBefore')
add('elder_no_answer_keeps_badge_locked',elder,SHRINE+'_Text_DragonMasterReflect',flags={CLAIR:True},answer='NO')
add('elder_yes_awards_badge_and_tm02',elder,SHRINE+'_Text_DragonMasterAfter',flags={CLAIR:True},answer='YES',expect_flags={TRIAL:True,B8:True,CTM2:True},delta={'ITEM_TM02':1})
add('elder_full_tm_keeps_new_badge',elder,SHRINE+'_Text_DragonMasterFull',flags={CLAIR:True},answer='YES',items={'ITEM_TM02':999},expect_flags={TRIAL:True,B8:True})
add('elder_reward_retry_without_new_battle',elder,SHRINE+'_Text_DragonMasterAfter',flags={CLAIR:True,TRIAL:True,B8:True},items={'ITEM_TM02':998},expect_flags={CTM2:True},delta={'ITEM_TM02':1})
add('elder_tm_not_reissued',elder,SHRINE+'_Text_DragonMasterAfter',flags={CLAIR:True,TRIAL:True,B8:True,CTM2:True})
assert len(cases)==25
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='blackthorn-native-events-') as td:
  for c in cases:
   path=Path(td)/(c['name']+'.sav');prepared=fixture(path,c)
   with ReadOnlyEmu(str(rom),str(path),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    interaction(e,c)
    if c.get('open_gate'):
     native_step(e,'RIGHT');assert e.location()[2:]==(2,16),'open coordinate event retriggered'
    after=snapshot(e)
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
