from pathlib import Path
import importlib.util,hashlib,json,struct,numpy as np
root=Path('/workspaces/pokefirered');out=root/'outputs/opening-rom-v7';out.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('extend',root/'work/extend_opening_full_frlg.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);env=mod.load_renderer(root/'work/native-opening-v5/render_opening.py',root,out)
expected=json.loads((root/'outputs/opening-full-frlg-v7/validation.json').read_text());assert expected['frames']==752 and mod.sha(root/'work/native-opening-v5/render_opening.py')==mod.SOURCE_SHA
pool=bytearray();pals=bytearray();timeline=bytearray();pixelsmap={};palmap={};colors=[];maxcolors=0
for n in range(752):
 if n<585:im=env['render'](n)
 else:
  viewport=env['shot_sky_extended'](n-468)
  if n>736:viewport=env['wash'](viewport,(0,0,0),(n-736)/15)
  im=env['Image'].new('RGB',(240,160),(0,0,0));im.paste(viewport.convert('RGB'),(0,32))
 raw=im.tobytes();assert hashlib.sha256(raw).hexdigest()==expected['frame_sha256'][n],('source mismatch',n)
 a=np.frombuffer(raw,dtype=np.uint8).reshape(160,240,3);assert not np.any(a[:32]) and not np.any(a[128:]);a=a[32:128].astype(np.uint16);rgb=(a[:,:,0]>>3)|((a[:,:,1]>>3)<<5)|((a[:,:,2]>>3)<<10);u,ix=np.unique(rgb,return_inverse=True)
 if u[0]!=0:u=np.concatenate((np.array([0],dtype=np.uint16),u));ix+=1
 assert len(u)<=256,('frame colors exceed256',n,len(u));maxcolors=max(maxcolors,len(u));palette=np.zeros(256,dtype='<u2');palette[:len(u)]=u;pix=ix.astype(np.uint8).tobytes();pal=palette.tobytes();assert np.array_equal(palette[np.frombuffer(pix,dtype=np.uint8)].reshape(96,240),rgb)
 if pix not in pixelsmap:pixelsmap[pix]=len(pool);pool.extend(pix)
 if pal not in palmap:palmap[pal]=len(pals)//512;pals.extend(pal)
 timeline.extend(struct.pack('<IHH',pixelsmap[pix],palmap[pal],0));colors.append(len(u))
 if n in [0,135,211,288,441,518,584,736,751]:im.save(out/('approved-%04d.png'%n))
 if n%120==0:print('ENCODING',n,'pixel_pool',len(pool),'maxcolors',maxcolors,flush=True)
assert len(pool)+len(pals)+len(timeline)+15694620<=0x2000000
assets=root/'graphics/intro/opening_movie_v7';assert not assets.exists();assets.mkdir(parents=True);(assets/'pixels.8bpp').write_bytes(pool);(assets/'palettes.gbapal').write_bytes(pals);(assets/'frames.bin').write_bytes(timeline)
report={'pass':True,'frames':752,'source_all_frame_hashes_match':True,'rgb555_lossless':True,'max_colors':maxcolors,'unique_pixel_frames':len(pixelsmap),'unique_palettes':len(palmap),'bytes':{'pixels':len(pool),'palettes':len(pals),'timeline':len(timeline)},'original_source_sha256':mod.SOURCE_SHA,'reference_archive_sha256':expected['reference_archive_sha256'],'assets':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in assets.iterdir()},'rom_connected':False,'runtime_qa':False};(out/'encoding-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
