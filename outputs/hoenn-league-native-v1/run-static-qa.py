from pathlib import Path
import subprocess,json
r=Path('/workspaces/pokefirered');d=Path('/workspaces/pokefirered/outputs/hoenn-league-native-v1')
jobs=[('min-events', ['python3', '-B', 'tools/qa/eventcheck.py', 'tools/qa/cases/hoenn-league-v1-min.jsonl', '--rom', 'poketitlev8qa.gba', '--shots', '/workspaces/pokefirered/outputs/hoenn-league-native-v1/min-events']), ('league-maps', ['python3', '-B', 'tools/qa/mapsmoke.py', 'MossdeepCity_Gym', 'SootopolisCity_Gym_1F', 'EverGrandeCity_PokemonLeague_1F', 'EverGrandeCity_SidneysRoom', 'EverGrandeCity_PhoebesRoom', 'EverGrandeCity_GlaciasRoom', 'EverGrandeCity_DrakesRoom', 'EverGrandeCity_ChampionsRoom', 'EverGrandeCity_HallOfFame', '--rom', 'poketitlev8qa.gba', '--base', 'saves/pokemonthyl_v1.2.sav', '--shots', '/workspaces/pokefirered/outputs/hoenn-league-native-v1/league-maps', '--shots-all', '-j', '2'])]
results={}
for name,cmd in jobs:
 with (d/(name+".log")).open("w") as f:p=subprocess.run(cmd,cwd=r,stdout=f,stderr=subprocess.STDOUT)
 results[name]=p.returncode
 (d/"static-qa-results.json").write_text(json.dumps(results))
 print(name,p.returncode,flush=True)
