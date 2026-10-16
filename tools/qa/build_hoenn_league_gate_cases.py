import json
from pathlib import Path
C=[]; B=[f'flag FLAG_HOENN_BADGE{i:02d}_GET 1' for i in range(1,9)]
T=['TRAINER_HOENN_'+n for n in ['SIDNEY','PHOEBE','GLACIA','DRAKE','WALLACE']]
R=['EverGrandeCity_'+n for n in ['SidneysRoom','PhoebesRoom','GlaciasRoom','DrakesRoom','ChampionsRoom']]
V='VAR_HOENN_LEAGUE_PROGRESS'; F='FLAG_HOENN_LEAGUE_CLEAR'; L='EverGrandeCity_PokemonLeague_1F'
def add(n,e,s): C.append(dict(name=n,base='saves/pokemonthyl_v1.2.sav',edit=['noquestlog','fastbattle',f'flag {F} 0']+e,steps=s))
for i in range(1,9):
 add('missing_badge_%d'%i,[f'warp {L} 9 3',*B,f'flag FLAG_HOENN_BADGE{i:02d}_GET 0'],['UP','A','mash 100',f'expect map {L}',f'expect var {V} = 0',f'expect flag {F} = 0','expect overworld'])
for i in range(5):
 common=[*B,*[f'trainer {t} {int(j<i)}' for j,t in enumerate(T)],f'warp {R[i]} 6 10']
 for n,k in [('too_low',i),('too_high',7)]:
  add(f'stage_{n}_{i}',[*common,f'var {V} {k}'],['mash 100',f'expect map {L}',f'expect flag {F} = 0','expect overworld'])
 if i:
  add('missing_prior_win_%d'%i,[*common,f'var {V} {i+1}',f'trainer {T[i-1]} 0'],['mash 100',f'expect map {L}',f'expect flag {F} = 0','expect overworld'])
 if i<4:
  add('resume_after_win_%d'%i,[*B,*[f'trainer {t} {int(j<=i)}' for j,t in enumerate(T)],f'warp {R[i]} 6 6',f'var {V} {i+2}'],['UP','A','mash 100',f'expect map {R[i+1]}',f'expect var {V} = {i+2}',f'expect flag {F} = 0','expect overworld'])
for i in range(5):
 add('hof_missing_win_%d'%i,[*B,*[f'trainer {t} {int(j!=i)}' for j,t in enumerate(T)],'warp EverGrandeCity_HallOfFame 7 10',f'var {V} 6'],['mash 100',f'expect map {L}',f'expect flag {F} = 0','expect overworld'])
add('rematch_lobby_keeps_completed_region',[f'flag {F} 1',*B,*[f'trainer {t} 1' for t in T],f'var {V} 7',f'warp {L} 9 6'],['wait 60',f'expect flag {F} = 1',f'expect var {V} = 0',*[f'expect trainer {t} = 0' for t in T],'expect overworld'])
for nm,x,y,tr,badge,tm,flag in [('MossdeepCity_Gym',24,8,'TRAINER_HOENN_TATE_AND_LIZA_1','FLAG_HOENN_BADGE07_GET','ITEM_TM04','FLAG_HOENN_GOT_TM04'),('SootopolisCity_Gym_1F',8,3,'TRAINER_HOENN_JUAN_1','FLAG_HOENN_BADGE08_GET','ITEM_TM03','FLAG_HOENN_GOT_TM03')]:
 add(nm+'_retalk_no_duplicate',[f'warp {nm} {x} {y}',f'trainer {tr} 1',f'flag {badge} 0',f'flag {flag} 0',f'item {tm} 0'],['UP','A','mash 100',f'expect flag {badge} = 1',f'expect flag {flag} = 1',f'expect item {tm} = 1','A','mash 100',f'expect item {tm} = 1','expect overworld'])
add('mossdeep_needs_two_healthy',['warp MossdeepCity_Gym 23 8','party 1','hp 0 100','trainer TRAINER_HOENN_TATE_AND_LIZA_1 0','flag FLAG_HOENN_BADGE07_GET 0'],['UP','A','mash 100','expect trainer TRAINER_HOENN_TATE_AND_LIZA_1 = 0','expect flag FLAG_HOENN_BADGE07_GET = 0','expect overworld'])
p=Path('tools/qa/cases/hoenn-league-v1-gates.jsonl');p.write_text(''.join(json.dumps(c)+'\n' for c in C));assert len(C)==35;print(len(C))
