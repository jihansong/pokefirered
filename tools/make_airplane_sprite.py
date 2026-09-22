#!/usr/bin/env python3
"""Draw the airliners of the Vermilion airport.

The parked airliner is a 20x20 top down plane inside a 32x32 sprite frame (the
GBA only has 8, 16, 32 and 64 pixel sprites), drawn pixel by pixel from the
table below with the colours the truck palette already has, so the two share
one object palette slot. The sheet holds three frames, in the order the
standard facing animations use them: nose south, nose north and nose west
(east is west flipped).

The plane that flies over the airport (src/airport_flyover.c) is nearer the
viewer, so it is drawn half as large again: 30x30, one frame, nose north. Its
ground shadow is the parked plane's 20x20 silhouette.
"""
import os
from PIL import Image, ImageDraw

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = FR + '/graphics/object_events/pics/misc/airplane.png'
SHADOW_OUT = FR + '/graphics/object_events/pics/misc/airplane_shadow.png'
FLYOVER_OUT = FR + '/graphics/object_events/pics/misc/airplane_flyover.png'
PALETTE = FR + '/graphics/object_events/palettes/truck.pal'

# indices into the truck palette
CLEAR, WHITE, OFFWHITE, LIGHT, GREY, NAVY, BLUE, DARK, BLACK = 0, 14, 5, 6, 7, 8, 11, 13, 15


def poly(d, pts, fill):
    d.polygon([(x, y) for x, y in pts], fill=fill)


# The parked plane, nose north: the left ten columns of the 20x20 art, the
# right half is their mirror image. D outline, W white body, o/l/g the greys
# (light to dark), n navy windows and fin, B the blue livery band, K exhaust.
SMALL_KEY = {'.': CLEAR, 'D': DARK, 'W': WHITE, 'o': OFFWHITE, 'l': LIGHT,
             'g': GREY, 'n': NAVY, 'B': BLUE, 'K': BLACK}
SMALL_LEFT = [
    '........DD',   # nose
    '.......DWW',
    '.......Dnn',   # cockpit
    '.......DoW',
    '.......DoW',
    '.......DnW',   # cabin window
    '......DDoW',   # wing root
    '....DDlloW',
    '..DDlllloW',
    'DDllllllnW',
    'DlDggDlloW',   # engine under the wing
    'DgDggDDDoW',
    'DDDggD.DoW',   # wing tip
    '..DKKD.DoW',   # exhaust
    '.......DoW',
    '.....DDDBB',   # livery band, tailplane
    '...DDlllBn',   # fin
    '...DllllBn',
    '...DDDDDBn',
    '.......DDD',
]
SMALL_SIZE = 20


def draw_small(im):
    """The 20x20 parked plane, centred in the 32x32 frame."""
    off = (32 - SMALL_SIZE) // 2
    for y, left in enumerate(SMALL_LEFT):
        row = left + left[::-1]
        for x, ch in enumerate(row):
            if ch != '.':
                im.putpixel((off + x, off + y), SMALL_KEY[ch])


def draw(im):
    """Draw the 30x30 plane: the left half; the right half is mirrored onto it."""
    d = ImageDraw.Draw(im)
    # the fuselage is centred between columns 15 and 16, so column c mirrors to 31 - c
    for grow in (1, 0):
        body = DARK if grow else WHITE
        wing = DARK if grow else LIGHT
        # wing: swept back from the root to a short tip chord
        poly(d, [(13 - grow, 11 - grow), (16, 11 - grow), (16, 17),
                 (2 - grow, 21 + grow), (2 - grow, 18 - grow)], wing)
        # tailplane
        poly(d, [(13 - grow, 23 - grow), (16, 23 - grow), (16, 28 + grow),
                 (7 - grow, 28 + grow), (7 - grow, 26 - grow)], wing)
        # fuselage
        d.rounded_rectangle([13 - grow, 2 - grow, 16, 29 + grow], radius=3 + grow, fill=body)

    # fuselage shading, lit from the left
    d.line([(13, 6), (13, 26)], fill=OFFWHITE)
    # wing shading along the trailing edge
    d.line([(3, 20), (13, 17)], fill=GREY)
    d.line([(8, 27), (13, 27)], fill=GREY)
    # engine under the wing
    d.rectangle([6, 16, 9, 22], fill=DARK)
    d.rectangle([7, 17, 8, 21], fill=GREY)
    d.line([(7, 22), (8, 22)], fill=BLACK)
    # cockpit and cabin windows
    d.rectangle([13, 5, 16, 6], fill=NAVY)
    for y in range(9, 22, 3):
        d.point((13, y), fill=NAVY)

    # mirror the left half onto the right
    im.paste(im.crop((0, 0, 16, 32)).transpose(Image.FLIP_LEFT_RIGHT), (16, 0))

    # details that cross the middle: the livery band and the fin
    d = ImageDraw.Draw(im)
    d.rectangle([13, 23, 18, 24], fill=BLUE)
    poly(d, [(15, 21), (16, 21), (17, 29), (14, 29)], BLUE)
    d.line([(15, 25), (15, 29)], fill=NAVY)
    d.line([(16, 25), (16, 29)], fill=NAVY)


def main():
    pal = [int(v) for line in open(PALETTE).read().splitlines()[3:19] for v in line.split()]
    north = Image.new('P', (32, 32), CLEAR)
    north.putpalette(pal)
    draw_small(north)
    # the plane is centred on (16, 16), so quarter turns keep it inside the frame
    frames = [north.rotate(180), north, north.rotate(90)]
    sheet = Image.new('P', (32, 32 * len(frames)), CLEAR)
    sheet.putpalette(pal)
    for i, f in enumerate(frames):
        sheet.paste(f, (0, 32 * i))
    sheet.save(OUT)
    used = sorted(set(sheet.getdata()))
    print(f'{OUT}: {sheet.size[0]}x{sheet.size[1]}, {len(frames)} frames, {len(used)} colours {used}')

    # The plane flying over the airport, 30x30, nose north.
    big = Image.new('P', (32, 32), CLEAR)
    big.putpalette(pal)
    draw(big)
    big.save(FLYOVER_OUT)
    print(f'{FLYOVER_OUT}: 32x32, colours {sorted(set(big.getdata()))}')

    # Its ground shadow (src/airport_flyover.c): the 20x20 silhouette, nose
    # north, as a checkerboard of the palette's darkest blue, so the ground
    # shows through every other pixel. It stays two thirds the size of the
    # plane, as it was when the flyover was the 30x30 plane drawn 1.5x.
    shadow = Image.new('P', (32, 32), CLEAR)
    shadow.putpalette(pal)
    for y in range(32):
        for x in range(32):
            if north.getpixel((x, y)) != CLEAR and (x + y) % 2 == 0:
                shadow.putpixel((x, y), DARK)
    shadow.save(SHADOW_OUT)
    print(f'{SHADOW_OUT}: 20x20 shadow in 32x32, colours {sorted(set(shadow.getdata()))}')


if __name__ == '__main__':
    main()
