#!/usr/bin/env python3
"""Radio Tower native QA; original SAV remains read-only and all outcomes use game inputs."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_radio_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='bbb842feb5d4cd98813d057411e440d45fb8838126a5a550ff2e1be46f1993ed'
exec(compile(_boot_text,str(_boot),'exec'),globals())

TEAMS={'RADIO_GRUNT_A':['RATICATE','GOLBAT'],'RADIO_GRUNT_B':['GRIMER','MUK'],'RADIO_SCIENTIST':['MAGNEMITE','MAGNETON'],
 'PETREL_RADIO':['KOFFING','KOFFING','KOFFING','WEEZING'],'SILVER_UNDERGROUND':['GOLBAT','MAGNEMITE','HAUNTER','SNEASEL','FERALIGATR'],
 'WAREHOUSE_GRUNT_A':['RATICATE','KOFFING'],'WAREHOUSE_GRUNT_B':['GLOOM','GOLBAT'],'WAREHOUSE_SCIENTIST':['MAGNEMITE','MAGNETON'],
 'ARIANA_RADIO':['ARBOK','GLOOM','MURKROW'],'ARCHER':['HOUNDOUR','KOFFING','HOUNDOOM']}
POSITIONS={'RADIO_GRUNT_A':('GoldenrodCity_RadioTower_2F',10,10),'RADIO_GRUNT_B':('GoldenrodCity_RadioTower_2F',22,14),
 'RADIO_SCIENTIST':('GoldenrodCity_RadioTower_3F',9,14),'PETREL_RADIO':('GoldenrodCity_RadioTower_3F',16,10),
 'SILVER_UNDERGROUND':('GoldenrodUnderground_Basement',16,10),'WAREHOUSE_GRUNT_A':('GoldenrodWarehouse',9,10),
 'WAREHOUSE_GRUNT_B':('GoldenrodWarehouse',23,10),'WAREHOUSE_SCIENTIST':('GoldenrodWarehouse',16,14),
 'ARIANA_RADIO':('GoldenrodCity_RadioTower_4F',16,10),'ARCHER':('GoldenrodCity_RadioTower_5F',16,10)}
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
def battle_fixture(path,name,loss=False):
 flags={}
 if name=='SILVER_UNDERGROUND':flags[ACCESS]=True
 if name=='ARCHER':flags[DIRECTOR]=True
 trainers={'ARIANA_RADIO':True} if name=='ARCHER' else {}
 return fixture(path,{'where':POSITIONS[name],'loss':loss,'flags':flags,'trainers':trainers})
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
 if not loss:
  if name=='PETREL_RADIO':flags[ACCESS]=True;flags[HPETREL]=True
  if name=='SILVER_UNDERGROUND':flags[HSILVER]=True
  if name=='ARCHER':flags[RADIO]=True
 assert after['flags']==flags,(tag,'post-victory script flags',after['flags'],flags)
 assert after['trainers']==trainers,(tag,'trainer record')
 assert after['pc']==before['pc']==bytes(prepared.blocks['storage'])
 party_identity(before,after,tag)
 for item in ITEMS:assert after['items'][item]==before['items'][item],(tag,item)
 for key in ['pc_hm','pc_hm3','pc_hm02','pc_hm04']:assert after[key]==before[key],(tag,key)
 for old,new in zip(before['dex'],after['dex']):assert old[0]==new[0] and all(not a or b for a,b in zip(old,new)),(tag,'dex preservation')
 if not loss and name in ('PETREL_RADIO','SILVER_UNDERGROUND','ARCHER'):
  object_absent(e,2 if name=='PETREL_RADIO' else 1)
 e.shot(str(out/(tag+'.png')),scale=3);saved=flash_reload(e,tag)
 if not loss and name in ('PETREL_RADIO','SILVER_UNDERGROUND','ARCHER'):
  object_absent(e,2 if name=='PETREL_RADIO' else 1)
 return {'case':tag,'turns':turns,'native_outcome':outcome,'enemies':actual,'save':saved,'pc_preserved':True,
  'player_pid_ot_species_and_checksum_preserved':True,'forced_memory_writes':0,'forced_battle_outcomes':0}
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='radio-native-battles-') as td:
  for name,loss in [(n,False) for n in RADIO_ACTORS]+[('PETREL_RADIO',True),('ARCHER',True)]:
   tag=name.lower()+('_loss' if loss else '_win')
   target=Path(td)/(tag+'.sav');prepared=battle_fixture(target,name,loss)
   with ReadOnlyEmu(str(rom),str(target),sym='') as e:row=battle_attempt(e,name,loss,prepared,tag)
   results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sh in originals.items():assert digest(path.read_bytes())==sh,('original changed',str(path))
assert len(results)==12
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'cases':results,'all_pass':True,'original_files_unchanged':True,'forced_memory_writes':0,'forced_battle_outcomes':0},indent=2))
