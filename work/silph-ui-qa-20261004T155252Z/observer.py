"""UI-only SAVE/CONTINUE observer for the disposable Silph Snag QA case.
No ROM modification, emulator-memory writes, or native-function injection.
Call after the capture case has reached the idle overworld.
"""
import hashlib, inspect, json, struct
from pathlib import Path

PID = 0x003A5580
ORDERS = "GAEM GAME GEAM GEMA GMAE GMEA AGEM AGME AEGM AEMG AMGE AMEG EGAM EGMA EAGM EAMG EMGA EMAG MGAE MGEA MAGE MAEG MEGA MEAG".split()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def describe(raw):
    assert len(raw) == 80
    pid, ot = struct.unpack_from("<II", raw)
    plain = struct.pack("<12I", *(n ^ pid ^ ot for n in struct.unpack_from("<12I", raw, 32)))
    order = ORDERS[pid % 24]
    growth = plain[12 * order.index("G"):12 * (order.index("G") + 1)]
    return {"pid": pid, "ot": ot, "flags": raw[19],
            "species": struct.unpack_from("<H", growth)[0],
            "exp": struct.unpack_from("<I", growth, 4)[0],
            "stored_checksum": struct.unpack_from("<H", raw, 28)[0],
            "computed_checksum": sum(struct.unpack("<24H", plain)) & 65535,
            "raw_sha256": sha(raw), "raw_hex": raw.hex()}

def target(boxes, player_ot):
    matches = [(i // 80, boxes[i:i+80]) for i in range(0, len(boxes), 80)
               if struct.unpack_from("<I", boxes, i)[0] == PID]
    assert len(matches) == 1, "Expected one new Silph Lickitung; duplicate/missing PID"
    index, raw = matches[0]
    d = describe(raw)
    assert d["species"] == 108 and d["ot"] == player_ot
    assert d["stored_checksum"] == d["computed_checksum"], "Lickitung checksum mismatch"
    assert d["flags"] & 5 == 0 and d["flags"] & 0x22 == 0x22
    assert d["exp"] == 59319, "Captured level-39 EXP differs"
    assert raw[20:27] == bytes.fromhex("c4bfcdcdc3bfff"), "OT is not JESSIE"
    return dict(d, box=index // 30 + 1, slot=index % 30 + 1)

def ui_save_reload(e, rom, output_dir):
    from emu import Emu
    from gamedata import off, const
    out = Path(output_dir)
    assert not out.exists(), "Use a fresh QA output directory"
    out.mkdir(parents=True)
    result = {"pass": False, "physical_DELTA_tested": False,
              "runtime_memory_writes": False, "synthetic_fixture": True}
    box_size = off("boxmon")
    assert box_size == 80
    size = const("TOTAL_BOXES_COUNT") * const("IN_BOX_COUNT") * box_size
    def boxes(emu):
        return emu.read(emu.ptr("gPokemonStoragePtr") + off("storage.boxes"), size)
    def stable_boxes(emu):
        previous, repeats = None, 0
        for _ in range(60):
            current = boxes(emu)
            repeats = repeats + 1 if current == previous else 0
            if repeats >= 2:
                return current
            previous = current
            emu.run(1)
        raise AssertionError("PC records did not settle")
    try:
        assert e.field_idle(), "Capture case must finish in the idle overworld"
        ot = e.u32(e.ptr("gSaveBlock2Ptr") + off("sb2.playerTrainerId"))
        before = stable_boxes(e)
        result["before_save"] = target(before, ot)
        counter = e.u32(e.sym("gSaveCounter"))
        e.press("START", after=60)
        count = e.u8(e.sym("sNumStartMenuItems"))
        order = list(e.read(e.sym("sStartMenuOrder"), count))
        assert order.count(4) == 1, "Expected verified STARTMENU_SAVE == 4"
        wanted = order.index(4)
        for _ in range(count):
            if e.u8(e.sym("sStartMenuCursorPos")) == wanted:
                break
            e.press("DOWN", after=15)
        assert e.u8(e.sym("sStartMenuCursorPos")) == wanted
        e.press("A", after=120)
        e.shot(str(out / "save-confirm.png"))
        for _ in range(24):
            if e.u32(e.sym("gSaveCounter")) != counter:
                break
            e.press("A", after=45)
        assert e.u32(e.sym("gSaveCounter")) == counter + 1
        for _ in range(200):
            status = e.u16(e.sym("gSaveAttemptStatus"))
            assert status != 255, "SAVE_STATUS_ERROR"
            callback = e.u32(e.sym("sSaveDialogCB")) & ~1
            if status == 1 and callback != (e.sym("SaveDialogCB_DoSave") & ~1):
                break
            e.run(60)
        else:
            raise AssertionError("Flash save did not finish")
        assert e.u32(e.sym("gDamagedSaveSectors")) == 0
        assert e.u32(e.sym("gSaveCounter")) == counter + 1
        assert stable_boxes(e) == before, "SAVE changed PC records"
        e.run(240)
        e.shot(str(out / "save-complete.png"))
        e.lib.qa_close(e.h)
        e.h = None
        saved = Path(e.sav_path).read_bytes()
        saved_path = out / "disposable-ui-save.sav"
        with saved_path.open("xb") as f:
            f.write(saved)
        with Emu(str(rom), str(saved_path), sym=str(Path(rom).with_suffix(".sym"))) as reloaded:
            assert "on_menu" in inspect.signature(reloaded.boot_continue).parameters
            def on_menu(check):
                assert check.u8(check.sym("gSaveFileStatus")) == 1
                assert check.u32(check.sym("gSaveCounter")) == counter + 1
                assert boxes(check) == before, "Reloaded PC data differ"
            reloaded.boot_continue(on_menu=on_menu)
            again = stable_boxes(reloaded)
            assert again == before, "CONTINUE changed PC records"
            result["after_continue"] = target(again, ot)
            reloaded.shot(str(out / "continued.png"))
        result.update(pass_=True, before_counter=counter, after_counter=counter+1,
                      saved_sha256=sha(saved), all_pc_bytes_preserved=True)
        result["pass"] = result.pop("pass_")
        return result
    except Exception as ex:
        result["error"] = repr(ex)
        raise
    finally:
        with (out / "result.json").open("x", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
