#!/usr/bin/env python3
"""Review material for scene 2 of the opening, from the built ROM.

    python3 tools/make_intro_opening_drafts.py [rom] [--out docs/anim/drafts/scene2-C]
        [--label final] [--wav-tool path/to/audiocap.py]

Boots the ROM with no save and no input in the headless emulator (tools/qa/emu.py),
captures F760-930 (the end of scene 1, all of scene 2, the start of scene 3) and writes:

- keyN_FXXXX.png and keyN_FXXXX_x3.png: the key frames, 240x160 and 3x;
- keyN_FXXXX_crop.png and keyN_FXXXX_crop_x3.png: PIKACHU cropped at 1x and 3x for the
  wide sulk (F890) and the close-up "hmph" (F900);
- emu-every3.png: every third frame of the scene as captured;
- cuts.png: the frames either side of each cut (into scene 2, into the close-up, out);
- models.png: PIKACHU's frames beside FR/LG's front sprite at 6x, the close-up at 3x,
  then the arm, ball, puff, spark and bolt frames at 4x;
- preview.gif: F760-930 at 2x, 30 frames a second (every second frame);
- preview.wav: the same span of sound, if --wav-tool names an audio-capable
  tools/qa/audiocap.py (22050 Hz mono);
- contact-sheet.png: one page with the key frames, a strip and the models.

A capture named F shows the picture the game drew during frame F after power on,
one frame after the code set it up: the cut the code makes at F842 is first seen at
F843, so scene 2 is seen F843-918 (76 frames) and table frame t is seen at F843+t.
"""
import argparse
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
import intro_opening_pikachu as pika  # noqa: E402
from intro_opening_art import to_image  # noqa: E402

FIRST, LAST = 843, 918           # captures showing scene 2
SPAN = (760, 930)                # the moving preview
KEYS = [(843, 'camera truck starts, ball and hand in the middle'),
        (857, 'truck ends; PIKACHU narrows its eyes'),
        (864, 'beat 2: the ball opens, PIKACHU snaps away (smear), sparks warn'),
        (866, 'the bolt hits the ball, the screen shakes'),
        (868, 'the ball pops out in a puff, ears and tail overshoot'),
        (882, 'beat 3: the ball lands, the table bumps, the tail slaps'),
        (890, 'sulking, arms at its sides (last wide frame)'),
        (891, 'cut to the close-up (half a beat before beat 4)'),
        (900, 'beat 4: pressed down a pixel, the cheek crackles'),
        (910, 'second crackle, the camera has crept in')]
CROPS = {890: (132, 36, 212, 120), 900: (40, 32, 200, 128)}   # PIKACHU at the wide sulk, the close-up
CUTS = [842, 843, 890, 891, 918, 919]


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
    cu = pika.closeup_frames()
    close = labelled([on_blue(to_image(cu[n], s2.PIKA_PAL)) for n in ('CU', 'CU_hmph')],
                     ['close-up (2x model, 1 px lines)', 'close-up "hmph"'], 2, 3)
    props = [on_blue(to_image(f, s2.PROP_PAL)) for f in (s2.arm('hold'), s2.arm('open'))]
    small = [on_blue(to_image(f, s2.PROP_PAL)) for f in s2.ball_frames()] + \
            [on_blue(to_image(f, s2.PIKA_PAL)) for f in s2.spark_frames() + s2.crackle_frames()]
    bolts = [on_blue(to_image(f, s2.PIKA_PAL)) for f in s2.bolt_frames()]
    mid = labelled(props + bolts, ['arm: hold', 'arm: open', 'bolt 0', 'bolt 1'], 4, 4)
    low = labelled(small, ['ball', 'ball 90', 'ball 180', 'ball 270', 'ball opening', 'puff 0', 'puff 1',
                           'spark 0', 'spark 1', 'crackle 0', 'crackle 1'], 11, 4)
    return stack(top, close, mid, low)


def gif(shots, path):
    frames = [shots[f].resize((480, 320), Image.NEAREST) for f in range(SPAN[0], SPAN[1] + 1, 2)]
    durations = [30 if i % 3 else 40 for i in range(len(frames))]   # 33.3 ms on average
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations, loop=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom', nargs='?', default=os.path.join(ROOT, 'pokemonthyl.gba'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs/anim/drafts/scene2-final'))
    ap.add_argument('--label', default='final')
    ap.add_argument('--wav-tool', default=None, help='an audio-capable tools/qa/audiocap.py')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    frames = set(range(SPAN[0], SPAN[1] + 1)) | set(CUTS) | {f for f, _ in KEYS}
    shots = capture(a.rom, frames)
    for i, (f, _) in enumerate(KEYS, 1):
        shots[f].save(os.path.join(a.out, 'key%d_F%04d.png' % (i, f)))
        shots[f].resize((720, 480), Image.NEAREST).save(os.path.join(a.out, 'key%d_F%04d_x3.png' % (i, f)))
        if f in CROPS:
            crop = shots[f].crop(CROPS[f])
            crop.save(os.path.join(a.out, 'key%d_F%04d_crop.png' % (i, f)))
            crop.resize((crop.size[0] * 3, crop.size[1] * 3), Image.NEAREST).save(
                os.path.join(a.out, 'key%d_F%04d_crop_x3.png' % (i, f)))
    every = list(range(FIRST, LAST + 1, 3))
    labelled([shots[f] for f in every], ['F%d (t%d)' % (f, f - FIRST) for f in every], 6, 1,
             'scene 2 draft %s in the emulator, every 3rd frame (t = frame of the scene)' % a.label).save(
        os.path.join(a.out, 'emu-every3.png'))
    labelled([shots[f] for f in CUTS], ['F%d' % f for f in CUTS], 2, 1,
             'cuts: into scene 2 (F842 | F843), into the close-up (F890 | F891), '
             'into scene 3 (F918 | F919)').save(os.path.join(a.out, 'cuts.png'))
    m = models()
    m.save(os.path.join(a.out, 'models.png'))
    gif(shots, os.path.join(a.out, 'preview.gif'))
    if a.wav_tool:
        subprocess.check_call([sys.executable, a.wav_tool, a.rom, os.path.join(a.out, 'preview.wav'),
                               '--skip', str(SPAN[0] - 1), '--frames', str(SPAN[1] - SPAN[0] + 1), '--small'])
    keys = labelled([shots[f] for f, _ in KEYS], ['%d. F%d %s' % (i, f, t) for i, (f, t) in enumerate(KEYS, 1)],
                    5, 2, 'Thunder Yellow opening, scene 2 draft %s: the PIKACHU that hates POKe BALLS '
                          '(76 frames, bar 2 of MUS_INTRO_FIGHT)' % a.label)
    strip = labelled([shots[f] for f in range(FIRST, LAST + 1, 6)],
                     ['F%d' % f for f in range(FIRST, LAST + 1, 6)], 13, 1, 'every 6th frame')
    stack(keys, strip, m).save(os.path.join(a.out, 'contact-sheet.png'))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
