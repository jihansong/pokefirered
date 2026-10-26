#!/usr/bin/env python3
"""Verify a public source projection and exact Linux build artifacts.

This command never builds, starts an emulator, loads a DLL or modifies a source
tree. --source-only reports source/offline-art results without a compiled PASS.
The linked mode requires a fresh, explicitly selected Linux provenance bundle.
"""
import argparse
import json
from pathlib import Path
import re
import struct
import traceback

from space_elf import Elf, audit_object, lz77, map_sections, sha
from space_source_checks import check_source


AGBCC = 'da598c1d918402c42c0c0d7128ba14567f3175e9'
CONTAINER = 'sha256:116afba8df8453961de2936ffab20dd441edf4d682856c1ec8b0e53d7ed0bbf5'
REQUIRED_UNITS = [
    'src/'+n+'.o' for n in (
        'pokemon', 'learn_move', 'item', 'item_menu_icons', 'pokedex_screen',
        'battle_script_commands', 'evolution_scene', 'pokemon_summary_screen',
        'reshow_battle_screen', 'battle_main', 'battle_bg', 'battle_util2',
        'battle_message', 'battle_gfx_sfx_util', 'librfu_intr', 'overworld',
        'fieldmap', 'field_specials', 'field_fadetransition', 'hoenn_space_story',
        'tilesets', 'intro_opening', 'title_screen', 'credits')
] + ['data/maps.o', 'data/map_events.o', 'data/event_scripts.o', 'sound/songs/midi/mus_credits.o']


def load(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def confined(root, rel):
    assert isinstance(rel, str) and '\\' not in rel
    path = (root/rel).resolve()
    assert path.is_relative_to(root) and path != root, ('Artifact path escapes bundle', rel)
    return path


def pinned(root, row):
    path = confined(root, row['path']); raw = path.read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], ('Artifact drift', row['path'])
    return path


def linked(source, artifact_dir, reference_path, reference):
    artifact_dir = artifact_dir.resolve(); source = source.resolve()
    provenance_path = artifact_dir/'provenance.json'; p = load(provenance_path)
    assert p['schema'] == 'TY_SPACE_LINUX_BUILD_V1'
    assert p['platform'] == 'linux' and re.fullmatch('[0-9a-f]{40}', p['source_commit'])
    assert p['reference_manifest_sha256'] == sha(reference_path.read_bytes())
    assert p['toolchain']['agbcc_commit'] == AGBCC and p['toolchain']['container_digest'] == CONTAINER
    assert p['source_tree_verified_before_build'] is True
    assert p['source_file_hashes'] == {n:v['sha256'] for n,v in reference['files'].items()}
    assert p['source_file_hashes_after'] == p['source_file_hashes']
    assert p['steps'] and all(x['returncode'] == 0 and isinstance(x['command'], list) and x['command'] for x in p['steps'])
    logs = []
    for row in p['steps']:
        log = pinned(artifact_dir, row['log']).read_text('utf8', errors='replace'); logs.append(log)
        assert not re.search(r'\bwarning\s*:', log, re.I), ('Build warning', row['name'])
        command = ' '.join(row['command'])
        assert not re.search(r'\bmake\s+clean\b|libmgba|libqa\.(?:so|dll)', command, re.I)
    full_log = '\n'.join(logs)
    control=p['warning_control']; warnings=[]
    for step in control['steps']:
        assert step['returncode']==0
        text=pinned(artifact_dir,step['log']).read_text('utf8',errors='replace')
        warnings.extend(line for line in text.splitlines() if re.search(r'\bwarning\s*:',line,re.I))
    assert len(warnings)==1 and re.search(r'warning:\s+.*pokemonthyl\.elf has a LOAD segment with RWX permissions\s*$',warnings[0])
    for key in ('rom','elf','map','sym'):
        rows=[control['baseline_artifacts'][key],control['warning_artifacts'][key],control['final_artifacts'][key],p['artifacts'][key]]
        assert len({(row['bytes'],row['sha256']) for row in rows})==1
        for row in rows: pinned(artifact_dir,row)
    for rel,row in reference['required_generated_sources'].items():
        raw=(source/rel).read_bytes()
        assert len(raw)==row['bytes'] and sha(raw)==row['sha256'],('Generated source differs from frozen canonical output',rel)
    paths = {k:pinned(artifact_dir, p['artifacts'][k]) for k in ['rom', 'elf', 'map', 'sym', 'abi_probe']}
    rom = paths['rom'].read_bytes(); assert len(rom) == 32*1024*1024
    if reference.get('expected_game_rom_sha256'):
        assert sha(rom) == reference['expected_game_rom_sha256'], 'QA-only revision changed game ROM bytes'
    elf = Elf(paths['elf']); assert elf.kind == 2
    maptext = paths['map'].read_text('utf8'); symtext = paths['sym'].read_text('utf8')
    all_sections = []
    for s in elf.sections:
        if s['type'] == 1 and s['flags']&2 and 0x08000000 <= s['address'] < 0x0a000000 and s['size']:
            assert rom[s['address']-0x08000000:s['address']-0x08000000+s['size']] == elf.content(s)
            all_sections.append(dict(name=s['name'], address=hex(s['address']), bytes=s['size']))
    syms = {}
    for line in symtext.splitlines():
        fields = line.split()
        if len(fields) >= 4 and re.fullmatch('[0-9a-fA-F]{8}', fields[0]):
            syms.setdefault(fields[-1], set()).add(int(fields[0], 16))
    for name in ['gMapGroups', 'gMapLayouts', 'gSaveBlock1', 'gSaveBlock2', 'gPokemonStorage', 'gMain', 'gPlayerParty']:
        assert syms.get(name) == {elf.one(name)['value']}, ('SYM not bound to ELF', name)

    objects = {x['unit']:x for x in p['objects']}
    assert len(objects) == len(p['objects']) and set(REQUIRED_UNITS) <= objects.keys()
    parsed = {}; placements = {}; object_proofs = []
    for unit in REQUIRED_UNITS:
        row = objects[unit]; path = pinned(artifact_dir, row)
        expected_source=reference['files'].get(row['source']) or reference['required_generated_sources'].get(row['source'])
        assert expected_source and row['source_sha256'] == expected_source['sha256']
        assert row['compile_log'] in range(len(logs)) and row['source'] in logs[row['compile_log']]
        # All objects come from the same immutable selected Linux bundle.
        object_proofs.append(audit_object(path, unit, elf, rom, maptext))
        parsed[unit] = Elf(path); placements[unit] = map_sections(maptext, unit)

    probe = Elf(paths['abi_probe']); assert probe.kind == 1
    abi = list(struct.unpack('<18I', probe.named_bytes('gSpaceAbiProbe')))
    assert abi == reference['compiled_abi_expected'], ('Compiled ABI changed', abi)
    assert p['abi_probe_source_sha256'] == reference['files']['tools/qa/space_abi_probe.c']['sha256']
    actual_ram = sorted([[x['name'], x['value'], x['size'], x['type']] for x in elf.symbols
                         if x['name'] and not x['name'].startswith('$') and x['size'] and
                         (0x02000000 <= x['value'] < 0x02040000 or 0x03000000 <= x['value'] < 0x03008000)])
    assert actual_ram == reference['RAM_symbols'], 'Named RAM layout changed'
    for row in reference['save_symbols']:
        x = elf.one(row['name']); assert [x['value'], x['size']] == [row['address'], row['bytes']]

    def object_symbol(unit, name):
        obj = parsed[unit]; x = obj.one(name); s = obj.sections[x['ndx']]
        assert s['name'] in placements[unit]
        return placements[unit][s['name']][0]+x['value'], x['size']

    bound = []
    for row in reference['direct_blobs']:
        address, size = object_symbol(row['unit'], row['symbol']); raw = (source/row['source']).read_bytes()
        assert size == len(raw) == row['bytes'] and sha(raw)==row['sha256'] and elf.at(address, size) == raw
        bound.append(dict(unit=row['unit'], symbol=row['symbol'], bytes=size, sha256=sha(raw), source_exact=True))
    assert sum(x['unit'] == 'src/hoenn_space_story.o' for x in bound) == 35
    exterior = reference.get('exterior_revision')
    if exterior:
        assert len(exterior['original_story_inputs_preserved']) == 35
        for row in exterior['original_story_inputs_preserved']:
            raw = (source/row['source']).read_bytes()
            assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
        replaced = exterior['intentional_linked_replacements']
        assert len(replaced) == 9 and len({x['symbol'] for x in replaced}) == 9
        for row in replaced:
            actual = next(x for x in reference['direct_blobs'] if x['unit'] == 'src/hoenn_space_story.o' and x['symbol'] == row['symbol'])
            assert [actual[k] for k in ('source', 'bytes', 'sha256')] == [row['new_source'], row['bytes'], row['sha256']]
    assert sum(x['unit'] == 'src/tilesets.o' for x in bound) == 68
    approved = []
    for name, row in reference['approved_media'].items():
        x = elf.one(name); raw = elf.at(x['value'], row['symbol_size'] if row['symbol_size'] else row['bytes'])
        decoded = lz77(raw) if row['encoding'] == 'LZ77' else raw[:row['bytes']]
        assert len(decoded) == row['bytes'] and sha(decoded) == row['sha256'], ('Approved media changed', name)
        approved.append(dict(symbol=name, bytes=len(decoded), sha256=sha(decoded)))
    field = []
    for row in reference['field_assets']:
        raw = elf.named_bytes(row['name']); assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
        field.append(row['name'])
    assert len(field) == 287
    for row in reference['fixed_symbol_payloads']:
        assert sha(elf.named_bytes(row['name'])) == row['sha256'], ('Fixed sequence changed', row['name'])
    song = reference['credits_song']; raw = bytearray(elf.at(elf.one(song['start_label'])['value'], song['bytes']))
    for word in song['pointer_words']:
        assert struct.unpack_from('<I', raw, word['offset'])[0] == elf.one(word['target'])['value']
        raw[word['offset']:word['offset']+4] = b'\0'*4
    assert sha(raw) == song['normalized_sha256'], 'Credits command/note payload changed'

    groups = load(source/'data/maps/map_groups.json'); layouts = load(source/'data/layouts/layouts.json')['layouts']
    ids = {load(source/'data/maps'/name/'map.json')['id']:(g,n) for g,group in enumerate(groups['group_order']) for n,name in enumerate(groups[group])}
    for g, group in enumerate(groups['group_order']):
        ptr = struct.unpack('<I', elf.at(elf.one('gMapGroups')['value']+4*g, 4))[0]
        assert ptr == elf.one(group)['value']
        for n,name in enumerate(groups[group]):
            assert struct.unpack('<I', elf.at(ptr+4*n, 4))[0] == elf.one(name)['value']
    null_layout_slots = 0
    for i, layout in enumerate(layouts):
        assert isinstance(layout, dict), ('Malformed layout slot', i)
        actual_layout = struct.unpack('<I', elf.at(elf.one('gMapLayouts')['value']+4*i,4))[0]
        expected_layout = 0 if layout == {} else elf.one(layout['name'])['value']
        assert actual_layout == expected_layout, ('Linked layout slot mismatch', i, actual_layout, expected_layout)
        null_layout_slots += int(layout == {})
    contract = load(source/'tools/hoenn_import/space_deck_v4_contract.json'); rooms = []
    tileset_text = (source/'src/data/tilesets/ty_space_deck_v4.h').read_text()
    for room in contract['maps']:
        m = load(source/'data/maps'/room['map']/'map.json'); layout = layouts[room['proposed_layout_num']-1]
        address = elf.one(layout['name'])['value']; width,height,border,blocks,primary,secondary,bw,bh = struct.unpack('<6IBB2x',elf.at(address,28))
        assert [width,height] == room['size'] and [bw,bh] == [layout['border_width'],layout['border_height']]
        assert primary == elf.one(layout['primary_tileset'])['value'] and secondary == elf.one(layout['secondary_tileset'])['value']
        for pointer,rel in [(border,layout['border_filepath']),(blocks,layout['blockdata_filepath'])]:
            raw = (source/rel).read_bytes(); assert elf.at(pointer,len(raw)) == raw
        tile = elf.at(secondary,24); assert tile[:3] == bytes([0,1,1]); pointers = struct.unpack_from('<5I',tile,4); assert pointers[3] == 0
        declaration = re.search(r'const struct Tileset '+layout['secondary_tileset']+r'\s*=\s*\{(.*?)\};',tileset_text,re.S).group(1)
        named = dict(re.findall(r'\.(tiles|palettes|metatiles|metatileAttributes)\s*=\s*(\w+)',declaration))
        for index,key in [(0,'tiles'),(1,'palettes'),(2,'metatiles'),(4,'metatileAttributes')]:
            assert pointers[index] == object_symbol('src/tilesets.o',named[key])[0]
        header = elf.at(elf.one(room['map'])['value'],28); assert struct.unpack_from('<I',header)[0] == address
        assert struct.unpack_from('<H',header,18)[0] == room['proposed_layout_num']
        events = struct.unpack_from('<I',header,4)[0]; ev = elf.at(events,20)
        assert list(ev[:4]) == [len(m['object_events']),len(m['warp_events']),len(m['coord_events']),len(m['bg_events'])]
        actors_ptr,warps_ptr = struct.unpack_from('<II',ev,4)
        for index,obj in enumerate(m['object_events']):
            raw = elf.at(actors_ptr+24*index,24)
            assert struct.unpack_from('<hh',raw,4) == (obj['x'],obj['y'])
            if str(obj.get('local_id','')).isdigit(): assert raw[0] == int(obj['local_id'])
            assert struct.unpack_from('<I',raw,16)[0] == elf.one(obj['script'])['value']
        for index,w in enumerate(m['warp_events']):
            raw = elf.at(warps_ptr+8*index,8); assert struct.unpack_from('<hh',raw) == (w['x'],w['y'])
            assert [raw[7],raw[6]] == list(ids[w['dest_map']]) and raw[5] == int(w['dest_warp_id'])
        if room['map'] == 'HoennSpacecraftCabin':
            pc=next(a for a in room['interaction_tiles'] if a['script_label']=='SpaceFacility_PC');tx,ty=pc['target'];sx,sy=pc['stand']
            raw = elf.at(blocks,width*height*2); target = struct.unpack_from('<H',raw,2*(ty*width+tx))[0]; stand=struct.unpack_from('<H',raw,2*(sy*width+sx))[0]
            assert target&1023 == 1005 and stand>>10&3 == 0
            for n in (1005,1006): assert struct.unpack('<I',elf.at(pointers[4]+4*(n-512),4))[0]&511 == 0x83
        rooms.append(dict(map=room['map'], layout=room['proposed_layout_num'], linked_actors=len(m['object_events']), linked_warps=len(m['warp_events'])))
    return dict(status='COMPILED_SOURCE_LINK_AND_ART_PASS_GAMEPLAY_PENDING', provenance_sha256=sha(provenance_path.read_bytes()),
                source_commit=p['source_commit'], ELF_ROM_sections=all_sections, object_proofs=object_proofs,
                compiled_abi=abi, RAM_symbols=len(actual_ram), save_symbols=len(reference['save_symbols']),
                direct_blobs=bound, intentional_exterior_replacements=exterior['intentional_linked_replacements'] if exterior else [],
                original35_source_inputs_preserved=bool(exterior),
                approved_media=approved, original_field_assets=len(field), linked_rooms=rooms,
                all_maps=1040, all_layouts=862, null_layout_slots=null_layout_slots, limits=['No emulator or installed iOS Delta execution.',
                'Facilities, mission branches, battles, followers, normal SAVE and cold Continue require separate actual-play evidence.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--artifact-dir',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--reference-manifest',type=Path,required=True)
    parser.add_argument('--source-only',action='store_true')
    parser.add_argument('--skip-poses',action='store_true',help='Explicitly omit offline model; never implies runtime coverage')
    a=parser.parse_args(); assert a.source_only or a.artifact_dir is not None
    assert not a.out.exists() and not a.out.resolve().is_relative_to(a.source.resolve())
    a.out.mkdir(parents=True)
    try:
        reference=load(a.reference_manifest); assert reference['schema']=='TY_SPACE_PUBLIC_REFERENCE_V1'
        source_result=check_source(a.source,reference,with_poses=not a.skip_poses)
        (a.out/'source-art.json').write_text(json.dumps(source_result,indent=2)+'\n')
        result=dict(status='SOURCE_OFFLINE_ONLY_LINKED_NOT_RUN', source=source_result, compiled_checks_executed=0,
                    operations=dict(builds=0,compilers=0,games=0,DLLs=0,source_writes=0))
        if not a.source_only:
            result['linked']=linked(a.source,a.artifact_dir,a.reference_manifest,reference)
            result['status']=result['linked']['status']; result['compiled_checks_executed']=1
        (a.out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(status=result['status'],result_sha256=sha((a.out/'result.json').read_bytes()))))
    except Exception as error:
        (a.out/'error.json').write_text(json.dumps(dict(status='VERIFICATION_STOP_NO_PASS',error=repr(error),traceback=traceback.format_exc()),indent=2)+'\n')
        raise


if __name__=='__main__':
    main()
