from pathlib import Path
import subprocess,shutil,json,hashlib
p=Path('/workspaces/pokefirered');w=p/'work/regional-starters-20261013'
args=['BUILD_NAME=blackthornlgqa','MODERN=0','COMPARE=0']
d={'leafgreen':subprocess.call(['make','leafgreen','-j2']+args,cwd=p)}
if d['leafgreen']==0:
 d['syms']=subprocess.call(['make','GAME_VERSION=LEAFGREEN','syms']+args,cwd=p)
 if d['syms']==0:
  out=w/'candidate';out.mkdir()
  for ext in ['gba','elf','sym','map']:shutil.copy2(p/('pokeblackthornlgqa.'+ext),out/('pokemonthyl.'+ext))
  d['hashes']={ext:hashlib.sha256((out/('pokemonthyl.'+ext)).read_bytes()).hexdigest() for ext in ['gba','elf','sym','map']}
(w/'build-result.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d),flush=True)
