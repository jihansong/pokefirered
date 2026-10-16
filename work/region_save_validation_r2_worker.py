from pathlib import Path
import sys,json,hashlib,subprocess,datetime,traceback
R=Path('/workspaces/pokefirered');stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=R/('work/region-save-validation-r2-'+stamp);out.mkdir();(R/'work/region-save-validation-latest.txt').write_text(str(out)+'\n');(out/'shots').mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
orig={str(p.relative_to(R)):sha(p) for p in (R/'saves').glob('*.sav')};results=[]
try:
 cmds=[('build',['make','leafgreen','-j2']),('syms',['make','GAME_VERSION=LEAFGREEN','syms']),('winona_strict',[sys.executable,'work/region-bridge/winona_strict_cases.py',str(out/'shots'),str(out/'winona-cases.json')]),('flannery',[sys.executable,'tools/qa/eventcheck.py','tools/qa/cases/z4_flannery.jsonl']),('roxanne',[sys.executable,'tools/qa/eventcheck.py','tools/qa/cases/z3_roxanne.jsonl']),('snag',[sys.executable,'tools/qa/eventcheck.py','tools/qa/cases/snag.jsonl']),('snag_tools',[sys.executable,'tools/qa/eventcheck.py','tools/qa/cases/snag_tools.jsonl']),('dock_mew',[sys.executable,'tools/qa/dock_mew_check.py']),('textwidth',[sys.executable,'tools/qa/textwidth.py','tools/hoenn_import/patches/FortreeCity_Gym.text.inc']),('map_integrity',[sys.executable,'tools/check_map_integrity.py']),('savecompat',['sh','tools/qa/savetest_all.sh']),('dex',[sys.executable,'tools/qa/dexcheck.py','--version','leafgreen','--hoenn','open']),('native_continue',None)]
 for name,cmd in cmds:
  if name=='native_continue':
   cmd=[sys.executable,'-B','work/save-integrity-audit/native_continue_check.py','--rom','pokemonthyl.gba',sha(R/'pokemonthyl.gba'),'--sym','pokemonthyl.sym',sha(R/'pokemonthyl.sym'),'--audit','work/save-integrity-audit/readonly_audit.py']
   for p,h in sorted(orig.items()):cmd+=['--save',p,h]
  log=out/(name+'.json' if name=='native_continue' else name+'.log');print('START',name,flush=True)
  with log.open('w') as f:rc=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
  results.append({'name':name,'returncode':rc,'log':str(log.relative_to(R))});print('END',name,rc,flush=True)
  if rc!=0:break
except Exception as exc:results.append({'error':str(exc),'traceback':traceback.format_exc()})
unchanged=all((R/p).exists() and sha(R/p)==h for p,h in orig.items());report={'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'all_pass':len(results)==13 and all(x.get('returncode')==0 for x in results) and unchanged,'original_saves_unchanged':unchanged,'save_sha256':orig,'rom_sha256':sha(R/'pokemonthyl.gba'),'sym_sha256':sha(R/'pokemonthyl.sym'),'pokemon_c_sha256':sha(R/'src/pokemon.c'),'all_regions_complete':False,'delta_tested':False};(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
