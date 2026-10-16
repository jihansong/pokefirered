from pathlib import Path
import subprocess,shutil,json
w=Path('work/heartbeat-20261012T1131')
args=['BUILD_NAME=blackthornlgqa','MODERN=0','COMPARE=0']
d={'leafgreen':subprocess.call(['make','leafgreen','-j2']+args)}
if d['leafgreen']==0:
 d['syms']=subprocess.call(['make','GAME_VERSION=LEAFGREEN','syms']+args)
 if d['syms']==0:
  out=w/'canonical-candidate';out.mkdir()
  for ext in ['gba','elf','sym','map']:shutil.copy2('pokeblackthornlgqa.'+ext,out/('pokemonthyl.'+ext))
(w/'canonical-build-result.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d),flush=True)
