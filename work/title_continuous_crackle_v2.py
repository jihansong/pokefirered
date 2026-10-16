#!/usr/bin/env python3
from pathlib import Path
import argparse,array,hashlib,json,math,shutil,subprocess,sys,wave
URL='https://opengameart.org/sites/default/files/crackleelectricityloop.wav'
PAGE='https://opengameart.org/content/electricity-game-sound-pack'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pcm(data,kind):
 a=array.array(kind);a.frombytes(data)
 if sys.byteorder!='little':a.byteswap()
 return a
def audit(a):
 assert len(a)==176400,('Expected four seconds',len(a))
 rms=[math.sqrt(sum(v*v for v in a[i:i+882])/882) for i in range(0,len(a),882)]
 quiet=sum(v<32.767 for v in rms)
 assert quiet==0,('Near-silent 20ms windows',quiet)
 assert max(abs(v) for v in a)<32767,'Clipping'
 return {'silent_20ms_windows_below_minus60dB':quiet,'peak_dBFS':20*math.log10(max(abs(v) for v in a)/32767),'samples':len(a)}
def main():
 ap=argparse.ArgumentParser()
 for key in ('wav','video','png','gif_dir','out'):ap.add_argument('--'+key,type=Path,required=True)
 a=ap.parse_args();assert not a.out.exists(),'Use fresh output'
 assert sha(a.png)=='7e370cc2d5b4cd71a1ae68b1da6934b62a049fc9e83efb2fc51619231cc122c5'
 assert a.wav.name=='crackleelectricityloop.wav'
 assert sha(a.wav)=='c872ff9719f9bdf503e5d87fe9b1b128255fe2f9506e3a380ff022b83e0b7be8'
 gifs=sorted(a.gif_dir.glob('*.gif'));assert len(gifs)>=2
 assert all('title-animation-tech' not in str(p) for p in gifs)
 inputs=[a.wav,a.video,a.png]+gifs;before={str(p):sha(p) for p in inputs}
 ff=shutil.which('ffmpeg');assert ff
 def run(args):return subprocess.run([ff,'-v','error','-nostdin']+list(map(str,args)),check=True,stdout=subprocess.PIPE).stdout
 raw=pcm(run(['-i',a.wav,'-vn','-ac','1','-ar','44100','-f','f32le','pipe:1']),'f')
 length=len(raw)/44100;peak=max(abs(v) for v in raw)
 assert .15<length<60 and peak>0
 fade=min(.04,length/4);copies=max(2,math.ceil((4-length)/(length-fade))+2)
 graph=f'[0:a]aresample=44100,aformat=channel_layouts=mono,asplit={copies}'+''.join(f'[a{i}]' for i in range(copies))+';'
 prev='a0'
 for i in range(1,copies):graph+=f'[{prev}][a{i}]acrossfade=d={fade}:c1=tri:c2=tri[b{i}];';prev=f'b{i}'
 graph+=f'[{prev}]atrim=end_sample=176400,asetpts=N/SR/TB,volume={.35/peak}[out]'
 a.out.mkdir(parents=True);wav=a.out/'continuous-electricity.wav';mp4=a.out/'title-current-continuous-electricity.mp4'
 run(['-n','-i',a.wav,'-filter_complex',graph,'-map','[out]','-ac','1','-ar','44100','-c:a','pcm_s16le',wav])
 with wave.open(str(wav),'rb') as w:assert w.getnframes()==176400;wav_qa=audit(pcm(w.readframes(w.getnframes()),'h'))
 run(['-n','-i',a.video,'-i',wav,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-t','4','-movflags','+faststart',mp4])
 aac_qa=audit(pcm(run(['-i',mp4,'-vn','-t','4','-ac','1','-ar','44100','-f','s16le','pipe:1']),'h'))
 def video_hash(p):return run(['-i',p,'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','pipe:1']).decode().strip()
 assert video_hash(a.video)==video_hash(mp4)
 assert before=={str(p):sha(p) for p in inputs}
 report={'status':'CONTINUOUS_CC0_CRACKLE','source_url':URL,'source_page':PAGE,'author':'faxcorp','license':'CC0-1.0','license_url':'https://creativecommons.org/publicdomain/zero/1.0/','source_sha256':before[str(a.wav)],'crossfade_seconds':fade,'source_copies':copies,'wav':wav_qa,'aac':aac_qa,'video_packets_unchanged':True,'gif_png_unchanged':True,'new_music_created':False,'auditioned':False,'files':{p.name:sha(p) for p in (wav,mp4)}}
 (a.out/'validation.json').write_text(json.dumps(report,indent=2)+chr(10),encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
