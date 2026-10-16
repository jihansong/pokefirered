#!/usr/bin/env python3
"""Unify native Surf badge gating for the three story regions; dry run by default."""
import argparse,datetime,hashlib,json,re,subprocess
from pathlib import Path
MARK='STORY_REGION_SURF_GATE_V1'
HELPER='''bool8 CanUseSurfAtCurrentMap(void)
{
    // STORY_REGION_SURF_GATE_V1
    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_NEW_BARK_TOWN))
        return FlagGet(FLAG_JOHTO_BADGE04_GET);
    if (IsNamedHoennMapSec(gMapHeader.regionMapSectionId))
        return FlagGet(FLAG_HOENN_BADGE05_GET);
    return FlagGet(FLAG_BADGE05_GET);
}

'''
def once(t,a,b,label):
 if b in t:
  assert t.count(b)==1,(label,'duplicate replacement')
  return t
 assert t.count(a)==1,(label,'live source anchor differs')
 return t.replace(a,b,1)
def build(root):
 paths=['src/field_control_avatar.c','include/field_control_avatar.h','src/party_menu.c']
 originals={p:(root/p).read_bytes() for p in paths};out={}
 t=originals[paths[0]].decode()
 assert '#include "region_map.h"' in t and 'bool8 CanUseWaterfallAtCurrentMap(void)' in t
 if MARK not in t:
  t=once(t,'bool8 CanUseWaterfallAtCurrentMap(void)',HELPER+'bool8 CanUseWaterfallAtCurrentMap(void)','Surf helper')
 else:assert HELPER in t
 if '#include "constants/flags_johto_story.h"' not in t:
  t=once(t,'#include "constants/maps.h"','#include "constants/maps.h"\n#include "constants/flags_johto_story.h"','Johto flags header')
 t=once(t,'FlagGet(FLAG_BADGE05_GET) == TRUE && PartyHasMonWithSurf() == TRUE && IsPlayerFacingSurfableFishableWater() == TRUE',
     'CanUseSurfAtCurrentMap() == TRUE && PartyHasMonWithSurf() == TRUE && IsPlayerFacingSurfableFishableWater() == TRUE','water-facing A gate')
 out[paths[0]]=t.encode()
 t=originals[paths[1]].decode()
 t=once(t,'bool8 CanUseWaterfallAtCurrentMap(void);','bool8 CanUseSurfAtCurrentMap(void);\nbool8 CanUseWaterfallAtCurrentMap(void);','public Surf declaration')
 out[paths[1]]=t.encode()
 t=originals[paths[2]].decode()
 old='fieldMove < FIELD_MOVE_WATERFALL && FlagGet(FLAG_BADGE01_GET + fieldMove) != TRUE'
 new='fieldMove < FIELD_MOVE_WATERFALL && fieldMove != FIELD_MOVE_SURF && FlagGet(FLAG_BADGE01_GET + fieldMove) != TRUE'
 t=once(t,old,new,'Kanto-only generic field gate excludes Surf')
 old='(fieldMove == FIELD_MOVE_WATERFALL && !CanUseWaterfallAtCurrentMap())'
 new='(fieldMove == FIELD_MOVE_SURF && !CanUseSurfAtCurrentMap())\n         || (fieldMove == FIELD_MOVE_WATERFALL && !CanUseWaterfallAtCurrentMap())'
 t=once(t,old,new,'party Surf gate')
 assert '#include "field_control_avatar.h"' in t,'shared HM header must already be included'
 out[paths[2]]=t.encode()
 assert HELPER in out[paths[0]].decode()
 assert all(x not in out for x in ['include/global.h','include/pokemon.h','src/save.c','src/load_save.c'])
 return originals,out
def digest(b):return hashlib.sha256(b).hexdigest()
def apply(root,mutate):
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 before,out=build(root);changed={p:b for p,b in out.items() if b!=before[p]}
 stat={'save_structure_changed':False,'regions':{'Kanto':'FLAG_BADGE05_GET','Johto':'FLAG_JOHTO_BADGE04_GET','Hoenn':'FLAG_HOENN_BADGE05_GET'},'native_checks':'NOT_RUN_BY_PATCH','paths':{p:{'before':digest(before[p]),'after':digest(b)} for p,b in changed.items()}}
 print(json.dumps({'apply':mutate,'validation':stat},indent=2))
 if not mutate or not changed:return
 for p,b in before.items():assert (root/p).read_bytes()==b,('concurrent edit',p)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=root/'outputs/johto-surf-region-gate-v1'/stamp;dest.mkdir(parents=True,exist_ok=False)
 for p in changed:
  bak=dest/'before'/p;bak.parent.mkdir(parents=True,exist_ok=True);bak.write_bytes(before[p])
 (dest/'manifest.json').write_text(json.dumps(stat,indent=2)+'\n')
 for p,b in changed.items():
  target=root/p;tmp=target.with_name(target.name+'.surf-region.tmp');assert not tmp.exists()
  tmp.write_bytes(b);tmp.replace(target)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--root',default='.');a.add_argument('--apply',action='store_true');ns=a.parse_args()
 apply(Path(ns.root).resolve(),ns.apply)
