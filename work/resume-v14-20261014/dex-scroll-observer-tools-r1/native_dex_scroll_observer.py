"""Observe numerical dex scrolling through actual UI and read-only memory.

No injected task counter is available through the current Emu API. We explicitly
observe hardware frames, guest VBlank counter2, stable-held-key ReadKeys repeat
heartbeat, UI state and actual list-row movement instead. Those measurements
cannot be renamed 'task invocation counts' or physical DELTA-device FPS.
"""
import argparse
import hashlib
import json
import os
import re
import struct
import sys
import traceback
from pathlib import Path

parser = argparse.ArgumentParser()
for name in ('root', 'rom', 'sav', 'abi-json', 'out'):
    parser.add_argument('--' + name, required=True, type=Path)
parser.add_argument('--expect-sav-sha', required=True)
args = parser.parse_args()
root, rom, sav, out, abi_path = [getattr(args, key).resolve() for key in ('root', 'rom', 'sav', 'out', 'abi_json')]
os.chdir(root)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
abi = json.loads(abi_path.read_text())
assert abi['schema'] == 'thunder-yellow-dex-ui-compiler-probe-v1'
assert sha(rom) == abi['ROM_sha256'] == '0845f8cbc1afa5d957a64f76a4ae2700606175dd55bcd101184e6ba2a650b7fa'
assert sha(sav) == args.expect_sav_sha
for rel, digest in abi['source_sha256'].items():
    assert sha(root / rel) == digest
assert not out.exists() and out.is_relative_to(root / 'work')
for name, expected in {'tools/qa/emu.py': 'c8d3ba672d7ecc84dcefab513d84223f410e9d8cb43081cee4b37555e1378e69',
                       'tools/qa/savefile.py': 'e6cc1acb8569dbdca6d1b7b095835a5271c9e16de9d2fa3f976d15b50b9b7daa',
                       'tools/qa/gamedata.py': 'acaa4654ed889dc4f98f6c20dc26a85ea8d35963a771967c159ca4edc26a7ab3'}.items():
    assert sha(root / name) == expected
start_source = (root / 'src/start_menu.c').read_text()
assert re.search(r'\bSTARTMENU_POKEDEX\s*=\s*0\b', start_source)
main_source = (root / 'src/main.c').read_text()
assert 'if (keyInput != 0 && gMain.heldKeys == keyInput)' in main_source
assert 'gMain.keyRepeatCounter--;' in main_source and 'gMain.keyRepeatCounter = gKeyRepeatContinueDelay;' in main_source
sys.path.insert(0, str(root / 'tools/qa'))
from emu import Emu
from savefile import SaveFile
import gamedata as gd
gd.CACHE = str(out / 'compiler-cache')
gd._OFFSETS = None
class ReadOnlyEmu(Emu):
    def write(self, *arguments, **keywords):
        raise AssertionError('Scroll observer must not inject RAM, functions or task counters')
offsets = abi['offsets']
symbols = {name: row['value'] for name, row in abi['symbols'].items()}
out.mkdir(parents=True)
protected = {path: sha(path) for path in set((root / 'saves').rglob('*.sav')) | {sav, rom, abi_path}}
report = dict(schema='thunder-yellow-read-only-native-dex-scroll-v1', pass_all=False,
              ROM_sha256=sha(rom), SAV_sha256=sha(sav), ABI_sha256=sha(abi_path),
              measurement='Actual UI rendering plus read-only guest-key-repeat heartbeat; no task invocation counter',
              RAM_writes=0, direct_engine_calls=0, State_restore=0, preboot_fixtures=0,
              DELTA_device_FPS_measured=False, full_campaign_verified=False, cases=[])
e = None

def memory_range(address, size):
    return ((0x02000000 <= address and address + size <= 0x02040000)
            or (0x03000000 <= address and address + size <= 0x03008000))

def u8(base, name):
    return e.u8(base + offsets[name])

def u16(base, name):
    return e.u16(base + offsets[name])

def task_data(task):
    assert 0 <= task < 16
    address = symbols['gTasks'] + offsets['task.size'] * task
    assert e.u8(address + offsets['task.active'])
    assert e.u32(address + offsets['task.func']) & ~1 == symbols['ListMenuDummyTask'] & ~1
    return address + offsets['task.data']

def screen_info(ordered):
    address = e.u32(symbols['sPokedexScreenData'])
    assert memory_range(address, offsets['dex.size'])
    task = u8(address, 'dex.orderedListTask' if ordered else 'dex.topListTask')
    data = task_data(task)
    template = data + offsets['list.template']
    count = u16(template, 'listTemplate.count')
    shown = u16(template, 'listTemplate.shown')
    pointer = e.u32(template + offsets['listTemplate.items'])
    assert count > 0 and 0 < shown <= count and memory_range(pointer, count * offsets['listItem.size'])
    scroll, row = u16(data, 'list.offset'), u16(data, 'list.row')
    assert row < shown and scroll + row < count
    selected = e.u32(pointer + (scroll + row) * offsets['listItem.size'] + offsets['listItem.index'])
    return dict(address=address, task=task, state=u8(address, 'dex.state'), scroll_offset=scroll,
                cursor_row=row, count=count, shown=shown, selected_item=selected,
                region=u8(address, 'dex.region'), show_national=bool(u8(address, 'dex.national')))

def palette_active():
    return bool(e.u8(symbols['gPaletteFade'] + abi['palette_active_byte']) & abi['palette_active_mask'])

def stable_ui(ordered, timeout=1800):
    correct_task = symbols['Task_DexScreen_NumericalOrder' if ordered else 'Task_PokedexScreen'] & ~1
    steady = 0
    for _ in range(timeout):
        if e.reset_seen():
            raise RuntimeError('game reset while navigating dex')
        address = e.u32(symbols['sPokedexScreenData'])
        if e.callback2() & ~1 == symbols['CB2_PokedexScreen'] & ~1 and memory_range(address, offsets['dex.size']):
            task = u8(address, 'dex.task')
            if task < 16:
                ta = symbols['gTasks'] + offsets['task.size'] * task
                ready = (e.u8(ta + offsets['task.active']) and e.u32(ta + offsets['task.func']) & ~1 == correct_task
                         and u8(address, 'dex.state') == 6 and not palette_active())
                if ready:
                    steady += 1
                    if steady >= 12:
                        return screen_info(ordered)
                else:
                    steady = 0
        e.run(1)
    raise TimeoutError('active numerical/top dex UI not observed')

def snapshot_records():
    s1, s2 = e.ptr('gSaveBlock1Ptr'), e.ptr('gSaveBlock2Ptr')
    count = e.u8(e.sym('gPlayerPartyCount'))
    sb1, sb2 = e.read(s1, gd.off('sb1')), e.read(s2, gd.off('sb2'))
    n = (gd.const('NUM_SPECIES') + 7) // 8
    assert n == gd.off('dex.seen') - gd.off('dex.owned')
    return (e.read(e.sym('gPlayerParty'), 600), count, e.read(e.ptr('gPokemonStoragePtr'), gd.off('storage')),
            sb1[gd.off('sb1.flags'):gd.off('sb1.vars')],
            sb1[gd.off('sb1.vars'):gd.off('sb1.vars') + gd.const('VARS_COUNT') * 2],
            sb2[gd.off('sb2.hoennTrainerFlags'):gd.off('sb2.hoennVars') + 0x100],
            sb1[gd.off('sb1.seen1'):gd.off('sb1.seen1') + n], sb1[gd.off('sb1.seen2'):gd.off('sb1.seen2') + n],
            sb2[gd.off('sb2.pokedex') + gd.off('dex.owned'):gd.off('sb2.pokedex') + gd.off('dex.owned') + n],
            sb2[gd.off('sb2.pokedex') + gd.off('dex.seen'):gd.off('sb2.pokedex') + gd.off('dex.seen') + n])

def take_sample():
    view = screen_info(True)
    main = symbols['gMain']
    view.update(hardware_frame=e.frame(), guest_vblank_counter2=e.u32(main + offsets['main.vblankCounter2']),
                key_repeat_counter=u16(main, 'main.keyRepeatCounter'),
                held_keys_raw=u16(main, 'main.heldKeysRaw'),
                new_and_repeated_keys=u16(main, 'main.newAndRepeatedKeys'), palette_active=palette_active(),
                bg_copy_bits_nonzero=any(e.read(symbols['sDmaBusyBitfield'], 16)))
    return view

try:
    e = ReadOnlyEmu(str(rom), str(sav), sym='')
    # Use the probe's uniquely bound current ELF helpers; do not regenerate or
    # rewrite the repository's symbol file through Rom/fresh_syms.
    # Emu's high-level callback helpers compare against an even code address.
    # Task/data memory retains the actual ELF values above; only this lookup
    # normalizes STT_FUNC symbols to avoid Thumb-pointer comparison ambiguity.
    all_rows = dict(abi['helper_symbols'])
    all_rows.update(abi['symbols'])
    e.syms = {name: row['value'] & ~1 if row['info'] & 15 == 2 else row['value']
              for name, row in all_rows.items()}
    e.boot_continue()
    for _ in range(600):
        if e.field_idle() and not e.quest_log_playing():
            break
        e.run(1)
    else:
        raise TimeoutError('field not idle')
    original_records = snapshot_records()
    e.press('START', hold=3, after=60)
    count = e.u8(symbols['sNumStartMenuItems'])
    assert 0 < count <= abi['symbols']['sStartMenuOrder']['size']
    order = list(e.read(symbols['sStartMenuOrder'], count))
    assert 0 in order
    wanted = order.index(0)
    for _ in range(count + 1):
        if e.u8(symbols['sStartMenuCursorPos']) == wanted:
            break
        e.press('DOWN', hold=3, after=12)
    else:
        raise RuntimeError('actual START dex cursor unavailable')
    e.press('A', hold=3, after=12)
    stable_ui(False)
    for _ in range(24):
        top = screen_info(False)
        if top['selected_item'] == offsets['menu.numericalItem']:
            break
        e.press('DOWN', hold=3, after=12)
    else:
        raise RuntimeError('regional numerical menu entry not reachable')
    e.press('A', hold=3, after=12)
    ready = stable_ui(True)
    assert ready['count'] > ready['shown']
    e.shot(str(out / 'numerical-list-ready.png'), scale=4)
    repeat = e.u16(symbols['gKeyRepeatContinueDelay'])
    assert repeat > 1
    for label, key, mask in (('cold-down', 'DOWN', 128), ('reverse-up', 'UP', 64), ('warm-down', 'DOWN', 128)):
        e.hold()
        e.run(12)
        stable_ui(True)
        start = e.frame()
        samples = [take_sample()]
        e.hold(key)
        for _ in range(360):
            e.run(1)
            samples.append(take_sample())
        e.hold()
        assert e.frame() - start == 360
        changed, heartbeat_gaps, transitions, eligible, edge_frames = 0, [], 0, 0, 0
        for before, after in zip(samples, samples[1:]):
            assert after['hardware_frame'] - before['hardware_frame'] == 1
            assert after['guest_vblank_counter2'] - before['guest_vblank_counter2'] in (0, 1, 2)
            moved = (before['scroll_offset'], before['cursor_row']) != (after['scroll_offset'], after['cursor_row'])
            changed += moved
            edge = ((key == 'UP' and before['scroll_offset'] + before['cursor_row'] == 0)
                    or (key == 'DOWN' and before['scroll_offset'] + before['cursor_row'] == before['count'] - 1))
            edge_frames += edge
            if before['state'] != 6 or before['palette_active'] or before['held_keys_raw'] != mask:
                transitions += 1
                continue
            eligible += 1
            count_before = before['key_repeat_counter']
            assert count_before > 0
            expected = repeat if count_before == 1 else count_before - 1
            if after['key_repeat_counter'] != expected:
                heartbeat_gaps.append(dict(frame=after['hardware_frame'], before=count_before,
                                           after=after['key_repeat_counter'], expected_single_loop=expected,
                                           moved=moved, at_edge=edge, dma_bitfield_nonzero=before['bg_copy_bits_nonzero']))
        assert changed > 0, 'holding direction did not move actual list cursor'
        assert snapshot_records() == original_records, 'scroll workload changed protected player/PC/dex/story records'
        (out / (label + '-samples.json')).write_text(json.dumps(dict(ROM_sha256=sha(rom), samples=samples), indent=2))
        e.shot(str(out / (label + '.png')), scale=4)
        report['cases'].append(dict(label=label, hardware_frames=360, eligible_steady_held_frames=eligible,
                                    excluded_transition_or_first_key_frames=transitions, edge_frames=edge_frames,
                                    actual_cursor_changes=changed, Main_ReadKeys_heartbeat_anomalies=heartbeat_gaps,
                                    guest_vblank_counter2_delta=samples[-1]['guest_vblank_counter2'] - samples[0]['guest_vblank_counter2'],
                                    interpretation='Heartbeat anomalies are diagnostic candidates, not measured task counts or DELTA FPS drops'))
    report.update(pass_all=True, status='observed', protected_player_records_preserved=True,
                  task_invocation_count_available=False, current_dex_ROM_patch_written=False)
except Exception as error:
    report.update(status='failed', error=repr(error), traceback=traceback.format_exc())
    if e and e.h:
        e.shot(str(out / 'failure.png'), scale=4)
finally:
    if e:
        e.close()
    unchanged = all(sha(path) == digest for path, digest in protected.items())
    report['original_inputs_unchanged'] = unchanged
    assert unchanged
    (out / 'validation.json').write_text(json.dumps(report, indent=2))
print(json.dumps({key: report.get(key) for key in ('status', 'pass_all', 'error', 'original_inputs_unchanged', 'cases')}))
sys.exit(0 if report['pass_all'] else 1)
