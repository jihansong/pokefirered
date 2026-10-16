from pathlib import Path
import argparse,hashlib,json,subprocess,sys
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--base',default='saves/hoenn.sav');ap.add_argument('--output',required=True,type=Path);ap.add_argument('--run',action='store_true');ap.add_argument('--rom',default='pokemonthyl.gba');args=ap.parse_args();base=Path(args.base).resolve();before=sha(base);text='SlateportCity_Harbor_Text_SternArrival';cases=[]
for scene,met in [(0,0),(0,1),(1,1)]:
 for progress in [0,1,5,7]:
  p=max(1,progress) if scene==0 else progress;intro=int(scene==0 and met==0)
  cases.append({'name':f'harbor_scene{scene}_met{met}_progress{progress}','base':str(base),'leave_menu_only':True,'edit':['warp SlateportCity_Harbor 12 13','noquestlog',f'flag FLAG_HOENN_MET_STERN {met}',f'var VAR_HOENN_SCENE_HARBOR {scene}',f'var VAR_HOENN_STAGE1_PROGRESS {progress}'],'steps':[f'watch {text}','wait 120','mash 100','expect map SlateportCity_Harbor','expect overworld','expect sym sLockFieldControls = 0','expect var VAR_HOENN_SCENE_HARBOR = 1','expect flag FLAG_HOENN_MET_STERN = 1',f'expect var VAR_HOENN_STAGE1_PROGRESS = {p}',f'expect saw {text} = {intro}','wait 180','mash 20','expect presses <= 0',f'expect var VAR_HOENN_STAGE1_PROGRESS = {p}']})
for name,idx,last in [('control_fresh_intro_not_seen',0,f'expect saw {text} = 0'),('control_legacy_progress_rolled_back',6,'expect var VAR_HOENN_STAGE1_PROGRESS = 1')]:
 c=json.loads(json.dumps(cases[idx]));c.update(name=name,xfail=True);c['steps'].append(last);cases.append(c)
args.output.parent.mkdir(parents=True,exist_ok=True)
with args.output.open('x',encoding='utf-8') as f:
 for c in cases:f.write(json.dumps(c)+'\n')
result={'cases':len(cases),'positive':12,'negative_controls':2,'source_save':str(base),'source_save_sha256':before,'executed':False}
try:
 if args.run:
  rc=subprocess.run([sys.executable,'-B','tools/qa/eventcheck.py',str(args.output),'--rom',args.rom,'--shots',str(args.output.parent/'harbor-shots')]).returncode;result.update(executed=True,returncode=rc)
finally:
 result['source_save_unchanged']=sha(base)==before;print(json.dumps(result,indent=2))
 if not result['source_save_unchanged']:raise RuntimeError('Source save changed')
if args.run:raise SystemExit(rc)
