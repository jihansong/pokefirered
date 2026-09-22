#!/usr/bin/env python3
"""Draw Oak's PIKACHU carrying the player on a balloon, for FLY.

Yellow shows PIKACHU holding a red balloon instead of a bird whenever it is the
POKéMON that FLIES. This builds the same five 64x64 frames the bird sheet has
(alone, then with the male and the female player, flying out and flying in), so
the FLY field effect can play them with the animations it already has.

Nothing is drawn freehand except the balloon:
  * the player is cut straight out of graphics/field_effects/pics/bird.png, pixel
    for pixel and in the same place in the frame, so the sprite still lines up
    with the player's own sprite while it flies (PLAYER_CUTOUT);
  * PIKACHU is its overworld sprite (front, back and side), recoloured from the
    NPC blue palette into the player palette, which the bird sheet uses and which
    happens to carry two of the same yellows, the cheek reds and two browns;
  * the balloon is an ellipse shaded the FR/LG way - a lit face, a body colour, a
    shaded underside, one white catchlight and a black outline - in the reds of
    that same palette, so the sheet stays inside one 16-colour palette.
"""
import os
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BIRD = ROOT + '/graphics/field_effects/pics/bird.png'
PIKA = ROOT + '/graphics/object_events/pics/pokemon/pikachu.png'
OUT = ROOT + '/graphics/field_effects/pics/fly_pikachu.png'

SIZE = 64
CLEAR = 0

# Colours of the player palette (graphics/object_events/palettes/player.pal), the
# one the bird sheet is drawn in and the one the FLY sprite is shown with.
BROWN, DARK_BROWN = 1, 4
WHITE, GREY = 9, 10
RED_LIT, RED, RED_DARK = 11, 12, 8
YELLOW, YELLOW_DARK = 13, 14
BLACK = 15

# PIKACHU's overworld sprite is drawn in the NPC blue palette; these are the same
# colours in the player palette. Its three yellows land on the player palette's
# two yellows plus a brown, its dark outline on the dark brown, and its cheeks,
# eye glints and black (ears, eyes) are already there.
PIKACHU_COLORS = {0: CLEAR, 5: YELLOW, 6: YELLOW_DARK, 7: BROWN,
                  11: RED_LIT, 13: DARK_BROWN, 14: WHITE, 15: BLACK}
FRONT, BACK, SIDE = 0, 1, 2            # frames of pikachu.png

# The part of each bird frame that is the player: for every row, the first and the
# last column of the player, read off the sheet. Everything outside is bird.
# Frames of bird.png: 1 male flying out, 2 male flying in, 3 female out, 4 female in.
PLAYER_CUTOUT = {
    1: {21: (27, 32), 22: (25, 34), 23: (24, 34), 24: (24, 35), 25: (24, 35),
        26: (24, 35), 27: (24, 35), 28: (24, 36), 29: (24, 36), 30: (24, 35),
        31: (24, 34), 32: (26, 35), 33: (27, 35), 34: (27, 33)},
    3: {21: (27, 32), 22: (25, 34), 23: (24, 34), 24: (24, 35), 25: (24, 36),
        26: (24, 36), 27: (24, 36), 28: (24, 38), 29: (24, 38), 30: (24, 37),
        31: (24, 36), 32: (25, 35), 33: (27, 35), 34: (27, 33)},
    2: {21: (27, 32), 22: (25, 34), 23: (25, 35), 24: (24, 35), 25: (24, 35),
        26: (24, 35), 27: (24, 35), 28: (25, 35), 29: (25, 35), 30: (25, 34),
        31: (26, 35), 32: (26, 34), 33: (26, 35), 34: (26, 35)},
    4: {21: (28, 33), 22: (26, 35), 23: (26, 36), 24: (25, 36), 25: (24, 37),
        26: (24, 37), 27: (24, 37), 28: (25, 36), 29: (25, 36), 30: (25, 37),
        31: (26, 37), 32: (26, 37), 33: (26, 37), 34: (26, 35)},
}

# The balloon: up and to the left of the player, where the bird's raised wing used
# to be. A slightly pear-shaped ellipse, lit from the upper left like everything
# else in FR/LG, with a black outline, a shaded rim along the underside, a lit
# face and one white catchlight.
BALLOON = (21, 13, 8, 9)               # centre x, centre y, x radius, y radius
PEAR = 0.18                            # how much narrower the balloon is at the bottom
LIT = (-0.42, -0.45)                   # where the light falls on it, in radii
CATCHLIGHT = (-5, -6)                  # the white 2x2 glint, in pixels from the centre


def balloon(frame):
    cx, cy, rx, ry = BALLOON
    px = frame.load()

    def norm(x, y):
        ny = (y - cy) / ry
        nx = (x - cx) / (rx * (1.0 - PEAR * max(0.0, ny)))
        return nx, ny

    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            nx, ny = norm(x, y)
            r = (nx * nx + ny * ny) ** 0.5
            if r > 1.0:
                # a black outline one pixel around the whole balloon
                if min((((x + dx - cx) / rx) ** 2 + ((y + dy - cy) / ry) ** 2) ** 0.5
                       for dx in (-1, 0, 1) for dy in (-1, 0, 1)) <= 1.0:
                    px[x, y] = BLACK
                continue
            lit = ((nx - LIT[0]) ** 2 + (ny - LIT[1]) ** 2) ** 0.5
            px[x, y] = (RED_DARK if r > 0.70 and nx * 0.6 + ny * 0.8 > 0.34
                        else RED_LIT if lit < 0.58 else RED)
    for y in range(cy + CATCHLIGHT[1], cy + CATCHLIGHT[1] + 2):
        for x in range(cx + CATCHLIGHT[0], cx + CATCHLIGHT[0] + 2):
            px[x, y] = WHITE
    # the knot, a couple of pixels of it, tied under the balloon
    px[cx - 1, cy + ry] = BLACK
    px[cx, cy + ry] = RED_DARK
    px[cx + 1, cy + ry] = BLACK
    px[cx, cy + ry + 1] = BLACK


def string(frame, end):
    """The balloon's string, from the knot down to PIKACHU's paw."""
    cx, cy, _rx, ry = BALLOON
    x0, y0 = cx, cy + ry + 2
    x1, y1 = end
    px = frame.load()
    for y in range(y0, y1 + 1):
        x = x0 + round((x1 - x0) * (y - y0) / (y1 - y0))
        px[x, y] = GREY


def pikachu(frame, sheet, pose, at):
    px = frame.load()
    src = sheet.crop((pose * 16, 0, pose * 16 + 16, 16)).load()
    for y in range(16):
        for x in range(16):
            c = PIKACHU_COLORS[src[x, y]]
            if c != CLEAR:
                px[at[0] + x, at[1] + y] = c


def player(frame, bird, birdFrame):
    """Copy the player out of one of the bird frames, into the same place."""
    px = frame.load()
    src = bird.crop((0, birdFrame * SIZE, SIZE, birdFrame * SIZE + SIZE)).load()
    for y, (x0, x1) in PLAYER_CUTOUT[birdFrame].items():
        for x in range(x0, x1 + 1):
            if src[x, y] != CLEAR:
                px[x, y] = src[x, y]


def main():
    bird = Image.open(BIRD)
    sheet = Image.open(PIKA)
    out = Image.new('P', (SIZE, SIZE * 5), CLEAR)
    out.putpalette(bird.getpalette())

    # (bird frame the player comes from, PIKACHU's pose, where PIKACHU goes,
    #  where its paw holds the string)
    frames = [
        (None, SIDE,  (24, 34), (24, 43)),   # 0: alone, as it leaves and re-enters the ball
        (1,    FRONT, (24, 34), (24, 43)),   # 1: male flying out
        (2,    BACK,  (24, 34), (24, 43)),   # 2: male flying in
        (3,    FRONT, (24, 34), (24, 43)),   # 3: female flying out
        (4,    BACK,  (24, 34), (24, 43)),   # 4: female flying in
    ]
    for n, (birdFrame, pose, at, paw) in enumerate(frames):
        frame = Image.new('P', (SIZE, SIZE), CLEAR)
        frame.putpalette(bird.getpalette())
        balloon(frame)
        string(frame, paw)
        pikachu(frame, sheet, pose, at)
        if birdFrame is not None:
            player(frame, bird, birdFrame)
        out.paste(frame, (0, n * SIZE))
    out.save(OUT)


if __name__ == '__main__':
    main()
