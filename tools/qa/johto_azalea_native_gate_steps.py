#!/usr/bin/env python3
"""Eight native Azalea battles using the verified Violet QA bootstrap.
Usage: python SCRIPT VERIFIED_VIOLET_QA --rom ROM --elf ELF --sav SAV --out NEWDIR
Only temporary copies of the supplied save are played; no game-memory writes.
"""
from pathlib import Path
import ast,hashlib,sys
base=Path(sys.argv.pop(1))
text=base.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='83c4557b96c344b241fc6f79e9b17722acfc0b0e81e0f9e6d649ff5d8b1c84bb','Violet helper differs; inspect before reuse'
assert text.count('\nresults=[]\n')==1
exec(compile(text.split('\nresults=[]\n')[0],str(base),'exec'),globals())
def step_once(e,key):
 start=e.location();e.hold(key)
 try:
  for frames in range(1,91):
   e.run(1)
   if e.location()[2:]!=start[2:]:break
  else:raise AssertionError('native step did not begin')
 finally:e.hold()
 e.run(60)
 return {'held_frames':frames,'start':start,'finish':e.location()}
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='azalea-gate-native-') as td:
  for opened in [False,True]:
   tag='badge_open' if opened else 'badge_locked';path=Path(td)/(tag+'.sav')
   prepared=SaveFile(str(sav))
   for i in range(const('QUEST_LOG_SCENE_COUNT')):prepared.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
   for f in [A,L,E]+K:prepared.set_flag(f,True)
   prepared.set_flag(B,opened);prepared.set_var('VAR_REPEL_STEP_COUNT',250)
   prepared.warp('JohtoRoute32',9,3);prepared.save(str(path))
   with ReadOnlyEmu(str(rom),str(path),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60)
    assert e.location()[2:]==(9,3)
    before=snapshot(e);seen=[False];run=e.run
    token=e.read(syms['JohtoRoute32_Text_BadgeNeeded'],24).split(b'\xff')[0]
    def watch_run(frames=1):
     run(frames)
     if token in e.sym_read('gStringVar4',256):seen[0]=True
    e.run=watch_run
    first=step_once(e,'DOWN')
    if opened:
     assert e.location()[2:]==(9,4),first
     assert e.field_idle() and blocks(e).var('VAR_TEMP_0')==1
     second=step_once(e,'DOWN')
     assert e.location()[2:]==(9,5),second
     assert e.field_idle() and not seen[0]
    else:
     settle(e);assert e.location()[2:]==(9,3),first
     assert e.field_idle() and seen[0] and blocks(e).var('VAR_TEMP_0')==0
     second=None
    e.run=run;after=snapshot(e)
    assert after['flags']==before['flags'] and after['trainers']==before['trainers']
    assert after['pc']==before['pc']==bytes(prepared.blocks['storage'])
    assert after['dex']==before['dex']
    e.shot(str(out/(tag+'.png')),scale=3)
    row={'case':tag,'first_step':first,'second_step':second,'saw_badge_dialogue':seen[0],
     'temp0':blocks(e).var('VAR_TEMP_0'),'pc_dex_flags_preserved':True,'forced_memory_writes':0}
    results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sha in originals.items():assert digest(path.read_bytes())==sha,('original changed',str(path))
(out/'result.json').write_text(json.dumps({'all_pass':len(results)==2,'cases':results,
 'rom_sha256':digest(rom.read_bytes()),'input_sav_sha256':originals[sav]},indent=2))
