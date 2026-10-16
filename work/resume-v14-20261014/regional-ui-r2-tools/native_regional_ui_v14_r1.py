#!/usr/bin/env python3
"""Native Pokédex browsing and SAVE/cold Continue of the unwarped v1.4 copy.

No preboot fixtures, save-state loading, RAM writes, script calls, catches,
story changes, or product edits. A successful run covers only the region
actually unlocked in this player's battery, not all three story unlocks.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct
import sys
import traceback

ap = argparse.ArgumentParser()
for name in ("root", "rom", "elf", "sav", "out", "abi-json", "base-runner", "ui-abi", "ui-probe"):
    ap.add_argument("--" + name, type=Path, required=True)
for name in ("expect-sav-sha", "expect-base-runner-sha", "expect-ui-probe-sha"):
    ap.add_argument("--" + name, required=True)
task_cfg = ap.parse_args()
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(task_cfg.base_runner) == task_cfg.expect_base_runner_sha
assert digest(task_cfg.ui_probe) == task_cfg.expect_ui_probe_sha
base_source = task_cfg.base_runner.read_text()
cut = "\ntry:\n    e = Emu(str(rom), str(sav), sym='')"
assert base_source.count(cut) == 1
base_argv = ["v14-native-definitions"]
for name in ("root", "rom", "elf", "sav", "out", "abi-json", "expect-sav-sha"):
    base_argv += ["--" + name, str(getattr(task_cfg, name.replace("-", "_")))]
sys.argv = base_argv
ctx = {"__name__": "definitions_only", "__file__": str(task_cfg.base_runner)}
exec(compile(base_source.split(cut)[0], "<hash-verified-v14-continue-definitions>", "exec"), ctx)
root, rom, elf, sav, out, base_abi = [ctx[n] for n in ("root", "rom", "elf", "sav", "out", "abi")]
Emu, SaveFile, Blocks, checksum, off, const, syms, settle, native_save, snapshot, compact, invariant = [ctx[n] for n in (
    "Emu", "SaveFile", "Blocks", "checksum", "off", "const", "syms", "settle", "native_save", "snapshot", "compact", "invariant")]
ui_abi = json.loads(task_cfg.ui_abi.read_text())
assert digest(rom) == ui_abi["rom_sha256"] and digest(elf) == ui_abi["elf_sha256"]
for rel, value in ui_abi["source_sha256"].items():
    assert digest(root / rel) == value, ("Current UI source mismatch", rel)
spec = importlib.util.spec_from_file_location("verified_regional_ui_probe", task_cfg.ui_probe)
probe = importlib.util.module_from_spec(spec); spec.loader.exec_module(probe)
linked = probe.Elf32(elf)
for name, binding in ui_abi["symbols"].items():
    assert binding == linked.bind(name, probe.OWNERS.get(name)), ("UI ABI does not match actual current ELF", name)
    syms[name] = binding["value"]
O, C, S = [ui_abi[n] for n in ("offsets", "constants", "symbols")]
assert O["item"] == 8 and O["task"] == 40 and C["NATIONAL_DEX_COUNT"] == 386
assert C["DEX_ORDER_NUMERICAL_KANTO"] == 0 and C["DEX_ORDER_NUMERICAL_NATIONAL"] == 5
rom_bytes = rom.read_bytes()


def rom_u16_table(name):
    symbol = S[name]
    offset = symbol["value"] - 0x08000000
    assert 0 <= offset and offset + symbol["size"] <= len(rom_bytes) and symbol["size"] % 2 == 0
    return list(struct.unpack("<" + "H" * (symbol["size"] // 2), rom_bytes[offset:offset + symbol["size"]]))


species_to_national = rom_u16_table("sSpeciesToNationalPokedexNum")
national_to_species = {}
for index, national in enumerate(species_to_national):
    if 1 <= national <= C["NATIONAL_DEX_COUNT"]:
        assert national not in national_to_species
        national_to_species[national] = index + 1
assert set(national_to_species) == set(range(1, 387))
regional_orders = [list(range(1, C["KANTO_DEX_COUNT"] + 1)), rom_u16_table("sJohtoToNationalOrder"),
                   rom_u16_table("sHoennToNationalOrder")[:C["HOENN_DEX_COUNT"]]]
assert [len(x) for x in regional_orders] == [151, 251, 202]
protected = ctx["protected"]
protected.update({task_cfg.ui_abi.resolve(): digest(task_cfg.ui_abi), task_cfg.ui_probe.resolve(): digest(task_cfg.ui_probe),
                  task_cfg.base_runner.resolve(): digest(task_cfg.base_runner), Path(__file__).resolve(): digest(__file__)})
report = dict(pass_all=False, scope="Unmodified progression of updated v1.4: current regional/national UI, detail-page navigation, native SAVE/cold Continue",
              ROM_sha256=digest(rom), ELF_sha256=digest(elf), input_SAV_sha256=digest(sav),
              ui_abi_sha256=digest(task_cfg.ui_abi), base_abi_sha256=digest(base_abi),
              base_runner_sha256=digest(task_cfg.base_runner), ui_probe_sha256=digest(task_cfg.ui_probe),
              runner_sha256=digest(__file__),
              preboot_fixture_edits=0, RAM_writes=0, state_loads=0, direct_engine_calls=0,
              all_three_regions_tested=False, actual_story_unlock_events_tested=False,
              full_campaign_tested=False, DELTA_device_FPS_measured=False,
              rendered_frames_require_visual_review=True, stages=[])
e = None


def ram(address, size):
    assert size >= 0
    assert (0x02000000 <= address and address + size <= 0x02040000) or (0x03000000 <= address and address + size <= 0x03008000), ("Read outside native RAM", hex(address), size)
    return e.read(address, size)


def value(address, fmt):
    return struct.unpack("<" + fmt, ram(address, struct.calcsize("<" + fmt)))[0]


def ui():
    address = value(S["sPokedexScreenData"]["value"], "I")
    if not address: return None
    data = ram(address, O["pokedex"])
    task = data[O["pokedex.taskId"]]
    if task >= C["NUM_TASKS"]: return None
    task_address = S["gTasks"]["value"] + task * O["task"]
    if not value(task_address + O["task.active"], "B"): return None
    result = {"pointer": address, "task": task, "callback": value(task_address + O["task.func"], "I") & ~1}
    for name in ("state", "regionalDex", "showNationalNumbers", "dexOrderId", "modeSelectListMenuId", "orderedListMenuTaskId"):
        result[name] = data[O["pokedex." + name]]
    for name in ("orderedDexCount", "dexSpecies", "numSeenKanto", "numOwnedKanto", "numSeenNational", "numOwnedNational"):
        result[name] = struct.unpack_from("<H", data, O["pokedex." + name])[0]
    result["listItems"] = struct.unpack_from("<I", data, O["pokedex.listItems"])[0]
    return result


def wait_ui(callback, state, frames=1500):
    expected = S[callback]["value"] & ~1
    for _ in range(frames):
        observed = ui()
        if observed and observed["callback"] == expected and observed["state"] == state:
            e.run(30)
            observed = ui()
            if observed and observed["callback"] == expected and observed["state"] == state: return observed
        e.run(1)
    raise AssertionError(("Native UI state not reached", callback, state, ui()))


def list_state(task):
    assert 0 <= task < C["NUM_TASKS"]
    address = S["gTasks"]["value"] + task * O["task"]
    assert value(address + O["task.active"], "B")
    assert value(address + O["task.func"], "I") & ~1 == S["ListMenuDummyTask"]["value"] & ~1
    data = address + O["task.data"]
    total = value(data + O["list.template"] + O["template.total"], "H")
    pointer = value(data + O["list.template"] + O["template.items"], "I")
    selected = value(data + O["list.cursor"], "H") + value(data + O["list.above"], "H")
    assert 0 < total <= 386 and selected < total
    return {"pointer": pointer, "total": total, "selected": selected}


def item_index(pointer, index): return value(pointer + index * O["item"] + O["item.index"], "I")


def move_list_to(task, row):
    for _ in range(450):
        ls = list_state(task)
        assert 0 <= row < ls["total"]
        if ls["selected"] == row: return ls
        e.press("DOWN" if ls["selected"] < row else "UP", hold=2, after=10)
    raise AssertionError("Native list cursor did not reach target")


def select_top_item(item):
    current = wait_ui("Task_PokedexScreen", 6)
    menu = list_state(current["modeSelectListMenuId"])
    options = [item_index(menu["pointer"], i) for i in range(menu["total"])]
    assert options.count(item) == 1, ("Expected menu item absent", item, options)
    move_list_to(current["modeSelectListMenuId"], options.index(item))
    e.press("A", hold=2, after=10)
    return wait_ui("Task_DexScreen_NumericalOrder", 6)


def top_items():
    current = wait_ui("Task_PokedexScreen", 6)
    menu = list_state(current["modeSelectListMenuId"])
    return [item_index(menu["pointer"], row) for row in range(menu["total"])]


def open_dex(tag):
    assert e.field_idle()
    e.press("START", hold=3, after=60)
    count = value(S["sNumStartMenuItems"]["value"], "B")
    assert 0 < count <= C["MAX_STARTMENU_ITEMS"]
    order = list(ram(S["sStartMenuOrder"]["value"], count))
    assert order.count(C["STARTMENU_POKEDEX"]) == 1
    target = order.index(C["STARTMENU_POKEDEX"])
    for _ in range(count + 1):
        cursor = value(S["sStartMenuCursorPos"]["value"], "B")
        assert cursor < count
        if cursor == target: break
        e.press("DOWN", hold=2, after=12)
    else: raise AssertionError("Native POKéDEX cursor not reached")
    e.press("A", hold=3, after=10)
    observed = wait_ui("Task_PokedexScreen", 6)
    assert observed["regionalDex"] == expected_region and not observed["showNationalNumbers"]
    mapping = list(struct.unpack("<387H", ram(observed["pointer"] + O["pokedex.regionalNumberByNational"], 774)))
    assert mapping == expected_inverse
    assert observed["numSeenKanto"] == sum(flags_seen[n] for n in expected_order)
    assert observed["numOwnedKanto"] == sum(flags_caught[n] for n in expected_order)
    assert observed["numSeenNational"] == sum(flags_seen.values())
    assert observed["numOwnedNational"] == sum(flags_caught.values())
    e.shot(str(out / (tag + "-top-menu.png")), scale=4)
    report["stages"].append({"stage": tag + "-regional-default", "pass": True, "observed": observed})


def verify_list(national_mode, tag):
    observed = wait_ui("Task_DexScreen_NumericalOrder", 6)
    assert bool(observed["showNationalNumbers"]) == national_mode
    assert observed["dexOrderId"] == C["DEX_ORDER_NUMERICAL_NATIONAL" if national_mode else "DEX_ORDER_NUMERICAL_KANTO"]
    order = list(range(1, 387)) if national_mode else expected_order
    last = max((i + 1 for i, n in enumerate(order) if flags_seen[n]), default=0)
    count = observed["orderedDexCount"]
    assert count == max(1, last), ("Native list length", count, last)
    entries = [item_index(observed["listItems"], i) for i in range(count)]
    if last:
        for index, entry in enumerate(entries):
            n = order[index]
            assert entry & 0xFFFF == national_to_species[n], ("Species renumbered", index, entry, n)
            assert bool(entry >> 16 & 1) == flags_seen[n]
            assert bool(entry >> 17 & 1) == flags_caught[n]
    else: assert entries == [0]
    ls = list_state(observed["orderedListMenuTaskId"])
    assert ls["pointer"] == observed["listItems"] and ls["total"] == count
    e.shot(str(out / (tag + "-list.png")), scale=4)
    report["stages"].append({"stage": tag, "pass": True, "observed": observed,
                             "entries_sha256": hashlib.sha256(struct.pack("<" + "I" * count, *entries)).hexdigest(),
                             "title_expected": "NATIONAL" if national_mode else ["KANTO - 151", "JOHTO - 251", "HOENN - 202"][expected_region],
                             "rendered_capture": str(out / (tag + "-list.png"))})
    return observed, order, entries


def details(tag, observed, order, entries):
    seen_rows = [i for i, entry in enumerate(entries) if entry >> 16 & 1]
    assert len(seen_rows) >= 3, "Current battery has fewer than three seen entries; do not synthesize a fixture"
    move_list_to(observed["orderedListMenuTaskId"], seen_rows[0])
    e.press("A", hold=2, after=10)
    for step, row in enumerate(seen_rows[:3]):
        page = wait_ui("Task_DexScreen_ShowMonPage", 5)
        assert page["dexSpecies"] == (entries[row] & 0xFFFF)
        national = order[row]
        shown = national if page["showNationalNumbers"] else expected_inverse[national]
        capture = out / f"{tag}-detail-{step + 1}-{shown:03d}.png"
        e.shot(str(capture), scale=4)
        report["stages"].append({"stage": f"{tag}-detail-{step + 1}", "pass": True,
                                 "internal_species": page["dexSpecies"], "national_no": national,
                                 "display_no_expected_from_verified_branch": shown, "capture": str(capture)})
        if step < 2: e.press("DOWN", hold=2, after=10)
    e.press("UP", hold=2, after=10)
    page = wait_ui("Task_DexScreen_ShowMonPage", 5)
    assert page["dexSpecies"] == (entries[seen_rows[1]] & 0xFFFF)
    report["stages"].append({"stage": tag + "-detail-reverse", "pass": True, "species": page["dexSpecies"]})
    e.press("B", hold=2, after=10)
    wait_ui("Task_DexScreen_NumericalOrder", 6)


def back_top():
    e.press("B", hold=2, after=10)
    observed = wait_ui("Task_PokedexScreen", 6)
    assert not observed["showNationalNumbers"] and observed["regionalDex"] == expected_region
    return observed


def close_dex():
    e.press("B", hold=2, after=90)
    for _ in range(5):
        if e.field_idle(): return
        e.press("B", hold=2, after=30)
    raise AssertionError("Native Pokédex/start menu did not close")


try:
    e = Emu(str(rom), str(sav), sym="")
    e.syms = syms
    candidate = SaveFile(str(sav))
    def on_continue_menu(emu):
        loaded1 = emu.read(emu.ptr("gSaveBlock1Ptr"), off("sb1"))
        loaded2 = bytearray(emu.read(emu.ptr("gSaveBlock2Ptr"), off("sb2")))
        expected2 = bytearray(candidate.sb2)
        assert loaded1 == bytes(candidate.sb1)
        assert emu.read(emu.ptr("gPokemonStoragePtr"), off("storage")) == bytes(candidate.blocks["storage"])
        for field, size in [("playTimeHours", 2), ("playTimeMinutes", 1), ("playTimeSeconds", 1), ("playTimeVBlanks", 1)]:
            pos = off("sb2." + field); loaded2[pos:pos + size] = expected2[pos:pos + size] = bytes(size)
        assert loaded2 == expected2
        report["initial_load_exact"] = True
    e.boot_continue(on_menu=on_continue_menu); settle(e)
    assert report.get("initial_load_exact")
    before = snapshot(e)
    block = Blocks(before["sb1"], before["sb2"])
    flags = {name: block.flag(name) for name in ("FLAG_HOENN_BIRCH_RESCUED", "FLAG_HOENN_MET_STERN", "FLAG_JOHTO_ARRIVAL_BRIEFED", "FLAG_JOHTO_MET_LAB_ASSISTANT")}
    expected_region = 2 if flags["FLAG_HOENN_BIRCH_RESCUED"] or flags["FLAG_HOENN_MET_STERN"] else 1 if flags["FLAG_JOHTO_ARRIVAL_BRIEFED"] or flags["FLAG_JOHTO_MET_LAB_ASSISTANT"] else 0
    expected_order = regional_orders[expected_region]
    expected_inverse = [0] * 387
    for row, n in enumerate(expected_order, 1): expected_inverse[n] = row
    flags_seen = {n: all(before["dex"][n - 1][1:]) for n in range(1, 387)}
    flags_caught = {n: all(before["dex"][n - 1]) for n in range(1, 387)}
    report.update(actual_story_flags=flags, active_region_expected=expected_region, input_progress_snapshot=compact(before))
    open_dex("before-save")
    select_top_item(C["DEX_CATEGORY_COUNT"] + C["DEX_ORDER_NUMERICAL_KANTO"])
    observed, order, entries = verify_list(False, "regional")
    details("regional", observed, order, entries)
    back_top()
    national_item = C["DEX_CATEGORY_COUNT"] + C["DEX_ORDER_NUMERICAL_NATIONAL"]
    available = top_items()
    if national_item in available:
        select_top_item(national_item)
        observed, order, entries = verify_list(True, "national")
        details("national", observed, order, entries)
        returned = back_top()
        e.shot(str(out / "national-return-regional-default.png"), scale=4)
        report["stages"].append({"stage": "national-return-regional-default", "pass": True, "observed": returned})
        report["national_mode_exercised"] = True
    else:
        report["national_mode_exercised"] = False
        report["national_mode_limitation"] = "Not unlocked in this actual battery; no fixture or story flag change allowed"
        report["actual_top_menu_items"] = available
    close_dex()
    after_ui = snapshot(e); invariant(before, after_ui)
    report["ui_party_PC_dex_story_location_preserved"] = True
    counter = native_save(e)
    assert counter[1] == counter[0] + 1
    live = snapshot(e); invariant(before, live)
    e.run(30); e.lib.qa_close(e.h); e.h = None
    stored = SaveFile(e.sav_path)
    assert stored.counter == counter[1] and len(stored.layout) == 14
    for _, sid, size in stored.layout:
        pos = stored.where[sid] * 4096
        assert checksum(stored.raw[pos:pos + size]) == struct.unpack_from("<H", stored.raw, pos + 0xff6)[0]
    assert bytes(stored.blocks["storage"]) == live["pc"]
    assert bytes(stored.sb1[off("sb1.playerParty"):off("sb1.playerParty") + 600]) == live["party"]
    assert [stored.dex_state(n) for n in range(1, 387)] == live["dex"]
    qa = out / "v14-regional-ui-native-cold-QA-only.sav"
    qa.write_bytes(Path(e.sav_path).read_bytes())
    e.h = e.lib.qa_open(str(rom).encode(), str(e.sav_path).encode()); assert e.h
    e.boot_continue(); settle(e)
    cold = snapshot(e); invariant(live, cold)
    open_dex("cold")
    select_top_item(C["DEX_CATEGORY_COUNT"] + C["DEX_ORDER_NUMERICAL_KANTO"])
    verify_list(False, "cold-regional")
    back_top(); close_dex()
    invariant(cold, snapshot(e))
    report["stages"].append({"stage": "native-SAVE-cold-Continue-current-regional-UI", "pass": True,
                             "counter": list(counter), "checksummed_sectors": 14,
                             "qa_save": str(qa), "qa_save_sha256": digest(qa), "cold_progress_snapshot": compact(cold)})
    report.update(pass_all=True, status="NATIVE_CURRENT_REGION_UI_SAVE_COLD_PASS")
except Exception as error:
    report.update(status="failed", error=repr(error), traceback=traceback.format_exc())
    if e and e.h:
        try:
            report["last_ui_state"] = ui()
            e.shot(str(out / "failure.png"), scale=4)
        except Exception as diagnostic_error:
            report["diagnostic_error"] = repr(diagnostic_error)
finally:
    if e: e.close()
    unchanged = all(digest(path) == old for path, old in protected.items())
    report["all_original_inputs_unchanged"] = unchanged
    assert unchanged
    (out / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: report.get(key) for key in ("pass_all", "status", "error", "active_region_expected", "all_original_inputs_unchanged")}))
sys.exit(0 if report["pass_all"] else 1)
