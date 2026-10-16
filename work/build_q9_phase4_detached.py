from pathlib import Path
import json,hashlib,subprocess,time,shutil
r=Path('/workspaces/pokefirered');o=r/'outputs/regions-q9-review-v1';o.mkdir(exist_ok=True);t=time.time()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
main={e:sha(r/('pokemonthyl.'+e)) for e in ['gba','elf','sym','map']};sv={str(p):sha(p) for p in (r/'saves').glob('*.sav')}
state={'status':'BUILDING_CORRECT_LEAFGREEN_BASE','reason':'Q9 phase3 features plus bounded Union Room name safety for cold custom Pokemon Centers','main_before':main,'save_before':sv};out=o/'build-q9-phase4-result.json';out.write_text(json.dumps(state,indent=2))
cmd=['make','-j2','syms','rom','GAME_VERSION=LEAFGREEN','GAME_REVISION=0','BUILD_NAME=blackthornlgqa','MODERN=0','COMPARE=0']
with (o/'build-q9-phase4.log').open('w') as log:proc=subprocess.run(cmd,cwd=r,stdout=log,stderr=subprocess.STDOUT)
state.update(exit_code=proc.returncode,seconds=time.time()-t,command=cmd,main_unchanged=main=={e:sha(r/('pokemonthyl.'+e)) for e in main},original_saves_unchanged=sv=={str(p):sha(p) for p in (r/'saves').glob('*.sav')})
if proc.returncode==0:
 assert (r/'pokeblackthornlgqa.gba').read_bytes()[0xac:0xb0]==b'BPGE','wrong game base despite clean object directory'
 candidate={}
 for e in main:
  src=r/('pokeblackthornlgqa.'+e);dst=o/('pokemonthyl-q9-phase4.'+e);assert not dst.exists();shutil.copy2(src,dst);candidate[e]={'path':str(dst),'size':dst.stat().st_size,'sha256':sha(dst)}
 state['candidate']=candidate;state['status']='BUILD_PASS_NATIVE_PENDING'
else:state['status']='BUILD_FAILED';state['log_tail']=(o/'build-q9-phase4.log').read_text(errors='replace')[-7000:]
out.write_text(json.dumps(state,indent=2));print('Q9_PHASE4_BUILD_RESULT',json.dumps(state))
