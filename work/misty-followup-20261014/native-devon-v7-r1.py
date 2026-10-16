"""Native Devon QA v7-r1: actual Roxanne battle, Gym exit, theft, SAVE/cold.

Run only after current ROM/ELF/SAV and the ELF-bound ABI JSON are verified.
Temporary preboot eligibility fixtures do not prove a complete campaign.
No emulator RAM writes, direct event calls, or forced battle results.
"""
from pathlib import Path
from collections import Counter, defaultdict, deque
import argparse
import hashlib
import json
import os
import struct
import sys
import traceback


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


P = argparse.ArgumentParser(description=__doc__)
P.add_argument('--root', default='/workspaces/pokefirered')
P.add_argument('--rom', required=True)
P.add_argument('--elf', required=True)
P.add_argument('--sav', required=True)
P.add_argument('--expect-rom-sha', required=True)
P.add_argument('--expect-elf-sha', required=True)
P.add_argument('--expect-sav-sha', required=True)
P.add_argument('--abi-json', required=True)
P.add_argument('--out', default='work/hoenn-devon-native-20261013/native-v7-r1')
DEVON_CFG = P.parse_args()
root = Path(DEVON_CFG.root).resolve()
os.chdir(root)
rom, elf, sav = [Path(x).resolve() for x in
                 (DEVON_CFG.rom, DEVON_CFG.elf, DEVON_CFG.sav)]
out = Path(DEVON_CFG.out).resolve()
assert out.is_relative_to(root / 'work'), 'QA output must be inside workspace/work'
assert not out.exists(), 'Use a new output folder; retain previous QA results'
out.mkdir(parents=True)
ABI_PATH = Path(DEVON_CFG.abi_json).resolve()
HELPER_PATH = Path(__file__).resolve().with_name('devon_party_controller_prepared_v1.py')
HELPER_SHA = '33816d6f22d28b0a52305b555f5092c0b8ea12f615c088161c156d5db0afae36'
e = None
protected = {}
report = {'pass': False, 'status': 'preflight', 'runner_version': 7, 'runner_revision': 1,
          'ROM_sha256': None, 'ELF_sha256': None,
          'SAV_sha256': None, 'source_sav': str(sav),
          'RAM_writes': 0, 'direct_script_calls': 0,
          'forced_battle_outcomes': 0, 'cases': [], 'stages': [],
          'scope': 'Preboot eligible fixtures; actual Roxanne win, continuous Gym exit and Devon coord, native SAVE/cold; not whole campaign'}


def emit():
    (out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')


try:
    protected = {f.resolve(): file_sha(f) for f in
                 set((root / 'saves').rglob('*.sav')) | {rom, elf, sav, ABI_PATH, HELPER_PATH}}
    report.update({'ROM_sha256': protected[rom], 'ELF_sha256': protected[elf],
                   'SAV_sha256': protected[sav]})
    for kind, actual, expected in [('ROM', protected[rom], DEVON_CFG.expect_rom_sha),
                                  ('ELF', protected[elf], DEVON_CFG.expect_elf_sha),
                                  ('SAV', protected[sav], DEVON_CFG.expect_sav_sha)]:
        assert len(expected) == 64 and actual == expected, (kind, actual, expected)
    assert protected[rom].startswith('e156'), 'This v7 is prepared for the approved e156 ROM'
    assert protected[sav].startswith('917c'), 'This v7 is prepared for the approved 917c SAV'
    assert protected[HELPER_PATH] == HELPER_SHA, 'Prepared helper identity mismatch'
    ABI = json.loads(ABI_PATH.read_text())
    assert ABI['rom_sha256'] == protected[rom]
    assert ABI['elf_sha256'] == protected[elf]
    required_fields = ['PartyMenu.slotId', 'PartyMenu.action', 'Task.size', 'Task.func',
                       'Task.isActive', 'Pokemon.hp', 'PartyMenuInternal.actions',
                       'PartyMenuInternal.numActions', 'Menu.cursorPos',
                       'BattleStruct.playerPartyIdx', 'CursorOption.size',
                       'CursorOption.text', 'CursorOption.func',
                       'PaletteFade.active.byteOffset', 'PaletteFade.active.mask']
    AF = ABI['offsets']
    assert all(isinstance(AF.get(k), int) and AF[k] >= 0 for k in required_fields)
    assert AF['Task.size'] <= 128 and AF['Task.func'] + 4 <= AF['Task.size']
    assert AF['Task.isActive'] < AF['Task.size'] and AF['Pokemon.hp'] + 2 <= 100
    assert 1 <= ABI['task_count'] <= 32
    assert AF['CursorOption.size'] == 8
    assert AF['CursorOption.text'] == 0 and AF['CursorOption.func'] == 4
    assert 0 < AF['PaletteFade.active.mask'] <= 255
    source_hashes = ABI['source_sha256']
    assert {'src/party_menu.c', 'src/menu.c', 'src/data/party_menu.h',
            'include/party_menu.h'} <= set(source_hashes)
    for source_path, wanted in source_hashes.items():
        path = (root / source_path).resolve()
        assert path.is_relative_to(root)
        assert file_sha(path) == wanted, ('ABI source changed', source_path)
        protected[path] = wanted
    sys.path.insert(0, str(HELPER_PATH.parent))
    from devon_party_controller_prepared_v1 import (
        UiMon, decode_battle_order, replacement_ui_slots,
        battle_phase, navigate_ui_slot)

    # Keep only the existing definitions prefix, never execute Misty QA cases.
    sys.argv = ['devon', '--rom', str(rom), '--elf', str(elf),
                '--sav', str(sav), '--out', str(out)]
    q = (root / 'tools/qa/native_misty_basic_qa.py').read_text()
    assert hashlib.sha256(q.encode()).hexdigest() == '5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
    marker = '\nresults=[];rows=[]\n'
    assert q.count(marker) == 1
    exec(compile(q.split(marker)[0], '<verified-definitions-only>', 'exec'))

    def forbidden_engine_call(*args, **kwargs):
        raise AssertionError('Direct engine/event calls are forbidden in Devon v7')

    call = flag = trail = forbidden_engine_call
    required_symbols = ['CB2_UpdatePartyMenu', 'Task_HandleChooseMonInput',
                        'Task_HandleSelectionMenuInput', 'CursorCB_SendMon',
                        'gPartyMenu', 'sPartyMenuInternal', 'sMenu',
                        'gBattlePartyCurrentOrder', 'gBattlerPartyIndexes',
                        'gBattlersCount', 'gBattlerInMenuId', 'gBattleStruct',
                        'sCursorOptions', 'gText_SendOut', 'gSelectedMonPartyId',
                        'gTasks', 'gBattleOutcome', 'BattleMainCB2', 'gPaletteFade']
    assert all(n in syms for n in required_symbols), [n for n in required_symbols if n not in syms]
    for name in ['CB2_UpdatePartyMenu', 'gPartyMenu', 'sPartyMenuInternal',
                 'sMenu', 'sCursorOptions', 'gText_SendOut']:
        assert len(sets.get(name, {syms[name] & ~1})) == 1, ('ambiguous ELF symbol', name)
    report['ABI_manifest_sha256'] = file_sha(ABI_PATH)
    report['ABI_offsets'] = AF
    report['status'] = 'running'
    emit()

    F = ['FLAG_HOENN_BADGE01_GET', 'FLAG_HOENN_DEFEATED_RUSTBORO_GYM',
         'FLAG_HOENN_GOT_TM39_FROM_ROXANNE', 'FLAG_HIDE_HOENN_RUSTBORO_THIEF',
         'FLAG_HOENN_WOODS_RESEARCHER_SAVED']

    def state():
        b = blocks(e)
        return {'position': e.location(), 'devon_scene': b.var('VAR_HOENN_SCENE_DEVON'),
                'flags': {f: b.flag(f) for f in F},
                'roxanne_beaten': b.trainer_beaten('TRAINER_HOENN_ROXANNE_1'),
                'idle': bool(e.field_idle())}

    def stage(tag):
        report['stages'].append({'stage': tag, **state()})
        emit()

    def is_party_menu():
        return (e.callback2() & ~1) == (syms['CB2_UpdatePartyMenu'] & ~1)

    def active_task(name):
        wanted = sets.get(name, {syms[name] & ~1})
        return [i for i in range(ABI['task_count'])
                if e.u8(syms['gTasks'] + AF['Task.size'] * i + AF['Task.isActive'])
                and (e.u32(syms['gTasks'] + AF['Task.size'] * i + AF['Task.func']) & ~1) in wanted]

    def choose_ready():
        faded = not (e.u8(syms['gPaletteFade'] + AF['PaletteFade.active.byteOffset'])
                     & AF['PaletteFade.active.mask'])
        return is_party_menu() and faded and len(active_task('Task_HandleChooseMonInput')) == 1

    def slot():
        return struct.unpack('<b', e.read(syms['gPartyMenu'] + AF['PartyMenu.slotId'], 1))[0]

    def party_profiles(raw, count):
        rows = []
        for i in range(count):
            a = raw[i * 100:(i + 1) * 100]
            m = Mon(bytearray(a), 0)
            subs = m.subs()
            valid = (sum(x[0] for s in subs.values() for x in struct.iter_unpack('<H', s)) & 65535) == struct.unpack_from('<H', a, 28)[0]
            rows.append((a, m, subs, valid))
        return rows

    def immutable_core(row):
        raw, mon, s, valid = row
        assert valid and not raw[19] & 1, 'Bad Egg/checksum failure in party'
        return (bytes(raw[:28]), bytes(s['M']), bytes(s['G'][:4]),
                bytes(s['G'][8:9]), bytes(s['G'][10:]),
                bytes(s['A'][:8]), bytes(s['E'][6:]))

    def preserve(before):
        after = snapshot(e)
        assert after['pc'] == before['pc'], 'Existing PC bytes changed'
        assert after['party_count'] == before['party_count']
        old = party_profiles(before['party'], before['party_count'])
        new = party_profiles(after['party'], after['party_count'])
        ident = lambda rows: Counter((m.personality, m.otid) for _, m, _, _ in rows)
        assert ident(old) == ident(new), 'Lost/duplicated party identity'
        assert Counter(immutable_core(x) for x in old) == Counter(immutable_core(x) for x in new), 'Party IV/origin/species/moves/core changed'
        pending = defaultdict(deque)
        for i, row in enumerate(old):
            pending[immutable_core(row)].append((i, row))
        ledger = []
        for i, row in enumerate(new):
            old_slot, previous = pending[immutable_core(row)].popleft()
            a, m, s, _ = previous
            b, n, t, _ = row
            ledger.append({'old_slot': old_slot, 'new_slot': i, 'pid': m.personality,
                           'ot': m.otid, 'species': m.species(),
                           'EXP_before_after': [struct.unpack_from('<I', s['G'], 4)[0], struct.unpack_from('<I', t['G'], 4)[0]],
                           'friendship_before_after': [s['G'][9], t['G'][9]],
                           'EV_before_after': [list(s['E'][:6]), list(t['E'][:6])],
                           'PP_before_after': [list(s['A'][8:]), list(t['A'][8:])],
                           'party_cache_changed': a[80:] != b[80:],
                           'checksum_ok': True, 'IV_and_origin_preserved': True})
        assert len(before['dex']) == len(after['dex'])
        for a, b in zip(before['dex'], after['dex']):
            assert all(not x or y for x, y in zip(a, b)), 'Lost dex bits'
        return ledger

    def native_send_out():
        assert choose_ready()
        assert not e.u32(syms['gBattleTypeFlags']) & 1, 'This QA controller supports a single battle only'
        count = e.u8(syms['gPlayerPartyCount'])
        packed = e.read(syms['gBattlePartyCurrentOrder'], 3)
        order = decode_battle_order(packed)
        profiles = party_profiles(e.read(syms['gPlayerParty'], 600), count)
        ui = [UiMon(m.personality, m.otid, m.species(),
                    struct.unpack_from('<H', raw, AF['Pokemon.hp'])[0],
                    bool(struct.unpack_from('<I', subs['M'], 4)[0] & (1 << 30)),
                    bool(raw[19] & 1), valid)
              for raw, m, subs, valid in profiles]
        nb = e.u8(syms['gBattlersCount'])
        assert nb == 2, ('Expected a single battle', nb)
        active = {e.u8(syms['gBattlerPartyIndexes'])}
        bs = e.u32(syms['gBattleStruct'])
        assert 0x02000000 <= bs < 0x02040000
        reserved = e.u8(bs + AF['BattleStruct.playerPartyIdx'])
        choices = replacement_ui_slots(ui, packed, active, reserved)
        assert choices, ('No eligible native replacement', order, active, reserved, ui)
        target = choices[0]
        row = {'frame': e.frame(), 'UI_target': target, 'battle_index': order[target],
               'party_order': list(order), 'active_battle_indexes': sorted(active),
               'reserved_battle_index': reserved,
               'party_action': e.u8(syms['gPartyMenu'] + AF['PartyMenu.action']),
               'candidate_pid': ui[target].pid, 'candidate_ot': ui[target].ot,
               'candidate_HP': ui[target].hp}
        row['cursor_trace'] = navigate_ui_slot(e, target, slot, choose_ready,
                                               lambda: safe(e), single_battle_verified=True)
        assert slot() == target and choose_ready()
        e.shot(str(out / ('replacement-%02d-slot.png' % len(report.setdefault('replacements', [])))), scale=3)
        e.press('A', hold=2, after=14)
        for _ in range(300):
            safe(e)
            if is_party_menu() and len(active_task('Task_HandleSelectionMenuInput')) == 1:
                break
            e.run(1)
        else:
            raise AssertionError('Actual SEND OUT selection window did not open')
        assert slot() == target
        pi = e.u32(syms['sPartyMenuInternal'])
        assert 0x02000000 <= pi < 0x02040000
        num = e.u8(pi + AF['PartyMenuInternal.numActions'])
        assert 1 <= num <= 8
        options = list(e.read(pi + AF['PartyMenuInternal.actions'], num))
        # Verify both the displayed SEND OUT text and its actual callback.
        sends = []
        for i, option in enumerate(options):
            p = syms['sCursorOptions'] + AF['CursorOption.size'] * option
            text = e.u32(p + AF['CursorOption.text'])
            func = e.u32(p + AF['CursorOption.func']) & ~1
            if text == syms['gText_SendOut'] and func == (syms['CursorCB_SendMon'] & ~1):
                sends.append(i)
        assert len(sends) == 1, ('SEND OUT option not unique', options, sends)
        wanted = sends[0]
        def selection_cursor():
            return struct.unpack('<b', e.read(syms['sMenu'] + AF['Menu.cursorPos'], 1))[0]
        for _ in range(10):
            cur = selection_cursor()
            if cur == wanted:
                break
            assert 0 <= cur < num and len(active_task('Task_HandleSelectionMenuInput')) == 1
            e.press('DOWN' if cur < wanted else 'UP', hold=2, after=14)
        else:
            raise AssertionError('SEND OUT cursor did not reach verified option')
        assert selection_cursor() == wanted
        row.update({'selection_options': options, 'SEND_OUT_index': wanted,
                    'selected_ui_slot_verified': True})
        e.press('A', hold=2, after=20)
        for _ in range(600):
            safe(e)
            if not is_party_menu():
                break
            e.run(1)
        else:
            raise AssertionError('SEND OUT was not accepted; party menu remained open')
        assert e.u8(syms['gSelectedMonPartyId']) == order[target], 'Native selected battle index mismatch'
        row.update({'accepted': True, 'frame_after': e.frame(),
                    'callback_after': hex(e.callback2()),
                    'battle_outcome_after': e.u8(syms['gBattleOutcome'])})
        report['replacements'].append(row)
        emit()

    def battle_menu_checked():
        trace = report.setdefault('battle_callback_trace', [])
        for tick in range(2400):
            safe(e)
            outcome = e.u8(syms['gBattleOutcome'])
            phase = battle_phase(e.callback2(), battle_callback=syms['BattleMainCB2'],
                                 party_callback=syms['CB2_UpdatePartyMenu'],
                                 overworld=e.in_overworld(), outcome=outcome,
                                 action_ready=e.in_battle() and ctrl(e, 0, 'HandleInputChooseAction'),
                                 choose_mon_ready=choose_ready())
            now = (hex(e.callback2()), outcome, phase)
            if not trace or trace[-1]['state'] != list(now):
                trace.append({'frame': e.frame(), 'tick': tick, 'state': list(now)})
                emit()
            if phase == 'fight-action':
                e.run(20)
                return True
            if phase == 'field-with-result':
                return False
            if phase == 'party-select':
                native_send_out()
                continue
            if phase == 'party-transition':
                e.run(2)
            else:
                # B only advances battle text; never use it to cancel forced replacement.
                e.press('B', hold=2, after=14)
        raise AssertionError(('No confirmed battle end/action menu', now))

    def idle():
        for _ in range(1500):
            safe(e)
            if e.field_idle():
                return
            assert not e.in_battle() and not is_party_menu(), 'Unexpected battle/modal while dismissing field event'
            e.press('B', hold=2, after=14)
        raise AssertionError(('Field event did not finish', state()))

    def step(key, warp=False):
        start = e.location()
        dx, dy = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}[key]
        want = (*start[:2], start[2] + dx, start[3] + dy)
        e.hold(key)
        try:
            for _ in range(120):
                e.run(1)
                if e.location() != start:
                    break
            else:
                raise AssertionError(('Native step blocked', start, key))
        finally:
            e.hold()
        if not warp:
            assert e.location() == want, ('Native step overshot', start, key, e.location())
        idle()
        e.run(20)
        if not warp:
            assert e.location() == want
        return e.location()

    def fixture(scene):
        s = SaveFile(str(sav))
        s.fast_battles()
        s.set_flag('FLAG_SYS_GAME_CLEAR', True)
        s.set_flag('FLAG_HOENN_BIRCH_RESCUED', True)
        s.set_var('VAR_HOENN_SCENE_BIRCH', 3)
        s.set_var('VAR_HOENN_SCENE_DEVON', scene)
        s.set_flag('FLAG_HOENN_ROCKET_WOODS', True)
        s.set_trainer_beaten('TRAINER_HOENN_GRUNT_PETALBURG_WOODS', True)
        s.set_flag('FLAG_HOENN_WOODS_RESEARCHER_SAVED', scene == 1)
        for f in F[:3]:
            s.set_flag(f, False)
        s.set_trainer_beaten('TRAINER_HOENN_ROXANNE_1', False)
        for t in ['TRAINER_HOENN_JOSH', 'TRAINER_HOENN_TOMMY', 'TRAINER_HOENN_MARC']:
            s.set_trainer_beaten(t, True)
        s.set_item('ITEM_TM39', 0)
        s.set_item('ITEM_TM_CASE', 1)
        for i in range(const('QUEST_LOG_SCENE_COUNT')):
            s.sb1[off('sb1.questLog') + i * off('questlogscene')] = 0
        s.set_var('VAR_REPEL_STEP_COUNT', 250)
        s.warp('RustboroCity_Gym', 5, 3)
        f = out / ('scene%d-before-QA-only.sav' % scene)
        s.save(str(f))
        return f

    for scene in [1, 0]:
        f = fixture(scene)
        e = ReadOnlyEmu(str(rom), str(f), sym='')
        e.syms = syms
        e.boot_continue()
        settle(e)
        e.run(30)
        before = snapshot(e)
        stage('scene%d-Gym-start' % scene)
        report['objects_before_talk'] = object_rows(e, 1)
        e.shot(str(out / ('scene%d-gym-before.png' % scene)), scale=3)
        e.press('UP', hold=4, after=30)
        assert e.location()[2:] == (5, 3)
        e.press('A', hold=3, after=12)
        mash_until(e, e.in_battle, 300)
        assert battle_menu_checked()
        assert e.u16(syms['gTrainerBattleOpponent_A']) == const('TRAINER_HOENN_ROXANNE_1')
        turns = 0
        while battle_menu_checked():
            assert turns < 60, 'Roxanne battle exceeded turn bound'
            fight_one_turn(e, loss=False)
            turns += 1
        report['after_battle_before_dismiss'] = state()
        report['outcome_before_dismiss'] = e.u8(syms['gBattleOutcome'])
        emit()
        e.shot(str(out / ('scene%d-after-battle.png' % scene)), scale=3)
        idle()
        assert e.u8(syms['gBattleOutcome']) == const('B_OUTCOME_WON')
        assert blocks(e).trainer_beaten('TRAINER_HOENN_ROXANNE_1')
        assert all(blocks(e).flag(f) for f in F[:3])
        assert blocks(e).item_count('ITEM_TM39') == 1
        stage('scene%d-Roxanne-win' % scene)
        step('RIGHT')
        for _ in range(15):
            step('DOWN')
        step('LEFT')
        step('DOWN', warp=True)
        city = map_info('RustboroCity')
        assert e.location()[:2] == (city['group'], city['num'])
        stage('scene%d-Gym-exit' % scene)
        while e.location()[2] > 23:
            step('LEFT')
        assert e.location()[2] == 23 and 20 <= e.location()[3] <= 24
        idle()
        stage('scene%d-Devon-coord-complete' % scene)
        assert blocks(e).var('VAR_HOENN_SCENE_DEVON') == (2 if scene == 1 else 0)
        assert blocks(e).flag('FLAG_HIDE_HOENN_RUSTBORO_THIEF')
        ledger = preserve(before)
        e.shot(str(out / ('scene%d-city.png' % scene)), scale=3)
        saved_state = state()
        save = flash_reload(e, 'scene%d-Devon' % scene)
        assert state() == saved_state
        preserve(before)
        stage('scene%d-native-SAVE-cold' % scene)
        report['cases'].append({'scene_at_boot': scene, 'pass': True,
                                'actual_Roxanne_win': True, 'turns': turns,
                                'continuous_Gym_exit_and_City_coord': True,
                                'expected_theft': scene == 1, 'SAVE_cold': save,
                                'party_changes': ledger,
                                'party_PID_OT_multiplicities_preserved': True,
                                'PC_33744_bytes_preserved': True,
                                'existing_damaged_PC_record_preserved': True})
        emit()
        e.close()
        e = None
    report['pass'] = len(report['cases']) == 2
    report['status'] = 'complete'
except Exception as err:
    report['pass'] = False
    report['status'] = 'failed'
    report['error'] = repr(err)
    report['traceback'] = traceback.format_exc()
    if e is not None:
        try:
            report['failure_state'] = state()
            report['battle_outcome_failure'] = e.u8(syms['gBattleOutcome'])
            e.shot(str(out / 'failure.png'), scale=3)
        except Exception as diagnostic_error:
            report['diagnostic_error'] = repr(diagnostic_error)
finally:
    if e is not None:
        e.close()
    report['protected_original_inputs_unchanged'] = all(
        f.exists() and file_sha(f) == h for f, h in protected.items())
    if not report['protected_original_inputs_unchanged']:
        report['pass'] = False
        report['status'] = 'failed'
    emit()
print(json.dumps({'pass': report['pass'], 'status': report['status'],
                  'cases': len(report['cases']), 'error': report.get('error')}), flush=True)
raise SystemExit(0 if report['pass'] else 1)
