from pathlib import Path
import json,subprocess,time,hashlib
w=Path('work/heartbeat-20261012T1131');o=w/'final-canonical-checks';o.mkdir();r=w/'canonical-candidate/pokemonthyl.gba';ef=r.with_suffix('.elf')
cmds=[('binary',['python3',str(w/'canonical-binary-audit.py')]),('native-seven',['python3',str(w/'native-canonical.py'),'--rom',str(r),'--elf',str(ef),'--sav','saves/pokemonthyl_v1.2.sav','--out',str(o/'native')]),('legacy-six',['bash','tools/qa/savetest_all.sh','--rom',str(r.resolve())]),('user-saves',['python3','tools/qa/savetest.py','saves/pokemonthyl_v1.1.sav:q8','saves/pokemonthyl_v1.2.sav:q8','--rom',str(r),'--base','outputs/regions-q9-review-v1/required-gates-phase5/qa-base-q8']),('map-integrity',['python3','tools/check_map_integrity.py','--no-upstream']),('maps-two',['python3','tools/qa/mapsmoke.py','Route114','JohtoCherrygroveAirstrip','--rom',str(r),'--quick','-j','2','--shots-all','--shots',str(o/'map-shots')]),('events-three',['python3','tools/qa/eventcheck.py','tools/qa/cases/oct12_route114_onward.jsonl','--rom',str(r),'--shots',str(o/'event-shots')]),('width',['python3','tools/qa/textwidth.py','data/maps/Route114','data/maps/JohtoCherrygroveAirstrip']),('dex',['python3','tools/qa/dexcheck.py','--version','leafgreen','--hoenn','open'])]
rows=[]
for name,cmd in cmds:
 t=time.time()
 with (o/(name+'.log')).open('w') as log:rc=subprocess.call(cmd,stdout=log,stderr=subprocess.STDOUT)
 rows.append({'name':name,'exit_code':rc,'seconds':time.time()-t,'log':str(o/(name+'.log'))});(o/'progress.json').write_text(json.dumps(rows,indent=2))
receipt=json.loads((w/'route114-onward-source-receipt.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d={'checks':rows,'all_command_exits_zero':all(x['exit_code']==0 for x in rows),'candidate_sha256':sha(r),'original14_SAVs_unchanged':all(sha(p)==h for p,h in receipt['original_savs'].items()),'main_ROM_unchanged':sha('pokemonthyl.gba')==receipt['main_rom_before'],'scope':'Scoped fixes; global imported text and existing event gaps do not imply whole-campaign PASS'}
(o/'result.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d),flush=True)
