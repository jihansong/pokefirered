import sys,pathlib,struct,hashlib,json,atexit
R=pathlib.Path('/workspaces/pokefirered')
rom=pathlib.Path(sys.argv[1]).resolve();sav=pathlib.Path(sys.argv[2]).resolve()
def h(b):return hashlib.sha256(b).hexdigest()
def emit(k,v):print(json.dumps({k:v}),flush=True)
def saves():return {str(p):h(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}
old=saves();old[str(sav)]=h(sav.read_bytes())
atexit.register(lambda:emit('original_saves_final_check',dict(saves(),**{str(sav):h(sav.read_bytes())})==old))
b=rom.with_suffix('.elf').read_bytes();z=struct.unpack_from('<16sHHIIIIIHHHHHH',b)
ss=[struct.unpack_from('<IIIIIIIIII',b,z[6]+i*z[11]) for i in range(z[12])];sy={}
for t in ss:
 if t[1]!=2:continue
 q=ss[t[6]];st=b[q[4]:q[4]+q[5]]
 for i in range(t[4],t[4]+t[5],t[9] or 16):
  n,v,sz,k,_,ix=struct.unpack_from('<IIIBBH',b,i)
  if n and ix:sy[st[n:st.find(b'\0',n)].decode()]=v&~1 if k&15==2 else v
rb=rom.read_bytes()
for q in ss:
 if q[2]&2 and q[1]!=8 and 0x08000000<=q[3]<0x0a000000 and q[5]:assert rb[q[3]-0x08000000:q[3]-0x08000000+q[5]]==b[q[4]:q[4]+q[5]],'ELF/ROM'
end=max(q[3]+q[5] for q in ss if q[2]&2 and 0x02000000<=q[3]<0x02040000);S=(end+3)&~3
assert S+96<=0x02040000,'no safe emulator-only scratch'
assert (R/'tools/qa/libqa.so').stat().st_mtime>=(R/'tools/qa/libqa.c').stat().st_mtime,'QA lib rebuild needed; stopped'
sys.path.insert(0,str(R/'tools/qa'))
from emu import Emu
emit('identity',dict(rom_sha=h(rb),save_sha=h(sav.read_bytes()),ewram_free=0x02040000-end,scratch=hex(S),scope='copied SAV, temporary emulator-only native function fixture'))
with Emu(str(rom),str(sav),sym='') as e:
 e.syms=sy;e.boot_continue();e.run(30);assert e.field_idle(),'not field idle'
 def w(a,v):e.write(a,struct.pack('<I',v))
 def call(name,*args):
  assert len(args)<=6
  prev=e.callback2();backup=e.read(S,96)
  vals={'cb':sy['gMain']+4,'prev':prev,**{'a'+str(i):v for i,v in enumerate(list(args)+[0]*(6-len(args)))},'ret':S+35,'fn':sy[name]|1,'res':S+88}
  ins=[0xb510,0xb082,('l',4,'cb'),('l',0,'prev'),0x6020,('l',0,'a0'),('l',1,'a1'),('l',2,'a2'),('l',3,'a3'),('l',4,'a4'),0x9400,('l',4,'a5'),0x9401,('l',4,'ret'),0x46a6,('l',4,'fn'),0x4720,('l',4,'res'),0x6020,0xb002,0xbd10,0x46c0]
  keys=list(vals)
  for i,q in enumerate(ins):
   if isinstance(q,tuple):
    disp=S+44+4*keys.index(q[2])-((S+2*i+4)&~3);assert 0<=disp<=1020 and disp%4==0;ins[i]=0x4800+(q[1]<<8)+disp//4
  code=struct.pack('<22H',*ins)+struct.pack('<11I',*vals.values());assert len(code)==88
  try:
   e.write(S,code+struct.pack('<I',0xdecafbad));w(sy['gMain']+4,S|1);e.run(1);value=e.u32(S+88)
   for _ in range(20):
    if value!=0xdecafbad:break
    e.run(1);value=e.u32(S+88)
   assert value!=0xdecafbad,'native call did not return: '+name
   return value
  finally:e.write(S,backup)
 def dex():return e.ptr('sPokedexScreenData')
 def task(name):
  for i in range(16):
   a=sy['gTasks']+i*40
   if e.u8(a+4) and e.u32(a)&~1==sy[name]:return i
 def wait(name,state,limit=700):
  for _ in range(limit):
   e.run(1);p=dex()
   if p and task(name) is not None and e.u8(p+1)==state:e.run(24);return dex()
  raise AssertionError('timeout: '+name+' state '+str(state))
 def region(r):
  for f in (0x1208,0x1236,0x1500,0x1501):call('FlagClear',f)
  if r:call('FlagSet',0x1500 if r==1 else 0x1236)
  assert call('GetStoryRegionalDex')==r
 def number(win,n,x=9,y=0):
  a=sy['gWindows']+win*12;wd=e.u8(a+3);ht=e.u8(a+4);p=e.u32(a+8);assert 0<wd<=32 and 0<ht<=32 and 0x02000000<=p<0x02040000
  raw=e.read(p,wd*ht*32)
  def crop(q):return bytes((q[((yy//8)*wd+xx//8)*32+(yy%8)*4+(xx%8)//2]>>(4*(xx%2)))&15 for yy in range(y,y+12) for xx in range(x,x+18))
  actual=crop(raw);call('FillWindowPixelRect',win,0,x,y,18,12);call('DexScreen_PrintNum3LeadingZeroes',win,0,n,x,y,0);expected=crop(e.read(p,len(raw)));e.write(p,raw);assert actual==expected,'printed dex number mismatch '+str(n)
 from pathlib import Path
 from gamedata import const,map_info,CONST_HEADERS
 from savefile import Mon
 import json,struct
 if 'constants/time_of_day.h' not in CONST_HEADERS:CONST_HEADERS.append('constants/time_of_day.h')
 j=json.loads(Path('tools/johto/route31_wild.json').read_text())
 mi=map_info('JohtoRoute31')
 symbols={const('TIME_MORNING'):('gWildMonHeadersMorning','land_mons_morning'),const('TIME_DAY'):('gWildMonHeaders','land_mons'),const('TIME_NIGHT'):('gWildMonHeadersNight','land_mons_night')}
 cases=[(0,0,2),(3,59,2),(4,0,0),(4,17,0),(9,59,0),(10,0,1),(10,17,1),(19,59,1),(20,0,2),(20,17,2),(23,59,2)]
 state=e.save_state();results=[]
 def route_info(address):
  matches=[]
  for k in range(2048):
   p=address+20*k
   group,num=struct.unpack('<BB',e.read(p,2))
   if group==255:break
   if (group,num)==(mi['group'],mi['num']):matches.append(e.u32(p+4))
  else:raise AssertionError('missing wild header sentinel')
  assert len(matches)==1 and matches[0],matches
  return matches[0]
 try:
  for hour,minute,phase in cases:
   e.load_state(state)
   call('SetGameClock',0,hour,minute)
   call('TimeOfDay_InvalidateCache')
   actual=call('GetTimeOfDay');assert actual==phase,(hour,minute,actual,phase)
   selected=call('GetTimeOfDayWildMonHeaders')
   name,field=symbols[phase]
   assert selected==sy[name],(hour,minute,hex(selected),hex(sy[name]))
   info=route_info(selected);rate=e.u8(info);mons=e.u32(info+4)
   decoded=[struct.unpack('<BBH',e.read(mons+4*i,4)) for i in range(12)]
   expected=[(m['min_level'],m['max_level'],const(m['species'])) for m in j[field]['mons']]
   assert rate==j[field]['encounter_rate'] and decoded==expected,(field,decoded,expected)
   item={'time':f'{hour:02}:{minute:02}','phase':phase,'table':name,'address':hex(selected),'rate':rate,'native_slots':decoded}
   if minute==17:
    seen=set();samples=[]
    for seed in range(48):
     call('SeedWildEncounterRng',seed*997+17)
     assert call('TryGenerateWildMon',info,0,0)==1
     raw=bytearray(e.read(sy['gEnemyParty'],100));mon=Mon(raw,0)
     species,level=mon.species(),mon.level()
     assert any(sp==species and lo<=level<=hi for lo,hi,sp in expected),(field,species,level)
     assert mon.has_species() and not mon.is_egg() and not (raw[19]&1)
     dec=b''.join(bytes(mon.subs()[c]) for c in 'GAEM')
     assert (sum(v[0] for v in struct.iter_unpack('<H',dec))&65535)==struct.unpack_from('<H',raw,28)[0]
     samples.append([species,level]);seen.add(species)
    opposite=j['land_mons_night' if phase!=2 else 'land_mons']['mons']
    exclusive={sp for _,_,sp in expected}-{const(m['species']) for m in opposite}
    assert seen&exclusive,('no time-exclusive species sampled',field,seen)
    item['generated_count']=len(samples);item['generated_species']=sorted(seen);item['native_generated_samples']=samples
   results.append(item)
  emit('route31_clock_tables_and_generated_mons',{'cases':results,'boundary_and_midminute_checks':len(results),'native_generated_total':144,'limits':'Native table selection and generated encrypted records; walking encounter UI is covered separately.'})
 finally:
  e.load_state(state)

after=saves();after[str(sav)]=h(sav.read_bytes());assert after==old
emit('original_saves_preserved',True)
