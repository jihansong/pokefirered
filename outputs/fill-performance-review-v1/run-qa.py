from pathlib import Path
import subprocess,json,concurrent.futures,threading,time
r=Path('/workspaces/pokefirered');d=Path('/workspaces/pokefirered/outputs/fill-performance-review-v1');jobs=[('fill-bytes', ['python3', '-B', 'tools/qa/native_fill_rect_qa.py', 'outputs/regional-dex-story-v1/regional_ui_qa.py', '/workspaces/pokefirered/outputs/fill-performance-review-v1/fill-violet-candidate.gba', 'saves/pokemonthyl_v1.2.sav']), ('scroll', ['python3', '-B', 'outputs/scroll-performance-review-v1/comparison14.py', '/workspaces/pokefirered/outputs/fill-performance-review-v1/fill-violet-candidate.gba', 'saves/pokemonthyl_v1.2.sav', '/workspaces/pokefirered/outputs/fill-performance-review-v1/fill-violet-candidate.elf']), ('dex-ui', ['python3', '-B', 'outputs/scroll-performance-review-v1/functional_ui14.py', '/workspaces/pokefirered/outputs/fill-performance-review-v1/fill-violet-candidate.gba', 'saves/pokemonthyl_v1.2.sav']), ('cb2', ['python3', '-B', 'tools/qa/native_cb2_profile.py', 'tools/qa/native_dex_profile.py', 'outputs/regional-dex-story-v1/regional_ui_qa.py', '/workspaces/pokefirered/outputs/fill-performance-review-v1/fill-violet-candidate.gba', 'saves/pokemonthyl_v1.2.sav'])]
results={};lock=threading.Lock()
def run(item):
 name,cmd=item;start=time.time()
 with (d/(name+'.log')).open('w') as f:q=subprocess.run(cmd,cwd=r,stdout=f,stderr=subprocess.STDOUT)
 with lock:
  results[name]={'exit':q.returncode,'seconds':round(time.time()-start,2)};(d/'qa-results.json').write_text(json.dumps(results,indent=2));print(name,results[name],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,jobs))
