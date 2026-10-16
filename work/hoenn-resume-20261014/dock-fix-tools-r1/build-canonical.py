from pathlib import Path
import subprocess,json,hashlib
r=Path('/workspaces/pokefirered');o=r/'work/hoenn-resume-20261014/dock-fix-tools-r1'
f=(o/'canonical-build.log').open('w')
a=subprocess.run(['make','leafgreen','-j4'],cwd=r,stdout=f,stderr=subprocess.STDOUT).returncode
b=subprocess.run(['make','GAME_VERSION=LEAFGREEN','syms'],cwd=r,stdout=f,stderr=subprocess.STDOUT).returncode if a==0 else None
d={'make_leafgreen_returncode':a,'syms_returncode':b,'ROM_sha256':hashlib.sha256((r/'pokemonthyl.gba').read_bytes()).hexdigest(),'ELF_sha256':hashlib.sha256((r/'pokemonthyl.elf').read_bytes()).hexdigest()}
(o/'canonical-build-result.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
