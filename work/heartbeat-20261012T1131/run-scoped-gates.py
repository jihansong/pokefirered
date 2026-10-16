from pathlib import Path
import subprocess,json,time,hashlib,statistics
w=Path('work/heartbeat-20261012T1131');o=w/'required-scoped-gates';o.mkdir()
rom=w/'route114-onward-candidate/pokemonthyl.gba'
cmds=[('touched-width',['python3','tools/qa/textwidth.py','data/maps/Route114','data/maps/JohtoCherrygroveAirstrip']),('touched-audit',['python3','tools/qa/textaudit.py','--fail','--map','Route114','--map','JohtoCherrygroveAirstrip']),('user-save-compat',['python3','tools/qa/savetest.py','saves/pokemonthyl_v1.1.sav:q8','saves/pokemonthyl_v1.2.sav:q8','--rom',str(rom),'--base','outputs/regions-q9-review-v1/required-gates-phase5/qa-base-q8']),('event-wiring-existing-global',['python3','tools/check_event_wiring.py'])]
checks=[]
for name,cmd in cmds:
 start=time.time()
 with (o/(name+'.log')).open('w') as log:rc=subprocess.call(cmd,stdout=log,stderr=subprocess.STDOUT)
 checks.append({'name':name,'exit_code':rc,'seconds':time.time()-start,'log':str(o/(name+'.log'))});(o/'progress.json').write_text(json.dumps(checks,indent=2))
pairs=[]
fixture=w/'native-route114-onward-mapAPI-fixed/return-after-league-0-fixture.sav'
for pair,order in enumerate([['baseline','candidate'],['candidate','baseline'],['baseline','candidate']]):
 row={}
 for name in order:
  stem=Path('pokemonthyl') if name=='baseline' else w/'route114-onward-candidate/pokemonthyl'
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
s=json.loads((w/'route114-onward-source-receipt.json').read_text())
d={'checks':checks,'performance_file':str(o/'performance-result.json'),'original_14_saves_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in s['original_savs'].items()),'main_ROM_unchanged':hashlib.sha256(Path('pokemonthyl.gba').read_bytes()).hexdigest()==s['main_rom_before'],'candidate_sha256':hashlib.sha256(rom.read_bytes()).hexdigest()}
(o/'result.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d),flush=True)
