from pathlib import Path
import subprocess,json,time
r=Path('/workspaces/pokefirered');root=r/'work/regression-oct12';o=root/'state-cross-rom-correct-profile';o.mkdir(exist_ok=False);receipt=json.loads((root/'promotion-receipt.json').read_text());old=Path(receipt['rollback'])/'pokemonthyl.gba';new=r/'pokemonthyl.gba';jobs=[]
for tag,rom,state,ptr in [('control-q8-to-q8',old,root/'state-cross-rom/capture-q8/native-core-state.bin','0x2029348'),('control-current-to-current',new,root/'state-cross-rom/capture-current/native-core-state.bin','0x2029348'),('cross-q8-to-current',new,root/'state-cross-rom/capture-q8/native-core-state.bin','0x2029348')]:
 d=o/tag;d.mkdir();cfg=d/'config.json';cfg.write_text(json.dumps({'operation':'restore','state':str(state),'old_elf':str(old.with_suffix('.elf')),'fixed_original_pc_pointer':ptr}));args=['python3',str(root/'state-cross-rom-correct-profile-child.py'),str(cfg),'--rom',str(rom),'--elf',str(rom.with_suffix('.elf')),'--sav',str(r/'saves/pokemonthyl_v1.2.sav'),'--out',str(d)]
 with (d/'runner.log').open('w') as f:
  try:rc=subprocess.run(args,cwd=r,stdout=f,stderr=subprocess.STDOUT,timeout=45).returncode
  except subprocess.TimeoutExpired:rc='timeout'
 jobs.append({'case':tag,'process_exit':rc,'result':str(d/'result.json')})
(o/'summary.json').write_text(json.dumps({'jobs':jobs,'scope':'Actual raw-state restore experiment; corrected full-storage vs boxed-record slice diagnostic; originals untouched'},indent=2));print(json.dumps(jobs))
