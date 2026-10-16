"""Read-only decoding of existing game assets."""
from pathlib import Path
from functools import lru_cache
import hashlib,importlib.util,json,re,struct
from PIL import Image,ImageOps
import runtime
ROOT=Path(__file__).resolve().parents[2];REPO=runtime.repo_path(ROOT)
SOURCES={}
def source(rel):
 p=REPO/rel;SOURCES[rel]=hashlib.sha256(p.read_bytes()).hexdigest();return p
spec=importlib.util.spec_from_file_location('hoenn_gfx',runtime.gfx_path(ROOT));gfx=importlib.util.module_from_spec(spec);spec.loader.exec_module(gfx);gfx.ROOT=str(REPO)
headers='\n'.join(source(p).read_text(encoding='utf-8')for p in ['src/data/tilesets/graphics.h','src/data/tilesets/hoenn_graphics.h','src/graphics.c'])
DIRS={k:v for k,v in re.findall(r'gTilesetTiles_(\w+)\[\]\s*=\s*INCBIN_U32\("([^"]+)/tiles\.',headers)}
LAYOUTS={Path(r['blockdata_filepath']).parent.name:r for r in json.loads(source('data/layouts/layouts.json').read_text())['layouts']if r.get('blockdata_filepath')}
@lru_cache(maxsize=8)
def map_image(name):
 row=LAYOUTS[name];dirs=[DIRS[row[k].replace('gTileset_','')]for k in ['primary_tileset','secondary_tileset']]
 emerald=row['primary_tileset'].startswith('gTileset_Em');split=512 if emerald else 640;pal_split=6 if emerald else 7
 all_tiles=[];all_metas=[]
 for d in dirs:
  source(d+'/tiles.png');source(d+'/metatiles.bin');all_tiles.append(gfx.tiles(d+'/tiles.png'))
  raw=struct.unpack('<'+'H'*(len((REPO/d/'metatiles.bin').read_bytes())//2),(REPO/d/'metatiles.bin').read_bytes());all_metas.append([raw[i:i+8]for i in range(0,len(raw),8)])
 pals=[]
 for n in range(16):
  p=dirs[0 if n<pal_split else 1]+f'/palettes/{n:02d}.pal';pals.append(gfx.read_pal(str(source(p)))if(REPO/p).exists()else[(0,0,0)]*16)
 raw=source(row['blockdata_filepath']).read_bytes();blocks=struct.unpack('<'+'H'*(len(raw)//2),raw)
 im=Image.new('RGBA',(row['width']*16,row['height']*16),(0,0,0,255));px=im.load()
 for pos,b in enumerate(blocks):
  mid=b&1023;meta=all_metas[0][mid]if mid<split else all_metas[1][mid-split];by,bx=divmod(pos,row['width'])
  for layer in range(2):
   for q in range(4):
    entry=meta[layer*4+q];t=entry&1023;bank=entry>>12;hf=entry&1024;vf=entry&2048;tiles=all_tiles[0]if t<split else all_tiles[1];index=t if t<split else t-split
    assert 0<=index<len(tiles),(name,pos,mid,index,len(tiles));art=tiles[index]
    for y in range(8):
     for x in range(8):
      c=art[7-y if vf else y][7-x if hf else x]
      if c==0 and layer:continue
      px[bx*16+(q%2)*8+x,by*16+(q//2)*8+y]=(*pals[bank][c],255)
 return im
@lru_cache(maxsize=128)
def sprite(rel,frame=0,w=16,h=32,pal=None,flip=False):
 source(rel)
 if pal:source(pal)
 art=gfx.sprite(rel,frame,w,h,pal);return ImageOps.mirror(art)if flip else art
def field(name,n=0,direction='south',moving=False):
 paths={'red':('people/red_normal',16,32,None),'pika':('pokemon/pikachu',16,16,None),'birch':('hoenn/prof_birch',16,32,'hoenn/npc3'),'zigzagoon':('hoenn/enemy_zigzagoon',32,32,'hoenn/enemy_zigzagoon')}
 rel,w,h,pal=paths[name];table={'south':[0,3,0,4],'north':[1,5,1,6],'west':[2,7,2,8],'east':[2,7,2,8]};frame=table[direction][(n//8)%4 if moving else 0]
 return sprite('graphics/object_events/pics/'+rel+'.png',frame,w,h,'graphics/object_events/palettes/'+pal+'.pal'if pal else None,direction=='east')
def put(im,art,x,y):im.alpha_composite(art,(round(x),round(y)))
def foot(im,art,x,y):
 box=art.getbbox()
 if box:
  l,t,r,b=box;put(im,art,x-(l+r)/2,y-b)
if __name__=='__main__':raise SystemExit('Read-only asset module')
