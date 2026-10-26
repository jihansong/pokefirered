"""Explicit original-pixel service rooms; no nearest-free furniture placement.

Cabin keeps the private PC at (3, 4) and the flight arrival at (10, 12).
The current Cabin scripts were read: Captain/Pilot have no literal walks;
the LaunchPad captain boarding walk belongs to another map. No scripts,
door endpoints, map dimensions, save data, or shared tilesets are changed.

Native mixed-collision composites retain their employee floor holes. A
service is customer -> ONE MB_COUNTER tile -> employee, at elevation 3.
ROOM_PLANS talk_tile is the customer position, not the counter position.
Root must rebuild the contract hard/reachable sets from these plans; an
enclosed employee floor is not a customer BFS destination.
"""

ROOM_PLANS = {
    'Cabin': {
        'actors': {
            'Space_CabinCaptain': {'xy': [8, 4], 'facing': 'UP', 'talk_tile': [8, 5]},
            'Space_CabinPilot': {'xy': [13, 4], 'facing': 'UP', 'talk_tile': [13, 5]},
            'Space_FlightCheck': {'xy': [3, 8], 'facing': 'RIGHT', 'talk_tile': [4, 8]},
            'Space_Heal': {'xy': [9, 10], 'facing': 'DOWN', 'talk_tile': [9, 12]},
            'Space_CabinAttendant': {'xy': [15, 8], 'facing': 'LEFT', 'talk_tile': [14, 8]},
            'Space_CabinPassengerA': {'xy': [3, 12], 'facing': 'RIGHT', 'talk_tile': [4, 12]},
            'Space_CabinPassengerB': {'xy': [15, 12], 'facing': 'UP', 'talk_tile': [15, 11]},
            'SpaceFacility_Shop': {'xy': [5, 3], 'facing': 'RIGHT', 'talk_tile': [7, 3]},
        },
        'interactions': {'SpaceFacility_PC': {'target': [3, 4], 'stand': [3, 5]}},
    },
    'Lounge': {
        'actors': {
            'SpaceFacility_DrinkShop': {'xy': [9, 3], 'facing': 'DOWN', 'talk_tile': [9, 5]},
            'SpaceFacility_LoungeGuest': {'xy': [14, 9], 'facing': 'UP', 'talk_tile': [14, 8]},
        },
        'interactions': {},
    },
    'CrewMess': {
        'actors': {
            'SpaceFacility_Cook': {'xy': [6, 4], 'facing': 'DOWN', 'talk_tile': [6, 6]},
        },
        'interactions': {'SpaceFacility_Rest': {'target': [8, 10], 'stand': [8, 11]}},
    },
    'FoodCourt': {
        'actors': {
            'SpaceFacility_FoodShop': {'xy': [6, 4], 'facing': 'DOWN', 'talk_tile': [6, 6]},
            'SpaceFacility_FoodGuest': {'xy': [14, 8], 'facing': 'UP', 'talk_tile': [14, 7]},
        },
        'interactions': {},
    },
}

SERVICE_APPROACHES = {
    'Cabin': [
        {'script': 'SpaceFacility_Shop', 'local_id': 8, 'npc': [5, 3],
         'counter': [6, 3], 'stand': [7, 3], 'player_facing': 'LEFT',
         'source': ['mart', 677]},
        {'script': 'Space_Heal', 'local_id': 3, 'npc': [9, 10],
         'counter': [9, 11], 'stand': [9, 12], 'player_facing': 'UP',
         'source': ['pc', 664]},
    ],
    'Lounge': [
        {'script': 'SpaceFacility_DrinkShop', 'local_id': 1, 'npc': [9, 3],
         'counter': [9, 4], 'stand': [9, 5], 'player_facing': 'UP',
         'source': ['game', 701]},
    ],
    'CrewMess': [
        {'script': 'SpaceFacility_Cook', 'local_id': 1, 'npc': [6, 4],
         'counter': [6, 5], 'stand': [6, 6], 'player_facing': 'UP',
         'source': ['pc', 700]},
    ],
    'FoodCourt': [
        {'script': 'SpaceFacility_FoodShop', 'local_id': 1, 'npc': [6, 4],
         'counter': [6, 5], 'stand': [6, 6], 'player_facing': 'UP',
         'source': ['pc', 700]},
    ],
}

# Source regions were read from the actual original layout blocks, including
# collision bits. PC: cols4..10, rows0..4; Mart: cols1..3, rows1..6;
# GameCorner: cols1..9, rows2..3. No invented pixel or behavior is used.
_PC_ROWS = [
    [644, 644, 644, 646, 647, 644, 644],
    [681, 682, 683, 654, 655, 684, 685],
    [689, 690, 691, 656, 867, 692, 693],
    [697, 700, 700, 664, 700, 700, 701],
    [675, 695, 695, 695, 695, 695, 695],
]
_PC_BLOCKED = ['1111111', '1111111', '1110011', '1111111', '0000000']
_MART_ROWS = [
    [693, 654, 661], [694, 644, 669], [681, 682, 677],
    [689, 690, 685], [695, 700, 644], [705, 706, 651],
]
_MART_BLOCKED = ['111', '101', '001', '111', '000', '110']
_LOUNGE_ROWS = [
    [663, 708, 711, 692, 693, 694, 710, 788, 655],
    [667, 673, 674, 700, 701, 702, 672, 673, 675],
]
_LOUNGE_BLOCKED = ['100000001', '111111111']
_ROUND_TABLE = [[598, 599], [606, 607]]


def _get(ctx, name):
    return ctx[name] if isinstance(ctx, dict) else getattr(ctx, name)


def _counter_behavior(ctx, fam, metatile):
    profile = _get(ctx, 'P')[fam]
    bank = int(metatile >= profile['cut'])
    index = metatile - profile['cut'] if bank else metatile
    raw = profile['attr'][bank]
    value = int.from_bytes(raw[index * 4:index * 4 + 4], 'little')
    assert value & 0xff == 0x80, (fam, metatile, 'not native MB_COUNTER')


def _native(ctx, label, fam, rows, blocked_rows, x, y, source_region):
    """Copy one fixed native composite, retaining its open staff cells.

    place() receives only explicit required=True blocking runs. The native
    floor cells use setcell(), so a hard employee/talk tile stays open rather
    than causing the entire fixture to be displaced by the old fallback.
    """
    place, setcell = _get(ctx, 'place'), _get(ctx, 'setcell')
    occupied, hard = _get(ctx, 'occupied'), _get(ctx, 'hard')
    width, height = len(rows[0]), len(rows)
    assert len(blocked_rows) == height
    assert all(len(row) == width for row in rows)
    assert all(len(row) == width for row in blocked_rows)
    cells = {(x + dx, y + dy) for dy in range(height) for dx in range(width)}
    assert all(1 <= xx < _get(ctx, 'w') - 1 and
               1 <= yy < _get(ctx, 'h') - 1 for xx, yy in cells), (label, 'bounds')
    assert not cells & occupied, (label, 'overlapping earlier furniture')
    blocked = {(x + dx, y + dy) for dy, mask in enumerate(blocked_rows)
               for dx, bit in enumerate(mask) if bit == '1'}
    assert not blocked & hard, (label, 'blocking an actor, approach, or door')
    for dy, (row, mask) in enumerate(zip(rows, blocked_rows)):
        dx = 0
        while dx < width:
            if mask[dx] == '0':
                setcell(x + dx, y + dy, (fam, row[dx]), False)
                dx += 1
                continue
            end = dx + 1
            while end < width and mask[end] == '1':
                end += 1
            place(label + '_part_%d_%d' % (dy, dx), fam, [row[dx:end]],
                  x + dx, y + dy, required=True, collision=True)
            dx = end
    _get(ctx, 'pieces').append({
        'label': label, 'source_profile': fam, 'metatile_rows': rows,
        'xy': [x, y], 'complete_shape': True, 'blocked': 'native mixed collision',
        'collision_rows': blocked_rows, 'source_region': source_region,
        'relocation': False,
    })


def _table(ctx, label, x, y):
    """One complete SSTidal table and its paired side chairs, fixed together."""
    place = _get(ctx, 'place')
    place(label + '_table', 'tidal', _ROUND_TABLE, x, y, required=True)
    place(label + '_left_chair', 'tidal', [[608]], x - 1, y + 1, required=True)
    place(label + '_right_chair', 'tidal', [[609]], x + 2, y + 1, required=True)


def _food_counter(ctx, label, x, y, width):
    """Native one-tile-deep PC front counter, with both original end caps."""
    _get(ctx, 'place')(label, 'pc', [[697] + [700] * (width - 2) + [701]],
                       x, y, required=True)


def decorate(role, ctx):
    """Decorate an owned room and return True; other roles return False."""
    if role not in ROOM_PLANS:
        return False
    assert [_get(ctx, 'w'), _get(ctx, 'h')] == [20, 16], (role, 'unexpected size')
    place, setcell = _get(ctx, 'place'), _get(ctx, 'setcell')
    for service in SERVICE_APPROACHES[role]:
        _counter_behavior(ctx, *service['source'])

    if role == 'Cabin':
        _native(ctx, 'whole_native_Mart_clerk_booth', 'mart',
                _MART_ROWS, _MART_BLOCKED, 4, 1, 'Mart columns1..3 rows1..6')
        _native(ctx, 'whole_native_PokemonCenter_healing_counter', 'pc',
                _PC_ROWS, _PC_BLOCKED, 6, 8, 'PokemonCenter_1F columns4..10 rows0..4')
        place('boarding_information_display', 'facility', [[885, 886, 887]],
              7, 2, required=True)
        place('pilot_workstation', 'facility', [[867, 868], [875, 876]],
              12, 2, required=True)
        # Fixed scoped PC: 1005/1006 assignment remains the builder's job.
        setcell(3, 3, ('pc', 645), True)
        setcell(3, 4, ('pc', 98), True)
        setcell(3, 5, ('pc', 661), False)
        _get(ctx, 'occupied').update({(3, 3), (3, 4)})
        _get(ctx, 'pieces').append({
            'label': 'complete_fixed_PC_1005_1006', 'source_profile': 'pc',
            'metatile_rows': [[645], [98], [661]], 'xy': [3, 3],
            'complete_shape': True, 'blocked': 'cap/middle; front base open',
        })
        place('waiting_table', 'pc', [[668, 669], [676, 677]], 13, 10, required=True)
        place('waiting_pair_yellow', 'pc', [[757]], 13, 9, required=True)
        place('waiting_pair_blue', 'pc', [[765]], 14, 9, required=True)

    elif role == 'Lounge':
        # Actual native staff-floor/counter pair, rather than the old solid
        # two-row green strip. The source cashier machines are not copied.
        _native(ctx, 'whole_native_U_service_counter', 'game', _LOUNGE_ROWS,
                _LOUNGE_BLOCKED, 5, 3, 'GameCorner columns1..9 rows2..3')
        for x in [3, 15]:
            place('lounge_back_shelf_%d' % x, 'anne', [[762], [770]],
                  x, 2, required=True)
        for x in [8, 10, 12]:
            place('aligned_bar_stool_%d' % x, 'facility', [[865]],
                  x, 7, required=True)
        _table(ctx, 'lounge_left', 4, 10)
        _table(ctx, 'lounge_right', 13, 10)

    elif role == 'CrewMess':
        # A compact crew galley, one short serving face, and three shared
        # tables on a single row. Tables and chairs never move separately.
        place('crew_sink', 'anne', [[712, 713], [722, 723], [730, 731]],
              3, 2, required=True)
        place('crew_hot_worktop', 'anne', [[712, 713], [720, 721], [728, 729]],
              12, 2, required=True)
        _food_counter(ctx, 'complete_crew_serving_counter', 4, 5, 5)
        for x in [3, 8, 13]:
            _table(ctx, 'crew_shared_%d' % x, x, 9)

    elif role == 'FoodCourt':
        # Distinct passenger cafe: continuous serving frontage, broad public
        # queue apron at y6..8, and two dining groups with exact paired chairs.
        for y in range(2, 6):
            for x in range(2, _get(ctx, 'w') - 2):
                setcell(x, y, ('anne', 665), False)
        place('passenger_kitchen_sink', 'anne', [[712, 713], [722, 723], [730, 731]],
              3, 2, required=True)
        place('passenger_food_worktop', 'anne', [[712, 713], [720, 721], [728, 729]],
              13, 2, required=True)
        _food_counter(ctx, 'complete_passenger_serving_counter', 3, 5, 12)
        _table(ctx, 'cafe_left', 4, 10)
        _table(ctx, 'cafe_right', 12, 10)
    return True
