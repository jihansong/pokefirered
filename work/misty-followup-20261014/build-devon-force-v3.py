from pathlib import Path
import subprocess,json,hashlib
repo=Path("/workspaces/pokefirered");w=repo/"work/misty-followup-20261014"
with (w/"build-devon-force-v3.log").open("wb") as f:
 subprocess.run(["make","GAME_VERSION=LEAFGREEN","rom","syms","-W","data/event_scripts.s"],cwd=repo,stdout=f,stderr=subprocess.STDOUT,check=True)
j={n:hashlib.sha256((repo/n).read_bytes()).hexdigest() for n in ["pokemonthyl.gba","pokemonthyl.elf"]};j["pass"]=True
(w/"build-devon-force-v3-result.json").write_text(json.dumps(j,indent=2))