from pathlib import Path
import subprocess,sys,json,hashlib,datetime
r=Path('/workspaces/pokefirered');out=Path(sys.argv[1]);before={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in(r/'saves').glob('*.sav')};steps=[]
def run(name,args):
 with(out/(name+'.log')).open('wb')as f:rc=subprocess.run(args,cwd=r,stdout=f,stderr=subprocess.STDOUT).returncode
 steps.append({'name':name,'rc':rc});(out/'progress.json').write_text(json.dumps(steps,indent=2));return rc==0
ok=run('apply',[sys.executable,'tools/johto/route29_entry_apply.py','--apply'])
if ok:ok=run('build',['make','leafgreen','-j2'])
if ok:ok=run('syms',['make','GAME_VERSION=LEAFGREEN','syms'])
if ok:ok=run('map',[sys.executable,'tools/check_map_integrity.py'])
rom=r/'pokemonthyl.gba';sym=r/'pokemonthyl.sym';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if ok:ok=run('native',[sys.executable,'tools/qa/johto_route29_check.py','--rom',str(rom),'--rom-sha',sha(rom),'--sym-sha',sha(sym),'--grass','9','7','--output',str(out/'native')])
if ok:ok=run('norman-legacy-integration',[sys.executable,'tools/qa/norman_strict_check.py','--only','norman_old_winner_wally_1'])
report={'steps':steps,'all_pass':ok,'rom_sha256':sha(rom),'sym_sha256':sha(sym),'original_saves_unchanged':all(sha(Path(p))==h for p,h in before.items()),'full_regions_complete':False,'delta_device_tested':False,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat()};(out/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
