#!/usr/bin/env python3
"""Restrict native Fly icon allocation to the displayed region; keep Town Map unchanged."""
import argparse,datetime,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path('.'));p.add_argument('--out',type=Path,required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
EXPECTED_SOURCE_SHA='9f1ab875551d1b3e7eaa13e35f3b4a59ad9c1a998b0baf849ea0da88e109e435'
OLD={'CreateFlyIcons': 'static void CreateFlyIcons(void)\n{\n    u16 i, y, x;\n    u8 numIcons = 0;\n    if (GetRegionMapPermission(MAPPERM_HAS_FLY_DESTINATIONS))\n    {\n        for (i = 0; i < REGIONMAP_COUNT; i++)\n        {\n            // JOHTO_FLY_ICON_SCOPE_V1: Johto has no cross-region switch.\n            if ((GetSelectedRegionMap() == REGIONMAP_JOHTO_ENTRY) != (i == REGIONMAP_JOHTO_ENTRY))\n                continue;\n            for (y = 0; y < sRegionMapGeometry[i].height; y++)\n            {\n                for (x = 0; x < sRegionMapGeometry[i].width; x++)\n                {\n                    if (GetMapsecType(GetSelectedMapSection(i, LAYER_MAP, y, x)) == MAPSECTYPE_VISITED)\n                    {\n                        if (numIcons >= NELEMS(sMapIcons->flyIcons))\n                            return;\n                        CreateFlyIconSprite(i, numIcons, x, y, numIcons + 100, 10);\n                        if (sMapIcons->flyIcons[numIcons].sprite != NULL)\n                            numIcons++;\n                    }\n                }\n            }\n        }\n    }\n}', 'CreateDungeonIcons': 'static void CreateDungeonIcons(void)\n{\n    u16 i, y, x;\n    u8 numIcons = 0;\n    u8 mapsec;\n    if (GetSelectedRegionMap() == REGIONMAP_JOHTO_ENTRY)\n        return;\n    for (i = 0; i < REGIONMAP_COUNT; i++)\n    {\n        for (y = 0; y < sRegionMapGeometry[i].height; y++)\n        {\n            for (x = 0; x < sRegionMapGeometry[i].width; x++)\n            {\n                mapsec = GetSelectedMapSection(i, LAYER_DUNGEON, y, x);\n                if (mapsec == MAPSEC_NONE)\n                    continue;\n                if (mapsec == MAPSEC_CERULEAN_CAVE && !FlagGet(FLAG_SYS_CAN_LINK_WITH_RS))\n                    continue;\n                if (numIcons >= NELEMS(sMapIcons->dungeonIcons))\n                    return;\n                CreateDungeonIconSprite(i, numIcons, x, y, numIcons + 35, 10);\n                if (sMapIcons->dungeonIcons[numIcons].sprite == NULL)\n                    continue;\n                if (GetDungeonMapsecType(mapsec) != 2)\n                {\n                    StartSpriteAnim(sMapIcons->dungeonIcons[numIcons].sprite, 1);\n                }\n                numIcons++;\n            }\n        }\n    }\n}'}
NEW={'CreateFlyIcons': 'static void CreateFlyIcons(void)\n{\n    u16 i, y, x;\n    u8 numIcons = 0;\n    if (GetRegionMapPermission(MAPPERM_HAS_FLY_DESTINATIONS))\n    {\n        for (i = 0; i < REGIONMAP_COUNT; i++)\n        {\n            // FLY_SELECTED_ICON_SCOPE_V2: Fly has no cross-region switch.\n            if (sRegionMap->type == REGIONMAP_TYPE_FLY && i != GetSelectedRegionMap())\n                continue;\n            // JOHTO_FLY_ICON_SCOPE_V1: Johto has no cross-region switch.\n            if ((GetSelectedRegionMap() == REGIONMAP_JOHTO_ENTRY) != (i == REGIONMAP_JOHTO_ENTRY))\n                continue;\n            for (y = 0; y < sRegionMapGeometry[i].height; y++)\n            {\n                for (x = 0; x < sRegionMapGeometry[i].width; x++)\n                {\n                    if (GetMapsecType(GetSelectedMapSection(i, LAYER_MAP, y, x)) == MAPSECTYPE_VISITED)\n                    {\n                        if (numIcons >= NELEMS(sMapIcons->flyIcons))\n                            return;\n                        CreateFlyIconSprite(i, numIcons, x, y, numIcons + 100, 10);\n                        if (sMapIcons->flyIcons[numIcons].sprite != NULL)\n                            numIcons++;\n                    }\n                }\n            }\n        }\n    }\n}', 'CreateDungeonIcons': 'static void CreateDungeonIcons(void)\n{\n    u16 i, y, x;\n    u8 numIcons = 0;\n    u8 mapsec;\n    if (GetSelectedRegionMap() == REGIONMAP_JOHTO_ENTRY)\n        return;\n    for (i = 0; i < REGIONMAP_COUNT; i++)\n    {\n        // FLY_SELECTED_ICON_SCOPE_V2: Fly has no cross-region switch.\n        if (sRegionMap->type == REGIONMAP_TYPE_FLY && i != GetSelectedRegionMap())\n            continue;\n        for (y = 0; y < sRegionMapGeometry[i].height; y++)\n        {\n            for (x = 0; x < sRegionMapGeometry[i].width; x++)\n            {\n                mapsec = GetSelectedMapSection(i, LAYER_DUNGEON, y, x);\n                if (mapsec == MAPSEC_NONE)\n                    continue;\n                if (mapsec == MAPSEC_CERULEAN_CAVE && !FlagGet(FLAG_SYS_CAN_LINK_WITH_RS))\n                    continue;\n                if (numIcons >= NELEMS(sMapIcons->dungeonIcons))\n                    return;\n                CreateDungeonIconSprite(i, numIcons, x, y, numIcons + 35, 10);\n                if (sMapIcons->dungeonIcons[numIcons].sprite == NULL)\n                    continue;\n                if (GetDungeonMapsecType(mapsec) != 2)\n                {\n                    StartSpriteAnim(sMapIcons->dungeonIcons[numIcons].sprite, 1);\n                }\n                numIcons++;\n            }\n        }\n    }\n}'}
f=a.repo/'src/region_map.c';raw=f.read_bytes();s=raw.decode()
if all(s.count(v)==1 for v in NEW.values()):
 print(json.dumps({'already_applied':True,'source_sha256':sha(raw),'product_changes':0}));raise SystemExit(0)
assert sha(raw)==EXPECTED_SOURCE_SHA,'canonical region-map source changed before scoped fix'
assert all(s.count(v)==1 for v in OLD.values()),'exact icon definitions changed'
# Fly cannot switch regions. Other modes retain the original region iteration.
fly=re.search(r'\[REGIONMAP_TYPE_FLY\]\s*=\s*\{([^{}]*)\}',s);assert fly
assert re.search(r'\[MAPPERM_HAS_SWITCH_BUTTON\]\s*=\s*FALSE',fly.group(1))
assert re.search(r'\[MAPPERM_HAS_FLY_DESTINATIONS\]\s*=\s*TRUE',fly.group(1))
t=s
for name in OLD:t=t.replace(OLD[name],NEW[name],1)
u=t
for name in OLD:u=u.replace(NEW[name],OLD[name],1)
assert u==s,'change escaped the two icon definitions'
for name in ['RegionMap','MapIcons','MapIconSprite']:
 pat=r'struct '+name+r'\s*\{[^{}]*\};'
 assert re.findall(pat,s)==re.findall(pat,t),'native private struct ABI changed'
assert t.count('FLY_SELECTED_ICON_SCOPE_V2')==2
assert t.count('sRegionMap->type == REGIONMAP_TYPE_FLY && i != GetSelectedRegionMap()')==2
out=a.out;a.out.mkdir(parents=True,exist_ok=True)
manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256_before':sha(raw),
 'source_sha256_after':sha(t.encode()),'changed_definitions':list(OLD),'fly_switch_button':False,
 'only_displayed_region_in_fly':True,'normal_wall_map_branch_changed':False,
 'native_struct_abi_unchanged':True,'sprite_array_capacity_changed':False,'save_abi_changed':False,
 'applied':a.apply,'native_qa_pass':False}
(out/'region-map-before.c').write_bytes(raw)
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if a.apply:f.write_text(t)
print(json.dumps(manifest))
