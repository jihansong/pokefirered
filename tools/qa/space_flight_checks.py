"""Ordinary-key exterior round trip from a disclosed, from-zero terminal seed.

Uses the existing read-only Guest protocol. Task layout comes from the fresh ARM
schema; task symbols, text and scene frame constants come from this source/ROM.
No guest write, callable special, warp, state-load or reset interface is used.
"""
import json
import re
import struct


class FlightChecks:
    def __init__(self, guest, tour, source):
        self.g, self.tour, self.source = guest, tour, source
        self.story = (source/'src/hoenn_space_story.c').read_text()
        self.samples = []
        self.tasks_seen = []
        for name in ('gTasks', 'Task_SpaceFlight', 'Task_YesNoMenu_HandleInput', 'gStringVar4'):
            assert name in guest.sym, ('Missing fresh flight symbol', name)
        for name in ('sizes.Task', 'offset.Task.func', 'offset.Task.isActive', 'offset.Task.data', 'constant.NUM_TASKS'):
            assert name in guest.values, ('Missing ARM task field', name)
        self.indices = {k: int(re.search(r'#define\s+t'+k+r'\s+data\[(\d+)\]', self.story).group(1))
                        for k in ('State', 'Frame', 'Returning')}
        for name in ('HoennSpaceportTerminal', 'HoennSpaceportLaunchPad'):
            tour.add_map(source/'data/maps'/name)

    def tasks(self):
        g, v = self.g, self.g.values
        size, count = v['sizes.Task'], v['constant.NUM_TASKS']
        raw = g.read(g.sym['gTasks'], size*count)
        result = []
        for i in range(count):
            cell = raw[i*size:(i+1)*size]
            if cell[v['offset.Task.isActive']]:
                result.append({'id': i, 'function': int.from_bytes(cell[v['offset.Task.func']:v['offset.Task.func']+4], 'little') & ~1,
                               'data': list(struct.unpack_from('<16h', cell, v['offset.Task.data']))})
        return result

    def task(self, name):
        rows = [x for x in self.tasks() if x['function'] == self.g.sym[name] & ~1]
        assert len(rows) <= 1
        return rows[0] if rows else None

    def text(self, label):
        expected = self.g.read(self.g.sym[label], 24).split(b'\xff', 1)[0]
        assert len(expected) >= 16
        return self.g.read(self.g.sym['gStringVar4'], 24).startswith(expected[:16])

    def choose_yes(self, label):
        for i in range(120):
            if self.task('Task_YesNoMenu_HandleInput'):
                assert self.text(label), ('Wrong YES/NO prompt', label, self.g.snapshot())
                self.g.step(0, 12)
                self.g.picture(label+'-yes-no')
                self.g.tap('A', settle=12)
                return
            assert not self.task('Task_SpaceFlight'), 'Flight started before observed YES choice'
            self.g.tap('A', settle=12) if i % 4 == 3 else self.g.step(0, 12)
        raise AssertionError(('YES/NO prompt not observed', label))

    def unlock(self, bound=16):
        for _ in range(bound):
            snap = self.g.snapshot()
            if self.g.field(snap) and not snap['script_locked']:
                return snap
            self.g.tap('A', settle=48)
        raise AssertionError(('Dialogue did not release', self.g.snapshot()))

    def flight(self, returning):
        length_name = 'SPACE_RETURN_FRAMES' if returning else 'SPACE_OUTBOUND_FRAMES'
        length = int(re.search(r'#define\s+'+length_name+r'\s+(\d+)', self.story).group(1))
        targets = ([0, 360, 479, 535, 536, 552, 567, 568, 569, 600, 631, 632,
                    720, 839, 900, 1020, 1320, 1560, length-1]
                   if not returning else [0, 627, 628, 629, 659, 660, 691, 692,
                                          900, 1020, 1080, 1140, 1200, 1320, length-1])
        # tFrame advances after RenderSpaceFrame; sample N after tFrame becomes N+1.
        observed = []
        for waiting in range(720):
            task = self.task('Task_SpaceFlight')
            if task is not None:
                break
            # Returning has one ordinary secure-seat message before PlayFlight.
            # Poll each frame so setup cannot advance unnoticed between taps.
            self.g.step(1 if returning and waiting % 48 == 47 else 0, 1)
        else:
            raise AssertionError('Normal boarding did not create flight task')
        seen_running = False
        for _ in range(length+240):
            task = self.task('Task_SpaceFlight')
            if task is None:
                break
            data = task['data']
            assert data[self.indices['Returning']] == int(returning)
            state, frame = data[self.indices['State']], data[self.indices['Frame']]
            if state == 0 or state == 1 and frame == 0:
                seen_running = True
                rendered = length-1 if state == 1 else frame-1
                if rendered in targets and rendered not in observed:
                    name = ('return' if returning else 'outbound')+'-frame-%04d' % rendered
                    self.g.picture(name)
                    observed.append(rendered)
                    self.samples.append({'scene': 'return' if returning else 'outbound', 'rendered_frame': rendered,
                                         'task': task, 'video_frame': self.g.last_status.get('video_frames', 0), 'picture': name+'.ppm'})
            self.g.step(0, 1)
        else:
            raise AssertionError('Flight task exceeded source duration and cleanup bound')
        assert seen_running and observed == targets, ('Flight frame coverage incomplete', returning, observed, targets)
        expected = 'HoennSpaceportLaunchPad' if returning else 'HoennSpacecraftCabin'
        for _ in range(90):
            snap = self.g.snapshot()
            if self.g.field(snap) and not snap['script_locked'] and self.tour.name(snap) == expected:
                assert snap['xy'] == ([15, 18] if returning else [10, 12]), snap
                self.g.picture('after-'+('landing' if returning else 'outbound'))
                self.tasks_seen.append({'returning': returning, 'duration': length, 'sampled_frames': observed, 'destination': snap})
                return
            self.g.step(0, 12)
        raise AssertionError(('Flight destination did not unlock', expected, self.g.snapshot()))

    def run(self):
        t, g = self.tour, self.g
        assert t.name() == 'HoennSpaceportTerminal' and g.snapshot()['xy'] == [8, 7]
        terminal_before = g.snapshot()
        g.step(64, 1); g.step(0, 12); g.tap('A', settle=24)
        self.choose_yes('Space_Text_Offer')
        self.unlock()
        assert g.snapshot()['map'] == terminal_before['map']
        t.crossing('HoennSpaceportTerminal', 1)
        t.walk('HoennSpaceportLaunchPad', (15, 13))
        t.move('N')
        assert g.snapshot()['xy'] == [15, 12]
        self.choose_yes('Space_Text_Board')
        self.flight(False)
        # Use the unchanged in-game exit tile, not a direct special invocation.
        t.walk('HoennSpacecraftCabin', (10, 13)); t.move('S')
        assert g.snapshot()['xy'] == [10, 14]
        self.choose_yes('Space_Text_Return')
        self.flight(True)
        assert not self.task('Task_SpaceFlight')
        return {'status': 'PASS_NORMAL_KEYS_OUTBOUND_RETURN', 'scenes': self.tasks_seen, 'frame_samples': self.samples,
                'normal_registration': True, 'runtime_memory_writes': 0,
                'scope': 'Synthetic terminal start, normal registration, boarding, full source-duration scenes and ordinary exit return; pixel quality reviewed separately.'}


def run_flight_checks(guest, tour, source):
    return FlightChecks(guest, tour, source).run()
