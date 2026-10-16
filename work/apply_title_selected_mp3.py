#!/usr/bin/env python3
"""Install the user-selected complete MP3 as the title cry; never synthesize/trim."""
from pathlib import Path
import argparse,hashlib,io,json,math,re,shutil,subprocess,wave
def sha(b):return hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument("--repo",type=Path,default=Path.cwd());p.add_argument("--source",type=Path,required=True)
p.add_argument("--expect-title",required=True);p.add_argument("--expect-table",required=True);p.add_argument("--write",action="store_true")
a=p.parse_args();r=a.repo.resolve();source=a.source.read_bytes()
expected="fe53196f162c72c75e6fff5aea9c547c0287913a7902fc8318d6baab96fda219"
assert sha(source)==expected,"Wrong user-selected original MP3"
ff=shutil.which("ffmpeg");assert ff,"Existing FFmpeg required"
raw=subprocess.check_output([ff,"-nostdin","-v","error","-i",str(a.source),"-map","0:a:0","-ac","1","-ar","11025","-f","u8","pipe:1"])
frames=math.ceil(len(raw)/11025*60)+2
assert 2<frames<=255,"Whole clip exceeds u8 cry length: extend length API; do not trim"
buf=io.BytesIO()
with wave.open(buf,"wb") as w:w.setnchannels(1);w.setsampwidth(1);w.setframerate(11025);w.writeframes(raw)
wav=buf.getvalue();names=("src/title_screen.c","sound/pikachu_voice_table.inc","sound/direct_sound_data.inc")
old={f:(r/f).read_bytes() for f in names};text={f:b.decode() for f,b in old.items()}
assert sha(old[names[0]])==a.expect_title and sha(old[names[1]])==a.expect_table,"Fresh source SHA required"
assert len(re.findall(r"^\s*cry PikachuVoice_\d+\s*$",text[names[1]],re.M))==42
assert "PikachuVoice_Title" not in text[names[1]]+text[names[2]]
title=text[names[0]];anchor='#include "constants/songs.h"'
assert title.count(anchor)==1 and "title_pikachu_voice.h" not in title
inc='\n#include "title_pikachu_voice.h"'
if '#include "sound.h"' not in title:inc+='\n#include "sound.h"'
title=title.replace(anchor,anchor+inc,1)
start=title.index("static void SetTitleScreenScene_Cry(s16 *data)\n{");end=title.index("\n}",start)+2;part=title[start:end]
call="PlayCry_Normal(TITLE_SPECIES, 0);";wait="else if (!IsSlashSpriteDeactivated(tSlashSpriteId))"
assert part.count(call)==part.count(wait)==1
part=part.replace(call,"PlayPikachuVoice(TITLE_PIKACHU_VOICE_ID, TITLE_PIKACHU_VOICE_FRAMES);")
part=part.replace(wait,"else if (IsCryFinished() && !IsSlashSpriteDeactivated(tSlashSpriteId))")
title=title[:start]+part+title[end:]
header=("#ifndef GUARD_TITLE_PIKACHU_VOICE_H\n#define GUARD_TITLE_PIKACHU_VOICE_H\n"
        "// Appended title-only voice; the original 42 emotion IDs stay unchanged.\n"
        "#define TITLE_PIKACHU_VOICE_ID 42\n"+f"#define TITLE_PIKACHU_VOICE_FRAMES {frames}\n#endif\n")
origin={"source_file":a.source.name,"source_sha256":expected,"selected_by_user":True,"agent_auditioned":False,
        "whole_clip":True,"trimmed":False,"synthesized":False,"pitch_or_time_stretch":False,
        "processing":["MP3 decode","mono downmix","11025 Hz resample","8-bit PCM game format"],
        "native_samples":len(raw),"native_seconds":len(raw)/11025,"note_frames":frames,"wav_sha256":sha(wav)}
new={names[0]:title.encode(),names[1]:(text[names[1]].rstrip()+"\n\tcry PikachuVoice_Title\n").encode(),
     names[2]:(text[names[2]].rstrip()+'\n\n\t.align 2\nPikachuVoice_Title::\n\t.incbin "sound/direct_sound_samples/cries/title_pikachu_voice.bin"\n').encode(),
     "include/title_pikachu_voice.h":header.encode(),"sound/direct_sound_samples/cries/title_pikachu_voice.wav":wav,
     "docs/music/title-pikachu-voice-origin.json":(json.dumps(origin,indent=2)+"\n").encode()}
for name in new:
    target=(r/name).resolve();assert target.is_relative_to(r)
    if name not in old:assert not target.exists(),("Existing file preserved",name)
assert a.source.read_bytes()==source,"Original changed during conversion"
report={"state":"PREFLIGHT_ONLY","origin":origin,"game_audio_verified":False,"save_layout_changed":False,
        "files":{f:{"before":sha(old[f]) if f in old else None,"after":sha(b)} for f,b in new.items()}}
if a.write:
    backup=r/"work/title-pika-selected-mp3-v1";assert not backup.exists(),"Prior run preserved"
    for name,b in old.items():assert (r/name).read_bytes()==b,"Concurrent source edit"
    backup.mkdir(parents=True)
    for name,b in old.items():
        target=backup/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
    (backup/"manifest.json").write_text(json.dumps(report,indent=2))
    for name,b in new.items():
        target=r/name;target.parent.mkdir(parents=True,exist_ok=True)
        if name in old:assert target.read_bytes()==old[name];target.write_bytes(b)
        else:
            with target.open("xb") as f:f.write(b)
    for name,b in new.items():assert (r/name).read_bytes()==b
    assert a.source.read_bytes()==source
    report["state"]="APPLIED_USER_SELECTED_ORIGINAL_MP3"
    (backup/"manifest.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
