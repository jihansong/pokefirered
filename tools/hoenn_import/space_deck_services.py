"""Explicit original-pixel service rooms; no nearest-free furniture placement.

Cabin follows EverGrandeCity_PokemonLeague_1F's whole upper service frontage.
Its original PC moves to (6, 1), with its complete cap at (6, 0) and front
at (6, 2). Root must bind the scoped 1005/1006 animation to that target.
The flight arrival at (10, 12), return at (10, 14), and seven doors stay.
The current Cabin scripts were read: Captain/Pilot have no literal walks;
the LaunchPad captain boarding walk belongs to another map. No scripts,
door endpoints, map dimensions, save data, or shared tilesets are changed.

Native mixed-collision composites retain their employee floor holes. A
service is customer -> ONE MB_COUNTER tile -> employee, at elevation 3.
ROOM_PLANS talk_tile is the customer position, not the counter position.
Root must rebuild the contract hard/reachable sets from these plans; an
enclosed employee floor is not a customer BFS destination.
"""

DONOR_PROFILES = {'league': ('em_building', 'em_pokemon_center', True)}
FLOOR_OVERRIDES = {role: ('league', 576)
                   for role in ('Cabin', 'Lounge', 'CrewMess', 'FoodCourt')}
PC_STATES = {'off': ('league', 4), 'on': ('league', 5)}

ROOM_PLANS = {
    'Cabin': {
        'actors': {
            'Space_CabinCaptain': {'xy': [8, 2], 'facing': 'DOWN', 'talk_tile': [8, 3]},
            'Space_CabinPilot': {'xy': [11, 2], 'facing': 'DOWN', 'talk_tile': [11, 3]},
            'Space_FlightCheck': {'xy': [3, 8], 'facing': 'RIGHT', 'talk_tile': [4, 8]},
            'Space_Heal': {'xy': [3, 2], 'facing': 'DOWN', 'talk_tile': [3, 4]},
            'Space_CabinAttendant': {'xy': [12, 8], 'facing': 'LEFT', 'talk_tile': [11, 8], 'graphics_id': 'OBJ_EVENT_GFX_UNION_ROOM_RECEPTIONIST'},
            'Space_CabinPassengerA': {
                'xy': [7, 12], 'facing': 'LEFT', 'talk_tile': [7, 13],
                'movement_type': 'MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT',
                'movement_range_x': 1, 'movement_range_y': 1},
            'Space_CabinPassengerB': {
                'xy': [14, 12], 'facing': 'RIGHT', 'talk_tile': [14, 13],
                'movement_type': 'MOVEMENT_TYPE_WANDER_RIGHT_AND_LEFT',
                'movement_range_x': 1, 'movement_range_y': 1},
            'SpaceFacility_Shop': {'xy': [16, 2], 'facing': 'DOWN', 'talk_tile': [16, 4]},
        },
        'interactions': {'SpaceFacility_PC': {'target': [6, 1], 'stand': [6, 2]}},
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
        {'script': 'SpaceFacility_Shop', 'local_id': 8, 'npc': [16, 2],
         'counter': [16, 3], 'stand': [16, 4], 'player_facing': 'UP',
         'source': ['league', 517]},
        {'script': 'Space_Heal', 'local_id': 3, 'npc': [3, 2],
         'counter': [3, 3], 'stand': [3, 4], 'player_facing': 'UP',
         'source': ['league', 517]},
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

# Exact EverGrandeCity_PokemonLeague_1F rows0..4, including the common wall,
# both service fronts, employee floors, and the original PC's complete body.
_LEAGUE_TOP = [
 [520,523,523,586,587,523,524,523,691,692,692,693,525,526,523,523,523,523,527],
 [528,546,547,594,595,585,4,531,699,700,700,701,533,534,584,531,531,531,535],
 [627,554,555,519,603,593,548,541,707,708,708,709,542,542,592,637,553,628,629],
 [545,545,545,517,545,601,572,576,576,576,576,576,576,576,600,545,517,545,545],
 [544,518,518,518,518,518,549,576,576,560,563,576,576,576,615,518,518,518,580],
]
_LEAGUE_TOP_BLOCKED = [
 '1111111111111111111', '1111111110011111111',
 '0110110000000010000', '1111110000000011111', '0000000000000000000',
]
MOVEMENT_AREAS = {
 'Cabin': [
  {'script': 'Space_CabinPassengerA', 'axis': 'x', 'cells': [[x,12] for x in (6,7,8)],
   'engine': 'MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', 'range_x': 1, 'range_y': 1},
  {'script': 'Space_CabinPassengerB', 'axis': 'x', 'cells': [[x,12] for x in (13,14,15)],
   'engine': 'MOVEMENT_TYPE_WANDER_RIGHT_AND_LEFT', 'range_x': 1, 'range_y': 1},
 ]
}


def _league_surface(ctx, label, rows, masks, x, y, source_region):
    """Explicit source surface; zero-edge wall/cap cells need setcell, not place."""
    occupied, hard = _get(ctx, 'occupied'), _get(ctx, 'hard')
    cells = {(x+dx,y+dy) for dy,row in enumerate(rows) for dx in range(len(row))}
    assert all(0 <= xx < _get(ctx,'w') and 0 <= yy < _get(ctx,'h') for xx,yy in cells)
    assert not cells & occupied, (label, 'earlier furniture')
    blocked = {(x+dx,y+dy) for dy,mask in enumerate(masks)
               for dx,bit in enumerate(mask) if bit == '1'}
    assert not blocked & hard, (label, 'blocking required floor', sorted(blocked & hard))
    for dy,(row,mask) in enumerate(zip(rows,masks)):
        assert len(row) == len(mask)
        for dx,n in enumerate(row):
            _get(ctx,'setcell')(x+dx,y+dy,('league',n),mask[dx] == '1')
    occupied.update(blocked)
    _get(ctx,'pieces').append({'label': label, 'source_profile': 'league',
        'metatile_rows': rows, 'xy': [x,y], 'complete_shape': True,
        'blocked': 'original mixed collision', 'collision_rows': masks,
        'source_region': source_region, 'relocation': False})


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
        # One whole room finish, including the perimeter. No blue Mart patch,
        # gray facility desk, floating clinic back wall, or unrelated PC pod.
        assert not _get(ctx, 'occupied'), 'Cabin surfaces precede all furniture'
        assert not {(0,14),(18,14)} & _get(ctx, 'hard'), 'bottom corner on required floor'
        for y in range(5, 15):
            for x in range(19):
                setcell(x, y, ('league', 576), False)
            setcell(0, y, ('league', 544), False)
            setcell(18, y, ('league', 551), False)
        setcell(0, 14, ('league', 552), True)
        setcell(18, 14, ('league', 567), True)
        _league_surface(ctx, 'complete_EverGrande_parallel_service_frontage',
                        _LEAGUE_TOP, _LEAGUE_TOP_BLOCKED, 0, 0,
                        'EverGrandeCity_PokemonLeague_1F columns0..18 rows0..4')
        # The original continuous cream floor's central medallion, all
        # walkable. It belongs to this room family rather than a floor patch.
        _league_surface(ctx, 'EverGrande_shared_lobby_medallion', [
            [576,576,560,563,576,576], [576,630,635,635,631,576],
            [560,635,646,647,635,563], [568,636,654,655,636,571],
            [576,638,636,636,639,576],
        ], ['000000'] * 5, 7, 5,
            'EverGrandeCity_PokemonLeague_1F columns7..12 rows4..8')
        _league_surface(ctx, 'EverGrande_complete_left_waiting_group', [
            [576,576,550,576,576], [606,606,573,574,564],
            [614,614,581,582,550],
        ], ['00000','11110','11110'], 4, 9,
            'EverGrandeCity_PokemonLeague_1F columns1..5 rows9..11')
        _league_surface(ctx, 'EverGrande_complete_right_waiting_group', [
            [576,576,606], [576,550,614], [573,574,576],
            [581,582,564], [550,564,576],
        ], ['001','001','110','110','000'], 13, 7,
            'EverGrandeCity_PokemonLeague_1F columns15..17 rows6..10')
        # Reserve complete, dedicated walking lanes, not just spawn cells.
        reserved = {(6,2),(3,4),(16,4),(10,12),(10,14)}
        for movement in MOVEMENT_AREAS['Cabin']:
            lane = {tuple(xy) for xy in movement['cells']}
            assert not lane & (reserved | _get(ctx,'occupied'))
            spawn = tuple(ROOM_PLANS['Cabin']['actors'][movement['script']]['xy'])
            assert not lane & (_get(ctx,'hard') - {spawn}), (movement['script'], 'reserved walking lane')
            for x,y in lane:
                setcell(x,y,('league',576),False)

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
        place('passenger_kitchen_sink', 'anne', [[712, 713], [722, 723], [730, 731]],
              3, 2, required=True)
        place('passenger_food_worktop', 'anne', [[712, 713], [720, 721], [728, 729]],
              13, 2, required=True)
        _food_counter(ctx, 'complete_passenger_serving_counter', 3, 5, 12)
        _table(ctx, 'cafe_left', 4, 10)
        _table(ctx, 'cafe_right', 12, 10)
    return True
