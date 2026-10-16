import sys,pathlib,struct,hashlib,json,atexit
R=pathlib.Path('/workspaces/pokefirered')
rom=pathlib.Path(sys.argv[1]).resolve();sav=pathlib.Path(sys.argv[2]).resolve()
def h(b):return hashlib.sha256(b).hexdigest()
def emit(k,v):print(json.dumps({k:v}),flush=True)
def saves():return {str(p):h(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}
old=saves();old[str(sav)]=h(sav.read_bytes())
atexit.register(lambda:emit('original_saves_final_check',dict(saves(),**{str(sav):h(sav.read_bytes())})==old))
b=pathlib.Path(sys.argv[3]).read_bytes();z=struct.unpack_from('<16sHHIIIIIHHHHHH',b)
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

 pristine=e.save_state()
 for f in (0x1208,0x1236,0x1500,0x1501):call('FlagClear',f)
 for n in range(1,387):
  call('GetSetPokedexFlag',n,2);call('GetSetPokedexFlag',n,3)
 call('CB2_OpenPokedexFromStartMenu');wait('Task_PokedexScreen',6)
 e.press('A');p=wait('Task_DexScreen_NumericalOrder',6)
 assert e.u8(p+66)==0 and e.u16(p+72)==151
 start=e.save_state()
 for label,keys in [('idle',()),('down',('DOWN',)),('up',('UP',)),('idle_repeat',())]:
  if label != 'up':e.load_state(start)
  p=dex();a=S+128;backup=e.read(a,24)
  e.write(a,struct.pack('<10HI',0x1c01,0x0080,0x1840,0x00c0,0x4902,0x1840,0x8801,0x3101,0x8001,0x4770,sy['gTasks']+8))
  tid=call('CreateTask',a|1,255);assert tid<16
  ta=sy['gTasks']+40*tid;c=e.u16(ta+8);v=e.u32(sy['gMain']+36);f=e.frame()
  try:
   e.hold(*keys);e.run(360);e.hold()
   active=e.u8(ta+4) and (e.u32(ta)&~1)==a
   dc=(e.u16(ta+8)-c)&65535;dv=(e.u32(sy['gMain']+36)-v)&0xffffffff;df=e.frame()-f
   emit('kanto_comparison',dict(case=label,rom_sha=h(rb),hardware=df,vblank=dv,tasks=dc,missed=max(0,df-dc),counter_survived=bool(active),task_data_sha=h(e.read(ta+8,32)),scope='same copied v1.2/all-seen/Kanto151/default numeric menu'))
   assert active and df==360 and abs(df-dv)<=1
  finally:
   e.hold()
   if e.u8(ta+4) and (e.u32(ta)&~1)==a:call('DestroyTask',tid)
   e.write(a,backup)
 e.load_state(pristine)
