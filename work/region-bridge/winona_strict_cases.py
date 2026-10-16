import sys,json,hashlib
from pathlib import Path
R=Path('/workspaces/pokefirered');sys.path.insert(0,str(R/'tools/qa'))
import eventcheck
Path(sys.argv[1]).mkdir(parents=True,exist_ok=True)
p=R/'tools/qa/cases/z5_winona.jsonl'
cases=[json.loads(l) for l in p.read_text().splitlines() if l.strip() and not l.startswith('#')];assert len(cases)==14
wanted={'z5_winona_duplicate_negative_control':'expect item ITEM_TM40 = 1: item ITEM_TM40 is 0','z5_winona_full_stack_negative_control':'expect flag FLAG_HOENN_GOT_TM40_FROM_WINONA = 1: flag FLAG_HOENN_GOT_TM40_FROM_WINONA is 0, expected 1'}
orig={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in (R/'saves').glob('*.sav')};passed=0;results=[]
try:
 for c in cases:
  counts=[];ok,errors=eventcheck.run_case(c,str(R/'pokemonthyl.gba'),sys.argv[1],counts)
  valid=(not ok and errors==[wanted[c['name']]]) if c.get('xfail') else (ok and not errors)
  passed+=bool(valid);res={'case':c['name'],'passed':valid,'native_ok':ok,'errors':errors,'A_presses':counts};results.append(res);print(json.dumps(res),flush=True)
finally:
 assert all(Path(p).exists() and hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in orig.items()),'Original save changed'
Path(sys.argv[2]).write_text(json.dumps({'cases':results,'passed':passed,'total':14,'original_saves_unchanged':True},indent=2)+'\n');print(f'{passed}/14 strict cases passed');raise SystemExit(0 if passed==14 else 1)
