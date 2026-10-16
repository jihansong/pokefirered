#!/usr/bin/env python3
"""Guarded harbor dialogue correction; dry by default, source and owned assets together."""
import argparse,ast,datetime,hashlib,importlib.util,json,sys
from pathlib import Path
MARK='HARBOR_CURED_DIALOGUE_V1'
CHUNK=" # HARBOR_CURED_DIALOGUE_V1\n for n,k,paras in [\n  ('OlivineCity','DockWorker',[\"AMPHY's light guides us again.\\nThe harbor is safe. Thank you!\",\"CIANWOOD and OLIVINE worked\\ntogether to save the lamp.\"]),\n  ('OlivineCity','GymGuide',[\"JASMINE returned to her GYM.\\nYour help for AMPHY mattered.\"]),\n  ('OlivineLighthouse_1F','Keeper',[\"AMPHY's light shines again.\\nJASMINE returned to her GYM.\"]),\n  ('OlivineCity_Gym','Guide',[\"JASMINE returned from the lamp.\\nYour help will not be forgotten.\"])]:\n  old='msgbox '+n+'_Text_'+k+', MSGBOX_NPC\\n    end'\n  assert scripts[n].count(old)==1,(n,k,'NPC dialogue anchor')\n  new='    goto_if_set FLAG_JOHTO_AMPHY_CURED, '+n+'_'+k+'Restored\\n'+old+'\\n'+n+'_'+k+'Restored::\\n    msgbox '+n+'_Text_'+k+'Restored, MSGBOX_NPC\\n    end'\n  scripts[n]=scripts[n].replace(old,new,1);texts[n][k+'Restored']=paras\n"
TARGETS=('OlivineCity','OlivineLighthouse_1F','OlivineCity_Gym')
ANCHOR=' for n,d in texts.items():\n'
def sha(b):return hashlib.sha256(b).hexdigest()
def amended(src):
 if MARK in src:
  assert src.count(CHUNK)==1,'unexpected existing dialogue patch'
  return src
 assert src.count(ANCHOR)==1,'story wrapping anchor is not unique'
 return src.replace(ANCHOR,CHUNK+ANCHOR,1)
def new_story(src,namespace):
 tree=ast.parse(src);fn=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='story']
 assert len(fn)==1
 ns=dict(namespace);exec(compile(ast.Module(body=fn,type_ignores=[]),'harbor-dialogue-story','exec'),ns)
 return ns['story']()
def product_maps(script,texts,encoder):
 result={}
 for n in TARGETS:
  result['data/maps/'+n+'/scripts.inc']=script[n].encode()
  result['data/maps/'+n+'/text.inc']=encoder(n,texts[n]).encode()
 return result
def apply(root,generator,mutate):
 root=root.resolve();gp=(root/generator).resolve();assert gp.is_relative_to(root) and gp.is_file()
 before_source=gp.read_bytes();source=before_source.decode();after_source=amended(source);ast.parse(after_source)
 sys.path.insert(0,str(gp.parent));spec=importlib.util.spec_from_file_location('qa_harbor_dialogue_original',gp)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 old_scripts,old_texts=module.story();new_scripts,new_texts=new_story(after_source,module.__dict__)
 assert {n:v for n,v in old_scripts.items() if n not in TARGETS}=={n:v for n,v in new_scripts.items() if n not in TARGETS},'unrelated map script changed'
 assert {n:v for n,v in old_texts.items() if n not in TARGETS}=={n:v for n,v in new_texts.items() if n not in TARGETS},'unrelated map text changed'
 old=product_maps(old_scripts,old_texts,module.C.texts);new=product_maps(new_scripts,new_texts,module.C.texts)
 assert set(old)==set(new) and len(new)==6
 originals={p:(root/p).read_bytes() for p in new}
 assert all(originals[p]==old[p] for p in old),'canonical dialogue differs from current generator; do not overwrite it'
 changes={p:b for p,b in new.items() if b!=originals[p]}
 rel=str(gp.relative_to(root));assert rel not in changes
 if after_source!=source:changes[rel]=after_source.encode();originals[rel]=before_source
 if MARK not in source:assert len(changes)==7,'expected three scripts/three texts plus generator'
 else:assert not changes,'idempotent patch diverged'
 report={'patch':MARK,'apply':mutate,'story_flag_for_branch':'FLAG_JOHTO_AMPHY_CURED','npc_branches':4,'map_scripts':3,'map_texts':3,'source_before_sha256':sha(before_source),'source_after_sha256':sha(after_source.encode()),'files':{p:{'before':sha(originals[p]),'after':sha(b)} for p,b in changes.items()},'save_layout_changed':False,'native_qa':'NOT_RUN_BY_THIS_PATCH','unrelated_generated_dialogue_preserved':True}
 print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
 if not mutate or not changes:return
 assert gp.read_bytes()==before_source,'concurrent generator change'
 assert all((root/p).read_bytes()==b for p,b in originals.items()),'concurrent canonical change'
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 backup=root/'outputs'/('johto-harbor-dialogue-'+stamp);backup.mkdir(parents=True,exist_ok=False)
 for p,b in originals.items():
  q=backup/'before'/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
 (backup/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 staged=[]
 for p,b in changes.items():
  path=(root/p).resolve();assert path.is_relative_to(root)
  temp=path.with_name(path.name+'.harbor-dialogue.next');assert not temp.exists()
  temp.write_bytes(b);staged.append((temp,path))
 assert gp.read_bytes()==before_source and all((root/p).read_bytes()==b for p,b in originals.items()),'concurrent pre-replace change'
 for temp,path in staged:temp.replace(path)
 assert all((root/p).read_bytes()==b for p,b in changes.items()),'written bytes differ'
 print('HARBOR_DIALOGUE_APPLIED',str(backup),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--generator',default='tools/johto/build_olivine_cianwood.py');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root),a.generator,a.apply)
