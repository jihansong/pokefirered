#!/usr/bin/env python3
"""Rebuild the Kanto/Sevii slots of src/data/wild_encounters.json from habitats.py.

    python3 tools/dex_habitat/apply_habitats.py            # rewrite the json
    python3 tools/dex_habitat/apply_habitats.py --table    # print the doc table

The Yellow (Kanto) and LeafGreen (Sevii) tables as they were before the dex
completion work come from git (commit f1afbe4bb's parent). Every Kanto/Sevii
table is reset to them, the morning/night tables are dropped, and the rows in
habitats.py are applied again. Hoenn tables are not touched.
"""
import argparse
import copy
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from habitats import HABITATS  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JSON_PATH = os.path.join(ROOT, "src", "data", "wild_encounters.json")
BASE_REV = "f1afbe4bb^"

TABLE_KEYS = {"land": "land_mons", "water": "water_mons", "fishing": "fishing_mons", "rock_smash": "rock_smash_mons"}
RATES = {
    "land_mons": [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1],
    "water_mons": [60, 30, 5, 4, 1],
    "rock_smash_mons": [60, 30, 5, 4, 1],
    "fishing_mons": [70, 30, 60, 20, 20, 40, 40, 15, 4, 1],
}
TOD_KEYS = ("land_mons_morning", "land_mons_night", "water_mons_night", "fishing_mons_night")


def load_base():
    text = subprocess.run(["git", "-C", ROOT, "show", BASE_REV + ":src/data/wild_encounters.json"],
                          check=True, capture_output=True, text=True).stdout
    return json.loads(text)


def leafgreen_encounters(data):
    for group in data["wild_encounter_groups"]:
        if not group.get("for_maps"):
            continue
        for enc in group["encounters"]:
            if "FireRed" in enc.get("base_label", ""):
                continue
            yield enc


def set_slots(table, row, base_table):
    _, _, _, slots, species, levels, _ = row
    for i in slots:
        mon = table["mons"][i]
        mon["species"] = species
        if levels is not None:
            mon["min_level"], mon["max_level"] = levels
        elif base_table is not None:
            mon["min_level"] = base_table["mons"][i]["min_level"]
            mon["max_level"] = base_table["mons"][i]["max_level"]


def revert_slots(table, row, base_table):
    for i in row[3]:
        table["mons"][i] = copy.deepcopy(base_table["mons"][i])


def build(current, base):
    base_by_label = {e["base_label"]: e for e in leafgreen_encounters(base)}
    rows_by_map = {}
    for row in HABITATS:
        rows_by_map.setdefault(row[0], []).append(row)
    used = set()

    for enc in leafgreen_encounters(current):
        base_enc = base_by_label.get(enc["base_label"])
        if base_enc is None:
            continue  # Hoenn and other maps that did not exist before the dex work
        for key in TOD_KEYS:
            enc.pop(key, None)
        for key in TABLE_KEYS.values():
            if key in base_enc:
                enc[key] = copy.deepcopy(base_enc[key])
        rows = rows_by_map.get(enc["map"], [])
        if not rows:
            continue
        if enc["map"] in used:
            raise SystemExit("%s has more than one table" % enc["map"])
        used.add(enc["map"])

        for tkey, key in TABLE_KEYS.items():
            trows = [r for r in rows if r[1] == tkey]
            if not trows:
                continue
            base_table = base_enc[key]
            day = copy.deepcopy(base_table)
            for r in trows:
                if r[2] in ("all", "daymorn", "day"):
                    set_slots(day, r, base_table)
            # Every species of the original table must still appear
            left = {m["species"] for m in day["mons"]}
            for m in base_table["mons"]:
                if m["species"] not in left:
                    raise SystemExit("%s %s loses %s" % (enc["map"], key, m["species"]))
            enc[key] = day
            if any(r[2] in ("morning", "night", "day", "daymorn") for r in trows):
                if key != "land_mons" and any(r[2] != "night" and r[2] != "all" for r in trows):
                    raise SystemExit("%s: only land tables have a morning table" % enc["map"])
                morning = copy.deepcopy(day)
                night = copy.deepcopy(day)
                for r in trows:
                    if r[2] == "day":
                        revert_slots(morning, r, base_table)
                    if r[2] in ("day", "daymorn"):
                        revert_slots(night, r, base_table)
                for r in trows:
                    if r[2] == "morning":
                        set_slots(morning, r, base_table)
                    if r[2] == "night":
                        set_slots(night, r, base_table)
                if morning != day and key == "land_mons":
                    enc[key + "_morning"] = morning
                if night != day:
                    enc[key + "_night"] = night
        # Keep the key order the template and the older edits used
        order = ["map", "base_label", "land_mons", "land_mons_night", "land_mons_morning",
                 "water_mons", "water_mons_night", "rock_smash_mons", "fishing_mons", "fishing_mons_night"]
        items = sorted(enc.items(), key=lambda kv: order.index(kv[0]) if kv[0] in order else 99)
        enc.clear()
        enc.update(items)

    missing = set(rows_by_map) - used
    if missing:
        raise SystemExit("maps not found: %s" % ", ".join(sorted(missing)))
    return current


def pct(key, slots):
    rates = RATES[key.replace("_morning", "").replace("_night", "")]
    return sum(rates[i] for i in slots)


def method(tkey, slots):
    if tkey == "land":
        return "풀숲/동굴"
    if tkey == "water":
        return "파도타기"
    if tkey == "rock_smash":
        return "바위깨기"
    rods = {i: ("낡은낚싯대" if i < 2 else "좋은낚싯대" if i < 5 else "대단한낚싯대") for i in range(10)}
    return "/".join(sorted({rods[i] for i in slots}, key=["낡은낚싯대", "좋은낚싯대", "대단한낚싯대"].index))


WHEN = {"all": "하루 종일", "daymorn": "아침·낮", "day": "낮", "morning": "아침", "night": "밤"}


def print_table():
    print("| 포켓몬 | 맵 | 방식 | 시간대 | 칸(확률) | 레벨 | 근거 |")
    print("|---|---|---|---|---|---|---|")
    for m, tkey, when, slots, species, levels, source in HABITATS:
        name = species.replace("SPECIES_", "").capitalize().replace("_", " ")
        mapname = m.replace("MAP_", "")
        lv = "%d" % levels[0] if levels and levels[0] == levels[1] else ("%d-%d" % levels if levels else "칸 그대로")
        print("| %s | `%s` | %s | %s | %s (%d%%) | %s | %s |" % (
            name, mapname, method(tkey, slots), WHEN[when], ",".join(str(s) for s in slots),
            pct(TABLE_KEYS[tkey], slots), lv, source))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", action="store_true", help="print the markdown table instead")
    args = ap.parse_args()
    if args.table:
        print_table()
        return
    with open(JSON_PATH) as f:
        current = json.load(f)
    build(current, load_base())
    with open(JSON_PATH, "w") as f:
        f.write(json.dumps(current, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
