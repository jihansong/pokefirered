"""Pure source, original-pixel and foreground-mask checks. Never starts a game."""
from collections import deque
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import re
import runpy
import struct


EMBEDDED = {
    'data/mb_berry_fix.gba': ('0afff07f5d2314e2bd35d99de518cbc114009b5e', 15348),
    'data/mb_colosseum.gba': ('2ff3f88bcc4a807954e3576f354e88612ef68bf9', 163840),
    'data/mb_ereader.gba': ('63d26ca2af53300a62611f46d540c49154d6b8af', 14176),
}
BLOCKED_EXTENSIONS = {'.sav', '.srm', '.sa1', '.sgm', '.elf', '.o', '.exe', '.dll', '.so', '.sym', '.pyc', '.pyo', '.zip', '.7z', '.bak'}
TEXT_EXTENSIONS = {'.c', '.h', '.s', '.inc', '.py', '.md', '.json', '.mk', '.txt', '.ld', '.yml', '.yaml', '.toml'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def json_hash(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode())


def public_scan(root, relative_files=None):
    """Reject local paths, personal-only hooks and runtime artifacts by default.

    Exact public R23 source selection is checked by the reference manifest.
    Private save identities are never encoded in this public scanner.
    """
    root = Path(root); count = 0
    forbidden_text = [re.compile(r'[A-Za-z]:[/\\]+Users[/\\]+', re.I),
                      re.compile('/' + r'Users/[^\s/]+/'),
                      re.compile(r'\b(?:IsPlayerCustom\w+|ScalePlayer\w+Stat)\b')]
    paths=(root/n for n in relative_files) if relative_files is not None else root.rglob('*')
    for p in paths:
        if not p.is_file() or '.git' in p.parts:
            continue
        rel = p.relative_to(root).as_posix(); count += 1
        assert not any(x in {'__pycache__', 'backups', 'reference', 'saves'} for x in p.relative_to(root).parts)
        assert p.suffix.lower() not in BLOCKED_EXTENSIONS, ('Forbidden public artifact', rel)
        if p.suffix.lower() == '.gba':
            assert rel in EMBEDDED, ('Only three original embedded source payloads are allowed', rel)
            expected, size = EMBEDDED[rel]; raw = p.read_bytes()
            assert len(raw) == size
            assert hashlib.sha1(b'blob '+str(size).encode()+b'\0'+raw).hexdigest() == expected
        if p.suffix.lower() in TEXT_EXTENSIONS or p.name == 'Makefile':
            try: text = p.read_text('utf-8-sig')
            except UnicodeDecodeError: continue
            for pattern in forbidden_text:
                assert not pattern.search(text), ('Private-only content or local path', rel)
    return dict(files=count, private_values_in_scanner=False, embedded_source_exceptions=sorted(EMBEDDED),scope='Explicit sparse source input projection; unrelated Git files/history excluded')


def pose_checks(source, contract, build_proof):
    """Check actual source sprite frames against real BG foreground masks."""
    from PIL import Image, ImageChops
    source = Path(source)
    from space_pose_scope_v18 import domains, allowed_foot
    pose_domains = domains(source, contract)
    allowed_occlusions = []
    excluded_cells = []
    npc_total = 0
    pointer = (source/'src/data/object_events/object_event_graphics_info_pointers.h').read_text('utf-8-sig')
    infos = (source/'src/data/object_events/object_event_graphics_info.h').read_text('utf-8-sig')
    pics = (source/'src/data/object_events/object_event_pic_tables.h').read_text('utf-8-sig')
    images = (source/'src/data/object_events/object_event_graphics.h').read_text('utf-8-sig')

    movement = (source/'src/event_object_movement.c').read_text('utf8')
    match = re.search(r'const struct ObjectEventGraphicsInfo \*GetObjectEventGraphicsInfo\(u8 graphicsId\)\s*\{(.*?)\n\}', movement, re.S)
    assert match, 'Source graphics selector missing'
    selector = match.group(1)
    scoped_branch = re.search(
        r'if\s*\(\s*graphicsId\s*==\s*OBJ_EVENT_GFX_CABLE_CLUB_RECEPTIONIST\s*'
        r'&&\s*gSaveBlock1Ptr->location.mapGroup\s*==\s*MAP_GROUP\(MAP_HOENN_SPACECRAFT_CABIN\)\s*'
        r'&&\s*gSaveBlock1Ptr->location.mapNum\s*==\s*MAP_NUM\(MAP_HOENN_SPACECRAFT_CABIN\)\s*\)\s*'
        r'return\s*&gObjectEventGraphicsInfo_SpaceBoardingGuide\s*;', selector)
    assert scoped_branch and selector.count('&gObjectEventGraphicsInfo_SpaceBoardingGuide') == 1
    assert scoped_branch.start() < selector.index('return gObjectEventGraphicsInfoPointers[graphicsId]')

    @lru_cache(None)
    def sprite(gfx, map_name):
        info = ('gObjectEventGraphicsInfo_SpaceBoardingGuide'
                if map_name == 'HoennSpacecraftCabin' and gfx == 'OBJ_EVENT_GFX_CABLE_CLUB_RECEPTIONIST'
                else re.search(r'\['+re.escape(gfx)+r'\]\s*=\s*&(\w+)', pointer).group(1))
        body = re.search(r'const struct ObjectEventGraphicsInfo '+info+r'\s*=\s*\{(.*?)\};', infos, re.S).group(1)
        width = int(re.search(r'\.width\s*=\s*(\d+)', body).group(1)); height = int(re.search(r'\.height\s*=\s*(\d+)', body).group(1))
        table = re.search(r'\.images\s*=\s*(\w+)', body).group(1)
        body = re.search(r'static const struct SpriteFrameImage '+table+r'\[\]\s*=\s*\{(.*?)\};', pics, re.S).group(1)
        frames = []
        for image, index in re.findall(r'overworld_frame\((\w+),\s*\d+,\s*\d+,\s*(\d+)\)', body):
            rel = re.search(r'const u16 '+image+r'\[\]\s*=\s*INCBIN_U16\("([^"]+)"', images).group(1).replace('.4bpp', '.png')
            frames.append((rel, int(index)))
        assert frames, gfx
        return width, height, frames

    @lru_cache(None)
    def actor(gfx, frame, flip=False, map_name=None):
        width, height, frames = sprite(gfx, map_name); rel, index = frames[frame if frame < len(frames) else 0]
        image = Image.open(source/rel).crop((width*index, 0, width*(index+1), height))
        pixels = image.get_flattened_data() if hasattr(image, 'get_flattened_data') else image.getdata()
        mask = Image.frombytes('L', image.size, bytes(255 if v else 0 for v in pixels))
        return mask.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if flip else mask

    poses = [(0, False), (3, False), (4, False), (1, False), (5, False), (6, False),
             (2, False), (7, False), (8, False), (2, True), (7, True), (8, True)]
    characters = ['OBJ_EVENT_GFX_RED_NORMAL', 'OBJ_EVENT_GFX_PIKACHU', 'OBJ_EVENT_GFX_MISTY_COMPANION']
    layouts = json.loads((source/'data/layouts/layouts.json').read_bytes())['layouts']; results = []; total = 0
    for room in contract['maps']:
        record = next(x for x in build_proof['maps'] if x['map'] == room['map'])
        folder = source/record['folder']; tiles = (folder/'tiles.4bpp').read_bytes()
        metatiles = (folder/'metatiles.bin').read_bytes(); attributes = (folder/'metatile_attributes.bin').read_bytes()
        m = json.loads((source/'data/maps'/room['map']/'map.json').read_bytes())
        layout = next(x for x in layouts if x.get('id') == m['layout']); width, height = room['size']
        raw = (source/layout['blockdata_filepath']).read_bytes(); cells = struct.unpack('<%dH' % (len(raw)//2), raw)
        foreground = Image.new('L', (width*16, height*16))
        for index, word in enumerate(cells):
            n = word & 1023; assert n >= 512
            kind = struct.unpack_from('<I', attributes, (n-512)*4)[0] >> 29 & 3
            assert kind in (0, 1, 2)
            if kind == 1: continue
            upper = struct.unpack_from('<4H', metatiles, (n-512)*16+8)
            tile = Image.new('L', (16, 16))
            for corner, value in enumerate(upper):
                t = (value&1023)-512; assert t >= 0
                pixels = tiles[t*32:(t+1)*32]; assert len(pixels) == 32
                for y in range(8):
                    for x in range(8):
                        xx = 7-x if value&1024 else x; yy = 7-y if value&2048 else y
                        color = pixels[yy*4+xx//2] >> (4*(xx&1)) & 15
                        tile.putpixel((corner%2*8+x, corner//2*8+y), 255 if color else 0)
            foreground.paste(tile, (index%width*16, index//width*16))
        checked = 0
        domain = pose_domains[room['map']]
        for xx, yy in sorted(domain['excluded']):
            tile_id = cells[yy*width+xx] & 1023
            excluded_cells.append(dict(map=room['map'], xy=[xx, yy],
                source_ref=record['metatile_source_map'][str(tile_id)],
                reason='No path from safe anchor or any normal door arrival; NPC domain checked separately'))
        for index, word in enumerate(cells):
            if word >> 10 & 3: continue
            x, y = index%width, index//width
            if (x, y) not in domain['player']: continue
            for gfx in characters:
                for frame, flip in poses:
                    mask = actor(gfx, frame, flip, room['map']); xx, yy = x*16, y*16+16-mask.height
                    hit = ImageChops.multiply(mask, foreground.crop((xx, yy, xx+mask.width, yy+mask.height)))
                    if hit.getbbox():
                        allowance = allowed_foot(room['map'], (x,y), gfx, mask.height, hit.getbbox(),
                            record['metatile_source_map'][str(word & 1023)])
                        assert allowance, ('Reachable player head/body foreground overlap', room['map'], x, y, gfx, frame, flip, hit.getbbox())
                        allowance.update(frame=frame, flip=flip, domain='normal_player')
                        allowed_occlusions.append(allowance)
                    checked += 1
        npc_checked = 0
        for npc in domain['npcs']:
            obj = npc['object']; local = npc['local_id']
            for px, py in sorted(npc['points']):
                for frame, flip in poses:
                    mask = actor(obj['graphics_id'], frame, flip, room['map'])
                    xx, yy = px*16, py*16+16-mask.height
                    hit = ImageChops.multiply(mask, foreground.crop((xx,yy,xx+mask.width,yy+mask.height)))
                    if hit.getbbox():
                        tile_id = cells[py*width+px] & 1023
                        allowance = allowed_foot(room['map'], (px,py), obj['graphics_id'], mask.height,
                            hit.getbbox(), record['metatile_source_map'][str(tile_id)], local)
                        assert allowance, ('NPC spawn/wander head/body foreground overlap', room['map'],local,px,py,frame,flip,hit.getbbox())
                        allowance.update(frame=frame, flip=flip, domain='NPC_spawn_or_bounded_wander')
                        allowed_occlusions.append(allowance)
                    npc_checked += 1
        npc_total += npc_checked
        total += checked; results.append(dict(map=room['map'], character_pose_checks=checked, untyped_foreground_overlaps=0, NPCs=len(m['object_events']), npc_pose_checks=npc_checked, player_domain_cells=len(domain['player']), normal_arrival_seeds=sorted(domain['seeds']), npc_domains=[dict(local_id=n['local_id'],points=sorted(n['points'])) for n in domain['npcs']], literal_movements=domain['literal_movements']))
    return dict(scoped_graphics_choice={'map':'HoennSpacecraftCabin','graphics_id':'OBJ_EVENT_GFX_CABLE_CLUB_RECEPTIONIST','info':'gObjectEventGraphicsInfo_SpaceBoardingGuide','source_function':'GetObjectEventGraphicsInfo'}, total_character_pose_checks=total, total_npc_pose_checks=npc_total, rooms=results, excluded_player_cells=excluded_cells, typed_native_counter_foot_occlusions=allowed_occlusions, untyped_head_body_overlaps=0, scope='Normal-arrival player flood and actual NPC spawn/bounded-wander masks; only named native counter final-four-row foot occlusion is allowed. Runtime camera/OAM/follower spacing remains separate')


def check_source(source, reference, with_poses=True):
    source = Path(source); scan = public_scan(source,reference['files'])
    for rel, row in reference['files'].items():
        raw = (source/rel).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], ('Source drift', rel)
    assert sha((source/'src/pokemon.c').read_bytes()) == reference['public_pokemon_sha256']
    groups = json.loads((source/'data/maps/map_groups.json').read_bytes())
    layouts = json.loads((source/'data/layouts/layouts.json').read_bytes())['layouts']
    assert len(groups['group_order']) == 77 and sum(len(groups[n]) for n in groups['group_order']) == 1040 and len(layouts) == 862
    contract = json.loads((source/'tools/hoenn_import/space_deck_v4_contract.json').read_bytes())
    assert json_hash(contract['maps']) == reference['room_contract_geometry_sha256']
    by_name = {x['map']:x for x in contract['maps']}; warps = 0
    for room in contract['maps']:
        m = json.loads((source/'data/maps'/room['map']/'map.json').read_bytes())
        assert groups[groups['group_order'][69]][room['proposed_map_num']] == room['map']
        assert layouts[room['proposed_layout_num']-1]['id'] == m['layout']
        assert len(m['warp_events']) == len(room['warps'])
        for w in room['warps']:
            actual = m['warp_events'][w['id']]; target = by_name[w['destination']]
            reverse = target['warps'][w['destination_warp']]
            dest_map = json.loads((source/'data/maps'/target['map']/'map.json').read_bytes())['id']
            assert [actual['x'], actual['y']] == w['xy'] and actual['dest_map'] == dest_map
            assert actual['dest_warp_id'] == str(w['destination_warp']) or actual['dest_warp_id'] == w['destination_warp']
            assert reverse['destination'] == room['map'] and reverse['destination_warp'] == w['id']
            warps += 1
    assert len(contract['maps']) == 17 and warps == 32
    builder = runpy.run_path(str(source/'tools/hoenn_import/build_space_decks_v4.py'))
    outputs, proof = builder['build'](source, contract)
    assert len(outputs) == 137 and all((source/p).read_bytes() == raw for p, raw in outputs.items())
    result = dict(status='SOURCE_AND_OFFLINE_ART_ONLY_NOT_COMPILED_OR_GAMEPLAY', frozen_source_files=len(reference['files']), public_scan=scan,
                  maps=1040, layouts=862, interiors=17, reciprocal_warp_pairs=16, pure_regenerated_art_outputs=137,
                  source_writes=0, compilers=0, game_runs=0)
    if with_poses:
        result['pose_model'] = pose_checks(source, contract, proof)
        assert result['pose_model']['total_character_pose_checks'] == reference['offline_pose_checks']
        assert result['pose_model']['total_npc_pose_checks'] == reference['offline_npc_pose_checks']
    return result
