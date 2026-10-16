#!/usr/bin/env python3
"""Run the unchanged full Basic native checks with stage/call diagnostics."""
from pathlib import Path
import hashlib,json
q=Path('tools/qa/native_misty_basic_qa.py').read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
def once(old,new):
 global q
 assert q.count(old)==1,(old,q.count(old));q=q.replace(old,new)
once("  raise AssertionError('native call did not return: '+name)","""  diag=dict(function=name,args=list(args),stage=globals().get('stage'),frame=e.frame(),callback2=hex(e.callback2()),scratch=hex(S),scratch_bytes=e.read(S,96).hex(),result=hex(e.u32(S+88)),enemy_party_hex=e.read(e.sym('gEnemyParty'),600).hex(),battle_type_flags=e.u32(e.sym('gBattleTypeFlags')),reset_seen=e.reset_seen())
  print(json.dumps({'misty_basic_call_failure':diag}),flush=True)
  (out/'basic-call-failure.json').write_text(json.dumps(diag,indent=2))
  raise AssertionError('native call did not return: '+name)""")
once("   n=call(e,'CreateNPCTrainerParty',e.sym('gEnemyParty'),const('TRAINER_MISTY_COMPANION_STAGE%d'%stage))","""   tid=const('TRAINER_MISTY_COMPANION_STAGE%d'%stage);start=e.frame()
   diag=dict(stage=stage,trainer_id=tid,enemy_party=hex(e.sym('gEnemyParty')),callback2=hex(e.callback2()),battle_type_flags=e.u32(e.sym('gBattleTypeFlags')),growth_flags={f:blocks(e).flag(f) for f in growth})
   print(json.dumps({'misty_basic_stage_before':diag}),flush=True)
   n=call(e,'CreateNPCTrainerParty',e.sym('gEnemyParty'),tid)
   diag.update(returned_count=n,native_frames=e.frame()-start)
   print(json.dumps({'misty_basic_stage_after':diag}),flush=True)""")
exec(compile(q,'<unchanged-full-Misty-basic-with-stage-diagnostic>','exec'))
