#!/usr/bin/env python3
"""Read-only compiled wild-header alignment and map-region bounds audit."""
import argparse, hashlib, json, struct
from pathlib import Path

a=argparse.ArgumentParser()
a.add_argument('--rom',required=True);a.add_argument('--elf',required=True)
a.add_argument('--root',default='.')
a.add_argument('--nm',default='arm-none-eabi-nm')
a=a.parse_args()
root=Path(a.root).resolve();rom=Path(a.rom).resolve();elf=Path(a.elf).resolve()
b=rom.read_bytes();before=hashlib.sha256(b).hexdigest()
g=json.loads((root/'data/maps/map_groups.json').read_text())
order=g['group_order'];pairs={}
for gi,k in enumerate(order):
    for ni,name in enumerate(g[k]):pairs[(gi,ni)]=name
hoenn=[i for i,k in enumerate(order) if k.startswith('gMapGroup_Hoenn')]
assert hoenn==list(range(43,76)),hoenn
assert order[76]=='gMapGroup_JohtoEntry',order[76]
assert g[order[75]]==['Route124_DivingTreasureHuntersHouse']
assert 'NewBarkTown' in g[order[76]]
eb=elf.read_bytes();eh=struct.unpack_from('<16sHHIIIIIHHHHHH',eb)
assert eh[0][:6]==bytes([127,69,76,70,1,1]) and eh[2]==40,'requires ARM ELF32 little endian'
sections=[struct.unpack_from('<IIIIIIIIII',eb,eh[6]+i*eh[11]) for i in range(eh[12])]
symbols={}
for section in sections:
    if section[1]!=2:continue
    string_section=sections[section[6]]
    strings=eb[string_section[4]:string_section[4]+string_section[5]]
    stride=section[9] or 16
    assert stride>=16 and section[5]%stride==0
    for at in range(section[4],section[4]+section[5],stride):
        no,address,size,info,other,index=struct.unpack_from('<IIIBBH',eb,at)
        if not no or not index:continue
        assert no<len(strings)
        end=strings.find(bytes([0]),no);assert end>=no
        name=strings[no:end].decode()
        if name in ('gWildMonHeaders','gWildMonHeadersMorning','gWildMonHeadersNight'):
            assert info&15==1,'wild header symbol is not ELF object'
            assert name not in symbols,'duplicate wild header symbol'
            symbols[name]=(address,size)
assert len(symbols)==3,symbols
seqs={}
for name,(address,size) in symbols.items():
    assert size>=20 and size%20==0,(name,size)
    offset=address-0x08000000
    assert 0<=offset<=len(b)-size,(name,address,size)
    data=b[offset:offset+size]
    seq=[tuple(data[i:i+2]) for i in range(0,size,20)]
    assert seq[-1]==(255,255) and (255,255) not in seq[:-1],(name,'sentinel')
    for i,pair in enumerate(seq[:-1]):
        assert pair in pairs,(name,i,pair)
        for pointer,count in zip(struct.unpack_from('<4I',data,i*20+4),(12,5,5,10)):
            if pointer==0:continue
            po=pointer-0x08000000
            assert pointer%4==0 and 0<=po<=len(b)-8,(name,i,hex(pointer))
            mons=struct.unpack_from('<I',b,po+4)[0];mo=mons-0x08000000
            assert mons%2==0 and 0<=mo<=len(b)-count*4,(name,i,hex(mons),count)
    seqs[name]=seq
base=seqs['gWildMonHeaders']
assert all(seq==base for seq in seqs.values()),'time-table map/index mismatch'
assert hashlib.sha256(rom.read_bytes()).hexdigest()==before,'ROM mutated'
entries=base[:-1]
report={'audit':'compiled-wild-header-regions','rom_sha256':before,'symbol_source':'ELF32_SYMTAB','tables':3,'headers_per_table':len(entries),'time_table_map_alignment':True,'valid_map_pairs':True,'valid_rom_info_and_mon_table_bounds':True,'sentinels_valid':True,'hoenn_group_range':[43,75],'johto_group':76,'hoenn_headers':sum(43<=x<=75 for x,y in entries),'johto_headers':sum(x==76 for x,y in entries),'johto_maps':[pairs[p] for p in entries if p[0]==76],'save_files_read_or_written':False,'ram_instrumentation':False,'pass_all':True}
print(json.dumps(report,separators=(',',':')))
