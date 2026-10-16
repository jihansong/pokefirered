#!/usr/bin/env python3
"""Compiled Misty trainer table + unchanged bounded native-call diagnostic."""
from pathlib import Path
import hashlib,json,struct,subprocess,tempfile
q=Path('tools/qa/native_misty_basic_qa.py').read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
anchor='\nresults=[];rows=[]\n';assert q.count(anchor)==1
prefix=q.split(anchor)[0]
old="  raise AssertionError('native call did not return: '+name)"
new="""  probe=dict(function=name,args=list(args),frame=e.frame(),callback2=hex(e.callback2()),scratch=hex(S),scratch_bytes=e.read(S,96).hex(),result=hex(e.u32(S+88)),enemy_party_head=e.read(e.sym('gEnemyParty'),100).hex(),battle_type_flags=hex(e.u32(e.sym('gBattleTypeFlags'))),reset_seen=e.reset_seen())
  diagnostic['failed_call']=probe
  print(json.dumps({'misty_native_call_failure':probe}),flush=True)
  raise AssertionError('native call did not return: '+name)"""
assert prefix.count(old)==1;prefix=prefix.replace(old,new)
exec(compile(prefix,'<verified-bounded-basic-call-with-diagnostic-only>','exec'))
diagnostic={'native_executed':False,'timeout_frames_unchanged':20,'product_mutations':0}
def trainer_abi():
 expressions={
 'trainer_size':'sizeof(struct Trainer)','name_size':'sizeof(((struct Trainer *)0)->trainerName)',
 'name':'offsetof(struct Trainer,trainerName)','count':'offsetof(struct Trainer,partySize)','flags':'offsetof(struct Trainer,partyFlags)','pointer':'offsetof(struct Trainer,party)',
 'party_size':'sizeof(struct TrainerMonNoItemCustomMoves)','iv':'offsetof(struct TrainerMonNoItemCustomMoves,iv)','level':'offsetof(struct TrainerMonNoItemCustomMoves,lvl)','species':'offsetof(struct TrainerMonNoItemCustomMoves,species)','moves':'offsetof(struct TrainerMonNoItemCustomMoves,moves)',
 'species_name_size':'POKEMON_NAME_LENGTH+1','eos':'EOS'}
 gcc,nm=gd._gcc()
 with tempfile.TemporaryDirectory(prefix='misty-trainer-abi-') as td:
  c=Path(td)/'abi.c';o=Path(td)/'abi.o'
  c.write_text('#include "global.h"\n#include "battle.h"\n#include "characters.h"\n'+'\n'.join('char qa_misty_'+k+'[('+v+')+1];' for k,v in expressions.items())+'\n')
  subprocess.check_call([gcc,'-c','-w','-mthumb','-mabi=apcs-gnu','-march=armv4t','-fcommon','-iquote','include','-DLEAFGREEN','-DREVISION=0','-DENGLISH','-DMODERN=1','-o',str(o),str(c)],cwd=gd.REPO)
  data=subprocess.check_output([nm,'-S',str(o)],text=True)
  result={p[3][9:]:int(p[1],16)-1 for l in data.splitlines() if len(p:=l.split())==4 and p[3].startswith('qa_misty_')}
 assert set(result)==set(expressions)
 return result
def elf_symbol(name):
 hits=[]
 for section in sections:
  if section[1] not in (2,11):continue
  strings=sections[section[6]];names=elf_raw[strings[4]:strings[4]+strings[5]]
  assert section[9]==16
  for pos in range(section[4],section[4]+section[5],16):
   no,value,size,info,other,index=struct.unpack_from('<IIIBBH',elf_raw,pos)
   if names[no:names.find(b'\0',no)].decode('ascii',errors='replace')==name:hits.append((value,size,info,index))
 assert len(hits)==1,(name,hits)
 return hits[0]
def at(addr,size):
 assert 0x08000000<=addr<=0x08000000+len(r.data)-size,('ROM pointer out of bounds',hex(addr),size)
 b=r.at(addr,size);assert len(b)==size
 return b
try:
 abi=trainer_abi();table=elf_symbol('gTrainers');fn=elf_symbol('CreateNPCTrainerParty')
 assert table[0]==syms['gTrainers'] and table[1]>0 and table[1]%abi['trainer_size']==0
 total=table[1]//abi['trainer_size'];rows=[]
 expected=[['STARMIE','PSYDUCK','HORSEA'],['STARMIE','PSYDUCK','HORSEA','POLIWHIRL'],['STARMIE','GOLDUCK','SEADRA','POLIWHIRL','CORSOLA'],['STARMIE','GOLDUCK','KINGDRA','POLITOED','CORSOLA','AZUMARILL'],['STARMIE','GOLDUCK','KINGDRA','POLITOED','CORSOLA','AZUMARILL']]
 for stage in range(5):
  tid=const('TRAINER_MISTY_COMPANION_STAGE%d'%stage);assert 0<=tid<total
  raw=at(table[0]+tid*abi['trainer_size'],abi['trainer_size']);name=raw[abi['name']:abi['name']+abi['name_size']]
  count=raw[abi['count']];flags=raw[abi['flags']];ptr=struct.unpack_from('<I',raw,abi['pointer'])[0]
  assert abi['eos'] in name,'compiled trainerName is not terminated'
  assert count==[3,4,5,6,6][stage] and flags==const('F_TRAINER_PARTY_CUSTOM_MOVESET')
  assert ptr==syms['sPartyMistyCompanionStage%d'%stage],'compiled party pointer does not select reviewed team'
  team=[]
  for i in range(count):
   m=at(ptr+i*abi['party_size'],abi['party_size']);sid=struct.unpack_from('<H',m,abi['species'])[0];moves=list(struct.unpack_from('<4H',m,abi['moves']));level=m[abi['level']]
   assert sid==const('SPECIES_'+expected[stage][i]) and level==[48,52,56,60,66][stage]
   assert all(0<move<const('MOVES_COUNT') for move in moves)
   sn=at(syms['gSpeciesNames']+sid*abi['species_name_size'],abi['species_name_size']);assert abi['eos'] in sn,'compiled species name not terminated'
   team.append(dict(species=sid,level=level,moves=moves,species_name_bytes=sn.hex()))
  rows.append(dict(stage=stage,trainer_id=tid,trainer_record=(table[0]+tid*abi['trainer_size']),name_bytes=name.hex(),count=count,party_flags=flags,party_pointer=ptr,team=team))
 diagnostic.update(abi=abi,compiled_trainer_count=total,compiled_table_checks_pass=True,trainers=rows,function_symbol=fn,function_entry=at(fn[0]&~1,24).hex(),rom_sha256=digest(rom.read_bytes()))
 print(json.dumps({'misty_compiled_table':diagnostic}),flush=True)
 with Emu(str(rom),str(sav),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30);pristine=e.save_state();before=record(e)
  e.write(e.sym('gBattleTypeFlags'),struct.pack('<I',const('BATTLE_TYPE_TRAINER')))
  diagnostic['native_executed']=True
  try:
   n=call(e,'CreateNPCTrainerParty',e.sym('gEnemyParty'),rows[0]['trainer_id'])
   diagnostic['creation_returned']=True;diagnostic['returned_count']=n
   diagnostic['created_identities']=identity(e.read(e.sym('gEnemyParty'),600),n)
   assert n==3;same_records(e,before)
  finally:e.load_state(pristine);same_records(e,before)
finally:
 for f,h in originals.items():assert digest(f.read_bytes())==h,('original file changed',str(f))
 (out/'trainer-call-diagnostic.json').write_text(json.dumps(diagnostic,indent=2))
