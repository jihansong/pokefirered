from pathlib import Path
import subprocess,json,shutil
w=Path('work/heartbeat-20261012T1131')
args=['GAME_VERSION=LEAFGREEN','GAME_REVISION=0','BUILD_NAME=blackthornlgqa','MODERN=0','COMPARE=0']
d={'rom':subprocess.call(['make','-j2','rom']+args)}
if d['rom']==0:
 d['syms']=subprocess.call(['make','syms']+args)
 if d['syms']==0:
  p=w/'route114-onward-candidate';p.mkdir()
  for ext in ['gba','elf','sym','map']:shutil.copy2('pokeblackthornlgqa.'+ext,p/('pokemonthyl.'+ext))
(w/'route114-onward-build-result.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d),flush=True)
