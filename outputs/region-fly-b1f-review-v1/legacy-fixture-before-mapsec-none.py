#!/usr/bin/env python3
"""Native legacy all-visited Fly allocation audit; original SAV is read-only."""
from pathlib import Path
import hashlib
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
new="('region.selected','RegionMap','selectedRegion'),('sprite.size','Sprite',None),('hoenn_destination.size','HoennFlyDestination',None),('hoenn_destination.flag','HoennFlyDestination','visitedFlag')]"
assert prefix.count(old)==1;prefix=prefix.replace(old,new,1)
old="section_names=['MAPSEC_NEW_BARK_TOWN'"
new="section_names=['KANTO_MAPSEC_START','MAPSEC_NEW_BARK_TOWN'"
assert prefix.count(old)==1;prefix=prefix.replace(old,new,1)
exec(compile(prefix,str(base),'exec'))
assert a.case in ['kanto-on','hoenn-on'],'use only independent legacy all-visited cases'
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
  assert len(grid)==height*width and all(v<count for v in grid),'candidate Hoenn map grid out of bounds'
  eligible=sum(bool(ids[v]) for v in grid)
  assert eligible==24,('candidate Hoenn visited-cell oracle changed',eligible)
  report['all_visited_fixture']={'hoenn_flags':hoenn_flags,'compiled_hoenn_flag_ids':sorted(resolved),
   'compiled_table_stride':stride,'compiled_flag_offset':fo,'compiled_hoenn_eligible_cells':eligible,
   'source_destination_sha256':sha(dest_source.encode()),'all_declared_flags_set':True}
"""
setup=setup.replace(world_anchor,"  s.set_flag('FLAG_SYS_CAN_LINK_WITH_RS',True)\n"+hoenn_fixture+world_anchor,1)
body=r"""
  def regional_flags():
   b=blocks(e)
   f=off('sb1.flags');end=off('sb1.vars')
   t=off('sb2.hoennTrainerFlags');h=off('sb2.hoennFlags');v=off('sb2.hoennVars')
   assert 0<f<end<=len(b.sb1) and 0<t<h<v<=len(b.sb2)
   return bytes(b.sb1[f:end]),bytes(b.sb2[t:h]),bytes(b.sb2[h:v])
  assert all(blocks(e).flag(name) for name in hoenn_flags),'all-visited Hoenn flags not preserved through native cold boot'
  report['all_visited_fixture']['native_cold_flags_confirmed']=True
  flags_before=regional_flags()
  start_party();report['ui_stage']='wait-native-all-visited-Fly-map'
  await_state(fly_ready,4000);e.run(2)
  rp=e.ptr('sRegionMap')
  assert e.u8(rp+ABI['region.selected'])==expected_region,'wrong legacy Fly region'
  move_cursor_to(target_cell);c=cursor()
  assert c['mapsec']==ABI['section.'+target_section] and c['type']==TYPES.index('MAPSECTYPE_VISITED')
  allocation=icon_snapshot();photo(e,'legacy-all-visited-Fly-icons')
  maximum=int(re.search(r'#define\s+MAX_SPRITES\s+(\d+)',Path('include/sprite.h').read_text()).group(1))
  assert maximum==64,'native sprite pool ABI changed'
  sprites=allocation['fly']+allocation['dungeon']
  ids=[v['sprite'] for v in sprites]
  assert len(ids)==len(set(ids)),'Fly/dungeon records alias the same native sprite'
  active=sum(bool(e.u8(syms['gSprites']+i*ABI['sprite.size']+0x3e)&1) for i in range(maximum))
  assert len(ids)<=active<=maximum,'native icon pool count impossible'
  counts={name:sum(v['region']==i for v in allocation['fly']) for i,name in enumerate(REGIONS)}
  expected_counts={'REGIONMAP_KANTO':13,'REGIONMAP_HOENN':24}
  assert set(expected_counts)<=set(REGIONS)
  complete=(len(allocation['fly'])==44 and all(counts[k]==v for k,v in expected_counts.items()))
  report['legacy_allocation_audit']={'allocated_fly':len(allocation['fly']),
   'allocated_dungeon':len(allocation['dungeon']),'expected_legacy_fly':44,
   'expected_kanto_hoenn':expected_counts,'allocated_by_region':counts,
   'missing_legacy_fly':max(0,44-len(allocation['fly'])),
   'native_active_sprites':active,'native_sprite_capacity':maximum,
   'pointer_bounds_unique_active_pass':True,'all_visited_icons_complete':complete}
  report['ui_stage']='cancel-legacy-all-visited-Fly-map'
  await_state(e.field_idle,4000,'B');invariants();companion_state()
  assert e.location()==initial,'allocation audit unexpectedly flew or warped'
  assert regional_flags()==flags_before,'opening/closing Fly changed regional story/trainer flags'
  assert {f:blocks(e).flag(f) for f in flags}==initial_flags
  report.update(native_allocation_safe=True,legacy_all_visited_icons_complete=complete,
   full_original_storage_unchanged=True,pass_=complete)
  report['pass']=complete
  if not complete:report['incomplete_reason']='native Fly records missing in the all-visited legacy fixture; allocation counts retained as evidence'
"""
suffix='\nexcept Exception as ex:'+tail.split('\nexcept Exception as ex:',1)[1]
exec(compile('e=None\ntry:'+setup+body+suffix,'native-legacy-Fly-allocation-body','exec'))
