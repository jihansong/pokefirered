#!/usr/bin/env python3
"""Guarded Route 29 grass, wild tables and entry-area page. Default: dry run."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re
PINS={
"src/data/wild_encounters.json":"fea684db1b486e980c74e67e3bac9568b9687c4115efa2667743633e7ecbe977",
"src/data/wild_encounters.json.txt":"39bf3af02412bf9dcbdd00068a5efdfa8d846e85045fba6a5c1d5c8bb1d9ca2f",
"src/wild_pokemon_area.c":"4d7549c83956633385ae74038855d2eaf7411c486a0728caf3bddc627b0defd2",
"include/wild_pokemon_area.h":"5bd063823209809c26476b8fdcc5e0a0c609e1882ab2d89790ab3f79779f9bd6",
"src/pokedex_area_markers.c":"b29eea206ed1a7e5131acc83b46c2c4dc3e01bb65078b0095000a405f47da68c",
"include/pokedex_area_markers.h":"24c05e359f8db1d0aa73319f8a39cfd706c2e71cceb832441b815c129f739fba",
"src/pokedex_screen.c":"4978736c51bdcf77f292df2b777fd9be63a1c6205025f68b972d1b1f547c8fe7",
"tools/johto/build_entry.py":"365e95ed857e9047d255f13d585e8d9d7325066dece2de3317a030bde491bb00",
"src/data/region_map/region_map_sections.json":"7e969c9a844ee81cb7d93aa4e459000075ee7dc264ffb25b51e6fc542e88dbc7",
"data/layouts/JohtoRoute29/map.bin":"a7aee302dcfc8f8cadf7e17be1486d58d0297152c508bc7b2d13b7e8b5640074",
"data/layouts/JohtoRoute29/border.bin":"4f4aa105dfd88fa5d7cfa853fd7f794bf2acea638cdba8823481fac2ea22a91f",
"data/maps/JohtoRoute29/map.json":"661b02f43cb5c31e2a249014bd72ba37996f4ba6aa46179d0bd0379273b8f4f0",
"data/tilesets/primary/general/metatile_attributes.bin":"1f62a949da41adca90ad36ca3597754bee953a8f21781f32aedf6158922c89cb",
"src/time_of_day.c":"085ae97022fd04742da19b4b6075243a6c28a663896eb37b43041222dd55d57b"}
RATES=[20,20,10,10,10,10,5,5,4,4,1,1]
# Exact split of Crystal's 30/30/20/10/5/4/1 weights, preserving levels.
SPLIT=[0,1,0,1,2,2,3,3,4,5,4,6]
DAY=[(2,"PIDGEY"),(2,"SENTRET"),(3,"PIDGEY"),(3,"SENTRET"),(2,"RATTATA"),(3,"HOPPIP"),(3,"HOPPIP")]
NIGHT=[(2,"HOOTHOOT"),(2,"RATTATA"),(3,"HOOTHOOT"),(3,"RATTATA"),(2,"RATTATA"),(3,"HOOTHOOT"),(3,"HOOTHOOT")]
def table(rows):
 return {"encounter_rate":10,"mons":[{"min_level":rows[i][0],"max_level":rows[i][0],"species":"SPECIES_"+rows[i][1]} for i in SPLIT]}
ENTRY={"map":"MAP_JOHTO_ROUTE29","base_label":"sJohtoRoute29","land_mons":table(DAY),"land_mons_morning":table(DAY),"land_mons_night":table(NIGHT)}
REAPPLY=r'''#!/usr/bin/env python3
"""Reapply only the canonical Johto Route 29 table; --write is explicit."""
from pathlib import Path
import argparse,hashlib,json
def build(root):
 p=root/"src/data/wild_encounters.json"
 old=json.loads(p.read_text())
 data=json.loads(json.dumps(old))
 entry=json.loads((root/"tools/johto/route29_wild.json").read_text())
 assert entry["map"]=="MAP_JOHTO_ROUTE29" and entry["base_label"]=="sJohtoRoute29"
 groups=[g for g in data["wild_encounter_groups"] if g["label"]=="gWildMonHeaders"]
 assert len(groups)==1 and groups[0]["for_maps"]
 rows=groups[0]["encounters"]
 hits=[i for i,e in enumerate(rows) if e["map"]==entry["map"] or e["base_label"]==entry["base_label"]]
 assert len(hits)<=1,"Duplicate or colliding Route 29 headers"
 if hits:
  assert rows[hits[0]]["map"]==entry["map"] and rows[hits[0]]["base_label"]==entry["base_label"]
  rows[hits[0]]=entry
 else:rows.append(entry)
 return (json.dumps(data,ensure_ascii=False,indent=2)+"\n").encode()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--write",action="store_true");a=ap.parse_args()
 root=Path(__file__).resolve().parents[2];p=root/"src/data/wild_encounters.json";old=p.read_bytes();new=build(root)
 if a.write and new!=old:
  from datetime import datetime,timezone
  dest=root/"work/johto-wild-backups"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
  dest.mkdir(parents=True);(dest/"wild_encounters.json").write_bytes(old);p.write_bytes(new)
 print(json.dumps({"changed":old!=new,"written":bool(a.write and old!=new),"sha256":hashlib.sha256(new).hexdigest()}))
if __name__=="__main__":main()
'''
DRAW=r'''
static const u8 sText_JohtoArea[] = _("JOHTO AREA");
static const u8 sText_JohtoRoute29[] = _("ROUTE 29");
static const u8 sText_JohtoAirstrip[] = _("AIRSTRIP");
static const u8 sText_JohtoNewBark[] = _("NEW BARK");

// A schematic of the three connected entry maps, not the whole Johto region.
// These use the existing area-map palette: frame 2, light 3, white 5, land 6.
static void DexScreen_DrawJohtoEntryArea(u8 windowId)
{
    FillWindowPixelBuffer(windowId, PIXEL_FILL(2));
    FillWindowPixelRect(windowId, PIXEL_FILL(6), 3, 3, 122, 66);
    FillWindowPixelRect(windowId, PIXEL_FILL(3), 24, 33, 80, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 24, 35, 80, 4);
    FillWindowPixelRect(windowId, PIXEL_FILL(2), 20, 31, 8, 12);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 22, 33, 4, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(2), 100, 31, 8, 12);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 102, 33, 4, 8);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoRoute29, 43, 13, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoAirstrip, 5, 49, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoNewBark, 80, 49, 0);
}
'''
MARKER=r'''
// Relative to the shared 128x72 window. The entry-page band is at y=33..40.
void GetJohtoRoute29AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites)
{
    if (subsprites == NULL)
        return;
    subsprites[i] = sSubsprite_MediumHorizontal;
    subsprites[i].x = 48 + (HOENN_AREA_MAP_LEFT * 8 - 104);
    subsprites[i].y = 29;
}
'''
def sha(b):return hashlib.sha256(b).hexdigest()
def one(s,a,b):
 if s.count(a)!=1:raise ValueError("Non-unique patch anchor: "+a[:100])
 return s.replace(a,b,1)
def make_changes(raw):
 out={}
 def change(p,a,b):
  s=out.get(p,raw[p]).decode();out[p]=one(s,a,b).encode()
 p="include/wild_pokemon_area.h"
 change(p,"    DEX_AREA_REGION_COUNT","    DEX_AREA_REGION_JOHTO, // appended: preserve Kanto=0 and Hoenn=1\n    DEX_AREA_REGION_COUNT")
 p="src/wild_pokemon_area.c"
 change(p,"    u8 seviiIslands;","    bool8 johtoRoute29;\n    u8 seviiIslands;")
 change(p,"        mapSecId = GetMapSecIdFromWildMonHeader(header);",'''        // Check the implemented Johto header before the legacy Hoenn group range.
        if (header->mapGroup == MAP_GROUP(MAP_JOHTO_ROUTE29)
         && header->mapNum == MAP_NUM(MAP_JOHTO_ROUTE29))
        {
            habitats->johtoRoute29 = TRUE;
            continue;
        }
        mapSecId = GetMapSecIdFromWildMonHeader(header);''')
 change(p,"    *seviiIslands = habitats.seviiIslands;","    if (habitats.johtoRoute29)\n        regions |= 1 << DEX_AREA_REGION_JOHTO;\n    *seviiIslands = habitats.seviiIslands;")
 anchor="    FindSpeciesHabitats(species, &habitats);\n    if (region == DEX_AREA_REGION_HOENN)"
 change(p,anchor,'''    FindSpeciesHabitats(species, &habitats);
    if (region == DEX_AREA_REGION_JOHTO)
    {
        if (habitats.johtoRoute29)
            GetJohtoRoute29AreaMarkerSubsprite(areaCount++, subsprites);
        return areaCount;
    }
    if (region == DEX_AREA_REGION_HOENN)''')
 p="include/pokedex_area_markers.h"
 change(p,"u8 GetNumPokedexAreaMarkers(u8 taskId);","void GetJohtoRoute29AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);\nu8 GetNumPokedexAreaMarkers(u8 taskId);")
 p="src/pokedex_area_markers.c"
 change(p,"u8 GetNumPokedexAreaMarkers(u8 taskId)",MARKER+"\nu8 GetNumPokedexAreaMarkers(u8 taskId)")
 p="src/pokedex_screen.c"
 change(p,"u8 DexScreen_DrawMonAreaPage(void)\n{",DRAW+"\nu8 DexScreen_DrawMonAreaPage(void)\n{")
 change(p,'''        else
            sPokedexScreenData->areaRegion = DEX_AREA_REGION_KANTO;
    }

    // Unlocked islands''','''        else if (!(regions & (1 << DEX_AREA_REGION_KANTO)) && (regions & (1 << DEX_AREA_REGION_JOHTO)))
            sPokedexScreenData->areaRegion = DEX_AREA_REGION_JOHTO;
        else
            sPokedexScreenData->areaRegion = DEX_AREA_REGION_KANTO;
    }

    // Unlocked islands''')
 change(p,'''    if (sPokedexScreenData->areaRegion == DEX_AREA_REGION_HOENN)
    {
        kantoMapVoff''','''    if (sPokedexScreenData->areaRegion == DEX_AREA_REGION_JOHTO)
    {
        kantoMapVoff = HOENN_AREA_MAP_TOP - 4;
        sPokedexScreenData->windowIds[0] = AddWindow(&sWindowTemplate_AreaMap_Hoenn);
        DexScreen_DrawJohtoEntryArea(sPokedexScreenData->windowIds[0]);
        PutWindowTilemap(sPokedexScreenData->windowIds[0]);
    }
    else if (sPokedexScreenData->areaRegion == DEX_AREA_REGION_HOENN)
    {
        kantoMapVoff''')
 change(p,"const u8 *areaText = sPokedexScreenData->areaRegion == DEX_AREA_REGION_HOENN ? gText_HoennArea : gText_KantoArea;","const u8 *areaText = sPokedexScreenData->areaRegion == DEX_AREA_REGION_JOHTO ? sText_JohtoArea : (sPokedexScreenData->areaRegion == DEX_AREA_REGION_HOENN ? gText_HoennArea : gText_KantoArea);")
 change(p,"s32 mapWidth = sPokedexScreenData->areaRegion == DEX_AREA_REGION_HOENN ? sWindowTemplate_AreaMap_Hoenn.width * 8 : 96;","s32 mapWidth = sPokedexScreenData->areaRegion != DEX_AREA_REGION_KANTO ? sWindowTemplate_AreaMap_Hoenn.width * 8 : 96;")
 change(p,'''    if (sPokedexScreenData->areaRegion == DEX_AREA_REGION_HOENN)
        sPokedexScreenData->areaRegion = DEX_AREA_REGION_KANTO;
    else
        sPokedexScreenData->areaRegion = DEX_AREA_REGION_HOENN;''','''    sPokedexScreenData->areaRegion++;
    if (sPokedexScreenData->areaRegion >= DEX_AREA_REGION_COUNT)
        sPokedexScreenData->areaRegion = DEX_AREA_REGION_KANTO;''')
 change(p,"// SELECT on the area screen flips between the Kanto and Hoenn maps (L and R","// SELECT cycles Kanto, Hoenn and the Johto entry map (L and R")
 p="src/data/wild_encounters.json";old=json.loads(raw[p]);data=json.loads(raw[p])
 groups=[g for g in data["wild_encounter_groups"] if g["label"]=="gWildMonHeaders"]
 assert len(groups)==1 and groups[0]["for_maps"]
 rows=groups[0]["encounters"]
 assert not any(e["map"]==ENTRY["map"] or e["base_label"]==ENTRY["base_label"] for e in rows)
 assert next(f["encounter_rates"] for f in groups[0]["fields"] if f["type"]=="land_mons")==RATES
 rows.append(ENTRY)
 test=json.loads(json.dumps(data));next(g for g in test["wild_encounter_groups"] if g["label"]=="gWildMonHeaders")["encounters"].pop()
 assert test==old,"Any old encounter changed"
 out[p]=(json.dumps(data,ensure_ascii=False,indent=2)+"\n").encode()
 out["tools/johto/route29_wild.json"]=(json.dumps(ENTRY,indent=2)+"\n").encode()
 out["tools/johto/apply_route29_wild.py"]=REAPPLY.encode()
 assert len(out)==8
 return out

def add_grass(raw,root):
 import struct
 p="tools/johto/build_entry.py";src=raw[p].decode()
 pattern=r"(?m)^([ \t]*)route\[10\]\[36\]\s*=\s*0x3402\b"
 hits=list(re.finditer(pattern,src));assert len(hits)==1,"Route 29 sign anchor drift"
 a=hits[0].start();indent=hits[0].group(1)
 new=src[:a]+indent+"rect(route,6,7,6,2,0x300D)  # Route 29: native tall grass, not plain lawn.\n"+src[a:]
 compile(new,p,"exec")
 map_path="data/layouts/JohtoRoute29/map.bin";old=raw[map_path]
 assert len(old)==40*24*2
 words=list(struct.unpack("<960H",old));indices=[y*40+x for y in (7,8)for x in range(6,12)]
 assert all(words[i]==0x3001 for i in indices),"Grass rectangle is not clear level-3 lawn"
 attrs=struct.unpack("<%dI"%(len(raw["data/tilesets/primary/general/metatile_attributes.bin"])//4),raw["data/tilesets/primary/general/metatile_attributes.bin"])
 assert attrs[13]&0x1FF==2 and (attrs[13]>>24)&7==1,"ID13 is not native land-encounter grass"
 route=json.loads(raw["data/maps/JohtoRoute29/map.json"])
 assert route["layout"]=="LAYOUT_JOHTO_ROUTE29"
 for kind in ["object_events","warp_events","coord_events","bg_events"]:
  assert all(not(6<=int(e["x"])<=11 and 7<=int(e["y"])<=8)for e in route.get(kind,[])),kind+" overlaps grass"
 for i in indices:words[i]=0x300D
 expected=struct.pack("<960H",*words)
 generated=[]
 for text in [src,new]:
  ns={"__name__":"johto_route29_preflight","__file__":str(root/p)}
  exec(compile(text,str(root/p),"exec"),ns)
  data,meta=ns["build"](root)
  ns["verify"](root,data,meta)
  generated.append(data)
 before,after=generated
 assert set(before)==set(after)
 assert before[map_path]==old,"Canonical builder no longer reproduces the current Route 29 map"
 assert after[map_path]==expected
 assert all(before[k]==after[k]for k in before if k!=map_path),"Grass changed unrelated generated files"
 changed=[i for i,(a,b)in enumerate(zip(struct.unpack("<960H",old),words))if a!=b]
 assert changed==indices and words[7*40+9]==words[7*40+8]==0x300D
 return {p:new.encode(),map_path:expected},{"rectangle":[6,7,6,2],"changed_tiles":12,"grass_metatile":13,"behavior":2,"encounter_type":1,"collision":0,"elevation":3,"qa_start":[9,7],"qa_left":[8,7],"canonical_build_and_verify":True,"other_generated_outputs_unchanged":True}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--repo",type=Path,default=Path("."));ap.add_argument("--apply",action="store_true");a=ap.parse_args();r=a.repo.resolve()
 raw={p:(r/p).read_bytes() for p in PINS}
 assert all(sha(raw[p])==v for p,v in PINS.items()),"Current source pin differs; read before editing"
 for m in ["JohtoRoute29","JohtoCherrygroveAirstrip","NewBarkTown"]:
  assert (r/"data/maps"/m/"map.json").is_file(),m
 route=json.loads((r/"data/maps/JohtoRoute29/map.json").read_text())
 assert route["id"]=="MAP_JOHTO_ROUTE29" and route["region_map_section"]=="MAPSEC_JOHTO_ROUTE_29"
 out=make_changes(raw)
 grass,grass_report=add_grass(raw,r);out.update(grass)
 assert len(out)==10
 for p in out:
  if p not in raw:assert not (r/p).exists(),"Refuse overwrite new canonical "+p
 compile(REAPPLY,"apply_route29_wild.py","exec")
 report={"status":"dry_run","changes":{p:sha(v) for p,v in out.items()},"source_sha256":PINS,"save_layout_changed":False,"global_ram_added":0,"full_region_complete":False,"native_tested":False,"grass":grass_report}
 if a.apply:
  assert all((r/p).read_bytes()==b for p,b in raw.items()),"Source changed during preflight"
  backup=r/"work/johto-route29-backup"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
  backup.mkdir(parents=True)
  for p in out:
   if p in raw:
    dst=backup/p;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw[p])
  (backup/"manifest.json").write_text(json.dumps(report,indent=2))
  for p,b in out.items():
   dst=r/p;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(b)
  assert all((r/p).read_bytes()==b for p,b in out.items())
  report.update(status="applied_unbuilt",backup=str(backup))
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
