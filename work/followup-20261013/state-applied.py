from pathlib import Path
import sys,json,hashlib,traceback,ctypes
root=Path('/workspaces/pokefirered');out=root/'work/followup-20261013/state-applied';out.mkdir(exist_ok=True)
sav=root/'saves/pokemonthyl_v1.25-items99-iv2x.sav';rom=root/'pokemonthyl.gba';elf=root/'pokemonthyl.elf'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p) for p in [sav,rom,elf]+list((root/'saves').glob('*.sav'))}
assert sha(rom)=='f31b2eea1ae45fd1dd40057c80510a8875936394e5807d00806a90cff1dee73d'
sys.argv=['state-applied','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
q=(root/'tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<readonly-definitions>','exec'))
report={'pass':False,'rom_sha256':sha(rom),'save_sha256':sha(sav),'ram_writes':0,'scope':'same ROM and same Flash; not old DELTA state'}
def marker(e):return {'frame':e.frame(),'rng':e.u32(syms['gRngValue'])}
try:
 with ReadOnlyEmu(str(rom),str(sav),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.hold();baseline=record(e);original=marker(e)
  state=e.save_state();flash=sha(Path(e.sav_path));e.run(120);advanced=marker(e);assert advanced['frame']==original['frame']+120 and advanced['rng']!=original['rng']
  result=e.lib.qa_load_state(e.h,state);assert result==1,('load-state rejected',result)
  restored=marker(e);assert restored==original,('actual execution marker not restored',original,advanced,restored)
  assert record(e)==baseline and e.field_idle() and not e.reset_seen()
  report['same_instance']={'saved':original,'advanced':advanced,'restored':restored,'load_return':result}
 with ReadOnlyEmu(str(rom),str(sav),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(91);pre=marker(e);assert pre!=original
  assert sha(Path(e.sav_path))==flash
  result=e.lib.qa_load_state(e.h,state);assert result==1
  restored=marker(e);assert restored==original and record(e)==baseline
  report['fresh_instance']={'before':pre,'restored':restored,'load_return':result,'flash_identical':True,'checks':[]}
  for frames in (0,60,180):
   if frames:e.run(frames)
   assert record(e)==baseline and e.field_idle() and not e.reset_seen()
   report['fresh_instance']['checks'].append({'additional_frames':frames,'marker':marker(e),'payload_preserved':True})
  assert sha(Path(e.sav_path))==flash
 report['pass']=True
except Exception as ex:
 report['error']=repr(ex);report['traceback']=traceback.format_exc()
finally:
 report['inputs_unchanged']=all(sha(Path(p))==h for p,h in before.items())
 if not report['inputs_unchanged']:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
sys.exit(0 if report['pass'] else 1)
