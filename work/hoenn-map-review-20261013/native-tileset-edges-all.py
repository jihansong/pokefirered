from pathlib import Path
import sys,json,struct,hashlib
root=Path('/workspaces/pokefirered');out=root/'work/hoenn-map-review-20261013/native-tileset-edges-all';out.mkdir(exist_ok=True)
rom=root/'pokemonthyl.gba';elf=root/'pokemonthyl.elf';sav=root/'saves/pokemonthyl_v1.25.sav'
sys.argv=['tile-edges-review','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
src=(root/'tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(src.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(src.split('\nresults=[];rows=[]\n')[0],'<verified-readonly-native>','exec'))
layouts={x['id']:x for x in json.loads((root/'data/layouts/layouts.json').read_text())['layouts'] if x}
results=[]
for name,mid in [('LittlerootTown',586),('RustboroCity_PokemonSchool',529)]:
 m=json.loads((root/'data/maps'/name/'map.json').read_text());l=layouts[m['layout']];raw=(root/l['blockdata_filepath']).read_bytes()
 coords=[(i%l['width'],i//l['width']) for i,(v,) in enumerate(struct.iter_unpack('<H',raw)) if v&1023==mid]
 assert coords; x,y=coords[0];p=out/(name+'-QA-only.sav');s=SaveFile(str(sav));s.warp(name,x,y);s.save(str(p))
 with ReadOnlyEmu(str(rom),str(p),sym='') as e:
  e.syms=syms;e.boot_continue();e.run(240);e.shot(str(out/(name+'.png')))
  if name=='LittlerootTown':
   native=e.read(e.sym('gPlttBufferUnfaded')+14*32,32);declared=r.at(syms['gTilesetPalettes_EmPetalburg']+14*32,32)
   metatile=r.at(syms['gMetatiles_EmPetalburg']+(mid-512)*16,16)
   paletteused=[]
   metatile=b''.join(r.at(syms['gMetatiles_EmPetalburg']+(k-512)*16,16) for k in [586,587])
   for (entry,) in struct.iter_unpack('<H',metatile):
    if entry>>12==14:
     tileid=entry&1023;data=e.read(0x06000000+tileid*32,32);nibs={v for b in data for v in [b&15,b>>4] if v}
     paletteused.append({'tile':tileid,'nonzero_pixels':len(nibs),'color_indices':sorted(nibs),'palette_colors_match':all(struct.unpack_from('<H',native,k*2)==struct.unpack_from('<H',declared,k*2) for k in nibs)})
   row={'map':name,'mid':mid,'coords':coords[:8],'native_palette14':list(struct.unpack('<16H',native)),'declared_palette14':list(struct.unpack('<16H',declared)),'tiles':paletteused,'actual_visible_colors_match':all(x['palette_colors_match'] for x in paletteused)}
  else:
   tiles={k:e.read(0x06000000+k*32,32).hex() for k in [791,792,793]};row={'map':name,'mid':mid,'coords':coords[:8],'native_vram_tiles':tiles,'all_zero_transparent':all(set(bytes.fromhex(v))=={0} for v in tiles.values())}
  row.update(location=e.location(),reset=e.reset_seen(),black_fraction=e.black_fraction(),readonly_memory=True);results.append(row)
res={'rom_sha256':digest(rom.read_bytes()),'cases':results,'input_sav_unchanged':digest(sav.read_bytes())=='53d923bf4668373724b19c9d3c8526b002701606ab7ac082d657ee990e23d7b3'}
(out/'validation.json').write_text(json.dumps(res,indent=2));print(json.dumps(res))
