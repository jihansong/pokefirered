from pathlib import Path
import subprocess,json,hashlib
r=Path('/workspaces/pokefirered');d=Path('/workspaces/pokefirered/outputs/glyph-performance-review-v1')
with (d/"build.log").open("w") as f:p=subprocess.run(["make","GAME_VERSION=LEAFGREEN","BUILD_NAME=titlev8qa","-j2","rom","syms"],cwd=r,stdout=f,stderr=subprocess.STDOUT)
a={"exit":p.returncode}
if p.returncode==0:a["rom_sha256"]=hashlib.sha256((r/"poketitlev8qa.gba").read_bytes()).hexdigest()
(d/"build-result.json").write_text(json.dumps(a));print(a)
