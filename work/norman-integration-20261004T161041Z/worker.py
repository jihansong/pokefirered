from pathlib import Path
import subprocess,sys,json,hashlib
o=Path('work/norman-integration-20261004T161041Z' )
steps=[]
for name,args in [('apply',[sys.executable,'-B','work/norman_apply_v2.py','--flags-sha','03f77024541e910acdcca743a18a3be1757a4330846a88357b4010e30bf75157','--write']),('build',['make','leafgreen','-j2']),('syms',['make','GAME_VERSION=LEAFGREEN','syms']),('map',[sys.executable,'-B','tools/check_map_integrity.py']),('strict',[sys.executable,'-B','tools/qa/norman_strict_check.py','--root',str(Path.cwd())])]:
 with (o/(name+'.log')).open('w')as f:q=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
 steps.append({'name':name,'rc':q.returncode});print(json.dumps(steps[-1]),flush=True)
 if q.returncode:break
r={'steps':steps,'rom_sha256':hashlib.sha256(Path('pokemonthyl.gba').read_bytes()).hexdigest(),'sym_sha256':hashlib.sha256(Path('pokemonthyl.sym').read_bytes()).hexdigest(),'all_pass':len(steps)==5 and all(x['rc']==0 for x in steps),'full_regions_complete':False}
(o/'result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
