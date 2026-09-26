"""Shared drawing rules for the new opening's pixel art (tools/make_intro_opening_*.py).

The FR/LG way of drawing POKeMON and people, done by rule so that every frame of
every scene comes out the same way (art direction review of scene 2 draft A,
docs/team/art/v0.11.0-opening-scene2-A*.md):

- A figure is a stack of parts (ellipses, lens shapes, polygons, thick strokes) on a
  small canvas. Later parts cover earlier ones.
- Selective outline: the rim of a part is BLACK where the figure ends below or to the
  right of it (the side away from the light) and the part's own dark colour where it
  ends above or to the left (the lit side). FR/LG's PIKACHU front sprite, the partner,
  the title PIKACHU and OAK all work like this.
- Where a part lies over another part (an arm over the body) its rim gets a line in
  the part's dark colour, unless the pair is merged (head, cheeks and body are one mass).
- Shading is by mass, not by edge: the light comes from the upper left, so the
  lower-right crescent of each mass is the shade colour. A pixel is in shade when the
  same pixel moved (kx, ky) further down and right would fall outside the mass.
  There is no light rim along the edges; highlights are small hand-placed blobs.
- Faces, highlights and cheeks are hand-placed pixel stamps.
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
        self.owner = None

    def _add(self, name, pts, kind):
        pts = {(x, y) for x, y in pts if 0 <= x < self.w and 0 <= y < self.h}
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

    def lens(self, name, x0, y0, x1, y1, width, kind='Y'):
        """A pointed leaf from (x0, y0) (widest near there) to the tip (x1, y1)."""
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        nx, ny = -uy, ux
        pts = []
        steps = 12
        for side in (1, -1):
            rng = range(steps + 1) if side == 1 else range(steps, -1, -1)
            for i in rng:
                t = i / steps
                half = width / 2 * min(1.0, (1 - t) * 1.7) * (0.75 + 0.25 * min(1.0, t * 4))
                pts.append((x0 + dx * t + nx * half * side, y0 + dy * t + ny * half * side))
        return self.poly(name, pts, kind)

    def stroke(self, name, points, widths, kind='Y'):
        """A thick polyline: each segment a quad whose width goes from widths[i] to
        widths[i+1]; the union of all segments."""
        pts = set()
        for i in range(len(points) - 1):
            (x0, y0), (x1, y1) = points[i], points[i + 1]
            w0, w1 = widths[i] / 2, widths[i + 1] / 2
            dx, dy = x1 - x0, y1 - y0
            length = math.hypot(dx, dy) or 1
            nx, ny = -dy / length, dx / length
            quad = [(x0 + nx * w0, y0 + ny * w0), (x1 + nx * w1, y1 + ny * w1),
                    (x1 - nx * w1, y1 - ny * w1), (x0 - nx * w0, y0 - ny * w0)]
            pts |= {(x, y) for y in range(self.h) for x in range(self.w) if inside(x + 0.5, y + 0.5, quad)}
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
        """colors: kind -> dict(
             base=  body colour,
             rim=   outline on the lit (upper-left) side,
             rim_dark= outline on the shaded (lower-right) side (default rim),
             line=  line where this part lies over another part (default rim),
             mid=   shade colour for the lower-right crescent (optional),
             shade= (kx, ky) depth of the crescent in pixels (default (3, 3)),
             no_line_over= kinds this part draws no line over)
        Returns rows of palette indices (0 = clear). Keeps self.owner / self.edge."""
        w, h = self.w, self.h
        owner = [[None] * w for _ in range(h)]
        kind, order = {}, {}
        for i, (name, pts, k) in enumerate(self.parts):
            kind[name], order[name] = k, i
            for x, y in pts:
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
                # the figure ends here: dark side first (below, right), then the lit side
                if at(x, y + 1) is None or at(x + 1, y) is None:
                    c, edge[y][x] = col.get('rim_dark', col['rim']), True
                elif at(x, y - 1) is None or at(x - 1, y) is None:
                    c, edge[y][x] = col['rim'], True
                else:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        n = at(x + dx, y + dy)
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
                kx, ky = col.get('shade', (3, 3))

                def inside_mass(px, py):
                    n = at(px, py)
                    if n is None:
                        return False
                    if same(n, o):
                        return True
                    return order[n] > order[o]      # a part lying over this one
                steps = max(kx, ky)
                lit = all(inside_mass(round(x + kx * i / steps), round(y + ky * i / steps))
                          for i in range(1, steps + 1))
                if not lit:
                    img[y][x] = col['mid']
        self.owner, self.edge = owner, edge
        return img


def stamp(img, x0, y0, rows, key, clip=True):
    """Hand-placed pixels: rows of characters, key maps a character to an index.
    With clip, pixels outside the figure (clear) are not drawn."""
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch in key:
                y, x = y0 + dy, x0 + dx
                if 0 <= y < len(img) and 0 <= x < len(img[0]):
                    if clip and img[y][x] == 0:
                        continue
                    img[y][x] = key[ch]


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


def shift(rows, dx, dy):
    """The picture moved by (dx, dy) on the same canvas."""
    h, w = len(rows), len(rows[0])
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if 0 <= y - dy < h and 0 <= x - dx < w:
                out[y][x] = rows[y - dy][x - dx]
    return out


def enlarge(im, scale):
    return im.convert('RGB').resize((im.size[0] * scale, im.size[1] * scale), Image.NEAREST)
