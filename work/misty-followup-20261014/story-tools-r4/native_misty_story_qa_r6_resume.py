#!/usr/bin/env python3
"""Native Misty species/Gym/heart QA. Fixtures and function hooks are explicit.

This does not claim a natural full-campaign traversal or actual mobile FPS.
Product ROM/ELF/SAV and every existing saves/*.sav are hash-guarded by the reused
native bootstrap. Prepared copies never replace the player's save.
"""
from pathlib import Path
import ast,hashlib,json,re,struct

basic_path=Path('tools/qa/native_misty_basic_qa.py')
q=basic_path.read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
assert q.count('results=[];rows=[]\n')==1
prefix=q.split('results=[];rows=[]\n')[0]
old='  for _ in range(20):'
assert prefix.count(old)==1
prefix=prefix.replace(old,"  for _ in range(60 if name=='CreateNPCTrainerParty' else 20):")
exec(compile(prefix,'<verified-Misty-native-definitions-only-with-creation-budget>','exec'))
if 'constants/field_effects.h' not in gd.CONST_HEADERS:
 gd.CONST_HEADERS.append('constants/field_effects.h')
gd._OFFSETS=None
checks=[];rows=[]
expected=[['STARMIE','GOLDUCK','SEADRA'],['STARMIE','GOLDUCK','SEADRA','POLITOED'],
 ['STARMIE','GOLDUCK','SEADRA','POLITOED','CORSOLA'],
 ['STARMIE','GOLDUCK','KINGDRA','POLITOED','CORSOLA','AZUMARILL'],
 ['STARMIE','GOLDUCK','KINGDRA','POLITOED','CORSOLA','AZUMARILL']]

def task(e,name):
 assert name in syms
 return [i for i in range(16) if e.u8(e.sym('gTasks')+40*i+4)
   and e.u32(e.sym('gTasks')+40*i)&~1==syms[name]&~1]

# Reuse only these already-executed real button helpers; never execute their suite.
pika_source=Path('tools/qa/native_misty_pika_dialogue_qa.py').read_text()
assert hashlib.sha256(pika_source.encode()).hexdigest()=='8e94e9a6b2c842fb83ea540d8c56254516b2c840d664e3b5093feda381ede343'
names={'turn_only','open_pika_A','answer_choice'}
nodes=[n for n in ast.parse(pika_source).body if isinstance(n,ast.FunctionDef) and n.name in names]
assert {n.name for n in nodes}==names
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<verified-real-PIKA-A-button-helpers>','exec'))

def add(name,**data):
 row=dict(case=name,pass_all=True,**data);checks.append(row);print(json.dumps(row),flush=True)

def prepared(name,mapname,x,y,joined,eligible=True,tm_received=True,tm_quantity=None):
 f=out/(name+'-fixture-QA-only.sav');assert not f.exists()
 s=SaveFile(str(sav));original=snapshot_save(s)
 s.warp(mapname,x,y)
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 s.set_var('VAR_MAP_SCENE_PALLET_TOWN_OAK',3)
 s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
 s.set_flag(join,joined);s.set_flag('FLAG_SYS_GAME_CLEAR',eligible)
 if joined:
  for trainer_name in ['TRAINER_SWIMMER_MALE_LUIS','TRAINER_PICNICKER_DIANA']:s.set_trainer_beaten(trainer_name,True)
 for flag_name in K:s.set_flag(flag_name,eligible)
 s.set_flag('FLAG_GOT_TM03_FROM_MISTY',tm_received)
 # Avoid re-arming a saved post-champion invitation in an unrelated fixture.
 s.set_var('VAR_TEMP_7',0)
 s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
 if tm_quantity is not None:s.set_item('ITEM_TM03',tm_quantity)
 s.save(str(f));assert snapshot_save(s)==original
 return f

def snapshot_save(s):
 return (bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]),
         s.party_count(),bytes(s.blocks['storage']),[s.dex_state(i) for i in range(1,387)])

def finish_dialogue(e):
 for _ in range(400):
  safe(e);assert not e.in_battle()
  if e.field_idle():break
  e.press('A',hold=2,after=12)
 else:raise AssertionError('dialogue failed to release native player control')
 settle(e);e.run(20)

def map_pair(name):
 m=map_info(name)
 return m['group'],m['num']

def leave_gym_by_real_keys(e):
 expected='798535cd49ca3db8ced17ec6fd47d1bd52da29b05df556725620b4924a080a09'
 assert hashlib.sha256(Path('data/layouts/CeruleanCity_Gym/map.bin').read_bytes()).hexdigest()==expected
 assert e.location()[2:]==(8,8)
 # The centre is a pool. Follow the real eastern walkway to the southern door.
 for key in ['RIGHT','UP','RIGHT','RIGHT','RIGHT','DOWN','DOWN','DOWN','LEFT','LEFT','LEFT']+['DOWN']*7:
  one_tile(e,key)
  assert not object_rows(e,3),'joined legacy leader respawned during movement'
 assert e.location()[2:]==(9,17)
 one_tile(e,'DOWN');one_tile(e,'LEFT')
 assert e.location()[2:]==(8,18)
 e.press('DOWN',hold=12,after=90);settle(e);e.run(20)
 assert e.location()[:2]==map_pair('CeruleanCity')

def heart_rows(e):
 cb=syms['SpriteCB_MistyHeart']&~1
 return [i for i in range(64) if e.u8(e.sym('gSprites')+68*i+0x3e)&1
    and e.u32(e.sym('gSprites')+68*i+0x1c)&~1==cb]

def heart_palette_count(e):
 assert 'sSpritePaletteTags' in syms
 return list(struct.unpack('<16H',e.read(e.sym('sSpritePaletteTags'),32))).count(0xD7F1)

def choose_misty(e):
 if call(e,'GetPlayerFacingDirection') != const('DIR_WEST'):
  turn_only(e,'LEFT')
 open_pika_A(e,True);answer_choice(e,True)
 for _ in range(240):
  safe(e);assert not e.in_battle()
  if e.u16(e.sym('gSpecialVar_LastTalked'))==253:return
  e.press('A',hold=2,after=10)
 raise AssertionError('real PIKA A choice did not select Misty companion')

def affectionate_A(e,stage):
 choose_misty(e)
 for _ in range(240):
  safe(e);assert not e.in_battle()
  if task(e,'Task_YesNoMenu_HandleInput'):break
  e.press('A',hold=2,after=10)
 else:raise AssertionError('real Misty training YES/NO was not reached')
 answer_choice(e,False)
 for _ in range(35):
  safe(e);assert not e.in_battle()
  if heart_rows(e):break
  e.run(1)
 else:raise AssertionError('training NO did not play native heart')
 e.shot(str(out/('affection-stage-'+str(stage)+'.png')),scale=3)
 # Observe the actual message expanded from the current stage's ROM text label.
 expected_text=r.at(syms['MistyCompanion_Text_Moment%d'%stage],512).split(b'\xff',1)[0]
 # No placeholders occur in the prefix before the first newline.
 prefix_text=expected_text.split(b'\xfe',1)[0]
 for _ in range(100):
  if e.read(e.sym('gStringVar4'),len(prefix_text))==prefix_text:break
  safe(e);e.run(1)
 else:raise AssertionError(('wrong actual regional affectionate message',stage))
 finish_dialogue(e)
 assert not heart_rows(e) and not call(e,'FieldEffectActiveListContains',const('FLDEFF_MISTY_HEART'))

prior=json.loads(Path('work/misty-followup-20261014/native-story-v4/story-progress.json').read_text())
assert prior['original_savs_unchanged'] and len(prior['checks'])==10 and all(q['pass_all'] for q in prior['checks'])
assert digest(rom.read_bytes())=='0a3a8d39f10f3284bbadf503a6baf80a7c3bed5cd54a27eeceb604beac18155a'
checks.extend(prior['checks'])
try:
 # True old-template Continue: create a native save, then alter only QA eligibility.
 gd.FIELDS.update({'legacy.templates':('SaveBlock1','objectEventTemplates'),'legacy.template.size':('ObjectEventTemplate',None),'legacy.template.local':('ObjectEventTemplate','localId'),'legacy.template.flag':('ObjectEventTemplate','flagId')});gd._OFFSETS=None
 f=prepared('legacy-gym-native-base','CeruleanCity_Gym',8,8,False,True)
 with Emu(str(rom),str(f),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30);before=record(e)
  assert len(object_rows(e,3))==1
  legacy_saved=flash_reload(e,'legacy-gym-base-native-save');same_records(e,before)
 legacy=out/'legacy-flag0-normal-Continue-QA-only.sav';assert not legacy.exists()
 s=SaveFile(legacy_saved['qa_save']);preserved=snapshot_save(s)
 n=len(map_info('CeruleanCity_Gym')['json']['object_events']);size=off('legacy.template.size');start=off('legacy.templates')
 leaders=[start+i*size for i in range(n) if s.sb1[start+i*size+off('legacy.template.local')]==3];assert len(leaders)==1
 leader=leaders[0];assert struct.unpack_from('<H',s.sb1,leader+off('legacy.template.flag'))[0]==const(join)
 struct.pack_into('<H',s.sb1,leader+off('legacy.template.flag'),0)
 s.set_flag(join,True);s.set_var('VAR_TEMP_1',1);s.sb2[off('sb2.specialSaveWarpFlags')]&=~1
 for trainer_name in ['TRAINER_SWIMMER_MALE_LUIS','TRAINER_PICNICKER_DIANA']:s.set_trainer_beaten(trainer_name,True)
 assert snapshot_save(s)==preserved;s.save(str(legacy))
 with Emu(str(rom),str(legacy),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30)
  assert e.location()[:2]==map_pair('CeruleanCity_Gym') and e.location()[2:]==(8,8)
  actual_legacy_flag=struct.unpack_from('<H',blocks(e).sb1,leader+off('legacy.template.flag'))[0]
  assert actual_legacy_flag in [0,const(join)]
  assert not object_rows(e,3) and len(object_rows(e,253))==1 and blocks(e).var('VAR_TEMP_1')==0
  leave_gym_by_real_keys(e);same_records(e,before)
  add('legacy-flag0-normal-Continue-no-duplicate-and-exit',native_base_save=legacy_saved,prepared_legacy_template_flag0=True,continue_game_warp_bit_cleared=True,old_cached_template_retained=(actual_legacy_flag==0),engine_refreshed_legacy_template=(actual_legacy_flag==const(join)),static_leader_absent=True,actual_walkway_exit=True)

 # A native visible follower is produced by normal three-step walking.
 f=prepared('heart','PalletTown',5,9,True)
 with Emu(str(rom),str(f),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30);before=record(e)
  for j in range(4):one_tile(e,'RIGHT');trail(e,'heart-walk-'+str(j),need_visible=j>=2)
  ms=object_rows(e,253);assert ms[0]['visible']
  state=e.save_state();base_pal=heart_palette_count(e)
  for attempt in range(3):
   call(e,'FieldEffectStart',const('FLDEFF_MISTY_HEART'))
   assert call(e,'FieldEffectActiveListContains',const('FLDEFF_MISTY_HEART'))
   assert len(heart_rows(e))==1 and heart_palette_count(e)==base_pal+1
   e.shot(str(out/('heart-repeat-'+str(attempt)+'.png')),scale=3)
   e.run(60)
   assert not heart_rows(e) and heart_palette_count(e)==base_pal
   assert not call(e,'FieldEffectActiveListContains',const('FLDEFF_MISTY_HEART'))
  same_records(e,before)
  add('native-heart-three-repeats-clean-resources',native_function_hook=True,palette_returns_to_baseline=True,lifetime_frames_at_most=60)
  # Absent companion is a native join-flag fixture; no object pointer is forged.
  flag(e,join,False);e.run(30);assert not object_rows(e,253)
  call(e,'FieldEffectStart',const('FLDEFF_MISTY_HEART'));e.run(2)
  assert not heart_rows(e) and not call(e,'FieldEffectActiveListContains',const('FLDEFF_MISTY_HEART'))
  assert heart_palette_count(e)==base_pal
  same_records(e,before)
  add('absent-companion-heart-negative-does-not-wait',temporary_native_join_flag=True)
  e.load_state(state)
  # Palette-full negative control changes the allocation bookkeeping in RAM only.
  tags=e.sym('sSpritePaletteTags');old_tags=e.read(tags,32)
  reserved=e.u8(e.sym('gReservedSpritePaletteCount'))
  assert 0<=reserved<16
  for i in range(reserved,16):
   if e.u16(tags+2*i)==0xffff:e.write(tags+2*i,struct.pack('<H',0xd800+i))
  call(e,'FieldEffectStart',const('FLDEFF_MISTY_HEART'))
  assert not call(e,'FieldEffectActiveListContains',const('FLDEFF_MISTY_HEART')) and not heart_rows(e)
  assert heart_palette_count(e)==base_pal
  e.write(tags,old_tags);e.load_state(state);same_records(e,before)
  add('full-palette-capacity-negative-does-not-wait',temporary_native_palette_table_fixture=True)
  # Failed sprite allocation uses real occupied OAM slots, not product save edits.
  free=[]
  for i in range(64):
   ptr=e.sym('gSprites')+68*i
   if not e.u8(ptr+0x3e)&1:
    raw=e.read(ptr,68);free.append((ptr,raw))
    dummy=bytearray(68);struct.pack_into('<I',dummy,0x1c,syms['SpriteCallbackDummy']|1)
    dummy[0x2c]=0x40 # animPaused; no NULL animation-table access in ContinueAnim.
    dummy[0x3e]=5 # inUse and invisible; callbacks are real inert engine callbacks.
    e.write(ptr,dummy)
  call(e,'FieldEffectStart',const('FLDEFF_MISTY_HEART'))
  assert not call(e,'FieldEffectActiveListContains',const('FLDEFF_MISTY_HEART')) and not heart_rows(e)
  assert heart_palette_count(e)==base_pal
  for ptr,raw in free:e.write(ptr,raw)
  e.load_state(state);same_records(e,before)
  add('full-sprite-capacity-negative-cleans-palette-and-wait',temporary_native_OAM_fixture=True)
  # Use the actual engine warp functions: no location or callback identity pokes.
  # This is a named native hook, not proof of an unassisted door traversal.
  call(e,'FieldEffectStart',const('FLDEFF_MISTY_HEART'));assert heart_rows(e)
  dest=map_pair('CeruleanCity')
  call(e,'SetWarpDestination',dest[0],dest[1],0xffffffff,31,22)
  call(e,'DoWarp');settle(e);e.run(30)
  assert e.location()[:2]==dest
  assert not heart_rows(e) and heart_palette_count(e)==0
  assert not call(e,'FieldEffectActiveListContains',const('FLDEFF_MISTY_HEART'))
  same_records(e,before)
  add('active-heart-native-engine-warp-cleanup',native_SetWarpDestination_and_DoWarp_hooks=True,
      map_identity_not_poked=True,no_owned_resources_or_wait_left=True)

 # Actual A -> PIKA reaction -> Misty YES -> training NO at every regional stage.
 f=prepared('affection','PalletTown',5,9,True)
 with Emu(str(rom),str(f),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30);before=record(e)
  for j in range(4):one_tile(e,'RIGHT');trail(e,'affection-walk-'+str(j),need_visible=j>=2)
  state=e.save_state()
  for stage in range(5):
   e.load_state(state)
   for i,growth_flag in enumerate(growth):flag(e,growth_flag,i<stage)
   affectionate_A(e,stage);same_records(e,before)
   add('actual-A-affection-stage-'+str(stage),pika_emotion_preserved=True,
       actual_A_and_yesno_only=True,native_heart=True,regional_text_from_ROM=True,
       temporary_native_growth_flags=True)
  saved=flash_reload(e,'affection-native-save')
  assert blocks(e).flag(join) and blocks(e).flag('FLAG_GOT_TM03_FROM_MISTY')
  # Continue resets transient positions, so clear the trail with real steps again.
  for j in range(4):one_tile(e,'LEFT');trail(e,'cold-affection-walk-'+str(j),need_visible=j>=2)
  turn_only(e,'RIGHT')
  # The ordinary helper assumes facing LEFT, so use a retained native state after
  # walking right to put both followers on the left of the player again.
  for j in range(4):one_tile(e,'RIGHT');trail(e,'cold-affection-return-'+str(j),need_visible=j>=2)
  affectionate_A(e,4);same_records(e,before)
  add('actual-A-affection-native-SAVE-cold-repeat',save=saved,actual_A_and_yesno_only=True)

 # Pending TM03 at its native stack capacity must fail, remain pending, then retry.
 f=prepared('pending-TM03-stack-full','PalletTown',5,9,True,tm_received=False,tm_quantity=999)
 with Emu(str(rom),str(f),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30);before=record(e)
  assert blocks(e).item_count('ITEM_TM03')==999
  assert not call(e,'CheckBagHasSpace',const('ITEM_TM03'),1),'fixture does not reach actual stack capacity'
  for j in range(4):one_tile(e,'RIGHT');trail(e,'TM03-walk-'+str(j),need_visible=j>=2)
  choose_misty(e);finish_dialogue(e)
  assert not blocks(e).flag('FLAG_GOT_TM03_FROM_MISTY') and blocks(e).item_count('ITEM_TM03')==999
  assert not e.in_battle();same_records(e,before)
  add('TM03-full-stack-actual-A-reward-stays-pending',prepared_max_stack_fixture=True,actual_A_choice=True)
  # A native item-removal fixture frees one unit; no source save or Pokemon edited.
  assert call(e,'RemoveBagItem',const('ITEM_TM03'),1)
  assert blocks(e).item_count('ITEM_TM03')==998
  choose_misty(e);finish_dialogue(e)
  assert blocks(e).flag('FLAG_GOT_TM03_FROM_MISTY') and blocks(e).item_count('ITEM_TM03')==999
  same_records(e,before)
  add('TM03-pending-native-removal-then-actual-A-retry',native_item_fixture=True,existing_reward_flag_on_success=True)
  affectionate_A(e,call(e,'MistyGetGrowthStage'))
  assert blocks(e).item_count('ITEM_TM03')==999
  saved=flash_reload(e,'TM03-retry-native-save')
  assert blocks(e).flag(join) and blocks(e).flag('FLAG_GOT_TM03_FROM_MISTY') and blocks(e).item_count('ITEM_TM03')==999
  same_records(e,before)
  add('TM03-repeat-no-duplicate-native-SAVE-cold',save=saved,no_duplicate_TM03=True)
finally:
 for f,h in originals.items():assert digest(f.read_bytes())==h,('original file changed',str(f))
 (out/'story-progress.json').write_text(json.dumps({'checks':checks,'trail_samples':rows,'original_savs_unchanged':True},indent=2))
(out/'story-result.json').write_text(json.dumps({'all_pass':True,'rom_sha256':digest(rom.read_bytes()),
 'elf_sha256':digest(elf.read_bytes()),'input_sav_sha256':originals[sav],'checks':checks,
 'temporary_native_ram_fixtures':True,'prepared_save_fixtures':True,'native_save_cold':True,
 'actual_A_affection_dialogue_tested':True,'TM03_bagfull_retry_tested':True,
 'full_campaign_complete':False,'actual_mobile_FPS_tested':False},indent=2))
