#!/usr/bin/env python3
"""Read-only runtime visual QA; pre-boot HOF state is a temporary fixture."""
import argparse,hashlib,json,os,re,struct,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
R=Path.cwd(); sys.path.insert(0,str(R/'tools/qa'))
from emu import Emu
from gamedata import const,off,map_info
from savefile import SaveFile
p=argparse.ArgumentParser()
for n in ('rom','elf','sav','out'):p.add_argument('--'+n,required=True)
a=p.parse_args(); rom=Path(a.rom).resolve(); sav=Path(a.sav).resolve(); out=Path(a.out).resolve(); out.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
protected={q.resolve() for q in (R/'saves').rglob('*.sav')}|{sav}
before={str(q):sha(q.read_bytes()) for q in protected}
dka=Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))
symbols=subprocess.check_output([str(dka/'bin/arm-none-eabi-objdump'),'-t',a.elf],text=True)
S={}
for line in symbols.splitlines():
 q=line.split()
 if len(q)>=5 and re.fullmatch('[0-9a-fA-F]{8}',q[0]):S[q[-1]]=int(q[0],16)
romdata=rom.read_bytes()
def rb(addr,n):return romdata[addr-0x8000000:addr-0x8000000+n]
def ptr(addr):return struct.unpack('<I',rb(addr,4))[0]
def unlz(addr):
 raw=rb(addr,0x20000); assert raw[0]==16
 n=int.from_bytes(raw[1:4],'little'); pos=4; d=bytearray()
 while len(d)<n:
  f=raw[pos];pos+=1
  for bit in range(7,-1,-1):
   if len(d)>=n:break
   if f&(1<<bit):
    z=(raw[pos]<<8)|raw[pos+1];pos+=2;length=(z>>12)+3;dist=(z&4095)+1
    for _ in range(length):d.append(d[-dist])
   else:d.append(raw[pos]);pos+=1
 return bytes(d[:n])
maps=['SlateportCity','Route101','LittlerootTown_ProfessorBirchsLab','MauvilleCity','MtChimney','Route119_WeatherInstitute_2F','SeafloorCavern_Room9','SkyPillar_Top','SootopolisCity','EverGrandeCity','EverGrandeCity_ChampionsRoom','EverGrandeCity_HallOfFame','SlateportCity']
scene_ptrs={S['sHoennCreditsScene%d'%i]:i for i in range(13)}
species=['BLAZIKEN','SCEPTILE','SWAMPERT','RAYQUAZA']
lib=R/'tools/qa/libqa.so';assert lib.exists() and lib.stat().st_mtime >= (R/'tools/qa/libqa.c').stat().st_mtime
report={'pass':False,'rom_sha256':sha(romdata),'fixture':'HOF pre-boot fixture; not evidence of five victories','cameras':{},'pokemon':{},'manual_visual_review_required':True}
images={}; ages=[0]*13; firsts={}; pending={}
def save_img(raw,name):
 im=Image.frombytes('RGB',(240,160),raw); im.save(out/(name+'.png')); images[name]=im
def check_mon(e,i):
 w=e.read(S['gWindows'],12)
 assert tuple(w[:6])==(0,11,6,8,8,10),('unexpected mon window',list(w))
 base=struct.unpack_from('<H',w,6)[0]; data=e.read(struct.unpack_from('<I',w,8)[0],2048)
 sp=const('SPECIES_'+species[i]); expected=unlz(ptr(S['gMonFrontPicTable']+sp*8))[:2048]
 assert data==expected,('window gfx differs from native species',species[i])
 reg=e.u16(0x4000008); charbase=((reg>>2)&3)*0x4000; mapbase=((reg>>8)&31)*0x800
 assert e.read(0x6000000+charbase+base*32,2048)==expected,'primary mon gfx not uploaded'
 for y in range(8):
  row=struct.unpack('<8H',e.read(0x6000000+mapbase+((y+6)*32+11)*2,16))
  assert row==tuple(0xa000|base+y*8+x for x in range(8)),('mon tilemap missing',i,y,row)
 pal=unlz(ptr(S['gMonPaletteTable']+sp*8))[:32]
 assert e.read(0x5000000+10*32,32)==pal,'native normal palette missing'
 cols=struct.unpack('<16H',pal); pix=e.screen(); visible=matched=0
 for y in range(64):
  for x in range(64):
   v=expected[((y//8)*8+x//8)*32+(y%8)*4+(x%8)//2]; c=(v>>(4*(x&1)))&15
   if not c:continue
   visible+=1; rgb=[((cols[c]>>s)&31)*255//31 for s in (0,5,10)]
   got=pix[((y+48)*240+x+88)*3:((y+48)*240+x+88)*3+3]
   if max(abs(got[k]-rgb[k]) for k in range(3))<=8:matched+=1
 assert visible>100 and matched/visible>.995,('native mon not visible on screen',i,matched,visible)
 save_img(pix,'mon-%d-%s'%(i,species[i]))
 report['pokemon'][str(i)]={'species':species[i],'vram_sha256':sha(expected),'palette_sha256':sha(pal),'visible_pixels':visible,'screen_matching_pixels':matched,'frame':e.frame()}
e=None
try:
 with tempfile.TemporaryDirectory(prefix='hoenn-credit-visual-') as td:
  fixture=Path(td)/'fixture.sav'; s=SaveFile(str(sav))
  for j in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+j*off('questlogscene')]=0
  for j in range(1,9):s.set_flag('FLAG_HOENN_BADGE%02d_GET'%j,True)
  for tr in ['SIDNEY','PHOEBE','GLACIA','DRAKE','WALLACE']:s.set_trainer_beaten('TRAINER_HOENN_'+tr,True)
  s.set_var('VAR_HOENN_LEAGUE_PROGRESS',6);s.set_flag('FLAG_HOENN_LEAGUE_CLEAR',False)
  s.warp('EverGrandeCity_HallOfFame',7,10);s.save(str(fixture))
  e=Emu(str(rom),str(fixture),sym='');e.syms=S;e.boot_continue(leave_menu_only=True)
  for _ in range(1200):
   if (e.callback2()&~1)==S['CB2_Credits']:break
   assert not e.reset_seen(),'reset before credits'
   e.press('A',hold=2,after=14)
  else:raise AssertionError('native HOF did not reach credits')
  e.hold(); begin=e.frame(); song_start=None; end_frame=None; wait_end=None
  while e.frame()-begin<19000:
   if (e.callback2()&~1)!=S['CB2_Credits']:end_frame=e.frame();break
   m=e.ptr('sCreditsMgr');assert e.u8(m+16)==2
   main=e.u8(m);sub=e.u8(m+1);which=e.u8(m+9);timer=e.u16(m+12)
   if e.ptr('gMPlayInfo_BGM')==S['mus_credits'] and e.u32(S['gMPlayInfo_BGM']+4)&0xffff:
    if song_start is None:song_start=e.frame()
   active=e.ptr('sCreditsOverworld_Script')
   if active in scene_ptrs and main in (6,7,8,9,20):
    i=scene_ptrs[active];mi=map_info(maps[i])
    assert e.location()[:2]==(mi['group'],mi['num']),(i,e.location(),maps[i])
    ages[i]+=1
    if ages[i] in (80,480):
     tag='start' if ages[i]==80 else 'late'; name='map-%02d-%s'%(i,tag)
     raw=e.screen();save_img(raw,name)
     report['cameras'].setdefault(str(i),{'map':maps[i],'shots':{}})['shots'][tag]={'file':name+'.png','frame':e.frame(),'location':e.location(),'sha256':sha(raw)}
    if ages[i]>=80:pending[i]=(e.frame(),e.screen()) if ages[i]%120==0 else pending.get(i)
   if main==14 and sub==8 and timer<=110 and str(which) not in report['pokemon']:check_mon(e,which)
   if main==17 and wait_end is None:
    wait_end=e.frame();save_img(e.screen(),'the-end')
   e.run(1)
  assert end_frame is not None,'credits did not terminate naturally'
  assert song_start is not None and wait_end is not None
  for i in range(13):
   assert str(i) in report['cameras'],('camera never visible',i,maps[i],ages[i])
   if 'late' not in report['cameras'][str(i)]['shots']:
    assert pending.get(i),('camera too brief for late shot',i,ages[i])
    fr,raw=pending[i];name='map-%02d-late'%i;save_img(raw,name)
    report['cameras'][str(i)]['shots']['late']={'file':name+'.png','frame':fr,'sha256':sha(raw)}
  assert len(report['pokemon'])==4
  report.update(pass_=True,song_start_frame=song_start,the_end_frame=wait_end,end_frame=end_frame,native_frames_from_music=end_frame-song_start)
  report['pass']=True;del report['pass_']
except Exception as ex:
 report['error']=repr(ex)
 if e and e.h:save_img(e.screen(),'failure')
finally:
 if e:e.close()
 report['original_saves_unchanged']=before=={p:sha(Path(p).read_bytes()) for p in before}
 if not report['original_saves_unchanged']:report['pass']=False
 for page in range(3):
  sheet=Image.new('RGB',(480,176*min(5,13-page*5)),(24,24,24));d=ImageDraw.Draw(sheet)
  for row,i in enumerate(range(page*5,min(page*5+5,13))):
   for col,tag in enumerate(('start','late')):
    name='map-%02d-%s'%(i,tag)
    if name in images:sheet.paste(images[name],(col*240,row*176+16))
    d.text((col*240+2,row*176+2),('%02d %s %s'%(i,tag,maps[i]))[:38],fill='white')
  sheet.resize((sheet.width*2,sheet.height*2),Image.Resampling.NEAREST).save(out/('camera-sheet-%d.png'%page))
 sheet=Image.new('RGB',(480,352),(24,24,24));d=ImageDraw.Draw(sheet)
 for i,name in enumerate(species):
  key='mon-%d-%s'%(i,name);x=(i%2)*240;y=(i//2)*176
  if key in images:sheet.paste(images[key],(x,y+16))
  d.text((x+2,y+2),name,fill='white')
 sheet.resize((960,704),Image.Resampling.NEAREST).save(out/'pokemon-sheet.png')
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'pass':report['pass'],'cameras':len(report['cameras']),'pokemon':len(report['pokemon']),'error':report.get('error'),'native_frames_from_music':report.get('native_frames_from_music'),'original_saves_unchanged':report['original_saves_unchanged']}))
sys.exit(0 if report['pass'] else 1)
