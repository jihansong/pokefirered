"""R7 constant/header and complete dependency preflight; actual Misty walk/run frame QA; separate preboot story/position fixtures.

No engine calls or RAM writes. Existing player Pokemon/PC/Dex remain unchanged.
This is not full campaign traversal, actual DELTA FPS or art approval.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, struct, sys, traceback

p=argparse.ArgumentParser(description=__doc__)
for name in ['rom','elf','sav','out','expect-rom-sha','expect-elf-sha','expect-sav-sha']:
    p.add_argument('--'+name,required=True)
p.add_argument('--root',default='/workspaces/pokefirered')
p.add_argument('--verifier',required=True)
p.add_argument('--guard-manifest',required=True)
cfg=p.parse_args();root=Path(cfg.root).resolve();os.chdir(root)
inputs={Path(cfg.rom).resolve():cfg.expect_rom_sha,Path(cfg.elf).resolve():cfg.expect_elf_sha,Path(cfg.sav).resolve():cfg.expect_sav_sha}
qa_hash_bytes=lambda x:hashlib.sha256(x).hexdigest()
for f,wanted in inputs.items():assert qa_hash_bytes(f.read_bytes())==wanted,(f,'SHA mismatch')
target=Path(cfg.out).resolve();assert target.is_relative_to(root/'work') and not target.exists()
target.mkdir(parents=True)
sys.path.insert(0,str(root/'tools/qa'))
import gamedata as gd
# Process-local QA include list; the guarded product header/helper is unchanged.
if 'constants/event_objects.h' not in gd.CONST_HEADERS:gd.CONST_HEADERS.append('constants/event_objects.h')
gd.CACHE=str(target/'compiler-cache');gd._OFFSETS=None
sys.argv=['native-walk','--rom',cfg.rom,'--elf',cfg.elf,'--sav',cfg.sav,'--out',str(target)]
basic_path=root/'tools/qa/native_misty_basic_qa.py'
basic=basic_path.read_text();assert qa_hash_bytes(basic.encode())=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
assert basic.count('results=[];rows=[]\n')==1
exec(compile(basic.split('results=[];rows=[]\n')[0],'<verified-basic-definitions-only>','exec'))
def forbidden(*unused,**kw):raise AssertionError('Direct engine call/RAM fixture forbidden in walk QA')
call=flag=trail=forbidden
verifier_path=Path(cfg.verifier).resolve()
assert qa_hash_bytes(verifier_path.read_bytes())=='40647f774f3e470ffc29b29f82ef2fb188c0473d983f87f72d6d7e3d1642c200'
vspec=importlib.util.spec_from_file_location('current_native_elf_verifier',verifier_path)
v=importlib.util.module_from_spec(vspec);sys.modules[vspec.name]=v;vspec.loader.exec_module(v)
current_elf=v.Elf(elf)
required_symbols=['gMain','gSprites','gObjectEvents','gPlayerAvatar','gPlayerParty','gPlayerPartyCount',
                  'gSaveBlock1Ptr','gSaveBlock2Ptr','gPokemonStoragePtr','gSaveCounter','gSaveAttemptStatus',
                  'gObjectEventPic_MistyCompanion','gObjectEventPal_Player','CB2_Overworld','BattleMainCB2',
                  'sNumStartMenuItems','sStartMenuOrder','sStartMenuCursorPos','sGlobalScriptContextStatus','sLockFieldControls']
from emu import BOOT_CALLBACKS
qa_defined_symbol_names = {row.name for row in current_elf.symbols}
qa_absent_optional_boot_callbacks = [name for name in BOOT_CALLBACKS if name not in qa_defined_symbol_names]
required_symbols += ['CB2_MainMenu','gQuestLogState','gQuestLogPlaybackState',
                     'gTypeEffectiveness','gStringVar4','JohtoRoute29_Text_Hiker','JohtoRoute29_Text_Sign'] + [name for name in BOOT_CALLBACKS if name in qa_defined_symbol_names]
required_symbols = sorted(set(required_symbols))
unique_bindings={name:current_elf.unique(name) for name in required_symbols}
for name,row in unique_bindings.items():syms[name]=(row.addr & ~1) if row.kind == 2 else row.addr
r.syms=syms
assert v.segment_match(current_elf,r.data)['pass']
source_guard=json.loads(Path(cfg.guard_manifest).read_text())
for rel,want in source_guard['guarded_sources'].items():assert qa_hash_bytes((root/rel).read_bytes())==want,('current source guard differs',rel)
for rel,row in source_guard['product_inputs'].items():assert qa_hash_bytes((root/rel).read_bytes())==row['after_sha256'],('integrated candidate absent',rel)
gd.FIELDS.update({'walk.obj.gfx':('ObjectEvent','graphicsId'),'walk.sprite.oam':('Sprite','oam'),
                  'walk.sprite.anim':('Sprite','animNum'),'walk.sprite.cmd':('Sprite','animCmdIndex'),'walk.player.objectId':('PlayerAvatar','objectEventId'),'walk.daycare.stepCounter':('DayCare','stepCounter'),'walk.daycare':('DayCare',None)})
gd._OFFSETS=None
# Resolve every constant, registered offset, and reachable map before creating
# a fixture or opening the emulator. Includes indirect SaveFile flag/var helpers.
qa_constant_names = sorted(set([
    'OBJ_EVENT_GFX_MISTY_COMPANION','QUEST_LOG_SCENE_COUNT','NUM_SPECIES',
    'VARS_COUNT','VARS_START','VARS_END','HOENN_VARS_START','HOENN_VARS_END',
    'HOENN_FLAGS_START','HOENN_FLAGS_COUNT','FLAGS_COUNT',
    'FLAG_MISTY_COMPANION_JOINED','FLAG_HIDE_MISTY_PALLET','FLAG_SYS_GAME_CLEAR',
    'FLAG_RECEIVED_STARTER_PIKACHU','FLAG_JOHTO_ARRIVAL_BRIEFED','FLAG_JOHTO_MET_LAB_ASSISTANT',
    'VAR_MAP_SCENE_PALLET_TOWN_OAK','VAR_TEMP_7','VAR_HAPPINESS_STEP_COUNTER','VAR_REPEL_STEP_COUNT'] + K))
qa_resolved_constants = gd.consts(qa_constant_names)
qa_resolved_offsets = {name:off(name) for name in sorted(gd.FIELDS)}
assert qa_resolved_offsets['sb1.pos']==0 and qa_resolved_offsets['sb1.location']==4
assert qa_resolved_offsets['pokemon']==100 and qa_resolved_offsets['boxmon']==80
assert qa_resolved_offsets['sb1']==15720 and qa_resolved_offsets['sb2']==3876 and qa_resolved_offsets['storage']==33744
assert qa_resolved_offsets['misty_obj']==36 and qa_resolved_offsets['misty_sprite']==68
assert qa_resolved_constants['VARS_START']<=qa_resolved_constants['VAR_TEMP_7']<=qa_resolved_constants['VARS_END']
qa_resolved_maps = {name:map_info(name) for name in ['PalletTown','JohtoRoute29','JohtoCherrygroveAirstrip','NewBarkTown']}
qa_dependencies = {'pass':True,'process_local_added_header':'constants/event_objects.h',
    'guarded_header_sha256':qa_hash_bytes((root/'include/constants/event_objects.h').read_bytes()),
    'resolved_constants':qa_resolved_constants,'resolved_offsets':qa_resolved_offsets,
    'maps':{name:{k:row[k] for k in ('group','num','layout_id','layout','id')} for name,row in qa_resolved_maps.items()},
    'VAR_TEMP_7_preboot_SAV_location_validated':True,
    'absent_optional_boot_callbacks':qa_absent_optional_boot_callbacks,
    'unique_ELF_bindings':{name:dict(addr=hex(row.addr),size=row.size,owner=row.unit) for name,row in unique_bindings.items()}}
(out/'dependency-preflight.json').write_text(json.dumps(qa_dependencies,indent=2)+'\n')
GFX=const('OBJ_EVENT_GFX_MISTY_COMPANION');assert GFX==237
PIC='gObjectEventPic_MistyCompanion';assert PIC in syms
frame_data=r.at(syms[PIC],9*256);expected={qa_hash_bytes(frame_data[i*256:(i+1)*256]):i for i in range(9)}
assert len(expected)>=7,'Compiled walking art lacks distinct image frames'
protected={f.resolve():qa_hash_bytes(f.read_bytes()) for f in set((root/'saves').rglob('*.sav'))|set(inputs)|{basic_path}}
report={'pass':False,'status':'running','scope':'preboot position/story and egg-step-counter visual fixtures; actual walk/run keys and SAVE/cold, not natural story completion or mobile FPS',
        'ROM_sha256':inputs[Path(cfg.rom).resolve()],'ELF_sha256':inputs[Path(cfg.elf).resolve()],
        'SAV_sha256':inputs[Path(cfg.sav).resolve()],'dependency_preflight':qa_dependencies,'RAM_writes':0,'engine_calls':0,'preboot_visual_fixtures':True,'natural_story_completion':False,'current_compiler_cache_isolated':True,'unique_ELF_bindings':{name:dict(addr=hex(row.addr),size=row.size,owner=row.unit) for name,row in unique_bindings.items()},'cases':[],'native_samples':[]}
protected.update({verifier_path:qa_hash_bytes(verifier_path.read_bytes()),Path(cfg.guard_manifest).resolve():qa_hash_bytes(Path(cfg.guard_manifest).read_bytes()),Path(__file__).resolve():qa_hash_bytes(Path(__file__).read_bytes())})
for rel,want in source_guard['guarded_sources'].items():protected[(root/rel).resolve()]=want
for rel,row in source_guard['product_inputs'].items():protected[(root/rel).resolve()]=row['after_sha256']

def emit():(out/'walk-validation.json').write_text(json.dumps(report,indent=2)+'\n')
e=None

def pixel_sample(tag):
    rows=object_rows(e,253)
    assert len(rows)==1,'Joined fixture has no runtime Misty'
    row=rows[0]
    assert e.u8(row['ptr']+off('walk.obj.gfx'))==GFX,'Runtime Misty uses original swimsuit GFX'
    if not row['visible']:return None
    sp=syms['gSprites']+68*row['sprite'];o=sp+off('walk.sprite.oam')
    a0,a1,a2=struct.unpack('<HHH',e.read(o,6));shape=a0>>14;size=a1>>14
    dimensions=[[(8,8),(16,16),(32,32),(64,64)],[(16,8),(32,8),(32,16),(64,32)],[(8,16),(8,32),(16,32),(32,64)]]
    assert shape<3
    w,h=dimensions[shape][size];assert (w,h)==(16,32),(shape,size,w,h)
    assert not a0&0x2000,'Expected 4bpp Misty native art'
    tile=a2&1023;one_d=bool(e.u16(0x04000000)&64);pitch=(w//8)*32 if one_d else 32*32
    vram=b''.join(e.read(0x06010000+tile*32+yy*pitch,(w//8)*32) for yy in range(h//8))
    digest=qa_hash_bytes(vram)
    # Only post-VBlank native bytes are evidence. Unknown transitional DMA bytes
    # are recorded but cannot satisfy the walking-frame assertion.
    sample={'tag':tag,'frame':e.frame(),'player':e.location(),'Misty_feet':row['feet'],
            'Misty_xy':row['xy'],'sprite':row['sprite'],'gfx':GFX,'anim':e.u8(sp+off('walk.sprite.anim')),
            'anim_cmd':e.u8(sp+off('walk.sprite.cmd')),'VRAM_sha256':digest,
            'compiled_frame':expected.get(digest),'palette_slot':a2>>12,'hflip':bool(a1&0x1000),'size':[w,h]}
    player_object=e.u8(syms['gPlayerAvatar']+off('walk.player.objectId'));assert player_object<16
    player_sprite=e.u8(syms['gObjectEvents']+player_object*off('misty_obj')+off('misty_obj.sprite'));assert player_sprite<64
    player_oam=syms['gSprites']+player_sprite*off('misty_sprite')+off('walk.sprite.oam')
    player_palette=e.u16(player_oam+4)>>12
    assert sample['palette_slot']==player_palette,'Misty OAM lost shared player palette slot'
    runtime_palette=e.read(0x05000200+sample['palette_slot']*32,32)
    source_palette=r.at(syms['gObjectEventPal_Player'],32)
    sample.update(player_palette_slot=player_palette,runtime_palette_BGR555_sha256=qa_hash_bytes(runtime_palette),
                  source_palette_BGR555_sha256=qa_hash_bytes(source_palette),runtime_palette_equals_unfaded_source=runtime_palette==source_palette)
    report['native_samples'].append(sample)
    if tag in [d+'-walk-'+str(i) for d in ('RIGHT','UP','DOWN') for i in (3,4)] and e.frame()%3==0:
        shots=out/'actual-walk-frames';shots.mkdir(exist_ok=True)
        e.shot(str(shots/('%08d.png'%e.frame())),scale=3)
    return sample

def line_fixture(direction):
    meta=json.loads((root/'data/maps/PalletTown/map.json').read_text())
    layouts=json.loads((root/'data/layouts/layouts.json').read_text())['layouts']
    layout=[x for x in layouts if x.get('id')==meta['layout']];assert len(layout)==1
    layout=layout[0];w,h=layout['width'],layout['height'];terrain=(root/layout['blockdata_filepath']).read_bytes()
    assert len(terrain)==2*w*h
    blocked=set()
    for kind in ['warp_events','coord_events','bg_events','object_events']:
        for obj in meta.get(kind,[]) or []:
            # Joined Misty is absent from the static map. Other wandering NPCs
            # are kept outside the whole test line and its adjacent tiles.
            if obj.get('script')=='PalletTown_EventScript_MistyJoin':continue
            if kind == "object_events" and obj.get("flag") == "FLAG_HIDE_OAK_IN_PALLET_TOWN":
                assert const("FLAG_HIDE_OAK_IN_PALLET_TOWN") == 44 and off("sb1.flags") == 3808
                assert SaveFile(str(sav)).sb1[3808 + 44//8] & (1 << (44%8)), "Oak is active; preserve blocker"
                continue
            ox,oy=obj.get('x',-100),obj.get('y',-100)
            # Non-object signs do not activate while walking past them. Warp
            # and coordinate tiles themselves are still excluded.
            rx,ry=(obj.get('movement_range_x',0)+1,obj.get('movement_range_y',0)+1) if kind=='object_events' else (0,0)
            blocked.update((x,y) for x in range(ox-rx,ox+rx+1) for y in range(oy-ry,oy+ry+1))
    dx,dy={'RIGHT':(1,0),'LEFT':(-1,0),'UP':(0,-1),'DOWN':(0,1)}[direction]
    lines=[]
    for y in range(1,h-1):
        for x in range(1,w-1):
            pts=[(x+i*dx,y+i*dy) for i in range(6)]
            if all(0<=a<w and 0<=b<h and (a,b) not in blocked and struct.unpack_from('<H',terrain,2*(b*w+a))[0]==0x3296 for a,b in pts):lines.append(pts)
    assert lines,('No six-tile verified quiet Pallet grass line',direction)
    # Prefer the previously native-tested row when available.
    lines.sort(key=lambda pts:(pts[0][1]!=9,abs(pts[0][0]-5),pts[0]))
    pts=lines[0];s=SaveFile(str(sav));source=(bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]),bytes(s.blocks['storage']),[s.dex_state(i) for i in range(1,387)])
    s.warp('PalletTown',*pts[0]);s.set_flag(join,True);s.set_flag('FLAG_SYS_GAME_CLEAR',True)
    for f in K:s.set_flag(f,True)
    s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True);s.set_flag(hide,True)
    s.set_var('VAR_MAP_SCENE_PALLET_TOWN_OAK',3);s.set_var('VAR_TEMP_7',0)
    s.set_var('VAR_HAPPINESS_STEP_COUNTER',0);s.set_var('VAR_REPEL_STEP_COUNT',250)
    # QA-only preboot setup avoids unrelated natural hatch during short art cases.
    s.sb1[off('sb1.daycare')+off('walk.daycare.stepCounter')]=0
    for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
    assert (bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]),bytes(s.blocks['storage']),[s.dex_state(i) for i in range(1,387)])==source
    f=out/(direction.lower()+'-preboot-QA-only.sav');s.save(str(f));return f,pts

def step_record(direction,run,label):
    start=e.location();dx,dy={'RIGHT':(1,0),'LEFT':(-1,0),'UP':(0,-1),'DOWN':(0,1)}[direction]
    want=(*start[:2],start[2]+dx,start[3]+dy)
    e.hold(*([direction,'B'] if run else [direction]))
    try:
        for _ in range(120):
            e.run(1);safe(e);pixel_sample(label)
            if e.location()!=start:break
        else:raise AssertionError(('Native step blocked',start,direction))
    finally:e.hold()
    assert e.location()==want,('Native step overshot',e.location(),want)
    if run:assert e.u8(syms['gPlayerAvatar'])&128,'B input did not enter native DASH'
    for _ in range(90):
        safe(e);pixel_sample(label)
        if e.field_idle():break
        e.run(1)
    else:raise AssertionError('Native step failed to settle')
    for _ in range(40):
        e.run(1);safe(e);pixel_sample(label)
    assert e.location()==want


def persistence_record(b,party,count,pc,position):
    trainer_start=off('sb2.hoennTrainerFlags');flags_start=off('sb2.hoennFlags');vars_start=off('sb2.hoennVars');dx=(const('NUM_SPECIES')+7)//8
    return {'party':bytes(party),'count':count,'pc':bytes(pc),'position':tuple(position),
            'flags_raw':bytes(b.sb1[off('sb1.flags'):off('sb1.vars')]),
            'vars_raw':bytes(b.sb1[off('sb1.vars'):off('sb1.vars')+const('VARS_COUNT')*2]),
            'dex':[b.dex_state(i) for i in range(1,387)],
            'dex_raw':bytes(b.sb1[off('sb1.seen1'):off('sb1.seen1')+dx]+b.sb1[off('sb1.seen2'):off('sb1.seen2')+dx]+b.sb2[off('sb2.pokedex')+off('dex.owned'):off('sb2.pokedex')+off('dex.owned')+dx]+b.sb2[off('sb2.pokedex')+off('dex.seen'):off('sb2.pokedex')+off('dex.seen')+dx]),
            'daycare':bytes(b.sb1[off('sb1.daycare'):off('sb1.daycare')+off('walk.daycare')]),
            'hoenn_trainers':bytes(b.sb2[trainer_start:flags_start]),
            'hoenn_flags':bytes(b.sb2[flags_start:vars_start]),
            'hoenn_vars':bytes(b.sb2[vars_start:vars_start+(const('HOENN_VARS_END')-const('HOENN_VARS_START')+1)*2])}


def persistence_live():
    return persistence_record(blocks(e),e.read(syms['gPlayerParty'],600),e.u8(syms['gPlayerPartyCount']),
                              e.read(e.ptr('gPokemonStoragePtr'),off('storage')),e.location())


def flash_reload(e,name):
    # Reuse the proven real menu-SAVE controller; extend comparison to all
    # saved story flag/var blocks instead of a handful of selected flags.
    before=persistence_live();counters=native_save(e);assert counters[1]==counters[0]+1
    live=persistence_live();assert before==live,('SAVE changed preserved logical fields',[k for k in before if before[k]!=live[k]])
    e.run(30);e.lib.qa_close(e.h);e.h=None
    stored=SaveFile(e.sav_path)
    for _,sid,size in stored.layout:
        pos=stored.where[sid]*4096
        assert checksum(stored.raw[pos:pos+size])==struct.unpack_from('<H',stored.raw,pos+0xff6)[0]
    assert stored.counter==counters[1] and len(stored.layout)==14
    stored_position=(*struct.unpack_from('<bb',stored.sb1,off('sb1.location')),*struct.unpack_from('<hh',stored.sb1,off('sb1.pos')))
    saved=persistence_record(stored,stored.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600],stored.party_count(),stored.blocks['storage'],stored_position)
    assert saved==live,('Stored bytes differ from live saved fields',[k for k in saved if saved[k]!=live[k]])
    dst=out/(name+'-native-QA-only.sav');assert not dst.exists();dst.write_bytes(Path(e.sav_path).read_bytes())
    e.h=e.lib.qa_open(str(rom).encode(),str(e.sav_path).encode());assert e.h
    e.boot_continue();settle(e);cold=persistence_live()
    assert cold==live,('Cold-load differs',[k for k in cold if cold[k]!=live[k]])
    return {'counter':counters,'checksummed_sectors':len(stored.layout),'qa_save':str(dst),
            'party_PC_location_all_flags_vars_fourfold_dex_live_stored_cold_equal':True}

try:
    for direction in ['RIGHT','LEFT','UP','DOWN']:
        fixture,pts=line_fixture(direction)
        for run in [False,True]:
            e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e);e.run(40)
            pristine=record(e);assert e.location()[2:]==tuple(pts[0]) and blocks(e).flag(join)
            assert e.u8(syms['gPlayerAvatar'])&128==0
            mode=direction+'-'+('run' if run else 'walk');begin=len(report['native_samples'])
            for step_index in range(5):step_record(direction,run,mode+'-'+str(step_index))
            seen=report['native_samples'][begin:]
            frames={row['compiled_frame'] for row in seen if row['compiled_frame'] is not None}
            directional={'RIGHT':{2,7,8},'LEFT':{2,7,8},'UP':{1,5,6},'DOWN':{0,3,4}}[direction]
            mature=[q for q in seen if int(q['tag'].rsplit('-',1)[1])>=3 and q['compiled_frame'] is not None]
            mature_frames={q['compiled_frame'] for q in mature}
            assert mature_frames==directional,('Wrong direction or missing foot pose',mode,mature_frames,directional)
            if direction in ['LEFT','RIGHT']:
                assert all(q['hflip']==(direction=='RIGHT') for q in mature if q['compiled_frame'] in {7,8}),('Incorrect east/west flip',mode)
            assert len({tuple(row['Misty_feet']) for row in seen})>=8,('Misty position did not animate',mode)
            same_records(e,pristine)
            e.shot(str(out/(mode+'-final.png')),scale=4)
            report['cases'].append({'direction':direction,'run':run,'pass':True,'native_image_frames':sorted(frames),
                                    'real_player_steps':5,'per_frame_samples':len(seen),'player_party_PC_Dex_preserved':True})
            emit()
            if direction=='RIGHT' and not run:
                saved=flash_reload(e,'Misty-walk-save-cold');same_records(e,pristine)
                assert blocks(e).flag(join) and len(object_rows(e,253))==1
                pixel_sample('cold-Continue');report['native_SAVE_cold']=saved
                e.shot(str(out/'cold-continue.png'),scale=4)
            e.close();e=None
    report['pass']=len(report['cases'])==8
    report['status']='complete'
except Exception as error:
    report['status']='failed';report['error']=repr(error);report['traceback']=traceback.format_exc()
    if e is not None:
        try:e.shot(str(out/'failure.png'),scale=4);report['failure_callback']=hex(e.callback2());report['failure_position']=e.location()
        except Exception as diagnostic:report['diagnostic_error']=repr(diagnostic)
finally:
    if e is not None:e.close()
    report['original_inputs_unchanged']=all(f.exists() and qa_hash_bytes(f.read_bytes())==h for f,h in protected.items())
    if not report['original_inputs_unchanged']:report['pass']=False;report['status']='failed'
    emit()
print(json.dumps({'pass':report['pass'],'cases':len(report['cases']),'error':report.get('error')}),flush=True)
raise SystemExit(0 if report['pass'] else 1)
