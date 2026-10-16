from pathlib import Path
import hashlib,json,subprocess,time,shutil
r=Path('/workspaces/pokefirered');o=r/'outputs/regions-q9-review-v1';p=o/'required-gates-phase4';p.mkdir(exist_ok=False)
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
protected=[x for x in (r/'saves').glob('*.sav')]+[r/('pokemonthyl.'+x)for x in ['gba','elf','sym','map']]
before={str(x):sha(x)for x in protected}
for tag in ['v0.1.0','v0.2.1','v0.3.0','v0.5.1','v0.7.0','v0.8.0']:
 assert all((r/'qa-base'/tag/('pokemonthyl.'+e)).exists()for e in ['gba','sym'])
base=p/'qa-base-q8'/'q8';base.mkdir(parents=True)
for ext in ['gba','sym']:shutil.copy2(r/('pokemonthyl.'+ext),base/('pokemonthyl.'+ext))
groups=json.loads((r/'data/maps/map_groups.json').read_text());maps=groups['gMapGroup_JohtoEntry'][-12:]
assert len(maps)==12
maps+=['PalletTown','Route110','Route119']
rom=str(o/'pokemonthyl-q9-phase4.gba')
checks=[('map-integrity',['python3','tools/check_map_integrity.py','--no-upstream']),
 ('event-wiring',['python3','tools/check_event_wiring.py']),
 ('text-width',['python3','tools/qa/textwidth.py']+['data/maps/'+m for m in maps]+['data/scripts/companion_misty.inc','data/scripts/follower_pikachu.inc']),
 ('text-audit',['python3','tools/qa/textaudit.py','--fail']+sum([['--map',m]for m in maps],[])),
 ('dexcheck',['python3','tools/qa/dexcheck.py','--version','leafgreen','--hoenn','open']),
 ('save-compat-all',['bash','tools/qa/savetest_all.sh','--rom',rom]),
 ('save-compat-user-v11-v12',['python3','tools/qa/savetest.py','saves/pokemonthyl_v1.1.sav:q8','saves/pokemonthyl_v1.2.sav:q8','--rom',rom,'--base',str(p/'qa-base-q8')])]
results=[]
try:
 for label,cmd in checks:
  start=time.monotonic();log=p/(label+'.log')
  with log.open('w')as h:ret=subprocess.run(cmd,cwd=r,stdout=h,stderr=subprocess.STDOUT)
  results.append({'check':label,'exit_code':ret.returncode,'seconds':round(time.monotonic()-start,2),'log':str(log),'command':cmd})
  print(json.dumps(results[-1]),flush=True)
finally:
 after={str(x):sha(x)for x in protected};assert before==after,'original SAVE or release changed'
 (p/'result.json').write_text(json.dumps({'candidate_sha256':sha(o/'pokemonthyl-q9-phase4.gba'),'checks':results,'originals_unchanged':True},indent=2))
