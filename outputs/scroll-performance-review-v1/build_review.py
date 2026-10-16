import pathlib,subprocess,json
with pathlib.Path('outputs/scroll-performance-review-v1/build.log').open('w') as f:r=subprocess.run(['make','GAME_VERSION=LEAFGREEN','BUILD_NAME=titlev8qa','-j2','rom','syms'],stdout=f,stderr=subprocess.STDOUT)
pathlib.Path('outputs/scroll-performance-review-v1/build-result.json').write_text(json.dumps({'exit_code':r.returncode}))
