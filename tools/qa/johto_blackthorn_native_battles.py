#!/usr/bin/env python3
"""Blackthorn native QA; original SAV read-only and native inputs only."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_blackthorn_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='2a96b6d26b6f0abbb7a6cc2444ef887cf5e709d8f2373bd2698b086e3d17d032'
exec(compile(_boot_text,str(_boot),'exec'),globals())

TEAMS={'WILTON':['GOLDEEN','SEAKING'],'VANCE':['PIDGEOTTO','FEAROW'],'ALLEN':['DRATINI','DRAGONAIR'],
 'FRAN':['SEADRA','DRAGONAIR'],'CLAIR':['DRAGONAIR','DRAGONAIR','KINGDRA']}
POSITIONS={'WILTON':('JohtoRoute44',12,14),'VANCE':('JohtoRoute44',31,13),'ALLEN':('BlackthornCity_Gym',4,14),
 'FRAN':('BlackthornCity_Gym',10,12),'CLAIR':('BlackthornCity_Gym',7,7)}
def legal_checksum(raw,label):
 mon=Mon(bytearray(raw),0);decrypted=b''.join(bytes(v) for v in mon.subs().values())
 assert len(decrypted)==48
 checksum=sum(v for(v,)in struct.iter_unpack('<H',decrypted))&0xffff
 assert checksum==struct.unpack_from('<H',raw,28)[0],(label,'party Pokemon checksum mismatch')
 return mon
def party_identity(before,after,label):
 assert after['party_count']==before['party_count']
 for i in range(before['party_count']):
  old=before['party'][i*100:(i+1)*100];new=after['party'][i*100:(i+1)*100]
  a=legal_checksum(old,label+' before');b=legal_checksum(new,label+' after')
  assert old[:8]==new[:8] and a.species()==b.species(),(label,'player PID/OT/species changed',i)
  assert old[19]&1==new[19]&1,(label,'new Bad Egg flag',i)
def battle_fixture(path,name,loss=False,full=False):
 return fixture(path,{'where':POSITIONS[name],'loss':loss,'items':{'ITEM_TM02':999} if full else {}})
def battle_attempt(e,name,loss,prepared,tag):
 e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
 native_step(e,'UP');e.press('A',hold=3,after=12);mash_until(e,e.in_battle,300);assert menu(e)
 assert e.u16(e.sym('gTrainerBattleOpponent_A'))==const('TRAINER_JOHTO_'+name)
 raw=e.read(syms['gEnemyParty'],600)
 actual=[Mon(bytearray(raw),i*100).species() for i in range(6) if Mon(bytearray(raw),i*100).has_species()]
 assert actual==[const('SPECIES_'+n) for n in TEAMS[name]],(tag,'wrong party',actual)
 turns=0
 while menu(e):
  assert turns<90,'native battle failed to finish'
  fight_one_turn(e,loss=loss);turns+=1
 outcome=e.u8(e.sym('gBattleOutcome'));assert outcome==(2 if loss else 1),(tag,'outcome',outcome)
 settle(e);after=snapshot(e);flags=dict(before['flags']);trainers=dict(before['trainers']);trainers[name]=not loss
 if not loss and name=='CLAIR':flags[CLAIR]=True
 assert after['flags']==flags,(tag,'post-victory script flags',after['flags'],flags)
 assert after['trainers']==trainers,(tag,'trainer record')
 assert after['pc']==before['pc']==bytes(prepared.blocks['storage'])
 party_identity(before,after,tag)
 for item in ITEMS:assert after['items'][item]==before['items'][item],(tag,item)
 for key in ['pc_hm','pc_hm3','pc_hm02','pc_hm04','pc_hm07']:assert after[key]==before[key],(tag,key)
 for old,new in zip(before['dex'],after['dex']):assert old[0]==new[0] and all(not a or b for a,b in zip(old,new)),(tag,'dex preservation')
 e.shot(str(out/(tag+'.png')),scale=3);saved=flash_reload(e,tag)
 return {'case':tag,'turns':turns,'native_outcome':outcome,'enemies':actual,'save':saved,'pc_preserved':True,
  'player_pid_ot_species_and_checksum_preserved':True,'forced_memory_writes':0,'forced_battle_outcomes':0}
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='blackthorn-native-battles-') as td:
  for name,loss,full in [(n,False,False) for n in BLACK_ACTORS]+[('CLAIR',True,False),('CLAIR',False,True)]:
   tag=name.lower()+('_loss' if loss else ('_full_tm_win' if full else '_win'))
   target=Path(td)/(tag+'.sav');prepared=battle_fixture(target,name,loss,full)
   with ReadOnlyEmu(str(rom),str(target),sym='') as e:row=battle_attempt(e,name,loss,prepared,tag)
   results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==7
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,
 'original_files_unchanged':True,'forced_memory_writes':0,'forced_battle_outcomes':0},indent=2))
