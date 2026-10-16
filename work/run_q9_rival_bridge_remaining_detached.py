from pathlib import Path
import json,subprocess,time,hashlib,concurrent.futures
r=Path('/workspaces/pokefirered');o=r/'outputs/regions-q9-review-v1';rom=o/'pokemonthyl-q9-phase2.gba';elf=rom.with_suffix('.elf');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(rom)=='af9ba1f61fce4630d488567ed11b83847dfbc1fcff435653bedd4d86dc622818';sv=r/'saves/pokemonthyl_v1.2.sav';main=sha(r/'pokemonthyl.gba');originals={str(p):sha(p) for p in (r/'saves').glob('*.sav')};jobs=[]
assert sha(r/'tools/qa/native_hoenn_rival_110_119_qa.py')=='4848c97a67f4df1de7882c2d176f29e30ee34ed9a842513013dbc67eea8dcff9'
assert sha(r/'tools/qa/johto_league_native_hof.py')=='244277c45e4e2f03f198850901f4d39adacd5b6d0dba1642b2675437172c0000'
import ast
for kind,script,skip in [('rival','native_hoenn_rival_110_119_qa.py',{'110-may-win-2','119-gift-full-retry'}),('bridge','native_hoenn_weather_bridge_qa.py',{'blocked-upper','clear-lower'})]:
 tree=ast.parse((r/'tools/qa'/script).read_text());cases=None
 for n in tree.body:
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cases' for t in n.targets):cases=ast.literal_eval(n.value);break
 assert isinstance(cases,list),(kind,'no verified cases list')
 selected=[x for x in cases if x not in skip];assert len(selected)==(24 if kind=='rival' else 6),(kind,len(selected))
 for case in selected:
  name=kind+'-'+case;output=o/('native-phase2-remaining-'+name);assert not output.exists();jobs.append((name,['python3','tools/qa/'+script,'--case',case,'--rom',str(rom),'--elf',str(elf),'--sav',str(sv),'--out',str(output)]))
output=o/'native-phase2-nurse-storage-diagnostic';assert not output.exists();jobs.append(('nurse-storage-diagnostic',['python3','tools/qa/native_johto_league_nurse_diag.py','tools/qa/johto_violet_native_bootstrap_v1.py','--rom',str(rom),'--elf',str(elf),'--sav',str(o/'native-league-chain/chain_silver_opens_plateau_arrival-native-QA-only.sav'),'--out',str(output)]))
state={'status':'RUNNING','rom_sha256':sha(rom),'jobs_total':len(jobs),'max_workers':2,'results':[]};rp=o/'native-phase2-rival-bridge-remaining-run.json';assert not rp.exists();rp.write_text(json.dumps(state,indent=2))
def run(x):
 name,cmd=x;log=o/('run-phase2-remaining-'+name+'.log');t=time.time()
 with log.open('w') as f:p=subprocess.run(cmd,cwd=r,stdout=f,stderr=subprocess.STDOUT)
 return {'name':name,'exit':p.returncode,'seconds':time.time()-t,'log':str(log)}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for future in concurrent.futures.as_completed([pool.submit(run,x) for x in jobs]):
  row=future.result();state['results'].append(row);rp.write_text(json.dumps(state,indent=2));print('Q9_NATIVE_REMAINING',json.dumps(row),flush=True)
state.update(status='FINISHED',all_pass=all(x['exit']==0 for x in state['results']),main_unchanged=main==sha(r/'pokemonthyl.gba'),original_saves_unchanged=originals=={str(p):sha(p) for p in (r/'saves').glob('*.sav')});rp.write_text(json.dumps(state,indent=2))
