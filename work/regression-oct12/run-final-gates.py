from pathlib import Path
import subprocess,json,time,hashlib
r=Path('/workspaces/pokefirered');o=r/'work/regression-oct12/final-gates';o.mkdir(exist_ok=True)
rom=r/'work/regression-oct12/final-candidate/pokemonthyl-oct12-repair.gba';saves={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/'saves').rglob('*.sav')}
old=json.loads((r/'outputs/regions-q9-review-v1/required-gates-phase5/result.json').read_text())
cmds=[('map-integrity',['python3','tools/check_map_integrity.py','--no-upstream']),('text-width-touched',['python3','tools/qa/textwidth.py',*['data/maps/'+n for n in ['JohtoCherrygroveAirstrip','JohtoRoute29','NewBarkTown','NewBarkTown_ElmsLab','KantoAirport','PalletTown']],'data/scripts/companion_misty.inc']),('text-audit-touched',['python3','tools/qa/textaudit.py','--fail',*[x for n in ['JohtoCherrygroveAirstrip','JohtoRoute29','NewBarkTown','NewBarkTown_ElmsLab','KantoAirport','PalletTown'] for x in ['--map',n]]]),('event-wiring-global-existing',['python3','tools/check_event_wiring.py']),('dexcheck',['python3','tools/qa/dexcheck.py','--version','leafgreen','--hoenn','open']),('save-compat-all',['bash','tools/qa/savetest_all.sh','--rom',str(rom)]),('save-compat-user',['python3','tools/qa/savetest.py','saves/pokemonthyl_v1.1.sav:q8','saves/pokemonthyl_v1.2.sav:q8','--rom',str(rom),'--base',str(r/'outputs/regions-q9-review-v1/required-gates-phase5/qa-base-q8')])]
rows=[]
for name,cmd in cmds:
 start=time.time()
 with (o/(name+'.log')).open('w') as f:rc=subprocess.call(cmd,cwd=r,stdout=f,stderr=subprocess.STDOUT)
 rows.append(dict(check=name,exit_code=rc,seconds=round(time.time()-start,2),command=cmd,log=str(o/(name+'.log'))))
 (o/'progress.json').write_text(json.dumps(rows,indent=2))
final={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/'saves').rglob('*.sav')}
res={'checks':rows,'candidate_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'original_all_saves_unchanged':saves==final,'save_count':len(saves),'whole_regions_complete':False,'global_event_gate_known_unfinished':True}
(o/'result.json').write_text(json.dumps(res,indent=2));print(json.dumps(res),flush=True)
