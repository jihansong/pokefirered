from pathlib import Path
from fractions import Fraction
import hashlib,json,os,shutil,struct,subprocess,tempfile
from PIL import ImageFont
PINNED_COPYRIGHT={'graphics/credits/copyright.bin':'949bbce87679fbc75523b4e154685ba5c5502b4f29ee2b8c7cee4d439dfc5453','graphics/credits/copyright.png':'b3bb14718b28f023bd14d066152fc519b95163e51b863c1d468ad20c9761bda9'}
PINNED_COMMIT='037335f4c725d7c9aecdac87066f2002b4bd7e14'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require_files(paths):
 missing=[str(Path(p))for p in paths if not Path(p).is_file()]
 if missing:raise FileNotFoundError('Required existing inputs missing:\n'+'\n'.join(missing))
def repo_path(root,explicit=None):
 result=Path(explicit or os.environ.get('THUNDER_ENDING_REPO')or root).resolve();require_files(result/p for p in ['src/credits.c','src/strings.c','data/layouts/layouts.json']);return result
def gfx_path(root,explicit=None):
 value=explicit or os.environ.get('THUNDER_ENDING_GFX');candidates=[Path(value)]if value else[Path(root)/'work'/name/'official_gfx.py'for name in ['native-opening-v4','native-opening-v3','native-opening']]
 for p in candidates:
  if p.is_file():return p.resolve()
 raise FileNotFoundError('Existing official_gfx.py required; tried: '+', '.join(map(str,candidates)))
def fresh_output(path):
 path=Path(path).resolve()
 if path.exists():raise FileExistsError('Refusing to replace prior output: '+str(path))
 path.mkdir(parents=True);return path
def review_font(size,explicit=None):
 if explicit:require_files([explicit]);return ImageFont.truetype(str(explicit),size)
 for name in ['DejaVuSans.ttf','Arial.ttf']:
  try:return ImageFont.truetype(name,size)
  except OSError:pass
 try:return ImageFont.load_default(size=size)
 except TypeError:return ImageFont.load_default()
def source_manifest(repo,rels):
 repo=Path(repo);p=subprocess.run(['git','-C',str(repo),'rev-parse','HEAD'],capture_output=True,text=True)
 return dict(repo=str(repo),head=p.stdout.strip()if p.returncode==0 else None,head_is_not_working_tree_content_proof=True,sha256={r:sha(repo/r)for r in sorted(set(rels))},source_files_written=False)
def verify_copyright(repo):
 repo=Path(repo)
 for rel,digest in PINNED_COPYRIGHT.items():
  actual=sha(repo/rel)
  if actual!=digest:raise ValueError('Original copyright source hash mismatch: '+rel+' '+actual)
 entries=struct.unpack('<1024H',(repo/'graphics/credits/copyright.bin').read_bytes());assert {entries[y*32+x]for y in range(20)for x in range(30)}=={1}
 return dict(status='CURRENT_INPUTS_MATCH_PINNED_ORIGINAL',upstream_commit=PINNED_COMMIT,input_sha256=dict(PINNED_COPYRIGHT),visible_tilemap_unique_values=[1],runtime_timing_or_audio_verified=False)
def binary(name):
 override=os.environ.get(name.upper()+'_BINARY');found=shutil.which(override or name)
 if not found:raise FileNotFoundError('Installed '+name+' required; no download attempted.')
 return found
class VideoIO:
 @staticmethod
 def get_ffmpeg_exe():return binary('ffmpeg')
 @staticmethod
 def probe(path,count=False):
  cmd=[binary('ffprobe'),'-v','error','-select_streams','v:0']
  if count:cmd+=['-count_frames']
  cmd+=['-show_entries','stream=width,height,avg_frame_rate,duration,nb_read_frames','-of','json',str(path)]
  result=subprocess.run(cmd,capture_output=True,text=True,check=True);streams=json.loads(result.stdout).get('streams',[])
  if len(streams)!=1:raise ValueError('Expected one selected video stream: '+str(path))
  return streams[0]
 @classmethod
 def count_frames_and_secs(cls,path):
  meta=cls.probe(path,True);count=int(meta['nb_read_frames']);fps=Fraction(meta['avg_frame_rate']);assert fps>0;return count,float(count/fps)
 @classmethod
 def read_frames(cls,path,pix_fmt='rgb24'):
  if pix_fmt!='rgb24':raise ValueError('Only explicit RGB24 decoding supported')
  meta=cls.probe(path);width,height=int(meta['width']),int(meta['height']);frame_bytes=width*height*3
  with tempfile.TemporaryFile()as err:
   proc=subprocess.Popen([binary('ffmpeg'),'-v','error','-i',str(path),'-map','0:v:0','-vsync','0','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=err)
   try:
    yield dict(size=(width,height),fps=float(Fraction(meta['avg_frame_rate'])))
    while True:
     raw=bytearray()
     while len(raw)<frame_bytes:
      part=proc.stdout.read(frame_bytes-len(raw))
      if not part:break
      raw.extend(part)
     if not raw:break
     if len(raw)!=frame_bytes:raise RuntimeError('Truncated decoded RGB frame')
     yield bytes(raw)
    rc=proc.wait();err.seek(0);errors=err.read().decode('utf-8','replace')
    if rc or errors.strip():raise RuntimeError('FFmpeg decode failed: '+errors)
   finally:
    proc.stdout.close()
    if proc.poll()is None:
     proc.terminate()
     try:proc.wait(timeout=5)
     except subprocess.TimeoutExpired:proc.kill();proc.wait()
imageio_ffmpeg=VideoIO
def pixels(im):return im.get_flattened_data()if hasattr(im,'get_flattened_data')else im.getdata()
