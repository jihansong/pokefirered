"""Reapply only appended space edge-arrow aliases and canonical map patches.
No build/emulator/save operations. Call after editing the canonical space maps.
"""
from pathlib import Path
import json,struct
S=Path(__file__).resolve().parents[2]
r=json.loads(Path(__file__).with_name('space_warp_directions.json').read_text(encoding='utf8'))
q=S/r['tileset'];mt=bytearray((q/'metatiles.bin').read_bytes());a=bytearray((q/'metatile_attributes.bin').read_bytes())
i=r['source_door_metatile']-512; template=bytes(mt[i*16:(i+1)*16]);attr=struct.unpack_from('<I',a,i*4)[0]
assert attr&511==0x60
for cfg in r['directions'].values():
    k=cfg['id']-512;mt[k*16:(k+1)*16]=template;struct.pack_into('<I',a,k*4,(attr&~511)|cfg['behavior'])
(q/'metatiles.bin').write_bytes(mt);(q/'metatile_attributes.bin').write_bytes(a)
layouts=json.loads((S/'data/layouts/layouts.json').read_text(encoding='utf8'))['layouts']
for name,ds in r['maps'].items():
    m=json.loads((S/f'data/maps/{name}/map.json').read_text(encoding='utf8'));l=next(x for x in layouts if x.get('id')==m['layout'])
    canonical=S/f'tools/hoenn_import/patches/{name}.blockdata.bin';raw=canonical.read_bytes()
    assert len(raw)==2*l['width']*l['height'] and len(ds)==len(m['warp_events'])
    words=list(struct.unpack('<%dH'%(len(raw)//2),raw))
    for ev,d in zip(m['warp_events'],ds):words[ev['y']*l['width']+ev['x']]=0x3000|r['directions'][d]['id']
    raw=struct.pack('<%dH'%len(words),*words);canonical.write_bytes(raw);(S/l['blockdata_filepath']).write_bytes(raw)
print('Seven space arrow warps reapplied; unrelated maps/events untouched.')
