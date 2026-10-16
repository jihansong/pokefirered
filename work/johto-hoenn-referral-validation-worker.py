from pathlib import Path
import datetime,json,subprocess,hashlib,shutil
R=Path('/workspaces/pokefirered')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=R/('work/johto-hoenn-referral-validation-'+stamp);out.mkdir(exist_ok=False)
backup=out/'build-before';backup.mkdir()
for rel in ('pokemonthyl.gba','pokemonthyl.elf','pokemonthyl.sym'):
 if (R/rel).exists():shutil.copy2(R/rel,backup/rel)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
saves={str(p.relative_to(R)):sha(p) for p in (R/'saves').glob('*.sav')}
old=json.loads((R/'work/harbor-bridge-runtime-current.json').read_text())
oldcases=str(Path(old['directory'])/'cases.jsonl')
checks=[('build',['make','leafgreen','-j2']),('symbols',['make','GAME_VERSION=LEAFGREEN','syms']),('referral_runtime',['python3','-B','work/region-bridge/harbor_johto_referral_qa_v2.py','--harbor-cases',oldcases,'--output',str(out/'referral-cases.jsonl'),'--run']),('dock_runtime',['python3','-B','tools/qa/dock_mew_check.py']),('map_integrity',['python3','tools/check_map_integrity.py']),('savecompat',['bash','tools/qa/savetest_all.sh'])]
report={'directory':str(out),'steps':[],'original_save_sha256':saves,'user_device_tested':False}
try:
 for name,cmd in checks:
  log=out/(name+'.log');print('CHECK_START',name,flush=True)
  with log.open('wb') as f:code=subprocess.call(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  report['steps'].append({'name':name,'exit_code':code,'log':str(log)});(out/'result.json').write_text(json.dumps(report,indent=2))
  print('CHECK_DONE',name,code,flush=True)
  if code and name in ('build','symbols'):break
finally:
 report['original_saves_unchanged']=all((R/rel).is_file() and sha(R/rel)==h for rel,h in saves.items())
 report['all_pass']=len(report['steps'])==len(checks) and all(s['exit_code']==0 for s in report['steps']) and report['original_saves_unchanged']
 report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (out/'result.json').write_text(json.dumps(report,indent=2));(R/'work/johto-hoenn-referral-validation-latest.json').write_text(json.dumps({'directory':str(out),'all_pass':report['all_pass']})+chr(10))
 print(json.dumps(report),flush=True)
