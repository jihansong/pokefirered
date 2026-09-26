#!/usr/bin/env python3
"""Stand-in graphics for the opening scenes that are not drawn yet.

Until a scene gets its own pictures (docs/v0.11.0-plan.md 10.1, O2-O4), the opening
shows a flat colour card with the scene's number on it, cut on the same bars of the
music the finished scene will use. This draws the numbers 1-7 as 32x32 sprites
(white, black outline) into graphics/intro/opening/placeholder_digits.png.
"""
import os

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = ROOT + '/graphics/intro/opening/placeholder_digits.png'

FONT = {  # 5x7
    '1': ['..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '.###.'],
    '2': ['.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'],
    '3': ['####.', '....#', '....#', '.###.', '....#', '....#', '####.'],
    '4': ['...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'],
    '5': ['#####', '#....', '####.', '....#', '....#', '#...#', '.###.'],
    '6': ['..##.', '.#...', '#....', '####.', '#...#', '#...#', '.###.'],
    '7': ['#####', '....#', '...#.', '..#..', '.#...', '.#...', '.#...'],
}
PAL = [(0, 0, 0), (255, 255, 255), (16, 16, 16)] + [(0, 0, 0)] * 13
SCALE = 4


def digit(ch):
    img = [[0] * 32 for _ in range(32)]
    x0, y0 = (32 - 5 * SCALE) // 2, (32 - 7 * SCALE) // 2
    for r, row in enumerate(FONT[ch]):
        for c, v in enumerate(row):
            if v == '#':
                for dy in range(SCALE):
                    for dx in range(SCALE):
                        img[y0 + r * SCALE + dy][x0 + c * SCALE + dx] = 1
    for y in range(32):
        for x in range(32):
            if img[y][x] == 0 and any(0 <= y + dy < 32 and 0 <= x + dx < 32 and img[y + dy][x + dx] == 1
                                      for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                img[y][x] = 2
    return img


def main():
    rows = [r for ch in '1234567' for r in digit(ch)]
    im = Image.new('P', (32, len(rows)), 0)
    flat = []
    for c in PAL:
        flat += c
    im.putpalette(flat)
    im.putdata([v for r in rows for v in r])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    im.save(OUT)


if __name__ == '__main__':
    main()
