from pathlib import Path
import subprocess,json
r=Path('/workspaces/pokefirered')
a=['python3','-B','work/capture_opening_frlg_music.py','--repo',str(r),'--rom',str(r/'pokemonthyl.gba'),'--video',str(r/'outputs/opening-hooh-color-v5/opening-10s-preview.mp4'),'--out',str(r/'outputs/opening-frlg-music-v6')]
rc=subprocess.run(a,cwd=r).returncode
(r/'work/opening-frlg-music-result.json').write_text(json.dumps({'exit_code':rc}))
