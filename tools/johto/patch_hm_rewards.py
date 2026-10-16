#!/usr/bin/env python3
"""Patch only Sprout Tower reward selection and its canonical generator."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,sys,types
p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args()
r=Path(a.root).resolve();gp=r/'tools/johto/build_violet.py';before=gp.read_text()
old="""SproutTower_3F_Reward::
    goto_if_set FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED, SproutTower_3F_After
    checkitem ITEM_HM05
    goto_if_eq VAR_RESULT, TRUE, SproutTower_3F_RecordFlash
    checkitemspace ITEM_HM05
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    giveitem ITEM_HM05
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
SproutTower_3F_RecordFlash::
    setflag FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED
"""
new="""SproutTower_3F_Reward::
    goto_if_set FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED, SproutTower_3F_After
    goto_if_set FLAG_GOT_HM05, SproutTower_3F_AlternateReward
    checkitem ITEM_HM05
    goto_if_eq VAR_RESULT, TRUE, SproutTower_3F_AlternateReward
    checkpcitem ITEM_HM05
    goto_if_eq VAR_RESULT, TRUE, SproutTower_3F_AlternateReward
    checkitemspace ITEM_HM05
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    giveitem ITEM_HM05
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    setflag FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED
    msgbox SproutTower_3F_Text_Flash
    goto SproutTower_3F_After
SproutTower_3F_AlternateReward::
    checkitemspace ITEM_TM10
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    msgbox SproutTower_3F_Text_KnownFlash
    giveitem ITEM_TM10
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    setflag FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED
    msgbox SproutTower_3F_Text_Alternate
"""
replacements=[
 (old,new),
 (r"'FLASH lights dark places.\nKeep your old HM if you have it.'",r"'Use what you learned here.\nYour next challenge awaits.'"),
 (r"'BagFull':['Please make room for FLASH.\nThe reward will wait for you.']",
  r"'BagFull':['Please make room for the reward.\nI will keep it until you return.'], 'Flash':['FLASH lights dark places.\nUse it with care.'], 'KnownFlash':['You already received FLASH.\nLet us try something different.'], 'Alternate':['TM10 teaches HIDDEN POWER.\nIts power depends on the user.']")]
after=before
for x,y in replacements:
 assert after.count(x)==1,(x[:90],after.count(x))
 after=after.replace(x,y)
sys.path.insert(0,str(gp.parent))
def events(code):
 m=types.ModuleType('_reward_build');m.__file__=str(gp)
 exec(compile(code,str(gp),'exec'),m.__dict__)
 return m.events()
bs,bt=events(before);ns,nt=events(after);name='SproutTower_3F'
assert bs.keys()==ns.keys() and bt.keys()==nt.keys()
assert all(bs[k]==ns[k] for k in bs if k!=name)
assert all(bt[k]==nt[k] for k in bt if k!=name)
changes={gp:after.encode(),r/f'data/maps/{name}/scripts.inc':ns[name].encode(),r/f'data/maps/{name}/text.inc':nt[name].encode()}
original={path:path.read_bytes() for path in changes}
assert original[r/f'data/maps/{name}/scripts.inc']==bs[name].encode(),'live scripts differ from canonical generator'
assert original[r/f'data/maps/{name}/text.inc']==bt[name].encode(),'live text differs from canonical generator'
assert 'giveitem ITEM_TM10' in ns[name] and 'checkpcitem ITEM_HM05' in ns[name]
assert ns[name].count('setflag FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED')==2
def h(b):return hashlib.sha256(b).hexdigest()
manifest={'apply':a.apply,'reward':'HM05 or TM10 HIDDEN POWER','legacy_completed_rewards':'preserved without additional award',
 'save_layout_changed':False,'files':{str(path.relative_to(r)):{'before':h(original[path]),'after':h(value)} for path,value in changes.items()}}
print(json.dumps(manifest,indent=2))
if a.apply:
 import subprocess
 assert subprocess.check_output(['git','branch','--show-current'],cwd=r,text=True).strip()=='hoenn-z3'
 for path,raw in original.items():assert path.read_bytes()==raw,'concurrent edit'
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=r/'outputs/johto-hm-reward-v1'/stamp;dest.mkdir(parents=True,exist_ok=False)
 for path,raw in original.items():
  target=dest/'before'/path.relative_to(r);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 (dest/'manifest.json').write_text(json.dumps(manifest,indent=2))
 for path,data in changes.items():
  tmp=path.with_name(path.name+'.hmreward.tmp');assert not tmp.exists()
  tmp.write_bytes(data);tmp.replace(path)
 print('APPLIED',dest)
