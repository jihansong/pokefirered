from pathlib import Path
import subprocess,json
r=Path('/workspaces/pokefirered');d=r/'outputs/scroll-performance-review-v1';old=Path((r/'work/current-integration-v8-path.txt').read_text().strip())
commands=[('comparison-old14',['python3','-B',str(d/'comparison14.py'),str(old/'pokemonthyl.gba.before-v8'),'saves/pokemonthyl_v1.2.sav',str(old/'pokemonthyl.elf.before-v8')]),('comparison-candidate14',['python3','-B',str(d/'comparison14.py'),'poketitlev8qa.gba','saves/pokemonthyl_v1.2.sav','poketitlev8qa.elf']),('functional-ui14',['python3','-B',str(d/'functional_ui14.py'),'poketitlev8qa.gba','saves/pokemonthyl_v1.2.sav']),('field14',['python3','-B',str(d/'field14.py'),'poketitlev8qa.gba','saves/pokemonthyl_v1.2.sav'])]
children=[]
for name,args in commands:
 f=(d/(name+'.log')).open('w');p=subprocess.Popen(args,cwd=r,stdout=f,stderr=subprocess.STDOUT);children.append((name,p))
res={name:p.wait() for name,p in children};(d/'combined14-result.json').write_text(json.dumps(res));print(res)
