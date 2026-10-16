import contextlib,io,runpy,sys,json,struct,hashlib,re
from pathlib import Path
with contextlib.redirect_stdout(io.StringIO()):
 env=runpy.run_path(sys.argv[1])
r=env['r'];rom=env['rom'];sy=env['sy'];ts=env['ts'];layouts=env['layouts']
def rb(a,n):
 q=a-0x08000000
 if q<0 or q+n>len(rom):raise ValueError('ROM pointer out of range: '+hex(a))
 return rom[q:q+n]
def ptr(a):return struct.unpack('<I',rb(a,4))[0]
g=json.loads((r/'data/maps/map_groups.json').read_text());order=g.get('group_order',[])
if not order or 'gMapGroups' not in sy:raise SystemExit('No actual group order/gMapGroups symbol. Do not guess indices.')
source=(r/'src/data/tilesets/graphics.h').read_text()+'\n'+(r/'src/data/tilesets/metatiles.h').read_text()
decl={m[1]:m[2] for m in re.finditer(r'\b(g[A-Za-z0-9_]+)\s*(?:\[[^\]]*\]\s*)+\s*=\s*(.*?);',source,re.S)}
assets={}
for name in ['gTileset_General','gTileset_Building','gTileset_VermilionCity','gTileset_PalletTown','gTileset_Lab','gTileset_RockTunnel']:
 f=ts[name];raw=rb(sy[name][0],24);values=struct.unpack_from('<IIIII',raw,4)
 expected=[f.get(k) for k in ('tiles','palettes','metatiles','callback','metatileAttributes')]
 rec={'flags':list(raw[:3]),'pointers':[],'assets':[]}
 for key,sym,a in zip(('tiles','palettes','metatiles','callback','metatileAttributes'),expected,values):
  rec['pointers'].append({'field':key,'symbol':sym,'rom':hex(a),'source_symbol_matches':None if sym not in sy else a==sy[sym][0]})
  if key=='callback':continue
  paths=re.findall(r'INCBIN_\w+\(\s*"([^"]+)"',decl.get(sym,''))
  if paths and all((r/p).exists() for p in paths):
   b=b''.join((r/p).read_bytes() for p in paths)
   rec['assets'].append({'field':key,'bytes':len(b),'source_paths':paths,'source_sha256':hashlib.sha256(b).hexdigest(),'rom_equal':rb(a,len(b))==b})
  else:rec['assets'].append({'field':key,'source_paths':paths,'rom_equal':None,'note':'No compiled INCBIN source found; do not claim comparison PASS'})
 assets[name]=rec
maps=[]
assert '/* 0x12 */ u16 mapLayoutId;' in (r/'include/global.fieldmap.h').read_text()
for name in ['JohtoCherrygroveAirstrip','JohtoRoute29','NewBarkTown','NewBarkTown_ElmsLab','MtMortar_1F']:
 try:
  m=json.loads((r/'data/maps'/name/'map.json').read_text());x=layouts[m['layout']]
  matches=[(i,gname,g[gname].index(name)) for i,gname in enumerate(order) if name in g.get(gname,[])]
  if len(matches)!=1:raise ValueError('Map not uniquely present in current group order')
  group,gname,num=matches[0];gp=ptr(sy['gMapGroups'][0]+4*group);mh=ptr(gp+4*num);lp=ptr(mh)
  layout_id=struct.unpack('<H',rb(mh+0x12,2))[0]
  table_layout=ptr(sy['gMapLayouts'][0]+4*(layout_id-1)) if layout_id else 0
  w,h,border,blocks,primary,secondary=struct.unpack('<6I',rb(lp,24));bw,bh=rb(lp+24,2)
  bb=(r/x['blockdata_filepath']).read_bytes();bd=(r/x['border_filepath']).read_bytes()
  maps.append({'map':name,'group':group,'number':num,'map_header':hex(mh),'layout_pointer':hex(lp),'layout_id':layout_id,'table_layout':hex(table_layout),'layout_id_matches_direct_pointer':table_layout==lp,'rom_dimensions':[w,h],'source_dimensions':[x['width'],x['height']],'rom_border_dimensions':[bw,bh],'source_border_dimensions':[x.get('border_width',2),x.get('border_height',2)],'dimensions_equal':(w,h)==(x['width'],x['height']),'primary_equal':primary==sy[x['primary_tileset']][0],'secondary_equal':secondary==sy[x['secondary_tileset']][0],'rom_blockdata_equal_source':rb(blocks,len(bb))==bb,'rom_border_equal_source':rb(border,len(bd))==bd})
 except Exception as e:maps.append({'map':name,'error':str(e)})
print(json.dumps({'rom_sha256':hashlib.sha256(rom).hexdigest(),'assets':assets,'maps':maps,'limitation':'Exact ROM/source links and data do not prove visual quality or runtime VRAM correctness.'},indent=2))
