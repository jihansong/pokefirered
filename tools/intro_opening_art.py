"""Shared drawing helpers for the new opening's pixel art (tools/make_intro_opening_*.py).

The FR/LG way of drawing, done by rule so every frame is drawn the same way:

- a figure is a stack of parts (ellipses and polygons) on a small canvas;
- every part gets an outline on its own rim: dark brown around yellow, black around
  black, dark red around red (FR/LG "coloured outlines", not pure black);
- where a part lies over another part (an arm over the body) its rim gets a line too,
  unless the pair is listed as merged (head and body are one mass);
- yellow is lit from the upper left: one pixel of light yellow along the upper-left
  rim, a two pixel band of the middle yellow along the lower-right rim;
- faces, eyes and cheeks are small hand-placed pixel stamps.
"""
import math
from PIL import Image


def inside(x, y, poly):
    n, c = len(poly), False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


class Figure:
    """Parts on a w x h canvas. Later parts cover earlier ones."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.parts = []          # (name, set of (x, y), kind)
        self.merge = set()

    def _add(self, name, pts, kind):
        self.parts.append((name, pts, kind))
        return pts

    def ellipse(self, name, cx, cy, rx, ry, kind='Y', rot=0.0):
        c, s = math.cos(rot), math.sin(rot)
        pts = set()
        for y in range(self.h):
            for x in range(self.w):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                u, v = dx * c + dy * s, -dx * s + dy * c
                if (u / rx) ** 2 + (v / ry) ** 2 <= 1.0:
                    pts.add((x, y))
        return self._add(name, pts, kind)

    def poly(self, name, poly, kind='Y'):
        pts = {(x, y) for y in range(self.h) for x in range(self.w) if inside(x + 0.5, y + 0.5, poly)}
        return self._add(name, pts, kind)

    def pixels(self, name, pts, kind='Y'):
        return self._add(name, set(pts), kind)

    def clip(self, name, keep):
        """Keep only the pixels of part `name` for which keep(x, y) is true."""
        for i, (n, pts, k) in enumerate(self.parts):
            if n == name:
                self.parts[i] = (n, {p for p in pts if keep(*p)}, k)

    def merged(self, *names):
        for a in names:
            for b in names:
                if a != b:
                    self.merge.add(frozenset((a, b)))

    def render(self, colors):
        """colors: kind -> dict(base=, rim=, line=, light=, mid=) palette indices
        (light/mid only for shaded kinds). Returns rows of indices (0 = clear)."""
        w, h = self.w, self.h
        owner = [[None] * w for _ in range(h)]
        kind, order = {}, {}
        for i, (name, pts, k) in enumerate(self.parts):
            kind[name], order[name] = k, i
            for x, y in pts:
                if 0 <= x < w and 0 <= y < h:
                    owner[y][x] = name
        at = lambda x, y: owner[y][x] if 0 <= x < w and 0 <= y < h else None
        same = lambda a, b: a is not None and (a == b or frozenset((a, b)) in self.merge)
        img = [[0] * w for _ in range(h)]
        edge = [[False] * w for _ in range(h)]
        for y in range(h):
            for x in range(w):
                o = owner[y][x]
                if o is None:
                    continue
                col = colors[kind[o]]
                c = col['base']
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = at(x + dx, y + dy)
                    if n is None:
                        c, edge[y][x] = col['rim'], True
                        break
                    if not same(n, o) and order[o] > order[n] and kind[n] not in col.get('no_line_over', ()):
                        c, edge[y][x] = col.get('line', col['rim']), True
                        break
                img[y][x] = c
        for y in range(h):
            for x in range(w):
                o = owner[y][x]
                if o is None or edge[y][x] or 'mid' not in colors[kind[o]]:
                    continue
                col = colors[kind[o]]
                def ok(dx, dy):
                    # still inside this mass: its own pixels, or a part lying over it
                    if not (0 <= x + dx < w and 0 <= y + dy < h):
                        return False
                    n = at(x + dx, y + dy)
                    if n is None:
                        return False
                    if same(n, o):
                        return not edge[y + dy][x + dx]
                    return order[n] > order[o]
                near = ((1, 0), (0, 1), (1, 1)) if col.get('band', 2) == 1 else \
                    ((1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (2, 1), (1, 2))
                if not all(ok(dx, dy) for dx, dy in near):
                    img[y][x] = col['mid']
                elif not all(ok(dx, dy) for dx, dy in ((-1, 0), (0, -1))):
                    img[y][x] = col['light']
        return img


def stamp(img, x0, y0, rows, key, clip=True):
    """Hand-placed pixels: rows of characters, key maps a character to an index.
    With clip, only pixels already inside the figure (not clear, not its rim) change."""
    rims = stamp.rims
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch in key:
                y, x = y0 + dy, x0 + dx
                if 0 <= y < len(img) and 0 <= x < len(img[0]):
                    if clip and (img[y][x] == 0 or img[y][x] in rims):
                        continue
                    img[y][x] = key[ch]


stamp.rims = ()


def flat_palette(pal):
    out = []
    for c in pal:
        out += list(c)
    return out


def to_image(rows, pal):
    h, w = len(rows), len(rows[0])
    im = Image.new('P', (w, h), 0)
    im.putpalette(flat_palette(pal))
    im.putdata([v for r in rows for v in r])
    return im


def mirror(rows):
    return [list(reversed(r)) for r in rows]


def paste(dst, src, x0, y0, transparent=0):
    for y, r in enumerate(src):
        for x, v in enumerate(r):
            if v != transparent and 0 <= y0 + y < len(dst) and 0 <= x0 + x < len(dst[0]):
                dst[y0 + y][x0 + x] = v


def enlarge(im, scale):
    return im.convert('RGB').resize((im.size[0] * scale, im.size[1] * scale), Image.NEAREST)


def gba_color(c):
    """Round an RGB colour to what the GBA shows (5 bits a channel)."""
    return tuple((v >> 3) * 255 // 31 for v in c)
