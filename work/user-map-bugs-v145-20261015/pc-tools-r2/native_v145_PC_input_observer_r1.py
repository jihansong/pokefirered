"""Actual v1.45 cold Continue + input-only PC inspection on a private battery clone.

Append one JSON object per line to --commands. Every accepted action gets an
atomic JSON observation and a screenshot. No RAM writes, script calls, save
states, fixtures, force warps, or source/product/save edits are available.
The original save and all existing saves remain hash protected.
"""
from pathlib import Path
import argparse, hashlib, json, os, struct, sys, time, traceback

ap = argparse.ArgumentParser()
for n in ('root','rom','elf','sav','out','abi-json','ui-abi','base-helper','commands'):
    ap.add_argument('--'+n, type=Path, required=True)
ap.add_argument('--max-seconds', type=int, default=1800)
c = ap.parse_args()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(c.sav) == '0949ebf04557a76e2175602e967eefadb7ffb722f2746be8a40ddb1fd66550a9'
assert sha(c.base_helper) == 'f2a9b3bbcdf9077270c81d4bd9cea4e33096eb8b9162b597e6713f42ba60070b'
ui = json.loads(c.ui_abi.read_text())
assert ui['ROM_sha256'] == sha(c.rom) == 'af2677993a75979fb36f0768c390d1bad7424e61f2d569b5054d40702250d2e8'
assert ui['ELF_sha256'] == sha(c.elf) == '2549852a48935c680e06e81719b54663b9c0efa7fdaccd31d1f4683886c5d64e'
for rel, h in {**ui['source_sha256'], **ui['compiler_dependency_sha256']}.items():
    assert sha(c.root/rel) == h, ('Stale PC ABI dependency', rel)
commands = c.commands.resolve()
assert commands.is_relative_to(c.root.resolve()/'work')
assert 30 <= c.max_seconds <= 3600
text = c.base_helper.read_text()
separator = '\ntry:\n    e = Emu(str(rom), str(sav), sym=\'\')'
assert text.count(separator)==1
sys.argv = [str(c.base_helper)]
for n in ('root','rom','elf','sav','out','abi-json'):
    sys.argv += ['--'+n, str(getattr(c,n.replace('-','_')))]
sys.argv += ['--expect-sav-sha', sha(c.sav)]
scope = {'__name__':'verified_definitions_only','__file__':str(c.base_helper)}
exec(compile(text.split(separator)[0], '<guarded-native-definitions>', 'exec'), scope)
for n in ('Emu','SaveFile','Mon','Blocks','checksum','off','const','syms','settle','native_save',
          'snapshot','compact','protected','out','rom','elf','sav'):
    globals()[n] = scope[n]
uoff, uc = ui['offsets'], ui['constants']
usyms = {n:r['value'] for n,r in ui['symbols'].items()}
syms.update(usyms)
protected[c.ui_abi.resolve()] = sha(c.ui_abi)
protected[c.base_helper.resolve()] = sha(c.base_helper)
LAP_PID, LAP_OT = 2245990591, 2839214970
LAP_SHA = '60d1c18b1eb7be18e53e23f3d8d5466471fc94095c895d14bed793ad2b9da8d7'
LAP_OFFSET = 4 + (2*uc['IN_BOX_COUNT']+10)*80
assert LAP_OFFSET == 5604
e = None; initial = None; summary_verified = False; saved_cold = False
report = dict(status='starting', pass_all=False, original_SAV_sha256=sha(sav), ROM_sha256=sha(rom),
              ELF_sha256=sha(elf), input_only=True, RAM_writes=0, state_loads=0, fixtures=0,
              direct_engine_calls=0, DELTA_device_tested=False, observations=[], commands=[])

def dump():
    tmp = out/'validation.tmp'
    tmp.write_text(json.dumps(report, indent=2)+'\n'); os.replace(tmp,out/'validation.json')

def addr(n): return usyms[n]
def ram(p,n=1): return 0x02000000 <= p and p+n <= 0x02040000 or 0x03000000 <= p and p+n <= 0x03008000
def read_field(p,typ,member,n=1): return e.read(p+uoff[typ+'.'+member],n)
def f8(p,typ,m): return read_field(p,typ,m)[0]
def f16(p,typ,m): return struct.unpack('<H',read_field(p,typ,m,2))[0]
def f32(p,typ,m): return struct.unpack('<I',read_field(p,typ,m,4))[0]

def raw_lap():
    p = e.ptr('gPokemonStoragePtr')
    assert ram(p,off('storage'))
    raw = e.read(p+LAP_OFFSET,80)
    assert struct.unpack_from('<II',raw)==(LAP_PID,LAP_OT), 'Target PC identity changed'
    return raw

def observation(label):
    raw = raw_lap()
    row = {'label':label,'frame':e.frame(),'callback2':e.callback2(),
           'location':list(e.location()),'field_idle':e.field_idle(),
           'Lapras80_sha256':hashlib.sha256(raw).hexdigest(),'Lapras80_hex':raw.hex(),
           'Lapras_header_flags':raw[19], 'Lapras_stored_checksum':struct.unpack_from('<H',raw,28)[0]}
    pc = e.read(e.ptr('gPokemonStoragePtr'),off('storage'))
    row['current_box_zero_based'] = struct.unpack_from('<I',pc)[0]
    if initial is not None:
        changed = [i for i,(a,b) in enumerate(zip(initial['pc'],pc)) if a!=b]
        row['PC_changed_byte_count'] = len(changed)
        row['PC_record_changed_offsets'] = [i for i in changed if 4<=i<4+uc['TOTAL_BOXES_COUNT']*uc['IN_BOX_COUNT']*80]
    tasks=[]
    for i in range(uc['NUM_TASKS']):
        p=addr('gTasks')+i*uoff['Task.size']
        if f8(p,'Task','isActive'):
            f=f32(p,'Task','func')
            names=[n for n,v in usyms.items() if (v&~1)==(f&~1)]
            tasks.append({'id':i,'function':f,'names':names,'data':list(struct.unpack('<16h',read_field(p,'Task','data',32)))})
    row['tasks']=tasks
    storage=e.u32(addr('gStorage'))
    storage_active=any((t['function']&~1) in {addr(n)&~1 for n in ('Task_PokeStorageMain','Task_OnSelectedMon','Task_ShowMonSummary')} for t in tasks)
    if storage_active and ram(storage,uoff['PokemonStorageSystemData.size']):
        st={m:f8(storage,'PokemonStorageSystemData',m) for m in ('state','boxOption','menuItemsCount','displayMonIsEgg','displayMonLevel','summaryCursorPos')}
        st.update(cursor_area=e.u8(addr('sCursorArea')),cursor_position=e.u8(addr('sCursorPosition')),
                  mon_in_hand=e.u8(addr('sIsMonBeingMoved')),
                  display_species=f16(storage,'PokemonStorageSystemData','displayMonSpecies'),
                  display_PID=f32(storage,'PokemonStorageSystemData','displayMonPersonality'))
        count=st['menuItemsCount']
        if count<=7:
            base=storage+uoff['PokemonStorageSystemData.menuItems']
            st['menu_text_ids']=[e.u32(base+i*uoff['StorageMenu.size']+uoff['StorageMenu.textId']) for i in range(count)]
        row['storage']=st
        assert st['mon_in_hand']==0, 'Observation stopped: a Pokemon was picked up; do not move/place/release it'
    row['menu_cursor']=e.u8(addr('sMenu')+uoff['Menu.cursorPos'])
    if (e.callback2()&~1)==(addr('CB2_RunPokemonSummaryScreen')&~1):
        p=e.u32(addr('sMonSummaryScreen'))
        assert ram(p,uoff['PokemonSummaryScreenData.size'])
        mr=read_field(p,'PokemonSummaryScreenData','currentMon',100)
        row['summary']={'isEgg':f8(p,'PokemonSummaryScreenData','isEgg'),
                        'isBadEgg':f8(p,'PokemonSummaryScreenData','isBadEgg'),
                        'isBoxMon':f8(p,'PokemonSummaryScreenData','isBoxMon'),
                        'setup_step':f8(p,'PokemonSummaryScreenData','summarySetupStep'),
                        'currentMon_PID_OT':list(struct.unpack_from('<II',mr)),
                        'currentMon_box80_sha256':hashlib.sha256(mr[:80]).hexdigest()}
    shot=out/f'{len(report["observations"]):03d}-{label}.png'
    e.shot(str(shot),scale=4); row['screenshot']=str(shot)
    report['observations'].append(row); dump(); print(json.dumps(row),flush=True)
    return row

def summary_check():
    global summary_verified
    row=observation('actual-Lapras-summary')
    assert 'summary' in row, 'Actual PC summary UI is not open'
    s=row['summary']
    assert s['currentMon_PID_OT']==[LAP_PID,LAP_OT], 'Summary is for a different Pokemon'
    assert s['isBoxMon']==1, 'Not a PC Pokemon summary'
    report['actual_getter_result']=s
    report['BadEgg_reproduced_in_current_ROM_PC']=bool(s['isBadEgg'])
    report['Lapras_healthy_bytes_preserved_through_actual_summary']=(row['Lapras80_sha256']==LAP_SHA)
    summary_verified=True; dump()

def task_active(name):
    for i in range(uc['NUM_TASKS']):
        p=addr('gTasks')+i*uoff['Task.size']
        if f8(p,'Task','isActive') and (f32(p,'Task','func')&~1)==(addr(name)&~1):
            return p
    return None

def wait_for(test, frames=1200):
    for _ in range(frames):
        if test(): return
        e.run(1)
    raise AssertionError('Normal UI did not reach the expected state')

def open_lapras_summary():
    """From actual MOVE POKEMON box UI only; read cursors and press normal keys."""
    def main_ready():
        p=e.u32(addr('gStorage'))
        return task_active('Task_PokeStorageMain') and ram(p,uoff['PokemonStorageSystemData.size']) and f8(p,'PokemonStorageSystemData','state')==0
    wait_for(main_ready)
    p=e.u32(addr('gStorage'))
    assert f8(p,'PokemonStorageSystemData','boxOption')==uc['OPTION_MOVE_MONS']
    assert e.u8(addr('sIsMonBeingMoved'))==0 and e.u8(addr('sInMultiMoveMode'))==0
    assert e.u8(addr('sCursorArea'))==uc['CURSOR_AREA_IN_BOX'], 'Place the cursor inside the normal box UI first'
    e.press('START',after=40); wait_for(main_ready)
    assert e.u8(addr('sCursorArea'))==uc['CURSOR_AREA_BOX_TITLE']
    cur=struct.unpack('<I',e.read(e.ptr('gPokemonStoragePtr'),4))[0]
    n=uc['TOTAL_BOXES_COUNT']
    left=(cur-2)%n; right=(2-cur)%n
    key,steps=('LEFT',left) if left<=right else ('RIGHT',right)
    for _ in range(steps):
        old=struct.unpack('<I',e.read(e.ptr('gPokemonStoragePtr'),4))[0]
        e.press(key,after=100); wait_for(main_ready)
        got=struct.unpack('<I',e.read(e.ptr('gPokemonStoragePtr'),4))[0]
        assert got==(old+(-1 if key=='LEFT' else 1))%n, 'Normal box scroll did not advance one box'
    assert struct.unpack('<I',e.read(e.ptr('gPokemonStoragePtr'),4))[0]==2
    e.press('DOWN',after=40); wait_for(main_ready)
    cols=uc['IN_BOX_COLUMNS']
    for _ in range(uc['IN_BOX_COUNT']):
        assert e.u8(addr('sCursorArea'))==uc['CURSOR_AREA_IN_BOX']
        pos=e.u8(addr('sCursorPosition'))
        if pos==10: break
        dy=10//cols-pos//cols; dx=10%cols-pos%cols
        key=('DOWN' if dy>0 else 'UP') if dy else ('RIGHT' if dx>0 else 'LEFT')
        e.press(key,after=30); wait_for(main_ready)
    else: raise AssertionError('Normal cursor navigation failed to reach BOX3 cell11')
    assert hashlib.sha256(raw_lap()).hexdigest()==LAP_SHA
    observation('actual-PC-Lapras-selected')
    e.press('A',after=60)
    def selected_ready():
        q=e.u32(addr('gStorage'))
        return task_active('Task_OnSelectedMon') and f8(q,'PokemonStorageSystemData','state')==2
    wait_for(selected_ready)
    p=e.u32(addr('gStorage')); count=f8(p,'PokemonStorageSystemData','menuItemsCount')
    assert 1<=count<=7
    base=p+uoff['PokemonStorageSystemData.menuItems']
    ids=[e.u32(base+i*uoff['StorageMenu.size']+uoff['StorageMenu.textId']) for i in range(count)]
    assert ids.count(uc['MENU_TEXT_SUMMARY'])==1
    goal=ids.index(uc['MENU_TEXT_SUMMARY'])
    for _ in range(count):
        pos=e.u8(addr('sMenu')+uoff['Menu.cursorPos'])
        if pos==goal: break
        e.press('DOWN',after=20)
    else: raise AssertionError('Normal mon menu did not select SUMMARY')
    assert e.u8(addr('sIsMonBeingMoved'))==0
    e.press('A',after=180)
    wait_for(lambda:(e.callback2()&~1)==(addr('CB2_RunPokemonSummaryScreen')&~1))
    e.run(90); summary_check()

def save_cold_check():
    global saved_cold
    assert summary_verified, 'Inspect the actual Lapras summary before SAVE/cold check'
    assert e.field_idle(), 'Exit PC normally to the field before saving'
    before=snapshot(e)
    counters=native_save(e)
    assert counters==(84,85), ('Unexpected native SAVE counter',counters)
    live=snapshot(e)
    for key in ('party','count','pc','dex_raw','flags','vars','hoenn_trainer_flags','hoenn_flags','hoenn_vars','location'):
        assert before[key]==live[key], ('SAVE changed loaded data',key)
    e.run(30); e.lib.qa_close(e.h); e.h=None
    q=out/'v145-native-PC-SAVE-cold-QA-clone-only.sav'
    q.write_bytes(Path(e.sav_path).read_bytes())
    stored=SaveFile(str(q)); assert stored.counter==85
    assert bytes(stored.blocks['storage'])==live['pc']
    for _,sid,size in stored.layout:
        pos=stored.where[sid]*4096
        assert checksum(stored.raw[pos:pos+size])==struct.unpack_from('<H',stored.raw,pos+0xff6)[0]
    e.h=e.lib.qa_open(str(rom).encode(),str(e.sav_path).encode()); assert e.h
    e.boot_continue(); settle(e); cold=snapshot(e)
    for key in ('party','count','pc','dex_raw','flags','vars','hoenn_trainer_flags','hoenn_flags','hoenn_vars','location'):
        assert live[key]==cold[key], ('Cold Continue differs',key)
    assert initial['pc'][4:4+uc['TOTAL_BOXES_COUNT']*uc['IN_BOX_COUNT']*80]==cold['pc'][4:4+uc['TOTAL_BOXES_COUNT']*uc['IN_BOX_COUNT']*80], 'PC records changed during browsing/SAVE'
    report['native_SAVE_cold_Continue']={'pass':True,'counters':list(counters),'SAV':str(q),'SAV_sha256':sha(q),'PC_records_unchanged':True}
    saved_cold=True; observation('native-SAVE-cold-Continue')

try:
    e=Emu(str(rom),str(sav),sym=''); e.syms=syms
    candidate=SaveFile(str(sav))
    assert candidate.counter==84
    def on_menu(emu):
        assert emu.read(emu.ptr('gSaveBlock1Ptr'),off('sb1'))==bytes(candidate.sb1)
        assert emu.read(emu.ptr('gPokemonStoragePtr'),off('storage'))==bytes(candidate.blocks['storage'])
        report['initial_native_PC_bytes_exact']=True
    e.boot_continue(on_menu=on_menu); settle(e)
    initial=snapshot(e)
    assert hashlib.sha256(raw_lap()).hexdigest()==LAP_SHA
    report['status']='ready_for_input_only_commands'
    observation('cold-Continue')
    index=0; start=time.monotonic()
    while time.monotonic()-start<c.max_seconds:
        rows=commands.read_text().splitlines() if commands.exists() else []
        if index>=len(rows):
            time.sleep(.2); continue
        raw=rows[index]; index+=1
        if not raw.strip(): continue
        action=json.loads(raw); op=action.get('op')
        report['commands'].append(action)
        if op=='press':
            key=action['key'].upper()
            assert key in ('A','B','START','SELECT','UP','DOWN','LEFT','RIGHT','L','R')
            hold,after=int(action.get('hold',3)),int(action.get('after',30))
            assert 1<=hold<=120 and 0<=after<=1800
            e.press(key,hold=hold,after=after); observation('input-'+key.lower())
        elif op=='run':
            frames=int(action['frames']); assert 0<=frames<=3600
            e.run(frames); observation('wait')
        elif op=='observe': observation('manual-observation')
        elif op=='summary-check': summary_check()
        elif op=='open-Lapras-summary': open_lapras_summary()
        elif op=='save-cold-check': save_cold_check()
        elif op=='stop':
            report['status']='complete' if saved_cold else 'stopped-with-partial-evidence'
            break
        else: raise AssertionError(('Unknown input-only operation',op))
    else: report['status']='bounded-session-timeout-partial-evidence'
    report['pass_all']=bool(summary_verified and saved_cold)
except Exception as exc:
    report.update(status='failed',error=repr(exc),traceback=traceback.format_exc())
    if e and e.h:
        e.shot(str(out/'failure.png'),scale=4)
finally:
    if e: e.close()
    report['all_original_inputs_unchanged']=all(sha(p)==h for p,h in protected.items())
    assert report['all_original_inputs_unchanged']
    dump()
print(json.dumps({k:report.get(k) for k in ('status','pass_all','error','all_original_inputs_unchanged')}),flush=True)
sys.exit(0 if report['pass_all'] else 1)
