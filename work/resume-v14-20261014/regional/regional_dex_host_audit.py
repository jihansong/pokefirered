#!/usr/bin/env python3
"""Compile and run the actual regional mapping/list/number C bodies in a host shim.

This is a source-unit check, not an emulator, a ROM attachment check, a SAVE test,
or a fresh-play story check. It never writes product source or battery saves.
Every extracted source/header must be in the supplied SHA256 guard manifest.
The graphics/text-printer adapters only record the final number; other tested
bodies, national/species conversion tables, and list-order tables are verbatim.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

REQUIRED = (
    "src/pokedex.c", "src/pokedex_screen.c", "src/pokemon.c",
    "src/data/pokemon/johto_dex_order.h", "src/data/pokemon/pokedex_orders.h",
    "include/pokedex.h", "include/pokedex_screen.h",
    "include/constants/pokedex.h", "include/constants/species.h",
    "include/constants/flags.h", "include/constants/flags_hoenn_story.h",
    "include/constants/flags_johto_story.h",
)
STORY_FLAGS = (
    "FLAG_HOENN_BIRCH_RESCUED", "FLAG_HOENN_MET_STERN",
    "FLAG_JOHTO_ARRIVAL_BRIEFED", "FLAG_JOHTO_MET_LAB_ASSISTANT",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def balanced_definition(source: str, pattern: str) -> str:
    matches = list(re.finditer(pattern, source, re.M))
    if len(matches) != 1:
        raise AssertionError(f"Expected one actual definition: {pattern}: {len(matches)}")
    start = matches[0].start()
    left = source.index("{", matches[0].end() - 1)
    depth = 0
    state = "normal"
    idx = left
    while idx < len(source):
        c, n = source[idx], source[idx:idx + 2]
        if state == "line":
            if c == "\n": state = "normal"
        elif state == "block":
            if n == "*/": state = "normal"; idx += 1
        elif state in ("string", "char"):
            if c == "\\": idx += 1
            elif c == ('"' if state == "string" else "'"): state = "normal"
        elif n == "//": state = "line"; idx += 1
        elif n == "/*": state = "block"; idx += 1
        elif c == '"': state = "string"
        elif c == "'": state = "char"
        elif c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = idx + 1
                if source[end:end + 1] == ";": end += 1
                return source[start:end]
        idx += 1
    raise AssertionError("Unclosed actual C definition")


def function(source: str, name: str) -> str:
    return balanced_definition(source, rf"^(?:static\s+)?(?:u\d+|s\d+|bool\d+|void|int)\s+{re.escape(name)}\([^;{{]*\)\s*\{{")


def constant_values(sources: list[str], requested: tuple[str, ...]) -> dict[str, int]:
    defines = {}
    for text in sources:
        for m in re.finditer(r"^#define\s+(\w+)\s+([^\n]+)", text, re.M):
            value = re.sub(r"//.*|/\*.*?\*/", "", m.group(2)).strip()
            if m.group(1) in defines and defines[m.group(1)] != value:
                raise AssertionError(f"Conflicting macro {m.group(1)}")
            defines[m.group(1)] = value
    memo = {}

    def expr(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, int): return node.value
        if isinstance(node, ast.Name): return get(node.id)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub): return -expr(node.operand)
        if isinstance(node, ast.BinOp):
            a, b = expr(node.left), expr(node.right)
            ops = {ast.Add: lambda: a + b, ast.Sub: lambda: a - b,
                   ast.BitOr: lambda: a | b, ast.BitAnd: lambda: a & b,
                   ast.LShift: lambda: a << b, ast.RShift: lambda: a >> b}
            if type(node.op) in ops: return ops[type(node.op)]()
        raise AssertionError(f"Unsupported flag macro expression: {ast.dump(node)}")

    def get(name):
        if name not in memo:
            if name not in defines: raise AssertionError(f"Missing current macro dependency: {name}")
            memo[name] = expr(ast.parse(defines[name], mode="eval").body)
        return memo[name]
    return {name: get(name) for name in requested}


PREAMBLE = r'''
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32;
typedef int8_t s8; typedef int16_t s16; typedef int32_t s32;
typedef u8 bool8; typedef u16 bool16; typedef u32 bool32;
#define TRUE 1
#define FALSE 0
#include "constants/pokedex.h"
#include "constants/species.h"
#include "pokedex.h"
#include "pokedex_screen.h"
#define SPECIES_TO_NATIONAL(name) [SPECIES_##name - 1] = NATIONAL_DEX_##name
#define HOENN_TO_NATIONAL(name) [HOENN_DEX_##name - 1] = NATIONAL_DEX_##name
struct ListMenuItem { const u8 *label; s32 index; };
static unsigned storyMask;
static unsigned flagReadCount;
static unsigned FlagGet(u16 flag) {
    flagReadCount++;
    for (unsigned i = 0; i < 4; ++i)
        if (flag == storyFlagIds[i]) return !!(storyMask & (1u << i));
    fprintf(stderr, "Unexpected flag read %u\n", flag); abort();
}
'''

SCREEN_SHIM = r'''
static struct PokedexScreenData screen;
static struct PokedexScreenData *sPokedexScreenData = &screen;
static struct ListMenuItem items[NATIONAL_DEX_COUNT];
static const u8 gSpeciesNames[NUM_SPECIES][1] = {{0}};
static const u8 gText_5Dashes[] = "-----";
static const u8 gText_PokedexNo[] = "No.";
struct ShimDexBits { u8 seen[64], owned[64]; };
struct ShimSave2 { struct ShimDexBits pokedex; };
struct ShimSave1 { u8 seen1[64], seen2[64]; };
static struct ShimSave2 save2;
static struct ShimSave1 save1;
static struct ShimSave2 *gSaveBlock2Ptr = &save2;
static struct ShimSave1 *gSaveBlock1Ptr = &save1;
static u16 printedNumber;
static void DexScreen_AddTextPrinterParameterized(u8 a, u8 b, const u8 *c, u8 d, u8 e, u8 f) {
    (void)a; (void)b; (void)c; (void)d; (void)e; (void)f;
}
static void DexScreen_PrintNum3LeadingZeroes(u8 a, u8 b, u16 n, u8 d, u8 e, u8 f) {
    (void)a; (void)b; (void)d; (void)e; (void)f; printedNumber = n;
}
'''

TESTS = r'''
int main(void) {
    const u16 expectedCounts[] = {151, 251, 202};
    const u16 flagsBefore[] = {storyFlagIds[0], storyFlagIds[1], storyFlagIds[2], storyFlagIds[3]};
    unsigned mappingChecks = 0, listChecks = 0, printChecks = 0;
    screen.listItems = items;
    for (unsigned mask = 0; mask < 16; ++mask) {
        storyMask = mask;
        unsigned expected = (mask & 3) ? STORY_DEX_HOENN : (mask & 12) ? STORY_DEX_JOHTO : STORY_DEX_KANTO;
        assert(GetStoryRegionalDex() == expected);
    }
    for (unsigned region = 0; region < 3; ++region) {
        u8 used[NATIONAL_DEX_COUNT + 1] = {0};
        assert(GetRegionalDexCount(region) == expectedCounts[region]);
        assert(RegionalDexToNational(region, 0) == 0);
        assert(RegionalDexToNational(region, expectedCounts[region] + 1) == 0);
        assert(RegionalDexToNational(region, UINT16_MAX) == 0);
        assert(NationalToRegionalDex(region, 0) == 0);
        assert(NationalToRegionalDex(region, NATIONAL_DEX_COUNT + 1) == 0);
        assert(NationalToRegionalDex(region, UINT16_MAX) == 0);
        for (unsigned regional = 1; regional <= expectedCounts[region]; ++regional) {
            u16 nat = RegionalDexToNational(region, regional);
            assert(nat > 0 && nat <= NATIONAL_DEX_COUNT && !used[nat]);
            used[nat] = 1;
            assert(NationalToRegionalDex(region, nat) == regional);
            if (region == STORY_DEX_KANTO) assert(nat == regional);
            if (region == STORY_DEX_JOHTO) assert(nat <= 251);
            assert(SpeciesToNationalPokedexNum(NationalPokedexNumToSpecies(nat)) == nat);
            mappingChecks++;
        }
        if (region == STORY_DEX_JOHTO)
            for (unsigned nat = 1; nat <= 251; ++nat) assert(used[nat]);
        storyMask = region == STORY_DEX_KANTO ? 0 : region == STORY_DEX_JOHTO ? 4 : 1;
        for (unsigned fixture = 0; fixture < 3; ++fixture) {
            memset(&save1, 0, sizeof(save1)); memset(&save2, 0, sizeof(save2));
            for (unsigned nat = 1; nat <= NATIONAL_DEX_COUNT; ++nat) {
                unsigned selected = fixture == 1 || (fixture == 2 && (nat % 13 == 0 || nat == 1 || nat == 251 || nat == 386));
                if (selected) {
                    unsigned idx = (nat - 1) / 8, bit = 1u << ((nat - 1) % 8);
                    save2.pokedex.seen[idx] |= bit;
                    save1.seen1[idx] |= bit; save1.seen2[idx] |= bit;
                    if (fixture == 1 || nat % 2 == 0) save2.pokedex.owned[idx] |= bit;
                }
            }
            struct ShimSave1 old1 = save1; struct ShimSave2 old2 = save2;
            DexScreen_InitRegionalView();
            assert(screen.regionalDex == region && !screen.showNationalNumbers);
            for (unsigned nat = 1; nat <= NATIONAL_DEX_COUNT; ++nat) {
                assert(DexScreen_IsRegionalMon(nat) == !!used[nat]);
                assert(screen.regionalNumberByNational[nat] == NationalToRegionalDex(region, nat));
                u16 species = NationalPokedexNumToSpecies(nat);
                assert(species > 0 && species < NUM_SPECIES);
                for (unsigned nationalMode = 0; nationalMode < 2; ++nationalMode) {
                    screen.showNationalNumbers = nationalMode;
                    printedNumber = UINT16_MAX;
                    DexScreen_PrintMonDexNo(0, 0, species, 0, 0);
                    u16 expected = nationalMode || !used[nat] ? nat : screen.regionalNumberByNational[nat];
                    assert(printedNumber == expected); printChecks++;
                }
            }
            screen.showNationalNumbers = FALSE;
            for (unsigned order = 0; order < 6; ++order) {
                memset(items, 0xAB, sizeof(items));
                unsigned count = DexScreen_CountMonsInOrderedList(order);
                assert(count >= 1 && count <= NATIONAL_DEX_COUNT);
                if (!fixture) assert(count == 1 && items[0].index == SPECIES_NONE);
                else if (fixture == 1)
                    assert(count == (order == DEX_ORDER_NUMERICAL_NATIONAL ? NATIONAL_DEX_COUNT : expectedCounts[region]));
                for (unsigned row = 0; row < count; ++row) {
                    u16 species = (u16)items[row].index;
                    if (species == SPECIES_NONE) { assert(!fixture || count == 1); continue; }
                    assert(species < NUM_SPECIES);
                    u16 nat = SpeciesToNationalPokedexNum(species);
                    assert(nat > 0 && nat <= NATIONAL_DEX_COUNT);
                    if (order != DEX_ORDER_NUMERICAL_NATIONAL) assert(used[nat]);
                    if (order == DEX_ORDER_NUMERICAL_KANTO) assert(nat == RegionalDexToNational(region, row + 1));
                    if (order == DEX_ORDER_NUMERICAL_NATIONAL) assert(nat == row + 1);
                    assert(((u32)items[row].index >> 16 & 1) == (unsigned)DexScreen_GetSetPokedexFlag(nat, FLAG_GET_SEEN, FALSE));
                    assert(((u32)items[row].index >> 17 & 1) == (unsigned)DexScreen_GetSetPokedexFlag(nat, FLAG_GET_CAUGHT, FALSE));
                }
                listChecks++;
            }
            assert(!memcmp(&save1, &old1, sizeof(save1)));
            assert(!memcmp(&save2, &old2, sizeof(save2)));
        }
    }
    assert(!memcmp(flagsBefore, storyFlagIds, sizeof(flagsBefore)));
    puts("SOURCE_UNIT_PASS");
    printf("mapping_checks=%u list_fixtures=%u number_checks=%u story_masks=16\n", mappingChecks, listChecks, printChecks);
    return 0;
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--guard-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cc", default="cc")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    report = {"status": "NOT_EXECUTED", "scope": "actual C source-unit checks with host graphics/save shims",
              "native_emulator_pass": False, "rom_attachment_verified": False,
              "full_story_playthrough": False, "battery_save_tested": False,
              "product_source_modified": False, "original_save_modified": False,
              "required": list(REQUIRED), "guard_manifest_sha256": digest(args.guard_manifest)}
    try:
        guard = json.loads(args.guard_manifest.read_text(encoding="utf-8-sig"))
        guard = guard.get("files", guard)
        texts, hashes = {}, {}
        for rel in REQUIRED:
            expected = guard.get(rel)
            if isinstance(expected, dict): expected = expected.get("sha256")
            if not isinstance(expected, str) or not re.fullmatch("[a-f0-9]{64}", expected):
                raise AssertionError(f"Missing trusted snapshot hash for {rel}")
            path = args.repo / rel
            observed = digest(path)
            if observed != expected: raise AssertionError(f"Current-source hash mismatch: {rel}")
            hashes[rel] = observed
            texts[rel] = path.read_text(encoding="utf-8")
        report["source_sha256"] = hashes
        flags = constant_values([texts[p] for p in REQUIRED if "/flags" in p], STORY_FLAGS)
        if len(set(flags.values())) != 4: raise AssertionError("Story flags alias each other")
        report["story_flag_ids"] = flags
        c = PREAMBLE.replace("static unsigned storyMask;", "\n".join(
            [f"#define {name} {value}" for name, value in flags.items()]
            + ["static const u16 storyFlagIds[] = {" + ",".join(map(str, flags.values())) + "};", "static unsigned storyMask;"]))
        pokemon = texts["src/pokemon.c"]
        for name in ("sSpeciesToNationalPokedexNum", "sHoennToNationalOrder"):
            c += "\n" + balanced_definition(pokemon, rf"^static const u16 {name}\[[^\]]+\]\s*=\s*\{{") + "\n"
        for name in ("NationalPokedexNumToSpecies", "SpeciesToNationalPokedexNum", "HoennToNationalOrder"):
            c += function(pokemon, name) + "\n"
        c += '#include "data/pokemon/johto_dex_order.h"\n#include "data/pokemon/pokedex_orders.h"\n'
        for name in ("GetStoryRegionalDex", "GetRegionalDexCount", "RegionalDexToNational", "NationalToRegionalDex"):
            c += function(texts["src/pokedex.c"], name) + "\n"
        screen_source = texts["src/pokedex_screen.c"]
        c += balanced_definition(screen_source, r"^struct PokedexScreenData\s*\{") + "\n" + SCREEN_SHIM
        for name in ("DexScreen_InitRegionalView", "DexScreen_IsRegionalMon", "DexScreen_GetSetPokedexFlag",
                     "DexScreen_CountMonsInOrderedList", "DexScreen_PrintMonDexNo"):
            c += function(screen_source, name) + "\n"
        c += TESTS
        generated = args.out / "actual-regional-dex-source-unit.c"
        generated.write_text(c, encoding="utf-8")
        report["generated_c_sha256"] = digest(generated)
        if args.generate_only:
            report["status"] = "GENERATED_NOT_COMPILED"
        else:
            cc = shutil.which(args.cc)
            if not cc: raise AssertionError(f"Host C compiler unavailable: {args.cc}")
            binary = args.out / "actual-regional-dex-source-unit"
            proc = subprocess.run([cc, "-std=c99", "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined",
                                   "-fno-omit-frame-pointer", "-I", str(args.repo / "include"), "-I", str(args.repo / "src"),
                                   str(generated), "-o", str(binary)], capture_output=True, text=True, timeout=60)
            report["compile"] = {"exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
            if proc.returncode: raise AssertionError("Actual C source-unit compilation failed")
            proc = subprocess.run([str(binary.resolve())], capture_output=True, text=True, timeout=30)
            report["execution"] = {"exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
            if proc.returncode or "SOURCE_UNIT_PASS" not in proc.stdout: raise AssertionError("Actual C source-unit execution failed")
            report["status"] = "SOURCE_UNIT_PASS"
    except Exception as exc:
        report["status"] = "SOURCE_UNIT_FAILED"
        report["error"] = f"{type(exc).__name__}: {exc}"
    (args.out / "validation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "scope", "native_emulator_pass")}))
    if report["status"] == "SOURCE_UNIT_FAILED": raise SystemExit(1)


if __name__ == "__main__":
    main()
