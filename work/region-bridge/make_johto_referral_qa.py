from pathlib import Path
import argparse, hashlib, json, subprocess, sys
ap=argparse.ArgumentParser();ap.add_argument('--lab-cases',type=Path,required=True);ap.add_argument('--base',default='saves/hoenn.sav');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--rom',default='pokemonthyl.gba');ap.add_argument('--run',action='store_true');a=ap.parse_args()
A='FLAG_JOHTO_ARRIVAL_BRIEFED';M='FLAG_JOHTO_MET_LAB_ASSISTANT';T='JohtoCherrygroveAirstrip_Text_ResearchArrival';cases=[]
for arrival,met in [(0,0),(0,1),(1,0),(1,1)]:
 cases.append({'name':f'johto_referral_arrival{arrival}_met{met}','base':a.base,'leave_menu_only':True,'edit':['noquestlog','warp JohtoCherrygroveAirstrip 22 12',f'flag {A} {arrival}',f'flag {M} {met}','flag FLAG_GOT_CYNDAQUIL_FROM_AIDE 0'],'steps':[f'watch {T}','wait 120','mash 100','expect overworld','expect map JohtoCherrygroveAirstrip',f'expect flag {A} = 1',f'expect flag {M} = {met}',f'expect saw {T} = {int(not arrival and not met)}','expect flag FLAG_GOT_CYNDAQUIL_FROM_AIDE = 0','expect sym sLockFieldControls = 0','expect var VAR_TEMP_0 = 1','wait 180','mash 20','expect presses <= 0']})
old=[json.loads(s) for s in a.lab_cases.read_text(encoding='utf-8').splitlines() if s.strip() and not s.lstrip().startswith('#')]
if len(old)!=8:raise ValueError('Expected eight validated lab cases')
for c in old:
 c=json.loads(json.dumps(c))
 if not any(x.startswith('warp NewBarkTown_ElmsLab ') for x in c.get('edit',[])):raise ValueError('Unexpected fixture: '+c['name'])
 c['name']='johto_referral_'+c['name'];c.setdefault('base',a.base);c['edit'] += [f'flag {A} 0',f'flag {M} 0'];c['steps'] += [f'expect flag {M} = 1',f'expect flag {A} = 0'];cases.append(c)
sources={Path(c.get('base',a.base)).resolve() for c in cases}
if any(not p.is_file() for p in sources):raise FileNotFoundError('Missing original QA base')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={p:sha(p) for p in sources};a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('x',encoding='utf-8') as f:
 for c in cases:f.write(json.dumps(c)+'\n')
report={'case_count':len(cases),'existing_lab_checks_preserved':8,'executed':False}
try:
 if a.run:
  rc=subprocess.run([sys.executable,'-B','tools/qa/eventcheck.py',str(a.output),'--rom',a.rom]).returncode;report.update(executed=True,returncode=rc)
finally:
 report['source_saves_unchanged']=all(sha(p)==h for p,h in before.items());print(json.dumps(report,indent=2))
 if not report['source_saves_unchanged']:raise RuntimeError('Original QA base changed')
if a.run:raise SystemExit(rc)
