#!/usr/bin/env python3
"""Keep the cured Jasmine readiness text synchronized with its generator; dry by default."""
import argparse,ast,datetime,hashlib,importlib.util,json,sys
from pathlib import Path
MARK='GYM_CURED_NOTREADY_TEXT_V1'
CHUNK=" # GYM_CURED_NOTREADY_TEXT_V1\n texts['OlivineCity_Gym']['NotReady']=[\"AMPHY is well. Please earn\\nCHUCK's STORMBADGE first.\"]\n"
ANCHOR=' for n,d in texts.items():\n'
MAP='OlivineCity_Gym'
def sha(b):return hashlib.sha256(b).hexdigest()
def amended(src):
 assert 'HARBOR_CURED_DIALOGUE_V1' in src,'apply the harbor dialogue sync first'
 if MARK in src:
  assert src.count(CHUNK)==1,'unexpected existing readiness text patch'
  return src
 assert src.count(ANCHOR)==1,'story wrapping anchor is not unique'
 return src.replace(ANCHOR,CHUNK+ANCHOR,1)
def story(src,namespace):
 ns=dict(namespace);tree=ast.parse(src);fn=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='story'];assert len(fn)==1
 exec(compile(ast.Module(body=fn,type_ignores=[]),'cured-readiness-story','exec'),ns);return ns['story']()
def apply(root,generator,mutate):
 root=root.resolve();gp=(root/generator).resolve();assert gp.is_relative_to(root) and gp.is_file()
 source0=gp.read_bytes();source=source0.decode();source1=amended(source);ast.parse(source1)
 sys.path.insert(0,str(gp.parent));spec=importlib.util.spec_from_file_location('qa_cured_readiness_original',gp);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 oldS,oldT=module.story();newS,newT=story(source1,module.__dict__)
 assert oldS==newS,'scripts or markers changed'
 assert {n:v for n,v in oldT.items() if n!=MAP}=={n:v for n,v in newT.items() if n!=MAP},'unrelated text changed'
 assert set(oldT[MAP])==set(newT[MAP])
 assert all(v==newT[MAP][k] for k,v in oldT[MAP].items() if k!='NotReady'),'other gym text changed'
 rel=str(gp.relative_to(root));textpath='data/maps/'+MAP+'/text.inc';canonical=(root/textpath).read_bytes()
 text0=module.C.texts(MAP,oldT[MAP]).encode();text1=module.C.texts(MAP,newT[MAP]).encode()
 assert canonical==text0,'canonical readiness text differs from generator'
 changes={};originals={}
 if source1!=source:changes[rel]=source1.encode();originals[rel]=source0
 if text1!=text0:changes[textpath]=text1;originals[textpath]=canonical
 assert len(changes)==(0 if MARK in source else 2),'expected generator and one text file only'
 report={'patch':MARK,'apply':mutate,'files':{p:{'before':sha(originals[p]),'after':sha(b)} for p,b in changes.items()},'script_and_marker_changes':0,'story_or_reward_condition_changes':0,'save_layout_changed':False,'native_qa':'NOT_RUN_BY_THIS_PATCH'}
 print(json.dumps(report,indent=2),flush=True)
 if not mutate or not changes:return
 assert gp.read_bytes()==source0 and (root/textpath).read_bytes()==canonical,'concurrent edit'
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');backup=root/'outputs'/('johto-jasmine-ready-text-'+stamp);backup.mkdir(parents=True,exist_ok=False)
 for p,b in originals.items():
  target=backup/'before'/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
 (backup/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 staged=[]
 for p,b in changes.items():
  target=(root/p).resolve();assert target.is_relative_to(root);temp=target.with_name(target.name+'.ready-text.next');assert not temp.exists();temp.write_bytes(b);staged.append((temp,target))
 assert gp.read_bytes()==source0 and (root/textpath).read_bytes()==canonical,'concurrent pre-replace edit'
 for temp,target in staged:temp.replace(target)
 assert all((root/p).read_bytes()==b for p,b in changes.items())
 print('JASMINE_READY_TEXT_APPLIED',str(backup),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--generator',default='tools/johto/build_olivine_cianwood.py');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root),a.generator,a.apply)
