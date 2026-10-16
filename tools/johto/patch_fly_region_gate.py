#!/usr/bin/env python3
"""Use the active story region's Fly badge without changing saves or destinations."""
import argparse,datetime,hashlib,json,subprocess
from pathlib import Path
MARK='STORY_REGION_FLY_GATE_V1'
HELPER='''bool8 CanUseFlyAtCurrentMap(void)
{
    // STORY_REGION_FLY_GATE_V1
    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_NEW_BARK_TOWN))
        return FlagGet(FLAG_JOHTO_BADGE05_GET);
    if (IsNamedHoennMapSec(gMapHeader.regionMapSectionId))
        return FlagGet(FLAG_HOENN_BADGE06_GET);
    return FlagGet(FLAG_BADGE03_GET);
}

'''
def once(t,old,new,label):
 if new in t:
  assert t.count(new)==1,(label,'duplicate replacement')
  return t
 assert t.count(old)==1,(label,'live source anchor differs')
 return t.replace(old,new,1)
def sha(b):return hashlib.sha256(b).hexdigest()
def build(root):
 paths=['src/field_control_avatar.c','include/field_control_avatar.h','src/party_menu.c']
 before={p:(root/p).read_bytes() for p in paths};out={}
 t=before[paths[0]].decode()
 assert '#include "region_map.h"' in t and '#include "constants/flags_johto_story.h"' in t
 if MARK not in t:t=once(t,'bool8 CanUseSurfAtCurrentMap(void)',HELPER+'bool8 CanUseSurfAtCurrentMap(void)','Fly region helper')
 else:assert HELPER in t
 out[paths[0]]=t.encode()
 t=before[paths[1]].decode()
 t=once(t,'bool8 CanUseSurfAtCurrentMap(void);','bool8 CanUseFlyAtCurrentMap(void);\nbool8 CanUseSurfAtCurrentMap(void);','Fly public declaration')
 out[paths[1]]=t.encode()
 t=before[paths[2]].decode()
 t=once(t,'fieldMove < FIELD_MOVE_WATERFALL &&','fieldMove < FIELD_MOVE_WATERFALL && fieldMove != FIELD_MOVE_FLY &&','generic HM badge gate excludes Fly')
 t=once(t,'(fieldMove == FIELD_MOVE_SURF && !CanUseSurfAtCurrentMap())','(fieldMove == FIELD_MOVE_FLY && !CanUseFlyAtCurrentMap())\n         || (fieldMove == FIELD_MOVE_SURF && !CanUseSurfAtCurrentMap())','party Fly region predicate')
 assert '#include "field_control_avatar.h"' in t
 assert 'gPartyMenu.exitCallback = CB2_OpenFlyMap;' in t,'native Fly destination flow missing'
 assert 'Overworld_MapTypeAllowsTeleportAndFly(gMapHeader.mapType)' in t,'native indoor/link restrictions must remain'
 out[paths[2]]=t.encode()
 assert build_guard(before,out)
 return before,out
def build_guard(before,out):
 for p in before:
  text=out[p].decode()
  if p.endswith('.c'):
   assert 'CanUseSurfAtCurrentMap' in text
 for token in ['CanUseWaterfallAtCurrentMap','FIELD_MOVE_DIVE','CursorCB_FieldMove','SetUpFieldMove_Fly']:
  assert before['src/party_menu.c'].decode().count(token)==out['src/party_menu.c'].decode().count(token),('unrelated field move altered',token)
 return True
def apply(root,mutate):
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 before,out=build(root);changed={p:b for p,b in out.items() if b!=before[p]}
 stats={'save_structure_changed':False,'fly_destinations_changed':False,'EWRAM_globals_added':0,'region_badges':{'Kanto':3,'Johto':5,'Hoenn':6},'native_party_and_destination_checks':'PENDING','files':{p:{'before':sha(before[p]),'after':sha(b)} for p,b in changed.items()}}
 print(json.dumps({'apply':mutate,'validation':stats},indent=2))
 if not mutate or not changed:return
 for p,b in before.items():assert (root/p).read_bytes()==b,('concurrent edit',p)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=root/'outputs/johto-fly-region-gate-v1'/stamp;dest.mkdir(parents=True,exist_ok=False)
 for p in changed:
  bak=dest/'before'/p;bak.parent.mkdir(parents=True,exist_ok=True);bak.write_bytes(before[p])
 (dest/'manifest.json').write_text(json.dumps(stats,indent=2)+'\n')
 for p,b in changed.items():
  target=root/p;tmp=target.with_name(target.name+'.fly-region.tmp');assert not tmp.exists();tmp.write_bytes(b);tmp.replace(target)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root).resolve(),a.apply)
