"""What the QA scripts know about the game, read from the source tree and the
built ROM rather than written down by hand.

- struct offsets: compiled from include/global.h with devkitARM's gcc and read
  back with nm (each offset becomes the size of a common symbol), cached in
  tools/qa/.cache/offsets.json and rebuilt when a header changes;
- constants (FLAG_*, VAR_*, MAP_*, LAYOUT_*, SPECIES_*, ITEM_*, ...): expanded
  with the host C preprocessor from include/constants;
- maps: data/maps/*/map.json;
- ROM tables (species base stats, experience tables): read from the .gba
  through the .sym file.
"""

import glob
import json
import os
import re
import struct
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
CACHE = os.path.join(HERE, '.cache')
DEFAULT_ROM = os.path.join(REPO, 'pokemonthyl.gba')

# name -> (struct, member) ; member None means sizeof(struct)
FIELDS = {
    'sb1.pos': ('SaveBlock1', 'pos'),
    'sb1.location': ('SaveBlock1', 'location'),
    'sb1.continueGameWarp': ('SaveBlock1', 'continueGameWarp'),
    'sb1.mapLayoutId': ('SaveBlock1', 'mapLayoutId'),
    'sb1.playerPartyCount': ('SaveBlock1', 'playerPartyCount'),
    'sb1.playerParty': ('SaveBlock1', 'playerParty'),
    'sb1.money': ('SaveBlock1', 'money'),
    'sb1.coins': ('SaveBlock1', 'coins'),
    'sb1.seen1': ('SaveBlock1', 'seen1'),
    'sb1.seen2': ('SaveBlock1', 'seen2'),
    'sb1.flags': ('SaveBlock1', 'flags'),
    'sb1.vars': ('SaveBlock1', 'vars'),
    'sb1.daycare': ('SaveBlock1', 'daycare'),
    'sb1.pcItems': ('SaveBlock1', 'pcItems'),
    'sb1.bagPocket_Items': ('SaveBlock1', 'bagPocket_Items'),
    'sb1.bagPocket_KeyItems': ('SaveBlock1', 'bagPocket_KeyItems'),
    'sb1.bagPocket_PokeBalls': ('SaveBlock1', 'bagPocket_PokeBalls'),
    'sb1.bagPocket_TMHM': ('SaveBlock1', 'bagPocket_TMHM'),
    'sb1.bagPocket_Berries': ('SaveBlock1', 'bagPocket_Berries'),
    'sb1': ('SaveBlock1', None),
    'sb2.playerName': ('SaveBlock2', 'playerName'),
    'sb2.specialSaveWarpFlags': ('SaveBlock2', 'specialSaveWarpFlags'),
    'sb2.optionsButtonMode': ('SaveBlock2', 'optionsButtonMode'),
    'sb2.playTimeHours': ('SaveBlock2', 'playTimeHours'),
    'sb2.playTimeVBlanks': ('SaveBlock2', 'playTimeVBlanks'),
    'sb2.playTimeMinutes': ('SaveBlock2', 'playTimeMinutes'),
    'sb2.playTimeSeconds': ('SaveBlock2', 'playTimeSeconds'),
    'sb2.lastBerryTreeUpdate': ('SaveBlock2', 'lastBerryTreeUpdate'),
    'sb2.pokedex': ('SaveBlock2', 'pokedex'),
    'sb2.localTimeOffset': ('SaveBlock2', 'localTimeOffset'),
    'sb2.hoennTrainerFlags': ('SaveBlock2', 'hoennTrainerFlags'),
    'sb2.hoennFlags': ('SaveBlock2', 'hoennFlags'),
    'sb2.hoennVars': ('SaveBlock2', 'hoennVars'),
    'sb2.encryptionKey': ('SaveBlock2', 'encryptionKey'),
    'sb2': ('SaveBlock2', None),
    'storage': ('PokemonStorage', None),
    'storage.boxes': ('PokemonStorage', 'boxes'),
    'boxmon': ('BoxPokemon', None),
    'time.hours': ('Time', 'hours'),
    'time.minutes': ('Time', 'minutes'),
    'dex.owned': ('Pokedex', 'owned'),
    'dex.seen': ('Pokedex', 'seen'),
    'warp.mapGroup': ('WarpData', 'mapGroup'),
    'warp.mapNum': ('WarpData', 'mapNum'),
    'warp.warpId': ('WarpData', 'warpId'),
    'warp.x': ('WarpData', 'x'),
    'warp.y': ('WarpData', 'y'),
    'time.days': ('Time', 'days'),
    'species.growthRate': ('SpeciesInfo', 'growthRate'),
    'species': ('SpeciesInfo', None),
    'pokemon': ('Pokemon', None),
}


def _headers_stamp():
    newest = 0
    for p in glob.glob(os.path.join(REPO, 'include', '**', '*.h'), recursive=True):
        newest = max(newest, os.path.getmtime(p))
    return newest


def _gcc():
    dka = os.environ.get('DEVKITARM', '/opt/devkitpro/devkitARM')
    return os.path.join(dka, 'bin', 'arm-none-eabi-gcc'), os.path.join(dka, 'bin', 'arm-none-eabi-nm')


_OFFSETS = None


def offsets():
    """Byte offsets/sizes named as in FIELDS, from the real headers."""
    global _OFFSETS
    if _OFFSETS is not None:
        return _OFFSETS
    path = os.path.join(CACHE, 'offsets.json')
    stamp = _headers_stamp()
    if os.path.exists(path):
        with open(path) as f:
            cached = json.load(f)
        if cached.get('_stamp') == stamp and set(FIELDS) <= set(cached):
            _OFFSETS = cached
            return cached
    gcc, nm = _gcc()
    src = ['#include "global.h"', '#include "pokemon_storage_system.h"']
    names = {}
    for i, (key, (st, member)) in enumerate(sorted(FIELDS.items())):
        sym = 'qa_%d' % i
        names[sym] = key
        expr = 'sizeof(struct %s)' % st if member is None else 'offsetof(struct %s, %s)' % (st, member)
        src.append('char %s[%s + 1];' % (sym, expr))
    with tempfile.TemporaryDirectory() as tmp:
        c = os.path.join(tmp, 'off.c')
        o = os.path.join(tmp, 'off.o')
        with open(c, 'w') as f:
            f.write('\n'.join(src) + '\n')
        subprocess.check_call([gcc, '-c', '-w', '-mthumb', '-mabi=apcs-gnu', '-march=armv4t', '-fcommon',
                               '-iquote', 'include', '-DLEAFGREEN', '-DREVISION=0', '-DENGLISH', '-DMODERN=1',
                               '-o', o, c], cwd=REPO)
        out = subprocess.check_output([nm, '-S', o], text=True)
    result = {'_stamp': stamp}
    for line in out.splitlines():
        p = line.split()
        if len(p) == 4 and p[3] in names:
            result[names[p[3]]] = int(p[1], 16) - 1
    os.makedirs(CACHE, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(result, f, indent=1, sort_keys=True)
    _OFFSETS = result
    return result


def off(name):
    return offsets()[name]


# ---------------------------------------------------------------- constants

CONST_HEADERS = ['constants/flags.h', 'constants/vars.h', 'constants/map_groups.h', 'constants/layouts.h',
                 'constants/species.h', 'constants/items.h', 'constants/moves.h', 'constants/opponents.h',
                 'pokemon_storage_system.h']
_CONST_CACHE = {}


def _c_eval(expr):
    expr = re.sub(r'\(\s*(u8|u16|u32|s8|s16|s32|int|unsigned)\s*\)', '', expr)
    expr = re.sub(r'\b(0x[0-9A-Fa-f]+|\d+)[uUlL]+\b', r'\1', expr)
    expr = expr.replace('&&', ' and ').replace('||', ' or ')
    return int(eval(expr, {'__builtins__': {}}, {}))


def consts(names):
    """Resolve C constant names to ints with the host preprocessor."""
    want = [n for n in names if n not in _CONST_CACHE]
    if want:
        src = ['#include "global.h"'] + ['#include "%s"' % h for h in CONST_HEADERS]
        src += ['QA_%s = %s' % (n, n) for n in want]
        out = subprocess.run(['cc', '-E', '-P', '-w', '-iquote', 'include', '-DLEAFGREEN', '-DREVISION=0',
                              '-DENGLISH', '-DMODERN=1', '-x', 'c', '-'], input='\n'.join(src) + '\n',
                             capture_output=True, text=True, cwd=REPO)
        got = {}
        for line in out.stdout.splitlines():
            m = re.match(r'QA_(\w+) = (.*)$', line)
            if m:
                got[m.group(1)] = m.group(2)
        for n in want:
            val = got.get(n)
            if val is None or val.strip() == n:
                raise KeyError('unknown constant %s' % n)
            _CONST_CACHE[n] = _c_eval(val)
    return {n: _CONST_CACHE[n] for n in names}


def const(name_or_number):
    if isinstance(name_or_number, int):
        return name_or_number
    s = str(name_or_number)
    if re.match(r'^(0x[0-9a-fA-F]+|\d+)$', s):
        return int(s, 0)
    return consts([s])[s]


# --------------------------------------------------------------------- maps

_MAPS = None


def maps():
    """MAP_* constant -> dict(dir, name, id, layout, group, num, warps, json)."""
    global _MAPS
    if _MAPS is None:
        found = {}
        for path in sorted(glob.glob(os.path.join(REPO, 'data', 'maps', '*', 'map.json'))):
            with open(path) as f:
                j = json.load(f)
            if 'id' not in j:
                continue
            found[j['id']] = {'dir': os.path.basename(os.path.dirname(path)), 'name': j.get('name'),
                              'id': j['id'], 'layout': j.get('layout'), 'json': j}
        vals = consts(list(found))
        lays = consts(sorted({m['layout'] for m in found.values() if m['layout']}))
        for k, m in found.items():
            v = vals[k]
            m['group'], m['num'] = v >> 8, v & 0xFF
            m['layout_id'] = lays.get(m['layout'])
        _MAPS = found
    return _MAPS


def map_info(name):
    """Accepts MAP_ROUTE110, ROUTE110 or the directory name Route110."""
    ms = maps()
    for key in (name, 'MAP_' + name):
        if key in ms:
            return ms[key]
    for m in ms.values():
        if m['dir'] == name or m['name'] == name:
            return m
    raise KeyError('unknown map %s' % name)


# -------------------------------------------------------------------- items

# bag pockets in SaveBlock1: POCKET_* -> (field, slot count constant)
POCKETS = {
    'POCKET_ITEMS': ('sb1.bagPocket_Items', 'BAG_ITEMS_COUNT'),
    'POCKET_KEY_ITEMS': ('sb1.bagPocket_KeyItems', 'BAG_KEYITEMS_COUNT'),
    'POCKET_POKE_BALLS': ('sb1.bagPocket_PokeBalls', 'BAG_POKEBALLS_COUNT'),
    'POCKET_TM_CASE': ('sb1.bagPocket_TMHM', 'BAG_TMHM_COUNT'),
    'POCKET_BERRY_POUCH': ('sb1.bagPocket_Berries', 'BAG_BERRIES_COUNT'),
}
_ITEMS = None


def items():
    """ITEM_* name -> its bag pocket (POCKET_*), from src/data/items.json."""
    global _ITEMS
    if _ITEMS is None:
        with open(os.path.join(REPO, 'src', 'data', 'items.json')) as f:
            _ITEMS = {i['itemId']: i['pocket'] for i in json.load(f)['items']}
    return _ITEMS


def item_name(name_or_number):
    """Accepts ITEM_RARE_CANDY, RARE_CANDY or a number; returns the ITEM_ name."""
    s = str(name_or_number)
    if s.isdigit():
        n = int(s)
        for k in items():
            if const(k) == n:
                return k
        raise KeyError('no item %d' % n)
    return s if s.startswith('ITEM_') else 'ITEM_' + s


# ---------------------------------------------------------------- ROM tables

class Rom:
    def __init__(self, path=DEFAULT_ROM):
        with open(path, 'rb') as f:
            self.data = f.read()
        from emu import fresh_syms, load_syms
        self.syms = load_syms(fresh_syms(path))

    def at(self, addr, n):
        o = addr - 0x08000000
        return self.data[o:o + n]

    def species_info(self, species):
        size = off('species')
        raw = self.at(self.syms['gSpeciesInfo'] + species * size, size)
        return {'base': list(raw[0:6]), 'growthRate': raw[off('species.growthRate')]}

    def exp_for_level(self, growth, level):
        # gExperienceTables[GROWTH_COUNT][MAX_LEVEL + 1] of u32
        row = 101 * 4
        return struct.unpack_from('<I', self.at(self.syms['gExperienceTables'] + growth * row + level * 4, 4))[0]
