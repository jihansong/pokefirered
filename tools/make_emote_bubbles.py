#!/usr/bin/env python3
"""Redraw the starter PIKACHU's emote bubbles (graphics/pikachu_emotions/emote_bubbles.png)
in FR/LG's style.

Yellow's bubbles were black and white. These use the bubble of FR/LG's own emoticons
(graphics/misc/emoticons.png, the fully open frames): white with a pale blue rim, and
its palette. The "!", "?" and smile are FR/LG's icons as they are; the skull, heart,
bolt, sleeping Zs and fish are drawn in the same space and colors. Same order and
size as before: eight 16x16 bubbles stacked vertically.
"""
import os
from PIL import Image

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
EMOTICONS = FR + '/graphics/misc/emoticons.png'
OUT = FR + '/graphics/pikachu_emotions/emote_bubbles.png'

# rows of the open bubbles in emoticons.png (third column)
FRLG_EXCLAMATION, FRLG_SMILE, FRLG_QUESTION = 0, 3, 4
FILL = 9                      # the bubble's white
INNER_X, INNER_Y = 4, 5       # top left of the 8x7 space for a symbol

# symbols in the emoticon palette: 5 blue, 6 dark blue, 9 white, B red, C dark red,
# D yellow, E dark yellow
SYMBOLS = {
    'SKULL': [
        '..6666..',
        '.699996.',
        '.669966.',
        '.699996.',
        '..6996..',
        '..6666..',
        '..6.6.6.',
    ],
    'HEART': [
        '.CC..CC.',
        'CB9CCBBC',
        'CBBBBBBC',
        'CBBBBBBC',
        '.CBBBBC.',
        '..CBBC..',
        '...CC...',
    ],
    'BOLT': [
        '....EEE.',
        '...EDDE.',
        '..EDDE..',
        '.EDDDDDE',
        '..EEDDE.',
        '...EDE..',
        '...EE...',
    ],
    'ZZZ': [
        '....5555',
        '.....55.',
        '....5555',
        '5555....',
        '..55....',
        '.55.....',
        '5555....',
    ],
    'FISH': [
        '........',
        '..6666.6',
        '.695556 ',
        '65555566',
        '.6555566',
        '..6666.6',
        '........',
    ],
}
ORDER = ['EXCLAMATION', 'QUESTION', 'SMILE', 'SKULL', 'HEART', 'BOLT', 'ZZZ', 'FISH']


def frlg_icon(sheet, row):
    return sheet.crop((32, row * 16, 48, row * 16 + 16))


def empty_bubble(sheet):
    """The "!" bubble with its mark painted over in the bubble's white."""
    icon = frlg_icon(sheet, FRLG_EXCLAMATION).copy()
    for y in range(4, 12):
        for x in range(3, 13):
            if icon.getpixel((x, y)) in (0xB, 0xC):
                icon.putpixel((x, y), FILL)
    return icon


def draw(bubble, symbol):
    for y, line in enumerate(symbol):
        for x, ch in enumerate(line):
            if ch not in '. ':
                bubble.putpixel((INNER_X + x, INNER_Y + y), int(ch, 16))
    return bubble


def main():
    sheet = Image.open(EMOTICONS)
    frames = []
    for name in ORDER:
        if name == 'EXCLAMATION':
            frames.append(frlg_icon(sheet, FRLG_EXCLAMATION))
        elif name == 'QUESTION':
            frames.append(frlg_icon(sheet, FRLG_QUESTION))
        elif name == 'SMILE':
            frames.append(frlg_icon(sheet, FRLG_SMILE))
        else:
            frames.append(draw(empty_bubble(sheet), SYMBOLS[name]))
    out = Image.new('P', (16, 16 * len(frames)), 0)
    out.putpalette(sheet.getpalette())
    for i, f in enumerate(frames):
        out.paste(f, (0, 16 * i))
    out.save(OUT)
    print(f'{OUT}: {out.size}, colors {sorted(set(out.getdata()))}')


if __name__ == '__main__':
    main()
