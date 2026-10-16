import pathlib,sys
base=pathlib.Path('outputs/regional-dex-story-v1/regional_ui_qa.py').read_text().split(' pristine=e.save_state()')[0]
base=base.replace('def number(win,n,x=9,y=0):','def number(win,n,x=9,y=0,bg=False):')
base=base.replace("actual=crop(raw);call('FillWindowPixelRect',win,0,x,y,18,12);","actual=crop(raw)\n  if bg:call('CopyToWindowPixelBuffer',win,sy['sCategoryMonInfoBgTiles'],0,0)\n  else:call('FillWindowPixelRect',win,0,x,y,18,12)\n  " )
tail=r'''
 pristine=e.save_state()
 def heap():
  p=e.ptr('sHeapStart');start=p;free=[]
  for _ in range(1000):
   flag,magic,size,prev,nxt=struct.unpack('<HHIII',e.read(p,16));assert magic==0xa3a3 and size<0x40000,'heap corruption'
   if not flag:free.append(size)
   if nxt==start:return {'free':sum(free),'largest':max(free,default=0)}
   assert nxt>p and nxt<0x02040000;p=nxt
  raise AssertionError('heap loop')
 def perf(label,frames=360,keys=()):
  a=S+128;backup=e.read(a,24);e.write(a,struct.pack('<10HI',0x1c01,0x0080,0x1840,0x00c0,0x4902,0x1840,0x8801,0x3101,0x8001,0x4770,sy['gTasks']+8));tid=call('CreateTask',a|1,255);assert tid<16
  ta=sy['gTasks']+tid*40;c=e.u16(ta+8);v=e.u32(sy['gMain']+36);f=e.frame()
  try:
   e.hold(*keys);e.run(frames);e.hold();active=e.u8(ta+4) and (e.u32(ta)&~1)==a;dc=(e.u16(ta+8)-c)&65535;dv=(e.u32(sy['gMain']+36)-v)&0xffffffff;df=e.frame()-f
   emit('performance',dict(label=label,hardware_frames=df,vblanks=dv,task_callbacks=dc,missed=max(0,df-dc),counter_survived=bool(active),scope='mGBA frame budget; not host FPS or Delta device latency'));assert active and abs(df-dv)<=1,'counter or hardware/VBlank failure'
  finally:
   e.hold()
   if e.u8(ta+4) and (e.u32(ta)&~1)==a:call('DestroyTask',tid)
   e.write(a,backup)
 def close_dex():
  e.press('B')
  for i in range(900):
   e.run(1)
   if e.field_idle():return
   if e.in_overworld() and i%30==0:e.press('B')
  raise AssertionError('dex did not close to idle field')
 def select(mode):
  for _ in range(24):
   p=dex();tid=e.u8(p+23);lm=sy['gTasks']+40*tid+8;ix=e.u16(lm+24)+e.u16(lm+26);selected=e.u32(e.u32(lm)+8*ix+4)
   if selected==mode:e.press('A');return
   e.press('DOWN')
  raise AssertionError('missing menu mode '+str(mode))
 perf('loaded_save_overworld_idle')
 for n in range(1,387):call('GetSetPokedexFlag',n,2);call('GetSetPokedexFlag',n,3)
 baseline=e.save_state()
 for r in range(3):
  e.load_state(baseline);region(r);call('CB2_OpenPokedexFromStartMenu');p=wait('Task_PokedexScreen',6);top=e.save_state()
  for cat in range(9):
   e.load_state(top);select(cat);p=wait('Task_DexScreen_CategorySubmenu',5);assert not e.u8(p+111);count=e.u8(p+44);assert 1<=count<=4
   for i in range(count):
    nat=call('SpeciesToNationalPokedexNum',e.u16(p+24+2*i));n=e.u16(p+112+2*nat);assert n>0,'out-of-region species in category';number(e.u8(p+36+i),n,21,0,True)
  emit('categories',dict(profile=r,pages=9,pass_all=True));e.load_state(top);select(9);p=wait('Task_DexScreen_NumericalOrder',6);perf('regional_'+str(r)+'_scroll',keys=('DOWN',));e.load_state(top)
  if call('IsNationalPokedexEnabled'):
   select(14);p=wait('Task_DexScreen_NumericalOrder',6);assert e.u8(p+66)==5 and e.u8(p+111) and e.u16(p+72)==386;e.press('A');p=wait('Task_DexScreen_ShowMonPage',5);number(e.u8(p+75),1);emit('national_switch',dict(profile=r,count=386,pass_all=True))
  else:emit('national_switch',dict(profile=r,skipped='national not unlocked in source save'))
  sizes=[]
  for _ in range(3):
   e.load_state(top) if not sizes else call('CB2_OpenPokedexFromStartMenu');wait('Task_PokedexScreen',6);close_dex();sizes.append(heap())
  assert sizes[0]==sizes[1]==sizes[2],('dex heap leak',sizes);emit('dex_close_heap',dict(profile=r,cycles=sizes,pass_all=True))
 e.load_state(pristine)
emit('supplement_complete',dict(functional_ui_only=True,performance_status='reported separately; baseline scrolling misses are not a pass'))
'''
assert 'def number' in base;exec(compile(base+tail,'regional_supplement','exec'))
