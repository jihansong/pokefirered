#!/usr/bin/env python3
"""Azalea native interaction fixtures. Never alters an input SAV."""
from pathlib import Path
import argparse,hashlib,json,sys
p=argparse.ArgumentParser();p.add_argument('--base',default='saves/pokemonthyl_v1.2.sav');p.add_argument('--out',default='tools/qa/cases/johto_azalea.jsonl');a=p.parse_args()
sys.path.insert(0,str(Path.cwd()/'tools/qa'))
from gamedata import off
source=Path(a.base);digest=hashlib.sha256(source.read_bytes()).hexdigest()
A='FLAG_JOHTO_ARRIVAL_BRIEFED';L='FLAG_JOHTO_MET_LAB_ASSISTANT';E='FLAG_JOHTO_ELM_REPORT_DELIVERED';B='FLAG_JOHTO_BADGE01_GET'
Q='FLAG_JOHTO_KURT_RESCUE_REQUESTED';W='FLAG_JOHTO_SLOWPOKE_WELL_CLEARED';R='FLAG_JOHTO_KURT_REPORT_DELIVERED';N='FLAG_JOHTO_GOT_NET_BALLS_FROM_KURT';G='FLAG_JOHTO_BADGE02_GET';T='FLAG_JOHTO_GOT_TM06_FROM_BUGSY'
K={f'FLAG_BADGE{i:02d}_GET':1 for i in range(1,9)}
def f(k,v):return f'expect flag {k} = {v}'
cases=[]
def add(name,where,steps,flags=None,edit=None):
 flags={A:1,L:1,E:1,B:1,Q:0,W:0,R:0,N:0,G:0,T:0,**K,**(flags or {})}
 cases.append({'name':'johto_azalea_'+name,'base':a.base,'edit':['warp '+where,'noquestlog']+[f'flag {k} {v}' for k,v in flags.items()]+(edit or []),'steps':['wait 60']+steps+[f(k,1) for k in K]})
def talk(label,checks=(),direction='UP'):
 return ['watch '+label,direction,'wait 30','A','mash','expect overworld','expect saw '+label+' = 1']+list(checks)
for name,where,d,dst in [
 ('violet_south','VioletCity 19 30','DOWN 2','JohtoRoute32'),
 ('route32_north','JohtoRoute32 9 1','UP 2','VioletCity'),
 ('route33_west','JohtoRoute33 1 13','LEFT 2','AzaleaTown'),
 ('azalea_east','AzaleaTown 38 13','RIGHT 2','JohtoRoute33')]:
 add(name,where,[d,'wait 120','expect map '+dst,'expect overworld','shot '+name])
for name,where,dst in [('north_cave','JohtoRoute32 11 58','JohtoRoute32'),('south_cave','JohtoRoute33 26 6','JohtoRoute33')]:
 add(name+'_roundtrip',where,['UP','wait 120','expect map JohtoUnionCave_1F','expect overworld','DOWN 3','wait 120','expect map '+dst,'expect overworld'])
for tag,x,y,dst in [('center',7,23,'AzaleaTown_PokemonCenter_1F'),('mart',30,23,'AzaleaTown_Mart'),('kurt',7,9,'AzaleaTown_KurtsHouse'),('gym',21,10,'AzaleaTown_Gym'),('well',32,7,'SlowpokeWell_1F')]:
 add(tag+'_door_roundtrip',f'AzaleaTown {x} {y}',['UP','wait 120','expect map '+dst,'expect overworld','shot '+tag,'DOWN 3','wait 120','expect map AzaleaTown','expect overworld'])
add('center_heals','AzaleaTown_PokemonCenter_1F 7 4',['watch Text_WelcomeWantToHealPkmn','UP','wait 30','A','mashtext Text_WelcomeWantToHealPkmn 40','wait 60','A','mash','expect overworld','expect hp 0 = full'],edit=['hp 0 1'])
kurt='AzaleaTown_KurtsHouse 4 6';kp='AzaleaTown_KurtsHouse_Text_'
add('kurt_elm_gate',kurt,talk(kp+'BeforeElm',[f(Q,0),f(R,0)]),{E:0})
add('kurt_request_once',kurt,talk(kp+'Request',[f(Q,1),f(W,0),f(R,0)]))
add('kurt_request_repeat',kurt,talk(kp+'Wait',[f(Q,1),f(W,0),f(R,0)]),{Q:1})
add('kurt_report_reward_repeat',kurt,talk(kp+'Report',[f(R,1),f(N,1),'expect item ITEM_NET_BALL = 3','A','mash','expect overworld','expect item ITEM_NET_BALL = 3']),{Q:1,W:1},['item ITEM_NET_BALL 0'])
add('kurt_full_stack_keeps_story_progress',kurt,talk(kp+'BagFull',[f(R,1),f(N,0),'expect item ITEM_NET_BALL = 999']),{Q:1,W:1},['item ITEM_NET_BALL 999'])
add('kurt_reward_retry_after_space',kurt,talk(kp+'After',[f(R,1),f(N,1),'expect item ITEM_NET_BALL = 999']),{Q:1,W:1,R:1},['item ITEM_NET_BALL 996'])
add('kurt_claimed_reward_not_reissued',kurt,talk(kp+'After',[f(R,1),f(N,1),'expect item ITEM_NET_BALL = 0']),{Q:1,W:1,R:1,N:1},['item ITEM_NET_BALL 0'])
cmd='SlowpokeWell_1F 12 7';cp='SlowpokeWell_1F_Text_'
add('commander_request_gate',cmd,talk(cp+'NoRequest',[f(W,0),'expect trainer TRAINER_JOHTO_WELL_COMMANDER = 0']),edit=['trainer TRAINER_JOHTO_WELL_COMMANDER 0'])
for tag,ta,tb in [('neither_guard',0,0),('guard_b_pending',1,0),('guard_a_pending',0,1)]:
 add('commander_'+tag,cmd,talk(cp+'Guards',[f(W,0),'expect trainer TRAINER_JOHTO_WELL_COMMANDER = 0']),{Q:1},[f'trainer TRAINER_JOHTO_WELL_GRUNT_A {ta}',f'trainer TRAINER_JOHTO_WELL_GRUNT_B {tb}','trainer TRAINER_JOHTO_WELL_COMMANDER 0'])
gym='AzaleaTown_Gym 6 5';gp='AzaleaTown_Gym_Text_'
for tag,flags in [('first_badge_missing',{B:0,Q:1,W:1,R:1}),('report_missing',{Q:1,W:1,R:0})]:
 add('bugsy_'+tag,gym,talk(gp+'NotReady',[f(G,0),f(T,0),'expect trainer TRAINER_JOHTO_BUGSY = 0']),flags,['trainer TRAINER_JOHTO_BUGSY 0'])
ready={Q:1,W:1,R:1,G:1}
add('bugsy_tm_award_repeat',gym,talk(gp+'TM',[f(G,1),f(T,1),'expect item ITEM_TM06 = 1','A','mash','expect overworld','expect item ITEM_TM06 = 1']),ready,['trainer TRAINER_JOHTO_BUGSY 1','item ITEM_TM_CASE 1','item ITEM_TM06 0'])
add('bugsy_tm_full_retry_kept',gym,talk(gp+'BagFull',[f(G,1),f(T,0),'expect item ITEM_TM06 = 999']),ready,['trainer TRAINER_JOHTO_BUGSY 1','item ITEM_TM06 999'])
add('bugsy_tm_retry_after_space',gym,talk(gp+'TM',[f(G,1),f(T,1),'expect item ITEM_TM06 = 999']),ready,['trainer TRAINER_JOHTO_BUGSY 1','item ITEM_TM06 998'])
add('bugsy_claimed_tm_not_reissued',gym,talk(gp+'After',[f(G,1),f(T,1),'expect item ITEM_TM06 = 0']),{**ready,T:1},['trainer TRAINER_JOHTO_BUGSY 1','item ITEM_TM06 0'])
for done in [0,1]:
 add('slowpoke_'+('safe' if done else 'worried'),'SlowpokeWell_1F 4 5',talk(cp+('SlowpokeSafe' if done else 'SlowpokeWorried'),[f(W,done)]),{Q:1,W:done})
pos=off('sb1.pos')
add('route32_first_badge_gate','JohtoRoute32 9 3',['watch JohtoRoute32_Text_BadgeNeeded','DOWN','mash','expect overworld','expect saw JohtoRoute32_Text_BadgeNeeded = 1',f'expect deref gSaveBlock1Ptr {pos+2} = 3'],{B:0})
add('route32_first_badge_opens','JohtoRoute32 9 3',['watch JohtoRoute32_Text_BadgeNeeded','DOWN','wait 90','expect overworld','expect var VAR_TEMP_0 = 1','expect saw JohtoRoute32_Text_BadgeNeeded = 0',f'expect deref gSaveBlock1Ptr {pos+2} = 5'])
assert len(cases)==33,len(cases)
dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
raw=''.join(json.dumps(c)+'\n' for c in cases)
assert not dst.exists() or dst.read_text()==raw
dst.write_text(raw,encoding='utf8');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print(json.dumps({'cases':len(cases),'output':str(dst),'input_sav_sha256':digest,'native_execution':'pending'}))
