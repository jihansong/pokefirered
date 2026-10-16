#!/usr/bin/env python3
"""Verify original selected title voice linkage and A/START playback in the ROM."""
from pathlib import Path
import argparse,hashlib,json,struct,sys,wave
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"tools/qa"))
from emu import Emu
from gamedata import const,CONST_HEADERS
if "constants/songs.h" not in CONST_HEADERS:CONST_HEADERS.append("constants/songs.h")
def sha(b):return hashlib.sha256(b).hexdigest()
def task(e,name):
    fn=e.sym(name)
    for i in range(16):
        t=e.sym("gTasks")+i*40
        if e.u8(t+4) and (e.u32(t)&~1)==fn:return t
    return None
p=argparse.ArgumentParser();p.add_argument("--rom",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
p.add_argument("--expect-source",required=True)
a=p.parse_args();a.rom=a.rom.resolve();assert not a.out.exists(),"Fresh audio QA output required"
rom=a.rom.read_bytes();before=sha(rom)
origin=json.loads((ROOT/"docs/music/title-pikachu-voice-origin.json").read_text())
assert a.expect_source=="10a2a254c12eed24a7e4d7a4db9ffff3f318ae20c17a5b15dbe53bbcf4c50734"
assert origin["source_sha256"]==a.expect_source
assert origin["archive_sha256"]=="13d6f49f3e208573d9129378bdf8836d060fcdb9c73ea810526cda8921164d93"
assert origin["source_type"]=="creator_linked_archive" and not origin["direct_youtube_extraction"]
assert origin["distribution_url"]=="https://soundsverse.com/wp-content/uploads/s/pokemon-video-game-pikachu-voice-sound-effect.zip"
assert Path(origin["archive_entry"]).name=="pokemon-video-game-pikachu-voice-sound-effect.wav"
assert origin["native_samples"]==17638 and origin["note_frames"]==98
assert origin["source_url"]=="https://www.youtube.com/watch?v=gF1FJRM8Wck"
assert origin["whole_clip"] and not origin["trimmed"] and not origin["synthesized"]
binary=(ROOT/"sound/direct_sound_samples/cries/title_pikachu_voice.bin").read_bytes()
a.out.mkdir(parents=True);results=[]
for key in ("START","A"):
    row={"key":key,"pass":False}
    try:
        with Emu(str(a.rom)) as e:
            tone=e.sym("gPikachuVoiceTable")+42*12;sample=e.sym("PikachuVoice_Title")
            assert e.read(sample,len(binary))==binary,"Built sample does not match linked sample"
            assert e.read(tone,4)==bytes((0x20,60,0,0)) and e.u32(tone+4)==sample
            assert e.u32(sample+4)==11025*1024,"Unexpected sample pitch/rate"
            assert e.u32(sample+12)==origin["native_samples"],"Built sample duration was truncated"
            for _ in range(6000):
                t=task(e,"Task_TitleScreenMain")
                if (e.callback2()&~1)==e.sym("CB2_TitleScreenRun") and t is not None and e.u16(t+8)==3 and e.u16(t+10)==1:break
                e.hold();e.run(1)
            else:raise AssertionError("Title input-ready scene not reached")
            song=e.u32(e.sym("gSongTable")+const("MUS_TITLE")*8)
            assert e.ptr("gMPlayInfo_BGM")==song,"Expected existing FR/LG title BGM"
            e.audio_start(32768);pcm=bytearray(e.run_audio(8));e.hold(key)
            first=None;finished=None;exit_frame=None
            for frame in range(origin["note_frames"]+300):
                if frame==3:e.hold()
                pcm.extend(e.run_audio(1));duck=task(e,"Task_DuckBGMForPokemonCry")
                if duck is not None:
                    cry=e.ptr("gMPlay_PokemonCry");assert cry
                    header=e.u32(cry);assert e.u32(header+4)==tone,"Wrong cry tone played"
                    if first is None:
                        first=frame
                        assert e.u16(e.sym("gPokemonCrySong")+0x2e)==origin["note_frames"]
                        assert e.u8(e.sym("gPokemonCrySong")+0x2a)==60,"Unexpected voice pitch shift"
                elif first is not None and finished is None:finished=frame
                if (e.callback2()&~1)!=e.sym("CB2_TitleScreenRun"):
                    assert first is not None and finished is not None,"Title exited before original cry finished"
                    assert frame>=90,"Existing minimum transition delay regressed"
                    exit_frame=frame;break
            assert exit_frame is not None,"Title did not proceed after the original clip"
            e.hold();pcm.extend(e.run_audio(30));e.shot(str(a.out/(key.lower()+"-after.png")),scale=4)
            audio=a.out/(key.lower()+"-title-voice-game.wav")
            with wave.open(str(audio),"wb") as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(32768);w.writeframes(pcm)
            samples=struct.unpack("<%dh"%(len(pcm)//2),pcm);assert max(abs(x) for x in samples)>0
            row.update({"pass":True,"voice_first_frame":first,"voice_finished_frame":finished,"title_exit_frame":exit_frame,
                        "capture_sha256":sha(pcm),"capture_seconds":len(pcm)/4/32768,"linked_sample_sha256":sha(binary)})
    except Exception as ex:row.update({"pass":False,"error":repr(ex)})
    results.append(row);print(json.dumps(row),flush=True)
report={"pass":all(x["pass"] for x in results),"cases":results,"rom_sha256":before,
        "rom_preserved":sha(a.rom.read_bytes())==before,"user_save_loaded":False,
        "original_source_sha256":origin["source_sha256"],"source_url":origin["source_url"],
        "archive_sha256":origin["archive_sha256"],"archive_entry":origin["archive_entry"],"distribution_url":origin["distribution_url"],"audio_auditioned":False,"content_synthesized":False}
report["pass"]=report["pass"] and report["rom_preserved"]
(a.out/"validation.json").write_text(json.dumps(report,indent=2))
raise SystemExit(0 if report["pass"] else 1)
