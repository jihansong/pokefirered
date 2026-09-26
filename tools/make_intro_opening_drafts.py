#!/usr/bin/env python3
"""Review material for scene 2 of the opening, from the built ROM.

    python3 tools/make_intro_opening_drafts.py [rom] [--out docs/anim/drafts/scene2-B]
                                               [--compare-rev 4041f0986 --compare-dir docs/anim/drafts/scene2]

Boots the ROM with no save and no input in the headless emulator (tools/qa/emu.py),
captures every frame of scene 2 and the frames around its cuts, and writes:

- keyN_FXXXX.png and keyN_FXXXX_x3.png: the key frames, 240x160 and 3x;
- emu-every3.png: every third frame of the scene as captured;
- cuts.png: the two frames either side of each cut (no blank or mixed frame);
- models.png: PIKACHU's frames beside FR/LG's front sprite at 6x, then the arm, ball,
  puff, spark and bolt frames at 4x;
- compare-A-B.png: draft A's key frames and PIKACHU beside draft B's (A's frames from
  --compare-dir, A's PIKACHU sheet from git at --compare-rev);
- contact-sheet.png: one page with the key frames, a strip and the models.

A capture named F shows the picture the game drew during frame F after power on,
one frame after the code set it up: the cut the code makes at F842 is first seen
at F843, so scene 2 is seen F843-918 (76 frames) and table frame t is seen at F843+t.
"""
import argparse
import io
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(HERE, 'qa'))
sys.path.insert(0, HERE)
from emu import Emu  # noqa: E402
import make_intro_opening_scene2 as s2  # noqa: E402
from intro_opening_art import to_image  # noqa: E402

FIRST, LAST = 843, 918           # captures showing scene 2
KEYS = [(843, 'camera truck starts, ball and hand in the middle'),
        (857, 'truck ends; PIKACHU narrows its eyes'),
        (864, 'beat 2: the ball opens, PIKACHU snaps away (smear), sparks warn'),
        (866, 'the bolt hits the ball, the screen shakes'),
        (868, 'the ball pops out in a puff, ears and tail overshoot'),
        (882, 'beat 3: the ball lands, the table bumps'),
        (901, 'beat 4: "hmph!" chin up, cheeks crackle'),
        (910, 'second crackle: the tail flicks')]
CUTS = [841, 842, 843, 844, 917, 918, 919, 920]
# draft A key frames to set beside draft B (same moments)
COMPARE = [('key2_F0863.png', 864, 'snap'), ('key3_F0866.png', 866, 'zap'),
           ('key5_F0881.png', 882, 'bounce'), ('key6_F0901.png', 901, 'sulk')]


def capture(rom, frames):
    shots = {}
    with Emu(rom) as e:
        for f in range(1, max(frames) + 1):
            e.run(1)
            if f in frames:
                shots[f] = Image.frombytes('RGB', (240, 160), e.screen())
    return shots


def labelled(images, labels, cols, scale, title=None, pad=6, bar=14, bg=(40, 40, 40)):
    ims = [im.resize((im.size[0] * scale, im.size[1] * scale), Image.NEAREST) for im in images]
    w = max(i.size[0] for i in ims)
    h = max(i.size[1] for i in ims)
    rows = (len(ims) + cols - 1) // cols
    top = bar + pad if title else 0
    out = Image.new('RGB', (cols * (w + pad) + pad, top + rows * (h + bar + pad) + pad), bg)
    d = ImageDraw.Draw(out)
    if title:
        d.text((pad, pad // 2), title, fill=(255, 255, 255))
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x, y = pad + c * (w + pad), top + pad + r * (h + bar + pad)
        d.text((x, y + 1), labels[i], fill=(255, 255, 255))
        out.paste(im, (x, y + bar))
    return out


def on_blue(im):
    im = im.convert('P') if im.mode != 'P' else im
    canvas = Image.new('RGB', im.size, (150, 190, 230))
    mask = Image.frombytes('L', im.size, bytes(255 if v else 0 for v in im.getdata()))
    canvas.paste(im.convert('RGB'), (0, 0), mask)
    return canvas


def stack(*parts):
    w = max(p.size[0] for p in parts)
    out = Image.new('RGB', (w, sum(p.size[1] for p in parts)), (40, 40, 40))
    y = 0
    for p in parts:
        out.paste(p, (0, y))
        y += p.size[1]
    return out


def models():
    art = s2.art()
    ref = Image.open(os.path.join(ROOT, 'graphics/pokemon/pikachu/front.png'))
    pikas = [on_blue(ref)] + [on_blue(to_image(f, s2.PIKA_PAL)) for f in art['pikachu'][0]]
    top = labelled(pikas, ['FR/LG front.png'] + list(s2.PIKA_FRAMES), 5, 6,
                   'PIKACHU model (tools/intro_opening_pikachu.py), 6x, beside the game sprite')
    props = [on_blue(to_image(f, s2.PROP_PAL)) for f in (s2.arm('hold'), s2.arm('open'))]
    small = [on_blue(to_image(f, s2.PROP_PAL)) for f in s2.ball_frames()] + \
            [on_blue(to_image(f, s2.PIKA_PAL)) for f in s2.spark_frames()]
    bolts = [on_blue(to_image(f, s2.PIKA_PAL)) for f in s2.bolt_frames()]
    mid = labelled(props + bolts, ['arm: hold', 'arm: open', 'bolt 0', 'bolt 1'], 4, 4)
    low = labelled(small, ['ball', 'ball 90', 'ball 180', 'ball 270', 'ball opening', 'puff 0', 'puff 1',
                           'spark 0', 'spark 1'], 9, 4)
    return stack(top, mid, low)


def compare(shots, rev, adir):
    rows = []
    for fname, fb, what in COMPARE:
        pa = os.path.join(ROOT, adir, fname)
        if os.path.exists(pa):
            rows.append((Image.open(pa).convert('RGB'), 'A ' + fname[5:10] + ' ' + what))
            rows.append((shots[fb], 'B F%d %s' % (fb, what)))
    keys = labelled([r[0] for r in rows], [r[1] for r in rows], 2, 2,
                    'Draft A (left) and draft B (right), same moments, 2x')
    try:
        raw = subprocess.check_output(['git', '-C', ROOT, 'show', '%s:graphics/intro/opening/scene2/pikachu.png' % rev])
        sheet = Image.open(io.BytesIO(raw))
        a_frames = [sheet.crop((0, 64 * i, 64, 64 * i + 64)) for i in range(sheet.size[1] // 64)]
    except (subprocess.CalledProcessError, OSError):
        a_frames = []
    b = s2.art()['pikachu'][0]
    b_frames = [to_image(b[s2.PIKA_FRAMES.index(n)], s2.PIKA_PAL) for n in ('A', 'B', 'C')]
    models_row = labelled([on_blue(f) for f in a_frames] + [on_blue(f) for f in b_frames],
                          ['A pose %s' % n for n in 'ABC'][:len(a_frames)] + ['B pose %s' % n for n in 'ABC'], 6, 5,
                          'PIKACHU: draft A (left three) and draft B (right three), 5x')
    return stack(keys, models_row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom', nargs='?', default=os.path.join(ROOT, 'pokemonthyl.gba'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs/anim/drafts/scene2-B'))
    ap.add_argument('--compare-rev', default='4041f0986')
    ap.add_argument('--compare-dir', default='docs/anim/drafts/scene2')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    frames = set(range(FIRST, LAST + 1)) | set(CUTS) | {f for f, _ in KEYS}
    shots = capture(a.rom, frames)
    for i, (f, _) in enumerate(KEYS, 1):
        shots[f].save(os.path.join(a.out, 'key%d_F%04d.png' % (i, f)))
        shots[f].resize((720, 480), Image.NEAREST).save(os.path.join(a.out, 'key%d_F%04d_x3.png' % (i, f)))
    every = list(range(FIRST, LAST + 1, 3))
    labelled([shots[f] for f in every], ['F%d (t%d)' % (f, f - FIRST) for f in every], 6, 1,
             'scene 2 draft B in the emulator, every 3rd frame (t = frame of the scene)').save(
        os.path.join(a.out, 'emu-every3.png'))
    labelled([shots[f] for f in CUTS], ['F%d' % f for f in CUTS], 4, 1,
             'cuts: scene 1 -> 2 (F842 | F843) and 2 -> 3 (F918 | F919)').save(os.path.join(a.out, 'cuts.png'))
    m = models()
    m.save(os.path.join(a.out, 'models.png'))
    compare(shots, a.compare_rev, a.compare_dir).save(os.path.join(a.out, 'compare-A-B.png'))
    keys = labelled([shots[f] for f, _ in KEYS], ['%d. F%d %s' % (i, f, t) for i, (f, t) in enumerate(KEYS, 1)],
                    4, 2, 'Thunder Yellow opening, scene 2 draft B: the PIKACHU that hates POKe BALLS '
                          '(76 frames, bar 2 of MUS_INTRO_FIGHT)')
    strip = labelled([shots[f] for f in range(FIRST, LAST + 1, 6)],
                     ['F%d' % f for f in range(FIRST, LAST + 1, 6)], 13, 1, 'every 6th frame')
    stack(keys, strip, m).save(os.path.join(a.out, 'contact-sheet.png'))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
