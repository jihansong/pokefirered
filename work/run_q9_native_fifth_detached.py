from pathlib import Path
import json,subprocess,time,hashlib,concurrent.futures,os
r=Path('/workspaces/pokefirered');o=r/'outputs/regions-q9-review-v1';rom=o/'pokemonthyl-q9-phase2.gba';elf=rom.with_suffix('.elf');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(rom)=='af9ba1f61fce4630d488567ed11b83847dfbc1fcff435653bedd4d86dc622818';sv=r/'saves/pokemonthyl_v1.2.sav';main=sha(r/'pokemonthyl.gba');originals={str(p):sha(p) for p in (r/'saves').glob('*.sav')};joined=o/'native-misty-join/joined-native-save-native-QA-only.sav';joinreport=joined.parent/'join-result.json';jobs=[]
for name,script,mode in [('misty-duel-win-mainbit','native_misty_training_qa.py','win-repeat'),('misty-duel-loss-mainbit','native_misty_training_qa.py','loss')]:
 output=o/('native-phase2-'+name);assert not output.exists();env=os.environ.copy();env['MISTY_DUEL_MODE']=mode;jobs.append((name,['python3','tools/qa/'+script,'--rom',str(rom),'--elf',str(elf),'--sav',str(joined),'--out',str(output)],env))
output=o/'native-phase2-misty-walking-diagnostic';assert not output.exists();env=os.environ.copy();env['MISTY_PERF_WORKLOAD']='walking';jobs.append(('misty-walking-diagnostic',['python3','tools/qa/native_misty_performance_wrapper.py',str(rom),str(joined),str(sv),str(joinreport),str(output)],env))
output=o/'native-phase2-misty-water-helper-repaired';assert not output.exists();jobs.append(('misty-water-helper-repaired',['python3','tools/qa/native_misty_water_qa.py','--case','route','--rom',str(rom),'--elf',str(elf),'--sav',str(sv),'--out',str(output)],None))
output=o/'native-phase2-misty-basic-stage-diagnostic';assert not output.exists();jobs.append(('misty-basic-stage-diagnostic',['python3','tools/qa/native_misty_basic_stage_diagnostic.py','--rom',str(rom),'--elf',str(elf),'--sav',str(r/'outputs/misty-companion-review-v1/preserved-fixtures/basic.sav'),'--out',str(output)],None))
state={'status':'RUNNING','rom_sha256':sha(rom),'jobs_total':len(jobs),'max_workers':2,'results':[]};rp=o/'native-phase2-fifth-run.json';assert not rp.exists();rp.write_text(json.dumps(state,indent=2))
def run(x):
 name,cmd,env=x;log=o/('run-phase2-fifth-'+name+'.log');t=time.time()
 with log.open('w') as f:p=subprocess.run(cmd,cwd=r,stdout=f,stderr=subprocess.STDOUT,env=env)
 return {'name':name,'exit':p.returncode,'seconds':time.time()-t,'log':str(log)}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for future in concurrent.futures.as_completed([pool.submit(run,x) for x in jobs]):
  row=future.result();state['results'].append(row);rp.write_text(json.dumps(state,indent=2));print('Q9_NATIVE_FIFTH',json.dumps(row),flush=True)
state.update(status='FINISHED',all_pass=all(x['exit']==0 for x in state['results']),main_unchanged=main==sha(r/'pokemonthyl.gba'),original_saves_unchanged=originals=={str(p):sha(p) for p in (r/'saves').glob('*.sav')});rp.write_text(json.dumps(state,indent=2))
