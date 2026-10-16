#!/usr/bin/env python3
"""Shared story-region Strength/Rock Smash A/menu gates. Dry run by default."""
import argparse,datetime,hashlib,json,re,subprocess
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--apply',action='store_true');a=P.parse_args()
R=Path.cwd();sha=lambda b:hashlib.sha256(b).hexdigest()
paths=['src/field_control_avatar.c','include/field_control_avatar.h',
 'src/party_menu.c','data/scripts/field_moves.inc','data/specials.inc']
before={p:(R/p).read_bytes() for p in paths};out={}
HELPER="""// STORY_REGION_STRENGTH_ROCK_GATE_V1
// Gold/Crystal: PLAIN BADGE permits STRENGTH; ROCK SMASH needs no badge.
// Keep the same Johto boundary as the existing regional SURF helper.
bool8 CanUseStrengthAtCurrentMap(void)
{
    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_NEW_BARK_TOWN))
        return FlagGet(FLAG_JOHTO_BADGE03_GET);
    if (IsNamedHoennMapSec(gMapHeader.regionMapSectionId))
        return FlagGet(FLAG_HOENN_BADGE04_GET);
    return FlagGet(FLAG_BADGE04_GET);
}

bool8 CanUseRockSmashAtCurrentMap(void)
{
    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_NEW_BARK_TOWN))
        return TRUE;
    if (IsNamedHoennMapSec(gMapHeader.regionMapSectionId))
        return FlagGet(FLAG_HOENN_BADGE03_GET);
    return FlagGet(FLAG_BADGE06_GET);
}

"""
def once(t,old,new,label):
 if new in t:
  assert t.count(new)==1,(label,'duplicate')
  return t
 assert t.count(old)==1,(label,'live anchor differs')
 return t.replace(old,new,1)
t=before[paths[0]].decode()
assert '#include "region_map.h"' in t and '#include "constants/flags_johto_story.h"' in t
assert 'bool8 CanUseSurfAtCurrentMap(void)' in t and 'bool8 CanUseWaterfallAtCurrentMap(void)' in t
assert 'gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_NEW_BARK_TOWN)' in t
old_helpers={name:re.search(r'bool8 '+name+r'\(void\)\n\{[^{}]*\}\n',t).group(0)
 for name in ('CanUseSurfAtCurrentMap','CanUseWaterfallAtCurrentMap')}
if 'STORY_REGION_STRENGTH_ROCK_GATE_V1' not in t:
 t=once(t,'bool8 CanUseSurfAtCurrentMap(void)',HELPER+'bool8 CanUseSurfAtCurrentMap(void)','shared helpers')
else:assert HELPER in t
for name,body in old_helpers.items():assert body in t,(name,'changed unexpectedly')
out[paths[0]]=t.encode()
t=before[paths[1]].decode()
decl='bool8 CanUseStrengthAtCurrentMap(void);\nbool8 CanUseRockSmashAtCurrentMap(void);\n'
t=once(t,'bool8 CanUseSurfAtCurrentMap(void);\n',decl+'bool8 CanUseSurfAtCurrentMap(void);\n','public declarations')
out[paths[1]]=t.encode()
t=before[paths[2]].decode()
old='fieldMove < FIELD_MOVE_WATERFALL && fieldMove != FIELD_MOVE_SURF && FlagGet(FLAG_BADGE01_GET + fieldMove) != TRUE'
new=('fieldMove < FIELD_MOVE_WATERFALL && fieldMove != FIELD_MOVE_SURF\n'
 '          && fieldMove != FIELD_MOVE_STRENGTH && fieldMove != FIELD_MOVE_ROCK_SMASH\n'
 '          && FlagGet(FLAG_BADGE01_GET + fieldMove) != TRUE')
t=once(t,old,new,'exclude region-specific HMs from Kanto-only gate')
old='(fieldMove == FIELD_MOVE_SURF && !CanUseSurfAtCurrentMap())'
new=('(fieldMove == FIELD_MOVE_STRENGTH && !CanUseStrengthAtCurrentMap())\n'
 '         || (fieldMove == FIELD_MOVE_ROCK_SMASH && !CanUseRockSmashAtCurrentMap())\n'
 '         || (fieldMove == FIELD_MOVE_SURF && !CanUseSurfAtCurrentMap())')
t=once(t,old,new,'shared party-menu gates')
assert '(fieldMove == FIELD_MOVE_WATERFALL && !CanUseWaterfallAtCurrentMap())' in t
assert '(fieldMove == FIELD_MOVE_DIVE && gMapHeader.mapType != MAP_TYPE_UNDERWATER\n          && !FlagGet(FLAG_HOENN_BADGE07_GET))' in t
out[paths[2]]=t.encode()
t=before[paths[3]].decode()
for name,badge,label in [('Strength','04','EventScript_CantMoveBoulder'),('RockSmash','06','EventScript_CantSmashRock')]:
 old='\tgoto_if_unset FLAG_BADGE'+badge+'_GET, '+label
 new=('\tspecialvar VAR_RESULT, CanUse'+name+'AtCurrentMap\n'
      '\tgoto_if_eq VAR_RESULT, FALSE, '+label)
 t=once(t,old,new,'A-button '+name+' gate')
out[paths[3]]=t.encode()
t=before[paths[4]].decode()
decl='\tdef_special CanUseStrengthAtCurrentMap\n\tdef_special CanUseRockSmashAtCurrentMap\n'
old_specials=re.findall(r'^\s*def_special\s+(\w+)',t,re.M)
t=once(t,'gSpecialsEnd::',decl+'gSpecialsEnd::','append specials without shifting old IDs')
new_specials=re.findall(r'^\s*def_special\s+(\w+)',t,re.M)
assert new_specials==old_specials+['CanUseStrengthAtCurrentMap','CanUseRockSmashAtCurrentMap'] or (
 old_specials==new_specials and old_specials[-2:]==['CanUseStrengthAtCurrentMap','CanUseRockSmashAtCurrentMap'])
out[paths[4]]=t.encode()
flagheaders='\n'.join(p.read_text() for p in (R/'include/constants').glob('flags*.h'))
for f in ['FLAG_JOHTO_BADGE03_GET','FLAG_HOENN_BADGE04_GET','FLAG_HOENN_BADGE03_GET']:
 assert re.search(r'^\s*#define\s+'+f+r'\b',flagheaders,re.M),('missing native flag',f)
assert subprocess.check_output(['git','branch','--show-current'],text=True).strip()=='hoenn-z3'
changed={p:b for p,b in out.items() if b!=before[p]}
saves={str(p):sha(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}
receipt={'apply':a.apply,'changed':list(changed),'save_structure_changed':False,
 'all_existing_special_ids_preserved':True,'existing_surf_waterfall_dive_preserved':True,
 'strength_badges':{'Kanto':4,'Johto':3,'Hoenn':4},
 'rock_smash_badges':{'Kanto':6,'Johto':None,'Hoenn':3},
 'original_gsc_source':'https://github.com/pret/pokecrystal/blob/master/engine/events/overworld.asm',
 'native_a_menu_and_region_boundary_qa':'NOT_RUN',
 'files':{p:{'before':sha(before[p]),'after':sha(out[p])} for p in paths},
 'original_save_sha256':saves}
if a.apply and changed:
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=R/'work/backups'/('region-strength-rock-gates-v1-'+stamp)
 for p,b in before.items():assert (R/p).read_bytes()==b,('concurrent edit',p)
 for p in changed:
  q=dest/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[p])
 for p,b in changed.items():(R/p).write_bytes(b)
 receipt['backup']=str(dest.relative_to(R))
assert {str(p):sha(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}==saves,'original save changed'
print(json.dumps(receipt,indent=2))
