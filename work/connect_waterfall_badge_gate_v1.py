#!/usr/bin/env python3
"""One shared regional badge gate for native A-button and party-menu Waterfall."""
from pathlib import Path
import datetime,hashlib,json,shutil
r=Path.cwd();pending={}
fc=r/'src/field_control_avatar.c';h=r/'include/field_control_avatar.h';pm=r/'src/party_menu.c'
x=fc.read_text();y=h.read_text();z=pm.read_text()
assert 'bool8 IsNamedHoennMapSec(u16 mapsec);' in (r/'include/region_map.h').read_text()
assert 'return mapsec < KANTO_MAPSEC_START && sHoennMapNames[mapsec] != NULL;' in (r/'src/region_map.c').read_text()
assert 'CanUseWaterfallAtCurrentMap' not in x+y+z
if '#include "region_map.h"\n' not in x:
 anchor='#include "overworld.h"\n';assert x.count(anchor)==1
 x=x.replace(anchor,anchor+'#include "region_map.h"\n',1)
anchor='static const u8 *GetInteractedWaterScript(struct MapPosition *unused1, u8 metatileBehavior, u8 direction)\n'
assert x.count(anchor)==1
helper="""// One HM works across regions, but Hoenn's climb requires its RAIN BADGE.
// The named section predicate excludes Kanto, Sevii and Johto map sections.
bool8 CanUseWaterfallAtCurrentMap(void)
{
    if (IsNamedHoennMapSec(gMapHeader.regionMapSectionId))
        return FlagGet(FLAG_HOENN_BADGE08_GET);
    return FlagGet(FLAG_BADGE07_GET);
}

"""
x=x.replace(anchor,helper+anchor,1)
old='if (FlagGet(FLAG_BADGE07_GET) == TRUE && IsPlayerSurfingNorth() == TRUE)'
assert x.count(old)==1
x=x.replace(old,'if (CanUseWaterfallAtCurrentMap() == TRUE && IsPlayerSurfingNorth() == TRUE)',1)
anchor='u8 TrySetDiveWarp(void);\n';assert y.count(anchor)==1
y=y.replace(anchor,anchor+'bool8 CanUseWaterfallAtCurrentMap(void);\n',1)
old='if ((fieldMove <= FIELD_MOVE_WATERFALL && FlagGet(FLAG_BADGE01_GET + fieldMove) != TRUE)\n'
new='if ((fieldMove < FIELD_MOVE_WATERFALL && FlagGet(FLAG_BADGE01_GET + fieldMove) != TRUE)\n         || (fieldMove == FIELD_MOVE_WATERFALL && !CanUseWaterfallAtCurrentMap())\n'
assert z.count(old)==1;z=z.replace(old,new,1)
# Keep native Dive, all other HM badges, menu callbacks and Waterfall terrain checks.
assert '(fieldMove == FIELD_MOVE_DIVE && gMapHeader.mapType != MAP_TYPE_UNDERWATER\n          && !FlagGet(FLAG_HOENN_BADGE07_GET))' in z
pending={fc:x,h:y,pm:z}
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=r/'work'/('waterfall-badge-gate-backup-'+stamp);backup.mkdir(parents=True,exist_ok=False)
for target in pending:
 dest=backup/target.relative_to(r);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,dest)
before={str(f.relative_to(r)):hashlib.sha256(f.read_bytes()).hexdigest() for f in pending}
for f,s in pending.items():f.write_text(s)
print(json.dumps({'changed':[str(f.relative_to(r)) for f in pending],'backup':str(backup.relative_to(r)),
 'before':before,'after':{str(f.relative_to(r)):hashlib.sha256(f.read_bytes()).hexdigest() for f in pending},
 'hoenn_waterfall_badge':'FLAG_HOENN_BADGE08_GET','other_regions_badge':'FLAG_BADGE07_GET',
 'save_layout_unchanged':True,'native_a_and_menu_qa_pending':True}))
