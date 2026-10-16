from pathlib import Path
import sys,json,hashlib,subprocess,datetime,traceback
R=Path('/workspaces/pokefirered');stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=R/('work/winona-validation-'+stamp);out.mkdir();(R/'work/winona-validation-latest.txt').write_text(str(out)+'\n')
orig={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'saves').glob('*.sav')};results=[]
try:
 cmds=[('apply',[sys.executable,'work/region-bridge/winona_reward_apply.py']),('build',['make','leafgreen','-j2']),('syms',['make','GAME_VERSION=LEAFGREEN','syms']),('winona_strict',[sys.executable,'work/region-bridge/winona_strict_cases.py',str(out/'shots'),str(out/'winona-cases.json')]),('flannery',[sys.executable,'tools/qa/eventcheck.py','tools/qa/cases/z4_flannery.jsonl']),('roxanne',[sys.executable,'tools/qa/eventcheck.py','tools/qa/cases/z3_roxanne.jsonl']),('textwidth',[sys.executable,'tools/qa/textwidth.py','tools/hoenn_import/patches/FortreeCity_Gym.text.inc']),('map_integrity',['sh','tools/check_maps_integrity.sh']),('savecompat',['sh','tools/qa/savetest_all.sh']),('dex',[sys.executable,'tools/qa/dexcheck.py','--version','leafgreen','--hoenn','open'])]
 for name,cmd in cmds:
  log=out/(name+'.log');print('START',name,flush=True)
  with log.open('w') as f:rc=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
  results.append({'name':name,'returncode':rc,'log':str(log.relative_to(R))});print('END',name,rc,flush=True)
  if rc!=0:break
except Exception as exc:
 results.append({'error':str(exc),'traceback':traceback.format_exc()})
unchanged=all((R/p).exists() and hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in orig.items());report={'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'all_pass':len(results)==10 and all(x.get('returncode')==0 for x in results) and unchanged,'original_saves_unchanged':unchanged,'save_sha256':orig,'rom_sha256':hashlib.sha256((R/'pokemonthyl.gba').read_bytes()).hexdigest(),'all_regions_complete':False,'delta_tested':False};(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
