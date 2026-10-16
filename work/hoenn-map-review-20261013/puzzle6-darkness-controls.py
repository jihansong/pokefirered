from pathlib import Path
import sys,json,struct,hashlib
root=Path('/workspaces/pokefirered');out=root/'work/hoenn-map-review-20261013/puzzle6-darkness-controls';out.mkdir(exist_ok=True)
rom=root/'pokemonthyl.gba';elf=root/'pokemonthyl.elf';sav=root/'saves/pokemonthyl_v1.25.sav'
sys.argv=['darkroom-review','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
src=(root/'tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(src.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(src.split('\nresults=[];rows=[]\n')[0],'<verified-readonly-native>','exec'))
results=[]
for flash in [False,True]:
 p=out/('flash-'+str(flash)+'-QA-only.sav');s=SaveFile(str(sav));s.warp('Route110_TrickHousePuzzle6',0,21);s.set_flag('FLAG_SYS_FLASH_ACTIVE',flash);s.save(str(p))
 with ReadOnlyEmu(str(rom),str(p),sym='') as e:
  e.syms=syms;e.boot_continue();e.run(240)
  before=e.location();bf=e.black_fraction();level=e.u8(e.ptr('gSaveBlock1Ptr')+0x30)
  e.shot(str(out/('flash-'+str(flash)+'-initial.png')))
  e.walk('UP',2);e.walk('RIGHT',2);e.run(60)
  after=e.location();rows={'flash_flag_fixture':flash,'flash_level_native':level,'before':before,'after_keys':after,'black_fraction':bf,'field_idle':e.field_idle(),'reset':e.reset_seen(),'party_count':e.u8(e.sym('gPlayerPartyCount'))}
  assert not rows['reset'] and before[:2]==tuple(map_info('Route110_TrickHousePuzzle6')[k] for k in ['group','num'])
  e.shot(str(out/('flash-'+str(flash)+'-after-keys.png')));results.append(rows)
assert results[0]['black_fraction']>0.97 and results[0]['flash_level_native']>0
assert results[1]['black_fraction']<0.97 and results[1]['flash_level_native']==0
assert results[1]['before']!=results[1]['after_keys']
res={'pass':True,'classification':'BLACK caused by requires_flash and unlit native dark-room radius, not a corrupt tileset or reset','native_readonly_no_memory_writes':True,'fixtures_only':True,'rom_sha256':digest(rom.read_bytes()),'cases':results}
(out/'validation.json').write_text(json.dumps(res,indent=2));print(json.dumps(res))
