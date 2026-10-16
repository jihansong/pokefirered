#!/usr/bin/env python3
"""Ecruteak native map connections and services. The original SAV is immutable."""
from pathlib import Path
import argparse,hashlib,json
p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--out',required=True);a=p.parse_args()
base=Path(a.base);original=hashlib.sha256(base.read_bytes()).hexdigest()
flags={f'FLAG_BADGE{i:02d}_GET':1 for i in range(1,9)}
flags.update({f'FLAG_JOHTO_{k}':1 for k in ['ARRIVAL_BRIEFED','MET_LAB_ASSISTANT','ELM_REPORT_DELIVERED','BADGE01_GET','SPROUT_TOWER_CLEARED','SLOWPOKE_WELL_CLEARED','KURT_REPORT_DELIVERED','BADGE02_GET','SILVER_AZALEA_DEFEATED','ILEX_FARFETCHD_RETURNED','ILEX_CUT_BRIEFED','GOLDENROD_RESEARCH_REGISTERED','WHITNEY_ENCOURAGED','BADGE03_GET','SQUIRTBOTTLE_RECEIVED','SUDOWOODO_CLEARED','SILVER_BURNED_TOWER_DEFEATED']})
cases=[]
def add(name,where,steps,edit=()):
 cases.append({'name':'johto_ecruteak_'+name,'base':str(base),'edit':['warp '+where,'noquestlog','var VAR_REPEL_STEP_COUNT 250']+[f'flag {k} {v}' for k,v in flags.items()]+list(edit),
 'steps':['wait 60']+steps+[f'expect flag FLAG_BADGE{i:02d}_GET = 1' for i in range(1,9)]+['expect flag FLAG_JOHTO_BADGE03_GET = 1','expect flag FLAG_JOHTO_SUDOWOODO_CLEARED = 1']})
for name,where,move,dst in [
 ('goldenrod_north_into_gate','GoldenrodCity 21 4','UP','GoldenrodCity_NorthGate'),
 ('north_gate_back_goldenrod','GoldenrodCity_NorthGate 7 9','DOWN 2','GoldenrodCity'),
 ('north_gate_into_route35','GoldenrodCity_NorthGate 7 2','UP','JohtoRoute35'),
 ('route35_back_north_gate','JohtoRoute35 9 32','UP','GoldenrodCity_NorthGate'),
 ('route35_into_park_gate','JohtoRoute35 9 4','UP','JohtoRoute35_NationalParkGate'),
 ('park_gate_back_route35','JohtoRoute35_NationalParkGate 7 9','DOWN 2','JohtoRoute35'),
 ('park_gate_into_park','JohtoRoute35_NationalParkGate 7 2','UP','JohtoNationalPark'),
 ('park_back_south_gate','JohtoNationalPark 15 33','UP','JohtoRoute35_NationalParkGate'),
 ('park_into_east_gate','JohtoNationalPark 31 19','UP','JohtoNationalPark_Route36Gate'),
 ('east_gate_back_park','JohtoNationalPark_Route36Gate 7 9','DOWN 2','JohtoNationalPark'),
 ('east_gate_into_route36','JohtoNationalPark_Route36Gate 7 2','UP','JohtoRoute36'),
 ('route36_back_east_gate','JohtoRoute36 3 18','UP','JohtoNationalPark_Route36Gate'),
 ('route36_north_connection','JohtoRoute36 25 1','UP 2','JohtoRoute37'),
 ('route37_south_connection','JohtoRoute37 9 22','DOWN 3','JohtoRoute36'),
 ('route37_north_connection','JohtoRoute37 9 1','UP 2','EcruteakCity'),
 ('ecruteak_south_connection','EcruteakCity 19 34','DOWN 3','JohtoRoute37'),
 ('tower_descend_stairs','BurnedTower_1F 23 4','LEFT','BurnedTower_B1F'),
 ('tower_ascend_stairs','BurnedTower_B1F 23 4','RIGHT','BurnedTower_1F'),
 ('center_upstairs','EcruteakCity_PokemonCenter_1F 2 6','LEFT','EcruteakCity_PokemonCenter_2F'),
 ('center_downstairs','EcruteakCity_PokemonCenter_2F 2 6','LEFT','EcruteakCity_PokemonCenter_1F')]:
 add(name,where,[move,'wait 120','expect map '+dst,'expect overworld','shot '+name])
for name,where,dst in [
 ('center','EcruteakCity 8 29','EcruteakCity_PokemonCenter_1F'),
 ('mart','EcruteakCity 33 28','EcruteakCity_Mart'),
 ('gym','EcruteakCity 29 12','EcruteakCity_Gym'),
 ('dance_theater','EcruteakCity 14 15','EcruteakCity_DanceTheater'),
 ('burned_tower','EcruteakCity 7 7','BurnedTower_1F')]:
 add(name+'_roundtrip',where,['UP','wait 120','expect map '+dst,'expect overworld','shot '+name,'DOWN 3','wait 120','expect map EcruteakCity','expect overworld'])
add('center_native_heal','EcruteakCity_PokemonCenter_1F 7 4',['watch Text_WelcomeWantToHealPkmn','UP','wait 30','A','mashtext Text_WelcomeWantToHealPkmn 40','wait 60','A','mash','expect overworld','expect hp 0 = full'],['hp 0 1'])
assert len(cases)==26
target=Path(a.out);assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(''.join(json.dumps(c)+'\n' for c in cases))
assert hashlib.sha256(base.read_bytes()).hexdigest()==original
print(json.dumps({'cases':len(cases),'out':str(target),'source_unchanged':True}))
