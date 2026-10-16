#!/usr/bin/env python3
"""Native Route110/119 rival battles, original triggers, shared Fly gifts and save retries."""
from pathlib import Path
import hashlib,re,sys
sys.path.insert(0,str(Path.cwd()/'tools/qa'))
import gamedata as gd
gd.FIELDS['rival.gender']=('SaveBlock2','playerGender');gd._OFFSETS=None
qa=Path('tools/qa/native_strength_rock_puzzle_qa.py');text=qa.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='ab57a60e8f4961c318c0b975863c0ac36075f3e7556f363ae508b702928a3841'
prefix=text.split('e=None\ntry:',1)[0];assert prefix!=text
cases=["110-may-win-1","110-may-win-2","110-may-win-3","110-brendan-win-2","110-may-loss-2","110-brendan-loss-2","119-may-win-1","119-may-win-2","119-brendan-win-1","119-may-loss-1","119-brendan-loss-1","110-gift-fresh","110-gift-bag","110-gift-history","110-gift-done","119-gift-fresh","119-gift-bag","119-gift-pc","119-gift-history","119-gift-done","119-gift-full-retry","110-before-birch","119-before-weather","119-before-birch","119-before-110-receipt","119-before-110-battle"]
prefix,n=re.subn(r'cases=\[.*?\]\nassert head.count','cases='+repr(cases)+'\nassert head.count',prefix,count=1,flags=re.S);assert n==1
assert prefix.count('assert not a.loss\n')==1;prefix=prefix.replace('assert not a.loss\n','',1)
exec(compile(prefix,str(qa),'exec'))
protected_before=dict(before)
parts=a.case.split('-');M='Route'+parts[0]
IS_GIFT=parts[1]=='gift';NEGATIVE=parts[1]=='before'
if IS_GIFT:state='-'.join(parts[2:]);gender='may';trigger=2 if M=='Route110' else 1
elif NEGATIVE:state='-'.join(parts[2:]);gender='may';trigger=2 if M=='Route110' else 1
else:gender,state,rawtrigger=parts[1:];trigger=int(rawtrigger)
a.loss=state=='loss';BATTLE=not IS_GIFT and not NEGATIVE
RECEIPT='FLAG_HOENN_GOT_RIVAL110_GIFT' if M=='Route110' else 'FLAG_HOENN_GOT_RIVAL_FLY_REWARD'
HISTORY='FLAG_GOT_ITEMFINDER' if M=='Route110' else 'FLAG_GOT_HM02'
GIFT='ITEM_ITEMFINDER' if M=='Route110' else 'ITEM_HM02';TM='ITEM_TM02'
TR='TRAINER_HOENN_'+gender.upper()+'_ROUTE_'+parts[0]+'_TORCHIC';WT=TT=MT=TR
RIVALS=['TRAINER_HOENN_'+g+'_ROUTE_'+r+'_TORCHIC' for r in ('110','119') for g in ('MAY','BRENDAN')]
EARLIER='TRAINER_HOENN_'+gender.upper()+'_ROUTE_110_TORCHIC'
catalog={'Route110':(['SPECIES_LUDICOLO','SPECIES_MAGCARGO','SPECIES_SWAMPERT'],[64,65,67],[272,219,260]),
 'Route119':(['SPECIES_PELIPPER','SPECIES_LUDICOLO','SPECIES_MAGCARGO','SPECIES_SWAMPERT'],[66,67,67,69],[279,272,219,260])}
enemy_names,enemy_levels,enemy_national=catalog[M]
enemy_species=[const(x) for x in enemy_names]
hf=re.findall(r'^#define\s+(FLAG_(?:HIDE_)?HOENN_\w+)\b',Path('include/constants/flags_hoenn_story.h').read_text(),re.M)
flags=list(dict.fromkeys(storyflags+hf+['FLAG_GOT_HM02','FLAG_GOT_ITEMFINDER']))
report.update(mode='native-hoenn-rival-progress-'+a.case,stages=[],trigger_steps=[],
 fixture='temporary native battle/gift fixture only; original six-party SAV and full PC storage untouched',
 scope='Route103-to-110 and Weather-to-119 progression; not complete Hoenn playthrough')
original_pika=original_starter_copy(source)
expected_count=1 if a.loss else 2
NPC=(34,54) if M=='Route110' else (25,32);NPC_ID=26 if M=='Route110' else 30
APPROACH=(32+trigger,57) if M=='Route110' else (24+trigger,30)
RETRY_AT=(34,55) if M=='Route110' else (25,31)
START=RETRY_AT if IS_GIFT and state!='done' else APPROACH
LAYOUT='Hoenn'+M
TERRAIN={'Route110':'53c4da783116c4b726989d9ebb872ee4cbfaea1e148b39a4e345471e60a3d6da',
 'Route119':'f6c948a0fb90925afce408b4bf1742ba56e9e6c95ffb899a348d563d1ba5f47d'}[M]
assert sha(Path('data/layouts/'+LAYOUT+'/map.bin').read_bytes())==TERRAIN
j=map_info(M)['json'];row=j['object_events'][NPC_ID-1]
assert (row['x'],row['y'],row['graphics_id'],row['flag'])==(*NPC,'OBJ_EVENT_GFX_VAR_0','FLAG_TEMP_11')
assert row['script']==M+'_TYRival_Interact' and row['trainer_type']=='TRAINER_TYPE_NONE'
assert [(c['x'],c['y'],c['var'],int(c['var_value'])) for c in j['coord_events']]==(
 [(33,56,'VAR_TEMP_0',0),(34,56,'VAR_TEMP_0',0),(35,56,'VAR_TEMP_0',0)] if M=='Route110' else
 [(25,31,'VAR_TEMP_0',0),(26,31,'VAR_TEMP_0',0)])
PO=off('sb1.pcItems');PN=const('PC_ITEMS_COUNT')
def pcitems(s):return bytes(s.sb1[PO:PO+PN*4])
def set_pc_gift(s,amount):
 item=const(GIFT)
 for i in range(PN):
  p=PO+i*4
  if struct.unpack_from('<H',s.sb1,p)[0]==item:struct.pack_into('<HH',s.sb1,p,0,0)
 if amount:
  empty=[PO+i*4 for i in range(PN) if struct.unpack_from('<H',s.sb1,PO+i*4)[0]==0]
  assert empty;struct.pack_into('<HH',s.sb1,empty[0],item,amount)
def raw_dex_arrays(b):
 n=off('dex.seen')-off('dex.owned')
 assert 49<=n<=64
 p=off('sb2.pokedex')
 return tuple(bytes(x) for x in [
  b.sb2[p+off('dex.owned'):p+off('dex.owned')+n],
  b.sb2[p+off('dex.seen'):p+off('dex.seen')+n],
  b.sb1[off('sb1.seen1'):off('sb1.seen1')+n],
  b.sb1[off('sb1.seen2'):off('sb1.seen2')+n]])
baseline_dex_bytes=raw_dex_arrays(source)
# Resolve the actual compiled table; preserve existing caught/seen bits.
national_tables=[n for n in ('sSpeciesToNationalPokedexNum','gSpeciesToNationalPokedexNum') if n in syms]
assert len(national_tables)==1,('candidate species-to-national table missing or ambiguous',national_tables)
national_table=syms[national_tables[0]]

for name,number in zip(enemy_names,enemy_national):
 assert struct.unpack('<H',r.at(national_table+2*(const(name)-1),2))[0]==number
revealed=set()
def dex_invariants():
 now=raw_dex_arrays(blocks(e));assert now[0]==baseline_dex_bytes[0],'caught records changed in rival trainer/gift event'
 added=[]
 for i in range(1,4):
  expected=bytearray(baseline_dex_bytes[i])
  for number in revealed:bit=number-1;expected[bit//8]|=1<<(bit%8)
  assert now[i]==bytes(expected),('new seen bits outside actually revealed rival party',i)
  added.append([bit+1 for bit in range(len(expected)*8)
   if now[i][bit//8] & ~baseline_dex_bytes[i][bit//8] & (1<<(bit%8))])
 report['dex_guard']={'caught_unchanged':True,'old_seen_preserved':True,
  'actual_revealed_national':sorted(revealed),'added_per_replica':added}
def invariants():
 now=e.read(syms['gPlayerParty'],600);assert e.u8(syms['gPlayerPartyCount'])==expected_count
 party_valid(now,expected_count)
 assert now[100:200]==original_pika,'genuine Pika record edited'
 assert pc(e)==source_pc and e.read(e.ptr('gPokemonStoragePtr'),off('storage'))==source_storage
 assert pcitems(blocks(e))==fixture_pc_items
 dex_invariants()
def current_story():
 b=blocks(e)
 return {f:b.flag(f) for f in flags},{t:b.trainer_beaten(t) for t in RIVALS},{
  v:b.var(v) for v in ('VAR_HOENN_SCENE_BIRCH','VAR_HOENN_SCENE_DEVON','VAR_HOENN_SCENE_WALLY','VAR_HOENN_STAGE1_PROGRESS')}
def story_invariants():
 f,t,v=current_story();oldf,oldt,oldv=initial_story
 assert {n:x for n,x in f.items() if n!=RECEIPT}=={n:x for n,x in oldf.items() if n!=RECEIPT}
 assert {n:x for n,x in t.items() if n!=TR}=={n:x for n,x in oldt.items() if n!=TR}
 assert v==oldv,'existing story progress was forced forward by rival/gift'
 assert t[TR]==(oldt[TR] or (BATTLE and not a.loss))
def counts():
 b=blocks(e);return b.item_count(GIFT),b.item_count(TM)
def assert_object(visible):
 o=object_by_id(NPC_ID,visible)
 if not visible:return
 assert o['xy']==NPC and o['gfx']==blocks(e).var('VAR_OBJ_GFX_ID_0')
 assert blocks(e).var('VAR_OBJ_GFX_ID_0')==expected_graphics
 return o
def fresh_step(key):
 previous=e.location();e.hold(key)
 try:
  for _ in range(100):
   safe(e);e.run(1)
   if e.location()!=previous:break
  else:raise AssertionError(('native rival approach blocked',key,previous))
 finally:e.hold()
 e.run(20);report['trigger_steps'].append({'key':key,'before':previous,'after':e.location(),'A_input':False})
def finish_script():
 quiet_finish(e);invariants();story_invariants()
def talk():
 turn='UP' if M=='Route110' else 'DOWN'
 prior=e.location();e.press(turn,hold=1,after=20);assert e.location()==prior
 e.press('A',hold=3,after=20);finish_script()
def probe_after_success():
 if expected_count==2:
  if M=='Route110':probe_companion('rival-gift-after',('LEFT','RIGHT'))
  else:probe_companion('rival-gift-after',('RIGHT','LEFT'))
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

old_fight_one_turn=fight_one_turn
def traced_fight(e,loss):
 enemy=e.read(syms['gEnemyParty'],600)
 species=[Mon(bytearray(enemy),i*100).species() for i in range(6)]
 levels=[enemy[i*100+84] for i in range(len(enemy_species))]
 assert species[:len(enemy_species)]==enemy_species and not any(species[len(enemy_species):])
 assert levels==enemy_levels,('actual rival levels do not match chapter growth',levels,enemy_levels)
 idx=e.u8(syms['gBattlerPartyIndexes']+1);assert idx<len(enemy_species)
 revealed.add(enemy_national[idx])
 report['actual_enemy_party']={'species':species[:len(enemy_species)],'levels':levels}
 return old_fight_one_turn(e,loss)
fight_one_turn=traced_fight
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-hoenn-rival-progress-') as td:
  s=SaveFile(str(sav));s.fast_battles();s.keep_party(1)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
  s.set_var('VAR_HAPPINESS_STEP_COUNTER',0);s.set_var('VAR_REPEL_STEP_COUNT',250)
  s.sb2[off('rival.gender')]=1 if gender=='brendan' else 0
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  mon=s.party_mon(0);mon.set_otid(owner);mon.set_starter_bit(False);mon.set_snagged(False)
  mon.set_species(const('SPECIES_MEWTWO'),rom=r);sub=mon.subs();sub['E'][:6]=bytes(6);sub['A'][:]=bytes(12)
  move_names=['MOVE_TACKLE'] if a.loss else ['MOVE_PSYCHIC','MOVE_ICE_BEAM','MOVE_THUNDERBOLT','MOVE_SHADOW_BALL']
  for i,name in enumerate(move_names):
   mid=const(name);struct.pack_into('<H',sub['A'],i*2,mid)
   sub['A'][8+i]=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  struct.pack_into('<I',sub['M'],4,struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30))
  mon.put_subs(sub);mon.blk[mon.o+19]=(mon.blk[mon.o+19]&~5)|2;mon.set_held(0);mon.make_strong(1 if a.loss else 100,rom=r)
  if a.loss:struct.pack_into('<H',mon.blk,mon.o+86,1)
  po=off('sb1.playerParty');s.sb1[po+100:po+200]=original_pika;s.sb1[off('sb1.playerPartyCount')]=expected_count
  assert bytes(s.sb1[po+100:po+200])==original_pika
  if a.loss:report['loss_fixture']={'one_weak_active_mon':True,'genuine_pika100B_copied_to_inactive_slot':True,'no_pika_battle_or_follower_claim':True}
  for t in RIVALS:s.set_trainer_beaten(t,False)
  s.set_var('VAR_HOENN_SCENE_BIRCH',2 if NEGATIVE and state=='birch' else 3)
  s.set_flag('FLAG_HOENN_GOT_RIVAL110_GIFT',M=='Route119' and not(NEGATIVE and state=='110-receipt'))
  s.set_flag('FLAG_HOENN_GOT_RIVAL_FLY_REWARD',False)
  s.set_flag('FLAG_HOENN_WEATHER_RESCUED',not(NEGATIVE and state=='weather'))
  if M=='Route119':s.set_trainer_beaten(EARLIER,not(NEGATIVE and state=='110-battle'))
  if IS_GIFT:s.set_trainer_beaten(TR,True)
  s.set_flag(HISTORY,IS_GIFT and state in ('history','full-retry'))
  s.set_item(GIFT,1 if IS_GIFT and state in ('bag','done') else 0)
  s.set_item(TM,999 if state=='full-retry' else 2 if state=='done' else 0)
  if IS_GIFT and state=='done':s.set_flag(RECEIPT,True)
  set_pc_gift(s,1 if IS_GIFT and state=='pc' else 0);fixture_pc_items=pcitems(s)
  normalized=normalize_continue_object_flags(s)
  before_counts=(s.item_count(GIFT),s.item_count(TM))
  s.warp(M,*START)
  fixture=Path(td)/'native-rival-fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  assert loc_is(e,M) and e.location()[2:]==START
  initial_story=current_story();invariants()
  assert {f:initial_story[0][f] for f in normalized}==normalized
  expected_graphics=const('OBJ_EVENT_GFX_RIVAL_BRENDAN_NORMAL' if gender=='brendan' else 'OBJ_EVENT_GFX_RIVAL_MAY_NORMAL')
  assert blocks(e).var('VAR_OBJ_GFX_ID_0')==expected_graphics,('native opposite-gender rival gfx wrong',gender,blocks(e).var('VAR_OBJ_GFX_ID_0'),expected_graphics)
  hidden=NEGATIVE or(IS_GIFT and state=='done')
  assert blocks(e).flag('FLAG_TEMP_11')==hidden
  assert blocks(e).var('VAR_TEMP_0')==int(hidden)
  assert_object(not hidden)
  if not IS_GIFT and not a.loss:
   pre_keys=('RIGHT','LEFT') if M=='Route119' or trigger==1 else ('LEFT','RIGHT')
   probe_companion('native-rival-before',pre_keys)
  if BATTLE:
   fresh_step('UP' if M=='Route110' else 'DOWN')
   assert report['trigger_steps'][-1]['A_input'] is False
   native_battle(e,TR,len(enemy_species));finish_script()
   if a.loss:
    assert not blocks(e).flag(RECEIPT) and counts()==before_counts
    assert revealed,'native rival loss never revealed an opponent'
    report['native_loss_no_reward']=True
   else:
    assert sorted(revealed)==sorted(enemy_national),'not every native rival opponent was faced'
    assert loc_is(e,M) and e.location()[2:]==RETRY_AT
    assert blocks(e).flag(RECEIPT) and counts()==(before_counts[0]+1,before_counts[1])
    assert_object(False);probe_after_success()
    report['original_coordinate_trigger_native_victory']=True
  elif NEGATIVE or state=='done':
   fresh_step('UP' if M=='Route110' else 'DOWN')
   quiet_finish(e);invariants();story_invariants()
   assert loc_is(e,M) and e.location()[2:]==((START[0],56) if M=='Route110' else (START[0],31))
   assert not e.in_battle() and counts()==before_counts
   assert blocks(e).flag(RECEIPT)==(state=='done')
   assert_object(False);report['story_gate_rejected']=NEGATIVE
  else:
   talk()
   if state=='full-retry':
    assert not blocks(e).flag(RECEIPT) and counts()==before_counts
    assert_object(True);native_save_reopen(e,source_pc);invariants();story_invariants();assert_object(True)
    e.close();e=None
    released=SaveFile(str(out/'qa-only-native-save.sav'))
    assert released.trainer_beaten(TR) and not released.flag(RECEIPT)
    released.set_item(TM,998);retry=Path(td)/'native-save-capacity-release-fixture.sav';released.save(str(retry));check_sectors(SaveFile(str(retry)))
    e=ReadOnlyEmu(str(rom),str(retry),sym='');e.syms=syms;e.boot_continue();settle(e);invariants()
    assert loc_is(e,M) and e.location()[2:]==RETRY_AT and counts()==(before_counts[0],998)
    talk();assert counts()==(before_counts[0],999)
    report['full_retry']={'actual_victory_kept':True,'after_native_SAVE_cold':True,'capacity_release_fixture_only':True,'native_bag_toss_tested':False}
   elif M=='Route110':
    assert counts()==(before_counts[0]+(state=='fresh'),before_counts[1]),('Itemfinder gift duplicated or missing',counts(),before_counts)
   else:
    assert counts()==(before_counts[0]+(state=='fresh'),before_counts[1]+(state!='fresh'))
   assert blocks(e).flag(RECEIPT);assert_object(False);probe_after_success()
  result_counts=counts();native_save_reopen(e,source_pc);invariants();story_invariants()
  assert counts()==result_counts
  if not a.loss:
   assert loc_is(e,M)
   assert_object(not(NEGATIVE or blocks(e).flag(RECEIPT)))
   if blocks(e).flag(RECEIPT):
    assert blocks(e).flag('FLAG_TEMP_11') and blocks(e).var('VAR_TEMP_0')==1
    if e.location()[2:]==RETRY_AT:
     probe_after_success()
    assert counts()==result_counts,'repeat movement granted duplicate gift'
  report['pass']=True;report['original_routes_unmodified']=True;report['genuine_pika_record_unchanged']=True
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
