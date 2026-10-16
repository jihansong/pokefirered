from pathlib import Path
import sys,struct,json,subprocess,hashlib,re
r=Path('/workspaces/pokefirered');o=r/'work/hoenn-map-review-20261013'
sys.path.insert(0,str(r/'tools/qa'));from gamedata import Rom
rom=Rom(str(r/'pokemonthyl.gba'));table=subprocess.check_output(['/opt/devkitpro/devkitARM/bin/arm-none-eabi-objdump','-t',str(r/'pokemonthyl.elf')],text=True)
symbols={};sizes={}
for line in table.splitlines():
 v=line.split()
 if len(v)>=5 and re.fullmatch('[0-9a-fA-F]{8}',v[0]) and re.fullmatch('[0-9a-fA-F]+',v[-2]):
  addr=int(v[0],16);size=int(v[-2],16);symbols[v[-1]]=(addr,size)
  if size and 'O' in v:sizes[addr]=max(size,sizes.get(addr,0))
layouts={x['id']:x for x in json.loads((r/'data/layouts/layouts.json').read_text())['layouts'] if x}
maps=json.loads((o/'manifest.json').read_text())['maps'];problems=[];rows=[];cache={};palette_edges=[];graphics_edges=[]
def tileset(name):
 if name in cache:return cache[name]
 address=rom.syms[name];b=rom.at(address,24);comp,secondary,emerald=b[:3];gfx,pal,mt,cb,attr=struct.unpack_from('<5I',b,4)
 assert comp==1 and emerald==1,(name,'not imported Emerald')
 assert all(0x08000000<=p<0x0a000000 for p in [gfx,pal,mt,attr])
 mtbytes=sizes[mt];atbytes=sizes[attr];assert mtbytes%16==0 and atbytes==mtbytes//16*4,(name,'metatile attributes length')
 lz=rom.at(gfx,4);assert lz[0]==0x10;expanded=int.from_bytes(lz[1:4],'little');assert expanded%32==0
 data={'address':address,'count':mtbytes//16,'tiles':expanded//32,'secondary':secondary,'emerald':emerald,'metatiles':rom.at(mt,mtbytes),'palette_bytes':sizes[pal]}
 cache[name]=data;return data
for mapname in maps:
 try:
  m=json.loads((r/'data/maps'/mapname/'map.json').read_text());l=layouts[m['layout']];p=tileset(l['primary_tileset']);s=tileset(l['secondary_tileset'])
  assert p['secondary']==0 and s['secondary']==1
  addr=rom.syms[l['name']];raw=rom.at(addr,28);w,h,bd,grid,prim,sec=struct.unpack_from('<6I',raw)
  assert [w,h,prim,sec,raw[24],raw[25]]==[l['width'],l['height'],p['address'],s['address'],l['border_width'],l['border_height']]
  gridbytes=rom.at(grid,w*h*2);bdbytes=rom.at(bd,raw[24]*raw[25]*2)
  assert gridbytes==(r/l['blockdata_filepath']).read_bytes() and bdbytes==(r/l['border_filepath']).read_bytes()
  used={v[0]&1023 for v in struct.iter_unpack('<H',gridbytes+bdbytes)}
  for mid in used:
   ts=p if mid<512 else s;index=mid if mid<512 else mid-512
   assert index<ts['count'],(mapname,'metatile id outside array',mid,ts['count'])
   for (tile,) in struct.iter_unpack('<H',ts['metatiles'][index*16:(index+1)*16]):
    tileid=tile&1023;palette=tile>>12
    if palette>=13:palette_edges.append({'map':mapname,'mid':mid,'tile':tileid,'palette':palette})
    if tileid>=(p['tiles'] if tileid<512 else 512+s['tiles']):graphics_edges.append({'map':mapname,'mid':mid,'tile':tileid,'palette':palette})
  rows.append({'map':mapname,'layout':l['id'],'width':w,'height':h,'used_metatiles':len(used),'pass':True})
 except Exception as ex:problems.append({'map':mapname,'error':repr(ex)})
result={'rom_sha256':hashlib.sha256(rom.data).hexdigest(),'pass':not problems,'maps_checked':len(rows),'maps_expected':len(maps),'tilesets':len(cache),'failures':problems,'checks':['ROM layout pointers/flags match source','map and border ROM bytes equal source','Emerald512 split','metatile bounds','u32 attribute array lengths','tile graphics and palette bounds'],'maps':rows,'palette_edges':palette_edges,'graphics_edges':graphics_edges}
(o/'rom-tileset-structural-audit-v2.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='maps'}))
