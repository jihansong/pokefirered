"""Extend the existing opening to its captured FR/LG cue; no new artwork."""
import argparse, ast, copy, hashlib, io, json, math, shutil, subprocess, sys, wave, zipfile
from pathlib import Path
from types import SimpleNamespace
SOURCE_SHA = "2517e5d10adc07e303fb1f8b8c93f06d70d6a63fde57c93ccf13ef39d96f69de"
AUDIO_SHA = "5120399e966cef14b6a4c00a69461fdd01a83b881128dfe8845b9cc8f67c15d8"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def has_name(node, name):
    return any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(node))
def call_name(node, name):
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name
def load_renderer(source, root, out):
    tree = ast.parse(source.read_text(encoding="utf-8"))
    body = []
    skipped = {"ap": 0, "args": 0, "mkdir": 0}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(has_name(t, "KEYS") for t in node.targets): break
        if isinstance(node, ast.Assign) and any(has_name(t, "ap") for t in node.targets):
            skipped["ap"] += 1; continue
        if isinstance(node, ast.Assign) and any(has_name(t, "args") for t in node.targets):
            skipped["args"] += 1; continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            fun = node.value.func
            if isinstance(fun, ast.Attribute) and isinstance(fun.value, ast.Name):
                if fun.value.id == "ap": continue
                if fun.value.id == "OUT" and fun.attr == "mkdir":
                    skipped["mkdir"] += 1; continue
        body.append(node)
    else: raise AssertionError("KEYS boundary missing")
    assert skipped == {"ap": 1, "args": 1, "mkdir": 1}, skipped
    env = {"__file__": str(source), "__name__": "_opening_v5_source",
           "args": SimpleNamespace(repo=root, output=out, stills_only=True)}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(source), "exec"), env)
    assert (env["W"], env["H"], env["FPS"], env["COUNT"]) == (240,160,60,600)
    assert env["SHOTS"][-1][0:2] == (468,600)
    sky = copy.deepcopy(next(n for n in body if isinstance(n, ast.FunctionDef) and n.name == "shot_sky"))
    fade = [n for n in sky.body if isinstance(n, ast.If)
            and ast.dump(n.test) == ast.dump(ast.parse("t > 116", mode="eval").body)
            and any(call_name(x, "wash") for x in ast.walk(n))]
    assert len(fade) == 1, "Expected one final sky fade"
    sky.body.remove(fade[0])
    class ClampApproach(ast.NodeTransformer):
        cloud_calls = bird_calls = clamped = 0
        def visit_Call(self, n):
            if call_name(n, "put") and len(n.args)>1 and isinstance(n.args[1],ast.Name) and n.args[1].id=="cloud":
                self.cloud_calls += 1; return n
            if call_name(n, "hooh_field"):
                self.bird_calls += 1; return n
            return self.generic_visit(n)
        def visit_Name(self, n):
            if n.id=="t" and isinstance(n.ctx,ast.Load):
                self.clamped += 1
                return ast.copy_location(ast.parse("min(t,116)",mode="eval").body,n)
            return n
    tx = ClampApproach()
    sky = tx.visit(sky); sky.name = "shot_sky_extended"
    assert tx.cloud_calls == 1 and tx.bird_calls == 1 and tx.clamped > 0, vars(tx)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[sky],type_ignores=[])),
                 str(source)+":extended", "exec"),env)
    return env

def checked(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout

def probe(ffprobe,p):
    return json.loads(checked([ffprobe,"-v","error","-count_frames","-show_streams","-show_format","-of","json",str(p)]))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path.cwd())
    ap.add_argument("--output",type=Path)
    a=ap.parse_args(); root=a.root.resolve()
    source=root/"work/native-opening-v5/render_opening.py"
    audio=root/"outputs/opening-frlg-music-v6/frlg-mus-intro-fight.wav"
    assert sha(source)==SOURCE_SHA and sha(audio)==AUDIO_SHA, "Input changed"
    with wave.open(str(audio),"rb") as w:
        samples,rate,channels=w.getnframes(),w.getframerate(),w.getnchannels()
    assert (samples,rate,channels)==(410372,32768,2)
    count=(samples*60+rate-1)//rate
    assert count==752
    out=(a.output or root/"outputs/opening-full-frlg-v7").resolve()
    assert not out.exists(), "Output already exists; preserve it and select a new directory"
    ffmpeg=shutil.which("ffmpeg"); ffprobe=shutil.which("ffprobe")
    if not ffmpeg:
        sys.path.insert(0,str(root/"work/native-opening/vendor"))
        import imageio_ffmpeg
        ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    assert ffprobe, "ffprobe required for final validation"
    env=load_renderer(source,root,out)
    out.mkdir(parents=True)
    Image=env["Image"]; baseline=env["render"]
    archive=root/"outputs/opening-hooh-color-v5/opening-native-600-frames.zip"
    archive_sha=sha(archive)
    reference=hashlib.sha256()
    with zipfile.ZipFile(archive) as z:
        for n in range(585):
            prior=Image.open(io.BytesIO(z.read("frames/%04d.png"%n))).convert("RGB")
            assert prior.size==(240,160)
            assert baseline(n).tobytes()==prior.tobytes(), "v5 archive mismatch at %d"%n
            reference.update(prior.tobytes())
    def frame(n):
        if n<585: return baseline(n)
        viewport=env["shot_sky_extended"](n-468)
        if n>count-16: viewport=env["wash"](viewport,(0,0,0),(n-(count-16))/15)
        im=Image.new("RGB",(240,160),(0,0,0))
        im.paste(viewport.convert("RGB"),(0,32)); return im
    native=out/"opening-full-frlg-native.mp4"
    preview=out/"opening-full-frlg-preview.mp4"
    cmd=[ffmpeg,"-hide_banner","-loglevel","error","-n","-f","rawvideo",
         "-pixel_format","rgb24","-video_size","240x160","-framerate","60","-i","pipe:0",
         "-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","medium",
         "-crf","10","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",str(native)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    rendered=hashlib.sha256(); frame_hashes=[]
    try:
        for n in range(count):
            im=frame(n); raw=im.tobytes()
            if n<585: rendered.update(raw)
            frame_hashes.append(hashlib.sha256(raw).hexdigest())
            if n in {0,584,585,599,count-16,count-1}: im.save(out/("frame-%04d.png"%n))
            proc.stdin.write(raw)
            if n%120==0: print("Rendered",n,"/",count,flush=True)
    finally:
        proc.stdin.close()
    err=proc.stderr.read().decode(); assert proc.wait()==0,err
    assert rendered.digest()==reference.digest(), "First 585 RGB frames changed"
    assert not any(frame(count-1).tobytes()), "Final frame must retain original black fade endpoint"
    checked([ffmpeg,"-hide_banner","-loglevel","error","-n","-i",str(native),
             "-vf","scale=960:640:flags=neighbor","-c:v","libx264","-crf","12",
             "-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",str(preview)])
    reports={}
    for p,size in [(native,(240,160)),(preview,(960,640))]:
        info=probe(ffprobe,p); vs=next(s for s in info["streams"] if s["codec_type"]=="video")
        au=next(s for s in info["streams"] if s["codec_type"]=="audio")
        assert (vs["width"],vs["height"])==size and int(vs["nb_read_frames"])==count
        assert vs["avg_frame_rate"]=="60/1"
        assert abs(float(au["duration"])-samples/rate)<.002,au["duration"]
        checked([ffmpeg,"-hide_banner","-loglevel","error","-i",str(p),"-f","null","-"])
        reports[p.name]={"sha256":sha(p),"bytes":p.stat().st_size,"probe":info}
    assert sha(source)==SOURCE_SHA and sha(audio)==AUDIO_SHA and sha(archive)==archive_sha,"Original input changed"
    audit={"pass":True,"frames":count,"fps":60,"video_seconds":count/60,
           "audio_samples":samples,"audio_rate":rate,"audio_seconds":samples/rate,
           "video_audio_difference_seconds":count/60-samples/rate,
           "preserved_rgb_frames":[0,584],"preserved_rgb_sha256":rendered.hexdigest(),
           "fade_frames":[count-15,count-1],"new_artwork":False,"rom_integrated":False,
           "approach_clamped_at_sky_frame":116,"original_flap_and_cloud_animation":True,
           "source_sha256":SOURCE_SHA,"audio_sha256":AUDIO_SHA,
           "reference_archive_sha256":archive_sha,"reference_kind":"v5 archived PNG frames",
           "audio_length_kind":"Existing native MUS_INTRO_FIGHT capture including tail; not end-detected",
           "limitations":["Existing pose substitutions remain; no new keyframes.",
                          "RGB renderer prefix verified; lossy encoded video bytes are not identical.",
                          "Not the full original FR/LG visual opening; no listening or DELTA review claimed."],
           "frame_sha256":frame_hashes,"outputs":reports}
    (out/"validation.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
    print(json.dumps({"output":str(out),"frames":count,"prefix_same":True,"audio_seconds":samples/rate}))
if __name__=="__main__": main()
