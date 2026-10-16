from pathlib import Path
import subprocess,json,hashlib,os
r=Path('/workspaces/pokefirered');w=r/'work/follower-flag-20261004'
results=[]
for name,args in [('build',['make','leafgreen','-j'+str(os.cpu_count() or 2)]),('symbols',['make','GAME_VERSION=LEAFGREEN','syms']),('savecompat',['bash','tools/qa/savetest_all.sh'])]:
 with (w/(name+'.log')).open('w') as log: rc=subprocess.run(args,cwd=r,stdout=log,stderr=subprocess.STDOUT).returncode
 results.append({'check':name,'exit_code':rc})
 (w/'results.json').write_text(json.dumps(results,indent=2))
 if rc: break
before=json.loads((w/'save-hashes-before.json').read_text())
unchanged=all(hashlib.sha256((r/q).read_bytes()).hexdigest()==v for q,v in before.items())
(w/'source-saves-unchanged.json').write_text(json.dumps({'unchanged':unchanged,'count':len(before)}))
print('FOLLOWER_BUILD_RESULTS',results,'SAVES_UNCHANGED',unchanged,flush=True)
