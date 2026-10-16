"""Silent ten-second first-scene excerpt; not a full Johto ending."""
from pathlib import Path
import argparse,hashlib,importlib,json,os,struct,subprocess,sys
from PIL import Image
FPS_ARG='262144/4389';FPS=262144/4389;FRAMES=597;MOVE_START=45;MOVE_END=441;MAP='NewBarkTown'
TILES=[(3,12),(4,12),(11,12),(11,10),(11,9)];RED_START_DISTANCE=16;RED_END_DISTANCE=176
def sha(data):return hashlib.sha256(data).hexdigest()
def pixel(tile):return tile[0]*16+8,tile[1]*16+16
POINTS=[pixel(t)for t in TILES]
def at_distance(distance):
 distance=max(0,min(RED_END_DISTANCE,distance))
 for(ax,ay),(bx,by)in zip(POINTS,POINTS[1:]):
  length=abs(bx-ax)+abs(by-ay)
  if distance<=length:
   r=distance/length;return ax+(bx-ax)*r,ay+(by-ay)*r,('east'if bx>ax else'west')if bx!=ax else('south'if by>ay else'north')
  distance-=length
 return *POINTS[-1],'north'
def state(n):
 assert 0<=n<FRAMES;t=min(1,max(0,(n-MOVE_START)/(MOVE_END-MOVE_START)));d=RED_START_DISTANCE+(RED_END_DISTANCE-RED_START_DISTANCE)*t
 return at_distance(d),at_distance(d-16),MOVE_START<n<MOVE_END
def walk_tiles():
 result=[]
 for(ax,ay),(bx,by)in zip(TILES,TILES[1:]):
  assert ax==bx or ay==by;dx=(bx>ax)-(bx<ax);dy=(by>ay)-(by<ay)
  for k in range(abs(bx-ax)+abs(by-ay)+1):
   cell=ax+dx*k,ay+dy*k
   if cell not in result:result.append(cell)
 return result
def validate_map(repo,assets):
 assert MAP in assets.LAYOUTS,'Actual NewBarkTown missing';row=assets.LAYOUTS[MAP];assert(row['width'],row['height'])==(36,28);assert row['blockdata_filepath']=='data/layouts/NewBarkTown/map.bin'
 raw=assets.source(row['blockdata_filepath']).read_bytes();assert len(raw)==2016;assert sha(raw)=='af15a84de2d5ca1f51c9aa5f8fd493167bc9ce8dd2b2057c03ed387278beeae3';blocks=struct.unpack('<1008H',raw)
 for x,y in walk_tiles():assert(blocks[y*36+x]>>10)&3==0,('Blocked staging path',x,y)
 m=json.loads(assets.source('data/maps/NewBarkTown/map.json').read_text());assert m['layout']=='LAYOUT_NEW_BARK_TOWN'
 occupied={(int(o['x']),int(o['y']))for o in m.get('object_events',[])};assert not occupied.intersection(walk_tiles())
 return row,sha(raw)
def make_renderer(assets):
 bg=assets.map_image(MAP);assert bg.size==(576,448)
 def frame(n):
  red,pika,moving=state(n);cx=min(bg.width-240,max(0,round(red[0]-120)));cy=min(bg.height-160,max(0,round(red[1]-96)));im=bg.crop((cx,cy,cx+240,cy+160)).convert('RGBA')
  for who,pos in sorted([('red',red),('pika',pika)],key=lambda a:a[1][1]):assets.foot(im,assets.field(who,n-MOVE_START if moving else 0,pos[2],moving),pos[0]-cx,pos[1]-cy)
  return im.convert('RGB')
 return frame
def verify_motion(frame):
 points=[0,45,46,100,200,320,440,441,596];hashes={str(n):sha(frame(n).tobytes())for n in points};assert len({hashes[str(n)]for n in [46,100,200,320,440]})==5
 for n in range(FRAMES):
  red,pika,_=state(n);assert 0<=red[0]<576 and 0<=red[1]<=448 and 0<=pika[0]<576 and 0<=pika[1]<=448
  if n:
   previous=state(n-1);assert sum(abs(red[i]-previous[0][i])for i in(0,1))<1;assert sum(abs(pika[i]-previous[1][i])for i in(0,1))<1
 return hashes
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path.cwd());ap.add_argument('--bundle',type=Path,default=Path.cwd()/'work/ending-portable-v1');ap.add_argument('--gfx',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--stills-only',action='store_true');a=ap.parse_args()
 repo=a.repo.resolve();out=a.output.resolve();os.environ['THUNDER_ENDING_REPO']=str(repo)
 if a.gfx:os.environ['THUNDER_ENDING_GFX']=str(a.gfx.resolve())
 sys.path.insert(0,str(a.bundle.resolve()));runtime=importlib.import_module('runtime');assets=importlib.import_module('native_assets_portable');assert assets.REPO.resolve()==repo
 row,map_sha=validate_map(repo,assets);frame=make_renderer(assets);keyframes=verify_motion(frame)
 for n in range(FRAMES):frame(n)
 sources=dict(assets.SOURCES);assert all(runtime.sha(repo/p)==h for p,h in sources.items())
 if not a.stills_only:runtime.binary('ffmpeg');runtime.binary('ffprobe')
 runtime.fresh_output(out)
 for n in[0,100,200,320,441,596]:
  im=frame(n);im.save(out/f'new-bark-{n:03d}-native.png');im.resize((960,640),Image.Resampling.NEAREST).save(out/f'new-bark-{n:03d}-4x.png')
 report=dict(status='first_scene_stills_only'if a.stills_only else'first_scene_video',region='johto',story_beat='new_bark',story_beats_total=10,complete_johto_ending=False,ROM_integrated=False,audio=False,new_music=False,new_art_authored=False,source_map=MAP,source_map_sha256=map_sha,source_sha256=sources,frames=FRAMES,fps=FPS_ARG,seconds=FRAMES/FPS,red_route_tiles=TILES[1:],pikachu_trailing_distance_pixels=16,native_dimensions=[240,160],sample_frame_sha256=keyframes,limits=['Only first of ten journey beats.','Game collision execution not claimed.','Existing field cels reused.','Staff roll, remaining scenes and completion trigger pending.'])
 if not a.stills_only:
  native=out/'johto-new-bark-native.mp4';expected=[];proc=subprocess.Popen([runtime.binary('ffmpeg'),'-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','240x160','-r',FPS_ARG,'-i','pipe:0','-an','-c:v','libx264rgb','-crf','0','-preset','veryfast','-movflags','+faststart',str(native)],stdin=subprocess.PIPE)
  try:
   for n in range(FRAMES):raw=frame(n).tobytes();expected.append(sha(raw));proc.stdin.write(raw)
   proc.stdin.close();assert proc.wait()==0,'Native encoding failed'
  except BaseException:
   if proc.poll()is None:proc.terminate();proc.wait()
   raise
  decoded=runtime.imageio_ffmpeg.read_frames(native,pix_fmt='rgb24');assert next(decoded)['size']==(240,160);assert[sha(raw)for raw in decoded]==expected
  preview=out/'johto-new-bark-preview.mp4';subprocess.run([runtime.binary('ffmpeg'),'-hide_banner','-loglevel','error','-n','-i',str(native),'-vf','scale=960:640:flags=neighbor','-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(preview)],check=True)
  report.update(native_sha256=runtime.sha(native),preview_sha256=runtime.sha(preview),decoded_frames=FRAMES,decoded_frame_equality='PASS');(out/'frame-hashes.json').write_text(json.dumps(expected,indent=2)+'\n')
 assert all(runtime.sha(repo/p)==h for p,h in sources.items());(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
