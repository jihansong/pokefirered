#!/usr/bin/env python3
"""Native legacy all-visited Fly allocation audit; original SAV is read-only."""
from pathlib import Path
import hashlib
base=Path('tools/qa/native_fly_region_qa.py')
source_text=base.read_text()
expected='959c2b273025b22892183c7a6804b1e58380f5a88a14636e61f877c21f3cbde8'
assert hashlib.sha256(source_text.encode()).hexdigest()==expected,'Fly QA source guard changed'
marker='\ne=None\ntry:'
assert source_text.count(marker)==1
prefix,tail=source_text.split(marker,1)
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
setup=setup.replace(world_anchor,"  s.set_flag('FLAG_SYS_CAN_LINK_WITH_RS',True)\n"+world_anchor,1)
body=r"""
  def regional_flags():
   b=blocks(e)
   f=off('sb1.flags');end=off('sb1.vars')
   t=off('sb2.hoennTrainerFlags');h=off('sb2.hoennFlags');v=off('sb2.hoennVars')
   assert 0<f<end<=len(b.sb1) and 0<t<h<v<=len(b.sb2)
   return bytes(b.sb1[f:end]),bytes(b.sb2[t:h]),bytes(b.sb2[h:v])
  flags_before=regional_flags()
  start_party();report['ui_stage']='wait-native-all-visited-Fly-map'
  await_state(fly_ready,4000);e.run(2)
  rp=e.ptr('sRegionMap')
  assert e.u8(rp+ABI['region.selected'])==expected_region,'wrong legacy Fly region'
  move_cursor_to(target_cell);c=cursor()
  assert c['mapsec']==const(target_section) and c['type']==TYPES.index('MAPSECTYPE_VISITED')
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
