from pathlib import Path
import json,hashlib,subprocess,datetime,shutil
r=Path('/workspaces/pokefirered');d=r/'work/johto-entry-20261004-r2';d.mkdir(exist_ok=False)
def hashes():return {str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(r/'saves').glob('*.sav')}
before=hashes();(d/'source-saves-before.json').write_text(json.dumps(before,indent=2))
for n in ['pokeleafgreen.gba','pokeleafgreen.elf','pokeleafgreen.sym']:
 if(r/n).exists():shutil.copy2(r/n,d/('before-'+n))
checks=[('build',['make','leafgreen','-j2']),('symbols',['make','GAME_VERSION=LEAFGREEN','syms']),('johto',['python3','tools/qa/eventcheck.py','tools/qa/cases/johto_entry.jsonl','--shots','docs/team/qa/codex-johto-entry-20261004/shots']),('maps',['python3','tools/qa/mapsmoke.py','JohtoCherrygroveAirstrip','JohtoRoute29','NewBarkTown','NewBarkTown_ElmsLab','NewBarkTown_RestHouse','NewBarkTown_NeighborsHouse','--shots','docs/team/qa/codex-johto-entry-20261004/smoke','--shots-all','-j','2']),('map_integrity',['python3','tools/check_map_integrity.py']),('savecompat',['bash','tools/qa/savetest_all.sh'])]
results=[]
for name,cmd in checks:
 print('START',name,flush=True)
 with(d/(name+'.log')).open('w')as log:ret=subprocess.run(cmd,cwd=r,stdout=log,stderr=subprocess.STDOUT)
 results.append(dict(check=name,exit=ret.returncode,log=str(d/(name+'.log'))));(d/'progress.json').write_text(json.dumps(results,indent=2));print('FINISH',name,ret.returncode,flush=True)
 if name in('build','symbols')and ret.returncode:break
report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),results=results,original_saves_unchanged=before==hashes(),save_layout_changed=False,actual_SAVE_reload_tested=False,Delta_tested=False,region_complete=False)
(d/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('COMPLETE',json.dumps(report),flush=True)
