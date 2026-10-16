from pathlib import Path
import subprocess,json,hashlib
repo=Path('/workspaces/pokefirered');w=repo/'work/misty-profile-20261014'
with (w/'build-profile.log').open('wb') as f:
 subprocess.run(['make','GAME_VERSION=LEAFGREEN','rom','syms','-W','graphics/object_events/pics/people/misty_companion_season1.png'],cwd=repo,stdout=f,stderr=subprocess.STDOUT,check=True)
protected=json.loads((w/'protected-original-saves.json').read_text())
for name,wanted in protected.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==wanted
j={n:hashlib.sha256((repo/n).read_bytes()).hexdigest() for n in ['pokemonthyl.gba','pokemonthyl.elf']};j['pass']=True;j['all_original_SAVs_unchanged']=True
(w/'build-profile-result.json').write_text(json.dumps(j,indent=2))
