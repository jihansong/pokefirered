#!/usr/bin/env python3
"""Draw Oak's PIKACHU swimming with the player on its back, for SURF.

Six 32x32 frames laid out like the SURF blob's (south x2, north x2, west x2; east is
west flipped), so the blob's animations and bobbing apply unchanged. Each frame is
built from the follower PIKACHU's overworld sprite (front, back, side), placed so
that its face or tail shows around the player sitting on it (POSES), cut off at the
waterline with a line of foam; the second frame of each pair moves
the foam and the paws for the paddling. Colors are the NPC blue palette's, the one
the PIKACHU sprite uses.
"""
import os
from PIL import Image

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PIKA = FR + '/graphics/object_events/pics/pokemon/pikachu.png'
PAL = FR + '/graphics/object_events/palettes/npc_blue.pal'
OUT = FR + '/graphics/object_events/pics/misc/surf_pikachu.png'

CLEAR, YELLOW, DARK_YELLOW, BROWN, OUTLINE, WHITE = 0, 5, 6, 7, 13, 14
FRONT, BACK, SIDE = 0, 1, 2            # frames of pikachu.png


def pikachu_frame(sheet, n):
    return sheet.crop((n * 16, 0, n * 16 + 16, 16))


# Where each pose goes, in the 32x32 frame. The player's sprite covers columns 8..23
# down to row 24, so what must be seen is put outside that: PIKACHU's face below the
# player when heading south, its tail beside the player when heading north, and its
# head in front of / tail behind the player when heading west.
# Each part: (source columns x0..x1, source rows y0..y1, destination x, destination y)
POSES = {
    FRONT: {'parts': [(0, 15, 2, 12, 8, 18)], 'waterline': 29},
    BACK:  {'parts': [(0, 15, 2, 13, 10, 15)], 'waterline': 27},
    SIDE:  {'parts': [(0, 10, 2, 14, 2, 14), (11, 15, 6, 13, 22, 14)], 'waterline': 27},
}


def swimming(pika, pose, paddle):
    frame = Image.new('P', (32, 32), CLEAR)
    waterline = POSES[pose]['waterline']
    for x0, x1, y0, y1, dx, dy in POSES[pose]['parts']:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                c = pika.getpixel((x, y))
                tx, ty = dx + x - x0, dy + y - y0
                if c != CLEAR and ty <= waterline:
                    frame.putpixel((tx, ty), c)
    # foam along the waterline under everything that shows, a pixel wider each side
    cols = [x for x in range(32) if any(frame.getpixel((x, y)) != CLEAR for y in range(waterline - 2, waterline + 1))]
    if cols:
        x0, x1 = min(cols) - 1, max(cols) + 1
        for x in range(x0, x1 + 1):
            if (x + paddle) % 3:
                frame.putpixel((x, waterline + 1), WHITE)
            if x0 + 1 < x < x1 - 1 and (x + paddle) % 2 and waterline + 2 < 32:
                frame.putpixel((x, waterline + 2), WHITE)
        # a paw paddling at the waterline, left then right
        paw_x = x0 + 2 if paddle == 0 else x1 - 2
        frame.putpixel((paw_x, waterline), YELLOW)
        frame.putpixel((paw_x, waterline - 1), OUTLINE)
    return frame


def main():
    sheet = Image.open(PIKA)
    frames = []
    for pose in (FRONT, BACK, SIDE):
        pika = pikachu_frame(sheet, pose)
        for paddle in (0, 1):
            frames.append(swimming(pika, pose, paddle))
    out = Image.new('P', (32 * len(frames), 32), CLEAR)
    pal = [int(v) for line in open(PAL).read().splitlines()[3:19] for v in line.split()]
    out.putpalette(pal)
    for i, f in enumerate(frames):
        out.paste(f, (32 * i, 0))
    out.save(OUT)
    print(f'{OUT}: {out.size[0]}x{out.size[1]}, colors {sorted(set(out.getdata()))}')


if __name__ == '__main__':
    main()
