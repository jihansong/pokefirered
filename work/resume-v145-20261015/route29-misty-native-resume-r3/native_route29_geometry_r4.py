"""R3 pins dependency-preflight Misty R7; narrow Route29 native geometry/interaction QA on preboot clones.

Reuses guarded Misty walk definitions, ROM/ELF bindings and existing input
controllers. No forced engine calls, RAM edits, save-state loads or user-save edits.
Fixture visuals are not evidence of natural story progress or whole-region completion.
"""
from pathlib import Path
import argparse,hashlib,json,sys,traceback
ap=argparse.ArgumentParser()
for key in ('root','rom','elf','sav','out','expect-rom-sha','expect-elf-sha','expect-sav-sha','verifier','guard-manifest','walk-runner'):
    ap.add_argument('--'+key,required=True)
outer=ap.parse_args();runner=Path(outer.walk_runner).resolve()
assert hashlib.sha256(runner.read_bytes()).hexdigest()=='4fec42760e54472b5ec86b760c644a51e58df8a761939afbcba15fe42b237c2f'
source=runner.read_text();cut="\ntry:\n    for direction in ['RIGHT','LEFT','UP','DOWN']:"
assert source.count(cut)==1
sys.argv=['verified-Misty-definitions']
for key in ('root','rom','elf','sav','out','expect-rom-sha','expect-elf-sha','expect-sav-sha','verifier','guard-manifest'):
    sys.argv+=['--'+key,str(getattr(outer,key.replace('-','_')))]
exec(compile(source.split(cut)[0],'<hash-verified-input-and-fixture-definitions>','exec'),globals())
protected[runner]=qa_hash_bytes(runner.read_bytes())
report.update(kind='NATIVE_PREBOOT_ROUTE29_GEOMETRY_NOT_NATURAL_STORY',natural_story_completion=False,
              random_wild_battle_tested=False,wild_data_or_encounter_rates_changed=False)
def emit():(out/'route29-validation.json').write_text(json.dumps(report,indent=2)+'\n')

def route_fixture(tag,x,y):
    info=map_info('JohtoRoute29');meta=info['json']
    layouts=json.loads((root/'data/layouts/layouts.json').read_text())['layouts']
    layout=next(row for row in layouts if row.get('id')==meta['layout'])
    word=struct.unpack_from('<H',(root/layout['blockdata_filepath']).read_bytes(),2*(y*layout['width']+x))[0]
    assert not word&0x0c00 and word>>12==3,('Preboot fixture must be on real walkable ground',x,y,hex(word))
    s=SaveFile(str(sav));prior=(bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]),bytes(s.blocks['storage']),[s.dex_state(i) for i in range(1,387)])
    s.warp('JohtoRoute29',x,y)
    for f in [join,hide,'FLAG_SYS_GAME_CLEAR','FLAG_RECEIVED_STARTER_PIKACHU','FLAG_JOHTO_ARRIVAL_BRIEFED','FLAG_JOHTO_MET_LAB_ASSISTANT']+K:s.set_flag(f,True)
    s.set_var('VAR_HAPPINESS_STEP_COUNTER',0);s.set_var('VAR_REPEL_STEP_COUNT',250)
    s.sb1[off('sb1.daycare')+off('walk.daycare.stepCounter')]=0
    for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
    assert prior==(bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]),bytes(s.blocks['storage']),[s.dex_state(i) for i in range(1,387)])
    fixture=out/(tag+'-preboot-visual-QA-only.sav');assert not fixture.exists();s.save(str(fixture))
    return fixture


def begin(tag,x,y):
    global e
    fixture=route_fixture(tag,x,y)
    e=ReadOnlyEmu(str(rom),str(fixture),sym='');e.syms=syms;e.boot_continue();settle(e);e.run(40)
    assert e.location()[:2]==(map_info('JohtoRoute29')['group'],map_info('JohtoRoute29')['num'])
    assert e.location()[2:]==(x,y)
    return record(e)


def finish(tag,pristine):
    global e
    same_records(e,pristine);e.shot(str(out/(tag+'.png')),scale=4)
    report['cases'].append({'case':tag,'pass':True,'position':e.location(),'user_Pokemon_PC_dex_preserved':True,
                            'preboot_visual_fixture':True,'natural_story_progress_proved':False})
    emit();e.close();e=None


def cross(direction,expected_map):
    before=e.location();expect=map_info(expected_map)
    e.hold(direction)
    try:
        for _ in range(180):
            e.run(1);safe(e)
            if e.location()[:2]!=before[:2]:break
        else:raise AssertionError(('Native connection blocked',direction,before))
    finally:e.hold()
    settle(e)
    assert e.location()[:2]==(expect['group'],expect['num']),('Wrong actual map connection',expected_map,e.location())
    return {'before':before,'after':e.location(),'direction':direction}


def actual_text(symbol):
    row=current_elf.unique(symbol)
    raw=r.at(row.addr,512);end=raw.find(b'\xff');assert 0<=end<512
    result=raw[:end+1];assert b'\xfd' not in result
    e.press('UP',hold=2,after=8);e.press('A',hold=2,after=30)
    assert e.read(current_elf.unique('gStringVar4').addr,len(result))==result,('Expected native NPC/sign text not observed',symbol)
    e.shot(str(out/(symbol+'.png')),scale=4);settle(e)


try:
    # Native views show both top and bottom grove caps; each is a labelled
    # preboot position fixture, not a player reaching the route naturally.
    for tag,x,y in [('west-upper-grove',3,5),('center-upper-grove',18,6),('east-upper-grove',36,5),('lower-grove-caps',20,18)]:
        pristine=begin(tag,x,y);finish(tag,pristine)
    pristine=begin('road-walk',2,12)
    for index in range(34):
        step_record('RIGHT',False,'Route29-road-'+str(index))
        if index in (2,16,32):e.shot(str(out/('actual-road-'+str(index)+'.png')),scale=4)
    report['native_SAVE_cold']=flash_reload(e,'Route29-road-save-cold')
    finish('road-walk',pristine)
    for tag,x,direction,dest,reverse in [('west-seam',1,'LEFT','JohtoCherrygroveAirstrip','RIGHT'),('east-seam',38,'RIGHT','NewBarkTown','LEFT')]:
        pristine=begin(tag,x,12)
        one_tile(e,direction)
        outgoing=cross(direction,dest);e.shot(str(out/(tag+'-entered-neighbor.png')),scale=4)
        incoming=cross(reverse,'JohtoRoute29')
        report.setdefault('connection_crossings',[]).append({'case':tag,'outgoing':outgoing,'return':incoming})
        finish(tag,pristine)
    for tag,x,symbol in [('native-hiker',18,'JohtoRoute29_Text_Hiker'),('native-sign',36,'JohtoRoute29_Text_Sign')]:
        pristine=begin(tag,x,11);actual_text(symbol);finish(tag,pristine)
    pristine=begin('native-existing-grass-entry-with-repel',6,9)
    one_tile(e,'UP');assert e.location()[2:]==(6,8)
    finish('native-existing-grass-entry-with-repel',pristine)
    report['pass']=len(report['cases'])==10
    report['status']='complete' if report['pass'] else 'failed'
except Exception as error:
    report.update(status='failed',error=repr(error),traceback=traceback.format_exc())
    if e is not None:
        try:e.shot(str(out/'failure.png'),scale=4);report['failure_position']=e.location();report['failure_callback']=hex(e.callback2())
        except Exception:pass
finally:
    if e is not None:e.close()
    report['original_inputs_unchanged']=all(f.exists() and qa_hash_bytes(f.read_bytes())==h for f,h in protected.items())
    if not report['original_inputs_unchanged']:report['pass']=False;report['status']='failed'
    emit()
print(json.dumps({'pass':report['pass'],'cases':len(report['cases']),'error':report.get('error')}),flush=True)
raise SystemExit(0 if report['pass'] else 1)
