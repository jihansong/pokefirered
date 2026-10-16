from pathlib import Path
from PIL import Image
import base64,hashlib,io,json,struct
PNG_B64='''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'''
def sha(b):return hashlib.sha256(b).hexdigest()
png=base64.b64decode(PNG_B64);assert sha(png)=='210bd8b8c196cb83ce25fb35bc8affc0869743bd4a760b4be9fc90047a9ea438','PNG transport mismatch'
im=Image.open(io.BytesIO(png));assert im.mode=='P'and im.size==(96,96)and im.info.get('transparency')==0
indices=list(im.getdata());assert set(indices)==set(range(16))
palette=bytes.fromhex('0000210cc620292df762ff7b3f4f3a36ea4cd375d97e5320dc38df550855252a');assert sha(palette)=='02951ab3bc6bd04dbce501258a13e92e3ba934728bb8249514b41238f835b792'
PIECES=((0,0,64,64,0),(64,0,32,64,64),(0,64,64,32,96),(64,64,32,32,128));raw=bytearray()
for x,y,w,h,off in PIECES:
 assert len(raw)==off*32
 for ty in range(y,y+h,8):
  for tx in range(x,x+w,8):
   for row in range(8):
    for col in range(0,8,2):at=(ty+row)*96+tx+col;raw.append(indices[at]|indices[at+1]<<4)
assert len(raw)==4608 and sha(raw)=='99f3ff74b5438521ba48e4d7fc403acca7df233f003878ddd525bdba8ab14add'
decoded=[None]*9216
for x,y,w,h,off in PIECES:
 p=off*32
 for ty in range(y,y+h,8):
  for tx in range(x,x+w,8):
   for row in range(8):
    for col in range(0,8,2):
     at=(ty+row)*96+tx+col;assert decoded[at]is None and decoded[at+1]is None;decoded[at],decoded[at+1]=raw[p]&15,raw[p]>>4;p+=1
assert decoded==indices
colours=[tuple(((v>>s)&31)*8 for s in(0,5,10))for v,in struct.iter_unpack('<H',palette)];rgba=b''.join(bytes(colours[i])+(b'\xff'if i else b'\x00')for i in decoded);assert rgba==im.convert('RGBA').tobytes();assert sha(rgba)=='506d49907b4e10670ea2a54d073160893d1de5256eb362cb9b93036179d55c3a'
out=Path('outputs/rocket-art-v10-96-preview');assert not out.exists();out.mkdir(parents=True)
(out/'jessie-james-v10-96.png').write_bytes(png);im.convert('RGBA').resize((576,576),Image.Resampling.NEAREST).save(out/'jessie-james-v10-6x.png');(out/'jessie_james_hires.4bpp').write_bytes(raw);(out/'jessie_james_hires.gbapal').write_bytes(palette)
report=dict(status='EXISTING_V4_NATIVE_96_REVIEW_CANDIDATE',source_sha256='40e5a18ea80e4ba71192f0738ef4208073fb6286d6a3080c68a35e496ce98c8f',source_size=[1254,1254],source_crop=[81,112,1175,1196],fit_size=[94,93],offset=[1,2],native_size=[96,96],resampling='NEAREST directly from high-resolution v4, not 64px enlargement',source_art_redrawn=False,source_unchanged_verified_locally=True,ratio_or_pose_intentionally_changed=False,native_eye_edits=[[56,18,2,14],[62,17,10,14]],cleanup_changed_pixels=2,silhouette_changed_by_cleanup=False,opaque_pixels=sum(i!=0 for i in indices),opaque_colours=15,png_sha256=sha(png),packed_sha256=sha(raw),packed_bytes=len(raw),decoded_pixel_mismatches=0,new_original_art=False,rom_integrated=False,hires_feature_enabled=False,game_visual_QA='pending',user_review='pending')
(out/'validation.json').write_text(json.dumps(report,indent=2));print('ROCKET96_MATERIALIZED',json.dumps(report))
