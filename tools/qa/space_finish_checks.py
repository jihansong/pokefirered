"""Normal-key plant collision/camera cases; call only on a selected fresh ROM.

The case document must be frozen against the selected source18 layout. This
module has no import-time I/O and does not start a host, warp, or write RAM.
"""
import json
from collections import deque
from copy import deepcopy


KEYS = {'N': 64, 'S': 128, 'E': 16, 'W': 32}


def run_finish_checks(guest, tour, cases_path):
    document = json.loads(cases_path.read_text(encoding='utf-8'))
    assert document['strategy'] == 'two_row_blocked'
    room = document['map']
    initial = guest.snapshot()
    assert tour.name() == room and guest.field(initial) and not initial['script_locked']
    crossing_start = len(tour.crossings)
    map_ids = {x['definition']['id']: name for name, x in tour.maps.items()}

    def reach(destination):
        current = tour.name()
        q, previous = deque([current]), {current: None}
        while q and destination not in previous:
            name = q.popleft()
            for index, warp in enumerate(tour.maps[name]['definition']['warp_events']):
                target = map_ids.get(warp['dest_map'])
                if target is not None and target not in previous:
                    previous[target] = (name, index)
                    q.append(target)
        assert destination in previous, ('No ordinary door route', current, destination)
        route, name = [], destination
        while previous[name] is not None:
            source, index = previous[name]
            route.append((source, index, name))
            name = source
        for source, index, target in reversed(route):
            assert tour.name() == source
            actual, _ = tour.crossing(source, index)
            assert actual == target
        assert tour.name() == destination and not guest.snapshot()['script_locked']

    expected_rooms = document['expected_rooms']
    assert len(expected_rooms) == len(set(expected_rooms)) == 17
    assert set(expected_rooms) == set(tour.maps), 'Finish observations require the separate seventeen-room Tour'
    records, cameras, visited = [], [], []
    for destination in expected_rooms:
        reach(destination)
        visited.append(destination)
        for case in document['blocked_approaches']:
            if case.get('map', room) != destination:
                continue
            tour.walk(destination, tuple(case['stand']))
            before = guest.snapshot()
            assert before['xy'] == case['stand'] and not before['script_locked']
            guest.step(KEYS[case['direction']], 12)
            guest.step(0, 12)
            after = guest.snapshot()
            assert after['map'] == before['map'] and after['xy'] == before['xy'], ('Solid footprint admits player', case, before, after)
            assert guest.field(after) and not after['script_locked']
            name = 'finish18-blocked-'+case['id']
            guest.picture(name)
            records.append({'id': case['id'], 'map': destination, 'before': before, 'after': after,
                            'picture': name+'.ppm', 'video_frame': guest.last_status.get('video_frames')})
        for case in document['camera_positions']:
            if case['map'] != destination:
                continue
            tour.walk(destination, tuple(case['stand']))
            snap = guest.snapshot()
            assert snap['xy'] == case['stand'] and not snap['script_locked']
            name = 'finish18-camera-'+case['id']
            guest.picture(name)
            cameras.append({'id': case['id'], 'map': destination, 'snapshot': snap,
                            'acceptance_ids': case.get('acceptance_ids', []),
                            'picture': name+'.ppm', 'video_frame': guest.last_status.get('video_frames')})
    reach(room)
    tour.walk(room, tuple(initial['xy']))
    final = guest.snapshot()
    assert guest.field(final) and not final['script_locked'] and final['xy'] == initial['xy']
    assert len(records) == document['expected_counts']['blocked_attempts']
    assert len(cameras) == document['expected_counts']['cameras']
    assert set(x['map'] for x in cameras) == set(expected_rooms)
    return {'status': 'PASS_NORMAL_KEYS_FINISH_OBSERVATIONS_VISUAL_REVIEW_PENDING',
            'candidate': document['candidate'], 'blocked_attempts': records, 'cameras': cameras,
            'visited_rooms': visited, 'expected_counts': deepcopy(document['expected_counts']),
            'finish_directional_crossings': deepcopy(tour.crossings[crossing_start:]),
            'before': initial, 'after': final, 'runtime_memory_writes': 0,
            'scope': 'Explicit solid-collision attempts and seventeen-room close observation positions. Completed video must independently establish frames, thresholds, corners, caps, furniture and floor continuity. No whole-map visual perfection or iOS claim.'}
