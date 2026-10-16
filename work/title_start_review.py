"""Browser-only START review using approved title, existing mouth paths and original voice."""
import argparse, hashlib, json, xml.etree.ElementTree as ET
from pathlib import Path
PINS={
 "outputs/title-font-python-v3/title-font-candidate-240x160.png":"7e370cc2d5b4cd71a1ae68b1da6934b62a049fc9e83efb2fc51619231cc122c5",
 "outputs/pikachu-expression-edit-v1/03-release.svg":"47369561c896b4e1a99994d3e701b9c02803875000874bab91b033e004c79546",
 "outputs/title-front-edit-v1/front-mono-fitted.svg":"11f5011985dcbd17add685f9b9387781c0ef71d9f9d97ead06d701275e30a330",
 "graphics/battle_anims/sprites/lightning.png":"26a0fbf2622cf32ddff6193e8bfaccfa5a655ad85737292b0d1466caba934763",
 "reference/audio/pikachu-gF1FJRM8Wck/publisher-original/pokemon-video-game-pikachu-voice-sound-effect.wav":"10a2a254c12eed24a7e4d7a4db9ffff3f318ae20c17a5b15dbe53bbcf4c50734"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path.cwd())
 ap.add_argument("--output",type=Path);ap.add_argument("--thunder",type=Path)
 a=ap.parse_args();root=a.root.resolve();out=(a.output or root/"outputs/title-start-review-v1").resolve()
 assert not out.exists(),"Preserve existing output and choose another directory"
 for name,want in PINS.items():assert sha(root/name)==want,(name,"changed")
 paths=lambda name:ET.fromstring((root/name).read_text(encoding="utf-8")).iter("{http://www.w3.org/2000/svg}path")
 def exact(name,d):
  hits=[p for p in paths(name) if p.get("d")==d];assert len(hits)==1,(d,len(hits));return hits[0]
 front="outputs/title-front-edit-v1/front-mono-fitted.svg";release="outputs/pikachu-expression-edit-v1/03-release.svg"
 mask=exact(front,"M246 196 L316 196 320 218 245 218Z")
 mouth_specs=[
 ("M277 224 Q290 229 303 223 Q308 237 295 241 Q282 238 277 224Z","#281808"),
 ("M286 234 Q295 230 301 233 Q299 240 294 239Z","#D8A828"),
 ("M280 225 L298 226 294 229 284 227Z","#F8F8C8")]
 mouth="".join('<path d="'+exact(release,d).get("d")+'" fill="'+fill+'"/>' for d,fill in mouth_specs)
 overlay='<svg xmlns="http://www.w3.org/2000/svg" width="240" height="160" viewBox="0 0 240 160"><defs><clipPath id="mouth"><rect x="170" y="109" width="24" height="13"/></clipPath></defs><g clip-path="url(#mouth)"><svg x="152" y="56" width="86" height="90" viewBox="80 0 310 324"><g transform="translate(470 0) scale(-1 1)"><path d="'+mask.get("d")+'" fill="'+mask.get("fill")+'"/><g transform="translate(285 206) scale(1.7 1.3) translate(-292 -224)">'+mouth+'</g></g></svg></g></svg>'
 effect=(a.thunder.resolve() if a.thunder else root/"outputs/title-continuous-crackle-v3/continuous-electricity.wav")
 assert effect.is_file()
 routes={
 "/title-approved.png":next(iter(PINS)),
 "/title-start-mouth.svg":str((out/"start-mouth.svg").relative_to(root)),
 "/title-native-lightning.png":"graphics/battle_anims/sprites/lightning.png",
 "/title-original-pika.wav":"reference/audio/pikachu-gF1FJRM8Wck/publisher-original/pokemon-video-game-pikachu-voice-sound-effect.wav",
 "/title-start-electricity.wav":str(effect.relative_to(root)),
 "/title-current-continuous-electricity.mp4":"outputs/title-frlg-music-v4/title-frlg-music-crackle.mp4"}
 for name in routes.values():
  if name!=routes["/title-start-mouth.svg"]:assert (root/name).is_file(),name
 out.mkdir(parents=True)
 (out/"start-mouth.svg").write_text(overlay,encoding="utf-8")
 html=HTML.replace("__EFFECT_KIND__", "native-thunderbolt" if a.thunder else "existing-continuous-electricity")
 (out/"index.html").write_text(html,encoding="utf-8")
 report={"generated":True,"browser_review_pending":True,"rom_integrated":False,
         "approved_png_unchanged":True,"voice_unchanged":True,"new_artwork":False,
         "method":"Reuse three existing release mouth paths in a native SVG overlay; retain approved base PNG",
         "mouth_roi":[170,109,194,122],"mouth_source":release,"title_layout":[152,56,86,90],
         "lightning_animation_frames":[5,5,8,5,5],"effect_kind":"native-thunderbolt" if a.thunder else "existing-continuous-electricity",
         "effect_sha256":sha(effect),"source_hashes":PINS,"routes":routes,
         "limitations":["Interactive browser preview; not installed in the game.",
                        "Mouth is an existing expression overlay, not newly drawn artwork.",
                        "Original thunderbolt SFX is pending if effect_kind is existing-continuous-electricity."]}
 for name,want in PINS.items():assert sha(root/name)==want
 (out/"source-validation.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
 print(json.dumps({"output":str(out),"routes":routes,"effect_kind":report["effect_kind"]}))
HTML=r'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Thunder Yellow — START</title><style>
body{margin:0;background:#0b1020;color:#f9e98a;font:16px system-ui;display:grid;place-items:center;min-height:100vh}
main{width:min(96vw,960px);text-align:center}canvas{width:100%;image-rendering:pixelated;background:#000}
button{font:700 22px system-ui;color:#211b07;background:#ffdf54;border:0;border-radius:9px;padding:12px 40px;margin:18px}
button:disabled{opacity:.45}p{color:#bec7d5}a{color:#f9e98a}</style>
<main><canvas id="screen" width="240" height="160" aria-label="Thunder Yellow 타이틀 미리보기"></canvas>
<button id="start" disabled>준비 중…</button><p id="status" role="status">이미지와 원본 음성을 준비하고 있습니다.</p>
<p><small>START 연출 미리보기</small></p></main><script>
"use strict";
const canvas=document.getElementById("screen"),ctx=canvas.getContext("2d",{willReadFrequently:true});
const startButton=document.getElementById("start"),status=document.getElementById("status");
ctx.imageSmoothingEnabled=false;
const loadImage=url=>new Promise((resolve,reject)=>{const im=new Image;im.onload=()=>resolve(im);im.onerror=reject;im.src=url});
const bytes=async url=>{const r=await fetch(url);if(!r.ok)throw Error(url+" "+r.status);return r.arrayBuffer()};
let images,raw,ac,buffers,busy=false,raf=0,active=[],music=null,musicOffset=0,musicStarted=0;
const qa={effectKind:"__EFFECT_KIND__",sourceVoice:"publisher-original WAV",startEvents:[],staticPixelsPreserved:false};
window.titleStartReview=qa;
function base(){ctx.clearRect(0,0,240,160);ctx.drawImage(images[0],0,0)}
function paint(t=0,mouth=false){
 base();if(mouth)ctx.drawImage(images[1],0,0);
 const f=Math.floor(t*60),ends=[5,10,18,23,28],cell=ends.findIndex(x=>f<x);
 if(mouth&&f>=0&&cell>=0){ctx.drawImage(images[2],0,cell*32,32,32,204,74,32,32);ctx.drawImage(images[2],0,cell*32,32,32,204,106,32,32)}
}
function validateMouth(){
 base();const before=ctx.getImageData(0,0,240,160).data;
 ctx.drawImage(images[1],0,0);const after=ctx.getImageData(0,0,240,160).data;
 let changed=0,outside=0;
 for(let i=0;i<before.length;i+=4){if(before.slice(i,i+4).some((x,j)=>x!==after[i+j])){changed++;const p=i/4,x=p%240,y=Math.floor(p/240);if(x<170||x>=194||y<109||y>=122)outside++}}
 base();qa.mouthChangedPixels=changed;qa.mouthOutsideRoi=outside;
 if(!changed||outside)throw Error("입 오버레이 보존 검증 실패");
 const restored=ctx.getImageData(0,0,240,160).data;
 qa.staticPixelsPreserved=restored.every((v,i)=>v===before[i]);
 if(!qa.staticPixelsPreserved)throw Error("기본 이미지 보존 검증 실패");
}
function pauseMusic(){if(music){musicOffset=(Math.max(0,ac.currentTime-musicStarted)+musicOffset)%buffers[2].duration;music.stop();music=null}}
function resumeMusic(){if(buffers&&!music){musicStarted=ac.currentTime+.02;[music]=source(buffers[2],.75,musicStarted,true,musicOffset)}}
function stop(resume=true){cancelAnimationFrame(raf);active.forEach(s=>{try{s.stop()}catch{}});active=[];busy=false;if(images)base();if(resume)resumeMusic();startButton.disabled=false}
function source(buffer,gain,when,loop=false,offset=0){
 const s=ac.createBufferSource(),g=ac.createGain();s.buffer=buffer;s.loop=loop;g.gain.value=gain;s.connect(g);g.connect(ac.destination);s.start(when,offset);return [s,g];
}
async function run(){
 if(busy)return;busy=true;startButton.disabled=true;
 try{
  if(!ac)ac=new AudioContext;
  await ac.resume();
  if(!buffers)buffers=await Promise.all(raw.map(b=>ac.decodeAudioData(b.slice(0))));
  pauseMusic();
  const when=ac.currentTime+.06,duration=buffers[0].duration;
  const [voice]=source(buffers[0],.85,when),[effect]=source(buffers[1],.15,when);
  effect.stop(when+Math.min(duration,buffers[1].duration));active=[voice,effect];
  const event={voiceStart:when,effectStart:when,voiceDuration:duration,mouthFirstTime:null,finished:false};qa.startEvents.push(event);
  status.textContent="피카!";
  function tick(){
   const t=ac.currentTime-when;
   if(t<0){base();raf=requestAnimationFrame(tick);return}
   if(t<duration){if(event.mouthFirstTime===null)event.mouthFirstTime=ac.currentTime;paint(t,true);raf=requestAnimationFrame(tick)}
   else{event.finished=true;event.visualEnd=ac.currentTime;stop();status.textContent="START를 눌러 다시 재생할 수 있습니다."}
  }
  tick();
 }catch(e){stop();status.textContent="재생하지 못했습니다: "+e.message;qa.error=String(e)}
}
startButton.addEventListener("click",run);
addEventListener("keydown",e=>{if(["Enter"," ","a","A"].includes(e.key)&&!e.repeat&&!startButton.disabled){e.preventDefault();run()}});
addEventListener("pagehide",()=>{stop(false);pauseMusic()});
Promise.all([
 Promise.all(["/title-approved.png","/title-start-mouth.svg","/title-native-lightning.png"].map(loadImage)),
 Promise.all(["/title-original-pika.wav","/title-start-electricity.wav","/title-current-continuous-electricity.mp4"].map(bytes))
]).then(([ims,data])=>{
 images=ims;raw=data;
 const sheet=document.createElement("canvas");sheet.width=32;sheet.height=160;
 const c=sheet.getContext("2d");c.drawImage(images[2],0,0);const pixels=c.getImageData(0,0,32,160);
 for(let i=0;i<pixels.data.length;i+=4)if(pixels.data[i]===0&&pixels.data[i+1]===0&&pixels.data[i+2]===0)pixels.data[i+3]=0;
 c.putImageData(pixels,0,0);images[2]=sheet;validateMouth();
 startButton.textContent="START";startButton.disabled=false;status.textContent="소리를 켜고 START를 눌러 주세요.";
}).catch(e=>{status.textContent="준비하지 못했습니다: "+e.message;qa.error=String(e)});
</script></html>'''
if __name__=="__main__":main()
