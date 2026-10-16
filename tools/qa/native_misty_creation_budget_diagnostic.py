#!/usr/bin/env python3
"""Separate bounded creation diagnostic; original 20F failure is not converted to PASS."""
from pathlib import Path
import ast,hashlib,json,struct
source=Path('tools/qa/native_misty_trainer_call_diagnostic.py').read_text()
assert hashlib.sha256(source.encode()).hexdigest()=='dbee2a33e3e42618859f5df74d9db343915f25be302db73267502bef9b5e35eb'
anchor='\ntry:\n abi=trainer_abi();';assert source.count(anchor)==1
exec(compile(source.split(anchor)[0],'<verified-private-trainer-table-helper>','exec'))
# Read actual call implementation. Only this separate diagnostic receives a 60F cap.
basic=Path('tools/qa/native_misty_basic_qa.py').read_text()
assert hashlib.sha256(basic.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
node=next(n for n in ast.parse(basic).body if isinstance(n,ast.FunctionDef) and n.name=='call')
call_source=ast.get_source_segment(basic,node)
assert call_source.count('for _ in range(20):')==1
assert call_source.count('   v=e.u32(S+88)')==1
call_source=call_source.replace('for _ in range(20):','for _ in range(60):')
call_source=call_source.replace('   v=e.u32(S+88)',"""   elapsed=e.frame()-creation_start
   if elapsed in (10,15,20,21,30,40,50,60):
    raw=e.read(e.sym('gEnemyParty'),600)
    checkpoints.append(dict(elapsed=elapsed,result=hex(e.u32(S+88)),party_sha256=digest(raw),level_bytes=[raw[i*100+84] for i in range(6)],hp_values=[struct.unpack_from('<H',raw,i*100+86)[0] for i in range(6)],callback2=hex(e.callback2())))
   v=e.u32(S+88)""")
exec(compile(call_source,'<separate-60F-observational-native-call>','exec'))
diagnostic={'observational_diagnostic_only':True,'original_call_budget_frames':20,'diagnostic_max_frames':60,'original_basic_timeout_proof_unchanged':True,'product_mutations':0,'native_creation_runs':[]}
expected=[['STARMIE','PSYDUCK','HORSEA'],['STARMIE','PSYDUCK','HORSEA','POLIWHIRL'],['STARMIE','GOLDUCK','SEADRA','POLIWHIRL','CORSOLA'],['STARMIE','GOLDUCK','KINGDRA','POLITOED','CORSOLA','AZUMARILL'],['STARMIE','GOLDUCK','KINGDRA','POLITOED','CORSOLA','AZUMARILL']]
try:
 abi=trainer_abi();table=elf_symbol('gTrainers');fn=elf_symbol('CreateNPCTrainerParty')
 assert table[1]>0 and table[1]%abi['trainer_size']==0
 total=table[1]//abi['trainer_size'];teams=[]
 for stage in range(5):
  tid=const('TRAINER_MISTY_COMPANION_STAGE%d'%stage);assert 0<=tid<total
  b=at(table[0]+tid*abi['trainer_size'],abi['trainer_size'])
  n=b[abi['count']];ptr=struct.unpack_from('<I',b,abi['pointer'])[0]
  assert abi['eos'] in b[abi['name']:abi['name']+abi['name_size']]
  assert n==[3,4,5,6,6][stage] and b[abi['flags']]==const('F_TRAINER_PARTY_CUSTOM_MOVESET')
  assert ptr==syms['sPartyMistyCompanionStage%d'%stage]
  team=[]
  for i in range(n):
   m=at(ptr+i*abi['party_size'],abi['party_size']);sid=struct.unpack_from('<H',m,abi['species'])[0];moves=list(struct.unpack_from('<4H',m,abi['moves']))
   assert sid==const('SPECIES_'+expected[stage][i]) and m[abi['level']]==[48,52,56,60,66][stage]
   assert all(0<v<const('MOVES_COUNT') for v in moves)
   assert abi['eos'] in at(syms['gSpeciesNames']+sid*abi['species_name_size'],abi['species_name_size'])
   team.append(dict(species=sid,level=m[abi['level']],moves=moves))
  teams.append(dict(stage=stage,trainer_id=tid,count=n,team=team))
 diagnostic.update(abi=abi,compiled_table_checks_pass=True,rom_sha256=digest(rom.read_bytes()))
 with Emu(str(rom),str(sav),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30);pristine=e.save_state();before=record(e)
  for team in teams:
   e.load_state(pristine);e.write(e.sym('gBattleTypeFlags'),struct.pack('<I',const('BATTLE_TYPE_TRAINER')))
   checkpoints=[];creation_start=e.frame();entry=dict(stage=team['stage'],trainer_id=team['trainer_id'],checkpoints=checkpoints)
   diagnostic['native_creation_runs'].append(entry)
   try:
    n=call(e,'CreateNPCTrainerParty',e.sym('gEnemyParty'),team['trainer_id'])
    elapsed=e.frame()-creation_start;raw=e.read(e.sym('gEnemyParty'),600);ids=identity(raw,n)
    assert n==team['count'] and [v[2] for v in ids]==[m['species'] for m in team['team']]
    assert [raw[i*100+84] for i in range(n)]==[m['level'] for m in team['team']]
    for i,m in enumerate(team['team']):
     attack=Mon(bytearray(raw),i*100).subs()['A'];assert list(struct.unpack_from('<4H',attack))==m['moves']
    same_records(e,before)
    entry.update(naturally_returned=True,native_frames=elapsed,within_original_20_frame_budget=elapsed<=20,returned_count=n,created_identity=ids,complete_party_sha256=digest(raw),strict_team_and_checksum_pass=True)
    print(json.dumps({'Misty_creation_observation':entry}),flush=True)
   finally:e.load_state(pristine);same_records(e,before)
 diagnostic['all_five_returned_with_exact_team']=len(diagnostic['native_creation_runs'])==5 and all(v.get('strict_team_and_checksum_pass') for v in diagnostic['native_creation_runs'])
finally:
 for f,h in originals.items():assert digest(f.read_bytes())==h,('original file changed',str(f))
 (out/'creation-budget-diagnostic.json').write_text(json.dumps(diagnostic,indent=2))
