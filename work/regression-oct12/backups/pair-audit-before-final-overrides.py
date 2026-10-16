import json,ast,re,hashlib,struct
from pathlib import Path
r=Path('/workspaces/pokefirered');j=json.loads((r/'data/layouts/layouts.json').read_text())
layouts={x.get('id'):x for x in j['layouts'] if x.get('id')}
groups=json.loads((r/'data/maps/map_groups.json').read_text())
names=list(dict.fromkeys(n for k,v in groups.items() if 'johto' in k.lower() and isinstance(v,list) for n in v if isinstance(n,str)))
spec={};parse=[]
for p in (r/'tools/johto').glob('build*.py'):
 try:t=ast.parse(p.read_text())
 except Exception as ex:parse.append([str(p.relative_to(r)),str(ex)]);continue
 for d in ast.walk(t):
  if not isinstance(d,ast.Dict):continue
  for k,v in zip(d.keys,d.values):
   if isinstance(k,ast.Constant) and k.value in names and isinstance(v,(ast.Tuple,ast.List)) and len(v.elts)==3 and all(isinstance(e,ast.Constant) and isinstance(e.value,str) for e in v.elts):
    pr,se,donor=(e.value for e in v.elts)
    if donor.startswith('LAYOUT_'):spec.setdefault(k.value,[]).append([str(p.relative_to(r)),['gTileset_'+pr,'gTileset_'+se],donor])
rows=[]
for name in names:
 m=json.loads((r/'data/maps'/name/'map.json').read_text());l=layouts[m['layout']];p=[l['primary_tileset'],l['secondary_tileset']];b=(r/l['blockdata_filepath']).read_bytes()
 row={'map':name,'pair':p,'errors':[],'warnings':[],'donors':[]}
 if len(b)!=l['width']*l['height']*2:row['errors'].append('layout length')
 if m['map_type'] in ['MAP_TYPE_TOWN','MAP_TYPE_CITY','MAP_TYPE_ROUTE'] and 'Building' in p[0]:row['warnings'].append('outdoor Building')
 for path,decl,donor in spec.get(name,[]):
  d=layouts.get(donor);pair=[d['primary_tileset'],d['secondary_tileset']] if d else None
  row['donors'].append({'generator':path,'declaration':decl,'donor':donor,'donor_pair':pair})
  if p!=decl:row['warnings'].append('generator pair mismatch')
  if pair and p!=pair:row['warnings'].append('donor pair mismatch')
 for kind in ['object_events','warp_events','coord_events','bg_events']:
  for i,event in enumerate(m.get(kind,[]) or []):
   if isinstance(event.get('x'),int) and isinstance(event.get('y'),int) and not(0<=event['x']<l['width'] and 0<=event['y']<l['height']):row['warnings'].append(kind+' coordinate outside')
 rows.append(row)
report={'map_count':len(names),'parse_errors':parse,'errors':[x for x in rows if x['errors']],'warnings':[x for x in rows if x['warnings']],'maps':rows,'scope':'Static layout pairing/donor/coordinates; does not certify visual quality or full story playthrough'}
(r/'work/regression-oct12/johto-pair-geometry-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['map_count','parse_errors','errors','warnings']},indent=2))
