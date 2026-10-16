from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import mimetypes,re
ROOT=Path('/workspaces/pokefirered')
FILES={'opening-10s-preview.mp4': 'outputs/opening-frlg-music-v6/opening-hooh-v5-frlg-music.mp4', 'opening-10s-native.mp4': 'outputs/opening-frlg-music-v6/opening-hooh-v5-native-frlg-music.mp4', 'title-current-review.gif': 'outputs/title-approved-v3-effects-v1/title-current-review.gif', 'title-current-native.gif': 'outputs/title-approved-v3-effects-v1/title-current-native.gif', 'title-current-continuous-electricity.mp4': 'outputs/title-frlg-music-v4/title-frlg-music-crackle.mp4', 'continuous-electricity.wav': 'outputs/title-continuous-crackle-v3/continuous-electricity.wav', 'title-approved.png': 'outputs/title-font-python-v3/title-font-candidate-240x160.png', 'title-start-mouth.svg': 'outputs/title-start-review-v1/start-mouth.svg', 'title-native-lightning.png': 'graphics/battle_anims/sprites/lightning.png', 'title-original-pika.wav': 'reference/audio/pikachu-gF1FJRM8Wck/publisher-original/pokemon-video-game-pikachu-voice-sound-effect.wav', 'title-start-electricity.wav': 'outputs/title-continuous-crackle-v3/continuous-electricity.wav', 'opening-full-frlg-preview.mp4': 'outputs/opening-full-frlg-v7/opening-full-frlg-preview.mp4', 'opening-full-frlg-native.mp4': 'outputs/opening-full-frlg-v7/opening-full-frlg-native.mp4', 'title.html': 'outputs/title-start-review-v1/index.html'}
STYLE='<style>body{background:#121925;color:#eef2f8;font:18px system-ui;max-width:1000px;margin:30px auto;padding:15px}a{color:#a9d7ff}video,img{width:100%;max-width:960px;image-rendering:pixelated}audio{width:100%}</style>'
PAGES={'': '<h1>Thunder Yellow</h1><p><a href="/opening.html">Opening</a></p><p><a href="/title.html">Title START preview</a></p>', 'opening.html': '<h1>Thunder Yellow Opening</h1><video controls playsinline preload="metadata" src="/opening-full-frlg-preview.mp4"></video><p>12.53 seconds / original FR/LG intro music / existing artwork</p>'}
class Handler(BaseHTTPRequestHandler):
 def do_HEAD(self):self.serve(False)
 def do_GET(self):self.serve(True)
 def serve(self,send):
  key=self.path.split('?')[0].lstrip('/')
  if key in PAGES:
   body=('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Thunder Yellow current previews</title>'+STYLE+PAGES[key]).encode()
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers()
   if send:self.wfile.write(body)
   return
  if key not in FILES or not (ROOT/FILES[key]).is_file():self.send_error(404);return
  p=ROOT/FILES[key];size=p.stat().st_size;start=0;end=size-1;partial=False
  rh=self.headers.get('Range')
  if rh:
   m=re.fullmatch(r'bytes=(\d*)-(\d*)',rh)
   if not m:self.send_error(416);return
   a,b=m.groups()
   if a:start=int(a);end=min(int(b),end) if b else end
   elif b:start=max(0,size-int(b))
   else:self.send_error(416);return
   if start>end or start>=size:self.send_error(416);return
   partial=True
  self.send_response(206 if partial else 200)
  self.send_header('Content-Type',mimetypes.guess_type(key)[0] or 'application/octet-stream')
  self.send_header('Content-Disposition','inline; filename="'+key+'"')
  self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1));self.send_header('Cache-Control','no-store')
  if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  if send:
   with p.open('rb') as f:
    f.seek(start);left=end-start+1
    while left:
     chunk=f.read(min(65536,left));self.wfile.write(chunk);left-=len(chunk)
ThreadingHTTPServer(('127.0.0.1',31582),Handler).serve_forever()
