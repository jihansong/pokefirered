from pathlib import Path
import subprocess,json,hashlib
r=Path('/workspaces/pokefirered');w=r/'work/save-inventory-pp-20261013';cmd=['make','GAME_VERSION=LEAFGREEN','MODERN=0','ROM=work/save-inventory-pp-20261013/candidate/pokemonthyl.gba','-j2']
with (w/'build-v2.log').open('w') as log:p=subprocess.run(cmd,cwd=r,stdout=log,stderr=subprocess.STDOUT)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out={'command':cmd,'exit_code':p.returncode,'main_ROM_unchanged':sha(r/'pokemonthyl.gba')==sha(w/'before/pokemonthyl.gba'),'candidate_ROM_sha256':sha(w/'candidate/pokemonthyl.gba') if (w/'candidate/pokemonthyl.gba').exists() else None,'log_tail':(w/'build-v2.log').read_text()[-6000:]}
(w/'build-result-v2.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
