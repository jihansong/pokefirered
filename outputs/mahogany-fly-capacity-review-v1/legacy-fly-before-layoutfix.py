#!/usr/bin/env python3
"""Native legacy all-visited Fly allocation audit; original SAV is read-only."""
from pathlib import Path
import hashlib,sys
legacy_region=None
if '--legacy-region' in sys.argv:
 i=sys.argv.index('--legacy-region');assert i+1<len(sys.argv)
 legacy_region=sys.argv.pop(i+1);sys.argv.pop(i)
 assert legacy_region in ['kanto','sevii123','sevii45','sevii67','hoenn']
base=Path('tools/qa/native_fly_region_qa.py')
source_text=base.read_text()
expected='c99fcc261c0354689d53f3c7d3f285c4eb45056cf0c700255f6841fe4028f2e8'
assert hashlib.sha256(source_text.encode()).hexdigest()==expected,'Fly QA source guard changed'
marker='\ne=None\ntry:'
assert source_text.count(marker)==1
prefix,tail=source_text.split(marker,1)
# Extend only this wrapper's host-compiled private ABI, not the 21-case QA.
old="names=['MapCursor','FlyMap','MapIconSprite','MapIcons','RegionMap']"
new="names=['MapCursor','FlyMap','MapIconSprite','MapIcons','RegionMap','HoennFlyDestination']"
assert prefix.count(old)==1;prefix=prefix.replace(old,new,1)
old="('region.selected','RegionMap','selectedRegion'),('sprite.size','Sprite',None)]"
new="('region.selected','RegionMap','selectedRegion'),('region.type','RegionMap','type'),('region.permissions','RegionMap','permissions'),('sprite.size','Sprite',None),('layout.width','MapLayout','width'),('layout.height','MapLayout','height'),('layout.map','MapLayout','map'),('hoenn_destination.size','HoennFlyDestination',None),('hoenn_destination.flag','HoennFlyDestination','visitedFlag')]"
assert prefix.count(old)==1;prefix=prefix.replace(old,new,1)
old="section_names=['MAPSEC_NEW_BARK_TOWN'"
new="section_names=['KANTO_MAPSEC_START','MAPSEC_NONE','MAPSEC_NEW_BARK_TOWN'"
assert prefix.count(old)==1;prefix=prefix.replace(old,new,1)
old="for token in ['REGIONMAP_KANTO','MAPPERM_COUNT']:"
new="for token in ['REGIONMAP_KANTO','MAPPERM_COUNT','LAYER_COUNT']:"
assert prefix.count(old)==1;prefix=prefix.replace(old,new,1)
old=" fields.extend([('section.'+n,None,None) for n in section_names])"
new=""" for layout in Path('src/data/region_map').glob('region_map_layout_*.h'):
  section_names.extend(re.findall(r'\\bMAPSEC_[A-Z0-9_]+\\b',layout.read_text()))
 section_names.extend(['REGIONMAP_TYPE_FLY','MAPPERM_HAS_SWITCH_BUTTON','LAYER_MAP','LAYER_DUNGEON','LAYER_COUNT'])
 section_names=list(dict.fromkeys(section_names))
 fields.extend([('section.'+n,None,None) for n in section_names])"""
assert prefix.count(old)==1;prefix=prefix.replace(old,new,1)
old='c=\'#include "global.h"\\n#include "gflib.h"'
new='c=\'#include "region_map.h"\\n#include "global.h"\\n#include "gflib.h"'
assert prefix.count(old)==1;prefix=prefix.replace(old,new,1)
exec(compile(prefix,str(base),'exec'))
assert a.case in ['kanto-on','hoenn-on'],'use only independent legacy all-visited cases'
legacy_region=legacy_region or ('hoenn' if a.case=='hoenn-on' else 'kanto')
assert (a.case=='hoenn-on')==(legacy_region=='hoenn'),'Hoenn needs --case hoenn-on; others kanto-on'
SELECTED={
 'kanto':('REGIONMAP_KANTO',('PalletTown',11,18),'MAPSEC_PALLET_TOWN','kanto',13),
 'sevii123':('REGIONMAP_SEVII123',('OneIsland',8,14),'MAPSEC_ONE_ISLAND','sevii_123',3),
 'sevii45':('REGIONMAP_SEVII45',('FiveIsland',18,8),'MAPSEC_FIVE_ISLAND','sevii_45',2),
 'sevii67':('REGIONMAP_SEVII67',('SevenIsland',12,5),'MAPSEC_SEVEN_ISLAND','sevii_67',2),
 'hoenn':('REGIONMAP_HOENN',('SlateportCity',32,12),'MAPSEC_SLATEPORT_CITY','hoenn',24)}
selected_name,origin,target_section,layout_suffix,expected_fly_count=SELECTED[legacy_region]
expected_region=REGIONS.index(selected_name)
if legacy_region!='hoenn':target_cell=(sections[target_section]['x'],sections[target_section]['y'])
report.update(legacy_selected_region=selected_name,legacy_total_fly_cells_over_five_maps=44,
 original_44_destination_requirement_retained=True)
report.update(mode='native-legacy-Fly-all-visited-allocation',legacy_all_visited=True,
 existing_21_cases_changed=False,full_campaign_measured=False,actual_device_fps_measured=False)
setup_end="  initial_flags={f:blocks(e).flag(f) for f in flags}\n"
assert tail.count(setup_end)==1
setup=tail.split(setup_end,1)[0]+setup_end
old="  if key=='all-visited':\n"
assert setup.count(old)==1
setup=setup.replace(old,"  if True:\n",1)
world_anchor="  if region=='kanto':s.set_flag('FLAG_WORLD_MAP_PALLET_TOWN',True)\n"
assert setup.count(world_anchor)==1
hoenn_fixture=r"""
  s.set_flag('FLAG_SYS_SEVII_MAP_123',True);s.set_flag('FLAG_SYS_SEVII_MAP_4567',True)
  if legacy_region=='sevii123':s.set_var('VAR_MAP_SCENE_ONE_ISLAND_HARBOR',3)
  if legacy_region.startswith('sevii'):
   mn,px,py=origin;meta=json.loads(Path('data/maps',mn,'map.json').read_text())
   layouts=json.loads(Path('data/layouts/layouts.json').read_text())['layouts']
   layout=next(v for v in layouts if v['id']==meta['layout'])
   raw=Path(layout['blockdata_filepath']).read_bytes();mw=layout['width'];mh=layout['height']
   word=struct.unpack_from('<H',raw,2*(py*mw+px))[0]
   assert 0<=px<mw and 0<=py<mh and word&0xc00==0 and word>>12==3,'Sevii origin not free land'
   assert meta['region_map_section']==target_section
   for event in meta.get('warp_events',[])+meta.get('coord_events',[]):
    assert (int(event['x']),int(event['y']))!=(px,py),'Sevii origin is event tile'
   for event in meta.get('object_events',[]):
    rx=int(event.get('movement_range_x',0));ry=int(event.get('movement_range_y',0))
    assert not (abs(int(event['x'])-px)<=rx and abs(int(event['y'])-py)<=ry),'Sevii origin overlaps object range'
   lid=const(meta['layout']);assert lid>0
   ptr=struct.unpack('<I',r.at(syms['gMapLayouts']+(lid-1)*4,4))[0]
   nw=struct.unpack('<I',r.at(ptr+ABI['layout.width'],4))[0]
   nh=struct.unpack('<I',r.at(ptr+ABI['layout.height'],4))[0]
   data=struct.unpack('<I',r.at(ptr+ABI['layout.map'],4))[0]
   actual=struct.unpack('<H',r.at(data+2*(py*nw+px),2))[0]
   assert (nw,nh,actual)==(mw,mh,word),'Sevii source/candidate origin differs'
   report['sevii_origin_guard']={'map':mn,'x':px,'y':py,'native_raw_word':actual,
    'source_raw_word':word,'source_layout_sha256':sha(raw),'compiled_geometry_pass':True}
  # The destinations use flags_hoenn_map.h, which the old two-file regex missed.
  dest_source=Path('src/data/region_map/fly_destinations_hoenn.h').read_text()
  hoenn_flags=sorted(set(re.findall(r',\s*(FLAG_HOENN_WORLD_MAP_[A-Z0-9_]+)\s*\}',dest_source)))
  assert len(hoenn_flags)==18,('native Hoenn destination source changed',hoenn_flags)
  resolved={const(name) for name in hoenn_flags};assert len(resolved)==18
  stride=ABI['hoenn_destination.size'];fo=ABI['hoenn_destination.flag']
  count=ABI['section.KANTO_MAPSEC_START']
  assert 0<fo and fo+2<=stride and 0<count<256
  compiled=r.at(syms['sHoennFlyDestinations'],count*stride)
  assert len(compiled)==count*stride,'candidate Hoenn destination table out of ROM'
  ids=[struct.unpack_from('<H',compiled,i*stride+fo)[0] for i in range(count)]
  assert {v for v in ids if v}==resolved,'source/compiled Hoenn visited flags differ'
  for name in hoenn_flags:s.set_flag(name,True)
  assert all(s.flag(name) for name in hoenn_flags),'all-visited Hoenn fixture flag not set'
  region_source=Path('src/region_map.c').read_text()
  height=int(re.search(r'#define\s+MAP_HEIGHT\s+(\d+)\b',region_source).group(1))
  width=int(re.search(r'#define\s+HOENN_MAP_WIDTH\s+(\d+)\b',region_source).group(1))
  grid=r.at(syms['sRegionMapSections_Hoenn'],height*width)
  layout_source=Path('src/data/region_map/region_map_layout_hoenn.h').read_text()
  assert re.search(r'static\s+const\s+u8\s+sRegionMapSections_Hoenn\s*\[',layout_source),'candidate Hoenn grid is not native u8'
  none=ABI['section.MAPSEC_NONE']
  invalid=sorted(set(v for v in grid if v!=none and not 0<=v<count))
  report['hoenn_grid_audit']={'width':width,'height':height,'mapsec_none':none,
   'empty_cells':grid.count(none),'invalid_nonempty_sections':invalid,'native_u8':True}
  assert len(grid)==height*width and not invalid,('candidate Hoenn nonempty map grid out of bounds',report['hoenn_grid_audit'])
  eligible=sum(bool(ids[v]) for v in grid if v!=none)
  assert eligible==24,('candidate Hoenn visited-cell oracle changed',eligible)
  report['all_visited_fixture']={'hoenn_flags':hoenn_flags,'compiled_hoenn_flag_ids':sorted(resolved),
   'compiled_table_stride':stride,'compiled_flag_offset':fo,'compiled_hoenn_eligible_cells':eligible,
   'source_destination_sha256':sha(dest_source.encode()),'all_declared_flags_set':True}
"""
setup=setup.replace(world_anchor,"  s.set_flag('FLAG_SYS_CAN_LINK_WITH_RS',True)\n"+hoenn_fixture+world_anchor,1)
body=r"""
  def regional_flags():
   b=blocks(e);f=off('sb1.flags');end=off('sb1.vars')
   t=off('sb2.hoennTrainerFlags');h=off('sb2.hoennFlags');v=off('sb2.hoennVars')
   assert 0<f<end<=len(b.sb1) and 0<t<h<v<=len(b.sb2)
   return bytes(b.sb1[f:end]),bytes(b.sb2[t:h]),bytes(b.sb2[h:v])
  def definition(code,name):
   m=re.search(r'static u8 '+name+r'\([^;{}]*\)\s*\{',code);assert m,name
   p=m.end();depth=1;q=p
   while depth:
    depth+=(code[q]=='{')-(code[q]=='}');q+=1
   return code[p:q-1]
  assert all(blocks(e).flag(name) for name in hoenn_flags),'all Hoenn flags not preserved through cold boot'
  report['all_visited_fixture']['native_cold_flags_confirmed']=True
  # Native source+compiled layout is the oracle; every visited visible cell must get an icon.
  layout_source=Path('src/data/region_map/region_map_layout_'+layout_suffix+'.h').read_text()
  decl=re.search(r'static\s+const\s+u8\s+(sRegionMapSections_[A-Za-z0-9_]+)\s*\[',layout_source);assert decl
  symbol=decl.group(1);width_name='HOENN_MAP_WIDTH' if legacy_region=='hoenn' else 'MAP_WIDTH'
  w=int(re.search(r'#define\s+'+width_name+r'\s+(\d+)\b',region_source).group(1))
  n=height*w;layers=ABI['section.LAYER_COUNT'];assert layers==2
  layout_bytes=r.at(syms[symbol],layers*n);assert len(layout_bytes)==layers*n
  none=ABI['section.MAPSEC_NONE']
  fly_grid=layout_bytes[ABI['section.LAYER_MAP']*n:(ABI['section.LAYER_MAP']+1)*n]
  dungeon_grid=layout_bytes[ABI['section.LAYER_DUNGEON']*n:(ABI['section.LAYER_DUNGEON']+1)*n]
  allowed={ABI['section.'+name] for name in re.findall(r'\bMAPSEC_[A-Z0-9_]+\b',layout_source)}
  assert all(v in allowed for v in layout_bytes),'native grid contains source-unknown section'
  visitor={}
  fn=definition(region_source,'GetMapsecType')
  for m in re.finditer(r'case\s+(MAPSEC_[A-Z0-9_]+)\s*:(.*?)(?=\bcase\s+|\bdefault\s*:|$)',fn,re.S):
   flag=re.search(r'return\s+FlagGet\((FLAG_[A-Z0-9_]+)\)\s*\?',m.group(2))
   if flag:visitor[ABI['section.'+m.group(1)]]=flag.group(1)
  if legacy_region=='hoenn':expected_cells=[i for i,v in enumerate(fly_grid) if v!=none and ids[v] and blocks(e).flag(next(k for k in hoenn_flags if const(k)==ids[v]))]
  else:expected_cells=[i for i,v in enumerate(fly_grid) if v in visitor and blocks(e).flag(visitor[v])]
  assert len(expected_cells)==expected_fly_count,('full selected-map Fly oracle differs',legacy_region,len(expected_cells),expected_fly_count)
  cave=ABI.get('section.MAPSEC_CERULEAN_CAVE')
  expected_dungeon=sum(v!=none and not (v==cave and not blocks(e).flag('FLAG_SYS_CAN_LINK_WITH_RS')) for v in dungeon_grid)
  report['selected_map_oracle']={'region':selected_name,'native_width':w,'native_height':height,
   'visited_fly_cells':len(expected_cells),'dungeon_cells':expected_dungeon,
   'compiled_layout_sha256':sha(layout_bytes),'empty_section':none,'source_decl_u8':True}
  flags_before=regional_flags();start_party();await_state(fly_ready,4000);e.run(2)
  rp=e.ptr('sRegionMap');assert e.u8(rp+ABI['region.selected'])==expected_region
  assert e.u8(rp+ABI['region.type'])==ABI['section.REGIONMAP_TYPE_FLY'],'wrong native map UI type'
  assert e.u8(rp+ABI['region.permissions']+ABI['section.MAPPERM_HAS_SWITCH_BUTTON'])==0,'native Fly unexpectedly has map switching'
  move_cursor_to(target_cell);c=cursor()
  assert c['mapsec']==ABI['section.'+target_section] and c['type']==TYPES.index('MAPSECTYPE_VISITED')
  allocation=icon_snapshot();photo(e,'legacy-selected-all-visited-Fly-icons')
  maximum=int(re.search(r'#define\s+MAX_SPRITES\s+(\d+)',Path('include/sprite.h').read_text()).group(1));assert maximum==64
  records=allocation['fly']+allocation['dungeon'];pointers=[v['sprite'] for v in records]
  assert len(pointers)==len(set(pointers)),'Fly/dungeon records alias a native sprite'
  active=sum(bool(e.u8(syms['gSprites']+i*ABI['sprite.size']+0x3e)&1) for i in range(maximum))
  assert len(pointers)<=active<=maximum
  assert all(v['region']==expected_region for v in records),'Fly still allocates hidden foreign icons'
  assert all(not(e.u8(syms['gSprites']+v['sprite']*ABI['sprite.size']+0x3e)&4) for v in records),'selected-region icon is invisible'
  assert len(allocation['fly'])==len(expected_cells),'selected-map Fly destination icons missing'
  assert len(allocation['dungeon'])==expected_dungeon,'selected-map dungeon icons missing'
  report['legacy_allocation_audit']={'selected_region':selected_name,'allocated_fly':len(allocation['fly']),
   'expected_selected_fly':len(expected_cells),'allocated_dungeon':len(allocation['dungeon']),
   'expected_selected_dungeon':expected_dungeon,'missing_selected_fly':0,'missing_selected_dungeon':0,
   'native_active_sprites':active,'native_sprite_capacity':maximum,'hidden_foreign_icons':0,
   'pointer_bounds_unique_active_pass':True,'all_selected_icons_visible':True,'all_visible_destination_dungeon_icons_complete':True}
  # SELECT cannot switch Fly; held key must not activate the foreign-map menu.
  e.press('SELECT',hold=1,after=20)
  assert fly_ready() and e.u8(e.ptr('sRegionMap')+ABI['region.selected'])==expected_region
  assert not e.ptr('sSwitchMapMenu'),'disabled Fly SELECT opened map switch menu'
  await_state(e.field_idle,4000,'B');invariants();companion_state()
  assert e.location()==initial,'allocation audit flew or warped'
  assert regional_flags()==flags_before,'Fly opening/closing changed story/trainer flags'
  assert {f:blocks(e).flag(f) for f in flags}==initial_flags
  report.update(native_allocation_safe=True,legacy_selected_all_visited_icons_complete=True,
   full_original_storage_unchanged=True,fly_select_disabled_native_pass=True,pass_=True)
  report['pass']=True

"""
suffix='\nexcept Exception as ex:'+tail.split('\nexcept Exception as ex:',1)[1]
exec(compile('e=None\ntry:'+setup+body+suffix,'native-legacy-Fly-allocation-body','exec'))
