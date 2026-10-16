from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import mimetypes
ROOT=Path('/workspaces/pokefirered')
FILES={'opening-10s-preview.mp4':'outputs/opening-hooh-color-v5/opening-10s-preview.mp4','opening-10s-native.mp4':'outputs/opening-hooh-color-v5/opening-10s-native.mp4','title-font-candidate-4x.png':'outputs/title-font-python-v3/title-font-candidate-4x.png','title-font-candidate-240x160.png':'outputs/title-font-python-v3/title-font-candidate-240x160.png','title-current-review.gif':'outputs/title-approved-v3-effects-v1/title-current-review.gif','title-current-native.gif':'outputs/title-approved-v3-effects-v1/title-current-native.gif','title-current-with-sfx.mp4':'outputs/title-approved-v3-effects-v1/title-current-with-sfx.mp4'}
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  key=self.path.split('?')[0].lstrip('/')
  if not key:
   body=('<!doctype html><meta charset=utf-8><title>Thunder Yellow current media</title><h1>Thunder Yellow current media</h1>'+''.join('<p><a download href="/'+k+'">'+k+'</a></p>' for k,v in FILES.items() if (ROOT/v).is_file())).encode()
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
  if key not in FILES or not (ROOT/FILES[key]).is_file():self.send_error(404);return
  p=ROOT/FILES[key];body=p.read_bytes()
  self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(key)[0] or 'application/octet-stream');self.send_header('Content-Disposition','attachment; filename="'+key+'"');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
ThreadingHTTPServer(('127.0.0.1',31582),Handler).serve_forever()
