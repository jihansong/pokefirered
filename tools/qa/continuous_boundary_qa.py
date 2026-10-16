import pathlib,sys
src=pathlib.Path(sys.argv[1]).read_text();marker=' pristine=e.save_state()'
assert marker in src
prefix=src.split(marker)[0];sys.argv=[sys.argv[0],sys.argv[2],sys.argv[3]]
tail=r''' snap=e.save_state()
 try:
  for n in range(1,387):
   call('GetSetPokedexFlag',n,2);call('GetSetPokedexFlag',n,3)
  region(0);call('CB2_OpenPokedexFromStartMenu');wait('Task_PokedexScreen',6)
  e.press('A');wait('Task_DexScreen_NumericalOrder',6)
  e.hold('DOWN');e.run(80);e.hold();e.run(20)
  p=dex();tid=e.u8(p+65);lm=sy['gTasks']+tid*40+8
  cb=sy['CB2_PokedexScreen']|1;assert e.callback2()==cb
  assert not(e.u16(0x0400010a)&128),'Timer2 in use'
  a=S+128
  e.write(a,struct.pack('<10HI',0x1c01,0x0080,0x1840,0x00c0,0x4902,0x1840,0x8801,0x3101,0x8001,0x4770,sy['gTasks']+8))
  taskid=call('CreateTask',a|1,255);assert taskid<16
  taskptr=sy['gTasks']+taskid*40
  block=call('AllocZeroed',16656);assert block and block%4==0
  assert 0x02000000<=block<block+16656<=0x02040000
  meta=block+256;data=block+272
  ops=bytes.fromhex('70b5204e30682049884235d245011f496d181f491f4808601f49088828601f490868a8601e49088868611e490868a8611d4c002060802080812060801b48864614480047208828610020608012490888686012490868e86012490868e8613068013030600a4908680a4a904202d11048086070bd706070bd0120b06004490548086070bd')
  code=ops+struct.pack('<12I',meta,512,data,sy['gMain']+4,cb,0x04000006,sy['gMain']+36,sy['gMain']+48,lm+24,0x04000108,(block+68)|1,block|1)
  assert len(code)==180
  e.write(block,code);e.run(20);base=e.save_state()
  lp=e.u32(lm);maxshow=e.u16(lm+14);total=e.u16(lm+12)
  runs=[]
  for observer in (False,True):
   e.load_state(base)
   if observer:w(sy['gMain']+4,block|1)
   dc0=e.u16(taskptr+8);dv0=e.u32(sy['gMain']+36);df0=e.frame()
   e.hold('DOWN')
   for _ in range(360):e.run(1)
   dc=(e.u16(taskptr+8)-dc0)&65535;dv=(e.u32(sy['gMain']+36)-dv0)&0xffffffff;df=e.frame()-df0
   runs.append(dict(observer=observer,hardware=df,vblank=dv,tasks=dc,missed=df-dc))
   if observer:
    count=e.u32(meta);assert 0<count<=512 and e.u32(meta+4)==e.u32(meta+8)==0
    rows=[]
    for j in range(count):
     vc0,vc1,vb0,vb1,ticks,keys,before,after=struct.unpack('<8I',e.read(data+32*j,32))
     first0,row0=before&65535,before>>16;first1,row1=after&65535,after>>16
     idx=first1+maxshow-1 if first1>first0 else first1
     item=e.u32(lp+idx*8+4)&65535 if 0<=idx<total else -1
     lines=(160-vc0)%228 or 228
     rows.append(dict(call=j,vc=[vc0,vc1],vblank_cross=(vb1-vb0)&0xffffffff,cycles=ticks*64,key=keys,before=[first0,row0],after=[first1,row1],new_row_species=item,deadline_cycles=[(lines-1)*1232,lines*1232]))
    crosses=[q for q in rows if q['vblank_cross']]
    emit('continuous_cb2_boundary_probe',dict(scope='RAM-only trace; includes IRQ/DMA time',rom_sha256=h(rb),runs=runs,observer_task_difference=runs[1]['tasks']-runs[0]['tasks'],completed_callbacks=count,scroll_callbacks=sum(q['before']!=q['after'] for q in rows),crossed_vblank_count=len(crosses),crossed_vblank=crosses,worst=sorted(rows,key=lambda q:q['cycles'],reverse=True)[:8]))
 finally:e.load_state(snap)
after=saves();after[str(sav)]=h(sav.read_bytes());assert after==old
emit('original_saves_preserved',True)
'''
exec(compile(prefix+tail,'continuous_boundary_qa','exec'))
