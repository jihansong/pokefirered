from pathlib import Path
import subprocess,json,hashlib,time,os
r=Path('/workspaces/pokefirered');o=r/'outputs/regions-q9-review-v1';out=o/'native-phase2-walking-render-verified';log=o/'run-phase2-walking-render-verified.log';assert not out.exists() and not log.exists()
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();main={e:h(r/('pokemonthyl.'+e)) for e in ['gba','elf','sym','map']};sv={str(p):h(p) for p in (r/'saves').glob('*.sav')};t=time.time();env=os.environ.copy();env['MISTY_PERF_WORKLOAD']='walking'
cmd=['python3','tools/qa/native_misty_performance_wrapper.py',str(o/'pokemonthyl-q9-phase2.gba'),str(o/'native-misty-join/joined-native-save-native-QA-only.sav'),str(r/'saves/pokemonthyl_v1.2.sav'),str(o/'native-misty-join/join-result.json'),str(out)]
with log.open('w') as f:p=subprocess.run(cmd,cwd=r,stdout=f,stderr=subprocess.STDOUT,env=env)
state=dict(exit=p.returncode,seconds=time.time()-t,main_unchanged=main=={e:h(r/('pokemonthyl.'+e)) for e in main},original_saves_unchanged=sv=={str(p):h(p) for p in (r/'saves').glob('*.sav')},log=str(log));(o/'native-phase2-walking-render-verified-run.json').write_text(json.dumps(state,indent=2));print('WALK_RENDER_RESULT',json.dumps(state))
