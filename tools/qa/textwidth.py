#!/usr/bin/env python3
"""textwidth.py [--max 208] [--no-fail] [-v] [--strvar-chars 10] [path ...]

Measures every line of every .string in the map scripts/texts against the
field message box, which is 26 tiles = 208 px wide (sStandardTextBox_WindowTemplates
in src/new_menu_helpers.c). Read-only.

  paths      files or directories to scan; default data/maps (every
             scripts.inc/text.inc under it). data/text/*.inc can be added by
             hand, but several of those files print into other windows (fame
             checker, help system, berry tags), where 208 px means nothing.
  widths     the latin glyph width tables of src/text.c. Field messages print
             with FONT_NORMAL, or FONT_MALE/FONT_FEMALE for NPCs with a text
             colour (AddTextPrinterDiffStyle); the three tables
             are read and the widest glyph of the three is used. Latin glyphs
             advance by their width only (letterSpacing is applied to Japanese
             glyphs alone, see RenderText), so a line is the plain sum.
  bytes      charmap.txt maps each character or {NAME} to its bytes.
  lines      \\n, \\l and \\p start a new line; $ ends the string. A line is
             reported at the source line where it starts.

Placeholders are measured at their worst case:
  {PLAYER}, {RIVAL}   PLAYER_NAME_LENGTH (7) x the widest glyph on the naming
                      screen keyboard (sKeyboardChars in src/naming_screen.c)
  {STR_VAR_n}, {DYNAMIC n}
                      contents depend on the script (a species, an item, a
                      number), so they cannot be measured here. A line counts
                      as over only if it is too wide with them left empty; one
                      that fits empty but not with --strvar-chars (default
                      POKEMON_NAME_LENGTH, 10) x the widest keyboard glyph is
                      listed as "check" with the room it leaves, and does not
                      fail
  {VERSION}, {EVIL_TEAM}, ...
                      the wider of the two words in src/strings.c
  {A_BUTTON}, ...     the keypad icon width in src/text.c (sKeypadIcons)
  control codes       0 px ({COLOR}, {PAUSE}, {FONT_*}, sound...), except
                      {CLEAR_TO n}/{SHIFT_RIGHT n}, which move the pen to n

Exit status 1 if any line is wider than --max, unless --no-fail.
"""
import argparse
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

TABLES = ('sFontNormalLatinGlyphWidths', 'sFontMaleLatinGlyphWidths', 'sFontFemaleLatinGlyphWidths')
PLAYER_NAME_LENGTH = 7
POKEMON_NAME_LENGTH = 10
# placeholder -> the gExpandedPlaceholder_* words it can print (FireRed / LeafGreen)
VAR = ('STR_VAR_1', 'STR_VAR_2', 'STR_VAR_3', 'UNKNOWN_STR')
FIXED = {'KUN': ('Kun', 'Chan'), 'VERSION': ('Ruby', 'Sapphire'), 'EVIL_TEAM': ('Magma', 'Aqua'),
         'GOOD_TEAM': ('Aqua', 'Magma'), 'EVIL_LEADER': ('Maxie', 'Archie'), 'GOOD_LEADER': ('Archie', 'Maxie'),
         'EVIL_LEGENDARY': ('Groudon', 'Kyogre'), 'GOOD_LEGENDARY': ('Kyogre', 'Groudon')}


def read(path):
    return open(os.path.join(REPO, path), encoding='utf-8').read()


def c_array(src, name):
    i = src.index(name + '[]')
    j = src.index('{', i)
    return [int(x, 0) for x in re.findall(r'0x[0-9A-Fa-f]+|\d+', src[j:src.index('}', j)])]


def load_charmap():
    chars, names = {}, {}
    for line in read('charmap.txt').split('\n'):
        line = line.split('@')[0].strip()
        m = re.match(r"^'(.+)'\s*=\s*((?:[0-9A-Fa-f]{2}\s*)+)$", line)
        if m:
            c = m.group(1)
            if c.startswith('\\') and len(c) == 2 and c[1] not in 'nlp':
                c = c[1]
            chars.setdefault(c, [int(b, 16) for b in m.group(2).split()])
            continue
        m = re.match(r'^(\w+)\s*=\s*((?:[0-9A-Fa-f]{2}\s*)+)$', line)
        if m:
            names.setdefault(m.group(1), [int(b, 16) for b in m.group(2).split()])
    return chars, names


class Font:
    def __init__(self, strvar_chars):
        text_c = read('src/text.c')
        tables = [c_array(text_c, t) for t in TABLES]
        self.widths = [max(col) for col in zip(*tables)]
        self.keypad = [int(w) for w in re.findall(r'\{\s*0x[0-9A-Fa-f]+,\s*(\d+),\s*\d+\s*\}',
                                                   text_c[text_c.index('sKeypadIcons[]'):])[:13]]
        self.chars, self.names = load_charmap()
        # widest glyph the player can type into a name
        ns = read('src/naming_screen.c')
        kb = ns[ns.index('sKeyboardChars['):]
        kb = kb[:kb.index('};')]
        typed = {c for s in re.findall(r'__\("(.*?)"\)', kb) for c in s} - {' '}
        self.name_glyph = max(self.glyph(self.chars[c][0]) for c in typed if c in self.chars)
        name = PLAYER_NAME_LENGTH * self.name_glyph
        var = strvar_chars * self.name_glyph
        self.placeholder = {'PLAYER': name, 'RIVAL': name, 'STR_VAR_1': var, 'STR_VAR_2': var,
                            'STR_VAR_3': var, 'UNKNOWN_STR': var}
        for k, words in FIXED.items():
            self.placeholder[k] = max(self.text_width(w) for w in words)
        self.dynamic = var
        self.unknown = set()

    def glyph(self, b):
        return self.widths[b] if b < len(self.widths) else 6

    def text_width(self, s):
        return sum(self.glyph(self.chars[c][0]) if c in self.chars else 6 for c in s)

    def token(self, body):
        """width of one {...} -> (width, absolute, variable); absolute: the pen moves to width"""
        parts = body.replace(',', ' ').split()
        name, args = parts[0], parts[1:]
        if name in self.placeholder:
            return self.placeholder[name], False, name in VAR
        bs = self.names.get(name)
        if bs is None:
            if re.match(r'^(0x[0-9A-Fa-f]+|\d+)$', name):
                return self.glyph(int(name, 0)), False, False
            self.unknown.add(name)
            return 0, False, False
        b0 = bs[0]
        if b0 == 0xFD:                                   # placeholder not listed above
            return self.dynamic, False, True
        if b0 == 0xF7:                                   # {DYNAMIC n}
            return self.dynamic, False, True
        if b0 == 0xF8:                                   # keypad icon
            k = bs[1] if len(bs) > 1 else (int(args[0], 0) if args else 0)
            return (self.keypad[k] if k < len(self.keypad) else 16), False, False
        if b0 == 0xF9:                                   # extra symbol, glyph 0x100 | n
            k = bs[1] if len(bs) > 1 else (int(args[0], 0) if args else 0)
            return self.glyph(0x100 | k), False, False
        if b0 == 0xFC:
            if len(bs) > 1 and bs[1] in (0x0D, 0x13) and args:   # SHIFT_RIGHT / CLEAR_TO
                return int(args[0], 0), True, False
            return 0, False, False
        return sum(self.glyph(b) for b in bs), False, False


def split_lines(pieces, font):
    """pieces: [(source line no, string contents)] of one label.
    Yields (source line, text, width, variable part) for every printed line:
    width counts {STR_VAR_n} as empty, the variable part is their worst case."""
    start, text, w, var = None, '', 0, 0
    for lineno, s in pieces:
        i = 0
        while i < len(s):
            if start is None:
                start = lineno
            c = s[i]
            if c == '\\' and i + 1 < len(s):
                e = s[i + 1]
                i += 2
                if e in 'nlp':
                    yield start, text, w, var
                    start, text, w, var = None, '', 0, 0
                    continue
                c = e
                text += '\\' + e
                w += font.glyph(font.chars[c][0]) if c in font.chars else 6
                continue
            if c == '{':
                j = s.index('}', i)
                tw, absolute, isvar = font.token(s[i + 1:j])
                if absolute:
                    w, var = tw, 0
                elif isvar:
                    var += tw
                else:
                    w += tw
                text += s[i:j + 1]
                i = j + 1
                continue
            if c == '$':
                yield start, text, w, var
                return
            if c in font.chars:
                w += font.glyph(font.chars[c][0])
            else:
                font.unknown.add(c)
                w += 6
            text += c
            i += 1
    if start is not None:
        yield start, text, w, var


def labels(path):
    """label -> [(line no, .string contents)] for every text label in a file"""
    out, cur = {}, None
    for n, line in enumerate(open(path, encoding='utf-8'), 1):
        m = re.match(r'^(\w+)::?', line)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r'^\s*\.string\s+"(.*)"\s*(@.*)?$', line)
        if m and cur:
            out.setdefault(cur, []).append((n, m.group(1)))
    return out


def files(paths):
    for p in paths:
        p = os.path.join(REPO, p)
        if os.path.isdir(p):
            for root, _, fs in sorted(os.walk(p)):
                for f in sorted(fs):
                    if f in ('scripts.inc', 'text.inc') or (f.endswith('.inc') and root == p):
                        yield os.path.join(root, f)
        else:
            yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*', default=['data/maps'])
    ap.add_argument('--max', type=int, default=208, help='message box width in px (default 208)')
    ap.add_argument('--strvar-chars', type=int, default=POKEMON_NAME_LENGTH,
                    help='characters assumed for {STR_VAR_n} and other variable placeholders')
    ap.add_argument('--no-fail', action='store_true')
    ap.add_argument('-v', '--verbose', action='store_true', help='also list lines within 8 px of the limit')
    a = ap.parse_args()

    font = Font(a.strvar_chars)
    over, check, near, nlines, nlabels, nfiles = [], [], [], 0, 0, 0
    for path in files(a.paths):
        nfiles += 1
        rel = os.path.relpath(path, REPO)
        for label, pieces in labels(path).items():
            nlabels += 1
            for lineno, text, w, var in split_lines(pieces, font):
                nlines += 1
                if w > a.max:
                    over.append((rel, lineno, label, w, var, text))
                elif w + var > a.max:
                    check.append((rel, lineno, label, w, var, text))
                elif w + var > a.max - 8:
                    near.append((rel, lineno, label, w, var, text))

    print(f'{nfiles} files, {nlabels} labels, {nlines} lines; limit {a.max} px '
          f'({{PLAYER}}/{{RIVAL}} = {font.placeholder["PLAYER"]} px, {{STR_VAR_n}} = {font.dynamic} px)')
    for title, rows in (('over', over),
                        ('check: fits only if {STR_VAR_n} is short (px = fixed text, room = what is left for it)', check),
                        ('near (within 8 px)', near if a.verbose else [])):
        if not rows:
            continue
        print(f'\n{title}:')
        for rel, lineno, label, w, var, text in rows:
            room = f', room {a.max - w} px' if var else ''
            print(f'  {rel}:{lineno}: {w} px{room} [{label}] {text}')
    if font.unknown:
        print('\nnot in charmap.txt (counted as 6 px): ' + ' '.join(sorted(font.unknown)))
    print(f'\n{len(over)} line(s) over {a.max} px, {len(check)} to check by hand ({{STR_VAR_n}})')
    sys.exit(1 if over and not a.no_fail else 0)


if __name__ == '__main__':
    main()
