#!/usr/bin/env python3
"""Extract a review candidate from the supplied official clip; never synthesize."""
from pathlib import Path
import argparse,hashlib,json,math,shutil,subprocess,wave
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser()
p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
p.add_argument("--start",type=float,required=True);p.add_argument("--end",type=float,required=True)
a=p.parse_args()
expected="38a3a9557821d3db8106d86adc1c24819c0db66b07d889d7e2fec291aac3effe"
assert sha(a.source)==expected,"Wrong source clip"
assert 0<=a.start<a.end and .15<=a.end-a.start<=1.35,"Choose one short original call"
assert not a.out.exists(),"Fresh output required"
ff=shutil.which("ffmpeg");probe=shutil.which("ffprobe")
assert ff and probe,"Existing FFmpeg/ffprobe required"
meta=json.loads(subprocess.check_output([probe,"-v","error","-select_streams","a:0","-show_streams","-of","json",str(a.source)]))
stream=meta["streams"][0];rate=int(stream["sample_rate"]);channels=int(stream["channels"])
assert channels in (1,2) and abs(float(stream.get("start_time",0)))<1/rate,"Check nonzero source audio start offset"
n0=round(a.start*rate);n1=round(a.end*rate)
a.out.mkdir(parents=True)
original=a.out/"pika-source-candidate.wav";game=a.out/"pika-game-candidate.wav"
subprocess.run([ff,"-v","error","-nostdin","-n","-i",str(a.source),"-map","0:a:0","-af",f"atrim=start_sample={n0}:end_sample={n1},asetpts=N/SR/TB","-c:a","pcm_s16le",str(original)],check=True)
with wave.open(str(original),"rb") as w:
    assert (w.getframerate(),w.getnchannels(),w.getnframes())==(rate,channels,n1-n0),"Source excerpt mismatch"
subprocess.run([ff,"-v","error","-nostdin","-n","-i",str(original),"-ac","1","-ar","11025","-c:a","pcm_u8",str(game)],check=True)
with wave.open(str(game),"rb") as w:
    frames=math.ceil(w.getnframes()/w.getframerate()*60)+2
    assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,1,11025)
    assert frames<90,"Clip outlasts existing title transition"
assert sha(a.source)==expected,"Source changed"
report={"status":"ORIGINAL_CLIP_EXCERPT_REVIEW_REQUIRED","source_sha256":expected,"source_name":a.source.name,"requested_seconds":[a.start,a.end],"actual_source_samples":[n0,n1],"source_rate":rate,"actual_seconds":[n0/rate,n1/rate],"game_note_frames":frames,"processing":["sample-accurate trim","PCM format conversion","mono downmix","11025 Hz resample"],"synthesis_used":False,"pitch_or_time_stretch":False,"speech_content_verified":False,"isolated_voice_verified":False,"auditioned":False,"files":{f.name:{"bytes":f.stat().st_size,"sha256":sha(f)} for f in (original,game)}}
(a.out/"origin.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
