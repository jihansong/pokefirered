#!/usr/bin/env python3
"""Create native Violet interaction cases; never writes the input SAV."""
from pathlib import Path
import argparse,json,hashlib
p=argparse.ArgumentParser()
p.add_argument('--base',default='saves/pokemonthyl_v1.2.sav')
p.add_argument('--out',default='tools/qa/cases/johto_violet.jsonl')
a=p.parse_args();r=Path('.').resolve();src=r/a.base
assert src.is_file();original=hashlib.sha256(src.read_bytes()).hexdigest()
A='FLAG_JOHTO_ARRIVAL_BRIEFED';L='FLAG_JOHTO_MET_LAB_ASSISTANT'
E='FLAG_JOHTO_ELM_REPORT_DELIVERED';T='FLAG_JOHTO_SPROUT_TOWER_CLEARED'
H='FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED';B='FLAG_JOHTO_BADGE01_GET'
M='FLAG_JOHTO_GOT_TM40_FROM_FALKNER'
cases=[]
def flag(k,v):return f'expect flag {k} = {v}'
def add(name,where,steps,flags=None,edit=None):
 f={A:1,L:1,E:1,T:0,H:0,B:0,M:0};f.update(flags or {})
 cases.append({'name':'johto_violet_'+name,'base':a.base,'edit':['warp '+where,'noquestlog']+[f'flag {k} {v}' for k,v in f.items()]+(edit or []),'steps':['wait 60']+steps})
def talk(d,label,checks):
 return ['watch '+label,d,'wait 30','A','mash','expect overworld','expect saw '+label+' = 1']+checks
for name,where,d,dst in [
 ('route30_north','JohtoRoute30 9 1','UP 2','JohtoRoute31'),
 ('route31_south','JohtoRoute31 25 18','DOWN 2','JohtoRoute30'),
 ('route31_west','JohtoRoute31 1 13','LEFT 2','VioletCity'),
 ('violet_east','VioletCity 38 13','RIGHT 2','JohtoRoute31')]:
 add(name,where,[d,'wait 90','expect map '+dst,'expect overworld','shot '+name])
for tag,x,y,dst in [
 ('center',7,27,'VioletCity_PokemonCenter_1F'),('mart',31,27,'VioletCity_Mart'),
 ('academy',28,9,'VioletCity_Academy'),('gym',8,10,'VioletCity_Gym'),
 ('tower',20,9,'SproutTower_1F')]:
 add(tag+'_door_roundtrip',f'VioletCity {x} {y}',
 ['UP','wait 120','expect map '+dst,'expect overworld','shot '+tag,
 'DOWN 3','wait 120','expect map VioletCity','expect overworld'])
# Native stairs inspect the current tile: step onto it, then hold the same horizontal direction again.
for tag,where,d,dst in [
 ('tower_1_to_2','SproutTower_1F 9 4','RIGHT 2','SproutTower_2F'),
 ('tower_2_to_1','SproutTower_2F 4 4','LEFT 2','SproutTower_1F'),
 ('tower_2_to_3','SproutTower_2F 9 4','RIGHT 2','SproutTower_3F'),
 ('tower_3_to_2','SproutTower_3F 4 4','LEFT 2','SproutTower_2F')]:
 add(tag,where,[d,'wait 180','expect map '+dst,'expect overworld','shot '+tag])
add('center_heals','VioletCity_PokemonCenter_1F 7 4',
 ['watch Text_WelcomeWantToHealPkmn','UP','wait 30','A',
  'mashtext Text_WelcomeWantToHealPkmn 40','wait 60','A','mash',
  'expect overworld','expect saw Text_WelcomeWantToHealPkmn = 1',
  'expect hp 0 = full','shot nurse_healed'],edit=['hp 0 1'])
add('elder_report_gate','SproutTower_3F 6 9',
 talk('UP','SproutTower_3F_Text_NotReady',[flag(T,0),flag(H,0),
 'expect trainer TRAINER_JOHTO_LI = 0']),{E:0},
 ['trainer TRAINER_JOHTO_LI 0'])
add('falkner_tower_gate','VioletCity_Gym 6 6',
 talk('UP','VioletCity_Gym_Text_NotReady',[flag(B,0),flag(M,0),
 'expect trainer TRAINER_JOHTO_FALKNER = 0']),{T:0},
 ['trainer TRAINER_JOHTO_FALKNER 0'])
add('elder_flash_award_repeat','SproutTower_3F 6 9',
 talk('UP','SproutTower_3F_Text_After',[flag(T,1),flag(H,1),'expect item ITEM_HM05 = 1',
 'A','mash','expect overworld','expect item ITEM_HM05 = 1',flag(H,1)]),
 {T:1},['item ITEM_HM05 0','item ITEM_TM_CASE 1','trainer TRAINER_JOHTO_LI 1'])
add('elder_existing_flash_preserved','SproutTower_3F 6 9',
 talk('UP','SproutTower_3F_Text_After',[flag(H,1),'expect item ITEM_HM05 = 1']),
 {T:1},['item ITEM_HM05 1','trainer TRAINER_JOHTO_LI 1'])
add('elder_claimed_flash_not_reissued','SproutTower_3F 6 9',
 talk('UP','SproutTower_3F_Text_After',[flag(H,1),'expect item ITEM_HM05 = 0']),
 {T:1,H:1},['item ITEM_HM05 0','trainer TRAINER_JOHTO_LI 1'])
kantoflags={f'FLAG_BADGE{i:02d}_GET':1 for i in range(1,9)}
kanto_checks=[flag(k,v) for k,v in kantoflags.items()]
add('falkner_tm_award_repeat_kanto_preserved','VioletCity_Gym 6 6',
 talk('UP','VioletCity_Gym_Text_TM',[flag(B,1),flag(M,1),'expect item ITEM_TM40 = 1',
 'A','mash','expect overworld','expect item ITEM_TM40 = 1']+kanto_checks),
 {T:1,B:1,**kantoflags},['item ITEM_TM40 0','item ITEM_TM_CASE 1','trainer TRAINER_JOHTO_FALKNER 1'])
add('falkner_tm_stack_full_keeps_retry','VioletCity_Gym 6 6',
 talk('UP','VioletCity_Gym_Text_BagFull',[flag(B,1),flag(M,0),
 'expect item ITEM_TM40 = 999']+kanto_checks),
 {T:1,B:1,**kantoflags},['item ITEM_TM40 999','trainer TRAINER_JOHTO_FALKNER 1'])
add('falkner_tm_retry_after_space','VioletCity_Gym 6 6',
 talk('UP','VioletCity_Gym_Text_TM',[flag(B,1),flag(M,1),
 'expect item ITEM_TM40 = 999']+kanto_checks),
 {T:1,B:1,**kantoflags},['item ITEM_TM40 998','trainer TRAINER_JOHTO_FALKNER 1'])
add('falkner_claimed_tm_not_reissued','VioletCity_Gym 6 6',
 talk('UP','VioletCity_Gym_Text_After',[flag(B,1),flag(M,1),'expect item ITEM_TM40 = 0']),
 {T:1,B:1,M:1},['item ITEM_TM40 0','trainer TRAINER_JOHTO_FALKNER 1'])
add('academy_three_region_records','VioletCity_Academy 4 6',
 talk('UP','VioletCity_Academy_Text_Teacher',[flag(E,1),flag(T,0),flag(B,0)]))
negative=dict(cases[14]);negative['name']='johto_violet_negative_report_gate'
negative['steps']=negative['steps']+[flag(T,1)];negative['xfail']=True;cases.append(negative)
assert len(cases)==25
out=r/a.out;out.parent.mkdir(parents=True,exist_ok=True)
raw=''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in cases)
assert not out.exists() or out.read_text()==raw,'existing cases differ; preserve and review'
out.write_text(raw,encoding='utf8')
assert hashlib.sha256(src.read_bytes()).hexdigest()==original
print(json.dumps({'cases':len(cases),'path':str(out),'input_sha256':original,
 'native_execution':'pending','not_covered_by_this_file':['actual battle wins/losses','native flash save and cold reload','wild encounter draws','PC upstairs stairs']}))
