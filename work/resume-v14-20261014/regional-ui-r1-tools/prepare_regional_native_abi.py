#!/usr/bin/env python3
"""Build a current-source ARM layout probe and bind actual ELF UI symbols.

Only --out is written; product source, ROM, ELF and battery saves are read only.
Uses the original private PokedexScreenData and STARTMENU enum definitions, not
transcribed offsets. The probe runs no game function and injects no emulator RAM.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess

REQUIRED = ["src/pokedex.c", "src/pokedex_screen.c", "src/pokemon.c", "src/start_menu.c", "src/list_menu.c",
            "include/global.h", "include/pokedex.h", "include/pokedex_screen.h", "include/task.h", "include/list_menu.h",
            "include/constants/pokedex.h", "include/constants/species.h", "include/constants/flags.h",
            "include/constants/flags_johto_story.h", "include/constants/flags_hoenn_story.h",
            "src/data/pokemon/johto_dex_order.h", "src/data/pokemon/pokedex_orders.h"]
PKD_FIELDS = ["taskId", "state", "regionalDex", "showNationalNumbers", "regionalNumberByNational", "listItems",
              "orderedDexCount", "dexOrderId", "modeSelectListMenuId", "orderedListMenuTaskId", "dexSpecies",
              "modeSelectItems", "numSeenKanto", "numOwnedKanto", "numSeenNational", "numOwnedNational"]
LAYOUT = {"pokedex": ("PokedexScreenData", None), "task": ("Task", None), "task.func": ("Task", "func"),
          "task.active": ("Task", "isActive"), "task.data": ("Task", "data"),
          "list": ("ListMenu", None), "list.template": ("ListMenu", "template"),
          "list.cursor": ("ListMenu", "cursorPos"), "list.above": ("ListMenu", "itemsAbove"),
          "template": ("ListMenuTemplate", None), "template.items": ("ListMenuTemplate", "items"),
          "template.total": ("ListMenuTemplate", "totalItems"),
          "item": ("ListMenuItem", None), "item.index": ("ListMenuItem", "index"), "item.label": ("ListMenuItem", "label")}
LAYOUT.update({"pokedex." + n: ("PokedexScreenData", n) for n in PKD_FIELDS})
CONSTANTS = ["STARTMENU_POKEDEX", "MAX_STARTMENU_ITEMS", "DEX_ORDER_NUMERICAL_KANTO", "DEX_ORDER_NUMERICAL_NATIONAL",
             "DEX_CATEGORY_COUNT", "NATIONAL_DEX_COUNT", "JOHTO_DEX_COUNT", "HOENN_DEX_COUNT", "KANTO_DEX_COUNT",
             "NUM_SPECIES", "NUM_TASKS"]
OWNERS = {"sPokedexScreenData": "pokedex_screen.c", "Task_PokedexScreen": "pokedex_screen.c",
          "Task_DexScreen_NumericalOrder": "pokedex_screen.c", "Task_DexScreen_ShowMonPage": "pokedex_screen.c",
          "sText_DexTitleKanto": "pokedex_screen.c", "sText_DexTitleJohto": "pokedex_screen.c",
          "sText_DexTitleHoenn": "pokedex_screen.c", "sText_DexOrderJohto": "pokedex_screen.c",
          "sText_DexOrderHoenn": "pokedex_screen.c", "sNumStartMenuItems": "start_menu.c",
          "sStartMenuOrder": "start_menu.c", "sStartMenuCursorPos": "start_menu.c",
          "ListMenuDummyTask": "list_menu.c", "sHoennToNationalOrder": "pokemon.c",
          "sSpeciesToNationalPokedexNum": "pokemon.c", "sJohtoToNationalOrder": "pokedex.c"}
FUNCTIONS = {"Task_PokedexScreen", "Task_DexScreen_NumericalOrder", "Task_DexScreen_ShowMonPage", "ListMenuDummyTask"}
RAM_OBJECTS = {"sPokedexScreenData", "sNumStartMenuItems", "sStartMenuOrder", "sStartMenuCursorPos", "gTasks"}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Elf32:
    def __init__(self, path):
        self.raw = Path(path).read_bytes()
        assert self.raw[:7] == b"\x7fELF\x01\x01\x01"
        head = struct.unpack_from("<HHIIIIIHHHHHH", self.raw, 16)
        assert head[1] == 40 and head[10] >= 40
        assert head[5] + head[10] * head[11] <= len(self.raw)
        self.sections = [struct.unpack_from("<10I", self.raw, head[5] + i * head[10]) for i in range(head[11])]
        self.symbols = {}
        for sec in self.sections:
            if sec[1] != 2: continue
            assert sec[9] >= 16 and sec[5] % sec[9] == 0
            ss = self.sections[sec[6]]
            strings = self.raw[ss[4]:ss[4] + ss[5]]
            assert sec[4] + sec[5] <= len(self.raw)
            owner = None
            for i in range(0, sec[5], sec[9]):
                no, value, size, info, other, section = struct.unpack_from("<IIIBBH", self.raw, sec[4] + i)
                assert no < len(strings)
                end = strings.find(b"\0", no); assert end >= 0
                name = strings[no:end].decode()
                if info & 15 == 4: owner = name
                elif name and section:
                    self.symbols.setdefault(name, []).append({"value": value, "size": size, "section": section,
                                                              "info": info, "translation_unit": owner,
                                                              "symbol_index": i // sec[9]})

    def bind(self, name, owner=None):
        rows = self.symbols.get(name, [])
        if owner:
            rows = [r for r in rows if (r["translation_unit"] or "").replace("\\", "/").rsplit("/", 1)[-1] == owner]
        assert len(rows) == 1, ("missing/ambiguous current source-owned symbol", name, rows)
        row = rows[0]
        assert row["section"] < len(self.sections), ("non-section symbol", name, row)
        sec = self.sections[row["section"]]
        address = row["value"] & ~1 if row["info"] & 15 == 2 else row["value"]
        assert sec[3] <= address and address + row["size"] <= sec[3] + sec[5], (name, row, sec)
        return row


def main():
    ap = argparse.ArgumentParser()
    for name in ("root", "rom", "elf", "guard-manifest", "out"):
        ap.add_argument("--" + name, type=Path, required=True)
    ap.add_argument("--dka", type=Path, default=Path(os.environ.get("DEVKITARM", "/opt/devkitpro/devkitARM")))
    args = ap.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    assert out.is_relative_to(root / "work") and not out.exists()
    guard = json.loads(args.guard_manifest.read_text())
    guard = guard.get("files", guard)
    hashes = {}
    for rel in REQUIRED:
        expected = guard.get(rel)
        if isinstance(expected, dict): expected = expected["sha256"]
        assert expected and sha(root / rel) == expected, ("current source guard", rel)
        hashes[rel] = expected
    source = (root / "src/pokedex_screen.c").read_text()
    matched = re.findall(r"^struct PokedexScreenData\s*\{[\s\S]*?^\};", source, re.M)
    assert len(matched) == 1
    start_source = (root / "src/start_menu.c").read_text()
    enums = re.findall(r"^enum(?:\s+\w+)?\s*\{[\s\S]*?^\};", start_source, re.M)
    enums = [enum for enum in enums if "STARTMENU_POKEDEX = 0" in enum]
    assert len(enums) == 1
    list_source = (root / "src/list_menu.c").read_text()
    assert "struct ListMenu *list = (struct ListMenu *)gTasks[listTaskId].data;" in list_source
    out.mkdir(parents=True)
    lines = ['#include "global.h"', '#include "pokedex_screen.h"', '#include "task.h"', '#include "list_menu.h"',
             '#include "constants/pokedex.h"', '#include "constants/species.h"', matched[0], enums[0]]
    names = {}
    for index, (key, (typ, member)) in enumerate(LAYOUT.items()):
        sym = f"qa_{index}"
        expr = f"sizeof(struct {typ})" if member is None else f"offsetof(struct {typ}, {member})"
        lines.append(f"char {sym}[{expr} + 1];"); names[sym] = ("offsets", key)
    for index, name in enumerate(CONSTANTS):
        sym = f"qc_{index}"
        lines.append(f"char {sym}[{name} + 1];"); names[sym] = ("constants", name)
    probe = out / "actual-regional-ui-layout-probe.c"
    probe.write_text("\n".join(lines) + "\n")
    obj = out / "actual-regional-ui-layout-probe.o"
    flags = ["-c", "-w", "-mthumb", "-mabi=apcs-gnu", "-march=armv4t", "-fcommon", "-iquote", "include",
             "-DLEAFGREEN", "-DREVISION=0", "-DENGLISH", "-DMODERN=1"]
    compile_result = subprocess.run([str(args.dka / "bin/arm-none-eabi-gcc"), *flags, str(probe), "-o", str(obj)],
                                    cwd=root, capture_output=True, text=True, timeout=60)
    (out / "compile.json").write_text(json.dumps({"exit_code": compile_result.returncode, "stderr": compile_result.stderr}, indent=2))
    assert compile_result.returncode == 0, compile_result.stderr
    listing = subprocess.check_output([str(args.dka / "bin/arm-none-eabi-nm"), "-S", str(obj)], text=True)
    report = {"rom_sha256": sha(args.rom), "elf_sha256": sha(args.elf), "source_sha256": hashes,
              "guard_manifest_sha256": sha(args.guard_manifest), "probe_c_sha256": sha(probe),
              "probe_method": "verbatim private UI structure and enum + current ARM compiler offsetof/sizeof",
              "compiler_flags": flags, "offsets": {}, "constants": {}, "symbols": {},
              "native_executed": False, "product_changed": False}
    for line in listing.splitlines():
        v = line.split()
        if len(v) == 4 and v[3] in names:
            group, key = names[v[3]]; report[group][key] = int(v[1], 16) - 1
    assert set(report["offsets"]) == set(LAYOUT) and set(report["constants"]) == set(CONSTANTS)
    assert report["offsets"]["item"] == 8 and report["offsets"]["task"] == 40
    assert report["offsets"]["list"] <= 32 and report["constants"]["NATIONAL_DEX_COUNT"] == 386
    elf = Elf32(args.elf)
    for name in [*OWNERS, "gTasks"]:
        bound = elf.bind(name, OWNERS.get(name))
        kind = 2 if name in FUNCTIONS else 1
        assert bound["info"] & 15 == kind, (name, bound)
        address = bound["value"] & ~1 if kind == 2 else bound["value"]
        if name in RAM_OBJECTS:
            assert 0x02000000 <= address < 0x02040000 or 0x03000000 <= address < 0x03008000
        else: assert 0x08000000 <= address and address + bound["size"] <= 0x08000000 + args.rom.stat().st_size
        report["symbols"][name] = bound
    symbols, c = report["symbols"], report["constants"]
    assert symbols["sPokedexScreenData"]["size"] == 4
    assert symbols["sNumStartMenuItems"]["size"] == symbols["sStartMenuCursorPos"]["size"] == 1
    assert symbols["sStartMenuOrder"]["size"] == c["MAX_STARTMENU_ITEMS"]
    assert symbols["gTasks"]["size"] == report["offsets"]["task"] * c["NUM_TASKS"]
    assert symbols["sJohtoToNationalOrder"]["size"] == c["JOHTO_DEX_COUNT"] * 2
    assert symbols["sHoennToNationalOrder"]["size"] == symbols["sSpeciesToNationalPokedexNum"]["size"] == (c["NUM_SPECIES"] - 1) * 2
    (out / "regional-native-ui-abi.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "ABI_PREPARED", "pokedex_struct_size": report["offsets"]["pokedex"], "symbols_bound": len(symbols), "native_executed": False}))


if __name__ == "__main__": main()
