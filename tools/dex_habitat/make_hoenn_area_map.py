#!/usr/bin/env python3
"""Draw the Pokedex area screen's Hoenn map and its marker table.

    python3 tools/dex_habitat/make_hoenn_area_map.py

The land and sea come from the FLY map (graphics/region_map/hoenn.png and
hoenn_tilemap.bin, imported from pokeemerald); routes and towns are drawn from
pokeemerald's map section grid in the style of graphics/pokedex/map_kanto.png.
Writes graphics/pokedex/map_hoenn.png and src/data/pokedex_area_hoenn.h.
"""
import json
import os
import struct

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RM = os.path.join(ROOT, "graphics", "region_map")
SECTIONS = os.path.join(os.path.dirname(__file__), "hoenn_map_sections.json")

W, H = 128, 72                 # window size (16x9 tiles)
CELLS_X, CELLS_Y = 28, 15      # the FLY map's grid
SRC_X, SRC_Y = 8, 16           # screen pixel of cell (0, 0) on the FLY map
IN_X, IN_Y, IN_W, IN_H = 3, 3, 122, 66   # where the grid lands in the window
# map_kanto.png's palette indices
FRAME, LIGHT, WHITE, LAND, SEA = 2, 3, 5, 6, 7

# Hoenn map sections that are water routes: drawn like Kanto's sea routes
WATER = {"ROUTE_105", "ROUTE_106", "ROUTE_107", "ROUTE_108", "ROUTE_109", "ROUTE_122", "ROUTE_124",
         "ROUTE_125", "ROUTE_126", "ROUTE_127", "ROUTE_128", "ROUTE_129", "ROUTE_130", "ROUTE_131",
         "ROUTE_132", "ROUTE_133", "ROUTE_134"}


def render_fly_map():
    tiles = Image.open(os.path.join(RM, "hoenn.png"))
    tm = open(os.path.join(RM, "hoenn_tilemap.bin"), "rb").read()
    tw = tiles.size[0] // 8
    out = Image.new("P", (240, 160))
    out.putpalette(tiles.getpalette())
    for i in range(600):
        e = struct.unpack_from("<H", tm, i * 2)[0]
        t = e & 0x3FF
        tx, ty = (t % tw) * 8, (t // tw) * 8
        if ty >= tiles.size[1]:
            continue
        tile = tiles.crop((tx, ty, tx + 8, ty + 8))
        if e & 0x400:
            tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
        if e & 0x800:
            tile = tile.transpose(Image.FLIP_TOP_BOTTOM)
        out.paste(tile, ((i % 30) * 8, (i // 30) * 8))
    return out.convert("RGB")


def is_land(rgb):
    r, g, b = rgb
    return not (b > r + 24 and b >= g)   # blues are sea; greens, yellows and reds are land


def cell_to_px(cx, cy):
    return IN_X + cx * IN_W / CELLS_X, IN_Y + cy * IN_H / CELLS_Y


def main():
    src = render_fly_map()
    img = Image.new("P", (W, H), FRAME)
    pal = Image.open(os.path.join(ROOT, "graphics", "pokedex", "map_kanto.png")).getpalette()
    img.putpalette(pal)
    px = img.load()
    for y in range(IN_Y, IN_Y + IN_H):
        for x in range(IN_X, IN_X + IN_W):
            # sample the FLY map area this pixel covers and take the majority
            sx0 = SRC_X + (x - IN_X) * CELLS_X * 8 / IN_W
            sy0 = SRC_Y + (y - IN_Y) * CELLS_Y * 8 / IN_H
            land = 0
            n = 0
            for dy in (0.25, 0.75):
                for dx in (0.25, 0.75):
                    sx = int(sx0 + dx * CELLS_X * 8 / IN_W)
                    sy = int(sy0 + dy * CELLS_Y * 8 / IN_H)
                    # the FLY map's CANCEL button sits in the sea at the bottom right
                    button = sx >= SRC_X + 25 * 8 and sy >= SRC_Y + 12 * 8
                    land += 0 if button else is_land(src.getpixel((min(sx, 239), min(sy, 159))))
                    n += 1
            px[x, y] = LAND if land * 2 > n else SEA
    # rounded frame corners like the Kanto map
    for (x, y) in ((IN_X, IN_Y), (IN_X + IN_W - 1, IN_Y), (IN_X, IN_Y + IN_H - 1), (IN_X + IN_W - 1, IN_Y + IN_H - 1)):
        px[x, y] = FRAME

    sections = json.load(open(SECTIONS))
    # routes: a 2px white band along the section's long axis, light edge
    def band(x0, y0, x1, y1, colour):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                if IN_X <= x < IN_X + IN_W and IN_Y <= y < IN_Y + IN_H:
                    px[x, y] = colour
    towns = []
    routes = []
    for s in sections:
        if s.get("x") is None:
            continue
        name = s["id"].replace("MAPSEC_", "")
        if name.startswith("ROUTE_"):
            routes.append(s)
        elif name.endswith("_TOWN") or name.endswith("_CITY"):
            towns.append(s)
    def route_line(s):
        # one line through the middle of the section, along its long side
        w, h = s["width"], s["height"]
        if w >= 2 and h >= 2 and s["id"].replace("MAPSEC_", "") in WATER:
            return None  # open sea (Routes 124-127): only the marker shows it
        if w >= h:
            return (s["x"] + 0.5, s["y"] + h / 2, s["x"] + w - 0.5, s["y"] + h / 2)
        return (s["x"] + w / 2, s["y"] + 0.5, s["x"] + w / 2, s["y"] + h - 0.5)
    for inset, colour in ((2, LIGHT), (1, WHITE)):
        for s in routes:
            line = route_line(s)
            if line is None:
                continue
            x0, y0 = cell_to_px(line[0], line[1])
            x1, y1 = cell_to_px(line[2], line[3])
            band(x0 - inset, y0 - inset, x1 + inset - 1, y1 + inset - 1, colour)
    for s in towns:
        x0, y0 = cell_to_px(s["x"], s["y"])
        x1, y1 = cell_to_px(s["x"] + s["width"], s["y"] + s["height"])
        band(x0, y0, x1 - 1, y1 - 1, LIGHT)
        band(x0 + 1, y0 + 1, x1 - 2, y1 - 2, WHITE)
    img.save(os.path.join(ROOT, "graphics", "pokedex", "map_hoenn.png"))

    # Marker table: one subsprite per map section, centred on its cells
    shapes = [("MARKER_CIRCULAR", 8, 8), ("MARKER_SMALL_H", 16, 8), ("MARKER_SMALL_V", 8, 16),
              ("MARKER_MED_H", 32, 16), ("MARKER_MED_V", 16, 32)]
    lines = ["// Generated by tools/dex_habitat/make_hoenn_area_map.py from pokeemerald's",
             "// map section grid. {marker, x, y} relative to the Hoenn area map's top left.",
             "static const s8 sHoennAreaMarkers[][3] = {"]
    for s in sections:
        if s.get("x") is None:
            continue
        cx0, cy0 = cell_to_px(s["x"], s["y"])
        cx1, cy1 = cell_to_px(s["x"] + s["width"], s["y"] + s["height"])
        w, h = cx1 - cx0 + 4, cy1 - cy0 + 4
        best = min(shapes, key=lambda sh: abs(sh[1] - max(w, 8)) + abs(sh[2] - max(h, 8)))
        mx = round((cx0 + cx1) / 2 - best[1] / 2)
        my = round((cy0 + cy1) / 2 - best[2] / 2)
        lines.append("    [%s] = {%s, %d, %d}," % (s["id"], best[0], mx, my))
    lines.append("};")
    # pokeemerald's ALTERING CAVE (Route 103) uses FR/LG's MAPSEC_ALTERING_CAVE
    cx0, cy0 = cell_to_px(6, 8)
    cx1, cy1 = cell_to_px(7, 9)
    lines.append("")
    lines.append("static const s8 sHoennAlteringCaveMarker[3] = {MARKER_CIRCULAR, %d, %d};" % (
        round((cx0 + cx1) / 2 - 4), round((cy0 + cy1) / 2 - 4)))
    with open(os.path.join(ROOT, "src", "data", "pokedex_area_hoenn.h"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
