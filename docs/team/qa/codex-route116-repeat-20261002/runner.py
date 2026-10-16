from pathlib import Path
import os,json,hashlib,subprocess,time
r=Path('/workspaces/pokefirered'); os.chdir(r)
q=r/'docs/team/qa/codex-route116-repeat-20261002'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'checks':{},'scope':'Route116 repeat ball only'}
def run(name,cmd):
 print('START',name,flush=True); t=time.time()
 with (q/(name+'.log')).open('w') as f: rc=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT).returncode
 result['checks'][name]={'exit':rc,'seconds':round(time.time()-t,2)}
 (q/'result.json').write_text(json.dumps(result,indent=2))
 print('DONE',name,rc,flush=True)
 if rc: print((q/(name+'.log')).read_text()[-1500:],flush=True)
 return rc
cases=[json.loads(x) for x in (r/'tools/qa/cases/z3_route116_repeat.jsonl').read_text().splitlines()]
b=dict(cases[1]); b['steps']=[s for s in b['steps'] if 'watch ' not in s and 'expect saw ' not in s]
(q/'baseline.jsonl').write_text(json.dumps(b)+chr(10))
run('baseline-reward-only',['python3','tools/qa/eventcheck.py',str(q/'baseline.jsonl'),'--shots',str(q/'baseline-shots')])
assert run('build',['make','leafgreen','-j2'])==0
assert run('syms',['make','GAME_VERSION=LEAFGREEN','syms'])==0
run('events',['python3','tools/qa/eventcheck.py','tools/qa/cases/z3_route116_repeat.jsonl','--shots',str(q/'shots')])
run('devon-regression',['python3','tools/qa/eventcheck.py','tools/qa/cases/z3_devon.jsonl','--shots',str(q/'regression')])
run('save-compat',['bash','tools/qa/savetest_all.sh'])
run('map-integrity',['python3','tools/check_map_integrity.py'])
run('wiring-after',['python3','tools/check_event_wiring.py'])
run('map-smoke',['python3','tools/qa/mapsmoke.py','Route116','-j','2','--shots',str(q/'map-shots'),'--shots-all'])
run('text-width',['python3','tools/qa/textwidth.py','data/maps/Route116/text.inc'])
run('textaudit-z3',['python3','tools/qa/textaudit.py','--zone','Z3'])
run('dex',['python3','tools/qa/dexcheck.py'])
saved=json.loads((q/'preservation.json').read_text())
result['saves_unchanged']=saved['saves']=={str(p.relative_to(r)):digest(p) for p in (r/'saves').rglob('*.sav')}
result['protected_changes']=[n for n,h in saved['protected'].items() if digest(r/n)!=h]
a={l for l in (q/'wiring-before.log').read_text().splitlines() if l.startswith('- ')}
b={l for l in (q/'wiring-after.log').read_text().splitlines() if l.startswith('- ')}
result['new_wiring']=sorted(b-a)
result['build_warnings']=[l for l in (q/'build.log').read_text().splitlines() if 'warning:' in l.lower()]
result['complete']=True
(q/'result.json').write_text(json.dumps(result,indent=2))
print('COMPLETE',json.dumps(result),flush=True)
