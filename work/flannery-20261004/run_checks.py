from pathlib import Path
import json,hashlib,subprocess,datetime
r=Path('/workspaces/pokefirered');d=r/'work/flannery-20261004'
def hashes():return {str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/'saves').glob('*.sav')}
before=hashes();(d/'source-saves-before.json').write_text(json.dumps(before,indent=2))
checks=[('build',['make','leafgreen','-j2']),('symbols',['make','GAME_VERSION=LEAFGREEN','syms']),('flannery',['python3','tools/qa/eventcheck.py','tools/qa/cases/z4_flannery.jsonl','--shots','docs/team/qa/codex-z4-flannery-20261004/shots']),('roxanne',['python3','tools/qa/eventcheck.py','tools/qa/cases/z3_roxanne.jsonl','--shots','docs/team/qa/codex-z4-flannery-20261004/roxanne-regression']),('textwidth',['python3','tools/qa/textwidth.py','tools/hoenn_import/patches/LavaridgeTown_Gym_1F.text.inc']),('map_integrity',['python3','tools/check_map_integrity.py']),('event_wiring',['python3','tools/check_event_wiring.py']),('map_smoke',['python3','tools/qa/mapsmoke.py','LavaridgeTown_Gym_1F','--quick']),('dex',['python3','tools/qa/dexcheck.py']),('savecompat',['bash','tools/qa/savetest_all.sh'])]
results=[]
for name,cmd in checks:
 print('START',name,flush=True)
 with (d/(name+'.log')).open('w') as log:
  result=subprocess.run(cmd,cwd=r,stdout=log,stderr=subprocess.STDOUT)
 results.append({'check':name,'exit':result.returncode,'log':str(d/(name+'.log'))})
 (d/'progress.json').write_text(json.dumps(results,indent=2))
 print('FINISH',name,result.returncode,flush=True)
 if name in ('build','symbols') and result.returncode:break
after=hashes();report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'original_saves_unchanged':before==after,'source_saves_count':len(before),'save_layout_changed':False,'actual_SAVE_reload_tested':False,'Delta_tested':False,'region_complete':False}
(d/'result.json').write_text(json.dumps(report,indent=2)+'\n')
p=r/'work/animation-recreation-status.json';s=json.loads(p.read_text());s['latest_verified_20261004']['flannery_reward_bridge']=report;s['latest_verified_20261004']['regions']='incomplete; Flannery canonical reward bridge applied, QA result in work/flannery-20261004/result.json';p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print('COMPLETE',json.dumps(report),flush=True)
