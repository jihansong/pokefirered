#!/usr/bin/env python3
"""Capture the ROM's existing MUS_TITLE and mix it with approved crackle."""
from pathlib import Path
import argparse,array,hashlib,json,math,re,shutil,subprocess,sys,wave
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument("--repo",type=Path,default=Path.cwd())
    for n in ("rom","video","crackle","out"):p.add_argument("--"+n,type=Path,required=True)
    p.add_argument("--protect",type=Path,action="append",default=[]);p.add_argument("--ffmpeg");a=p.parse_args();repo=a.repo.resolve()
    assert not a.out.exists(),"Use a fresh output directory"
    inputs={str(f):sha(f.read_bytes()) for f in [a.rom,a.video,a.crackle]+a.protect}
    assert inputs[str(a.video)]=="60ad8bbefc0d4fc2322d58e764977d5dc401c516d84551ce822f0218bd2409f9","Not approved continuous-crackle video"
    assert inputs[str(a.crackle)]=="05fc393c54d7a7030be0bc86506ea7d0ef455e4b26ace4a6e3e3fadd6bcc2189","Wrong crackle WAV"
    sys.path.insert(0,str(repo/"tools/qa"))
    from emu import Emu,fresh_syms,load_syms
    syms=load_syms(fresh_syms(str(a.rom)))
    for name in ("mus_title","gMPlayInfo_BGM","CB2_TitleScreenRun","gMPlayInfo_SE1","gMPlayInfo_SE2","gMPlayInfo_SE3"):assert name in syms,name
    rate=32768;chunks=[];se_frames=0;start=None
    with Emu(str(a.rom)) as e:
        e.hold();e.audio_start(rate)
        for frame in range(5000):
            chunk=e.run_audio(1)
            if (e.callback2()&~1)==(syms["CB2_TitleScreenRun"]&~1) and e.ptr("gMPlayInfo_BGM")==syms["mus_title"]:
                chunks.append(chunk);start=frame+1;break
        assert start is not None,"MUS_TITLE did not start at the title screen"
        for _ in range(math.ceil(4.2*59.7275)):
            chunks.append(e.run_audio(1))
            assert e.ptr("gMPlayInfo_BGM")==syms["mus_title"],"Title music changed"
            se_frames+=int(any(e.u32(syms[k]+4)&0xffff for k in ("gMPlayInfo_SE1","gMPlayInfo_SE2","gMPlayInfo_SE3")))
    pcm=b"".join(chunks);samples=array.array("h");samples.frombytes(pcm)
    if sys.byteorder!="little":samples.byteswap()
    assert len(pcm)>=4*rate*4 and max(abs(v) for v in samples)>100,"Missing title music"
    assert se_frames==0,"Unexpected sound effects in title capture"
    a.out.mkdir(parents=True);music=a.out/"frlg-mus-title.wav";mixed=a.out/"title-music-and-crackle.wav";mp4=a.out/"title-frlg-music-crackle.mp4"
    with wave.open(str(music),"wb") as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm)
    ff=a.ffmpeg or shutil.which("ffmpeg")
    if not ff:
        import imageio_ffmpeg
        ff=imageio_ffmpeg.get_ffmpeg_exe()
    def run(args):return subprocess.run([ff,"-v","error","-nostdin"]+list(map(str,args)),check=True,stdout=subprocess.PIPE).stdout
    graph="[0:a]aresample=44100,atrim=end_sample=176400,asetpts=N/SR/TB,volume=0.70[m];[1:a]aresample=44100,atrim=end_sample=176400,asetpts=N/SR/TB,volume=0.30[e];[m][e]amix=inputs=2:duration=shortest:normalize=0,atrim=end_sample=176400[a]"
    run(["-n","-i",music,"-i",a.crackle,"-filter_complex",graph,"-map","[a]","-ac","2","-ar","44100","-c:a","pcm_s16le",mixed])
    with wave.open(str(mixed),"rb") as w:
        assert (w.getnchannels(),w.getframerate(),w.getnframes())==(2,44100,176400),"Mix length mismatch"
        raw=w.readframes(w.getnframes())
    def peak(buf):
        v=array.array("h");v.frombytes(buf)
        if sys.byteorder!="little":v.byteswap()
        return max(abs(x) for x in v)/32768
    assert peak(raw)<0.99,"Mixed WAV clips"
    run(["-n","-i",a.video,"-i",mixed,"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-ar","44100","-t","4","-movflags","+faststart",mp4])
    def vh(f):return run(["-i",f,"-map","0:v:0","-c","copy","-f","hash","-hash","sha256","pipe:1"]).decode().strip()
    assert vh(a.video)==vh(mp4),"Video packets changed"
    decoded=run(["-i",mp4,"-vn","-t","4","-ac","2","-ar","44100","-f","s16le","pipe:1"])
    assert len(decoded)==176400*4 and peak(decoded)<0.99,"AAC length/clipping failure"
    assert all(sha(Path(f).read_bytes())==h for f,h in inputs.items()),"Protected input changed"
    report={"status":"TITLE_EXISTING_FRLG_MUSIC_AND_CRACKLE_PREVIEW","song":"MUS_TITLE","music_gain":0.70,"electricity_gain":0.30,"seconds":4,"capture_start_frame":start,"se_active_frames":se_frames,"audio_peak":peak(raw),"aac_peak":peak(decoded),"video_packets_unchanged":True,"protected_inputs_unchanged":True,"new_music_created":False,"pika_voice_added":False,"auditioned":False,"scope":"4-second preview excerpt; native game already selects MUS_TITLE","input_sha256":inputs,"files":{f.name:{"bytes":f.stat().st_size,"sha256":sha(f.read_bytes())} for f in (music,mixed,mp4)}}
    (a.out/"validation.json").write_text(json.dumps(report,indent=2),encoding="utf-8");print(json.dumps(report,indent=2))
if __name__=="__main__":main()
