#!/usr/bin/env python3
"""Recolor the starter PIKACHU's emotion portraits (graphics/pikachu_emotions/portraits.png)
in FR/LG's style.

Yellow's portraits have the Game Boy's four shades: white (the background and
PIKACHU's fur alike), yellow, brown and near black. This keeps every line where
Yellow drew it and repaints the frames with the colors of FR/LG's PIKACHU battle
sprite (graphics/pokemon/pikachu/normal.pal):

- outlines in black;
- the white inside the outline (found by filling the background from the frame's
  edges) as yellow fur, lit where the outline is up and to the left and shaded where
  it is down and to the right, the light coming from the upper left like FR/LG's
  sprites; tiny white spots (eye shine) stay white;
- Yellow's yellow as shading where it touches the fur, and as the color of effects
  (hearts, bolts) floating around it;
- Yellow's brown split by shape: round filled patches are the cheeks (red, with a
  highlight and a shadow), thin bits deep shade, big ones (the flower pot) brown.

Run with --from to start from another copy of Yellow's sheet; by default it reads the
original colors from tools/data/pikachu_portraits_yellow.png, so running it twice
gives the same result.
"""
import os, sys
from PIL import Image

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = FR + '/tools/data/pikachu_portraits_yellow.png'
OUT = FR + '/graphics/pikachu_emotions/portraits.png'

# Yellow's indices
Y_CLEAR, Y_WHITE, Y_YELLOW, Y_BROWN, Y_DARK = 0, 1, 2, 3, 4

# the new palette (FR/LG PIKACHU colors plus the portrait window's white)
PALETTE = [
    (0, 0, 0),        # 0 transparent
    (255, 255, 246),  # 1 window white (as before)
    (255, 255, 123),  # 2 yellow highlight
    (255, 222, 0),    # 3 yellow
    (238, 180, 0),    # 4 yellow shade
    (197, 139, 0),    # 5 deep shade / body shadow
    (131, 82, 0),     # 6 brown
    (255, 123, 106),  # 7 cheek highlight
    (230, 41, 41),    # 8 cheek
    (164, 16, 16),    # 9 cheek shadow
    (16, 16, 16),     # 10 outline
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
]
WHITE, HILITE, YELLOW, SHADE, DEEP, BROWN, CHEEK_HI, CHEEK, CHEEK_LO, OUTLINE = range(1, 11)
FRAME = 40


def components(img, color, box):
    x0, y0, x1, y1 = box
    seen, comps = set(), []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if (x, y) in seen or img.getpixel((x, y)) != color:
                continue
            stack, comp = [(x, y)], []
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop()
                comp.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if x0 <= nx < x1 and y0 <= ny < y1 and (nx, ny) not in seen and img.getpixel((nx, ny)) == color:
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            comps.append(comp)
    return comps


def background(src, box):
    """The white around PIKACHU: white connected to the top and side edges of the
    frame (its body runs off the bottom edge, so that edge is left out)."""
    x0, y0, x1, y1 = box
    seeds = [(x, y0) for x in range(x0, x1)]
    seeds += [(x, y) for x in (x0, x1 - 1) for y in range(y0, y0 + (y1 - y0) * 3 // 4)]
    seen = set()
    stack = [p for p in seeds if src.getpixel(p) == Y_WHITE]
    seen.update(stack)
    while stack:
        cx, cy = stack.pop()
        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
            if x0 <= nx < x1 and y0 <= ny < y1 and (nx, ny) not in seen and src.getpixel((nx, ny)) == Y_WHITE:
                seen.add((nx, ny))
                stack.append((nx, ny))
    return seen


def recolor_frame(src, out, box):
    x0, y0, x1, y1 = box
    px = lambda x, y: src.getpixel((x, y)) if x0 <= x < x1 and y0 <= y < y1 else Y_WHITE
    bg = background(src, box)
    is_body = lambda x, y: x0 <= x < x1 and y0 <= y < y1 and (x, y) not in bg and src.getpixel((x, y)) in (Y_WHITE, Y_YELLOW)
    # white inside the outline is PIKACHU's fur, except tiny spots (eye shine, teeth)
    fur = set()
    for comp in components(src, Y_WHITE, box):
        if comp[0] in bg:
            continue
        if len(comp) <= 3:
            continue
        fur.update(comp)
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = src.getpixel((x, y))
            if c == Y_DARK:
                out.putpixel((x, y), OUTLINE)
            elif c == Y_CLEAR:
                out.putpixel((x, y), 0)
            elif (x, y) in fur:
                lower_right = Y_DARK in (px(x + 1, y), px(x, y + 1), px(x + 1, y + 1))
                upper_left = Y_DARK in (px(x - 1, y), px(x, y - 1), px(x - 1, y - 1))
                if lower_right and not upper_left:
                    out.putpixel((x, y), SHADE)
                elif upper_left and not lower_right:
                    out.putpixel((x, y), HILITE)
                else:
                    out.putpixel((x, y), YELLOW)
            elif c == Y_WHITE:
                out.putpixel((x, y), WHITE)
    # Yellow's yellow: shading where it touches the fur, an effect (hearts, bolts) elsewhere
    for comp in components(src, Y_YELLOW, box):
        touches_fur = any(n in fur for (x, y) in comp for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
        for (x, y) in comp:
            out.putpixel((x, y), SHADE if touches_fur else YELLOW)
    # Yellow's brown: round, filled patches are the cheeks, thin bits deep shade, big ones the pot
    for comp in components(src, Y_BROWN, box):
        xs, ys = [p[0] for p in comp], [p[1] for p in comp]
        w, h = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        filled = len(comp) / float(w * h)
        touches_fur = any(n in fur for (x, y) in comp for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
        if 6 <= len(comp) <= 30 and 3 <= w <= 7 and 3 <= h <= 7 and filled >= 0.45:
            # the cheek is the brown core and the ring of Yellow's yellow around it
            cheek = set(comp)
            for (x, y) in comp:
                for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1)):
                    if px(*n) == Y_YELLOW:
                        cheek.add(n)
            cxs, cys = [p[0] for p in cheek], [p[1] for p in cheek]
            for (x, y) in cheek:
                if (x + 1, y) not in cheek or (x, y + 1) not in cheek:
                    out.putpixel((x, y), CHEEK_LO)
                else:
                    out.putpixel((x, y), CHEEK)
            hx, hy = min(cxs) + (max(cxs) - min(cxs)) // 3, min(cys) + (max(cys) - min(cys)) // 3
            if (hx, hy) in cheek:
                out.putpixel((hx, hy), CHEEK_HI)
        else:
            color = DEEP if touches_fur or len(comp) < 6 else BROWN
            for (x, y) in comp:
                out.putpixel((x, y), color)


def main():
    src_path = sys.argv[sys.argv.index('--from') + 1] if '--from' in sys.argv else SRC
    src = Image.open(src_path)
    out = Image.new('P', src.size, 0)
    out.putpalette([v for c in PALETTE for v in c])
    for fy in range(0, src.size[1], FRAME):
        for fx in range(0, src.size[0], FRAME):
            recolor_frame(src, out, (fx, fy, fx + FRAME, fy + FRAME))
    out.save(OUT)
    print(f'{OUT}: {out.size}, colors {sorted(set(out.getdata()))}')


if __name__ == '__main__':
    main()
