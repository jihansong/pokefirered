from pathlib import Path
import subprocess,json,time,hashlib,statistics
w=Path('work/heartbeat-20261012T1131');o=w/'canonical-performance';o.mkdir()
rom=w/'canonical-candidate/pokemonthyl.gba'
pairs=[]
fixture=w/'final-canonical-checks/native/return-after-league-0-fixture.sav'
for pair,order in enumerate([['baseline','candidate'],['candidate','baseline'],['baseline','candidate']]):
 row={}
 for name in order:
  stem=Path('pokemonthyl') if name=='baseline' else w/'canonical-candidate/pokemonthyl'
  dst=o/('perf-'+str(pair)+'-'+name)
  with (o/('perf-'+str(pair)+'-'+name+'.log')).open('w') as log:rc=subprocess.call(['python3',str(w/'scoped-performance-child.py'),'--rom',str(stem)+'.gba','--elf',str(stem)+'.elf','--sav',str(fixture),'--out',str(dst)],stdout=log,stderr=subprocess.STDOUT)
  row[name]=json.loads((dst/'result.json').read_text()) if (dst/'result.json').exists() else {'pass':False,'exit_code':rc}
 pairs.append(row);(o/'performance-progress.json').write_text(json.dumps(pairs,indent=2))
perf={'pairs':pairs,'all_runs_pass':all(v.get('pass') and v.get('inputs_unchanged') for row in pairs for v in row.values()),'actual_DELTA_device_tested':False,'scope':'Same QA save, renderer and host; alternating order after build; no claims about full campaign or device'}
if perf['all_runs_pass']:
 ratios=[r['candidate']['render_seconds']/r['baseline']['render_seconds'] for r in pairs]
 meda=statistics.median([r['baseline']['render_seconds'] for r in pairs]);medb=statistics.median([r['candidate']['render_seconds'] for r in pairs])
 perf.update(pair_ratios=ratios,baseline_median_seconds=meda,candidate_median_seconds=medb,median_ratio=medb/meda,possible_regression=sum(x>=1.1 for x in ratios)>=2 and medb/meda>=1.1)
(o/'performance-result.json').write_text(json.dumps(perf,indent=2)+'\n')
