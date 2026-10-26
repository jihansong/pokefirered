#!/usr/bin/env python3
"""Normal Continue tests from zero-created public saved-player records.

All edits happen before boot in fresh synthetic flash buffers. No input-save,
runtime write, warp call, quickstate or reset interface is accepted.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
import struct
import traceback

from make_ty28_fixture import Schema, construct, payload_sizes, validate_ty28, write_flash
from space_runtime_probe import Guest, Tour, DELTA, REVERSE


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_saved_player(s, sb1):
    base = s.offset('SaveBlock1', 'objectEvents')
    xy = [s.get(sb1, 'Coords16', axis, s.offset('SaveBlock1', 'pos')) for axis in ('x', 'y')]
    for field in ('initialCoords', 'currentCoords', 'previousCoords'):
        offset = base+s.offset('ObjectEvent', field)
        assert [s.get(sb1, 'Coords16', axis, offset)-s.c('MAP_OFFSET') for axis in ('x', 'y')] == xy


def saved_player_fixture(source, schema, recipe):
    """Serialize one active saved player using only the fresh target ARM ABI."""
    recipe = deepcopy(recipe)
    recipe['continue_warp'] = False
    raw, validation, party, additional = construct(source, schema, recipe)
    s = Schema(schema)
    # These bytes were constructed immediately above, never read from a save.
    payload = b''.join(raw[i*s.c('SECTOR_SIZE'):i*s.c('SECTOR_SIZE')+size]
                       for i, size in enumerate(payload_sizes(s)))
    blocks = []
    cursor = 0
    for name in ('SaveBlock2', 'SaveBlock1', 'PokemonStorage', 'PokemonStorageExtra'):
        size = s.size(name)
        blocks.append(bytearray(payload[cursor:cursor+size]))
        cursor += size
    assert cursor == len(payload)
    sb2, sb1, _, _ = blocks
    assert s.get(sb2, 'SaveBlock2', 'specialSaveWarpFlags') == 0
    base = s.offset('SaveBlock1', 'objectEvents')
    assert s.width('SaveBlock1', 'objectEvents') == s.size('ObjectEvent')*s.c('OBJECT_EVENTS_COUNT')
    map_id = s.resolve(recipe['map'])
    xy = (int(recipe['x']), int(recipe['y']))
    for field, value in [('graphicsId', s.c('OBJ_EVENT_GFX_RED_NORMAL')),
                         ('movementType', s.c('MOVEMENT_TYPE_PLAYER')),
                         ('localId', s.c('OBJ_EVENT_ID_PLAYER')),
                         ('mapNum', map_id & 255), ('mapGroup', map_id >> 8)]:
        s.put(sb1, 'ObjectEvent', field, value, base)
    for field, value in [('active', 1), ('isPlayer', 1), ('trackedByCamera', 1),
                         ('invisible', 0), ('facingDirection', s.c('DIR_SOUTH')),
                         ('movementDirection', s.c('DIR_SOUTH'))]:
        s.bits(sb1, 'ObjectEvent', field, value, base)
    definition = json.loads((source/'data/maps'/recipe['_map_name']/'map.json').read_bytes())
    layouts = json.loads((source/'data/layouts/layouts.json').read_bytes())['layouts']
    layout = next(x for x in layouts if x.get('id') == definition['layout'])
    cells = (source/layout['blockdata_filepath']).read_bytes()
    word = struct.unpack_from('<H', cells, (xy[1]*layout['width']+xy[0])*2)[0]
    elevation = word >> 12
    for field in ('currentElevation', 'previousElevation'):
        s.bits(sb1, 'ObjectEvent', field, elevation, base)
    for field in ('initialCoords', 'currentCoords', 'previousCoords'):
        offset = base+s.offset('ObjectEvent', field)
        for axis, value in zip(('x', 'y'), xy):
            s.put(sb1, 'Coords16', axis, value+s.c('MAP_OFFSET'), offset)
    if recipe.get('_active_misty', False):
        follower = base+s.size('ObjectEvent')
        for field, value in [('spriteId', 1), ('graphicsId', s.c('OBJ_EVENT_GFX_MISTY_COMPANION')),
                             ('movementType', s.c('MOVEMENT_TYPE_NONE')),
                             ('localId', s.c('LOCALID_MISTY_COMPANION')),
                             ('mapNum', map_id & 255), ('mapGroup', map_id >> 8)]:
            s.put(sb1, 'ObjectEvent', field, value, follower)
        for field, value in [('active', 1), ('isPlayer', 0), ('invisible', 0),
                             ('facingDirection', s.c('DIR_SOUTH')), ('movementDirection', s.c('DIR_SOUTH')),
                             ('currentElevation', elevation), ('previousElevation', elevation)]:
            s.bits(sb1, 'ObjectEvent', field, value, follower)
        for field in ('initialCoords', 'currentCoords', 'previousCoords'):
            offset = follower+s.offset('ObjectEvent', field)
            for axis, value in zip(('x', 'y'), xy):
                s.put(sb1, 'Coords16', axis, value+s.c('MAP_OFFSET'), offset)
    assert s.get(sb1, 'Coords16', 'x', s.offset('SaveBlock1', 'pos')) == xy[0]
    assert s.get(sb1, 'Coords16', 'y', s.offset('SaveBlock1', 'pos')) == xy[1]
    check_saved_player(s, sb1)
    bad = bytearray(sb1)
    s.put(bad, 'Coords16', 'x', xy[0]+s.c('MAP_OFFSET')+1, base+s.offset('ObjectEvent', 'currentCoords'))
    try:
        check_saved_player(s, bad)
    except AssertionError:
        mismatch_rejected = True
    else:
        raise AssertionError('Saved-player fixture mismatch was accepted')
    rebuilt = write_flash(s, blocks, int(recipe.get('counter', 1)))
    validation = validate_ty28(rebuilt, s)
    return rebuilt, {'validation': validation, 'saved_player': {'slot': 0, 'active': True,
                     'isPlayer': True, 'map': [map_id >> 8, map_id & 255], 'xy': list(xy),
                     'three_object_coordinate_pairs_match': True,
                     'negative_saved_player_mismatch_rejected': mismatch_rejected},
                     'parents': [], 'save_inputs_read': 0, 'party': party,
                     'additional_map_source_sha256': additional}


def read_misty(guest, s):
    def bit(raw, type_name, field):
        p = s.data['bitfields'][type_name+'.'+field]
        value = int.from_bytes(raw[p['offset']:p['offset']+p['size']], 'little')
        return (value & p['mask']) >> p['shift']
    rows = []
    size = s.size('ObjectEvent')
    objects = guest.read(guest.sym['gObjectEvents'], size*s.c('OBJECT_EVENTS_COUNT'))
    for i in range(s.c('OBJECT_EVENTS_COUNT')):
        raw = objects[i*size:(i+1)*size]
        if not bit(raw, 'ObjectEvent', 'active') or s.get(raw, 'ObjectEvent', 'localId') != s.c('LOCALID_MISTY_COMPANION'):
            continue
        sprite_id = s.get(raw, 'ObjectEvent', 'spriteId')
        assert sprite_id < s.c('MAX_SPRITES')
        assert s.get(raw, 'ObjectEvent', 'graphicsId') == s.c('OBJ_EVENT_GFX_MISTY_COMPANION')
        sprite = guest.read(guest.sym['gSprites']+sprite_id*s.size('Sprite'), s.size('Sprite'))
        assert bit(sprite, 'Sprite', 'inUse')
        avatar = guest.read(guest.sym['gPlayerAvatar'], s.size('PlayerAvatar'))
        player_id = s.get(avatar, 'PlayerAvatar', 'objectEventId')
        assert player_id < s.c('OBJECT_EVENTS_COUNT')
        player = objects[player_id*size:(player_id+1)*size]
        assert bit(player, 'ObjectEvent', 'active') and bit(player, 'ObjectEvent', 'isPlayer')
        coords = {field: [s.get(raw, 'Coords16', axis, s.offset('ObjectEvent', field))-s.c('MAP_OFFSET')
                          for axis in ('x', 'y')]
                  for field in ('initialCoords', 'currentCoords', 'previousCoords')}
        rows.append({'slot': i, 'local_id': s.c('LOCALID_MISTY_COMPANION'), 'coordinates': coords,
                     'graphics_id': s.get(raw, 'ObjectEvent', 'graphicsId'),
                     'current_elevation': bit(raw, 'ObjectEvent', 'currentElevation'),
                     'previous_elevation': bit(raw, 'ObjectEvent', 'previousElevation'),
                     'player_current_elevation': bit(player, 'ObjectEvent', 'currentElevation'),
                     'player_previous_elevation': bit(player, 'ObjectEvent', 'previousElevation'),
                     'invisible': bool(bit(raw, 'ObjectEvent', 'invisible')),
                     'off_screen': bool(bit(raw, 'ObjectEvent', 'offScreen')),
                     'sprite_id': sprite_id, 'sprite_in_use': bool(bit(sprite, 'Sprite', 'inUse')),
                     'sprite_invisible': bool(bit(sprite, 'Sprite', 'invisible')),
                     'sprite_position': {field: int.from_bytes(sprite[s.offset('Sprite', field):s.offset('Sprite', field)+s.width('Sprite', field)], 'little', signed=True)
                                         for field in ('x', 'y', 'x2', 'y2')}})
    assert len(rows) == 1, ('One active Misty required', rows)
    return rows[0]


def misty_recovery(args, document, schema, base_recipe):
    case = document['misty_case']
    assert case['xy'] == [10, 3] and case['expected_xy'] == [10, 12]
    assert case['map'] == 'HoennSpacecraftCockpit' and case['normal_walk'] == ['E', 'E', 'E']
    s = Schema(schema)
    assert s.c(case['saved_local_id']) == 253
    recipe = deepcopy(base_recipe)
    recipe.update(map=case['map_token'], x=10, y=3, _map_name=case['map'], _active_misty=True)
    recipe['flags'][case['joined_flag']] = True
    raw, provenance = saved_player_fixture(args.source, schema, recipe)
    folder = args.artifact_dir/case['id']
    folder.mkdir()
    seed = folder/'public-misty.sav'
    with seed.open('xb') as stream:
        stream.write(raw)
    seed_hash = digest(seed)
    (folder/'fixture.json').write_text(json.dumps({'recipe': recipe, **provenance,
          'active_misty_local_id': 253, 'sha256': seed_hash}, indent=2)+'\n')
    guest = None
    try:
        guest = Guest(args, seed, folder/'continue', 'unused-no-export.sav')
        after = guest.boot()
        expected_map = s.resolve(case['map_token'])
        assert after['map'] == [expected_map >> 8, expected_map & 255]
        assert after['xy'] == case['expected_xy']
        initial = read_misty(guest, s)
        assert all(x == case['expected_xy'] for x in initial['coordinates'].values())
        assert initial['invisible'] and initial['sprite_invisible']
        assert initial['current_elevation'] == initial['previous_elevation']
        assert initial['current_elevation'] == initial['player_current_elevation'] == initial['player_previous_elevation']
        guest.picture('recovered-misty-hidden-under-player')
        tour = Tour(guest, args.source)
        observations = []
        for i, direction in enumerate(case['normal_walk'], 1):
            moved = tour.move(direction)
            assert moved['xy'] == [10+i, 12] and not moved['script_locked']
            observations.append({'player': moved, 'misty': read_misty(guest, s)})
        final = observations[-1]['misty']
        assert not final['invisible'] and not final['sprite_invisible'] and not final['off_screen']
        assert final['coordinates']['currentCoords'] != observations[-1]['player']['xy']
        assert sum(abs(a-b) for a, b in zip(final['coordinates']['currentCoords'], observations[-1]['player']['xy'])) in (1, 2)
        guest.picture('recovered-misty-visible-after-three-normal-steps')
        guest.close()
        guest = None
        assert digest(seed) == seed_hash and not (folder/'continue/unused-no-export.sav').exists()
        return {'status': 'PASS_ACTIVE_MISTY_RECOVERY_AND_NORMAL_REVEAL', 'after': after,
                'initial': initial, 'normal_steps': observations, 'seed_sha256_unchanged': seed_hash,
                'exit_code': 0, 'runtime_memory_writes': 0, 'Pikachu_runtime_verified': False}
    finally:
        if guest is not None:
            guest.close()


def run(args):
    source = args.source
    document = json.loads((source/'tools/qa/space-position-cases.json').read_bytes())
    assert document['legacy_count'] == 28 and document['unchanged_controls'] == 4
    assert len(document['cases']) == 32 and len({x['id'] for x in document['cases']}) == 32
    base_recipe = json.loads((source/document['base_recipe']).read_bytes())
    schema = json.loads(args.schema.read_bytes())
    s = Schema(schema)
    result = {'status': 'STARTED_NOT_PASS', 'rom_sha256': digest(args.rom),
              'schema_sha256': digest(args.schema), 'symbols_sha256': digest(args.symbols),
              'host_sha256': digest(args.host), 'cases': [], 'runtime_memory_writes': 0,
              'private_save_inputs': 0, 'active_misty_recovery_verified': False, 'Pikachu_runtime_verified': False,
              'scope': '32 independent fresh normal Continues plus one active Misty case from source-only CI_TEST preboot records; no normal SAVE or installed iOS Delta claim'}
    try:
        for case in document['cases']:
            assert re.fullmatch(r'[a-z0-9-]{1,80}', case['id'])
            result['attempted_case'] = case['id']
            folder = args.artifact_dir/case['id']
            folder.mkdir()
            recipe = deepcopy(base_recipe)
            recipe.update(map=case['map_token'], x=case['xy'][0], y=case['xy'][1], _map_name=case['map'])
            raw, provenance = saved_player_fixture(source, schema, recipe)
            seed = folder/'public-position.sav'
            with seed.open('xb') as stream:
                stream.write(raw)
            seed_hash = digest(seed)
            (folder/'fixture.json').write_text(json.dumps({'recipe': recipe, **provenance,
                 'sha256': seed_hash, 'origin': 'Zero buffers; active player added before first boot using fresh ARM offsets/bitfields'}, indent=2)+'\n')
            guest = None
            try:
                guest = Guest(args, seed, folder/'continue', 'unused-no-export.sav')
                after = guest.boot()
                expected_map = s.resolve(case['map_token'])
                assert after['map'] == [expected_map >> 8, expected_map & 255]
                assert after['xy'] == case['expected_xy'], ('Wrong recovery or unnecessary relocation', case, after)
                pointer = guest.number('gSaveBlock1Ptr')
                saved_xy = list(struct.unpack('<hh', guest.read(pointer+s.offset('SaveBlock1', 'pos'), s.size('Coords16'))))
                assert saved_xy == case['expected_xy'], ('Saved coordinate/object mismatch', case, saved_xy, after)
                guest.picture('normal-continued-position')
                tour = Tour(guest, source)
                here = tuple(after['xy'])
                definition = tour.maps[case['map']]['definition']
                events = {(x['x'], x['y']) for x in definition['warp_events']+definition['coord_events']}
                candidates = [(direction, (here[0]+dx, here[1]+dy)) for direction, (dx, dy) in DELTA.items()
                              if (here[0]+dx, here[1]+dy) in tour.maps[case['map']]['floor']-events]
                assert candidates, ('Recovered tile has no ordinary exit', case)
                direction, goal = candidates[0]
                moved = tour.move(direction)
                assert moved['xy'] == list(goal) and moved['map'] == after['map'] and not moved['script_locked']
                returned = tour.move(REVERSE[direction])
                assert returned['xy'] == after['xy'] and returned['map'] == after['map'] and not returned['script_locked']
                guest.tap('START', settle=40)
                assert guest.number('sNumStartMenuItems', 1) > 0 and guest.snapshot()['script_locked']
                assert guest.number('sStartMenuCallback') & ~1 == guest.sym['StartCB_HandleInput'] & ~1
                guest.picture('normal-start-menu')
                guest.tap('B')
                assert guest.field(guest.snapshot()) and not guest.snapshot()['script_locked']
                guest.close()
                guest = None
                assert digest(seed) == seed_hash and not (folder/'continue/unused-no-export.sav').exists()
                result['cases'].append({'id': case['id'], 'kind': case['kind'], 'preboot_xy': case['xy'],
                    'expected_xy': case['expected_xy'], 'after': after, 'saved_xy': saved_xy,
                    'normal_walk': {'out': moved, 'returned': returned}, 'menu_controls': True,
                    'seed_sha256_unchanged': seed_hash, 'exit_code': 0})
            finally:
                if guest is not None:
                    guest.close()
        assert sum(x['kind'] == 'legacy_recovery' for x in result['cases']) == 28
        assert sum(x['kind'] == 'normal_open_control' for x in result['cases']) == 4
        result['misty_recovery'] = misty_recovery(args, document, schema, base_recipe)
        result['active_misty_recovery_verified'] = True
        result['status'] = 'PASS_28_LEGACY_AND_4_UNCHANGED_NORMAL_CONTINUES'
    except Exception:
        result['status'] = 'FAIL_NOT_VERIFIED'
        result['error'] = traceback.format_exc()
        raise
    finally:
        (args.artifact_dir/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'host', 'schema', 'rom', 'symbols', 'artifact-dir'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    for name in ('source', 'host', 'schema', 'rom', 'symbols'):
        setattr(args, name, getattr(args, name).resolve(strict=True))
    assert not args.artifact_dir.exists() and not args.artifact_dir.resolve().is_relative_to(args.source)
    args.artifact_dir.mkdir(mode=0o700)
    args.artifact_dir = args.artifact_dir.resolve(strict=True)
    args.video = False
    result = run(args)
    print(json.dumps({'status': result['status'], 'fresh_processes': len(result['cases'])+1}))


if __name__ == '__main__':
    main()
