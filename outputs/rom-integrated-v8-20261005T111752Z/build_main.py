from pathlib import Path
import subprocess,json,hashlib,sys
out=Path(sys.argv[1])
commands=[['make','leafgreen','-j2'],['make','GAME_VERSION=LEAFGREEN','syms']]
results=[]
for cmd in commands:
 q=subprocess.run(cmd);results.append({'command':cmd,'returncode':q.returncode})
 if q.returncode:break
p=Path('pokemonthyl.gba');(out/'build-result.json').write_text(json.dumps({'results':results,'rom_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size},indent=2));print('MAIN_BUILD_RESULT',results,hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
