from pathlib import Path
import subprocess,json,hashlib
repo=Path('/workspaces/pokefirered');task=repo/'work/hoenn-resume-20261014';fixed=task/'fixed-profile-rom';abi=task/'abi-profile'
subprocess.run(['python3',str(task/'extract-profile-abi.py'),'--root',str(repo),'--rom',str(fixed/'pokemonthyl.gba'),'--elf',str(fixed/'pokemonthyl.elf'),'--out',str(abi)],cwd=repo,check=True)
probe=abi/'devon-v7-abi.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cmd=['python3',str(task/'native_devon_continuation_r1.py'),'--root',str(repo),'--rom',str(fixed/'pokemonthyl.gba'),'--elf',str(fixed/'pokemonthyl.elf'),'--sav',str(repo/'saves/pokemonthyl_v1.25-items99-iv2x-pp15.sav'),'--abi-json',str(probe),'--out',str(task/'native-continuation-r1'),'--expect-rom-sha',sha(fixed/'pokemonthyl.gba'),'--expect-elf-sha',sha(fixed/'pokemonthyl.elf'),'--expect-abi-sha',sha(probe)]
print('NATIVE_CONTINUATION_START',flush=True);code=subprocess.run(cmd,cwd=repo).returncode
(task/'continuation-exit.json').write_text(json.dumps({'returncode':code}))
