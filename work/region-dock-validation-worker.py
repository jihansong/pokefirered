from pathlib import Path
from datetime import datetime,timezone
import subprocess,json,hashlib,shutil
r=Path('/workspaces/pokefirered');out=r/'work'/('region-dock-validation-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));out.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
saves={str(p.relative_to(r)):sha(p) for p in (r/'saves').glob('*.sav')}
backup=out/'build-before';backup.mkdir()
for name in ['pokemonthyl.gba','pokemonthyl.elf','pokemonthyl.sym']:shutil.copy2(r/name,backup/name)
report={'started_at':datetime.now(timezone.utc).isoformat(),'out':str(out),'steps':[],'original_save_sha256':saves,'user_device_tested':False}
checks=[('build',['make','leafgreen','-j2']),('symbols',['make','GAME_VERSION=LEAFGREEN','syms']),('johto_cases',['python3','-B','work/region-bridge/make_johto_referral_qa.py','--lab-cases','tools/qa/cases/johto_lab.jsonl','--output',str(out/'johto-referral.jsonl')]),('johto_runtime',['python3','-B','tools/qa/eventcheck.py',str(out/'johto-referral.jsonl'),'--rom','pokemonthyl.gba','--shots',str(out/'johto-shots')]),('dock_runtime',['python3','-B','tools/qa/dock_mew_check.py']),('airport_regression',['python3','-B','tools/qa/eventcheck.py','work/johto-flight-retry-20261004/cases.jsonl','--rom','pokemonthyl.gba','--shots',str(out/'flight-shots')]),('map_integrity',['python3','tools/check_map_integrity.py']),('savecompat',['bash','tools/qa/savetest_all.sh'])]
try:
 for name,cmd in checks:
  print('CHECK_START',name,flush=True)
  with (out/(name+'.log')).open('w') as log:rc=subprocess.run(cmd,cwd=r,stdout=log,stderr=subprocess.STDOUT).returncode
  report['steps'].append({'name':name,'exit_code':rc,'log':str(out/(name+'.log'))});print('CHECK_DONE',name,rc,flush=True)
  (out/'result.json').write_text(json.dumps(report,indent=2))
  if rc and name in ['build','symbols']:break
finally:
 report['original_saves_unchanged']=all(sha(r/p)==h for p,h in saves.items());report['finished_at']=datetime.now(timezone.utc).isoformat();report['all_pass']=len(report['steps'])==len(checks) and all(s['exit_code']==0 for s in report['steps']) and report['original_saves_unchanged'];(out/'result.json').write_text(json.dumps(report,indent=2));(r/'work/region-dock-validation-latest.json').write_text(json.dumps({'directory':str(out),'all_pass':report['all_pass']}));print(json.dumps(report),flush=True)
