#!/usr/bin/env python3
"""Radio Tower native QA; original SAV remains read-only and all outcomes use game inputs."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_radio_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='bbb842feb5d4cd98813d057411e440d45fb8838126a5a550ff2e1be46f1993ed'
exec(compile(_boot_text,str(_boot),'exec'),globals())

import ast
_battle_path=Path(__file__).with_name('johto_radio_native_battles.py')
_battle_text=_battle_path.read_text()
assert hashlib.sha256(_battle_text.encode()).hexdigest()=='471241ba5e8709ec447d775cfb3e89cd1096f22c3de2dcaca8832c46fc8f8ede'
assert _battle_text.count('\nTEAMS=')==1 and _battle_text.count('\nresults=[]\n')==1
exec(compile('TEAMS='+_battle_text.split('\nTEAMS=',1)[1].split('\nresults=[]\n')[0],str(_battle_path),'exec'),globals())
gd.FIELDS['pokemon.hp']=('Pokemon','hp')
gd.FIELDS['pokemon.maxHP']=('Pokemon','maxHP')
gd.FIELDS['pokemon.status']=('Pokemon','status')
gd._OFFSETS=None
def warp_native_result(source,target,where):
 s=SaveFile(str(source));party=bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
 pc=bytes(s.blocks['storage']);dex=[s.dex_state(i) for i in range(1,387)]
 flag_bytes=bytes(s.sb1[off('sb1.flags'):off('sb1.vars')])
 trainers={n:s.trainer_beaten('TRAINER_JOHTO_'+n) for n in ACTORS}
 s.warp(*where);s.save(str(target));check=SaveFile(str(target))
 assert party==bytes(check.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
 assert pc==bytes(check.blocks['storage']) and dex==[check.dex_state(i) for i in range(1,387)]
 assert flag_bytes==bytes(check.sb1[off('sb1.flags'):off('sb1.vars')]),'position-only QA warp changed story flags'
 assert trainers=={n:check.trainer_beaten('TRAINER_JOHTO_'+n) for n in ACTORS}
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
   for field in ['pc','party_count','dex','pc_hm','pc_hm3','pc_hm02','pc_hm04']:assert after[field]==before[field],(c['name'],field)
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
 return ('dialog',('GoldenrodCity_PokemonCenter_1F',7,4),
  {'name':name,'marker':'Text_RestoredPkmnToFullHealth','face_only':True,'heal':True})
F1='GoldenrodCity_RadioTower_1F'
F3='GoldenrodCity_RadioTower_3F'
F4='GoldenrodCity_RadioTower_4F'
UG='GoldenrodUnderground'
WH='GoldenrodWarehouse'
steps=[
 nurse('chain_prepare_with_native_nurse'),
 ('dialog',(F1,3,10),{'name':'chain_broadcast_alarm','marker':F1+'_Text_BroadcastClerkAlarm'}),
 ('dialog',(F1,13,3),{'name':'chain_enter_studios','marker':None,'step':True,'direction':'LEFT','dest':'GoldenrodCity_RadioTower_2F'}),
 ('battle',POSITIONS['RADIO_GRUNT_A'],'RADIO_GRUNT_A'),
 ('battle',POSITIONS['RADIO_GRUNT_B'],'RADIO_GRUNT_B'),
 ('battle',POSITIONS['RADIO_SCIENTIST'],'RADIO_SCIENTIST'),
 nurse('chain_heal_after_lower_studios'),
 ('battle',POSITIONS['PETREL_RADIO'],'PETREL_RADIO'),
 ('dialog',(UG,30,2),{'name':'chain_code_opens_basement','marker':None,'step':True,'direction':'RIGHT','dest':'GoldenrodUnderground_Basement'}),
 ('battle',POSITIONS['SILVER_UNDERGROUND'],'SILVER_UNDERGROUND'),
 ('battle',POSITIONS['WAREHOUSE_GRUNT_A'],'WAREHOUSE_GRUNT_A'),
 ('battle',POSITIONS['WAREHOUSE_GRUNT_B'],'WAREHOUSE_GRUNT_B'),
 ('battle',POSITIONS['WAREHOUSE_SCIENTIST'],'WAREHOUSE_SCIENTIST'),
 ('dialog',(WH,16,18),{'name':'chain_rescue_real_director','marker':WH+'_Text_DirectorRescued','expect_flags':{DIRECTOR:True}}),
 nurse('chain_heal_before_executives'),
 ('dialog',(F3,29,2),{'name':'chain_director_opens_upper_studio','marker':None,'step':True,'direction':'RIGHT','dest':'GoldenrodCity_RadioTower_4F'}),
 ('battle',POSITIONS['ARIANA_RADIO'],'ARIANA_RADIO'),
 ('dialog',(F4,29,2),{'name':'chain_ariana_opens_transmitter','marker':None,'step':True,'direction':'LEFT','dest':'GoldenrodCity_RadioTower_5F'}),
 ('battle',POSITIONS['ARCHER'],'ARCHER'),
 ('dialog',(WH,16,18),{'name':'chain_director_reward','marker':WH+'_Text_DirectorAfter','expect_flags':{RTM:True},'delta':{'ITEM_TM11':1}}),
 ('dialog',(F1,3,10),{'name':'chain_normal_broadcast_returns','marker':F1+'_Text_BroadcastClerkAfter'})]
assert len(steps)==21
results=[]
try:
 # --sav must be the final q6 native chapter-chain save, never an invented completion fixture.
 initial=SaveFile(str(sav))
 assert all(initial.flag(f) for f in MAHO_FLAGS if f!=RADIO),'Requires q6 native Badge7/HQ completion save'
 assert not initial.flag(RADIO) and all(not initial.flag(f) for f in RADIO_FLAGS),'Radio chapter must begin unstarted'
 assert all(initial.trainer_beaten('TRAINER_JOHTO_'+n) for n in ['HQ_GUARD_A','HQ_GUARD_B','HQ_SCIENTIST','PETREL','ARIANA','PRYCE'])
 assert all(not initial.trainer_beaten('TRAINER_JOHTO_'+n) for n in RADIO_ACTORS)
 initial_pc=bytes(initial.blocks['storage']);initial_tm11=initial.item_count('ITEM_TM11')
 hoenn={f:initial.flag(f) for f in [SEA,RAY]}
 # Choose the actual starting Hoenn report; no cross-region state is fabricated.
 reward=steps[-2][2]
 reward['marker_para']=1
 reward['marker']=WH+('_Text_DirectorHoennCalm' if hoenn[RAY] else ('_Text_DirectorHoennStorm' if hoenn[SEA] else '_Text_DirectorAfter'))
 with tempfile.TemporaryDirectory(prefix='radio-same-native-save-chain-') as td:
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
  assert all(final.flag(f) for f in [ACCESS,DIRECTOR,RTM,HSILVER,HPETREL,RADIO])
  assert all(final.trainer_beaten('TRAINER_JOHTO_'+n) for n in RADIO_ACTORS)
  assert all(final.flag(f)==v for f,v in hoenn.items()),'Radio fabricated a Hoenn crisis/rescue flag'
  assert final.item_count('ITEM_TM11')==initial_tm11+1
  assert bytes(final.blocks['storage'])==initial_pc
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==21
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'initial_save':str(sav),
 'initial_save_sha256':digest(sav.read_bytes()),
 'initial_context':'Actual q6 native chapter-chain Badge7 completion save',
 'stages':results,'all_pass':True,'same_native_save_chain':True,'qa_position_only_warps':21,
 'native_nurse_heals':3,'forced_story_flags_after_initial_fixture':0,'forced_trainer_flags_after_initial_fixture':0,
 'forced_memory_writes':0,'forced_battle_outcomes':0,'hoenn_crisis_flags_unchanged':True,'blackthorn_and_league_still_pending':True,
 'original_files_unchanged':True},indent=2))
