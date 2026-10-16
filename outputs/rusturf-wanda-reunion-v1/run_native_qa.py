import subprocess,json,pathlib
res={}
for n,args in [('events',['python3','-B','tools/qa/eventcheck.py','tools/qa/cases/rusturf_wanda_reunion.jsonl','--rom','poketitlev8qa.gba','--shots','outputs/rusturf-wanda-reunion-v1/events']),('maps',['python3','-B','tools/qa/mapsmoke.py','RusturfTunnel','VerdanturfTown_WandasHouse','VerdanturfTown','--rom','poketitlev8qa.gba','--base','saves/pokemonthyl_v1.2.sav','--shots','outputs/rusturf-wanda-reunion-v1/maps','--shots-all'])]:
 with pathlib.Path('outputs/rusturf-wanda-reunion-v1/'+n+'.log').open('w') as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
 res[n]=r.returncode
 pathlib.Path('outputs/rusturf-wanda-reunion-v1/native-qa-result.json').write_text(json.dumps(res))
