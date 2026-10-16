"""Integrate imagegen's edited occiput only; preserve all other game pixels."""
from pathlib import Path
from PIL import Image
import hashlib, importlib.util, json, sys

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'misty-standard-20261014/phase-m0.3/misty_companion_season1.png'
spec = importlib.util.spec_from_file_location('gba_format', ROOT.parent / 'misty-standard-20261014/normalize_native_v5.py')
fmt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fmt)
source = Path(sys.argv[1])
out = ROOT / sys.argv[2]
out.mkdir(exist_ok=False)
assert hashlib.sha256(BASE.read_bytes()).hexdigest() == '1c8a8636dd35248d5d38395d6c5ceae78780b585796c4d3ee297c124fa77cb07'
original = Image.open(BASE)
generated = Image.open(source).convert('RGBA')
assert generated.width / generated.height == 1.5, generated.size
# One common logical grid, nearest sampling and existing 16-color game palette.
strip = fmt.indexed(generated.resize((48,32), Image.Resampling.NEAREST))
rect = (9,17,14,24)
native = original.copy()
source_x = int(sys.argv[3]) if len(sys.argv)>3 else rect[0]
source_rect = (source_x,rect[1],source_x+rect[2]-rect[0],rect[3])
patch = strip.crop(source_rect)
for frame in [2,7,8]:
    native.paste(patch, (frame*16+rect[0], rect[1]))
native.info['transparency'] = 0
native.save(out/'misty_companion_season1.png', transparency=0, bits=4, optimize=False)
encoded = fmt.encode_4bpp(native)
assert len(encoded) == 2304
assert fmt.decode_4bpp(encoded).tobytes() == native.tobytes()
(out/'misty_companion_season1.4bpp').write_bytes(encoded)
changes = []
for frame in range(9):
    a = original.crop((frame*16,0,(frame+1)*16,32))
    b = native.crop((frame*16,0,(frame+1)*16,32))
    pixels = [(x,y) for y in range(32) for x in range(16) if a.getpixel((x,y))!=b.getpixel((x,y))]
    assert not pixels or frame in [2,7,8]
    assert all(rect[0]<=x<rect[2] and rect[1]<=y<rect[3] for x,y in pixels)
    bbox = b.convert('RGBA').getbbox()
    assert 18 <= bbox[3]-bbox[1] <= 19
    changes.append({'frame':frame, 'changed_pixels':len(pixels), 'bbox':bbox})
rear = []
for y in range(18,24):
    visible = [x for x in range(16) if native.getpixel((2*16+x,y)) != 0]
    rear.append(max(visible))
report = {'stage':'DRAFT_REQUIRES_VISUAL_AND_NATIVE_ROM_REVIEW',
          'tool_mode':'built-in image_gen', 'source':str(source),
          'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'source_size':generated.size, 'native_grid':[48,32],
          'source_patch_frame':0,'source_patch_rectangle':source_rect,'patch_rectangle':rect,
          'posterior_patch_registration_offset_x':rect[0]-source_x,
          'same_generated_rear_patch_in_frames':[2,7,8],
          'unchanged_frames':[0,1,3,4,5,6],
          'all_other_pixels_byte_identical':True,
          'rear_silhouette_rows18_to23':rear,'frames':changes,
          'png_sha256':hashlib.sha256((out/'misty_companion_season1.png').read_bytes()).hexdigest(),
          'four_bpp_sha256':hashlib.sha256(encoded).hexdigest(),
          'palette_source':'existing PLAYER palette','roundtrip_4bpp':True}
(out/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
review = Image.new('RGBA',(48,64),(224,232,224,255))
for col,frame in enumerate([2,7,8]):
    review.alpha_composite(original.crop((frame*16,0,(frame+1)*16,32)).convert('RGBA'),(col*16,0))
    review.alpha_composite(native.crop((frame*16,0,(frame+1)*16,32)).convert('RGBA'),(col*16,32))
review.resize((768,1024),Image.Resampling.NEAREST).save(out/'before-top-after-bottom-16x.png')
print(json.dumps(report,indent=2))
