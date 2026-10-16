from pathlib import Path
import subprocess,json
r=Path('/workspaces/pokefirered')
a=['python3','-B','work/capture_title_frlg_music.py','--repo',str(r),'--rom',str(r/'pokemonthyl.gba'),'--video',str(r/'outputs/title-continuous-crackle-v3/title-current-continuous-electricity.mp4'),'--crackle',str(r/'outputs/title-continuous-crackle-v3/continuous-electricity.wav'),'--out',str(r/'outputs/title-frlg-music-v4'),'--protect',str(r/'outputs/title-approved-v3-effects-v1/title-current-native.gif'),'--protect',str(r/'outputs/title-font-python-v3/title-font-candidate-240x160.png')]
rc=subprocess.run(a,cwd=r).returncode
(r/'work/title-frlg-music-result.json').write_text(json.dumps({'exit_code':rc}))
