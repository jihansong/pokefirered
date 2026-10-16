from pathlib import Path
import subprocess,os,json,hashlib
r=Path('/workspaces/pokefirered');w=r/'work/misty-followup-20261014'
with (w/'build-misty-devon-v2.log').open('wb') as f:
 subprocess.run(['make','leafgreen','-j'+str(os.cpu_count())],cwd=r,stdout=f,stderr=subprocess.STDOUT,check=True)
 subprocess.run(['make','GAME_VERSION=LEAFGREEN','syms'],cwd=r,stdout=f,stderr=subprocess.STDOUT,check=True)
j={n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in ['pokemonthyl.gba','pokemonthyl.elf']}
j['build_pass']=True
(w/'build-misty-devon-v2-result.json').write_text(json.dumps(j,indent=2))
