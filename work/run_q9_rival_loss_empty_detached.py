from pathlib import Path
import json,subprocess,time,hashlib,concurrent.futures
r=Path('/workspaces/pokefirered');o=r/'outputs/regions-q9-review-v1';rom=o/'pokemonthyl-q9-phase3.gba';elf=rom.with_suffix('.elf');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(rom)=='3b319b64cc1b29a1eacb7a57c50afafd935496614aa9e596b74eb556e1d38806';sv=r/'saves/pokemonthyl_v1.2.sav';main=sha(r/'pokemonthyl.gba');originals={str(p):sha(p) for p in (r/'saves').glob('*.sav')};jobs=[]
assert sha(r/'tools/qa/native_hoenn_rival_110_119_qa.py')=='a8ba588dbe8eee64134c4f1a5bd29505e0e1af5432ca1d5782ac69d95630a3d1'
assert sha(r/'tools/qa/johto_league_native_hof.py')=='244277c45e4e2f03f198850901f4d39adacd5b6d0dba1642b2675437172c0000'
for case in ['110-may-loss-2','110-brendan-loss-2','119-may-loss-1','119-brendan-loss-1']:
 output=o/('native-phase3-loss-empty-'+case);assert not output.exists();jobs.append((case,['python3','tools/qa/native_hoenn_rival_110_119_qa.py','--case',case,'--rom',str(rom),'--elf',str(elf),'--sav',str(sv),'--out',str(output)]))
state={'status':'RUNNING','rom_sha256':sha(rom),'jobs_total':len(jobs),'max_workers':2,'results':[]};rp=o/'native-phase3-rival-loss-empty-run.json';assert not rp.exists();rp.write_text(json.dumps(state,indent=2))
def run(x):
 name,cmd=x;log=o/('run-phase3-loss-empty-'+name+'.log');t=time.time()
 with log.open('w') as f:p=subprocess.run(cmd,cwd=r,stdout=f,stderr=subprocess.STDOUT)
 return {'name':name,'exit':p.returncode,'seconds':time.time()-t,'log':str(log)}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for future in concurrent.futures.as_completed([pool.submit(run,x) for x in jobs]):
  row=future.result();state['results'].append(row);rp.write_text(json.dumps(state,indent=2));print('Q9_NATIVE_REMAINING',json.dumps(row),flush=True)
state.update(status='FINISHED',all_pass=all(x['exit']==0 for x in state['results']),main_unchanged=main==sha(r/'pokemonthyl.gba'),original_saves_unchanged=originals=={str(p):sha(p) for p in (r/'saves').glob('*.sav')});rp.write_text(json.dumps(state,indent=2))
