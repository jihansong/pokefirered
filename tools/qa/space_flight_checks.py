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
        self.observations = []
        self.gpu_blend_checks = []
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
                                          900, 1020, 1080, 1100, 1139, 1140, 1141, 1200, 1260,
                                          1317, 1318, 1319, 1320, 1387, length-1])
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
                video = self.g.last_status.get('video_frames', 0)
                assert not self.observations or not self.observations[-1]['scene'] == ('return' if returning else 'outbound') or rendered >= self.observations[-1]['observed_index'], 'Task index went backwards'
                self.observations.append({'scene': 'return' if returning else 'outbound',
                                          'observed_index': rendered, 'video_frame': video})
                if len(observed) < len(targets) and rendered >= targets[len(observed)]:
                    requested = targets[len(observed)]
                    previous = next((x for x in reversed(self.samples) if x['scene'] == ('return' if returning else 'outbound')), None)
                    if previous is None or rendered > previous['observed_index']:
                        lag = rendered - requested
                        assert 0 <= lag <= 1, ('Task sample exceeded one-index observation delay', requested, rendered)
                        if requested in (0, length-1):
                            assert lag == 0, ('Scene endpoint must be observed exactly', requested, rendered)
                        name = ('return' if returning else 'outbound')+'-requested-%04d-observed-%04d' % (requested, rendered)
                        if returning and requested == 660:
                            # Hardware registers are source-defined ARM constants;
                            # no fixed semantic RAM address or guest write is used.
                            values = self.g.values
                            def io_word(register):
                                return int.from_bytes(self.g.read(values['constant.REG_BASE']+
                                    values['constant.REG_OFFSET_'+register], 2), 'little')
                            registers = {key: io_word(key) for key in ('BG3CNT', 'BLDCNT', 'BLDALPHA')}
                            assert registers['BG3CNT'] & 3 == 0, ('Earth priority not committed before ShowBg', registers)
                            assert registers['BLDCNT'] & 0x3f == 8 and registers['BLDCNT'] >> 6 & 3 == 1
                            assert registers['BLDCNT'] >> 8 & 6 == 6, ('Runway/tower missing blend second-target', registers)
                            coefficients = [registers['BLDALPHA'] & 31, registers['BLDALPHA'] >> 8 & 31]
                            assert sum(coefficients) == 16 and all(0 < x < 16 for x in coefficients)
                            self.gpu_blend_checks.append({'requested_index': requested, 'observed_index': rendered,
                                                          'video_frame': video, 'hardware_registers': registers})
                        self.g.picture(name)
                        observed.append(requested)
                        self.samples.append({'scene': 'return' if returning else 'outbound',
                                             'requested_index': requested, 'observed_index': rendered,
                                             'observation_delay': lag, 'task': task, 'video_frame': video,
                                             'previous_observation': self.observations[-2] if len(self.observations) > 1 else None,
                                             'picture': name+'.ppm'})
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
                self.tasks_seen.append({'returning': returning, 'duration': length, 'nominal_task_duration': length, 'requested_samples_covered': observed, 'destination': snap})
                return
            self.g.step(0, 12)
        raise AssertionError(('Flight destination did not unlock', expected, self.g.snapshot()))

    def run(self, interior_check=None):
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
        interior = interior_check(t) if interior_check is not None else None
        # Use the unchanged in-game exit tile, not a direct special invocation.
        t.walk('HoennSpacecraftCabin', (10, 13)); t.move('S')
        assert g.snapshot()['xy'] == [10, 14]
        self.choose_yes('Space_Text_Return')
        self.flight(True)
        assert not self.task('Task_SpaceFlight')
        return {'status': 'PASS_NORMAL_KEYS_OUTBOUND_RETURN', 'scenes': self.tasks_seen, 'frame_samples': self.samples,
                'task_video_observations': self.observations, 'interior_check': interior,
                'gpu_blend_checks': self.gpu_blend_checks,
                'normal_registration': True, 'runtime_memory_writes': 0,
                'scope': 'Synthetic terminal start, normal registration, boarding, full source-duration scenes and ordinary exit return; pixel quality reviewed separately.'}


def run_flight_checks(guest, tour, source, interior_check=None):
    return FlightChecks(guest, tour, source).run(interior_check)
