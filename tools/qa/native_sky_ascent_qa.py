#!/usr/bin/env python3
"""Native Sky Pillar ascent; keys only after boot, original party/PC retained."""
from pathlib import Path
q=Path('tools/qa/native_hoenn_sea_sky_qa.py').read_text()
head=q.split('e=None\ntry:',1)[0]
old="choices=\"['seafloor','seafloor-early','seafloor-no-badge','sky','sky-early','city-storm','city-calm','gym-locked','gym-legacy','gym']\""
new="choices=\"['ascent','ascent-legacy','ascent-early']\""
assert head.count(old)==1
head=head.replace(old,new,1).replace('wo=weather_offsets()','wo={}')
exec(compile(head,'tools/qa/native_hoenn_sea_sky_qa.py','exec'))
import collections
assert not a.loss
report.update(mode='native-sky-'+a.case,fixture='temporary location/story fixture; genuine original full party retained',
 native_story_not_entire_regions=True,path=[],source_map_files_unchanged=False)
LAYOUTS={x['id']:x for x in json.loads(Path('data/layouts/layouts.json').read_text())['layouts'] if x.get('id')}
FLOORS=[('SkyPillar_1F',(10,1)),('SkyPillar_2F',(3,1)),('SkyPillar_3F',(11,1)),
 ('SkyPillar_4F',(3,1)),('SkyPillar_5F',(10,1)),('SkyPillar_Top',(14,9))]
source_maps={}
for name,target in FLOORS:
 m=json.loads((Path('data/maps')/name/'map.json').read_text());l=LAYOUTS[m['layout']]
 source_maps[l['blockdata_filepath']]=sha(Path(l['blockdata_filepath']).read_bytes())
source_storage=bytes(source.blocks['storage'][:off('storage')])
po=off('sb1.playerParty');original_party=bytes(source.sb1[po:po+600]);original_count=source.party_count()
original_dex=digest_dex(source)
assert original_count>0
party_valid(original_party,original_count)
assert 'VMap' in syms
fieldmap=Path('include/global.fieldmap.h').read_text()
assert re.search(r'struct BackupMapLayout\s*\{\s*s32 Xsize;\s*s32 Ysize;\s*u16 \*map;\s*\};',fieldmap)
def full_storage():
 return e.read(e.ptr('gPokemonStoragePtr'),off('storage'))
def invariants():
 assert full_storage()==source_storage,'full original storage changed'
 assert pc(e)==source_pc
 assert e.u8(syms['gPlayerPartyCount'])==original_count
 const_party=e.read(syms['gPlayerParty'],600);party_valid(const_party,original_count)
 normalized=bytearray(const_party);deltas=[]
 for i in range(original_count):
  old=Mon(bytearray(original_party),i*100);current=Mon(normalized,i*100)
  prior=old.subs()['G'][9];now=current.subs()['G'][9]
  assert prior<=now<=min(255,prior+12),('unexpected friendship change',i,prior,now)
  deltas.append(now-prior);current.set_friendship(prior)
 assert bytes(normalized)==original_party,'party changed beyond native walking friendship'
 report['native_walking_friendship_deltas']=deltas
 assert digest_dex(blocks(e))==original_dex,'original dex records changed'
def terrain(name):
 assert loc_is(e,name),(name,e.location())
 m=json.loads((Path('data/maps')/name/'map.json').read_text());l=LAYOUTS[m['layout']]
 vw,vh,p=struct.unpack('<iiI',e.read(syms['VMap'],12))
 assert (vw,vh)==(l['width']+15,l['height']+14),(name,vw,vh,l)
 assert 0x02000000<=p<0x03008000
 raw=e.read(p,vw*vh*2)
 grid=[struct.unpack_from('<H',raw,2*((y+7)*vw+x+7))[0]
       for y in range(l['height']) for x in range(l['width'])]
 return m,l,grid
def word(name,x,y):
 m,l,grid=terrain(name)
 return grid[y*l['width']+x]
def key_step(key):
 initial=e.location();e.hold(key)
 try:
  for _ in range(80):
   safe(e);assert not e.in_battle(),'unexpected wild battle on repel route'
   e.run(1)
   if e.location()!=initial:break
  else:raise AssertionError(('native step blocked',key,initial))
 finally:e.hold()
 for _ in range(40):
  safe(e);assert not e.in_battle(),'unexpected wild battle on repel route'
  e.run(1)
 return initial,e.location()
def route(name,target):
 m,l,grid=terrain(name);start=e.location()[2:]
 w,h=l['width'],l['height'];warps={(z['x'],z['y']) for z in m['warp_events']}-{target}
 actors={(o['xy'][0]-7,o['xy'][1]-7) for o in objects()
         if o['gfx']==const('OBJ_EVENT_GFX_RAYQUAZA') and not o['inanimate']}
 todo=collections.deque([start]);parents={start:None}
 while todo and target not in parents:
  x,y=todo.popleft()
  for dx,dy,key in [(0,-1,'UP'),(0,1,'DOWN'),(-1,0,'LEFT'),(1,0,'RIGHT')]:
   z=x+dx,y+dy
   if (0<=z[0]<w and 0<=z[1]<h and z not in parents and z not in warps
       and z not in actors and not(grid[z[1]*w+z[0]]&0xc00)):
    parents[z]=((x,y),key);todo.append(z)
 assert target in parents,('no native collision path',name,start,target,len(parents))
 path=[];z=target
 while z!=start:z,key=parents[z];path.append(key)
 path.reverse();row={'map':name,'start':list(start),'target':list(target),'keys':path,'steps':[]}
 for i,key in enumerate(path):
  before_step,after_step=key_step(key)
  row['steps'].append({'key':key,'from':list(before_step),'to':list(after_step)})
  if i<len(path)-1:
   assert loc_is(e,name),('premature warp',name,i,after_step)
   dx,dy={'UP':(0,-1),'DOWN':(0,1),'LEFT':(-1,0),'RIGHT':(1,0)}[key]
   assert after_step[2:]==(before_step[2]+dx,before_step[3]+dy),('step size',before_step,after_step)
 report['path'].append(row)
 if name!='SkyPillar_Top':
  next_name=FLOORS[[n for n,t in FLOORS].index(name)+1][0]
  for _ in range(1800):
   safe(e);assert not e.in_battle()
   if loc_is(e,next_name) and e.field_idle():break
   e.run(1)
  else:raise AssertionError(('stairs did not warp',name,next_name,e.location()))
 else:
  assert loc_is(e,name) and e.location()[2:]==target,e.location()
 photo(e,'native-ascent-'+name)
 invariants()
def safe_tile(expect_open):
 value=word('SkyPillar_4F',8,2)
 assert value==(0x3235 if expect_open else 0x3607),('story loose-stone tile',hex(value),expect_open)
 report.setdefault('stone_tile_checks',[]).append({'after_frame':e.frame(),'open':expect_open,'word':hex(value)})
e=None
try:
 with tempfile.TemporaryDirectory(prefix='native-sky-ascent-') as td:
  s=SaveFile(str(sav))
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  s.set_flag('FLAG_SYS_CRUISE_MODE',False)
  s.set_flag(SEA,a.case=='ascent')
  s.set_flag(RAY,False)
  s.set_flag(B8,a.case=='ascent-legacy')
  s.set_var('VAR_REPEL_STEP_COUNT',999)
  s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
  s.warp('SkyPillar_4F' if a.case=='ascent-early' else 'SkyPillar_1F',
         11 if a.case=='ascent-early' else 6,2 if a.case=='ascent-early' else 12)
  assert bytes(s.sb1[po:po+600])==original_party
  assert bytes(s.blocks['storage'][:off('storage')])==source_storage
  fixture=Path(td)/'fixture.sav';s.save(str(fixture));check_sectors(SaveFile(str(fixture)))
  e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e)
  kanto=[blocks(e).flag('FLAG_BADGE%02d_GET'%i) for i in range(1,9)]
  initial_flags=branch_flags();invariants()
  if a.case=='ascent-early':
   safe_tile(False)
   key_step('LEFT');key_step('LEFT');assert e.location()[2:]==(9,2),e.location()
   initial=e.location();e.press('LEFT',hold=60,after=40)
   assert e.location()==initial,'closed loose-stone tile became passable'
   safe_tile(False);assert branch_flags()==initial_flags
   native_save_reopen(e,source_pc);safe_tile(False);invariants()
   report['early_story_stairs_blocked']=True
  else:
   for name,target in FLOORS:
    if name=='SkyPillar_4F':
     safe_tile(True)
     native_save_reopen(e,source_pc);safe_tile(True);invariants()
    route(name,target)
   assert blocks(e).flag(RAY)==False
   z=legend('OBJ_EVENT_GFX_RAYQUAZA')
   assert z['xy']==[20,16] and not z['inanimate'] and z['anim'] in (0,4),z
   talk(e,'LEFT');seen=trace_scene()
   assert {10,6,9}<={z['anim'] for z in seen}
   assert any(z['xy'][1]<16 for z in seen)
   assert blocks(e).flag(RAY)
   assert blocks(e).flag(SEA)==(a.case=='ascent')
   assert blocks(e).flag(B8)==(a.case=='ascent-legacy')
   native_save_reopen(e,source_pc);invariants()
   assert blocks(e).flag(RAY)
   assert not any(o['gfx']==const('OBJ_EVENT_GFX_RAYQUAZA') for o in objects())
   report['native_full_ascent_and_awakening']=True
  assert [blocks(e).flag('FLAG_BADGE%02d_GET'%i) for i in range(1,9)]==kanto
  assert source_maps=={p:sha(Path(p).read_bytes()) for p in source_maps}
  report.update(source_map_files_unchanged=True,full_party_identity_preserved=True,
   full_storage_unchanged=True,dex_records_unchanged=True,native_stairs_warps=sum(n!='SkyPillar_Top' for n,t in FLOORS) if a.case!='ascent-early' else 0)
  report['pass']=True
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
