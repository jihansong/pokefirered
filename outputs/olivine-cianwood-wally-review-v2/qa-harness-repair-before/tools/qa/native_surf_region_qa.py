#!/usr/bin/env python3
"""Native story-region Surf A/menu badge gates; original party storage and save ABI preserved."""
from pathlib import Path
head=Path('tools/qa/hoenn_weather_space_native_qa.py').read_text().split('e=None\ntry:',1)[0]
old="choices=['weather-party','weather-pc','space']"
assert head.count(old)==1
head=head.replace(old,"choices=['kanto-on-a','kanto-on-menu','kanto-off-a','kanto-off-menu','kanto-foreign-a','kanto-foreign-menu','johto-on-a','johto-on-menu','johto-off-a','johto-off-menu','johto-foreign-a','johto-foreign-menu','hoenn-on-a','hoenn-on-menu','hoenn-off-a','hoenn-off-menu','hoenn-foreign-a','hoenn-foreign-menu']",1)
exec(compile(head,'tools/qa/hoenn_weather_space_native_qa.py','exec'))
# Register this QA's UI callbacks from the exact candidate ELF. The inherited
# weather helper keeps only its own task whitelist in sets.
import os,subprocess
qa_task_names=['Task_HandleChooseMonInput','Task_HandleSelectionMenuInput','Task_ReturnToChooseMonAfterText','Task_CancelAfterAorBPress','Task_YesNoMenu_HandleInput','Task_FldEffUseSurf']
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
SURF_MOVE=const('MOVE_SURF')
flags=['FLAG_BADGE05_GET','FLAG_JOHTO_BADGE04_GET','FLAG_HOENN_BADGE05_GET','FLAG_RECEIVED_STARTER_PIKACHU']
report.update(mode='native-surf-region-'+a.case,stages=[],
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
def await_state(pred,limit=2000,key=None):
 for i in range(limit):
  if pred():return
  safe(e);assert not e.in_battle(),'unexpected wild battle on repel route'
  if key and i%8==0:e.press(key,hold=1,after=1)
  else:e.run(1)
 report['ui_debug']=ui_snapshot()
 raise AssertionError(('native Surf timeout',report.get('ui_stage'),e.location(),hex(e.callback2())))
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
 await_state(lambda:(e.callback2()&~1)==(syms['CB2_UpdatePartyMenu']&~1) and active_task(e,'Task_HandleChooseMonInput') and fade_inactive())
 e.run(2)
 assert (e.callback2()&~1)==(syms['CB2_UpdatePartyMenu']&~1) and fade_inactive()
 assert fade_inactive(),'party choose input attempted during fade'
 report['ui_stage']='select-lapras-context'
 e.press('A',hold=3,after=20)
 await_state(lambda:active_task(e,'Task_HandleSelectionMenuInput') and fade_inactive())
 p=e.ptr('sPartyMenuInternal');actions=list(e.read(p+15,e.u8(p+23)))
 matches=[v for v in actions if struct.unpack('<I',r.at(syms['sCursorOptions']+v*8,4))[0]==syms['gMoveNames']+SURF_MOVE*13]
 assert len(matches)==1,('Surf menu must have exactly one native move entry',actions,matches)
 action=matches[0]
 assert struct.unpack('<I',r.at(syms['sCursorOptions']+action*8+4,4))[0]&~1==syms['CursorCB_FieldMove']&~1
 for _ in range(actions.index(action)):e.press('DOWN',hold=3,after=12)
 report['ui_stage']='choose-waterfall-action'
 photo(e,'native-surf-menu');e.press('A',hold=3,after=20)
def reject_menu(badge_missing):
 start_party()
 target='Task_ReturnToChooseMonAfterText' if badge_missing else 'Task_CancelAfterAorBPress'
 await_state(lambda:active_task(e,target),1800)
 photo(e,'native-surf-menu-rejection')
 report['menu_rejection_task']=target
 await_state(e.field_idle,2400,'B')
def use_a():
 e.press('A',hold=3,after=20)
 await_state(lambda:active_task(e,'Task_YesNoMenu_HandleInput'),1600,'A')
 e.run(10);e.press('UP',hold=2,after=5);e.press('A',hold=2,after=5)
region,gate,method=a.case.split('-')
BADGES={'kanto':'FLAG_BADGE05_GET','johto':'FLAG_JOHTO_BADGE04_GET','hoenn':'FLAG_HOENN_BADGE05_GET'}
COASTS={'kanto':('PalletTown',11,18,'LEFT',10,18),'johto':('CherrygroveCity',8,23,'LEFT',7,23)}
# The default Hoenn point must be confirmed as a passable sand/water coast before execution.
coast_env=os.environ.get('SURF_HOENN_COAST')
if region=='hoenn':
 assert coast_env,'set SURF_HOENN_COAST to the verified [map,x,y,direction,water_x,water_y] JSON'
 coast=json.loads(coast_env);assert len(coast)==6
else:coast=COASTS[region]
C,x,y,direction,wx,wy=coast
report.update(region=region,gate=gate,method=method,expected_permission=gate=='on',water_target=[wx,wy])
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-surf-region-qa-') as td:
  s=SaveFile(str(sav));original_pika=original_starter_copy(s)
  s.fast_battles();s.keep_party(1);s.set_var('VAR_REPEL_STEP_COUNT',250);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False)
  for i in range(1,9):
   s.set_flag('FLAG_BADGE%02d_GET'%i,False);s.set_flag('FLAG_HOENN_BADGE%02d_GET'%i,False)
  for i in range(1,5):s.set_flag('FLAG_JOHTO_BADGE%02d_GET'%i,False)
  if gate=='on':s.set_flag(BADGES[region],True)
  elif gate=='foreign':
   for other,flag in BADGES.items():
    if other!=region:s.set_flag(flag,True)
  s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True);s.warp(C,x,y)
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  m=s.party_mon(0);m.set_otid(owner);m.set_starter_bit(False);m.set_snagged(False);m.set_species(const('SPECIES_LAPRAS'),rom=r)
  sub=m.subs();sub['E'][:6]=bytes(6);sub['A'][:]=bytes(12)
  for i,name in enumerate(['MOVE_SURF','MOVE_TACKLE']):
   mid=const(name);struct.pack_into('<H',sub['A'],i*2,mid);sub['A'][8+i]=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  struct.pack_into('<I',sub['M'],4,struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30))
  m.put_subs(sub);m.blk[m.o+19]=(m.blk[m.o+19]&~5)|2;m.set_held(0);m.make_strong(50,rom=r)
  po=off('sb1.playerParty');s.sb1[po+100:po+200]=original_pika;s.sb1[off('sb1.playerPartyCount')]=2
  expected_party=bytes(s.sb1[po:po+600]);assert expected_party[100:200]==original_pika
  assert bytes(s.blocks['storage'][:off('storage')])==source_storage
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  initial=e.location();assert initial[2:]==(x,y) and not(e.u8(syms['gPlayerAvatar'])&SURF),'Surf fixture must start on land'
  invariants();initial_flags={f:blocks(e).flag(f) for f in flags};probe_companion('land-before')
  # Turn only. No uncontrolled step is permitted while facing the coast.
  e.press(direction,hold=1,after=20);assert e.location()==initial,('coast turn moved player',initial,e.location())
  if gate!='on':
   if method=='menu':reject_menu(True)
   else:
    e.press('A',hold=3,after=20);await_state(e.field_idle,2400,'B')
   assert e.location()==initial and not(e.u8(syms['gPlayerAvatar'])&SURF),'wrong-region badge allowed Surf'
   probe_companion('rejected-land')
  else:
   if method=='a':use_a()
   else:start_party()
   report['ui_stage']='await-surf-mount'
   await_state(lambda:bool(e.u8(syms['gPlayerAvatar'])&SURF) and e.location()[2:]==(wx,wy) and e.field_idle(),3000,'A')
   photo(e,'surf-native-mounted');invariants();probe_companion('surf-mounted')
   native_save_reopen(e,source_pc);invariants();probe_companion('surf-mounted-cold')
   assert e.location()[2:]==(wx,wy) and e.u8(syms['gPlayerAvatar'])&SURF
  invariants();assert {f:blocks(e).flag(f) for f in flags}==initial_flags
  report.update({'pass':True},native_story_region_gate=True,full_original_storage_unchanged=True)
except Exception as ex:
 report.update(error=repr(ex),traceback=traceback.format_exc())
 if e and e.h:report['failure_location']=e.location();photo(e,'failure')
finally:
 if e:e.close()
 after={p:sha(Path(p).read_bytes()) for p in before};report['original_saves_unchanged']=before==after
 if before!=after:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='traceback'}),flush=True)
sys.exit(0 if report.get('pass') else 1)
