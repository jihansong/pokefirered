from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import mimetypes,re
ROOT=Path('/workspaces/pokefirered')
FILES={'opening-10s-preview.mp4': 'outputs/opening-frlg-music-v6/opening-hooh-v5-frlg-music.mp4', 'opening-10s-native.mp4': 'outputs/opening-frlg-music-v6/opening-hooh-v5-native-frlg-music.mp4', 'title-current-review.gif': 'outputs/title-approved-v3-effects-v1/title-current-review.gif', 'title-current-native.gif': 'outputs/title-approved-v3-effects-v1/title-current-native.gif', 'title-current-continuous-electricity.mp4': 'outputs/title-frlg-music-v4/title-frlg-music-crackle.mp4', 'continuous-electricity.wav': 'outputs/title-continuous-crackle-v3/continuous-electricity.wav', 'title-approved.png': 'outputs/title-font-python-v3/title-font-candidate-240x160.png', 'title-start-mouth.svg': 'outputs/title-start-review-v3/start-mouth.svg', 'title-native-lightning.png': 'graphics/battle_anims/sprites/lightning.png', 'title-original-pika.wav': 'reference/audio/pikachu-gF1FJRM8Wck/publisher-original/pokemon-video-game-pikachu-voice-sound-effect.wav', 'title-start-electricity.wav': 'outputs/title-continuous-crackle-v3/continuous-electricity.wav', 'opening-full-frlg-preview.mp4': 'outputs/opening-full-frlg-v7/opening-full-frlg-preview.mp4', 'opening-full-frlg-native.mp4': 'outputs/opening-full-frlg-v7/opening-full-frlg-native.mp4', 'title.html': 'outputs/title-start-review-v3/index.html', 'rocket-v9-native.png': 'outputs/rocket-art-v9/jessie-james-v9-64.png', 'rocket-v9-review.png': 'outputs/rocket-art-v9/jessie-james-v9-8x.png', 'rocket-v10-native.png': 'outputs/rocket-art-v10-96-preview/jessie-james-v10-96.png', 'rocket-v10-review.png': 'outputs/rocket-art-v10-96-preview/jessie-james-v10-6x.png'}
STYLE='<style>body{background:#121925;color:#eef2f8;font:18px system-ui;max-width:1000px;margin:30px auto;padding:15px}a{color:#a9d7ff}video,img{width:100%;max-width:960px;image-rendering:pixelated}audio{width:100%}</style>'
PAGES={'': '<h1>Thunder Yellow</h1><p><a href="/opening.html">Opening</a></p><p><a href="/title.html">Title START preview</a></p><p><a href="/rocket.html">로이·로사 현재 작업본</a></p>', 'opening.html': '<h1>Thunder Yellow Opening</h1><video controls playsinline preload="metadata" src="/opening-full-frlg-preview.mp4"></video><p>12.53 seconds / original FR/LG intro music / existing artwork</p>', 'rocket.html': '<h1>로이·로사 현재 작업본</h1><p>승인된 v4 비율 유지. 최신 96×96 검토본과 64×64 정리본입니다.</p><div class="versions"><section><h2>96×96 · 최신 검토본</h2><img src="/rocket-v10-review.png" alt="로이·로사 최신 96픽셀 검토본" style="width:384px;max-width:100%"><p>기존 v4 원화에서 제작한 15색 후보. 64픽셀을 늘린 그림이 아닙니다.</p></section><section><h2>64×64 · 정리본</h2><img src="/rocket-v9-review.png" alt="로이·로사 64픽셀 정리본" style="width:384px;max-width:100%"><p>머리카락·장갑 26픽셀 정리. 눈과 손의 세부 표현은 추가 개선이 필요합니다.</p></section></div><p>96픽셀 검토본의 기본 게임 적용은 아직 완료되지 않았습니다.</p><style>.versions{display:flex;gap:32px;flex-wrap:wrap}.versions section{flex:1;min-width:300px}h2{font-size:21px}</style>'}
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
