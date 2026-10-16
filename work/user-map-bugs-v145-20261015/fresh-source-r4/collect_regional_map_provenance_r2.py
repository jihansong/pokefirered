"""Collect one guarded source bundle for all current Johto/Hoenn landscapes.

Read-only product access. Output must be a new work/ directory. No SAV, ROM or
ELF is copied, no emulator is opened, and this is not a gameplay PASS.
"""
import argparse, hashlib, json, re, struct, zipfile
from pathlib import Path


def sha(b):return hashlib.sha256(b).hexdigest()


def elf_symbols(blob):
    assert blob[:7]==b'\x7fELF\x01\x01\x01', 'Expected little-endian ELF32'
    shoff=struct.unpack_from('<I',blob,32)[0]
    shsize,count=struct.unpack_from('<HH',blob,46)
    assert shsize==40 and count<65535
    sections=[struct.unpack_from('<10I',blob,shoff+i*shsize)for i in range(count)]
    rows={}
    for section in sections:
        if section[1]!=2:continue
        assert section[9]==16 and section[5]%16==0
        strings=sections[section[6]];pool=blob[strings[4]:strings[4]+strings[5]];owner=''
        for offset in range(section[4],section[4]+section[5],16):
            name,value,size,info,other,index=struct.unpack_from('<IIIBBH',blob,offset)
            end=pool.find(b'\0',name);assert end>=name
            name=pool[name:end].decode('utf-8')
            if info&15==4:owner=name
            rows.setdefault(name,[]).append(dict(value=value,size=size,info=info,section=index,translation_unit=owner))
    return sections,rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True,type=Path)
    p.add_argument('--rom',required=True,type=Path)
    p.add_argument('--elf',required=True,type=Path)
    p.add_argument('--expect-rom-sha',required=True)
    p.add_argument('--expect-elf-sha',required=True)
    p.add_argument('--out',required=True,type=Path)
    a=p.parse_args();root=a.root.resolve(strict=True);out=a.out.resolve()
    assert not out.exists() and out.is_relative_to(root/'work')
    rompath=a.rom.resolve(strict=True);elfpath=a.elf.resolve(strict=True)
    assert rompath.is_relative_to(root) and elfpath.is_relative_to(root)
    rom=rompath.read_bytes();elf=elfpath.read_bytes()
    assert len(a.expect_rom_sha)==len(a.expect_elf_sha)==64
    assert sha(rom)==a.expect_rom_sha and sha(elf)==a.expect_elf_sha
    sections,symbols=elf_symbols(elf)
    copied={};missing=[]
    def read(rel,optional=False):
        path=(root/rel).resolve()
        assert path.is_relative_to(root) and not rel.startswith(('saves/','reference/'))
        if not path.exists():
            if optional:missing.append(rel);return None
            raise FileNotFoundError(rel)
        data=path.read_bytes();copied[rel]=data;return data
    def text(rel,optional=False):
        data=read(rel,optional);return data.decode('utf-8')if data is not None else ''
    def data_json(rel):return json.loads(text(rel))
    groups=data_json('data/maps/map_groups.json')
    layout_document=data_json('data/layouts/layouts.json');layouts=layout_document['layouts']
    by_layout={v['id']:v for v in layouts if 'id'in v}
    all_maps={}
    for group in groups['group_order']:
        for index,name in enumerate(groups[group]):
            path=root/'data/maps'/name/'map.json'
            d=json.loads(path.read_text());all_maps[name]=dict(meta=d,group=group,index=index)
    selected={name for name,row in all_maps.items()if 'Hoenn'in row['group']or'Johto'in row['group']}
    assert selected
    selected.update(name for name in ['KantoAirport','VermilionCity']if name in all_maps)
    by_id={row['meta']['id']:name for name,row in all_maps.items()}
    neighbors=set()
    for name in selected:
        for connection in all_maps[name]['meta'].get('connections')or []:
            if connection['map']in by_id:neighbors.add(by_id[connection['map']])
    selected.update(neighbors)
    selected_layouts=set()
    for name in sorted(selected):
        for file in ['map.json','scripts.inc','text.inc']:
            read('data/maps/'+name+'/'+file,optional=file!='map.json')
        d=all_maps[name]['meta'];selected_layouts.add(d['layout'])
        l=by_layout[d['layout']]
        read(l['blockdata_filepath']);read(l['border_filepath'])
    for rel in ['AGENTS.md','.claude/agents/engineer.md','.claude/agents/qa.md',
                'docs/INSTALL.md','docs/team/log.md','src/airplane_flight.c',
                'include/constants/airplane.h','include/fieldmap.h','include/global.fieldmap.h',
                'src/fieldmap.c','src/field_camera.c','src/tilesets.c','tools/hoenn_import/import_maps.py',
                'tools/hoenn_import/import_tilesets.py','tools/hoenn_import/apply_patches.py']:
        read(rel,optional=False)
    definition_paths=['src/data/tilesets/'+name+'.h'for name in
                      ['headers','hoenn_headers','graphics','hoenn_graphics','metatiles','hoenn_metatiles']]
    definitions='\n'.join(text(rel)for rel in definition_paths)+'\n'+text('src/graphics.c')
    used_sets={by_layout[layout][field]for layout in selected_layouts for field in ['primary_tileset','secondary_tileset']}
    asset_roots=set();unresolved=[]
    for name in sorted(used_sets-{'NULL'}):
        matches=re.findall(r'const struct Tileset\s+'+re.escape(name)+r'\s*=\s*\{(.*?)\};',definitions,re.S)
        assert len(matches)==1,('Missing/ambiguous named tileset definition',name)
        refs=re.findall(r'\.(?:tiles|palettes|metatiles|metatileAttributes)\s*=\s*(\w+)',matches[0])
        assert len(refs)==4
        for ref in refs:
            declaration=re.findall(r'const\s+[^;\n]*\b'+re.escape(ref)+r'\s*\[[^\]]*\](?:\[[^\]]*\])?\s*=\s*(.*?);',definitions,re.S)
            if len(declaration)!=1:unresolved.append(dict(tileset=name,symbol=ref));continue
            paths=re.findall(r'INCBIN_\w+\("([^"]+)"\)',declaration[0])
            assert paths,('No file paths in tileset asset',name,ref)
            for rel in paths:
                assert rel.startswith('data/tilesets/'),('Unexpected referenced tileset path',rel)
                bits=Path(rel).parts;assert len(bits)>=5
                asset_roots.add('/'.join(bits[:4]))
    assert not unresolved,('Unresolved tileset source symbols',unresolved)
    for base in sorted(asset_roots):
        folder=root/base;assert folder.is_dir()
        for file in sorted(folder.rglob('*')):
            if file.is_file()and file.suffix.lower()in ['.png','.pal','.bin']:
                read(file.relative_to(root).as_posix())
    for directory in ['tools/johto','tools/hoenn_import/patches']:
        for file in sorted((root/directory).rglob('*')):
            if file.is_file()and file.suffix.lower()in ['.py','.json','.inc','.mapscripts','.text','.jsonpatch']:
                read(file.relative_to(root).as_posix())
    def unique(name):
        rows=[v for v in symbols.get(name,[])if v['section']<len(sections)]
        assert len(rows)==1,('Missing/ambiguous current ELF symbol',name,rows)
        row=rows[0];section=sections[row['section']]
        assert section[2]&2 and 0x08000000<=row['value']<0x08000000+len(rom)
        assert section[3]<=row['value']<section[3]+section[5]
        return row,section
    def same_rom_elf(address,length,row,section):
        assert section[3]<=address<address+length<=section[3]+section[5]
        r=address-0x08000000;f=section[4]+address-section[3]
        rb=rom[r:r+length];assert len(rb)==length and elf[f:f+length]==rb
        return rb
    table,section=unique('gMapLayouts')
    table_bytes=same_rom_elf(table['value'],4*len(layouts),table,section)
    bindings=[]; geometry_anomalies=[]
    for index,layout in enumerate(layouts):
        pointer=struct.unpack_from('<I',table_bytes,index*4)[0]
        if not layout:
            assert pointer==0,('Non-null empty layout index',index);continue
        row,sec=unique(layout['name']);assert pointer==row['value']
        if layout['id']not in selected_layouts:continue
        # MapLayout's existing ARM layout is documented in global.fieldmap.h;
        # export its 28 raw bytes and source fields for independent checking.
        raw=same_rom_elf(pointer,28,row,sec)
        width,height,border,blocks,primary,secondary=struct.unpack_from('<6I',raw)
        assert (width,height)==(layout['width'],layout['height'])
        assert tuple(raw[24:26])==(layout.get('border_width',2),layout.get('border_height',2))
        data=copied[layout['blockdata_filepath']];bdata=copied[layout['border_filepath']]
        map_expected=width*height*2; border_expected=raw[24]*raw[25]*2
        size_notes=[]
        if len(data)!=map_expected:
            size_notes.append(dict(kind='blockdata_size_mismatch',path=layout['blockdata_filepath'],
                                   actual_bytes=len(data),declared_bytes=map_expected))
        if len(bdata)!=border_expected:
            size_notes.append(dict(kind='border_size_mismatch',path=layout['border_filepath'],
                                   actual_bytes=len(bdata),declared_bytes=border_expected))
        if size_notes:
            geometry_anomalies.append(dict(layout_id=layout['id'],layout_index=index,
                map_dimensions=[width,height],border_dimensions=list(raw[24:26]),
                layout_pointer=hex(pointer),blocks_pointer=hex(blocks),border_pointer=hex(border),
                anomalies=size_notes,engine_effect_not_inferred=True,original_binaries_preserved=True))
        assert rom[blocks-0x08000000:blocks-0x08000000+len(data)]==data,('Source/ROM map mismatch',layout['id'])
        assert rom[border-0x08000000:border-0x08000000+len(bdata)]==bdata,('Source/ROM border mismatch',layout['id'])
        tile_bindings=[]
        for field,ptr in [('primary_tileset',primary),('secondary_tileset',secondary)]:
            if layout[field]=='NULL':
                assert ptr==0
                tile_bindings.append(dict(field=field,name='NULL',symbol=None,header_raw_hex=None))
                continue
            tr,ts=unique(layout[field]);assert tr['value']==ptr
            traw=same_rom_elf(ptr,24,tr,ts)
            tile_bindings.append(dict(field=field,name=layout[field],symbol=tr,header_raw_hex=traw.hex()))
        bindings.append(dict(id=layout['id'],table_index=index,layout_symbol=row,layout_raw_hex=raw.hex(),
                             blockdata_sha256=sha(data),border_sha256=sha(bdata),tilesets=tile_bindings))
    assert len(bindings)==len(selected_layouts)
    # Fail if a rebuild or another agent changed a pinned input during capture.
    assert sha(rompath.read_bytes())==a.expect_rom_sha and sha(elfpath.read_bytes())==a.expect_elf_sha
    for rel,data in copied.items():assert (root/rel).read_bytes()==data,('Source changed while collecting',rel)
    proof=dict(status=('CURRENT_SOURCE_ROM_ELF_BOUND_WITH_GEOMETRY_ANOMALIES' if geometry_anomalies else 'CURRENT_SOURCE_ROM_ELF_LANDSCAPES_BOUND_READONLY'),ROM_sha256=a.expect_rom_sha,
               ELF_sha256=a.expect_elf_sha,map_layout_table_symbol=table,map_layout_table_sha256=sha(table_bytes),
               layouts=bindings,all_selected_source_blocks_and_borders_match_ROM_and_ELF=True,
               geometry_sizes_pass=not geometry_anomalies,geometry_anomalies=geometry_anomalies,
               geometry_size_anomaly_count=len(geometry_anomalies),
               source_bundle_only_not_gameplay_QA_pass=True,
               native_gameplay_executed=False,SAV_copied=False,product_edits=False)
    copied['QA-current-map-ROM-ELF-bindings.json']=(json.dumps(proof,indent=2)+'\n').encode()
    manifest=dict(status='SOURCE_AND_COMPILED_LANDSCAPE_BUNDLE_ONLY',ROM_sha256=a.expect_rom_sha,ELF_sha256=a.expect_elf_sha,
                  regional_map_count=sum('Hoenn'in row['group']or'Johto'in row['group']for row in all_maps.values()),
                  selected_map_count=len(selected),selected_layout_count=len(selected_layouts),
                  files={rel:dict(sha256=sha(data),bytes=len(data))for rel,data in copied.items()},
                  geometry_sizes_pass=not geometry_anomalies,geometry_anomaly_count=len(geometry_anomalies),
                  source_bundle_only_not_gameplay_QA_pass=True,
                  optional_files_absent=missing,product_edits=False,SAV_copied=False,native_gameplay_executed=False)
    out.mkdir(parents=True)
    archive=out/'regional-map-source-and-provenance.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for rel,data in copied.items():z.writestr(rel,data)
        z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None
        for rel,data in copied.items():assert sha(z.read(rel))==sha(data)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(status=proof['status'],selected_maps=len(selected),layouts=len(bindings),members=len(copied)+1,
                         archive=str(archive),archive_sha256=sha(archive.read_bytes()),bytes=archive.stat().st_size,
                         geometry_sizes_pass=not geometry_anomalies,geometry_anomalies=geometry_anomalies,
                         source_bundle_only_not_gameplay_QA_pass=True,
                         product_edits=False,SAV_copied=False,native_gameplay_executed=False)))


if __name__=='__main__':main()
