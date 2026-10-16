#!/usr/bin/env python3
"""Radio Tower native QA; original SAV remains read-only and all outcomes use game inputs."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_radio_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='bbb842feb5d4cd98813d057411e440d45fb8838126a5a550ff2e1be46f1993ed'
exec(compile(_boot_text,str(_boot),'exec'),globals())

cases=[]
def link(tag,where,key,dest):cases.append(dict(name=tag,where=where,key=key,dest=dest))
F1='GoldenrodCity_RadioTower_1F'
F2='GoldenrodCity_RadioTower_2F'
F3='GoldenrodCity_RadioTower_3F'
F4='GoldenrodCity_RadioTower_4F'
F5='GoldenrodCity_RadioTower_5F'
UG='GoldenrodUnderground'
UB='GoldenrodUnderground_Basement'
WH='GoldenrodWarehouse'
link('goldenrod_original_research_lobby',('GoldenrodCity',11,18),'UP',F1)
link('research_lobby_original_exit',(F1,7,10),'DOWN','GoldenrodCity')
link('research_lobby_new_upstairs',(F1,13,3),'LEFT',F2)
link('radio_second_floor_back_lobby',(F2,29,2),'RIGHT',F1)
link('radio_second_to_third',(F2,29,2),'LEFT',F3)
link('radio_third_back_second',(F3,29,2),'LEFT',F2)
link('radio_third_into_fourth',(F3,29,2),'RIGHT',F4)
link('radio_fourth_back_third',(F4,29,2),'RIGHT',F3)
link('radio_fourth_into_fifth',(F4,29,2),'LEFT',F5)
link('radio_fifth_back_fourth',(F5,29,2),'LEFT',F4)
link('goldenrod_new_underground',('GoldenrodCity',4,33),'UP',UG)
link('underground_back_city',(UG,8,20),'DOWN','GoldenrodCity')
link('underground_into_basement',(UG,30,2),'RIGHT',UB)
link('basement_back_underground',(UB,29,2),'RIGHT',UG)
link('basement_into_warehouse',(UB,29,2),'LEFT',WH)
link('warehouse_back_basement',(WH,29,2),'LEFT',UB)
assert len(cases)==16
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='radio-native-links-') as td:
  for c in cases:
   target=Path(td)/(c['name']+'.sav')
   prepared=fixture(target,dict(c,flags={ACCESS:True,DIRECTOR:True,HSILVER:True,HPETREL:True},trainers={n:True for n in RADIO_ACTORS if n!='ARCHER'}))
   with ReadOnlyEmu(str(rom),str(target),sym='') as e:
    e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
    taps=cross(e,c);after=snapshot(e)
    for field in ['flags','trainers','items']+PRESERVE:assert after[field]==before[field],(c['name'],'state preservation',field)
    e.shot(str(out/(c['name']+'.png')),scale=3)
    row={'case':c['name'],'from':c['where'],'to':c['dest'],'key':c['key'],'actual_location':e.location(),'fresh_native_taps':taps,
     'party_pc_dex_flags_preserved':True,'forced_memory_writes':0}
    results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==len(cases)
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,'original_files_unchanged':True,'forced_memory_writes':0},indent=2))
