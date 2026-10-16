from pathlib import Path
import subprocess,json,time,hashlib,shutil
r=Path('/workspaces/pokefirered');out=r/'work/regression-oct12/repair-build-final';out.mkdir(parents=True,exist_ok=True)
log=(out/'make.log').open('w')
args=['make','-j2','rom','GAME_VERSION=LEAFGREEN','GAME_REVISION=0','BUILD_NAME=blackthornlgqa','MODERN=0','COMPARE=0']
start=time.time()
rc=subprocess.call(args,cwd=r,stdout=log,stderr=subprocess.STDOUT)
if rc==0:
 rc=subprocess.call(['make','syms',*args[3:]],cwd=r,stdout=log,stderr=subprocess.STDOUT)
log.close()
art={str(p):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [r/('pokeblackthornlgqa'+s) for s in ['.gba','.elf','.sym','.map']] if p.exists()}
text=(out/'make.log').read_text(errors='replace')
res={'exit_code':rc,'seconds':time.time()-start,'warnings':[l for l in text.splitlines() if 'warning:' in l.lower()],'artifacts':art,'main_rom_sha256':hashlib.sha256((r/'pokemonthyl.gba').read_bytes()).hexdigest(),'source_repairs':'Misty v4 invitation, MtMortar General pairing, named Professor Elm and research report','promoted':False}
(out/'result.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res),flush=True)
