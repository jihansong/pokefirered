"""Prepare separate, guarded regional airport candidates; never write a repository.

Existing flight arrival, region gates, story scripts and original map IDs remain.
The current approved Vermilion facade must be explicitly cropped after review.
This program writes only a NEW candidate directory and does not build a ROM.
"""
import argparse
import copy
import hashlib
import json
import struct
from collections import deque
from pathlib import Path


AIR = "JohtoCherrygroveAirstrip"
JT = "JohtoAirportTerminal"
HE = "HoennAirportExterior"
HT = "HoennAirportTerminal"
IDS = {AIR: "JOHTO_CHERRYGROVE_AIRSTRIP", JT: "JOHTO_AIRPORT_TERMINAL",
       HE: "HOENN_AIRPORT_EXTERIOR", HT: "HOENN_AIRPORT_TERMINAL"}


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def enc(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode()


def words(blob, width, height):
    assert len(blob) == 2 * width * height
    flat = struct.unpack("<%dH" % (width * height), blob)
    return [list(flat[y * width:(y + 1) * width]) for y in range(height)]


def pack(grid):
    return struct.pack("<%dH" % sum(map(len, grid)), *(v for row in grid for v in row))


def warp(x, y, dest, index, elevation=3):
    return dict(x=x, y=y, elevation=elevation,
                dest_map="MAP_" + IDS.get(dest, dest), dest_warp_id=str(index))


def obj(graphics, x, y, script, movement="FACE_DOWN"):
    return dict(type="object", graphics_id="OBJ_EVENT_GFX_" + graphics,
                x=x, y=y, elevation=3, movement_type="MOVEMENT_TYPE_" + movement,
                movement_range_x=0, movement_range_y=0,
                trainer_type="TRAINER_TYPE_NONE", trainer_sight_or_berry_tree_id="0",
                script=script, flag="0")


def paths(grid, start, required, blockers=()):
    """Only a static collision flood; does not claim native movement."""
    width, height = len(grid[0]), len(grid)
    seen = {start}; q = deque([start]); blockers = set(blockers)
    while q:
        x, y = q.popleft()
        for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if (0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen
                    and (nx, ny) not in blockers and not (grid[ny][nx] & 0xC00)):
                seen.add((nx, ny)); q.append((nx, ny))
    assert set(required) <= seen, ("New airport path disconnected", set(required) - seen)
    return len(seen)


def importer_hook(source):
    """Exact, idempotent Harbor-only cell overrides for canonical import."""
    imports = "import json, os, re, sys\n"
    assert source.count(imports) == 1
    source = source.replace(imports, imports+"from pathlib import Path\n", 1)
    anchor = "            if key == 'coord_overrides':\n"
    assert source.count(anchor) == 1 and "key == 'layout_overrides'" not in source
    hook = '''            if key == 'layout_overrides':
                # Regional airport lobby exit: preserve this exact two-cell
                # overlay when the original Hoenn layout is imported again.
                assert name == 'SlateportCity_Harbor', name
                expected = [dict(x=2, y=14, before=0x3202, after=0x0206),
                            dict(x=3, y=14, before=0x3202, after=0x0207)]
                assert items == expected, 'Unexpected airport layout override'
                layouts = json.load(open(os.path.join(R, 'data/layouts/layouts.json')))['layouts']
                matches = [v for v in layouts if v.get('id') == m['layout']]
                assert len(matches) == 1
                layout = matches[0]
                assert (layout['width'], layout['height']) == (24, 15)
                blockpath = (Path(R) / layout['blockdata_filepath']).resolve(strict=True)
                assert blockpath.is_relative_to(Path(R).resolve())
                raw = bytearray(blockpath.read_bytes())
                assert len(raw) == 24 * 15 * 2
                for override in items:
                    offset = 2 * (override['y'] * 24 + override['x'])
                    current = int.from_bytes(raw[offset:offset+2], 'little')
                    assert current in (override['before'], override['after']), (name, override, current)
                    raw[offset:offset+2] = override['after'].to_bytes(2, 'little')
                blockpath.write_bytes(raw)
                continue
'''
    return source.replace(anchor, hook+anchor, 1)


def build(root, facade_rect, rom=None):
    inputs, output, evidence = {}, {}, {}

    def read(rel):
        p = (root / rel).resolve(strict=True)
        assert p.is_relative_to(root)
        blob = p.read_bytes()
        inputs[rel] = dict(bytes=len(blob), sha256=sha(blob))
        return blob

    def load(rel):
        return json.loads(read(rel))

    def put(rel, blob):
        assert not rel.startswith(("/", "..")) and ".." not in Path(rel).parts
        output[rel] = blob.encode() if isinstance(blob, str) else blob

    layouts = load("data/layouts/layouts.json")
    groups = load("data/maps/map_groups.json")
    before_layouts, before_groups = copy.deepcopy(layouts), copy.deepcopy(groups)
    layout_by_id = {x["id"]: x for x in layouts["layouts"] if "id" in x}

    def source(name):
        meta = load("data/maps/" + name + "/map.json")
        layout = layout_by_id[meta["layout"]]
        blob = read(layout["blockdata_filepath"])
        border = read(layout["border_filepath"])
        if rom is not None:
            assert blob in rom, ("Source landscape is not present in supplied current ROM", name)
            evidence.setdefault("source_landscapes_present_in_rom", {})[name] = sha(blob)
        return meta, layout, words(blob, layout["width"], layout["height"]), border

    air_meta, air_layout, original_air, air_border = source(AIR)
    kt_meta, kt_layout, terminal_grid, terminal_border = source("KantoAirport")
    verm_meta, verm_layout, verm, _ = source("VermilionCity")
    harbor_meta, harbor_layout, original_harbor, _ = source("SlateportCity_Harbor")
    assert (air_layout["width"], air_layout["height"]) == (32, 24)
    assert (kt_layout["width"], kt_layout["height"]) == (33, 10)
    assert (harbor_layout["width"], harbor_layout["height"]) == (24, 15)
    assert air_layout["primary_tileset"] == verm_layout["primary_tileset"] == "gTileset_General"
    assert air_layout["secondary_tileset"] == verm_layout["secondary_tileset"] == "gTileset_VermilionCity"
    assert kt_layout["primary_tileset"] == "gTileset_EmBuilding"
    assert kt_layout["secondary_tileset"] == "gTileset_KantoAirport"
    assert not air_meta["warp_events"] and len(harbor_meta["warp_events"]) == 4
    assert len(harbor_meta["object_events"]) == 4
    assert all(n not in sum((groups[g] for g in groups["group_order"]), []) for n in (JT, HE, HT))

    # The facade comes only from the CURRENT approved Kanto building, same pair.
    doors = [w for w in verm_meta["warp_events"] if w["dest_map"] == "MAP_KANTO_AIRPORT"]
    assert len(doors) == 1
    vd = doors[0]
    sx, sy, fw, fh = facade_rect
    assert 1 <= fw <= 10 and 1 <= fh <= 10
    assert 0 <= sx <= vd["x"] < sx + fw <= verm_layout["width"]
    assert sy + fh - 1 == vd["y"] and 0 <= sy
    assert not (verm[vd["y"]][vd["x"]] & 0xC00), "Approved door must be passable"
    dx, dy = 33, 10 - (fh-1)
    door_x, door_y = dx + vd["x"] - sx, 10
    assert dx + fw <= 43 and dy >= 1
    facade = [row[sx:sx+fw] for row in verm[sy:sy+fh]]
    # Reuse Vermilion's actual pedestrian ground, not a numeric ID borrowed
    # from PalletTown (0x296 is a cliff in the bound Vermilion secondary set).
    paving = verm[9][8]
    assert paving == 0x3115, "Approved pedestrian paving changed; inspect current art"
    evidence["approved_facade"] = dict(source_rect=facade_rect,
        source_door=[vd["x"], vd["y"]], source_sha256=sha(pack(facade)),
        destination_rect=[dx, dy, fw, fh], destination_door=[door_x, door_y],
        paving_source_xy=[8,9], paving_raw=hex(paving))

    # Keep ALL original 32 columns, including the original city connection and
    # flight landing (22,12). The east extension alone carries the new facade.
    air = [row + [0x3001] * 12 for row in original_air]
    for y in range(24):
        for x in range(32, 44):
            if y < 2 or y >= 22 or x >= 42:
                air[y][x] = 0x400 + ((28, 29) if y % 2 == 0 else (20, 21))[x % 2]
    for y in range(11, 14):
        for x in range(32, 44):
            air[y][x] = paving
    for fy, row in enumerate(facade):
        air[dy+fy][dx:dx+fw] = row
    assert all(row[:32] == original_air[y] for y, row in enumerate(air))
    air_meta_new = copy.deepcopy(air_meta)
    air_meta_new["warp_events"].append(warp(door_x, door_y, JT, 0, vd["elevation"]))
    old_air_layout = copy.deepcopy(air_layout)
    air_layout["width"] = 44
    put(air_layout["blockdata_filepath"], pack(air))
    put("data/maps/" + AIR + "/map.json", enc(air_meta_new))

    # Separate FRLG exterior avoids mixing Kanto 640 split art with Slateport's
    # Emerald 512 split city set. The existing harbor, docks and flights stay.
    # The new Hoenn map has no legacy coordinates to preserve. Keep its public
    # annex compact (32 columns); the old Johto map alone expands to 44 columns.
    he = copy.deepcopy(original_air)
    he_dx = 21
    he_door_x = he_dx + vd["x"] - sx
    # Old north connection becomes a physical tree boundary on this new map.
    for y in (0, 1):
        for x in range(2, 30):
            he[y][x] = 0x400 + ((28, 29) if y % 2 == 0 else (20, 21))[x % 2]
    for y in range(24):
        for x in (30, 31):
            he[y][x] = 0x400 + ((28, 29) if y % 2 == 0 else (20, 21))[x % 2]
    # Remove old outdoor counter sign: that sign has no event on the new map.
    he[10][25] = 0x3001
    for y in range(11, 14):
        for x in range(18, 30):
            he[y][x] = paving
    for fy, row in enumerate(facade):
        he[dy+fy][he_dx:he_dx+fw] = row
    for y in range(14, 24):
        for x in (22, 23):
            he[y][x] = paving
    # Native General SOUTH_ARROW_WARP (0x179): arrival faces north, no warp loop.
    he[23][22] = he[23][23] = 0x3179
    he_meta = copy.deepcopy(air_meta)
    he_meta.update(id="MAP_"+IDS[HE], name=HE, layout="LAYOUT_"+IDS[HE],
        music="MUS_SLATEPORT", region_map_section="MAPSEC_SLATEPORT_CITY",
        connections=None, object_events=[], coord_events=[], bg_events=[],
        warp_events=[warp(22, 23, "SLATEPORT_CITY_HARBOR", 4),
                     warp(23, 23, "SLATEPORT_CITY_HARBOR", 5),
                     warp(he_door_x, door_y, HT, 0, vd["elevation"])])
    he_meta["object_events"] = [obj("SAILOR", 26, 15, HE+"_Guide")]
    he_layout = copy.deepcopy(old_air_layout)
    he_layout.update(id="LAYOUT_"+IDS[HE], name=HE+"_Layout", width=32)
    evidence["hoenn_facade_destination_door"] = [he_door_x, door_y]

    # Existing four harbor IDs/objects/scripts remain; append paired lobby exit.
    harbor = copy.deepcopy(original_harbor)
    assert harbor[14][2] == harbor[14][3] == 0x3202
    harbor[14][2], harbor[14][3] = harbor[14][11], harbor[14][12]
    harbor_new = copy.deepcopy(harbor_meta)
    harbor_new["warp_events"] += [warp(2, 14, HE, 0, 0), warp(3, 14, HE, 1, 0)]
    assert harbor_new["warp_events"][:4] == harbor_meta["warp_events"]
    assert harbor_new["object_events"] == harbor_meta["object_events"]
    put("data/maps/SlateportCity_Harbor/map.json", enc(harbor_new))
    put(harbor_layout["blockdata_filepath"], pack(harbor))
    hp_path = "tools/hoenn_import/patches/SlateportCity_Harbor.json"
    hp = load(hp_path)
    assert hp["object_events"] == harbor_meta["object_events"]
    # The importer de-duplicates on .get('script'). Warp entries all have None;
    # provide the FULL list, so a future import cannot silently drop old warps.
    hp["warp_events"] = copy.deepcopy(harbor_new["warp_events"])
    hp["layout_overrides"] = [dict(x=2,y=14,before=0x3202,after=0x0206),
                              dict(x=3,y=14,before=0x3202,after=0x0207)]
    put(hp_path, enc(hp))
    hook_path = "tools/hoenn_import/apply_patches.py"
    put(hook_path, importer_hook(read(hook_path).decode()))

    def new_layout(name, template, grid, border):
        target = copy.deepcopy(template)
        target.update(id="LAYOUT_"+IDS[name], name=name+"_Layout",
                      border_filepath="data/layouts/"+name+"/border.bin",
                      blockdata_filepath="data/layouts/"+name+"/map.bin")
        assert target["id"] not in layout_by_id
        layouts["layouts"].append(target)
        put(target["border_filepath"], border)
        put(target["blockdata_filepath"], pack(grid))
        return target

    new_layout(HE, he_layout, he, air_border)
    put("data/maps/"+HE+"/map.json", enc(he_meta))
    put("data/maps/"+HE+"/scripts.inc", HE+"_MapScripts::\n\t.byte 0\n\n"+HE+
        "_Guide::\n\tmsgbox "+HE+"_Text_Guide, MSGBOX_NPC\n\tend\n")
    put("data/maps/"+HE+"/text.inc", HE+'_Text_Guide::\n'
        '    .string "The terminal is east of the runway.\\n"\n'
        '    .string "The south exit returns to the harbor.\\p"\n'
        '    .string "CAPTAIN STERN and the ships still\\n"\n'
        '    .string "use the harbor beside us.$"\n')

    for name, exterior, exterior_door, region, return_label in (
        (JT, AIR, 0, air_meta["region_map_section"], AIR+"_ReturnClerk"),
        (HT, HE, 2, "MAPSEC_SLATEPORT_CITY", "SlateportCity_Harbor_EventScript_AirlineClerk")):
        terminal = copy.deepcopy(kt_meta)
        terminal.update(id="MAP_"+IDS[name], name=name, layout="LAYOUT_"+IDS[name],
            region_map_section=region, connections=None, coord_events=[], bg_events=[],
            warp_events=[warp(12, 9, exterior, exterior_door),
                         warp(13, 9, exterior, exterior_door)])
        terminal["object_events"] = [obj("UNION_ROOM_RECEPTIONIST", 6, 5, return_label)]
        terminal["object_events"] += [obj("UNION_ROOM_RECEPTIONIST", x, 5, name+"_Info")
                                      for x in (10, 14, 18)]
        terminal["object_events"] += [obj("AIRPLANE_SMALL", 27, 1, "0x0"),
                                     obj("BOY", 30, 2, name+"_Window", "FACE_UP")]
        new_layout(name, kt_layout, terminal_grid, terminal_border)
        put("data/maps/"+name+"/map.json", enc(terminal))
        put("data/maps/"+name+"/scripts.inc", name+"_MapScripts::\n\t.byte 0\n\n"+
            name+"_Info::\n\tmsgbox "+name+"_Text_Info, MSGBOX_NPC\n\tend\n\n"+
            name+"_Window::\n\tmsgbox "+name+"_Text_Window, MSGBOX_NPC\n\tend\n")
        put("data/maps/"+name+"/text.inc", name+'_Text_Info::\n'
            '    .string "The west counter handles flights\\n"\n'
            '    .string "back to VERMILION AIRPORT.\\p"\n'
            '    .string "The return service is free.\\n"\n'
            '    .string "Use the south doors to go outside.$"\n\n'+name+'_Text_Window::\n'
            '    .string "You can watch the runway through\\n"\n'
            '    .string "this window. Boarding is at the desk.$"\n')

    groups["gMapGroup_JohtoEntry"].append(JT)
    groups["gMapGroup_HoennIndoorSlateport"] += [HE, HT]
    assert groups["group_order"] == before_groups["group_order"]
    for group in groups["group_order"]:
        assert groups[group][:len(before_groups[group])] == before_groups[group]
        assert len(groups[group]) < 256
    assert layouts["layouts"][:len(before_layouts["layouts"])] != before_layouts["layouts"]
    for old, new in zip(before_layouts["layouts"], layouts["layouts"]):
        if old.get("id") == old_air_layout["id"]:
            assert dict(new, width=32) == old
        else:
            assert new == old
    put("data/layouts/layouts.json", enc(layouts))
    put("data/maps/map_groups.json", enc(groups))

    event_source = read("data/event_scripts.s").decode()
    for name in (JT, HE, HT):
        for suffix in ("scripts.inc", "text.inc"):
            line = '\t.include "data/maps/'+name+'/'+suffix+'"'
            assert line not in event_source
            event_source += "\n"+line+"\n"
    put("data/event_scripts.s", event_source)
    movement = read("src/event_object_movement.c").decode()
    anchor = ("    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_KANTO_AIRPORT)\n"
              "     && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_KANTO_AIRPORT)\n"
              "     && objEvent->graphicsId != OBJ_EVENT_GFX_AIRPLANE_SMALL")
    assert movement.count(anchor) == 1, "Current airport window predicate changed; review fresh source"
    replacement = ("    if (((gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_KANTO_AIRPORT)\n"
        "       && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_KANTO_AIRPORT))\n"
        "      || (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_JOHTO_AIRPORT_TERMINAL)\n"
        "       && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_JOHTO_AIRPORT_TERMINAL))\n"
        "      || (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_HOENN_AIRPORT_TERMINAL)\n"
        "       && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_HOENN_AIRPORT_TERMINAL)))\n"
        "     && objEvent->graphicsId != OBJ_EVENT_GFX_AIRPLANE_SMALL")
    put("src/event_object_movement.c", movement.replace(anchor, replacement, 1))

    evidence.update(airstrip_old_32_columns_identical=True,
        old_map_group_indices_preserved=True, old_layout_indices_preserved=True,
        old_harbor_four_warps_and_npcs_preserved=True,
        flight_destinations_and_return_scripts_unchanged=True,
        save_fields_or_story_flags_added=False, kanto_taxi_triggers_not_copied=True,
        static_reachable_counts=dict(
            johto=paths(air, (22, 12), [(22,0), (43,12), (door_x,door_y)],
                        [(o["x"],o["y"]) for o in air_meta["object_events"]]),
            hoenn=paths(he, (22,23), [(23,23),(he_door_x,door_y)], [(26,15)]),
            harbor=paths(harbor, (12,13), [(2,14),(3,14),(11,14),(12,14)],
                         [(o["x"],o["y"]) for o in harbor_meta["object_events"]]),
            terminal=paths(terminal_grid, (12,9), [(6,6),(13,9),(30,3)])),
        static_only=True, compiled=False, emulator_executed=False)
    return inputs, output, evidence


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--facade-rect", type=int, nargs=4, required=True,
                    metavar=("X", "Y", "W", "H"))
    ap.add_argument("--rom", type=Path)
    args = ap.parse_args()
    root = args.root.resolve(strict=True); out = args.out.resolve()
    assert not out.exists() and not out.is_relative_to(root), "Write only a NEW separate candidate folder"
    rom = args.rom.read_bytes() if args.rom else None
    inputs, payload, evidence = build(root, args.facade_rect, rom)
    # Ship the deterministic recipe alongside its concrete payload. It does not
    # alter the old historical Johto generators or any Route29/Misty input.
    payload["tools/airports/build_regional_airport_terminals.py"] = Path(__file__).read_bytes()
    manifest = dict(kind="unapplied_regional_airport_candidate", product_edits=False,
                    inputs=inputs, evidence=evidence,
                    rom_sha256=sha(rom) if rom is not None else None, files={})
    for rel, blob in payload.items():
        p = out / "payload" / rel; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(blob)
        before = inputs.get(rel)
        assert before is not None or not (root / rel).exists(), ("Untracked existing target",rel)
        manifest["files"][rel] = dict(before=before, bytes=len(blob), sha256=sha(blob))
    (out / "manifest.json").write_bytes(enc(manifest))
    print(json.dumps(dict(out=str(out), files=len(payload), evidence=evidence), indent=2))


if __name__ == "__main__":
    main()
