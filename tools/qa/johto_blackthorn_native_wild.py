#!/usr/bin/env python3
"""Native Blackthorn chapter encounters, legal captures and compiled day/night tables."""
from pathlib import Path
import ast,hashlib,os,subprocess
_boot=Path(__file__).with_name('johto_blackthorn_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='2a96b6d26b6f0abbb7a6cc2444ef887cf5e709d8f2373bd2698b086e3d17d032'
exec(compile(_boot_text,str(_boot),'exec'),globals())

def wild_abi():
 names=[('header','sizeof(struct WildPokemonHeader)'),('group','offsetof(struct WildPokemonHeader,mapGroup)'),
 ('num','offsetof(struct WildPokemonHeader,mapNum)'),('land','offsetof(struct WildPokemonHeader,landMonsInfo)'),
 ('water','offsetof(struct WildPokemonHeader,waterMonsInfo)'),('info','sizeof(struct WildPokemonInfo)'),
 ('rate','offsetof(struct WildPokemonInfo,encounterRate)'),('slots','offsetof(struct WildPokemonInfo,wildPokemon)'),
 ('mon','sizeof(struct WildPokemon)'),('min','offsetof(struct WildPokemon,minLevel)'),
 ('max','offsetof(struct WildPokemon,maxLevel)'),('species','offsetof(struct WildPokemon,species)')]
 c='#include "global.h"\n#include "wild_encounter.h"\n#include <stddef.h>\nconst u32 qa_wild_abi[] __attribute__((section(".qa_wild_abi")))={'+','.join(v for k,v in names)+'};\n'
 tool=Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))/'bin'
 with tempfile.TemporaryDirectory(prefix='wild-abi-') as td:
  f=Path(td)/'abi.c';o=Path(td)/'abi.o';b=Path(td)/'abi.bin';f.write_text(c)
  subprocess.run([str(tool/'arm-none-eabi-gcc'),'-c','-w','-mthumb','-mabi=apcs-gnu','-march=armv4t','-fcommon',
   '-iquote','include','-DLEAFGREEN','-DREVISION=0','-DENGLISH','-DMODERN=1','-o',str(o),str(f)],check=True)
  subprocess.run([str(tool/'arm-none-eabi-objcopy'),'-O','binary','-j','.qa_wild_abi',str(o),str(b)],check=True)
  raw=b.read_bytes()
 assert len(raw)==len(names)*4
 return dict(zip((k for k,v in names),struct.unpack('<'+'I'*len(names),raw)))
ABI=wild_abi()
EXPECTED={
 'JohtoRoute44':(
 ['TANGELA','BELLSPROUT','WEEPINBELL','TANGELA','BELLSPROUT','WEEPINBELL','LICKITUNG','TANGELA','LICKITUNG','WEEPINBELL','LICKITUNG','TANGELA'],
 ['TANGELA','BELLSPROUT','WEEPINBELL','NOCTOWL','BELLSPROUT','WEEPINBELL','LICKITUNG','TANGELA','LICKITUNG','NOCTOWL','LICKITUNG','TANGELA'],
 [24,24,25,25,26,27,25,27,26,28,28,27])}
ICE=(['ZUBAT','SWINUB','JYNX','ZUBAT','SWINUB','GOLBAT','SNEASEL','JYNX','SNEASEL','SWINUB','JYNX','SNEASEL'],
 ['ZUBAT','SWINUB','JYNX','ZUBAT','SWINUB','GOLBAT','SNEASEL','JYNX','SNEASEL','SWINUB','JYNX','SNEASEL'],[22,22,23,24,24,25,25,26,26,27,28,29])
for n in ['IcePath_1F','IcePath_B1F','IcePath_B2F']:EXPECTED[n]=ICE
EXPECTED['DragonDen_1F']=(['ZUBAT','ZUBAT','GOLBAT','ZUBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT'],
 ['ZUBAT','ZUBAT','GOLBAT','ZUBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT'],[24,24,25,26,26,27,28,28,29,29,30,30])
WATER=(['MAGIKARP','MAGIKARP','DRATINI','DRATINI','DRAGONAIR'],[15,20,20,25,30])
TABLES={};TABLE_CHECKS=[]
def table_row(name,area,mode):
 table=syms[{'morning':'gWildMonHeadersMorning','day':'gWildMonHeaders','night':'gWildMonHeadersNight'}[mode]]
 info=map_info(name);matches=[]
 for i in range(1024):
  raw=r.at(table+i*ABI['header'],ABI['header'])
  group,num=raw[ABI['group']],raw[ABI['num']]
  if group==255 and num==255:break
  if (group,num)==(info['group'],info['num']):matches.append(raw)
 else:raise AssertionError(('wild table terminator missing',mode))
 assert len(matches)==1,(mode,name,'compiled map header missing/duplicate',len(matches))
 ptr=struct.unpack_from('<I',matches[0],ABI[area])[0];assert ptr
 header=r.at(ptr,ABI['info']);rate=header[ABI['rate']]
 slotptr=struct.unpack_from('<I',header,ABI['slots'])[0]
 count=12 if area=='land' else 5
 slots=[]
 for i in range(count):
  row=r.at(slotptr+i*ABI['mon'],ABI['mon'])
  slots.append((row[ABI['min']],row[ABI['max']],struct.unpack_from('<H',row,ABI['species'])[0]))
 return rate,slots
for mode in ['morning','day','night']:
 for name,(day,night,levels) in EXPECTED.items():
  actual=table_row(name,'land',mode)
  expected=(10,[(level,level,const('SPECIES_'+sp)) for sp,level in zip(night if mode=='night' else day,levels)])
  assert actual==expected,(name,mode,'compiled land slots',actual,expected)
  TABLES[name,'land',mode]=actual
  TABLE_CHECKS.append({'map':name,'area':'land','time_mode':mode,'slot_count':12,'compiled_slots_exact':True})
 actual=table_row('DragonDen_1F','water',mode)
 expected=(4,[(level,level,const('SPECIES_'+sp)) for sp,level in zip(*WATER)])
 assert actual==expected,('DragonDen',mode,'compiled water slots',actual,expected)
 TABLES['DragonDen_1F','water',mode]=actual
 TABLE_CHECKS.append({'map':'DragonDen_1F','area':'water','time_mode':mode,'slot_count':5,'compiled_slots_exact':True})
gd.FIELDS['pokemon.level']=('Pokemon','level');gd._OFFSETS=None
_trainer_bit=re.search(r'^#define\s+BATTLE_TYPE_TRAINER\s+\(1\s*<<\s*(\d+)\)',Path('include/constants/battle.h').read_text(),re.M)
assert _trainer_bit
TRAINER_BIT=1<<int(_trainer_bit.group(1))
node=next(n for n in ast.parse(Path('tools/qa/eventcheck.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='throw_ball')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<native-ball-input>','exec'),globals())
wait_action_menu=lambda e,rom:menu(e)
live_blocks=blocks;item_name=gd.item_name
def legal_checksum(raw,label):
 m=Mon(bytearray(raw),0);decrypted=b''.join(bytes(v) for v in m.subs().values())
 assert len(decrypted)==48
 assert (sum(v for(v,)in struct.iter_unpack('<H',decrypted))&65535)==struct.unpack_from('<H',raw,28)[0],(label,'checksum')
 assert not(raw[19]&1) and not m.is_egg(),(label,'Bad Egg/egg')
 return m

gd.FIELDS['sb1.registeredItem']=('SaveBlock1','registeredItem')
gd._OFFSETS=None
def clock_task(e):
 target=syms['Task_SetGameClock']&~1;raw=e.read(syms['gTasks'],40*16)
 rows=[(i//40,struct.unpack_from('<16h',raw,i+8)) for i in range(0,len(raw),40)
       if raw[i+4] and (struct.unpack_from('<I',raw,i)[0]&~1)==target]
 assert len(rows)<=1,'multiple native clock tasks'
 return rows[0] if rows else None
def native_set_hour(e,hour,tag):
 assert 0<=hour<24
 assert 'sUseRtc' in syms and 'sCachedTime' in syms and 'Task_SetGameClock' in syms
 before=snapshot(e);e.press('SELECT',hold=1,after=12)
 for _ in range(200):
  if yes_no_ready(e):break
  e.press('A',hold=1,after=8)
 assert yes_no_ready(e),(tag,'POKeWATCH native change-time question not reached')
 e.press('A',hold=1,after=12)
 for _ in range(100):
  if clock_task(e):break
  e.run(2)
 assert clock_task(e),(tag,'native clock edit window did not open')
 # Select hour using the game's current task state, then change via fresh directional inputs.
 for _ in range(3):
  if clock_task(e)[1][0]==1:break
  e.press('RIGHT',hold=1,after=4)
 assert clock_task(e)[1][0]==1
 for _ in range(24):
  data=clock_task(e)[1];current=data[2]
  if current==hour:break
  up=(hour-current)%24;down=(current-hour)%24
  e.press('UP' if up<=down else 'DOWN',hold=1,after=4)
 assert clock_task(e)[1][2]==hour,(tag,'native requested hour not selected')
 e.press('RIGHT',hold=1,after=4);assert clock_task(e)[1][0]==2
 for _ in range(60):
  minute=clock_task(e)[1][3]
  if minute==0:break
  e.press('DOWN' if minute<=30 else 'UP',hold=1,after=4)
 assert clock_task(e)[1][3]==0
 e.shot(str(out/(tag+'-native-clock-'+str(hour)+'.png')),scale=3)
 e.press('A',hold=1,after=12);settle(e);e.run(61)
 assert not clock_task(e) and blocks(e).flag('FLAG_GAME_CLOCK_SET')
 actual=e.u8(syms['sCachedTime']+off('time.hours'))
 assert actual==hour,(tag,'native RTC/virtual clock did not commit exact hour',actual,hour)
 after=snapshot(e)
 for field in ['flags','trainers','items']+PRESERVE:assert after[field]==before[field],(tag,'clock changed gameplay state',field)
 return {'requested_hour':hour,'native_hour':actual,'rtc_used':bool(e.u8(syms['sUseRtc'])),
  'method':'Native registered POKeWATCH SELECT/YES/directions/A','forced_memory_writes':0}

def encounter_fixture(path,c):
 s=fixture(path,{'where':c['where']})
 s.keep_party(1);s.set_var('VAR_REPEL_STEP_COUNT',0);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
 s.set_item('ITEM_MASTER_BALL',1);s.set_item('ITEM_POKE_WATCH',1)
 struct.pack_into('<H',s.sb1,off('sb1.registeredItem'),const('ITEM_POKE_WATCH'));s.save(str(path))
 return s
def walk_until_wild(e,c):
 start=e.location()
 if c['area']=='water':
  avatar_h=Path('include/global.fieldmap.h').read_text()
  enums=re.findall(r'enum\s*\{([^{}]*\bPLAYER_AVATAR_STATE_NORMAL\b[^{}]*)\}',re.sub(r'/\*.*?\*/|//[^\n]*','',avatar_h,flags=re.S))
  assert len(enums)==1 and '=' not in enums[0]
  states=re.findall(r'\bPLAYER_AVATAR_STATE_[A-Z_]+\b',enums[0])
  surf=1<<states.index('PLAYER_AVATAR_STATE_SURFING')
  assert e.u8(syms['gPlayerAvatar'])&surf,'native water boot did not mount Surf'
 points=[start[2:],(start[2]+1,start[3])]
 moves=0
 for attempt in range(800):
  if e.in_battle():break
  current=e.location();assert current[:2]==start[:2] and current[2:] in points,(c['name'],'left safe encounter corridor',current)
  key='RIGHT' if current[2:]==points[0] else 'LEFT'
  e.hold(key);e.run(1);e.hold();e.run(24)
  safe(e)
  if e.location()!=current:moves+=1
 else:raise AssertionError((c['name'],'no native random encounter after 800 fresh taps',moves,e.location()))
 assert menu(e),'wild action menu unavailable'
 assert not(e.u32(e.sym('gBattleTypeFlags'))&TRAINER_BIT),'random encounter was a trainer battle'
 assert not blocks(e).flag('FLAG_SYS_SPECIAL_WILD_BATTLE'),'random encounter inherited scripted wild state'
 assert 'sUseRtc' in syms,'native RTC mode symbol absent'
 assert 'sCachedTime' in syms,'native clock cache symbol absent'
 hour=e.u8(syms['sCachedTime']+off('time.hours'))
 assert {'morning':4<=hour<10,'day':10<=hour<20,'night':hour>=20 or hour<4}[c['mode']],(c['name'],'native time mode mismatch',hour)
 return moves,hour
def attempt(e,c,prepared):
 e.syms=syms;e.boot_continue();settle(e);e.run(60)
 clock=native_set_hour(e,c['hour'],c['name']);before=snapshot(e)
 moves,hour=walk_until_wild(e,c)
 raw=e.read(syms['gEnemyParty'],100);enemy=legal_checksum(raw,c['name']+' enemy');sp=enemy.species();level=raw[off('pokemon.level')]
 allowed=TABLES[c['where'][0],c['area'],c['mode']][1]
 assert any(lo<=level<=hi and species==sp for lo,hi,species in allowed),(c['name'],'wrong native species/level',sp,level)
 assert throw_ball(e,str(rom),'ITEM_MASTER_BALL',None) is None,'native capture bag input failed'
 settle(e);assert e.u8(e.sym('gBattleOutcome'))==7,(c['name'],'capture outcome')
 after=snapshot(e)
 assert after['flags']==before['flags'] and after['trainers']==before['trainers'],'random encounter changed story progress'
 assert after['party_count']==before['party_count']+1 and after['party_count']<=6
 assert after['pc']==before['pc']==bytes(prepared.blocks['storage'])
 for i in range(before['party_count']):
  old=before['party'][i*100:(i+1)*100];new=after['party'][i*100:(i+1)*100]
  a=legal_checksum(old,c['name']+' existing-before');b=legal_checksum(new,c['name']+' existing-after')
  assert old[:8]==new[:8] and a.species()==b.species(),'random encounter changed existing PID/OT/species'
 caught=legal_checksum(after['party'][before['party_count']*100:(before['party_count']+1)*100],c['name']+' caught')
 assert caught.species()==sp
 owner=struct.unpack_from('<I',blocks(e).sb2,off('sb2.playerTrainerId'))[0]
 assert caught.otid==owner,'native capture did not assign player OT'
 for item in ITEMS:assert after['items'][item]==before['items'][item],(c['name'],'unrelated reward changed',item)
 assert blocks(e).item_count('ITEM_MASTER_BALL')==0
 dex=struct.unpack('<H',r.at(syms['sSpeciesToNationalPokedexNum']+(sp-1)*2,2))[0]
 for i,(old,new) in enumerate(zip(before['dex'],after['dex']),1):
  assert new==((True,True,True,True) if i==dex else old),(c['name'],'native dex capture records',i,old,new)
 caught_id={'personality':caught.personality,'otid':caught.otid,'species':sp}
 e.shot(str(out/(c['name']+'.png')),scale=3);saved=flash_reload(e,c['name'])
 reloaded=snapshot(e);assert reloaded['party']==after['party'] and reloaded['dex']==after['dex']
 e.run(61);assert e.u8(syms['sCachedTime']+off('time.hours'))==c['hour'],'clock hour changed on cold load'
 cold=legal_checksum(reloaded['party'][before['party_count']*100:(before['party_count']+1)*100],c['name']+' cold')
 assert (cold.personality,cold.otid,cold.species())==(caught.personality,caught.otid,sp)
 return {'case':c['name'],'native_steps':moves,'native_clock_hour':hour,'native_clock_setting':clock,'time_mode':c['mode'],'species':sp,'level':level,
  'save':saved,'capture_identity':caught_id,'checksum_bad_egg_and_cold_identity_pass':True,'full_pc_preserved':True,
  'forced_game_memory_writes':0,'forced_battle_outcomes':0}
cases=[
 {'name':'route44_morning','where':('JohtoRoute44',6,6),'hour':6,'mode':'morning','area':'land'},
 {'name':'route44_day','where':('JohtoRoute44',6,6),'hour':12,'mode':'day','area':'land'},
 {'name':'route44_night','where':('JohtoRoute44',6,6),'hour':22,'mode':'night','area':'land'},
 *[{'name':n.lower()+'_day','where':(n,18,15),'hour':12,'mode':'day','area':'land'} for n in ['IcePath_1F','IcePath_B1F','IcePath_B2F']],
 {'name':'dragon_den_land','where':('DragonDen_1F',4,14),'hour':12,'mode':'day','area':'land'},
 {'name':'dragon_den_water','where':('DragonDen_1F',20,13),'hour':12,'mode':'day','area':'water'}]
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='blackthorn-native-wild-') as td:
  for c in cases:
   target=Path(td)/(c['name']+'.sav');prepared=encounter_fixture(target,c)
   with ReadOnlyEmu(str(rom),str(target),sym='') as e:row=attempt(e,c,prepared)
   results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==8 and len(TABLE_CHECKS)==18
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'native_cases':results,'compiled_table_checks':TABLE_CHECKS,
 'compiled_wild_abi':ABI,'all_pass':True,'original_files_unchanged':True,'forced_game_memory_writes':0,
 'forced_battle_outcomes':0,'full_johto_encounter_coverage_claimed':False},indent=2))
