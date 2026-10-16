from pathlib import Path
from datetime import datetime,timezone
import subprocess,hashlib,json,sys
r=Path('/workspaces/pokefirered');stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=r/'work'/('birch-bridge-validation-'+stamp);out.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
saves={str(p.relative_to(r)):sha(p) for p in (r/'saves').glob('*.sav')}
report={'directory':str(out),'steps':[],'original_save_sha256':saves,'all_pass':False,'user_device_tested':False}
(r/'work/birch-bridge-validation-latest.json').write_text(json.dumps({'result':str(out/'result.json')}));(out/'result.json').write_text(json.dumps(report,indent=2))
checks=[('build',['make','leafgreen','-j2']),('symbols',['make','GAME_VERSION=LEAFGREEN','syms']),('birch_runtime',['python3','-B','work/region-bridge/birch_johto_referral_qa.py','--output',str(out/'runtime'),'--run']),('map_integrity',['python3','tools/check_map_integrity.py']),('savecompat',['bash','tools/qa/savetest_all.sh'])]
for name,cmd in checks:
 log=out/(name+'.log');print('START',name,flush=True)
 with log.open('w') as f:x=subprocess.run(cmd,cwd=r,stdout=f,stderr=subprocess.STDOUT)
 report['steps'].append({'name':name,'exit_code':x.returncode,'log':str(log)});(out/'result.json').write_text(json.dumps(report,indent=2));print('END',name,x.returncode,flush=True)
 if x.returncode:break
report['original_saves_unchanged']=all((r/n).is_file() and sha(r/n)==h for n,h in saves.items());report['all_pass']=len(report['steps'])==len(checks) and all(x['exit_code']==0 for x in report['steps']) and report['original_saves_unchanged'];report['finished']=datetime.now(timezone.utc).isoformat()
(out/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
