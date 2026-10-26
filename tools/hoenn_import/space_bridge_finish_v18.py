"""GBA bridge and navigation room: purpose-built panels, windows and seats.

Pure generator module. Uses the existing steel floor and a deliberately bounded
15-colour bridge palette. No map metadata, actor, warp, script or save changes.
Reference images inform spatial relationships; no supplied stock image is copied.
"""
import struct

ROOM_PLANS = {}
DONOR_PROFILES = {}
FLOOR_OVERRIDES = {r: ('facility', 752) for r in ('Cockpit', 'Navigation')}


def _rgb(r, g, b):
    return r | g << 5 | b << 10


COLORS = [0] + [_rgb(*v) for v in (
    (12, 12, 15), (17, 18, 20), (21, 22, 23), (27, 27, 27),
    (3, 5, 9), (2, 7, 14), (3, 13, 21), (10, 24, 28),
    (22, 29, 30), (30, 31, 31), (31, 23, 7), (10, 25, 14),
    (28, 9, 8), (6, 11, 17), (9, 17, 24))]


def _rect(a, x0, y0, x1, y1, colour):
    for y in range(max(0, y0), min(len(a), y1 + 1)):
        for x in range(max(0, x0), min(len(a[0]), x1 + 1)):
            a[y][x] = colour


def _canvas(w, h, colour=3):
    return [[colour] * w for _ in range(h)]


def _source(ctx, ref):
    p = ctx['P'][ref[0]]
    n = ref[1]
    q = int(n >= p['cut'])
    i = n - p['cut'] if q else n
    result = [[None] * 16 for _ in range(16)]
    for k, word in enumerate(struct.unpack_from('<8H', p['mt'][q], i * 16)):
        tid = word & 1023
        tq = int(tid >= p['cut'])
        ti = tid - p['cut'] if tq else tid
        raw = p['tiles'][tq][ti * 32:(ti + 1) * 32]
        for y in range(8):
            for x in range(8):
                xx = 7 - x if word & 1024 else x
                yy = 7 - y if word & 2048 else y
                index = raw[yy * 4 + xx // 2] >> (4 * (xx % 2)) & 15
                if index:
                    result[(k % 4 // 2) * 8 + y][k % 2 * 8 + x] = p['pal'][word >> 12][index]
    return result


def _profile(ctx):
    if 'bridge18' in ctx['P']:
        return ctx['P']['bridge18']
    tiles, mts, attrs = bytearray(512 * 32), bytearray(512 * 16), bytearray(512 * 4)
    tile_ids, cell_ids = {}, {}
    p = dict(name='bridge18', cut=512, tiles=[bytes(512 * 32), tiles],
             mt=[bytes(512 * 16), mts], attr=[bytes(512 * 4), attrs],
             pal=[list(COLORS) for _ in range(13)])

    def add(pixels):
        key = tuple(tuple(row) for row in pixels)
        if key in cell_ids:
            return 'bridge18', cell_ids[key]
        mid = 512 + len(cell_ids)
        assert mid < 1000
        words = []
        for k in range(4):
            x0, y0 = k % 2 * 8, k // 2 * 8
            values = [pixels[y0 + y][x0 + x] for y in range(8) for x in range(8)]
            assert all(1 <= v <= 15 for v in values)
            raw = bytes(values[i] | values[i + 1] << 4 for i in range(0, 64, 2))
            if raw not in tile_ids:
                tid = 512 + len(tile_ids)
                assert tid < 1024
                tile_ids[raw] = tid
                tiles[(tid - 512) * 32:(tid - 511) * 32] = raw
            words.append(tile_ids[raw])
        struct.pack_into('<8H', mts, (mid - 512) * 16, *words, *([0] * 4))
        struct.pack_into('<I', attrs, (mid - 512) * 4, 0x20000000)
        cell_ids[key] = mid
        return 'bridge18', mid

    p['_add'] = add
    ctx['P']['bridge18'] = p
    return p


def _put_image(ctx, label, a, x0, y0, blocked=True):
    assert len(a) % 16 == 0 and len(a[0]) % 16 == 0
    cells = []
    for cy in range(len(a) // 16):
        for cx in range(len(a[0]) // 16):
            x, y = x0 + cx, y0 + cy
            assert 0 <= x < ctx['w'] and 0 <= y < ctx['h']
            assert not blocked or (x, y) not in ctx['hard'], (label, 'required floor', x, y)
            assert (x, y) not in ctx['occupied'], (label, 'overlap', x, y)
            pixels = [row[cx * 16:(cx + 1) * 16] for row in a[cy * 16:(cy + 1) * 16]]
            ctx['setcell'](x, y, _profile(ctx)['_add'](pixels), blocked)
            if blocked:
                ctx['occupied'].add((x, y))
            cells.append([x, y])
    ctx['pieces'].append(dict(label=label, xy=[x0, y0], complete_shape=True,
                             blocked=blocked, cells=cells,
                             provenance='Explicit GBA pixel composition; native steel floor retained'))


def _window(ctx, width):
    a = _canvas(width, 32, 1)
    _rect(a, 1, 1, width - 2, 30, 4)
    _rect(a, 3, 3, width - 4, 27, 5)
    # The existing ship Earth viewport is a source for a compact wide view.
    # Its deliberate palette/size adaptation is new bridge art, not an exact copy.
    earth = [[0] * 128 for _ in range(64)]
    for my in range(4):
        for mx in range(8):
            tile = _source(ctx, ('v3', 850 + my * 8 + mx))
            for y in range(16):
                for x in range(16):
                    earth[my * 16 + y][mx * 16 + x] = tile[y][x] or COLORS[5]
    shades = (5, 6, 7, 8, 9, 10)
    def nearest(c):
        return min(shades, key=lambda n: sum(((c >> s & 31) - (COLORS[n] >> s & 31)) ** 2
                                           for s in (0, 5, 10)))
    palette_cache = {c: nearest(c) for row in earth for c in row}
    for y in range(4, 27):
        for x in range(4, width - 4):
            sy = (y - 4) * 64 // 23
            sx = (x - 4) * 128 // (width - 8)
            a[y][x] = palette_cache[earth[sy][sx]]
    for x in (width // 3, width * 2 // 3):
        _rect(a, x, 3, x + 1, 27, 2)
        _rect(a, x + 2, 3, x + 2, 27, 4)
    _rect(a, 3, 28, width - 4, 29, 10)
    return a


def _console(width, height=32):
    a = _canvas(width, height, 1)
    _rect(a, 1, 1, width - 2, height - 4, 3)
    _rect(a, 1, 1, width - 2, 2, 10)
    _rect(a, 2, height - 4, width - 3, height - 3, 2)
    _rect(a, 2, height - 2, width - 3, height - 2, 5)
    for instrument, start in enumerate(range(4, width - 16, 32)):
        _rect(a, start, 4, start + 23, 17, 5)
        _rect(a, start + 1, 5, start + 22, 15, 6)
        _rect(a, start + 3, 7, start + 10, 8, 8)
        _rect(a, start + 3, 11, start + 7, 12, 9)
        _rect(a, start + 13, 7, start + 18, 12, 7)
        _rect(a, start + 15, 8, start + 16, 11, 8)
        if instrument % 3 == 1:
            _rect(a, start + 2, 6, start + 21, 14, 6)
            _rect(a, start + 5, 10, start + 18, 10, 8)
            _rect(a, start + 11, 7, start + 11, 13, 8)
            for dx, dy in ((8, 7), (14, 7), (8, 13), (14, 13)):
                a[dy][start + dx] = 9
        elif instrument % 3 == 2:
            for offset, height_bar in ((3, 4), (7, 7), (11, 5), (15, 8)):
                _rect(a, start + offset, 14 - height_bar, start + offset + 1, 14, 8)
        for dx, colour in ((1, 11), (5, 12), (9, 13)):
            _rect(a, start + dx, 21, start + dx + 1, 22, colour)
        _rect(a, start + 14, 20, start + 23, 23, 1)
        _rect(a, start + 15, 21, start + 22, 21, 4)
    return a


def _chair(ctx):
    floor = _source(ctx, ('facility', 752))
    a = [[COLORS.index(floor[y % 16][x]) for x in range(16)] for y in range(32)]
    # Facing north: the seat is toward the console and the visible backrest
    # occupies the southern/rear half, not the far/front edge of the chair.
    _rect(a, 3, 5, 12, 25, 5)
    _rect(a, 2, 8, 13, 24, 1)
    _rect(a, 4, 6, 11, 13, 14)
    _rect(a, 5, 7, 10, 11, 15)
    _rect(a, 4, 14, 11, 25, 14)
    _rect(a, 5, 15, 10, 23, 15)
    _rect(a, 5, 15, 10, 16, 8)
    _rect(a, 2, 9, 3, 19, 4)
    _rect(a, 12, 9, 13, 19, 4)
    _rect(a, 7, 26, 8, 28, 1)
    _rect(a, 4, 29, 11, 29, 1)
    return a


def _rectangular_hull(ctx, x0, y0, x1, y1):
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


def decorate_override(role, ctx):
    if role not in ('Cockpit', 'Navigation'):
        return False
    _profile(ctx)
    if role == 'Cockpit':
        _put_image(ctx, 'bridge_forward_space_window', _window(ctx, 224), 3, 1)
        _put_image(ctx, 'bridge_continuous_flight_console', _console(192), 4, 3)
        for x in (3, 16):
            wing = _console(32, 48)
            wing = [row[:16] for row in wing]
            if x == 16:
                wing = [row[::-1] for row in wing]
            _put_image(ctx, 'bridge_side_controls_' + str(x), wing, x, 3)
        # Pilots retain their standing sprites beside dedicated chairs; no fake
        # seated animation or desk foreground covers their head/body.
        for x in (6, 13):
            _put_image(ctx, 'bridge_forward_facing_seat_' + str(x), _chair(ctx), x, 5)
    else:
        # A legible operations room replaces the old zig-zag office envelope.
        # All five original exits and their standing tiles remain unchanged.
        _rectangular_hull(ctx, 1, 1, 18, 16)
        _put_image(ctx, 'nav_port_space_window', _window(ctx, 112), 2, 1)
        _put_image(ctx, 'nav_starboard_space_window', _window(ctx, 112), 11, 1)
        _put_image(ctx, 'nav_officer_continuous_console', _console(96), 2, 4)
        _put_image(ctx, 'nav_fixed_console_bank', _console(96), 11, 3)
        _put_image(ctx, 'nav_aft_status_panel', _console(80), 3, 10)
        _put_image(ctx, 'nav_aft_systems_panel', _console(80), 12, 10)
        for x in list(range(2, 8)) + list(range(12, 18)):
            ctx['setcell'](x, 8, ('v3', 901 if x in (2, 12) else 903 if x in (7, 17) else 902), True)
        _put_image(ctx, 'nav_aft_status_seat', _chair(ctx), 6, 12)
        _put_image(ctx, 'nav_starboard_seat', _chair(ctx), 14, 5)
    ctx['pieces'].append(dict(label='bridge18_design_contract',
        forward_view=True, continuous_controls=True, clear_central_aisle=True,
        actors_and_story_targets_unchanged=True, fixed_15_colour_profile=True))
    return True
