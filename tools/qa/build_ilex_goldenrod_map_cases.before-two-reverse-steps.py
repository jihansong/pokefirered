#!/usr/bin/env python3
"""Ilex/Goldenrod native map links and common services; original SAV is immutable."""
from pathlib import Path
import argparse,hashlib,json
p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--out',required=True);a=p.parse_args()
base=Path(a.base);original=hashlib.sha256(base.read_bytes()).hexdigest()
flags={f'FLAG_BADGE{i:02d}_GET':1 for i in range(1,9)}
flags.update({f'FLAG_JOHTO_{k}':1 for k in ['ARRIVAL_BRIEFED','MET_LAB_ASSISTANT','ELM_REPORT_DELIVERED','BADGE01_GET','SLOWPOKE_WELL_CLEARED','KURT_REPORT_DELIVERED','BADGE02_GET','SILVER_AZALEA_DEFEATED']})
cases=[]
def add(name,where,steps,edit=()):
 cases.append({'name':'johto_ilex_'+name,'base':str(base),'edit':['warp '+where,'noquestlog','var VAR_REPEL_STEP_COUNT 250']+[f'flag {k} {v}' for k,v in flags.items()]+list(edit),
 'steps':['wait 60']+steps+[f'expect flag FLAG_BADGE{i:02d}_GET = 1' for i in range(1,9)]})
for name,where,move,dst in [
 ('azalea_into_gate','AzaleaTown 4 15','UP','IlexForest_AzaleaGate'),
 ('gate_back_azalea','IlexForest_AzaleaGate 7 9','DOWN 2','AzaleaTown'),
 ('south_gate_into_forest','IlexForest_AzaleaGate 7 2','UP','IlexForest'),
 ('forest_back_south_gate','IlexForest 28 40','DOWN','IlexForest_AzaleaGate'),
 ('forest_into_north_gate','IlexForest 6 8','UP','IlexForest_Route34Gate'),
 ('north_gate_back_forest','IlexForest_Route34Gate 7 9','DOWN 2','IlexForest'),
 ('north_gate_into_route34','IlexForest_Route34Gate 7 2','UP','JohtoRoute34'),
 ('route34_back_north_gate','JohtoRoute34 9 42','UP','IlexForest_Route34Gate'),
 ('route34_into_goldenrod','JohtoRoute34 9 1','UP 2','GoldenrodCity'),
 ('goldenrod_back_route34','GoldenrodCity 21 38','DOWN 2','JohtoRoute34')]:
 add(name,where,[move,'wait 120','expect map '+dst,'expect overworld','shot '+name])
for name,where,dst in [
 ('daycare','JohtoRoute34 15 13','JohtoRoute34_DayCare'),
 ('center','GoldenrodCity 8 29','GoldenrodCity_PokemonCenter_1F'),
 ('mart','GoldenrodCity 39 29','GoldenrodCity_Mart'),
 ('gym','GoldenrodCity 33 11','GoldenrodCity_Gym'),
 ('radio','GoldenrodCity 11 18','GoldenrodCity_RadioTower_1F')]:
 parent=where.split()[0]
 add(name+'_roundtrip',where,['UP','wait 120','expect map '+dst,'expect overworld','shot '+name,'DOWN 3','wait 120','expect map '+parent,'expect overworld'])
add('center_native_heal','GoldenrodCity_PokemonCenter_1F 7 4',['watch Text_WelcomeWantToHealPkmn','UP','wait 30','A','mashtext Text_WelcomeWantToHealPkmn 40','wait 60','A','mash','expect overworld','expect hp 0 = full'],['hp 0 1'])
add('daycare_shared_nursery_information','JohtoRoute34_DayCare 5 5',['watch JohtoRoute34_DayCare_Text_Reception','RIGHT','wait 30','A','mash','expect saw JohtoRoute34_DayCare_Text_Reception = 1','expect overworld'])
assert len(cases)==17
target=Path(a.out);assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(''.join(json.dumps(c)+'\n' for c in cases))
assert hashlib.sha256(base.read_bytes()).hexdigest()==original
print(json.dumps({'cases':len(cases),'out':str(target),'source_unchanged':True}))
