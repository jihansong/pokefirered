from pathlib import Path
import subprocess,json,hashlib,datetime,shutil
root=Path('/workspaces/pokefirered');out=root/'work/johto-lab-20261004-v1';out.mkdir(exist_ok=False)
def hashes():return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'saves').glob('*.sav')}
before=hashes();backup=root/('.qa-lab-build-before-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));backup.mkdir(exist_ok=False)
for name in ('pokemonthyl.gba','pokemonthyl.elf','pokemonthyl.sym'):
 p=root/name
 if p.exists():shutil.copy2(p,backup/name)
checks=[('cases',['python3','tools/johto/build_lab_cases.py']),('build',['make','leafgreen','-j2']),('symbols',['make','GAME_VERSION=LEAFGREEN','syms']),('lab',['python3','tools/qa/eventcheck.py','tools/qa/cases/johto_lab.jsonl','--shots','work/johto-lab-20261004-v1/shots']),('airport_regression',['python3','tools/qa/eventcheck.py','work/johto-flight-retry-20261004/cases.jsonl','--shots','work/johto-lab-20261004-v1/flight-shots']),('savecompat',['bash','tools/qa/savetest_all.sh'])]
results={}
for label,cmd in checks:
 print('START',label,flush=True)
 with (out/(label+'.log')).open('w') as f:p=subprocess.run(cmd,cwd=root,stdout=f,stderr=subprocess.STDOUT)
 results[label]={'exit_code':p.returncode,'log':str((out/(label+'.log')).relative_to(root))};print('DONE',label,p.returncode,flush=True)
 if p.returncode and label in ('cases','build','symbols'):break
report={'results':results,'original_saves_preserved':hashes()==before,'save_sha256_before':before,'backup':str(backup.relative_to(root)),'actual_delta_test':False,'actual_save_reload_test':False}
(out/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
p=root/'work/animation-recreation-status.json'
s=json.loads(p.read_text());s.setdefault('latest_verified_results',{})['johto_lab_mini']=report;s['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
