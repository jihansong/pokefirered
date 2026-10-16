#!/usr/bin/env python3
"""Install durable build inputs after the guarded controller/core patch."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
p=argparse.ArgumentParser();p.add_argument("--repo",type=Path,default=Path.cwd());p.add_argument("--stage",type=Path,required=True);p.add_argument("--source",type=Path,required=True);p.add_argument("--write",action="store_true");a=p.parse_args()
r=a.repo.resolve();s=a.stage.resolve();src=a.source.read_bytes()
assert hashlib.sha256(src).hexdigest()=="210bd8b8c196cb83ce25fb35bc8affc0869743bd4a760b4be9fc90047a9ea438","Wrong native96 source"
assert (r/"include/rocket_trainer_portrait.h").is_file(),"Apply guarded core first"
files={"tools/rocket96_encode.py":(s/"tools/rocket96_encode.py").read_bytes(),"work/rocket96-review.mk":(s/"work/rocket96-review.mk").read_bytes(),"graphics/trainers/front_pics/jessie_james_hires.png":src}
rules=(s/"work/rocket96-build-rules.mk").read_bytes();rulepath=r/"graphics_file_rules.mk";old=rulepath.read_bytes()
assert b"ROCKET96_SOURCE" not in old,"Build rules already contain Rocket96; inspect existing state"
for name in files:assert not (r/name).exists(),("Existing file preserved",name)
for name in ("graphics/trainers/front_pics/jessie_james_hires.4bpp","graphics/trainers/palettes/jessie_james_hires.gbapal"):assert not (r/name).exists(),("Existing generated asset preserved",name)
backup=r/"work/rocket96-assets-install-v1";assert not backup.exists(),"Backup directory exists"
compile(files["tools/rocket96_encode.py"],"tools/rocket96_encode.py","exec")
report={"status":"WRITE" if a.write else "PREFLIGHT","default_feature_enabled":False,"new_files":{k:hashlib.sha256(v).hexdigest() for k,v in files.items()},"rules_before":hashlib.sha256(old).hexdigest(),"rules_after":hashlib.sha256(old+b"\n"+rules).hexdigest()}
print(json.dumps(report,indent=2),flush=True)
if not a.write:raise SystemExit()
assert rulepath.read_bytes()==old
backup.mkdir(parents=True);(backup/"graphics_file_rules.mk").write_bytes(old)
for name,content in files.items():
    dest=r/name;dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("xb") as f:f.write(content)
rulepath.write_bytes(old+b"\n"+rules)
subprocess.run(["make","graphics/trainers/front_pics/jessie_james_hires.4bpp","graphics/trainers/palettes/jessie_james_hires.gbapal"],cwd=r,check=True)
for rel,expected,n in (("graphics/trainers/front_pics/jessie_james_hires.4bpp","99f3ff74b5438521ba48e4d7fc403acca7df233f003878ddd525bdba8ab14add",4608),("graphics/trainers/palettes/jessie_james_hires.gbapal","02951ab3bc6bd04dbce501258a13e92e3ba934728bb8249514b41238f835b792",32)):
    b=(r/rel).read_bytes();assert len(b)==n and hashlib.sha256(b).hexdigest()==expected
report["status"]="DURABLE_ASSETS_INSTALLED_DEFAULT_64";(backup/"manifest.json").write_text(json.dumps(report,indent=2),encoding="utf-8");print(report["status"])
