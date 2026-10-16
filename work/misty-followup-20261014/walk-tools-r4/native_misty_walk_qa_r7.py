"""Actual Misty walk/run frame QA; separate preboot story/position fixtures.

No engine calls or RAM writes. Existing player Pokemon/PC/Dex remain unchanged.
This is not full campaign traversal, actual DELTA FPS or art approval.
"""
from pathlib import Path
import argparse, hashlib, json, os, struct, sys, traceback

p=argparse.ArgumentParser(description=__doc__)
for name in ['rom','elf','sav','out','expect-rom-sha','expect-elf-sha','expect-sav-sha']:
    p.add_argument('--'+name,required=True)
p.add_argument('--root',default='/workspaces/pokefirered')
cfg=p.parse_args();root=Path(cfg.root).resolve();os.chdir(root)
inputs={Path(cfg.rom).resolve():cfg.expect_rom_sha,Path(cfg.elf).resolve():cfg.expect_elf_sha,Path(cfg.sav).resolve():cfg.expect_sav_sha}
QA_SHA=lambda x:hashlib.sha256(x).hexdigest()
for f,wanted in inputs.items():assert QA_SHA(f.read_bytes())==wanted,(f,'SHA mismatch')
target=Path(cfg.out).resolve();assert target.is_relative_to(root/'work') and not target.exists()
target.mkdir(parents=True)
sys.argv=['native-walk','--rom',cfg.rom,'--elf',cfg.elf,'--sav',cfg.sav,'--out',str(target)]
basic_path=root/'tools/qa/native_misty_basic_qa.py'
basic=basic_path.read_text();assert QA_SHA(basic.encode())=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
assert basic.count('results=[];rows=[]\n')==1
exec(compile(basic.split('results=[];rows=[]\n')[0],'<verified-basic-definitions-only>','exec'))
def forbidden(*unused,**kw):raise AssertionError('Direct engine call/RAM fixture forbidden in walk QA')
call=flag=trail=forbidden
gd.FIELDS.update({'walk.obj.gfx':('ObjectEvent','graphicsId'),'walk.sprite.oam':('Sprite','oam'),
                  'walk.sprite.anim':('Sprite','animNum'),'walk.sprite.cmd':('Sprite','animCmdIndex')})
gd._OFFSETS=None
if 'constants/event_objects.h' not in gd.CONST_HEADERS:gd.CONST_HEADERS.append('constants/event_objects.h')
GFX=const('OBJ_EVENT_GFX_MISTY_COMPANION');assert GFX==237
PIC='gObjectEventPic_MistyCompanion';assert PIC in syms
frame_data=r.at(syms[PIC],9*256);expected={QA_SHA(frame_data[i*256:(i+1)*256]):i for i in range(9)}
assert len(expected)>=7,'Compiled walking art lacks distinct image frames'
protected={f.resolve():QA_SHA(f.read_bytes()) for f in set((root/'saves').rglob('*.sav'))|set(inputs)|{basic_path}}
report={'pass':False,'status':'running','scope':'preboot position/story fixtures; actual walk/run keys and SAVE/cold, not full campaign or mobile FPS',
        'ROM_sha256':inputs[Path(cfg.rom).resolve()],'ELF_sha256':inputs[Path(cfg.elf).resolve()],
        'SAV_sha256':inputs[Path(cfg.sav).resolve()],'RAM_writes':0,'engine_calls':0,'cases':[],'native_samples':[]}
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
    digest=QA_SHA(vram)
    # Only post-VBlank native bytes are evidence. Unknown transitional DMA bytes
    # are recorded but cannot satisfy the walking-frame assertion.
    sample={'tag':tag,'frame':e.frame(),'player':e.location(),'Misty_feet':row['feet'],
            'Misty_xy':row['xy'],'sprite':row['sprite'],'gfx':GFX,'anim':e.u8(sp+off('walk.sprite.anim')),
            'anim_cmd':e.u8(sp+off('walk.sprite.cmd')),'VRAM_sha256':digest,
            'compiled_frame':expected.get(digest),'palette_slot':a2>>12,'hflip':bool(a1&0x1000),'size':[w,h]}
    report['native_samples'].append(sample)
    if tag in ['RIGHT-walk-3','RIGHT-walk-4'] and e.frame()%3==0:
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
            if kind=='object_events' and obj.get('flag') in [hide,'FLAG_HIDE_OAK_IN_PALLET_TOWN']:continue
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
    s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True);s.set_flag(hide,True);s.set_flag('FLAG_HIDE_OAK_IN_PALLET_TOWN',True)
    s.set_var('VAR_MAP_SCENE_PALLET_TOWN_OAK',3);s.set_var('VAR_TEMP_7',0)
    s.set_var('VAR_HAPPINESS_STEP_COUNTER',0);s.set_var('VAR_REPEL_STEP_COUNT',250)
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
    e.run(4);pixel_sample(label)
    assert e.location()==want

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
            mature=[q for q in seen if int(q['tag'].rsplit('-',1)[1])>=2 and q['compiled_frame'] is not None]
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
    report['original_inputs_unchanged']=all(f.exists() and QA_SHA(f.read_bytes())==h for f,h in protected.items())
    if not report['original_inputs_unchanged']:report['pass']=False;report['status']='failed'
    emit()
print(json.dumps({'pass':report['pass'],'cases':len(report['cases']),'error':report.get('error')}),flush=True)
raise SystemExit(0 if report['pass'] else 1)
