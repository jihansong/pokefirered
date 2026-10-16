from pathlib import Path
import subprocess,json,hashlib,time
r=Path('/workspaces/pokefirered');o=r/'work/regression-oct12/state-cross-rom';o.mkdir(exist_ok=False)
receipt=json.loads((r/'work/regression-oct12/promotion-receipt.json').read_text());old=Path(receipt['rollback'])/'pokemonthyl.gba';new=r/'pokemonthyl.gba';script=r/'work/regression-oct12/state-cross-rom-child.py';sav=r/'saves/pokemonthyl_v1.2.sav'
def case(name,rom,operation,state=None):
 out=o/name;out.mkdir();cfg={'operation':operation}
 if state:cfg.update(state=str(state),old_elf=str(old.with_suffix('.elf')))
 config=out/'config.json';config.write_text(json.dumps(cfg));args=['python3',str(script),str(config),'--rom',str(rom),'--elf',str(rom.with_suffix('.elf')),'--sav',str(sav),'--out',str(out)]
 start=time.time()
 with (out/'runner.log').open('w') as f:
  try:rc=subprocess.run(args,cwd=r,stdout=f,stderr=subprocess.STDOUT,timeout=45).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 (out/'process.json').write_text(json.dumps({'returncode':rc,'seconds':time.time()-start,'command':args},indent=2))
 p=out/'result.json';j=json.loads(p.read_text()) if p.exists() else {'error':'no result','log_tail':(out/'runner.log').read_text(errors='replace')[-1000:]}
 return {'case':name,'process_exit':rc,'pass':j.get('pass',False),'api_return':j.get('api_return'),'phase':j.get('phase'),'error':j.get('error'),'path':str(p)}
rows=[]
rows.append(case('capture-q8',old,'capture'));rows.append(case('capture-current',new,'capture'))
if all(x['pass'] for x in rows):
 rows.append(case('control-q8-to-q8',old,'restore',o/'capture-q8/native-core-state.bin'));rows.append(case('control-current-to-current',new,'restore',o/'capture-current/native-core-state.bin'))
 if all(x['pass'] and x['api_return'] for x in rows[2:]):rows.append(case('cross-q8-to-current',new,'restore',o/'capture-q8/native-core-state.bin'))
(o/'summary.json').write_text(json.dumps({'cases':rows,'scope':'Raw mGBA core state experiment; no DELTA user state available; original SAVs not rewritten'},indent=2));print(json.dumps(rows),flush=True)
