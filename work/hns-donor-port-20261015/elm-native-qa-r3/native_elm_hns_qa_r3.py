"""Elm donor art: actual input-only lab dialogue/exit/reentry/menu SAVE/cold QA.

The guarded R10 prefix supplies only previously executed controllers and ABI
probing. Its Misty/Route29 cases are not run again. A separately labelled
preboot lab/story fixture preserves all six party records, PC and Dex bytes.
"""
from pathlib import Path
import argparse, hashlib, json, struct, subprocess, sys, traceback

elm_parser=argparse.ArgumentParser(description=__doc__)
for elm_name in ['root','rom','elf','sav','out','expect-rom-sha','expect-elf-sha',
                 'expect-sav-sha','verifier','guard-manifest','walk-runner','elm-manifest']:
    elm_parser.add_argument('--'+elm_name,required=True)
elm_cli=elm_parser.parse_args()
elm_output=Path(elm_cli.out).resolve()
elm_walk_path=Path(elm_cli.walk_runner).resolve()
elm_manifest_path=Path(elm_cli.elm_manifest).resolve()
elm_hash=lambda data:hashlib.sha256(data).hexdigest()
assert elm_hash(elm_walk_path.read_bytes())=='4fe78a90ea3a8a88603200be92a69b2660d63d61fa345d4a3e36c5c9ffe3b7bc'
elm_prefix=elm_walk_path.read_text().split("\ntry:\n    for direction in ['RIGHT','LEFT','UP','DOWN']:")
assert len(elm_prefix)==2,'R10 execution boundary differs'
elm_arg_names=['root','rom','elf','sav','out','expect_rom_sha','expect_elf_sha',
               'expect_sav_sha','verifier','guard_manifest']
sys.argv=['elm-r10-definitions']
for elm_name in elm_arg_names:
    sys.argv+=['--'+elm_name.replace('_','-'),getattr(elm_cli,elm_name)]
try:
    exec(compile(elm_prefix[0],str(elm_walk_path)+'::<definitions-only>','exec'),globals())
except Exception:
    elm_output.mkdir(parents=True,exist_ok=True)
    (elm_output/'elm-validation.json').write_text(json.dumps({'pass':False,
        'status':'DEPENDENCY_PREFLIGHT_FAILED_BEFORE_EMULATOR',
        'exception':traceback.format_exc(),'native_executed':False},indent=2)+'\n')
    raise

# The nested verified bootstrap has a global H string. All hashes below use
# qa_hash_bytes, which the verified R10 fixes explicitly after bootstrap.
assert callable(qa_hash_bytes)
elm_manifest=json.loads(elm_manifest_path.read_text())
assert qa_hash_bytes(elm_manifest_path.read_bytes())==source_guard['elm_manifest_sha256']
protected.update({elm_walk_path:qa_hash_bytes(elm_walk_path.read_bytes()),
                  elm_manifest_path:qa_hash_bytes(elm_manifest_path.read_bytes())})
report.update(status='preflight',scope='Actual native donor-Elm art in an explicitly preboot lab/story fixture; not natural Elm quest completion, whole Johto completion, or mobile FPS',
              cases=[],native_samples=[],native_executed=False,
              save_state_calls=0,natural_story_completion=False,
              skipped=['Elm east-neighbor interaction: cabinet collision at (8,8)',
                       'Elm walking: stationary professor has no natural walking route'])
elm_bindings={}
elm_frames=None
elm_palette=None
elm_palette_slots={}
elm_visibility_flags={}


def elm_forbidden(*args,**kwargs):
    raise AssertionError('Elm QA forbids RAM writes, direct engine calls and emulator states')


class ElmReadOnlyEmu(ReadOnlyEmu):
    save_state=elm_forbidden
    load_state=elm_forbidden


def elm_emit():
    (out/'elm-validation.json').write_text(json.dumps(report,indent=2)+'\n')


def elm_protected_check():
    result={str(path):qa_hash_bytes(path.read_bytes())==wanted for path,wanted in protected.items()}
    report['original_inputs_unchanged']=result
    assert all(result.values()),'Protected source, ROM, ELF or user save changed'


def elm_preflight():
    global elm_frames,elm_palette
    for name in ['gObjectEventPic_ProfElmHns','gObjectEventPal_ProfElmHns','gPlttBufferUnfaded']:
        row=current_elf.unique(name)
        assert row.kind!=2,('Expected data binding',name)
        syms[name]=row.addr
        elm_bindings[name]={'addr':hex(row.addr),'size':row.size,'owner':row.unit}
    r.syms=syms
    pic=current_elf.unique('gObjectEventPic_ProfElmHns')
    pal=current_elf.unique('gObjectEventPal_ProfElmHns')
    assert pic.size==2304 and pal.size==32,(pic.size,pal.size)
    elm_frames=r.at(pic.addr,2304)
    elm_palette=r.at(pal.addr,32)
    assert qa_hash_bytes(elm_frames)==elm_manifest['native_4bpp_sha256']
    assert qa_hash_bytes(elm_palette)==elm_manifest['native_gbapal_sha256']
    assert len({elm_frames[i*256:(i+1)*256] for i in range(9)})==9
    assert current_elf.unique('gPlttBufferUnfaded').size==1024
    # Resolve enum values with the exact compiler/symbol-size convention used
    # by the already verified gd.off helper. Enum identifiers cannot be read
    # by the preprocessor-only gd.const API.
    enum_names=['PALSLOT_PLAYER','PALSLOT_NPC_1','PALSLOT_NPC_4',
                'PALSLOT_NPC_SPECIAL','OBJ_PALSLOT_COUNT']
    enum_c=out/'elm-palette-enum-probe.c'
    enum_o=out/'elm-palette-enum-probe.o'
    enum_c.write_text('#include "global.h"\n#include "event_object_movement.h"\n'+
        '\n'.join('char qa_elm_%d[%s + 1];'%(i,name) for i,name in enumerate(enum_names))+'\n')
    gcc,nm=gd._gcc()
    subprocess.run([gcc,'-c','-w','-mthumb','-mabi=apcs-gnu','-march=armv4t','-fcommon',
        '-iquote','include','-DLEAFGREEN','-DREVISION=0','-DENGLISH','-DMODERN=1',
        '-o',str(enum_o),str(enum_c)],cwd=root,check=True)
    enum_nm=subprocess.check_output([nm,'-S',str(enum_o)],text=True)
    (out/'elm-palette-enum-probe.nm.txt').write_text(enum_nm)
    for line in enum_nm.splitlines():
        parts=line.split()
        if len(parts)==4 and parts[3].startswith('qa_elm_'):
            elm_palette_slots[enum_names[int(parts[3].rsplit('_',1)[1])]]=int(parts[1],16)-1
    assert elm_palette_slots==dict(zip(enum_names,[0,2,5,10,12])),elm_palette_slots
    if 'constants/metatile_behaviors.h' not in gd.CONST_HEADERS:
        gd.CONST_HEADERS.append('constants/metatile_behaviors.h')
    constants=gd.consts(['OBJ_EVENT_GFX_PROF_ELM','OBJ_EVENT_GFX_SCIENTIST',
        'FLAG_JOHTO_MET_LAB_ASSISTANT','FLAG_JOHTO_ELM_REPORT_DELIVERED','MB_SOUTH_ARROW_WARP'])
    assert constants['MB_SOUTH_ARROW_WARP']==0x65
    # Exact, already diagnosed initial Continue visibility synchronization.
    # These are NPC hide bits, not story milestones. All IDs are resolved
    # from current guarded headers before emulator boot.
    visibility_ids={
        'FLAG_HIDE_HOENN_BIRCH_LAB':0x1251,
        'FLAG_HIDE_HOENN_RIVAL_ROUTE103':0x1252,
        'FLAG_HIDE_HOENN_RUSTBORO_THIEF':0x1255,
        'FLAG_HIDE_HOENN_RUSTURF_GRUNT':0x1256,
        'FLAG_HIDE_HOENN_RUSTURF_PEEKO':0x1257,
        'FLAG_HIDE_HOENN_BRINEY':0x1258,
        'FLAG_HIDE_HOENN_WALLY_PETALBURG':0x1259,
        'FLAG_HIDE_HOENN_WALLY_VERDANTURF':0x125a,
        'FLAG_HIDE_HOENN_WANDA_BOYFRIEND':0x125b,
        'FLAG_HIDE_HOENN_ROCKET_WOODS':0x1260,
        'FLAG_HIDE_HOENN_RIVAL_LAB':0x1261}
    actual_ids=gd.consts(list(visibility_ids)+['HOENN_FLAGS_START'])
    assert actual_ids.pop('HOENN_FLAGS_START')==0x1000
    assert actual_ids==visibility_ids
    elm_visibility_flags.update(actual_ids)
    assert constants['OBJ_EVENT_GFX_PROF_ELM']==238
    assert constants['OBJ_EVENT_GFX_SCIENTIST']==55
    lab=map_info('NewBarkTown_ElmsLab')
    town=map_info('NewBarkTown')
    metadata=json.loads((root/'data/maps/NewBarkTown_ElmsLab/map.json').read_text())
    prof=[o for o in metadata['object_events'] if o['script']=='NewBarkTown_ElmsLab_ProfessorElm']
    researcher=[o for o in metadata['object_events'] if o['script']=='NewBarkTown_ElmsLab_Researcher']
    assert len(prof)==len(researcher)==1
    assert (prof[0]['x'],prof[0]['y'],prof[0]['graphics_id'])==(7,8,'OBJ_EVENT_GFX_PROF_ELM')
    assert (researcher[0]['x'],researcher[0]['y'],researcher[0]['graphics_id'])==(5,5,'OBJ_EVENT_GFX_SCIENTIST')
    assert prof[0]['movement_type']=='MOVEMENT_TYPE_FACE_DOWN'
    assert not metadata.get('coord_events')
    layouts=json.loads((root/'data/layouts/layouts.json').read_text())['layouts']
    layout=[q for q in layouts if q.get('id')==metadata['layout']]
    assert len(layout)==1
    layout=layout[0]
    assert (layout['width'],layout['height'])==(13,14)
    words=struct.unpack('<182H',(root/layout['blockdata_filepath']).read_bytes())
    for x,y in [(7,10),(7,9),(6,9),(6,8),(6,7),(7,7),(6,10),(6,11)]:
        assert words[y*13+x]==0x3289,('Known lab walking floor changed',x,y,hex(words[y*13+x]))
    primary_attributes=(root/'data/tilesets/primary/building/metatile_attributes.bin').read_bytes()
    lab_attributes=(root/'data/tilesets/secondary/lab/metatile_attributes.bin').read_bytes()
    assert len(primary_attributes)==2560
    primary_count=len(primary_attributes)//4
    exit_words=[words[12*13+x] for x in [5,6,7]]
    exit_behaviors=[struct.unpack_from('<I',lab_attributes,4*((word&0x3ff)-primary_count))[0]&0x1ff for word in exit_words]
    assert exit_words==[0x3290,0x3291,0x3292]
    assert exit_behaviors==[0,constants['MB_SOUTH_ARROW_WARP'],0],exit_behaviors
    assert (words[8*13+8]>>10)&3==1,'East cabinet collision changed; inspect path anew'
    report['Elm_dependency_preflight']={'pass':True,'unique_data_bindings':elm_bindings,
        'constants':constants,'ROM_2304B_all_nine_frames_sha256':qa_hash_bytes(elm_frames),
        'compiler_palette_enum':elm_palette_slots,
        'exact_initial_Continue_visibility_flag_ids':elm_visibility_flags,
        'actual_exit_tile_behavior':{'x':[5,6,7],'y':12,'words':exit_words,'behaviors':exit_behaviors,'walk_via_central_x':6},
        'ROM_32B_palette_sha256':qa_hash_bytes(elm_palette),
        'lab':{k:lab[k] for k in ['group','num','layout_id']},
        'town':{k:town[k] for k in ['group','num','layout_id']},
        'three_accessible_professor_neighbors_verified':True,'east_cabinet_collision':True}
    return lab,town


def elm_generic_sprite(row,tag):
    sp=syms['gSprites']+off('misty_sprite')*row['sprite']
    a0,a1,a2=struct.unpack('<HHH',e.read(sp+off('walk.sprite.oam'),6))
    shape,size=a0>>14,a1>>14
    dimensions=[[(8,8),(16,16),(32,32),(64,64)],[(16,8),(32,8),(32,16),(64,32)],[(8,16),(8,32),(16,32),(32,64)]]
    assert shape<3 and not a0&0x2000
    w,h=dimensions[shape][size]
    tile=a2&1023
    pitch=(w//8)*32 if e.u16(0x04000000)&64 else 32*32
    data=b''.join(e.read(0x06010000+tile*32+yy*pitch,(w//8)*32) for yy in range(h//8))
    slot=a2>>12
    return {'tag':tag,'frame':e.frame(),'visible':row['visible'],'gfx':e.u8(row['ptr']+off('walk.obj.gfx')),
        'local_id':e.u8(row['ptr']+off('misty_obj.local')),'sprite':row['sprite'],
        'native_size':[w,h],'palette_slot':slot,'hflip':bool(a1&0x1000),
        'VRAM_sha256':qa_hash_bytes(data),'compiled_frame':next((i for i in range(9) if data==elm_frames[i*256:(i+1)*256]),None),
        'hardware_palette_sha256':qa_hash_bytes(e.read(0x05000200+slot*32,32)),
        'unfaded_palette_sha256':qa_hash_bytes(e.read(syms['gPlttBufferUnfaded']+0x200+slot*32,32))}


def elm_object_by_gfx(gfx):
    rows=[]
    for index in range(16):
        ptr=syms['gObjectEvents']+index*off('misty_obj')
        if e.u8(ptr)&1 and e.u8(ptr+off('walk.obj.gfx'))==gfx:
            rows+=object_rows(e,e.u8(ptr+off('misty_obj.local')))
    assert len(rows)==1,('Expected one runtime object',gfx,rows)
    return rows[0]


def elm_inspect(tag,wanted_frame=None,followers=False):
    professor=elm_object_by_gfx(238)
    researcher=elm_object_by_gfx(55)
    player_id=e.u8(syms['gPlayerAvatar']+off('walk.player.objectId'))
    assert player_id<16
    player_xy=struct.unpack('<hh',e.read(syms['gObjectEvents']+player_id*off('misty_obj')+off('misty_obj.coords'),4))
    loc=e.location()
    offset=(player_xy[0]-loc[2],player_xy[1]-loc[3])
    for obj,want in [(professor,(7,8)),(researcher,(5,5))]:
        assert tuple(obj['xy'][i]-offset[i] for i in range(2))==want
    sample=elm_generic_sprite(professor,tag)
    assert sample['visible'] and sample['native_size']==[16,32]
    assert sample['palette_slot']==elm_palette_slots['PALSLOT_NPC_SPECIAL'],'Elm special palette slot differs from source registration'
    assert sample['compiled_frame'] is not None,'Elm visible VRAM is not one of the nine donor frames'
    assert sample['unfaded_palette_sha256']==qa_hash_bytes(elm_palette),'Elm unfaded palette is not the original donor palette'
    if wanted_frame is not None:
        assert sample['compiled_frame']==wanted_frame,('Wrong professor face frame',tag,sample)
    sample['hardware_palette_equals_unfaded_donor']=sample['hardware_palette_sha256']==qa_hash_bytes(elm_palette)
    sample['researcher']=elm_generic_sprite(researcher,tag+'-researcher')
    assert sample['researcher']['gfx']==55
    if followers:
        ms,pk=object_rows(e,253),object_rows(e,254)
        assert len(ms)==len(pk)==1,'Expected both joined Misty and Pikachu'
        sample['Misty']=elm_generic_sprite(ms[0],tag+'-Misty')
        sample['Pikachu']=elm_generic_sprite(pk[0],tag+'-Pikachu')
        assert all(x['visible'] for x in [sample['Misty'],sample['Pikachu']]),('Followers hidden',sample)
        assert sample['Misty']['gfx']==237
        assert sample['Misty']['palette_slot']!=10 and sample['Pikachu']['palette_slot']!=10,'Elm palette collided with a follower'
    report['native_samples'].append(sample)
    return sample


def elm_fixture():
    s=SaveFile(str(sav))
    before=(bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]),
        bytes(s.blocks['storage']),[s.dex_state(i) for i in range(1,387)])
    s.warp('NewBarkTown_ElmsLab',7,10)
    flags=[join,hide,'FLAG_SYS_GAME_CLEAR','FLAG_RECEIVED_STARTER_PIKACHU',
           'FLAG_JOHTO_MET_LAB_ASSISTANT','FLAG_JOHTO_ELM_REPORT_DELIVERED']+K
    for name in flags:s.set_flag(name,True)
    s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
    s.sb1[off('sb1.daycare')+off('walk.daycare.stepCounter')]=0
    for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
    assert before==(bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]),
        bytes(s.blocks['storage']),[s.dex_state(i) for i in range(1,387)])
    path=out/'elm-lab-preboot-visual-QA-only.sav'
    s.save(str(path))
    report['preboot_fixture']={'story_flags_set_true':flags,'position':['NewBarkTown_ElmsLab',7,10],
        'daycare_and_happiness_step_counters_reset':True,'quest_log_scenes_cleared':True,
        'all_six_party_records_PC_and_fourfold_Dex_preserved':True,
        'natural_story_completion':False,'source_sha256':qa_hash_bytes(sav.read_bytes()),
        'fixture_sha256':qa_hash_bytes(path.read_bytes())}
    return path,before


def elm_walk(key):
    before=one_tile(e,key)
    e.run(40)
    safe(e)
    report.setdefault('actual_steps',[]).append({'from':before,'key':key,'to':e.location()})


def elm_talk(tag,wanted_frame,facing):
    position=e.location()
    # The west/north approach ends facing along the aisle. A real direction
    # input into the solid professor turns the player without changing tiles.
    e.press(facing,hold=2,after=20)
    e.run(20)
    safe(e)
    assert e.location()==position,('Interaction turn moved off the verified neighbor',tag,e.location())
    report.setdefault('actual_interaction_turns',[]).append({'tag':tag,'key':facing,'position':position})
    e.press('A',hold=3,after=45)
    safe(e)
    assert not e.field_idle(),'A did not begin the actual Elm interaction'
    elm_inspect(tag,wanted_frame,followers=False)
    e.shot(str(out/(tag+'.png')),scale=4)
    for _ in range(180):
        if e.field_idle():break
        safe(e)
        e.press('A',hold=2,after=14)
    else:raise AssertionError('Elm dialogue did not return controls')
    e.run(40)


def elm_warp_walk(key,wanted_map):
    e.hold(key)
    try:
        for _ in range(160):
            e.run(1)
            if e.location()[:2]==wanted_map:break
        else:raise AssertionError(('Door warp not reached',key,e.location(),wanted_map))
    finally:e.hold()
    settle(e)
    e.run(40)
    assert e.location()[:2]==wanted_map
    report.setdefault('actual_door_warps',[]).append({'key':key,'arrived':e.location()})


def elm_initial_visibility_save_cold():
    """Expose the exact first-cycle 11-bit initialization before strict cycle2.

    No differences are masked in the normal flash_reload controller. Its next
    independent cycle must pass full strict live/stored/cold equality.
    """
    before=persistence_live()
    counters=native_save(e)
    assert counters[1]==counters[0]+1
    live=persistence_live()
    assert live==before,('First SAVE changed live state',[k for k in live if live[k]!=before[k]])
    e.run(30);e.lib.qa_close(e.h);e.h=None
    stored=SaveFile(e.sav_path)
    for _,sid,size in stored.layout:
        pos=stored.where[sid]*4096
        assert checksum(stored.raw[pos:pos+size])==struct.unpack_from('<H',stored.raw,pos+0xff6)[0]
    assert len(stored.layout)==14 and stored.counter==counters[1]
    position=(*struct.unpack_from('<bb',stored.sb1,off('sb1.location')),
        *struct.unpack_from('<hh',stored.sb1,off('sb1.pos')))
    saved=persistence_record(stored,stored.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600],
        stored.party_count(),stored.blocks['storage'],position)
    assert saved==live,('First stored SAVE differs from live',[k for k in saved if saved[k]!=live[k]])
    first_save=out/'elm-first-native-SAVE-before-Continue-visibility-init-QA-only.sav'
    assert not first_save.exists()
    first_save.write_bytes(Path(e.sav_path).read_bytes())
    e.h=e.lib.qa_open(str(rom).encode(),str(e.sav_path).encode());assert e.h
    e.boot_continue();settle(e)
    cold=persistence_live()
    changed_groups=[k for k in cold if cold[k]!=live[k]]
    assert changed_groups==['hoenn_flags'],('Unexpected first Continue changes',changed_groups)
    old=live['hoenn_flags'];new=cold['hoenn_flags']
    bit_changes=[]
    names={flag-0x1000:name for name,flag in elm_visibility_flags.items()}
    for i,(a,b) in enumerate(zip(old,new)):
        for bit in range(8):
            if (a^b)&(1<<bit):
                index=i*8+bit
                bit_changes.append({'name':names.get(index),'flag_id':hex(0x1000+index),
                    'byte':i,'bit':bit,'before':(a>>bit)&1,'after':(b>>bit)&1})
    assert len(old)==len(new)==256
    assert len(bit_changes)==11
    assert {row['name'] for row in bit_changes}==set(elm_visibility_flags)
    assert all(row['before']==0 and row['after']==1 for row in bit_changes)
    # Reconstruct the full exact expected bytes; every other bit and all other
    # persistence fields remain equal. This is a named source-derived event,
    # not a tolerance on the subsequent strict save/cold test.
    expected=bytearray(old)
    for flag in elm_visibility_flags.values():
        index=flag-0x1000
        expected[index//8]|=1<<(index%8)
    assert bytes(expected)==new
    expected_cold=dict(live,hoenn_flags=bytes(expected))
    assert cold==expected_cold
    event={'status':'FIRST_CONTINUE_EXACT_11_DERIVED_NPC_HIDE_BITS_INITIALIZED',
        'strict_cold_equals_pre_save_live':False,'unexpected_changes':False,
        'counter':counters,'checksummed_sectors':14,'changes':bit_changes,
        'changed_groups':changed_groups,'party_PC_Dex_all_other_story_and_location_equal':True,
        'stored_SAVE_equal_live_before_Continue':True,'first_pre_normalization_QA_save':str(first_save),
        'visibility_writer_source':'src/field_specials.c:HoennZ3_SetupObjectsOnContinue',
        'following_cycle_must_pass_unmodified_strict_flash_reload':True}
    report['initial_Continue_visibility_normalization']=event
    elm_emit()
    e.shot(str(out/'first-Continue-visibility-normalization.png'),scale=4)
    return event


try:
    elm_lab,elm_town=elm_preflight()
    elm_emit()
    # Unmodified original save on a temporary battery copy, before position
    # fixtures. This catches same-map cached-template compatibility if relevant.
    e=ElmReadOnlyEmu(str(rom),str(sav),sym='')
    e.syms=syms;e.boot_continue();settle(e);e.run(40)
    report['native_executed']=True
    source_loaded=record(e)
    source_file=SaveFile(str(sav))
    assert source_loaded['count']==source_file.party_count()
    assert source_loaded['party']==bytes(source_file.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])
    assert source_loaded['pc']==bytes(source_file.blocks['storage'])
    assert source_loaded['dex']==[source_file.dex_state(i) for i in range(1,387)]
    legacy_lab=e.location()[:2]==(elm_lab['group'],elm_lab['num'])
    legacy={'location':e.location(),'unchanged_party_PC_Dex_loaded':True,
            'same_map_cached_template_case_applicable':legacy_lab}
    if legacy_lab:
        try:
            legacy['sample']=elm_inspect('original-save-Continue')
            legacy['new_professor_loaded_without_preboot_position_change']=True
        except AssertionError as exc:
            legacy['new_professor_loaded_without_preboot_position_change']=False
            legacy['failure']=repr(exc)
    else:legacy['same_map_cached_template_status']='NOT_APPLICABLE_SOURCE_SAVED_ELSEWHERE'
    report['original_save_Continue']=legacy
    e.shot(str(out/'original-save-Continue.png'),scale=3)
    e.close();e=None
    elm_path,elm_preserved=elm_fixture()
    e=ElmReadOnlyEmu(str(rom),str(elm_path),sym='')
    e.syms=syms;e.boot_continue();settle(e);e.run(40)
    assert e.location()==(elm_lab['group'],elm_lab['num'],7,10)
    elm_pristine=record(e)
    assert (elm_pristine['party'],elm_pristine['pc'],elm_pristine['dex'])==elm_preserved
    elm_inspect('lab-boot')
    elm_walk('UP')
    elm_talk('face-south',0,'UP')
    for key in ['LEFT','UP']:elm_walk(key)
    elm_talk('face-west',2,'RIGHT')
    for key in ['UP','RIGHT']:elm_walk(key)
    elm_talk('face-north',1,'DOWN')
    for key in ['LEFT','DOWN','DOWN','RIGHT','DOWN']:elm_walk(key)
    assert e.location()[2:]==(7,10)
    sample_before=elm_inspect('coexist-before-exit',followers=True)
    e.shot(str(out/'elm-Misty-Pikachu-coexist-before.png'),scale=4)
    same_records(e,elm_pristine)
    elm_walk('LEFT')
    elm_walk('DOWN')
    elm_warp_walk('DOWN',(elm_town['group'],elm_town['num']))
    townpos=e.location()
    assert townpos[2]==11 and townpos[3] in (8,9),(townpos,'Unexpected lab external door')
    if townpos[3]==8:elm_walk('DOWN')
    assert e.location()[2:]==(11,9)
    elm_warp_walk('UP',(elm_lab['group'],elm_lab['num']))
    assert e.location()[2] in (5,6,7) and e.location()[3] in (11,12),e.location()
    if e.location()[3]==12:elm_walk('UP')
    while e.location()[2]<7:elm_walk('RIGHT')
    while e.location()[2]>7:elm_walk('LEFT')
    elm_walk('UP')
    assert e.location()[2:]==(7,10)
    # A map reload resets the follower trail. Fill it with actual legal steps
    # before requiring visible coexistence, as the verified R10 does.
    for key in ['UP','LEFT','DOWN','RIGHT']:elm_walk(key)
    sample_after=elm_inspect('coexist-after-reentry',followers=True)
    assert sample_before['unfaded_palette_sha256']==sample_after['unfaded_palette_sha256']
    same_records(e,elm_pristine)
    e.shot(str(out/'elm-Misty-Pikachu-coexist-after.png'),scale=4)
    elm_initial_visibility_save_cold()
    same_records(e,elm_pristine)
    report['actual_menu_SAVE_cold']=flash_reload(e,'elm-lab-second-strict-cycle')
    e.run(40)
    same_records(e,elm_pristine)
    elm_inspect('after-actual-SAVE-cold')
    assert len(object_rows(e,253))==len(object_rows(e,254))==1
    for key in ['UP','LEFT','DOWN','RIGHT']:elm_walk(key)
    same_records(e,elm_pristine)
    elm_inspect('after-cold-actual-follower-steps',followers=True)
    e.shot(str(out/'elm-actual-SAVE-cold.png'),scale=4)
    report['cases']=[{'case':'compiled_all_nine_donor_frames_and_palette','pass':True},
        {'case':'actual_three_accessible_faceplayer_interactions','pass':True,'frames':[0,2,1]},
        {'case':'researcher_55_and_dynamic_followers_palette_coexistence','pass':True},
        {'case':'actual_lab_door_roundtrip','pass':True},
        {'case':'first_Continue_exact_11_NPC_hide_bits_initialized','pass':True,'first_strict_equality':False},
        {'case':'actual_menu_SAVE_14sectors_and_cold_reentry','pass':True}]
    assert not (legacy_lab and not legacy['new_professor_loaded_without_preboot_position_change']),legacy
    report['pass']=True
    report['status']='NATIVE_ELM_DONOR_LAB_COEXISTENCE_SAVE_COLD_PASS'
except Exception:
    report['pass']=False
    report['status']='NATIVE_ELM_QA_FAILED'
    report['exception']=traceback.format_exc()
    if e is not None and getattr(e,'h',None):
        try:e.shot(str(out/'failure.png'),scale=4)
        except Exception:pass
    raise
finally:
    if e is not None:e.close()
    try:elm_protected_check()
    except Exception:
        report['pass']=False
        report['protected_input_failure']=traceback.format_exc()
        raise
    finally:elm_emit()
