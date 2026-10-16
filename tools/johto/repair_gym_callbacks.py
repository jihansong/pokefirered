#!/usr/bin/env python3
"""Synchronize Johto gyms' real post-battle continuation with their generator."""
import argparse,datetime,hashlib,json,sys,types
from pathlib import Path
OLD=r", '+n+'_Text_Defeat\n    setflag '+badge+"
NEW=r", '+n+'_Text_Defeat, '+n+'_Victory, NO_MUSIC\n    goto '+n+'_Victory\n'+n+'_Victory::\n    setflag '+badge+"
GYMS={'CianwoodCity_Gym':'CHUCK','OlivineCity_Gym':'JASMINE'}
def sha(b):return hashlib.sha256(b).hexdigest()
def module(text,path,name):
 m=types.ModuleType(name);m.__file__=str(path)
 exec(compile(text,str(path),'exec'),m.__dict__);return m
def run(root,mutate):
 path=root/'tools/johto/build_olivine_cianwood.py'
 raw=path.read_bytes();text=raw.decode('utf-8')
 sys.path.insert(0,str(path.parent))
 already=NEW in text
 if already:
  assert OLD not in text and text.count(NEW)==1,'ambiguous new gym source anchor'
  current=module(text,path,'_olivine_callback_current')
  scripts,_=current.story()
  for n,k in GYMS.items():
   p=root/'data/maps'/n/'scripts.inc'
   assert p.read_bytes()==scripts[n].encode(),'canonical generator mismatch: '+n
   assert scripts[n].count('trainerbattle_single TRAINER_JOHTO_'+k+', '+n+'_Text_Intro, '+n+'_Text_Defeat, '+n+'_Victory, NO_MUSIC')==1
   assert scripts[n].count(n+'_Victory::')==1
  print(json.dumps({'apply':mutate,'already_synchronized':True,'generator_sha256':sha(raw)}))
  return
 assert text.count(OLD)==1 and NEW not in text,'unexpected original gym source anchor'
 before=module(text,path,'_olivine_callback_before')
 oldscripts,oldtexts=before.story()
 replacement=text.replace(OLD,NEW,1)
 after=module(replacement,path,'_olivine_callback_after')
 newscripts,newtexts=after.story()
 changed={n for n in oldscripts if oldscripts[n]!=newscripts[n]}
 assert oldscripts.keys()==newscripts.keys() and changed==set(GYMS),('unexpected changed maps',sorted(changed))
 assert oldtexts==newtexts,'dialogue changed'
 files={path:replacement.encode('utf-8')};baseline={path:raw}
 evidence={}
 for n,k in GYMS.items():
  target=root/'data/maps'/n/'scripts.inc'
  prior=target.read_bytes();assert prior==oldscripts[n].encode(),'canonical generator mismatch: '+n
  oldline='    trainerbattle_single TRAINER_JOHTO_'+k+', '+n+'_Text_Intro, '+n+'_Text_Defeat\n'
  newline=oldline.rstrip('\n')+', '+n+'_Victory, NO_MUSIC\n    goto '+n+'_Victory\n'+n+'_Victory::\n'
  assert oldscripts[n].count(oldline)==1
  assert newscripts[n]==oldscripts[n].replace(oldline,newline,1),'unexpected gym script delta'
  assert newscripts[n].count(n+'_Victory::')==1 and newscripts[n].count('    setflag FLAG_JOHTO_BADGE0'+('5' if k=='CHUCK' else '6')+'_GET')==1
  files[target]=newscripts[n].encode();baseline[target]=prior
  evidence[n]={'callback':n+'_Victory','battle_mode':'TRAINER_BATTLE_CONTINUE_SCRIPT_NO_MUSIC','badge_and_TM_assertions_unchanged':True}
 manifest={'apply':mutate,'save_layout_changed':False,'native_revalidation':'PENDING','targets':{},'evidence':evidence}
 for target,data in files.items():
  key=target.relative_to(root).as_posix()
  manifest['targets'][key]={'before':sha(baseline[target]),'after':sha(data),'bytes':len(data)}
 print(json.dumps(manifest,indent=2))
 if not mutate:return
 for target,prior in baseline.items():assert target.read_bytes()==prior,'concurrent edit: '+str(target)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=root/'outputs/johto-gym-callback-repair'/stamp;dest.mkdir(parents=True,exist_ok=False)
 for target,prior in baseline.items():
  bak=dest/'before'/target.relative_to(root);bak.parent.mkdir(parents=True,exist_ok=True);bak.write_bytes(prior)
 (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 for target,data in files.items():
  tmp=target.with_name(target.name+'.callback.tmp');assert not tmp.exists();tmp.write_bytes(data);tmp.replace(target)
 print('APPLIED',dest/'manifest.json')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args()
 run(Path(a.root).resolve(),a.apply)
