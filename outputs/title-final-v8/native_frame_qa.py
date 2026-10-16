import sys,json,struct,hashlib,time
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'tools/qa');from emu import Emu
out=Path('outputs/title-final-v8/native-frame-qa');out.mkdir(exist_ok=False)
p=Path('graphics/title_screen/thunder_yellow');bank=(p/'approved-title-v8-start-roi.8bpp').read_bytes();pal=np.frombuffer((p/'approved-title-v8.gbapal').read_bytes(),dtype='<u2')&0x7fff
roi=pal[np.frombuffer(bank,dtype=np.uint8).reshape(40,14,18,8,8).transpose(0,1,3,2,4).reshape(40,112,144)]
idlet=np.frombuffer((p/'approved-title-v8.8bpp').read_bytes(),dtype=np.uint8).reshape(20,30,8,8).transpose(0,2,1,3).reshape(160,240);idle=pal[idlet]
saves=lambda:{str(q):hashlib.sha256(q.read_bytes()).hexdigest() for q in Path('saves').rglob('*.sav')};before=saves();result=[]
for key in ['START','A']:
 with Emu('poketitlev8qa.gba') as e:
  def task():
   b=e.read(e.sym('gTasks'),640)
   for i in range(16):
    if b[i*40+4] and (struct.unpack_from('<I',b,i*40)[0]&~1)==(e.sym('Task_TitleScreenMain')&~1):return struct.unpack_from('<16h',b,i*40+8)
  def vb():return e.u32(e.sym('gMain')+36)
  def screenval():
   a=np.frombuffer(e.screen(),dtype=np.uint8).reshape(160,240,3).astype(np.uint16);return (a[:,:,0]>>3)|((a[:,:,1]>>3)<<5)|((a[:,:,2]>>3)<<10)
  for k in range(3600):
   e.run();d=task()
   if d and d[0:2]==(3,1) and (e.callback2()&~1)==(e.sym('CB2_TitleScreenRun')&~1):break
  else:raise RuntimeError('title timeout')
  e.run(2);idlebad=int((screenval()!=idle).sum());e.shot(str(out/(key+'-idle.png')));e.hold(key);events=[];checks={};first=done=menu=None;last=0;lag=[];previous=None
  for t in range(700):
   e.run()
   if t==0:e.hold()
   f=vb();d=task()
   if d and d[0]==5:
    if d[8]!=last:
     assert d[8]==last+1;events.append((f,d[8]));first=f if first is None else first;last=d[8]
    if d[7]==1 and d[9]==3 and 1<=d[8]<=40 and d[8]-1 not in checks:
     i=d[8]-1;raw=b''.join(e.read(0x6000000+(6*30+12)*64+y*1920,1152) for y in range(14));bad=int((screenval()[48:160,96:240]!=roi[i]).sum());checks[i]={'screen_bad':bad,'vram_equal':raw==bank[i*16128:(i+1)*16128]}
     if i in [0,39] or bad:e.shot(str(out/(key+'-frame-'+str(i).zfill(2)+'.png')))
    if d[7]==2 and done is None:done=f
    if previous and previous[1][0:2]==(5,1) and d[0:2]==(5,1):
     pf,pd=previous
     if 1<=pd[2]<89 and f-pf==1 and d[2]-pd[2]!=1:lag.append((f,pd[2],d[2]))
    previous=(f,d)
   else:previous=None
   if (e.callback2()&~1)==(e.sym('CB2_MainMenu')&~1):menu=f;e.shot(str(out/(key+'-menu.png')));break
  intervals=[b[0]-a[0] for a,b in zip(events,events[1:])]
  r={'button':key,'idle_bad':idlebad,'copied':len(events),'compared':len(checks),'copy_intervals':sorted(set(intervals)),'first_copy':first,'done':done,'movie_ticks':None if done is None else done-first,'menu':menu,'frame_checks':checks,'callback_lag':lag};r['pass']=idlebad==0 and len(events)==40 and len(checks)==40 and all(c['screen_bad']==0 and c['vram_equal'] for c in checks.values()) and set(intervals)=={6} and done-first==240 and menu>=done and not lag;result.append(r);print(json.dumps(r),flush=True)
report={'pass':all(r['pass'] for r in result) and before==saves(),'cases':result,'original_saves_preserved':before==saves(),'rom_sha256':hashlib.sha256(Path('poketitlev8qa.gba').read_bytes()).hexdigest()};(out/'validation.json').write_text(json.dumps(report,indent=2));print('NATIVE_OVERALL',report['pass'])
