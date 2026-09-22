#!/usr/bin/env python3
"""Re-wraps imported Hoenn text to fit FR/LG's message box.

Emerald's message box is wider than FR/LG's (the FR/LG box shows about 208 px of
text), so many Emerald lines were cut off at the right edge. This re-flows every
paragraph that has a line wider than the box: words are packed greedily, the
first line ends with \\n and later ones with \\l (scroll), and \\p paragraph breaks
and the final $ are kept. Paragraphs that already fit are left untouched.

Used by import_maps.py on every imported text; run it directly to re-wrap the
text.inc files of maps marked with a .hoenn file:
    python3 tools/hoenn_import/rewrap_text.py [--check]"""
import os, re, sys

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
MAX = 204
PLACEHOLDER = {'PLAYER': 42, 'RIVAL': 42, 'STR_VAR_1': 60, 'STR_VAR_2': 60, 'STR_VAR_3': 60}


def _load_widths():
    src = open(R + '/src/text.c').read()
    tbl = src[src.index('sFontNormalLatinGlyphWidths[] ='):]
    widths = [int(x) for x in re.findall(r'\d+', tbl[tbl.index('{'):tbl.index('}')])]
    cm = {}
    for l in open(R + '/charmap.txt', encoding='utf-8'):
        m = re.match(r"^'(.+)'\s*=\s*([0-9A-Fa-f]{2})\s*$", l.strip())
        if m:
            cm.setdefault(m.group(1).replace("\\'", "'"), int(m.group(2), 16))
    return widths, cm


WIDTHS, CHARMAP = _load_widths()


def width(s):
    w, i = 0, 0
    while i < len(s):
        if s[i] == '{':
            j = s.index('}', i)
            w += PLACEHOLDER.get(s[i + 1:j], 0)
            i = j + 1
            continue
        c = CHARMAP.get(s[i])
        w += WIDTHS[c] if c is not None and c < len(WIDTHS) else 6
        i += 1
    return w


def rewrap_body(body):
    """body: the concatenated contents of a label's .string lines"""
    end = '$' if body.endswith('$') else ''
    core = body[:-1] if end else body
    paras = core.split('\\p')
    out = []
    for p in paras:
        lines = re.split(r'\\[nl]', p)
        if all(width(l) <= MAX for l in lines):
            out.append(p)
            continue
        words = re.findall(r'(?:\{[^}]*\}|[^\s{])+', ' '.join(l.strip() for l in lines))
        new, cur = [], ''
        for w_ in words:
            cand = w_ if not cur else cur + ' ' + w_
            if cur and width(cand) > MAX:
                new.append(cur)
                cur = w_
            else:
                cur = cand
        new.append(cur)
        out.append(new[0] + ''.join(('\\n' if i == 1 else '\\l') + l for i, l in enumerate(new[1:], 1)))
    return '\\p'.join(out) + end


def to_string_lines(body, indent):
    parts = re.split(r'(?<=\\[npl])', body)
    return [f'{indent}.string "{p}"' for p in parts if p]


def rewrap_lines(lines):
    """lines: a label's .string source lines; returns re-wrapped lines (same if unchanged)"""
    indent = re.match(r'^(\s*)', lines[0]).group(1)
    body = ''.join(re.search(r'\.string "(.*)"', l).group(1) for l in lines)
    new = rewrap_body(body)
    return lines if new == body else to_string_lines(new, indent)


def rewrap_file(path):
    src = open(path, encoding='utf-8').read().split('\n')
    out, block, changed = [], [], 0
    def flush():
        nonlocal changed
        if block:
            nb = rewrap_lines(block)
            changed += nb != block
            out.extend(nb)
            block.clear()
    for l in src:
        if re.match(r'^\s*\.string "', l):
            block.append(l)
        else:
            flush()
            out.append(l)
    flush()
    return '\n'.join(out), changed


if __name__ == '__main__':
    check = '--check' in sys.argv
    total = 0
    for m in sorted(os.listdir(R + '/data/maps')):
        d = f'{R}/data/maps/{m}'
        if not os.path.exists(d + '/.hoenn') or not os.path.exists(d + '/text.inc'):
            continue
        new, n = rewrap_file(d + '/text.inc')
        total += n
        if n and not check:
            open(d + '/text.inc', 'w', encoding='utf-8').write(new)
    print(('would re-wrap' if check else 're-wrapped'), total, 'texts')
