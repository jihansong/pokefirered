#!/usr/bin/env python3
"""Blackthorn native QA; original SAV read-only and native inputs only."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_blackthorn_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='2a96b6d26b6f0abbb7a6cc2444ef887cf5e709d8f2373bd2698b086e3d17d032'
exec(compile(_boot_text,str(_boot),'exec'),globals())

import ast
_battle_path=Path(__file__).with_name('johto_blackthorn_native_battles.py')
_battle_text=_battle_path.read_text()
assert hashlib.sha256(_battle_text.encode()).hexdigest()=='bef8b0f3910e74b9f0913f7d9657fb50b78298f0ee009200ba84650e4b8ebccf'
assert _battle_text.count('\nTEAMS=')==1 and _battle_text.count('\nresults=[]\n')==1
exec(compile('TEAMS='+_battle_text.split('\nTEAMS=',1)[1].split('\nresults=[]\n')[0],str(_battle_path),'exec'),globals())
gd.FIELDS['pokemon.hp']=('Pokemon','hp')
gd.FIELDS['pokemon.maxHP']=('Pokemon','maxHP')
gd.FIELDS['pokemon.status']=('Pokemon','status')
gd._OFFSETS=None
def warp_native_result(source,target,where):
 s=SaveFile(str(source));party=bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
 pc=bytes(s.blocks['storage']);dex=[s.dex_state(i) for i in range(1,387)]
 flag_bytes=bytes(s.sb1[off('sb1.flags'):off('sb1.vars')]);sb2_before=bytes(s.sb2)
 trainers={n:s.trainer_beaten('TRAINER_JOHTO_'+n) for n in ACTORS}
 s.warp(*where);s.save(str(target));check=SaveFile(str(target))
 assert party==bytes(check.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
 assert pc==bytes(check.blocks['storage']) and dex==[check.dex_state(i) for i in range(1,387)]
 assert flag_bytes==bytes(check.sb1[off('sb1.flags'):off('sb1.vars')]),'position-only QA warp changed story flags'
 assert trainers=={n:check.trainer_beaten('TRAINER_JOHTO_'+n) for n in ACTORS}
 expected_sb2=bytearray(sb2_before);expected_sb2[off('sb2.specialSaveWarpFlags')]|=1
 assert bytes(check.sb2)==bytes(expected_sb2),'QA warp changed cross-region story/trainer/player data'
 return check
def dialog_stage(source,target,where,c):
 assert not target.exists();prepared=warp_native_result(source,target,where)
 with ReadOnlyEmu(str(rom),str(target),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
  interaction(e,c);after=snapshot(e)
  assert after['flags']==existing_flags(before,c),(c['name'],'story flags')
  assert after['trainers']==before['trainers'],(c['name'],'trainer record changed without battle')
  for item in ITEMS:assert after['items'][item]==before['items'][item]+c.get('delta',{}).get(item,0),(c['name'],item)
  if c.get('heal'):
   for field in ['pc','party_count','dex','pc_hm','pc_hm3','pc_hm02','pc_hm04','pc_hm07']:assert after[field]==before[field],(c['name'],field)
   party_identity(before,after,c['name'])
   for i in range(after['party_count']):
    old=before['party'][i*100:(i+1)*100];new=after['party'][i*100:(i+1)*100]
    assert struct.unpack_from('<H',new,off('pokemon.hp'))[0]==struct.unpack_from('<H',new,off('pokemon.maxHP'))[0]
    assert struct.unpack_from('<I',new,off('pokemon.status'))[0]==0
    a=Mon(bytearray(old),0).subs()['A'];b=Mon(bytearray(new),0).subs()['A']
    assert a[:8]==b[:8],'Nurse changed moves'
    for j in range(4):
     if struct.unpack_from('<H',b,j*2)[0]!=const('MOVE_NONE'):assert b[8+j]>=a[8+j] and b[8+j]>0
  else:assert_preserved(before,after,c['name'])
  if c.get('dest'):
   m=map_info(c['dest']);assert e.location()[:2]==(m['group'],m['num']),(c['name'],'native destination',e.location())
  e.shot(str(out/(c['name']+'.png')),scale=3);saved=flash_reload(e,c['name'])
  return {'case':c['name'],'native_dialogue':c['marker'],'native_nurse_heal':bool(c.get('heal')),
   'save':saved,'forced_story_flags':0,'forced_trainer_flags':0,'forced_memory_writes':0}
def nurse(name):
 return ('dialog',('BlackthornCity_PokemonCenter_1F',7,4),
  {'name':name,'marker':'Text_RestoredPkmnToFullHealth','face_only':True,'heal':True})
R44='JohtoRoute44';B2='IcePath_B2F';GYM='BlackthornCity_Gym';DEN='DragonDen_1F';SHRINE='DragonDen_Shrine'
steps=[
 ('dialog',(R44,0,16),{'name':'chain_radio_clear_opens_east_road','marker':None,'step':True,'direction':'RIGHT'}),
 ('dialog',(R44,5,19),{'name':'chain_east_road_context','marker':R44+'_Text_Warden'}),
 ('battle',POSITIONS['WILTON'],'WILTON'),
 ('battle',POSITIONS['VANCE'],'VANCE'),
 ('dialog',(B2,10,18),{'name':'chain_waterfall_reward','marker':None,'face_only':True,'expect_flags':{WF:True}}),
 nurse('chain_heal_before_blackthorn_trainers'),
 ('battle',POSITIONS['ALLEN'],'ALLEN'),
 ('battle',POSITIONS['FRAN'],'FRAN'),
 nurse('chain_heal_before_clair'),
 ('battle',POSITIONS['CLAIR'],'CLAIR'),
 ('dialog',(DEN,15,6),{'name':'chain_clair_opens_elder_den','marker':None,'step':True,'dest':SHRINE}),
 ('dialog',(SHRINE,6,7),{'name':'chain_elder_no_answer_keeps_badge_locked','marker':SHRINE+'_Text_DragonMasterReflect','answer':'NO'}),
 ('dialog',(SHRINE,6,7),{'name':'chain_elder_accepts_partner_care','marker':SHRINE+'_Text_DragonMasterAfter','answer':'YES','expect_flags':{TRIAL:True,B8:True,CTM2:True},'delta':{'ITEM_TM02':1}}),
 ('dialog',(GYM,7,7),{'name':'chain_clair_recognizes_elder_approval','marker':GYM+'_Text_ClairAfter'}),
 ('dialog',(SHRINE,6,7),{'name':'chain_elder_reward_not_duplicated','marker':SHRINE+'_Text_DragonMasterAfter'}),
 nurse('chain_finish_with_native_nurse')]
assert len(steps)==16
results=[]
try:
 initial=SaveFile(str(sav))
 assert initial.flag(B7) and initial.flag(RADIO) and all(initial.flag(f) for f in RADIO_FLAGS),'Requires actual q7 Radio Tower completion save'
 assert all(initial.trainer_beaten('TRAINER_JOHTO_'+n) for n in RADIO_ACTORS)
 assert all(not initial.flag(f) for f in BLACK_FLAGS),'Blackthorn chapter must begin unstarted'
 assert all(not initial.trainer_beaten('TRAINER_JOHTO_'+n) for n in BLACK_ACTORS)
 assert initial.item_count('ITEM_TM02')<999,'Native chain needs room for the final TM'
 initial_pc=bytes(initial.blocks['storage']);initial_items={n:initial.item_count(n) for n in ['ITEM_HM07','ITEM_TM50','ITEM_TM02']}
 hoenn={f:initial.flag(f) for f in [SEA,RAY,HWATER]};kanto={KWATER:initial.flag(KWATER)}
 duplicate=bool(initial.item_count('ITEM_HM07') or pc_count(initial,'ITEM_HM07') or kanto[KWATER] or hoenn[HWATER])
 reward=steps[4][2];gift='ITEM_TM50' if duplicate else 'ITEM_HM07'
 assert initial.item_count(gift)<999,'Native chain needs room for the Ice Path gift'
 reward['marker']=B2+('_Text_WaterfallAlternate' if duplicate else '_Text_WaterfallNew')
 reward['delta']={gift:1}
 with tempfile.TemporaryDirectory(prefix='blackthorn-same-native-save-chain-') as td:
  td=Path(td);previous=sav
  for i,(kind,where,c) in enumerate(steps):
   target=td/('step-'+str(i+1)+'.sav')
   if kind=='dialog':row=dialog_stage(previous,target,where,c)
   else:
    prepared=warp_native_result(previous,target,where)
    assert not prepared.trainer_beaten('TRAINER_JOHTO_'+c)
    with ReadOnlyEmu(str(rom),str(target),sym='') as e:row=battle_attempt(e,c,False,prepared,'chain_actual_'+c.lower()+'_win')
   previous=Path(row['save']['qa_save']);results.append(row);print(json.dumps(row),flush=True)
  final=SaveFile(str(previous))
  assert all(final.flag(f) for f in BLACK_FLAGS)
  assert all(final.trainer_beaten('TRAINER_JOHTO_'+n) for n in BLACK_ACTORS)
  assert final.item_count('ITEM_TM02')==initial_items['ITEM_TM02']+1
  for n in ['ITEM_HM07','ITEM_TM50']:assert final.item_count(n)==initial_items[n]+(1 if n==gift else 0)
  assert all(final.flag(f)==v for f,v in {**hoenn,**kanto}.items()),'Blackthorn fabricated a cross-region event receipt'
  assert bytes(final.blocks['storage'])==initial_pc
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==16
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'initial_save':str(sav),'initial_save_sha256':digest(sav.read_bytes()),
 'initial_context':'Actual q7 Radio Tower native completion save','stages':results,'all_pass':True,'same_native_save_chain':True,
 'qa_position_only_warps':16,'native_nurse_heals':3,'forced_story_flags_after_initial_fixture':0,'forced_trainer_flags_after_initial_fixture':0,
 'forced_memory_writes':0,'forced_battle_outcomes':0,'cross_region_history_flags_unchanged':True,'johto_league_still_pending':True,
 'original_files_unchanged':True},indent=2))
