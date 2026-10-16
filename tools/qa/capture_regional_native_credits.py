#!/usr/bin/env python3
"""Capture each implemented native regional ending with its own audio.
Johto is intentionally unsupported until its separate profile is implemented.
Never reuse Kanto mixed audio as music-only audio for another region.
"""
import argparse,hashlib,json,os,re,shutil,struct,subprocess,sys,wave
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/qa'))
from emu import Emu
from gamedata import const,off
from savefile import SaveFile
import savedit

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def symbols(elf):
 exe=Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))/'bin/arm-none-eabi-objdump'
 lines=subprocess.check_output([str(exe),'-t',str(elf)],text=True).splitlines()
 return {p[-1]:int(p[0],16) for line in lines if len(p:=line.split())>=5 and re.fullmatch(r'[0-9a-fA-F]{8}',p[0])}
def snapshot():return {str(p.resolve()):sha(p) for p in (ROOT/'saves').rglob('*.sav')}
def exact_read(s,n):
 out=bytearray()
 while len(out)<n:
  q=s.read(n-len(out))
  if not q:break
  out.extend(q)
 return bytes(out)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--region',choices=['kanto','hoenn'],required=True);ap.add_argument('--rom',required=True);ap.add_argument('--elf',required=True);ap.add_argument('--base',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 before=snapshot();before[str(Path(a.base).resolve())]=sha(a.base);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);assert not (out/'validation.json').exists()
 ff=shutil.which('ffmpeg');assert ff
 sav=out/(a.region+'-clear-fixture.sav');assert not sav.exists()
 edits=['warp','IndigoPlateau_Exterior','11','6','var','VAR_MAP_SCENE_INDIGO_PLATEAU_EXTERIOR','1','noquestlog']
 if a.region=='kanto':
  assert savedit.run([a.base,'-o',str(sav)]+edits)==0
 else:
  assert 'DoHoennCredits' in symbols(a.elf),'candidate has no native Hoenn profile'
  s=SaveFile(str(Path(a.base).resolve()))
  for j in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+j*off('questlogscene')]=0
  for j in range(1,9):s.set_flag('FLAG_HOENN_BADGE%02d_GET'%j,True)
  for tr in ['SIDNEY','PHOEBE','GLACIA','DRAKE','WALLACE']:s.set_trainer_beaten('TRAINER_HOENN_'+tr,True)
  s.set_var('VAR_HOENN_LEAGUE_PROGRESS',6);s.set_flag('FLAG_HOENN_LEAGUE_CLEAR',False)
  s.warp('EverGrandeCity_HallOfFame',7,10);s.save(str(sav))
 sy=symbols(a.elf);credits,menu,song=[sy[n]&~1 for n in ['CB2_Credits','CB2_MainMenu','mus_credits']];bgm=sy['gMPlayInfo_BGM'];mgrsym=sy['sCreditsMgr']
 native=out/(a.region+'-native-silent.mp4');wavpath=out/(a.region+'-native-frlg.wav');final=out/(a.region+'-native-with-frlg.mp4')
 video=subprocess.Popen([ff,'-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','240x160','-r','262144/4389','-i','pipe:0','-an','-c:v','libx264rgb','-crf','0','-preset','veryfast',str(native)],stdin=subprocess.PIPE)
 hashes=[];events=[];distinct=set();t={};last=None;n=0;started=seen=waited=False;romsha=sha(a.rom);elfsha=sha(a.elf);fixture_sha=sha(sav)
 try:
  with wave.open(str(wavpath),'wb') as wav:
   wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(32768)
   with Emu(a.rom,str(sav),sym='') as e:
    e.syms=sy
    for f in range(6000):
     if e.callback2()&~1==menu:break
     e.hold('A') if f%30==0 else e.hold();e.run(1)
    else:raise AssertionError('main menu unreachable')
    e.hold();e.run(60)
    if a.region=='kanto':
     e.write(sy['gDisableMapMusicChangeOnMapLoad'],b'\x02');addr=sy['sSpecialFlags'];e.write(addr,bytes([e.u8(addr)|1]))
    e.audio_start(32768)
    script=sy['sCreditsScript'];waitidx=0
    while e.u8(script+waitidx*4)!=5:waitidx+=1
    for absolute in range(24000):
     e.hold('A') if not started and absolute%30==0 else e.hold()
     pcm=e.run_audio(1);header,status=struct.unpack('<II',e.read(bgm,8));playing=header==song and bool(status&0xffff)
     if playing and not started:started=True;t['song_start_emulator_frame']=e.frame()
     if not started:continue
     cb=e.callback2()&~1
     if cb==credits:
      seen=True;t.setdefault('credits_callback',n);mgr=e.u32(mgrsym);assert 0x02000000<=mgr<0x02040000;assert e.u8(mgr+16)==(2 if a.region=='hoenn' else 0),'wrong native regional ending';scene,idx=e.u8(mgr),e.u16(mgr+6)
      if idx==waitidx:t.setdefault('the_end',n)
      if idx==waitidx+1:waited=True;t.setdefault('the_end_wait',n)
      sb=e.u32(sy['gSaveBlock1Ptr']);event=(scene,idx,e.u8(sb+4),e.u8(sb+5),e.u8(mgr+9))
      if event!=last:events.append({'frame':n,'scene':scene,'script_index':idx,'map_group':event[2],'map_num':event[3],'map_or_mon_index':event[4]});last=event
     elif seen:
      assert waited,'credits exited before THE END';t['credits_exit']=n;break
     if not playing:t.setdefault('song_end',n)
     raw=e.screen();h=hashlib.sha256(raw).hexdigest();hashes.append(h);distinct.add(h);video.stdin.write(raw);wav.writeframesraw(pcm)
     if n in [0,1800,3600,7200,10800,14400,15207]:e.shot(str(out/('frame-%05d.png'%n)),scale=4)
     n+=1
     if n%1800==0:print(a.region.upper()+' captured',n,'native frames',flush=True)
    else:raise AssertionError('credits did not finish')
 finally:
  video.stdin.close();assert video.wait()==0
 assert started and seen and waited and n>=14970 and len(distinct)>100 and 'song_end' in t and t['song_end']<=n,t
 assert {p:sha(p) for p in before}==before and sha(a.rom)==romsha and sha(a.elf)==elfsha and sha(sav)==fixture_sha
 decoded=subprocess.Popen([ff,'-hide_banner','-loglevel','error','-i',str(native),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
 for i,h in enumerate(hashes):
  raw=exact_read(decoded.stdout,240*160*3);assert len(raw)==240*160*3 and hashlib.sha256(raw).hexdigest()==h,('decoded-frame-mismatch',i)
 assert not decoded.stdout.read(1) and decoded.wait()==0
 subprocess.check_call([ff,'-hide_banner','-loglevel','error','-n','-i',str(native),'-i',str(wavpath),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-af','apad','-t',str(n*4389/262144),'-movflags','+faststart',str(final)])
 report={'pass':True,'region':a.region,'rom_sha256':romsha,'elf_sha256':elfsha,'fixture_sav_sha256':fixture_sha,'scope':'native regional credits replay from a copied HOF/epilogue fixture; not proof of preceding victories or completion of requested bespoke story animation','temporary_fixture_forced_progress':a.region=='hoenn','new_music':False,'audio_region':a.region,'native_device_fps_measured':False,'frames':n,'seconds':n*4389/262144,'distinct_frames':len(distinct),'music':'native MUS_CREDITS','timing':t,'events':events,'all_original_saves_unchanged':True,'frame_hashes':hashes,'files':{p.name:sha(p) for p in [native,wavpath,final]}}
 (out/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['events','frame_hashes']},indent=2),flush=True)
if __name__=='__main__':main()
