"""Service checks for an already-authorized Guest/Tour on the NEW candidate.

Importing does not launch a host. All actions use normal keys; RAM/SYM reads
only. The caller pins fresh ROM/SYM/schema/fixture and closes its host. The
existing host07 and public Linux Guest expose the same methods used here.
"""
from collections import deque
from copy import deepcopy
import json
from pathlib import Path
import struct

DIR_KEYS = {'N': 64, 'S': 128, 'W': 32, 'E': 16}


class ServiceChecks:
    def __init__(self, guest, tour, candidate_id):
        assert candidate_id, 'Explicit new candidate required'
        self.g, self.tour, self.candidate_id = guest, tour, candidate_id
        self.records = []
        for name in ('gStringVar4', 'gSpecialVar_LastTalked', 'gPlayerParty', 'gPlayerPartyCount',
                     'gSaveBlock1Ptr', 'gSaveBlock2Ptr', 'CB2_BuyMenu'):
            assert name in guest.sym, ('Missing fresh candidate symbol', name)
        required = ['sizes.Pokemon']
        for kind, fields in (
            ('SaveBlock1', ['money', 'bagPocket_Items', 'bagPocket_KeyItems', 'bagPocket_PokeBalls', 'bagPocket_TMHM', 'bagPocket_Berries', 'unused_348C']),
            ('SaveBlock2', ['filler_DA0']),
            ('Pokemon', ['hp', 'maxHP', 'status']),
            ('BoxPokemon', ['personality', 'otId', 'secure', 'checksum']),
            ('PokemonSubstruct1', ['moves', 'pp']),
            ('PokemonSubstruct0', ['ppBonuses'])):
            for field in fields:
                required.extend(['offset.'+kind+'.'+field, 'size.'+kind+'.'+field])
        assert all(k in guest.values for k in required), ('Missing source-derived ABI fields', [k for k in required if k not in guest.values])
        assert guest.values['sizes.Pokemon'] == 100 and guest.values['size.BoxPokemon.secure'] == 48
        assert all(k in guest.schema for k in ('substruct_positions', 'move_pp'))

    def text_matches(self, label):
        assert label in self.g.sym, ('Missing candidate ROM text symbol', label)
        expected = self.g.read(self.g.sym[label], 48).split(b'\xff', 1)[0]
        # These facility prompts start with literal text, not placeholders.
        assert len(expected) >= 16 and not any(x in expected[:16] for x in (0xfc, 0xfd))
        return self.g.read(self.g.sym['gStringVar4'], 48).startswith(expected[:16])

    def stable(self, before):
        after = self.g.snapshot()
        assert after['map'] == before['map'] and after['xy'] == before['xy'], ('Unexpected movement/warp during service', before, after)
        return after

    def wait_text(self, label, before, frames=720):
        for _ in range(frames//24):
            self.stable(before)
            if self.text_matches(label):
                return
            self.g.step(0, 24)
        raise AssertionError(('Expected service text not reached', label, self.g.snapshot()))

    def wait_unlocked(self, before, max_a=8):
        for index in range(max_a+1):
            snap = self.stable(before)
            if self.g.field(snap) and not snap['script_locked']:
                return snap
            if index < max_a:
                self.g.tap('A', settle=60)
        raise AssertionError(('Service did not release controls', self.g.snapshot()))

    def passive_state(self):
        v = self.g.values
        p1, p2 = self.g.number('gSaveBlock1Ptr'), self.g.number('gSaveBlock2Ptr')
        assert 0x02000000 <= p1 < 0x02040000 and 0x02000000 <= p2 < 0x02040000
        result = {}
        for name, base, fields in (
            ('sb1', p1, ['money', 'bagPocket_Items', 'bagPocket_KeyItems', 'bagPocket_PokeBalls', 'bagPocket_TMHM', 'bagPocket_Berries', 'unused_348C']),
            ('sb2', p2, ['filler_DA0'])):
            for field in fields:
                key = ('SaveBlock1' if name == 'sb1' else 'SaveBlock2')+'.'+field
                result[key] = self.g.read(base+v['offset.'+key], v['size.'+key]).hex()
        count = self.g.number('gPlayerPartyCount', 1)
        assert 1 <= count <= 6
        result['party'] = self.g.read(self.g.sym['gPlayerParty'], count*v['sizes.Pokemon']).hex()
        return result

    def party_health(self):
        v, schema = self.g.values, self.g.schema
        count = self.g.number('gPlayerPartyCount', 1)
        raw = self.g.read(self.g.sym['gPlayerParty'], count*v['sizes.Pokemon'])
        result = []
        for i in range(count):
            mon = raw[i*v['sizes.Pokemon']:(i+1)*v['sizes.Pokemon']]
            def field(kind, name):
                at = v['offset.'+kind+'.'+name]
                return int.from_bytes(mon[at:at+v['size.'+kind+'.'+name]], 'little')
            pid, ot = field('BoxPokemon', 'personality'), field('BoxPokemon', 'otId')
            at = v['offset.BoxPokemon.secure']
            plain = b''.join((x^pid^ot).to_bytes(4, 'little') for x in struct.unpack('<12I', mon[at:at+48]))
            assert sum(struct.unpack('<24H', plain)) & 65535 == field('BoxPokemon', 'checksum')
            pos = schema['substruct_positions'][str(pid % 24)]
            growth, attacks = plain[pos[0]*12:(pos[0]+1)*12], plain[pos[1]*12:(pos[1]+1)*12]
            moves = struct.unpack_from('<4H', attacks, v['offset.PokemonSubstruct1.moves'])
            pp_at, ppup_at = v['offset.PokemonSubstruct1.pp'], v['offset.PokemonSubstruct0.ppBonuses']
            pp = list(attacks[pp_at:pp_at+4])
            max_pp = [schema['move_pp'][str(m)]*(5+((growth[ppup_at]>>(j*2))&3))//5 for j, m in enumerate(moves)]
            result.append({'hp': field('Pokemon', 'hp'), 'max_hp': field('Pokemon', 'maxHP'), 'status': field('Pokemon', 'status'), 'pp': pp, 'max_pp': max_pp})
        return result

    def open(self, case):
        assert self.tour.name() == case['map'], 'Caller must reach room by normal doors first'
        self.tour.walk(case['map'], tuple(case['stand']))
        before = self.g.snapshot()
        assert self.g.field(before) and not before['script_locked']
        # Facing a blocked counter/NPC does not move the player.
        self.g.step(DIR_KEYS[case['direction']], 1)
        self.g.step(0, 12)
        self.stable(before)
        self.g.picture(case['id']+'-approach')
        self.g.tap('A', settle=24)
        self.wait_text(case['entry_text'], before)
        if case.get('target_kind', 'npc') == 'npc':
            assert self.g.number('gSpecialVar_LastTalked', 2) == case['local_id'], 'Follower/other NPC intercepted interaction'
        assert self.g.snapshot()['script_locked'], 'Expected facility did not lock dialogue'
        self.g.step(0, 240)
        self.g.picture(case['id']+'-dialogue')
        return before

    def shop_cancel(self, case):
        before = self.open(case)
        protected = self.passive_state()
        target = self.g.sym['CB2_BuyMenu'] & ~1
        for _ in range(6):
            if self.g.snapshot()['callback2'] & ~1 == target:
                break
            self.g.tap('A', settle=120)
        else:
            raise AssertionError('Normal BUY menu was not reached')
        self.g.picture(case['id']+'-actual-buy-menu')
        for _ in range(12):
            snap = self.stable(before)
            if self.g.field(snap) and not snap['script_locked']:
                break
            self.g.tap('B', settle=60)
        else:
            raise AssertionError('Shop cancel did not release controls')
        assert self.passive_state() == protected, 'Shop cancellation changed money/bag/party'
        return self.record(case, 'ACTUAL_SHOP_BUY_MENU_AND_CANCEL_NO_PURCHASE', before)

    def heal(self, case, accept):
        before = self.open(case)
        protected, old_health = self.passive_state(), self.party_health()
        self.g.tap('A' if accept else 'B', settle=60)
        if case.get('result_text'):
            self.wait_text(case['result_text'], before, frames=1800)
            self.g.picture(case['id']+'-result')
        self.wait_unlocked(before)
        if not accept:
            assert self.passive_state() == protected, 'Healing NO changed money/bag/party'
            scope = 'ACTUAL_HEAL_DECLINE_UNCHANGED'
        else:
            health = self.party_health()
            assert all(x['hp'] == x['max_hp'] and x['status'] == 0 and x['pp'] == x['max_pp'] for x in health)
            depleted = any(x['hp'] < x['max_hp'] or x['status'] or x['pp'] != x['max_pp'] for x in old_health)
            scope = 'ACTUAL_HEAL_RESTORATION' if depleted else 'ACTUAL_HEAL_ACCEPT_DIALOGUE_ALREADY_FULL_EFFECT_NOT_DEMONSTRATED'
        return self.record(case, scope, before)

    def dialogue(self, case):
        before = self.open(case)
        self.wait_unlocked(before, max_a=12)
        return self.record(case, 'ACTUAL_NORMAL_NPC_DIALOGUE', before)

    def record(self, case, scope, before):
        self.g.picture(case['id']+'-released')
        row = {'case': case['id'], 'candidate_id': self.candidate_id, 'scope': scope, 'before': before, 'after': self.g.snapshot(), 'runtime_writes': 0, 'save_exports': 0}
        self.records.append(row)
        return row


def run_service_checks(guest, tour, cases_path):
    """Run six explicit checks via normal doors, separate from 17/32 tour scope.

    Caller must deepcopy the completed original tour result before this hook,
    because Tour.crossing appends to Tour.crossings. This function also returns
    a deep copy of only its own additional crossings. Pending PC/bed/mission
    cases are reported as static-only and are never silently executed.
    """
    document = json.loads(Path(cases_path).read_text(encoding='utf8'))
    cases = document['services']
    by_script = {}
    scripts = ('SpaceFacility_Shop', 'SpaceFacility_FoodShop',
               'SpaceFacility_DrinkShop', 'SpaceFacility_Cook', 'Space_Heal')
    for script in scripts:
        matches = [x for x in cases if x['script'] == script]
        assert len(matches) == 1, ('Expected exactly one explicit service case', script)
        by_script[script] = deepcopy(matches[0])
    expected_methods = {script: ('heal' if script == 'Space_Heal' else
                                'dialogue' if script == 'SpaceFacility_Cook' else 'shop_cancel')
                        for script in scripts}
    for script, case in by_script.items():
        assert case['runtime_method'] == expected_methods[script]
        assert case.get('target_kind', 'npc') == 'npc' and case['interaction'] == 'counter'
    checks = ServiceChecks(guest, tour, document['candidate_id'])
    required_texts = [x['entry_text'] for x in by_script.values()]
    heal = by_script['Space_Heal']
    required_texts.extend([heal['result_text_decline'], heal['result_text_accept']])
    assert all(label and label in guest.sym for label in required_texts), ('Missing fresh service text symbol', required_texts)
    origin = tour.name()
    initial = guest.snapshot()
    assert guest.field(initial) and not initial['script_locked']
    crossing_start = len(tour.crossings)
    map_ids = {row['definition']['id']: name for name, row in tour.maps.items()}

    def reach(destination):
        current = tour.name()
        assert destination in tour.maps
        q, previous = deque([current]), {current: None}
        while q and destination not in previous:
            name = q.popleft()
            for index, warp in enumerate(tour.maps[name]['definition']['warp_events']):
                target = map_ids.get(warp['dest_map'])
                if target is not None and target not in previous:
                    previous[target] = (name, index)
                    q.append(target)
        assert destination in previous, ('No ordinary-door graph route', current, destination)
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

    sequence = [('SpaceFacility_Shop', None), ('Space_Heal', False),
                ('Space_Heal', True), ('SpaceFacility_FoodShop', None),
                ('SpaceFacility_DrinkShop', None), ('SpaceFacility_Cook', None)]
    for script, accept in sequence:
        case = deepcopy(by_script[script])
        reach(case['map'])
        if case['runtime_method'] == 'shop_cancel':
            checks.shop_cancel(case)
        elif case['runtime_method'] == 'dialogue':
            checks.dialogue(case)
        elif case['runtime_method'] == 'heal':
            case['id'] += '-yes' if accept else '-no'
            case['result_text'] = case['result_text_accept'] if accept else case['result_text_decline']
            checks.heal(case, accept=accept)
        else:
            raise AssertionError('Unimplemented service method cannot run')
    reach(origin)
    final = guest.snapshot()
    assert guest.field(final) and not final['script_locked'] and tour.name() == origin
    assert len(checks.records) == 6
    return {'status': 'PASS_ACTUAL_EXPLICIT_SERVICE_DIALOGUES',
            'candidate_id': document['candidate_id'], 'before': initial, 'after': final,
            'checks': deepcopy(checks.records),
            'service_directional_crossings': deepcopy(tour.crossings[crossing_start:]),
            'static_only_cases': [x['id'] for x in cases if x['script'] not in scripts],
            'scope': 'Three BUY-menu/cancel checks, cook dialogue, medic NO and YES through normal keys and ordinary doors; no purchase, PC/bed/mission use or whole mission claimed',
            'heal_effect_note': 'Already-full party proves YES dialogue and full result only; restoration is claimed only if depletion was actually observed before YES',
            'runtime_memory_writes': 0, 'save_exports': 0}
