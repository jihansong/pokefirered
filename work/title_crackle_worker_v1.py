from pathlib import Path
import urllib.request,subprocess,sys,hashlib
r=Path('/workspaces/pokefirered')
s=r/'reference/audio/cc0-electricity-faxcorp';s.mkdir(parents=True,exist_ok=True)
p=s/'crackleelectricityloop.wav'
if not p.exists():
 data=urllib.request.urlopen('https://opengameart.org/sites/default/files/crackleelectricityloop.wav',timeout=20).read()
 assert data[:4]==b'RIFF' and data[8:12]==b'WAVE'
 p.write_bytes(data)
print('CC0_SOURCE',p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
cmd=[sys.executable,'work/title_continuous_crackle.py','--wav',str(p),'--video','outputs/title-approved-v3-effects-v1/title-current-with-sfx.mp4','--png','outputs/title-font-python-v3/title-font-candidate-240x160.png','--gif_dir','outputs/title-approved-v3-effects-v1','--out','outputs/title-continuous-crackle-v1']
subprocess.run(cmd,cwd=r,check=True)
