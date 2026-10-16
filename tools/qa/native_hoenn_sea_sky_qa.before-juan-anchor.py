#!/usr/bin/env python3
"""Native sea/sky chapter QA: battle, scenes, gates, receipts and cold saves."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/'tools/qa'))
import gamedata as gd
gd.FIELDS.update({'obj':('ObjectEvent',None),'sb1.weather':('SaveBlock1','weather')})
gd.CONST_HEADERS+=['constants/event_objects.h','constants/weather.h']
head=Path('tools/qa/hoenn_weather_space_native_qa.py').read_text().split('e=None\ntry:',1)[0]
choices="['seafloor','seafloor-early','seafloor-no-badge','sky','sky-early','city-storm','city-calm','gym-locked','gym-legacy','gym']"
assert head.count("choices=['weather-party','weather-pc','space']")==1
head=head.replace("choices=['weather-party','weather-pc','space']","choices="+choices)
exec(compile(head,'tools/qa/hoenn_weather_space_native_qa.py','exec'))
assert not a.loss or a.case in ('seafloor','gym')
SEA='FLAG_HOENN_SEAFLOOR_CLEARED';RAY='FLAG_HOENN_RAYQUAZA_AWAKENED'
B7='FLAG_HOENN_BADGE07_GET';B8='FLAG_HOENN_BADGE08_GET'
receipts=re.findall(r'^#define\s+(FLAG_HOENN_GOT_TM03_\w+)\s+',Path('include/constants/flags_hoenn_story.h').read_text(),re.M)
assert len(receipts)==1,('Juan receipt name',receipts)
TMFLAG=receipts[0]
flags=[SEA,RAY,B7,B8,TMFLAG,SF,HF]
WT='TRAINER_HOENN_ARCHIE';TT='TRAINER_HOENN_JUAN_1';MT=WT
C='SeafloorCavern_Room9';Y='SkyPillar_Top';J='SootopolisCity_Gym_1F';T='SootopolisCity'
report.update(mode='native-sea-sky-'+a.case+('-loss' if a.loss else ''),
 fixture='temporary level-100 battle fixture; original PC/source SAV unchanged',
 native_story_not_entire_regions=True,stages=[])
assert off('obj')==0x24
sprite_source=Path('include/sprite.h').read_text()
assert '/*0x2A*/ u8 animNum;' in sprite_source and '/*0x43*/ u8 subpriority;' in sprite_source
def objects():
 rows=[]
 m=e.location()[:2]
 for i in range(const('OBJECT_EVENTS_COUNT')):
  b=e.read(syms['gObjectEvents']+i*off('obj'),off('obj'))
  if b[0]&1 and (b[10],b[9])==m:
   rows.append({'slot':i,'sprite':b[4],'gfx':b[5],'local_id':b[8],
    'xy':list(struct.unpack_from('<hh',b,16)),
    'inanimate':bool(b[1]&16),'anim':e.u8(syms['gSprites']+b[4]*0x44+0x2a)})
 return rows
def legend(gfx):
 z=[o for o in objects() if o['gfx']==const(gfx)]
 assert len(z)==1,(gfx,objects())
 return z[0]
def trace_scene():
 seen=[];last=None;photos=set()
 for i in range(12000):
  assert not e.in_battle(),'scene entered a battle'
  row=[o for o in objects() if o['gfx']==const('OBJ_EVENT_GFX_RAYQUAZA')]
  if row:
   z=row[0];now=(z['anim'],tuple(z['xy']))
   if now!=last:seen.append({'frame':e.frame(),**z});last=now
   if z['anim'] not in photos:
    photos.add(z['anim']);photo(e,'ray-native-anim-'+str(z['anim']))
  if e.field_idle():break
  safe(e)
  if i%8==0:e.press('A',hold=1,after=1)
  else:e.run(1)
 else:raise AssertionError(('scene timeout',e.location()))
 report['rayquaza_native_animation_trace']=seen
 return seen
def clear_actor_flags(s):
 for f in flags:s.set_flag(f,False)
 for tr in [WT,TT]:s.set_trainer_beaten(tr,False)
 s.set_flag(SF,a.case!='seafloor-early')
 s.set_flag(B7,a.case!='seafloor-no-badge')
 if a.case in ('sky','city-storm','city-calm','gym-locked','gym'):
  s.set_flag(SEA,True)
 if a.case in ('city-calm','gym'):s.set_flag(RAY,True)
 if a.case=='gym-legacy':
  s.set_flag(B8,True);s.set_trainer_beaten(TT,True)
 s.set_item('ITEM_TM03',0)
def make_party(s):
 s.keep_party(1)
 owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
 m=s.party_mon(0);m.set_otid(owner);m.set_starter_bit(False);m.set_snagged(False)
 m.set_species(const('SPECIES_MAGIKARP' if a.loss else 'SPECIES_MEWTWO'),rom=r)
 sub=m.subs();sub['E'][:6]=bytes(6);sub['G'][8]=0 if a.loss else 255;sub['A'][:]=bytes(12)
 moves=['MOVE_SPLASH'] if a.loss else ['MOVE_AERIAL_ACE','MOVE_THUNDERBOLT','MOVE_ICE_BEAM','MOVE_SHADOW_BALL']
 for i,name in enumerate(moves):
  mid=const(name);struct.pack_into('<H',sub['A'],i*2,mid)
  pp=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  sub['A'][8+i]=pp if a.loss else pp*8//5
 struct.pack_into('<I',sub['M'],4,struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30))
 m.put_subs(sub);m.blk[m.o+19]=(m.blk[m.o+19]&~5)|2
 m.set_held(const('ITEM_NONE' if a.loss else 'ITEM_LEFTOVERS'))
 m.make_strong(1 if a.loss else 100,rom=r)
def weather_offsets():
 members=['currWeather','nextWeather','weatherChangeComplete','rainSpriteCount','targetRainSpriteCount']
 c='#include "global.h"\n#include "field_weather.h"\n'
 for m in members:c+='char qa_weather_'+m+'[offsetof(struct Weather, '+m+') + 1];\n'
 with tempfile.TemporaryDirectory(prefix='weather-read-offsets-') as td:
  f=Path(td)/'weather.c';o=Path(td)/'weather.o';f.write_text(c)
  subprocess.run([str(dka/'bin/arm-none-eabi-gcc'),'-c','-w','-mthumb','-mabi=apcs-gnu','-march=armv4t',
   '-fcommon','-iquote','include','-DLEAFGREEN','-DREVISION=0','-DENGLISH','-DMODERN=1','-o',str(o),str(f)],check=True)
  raw=subprocess.check_output([str(dka/'bin/arm-none-eabi-nm'),'-S',str(o)],text=True)
 result={}
 for line in raw.splitlines():
  z=line.split()
  if len(z)==4 and z[3].startswith('qa_weather_'):result[z[3][11:]]=int(z[1],16)-1
 assert set(result)==set(members),result
 return result
wo=weather_offsets()
def strict_weather(expected):
 for _ in range(1200):
  p=e.ptr('gWeatherPtr')
  z={m:e.u8(p+o) for m,o in wo.items()}
  if z['currWeather']==z['nextWeather']==expected and z['weatherChangeComplete']:break
  safe(e);e.run(1)
 else:raise AssertionError(('native weather did not settle',z,expected))
 assert active_task(e,'Task_WeatherMain'),('weather native task inactive',z)
 if expected==const('WEATHER_RAIN_THUNDERSTORM'):
  assert z['rainSpriteCount']>0 and z['targetRainSpriteCount']>0,('storm has no native rain sprites',z)
 else:assert z['rainSpriteCount']==0,('calm left native rain sprites',z)
 return z

def branch_flags():
 return {f:blocks(e).flag(f) for f in flags}
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-sea-sky-qa-') as td:
  s=SaveFile(str(sav));s.fast_battles()
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False);clear_actor_flags(s);make_party(s)
  if a.case.startswith('seafloor'):s.warp(C,13,42)
  elif a.case.startswith('sky'):s.warp(Y,14,9)
  elif a.case.startswith('city'):s.warp(J,8,24)
  else:s.warp(J,8,3)
  assert bytes(s.blocks['storage'][boxoff:boxoff+cs])==source_pc
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  kanto=[blocks(e).flag('FLAG_BADGE%02d_GET'%i) for i in range(1,9)]
  initial_flags=branch_flags()
  if a.case=='seafloor':
   assert loc_is(e,C)
   ky=legend('OBJ_EVENT_GFX_KYOGRE');assert ky['xy']==[24,46],ky
   photo(e,'native-seafloor-before')
   talk(e,'RIGHT');native_battle(e,WT,3)
   if a.loss:
    assert not loc_is(e,C) and not blocks(e).flag(SEA)
   else:
    assert loc_is(e,C) and blocks(e).flag(SEA) and not blocks(e).flag(RAY)
    assert not any(o['gfx'] in (const('OBJ_EVENT_GFX_KYOGRE'),const('OBJ_EVENT_GFX_ARCHIE')) for o in objects())
    native_save_reopen(e,source_pc)
    assert blocks(e).flag(SEA)
    assert not any(o['gfx'] in (const('OBJ_EVENT_GFX_KYOGRE'),const('OBJ_EVENT_GFX_ARCHIE')) for o in objects())
    report['native_seafloor_battle_and_scene']=True
  elif a.case in ('seafloor-early','seafloor-no-badge'):
   talk(e,'RIGHT');quiet_finish(e)
   assert branch_flags()==initial_flags and not blocks(e).trainer_beaten(WT)
   report['seafloor_gate_rejected']=True
  elif a.case.startswith('sky'):
   assert loc_is(e,Y);z=legend('OBJ_EVENT_GFX_RAYQUAZA')
   assert z['xy']==[20,16] and z['anim']==0 and not z['inanimate'],z
   photo(e,'native-sky-before');talk(e,'LEFT')
   if a.case=='sky-early':
    quiet_finish(e);assert branch_flags()==initial_flags
    assert legend('OBJ_EVENT_GFX_RAYQUAZA')['anim']==0
    report['sky_early_rejected']=True
   else:
    seen=trace_scene();nums={z['anim'] for z in seen}
    assert {10,6,9}<=nums,('native awake/call/rise animation missing',nums)
    assert any(z['xy'][1]<16 for z in seen),'Rayquaza did not rise'
    assert blocks(e).flag(RAY) and blocks(e).flag(SEA) and not blocks(e).flag(B8)
    assert not any(z['gfx']==const('OBJ_EVENT_GFX_RAYQUAZA') for z in objects())
    native_save_reopen(e,source_pc)
    assert blocks(e).flag(RAY) and not any(z['gfx']==const('OBJ_EVENT_GFX_RAYQUAZA') for z in objects())
    report['native_rayquaza_wake_and_rise']=True
  elif a.case.startswith('city'):
   # A genuine map transition runs the weather script; cold boot keeps saved weather.
   e.walk('DOWN');mash_until(e,lambda:loc_is(e,T) and e.field_idle(),220)
   e.walk('DOWN');go(e,28,34);talk(e,'UP');quiet_finish(e)
   expected=const('WEATHER_RAIN_THUNDERSTORM' if a.case=='city-storm' else 'WEATHER_SUNNY')
   weather=e.u8(e.ptr('gSaveBlock1Ptr')+off('sb1.weather'))
   assert weather==expected,('city weather',weather,expected)
   report['weather_runtime_before_save']=strict_weather(expected)
   photo(e,'native-city-'+a.case)
   assert branch_flags()==initial_flags
   native_save_reopen(e,source_pc)
   assert e.u8(e.ptr('gSaveBlock1Ptr')+off('sb1.weather'))==expected
   report['weather_runtime_after_cold_save']=strict_weather(expected)
   report['native_weather_and_wallace']={'weather':expected,'cold_save':True}
  elif a.case=='gym-locked':
   talk(e,'UP');quiet_finish(e)
   assert branch_flags()==initial_flags and not blocks(e).trainer_beaten(TT)
   assert blocks(e).item_count('ITEM_TM03')==0
   report['juan_storm_gate_rejected']=True
  elif a.case=='gym-legacy':
   talk(e,'UP');quiet_finish(e)
   assert blocks(e).flag(B8) and not blocks(e).flag(RAY)
   assert blocks(e).flag(TMFLAG) and blocks(e).item_count('ITEM_TM03')==1
   talk(e,'UP');quiet_finish(e)
   assert blocks(e).item_count('ITEM_TM03')==1
   report['legacy_badge_preserved_and_tm_retry']=True
  else:
   talk(e,'UP');native_battle(e,TT,5)
   if a.loss:
    assert not loc_is(e,J) and not blocks(e).flag(B8) and not blocks(e).flag(TMFLAG)
   else:
    assert loc_is(e,J) and blocks(e).flag(B8) and blocks(e).flag(TMFLAG)
    assert blocks(e).item_count('ITEM_TM03')==1
    talk(e,'UP');quiet_finish(e)
    assert blocks(e).item_count('ITEM_TM03')==1
    report['native_juan_gated_win_and_once_tm03']=True
  assert pc(e)==source_pc
  assert [blocks(e).flag('FLAG_BADGE%02d_GET'%i) for i in range(1,9)]==kanto
  native_save_reopen(e,source_pc)
  report['story_flags_after']=branch_flags();report['pass']=True
except Exception as ex:
 report['error']=repr(ex);report['traceback']=traceback.format_exc()
 if e and e.h:
  report['failure_location']=e.location();report['failure_callback2']=hex(e.callback2());photo(e,'failure')
finally:
 if e:e.close()
 after={p:sha(Path(p).read_bytes()) for p in before}
 report['original_saves_unchanged']=before==after
 if before!=after:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='traceback'}),flush=True)
sys.exit(0 if report['pass'] else 1)
