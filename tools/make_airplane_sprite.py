#!/usr/bin/env python3
"""Draw the parked airliner that stands on the Vermilion airport apron.

A 30x30 top down plane inside a 32x32 sprite frame (the GBA only has 8, 16,
32 and 64 pixel sprites), nose pointing north, drawn with the colours the
truck palette already has so the two share one object palette slot.
"""
import os
from PIL import Image, ImageDraw

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = FR + '/graphics/object_events/pics/misc/airplane.png'
PALETTE = FR + '/graphics/object_events/palettes/truck.pal'

# indices into the truck palette
CLEAR, WHITE, OFFWHITE, LIGHT, GREY, NAVY, BLUE, DARK, BLACK = 0, 14, 5, 6, 7, 8, 11, 13, 15


def poly(d, pts, fill):
    d.polygon([(x, y) for x, y in pts], fill=fill)


def draw(im):
    """Draw the left half of the plane; the right half is mirrored onto it."""
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
    im = Image.new('P', (32, 32), CLEAR)
    pal = [int(v) for line in open(PALETTE).read().splitlines()[3:19] for v in line.split()]
    im.putpalette(pal)
    draw(im)
    im.save(OUT)
    used = sorted(set(im.getdata()))
    print(f'{OUT}: {im.size[0]}x{im.size[1]}, bbox {im.getbbox()}, {len(used)} colours {used}')


if __name__ == '__main__':
    main()
