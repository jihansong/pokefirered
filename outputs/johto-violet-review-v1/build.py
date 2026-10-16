from pathlib import Path
import subprocess,json,hashlib,shutil
r=Path('/workspaces/pokefirered');d=Path('/workspaces/pokefirered/outputs/johto-violet-review-v1');
with (d/'build.log').open('w') as f:p=subprocess.run(['make','GAME_VERSION=LEAFGREEN','BUILD_NAME=titlev8qa','-j2','rom','syms'],cwd=r,stdout=f,stderr=subprocess.STDOUT)
v={'exit':p.returncode}
if p.returncode==0:
 for ext in ['gba','elf','sym','map']:shutil.copy2(r/('poketitlev8qa.'+ext),d/('violet-candidate.'+ext))
 v['rom_sha256']=hashlib.sha256((d/'violet-candidate.gba').read_bytes()).hexdigest()
(d/'build-result.json').write_text(json.dumps(v));print(v,flush=True)
