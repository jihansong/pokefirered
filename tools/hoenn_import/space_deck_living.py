"""Explicit source-pixel furniture plans for thirteen ship rooms.

This module has no filesystem or generator side effects. The integration owner
applies actor metadata, rebuilds hard footprints, then calls decorate. Every
piece has an explicit coordinate; nearest-position relocation is forbidden.
"""

ROOM_PLANS = {
    'CaptainsOffice': {
        'actors': {'SpaceFacility_OfficeCaptain': {
            'xy': [5, 5], 'facing': 'UP', 'talk_tile': [5, 6]}},
        'interactions': {},
    },
    'CrewQuarters': {
        'actors': {'SpaceFacility_CrewSleeper': {
            'xy': [8, 4], 'facing': 'LEFT', 'talk_tile': [8, 5]}},
        'interactions': {'SpaceFacility_Rest': {
            'target': [4, 4], 'stand': [4, 5]}},
    },
    'GuestRoom1': {
        'actors': {'SpaceFacility_Guest1': {
            'xy': [5, 6], 'facing': 'RIGHT', 'talk_tile': [5, 5]}},
        'interactions': {'SpaceFacility_Rest': {
            'target': [4, 3], 'stand': [4, 4]}},
    },
    'GuestRoom2': {
        'actors': {'SpaceFacility_Guest2': {
            'xy': [5, 6], 'facing': 'LEFT', 'talk_tile': [6, 6]}},
        'interactions': {'SpaceFacility_Rest': {
            'target': [4, 4], 'stand': [4, 5]}},
    },
    'GuestRoom3': {
        'actors': {'SpaceFacility_Guest3': {
            'xy': [7, 5], 'facing': 'UP', 'talk_tile': [7, 6]}},
        'interactions': {'SpaceFacility_Rest': {
            'target': [4, 7], 'stand': [4, 8]}},
    },
    # The duplicate pilot script is disambiguated by original position below.
    'Cockpit': {'actors': {}, 'interactions': {}},
    'Navigation': {
        'actors': {'SpaceFacility_NavigationOfficer': {
            'xy': [4, 6], 'facing': 'UP', 'talk_tile': [4, 7]}},
        'interactions': {'SpaceFacility_NavigationConsole': {
            'target': [12, 4], 'stand': [12, 5]}},
    },
    'CabinCorridor': {'actors': {}, 'interactions': {}},
    'CargoHold': {
        'actors': {'SpaceFacility_CargoResearcher': {
            'xy': [12, 5], 'facing': 'UP', 'talk_tile': [12, 6]}},
        'interactions': {'SpaceFacility_CargoClue': {
            'target': [6, 5], 'stand': [6, 6]}},
    },
    'Engineering': {
        'actors': {
            'Space_SystemsCheck': {
                'xy': [10, 7], 'facing': 'DOWN', 'talk_tile': [10, 8]},
            'Space_EngineeringCrew': {
                'xy': [5, 4], 'facing': 'LEFT', 'talk_tile': [5, 5]},
        },
        'interactions': {'Space_EngineeringConsole': {
            'target': [12, 4], 'stand': [12, 5]}},
    },
    'Observatory': {
        'actors': {
            'Space_ObservatoryCrew': {
                'xy': [14, 11], 'facing': 'LEFT', 'talk_tile': [14, 12]},
            'Space_JirachiEncounter': {
                'xy': [12, 6], 'facing': 'DOWN', 'talk_tile': [12, 7]},
        },
        'interactions': {'Space_RecordsConsole': {
            'target': [10, 8], 'stand': [10, 9]}},
    },
    'BattleDeck': {
        'actors': {
            'Space_BattleDeckOrbit': {
                'xy': [12, 7], 'facing': 'DOWN', 'talk_tile': [12, 8]},
            'SpaceFacility_ArenaSpectator': {
                'xy': [18, 8], 'facing': 'LEFT', 'talk_tile': [17, 8]},
        },
        'interactions': {},
    },
    'GameRoom': {
        'actors': {'SpaceFacility_GameAttendant': {
            'xy': [5, 4], 'facing': 'LEFT', 'talk_tile': [5, 5]}},
        'interactions': {'SpaceFacility_GameMachine': {
            'target': [10, 4], 'stand': [10, 5]}},
    },
}

ACTOR_INSTANCE_OVERRIDES = [
    {'role': 'Cockpit', 'script': 'SpaceFacility_CockpitPilot',
     'original_xy': [8, 5], 'xy': [8, 5],
     'facing': 'UP', 'talk_tile': [8, 6]},
    {'role': 'Cockpit', 'script': 'SpaceFacility_CockpitPilot',
     'original_xy': [12, 5], 'xy': [12, 5],
     'facing': 'UP', 'talk_tile': [12, 6]},
]

SEMANTIC_CONSTRAINTS = {
    'all': [
        'Map dimensions, map/layout IDs, warp positions and destinations stay fixed.',
        'All pieces are explicit complete donor units; relocation fallback is forbidden.',
        'Actors and talk stands stay open; interaction targets belong to blocked furniture.',
        'Actor sprites are not assumed to have seated animation merely because a stool exists.',
        'Root owns common doorway/deck glyphs and final hard/BFS/foreground checks.',
    ],
    'CaptainsOffice': ['Captain [5,5] works upward at book desk [4..6,3..4]; talk [5,6].',
                       'Compact hull [2,1]..[11,10], with west approach preserved.'],
    'CrewQuarters': ['Four intact beds flank a clear central spine x8..11.',
                     'Crew [8,4] faces desk left; rest target remains [4,4].'],
    'GuestRoom1': ['Compact six-column interior x3..8; resident faces desk to the right.',
                   'Bed/rest move together to [3,2]/[4,3]; chair touches desk edge.'],
    'GuestRoom2': ['Resident faces left into writing desk; sleeping and entry axes stay clear.'],
    'GuestRoom3': ['Bed moves as a full 3x2 unit to [3,6]; rest target moves with it to [4,7].'],
    'Cockpit': ['Both pilots keep their original positions and face their north consoles.',
                'Two complete window banks flank consoles; aft x8..12 remains a clear entry.'],
    'Navigation': ['Transit axis x9..11 is clear; officer and communications desk form west work bay.',
                   'Literal console [12,4] and approach [12,5] remain unchanged.',
                   'Full-width north workroom joins a three-column aft spine and west mess branch; no south plaza.'],
    'CabinCorridor': ['Door forecourts x4,9,14,19 remain unobstructed; seating only at ends.',
                      'Root must distinguish lobby return [4,1] from guest doors.'],
    'CargoHold': ['Central loading aisle x9..14 stays clear except story actor [12,5].',
                  'Clue [6,5] remains on an intact crate; researcher faces its work desk.'],
    'Engineering': ['Mission local1 [10,7], crew [5,4], literal setmetatile [12,4] remain fixed.',
                    'Crew faces adjacent west service panel; generators flank lower work bays.'],
    'Observatory': ['Jirachi local2 [12,6], crew [14,11], records [10,8] remain fixed.',
                   'Earth window uses the exact existing 8x4 donor unit and full lower frame.',
                   'Crew faces a left service console; records approach [10,9] stays open.'],
    'BattleDeck': ['Battle actor [12,7] remains on original full 8x6 platform.',
                   'Spectator [18,8] faces arena left; ringside route/talk [17,8] stays clear.'],
    'GameRoom': ['Attendant faces a desk edge; slot-machine target [10,4] remains fixed.',
                 'Five machines align at x6,8,10,12,14 with two-row customer aisle y5..6.',
                 'Compact machine hall joins a southeast entry alcove; native approach seats stay walkable.'],
}

BED = [[808, 809, 810], [816, 817, 818]]
BOOK_DESK = [[773, 774, 775], [781, 782, 783]]
WRITING_DESK = [[824, 825], [832, 833], [840, 841]]
CONSOLE = [[867, 868], [875, 876]]
PLANT = [[811], [819]]
SHELF = [[762], [770]]
GENERATOR = [[752, 753, 754], [760, 761, 762], [768, 769, 770]]
SERVICE_PANEL = [[751, 750], [759, 758]]
CARGO = [[736, 737, 738, 736, 737, 738],
         [747, 748, 749, 744, 745, 746],
         [755, 756, 757, 752, 753, 754],
         [743, 743, 743, 743, 743, 758]]


def _compact_hull(ctx, x0, y0, x1, y1):
    """Keep registered dimensions; reduce only usable interior envelope."""
    put = ctx['setcell']
    for y in range(ctx['h']):
        for x in range(ctx['w']):
            put(x, y, ('v3', 1004), True)
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            put(x, y, ctx['floor'], False)
    for x in range(x0, x1 + 1):
        put(x, y0, ('v3', 901 if x == x0 else 903 if x == x1 else 902))
        put(x, y1, ('v3', 906 if x == x0 else 908 if x == x1 else 907))
    for y in range(y0 + 1, y1):
        put(x0, y, ('v3', 904))
        put(x1, y, ('v3', 905))


def _add_hull(ctx, x0, y0, x1, y1):
    """Add one explicit hull rectangle; caller opens the union seams."""
    put = ctx['setcell']
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            put(x, y, ctx['floor'], False)
    for x in range(x0, x1 + 1):
        put(x, y0, ('v3', 901 if x == x0 else 903 if x == x1 else 902))
        put(x, y1, ('v3', 906 if x == x0 else 908 if x == x1 else 907))
    for y in range(y0 + 1, y1):
        put(x0, y, ('v3', 904))
        put(x1, y, ('v3', 905))


def decorate(role, ctx):
    """Draw only the requested room, returning False for other owners' roles."""
    if role not in ROOM_PLANS:
        return False
    place, put = ctx['place'], ctx['setcell']

    def piece(label, family, rows, x, y):
        # Always required: a collision signals an integration defect to fix.
        place(label, family, rows, x, y, required=True, collision=True)

    def native_seat(x, y, family='facility', metatile=865):
        # Like the original Game Corner approach, this remains walkable.
        put(x, y, (family, metatile), False)

    if role == 'CaptainsOffice':
        _compact_hull(ctx, 2, 1, 11, 10)
        piece('captain_work_book_desk', 'anne', BOOK_DESK, 4, 3)
        piece('captain_wall_map', 'anne', [[755, 756]], 7, 2)
        piece('captain_reference_shelf', 'anne', SHELF, 9, 2)
        piece('visitor_chair_north', 'anne', [[771]], 9, 6)
        piece('visitor_chair_south', 'anne', [[771]], 9, 7)
    elif role == 'CrewQuarters':
        for index, (x, y) in enumerate([(3, 3), (12, 3), (3, 10), (12, 10)]):
            piece('crew_bed_' + str(index + 1), 'anne', BED, x, y)
        piece('crew_writing_desk', 'anne', WRITING_DESK, 6, 2)
        piece('crew_desk_side_chair', 'anne', [[820]], 8, 3)
        piece('north_crew_locker', 'anne', SHELF, 16, 2)
        piece('south_crew_locker', 'anne', SHELF, 16, 10)
        for x in list(range(2, 7)) + list(range(12, 18)):
            if (x, 6) not in ctx['hard']:
                put(x, 6, ('v3', 901 if x in [2, 12] else 903 if x in [6, 17] else 902))
    elif role.startswith('GuestRoom'):
        _compact_hull(ctx, 2, 1, 9, 10)
        if role == 'GuestRoom1':
            piece('guest1_complete_bed', 'anne', BED, 3, 2)
            piece('guest1_writing_desk', 'anne', WRITING_DESK, 6, 5)
            piece('guest1_desk_side_chair', 'anne', [[820]], 8, 6)
            piece('guest1_plant', 'anne', PLANT, 8, 2)
        elif role == 'GuestRoom2':
            piece('guest2_complete_bed', 'anne', BED, 3, 3)
            piece('guest2_writing_desk', 'anne', WRITING_DESK, 3, 6)
            piece('guest2_desk_side_chair', 'anne', [[820]], 5, 7)
            piece('guest2_plant', 'anne', PLANT, 8, 2)
        else:
            piece('guest3_complete_bed', 'anne', BED, 3, 6)
            piece('guest3_writing_desk', 'anne', WRITING_DESK, 6, 2)
            piece('guest3_desk_side_chair', 'anne', [[820]], 8, 4)
            piece('guest3_plant', 'anne', PLANT, 8, 2)
    elif role == 'Cockpit':
        for x in [3, 13]:
            piece('complete_bridge_window_' + str(x), 'facility',
                  [[760] * 4, [768] * 4, [870] * 4], x, 1)
        for x in [7, 11]:
            piece('pilot_complete_console_' + str(x), 'facility', CONSOLE, x, 3)
        native_seat(8, 5)
        native_seat(12, 5)
    elif role == 'Navigation':
        _compact_hull(ctx, 1, 1, 18, 8)
        _add_hull(ctx, 8, 7, 12, 16)
        _add_hull(ctx, 1, 10, 10, 14)
        # Explicit rectangle-union seams: spine remains x9..11 throughout.
        for x in range(8, 13):
            put(x, 7, ctx['floor'], False)
        for y in range(8, 16):
            for x in range(9, 12):
                put(x, y, ctx['floor'], False)
        for y in range(11, 14):
            for x in range(8, 12):
                put(x, y, ctx['floor'], False)
        piece('communications_window', 'facility',
              [[760] * 4, [768] * 4, [870] * 4], 2, 1)
        piece('navigation_window', 'facility',
              [[760] * 3, [768] * 3, [870] * 3], 14, 1)
        piece('officer_communications_console', 'facility', CONSOLE, 3, 4)
        piece('fixed_navigation_console', 'facility', CONSOLE, 12, 3)
        piece('mess_branch_wall_navigation_display', 'facility', [[885, 886, 887]], 5, 10)
        piece('workbay_storage_partition', 'anne', SHELF, 8, 3)
        for x in [12, 13]:
            put(x, 7, ('v3', 907))
        native_seat(4, 6)
    elif role == 'CabinCorridor':
        for x in [6, 11, 16, 21]:
            piece('corridor_porthole_' + str(x), 'anne', [[826]], x, 1)
        for x in [2, 21]:
            piece('corridor_end_chair_' + str(x), 'anne', [[771]], x, 5)
    elif role == 'CargoHold':
        for index, (x, y) in enumerate([(3, 2), (15, 2), (3, 11), (15, 11)]):
            piece('cargo_complete_crate_group_' + str(index + 1), 'tidal', CARGO, x, y)
        piece('cargo_research_console', 'facility', CONSOLE, 11, 3)
    elif role == 'Engineering':
        piece('crew_adjacent_work_panel', 'power', SERVICE_PANEL, 3, 3)
        piece('fixed_story_systems_panel', 'power', SERVICE_PANEL, 12, 3)
        piece('port_generator', 'power', GENERATOR, 3, 9)
        piece('starboard_generator', 'power', GENERATOR, 14, 9)
    elif role == 'Observatory':
        piece('existing_complete_earth_viewport', 'v3',
              [[850 + y * 8 + x for x in range(8)] for y in range(4)], 6, 1)
        piece('complete_viewport_lower_frame', 'v3', [[906] + [907] * 8 + [908]], 5, 5)
        for x in range(5, 15):
            put(x, 0, ('v3', 901 if x == 5 else 903 if x == 14 else 902))
        for y in range(1, 5):
            put(5, y, ('v3', 904))
            put(14, y, ('v3', 905))
        piece('fixed_records_console', 'facility', CONSOLE, 9, 7)
        piece('observer_work_console', 'facility', CONSOLE, 12, 10)
        for x in [4, 5, 15, 16]:
            piece('visitor_observation_stool_' + str(x), 'facility', [[865]], x, 13)
        native_seat(14, 11)
    elif role == 'BattleDeck':
        arena = [[552 + y * 8 + x for x in range(8)] for y in range(5)]
        arena.append([541, 551, 551, 542, 541, 551, 551, 542])
        for y, row in enumerate(arena):
            for x, metatile in enumerate(row):
                put(8 + x, 5 + y, ('arena', metatile), False)
        ctx['pieces'].append({'label': 'complete_original_arena',
                              'source_profile': 'arena', 'metatile_rows': arena,
                              'xy': [8, 5], 'complete_shape': True, 'blocked': False})
        for x, y in [(6, 6), (6, 9), (18, 6), (18, 10)]:
            piece('ringside_stool_' + str(x) + '_' + str(y), 'facility', [[865]], x, y)
        native_seat(18, 8)
    elif role == 'GameRoom':
        _compact_hull(ctx, 1, 1, 18, 7)
        _add_hull(ctx, 12, 6, 18, 12)
        for x in range(12, 18):
            put(x, 6, ctx['floor'], False)
        for x in range(13, 18):
            put(x, 7, ctx['floor'], False)
        for x in [2, 3, 4, 5]:
            piece('attendant_wall_storage_' + str(x), 'anne', SHELF, x, 1)
        piece('attendant_work_desk', 'anne', BOOK_DESK, 2, 3)
        piece('attendant_side_chair', 'anne', [[820]], 5, 3)
        for x in [6, 8, 10, 12, 14]:
            piece('complete_front_slot_' + str(x), 'game',
                  [[645, 646], [653, 654], [710, 788]], x, 2)
            native_seat(x, 5, 'game', 683)
    return True
