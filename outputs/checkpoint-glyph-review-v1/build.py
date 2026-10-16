from pathlib import Path
import subprocess,json,hashlib,shutil
r=Path('/workspaces/pokefirered');d=Path('/workspaces/pokefirered/outputs/checkpoint-glyph-review-v1');
with (d/'build.log').open('w') as f:q=subprocess.run(['make','-j2','BUILD_NAME=titlev8qa','GAME_VERSION=LEAFGREEN','rom','syms'],cwd=r,stdout=f,stderr=subprocess.STDOUT)
result={'exit':q.returncode}
if q.returncode==0:
 for ext in ['gba','elf','sym','map']:shutil.copy2(r/('poketitlev8qa.'+ext),d/('checkpoint-candidate.'+ext))
 result['rom_sha256']=hashlib.sha256((d/'checkpoint-candidate.gba').read_bytes()).hexdigest()
(d/'build-result.json').write_text(json.dumps(result));print(result,flush=True)
