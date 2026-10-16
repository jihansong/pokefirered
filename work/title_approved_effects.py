#!/usr/bin/env python3
"""Approved title PNG -> small background effects GIF + MP4. No character redraw."""
from pathlib import Path
import argparse,hashlib,io,json,math,os,random,shutil,struct,subprocess,wave
from PIL import Image,ImageDraw
PIXEL_SHA="4bfde12265e9d35c72f6e9ea4e2865d801d0f0e9bed03a97b2077253f6ae9982"
N,FPS,MS=80,20,50
COLORS=[(104,152,232),(248,232,104),(248,248,216)]
def sha(b):return hashlib.sha256(b).hexdigest()
def allowed(x,y,p):
    if not(33<=y<111) or p[:3]!=(49,82,181):return False
    if x<171 and y<57:return False
    if 30<=x<137 and 56<=y<103:return False
    if 152<=x<239 and 56<=y<148:return False
    return True
def render(base):
    rgb=base.convert("RGB");pixels=list(rgb.getdata())
    mask=[allowed(i%240,i//240,p) for i,p in enumerate(pixels)]
    assert sum(mask)>100,"Expected background mask missing"
    palette=sorted(set(pixels)|set(COLORS));assert len(palette)<=256
    lut={c:i for i,c in enumerate(palette)}
    pal=[v for c in palette for v in c]+[0]*(768-len(palette)*3)
    frames=[];protected=0;changed=0
    for n in range(N):
        t=n/FPS;effect=Image.new("RGB",(240,160),(0,0,0));d=ImageDraw.Draw(effect)
        for k,(x,y) in enumerate([(9,69),(21,86),(143,78),(182,42),(217,38),(230,47)]):
            q=max(0,1-abs(((t+k*.47)%2)-1)*4)
            if q>.1:
                c=COLORS[min(2,int(q*3))]
                d.point((x,y),fill=c)
                if q>.45:d.line((x-1,y,x+1,y),fill=c);d.line((x,y-1,x,y+1),fill=c)
                if q>.8:d.point((x,y-2),fill=COLORS[0]);d.point((x,y+2),fill=COLORS[0])
        for start,x,y in [(.55,6,71),(1.5,140,63),(2.5,17,85),(3.2,199,38)]:
            dt=t-start
            if 0<=dt<.2:
                c=COLORS[2 if dt<.1 else 0]
                d.line([(x,y),(x+3,y+3),(x+1,y+6),(x+5,y+9)],fill=c,width=1)
        e=list(effect.getdata());out=list(pixels)
        for i in range(len(out)):
            if mask[i] and e[i]!=(0,0,0):out[i]=e[i]
            if out[i]!=pixels[i]:
                changed+=1
                if not mask[i]:protected+=1
        f=Image.new("P",(240,160));f.putpalette(pal);f.putdata([lut[p] for p in out]);frames.append(f)
    assert protected==0 and changed>0
    return frames,{"allowed_background_pixels":sum(mask),"protected_changes":protected,
                   "effect_pixel_changes_total":changed,"palette_entries":len(palette)}
def effects_wav(path):
    rate=44100;r=random.Random(7331);data=bytearray();prior=0.0
    for i in range(rate*4):
        t=i/rate;v=0.0;noise=r.uniform(-1,1);high=noise-prior;prior=noise
        for start in (.55,1.5,2.5,3.2):
            dt=t-start
            if 0<=dt<.17:
                env=min(1,dt/.006)*math.exp(-dt*26)
                v+=env*(.05*high+.025*math.sin(2*math.pi*1800*dt))
        data+=struct.pack("<h",round(max(-.2,min(.2,v))*32767))
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(data)
def verify_gif(path,frames,scale):
    g=Image.open(path);at=0
    assert g.info.get("loop")==0
    for j in range(g.n_frames):
        g.seek(j);duration=g.info["duration"];assert duration%MS==0
        got=g.convert("RGB")
        for n in range(at//MS,(at+duration)//MS):
            expect=frames[n].convert("RGB")
            if scale!=1:expect=expect.resize((240*scale,160*scale),Image.Resampling.NEAREST)
            assert got.tobytes()==expect.tobytes(),("GIF pixels differ",j,n)
        at+=duration
    assert at==4000
    return {"decoded_frames":g.n_frames,"duration_ms":at,"exact_pixel_roundtrip":True}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--png",type=Path,required=True);ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--ffmpeg");ap.add_argument("--music",type=Path)
    a=ap.parse_args();assert not a.out.exists(),"Output folder must be new"
    original=a.png.read_bytes();base=Image.open(io.BytesIO(original)).convert("RGBA")
    assert base.size==(240,160) and sha(base.tobytes())==PIXEL_SHA,"Not the approved current title PNG"
    assert {p[3] for p in base.getdata()}=={255}
    if a.music:
        assert a.music.is_file() and "click" not in a.music.name.lower(),"Use real existing game music only"
    exe=a.ffmpeg or shutil.which("ffmpeg") or os.environ.get("IMAGEIO_FFMPEG_EXE")
    if not exe:
        import imageio_ffmpeg
        exe=imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([exe,"-version"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    frames,report=render(base);a.out.mkdir(parents=True)
    native=a.out/"title-current-native.gif";preview=a.out/"title-current-review.gif"
    frames[0].save(native,save_all=True,append_images=frames[1:],duration=MS,loop=0,optimize=False,disposal=1)
    big=[f.resize((960,640),Image.Resampling.NEAREST) for f in frames]
    big[0].save(preview,save_all=True,append_images=big[1:],duration=MS,loop=0,optimize=False,disposal=1)
    report["native_gif"]=verify_gif(native,frames,1);report["preview_gif"]=verify_gif(preview,frames,4)
    if a.music:audio=a.music;audio_kind="existing game audio supplied; timing not ROM-calibrated"
    else:
        audio=a.out/"electric-effects.wav";effects_wav(audio);audio_kind="short electric effects only; no music"
    mp4=a.out/"title-current-with-sfx.mp4"
    cmd=[exe,"-v","error","-n","-f","rawvideo","-pix_fmt","rgb24","-s","240x160","-r",str(FPS),"-i","pipe:0",
         "-i",str(audio),"-map","0:v:0","-map","1:a:0","-vf","scale=960:640:flags=neighbor",
         "-c:v","libx264","-crf","15","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-t","4",
         "-af","afade=t=in:st=0:d=0.02,afade=t=out:st=3.8:d=0.2","-movflags","+faststart",str(mp4)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for f in frames:p.stdin.write(f.convert("RGB").tobytes())
        p.stdin.close();assert p.wait()==0,"MP4 encode failed"
    finally:
        if p.poll() is None:p.kill();p.wait()
    assert a.png.read_bytes()==original,"Source PNG changed"
    report.update(status="APPROVED_PNG_EFFECT_DRAFT",source_png_sha256=sha(original),source_rgba_sha256=PIXEL_SHA,
        source_png_preserved=True,pose_face_and_text_preserved=True,body_ear_tail_animation=False,
        gif_is_silent=True,mp4_audio=audio_kind,rom_integrated=False,new_music_created=False,
        files={p.name:{"bytes":p.stat().st_size,"sha256":sha(p.read_bytes())} for p in (native,preview,mp4)})
    (a.out/"validation.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
