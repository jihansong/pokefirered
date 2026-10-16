#!/usr/bin/env python3
"""Native story-region Fly menu and destination A tests; original storage and save ABI preserved."""
from pathlib import Path
head=Path('tools/qa/hoenn_weather_space_native_qa.py').read_text().split('e=None\ntry:',1)[0]
old="choices=['weather-party','weather-pc','space']"
assert head.count(old)==1
head=head.replace(old,"choices=['kanto-on','kanto-off','kanto-foreign','johto-on','johto-off','johto-foreign','hoenn-on','hoenn-off','hoenn-foreign','town-new_bark_town','town-cherrygrove_city','town-violet_city','town-azalea_town','town-goldenrod_city','town-ecruteak_city','town-olivine_city','town-cianwood_city','town-locked-olivine','town-locked-route','town-alternate-violet','town-all-visited']",1)
exec(compile(head,'tools/qa/hoenn_weather_space_native_qa.py','exec'))
# Register this QA's UI callbacks from the exact candidate ELF. The inherited
# weather helper keeps only its own task whitelist in sets.
import os,subprocess
qa_task_names=['Task_HandleChooseMonInput','Task_HandleSelectionMenuInput','Task_ReturnToChooseMonAfterText','Task_CancelAfterAorBPress','Task_FlyMap','Task_UseFly','Task_FlyIntoMap']
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
FLY_MOVE=const('MOVE_FLY')
flags=['FLAG_BADGE03_GET','FLAG_JOHTO_BADGE05_GET','FLAG_HOENN_BADGE06_GET','FLAG_RECEIVED_STARTER_PIKACHU']
report.update(mode='native-fly-region-'+a.case,stages=[],
 fixture='temporary Fearow mover plus exact copy of genuine original starter Pikachu; original SAV/PC/Dex unchanged',
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
 raise AssertionError(('native Fly timeout',report.get('ui_stage'),e.location(),hex(e.callback2())))
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
 report['ui_stage']='select-native-Fly-context'
 e.press('A',hold=3,after=20)
 await_state(lambda:active_task(e,'Task_HandleSelectionMenuInput') and fade_inactive())
 p=e.ptr('sPartyMenuInternal');actions=list(e.read(p+15,e.u8(p+23)))
 matches=[v for v in actions if struct.unpack('<I',r.at(syms['sCursorOptions']+v*8,4))[0]==syms['gMoveNames']+FLY_MOVE*13]
 assert len(matches)==1,('Fly menu must have exactly one native move entry',actions,matches)
 action=matches[0]
 assert struct.unpack('<I',r.at(syms['sCursorOptions']+action*8+4,4))[0]&~1==syms['CursorCB_FieldMove']&~1
 for _ in range(actions.index(action)):e.press('DOWN',hold=3,after=12)
 report['ui_stage']='choose-Fly-action'
 photo(e,'native-fly-menu');e.press('A',hold=3,after=20)
def reject_menu(badge_missing):
 start_party()
 target='Task_ReturnToChooseMonAfterText' if badge_missing else 'Task_CancelAfterAorBPress'
 await_state(lambda:active_task(e,target),1800)
 photo(e,'native-fly-menu-rejection')
 report['menu_rejection_task']=target
 await_state(e.field_idle,2400,'B')

def native_fly_abi():
 code=Path('src/region_map.c').read_text()
 names=['MapCursor','FlyMap','MapIconSprite','MapIcons','RegionMap']
 defs=[]
 for name in names:
  hits=re.findall(r'struct '+name+r'\s*\{[^{}]*\};',code);assert len(hits)==1,(name,'private struct declaration changed')
  defs.append(hits[0])
 enums=[]
 for token in ['REGIONMAP_KANTO','MAPPERM_COUNT']:
  hits=re.findall(r'enum\s*\{[^{}]*\b'+token+r'\b[^{}]*\};',code);assert len(hits)==1,(token,'enum missing')
  enums.append(hits[0])
 fields=[('cursor.x','MapCursor','x'),('cursor.y','MapCursor','y'),('cursor.move','MapCursor','moveCounter'),
 ('cursor.mapsec','MapCursor','selectedMapsec'),('cursor.type','MapCursor','selectedMapsecType'),
 ('fly.state','FlyMap','state'),('icons.fly','MapIcons','flyIcons'),('icons.dungeon','MapIcons','dungeonIcons'),
 ('icon.size','MapIconSprite',None),('icon.region','MapIconSprite','region'),('icon.sprite','MapIconSprite','sprite'),
 ('region.selected','RegionMap','selectedRegion'),('sprite.size','Sprite',None)]
 expressions=['sizeof(struct '+st+')' if member is None else 'offsetof(struct '+st+', '+member+')' for _,st,member in fields]
 section_names=['MAPSEC_NEW_BARK_TOWN','MAPSEC_CHERRYGROVE_CITY','MAPSEC_VIOLET_CITY',
  'MAPSEC_AZALEA_TOWN','MAPSEC_GOLDENROD_CITY','MAPSEC_ECRUTEAK_CITY','MAPSEC_OLIVINE_CITY',
  'MAPSEC_CIANWOOD_CITY','MAPSEC_JOHTO_ROUTE40','MAPSEC_PALLET_TOWN','MAPSEC_SLATEPORT_CITY']
 fields.extend([('section.'+n,None,None) for n in section_names])
 expressions.extend(section_names)
 c='#include "global.h"\n#include "gflib.h"\n#include "sprite.h"\n#include "task.h"\n#include "main.h"\n#include "constants/region_map_sections.h"\n'+ '\n'.join(enums+defs)+'\n'
 c+='const u32 qa_fly_abi[] __attribute__((section(".qa_fly_abi"))) = {'+', '.join(expressions)+'};\n'
 tool=Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))/'bin'
 with tempfile.TemporaryDirectory(prefix='fly-private-abi-') as td:
  f=Path(td)/'abi.c';o=Path(td)/'abi.o';b=Path(td)/'abi.bin';f.write_text(c)
  subprocess.run([str(tool/'arm-none-eabi-gcc'),'-c','-w','-mthumb','-mabi=apcs-gnu','-march=armv4t','-fcommon','-iquote','include','-DLEAFGREEN','-DREVISION=0','-DENGLISH','-DMODERN=1','-o',str(o),str(f)],check=True)
  subprocess.run([str(tool/'arm-none-eabi-objcopy'),'-O','binary','-j','.qa_fly_abi',str(o),str(b)],check=True);raw=b.read_bytes()
 assert len(raw)==4*len(fields)
 values=dict(zip([x[0] for x in fields],struct.unpack('<'+'I'*len(fields),raw)))
 region_names=re.findall(r'\bREGIONMAP_[A-Z0-9_]+\b',enums[0]);assert len(region_names)==len(set(region_names)) and '=' not in enums[0]
 types=re.findall(r'enum\s*\{([^{}]*\bMAPSECTYPE_VISITED\b[^{}]*)\}',code);assert len(types)==1 and '=' not in types[0]
 type_names=re.findall(r'\bMAPSECTYPE_[A-Z0-9_]+\b',types[0]);assert len(type_names)==len(set(type_names))
 report['private_fly_abi']={'offsets':values,'source_schema_sha256':sha(('\n'.join(enums+defs)).encode()),'regions':region_names,'mapsec_types':type_names}
 return values,region_names,type_names
ABI,REGIONS,TYPES=native_fly_abi()
BADGES={'kanto':'FLAG_BADGE03_GET','johto':'FLAG_JOHTO_BADGE05_GET','hoenn':'FLAG_HOENN_BADGE06_GET'}
TOWNS=[
 ('new_bark_town','NewBarkTown','NEW_BARK_TOWN','FLAG_JOHTO_MET_LAB_ASSISTANT','FLAG_JOHTO_ELM_REPORT_DELIVERED','HEAL_LOCATION_NONE',11,10),
 ('cherrygrove_city','CherrygroveCity','CHERRYGROVE_CITY','FLAG_JOHTO_MET_CHERRYGROVE_GUIDE','FLAG_JOHTO_ELM_REPORT_DELIVERED','HEAL_LOCATION_CHERRYGROVE_CITY',26,9),
 ('violet_city','VioletCity','VIOLET_CITY','FLAG_JOHTO_SPROUT_TOWER_CLEARED','FLAG_JOHTO_BADGE01_GET','HEAL_LOCATION_VIOLET_CITY',7,27),
 ('azalea_town','AzaleaTown','AZALEA_TOWN','FLAG_JOHTO_KURT_RESCUE_REQUESTED','FLAG_JOHTO_BADGE02_GET','HEAL_LOCATION_AZALEA_TOWN',7,23),
 ('goldenrod_city','GoldenrodCity','GOLDENROD_CITY','FLAG_JOHTO_GOLDENROD_RESEARCH_REGISTERED','FLAG_JOHTO_BADGE03_GET','HEAL_LOCATION_GOLDENROD_CITY',8,29),
 ('ecruteak_city','EcruteakCity','ECRUTEAK_CITY','FLAG_JOHTO_BURNED_TOWER_INVESTIGATED','FLAG_JOHTO_BADGE04_GET','HEAL_LOCATION_ECRUTEAK_CITY',8,29),
 ('olivine_city','OlivineCity','OLIVINE_CITY','FLAG_JOHTO_LIGHTHOUSE_MEDICINE_REQUESTED','FLAG_JOHTO_BADGE06_GET','HEAL_LOCATION_OLIVINE_CITY',7,20),
 ('cianwood_city','CianwoodCity','CIANWOOD_CITY','FLAG_JOHTO_CIANWOOD_MEDICINE_RECEIVED','FLAG_JOHTO_BADGE05_GET','HEAL_LOCATION_CIANWOOD_CITY',5,25)]
TOWN_BY_KEY={v[0]:v for v in TOWNS}
town_mode=a.case.startswith('town-')
if town_mode:
 region='johto';gate='on';origin=('CianwoodCity',10,16)
 key=a.case[5:];locked=key in ['locked-olivine','locked-route']
 target=TOWN_BY_KEY['olivine_city' if key=='locked-olivine' else 'violet_city' if key=='alternate-violet' else 'new_bark_town' if key in ['locked-route','all-visited'] else key]
 target_section='MAPSEC_JOHTO_ROUTE40' if key=='locked-route' else 'MAPSEC_'+target[2]
else:
 region,gate=a.case.split('-');locked=False;key=None
 origin={'kanto':('PalletTown',11,18),'johto':('CianwoodCity',10,16),'hoenn':('SlateportCity',32,12)}[region]
 target=TOWN_BY_KEY['cianwood_city'] if region=='johto' else None
 target_section={'kanto':'MAPSEC_PALLET_TOWN','johto':'MAPSEC_CIANWOOD_CITY','hoenn':'MAPSEC_SLATEPORT_CITY'}[region]
flags=sorted(set(flags+[v for row in TOWNS for v in row[3:5]]))
sections={v['id']:v for v in json.loads(Path('src/data/region_map/region_map_sections.json').read_text())['map_sections'] if v.get('id')}
assert target_section in sections
if 'x' in sections[target_section] and 'y' in sections[target_section]:
 target_cell=(sections[target_section]['x'],sections[target_section]['y'])
 report['target_cell_source']='native section geometry'
else:
 assert region=='hoenn','missing geometry outside imported Hoenn'
 layout_text=Path('src/data/region_map/region_map_layout_hoenn.h').read_text()
 assert 'static const u8 sRegionMapSections_Hoenn[LAYER_COUNT][MAP_HEIGHT][HOENN_MAP_WIDTH]' in layout_text
 region_source=Path('src/region_map.c').read_text()
 height=int(re.search(r'#define\s+MAP_HEIGHT\s+(\d+)\b',region_source).group(1))
 width=int(re.search(r'#define\s+HOENN_MAP_WIDTH\s+(\d+)\b',region_source).group(1))
 grid=r.at(syms['sRegionMapSections_Hoenn'],height*width)
 hits=[(i%width,i//width) for i,v in enumerate(grid) if v==ABI['section.'+target_section]]
 assert hits,('target absent from candidate Hoenn grid',target_section)
 target_cell=hits[0];report['target_cell_source']='candidate compiled Hoenn LAYER_MAP table'
 report['target_cells']=hits
expected_region=REGIONS.index({'kanto':'REGIONMAP_KANTO','johto':'REGIONMAP_JOHTO_ENTRY','hoenn':'REGIONMAP_HOENN'}[region])
def fly_ready():
 p=e.ptr('sFlyMap') if 'sFlyMap' in syms else 0
 return bool(p and active_task(e,'Task_FlyMap') and e.u8(p+ABI['fly.state'])==4 and fade_inactive())
def cursor():
 p=e.ptr('sMapCursor');assert 0x02000000<=p<0x02040000,hex(p)
 return {'x':e.u16(p+ABI['cursor.x']),'y':e.u16(p+ABI['cursor.y']),
  'mapsec':e.u16(p+ABI['cursor.mapsec']),'type':e.u16(p+ABI['cursor.type']),'move':e.u16(p+ABI['cursor.move'])}
def move_cursor_to(cell):
 for _ in range(80):
  c=cursor()
  if (c['x'],c['y'])==cell:return
  direction='RIGHT' if c['x']<cell[0] else 'LEFT' if c['x']>cell[0] else 'DOWN' if c['y']<cell[1] else 'UP'
  e.press(direction,hold=1,after=10);await_state(lambda:fly_ready() and cursor()['move']==0,400)
 raise AssertionError(('Fly cursor did not reach target',cursor(),cell))
def icon_snapshot():
 p=e.ptr('sMapIcons');assert p
 result={}
 for label,count,member in [('fly',48,'icons.fly'),('dungeon',25,'icons.dungeon')]:
  rows=[]
  for i in range(count):
   base=p+ABI[member]+i*ABI['icon.size'];sp=e.u32(base+ABI['icon.sprite'])
   if not sp:continue
   maximum=int(re.search(r'#define\s+MAX_SPRITES\s+(\d+)',Path('include/sprite.h').read_text()).group(1))
   assert syms['gSprites']<=sp<syms['gSprites']+maximum*ABI['sprite.size'] and (sp-syms['gSprites'])%ABI['sprite.size']==0,('icon sprite outside native pool',label,i,hex(sp))
   assert e.u8(sp+0x3e)&1,('icon points to inactive sprite',label,i)
   rows.append({'slot':i,'region':e.u8(base+ABI['icon.region']),'sprite':(sp-syms['gSprites'])//ABI['sprite.size']})
  result[label]=rows
 if region=='johto':
  assert all(v['region']==expected_region for v in result['fly'])
  assert not result['dungeon'],'hidden foreign dungeon sprites allocated in Johto'
  if key=='all-visited':assert len(result['fly'])==8,('all visited Johto icon count',len(result['fly']))
 report['icon_allocation']=result
 return result
report.update(mode='native-fly-region-'+a.case,region=region,gate=gate,method='party menu then native destination A',stages=[],native_story_not_entire_regions=True,
 original_party_storage_preserved=True,fly_destinations_not_story_completion=True)
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-fly-region-qa-') as td:
  s=SaveFile(str(sav));original_pika=original_starter_copy(s)
  s.fast_battles();s.keep_party(1);s.set_var('VAR_REPEL_STEP_COUNT',250);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False)
  for i in range(1,9):
   s.set_flag('FLAG_BADGE%02d_GET'%i,False);s.set_flag('FLAG_HOENN_BADGE%02d_GET'%i,False)
  for f in flags:
   if f!='FLAG_RECEIVED_STARTER_PIKACHU':s.set_flag(f,False)
  if gate=='on':s.set_flag(BADGES[region],True)
  elif gate=='foreign':
   for other,f in BADGES.items():
    if other!=region:s.set_flag(f,True)
  if target and not locked:s.set_flag(target[4] if key=='alternate-violet' else target[3],True)
  if key=='all-visited':
   for row in TOWNS:
    for f in row[3:5]:s.set_flag(f,True)
   for path in [Path('include/constants/flags.h'),Path('include/constants/flags_hoenn.h')]:
    if path.exists():
     for f in set(re.findall(r'^#define\s+(FLAG_(?:HOENN_)?WORLD_MAP_[A-Z0-9_]+)\b',path.read_text(),re.M)):s.set_flag(f,True)
  if region=='kanto':s.set_flag('FLAG_WORLD_MAP_PALLET_TOWN',True)
  if region=='hoenn':s.set_flag('FLAG_HOENN_WORLD_MAP_SLATEPORT_CITY',True)
  s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True);s.warp(*origin)
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  m=s.party_mon(0);m.set_otid(owner);m.set_starter_bit(False);m.set_snagged(False);m.set_species(const('SPECIES_FEAROW'),rom=r)
  sub=m.subs();sub['E'][:6]=bytes(6);sub['A'][:]=bytes(12)
  for i,name in enumerate(['MOVE_FLY','MOVE_TACKLE']):
   mid=const(name);struct.pack_into('<H',sub['A'],i*2,mid);sub['A'][8+i]=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  struct.pack_into('<I',sub['M'],4,struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30))
  m.put_subs(sub);m.blk[m.o+19]=(m.blk[m.o+19]&~5)|2;m.set_held(0);m.make_strong(50,rom=r)
  po=off('sb1.playerParty');s.sb1[po+100:po+200]=original_pika;s.sb1[off('sb1.playerPartyCount')]=2
  expected_party=bytes(s.sb1[po:po+600]);assert expected_party[100:200]==original_pika
  assert bytes(s.blocks['storage'][:off('storage')])==source_storage
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e);invariants();companion_state()
  initial=e.location();assert initial[2:]==origin[1:],('Fly fixture location',initial,origin)
  initial_flags={f:blocks(e).flag(f) for f in flags}
  if gate!='on':
   reject_menu(True)
   assert e.location()==initial and not active_task(e,'Task_UseFly'),'foreign badge authorized native Fly'
  else:
   start_party();report['ui_stage']='wait-native-Fly-map';await_state(fly_ready,4000);e.run(2)
   rp=e.ptr('sRegionMap');assert e.u8(rp+ABI['region.selected'])==expected_region,('wrong region Fly map',expected_region,e.u8(rp+ABI['region.selected']))
   move_cursor_to(target_cell);c=cursor();assert c['mapsec']==ABI['section.'+target_section],(c,target_section,target_cell)
   icon_snapshot();photo(e,'native-Fly-destination-map')
   if locked:
    assert c['type']==TYPES.index('MAPSECTYPE_ROUTE' if key=='locked-route' else 'MAPSECTYPE_NOT_VISITED'),c
    e.press('A',hold=2,after=120);assert fly_ready() and e.location()==initial and not active_task(e,'Task_UseFly'),'locked destination allowed Fly'
    report['ui_stage']='cancel-locked-Fly-map';await_state(e.field_idle,4000,'B')
   else:
    assert c['type']==TYPES.index('MAPSECTYPE_VISITED'),('Fly town not unlocked',c)
    report['ui_stage']='select-native-destination-A';e.press('A',hold=1,after=1)
    await_state(lambda:active_task(e,'Task_UseFly'),3000);report['native_fly_out_task_observed']=True
    await_state(e.field_idle,5000);e.run(30);invariants();companion_state()
    if region=='johto':
     info=map_info(target[1]);expected=(info['group'],info['num'],target[6],target[7])
    else:
     heals=json.loads(Path('src/data/heal_locations.json').read_text())['heal_locations']
     hid='HEAL_LOCATION_PALLET_TOWN' if region=='kanto' else 'HEAL_LOCATION_HOENN_SLATEPORT_CITY'
     row=next(v for v in heals if v['id']==hid);info=map_info(origin[0]);expected=(info['group'],info['num'],row['x'],row['y'])
    assert e.location()==expected,('native Fly landed elsewhere',expected,e.location())
    photo(e,'native-Fly-landed');report['landing']={'target':target_section,'expected':expected,'actual':e.location()}
    native_save_reopen(e,source_pc);invariants();companion_state();assert e.location()==expected,'Fly landing not preserved after native SAVE/cold'
  invariants();assert {f:blocks(e).flag(f) for f in flags}==initial_flags
  report.update(pass_=True,native_region_badge_gate=True,full_original_storage_unchanged=True);report['pass']=True
except Exception as ex:
 report.update(error=repr(ex),traceback=traceback.format_exc())
 if e and e.h:report['failure_location']=e.location();photo(e,'failure')
finally:
 if e:e.close()
 after={p:sha(Path(p).read_bytes()) for p in before};report['original_saves_unchanged']=before==after
 if before!=after:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='traceback'}),flush=True)
sys.exit(0 if report.get('pass') else 1)
