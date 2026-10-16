#!/usr/bin/env python3
"""Native regional Strength/Rock Smash gates, original puzzles and genuine Pika."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/'tools/qa'))
import gamedata as gd
gd.FIELDS.update({'puzzle_obj':('ObjectEvent',None),
 'puzzle_obj.current':('ObjectEvent','currentCoords'),
 'puzzle_obj.localid':('ObjectEvent','localId')})
gd._OFFSETS=None
gd.CONST_HEADERS+=['constants/event_objects.h','constants/flags_johto_story.h','constants/flags_hoenn_story.h']
gd._CONST_CACHE.clear()
head=Path('tools/qa/hoenn_weather_space_native_qa.py').read_text().split('e=None\ntry:',1)[0]
old="choices=['weather-party','weather-pc','space']"
cases=['strength-a','strength-menu','rock-a','rock-menu',
 'strength-no-own-a','strength-no-own-menu','rock-no-own-a','rock-no-own-menu',
 'strength-no-move-a','rock-no-move-a',
 'strength-kanto-own','strength-kanto-foreign','strength-johto-own','strength-johto-foreign',
 'rock-kanto-own','rock-kanto-foreign','rock-johto-no-badge']
assert head.count(old)==1;head=head.replace(old,'choices='+repr(cases),1)
exec(compile(head,'tools/qa/hoenn_weather_space_native_qa.py','exec'))
assert not a.loss
report.update(mode='native-regional-puzzle-'+a.case,stages=[],
 fixture='temporary Lapras mover plus unedited original starter Pikachu; no source save changes',
 native_story_not_entire_regions=True)
import os,subprocess
qa_task_names=['Task_HandleChooseMonInput','Task_HandleSelectionMenuInput',
 'Task_ReturnToChooseMonAfterText','Task_CancelAfterAorBPress','Task_YesNoMenu_HandleInput']
tab=subprocess.check_output([str(Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))/
 'bin/arm-none-eabi-objdump'),'-t',str(elf)],text=True)
for line in tab.splitlines():
 p=line.split()
 if len(p)>=6 and re.fullmatch('[0-9a-fA-F]{8}',p[0]) and p[-1] in qa_task_names:
  sets.setdefault(p[-1],set()).add(int(p[0],16)&~1)
assert all(sets.get(n) for n in qa_task_names),'candidate native UI tasks missing'
avatar_source=re.sub(r'/\*.*?\*/|//[^\n]*','',Path('include/global.fieldmap.h').read_text(),flags=re.S)
enums=re.findall(r'enum\s*\{([^{}]*\bPLAYER_AVATAR_STATE_NORMAL\b[^{}]*)\}',avatar_source)
assert len(enums)==1 and '=' not in enums[0]
avatar_states=re.findall(r'\bPLAYER_AVATAR_STATE_[A-Z_]+\b',enums[0])
SURF=1<<avatar_states.index('PLAYER_AVATAR_STATE_SURFING')
assert re.search(r'#define\s+PLAYER_AVATAR_FLAG_SURFING\s+\(1\s*<<\s*PLAYER_AVATAR_STATE_SURFING\s*\)',avatar_source)
MOVE=const('MOVE_STRENGTH' if a.case.startswith('strength-') else 'MOVE_ROCK_SMASH')
M='VictoryRoad_B1F';ST='FLAG_SYS_USE_STRENGTH'
TEMP=['FLAG_TEMP_1'+x for x in '123456789ABCDEF']
storyflags=['FLAG_BADGE%02d_GET'%i for i in range(1,9)]
storyflags+=['FLAG_HOENN_BADGE%02d_GET'%i for i in range(1,9)]
johto_header=Path('include/constants/flags_johto_story.h').read_text()
johto_defined=set(re.findall(r'^\s*#define\s+(FLAG_JOHTO_BADGE\d\d_GET)\b',johto_header,re.M))
assert 'FLAG_JOHTO_BADGE03_GET' in johto_defined,'required Johto Strength badge missing'
storyflags+=['FLAG_JOHTO_BADGE%02d_GET'%i for i in range(1,9)
 if 'FLAG_JOHTO_BADGE%02d_GET'%i in johto_defined]
report['johto_badges_defined']=sorted(johto_defined)
storyflags+=['FLAG_RECEIVED_STARTER_PIKACHU']
flags=storyflags+[ST]+TEMP
source_storage=bytes(source.blocks['storage'][:off('storage')])
original_dex=digest_dex(source);expected_party=None
def palette_active_mask():
 c='#include "global.h"\n#include "palette.h"\nconst struct PaletteFadeControl qa_palette_active __attribute__((section(".qa_palette_mask"))) = {.active=1};\n'
 tool=Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))/'bin'
 with tempfile.TemporaryDirectory(prefix='palette-read-mask-') as td:
  f=Path(td)/'palette.c';o=Path(td)/'palette.o';b=Path(td)/'palette.bin';f.write_text(c)
  subprocess.run([str(tool/'arm-none-eabi-gcc'),'-c','-w','-mthumb','-mabi=apcs-gnu','-march=armv4t',
   '-fcommon','-iquote','include','-DLEAFGREEN','-DREVISION=0','-DENGLISH','-DMODERN=1','-o',str(o),str(f)],check=True)
  subprocess.run([str(tool/'arm-none-eabi-objcopy'),'-O','binary','-j','.qa_palette_mask',str(o),str(b)],check=True)
  raw=b.read_bytes()
 hits=[(i,v) for i,v in enumerate(raw) if v]
 assert len(hits)==1 and hits[0][1]&(hits[0][1]-1)==0,('palette active mask',raw.hex())
 report['palette_active_abi_mask']={'size':len(raw),'offset':hits[0][0],'mask':hits[0][1]}
 return hits[0]
fade_offset,fade_mask=palette_active_mask()
def fade_inactive():
 return not(e.u8(syms['gPaletteFade']+fade_offset)&fade_mask)
def ui_snapshot():
 tasks=[]
 for i in range(16):
  t=e.read(syms['gTasks']+i*40,40)
  if t[4]:
   fn=struct.unpack_from('<I',t)[0]&~1
   tasks.append({'slot':i,'function':hex(fn),'names':[n for n,addresses in sets.items() if fn in addresses],
    'cursor_data0':struct.unpack_from('<h',t,8)[0]})
 snapshot={'stage':report.get('ui_stage'),'tasks':tasks,'callback2':hex(e.callback2()),
  'fade_inactive':fade_inactive(),'start_cursor':e.u8(syms['sStartMenuCursorPos'])}
 if 'gPartyMenu' in syms:
  raw=e.read(syms['gPartyMenu'],20)
  snapshot['party_menu_raw']=raw.hex()
  snapshot['party_slot']=struct.unpack_from('<b',raw,9)[0]
  snapshot['party_mode_byte']=raw[8]
 p=e.ptr('sPartyMenuInternal') if 'sPartyMenuInternal' in syms else 0
 if 0x02000000<=p<0x03008000:
  n=e.u8(p+23)
  snapshot['menu_actions']=list(e.read(p+15,n)) if n<=8 else ['invalid',n]
 return snapshot
def await_state(pred,limit=2000,key=None):
 for i in range(limit):
  if pred():return
  safe(e);assert not e.in_battle(),'unexpected wild battle on repel route'
  if key and i%8==0:e.press(key,hold=1,after=1)
  else:e.run(1)
 report['ui_debug']=ui_snapshot()
 raise AssertionError(('native puzzle timeout',report.get('ui_stage'),e.location(),hex(e.callback2())))
def walk_tile(key):
 initial=e.location();e.hold(key)
 try:
  for _ in range(80):
   safe(e);assert not e.in_battle();e.run(1)
   if e.location()!=initial:break
  else:raise AssertionError(('one native step blocked',key,initial))
 finally:e.hold()
 e.run(40);safe(e)
 return initial
_localid_header=Path('include/constants/event_objects.h').read_text()
_follower_id=int(re.search(r'#define\s+LOCALID_FOLLOWER\s+(\d+)',_localid_header).group(1))
assert _follower_id==254
_pika_gfx=int(re.search(r'#define\s+OBJ_EVENT_GFX_PIKACHU\s+(\d+)',_localid_header).group(1))
assert _pika_gfx==120
assert not a.loss
report['follower_checks']=[]
def original_starter_copy(s):
 owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
 name=bytes(s.sb2[off('sb2.playerName'):off('sb2.playerName')+7]).split(b'\xff',1)[0]
 found=[]
 for i in range(s.party_count()):
  m=s.party_mon(i)
  if (m.species()==const('SPECIES_PIKACHU') and m.starter_bit()
      and m.otid==owner and m.ot_name_raw().split(b'\xff',1)[0]==name):
   raw=bytes(m.blk[m.o:m.o+100])
   assert not m.is_egg() and not(raw[19]&1)
   assert struct.unpack_from('<H',raw,86)[0]>0,'starter in source party is fainted'
   found.append((i,raw))
 assert len(found)==1,('expected one genuine live party starter',len(found))
 i,raw=found[0]
 report['follower_original']={'party_index':i,'personality':struct.unpack_from('<I',raw)[0],
  'otid':owner,'box_sha256':sha(raw[:80]),'copied_without_editing':True}
 return raw
def companion_state():
 rows=[]
 for i in range(16):
  b=e.read(syms['gObjectEvents']+i*36,36)
  if b[0]&1 and b[8]==_follower_id:rows.append((i,b))
 assert len(rows)==1,('active follower count',len(rows),e.location())
 i,b=rows[0];g,n,x,y=e.location()
 assert b[9]==n and b[10]==g,('follower map mismatch',list(b[8:11]),g,n)
 assert b[5]==_pika_gfx,'approved follower graphics replaced'
 assert b[4]<128
 sp=syms['gSprites']+b[4]*68
 assert e.u8(sp+0x3e)&1,'follower sprite inactive'
 return b,sp
def check_companion_visible(previous,label):
 b,sp=companion_state()
 xy=struct.unpack_from('<hh',b,16)
 assert xy==(previous[0]+7,previous[1]+7),('follower did not follow previous tile',xy,previous)
 assert not(int.from_bytes(b[:4],'little')&((1<<13)|(1<<14))),'follower hidden or off screen'
 assert not(e.u8(sp+0x3e)&4),'follower sprite invisible'
 assert not(e.u8(syms['gPlayerAvatar'])&SURF),'land puzzle used SURF avatar'
 mon=e.read(syms['gPlayerParty']+100,100);m=Mon(bytearray(mon),0)
 assert m.personality==report['follower_original']['personality']
 assert m.otid==report['follower_original']['otid'] and m.starter_bit()
 assert m.species()==const('SPECIES_PIKACHU') and struct.unpack_from('<H',mon,86)[0]>0
 photo(e,'follower-'+label+'-'+str(len(report['follower_checks'])))
 report['follower_checks'].append({'label':label,'map':e.location()[:2],
  'player_xy':e.location()[2:],'follower_xy':[xy[0]-7,xy[1]-7],
  'visible':True,'native_sprite_active':True,'avatar_flags':e.u8(syms['gPlayerAvatar'])})
def probe_companion(label,keys=('RIGHT','LEFT')):
 initial=e.location()
 companion_state()
 walk_tile(keys[0]);await_state(e.field_idle,600);e.run(20)
 delta={'RIGHT':(1,0),'LEFT':(-1,0),'UP':(0,-1),'DOWN':(0,1)}[keys[0]]
 assert e.location()==(initial[0],initial[1],initial[2]+delta[0],initial[3]+delta[1]),e.location()
 check_companion_visible(initial[2:],label+'-right')
 previous=e.location()[2:]
 walk_tile(keys[1]);await_state(e.field_idle,600);e.run(20)
 assert e.location()==initial,e.location()
 check_companion_visible(previous,label+'-left')

def invariants():
 assert e.read(e.ptr('gPokemonStoragePtr'),off('storage'))==source_storage,'full storage changed'
 assert pc(e)==source_pc
 assert e.u8(syms['gPlayerPartyCount'])==2
 now=e.read(syms['gPlayerParty'],600);party_valid(now,2)
 assert now==expected_party,'fixture party changed'
 assert digest_dex(blocks(e))==original_dex
 assert not e.u8(syms['gPlayerAvatar']+6),'player movement stayed locked'
def start_party():
 report['ui_stage']='open-start-party'
 assert e.field_idle()
 e.press('START',hold=3,after=60)
 n=e.u8(syms['sNumStartMenuItems']);order=list(e.read(syms['sStartMenuOrder'],n))
 assert 1 in order,order;target=order.index(1)
 for _ in range(n+1):
  if e.u8(syms['sStartMenuCursorPos'])==target:break
  e.press('DOWN',hold=3,after=12)
 assert e.u8(syms['sStartMenuCursorPos'])==target
 e.press('A',hold=3,after=20)
 report['ui_stage']='wait-party-choose-and-fade'
 await_state(lambda:active_task(e,'Task_HandleChooseMonInput')
  and (e.callback2()&~1)==(syms['CB2_UpdatePartyMenu']&~1) and fade_inactive())
 e.run(2)
 assert active_task(e,'Task_HandleChooseMonInput') and (e.callback2()&~1)==(syms['CB2_UpdatePartyMenu']&~1) and fade_inactive(),'party choose input attempted before stable UpdatePartyMenu'
 report['ui_stage']='select-lapras-context'
 e.press('A',hold=3,after=20)
 await_state(lambda:active_task(e,'Task_HandleSelectionMenuInput') and fade_inactive())
 p=e.ptr('sPartyMenuInternal');actions=list(e.read(p+15,e.u8(p+23)))
 matches=[option for option in actions if struct.unpack('<I',r.at(syms['sCursorOptions']+option*8,4))[0]==syms['gMoveNames']+MOVE*13]
 assert len(matches)==1,('native requested HM menu label absent or ambiguous',actions,matches)
 action=matches[0]
 assert (struct.unpack('<I',r.at(syms['sCursorOptions']+action*8+4,4))[0]&~1)==(syms['CursorCB_FieldMove']&~1),'requested HM label has wrong native callback'
 report['native_hm_cursor_option']=action
 for _ in range(actions.index(action)):e.press('DOWN',hold=3,after=12)
 report['ui_stage']='choose-waterfall-action'
 photo(e,'native-puzzle-menu');e.press('A',hold=3,after=20)
def reject_menu(badge_missing):
 start_party()
 target='Task_ReturnToChooseMonAfterText' if badge_missing else 'Task_CancelAfterAorBPress'
 await_state(lambda:active_task(e,target),1800)
 photo(e,'native-waterfall-menu-rejection')
 report['menu_rejection_task']=target
 await_state(e.field_idle,2400,'B')
def use_a():
 e.press('A',hold=3,after=20)
 await_state(lambda:active_task(e,'Task_YesNoMenu_HandleInput'),1600,'A')
 e.run(10);e.press('UP',hold=2,after=5);e.press('A',hold=2,after=5)

def object_rows():
 rows=[]
 g,n=e.location()[:2]
 for i in range(const('OBJECT_EVENTS_COUNT')):
  b=e.read(syms['gObjectEvents']+i*off('puzzle_obj'),off('puzzle_obj'))
  if b[0]&1 and (b[10],b[9])==(g,n):
   x,y=struct.unpack_from('<hh',b,off('puzzle_obj.current'))
   rows.append({'slot':i,'id':b[off('puzzle_obj.localid')],'gfx':b[5],
    'xy':(x-7,y-7),'sprite':b[4]})
 assert len(rows)<=const('OBJECT_EVENTS_COUNT')
 return rows
def object_by_id(localid,required=True):
 z=[q for q in object_rows() if q['id']==localid]
 assert len(z)==(1 if required else 0),('puzzle object count',localid,z,object_rows())
 return z[0] if z else None
def no_player_overlap():
 player=e.location()[2:]
 obstacles=[q for q in object_rows() if q['gfx'] in
 (const('OBJ_EVENT_GFX_PUSHABLE_BOULDER'),const('OBJ_EVENT_GFX_ROCK_SMASH_ROCK'))]
 assert all(q['xy']!=player for q in obstacles),('player overlapped restored obstacle',player,obstacles)
 report['stages'].append({'label':'no-player-obstacle-overlap','player':player,'obstacles':obstacles})
def native_push():
 previous=e.location();assert previous[2:]==(4,8),previous
 before=object_by_id(10);assert before['xy']==(4,7) and before['gfx']==const('OBJ_EVENT_GFX_PUSHABLE_BOULDER')
 walk_tile('UP');await_state(e.field_idle,1800);e.run(30)
 assert e.location()[2:]==(4,7),('native one-tile push',e.location())
 after=object_by_id(10);assert after['xy']==(4,6),('boulder did not move natively',after)
 check_companion_visible(previous[2:],'native-strength-push')
 no_player_overlap();invariants()
 report['stages'].append({'label':'native-boulder-push','before':before,'after':after})
def check_story_unchanged(initial):
 assert {f:blocks(e).flag(f) for f in storyflags}==initial,'story badge flags changed through HM'
def set_badges(s):
 for f in storyflags+TEMP+[ST]:s.set_flag(f,False)
 s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
 if '-no-own-' in a.case:
  for i in range(1,9):s.set_flag('FLAG_BADGE%02d_GET'%i,True)
 elif '-kanto-own' in a.case:s.set_flag('FLAG_BADGE04_GET' if MOVE==const('MOVE_STRENGTH') else 'FLAG_BADGE06_GET',True)
 elif '-kanto-foreign' in a.case:
  for i in range(1,9):s.set_flag('FLAG_HOENN_BADGE%02d_GET'%i,True)
 elif '-johto-own' in a.case:s.set_flag('FLAG_JOHTO_BADGE03_GET',True)
 elif '-johto-foreign' in a.case:
  for i in range(1,9):s.set_flag('FLAG_BADGE%02d_GET'%i,True)
 elif '-johto-no-badge' in a.case:pass
 else:s.set_flag('FLAG_HOENN_BADGE04_GET' if MOVE==const('MOVE_STRENGTH') else 'FLAG_HOENN_BADGE03_GET',True)
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-regional-puzzle-qa-') as td:
  s=SaveFile(str(sav));original_pika=original_starter_copy(s)
  s.fast_battles();s.keep_party(1);s.set_var('VAR_REPEL_STEP_COUNT',250)
  s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);set_badges(s)
  boundary='-kanto-' in a.case or '-johto-' in a.case
  strength=MOVE==const('MOVE_STRENGTH')
  if '-kanto-' in a.case:s.warp('PalletTown',10,10)
  elif '-johto-' in a.case:
   m=map_info('NewBarkTown')['json']
   lab=[z for z in m['warp_events'] if z['dest_map']=='MAP_NEW_BARK_TOWN_ELMS_LAB']
   assert len(lab)==1
   s.warp('NewBarkTown',lab[0]['x'],lab[0]['y']+2)
  else:
   j=map_info(M)['json'];assert len(j['object_events'])==21,'original 14 obstacles not yet applied'
   assert j['object_events'][9]['graphics_id']=='OBJ_EVENT_GFX_PUSHABLE_BOULDER'
   assert (j['object_events'][9]['x'],j['object_events'][9]['y'])==(4,7)
   assert j['object_events'][14]['graphics_id']=='OBJ_EVENT_GFX_ROCK_SMASH_ROCK'
   assert (j['object_events'][14]['x'],j['object_events'][14]['y'])==(19,5)
   s.warp(M,4 if strength else 18,8 if strength else 5)
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  m=s.party_mon(0);m.set_otid(owner);m.set_starter_bit(False);m.set_snagged(False)
  m.set_species(const('SPECIES_LAPRAS'),rom=r)
  sub=m.subs();sub['E'][:6]=bytes(6);sub['A'][:]=bytes(12)
  move_names=['MOVE_STRENGTH','MOVE_ROCK_SMASH','MOVE_SURF','MOVE_TACKLE']
  if '-no-move-' in a.case:move_names.remove('MOVE_STRENGTH' if strength else 'MOVE_ROCK_SMASH')
  for i,name in enumerate(move_names):
   mid=const(name);struct.pack_into('<H',sub['A'],i*2,mid)
   sub['A'][8+i]=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  struct.pack_into('<I',sub['M'],4,struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30))
  m.put_subs(sub);m.blk[m.o+19]=(m.blk[m.o+19]&~5)|2;m.set_held(0);m.make_strong(100,rom=r)
  po=off('sb1.playerParty');s.sb1[po+100:po+200]=original_pika
  s.sb1[off('sb1.playerPartyCount')]=2;expected_party=bytes(s.sb1[po:po+600])
  assert expected_party[100:200]==original_pika
  assert bytes(s.blocks['storage'][:off('storage')])==source_storage
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  initial=e.location();invariants();initial_story={f:blocks(e).flag(f) for f in storyflags}
  assert not(e.u8(syms['gPlayerAvatar'])&SURF),'puzzle fixture must be land'
  if boundary:
   deny=a.case.endswith('foreign')
   reject_menu(deny)
   assert e.location()==initial
   assert not blocks(e).flag(ST)
   report['native_region_badge_boundary']={'badge_denied':deny,'location':initial}
  else:
   assert loc_is(e,M) and initial[2:]==((4,8) if strength else (18,5))
   objid=10 if strength else 15
   expected_gfx=const('OBJ_EVENT_GFX_PUSHABLE_BOULDER' if strength else 'OBJ_EVENT_GFX_ROCK_SMASH_ROCK')
   target=object_by_id(objid);assert target['gfx']==expected_gfx
   probe_companion('before-hm',('DOWN','UP') if strength else ('LEFT','RIGHT'))
   e.press('UP' if strength else 'RIGHT',hold=1,after=20)
   assert e.location()==initial,'turn moved through inactive obstacle'
   if '-no-own-' in a.case or '-no-move-' in a.case:
    if a.case.endswith('-menu'):reject_menu(True)
    else:e.press('A',hold=3,after=20);quiet_finish(e)
    assert e.location()==initial and not blocks(e).flag(ST)
    assert object_by_id(objid)['xy']==target['xy']
    assert not blocks(e).flag('FLAG_TEMP_19')
    probe_companion('rejected-still-follows',('DOWN','UP') if strength else ('LEFT','RIGHT'))
    report['native_hm_rejection']=True
   else:
    if a.case.endswith('-a'):use_a()
    else:start_party()
    quiet_finish(e)
    if strength:
     assert blocks(e).flag(ST),'native Strength did not enable pushing'
     native_push()
     native_save_reopen(e,source_pc);invariants();no_player_overlap()
     assert object_by_id(10)['xy']==(4,6),'saved pushed boulder position lost on cold continue'
     probe_companion('strength-push-cold',('DOWN','UP'))
     # Native cold Continue retains the active boulder's saved coordinates.
     # Once it despawns outside view, the original engine resets it to its template.
     # The original lower corridor needs one additional original boulder pushed
     # from (9,10) to (10,10); no object, map or player coordinates are written.
     for key in ['DOWN']*3+['RIGHT']*4:
      walk_tile(key);await_state(e.field_idle,900)
     assert e.location()[2:]==(8,10)
     assert object_by_id(11)['xy']==(9,10)
     walk_tile('RIGHT');await_state(e.field_idle,1800);e.run(30)
     assert e.location()[2:]==(9,10) and object_by_id(11)['xy']==(10,10)
     for key in ['DOWN']*3+['RIGHT']*6:
      walk_tile(key);await_state(e.field_idle,900)
     assert e.location()[2:]==(15,13),('pushed boulder actual screen exit',e.location())
     object_by_id(10,False)
     for key in ['LEFT']*6+['UP']*3+['LEFT']*5+['UP']*2:
      walk_tile(key);await_state(e.field_idle,900)
     assert e.location()[2:]==(4,8)
     assert object_by_id(10)['xy']==(4,7),'original boulder template reset after screen reentry differs'
     assert not blocks(e).flag('FLAG_TEMP_11'),'screen reset incorrectly hid the original boulder'
     no_player_overlap()
     report['stages'].append({'label':'original-boulder-reset-after-cold-and-screen-reentry',
      'local_id':10,'xy':object_by_id(10)['xy'],'reset_without_map_warp':True})
     # Confirm the original screen reset does not trap the player or block progress.
     prev=e.location();walk_tile('UP');await_state(e.field_idle,1800);e.run(30)
     assert e.location()[2:]==(4,7) and object_by_id(10)['xy']==(4,6)
     check_companion_visible(prev[2:],'strength-repush-after-cold-and-screen-reset')
    else:
     object_by_id(15,False);assert blocks(e).flag('FLAG_TEMP_19'),'native smashed rock flag missing'
     prev=e.location();walk_tile('RIGHT');await_state(e.field_idle,1800);e.run(20)
     assert e.location()[2:]==(19,5),'smashed tile still blocks native walking'
     check_companion_visible(prev[2:],'native-rock-smash')
     native_save_reopen(e,source_pc);invariants();object_by_id(15,False);no_player_overlap()
     assert blocks(e).flag('FLAG_TEMP_19'),'smashed rock returned on cold Continue'
     probe_companion('rock-smash-cold',('LEFT','RIGHT'))
     # Leave and re-enter the screen without a map warp: TEMP flag must still hide it.
     # This original ground corridor reaches (15,13), outside both the
     # current and initial rock's native spawn window; no NPC sight line.
     leave=['LEFT']*4+['DOWN']*8
     return_path=['UP']*8+['RIGHT']*4
     for key in leave:
      walk_tile(key);await_state(e.field_idle,900)
     assert e.location()[2:]==(15,13),('actual screen exit',e.location())
     object_by_id(15,False)
     for key in return_path:
      walk_tile(key);await_state(e.field_idle,900)
     assert e.location()[2:]==(19,5);object_by_id(15,False)
     assert blocks(e).flag('FLAG_TEMP_19'),'TEMP obstacle flag reset without a map change'
     report['stages'].append({'label':'rock-hidden-after-screen-reentry','temp_flag':True})
    invariants();check_story_unchanged(initial_story)
    assert all(not blocks(e).flag(f) for f in TEMP if f!='FLAG_TEMP_19')
  invariants();check_story_unchanged(initial_story)
  report['pass']=True;report['full_original_storage_unchanged']=True
except Exception as ex:
 report['error']=repr(ex);report['traceback']=traceback.format_exc()
 if e and e.h:report['failure_location']=e.location();photo(e,'failure')
finally:
 if e:e.close()
 after={p:sha(Path(p).read_bytes()) for p in before}
 report['original_saves_unchanged']=before==after
 if before!=after:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='traceback'}),flush=True)
sys.exit(0 if report['pass'] else 1)
