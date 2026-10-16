import pathlib,sys
src=pathlib.Path('outputs/regional-dex-story-v1/regional_ui_qa.py').read_text();prefix=src.split(' pristine=e.save_state()')[0]
tail=r"""
 import gamedata
 snap=e.save_state();results=[]
 def loc():
  p=e.ptr('gSaveBlock1Ptr');return (*struct.unpack('<hh',e.read(p,4)),e.u8(p+4),e.u8(p+5))
 def metric(label,m=None,walk=False,x=18,y=12):
  a=S+128;b=e.read(a,24);assert a+24<=0x02040000
  e.write(a,struct.pack('<10HI',0x1c01,0x0080,0x1840,0x00c0,0x4902,0x1840,0x8801,0x3101,0x8001,0x4770,sy['gTasks']+8))
  tid=call('CreateTask',a|1,255);assert tid<16
  t=sy['gTasks']+40*tid;c=e.u16(t+8);v=e.u32(sy['gMain']+36);f=e.frame();path=set();key='RIGHT'
  try:
   for i in range(360):
    q=loc()
    if m:assert q[2:]==(m['group'],m['num']) and q[1]==y and x-1<=q[0]<=x+2,('corridor',label,q)
    if walk:
     if q[0]>=x+1:key='LEFT'
     elif q[0]<=x:key='RIGHT'
     e.hold(key)
    else:e.hold()
    e.run(1);path.add(loc()[:2])
   dc=(e.u16(t+8)-c)&65535;dv=(e.u32(sy['gMain']+36)-v)&0xffffffff;df=e.frame()-f
   active=e.u8(t+4) and (e.u32(t)&~1)==a
   result=dict(label=label,hardware=df,vblank=dv,callbacks=dc,missed=max(0,df-dc),positions=sorted(path),pass_all=bool(active and dc==dv==df==360 and (not walk or len(path)>1)))
   emit('field_performance',result);results.append(result)
  finally:
   e.hold()
   if e.u8(t+4) and (e.u32(t)&~1)==a:call('DestroyTask',tid)
   e.write(a,b)
 try:
  for rr,name,x,y in ((1,'CherrygroveCity',18,13),(1,'JohtoRoute30',7,44)):
   e.load_state(snap);region(rr)
   if rr==1:call('FlagSet',0x1501)
   else:
    call('VarSet',gamedata.const('VAR_HOENN_SCENE_DEVON'),3)
    call('FlagSet',gamedata.const('FLAG_HOENN_PEEKO_RESCUED'))
   call('VarSet',gamedata.const('VAR_REPEL_STEP_COUNT'),250)
   m=gamedata.map_info(name);call('SetWarpDestination',m['group'],m['num'],255,x,y);call('DoWarp')
   for i in range(900):
    e.run(1)
    if loc()[2:]==(m['group'],m['num']) and e.field_idle():break
   else:raise AssertionError(('warp',name,loc()))
   e.run(30);assert e.field_idle();base=e.save_state()
   emit('map_fixture',dict(map=name,group=m['group'],num=m['num'],repel=250,scope='temporary copied SAV; emulated frame budget, not Delta FPS'))
   metric(name+'_idle',m,x=x,y=y);e.load_state(base);metric(name+'_walk',m,True,x=x,y=y)
 finally:e.load_state(snap)
 assert all(x['pass_all'] for x in results),'field performance/movement failure'
after=saves();after[str(sav)]=h(sav.read_bytes());assert after==old
emit('original_saves_preserved',True)
"""
exec(compile(prefix+tail,'field-performance','exec'))
