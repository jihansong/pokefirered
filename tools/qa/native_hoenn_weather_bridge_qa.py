#!/usr/bin/env python3
"""Original Route119 Aqua bridge guards block both lanes before Weather rescue and clear afterward."""
from pathlib import Path
import hashlib,re
qa=Path('tools/qa/native_strength_rock_puzzle_qa.py');text=qa.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='ab57a60e8f4961c318c0b975863c0ac36075f3e7556f363ae508b702928a3841'
prefix=text.split('e=None\ntry:',1)[0];assert prefix!=text
cases=['blocked-upper','blocked-lower','clear-upper','clear-lower',
 'legacy-badge-upper','legacy-badge-lower','legacy-win-upper','legacy-win-lower']
prefix,n=re.subn(r'cases=\[.*?\]\nassert head.count','cases='+repr(cases)+'\nassert head.count',prefix,count=1,flags=re.S);assert n==1
exec(compile(prefix,str(qa),'exec'))
protected_before=dict(before)
M='Route119';clear=not a.case.startswith('blocked-');y=33 if a.case.endswith('upper') else 34
weather_clear=a.case.startswith('clear-');legacy_badge=a.case.startswith('legacy-badge-');legacy_win=a.case.startswith('legacy-win-')
WT=TT=MT='TRAINER_HOENN_WINONA_1'
hf=re.findall(r'^#define\s+(FLAG_(?:HIDE_)?HOENN_\w+)\b',Path('include/constants/flags_hoenn_story.h').read_text(),re.M)
flags=list(dict.fromkeys(storyflags+hf))
report.update(mode='native-original-weather-bridge-'+a.case,stages=[],
 fixture='original six-party/PC/genuine Pika copied unchanged into an eligible temporary map fixture',
 scope='Both original Aqua-blocked lanes and existing completed Gym progress only; no whole Hoenn completion claim')
original_count=source.party_count();assert original_count==6
po=off('sb1.playerParty');original_party=bytes(source.sb1[po:po+600])
original_pika=original_starter_copy(source);assert original_party[100:200]==original_pika
assert sha(Path('data/layouts/HoennRoute119/map.bin').read_bytes())=='f6c948a0fb90925afce408b4bf1742ba56e9e6c95ffb899a348d563d1ba5f47d'
j=map_info(M)['json']
guards=[]
for y0 in (33,34):
 rows=[(i+1,o) for i,o in enumerate(j['object_events']) if (o['x'],o['y'])==(13,y0)]
 assert len(rows)==1;localid,o=rows[0]
 assert o['elevation']==4 and o['movement_type']=='MOVEMENT_TYPE_FACE_RIGHT'
 assert o['trainer_type']=='TRAINER_TYPE_NONE' and o['script']==M+'_TYWeather_BridgeGuard'+str(y0-32)
 assert o['flag']=='FLAG_TEMP_'+str(y0-21)
 assert o['graphics_id']!='OBJ_EVENT_GFX_VAR_0','bridge guard unexpectedly uses rival variable graphics'
 guards.append((localid,o))
def invariants():
 assert e.u8(syms['gPlayerPartyCount'])==original_count
 assert e.read(syms['gPlayerParty'],600)==original_party
 party_valid(original_party,original_count)
 assert e.read(syms['gPlayerParty']+100,100)==original_pika
 assert pc(e)==source_pc and e.read(e.ptr('gPokemonStoragePtr'),off('storage'))==source_storage
 assert digest_dex(blocks(e))==original_dex
def guard_visibility():
 for localid,o in guards:
  arow=object_by_id(localid,not clear)
  if not clear:
   assert arow['xy']==(o['x'],o['y']) and arow['gfx']==const(o['graphics_id'])
  assert blocks(e).flag(o['flag'])==clear
def cross_or_block():
 if clear:
  walk_tile('RIGHT');await_state(e.field_idle,1200);e.run(30)
  assert e.location()[2:]==(13,y),('cleared original Aqua tile still blocks bridge',e.location())
  previous=e.location();walk_tile('RIGHT');await_state(e.field_idle,1200);e.run(30)
  assert e.location()[2:]==(14,y)
  check_companion_visible(previous[2:],'original-bridge-clear')
  previous=e.location();walk_tile('RIGHT');await_state(e.field_idle,1200);e.run(30)
  assert e.location()[2:]==(15,y)
  check_companion_visible(previous[2:],'original-bridge-exit')
 else:
  e.hold('RIGHT');e.run(32);e.hold();e.run(40)
  assert e.location()[2:]==(12,y),'player crossed Aqua blockade before Weather rescue'
  e.press('A',hold=3,after=20);quiet_finish(e)
  assert e.location()[2:]==(12,y) and not e.in_battle()
  assert not blocks(e).flag('FLAG_HOENN_WEATHER_RESCUED')
  report['stages'].append({'label':'original-aqua-lookout-talk','battle_started':False})
 invariants();guard_visibility()
 report['stages'].append({'label':'original-bridge-physical-'+('clear' if clear else 'blocked'),'lane':y,'xy':e.location()[2:]})
def normalize_continue_object_flags(s):
 # Both route targets use the default Briney and Wanda map branches.
 assert M in ('Route110','Route119')
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
 with tempfile.TemporaryDirectory(prefix='native-weather-bridge-') as td:
  s=SaveFile(str(sav))
  for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
  s.set_var('VAR_REPEL_STEP_COUNT',250);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  s.set_flag('FLAG_HOENN_WEATHER_RESCUED',weather_clear)
  s.set_flag('FLAG_HOENN_BADGE06_GET',legacy_badge)
  s.set_trainer_beaten('TRAINER_HOENN_WINONA_1',legacy_win)
  report['temporary_bridge_eligibility']={'weather_rescued':weather_clear,'existing_badge6':legacy_badge,
   'actual_winona_victory':legacy_win,'original_source_save_changed':False}
  normalized=normalize_continue_object_flags(s)
  s.warp(M,12,y)
  fixture=Path(td)/'bridge-only-fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  assert loc_is(e,M) and e.location()[2:]==(12,y)
  assert not(e.u8(syms['gPlayerAvatar'])&SURF)
  invariants();initial_flags={f:blocks(e).flag(f) for f in flags}
  assert blocks(e).flag('FLAG_HOENN_WEATHER_RESCUED')==weather_clear
  assert blocks(e).flag('FLAG_HOENN_BADGE06_GET')==legacy_badge
  assert blocks(e).trainer_beaten('TRAINER_HOENN_WINONA_1')==legacy_win
  assert {f:initial_flags[f] for f in normalized}==normalized
  guard_visibility();probe_companion('bridge-before',('LEFT','RIGHT'))
  cross_or_block()
  assert {f:blocks(e).flag(f) for f in flags}==initial_flags
  native_save_reopen(e,source_pc);invariants();guard_visibility()
  assert loc_is(e,M) and e.location()[2:]==((15,y) if clear else (12,y))
  if not clear:cross_or_block()
  else:
   # Revisit the original guard tiles after cold Continue without setting any new progress.
   for x in (14,13,12):
    previous=walk_tile('LEFT');await_state(e.field_idle,1200);e.run(30)
    assert e.location()[2:]==(x,y);check_companion_visible(previous[2:],'bridge-clear-cold-return')
   cross_or_block()
  assert {f:blocks(e).flag(f) for f in flags}==initial_flags
  assert blocks(e).flag('FLAG_HOENN_WEATHER_RESCUED')==weather_clear
  assert blocks(e).flag('FLAG_HOENN_BADGE06_GET')==legacy_badge
  assert blocks(e).trainer_beaten('TRAINER_HOENN_WINONA_1')==legacy_win
  report['pass']=True;report['original_party600B_unchanged']=True;report['full_original_storage_unchanged']=True
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
