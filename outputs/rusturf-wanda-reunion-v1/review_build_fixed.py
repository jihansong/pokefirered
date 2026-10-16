import subprocess,json,pathlib
with pathlib.Path('outputs/rusturf-wanda-reunion-v1/build-fixed.log').open('w') as f:r=subprocess.run(['make','GAME_VERSION=LEAFGREEN','BUILD_NAME=titlev8qa','-j2','rom','syms'],stdout=f,stderr=subprocess.STDOUT)
pathlib.Path('outputs/rusturf-wanda-reunion-v1/build-fixed-result.json').write_text(json.dumps({'exit_code':r.returncode}))
