#!/usr/bin/env python3
import argparse,datetime,hashlib
from pathlib import Path
OLD_SHA='959c2b273025b22892183c7a6804b1e58380f5a88a14636e61f877c21f3cbde8'
NEW_SHA='c99fcc261c0354689d53f3c7d3f285c4eb45056cf0c700255f6841fe4028f2e8'
OLD=" c='#include \"global.h\"\\n#include \"gflib.h\"\\n#include \"sprite.h\"\\n#include \"task.h\"\\n#include \"main.h\"\\n'+ '\\n'.join(enums+defs)+'\\n'"
NEW=" section_names=['MAPSEC_NEW_BARK_TOWN','MAPSEC_CHERRYGROVE_CITY','MAPSEC_VIOLET_CITY',\n  'MAPSEC_AZALEA_TOWN','MAPSEC_GOLDENROD_CITY','MAPSEC_ECRUTEAK_CITY','MAPSEC_OLIVINE_CITY',\n  'MAPSEC_CIANWOOD_CITY','MAPSEC_JOHTO_ROUTE40','MAPSEC_PALLET_TOWN','MAPSEC_SLATEPORT_CITY']\n fields.extend([('section.'+n,None,None) for n in section_names])\n expressions.extend(section_names)\n c='#include \"global.h\"\\n#include \"gflib.h\"\\n#include \"sprite.h\"\\n#include \"task.h\"\\n#include \"main.h\"\\n#include \"constants/region_map_sections.h\"\\n'+ '\\n'.join(enums+defs)+'\\n'"
OLD_GRID="target_cell=(sections[target_section]['x'],sections[target_section]['y'])"
NEW_GRID="if 'x' in sections[target_section] and 'y' in sections[target_section]:\n target_cell=(sections[target_section]['x'],sections[target_section]['y'])\n report['target_cell_source']='native section geometry'\nelse:\n assert region=='hoenn','missing geometry outside imported Hoenn'\n layout_text=Path('src/data/region_map/region_map_layout_hoenn.h').read_text()\n assert 'static const u8 sRegionMapSections_Hoenn[LAYER_COUNT][MAP_HEIGHT][HOENN_MAP_WIDTH]' in layout_text\n region_source=Path('src/region_map.c').read_text()\n height=int(re.search(r'#define\\s+MAP_HEIGHT\\s+(\\d+)\\b',region_source).group(1))\n width=int(re.search(r'#define\\s+HOENN_MAP_WIDTH\\s+(\\d+)\\b',region_source).group(1))\n grid=r.at(syms['sRegionMapSections_Hoenn'],height*width)\n hits=[(i%width,i//width) for i,v in enumerate(grid) if v==ABI['section.'+target_section]]\n assert hits,('target absent from candidate Hoenn grid',target_section)\n target_cell=hits[0];report['target_cell_source']='candidate compiled Hoenn LAYER_MAP table'\n report['target_cells']=hits"
def sha(b):return hashlib.sha256(b).hexdigest()
def apply(root,mutate):
 p=root/'tools/qa/native_fly_region_qa.py';b=p.read_bytes()
 if sha(b)==NEW_SHA:print('ALREADY QA enum fix',NEW_SHA);return
 assert sha(b)==OLD_SHA,('unexpected QA source',sha(b))
 t=b.decode();assert t.count(OLD)==1 and t.count('const(target_section)')==2
 t=t.replace(OLD,NEW,1).replace('const(target_section)',"ABI['section.'+target_section]")
 assert t.count(OLD_GRID)==1;t=t.replace(OLD_GRID,NEW_GRID,1)
 after=t.encode();assert sha(after)==NEW_SHA
 compile(t,str(p),'exec');print('QA ENUM FIX',len(after),NEW_SHA,'apply',mutate)
 if not mutate:return
 d=root/'outputs/native-fly-enum-fix'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');d.mkdir(parents=True)
 (d/'native_fly_region_qa.before.py').write_bytes(b)
 assert p.read_bytes()==b
 tmp=p.with_name(p.name+'.enumfix.tmp');assert not tmp.exists();tmp.write_bytes(after);tmp.replace(p)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root).resolve(),a.apply)
