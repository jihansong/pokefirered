"""Reapply private space styles with the versioned interior generator.

Only owned assets, canonical blocks/borders and existing layout references change.
Map events, scripts, IDs, shared headers and flight media are not regenerated here.
"""
from pathlib import Path
import json,runpy
S=Path(__file__).resolve().parents[2]
r=json.loads(Path(__file__).with_name('space_map_styles_v2.json').read_text(encoding='utf8'))
if 'interior_v4' in r:
    cfg=r['interior_v4']
    contract=json.loads((S/cfg['contract']).read_text(encoding='utf8'))
    builder=runpy.run_path(str(S/cfg['generator']))
    room_outputs,room_proof=builder['build'](S,contract)
else:
    builder=runpy.run_path(str(Path(__file__).with_name('build_space_interiors_v3.py')))
    room_outputs,room_proof=builder['build'](S)
for rel,raw in room_outputs.items():
    dest=S/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
p=S/'data/layouts/layouts.json';before=p.read_bytes();j=json.loads(before)
for name,cfg in r['maps'].items():
    l=next(x for x in j['layouts'] if x.get('id')==cfg['layout'])
    l['secondary_tileset']=cfg['secondary_tileset']
    block=(S/cfg['canonical_blockdata']).read_bytes();border=(S/cfg['canonical_border']).read_bytes()
    assert len(block)==2*l['width']*l['height'] and len(border)==8
    (S/l['blockdata_filepath']).write_bytes(block);(S/l['border_filepath']).write_bytes(border)
if j!=json.loads(before):
    p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Private space style references and canonical blocks/borders applied.')
