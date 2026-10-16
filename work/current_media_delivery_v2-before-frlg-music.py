from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import mimetypes,re
ROOT=Path('/workspaces/pokefirered')
FILES={'opening-10s-preview.mp4':'outputs/opening-hooh-color-v5/opening-10s-preview.mp4','opening-10s-native.mp4':'outputs/opening-hooh-color-v5/opening-10s-native.mp4','title-current-review.gif':'outputs/title-approved-v3-effects-v1/title-current-review.gif','title-current-native.gif':'outputs/title-approved-v3-effects-v1/title-current-native.gif','title-current-continuous-electricity.mp4':'outputs/title-continuous-crackle-v3/title-current-continuous-electricity.mp4','continuous-electricity.wav':'outputs/title-continuous-crackle-v3/continuous-electricity.wav'}
STYLE='<style>body{background:#121925;color:#eef2f8;font:18px system-ui;max-width:1000px;margin:30px auto;padding:15px}a{color:#a9d7ff}video,img{width:100%;max-width:960px;image-rendering:pixelated}audio{width:100%}</style>'
PAGES={
'': '<h1>Thunder Yellow current previews</h1><p><a href="/opening.html">Opening v5</a></p><p><a href="/title.html">Approved title with continuous electricity</a></p>',
'opening.html':'<h1>Opening v5</h1><video controls playsinline preload="metadata" src="/opening-10s-preview.mp4"></video><p>10 seconds / approved v5 source</p>',
 'title.html':'<h1>Approved title + continuous electricity</h1><video controls loop playsinline preload="metadata" src="/title-current-continuous-electricity.mp4"></video><p>GIF is silent; the video carries the continuous sound.</p><img alt="Current approved GIF" src="/title-current-review.gif">'}
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
