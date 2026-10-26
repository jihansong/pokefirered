"""Galley rooms and source-furniture floor composites for the visual18 candidate.

No file I/O or placement search occurs on import. decorate_override constructs
complete S.S. Anne galley work islands on one metal floor. finish replaces only
edge-connected pixels matching each furniture donor's own floor; object and
shadow pixels outside that mask retain their original RGB555 values. These are
new floor composites/adapted layouts, not claims of unmodified native tiles.
The user's later revision also opens the red table apron between the metal
legs to the room floor; only the two documented red RGB555 values are removed.

The builder provides grid/blocked/getcell, place/setcell, floor/w/h/hard,
occupied/pieces/P, words/attribute/tile_raw. It owns the final walls/door pass.
"""
from collections import deque
import struct


DONOR_PROFILES = {}
FLOOR_OVERRIDES = {'CrewMess': ('facility', 752), 'FoodCourt': ('facility', 752)}

# The source map is SSAnne_Kitchen: three complete 2x6 prep islands at
# columns3..4,7..8,11..12 rows3..8. The candidate translates these by +1 X.
_ISLANDS = (
    ('left_sink_island', 4, [[712,713],[720,721],[724,721],[724,721],[722,723],[730,731]]),
    ('center_prep_island', 8, [[712,713],[724,721],[724,721],[720,721],[724,721],[728,729]]),
    ('right_sink_island', 12, [[712,713],[724,721],[724,721],[720,721],[722,723],[730,731]]),
)
_DONOR_FLOORS = {
    ('facility', 865): ('facility', 752),
    **{('tidal', n): ('tidal', 568) for n in (598,599,606,607,608,609)},
    **{('anne', n): ('anne', 665) for n in (712,713,720,721,722,723,724,728,729,730,731)},
    **{('anne', n): ('anne', 664) for n in (762,770)},
    **{('anne', n): ('anne', 664) for n in (771,773,774,775,781,782,783)},
}
_WALL_FLOOR_REFS = {('anne',667), ('anne',750), ('anne',751)}
_METAL_GALLEY_REFS = {('anne',n) for n in (712,713,720,721,722,723,724,728,729,730,731)}
_TABLE_OPEN_FRONTS = {('tidal',606), ('tidal',607)}
_RED_APRON_COLORS = {8567, 8663}  # Native RGB555 (23,11,8) and (23,14,8).


def _layers(ctx, ref):
    profile = ctx['P'][ref[0]]
    result = [[None]*256, [None]*256]
    for corner, word in enumerate(ctx['words'](ref)):
        raw = ctx['tile_raw'](profile, word)
        palette = profile['pal'][word >> 12]
        for y in range(8):
            for x in range(8):
                sx, sy = (7-x if word & 1024 else x), (7-y if word & 2048 else y)
                index = raw[sy*4+sx//2] >> (4*(sx & 1)) & 15
                at = ((corner % 4)//2*8+y)*16+(corner % 2*8+x)
                result[corner//4][at] = palette[index] if index else None
    return result


def _flat(layers):
    return [b if b is not None else a if a is not None else 0
            for a,b in zip(*layers)]


def _floor_mask(pixels, donor):
    eligible = {i for i,(a,b) in enumerate(zip(pixels, donor)) if a == b}
    queue = deque(i for i in eligible if i//16 in (0,15) or i % 16 in (0,15))
    mask = set(queue)
    while queue:
        i = queue.popleft(); x,y = i % 16, i//16
        for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            n = yy*16+xx
            if 0 <= xx < 16 and 0 <= yy < 16 and n in eligible and n not in mask:
                mask.add(n); queue.append(n)
    return mask


class _Profile:
    def __init__(self, ctx, role):
        self.alias = 'furniture18_'+role.lower()
        self.ctx = ctx
        assert self.alias not in ctx['P'], self.alias
        self.colors = []
        self.tiles = [bytes(32)]
        self.tile_ids = {}
        self.metatiles = []
        self.attributes = []
        self.publish()

    def publish(self):
        palettes = [[0]+group+[0]*(15-len(group)) for group in self.colors]
        palettes += [[0]*16 for _ in range(13-len(palettes))]
        self.ctx['P'][self.alias] = {
            'name': self.alias, 'cut': 512, 'tiles': [b'', b''.join(self.tiles)],
            'mt': [b'', b''.join(self.metatiles)],
            'attr': [b'', b''.join(struct.pack('<I', x) for x in self.attributes)],
            'pal': palettes,
        }

    def tile(self, values):
        colors = sorted({v for v in values if v is not None})
        assert len(colors) <= 15, ('Composite 8x8 tile exceeds native palette', self.alias, len(colors))
        bank = next((i for i,group in enumerate(self.colors) if len(set(group)|set(colors)) <= 15), None)
        if bank is None:
            bank = len(self.colors); assert bank < 13
            self.colors.append([])
        group = self.colors[bank]
        group.extend(c for c in colors if c not in group)
        indices = [0 if v is None else group.index(v)+1 for v in values]
        raw = bytes(indices[i] | indices[i+1] << 4 for i in range(0,64,2))
        key = bank,raw
        if key not in self.tile_ids:
            self.tile_ids[key] = 512+len(self.tiles)
            self.tiles.append(raw)
        assert self.tile_ids[key] < 1024
        return self.tile_ids[key] | bank << 12

    def add(self, layers, attribute):
        words = []
        for plane in layers:
            for cy,cx in ((0,0),(0,8),(8,0),(8,8)):
                words.append(self.tile([plane[(cy+y)*16+cx+x] for y in range(8) for x in range(8)]))
        index = 512+len(self.metatiles)
        self.metatiles.append(struct.pack('<8H', *words)); self.attributes.append(attribute)
        self.publish()
        return self.alias,index


def _profile(ctx, role):
    key = '_furniture18_profile'
    if key not in ctx:
        ctx[key] = _Profile(ctx, role)
    return ctx[key]


def _serving_bridge(ctx, role):
    """A complete narrow metal counter using the galley top and front lip.

    This is a declared new 32x16 composite. Ends connect to the full prep
    islands; the source center strips keep matching metal and wood shadows.
    """
    top = [_flat(_layers(ctx, ('anne', n))) for n in (712,713)]
    bottom = [_flat(_layers(ctx, ('anne', n))) for n in (730,731)]
    slab = _flat(_layers(ctx, ('anne', 721)))
    wood = set(_flat(_layers(ctx, ('anne',665))))
    floor = _flat(_layers(ctx, ctx['floor']))
    def sample(pair,x,y):
        return pair[x//16][y*16+x % 16]
    pixels = []
    for y in range(16):
        for x in range(32):
            if y < 3:
                color = sample(top, 8+x % 16, 13+y)
            elif y < 8:
                color = slab[(y-3)*16+4+x % 8]
            else:
                color = sample(bottom, 8+x % 16, y)
            if color in wood:
                color = floor[y*16+x % 16]
            pixels.append(color)
    refs = []
    for half in range(2):
        plane = [pixels[y*32+half*16+x] for y in range(16) for x in range(16)]
        refs.append(_profile(ctx, role).add([plane,[None]*256], 0x20000080))
    for x,ref in zip((6,7),refs):
        assert (x,5) not in ctx['hard'] and (x,5) not in ctx['occupied']
        ctx['setcell'](x,5,ref,True); ctx['occupied'].add((x,5))
    ctx['pieces'].append({'label':'complete_galley_serving_bridge','xy':[6,5],
                          'new_art':'native_metal_top_front_lip_composite','size':[2,1],
                          'source_profile':'anne','counter_behavior':128,
                          'npc':[6,4],'customer':[6,6],'floor':'whole-room facility752'})


def decorate_override(role, ctx):
    if role not in ('CrewMess','FoodCourt'):
        return False
    assert (ctx['w'],ctx['h']) == (20,16)
    assert tuple(ctx['floor'][:2]) == ('facility',752), 'Apply metal galley floor override after the base services floor'
    assert not ctx['occupied'], 'Galley replaces the previous mixed service decoration'
    for label,x,rows in _ISLANDS:
        ctx['place']('SSAnne_Kitchen_'+label, 'anne', rows, x, 3, required=True)
    _serving_bridge(ctx, role)
    # The complete galley north wall and its repeated original portholes.
    top = [646]+[652]*18+[647]
    middle = [654,742]+[642 if x in (2,6,12,16) else 660 for x in range(2,18)]+[743,655]
    lower = [654,750]+[667]*16+[751,655]
    for y,row in enumerate((top,middle,lower)):
        for x,n in enumerate(row):
            blocked = y < 2 or x in (0,1,18,19)
            assert not blocked or (x,y) not in ctx['hard']
            ctx['setcell'](x,y,('anne',n),blocked)
    ctx['pieces'].append({'label':'SSAnne_Kitchen_complete_north_window_wall',
                          'xy':[0,0],'size':[20,3],'source_profile':'anne',
                          'new_art':'native_window_wall_extended_to_room_width'})
    # Original complete dining units below the kitchen work islands. Their
    # curved corners/chair floors are composited by finish(), not left orange.
    for x in (3,12):
        ctx['place']('galley_dining_table_%d'%x,'tidal',[[598,599],[606,607]],x,11,required=True)
        for chair,tile in ((x-1,608),(x+2,609)):
            ctx['place']('galley_dining_chair_%d'%chair,'tidal',[[tile]],chair,12,required=True)
    if role == 'CrewMess':
        ctx['place']('crew_rest_seat_at_existing_interaction','tidal',[[608]],8,10,required=True)
    for x,y in ((6,4),(6,6)):
        assert not ctx['blocked'][y*ctx['w']+x]
    return True


def finish(role, ctx):
    floor = ctx['floor']; floor_pixels = _flat(_layers(ctx, floor))
    records = []; replacements = {}
    for ref in sorted(set(ctx['grid'])):
        original = ref[:2]
        donor = _DONOR_FLOORS.get(original)
        wall_floor = original in _WALL_FLOOR_REFS
        if donor is None and not wall_floor:
            continue
        source = _layers(ctx, ref); flat = _flat(source)
        if wall_floor or original in _METAL_GALLEY_REFS:
            # Metal galley equipment has no wooden foreground. These known
            # refs also contain phase-shifted wood floor under their feet.
            # Preserve metal/shadow and blue/white wall pixels; replace only
            # the three source wood FLOOR colors, independent of tile phase.
            donor = ('anne',665)
            colors = set(_flat(_layers(ctx, ('anne',664)))) | set(_flat(_layers(ctx, donor))) | set(_flat(_layers(ctx, ('anne',667))))
            mask = {i for i,v in enumerate(flat) if v in colors}
        else:
            mask = _floor_mask(flat, _flat(_layers(ctx, donor)))
        removed_panel = set()
        if original in _TABLE_OPEN_FRONTS:
            removed_panel = {i for i,color in enumerate(flat) if color in _RED_APRON_COLORS}
            assert len(removed_panel) == 46, ('Unexpected table apron source pixels', original)
            mask |= removed_panel
        changed = {i for i in mask if flat[i] != floor_pixels[i]}
        if not changed:
            continue
        out = [list(source[0]),list(source[1])]
        for i in mask:
            out[0][i] = floor_pixels[i]; out[1][i] = None
        composed = _flat(out)
        assert all(composed[i] == flat[i] for i in range(256) if i not in mask)
        replacement = _profile(ctx, role).add(out, ctx['attribute'](ref))
        replacements[ref] = replacement
        records.append({'source_profile':ref[0],'source_metatile':ref[1],
                        'donor_floor':list(donor),'room_floor':list(floor),
                        'floor_pixels_changed':len(changed),'foreground_shadow_pixels_preserved':256-len(mask),
                        'requested_red_panel_pixels_removed':len(removed_panel),
                        'classification':'new_floor_composite_and_requested_open_table_front' if removed_panel else
                                         'new_floor_composite_native_foreground_preserved'})
    for i,ref in enumerate(list(ctx['grid'])):
        if ref in replacements:
            x,y = i % ctx['w'], i//ctx['w']
            ctx['setcell'](x,y,replacements[ref],ctx['blocked'][i])
    return records
