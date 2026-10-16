_field_done=set()
def field_budget(label,e,elf,rom,syms,expected_weather,weather_offsets):
 import struct,json,gamedata
 from emu import Emu as PlainEmu
 location=e.location();selected=None
 for name,mask,left,right,y in (('SootopolisCity',1,28,29,34),):
  m=gamedata.map_info(name)
  if location[:2]==(m['group'],m['num']):selected=(name,mask,left,right,y)
 if selected is None or (label,selected[0]) in _field_done:return
 name,mask,left,right,y=selected
 assert location[3]==y and left<=location[2]<=right,(name,location)
 eb=elf.read_bytes();eh=struct.unpack_from('<16sHHIIIIIHHHHHH',eb)
 sections=[struct.unpack_from('<IIIIIIIIII',eb,eh[6]+i*eh[11]) for i in range(eh[12])]
 sc=(max(q[3]+q[5] for q in sections if q[2]&2 and 0x02000000<=q[3]<0x02040000)+3)&~3
 assert sc+88<=0x02040000
 original_frame=e.frame();state=e.save_state();results=[]
 with PlainEmu(str(rom),None,sym='') as pe:
  pe.syms=e.syms.copy();pe.load_state(state)
  assert pe.location()==location and pe.field_idle(),'clone state load'
  def invoke2(name,arg0,arg1):
   assert 0<=arg1<256
   vals={'cb':syms['gMain']+4,'prev':pe.callback2(),'a0':arg0,'ret':(sc+20)|1,'fn':syms[name]|1,'res':sc+56}
   ins=[0xb510,('l',2,'cb'),('l',3,'prev'),0x6013,('l',0,'a0'),0x2100|arg1,('l',2,'ret'),0x4696,('l',2,'fn'),0x4710,('l',2,'res'),0x6010,0xbd10,0x46c0]
   keys=list(vals)
   for i,v in enumerate(ins):
    if isinstance(v,tuple):
     d=sc+28+4*keys.index(v[2])-((sc+2*i+4)&~3)
     assert 0<=d<=1020 and d%4==0
     ins[i]=0x4800+(v[1]<<8)+d//4
   pe.write(sc,struct.pack('<14H6I',*ins,*vals.values()))
   pe.write(sc+56,struct.pack('<I',0xdecafbad));pe.write(syms['gMain']+4,struct.pack('<I',sc|1))
   for _ in range(20):
    pe.run(1);value=pe.u32(sc+56)
    if value!=0xdecafbad:return value
   raise AssertionError(('native metric call',name))
  repel=gamedata.const('VAR_REPEL_STEP_COUNT')
  invoke2('VarSet',repel,250);assert invoke2('VarGet',repel,0)==250
  weather=invoke2('GetCurrentWeather',0,0);assert weather==expected_weather,('native weather mismatch',label,weather,expected_weather)
  def rain_state():
   wp=pe.ptr('gWeatherPtr');count=pe.u8(wp+weather_offsets['rainSpriteCount']);assert count<=24
   ptrs=struct.unpack('<%dI'%count,pe.read(wp,count*4)) if count else ()
   pool=pe.read(syms['gSprites'],64*68);live=[]
   for ptr in ptrs:
    if not ptr:continue
    slot=(ptr-syms['gSprites'])//68
    assert 0<=slot<64 and syms['gSprites']+slot*68==ptr,('rain pointer',hex(ptr))
    if pool[slot*68+0x3e]&1:live.append(ptr)
   assert len(live)==len(set(live)),'aliased rain sprites'
   if expected_weather==gamedata.const('WEATHER_RAIN_THUNDERSTORM'):assert len(live)==count and count>0,('rain allocation',count,len(live))
   else:assert count==0,('calm rain allocation',count)
   return count,len(live),sum(bool(pool[i*68+0x3e]&1) for i in range(64))
  baseline=pe.save_state()
  for walking in (False,True):
   pe.load_state(baseline);pe.hold()
   counter=sc+64
   pe.write(counter,struct.pack('<10HI',0x1c01,0x0080,0x1840,0x00c0,0x4902,0x1840,0x8801,0x3101,0x8001,0x4770,syms['gTasks']+8))
   tid=invoke2('CreateTask',counter|1,255);assert tid<16
   ta=syms['gTasks']+40*tid;c=pe.u16(ta+8);v=pe.u32(syms['gMain']+36);f=pe.frame()
   path=set();visible=0;maxobjects=0;irregular=[];last=c;direction='RIGHT';rain=[];maxsprites=0
   for tick in range(360):
    loc=pe.location()
    assert loc[:2]==location[:2] and loc[3]==y and left<=loc[2]<=right,('corridor',loc)
    assert pe.u8(syms['gPlayerAvatar'])&mask and pe.field_idle()
    if walking:
     if loc[2]>=right:direction='LEFT'
     elif loc[2]<=left:direction='RIGHT'
     pe.hold(direction)
    else:pe.hold()
    pe.run(1);path.add(pe.location()[2:]);now=pe.u16(ta+8)
    if (now-last)&65535!=1:irregular.append(tick)
    last=now
    rc,ra,sprites=rain_state();rain.append((rc,ra));maxsprites=max(maxsprites,sprites)
    raw=pe.read(syms['gObjectEvents'],16*36);objects=[raw[i:i+36] for i in range(0,len(raw),36) if raw[i]&1]
    followers=[o for o in objects if o[8]==254]
    assert len(followers)==1
    visible+=not(int.from_bytes(followers[0][:4],'little')&0x2000);maxobjects=max(maxobjects,len(objects))
    tasks=pe.read(syms['gTasks'],16*40)
    assert sum(bool(tasks[i+4]) and (int.from_bytes(tasks[i:i+4],'little')&~1)==(syms['Task_FollowerPikachu']&~1) for i in range(0,640,40))==1
   dc=(pe.u16(ta+8)-c)&65535;dv=(pe.u32(syms['gMain']+36)-v)&0xffffffff;df=pe.frame()-f
   alive=pe.u8(ta+4) and (pe.u32(ta)&~1)==counter
   weather_end=invoke2('GetCurrentWeather',0,0);assert weather_end==expected_weather,('weather changed',label,weather_end,expected_weather)
   r=dict(map=name,label=label,weather=weather,weather_end=weather_end,rain_allocated_range=[min(z[1] for z in rain),max(z[1] for z in rain)],rain_count_range=[min(z[0] for z in rain),max(z[0] for z in rain)],max_active_sprites=maxsprites,walking=walking,repel=250,hardware=df,vblank=dv,callbacks=dc,missed=max(0,df-dc),irregular=irregular,positions=sorted(path),follower_objects=1,follower_tasks=1,max_objects=maxobjects,visible_frames=visible,counter_survived=bool(alive))
   r['pass_all']=bool(alive and df==dv==dc==360 and not irregular and visible and (not walking or len(path)>1))
   print(json.dumps({'storm_performance':r}),flush=True);results.append(r)
 assert e.frame()==original_frame and e.location()==location,'original core advanced'
 assert all(r['pass_all'] for r in results),'storm field budget/movement failure'
 _field_done.add((label,name))
