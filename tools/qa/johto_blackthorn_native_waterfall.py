#!/usr/bin/env python3
"""Native Johto Badge8 Waterfall A/menu boundaries, four-tile movement and genuine Pikachu."""
from pathlib import Path
head=Path('tools/qa/hoenn_weather_space_native_qa.py').read_text().split('e=None\ntry:',1)[0]
old="choices=['weather-party','weather-pc','space']"
assert head.count(old)==1
head=head.replace(old,"choices=['a','menu','no-badge-a','no-badge-menu','kanto-only-a','kanto-only-menu','hoenn-only-a','hoenn-only-menu']",1)
exec(compile(head,'tools/qa/hoenn_weather_space_native_qa.py','exec'))
# Register this QA's UI callbacks from the exact candidate ELF. The inherited
# weather helper keeps only its own task whitelist in sets.
import os,subprocess
qa_task_names=['Task_HandleChooseMonInput','Task_HandleSelectionMenuInput','Task_ReturnToChooseMonAfterText','Task_CancelAfterAorBPress','Task_YesNoMenu_HandleInput','Task_UseWaterfall']
qa_task_table=subprocess.check_output(
 [str(Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))/'bin/arm-none-eabi-objdump'),
  '-t',str(elf)],text=True)
for line in qa_task_table.splitlines():
 parts=line.split()
 if (len(parts)>=6 and re.fullmatch('[0-9a-fA-F]{8}',parts[0])
     and parts[-1] in qa_task_names):
  sets.setdefault(parts[-1],set()).add(int(parts[0],16)&~1)
assert all(sets.get(name) for name in qa_task_names),('missing candidate UI tasks',[name for name in qa_task_names if not sets.get(name)])
report['candidate_ui_task_symbols']={name:sorted(sets[name]) for name in qa_task_names}
assert not a.loss
# gamedata.const reads defines, not the implicit C enum used by avatar flags.
avatar_header=Path('include/global.fieldmap.h').read_text()
avatar_source=re.sub(r'/\*.*?\*/|//[^\n]*','',avatar_header,flags=re.S)
avatar_enums=re.findall(r'enum\s*\{([^{}]*\bPLAYER_AVATAR_STATE_NORMAL\b[^{}]*)\}',avatar_source)
assert len(avatar_enums)==1 and '=' not in avatar_enums[0],'avatar enum layout changed'
avatar_states=re.findall(r'\bPLAYER_AVATAR_STATE_[A-Z_]+\b',avatar_enums[0])
assert len(avatar_states)==len(set(avatar_states))
def avatar_flag(name):
 state='PLAYER_AVATAR_STATE_'+name
 assert re.search(r'#define\s+PLAYER_AVATAR_FLAG_'+name+r'\s+\(1\s*<<\s*'+state+r'\s*\)',avatar_source)
 return 1<<avatar_states.index(state)
SURF=avatar_flag('SURFING');FORCED=avatar_flag('FORCED')
WATERFALL=const('MOVE_WATERFALL');C='DragonDen_1F'
flags=['FLAG_JOHTO_BADGE08_GET','FLAG_JOHTO_BADGE04_GET','FLAG_HOENN_BADGE08_GET','FLAG_BADGE07_GET','FLAG_RECEIVED_STARTER_PIKACHU']
report.update(mode='native-johto-waterfall-'+a.case,stages=[],
 fixture='temporary Lapras mover plus exact copy of genuine original starter Pikachu; original SAV/PC/Dex unchanged',
 native_story_not_entire_regions=True)
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
def main_input_offsets():
 fields=['heldKeysRaw','newKeysRaw','heldKeys','newKeys','newAndRepeatedKeys','keyRepeatCounter','vblankCounter2']
 c='#include "global.h"\n#include "main.h"\n#include "link.h"\n#include <stddef.h>\nconst u32 qa_input_offsets[] __attribute__((section(".qa_input_offsets"))) = {\n'
 c+=','.join('offsetof(struct Main,'+name+')' for name in fields)
 c+=',offsetof(struct Link,recvQueue.count),OVERWORLD_RECV_QUEUE_MAX};\n'
 tool=Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))/'bin'
 with tempfile.TemporaryDirectory(prefix='input-read-offsets-') as td:
  f=Path(td)/'input.c';o=Path(td)/'input.o';b=Path(td)/'input.bin';f.write_text(c)
  subprocess.run([str(tool/'arm-none-eabi-gcc'),'-c','-w','-mthumb','-mabi=apcs-gnu','-march=armv4t',
   '-fcommon','-iquote','include','-DLEAFGREEN','-DREVISION=0','-DENGLISH','-DMODERN=1','-o',str(o),str(f)],check=True)
  subprocess.run([str(tool/'arm-none-eabi-objcopy'),'-O','binary','-j','.qa_input_offsets',str(o),str(b)],check=True)
  raw=b.read_bytes()
 assert len(raw)==4*(len(fields)+2)
 offsets=dict(zip(fields+['link_recv_count','link_overworld_max'],struct.unpack('<'+str(len(fields)+2)+'I',raw)))
 report['input_abi_offsets']=offsets
 return offsets
input_offsets=main_input_offsets()
def input_snapshot(label):
 q=ui_snapshot();q['label']=label;q['emulator_frame']=e.frame()
 q['input']={name:(e.u32(syms['gMain']+offset) if name=='vblankCounter2' else e.u16(syms['gMain']+offset))
  for name,offset in input_offsets.items() if not name.startswith('link_')}
 q['callback1']=hex(e.u32(syms['gMain']))
 q['link']={'received_remote_players':e.u8(syms['gReceivedRemoteLinkPlayers']),
  'wireless_comm_type':e.u8(syms['gWirelessCommType']),
  'wired_recv_count':e.u8(syms['gLink']+input_offsets['link_recv_count']),
  'wired_overworld_max':input_offsets['link_overworld_max']}
 q['hardware_keyinput']=e.u16(0x04000130)
 return q
def traced_party_confirm():
 samples=[input_snapshot('before-release')]
 e.hold()
 for i in range(3):
  e.run(1);samples.append(input_snapshot('release-%d'%i))
 e.hold('A')
 try:
  for i in range(12):
   e.run(1);samples.append(input_snapshot('hold-A-%d'%i))
 finally:e.hold()
 e.run(20);samples.append(input_snapshot('after-release'))
 report['party_confirm_input_trace']=samples
 print(json.dumps({'party_confirm_input_trace':samples}),flush=True)

def await_state(pred,limit=2000,key=None):
 for i in range(limit):
  if pred():return
  safe(e);assert not e.in_battle(),'unexpected wild battle on repel route'
  if key and i%8==0:e.press(key,hold=1,after=1)
  else:e.run(1)
 report['ui_debug']=ui_snapshot()
 raise AssertionError(('native waterfall timeout',report.get('ui_stage'),e.location(),hex(e.callback2())))
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
 assert e.u8(syms['gPlayerAvatar'])&SURF,'not in SURF avatar mode'
 mon=e.read(syms['gPlayerParty']+100,100);m=Mon(bytearray(mon),0)
 assert m.personality==report['follower_original']['personality']
 assert m.otid==report['follower_original']['otid'] and m.starter_bit()
 assert m.species()==const('SPECIES_PIKACHU') and struct.unpack_from('<H',mon,86)[0]>0
 photo(e,'follower-'+label+'-'+str(len(report['follower_checks'])))
 report['follower_checks'].append({'label':label,'map':e.location()[:2],
  'player_xy':e.location()[2:],'follower_xy':[xy[0]-7,xy[1]-7],
  'visible':True,'native_sprite_active':True,'avatar_flags':e.u8(syms['gPlayerAvatar'])})
def probe_companion(label):
 initial=e.location()
 companion_state()
 walk_tile('RIGHT');await_state(e.field_idle,600);e.run(20)
 assert e.location()==(initial[0],initial[1],initial[2]+1,initial[3]),e.location()
 check_companion_visible(initial[2:],label+'-right')
 previous=e.location()[2:]
 walk_tile('LEFT');await_state(e.field_idle,600);e.run(20)
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
 traced_party_confirm()
 await_state(lambda:active_task(e,'Task_HandleSelectionMenuInput') and fade_inactive())
 p=e.ptr('sPartyMenuInternal');actions=list(e.read(p+15,e.u8(p+23)))
 matches=[option for option in actions if struct.unpack('<I',r.at(syms['sCursorOptions']+option*8,4))[0]==syms['gMoveNames']+WATERFALL*13]
 assert len(matches)==1,('native WATERFALL menu label absent or ambiguous',actions,matches)
 action=matches[0]
 assert (struct.unpack('<I',r.at(syms['sCursorOptions']+action*8+4,4))[0]&~1)==(syms['CursorCB_FieldMove']&~1),'WATERFALL label has wrong native callback'
 report['native_waterfall_cursor_option']=action
 for _ in range(actions.index(action)):e.press('DOWN',hold=3,after=12)
 report['ui_stage']='choose-waterfall-action'
 photo(e,'native-waterfall-menu');e.press('A',hold=3,after=20)
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
def trace_to(y,label,key=None):
 steps=[];g,n,_,_=e.location();last=(g,n,20,10 if label=='ascent' else 6);seen_task=False
 for i in range(5000):
  safe(e);assert not e.in_battle()
  now=e.location()
  if now!=last:steps.append({'frame':e.frame(),'xy':list(now[2:])});last=now
  seen_task|=active_task(e,'Task_UseWaterfall')
  if (now[2:]==(20,y) and e.field_idle() and
      not active_task(e,'Task_UseWaterfall') and not e.u8(syms['gPlayerAvatar']+6)):
   e.run(40);break
  if key and i%8==0:e.press(key,hold=1,after=1)
  else:e.run(1)
 else:raise AssertionError(('waterfall movement timeout',label,e.location(),steps[-12:]))
 expected_ys=[9,8,7,6] if label=='ascent' else [7,8,9,10]
 assert [s['xy'][1] for s in steps]==expected_ys,(label,'native waterfall skipped or reversed tile',steps)
 assert all(s['xy'][0]==20 for s in steps),(label,'left waterfall column',steps)
 report['stages'].append({'label':label,'steps':steps,'native_waterfall_task_seen':seen_task,
  'avatar_flags':e.u8(syms['gPlayerAvatar'])})
 assert e.u8(syms['gPlayerAvatar'])&SURF
 assert not(e.u8(syms['gPlayerAvatar'])&FORCED),'forced movement flag stayed set'
 check_companion_visible((20,7 if label=='ascent' else 9),label)
 invariants()
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-johto-waterfall-qa-') as td:
  s=SaveFile(str(sav));original_pika=original_starter_copy(s)
  s.fast_battles();s.keep_party(1);s.set_var('VAR_REPEL_STEP_COUNT',250)
  s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False)
  for i in range(1,9):
   s.set_flag('FLAG_BADGE%02d_GET'%i,a.case.startswith('kanto-only') and i==7)
   s.set_flag('FLAG_HOENN_BADGE%02d_GET'%i,a.case.startswith('hoenn-only') and i==8)
   s.set_flag('FLAG_JOHTO_BADGE%02d_GET'%i,i==4 or (i==8 and a.case in ('a','menu')))
  s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
  s.warp(C,20,10)
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  m=s.party_mon(0);m.set_otid(owner);m.set_starter_bit(False);m.set_snagged(False)
  m.set_species(const('SPECIES_LAPRAS'),rom=r)
  sub=m.subs();sub['E'][:6]=bytes(6);sub['A'][:]=bytes(12)
  for i,name in enumerate(['MOVE_SURF','MOVE_WATERFALL']):
   mid=const(name);struct.pack_into('<H',sub['A'],i*2,mid)
   sub['A'][8+i]=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  struct.pack_into('<I',sub['M'],4,struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30))
  m.put_subs(sub);m.blk[m.o+19]=(m.blk[m.o+19]&~5)|2;m.set_held(0);m.make_strong(50,rom=r)
  po=off('sb1.playerParty');s.sb1[po+100:po+200]=original_pika
  s.sb1[off('sb1.playerPartyCount')]=2;expected_party=bytes(s.sb1[po:po+600])
  assert expected_party[100:200]==original_pika
  assert bytes(s.blocks['storage'][:off('storage')])==source_storage
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  initial=e.location();invariants();initial_flags={f:blocks(e).flag(f) for f in flags}
  assert loc_is(e,C) and initial[2:]==(20,10)
  # The fixture is directly on the native surfable water tile. Boot must select
  # the real SURF avatar; the harness never writes avatar state or game RAM.
  assert e.u8(syms['gPlayerAvatar'])&SURF,'native water boot did not mount SURF'
  probe_companion('base')
  e.press('UP',hold=1,after=20)
  assert e.location()==initial,'facing waterfall took an unintended step'
  if a.case in ('a','menu'):
   if a.case=='a':use_a()
   else:start_party()
   trace_to(6,'ascent','A')
   assert report['stages'][-1]['native_waterfall_task_seen']
   native_save_reopen(e,source_pc);invariants();probe_companion('summit-cold')
   assert e.location()[2:]==(20,6)
   e.hold('DOWN')
   try:
    for _ in range(80):
     safe(e);e.run(1)
     if e.location()[3]!=6:break
    else:raise AssertionError('native Johto waterfall descent never started')
   finally:e.hold()
   trace_to(10,'descent')
   native_save_reopen(e,source_pc);invariants();probe_companion('base-cold')
   report['native_four_tile_ascent_and_descent']=True
  else:
   if a.case.endswith('menu'):reject_menu(True)
   else:
    e.press('A',hold=3,after=20);quiet_finish(e)
    assert not active_task(e,'Task_UseWaterfall')
   assert e.location()==initial,'wrong region badge allowed Johto Waterfall'
   probe_companion('badge-rejected-still-follows')
   native_save_reopen(e,source_pc);invariants();probe_companion('badge-rejected-cold')
   report['native_region_badge_boundary']=True
  invariants()
  assert {f:blocks(e).flag(f) for f in flags}==initial_flags,'field move changed story flags'
  report['pass']=True;report['full_original_storage_unchanged']=True
  report['forced_game_memory_writes']=0;report['original_sav_modified']=False
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
