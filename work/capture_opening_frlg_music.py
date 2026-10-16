#!/usr/bin/env python3
"""Capture the existing FR/LG intro cue through the ROM mixer; attach it to v5."""
from pathlib import Path
import argparse,array,hashlib,json,math,re,shutil,struct,subprocess,sys,tempfile,wave
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,default=Path.cwd())
    for k in ("rom","video","out"):ap.add_argument("--"+k,type=Path,required=True)
    ap.add_argument("--ffmpeg");a=ap.parse_args();repo=a.repo.resolve()
    assert not a.out.exists(),"Choose a fresh output directory"
    video=a.video.read_bytes();original=a.rom.read_bytes()
    assert sha(video)=="6336f4a074fec054634271992c505c052c04d2ddb4a10d33417f0ef2cf7f38f1","Not reviewed v5 preview"
    sys.path.insert(0,str(repo/"tools/qa"))
    from emu import Emu,fresh_syms,load_syms
    sympath=fresh_syms(str(a.rom));syms=load_syms(sympath)
    required=["gSongTable","mus_intro_fight","gMPlayInfo_BGM","CB2_TitleScreenRun"]
    assert all(k in syms for k in required),("Missing symbols",required)
    constants=(repo/"include/constants/songs.h").read_text()
    def number(name):return int(re.search(r"^#define\s+"+name+r"\s+(\d+)\b",constants,re.M).group(1))
    intro,title=number("MUS_INTRO_FIGHT"),number("MUS_TITLE")
    table=syms["gSongTable"]-0x08000000;src=table+intro*8;dst=table+title*8
    assert 0<=src<len(original)-8 and 0<=dst<len(original)-8 and src!=dst
    entry=original[src:src+8];header,ms,me=struct.unpack("<IHH",entry)
    assert header==syms["mus_intro_fight"] and (ms,me)==(0,0),"Unexpected intro song entry"
    assert struct.unpack("<HH",original[dst+4:dst+8])==(0,0),"Title must use the BGM player"
    preview=bytearray(original);preview[dst:dst+8]=entry
    assert preview[:dst]==original[:dst] and preview[dst+8:]==original[dst+8:]
    rate=32768;se_frames=0;chunks=[];start_frame=None
    with tempfile.TemporaryDirectory(prefix="frlg-intro-audio-") as folder:
        copy=Path(folder)/"audio-preview.gba";copy.write_bytes(preview)
        with Emu(str(copy),sym=str(sympath)) as e:
            e.hold();e.audio_start(rate)
            for frame in range(5000):
                chunk=e.run_audio(1)
                if (e.callback2()&~1)==(syms["CB2_TitleScreenRun"]&~1) and e.ptr("gMPlayInfo_BGM")==header:
                    chunks.append(chunk);start_frame=frame+1;break
            assert start_frame is not None,"Patched title did not start the existing intro cue"
            for _ in range(math.ceil(12.5*59.7275)):
                chunks.append(e.run_audio(1))
                assert e.ptr("gMPlayInfo_BGM")==header,"BGM changed during capture"
                se_frames+=int(any(e.u32(syms[k]+4)&0xffff for k in ("gMPlayInfo_SE1","gMPlayInfo_SE2","gMPlayInfo_SE3") if k in syms))
    pcm=b"".join(chunks);samples=array.array("h");samples.frombytes(pcm)
    if sys.byteorder!="little":samples.byteswap()
    assert len(pcm)>=rate*10*4 and max(abs(v) for v in samples)>100,"Missing/short music"
    assert se_frames==0,"Another sound-effect player was active; inspect capture"
    a.out.mkdir(parents=True);wav=a.out/"frlg-mus-intro-fight.wav";mp4=a.out/"opening-hooh-v5-frlg-music.mp4"
    with wave.open(str(wav),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm)
    ff=a.ffmpeg or shutil.which("ffmpeg")
    if not ff:
        import imageio_ffmpeg
        ff=imageio_ffmpeg.get_ffmpeg_exe()
    def run(args):return subprocess.run([ff,"-v","error","-nostdin"]+list(map(str,args)),check=True,stdout=subprocess.PIPE).stdout
    run(["-n","-i",a.video,"-i",wav,"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-ar","44100","-af","aresample=44100,atrim=end_sample=441000,asetpts=N/SR/TB,afade=t=out:st=9.8:d=0.2","-t","10","-movflags","+faststart",mp4])
    def vhash(p):return run(["-i",p,"-map","0:v:0","-c","copy","-f","hash","-hash","sha256","pipe:1"]).decode().strip()
    assert vhash(a.video)==vhash(mp4),"Video packets changed"
    decoded=run(["-i",mp4,"-vn","-t","10","-ac","2","-ar","44100","-f","s16le","pipe:1"])
    assert len(decoded)==441000*4,("AAC duration mismatch",len(decoded))
    assert sha(a.rom.read_bytes())==sha(original) and a.video.read_bytes()==video,"Original inputs changed"
    report={"status":"EXISTING_FRLG_INTRO_MUSIC_ATTACHED","song":"MUS_INTRO_FIGHT","song_id":intro,"song_header":header,"source_rom_sha256":sha(original),"source_midi_sha256":sha((repo/"sound/songs/midi/mus_intro_fight.mid").read_bytes()),"temporary_title_entry_only":True,"real_game_rom_modified":False,"user_save_used":False,"capture_start_frame":start_frame,"capture_seconds":len(pcm)/rate/4,"se_active_frames":se_frames,"video_packets_unchanged":True,"audio_seconds":10,"excerpt":"First 10 seconds; final 0.2 seconds fade out; original tempo","new_music_created":False,"auditioned":False,"files":{p.name:{"bytes":p.stat().st_size,"sha256":sha(p.read_bytes())} for p in (wav,mp4)}}
    (a.out/"validation.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
