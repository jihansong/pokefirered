from pathlib import Path
import argparse,hashlib,json,os,re,struct,subprocess,sys
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--rom',required=True);ap.add_argument('--elf');ap.add_argument('--sav',required=True);ap.add_argument('--root',default='/workspaces/pokefirered');ap.add_argument('--out',required=True)
a=ap.parse_args();R=Path(a.root);rom=Path(a.rom);elf=Path(a.elf or rom.with_suffix('.elf'));sav=Path(a.sav);O=Path(a.out)
sha=lambda b:hashlib.sha256(b).hexdigest()
def sav_hashes():
 ps=set((R/'saves').rglob('*.sav'));ps.add(sav);return {str(p):sha(p.read_bytes()) for p in sorted(ps) if p.is_file()}
before=sav_hashes();rom_before=sha(rom.read_bytes());qadir=R/'tools/qa';lib=qadir/'libqa.so';c=qadir/'libqa.c';assert lib.exists() and lib.stat().st_mtime>=c.stat().st_mtime
sys.path.insert(0,str(qadir));from emu import Emu
objdump=Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))/'bin/arm-none-eabi-objdump';dump=subprocess.check_output([str(objdump),'-t',str(elf)],text=True);syms={}
for line in dump.splitlines():
 p=line.split()
 if len(p)>=5 and re.fullmatch('[0-9a-fA-F]{8}',p[0]):syms[p[-1]]=int(p[0],16)
for n in ['sOpening','gOpeningDroppedFrames','gMain','gMPlayInfo_BGM','mus_intro_fight','CB2_InitTitleScreen','OpeningMovie_VBlank']:assert n in syms,n
P=R/'graphics/intro/opening_movie_v7';px=(P/'pixels.8bpp').read_bytes();pal=(P/'palettes.gbapal').read_bytes();desc=(P/'frames.bin').read_bytes();assert len(desc)==752*8;rb=rom.read_bytes();assert len(rb)<=0x2000000
for name,data in [('sOpeningMoviePixels',px),('sOpeningMoviePalettes',pal),('sOpeningMovieFrames',desc)]:
 off=syms[name]-0x08000000;assert 0<=off<=len(rb)-len(data) and rb[off:off+len(data)]==data,('ROM asset mismatch',name)
expected=[];frame_data=[]
for n in range(752):
 off,pi,reserved=struct.unpack_from('<IHH',desc,n*8);assert reserved==0;pixels=px[off:off+23040];palette=pal[pi*512:(pi+1)*512];assert len(pixels)==23040 and len(palette)==512
 cols=np.frombuffer(palette,dtype='<u2');idx=np.frombuffer(pixels,dtype=np.uint8).reshape(96,240);full=np.zeros((160,240),dtype=np.uint16);full[32:128]=cols[idx];expected.append(full.tobytes());frame_data.append((pixels,palette))
def screen555(e):
 c=np.frombuffer(e.screen(),dtype=np.uint8).reshape(160,240,3).astype(np.uint16);return ((c[:,:,0]>>3)|((c[:,:,1]>>3)<<5)|((c[:,:,2]>>3)<<10)).tobytes()
def state(e):
 p=e.u32(syms['sOpening'])
 if not p:return None
 assert 0x02000000<=p<0x02040000,('bad sOpening',hex(p));return struct.unpack('<HHBBBB',e.read(p,8))
def newemu():
 e=Emu(str(rom),str(sav),sym='');e.syms=syms;return e
report={'rom_sha256':rom_before,'elf_sha256':sha(elf.read_bytes()),'rom_assets_exact':True}
try:
 with newemu() as e:
  uploads={};screens={};last_next=0;max_v=0;title_at=None;started=False;music_first=None;music_end=None;had_music=False;last_active=None
  for _ in range(4000):
   e.run(1);tick=e.frame();st=state(e)
   if st is not None:
    nxt,vmax,page,ready,music,reserved=st
    if ready:
     started=True;max_v=max(max_v,vmax)
     if nxt!=last_next:
      assert nxt==last_next+1,('nonsequential frame',tick,last_next,nxt);f=nxt-1;assert 0<=f<752
      assert e.read(0x06000000+page*0xA000+7680,23040)==frame_data[f][0],('VRAM',f);assert e.read(0x05000000,512)==frame_data[f][1],('palette',f)
      dc=e.u16(0x04000000);assert (dc&7)==4 and (dc&0xF00)==0x400 and not(dc&0xF080) and bool(dc&16)==bool(page),('display mode',f,hex(dc));uploads[f]=tick;last_next=nxt
   if started:screens[tick]=screen555(e)
   hdr,status=struct.unpack('<II',e.read(syms['gMPlayInfo_BGM'],8));playing=bool((status&0xFFFF) and not(status&0x80000000));intro=playing and hdr==syms['mus_intro_fight']
   if intro:
    had_music=True;last_active=tick
    if music_first is None:music_first={'tick':tick,'next_frame':st[0] if st else None}
   elif had_music and music_end is None:music_end={'tick':tick,'next_frame':st[0] if st else None}
   if title_at is None and (e.callback2()&~1)==(syms['CB2_InitTitleScreen']&~1):title_at=tick
   if title_at is not None and tick>=title_at+240:baseline=screen555(e);break
  else:raise AssertionError('natural playback did not reach stable title')
  assert len(uploads)==752 and sorted(uploads)==list(range(752)),('missing frames',len(uploads));assert all(uploads[i+1]-uploads[i]==1 for i in range(751)),'held/dropped frame'
  lag_results={lag:sum(screens.get(uploads[i]+lag)!=expected[i] for i in range(752)) for lag in (0,1,2)};lags=[lag for lag,n in lag_results.items() if n==0];assert lags,('display RGB555 differs',lag_results)
  dropped=e.u16(syms['gOpeningDroppedFrames']);assert dropped==0,('dropped',dropped);assert 160<=max_v<220,('VBlank end',max_v)
  assert music_first and music_first['next_frame'] in (20,21),('music cue20',music_first);assert music_end is not None,('intro BGM never ended',last_active)
  end_relative=music_end['tick']-uploads[0];assert 749<=end_relative<=755,('intro BGM end differs from cue751',end_relative,music_end)
  report['natural']={'frames_exact':752,'sequential':True,'first_upload_tick':uploads[0],'last_upload_tick':uploads[751],'display_lag_frames':lags,'dropped':dropped,'max_vcount_end':max_v,'music_start':music_first,'music_end':music_end,'music_end_relative':end_relative,'title_tick':title_at}
 skips=[]
 for key,at in [('A',0),('START',340),('SELECT',737)]:
  with newemu() as e:
   pressed=None;title_at=None
   for _ in range(4000):
    st=state(e)
    if pressed is None and st and st[3] and st[0]>=at+1:e.hold(key);pressed=e.frame()
    if pressed is not None and e.frame()==pressed+3:e.hold()
    e.run(1);tick=e.frame()
    if title_at is None and (e.callback2()&~1)==(syms['CB2_InitTitleScreen']&~1):title_at=tick
    if title_at is not None and tick>=title_at+240:
     assert pressed is not None and title_at-pressed<=12,('skip timeout',key,pressed,title_at);assert screen555(e)==baseline,('title differs after skip',key);assert e.u32(syms['sOpening'])==0,('opening heap not freed',key)
     skips.append({'key':key,'after_source_frame':at,'pressed_tick':pressed,'title_tick':title_at,'title_equals_natural':True});break
   else:raise AssertionError(('skip did not reach stable title',key))
 report['skips']=skips;report['pass']=True
except Exception as ex:report['pass']=False;report['error']=repr(ex)
finally:
 after=sav_hashes();report['original_saves_unchanged']=before==after;report['original_sav_sha256']=before.get(str(sav));report['rom_unchanged']=rom_before==sha(rom.read_bytes());report['pass']=report.get('pass',False) and report['original_saves_unchanged'] and report['rom_unchanged'];O.mkdir(parents=True,exist_ok=True);(O/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
sys.exit(0 if report['pass'] else 1)
