#!/usr/bin/env python3
"""Review material for scenes 4 and 5 of the opening, from the built ROM.

    python3 tools/make_intro_opening_drafts45.py [rom] [--out docs/anim/drafts/scene45-A]
        [--label A] [--wav-tool path/to/audiocap.py]

Boots the ROM with no save and no input (tools/qa/emu.py), captures F960-1330 (the end
of scene 3, scenes 4 and 5, the start of scene 6) and writes:

- keyN_FXXXX.png and keyN_FXXXX_x3.png: the key frames, 240x160 and 3x;
- emu-every3-scene4.png, emu-every3-scene5.png: every third frame as captured;
- cuts.png: the frames either side of each cut (into 4, the cut inside 4, into 5,
  the tilt, into 6);
- preview.gif: F960-1330 at 2x, 30 frames a second (every second frame);
- preview.wav: the same span of sound, if --wav-tool names an audio-capable
  tools/qa/audiocap.py (22050 Hz mono);
- contact-sheet.png: one page with the key frames and a strip of each scene.

A capture named F shows what the code set up at F-1 (storyboard 3.7): scene 4 is seen
at F996-1148, scene 5 at F1149-1301.
"""
import argparse
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(HERE, 'qa'))
from emu import Emu  # noqa: E402

SPAN = (960, 1330)
S4, S5 = (996, 1148), (1149, 1301)
KEYS = [(1000, '4a: the storm gathers, RED runs in'),
        (1036, '4a: running with the small PIKACHU in his arms; the flock comes in'),
        (1060, '4a: bending down (no cut: one shot from here to 5b)'),
        (1090, '4b: crouched over the small PIKACHU, the flock circling'),
        (1115, '4b: arms out as they dive (screen shakes)'),
        (1130, '4b: the distant flash on beat 4 (sky lit, field barely)'),
        (1154, '5a: the small PIKACHU crouches on his shoulder'),
        (1162, '5a: it springs up out of the picture'),
        (1175, '5b: the camera tilts up into the clouds'),
        (1187, '5b: beat 3: the lightning strikes PIKACHU (cry)'),
        (1215, '5b: hanging in the storm, cheeks crackling'),
        (1236, '5c: THUNDERBOLT, the flock closing in'),
        (1260, '5c: the flock struck, falling upside down'),
        (1290, '5c: the white-out into scene 6'),
        (1050, '4a: turned, holding it'),
        (1058, '4a: in-between 1: knees bending'),
        (1062, '4a: in-between 2: into the crouch'),
        (1223, '5b: the wind-up before THUNDERBOLT'),
        (1237, '5c: the flock struck: white for 2 frames'),
        (1242, '5c: the second burst drawing')]
CUTS = [995, 996, 1072, 1073, 1147, 1148, 1149, 1150, 1301, 1302]


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


def stack(*parts):
    w = max(p.size[0] for p in parts)
    out = Image.new('RGB', (w, sum(p.size[1] for p in parts)), (40, 40, 40))
    y = 0
    for p in parts:
        out.paste(p, (0, y))
        y += p.size[1]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom', nargs='?', default=os.path.join(ROOT, 'pokemonthyl.gba'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs/anim/drafts/scene45-B'))
    ap.add_argument('--label', default='B')
    ap.add_argument('--wav-tool', default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    shots = capture(a.rom, set(range(SPAN[0], SPAN[1] + 1)))
    for i, (f, _) in enumerate(KEYS, 1):
        shots[f].save(os.path.join(a.out, 'key%02d_F%04d.png' % (i, f)))
        box = (64, 32, 176, 128)                   # the middle of the picture at 1x and 3x
        crop = shots[f].crop(box)
        crop.save(os.path.join(a.out, 'key%02d_F%04d_mid.png' % (i, f)))
        crop.resize((crop.size[0] * 3, crop.size[1] * 3), Image.NEAREST).save(
            os.path.join(a.out, 'key%02d_F%04d_mid_x3.png' % (i, f)))
        shots[f].resize((720, 480), Image.NEAREST).save(os.path.join(a.out, 'key%02d_F%04d_x3.png' % (i, f)))
    for n, (f0, f1) in (('scene4', S4), ('scene5', S5)):
        every = list(range(f0, f1 + 1, 3))
        labelled([shots[f] for f in every], ['F%d (t%d)' % (f, f - f0) for f in every], 6, 1,
                 '%s draft %s in the emulator, every 3rd frame (t = frame of the scene)' % (n, a.label)).save(
            os.path.join(a.out, 'emu-every3-%s.png' % n))
    labelled([shots[f] for f in CUTS], ['F%d' % f for f in CUTS], 2, 1,
             'cuts: into 4 (F995|996), no cut any more at F1072|1073 (one continuous shot), '
             'into 5 (F1147-1150), into 6 (F1301|1302)').save(os.path.join(a.out, 'cuts.png'))
    frames = [shots[f].resize((480, 320), Image.NEAREST) for f in range(SPAN[0], SPAN[1] + 1, 2)]
    durations = [30 if i % 3 else 40 for i in range(len(frames))]
    frames[0].save(os.path.join(a.out, 'preview.gif'), save_all=True, append_images=frames[1:],
                   duration=durations, loop=0)
    if a.wav_tool:
        subprocess.check_call([sys.executable, a.wav_tool, a.rom, os.path.join(a.out, 'preview.wav'),
                               '--skip', str(SPAN[0] - 1), '--frames', str(SPAN[1] - SPAN[0] + 1), '--small'])
    keys = labelled([shots[f] for f, _ in KEYS], ['%d. F%d %s' % (i, f, t) for i, (f, t) in enumerate(KEYS, 1)],
                    4, 2, 'Thunder Yellow opening, scenes 4-5 draft %s: the storm and THUNDERBOLT '
                          '(F995-1300, bars 4-7 of MUS_INTRO_FIGHT)' % a.label)
    strips = [labelled([shots[f] for f in range(f0, f1 + 1, 9)], ['F%d' % f for f in range(f0, f1 + 1, 9)],
                       9, 1, '%s, every 9th frame' % n) for n, (f0, f1) in (('scene 4', S4), ('scene 5', S5))]
    stack(keys, *strips).save(os.path.join(a.out, 'contact-sheet.png'))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
