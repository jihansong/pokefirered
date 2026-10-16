"""Real A-button checks for the guarded Devon dialogue follow-up.

Pre-boot temporary eligibility/position fixtures only. No RAM writes, direct
event calls, party edits, forced battles or campaign-completion claims.
Requires the sixteen-file candidate already applied and rebuilt by root.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

BASIC_SHA = '5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
report = {'pass': False, 'cases': [], 'ram_writes': 0,
          'direct_script_calls': 0, 'forced_battle_outcomes': 0,
          'full_Hoenn_campaign_tested': False, 'status': 'preflight'}


def digest_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    for name in ['root', 'rom', 'elf', 'sav', 'out', 'package']:
        p.add_argument('--' + name, required=True, type=Path)
    for name in ['rom', 'elf', 'sav']:
        p.add_argument('--expect-' + name + '-sha', required=True)
    args = p.parse_args()
    args.root = args.root.resolve(strict=True)
    for name in ['rom', 'elf', 'sav', 'package']:
        setattr(args, name, getattr(args, name).resolve(strict=True))
    args.out = args.out.resolve()
    if args.out.exists():
        raise RuntimeError('Use a new evidence directory')
    args.out.mkdir(parents=True, exist_ok=False)
    os.chdir(args.root)
    for name in ['rom', 'elf', 'sav']:
        actual = digest_file(getattr(args, name))
        assert actual == getattr(args, 'expect_' + name + '_sha'), ('Input hash changed', name)
        report[name + '_sha256'] = actual
    manifest = json.loads((args.package / 'manifest.json').read_text())
    assert manifest['static']['pass'] and len(manifest['files']) == 8
    protected = {p.resolve(): digest_file(p) for p in (args.root / 'saves').rglob('*.sav')}
    for name in ['rom', 'elf', 'sav']:
        f = getattr(args, name)
        protected[f] = digest_file(f)
    for row in manifest['files']:
        for rel, want in [(row['path'], row['candidate_sha256']),
                          (row['canonical_path'], row['canonical_sha256'])]:
            f = args.root / rel
            assert digest_file(f) == want, ('Story candidate not applied', rel)
            protected[f] = want
    base = args.root / 'tools/qa/native_misty_basic_qa.py'
    assert digest_file(base) == BASIC_SHA
    marker = '\nresults=[];rows=[]\n'
    q = base.read_text()
    assert q.count(marker) == 1
    sys.argv = ['storyhint', '--rom', str(args.rom), '--elf', str(args.elf),
                '--sav', str(args.sav), '--out', str(args.out)]
    scope = {}
    exec(compile(q.split(marker)[0], '<verified-definitions-only>', 'exec'), scope)
    # These functions use RAM hooks in the original basic test; never use them.
    def forbidden(*a, **kw):
        raise AssertionError('Direct engine calls forbidden in storyhint QA')
    for name in ['call', 'flag', 'trail']:
        scope[name] = forbidden
    Emu = scope['ReadOnlyEmu']
    Save = scope['SaveFile']
    syms, sets = scope['syms'], scope['sets']
    settle, safe = scope['settle'], scope['safe']
    record, same_records = scope['record'], scope['same_records']
    blocks, off = scope['blocks'], scope['off']
    flash_reload = scope['flash_reload']
    report['status'] = 'running'
    fixtures = args.out / 'preboot-fixtures'
    fixtures.mkdir()
    cases = []
    for scene, suffix in [(0, 'H1'), (2, 'DispatchChase'), (3, 'DispatchRecovered'),
                          (4, 'DispatchWaiting'), (5, 'DispatchReward'), (6, 'DispatchDone')]:
        cases.append(('dispatch-scene%d' % scene, 'RustboroCity_DevonCorp_1F',
                      15, 6, 'UP', 2, scene, False,
                      'RustboroCity_DevonCorp_1F_Text_' + suffix))
    for scene, suffix in [(0, 'H1'), (3, 'AssistantRecovered'), (4, 'AssistantWaiting'),
                          (5, 'AssistantReward'), (6, 'AssistantDone')]:
        cases.append(('assistant-scene%d' % scene, 'RustboroCity_DevonCorp_3F',
                      14, 5, 'RIGHT', 2, scene, False,
                      'RustboroCity_DevonCorp_3F_Text_' + suffix))
    for opened in [False, True]:
        cases.append(('tunnel-sign-' + str(opened), 'Route116', 48, 10, 'UP', 0,
                      0, opened, 'Route116_Text_' + ('TunnelSignFinished' if opened else 'H11')))
        cases.append(('hiker-' + str(opened), 'RusturfTunnel', 31, 13, 'RIGHT', 3,
                      0, opened, 'RusturfTunnel_Text_' + ('HikerFinished' if opened else 'H0_2')))

    def story_state(e):
        b = blocks(e)
        return {'scene': b.var('VAR_HOENN_SCENE_DEVON'),
                'flags': {n: b.flag(n) for n in ['FLAG_HOENN_GOT_EXP_SHARE',
                          'FLAG_HOENN_DEVON_GOODS_DELIVERED', 'FLAG_HOENN_RUSTURF_OPEN']},
                'mike_beaten': b.trainer_beaten('TRAINER_HOENN_MIKE_2')}

    def active_message(e):
        wanted = sets['Task_DrawFieldMessageBox']
        return [i for i in range(16) if e.u8(syms['gTasks'] + 40 * i + 4)
                and (e.u32(syms['gTasks'] + 40 * i) & ~1) in wanted
                and e.u16(syms['gTasks'] + 40 * i + 8) >= 2]

    def face_live_dispatch_staff(e):
        before = record(e)
        def read_live():
            loc = e.location()
            players = []
            for i in range(16):
                ptr = syms['gObjectEvents'] + i * off('misty_obj')
                flags = e.u32(ptr)
                if flags & 1 and flags & (1 << 16):
                    raw = scope['struct'].unpack('<hh', e.read(ptr + off('misty_obj.coords'), 4))
                    players.append((ptr, raw))
            assert len(players) == 1, ('Live player object missing', players)
            padding = (players[0][1][0] - loc[2], players[0][1][1] - loc[3])
            assert padding == (7, 7), ('Unexpected map coordinate padding', padding)
            npc = scope['object_rows'](e, 2)
            assert len(npc) == 1, ('Live dispatch staff missing', npc)
            xy = (npc[0]['xy'][0] - padding[0], npc[0]['xy'][1] - padding[1])
            assert 13 <= xy[0] <= 17 and 4 <= xy[1] <= 6, ('Staff left declared wander range', xy)
            moving = bool(e.u32(npc[0]['ptr']) & ((1 << 1) | (1 << 6)))
            return loc, xy, moving
        faces = {(0, -1): 'UP', (0, 1): 'DOWN', (-1, 0): 'LEFT', (1, 0): 'RIGHT'}
        for _ in range(120):
            safe(e)
            assert not e.in_battle() and e.field_idle(), 'Unexpected event while approaching staff'
            loc, xy, moving = read_live()
            delta = (xy[0] - loc[2], xy[1] - loc[3])
            if delta in faces:
                if moving:
                    e.run(1)
                    continue
                facing = faces[delta]
                e.press(facing, hold=1, after=0)
                now, current, still_moving = read_live()
                assert now == loc, ('Facing staff moved player', loc, now)
                if current == xy and not still_moving:
                    same_records(e, before)
                    return loc, facing, {'staff_xy': list(xy), 'staff_idle': True, 'actual_key_approach': True, 'ram_writes': 0}
                continue
            if loc[3] < 7:
                key = 'DOWN'
            elif loc[3] > 7:
                raise AssertionError(('Staff approach left verified floor', loc))
            elif loc[2] != xy[0]:
                key = 'RIGHT' if loc[2] < xy[0] else 'LEFT'
            else:
                key = 'UP'
            try:
                scope['one_tile'](e, key)
            except AssertionError as error:
                if not (error.args and isinstance(error.args[0], tuple) and error.args[0][0] == 'native step blocked'):
                    raise
                assert e.location() == loc, ('Blocked step changed position', loc, e.location())
                e.run(1)
        raise AssertionError(('Could not approach actual roaming staff', read_live()))

    def actual_A(e, tag, label, facing, local_id):
        assert label in syms, ('Rebuilt candidate text absent from ELF', label)
        raw = scope['r'].at(syms[label], 1024)
        end = raw.index(255)
        expected = raw[:end + 1]
        assert len(expected) < 1000 and 253 not in expected, 'Unexpected dynamic placeholder'
        live_approach = None
        if label.startswith('RustboroCity_DevonCorp_1F_Text_') and local_id == 2:
            position, facing, live_approach = face_live_dispatch_staff(e)
        else:
            position = e.location()
            e.press(facing, hold=1, after=30)
            assert e.location() == position, ('Facing input moved', tag, position, e.location())
        before_record, before_story = record(e), story_state(e)
        e.press('A', hold=3, after=1)
        for _ in range(300):
            safe(e)
            assert not e.in_battle(), ('Dialogue unexpectedly started battle', tag)
            if (e.read(syms['gStringVar4'], len(expected)) == expected
                    and active_message(e) and not e.field_idle()):
                break
            e.run(1)
        else:
            raise AssertionError(('Native A did not display expected text', tag, label,
                                  e.location(), e.u16(syms['gSpecialVar_LastTalked'])))
        if local_id:
            assert e.u16(syms['gSpecialVar_LastTalked']) == local_id
        e.run(45)
        image = args.out / (tag + '-actual-A.png')
        e.shot(str(image), scale=3)
        for _ in range(400):
            safe(e)
            assert not e.in_battle()
            if e.field_idle():
                break
            e.press('A', hold=2, after=12)
        else:
            raise AssertionError(('Dialogue did not close', tag))
        settle(e)
        same_records(e, before_record)
        assert story_state(e) == before_story, ('Hint changed story progress', tag)
        assert e.location() == position
        return {'live_staff_approach': live_approach, 'actual_A': True, 'expected_compiled_text_label': label,
                'compiled_text_sha256': hashlib.sha256(expected).hexdigest(),
                'message_task_and_expanded_text_verified': True,
                'image': str(image), 'party_PC_dex_preserved': True,
                'checked_story_state_preserved': True}

    def emit():
        (args.out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')

    emit()
    try:
        for tag, name, x, y, facing, local_id, scene, opened, label in cases:
            source = Save(str(args.sav))
            def fixture_pokemon_record(s):
                return (s.party_count(),
                        bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty') + 600]),
                        bytes(s.blocks['storage']), [s.dex_state(i) for i in range(1, 387)])
            original_pokemon = fixture_pokemon_record(source)
            source.fast_battles()
            source.set_flag('FLAG_SYS_GAME_CLEAR', True)
            source.set_flag('FLAG_HOENN_BIRCH_RESCUED', True)
            source.set_flag('FLAG_HOENN_GOT_EXP_SHARE', False)
            source.set_flag('FLAG_HOENN_DEVON_GOODS_DELIVERED', False)
            source.set_flag('FLAG_HOENN_RUSTURF_OPEN', opened)
            source.set_trainer_beaten('TRAINER_HOENN_MIKE_2', True)
            source.set_var('VAR_HOENN_SCENE_DEVON', scene)
            source.warp(name, x, y)
            assert fixture_pokemon_record(source) == original_pokemon, 'Fixture helper edited Pokemon'
            f = fixtures / (tag + '.sav')
            assert not f.exists()
            source.save(str(f))
            with Emu(str(args.rom), str(f), sym='') as e:
                e.syms = syms
                e.boot_continue()
                settle(e)
                e.run(30)
                m = scope['map_info'](name)
                assert e.location() == (m['group'], m['num'], x, y)
                result = {'case': tag, 'scene_fixture': scene, 'opened_fixture': opened,
                          'preboot_fixture_Pokemon_unmodified': True,
                          **actual_A(e, tag, label, facing, local_id)}
                if tag in ['dispatch-scene4', 'hiker-True']:
                    before, story = record(e), story_state(e)
                    result['native_SAVE_cold'] = flash_reload(e, tag)
                    same_records(e, before)
                    assert story_state(e) == story
                    result['cold_actual_A'] = actual_A(e, tag + '-cold', label, facing, local_id)
                report['cases'].append(result)
                emit()
                print(json.dumps({'case_done': tag}), flush=True)
        assert len(report['cases']) == 15
        report['pass'] = True
        report['status'] = 'complete'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = repr(error)
        raise
    finally:
        for f, wanted in protected.items():
            assert digest_file(f) == wanted, ('Protected original changed', str(f))
        report['original_inputs_and_applied_story_sources_unchanged'] = True
        emit()


if __name__ == '__main__':
    main()
