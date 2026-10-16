#!/usr/bin/env python3
"""Native Johto League QA support; only separate QA saves are initialized."""
from pathlib import Path
import hashlib
_boot=Path(__file__).with_name('johto_blackthorn_native_bootstrap.py')
_boot_text=_boot.read_text()
assert hashlib.sha256(_boot_text.encode()).hexdigest()=='2a96b6d26b6f0abbb7a6cc2444ef887cf5e709d8f2373bd2698b086e3d17d032'
exec(compile(_boot_text,str(_boot),'exec'),globals())

assert rom.read_bytes()[0xac:0xb0]==b'BPGE','League candidate must preserve the verified LeafGreen game variant'
LEAGUE_FLAGS=['FLAG_JOHTO_SILVER_LEAGUE_RESOLVED','FLAG_JOHTO_WILL_CLEARED',
 'FLAG_JOHTO_KOGA_CLEARED','FLAG_JOHTO_BRUNO_CLEARED','FLAG_JOHTO_KAREN_CLEARED',
 'FLAG_JOHTO_LANCE_CHAMPION_CLEARED','FLAG_JOHTO_LEAGUE_CLEARED','FLAG_JOHTO_LEAGUE_ARRIVED']
SILVER_L,WILL,KOGA,BRUNO,KAREN,LANCE,L_CLEAR,L_ARRIVED=LEAGUE_FLAGS
SYS='FLAG_SYS_GAME_CLEAR'
LEAGUE_ACTORS=['SILVER_VICTORY_ROAD','WILL','KOGA','BRUNO','KAREN','LANCE_CHAMPION']
ELITE_FLAGS=LEAGUE_FLAGS[1:6]
ELITE_ACTORS=LEAGUE_ACTORS[1:]
_league_original_fixture=fixture
_league_original_snapshot=snapshot
STORY+=LEAGUE_FLAGS+[SYS]
ACTORS+=LEAGUE_ACTORS
def fixture(path,c):
 context=dict(c)
 context['flags']={f:True for f in BLACK_FLAGS}
 context['flags'].update(c.get('flags',{}))
 context['trainers']={n:True for n in BLACK_ACTORS}
 context['trainers'].update(c.get('trainers',{}))
 s=_league_original_fixture(path,context)
 # Eligibility is explicit initialization of this isolated test fixture, never a player/campaign claim.
 s.set_flag(SYS,c.get('flags',{}).get(SYS,True))
 for f in LEAGUE_FLAGS:s.set_flag(f,c.get('flags',{}).get(f,False))
 for n in LEAGUE_ACTORS:s.set_trainer_beaten('TRAINER_JOHTO_'+n,c.get('trainers',{}).get(n,False))
 s.set_var('VAR_TEMP_0',0);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
 s.warp(*c['where']);s.save(str(path));return s
def snapshot(e):
 d=_league_original_snapshot(e);b=blocks(e)
 for f in LEAGUE_FLAGS+[SYS]:d['flags'][f]=b.flag(f)
 for n in LEAGUE_ACTORS:d['trainers'][n]=b.trainer_beaten('TRAINER_JOHTO_'+n)
 return d
ROOMS=dict(zip(ELITE_ACTORS,['JohtoLeague_WillsRoom','JohtoLeague_KogasRoom','JohtoLeague_BrunosRoom',
 'JohtoLeague_KarensRoom','JohtoLeague_LancesRoom']))
TEAMS={
 'SILVER_VICTORY_ROAD':['SNEASEL','CROBAT','MAGNETON','GENGAR','ALAKAZAM','FERALIGATR'],
 'WILL':['XATU','JYNX','EXEGGUTOR','SLOWBRO','XATU'],
 'KOGA':['ARIADOS','VENOMOTH','FORRETRESS','MUK','CROBAT'],
 'BRUNO':['HITMONTOP','HITMONLEE','HITMONCHAN','ONIX','MACHAMP'],
 'KAREN':['UMBREON','VILEPLUME','MURKROW','GENGAR','HOUNDOOM'],
 'LANCE_CHAMPION':['GYARADOS','DRAGONITE','DRAGONITE','AERODACTYL','CHARIZARD','DRAGONITE']}
POSITIONS={n:(ROOMS[n],6,7) for n in ELITE_ACTORS}
POSITIONS['SILVER_VICTORY_ROAD']=('JohtoVictoryRoad_1F',16,9)
PRIOR={n:{f:True for f in ELITE_FLAGS[:i]} for i,n in enumerate(ELITE_ACTORS)}
WINS=dict(zip(LEAGUE_ACTORS,[SILVER_L]+ELITE_FLAGS))
_battle=Path(__file__).with_name('johto_blackthorn_native_battles.py')
_battle_text=_battle.read_text()
assert hashlib.sha256(_battle_text.encode()).hexdigest()=='bef8b0f3910e74b9f0913f7d9657fb50b78298f0ee009200ba84650e4b8ebccf'
import ast
_tree=ast.parse(_battle_text)
_nodes=[n for n in _tree.body if isinstance(n,ast.FunctionDef) and n.name in ('legal_checksum','party_identity')]
assert len(_nodes)==2
exec(compile(ast.Module(body=_nodes,type_ignores=[]),str(_battle),'exec'),globals())
def battle_attempt(e,name,loss,prepared,tag):
 e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
 native_step(e,'UP');e.press('A',hold=3,after=12);mash_until(e,e.in_battle,300);assert menu(e)
 assert e.u16(e.sym('gTrainerBattleOpponent_A'))==const('TRAINER_JOHTO_'+name)
 raw=e.read(syms['gEnemyParty'],600)
 enemies=[Mon(bytearray(raw),i*100).species() for i in range(6) if Mon(bytearray(raw),i*100).has_species()]
 assert enemies==[const('SPECIES_'+n) for n in TEAMS[name]],(tag,'wrong trainer team',enemies)
 turns=0
 while menu(e):
  assert turns<120,'native battle did not finish'
  fight_one_turn(e,loss=loss);turns+=1
 outcome=e.u8(e.sym('gBattleOutcome'));assert outcome==(2 if loss else 1),(tag,'battle outcome',outcome)
 settle(e);after=snapshot(e)
 flags=dict(before['flags']);trainers=dict(before['trainers']);trainers[name]=not loss
 if not loss:flags[WINS[name]]=True
 assert after['flags']==flags,(tag,'explicit native victory flags',after['flags'],flags)
 assert after['trainers']==trainers,(tag,'native trainer flags',after['trainers'],trainers)
 assert after['pc']==before['pc']==bytes(prepared.blocks['storage'])
 party_identity(before,after,tag)
 for item in ITEMS:assert after['items'][item]==before['items'][item],(tag,item)
 for field in ['pc_hm','pc_hm3','pc_hm02','pc_hm04','pc_hm07']:assert after[field]==before[field],(tag,field)
 for old,new in zip(before['dex'],after['dex']):
  assert old[0]==new[0] and all(not a or b for a,b in zip(old,new)),(tag,'lost dex history')
 assert after['flags'][L_CLEAR]==before['flags'][L_CLEAR],'winning alone fabricated a HOF registration'
 e.shot(str(out/(tag+'.png')),scale=3);saved=flash_reload(e,tag)
 return {'case':tag,'native_outcome':outcome,'actual_turns':turns,'native_enemy_species':enemies,
  'save':saved,'legal_party_identity_pc_and_history_preserved':True,'forced_memory_writes':0,'forced_battle_outcomes':0}
