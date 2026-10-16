#!/usr/bin/env python3
"""Native city storm/calm budget; genuine party and original saves preserved."""
from pathlib import Path
import hashlib,sys
sys.path.insert(0,str(Path.cwd()/'tools/qa'))
path=Path('tools/qa/native_hoenn_sea_sky_qa.py');src=path.read_text()
assert hashlib.sha256(src.encode()).hexdigest()=='bdc4804e2a6aad9140c12c92777ddb5424586065403fcc8d6ce05381d2fc8511','sea/sky QA source changed'
inject=r"""
import native_storm_budget_helper as budget
assert a.case in ('city-storm','city-calm') and not a.loss
assert off('pokemon')==100 and off('storage')==33744,'save ABI changed'
_storm_po=off('sb1.playerParty');_storm_party=bytes(source.sb1[_storm_po:_storm_po+600])
_storm_count=source.party_count();_storm_storage=bytes(source.blocks['storage']);_storm_dex=digest_dex(source)
party_valid(_storm_party,_storm_count);_genuine=[]
for _slot in range(_storm_count):
 _mon=Mon(bytearray(_storm_party),_slot*100);_raw=_storm_party[_slot*100:(_slot+1)*100]
 if (_mon.personality,_mon.otid)==(3742077845,2839214970):
  assert _mon.species()==const('SPECIES_PIKACHU') and _mon.starter_bit() and not _mon.is_egg()
  assert not _raw[19]&1 and struct.unpack_from('<H',_raw,86)[0]>0
  _genuine.append(_slot)
assert len(_genuine)==1,'original live starter not found'
_storm_samples=0
report.update(mode='native-storm-performance-'+a.case,fixture='temporary city fixture; genuine original party/PC/dex preserved',
 source_storage_full_sha256=sha(_storm_storage),source_party_full_sha256=sha(_storm_party),genuine_starter_slot=_genuine[0],actual_device_fps_measured=False)
def make_party(s):
 s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True);s.set_var('VAR_REPEL_STEP_COUNT',250);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
 assert s.party_count()==_storm_count and bytes(s.sb1[_storm_po:_storm_po+600])==_storm_party
 assert bytes(s.blocks['storage'])==_storm_storage and digest_dex(s)==_storm_dex

def _storm_preserved(em):
 assert not em.in_battle()
 assert em.u8(syms['gPlayerPartyCount'])==_storm_count
 assert em.read(syms['gPlayerParty'],600)==_storm_party,'runtime original party changed'
 assert em.read(em.ptr('gPokemonStoragePtr'),off('storage'))==_storm_storage,'runtime full PC changed'
 assert digest_dex(blocks(em))==_storm_dex,'runtime original dex changed'

def _storm_measure(expected):
 global _storm_samples
 assert _storm_samples==0 and loc_is(e,'SootopolisCity') and e.location()[2:] in ((28,34),(29,34))
 _storm_preserved(e)
 budget.field_budget(a.case,e,elf,rom,syms,expected,wo)
 assert budget._field_done=={(a.case,'SootopolisCity')},'missing storm native coverage'
 _storm_preserved(e);_storm_samples=1;report['storm_budget_pass']=True

_storm_native_save=native_save_reopen
def native_save_reopen(em,expected_pc):
 assert _storm_samples==1,'storm measurement hook did not run'
 _storm_preserved(em);_storm_native_save(em,expected_pc);_storm_preserved(em)
 _saved=SaveFile(em.sav_path)
 assert _saved.party_count()==_storm_count and bytes(_saved.sb1[_storm_po:_storm_po+600])==_storm_party
 assert bytes(_saved.blocks['storage'])==_storm_storage and digest_dex(_saved)==_storm_dex
 report['full_party_storage_dex_native_roundtrip']=True
"""
needle="   report['weather_runtime_before_save']=strict_weather(expected)\n"
assert src.count(needle)==1 and src.count('e=None\ntry:')==1
src=src.replace(needle,needle+'   _storm_measure(expected)\n',1)
src=src.replace('e=None\ntry:',inject+'\ne=None\ntry:',1)
try:
 exec(compile(src,str(path),'exec'),globals())
except SystemExit as exc:
 if exc.code not in (None,0):raise
 if _storm_samples!=1 or budget._field_done!={(a.case,'SootopolisCity')}:
  report['pass']=False;report['error']='storm coverage incomplete';(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
  raise AssertionError('storm coverage incomplete')
 raise
