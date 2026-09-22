"""Shared readers for the map analysis tools (hoenn_reachability.py,
check_map_integrity.py). Read-only: nothing here writes to the repo.

- load_maps(): every map.json listed in data/maps/map_groups.json
- ScriptIndex: labels of every event script file, with the warps, specials
  and label references each label makes (used to follow scripted warps)
- special_destinations(): maps a C special jumps to (airplane, Seagallop)
- ConstEval: evaluates #define values from include/constants/*.h
"""
import json
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Script macros that move the player to another map (asm/macros/event.inc).
# "set*" ones only prepare a destination that a later warp tile / special uses.
IMMEDIATE_WARPS = ('warp', 'warpsilent', 'warpdoor', 'warphole', 'warpteleport', 'warpspinenter')
DEFERRED_WARPS = ('setwarp', 'setdynamicwarp', 'setdivewarp', 'setholewarp')
# setescapewarp only records where an ESCAPE ROPE returns to (a place already
# visited), so it never opens a new map.
WARP_MACROS = IMMEDIATE_WARPS + DEFERRED_WARPS

# C specials that warp the player on their own. Their destinations are the
# MAP(MAP_X) entries of the table in the given source file.
SPECIAL_WARP_TABLES = {
    'DoAirplaneFlightScene': ('src/airplane_flight.c', 'sDestinations'),
    'DoSeagallopFerryScene': ('src/seagallop.c', 'sSeagallopSpawnTable'),
}

CONNECTION_OPPOSITE = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left', 'dive': 'emerge', 'emerge': 'dive'}


def rel(path):
    return os.path.join(ROOT, path)


def load_groups():
    return json.load(open(rel('data/maps/map_groups.json')))


def load_maps():
    """Returns (maps, order): maps[name] = map.json dict + '_group', '_hoenn'."""
    groups = load_groups()
    maps, order = {}, []
    for g in groups['group_order']:
        for m in groups[g]:
            d = json.load(open(rel(f'data/maps/{m}/map.json')))
            d['_group'] = g
            d['_hoenn'] = os.path.exists(rel(f'data/maps/{m}/.hoenn')) or 'Hoenn' in g
            maps[m] = d
            order.append(m)
    return maps, order


def map_ids(maps):
    """MAP_X constant -> map folder name"""
    return {d['id']: n for n, d in maps.items()}


LABEL_RE = re.compile(r'^([A-Za-z_]\w*)::?')
IDENT_RE = re.compile(r'\b[A-Za-z_]\w*\b')
ENDING_CMDS = ('end', 'return', 'goto', 'releaseend', 'step_end', 'warp', 'warpsilent', 'warpdoor',
               'warphole', 'warpteleport', 'warpspinenter')


class ScriptIndex:
    """Every label in the event script files, and what each one does."""

    def __init__(self, maps):
        self.labels = {}      # label -> dict(file, map, warps, specials, refs, next)
        self.map_labels = {}  # map name -> [labels defined in its scripts.inc]
        files = []
        for m in maps:
            p = f'data/maps/{m}/scripts.inc'
            if os.path.exists(rel(p)):
                files.append((p, m))
        for f in sorted(os.listdir(rel('data/scripts'))):
            if f.endswith('.inc'):
                files.append((f'data/scripts/{f}', None))
        if os.path.exists(rel('data/event_scripts.s')):
            files.append(('data/event_scripts.s', None))
        for path, owner in files:
            self._parse(path, owner)
        known = set(self.labels)
        for info in self.labels.values():
            info['refs'] = {r for r in info['refs'] if r in known}

    def _parse(self, path, owner):
        cur, prev = None, None
        for lineno, raw in enumerate(open(rel(path), encoding='utf-8', errors='replace'), 1):
            line = raw.split('@')[0].rstrip()
            mm = LABEL_RE.match(line)
            if mm:
                name = mm.group(1)
                if prev is not None and cur is not None and not cur['closed']:
                    cur['next'] = name
                cur = {'file': path, 'line': lineno, 'map': owner, 'warps': [], 'specials': set(),
                       'refs': set(), 'next': None, 'closed': False}
                self.labels[name] = cur
                if owner:
                    self.map_labels.setdefault(owner, []).append(name)
                prev = name
                rest = line[mm.end():].strip()
                if not rest:
                    continue
                line = rest
            if cur is None:
                continue
            s = line.strip()
            if not s:
                continue
            parts = s.split(None, 1)
            cmd = parts[0]
            args = parts[1] if len(parts) > 1 else ''
            if cmd in WARP_MACROS:
                target = args.split(',')[0].strip()
                cur['warps'].append((cmd, target, lineno))
            elif cmd == 'special':
                cur['specials'].add(args.strip())
            elif cmd == 'specialvar':
                cur['specials'].add(args.split(',')[-1].strip())
            for ident in IDENT_RE.findall(args):
                cur['refs'].add(ident)
            # data (.string, .2byte, .byte ...) never falls through into code
            cur['closed'] = cmd in ENDING_CMDS or cmd.startswith('.')

    def closure(self, roots):
        """All labels reachable from roots by goto/call/fall-through."""
        seen, stack = set(), [r for r in roots if r in self.labels]
        while stack:
            lab = stack.pop()
            if lab in seen:
                continue
            seen.add(lab)
            info = self.labels[lab]
            stack.extend(info['refs'] - seen)
            if info['next'] and not info['closed']:
                stack.append(info['next'])
        return seen

    def map_roots(self, name, mapdata):
        roots = set(self.map_labels.get(name, []))
        for key in ('object_events', 'bg_events', 'coord_events'):
            for ev in mapdata.get(key) or []:
                s = ev.get('script')
                if s and s not in ('0x0', '0', 'NULL'):
                    roots.add(s)
        return roots


def special_destinations():
    """special name -> [MAP_X...] read from the C tables in SPECIAL_WARP_TABLES"""
    out = {}
    for special, (path, table) in SPECIAL_WARP_TABLES.items():
        if not os.path.exists(rel(path)):
            continue
        src = open(rel(path)).read()
        m = re.search(re.escape(table) + r'[^=]*=\s*\{(.*?)\n\};', src, re.S)
        body = m.group(1) if m else src
        out[special] = re.findall(r'MAP\((MAP_\w+)\)', body)
    return out


# ---------------------------------------------------------------- metatiles

# Behaviors on which a warp event fires (src/field_control_avatar.c:
# IsWarpMetatileBehavior, IsArrowWarpMetatileBehavior, the directional stairs
# and TryDoorWarp). A warp event on any other tile does nothing until a script
# swaps the metatile (Emerald does this for TERRA/MARINE CAVE, for example).
WARP_BEHAVIOR_NAMES = ('MB_CAVE_DOOR', 'MB_LADDER', 'MB_EAST_ARROW_WARP', 'MB_WEST_ARROW_WARP', 'MB_NORTH_ARROW_WARP',
                       'MB_SOUTH_ARROW_WARP', 'MB_FALL_WARP', 'MB_REGULAR_WARP', 'MB_LAVARIDGE_1F_WARP', 'MB_WARP_DOOR',
                       'MB_UP_ESCALATOR', 'MB_DOWN_ESCALATOR', 'MB_UP_RIGHT_STAIR_WARP', 'MB_UP_LEFT_STAIR_WARP',
                       'MB_DOWN_RIGHT_STAIR_WARP', 'MB_DOWN_LEFT_STAIR_WARP', 'MB_UNION_ROOM_WARP')


class Metatiles:
    """Metatile behavior at a map position (layout block data + tileset attributes)."""

    def __init__(self):
        attr_path, self.tilesets = {}, {}
        for f in os.listdir(rel('src/data/tilesets')):
            text = open(rel('src/data/tilesets/' + f)).read()
            for m in re.finditer(r'(gMetatileAttributes_\w+)\[\]\s*=\s*INCBIN_U32\("([^"]+)"\)', text):
                attr_path[m.group(1)] = m.group(2)
            for m in re.finditer(r'const struct Tileset (gTileset_\w+)\s*=\s*\{(.*?)\};', text, re.S):
                body = m.group(2)
                a = re.search(r'\.metatileAttributes\s*=\s*(\w+)', body)
                self.tilesets[m.group(1)] = {'attrs': a.group(1) if a else None,
                                             'emerald': bool(re.search(r'\.isEmerald\s*=\s*TRUE', body))}
        self.attr_path = attr_path
        self.cache = {}
        self.layouts = {l['id']: l for l in json.load(open(rel('data/layouts/layouts.json')))['layouts'] if l}
        text = open(rel('include/constants/metatile_behaviors.h')).read()
        self.mb = {m.group(1): int(m.group(2), 0) for m in re.finditer(r'#define (MB_\w+)\s+(0x[0-9A-Fa-f]+|\d+)', text)}
        self.mb_name = {v: k for k, v in self.mb.items()}
        self.warp_behaviors = {self.mb[n] for n in WARP_BEHAVIOR_NAMES if n in self.mb}

    def _attrs(self, tileset):
        if tileset not in self.cache:
            p = self.attr_path.get((self.tilesets.get(tileset) or {}).get('attrs'))
            data = open(rel(p), 'rb').read() if p and os.path.exists(rel(p)) else b''
            self.cache[tileset] = [int.from_bytes(data[i:i + 4], 'little') for i in range(0, len(data) - 3, 4)]
        return self.cache[tileset]

    def behavior(self, layout_id, x, y):
        lay = self.layouts.get(layout_id)
        if not lay or not (0 <= x < lay['width'] and 0 <= y < lay['height']):
            return None
        key = ('blocks', layout_id)
        if key not in self.cache:
            self.cache[key] = open(rel(lay['blockdata_filepath']), 'rb').read()
        b = self.cache[key]
        i = (y * lay['width'] + x) * 2
        if i + 2 > len(b):
            return None
        metatile = int.from_bytes(b[i:i + 2], 'little') & 0x3FF
        prim = lay['primary_tileset']
        nprim = 512 if (self.tilesets.get(prim) or {}).get('emerald') else 640
        if metatile < nprim:
            attrs = self._attrs(prim)
        else:
            attrs, metatile = self._attrs(lay['secondary_tileset']), metatile - nprim
        if metatile >= len(attrs):
            return None
        return attrs[metatile] & 0x1FF

    def warp_is_live(self, mapdata, warp):
        """True/False, or None when the tile cannot be read"""
        v = self.behavior(mapdata['layout'], warp['x'], warp['y'])
        return None if v is None else v in self.warp_behaviors


# ---------------------------------------------------------------- constants

DEFINE_RE = re.compile(r'^\s*#define\s+([A-Za-z_]\w*)\s+(.*?)\s*$')


def strip_comment(s):
    s = re.sub(r'/\*.*?\*/', '', s)
    return s.split('//')[0].strip()


class ConstEval:
    """Numeric #define values from a set of headers (later files win)."""

    def __init__(self, paths, text_override=None):
        self.raw = {}       # name -> expression text
        self.comment = {}   # name -> trailing comment
        self.origin = {}    # name -> (file, line)
        self.order = []
        for p in paths:
            text = text_override.get(p) if text_override and p in text_override else None
            if text is None:
                if not os.path.exists(rel(p)):
                    continue
                text = open(rel(p), encoding='utf-8', errors='replace').read()
            for i, line in enumerate(text.splitlines(), 1):
                m = DEFINE_RE.match(line)
                if not m or '(' in m.group(1):
                    continue
                name, expr = m.group(1), m.group(2)
                if name.startswith('GUARD_'):
                    continue
                self.raw[name] = strip_comment(expr)
                c = expr.split('//', 1)
                self.comment[name] = c[1].strip() if len(c) > 1 else ''
                self.origin[name] = (p, i)
                self.order.append(name)
        self.cache = {}

    def value(self, name, depth=0):
        if name in self.cache:
            return self.cache[name]
        if name not in self.raw or depth > 50:
            return None
        expr = self.raw[name]
        if not expr:
            return None

        def sub(m):
            tok = m.group(0)
            if re.fullmatch(r'0[xX][0-9a-fA-F]+|\d+', tok):
                return str(int(tok, 0))
            v = self.value(tok, depth + 1)
            if v is None:
                raise ValueError(tok)
            return str(v)
        try:
            py = re.sub(r'0[xX][0-9a-fA-F]+|\b[A-Za-z_]\w*\b|\b\d+\b', sub, expr)
            if not re.fullmatch(r'[\d\s+\-*/()<>|&~%]+', py):
                return None
            v = int(eval(py.replace('/', '//')))  # only digits and operators remain
        except (ValueError, SyntaxError, ZeroDivisionError, TypeError):
            v = None
        self.cache[name] = v
        return v


def git_show(ref, path):
    """File text at a git ref, or None (used for the upstream baseline)."""
    try:
        return subprocess.run(['git', '-C', ROOT, 'show', f'{ref}:{path}'], capture_output=True,
                              text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
