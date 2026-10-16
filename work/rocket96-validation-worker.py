from pathlib import Path
from datetime import datetime,timezone
import subprocess,hashlib,json,sys
r=Path('/workspaces/pokefirered');stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=r/'work'/('rocket96-validation-'+stamp);out.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
saves={str(p.relative_to(r)):sha(p) for p in (r/'saves').glob('*.sav')}
main={n:sha(r/n) for n in ['pokemonthyl.gba','pokemonthyl.elf','pokemonthyl.sym'] if (r/n).exists()}
steps=[];report={'output':str(out),'steps':steps,'main_before':main,'saves_before':saves,'all_pass':False,'user_device_tested':False}
(r/'work/rocket96-validation-latest.json').write_text(json.dumps({'result':str(out/'result.json')}));(out/'result.json').write_text(json.dumps(report,indent=2))
cmds=[('assets-preflight',['python3','work/rocket96-stage/work/rocket96_assets_setup.py','--repo','.','--stage','work/rocket96-stage','--source','outputs/rocket-art-v10-96-preview/jessie-james-v10-96.png']),('assets-install',['python3','work/rocket96-stage/work/rocket96_assets_setup.py','--repo','.','--stage','work/rocket96-stage','--source','outputs/rocket-art-v10-96-preview/jessie-james-v10-96.png','--write']),('review-build',['make','-f','work/rocket96-review.mk','GAME_VERSION=LEAFGREEN','BUILD_NAME=rocket96qa','ROCKET_TRAINER_HIRES=1','-W','src/rocket_trainer_portrait.c','-j2','rom','syms']),('native-intro-qa',['python3','tools/qa/rocket96_intro_check.py','--rom','pokerocket96qa.gba','--out',str(r/'outputs'/('rocket96-game-intro-qa-'+stamp))])]
for label,cmd in cmds:
 log=out/(label+'.log');print('START',label,flush=True)
 with log.open('w') as f:x=subprocess.run(cmd,cwd=r,stdout=f,stderr=subprocess.STDOUT)
 steps.append({'name':label,'exit':x.returncode,'log':str(log)})
 (out/'result.json').write_text(json.dumps(report,indent=2));print('END',label,x.returncode,flush=True)
 if x.returncode:break
report['main_after']={n:sha(r/n) for n in main};report['main_preserved']=report['main_after']==main
report['saves_after']={n:sha(r/n) for n in saves};report['original_saves_preserved']=report['saves_after']==saves
report['all_pass']=len(steps)==len(cmds) and all(x['exit']==0 for x in steps) and report['main_preserved'] and report['original_saves_preserved'];report['finished']=datetime.now(timezone.utc).isoformat()
(out/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
