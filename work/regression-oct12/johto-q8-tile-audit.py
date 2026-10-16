import json, struct, hashlib, re
from pathlib import Path
r=Path('/workspaces/pokefirered'); rom=(r/'pokemonthyl.gba').read_bytes(); elf=(r/'pokemonthyl.elf').read_bytes()
h=struct.unpack_from('<16sHHIIIIIHHHHHH',elf,0)
assert h[0][:6]==b'\x7fELF\x01\x01'
segments=[]
for j in range(h[10]):
 p=struct.unpack_from('<IIIIIIII',elf,h[5]+j*h[9]); t,o,v,a,n=p[:5]
 if t==1 and n and 0x08000000<=a<0x0A000000:
  q=a-0x08000000; segments.append({'address':hex(a),'bytes':n,'equal':rom[q:q+n]==elf[o:o+n]})
assert segments and all(x['equal'] for x in segments), 'ELF does not match actual GBA'
ss=[struct.unpack_from('<IIIIIIIIII',elf,h[6]+j*h[11]) for j in range(h[12])]; sy={}
for s in ss:
 if s[1]!=2:continue
 z=ss[s[6]]; strings=elf[z[4]:z[4]+z[5]]
 for p in range(s[4],s[4]+s[5],s[9] or 16):
  n,a,size,info,other,idx=struct.unpack_from('<IIIBBH',elf,p)
  name=strings[n:strings.find(b'\x00',n)].decode(errors='replace')
  if name:sy[name]=(a,size)
def data(sym):
 a,n=sy[sym]
 if not n:n=min([v for v,z in sy.values() if a<v<0x0A000000])-a
 q=a-0x08000000; assert q>=0 and q+n<=len(rom),sym
 return rom[q:q+n]
def lz(b):
 assert b[0]==16; out=bytearray(); n=int.from_bytes(b[1:4],'little'); p=4
 while len(out)<n:
  f=b[p];p+=1
  for k in range(7,-1,-1):
   if len(out)>=n:break
   if f&(1<<k):
    v=b[p]*256+b[p+1];p+=2;d=(v&4095)+1; assert d<=len(out)
    for j in range((v>>12)+3):
     out.append(out[-d])
     if len(out)>=n:break
   else:out.append(b[p]);p+=1
 return out
hdr=(r/'src/data/tilesets/headers.h').read_text(); ts={}
for m in re.finditer(r'const\s+struct\s+Tileset\s+(gTileset_\w+)\s*=\s*\{(.*?)\};',hdr,re.S):
 ts[m[1]]=dict(re.findall(r'\.(\w+)\s*=\s*([A-Za-z_][A-Za-z_0-9]*)',m[2]))
cache={}
def get(name):
 if name not in cache:
  f=ts[name]; b=data(f['tiles']); b=lz(b) if f.get('isCompressed')=='TRUE' else b
  mt=data(f['metatiles']);at=data(f['metatileAttributes']);pal=data(f['palettes'])
  cache[name]={'tiles':len(b)//32,'metatiles':len(mt)//16,'attributes':len(at)//4,'palettes':len(pal)//32,'emerald':f.get('isEmerald')=='TRUE','callback':f.get('callback'),'mt':mt}
 return cache[name]
j=json.loads((r/'data/layouts/layouts.json').read_text()); rows=j.get('layouts',[]) if isinstance(j,dict) else j
layouts={x.get('id'):x for x in rows if isinstance(x,dict) and x.get('id')}
g=json.loads((r/'data/maps/map_groups.json').read_text()); names=['JohtoCherrygroveAirstrip','JohtoRoute29','NewBarkTown','NewBarkTown_ElmsLab','MtMortar_1F']
for key,value in g.items():
 if 'johto' in key.lower() and isinstance(value,list):names.extend(v for v in value if isinstance(v,str))
out=[]
for name in dict.fromkeys(names):
 try:
  m=json.loads((r/'data/maps'/name/'map.json').read_text()); x=layouts[m['layout']];p=get(x['primary_tileset']);s=get(x['secondary_tileset']);split=512 if p['emerald'] else 640
  blocks=(r/x['blockdata_filepath']).read_bytes();border=(r/x['border_filepath']).read_bytes();cells=blocks+border; used=sorted(set(v&1023 for v in struct.unpack('<%dH'%(len(cells)//2),cells)))
  bad=[];gaps=set();banks=set()
  for v in used:
   source,i=(p,v) if v<split else (s,v-split)
   if i>=source['metatiles']:bad.append(v);continue
   for w in struct.unpack_from('<8H',source['mt'],i*16):
    t=w&1023;b=w>>12
    if not ((t<split and t<p['tiles']) or (t>=split and t-split<s['tiles'])):gaps.add((v,t))
    if b>=13:banks.add((v,b))
  out.append({'map':name,'layout':m['layout'],'primary':x['primary_tileset'],'secondary':x['secondary_tileset'],'dimensions':[x['width'],x['height']],'block_size_ok':len(blocks)==x['width']*x['height']*2,'metatile_ids':used,'invalid_metatiles':bad,'beyond_initial_tile_upload':sorted(gaps),'palette_banks_outside_0_12':sorted(banks),'warning':'Callbacks can upload animated tiles. Initial tile gaps alone do not prove corruption.'})
 except Exception as e:out.append({'map':name,'error':str(e)})
print(json.dumps({'rom_sha256':hashlib.sha256(rom).hexdigest(),'elf_sha256':hashlib.sha256(elf).hexdigest(),'elf_rom_segments':segments,'tilesets':{k:{a:b for a,b in v.items() if a!='mt'} for k,v in cache.items()},'maps':out,'limitation':'Does not prove rendered frames or complete gameplay.'},indent=2))
