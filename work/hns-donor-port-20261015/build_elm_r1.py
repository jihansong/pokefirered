from pathlib import Path
import subprocess,json,hashlib,datetime
b=Path("work/hns-donor-port-20261015");r={"started_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (b/"elm-build-r1.log").open("w") as f:
    p=subprocess.run(["make","leafgreen","-j2"],stdout=f,stderr=subprocess.STDOUT);r["build_exit"]=p.returncode
    if p.returncode==0:r["syms_exit"]=subprocess.run(["make","GAME_VERSION=LEAFGREEN","syms"],stdout=f,stderr=subprocess.STDOUT).returncode
r["files"]={x:{"bytes":Path(x).stat().st_size,"sha256":hashlib.sha256(Path(x).read_bytes()).hexdigest()} for x in ["pokemonthyl.gba","pokemonthyl.elf","pokemonthyl.sym","saves/pokemonthyl_v1.45.sav"] if Path(x).exists()}
r["finished_utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat();(b/"elm-build-r1.json").write_text(json.dumps(r,indent=2))
