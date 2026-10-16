#!/usr/bin/env python3
"""Synchronize eight original Kanto badge prerequisites in the three League entry gates."""
from pathlib import Path
import ast,hashlib,json,re,sys
gen=Path('tools/johto/build_johto_league.py');oldgen=gen.read_bytes()
digest=lambda b:hashlib.sha256(b).hexdigest()
assert digest(oldgen)=='ba96cc75de8002aa4e41d6e463bdf5943c05b098a9fed15d67d802d9f4a41bf8'
t=oldgen.decode();a="  scripts[name]=scripts[name].replace(anchor,anchor+'    goto_if_unset FLAG_SYS_GAME_CLEAR, '+target+'\\n',1)\n";b="  scripts[name]=scripts[name].replace(anchor,anchor+'    goto_if_unset FLAG_SYS_GAME_CLEAR, '+target+'\\n',1)\n  if key in ('LeagueGate','Receptionist'):\n   badge_guards=''.join('    goto_if_unset FLAG_BADGE%02d_GET, '%i+target+'\\n' for i in range(1,9))\n   scripts[name]=scripts[name].replace(anchor,anchor+badge_guards,1)\n hof_name='JohtoLeague_HallOfFame'\n hof_anchor='    goto_if_unset FLAG_SYS_GAME_CLEAR, '+hof_name+'_NotReady\\n'\n assert scripts[hof_name].count(hof_anchor)==1\n scripts[hof_name]=scripts[hof_name].replace(hof_anchor,hof_anchor+''.join(\n  '    goto_if_unset FLAG_BADGE%02d_GET, '%i+hof_name+'_NotReady\\n' for i in range(1,9)),1)\n"
assert t.count(a)==1;t=t.replace(a,b);newgen=t.encode();ast.parse(newgen)
assert digest(newgen)=='25bc76f948ff4100a0aa05ffa54776a0ed74e4ed664a50109cf8757503a46ba7'
def story(text):
 tree=ast.parse(text);f=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='johto_league_story')
 ns={};exec(compile(ast.Module(body=[f],type_ignores=[]),'league-story-sync','exec'),ns)
 return ns['johto_league_story']()
before,oldtexts=story(oldgen.decode());after,newtexts=story(t)
paths=["data/maps/JohtoRoute27/scripts.inc","data/maps/JohtoLeague_PokemonCenter_1F/scripts.inc","data/maps/JohtoLeague_HallOfFame/scripts.inc"]
oldhash={"data/maps/JohtoRoute27/scripts.inc":"9b3137badda1d0f0a601795c3571d15535c3905cb16317977b1ba13256b3ddff","data/maps/JohtoLeague_PokemonCenter_1F/scripts.inc":"0b58ea8eaca2ccf87a86d8be89c9ec44467be7616fb9e5fed5d4ce36b547db0f","data/maps/JohtoLeague_HallOfFame/scripts.inc":"90797d7d948ac2c4455bad74f3276fc2d801693c783f8956729240ea0985b0a4"}
newhash={"data/maps/JohtoRoute27/scripts.inc":"51864795b46dfb0a9afd9ba28a459ce3b6026f4fd5af544cb5740e832881759b","data/maps/JohtoLeague_PokemonCenter_1F/scripts.inc":"4847d6f451a694a7fd9900b3efbd71dd3979363409a1b3595606b07470ae6ce6","data/maps/JohtoLeague_HallOfFame/scripts.inc":"a8ca285421e797153cd57d5c266bb3c7fa1eec795f994204ba3ac35ebef4c99a"}
assert oldtexts==newtexts
names=[p.split('/')[2]for p in paths]
assert {n for n in before if before[n]!=after[n]}==set(names)
old={gen:oldgen};new={gen:newgen}
for name,path in zip(names,paths):
 p=Path(path);raw=p.read_bytes();assert raw==before[name].encode()and digest(raw)==oldhash[path],('canonical script changed',path)
 out=after[name].encode();assert digest(out)==newhash[path]
 assert re.findall(r'\b(?:setflag|clearflag|cleartrainerflag)\s+(\w+)',before[name])==re.findall(r'\b(?:setflag|clearflag|cleartrainerflag)\s+(\w+)',after[name])
 for i in range(1,9):assert ('goto_if_unset FLAG_BADGE%02d_GET,'%i)in after[name]
 old[p]=raw;new[p]=out
report={'scope':['Route27 LeagueGate','League Receptionist','Johto Hall of Fame Record'],
 'existing_SYS_GAME_CLEAR_condition_preserved':True,'new_story_flags':0,'save_layout_changed':False,'maps_and_terrain_changed':False,
 'files':[{'path':str(p),'before_sha256':digest(old[p]),'bytes':len(v),'sha256':digest(v)}for p,v in new.items()],'apply':'--apply'in sys.argv}
print(json.dumps(report,indent=2))
if '--apply'in sys.argv:
 backups={p:p.with_name(p.name+'.before-kanto-eight-badge-gates')for p in new};assert all(not p.exists()for p in backups.values())
 for p,b in backups.items():b.write_bytes(old[p])
 for p,v in new.items():p.write_bytes(v)
