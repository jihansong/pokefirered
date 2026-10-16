#!/usr/bin/env python3
"""One natural Tohjo land-to-Surf-to-Waterfall-to-Route26 path; no repeated regional gate suite."""
from pathlib import Path
import hashlib,re,sys
sys.path.insert(0,str(Path.cwd()/'tools/qa'))
import gamedata as gd
gd.CONST_HEADERS+=['constants/flags_johto_story.h','constants/flags_hoenn_story.h'];gd._CONST_CACHE.clear()
qa=Path('tools/qa/native_waterfall_follower_qa.py');text=qa.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='740dbe6838a4c714c5ebf730b251e8cdc72d7668ead54a05dad685a41d691cee'
prefix=text.split('e=None\ntry:',1)[0];assert prefix!=text
pattern=r'head=head\.replace\(old,"choices=\[[^\n]*?\]",1\)'
prefix,n=re.subn(pattern,'head=head.replace(old,"choices=[\'a\']",1)',prefix,count=1);assert n==1
exec(compile(prefix,str(qa),'exec'))
protected_before=dict(before)
C='TohjoFalls';D='JohtoRoute26'
report.update(mode='native-johto-tohjo-natural-water-route',stages=[],route_steps=[],
 scope='One actual land/Surf/Waterfall/north-exit route; not full Johto or replay of completed Hoenn water cases')
j=map_info(C)['json'];assert len(j['warp_events'])==2
assert {(w['x'],w['y'],w['dest_map'],int(w['dest_warp_id'])) for w in j['warp_events']}=={
 (10,18,'MAP_JOHTO_ROUTE27',0),(10,3,'MAP_JOHTO_ROUTE26',0)}
assert not j['object_events'] and not j['coord_events']
layouts=Path('data/layouts/layouts.json')
layoutrows=__import__('json').loads(layouts.read_text())['layouts']
found=[v for v in layoutrows if v.get('id')==j['layout']];assert len(found)==1
terrain=Path(found[0]['blockdata_filepath'])
assert len(terrain.read_bytes())==1144 and sha(terrain.read_bytes())=='63ae01d21d19e54cb99ce1186a0c239ce56b4953d8279d73a0721f24837fa875'
report['original_terrain_sha256']=sha(terrain.read_bytes())
destination=map_info(D)['json'];assert (destination['warp_events'][0]['x'],destination['warp_events'][0]['y'])==(10,32)
assert not destination['object_events'] and not destination['coord_events']
johto_flags=re.findall(r'^#define\s+(FLAG_(?:HIDE_)?JOHTO_\w+)\b',Path('include/constants/flags_johto_story.h').read_text(),re.M)
hoenn_flags=re.findall(r'^#define\s+(FLAG_(?:HIDE_)?HOENN_\w+)\b',Path('include/constants/flags_hoenn_story.h').read_text(),re.M)
flags=list(dict.fromkeys(johto_flags+hoenn_flags+['FLAG_BADGE%02d_GET'%i for i in range(1,9)]+[
 'FLAG_SYS_GAME_CLEAR','FLAG_RECEIVED_STARTER_PIKACHU']))
def phase_companion(previous,label,water):
 b,sp=companion_state();xy=struct.unpack_from('<hh',b,16)
 assert xy==(previous[0]+7,previous[1]+7),('native Pika did not follow previous path tile',label,xy,previous)
 assert not(int.from_bytes(b[:4],'little')&((1<<13)|(1<<14))) and not(e.u8(sp+0x3e)&4)
 assert bool(e.u8(syms['gPlayerAvatar'])&SURF)==water,('wrong native water/land phase',label)
 assert e.read(syms['gPlayerParty']+100,100)==original_pika
 report['follower_checks'].append({'label':label,'player_xy':list(e.location()[2:]),
  'follower_xy':[xy[0]-7,xy[1]-7],'water':water,'visible':True,'sprite_active':True})
 photo(e,'tohjo-'+label)
def route_step(key,expected_map,expected_xy,water):
 previous=walk_tile(key);await_state(e.field_idle,1600);e.run(40)
 assert loc_is(e,expected_map) and e.location()[2:]==expected_xy,(key,e.location(),expected_map,expected_xy)
 invariants()
 phase_companion(previous[2:],'step-'+str(len(report['route_steps'])),water)
 report['route_steps'].append({'key':key,'before':previous,'after':e.location()})
def trace_ascent():
 steps=[];last=e.location();seen_task=active_task(e,'Task_UseWaterfall')
 for i in range(5000):
  safe(e);assert not e.in_battle()
  now=e.location()
  if now!=last:steps.append({'frame':e.frame(),'xy':list(now[2:])});last=now
  seen_task|=active_task(e,'Task_UseWaterfall')
  if (loc_is(e,C) and now[2:]==(10,6) and e.field_idle()
      and not active_task(e,'Task_UseWaterfall') and not e.u8(syms['gPlayerAvatar']+6)):
   e.run(40);break
  if i%8==0:e.press('A',hold=1,after=1)
  else:e.run(1)
 else:raise AssertionError(('actual Tohjo waterfall timed out',e.location(),steps[-12:]))
 assert len(steps)>=4 and seen_task,('native Tohjo ascent skipped movement/task',steps,seen_task)
 assert e.u8(syms['gPlayerAvatar'])&SURF and not(e.u8(syms['gPlayerAvatar'])&FORCED)
 phase_companion((10,7),'native-waterfall-top',True);invariants()
 report['stages'].append({'label':'native-tohjo-waterfall-ascent','steps':steps,'native_waterfall_task_seen':seen_task})
def normalize_continue_object_flags(s):
 # These two Johto maps use the existing default Briney/Wanda branches.
 assert C=='TohjoFalls'
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

def repel_guard(reference,M):
 # Exact candidate ARM tables; no species, order or level edits.
 assert hashlib.sha256(r.data).digest()==hashlib.sha256(Path(rom).read_bytes()).digest()
 lead=None
 for slot in range(reference.party_count()):
  m=reference.party_mon(slot);raw=bytes(m.blk[m.o:m.o+100])
  if struct.unpack_from('<H',raw,86)[0]>0 and not m.is_egg():
   assert not raw[19]&1,'native Repel lead is Bad Egg'
   checksum=sum(struct.unpack('<24H',b''.join(m.subs()[k] for k in 'GAEM')))&65535
   assert checksum==struct.unpack_from('<H',raw,28)[0],'native Repel lead checksum mismatch'
   lead={'slot':slot,'level':raw[84],'personality':m.personality,'otid':m.otid};break
 assert lead and lead['level']>0,'no healthy original Repel lead'
 mi=map_info(M);pair=(mi['group'],mi['num']);encounters=[]
 for table in ('gWildMonHeaders','gWildMonHeadersMorning','gWildMonHeadersNight'):
  assert table in syms and table in r.syms and syms[table]==r.syms[table],('candidate encounter symbol mismatch',table)
  found=[];ended=False
  for i in range(1024):
   raw=r.at(syms[table]+i*20,20);assert len(raw)==20
   g,n=raw[:2]
   if (g,n)==(255,255):ended=True;break
   if (g,n)!=pair:continue
   land=struct.unpack_from('<I',raw,4)[0];assert land and land%4==0
   info=r.at(land,8);assert len(info)==8 and info[0]>0
   mons=struct.unpack_from('<I',info,4)[0];assert mons and mons%2==0
   slots=r.at(mons,12*4);assert len(slots)==48
   assert all(0<slots[j*4]<=slots[j*4+1]<=100 for j in range(12))
   found.append({'table':table,'maximum_level':max(slots[j*4+1] for j in range(12)),'native_rate':info[0]})
  assert ended and len(found)==1,('native route wild header must be unique',table,found)
  encounters.extend(found)
 assert all(lead['level']>v['maximum_level'] for v in encounters),'original lead level does not guarantee Repel; do not edit party'
 report.setdefault('native_repel_guard',{})[M]={'fixture_lead':lead,'actual_candidate_encounters':encounters,'temporary_repel_steps':250}


def tohjo_diagnostic_abi():
 c="#include \"global.h\"\n#include \"fieldmap.h\"\n#include \"script.h\"\n#include \"constants/global.h\"\n#include <stddef.h>\nconst u32 qa_tohjo_offsets[] __attribute__((section(\".qa_tohjo_offsets\")))={offsetof(struct PlayerAvatar,flags),offsetof(struct PlayerAvatar,runningState),offsetof(struct PlayerAvatar,tileTransitionState),offsetof(struct PlayerAvatar,objectEventId),offsetof(struct PlayerAvatar,preventStep),offsetof(struct MapHeader,mapLayout),offsetof(struct MapHeader,regionMapSectionId),offsetof(struct MapHeader,mapType),offsetof(struct MapLayout,width),offsetof(struct MapLayout,height),offsetof(struct MapLayout,map),offsetof(struct MapLayout,primaryTileset),offsetof(struct MapLayout,secondaryTileset),offsetof(struct Tileset,isEmerald),offsetof(struct Tileset,metatileAttributes),offsetof(struct BackupMapLayout,Xsize),offsetof(struct BackupMapLayout,Ysize),offsetof(struct BackupMapLayout,map),offsetof(struct ObjectEvent,currentCoords),offsetof(struct ObjectEvent,previousCoords),offsetof(struct ObjectEvent,currentMetatileBehavior),offsetof(struct ScriptContext,mode),offsetof(struct ScriptContext,scriptPtr),sizeof(struct PlayerAvatar),sizeof(struct ObjectEvent),sizeof(struct ScriptContext),NUM_METATILES_IN_PRIMARY,EMERALD_NUM_METATILES_IN_PRIMARY,DIR_NORTH,T_NOT_MOVING,T_TILE_CENTER,PLAYER_AVATAR_FLAG_SURFING};\nconst struct ObjectEvent qa_tohjo_face __attribute__((section(\".qa_tohjo_face\")))={.facingDirection=15};\nconst struct ObjectEvent qa_tohjo_move __attribute__((section(\".qa_tohjo_move\")))={.movementDirection=15};\n"
 names=["avatar.flags","avatar.running","avatar.transition","avatar.object","avatar.prevent","header.layout","header.section","header.type","layout.width","layout.height","layout.map","layout.primary","layout.secondary","tileset.emerald","tileset.attrs","backup.width","backup.height","backup.map","obj.current","obj.previous","obj.behavior","script.mode","script.ptr","avatar.size","obj.size","script.size","metatiles.frlg","metatiles.emerald","direction.north","tile.notmoving","tile.center","avatar.surf"]
 tool=Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))/'bin'
 with tempfile.TemporaryDirectory(prefix='tohjo-native-read-abi-') as td:
  f=Path(td)/'abi.c';o=Path(td)/'abi.o';b=Path(td)/'abi.bin';f.write_text(c)
  subprocess.run([str(tool/'arm-none-eabi-gcc'),'-c','-w','-mthumb','-mabi=apcs-gnu','-march=armv4t',
   '-fcommon','-iquote','include','-DLEAFGREEN','-DREVISION=0','-DENGLISH','-DMODERN=1','-o',str(o),str(f)],check=True)
  subprocess.run([str(tool/'arm-none-eabi-objcopy'),'-O','binary','-j','.qa_tohjo_offsets',str(o),str(b)],check=True)
  raw=b.read_bytes();assert len(raw)==len(names)*4
  values=dict(zip(names,struct.unpack('<'+str(len(names))+'I',raw)))
  masks={}
  for label,section in (('face','.qa_tohjo_face'),('move','.qa_tohjo_move')):
   subprocess.run([str(tool/'arm-none-eabi-objcopy'),'-O','binary','-j',section,str(o),str(b)],check=True)
   raw=b.read_bytes();assert len(raw)==values['obj.size']
   nonzero=[(i,v) for i,v in enumerate(raw) if v];assert len(nonzero)==1
   masks[label]=nonzero[0]
  values['masks']=masks
 report['tohjo_read_abi']=values
 return values
tohjo_abi=tohjo_diagnostic_abi()
def tohjo_water_snapshot(label):
 q=input_snapshot(label);g,n,x,y=e.location();q['location']=[g,n,x,y]
 def u32_at(p):return e.u32(p)
 avatar=syms['gPlayerAvatar'];raw=e.read(avatar,tohjo_abi['avatar.size'])
 q['avatar']={key:e.u8(avatar+tohjo_abi['avatar.'+key]) for key in ('flags','running','transition','object','prevent')}
 q['avatar']['raw']=raw.hex()
 ob=syms['gObjectEvents']+q['avatar']['object']*tohjo_abi['obj.size']
 b=e.read(ob,tohjo_abi['obj.size'])
 faceoff,facemask=tohjo_abi['masks']['face'];moveoff,movemask=tohjo_abi['masks']['move']
 face=(b[faceoff]&facemask)//(facemask&-facemask);movement=(b[moveoff]&movemask)//(movemask&-movemask)
 q['player_object']={'raw':b.hex(),'facing_direction':face,'movement_direction':movement,
  'north_facing':face==tohjo_abi['direction.north'],'north_movement':movement==tohjo_abi['direction.north'],
  'current':list(struct.unpack_from('<hh',b,tohjo_abi['obj.current'])),
  'previous':list(struct.unpack_from('<hh',b,tohjo_abi['obj.previous'])),
  'current_behavior':b[tohjo_abi['obj.behavior']]}
 h=syms['gMapHeader'];layout=e.u32(h+tohjo_abi['header.layout'])
 assert 0x02000000<=layout<0x03008000 or 0x08000000<=layout<0x0a000000,hex(layout)
 width=e.u32(layout+tohjo_abi['layout.width']);height=e.u32(layout+tohjo_abi['layout.height'])
 base=e.u32(layout+tohjo_abi['layout.map'])
 primary=e.u32(layout+tohjo_abi['layout.primary']);secondary=e.u32(layout+tohjo_abi['layout.secondary'])
 split=tohjo_abi['metatiles.emerald'] if e.u8(primary+tohjo_abi['tileset.emerald']) else tohjo_abi['metatiles.frlg']
 q['layout']={'address':hex(layout),'size':[width,height],'map_pointer':hex(base),
  'primary':hex(primary),'secondary':hex(secondary),'primary_is_emerald':e.u8(primary+tohjo_abi['tileset.emerald']),
  'secondary_is_emerald':e.u8(secondary+tohjo_abi['tileset.emerald']),'primary_count':split,
  'section':e.u8(h+tohjo_abi['header.section']),'map_type':e.u8(h+tohjo_abi['header.type'])}
 backups=[name for name in ('VMap','gBackupMapLayout') if name in syms]
 assert len(backups)==1,('native map buffer symbol',backups)
 vm=syms[backups[0]];vw=e.u32(vm+tohjo_abi['backup.width']);vh=e.u32(vm+tohjo_abi['backup.height'])
 vbase=e.u32(vm+tohjo_abi['backup.map'])
 q['map_buffer']={'symbol':backups[0],'size':[vw,vh],'pointer':hex(vbase)}
 q['tiles']={}
 for label,tx,ty in (('current',x,y),('north_front',x,y-1)):
  assert 0<=tx<width and 0<=ty<height and 0<=tx+7<vw and 0<=ty+7<vh
  original=e.u16(base+2*(ty*width+tx));dynamic=e.u16(vbase+2*((ty+7)*vw+tx+7))
  tile=dynamic&0x3ff;ts=primary if tile<split else secondary;index=tile if tile<split else tile-split
  attrs=e.u32(ts+tohjo_abi['tileset.attrs']);attr=e.u32(attrs+index*4)
  q['tiles'][label]={'xy':[tx,ty],'rom_raw':hex(original),'live_raw':hex(dynamic),
   'metatile_id':tile,'collision':(dynamic>>10)&3,'elevation':dynamic>>12,
   'attributes_pointer':hex(attrs),'attributes_raw':hex(attr),'behavior':attr&0x1ff}
 q['badges']={flag:blocks(e).flag(flag) for flag in ('FLAG_JOHTO_BADGE04_GET','FLAG_JOHTO_BADGE08_GET','FLAG_BADGE07_GET','FLAG_HOENN_BADGE08_GET')}
 q['party_count']=e.u8(syms['gPlayerPartyCount'])
 mons=[]
 for i in range(q['party_count']):
  monraw=e.read(syms['gPlayerParty']+i*100,100);m=Mon(bytearray(monraw),0)
  mons.append({'slot':i,'species':m.species(),'hp':struct.unpack_from('<H',monraw,86)[0],'moves':list(struct.unpack('<4H',m.subs()['A'][:8]))})
 q['actual_party']=mons
 q['quest_log_state']=e.u8(syms['gQuestLogState']) if 'gQuestLogState' in syms else None
 q['script_contexts']={}
 for name in ('sGlobalScriptContext','sImmediateScriptContext'):
  if name in syms:
   p=syms[name];ptr=e.u32(p+tohjo_abi['script.ptr'])
   q['script_contexts'][name]={'mode':e.u8(p+tohjo_abi['script.mode']),'pointer':hex(ptr),
    'pointer_names':[name for name,address in syms.items() if address==ptr]}
 return q

def tohjo_trace_last_up():
 samples=[tohjo_water_snapshot('after-natural-approach-before-extra-UP')]
 e.hold()
 for i in range(3):
  e.run(1);samples.append(tohjo_water_snapshot('pre-UP-release-%d'%i))
 e.hold('UP')
 try:
  for i in range(3):
   e.run(1);samples.append(tohjo_water_snapshot('extra-UP-held-%d'%i))
 finally:e.hold()
 for i in range(24):
  e.run(1);samples.append(tohjo_water_snapshot('extra-UP-after-release-%d'%i))
 report['tohjo_extra_up_trace']=samples
 print(json.dumps({'tohjo_extra_up_trace':samples}),flush=True)

_tohjo_native_use_a=use_a
def use_a():
 if not (loc_is(e,C) and e.location()[2:]==(10,11)):return _tohjo_native_use_a()
 report['ui_stage']='Tohjo-waterfall-native-A-prompt'
 report['tohjo_prompt_before']=tohjo_water_snapshot('before-fresh-A')
 samples=[];press_count=0;original_press=e.press
 def traced_press(key,hold=3,after=20):
  nonlocal press_count
  press_count+=1
  e.hold(key)
  try:
   for i in range(hold):
    e.run(1)
    if key=='A':
     samples.append(tohjo_water_snapshot('A-press-%d-held-frame-%d'%(press_count,i)))
  finally:e.hold()
  e.run(after)
  if key=='A':samples.append(tohjo_water_snapshot('A-press-%d-after-release'%press_count))
  if len(samples)>72:samples[48:]=samples[-24:]
 e.press=traced_press
 try:
  photo(e,'tohjo-waterfall-before-native-A')
  _tohjo_native_use_a()
  report['tohjo_native_prompt_seen']=True
 finally:
  e.press=original_press
  report['tohjo_prompt_input_trace']=samples
  report['tohjo_prompt_after']=tohjo_water_snapshot('after-native-prompt-attempt')
  photo(e,'tohjo-waterfall-after-native-A')
  print(json.dumps({'tohjo_prompt_before':report['tohjo_prompt_before'],'tohjo_prompt_input_trace':samples,
   'tohjo_prompt_after':report['tohjo_prompt_after']}),flush=True)

e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-johto-tohjo-route-') as td:
  s=SaveFile(str(sav));original_pika=original_starter_copy(s)
  s.fast_battles();s.keep_party(1)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
  s.set_var('VAR_REPEL_STEP_COUNT',250);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  for f in ('FLAG_JOHTO_BADGE04_GET','FLAG_JOHTO_BADGE08_GET','FLAG_JOHTO_RADIO_TOWER_CLEARED','FLAG_SYS_GAME_CLEAR'):
   assert f in flags;s.set_flag(f,True)
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  mon=s.party_mon(0);mon.set_otid(owner);mon.set_starter_bit(False);mon.set_snagged(False)
  mon.set_species(const('SPECIES_LAPRAS'),rom=r);sub=mon.subs();sub['E'][:6]=bytes(6);sub['A'][:]=bytes(12)
  for i,name in enumerate(('MOVE_SURF','MOVE_WATERFALL')):
   mid=const(name);struct.pack_into('<H',sub['A'],i*2,mid)
   sub['A'][8+i]=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  struct.pack_into('<I',sub['M'],4,struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30))
  mon.put_subs(sub);mon.blk[mon.o+19]=(mon.blk[mon.o+19]&~5)|2;mon.set_held(0);mon.make_strong(100,rom=r)
  po=off('sb1.playerParty');s.sb1[po+100:po+200]=original_pika;s.sb1[off('sb1.playerPartyCount')]=2
  expected_party=bytes(s.sb1[po:po+600]);assert expected_party[100:200]==original_pika
  normalized=normalize_continue_object_flags(s)
  repel_guard(s,C);repel_guard(s,D)
  s.warp(C,10,17)
  fixture=Path(td)/'tohjo-eligible-fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  assert loc_is(e,C) and e.location()[2:]==(10,17) and not(e.u8(syms['gPlayerAvatar'])&SURF)
  invariants();initial_flags={f:blocks(e).flag(f) for f in flags}
  assert {f:initial_flags[f] for f in normalized}==normalized
  companion_state()
  # This is an actual shoreline interaction; fixture starts on land.
  e.press('UP',hold=1,after=20);assert e.location()[2:]==(10,17)
  use_a()
  await_state(lambda:loc_is(e,C) and e.location()[2:]==(10,16) and e.field_idle()
   and e.u8(syms['gPlayerAvatar'])&SURF and not e.u8(syms['gPlayerAvatar']+6),3000,'A')
  e.run(40);invariants();phase_companion((10,17),'native-shore-to-surf',True)
  report['stages'].append({'label':'land-to-native-Surf','player_xy':[10,16],'water_avatar':True})
  for y in range(15,10,-1):route_step('UP',C,(10,y),True)
  assert e.location()[2:]==(10,11)
  tohjo_trace_last_up();assert e.location()[2:]==(10,11)
  use_a();trace_ascent()
  native_save_reopen(e,source_pc);invariants()
  assert loc_is(e,C) and e.location()[2:]==(10,6) and e.u8(syms['gPlayerAvatar'])&SURF
  probe_companion('tohjo-top-cold')
  # Step to land; the normal dismount completes before checking the shore.
  previous=walk_tile('UP');await_state(e.field_idle,1600);e.run(40)
  assert loc_is(e,C) and e.location()[2:]==(10,5) and not(e.u8(syms['gPlayerAvatar'])&SURF)
  invariants();companion_state();report['stages'].append({'label':'native-Surf-to-land','player_xy':[10,5]})
  route_step('UP',C,(10,4),False)
  previous=walk_tile('UP')
  await_state(lambda:(loc_is(e,D) and e.field_idle()) or
   (loc_is(e,C) and e.location()[2:]==(10,3) and e.field_idle()),2000)
  if loc_is(e,C):
   assert e.location()[2:]==(10,3)
   # Native arrow warps act on the next outward input, just as original cave exits.
   e.press('UP',hold=3,after=20)
  await_state(lambda:loc_is(e,D) and e.field_idle(),3000);e.run(40)
  assert e.location()[2:] in ((10,32),(10,31)),('Route26 warp destination changed',e.location())
  report['stages'].append({'label':'native-Tohjo-north-exit','arrived_xy':list(e.location()[2:]),'RAM_warp':False})
  if e.location()[2:]==(10,32):route_step('UP',D,(10,31),False)
  route_step('LEFT',D,(9,31),False);route_step('RIGHT',D,(10,31),False)
  assert {f:blocks(e).flag(f) for f in flags}==initial_flags
  native_save_reopen(e,source_pc);invariants()
  assert loc_is(e,D) and e.location()[2:]==(10,31) and not(e.u8(syms['gPlayerAvatar'])&SURF)
  route_step('LEFT',D,(9,31),False);route_step('RIGHT',D,(10,31),False)
  assert {f:blocks(e).flag(f) for f in flags}==initial_flags
  report['pass']=True;report['full_original_storage_unchanged']=True
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
