from pathlib import Path
import argparse,hashlib,json,shutil,zipfile,datetime
ap=argparse.ArgumentParser();ap.add_argument("--apply",action="store_true");args=ap.parse_args()
root=Path.cwd().resolve(); base=root/"work/hns-donor-port-20261015"; archive=base/"fresh-target-r1/actual-donor-candidate-r2.zip"
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert H(archive)=="8d91fde1e058f0b34d5d7ff28f54b758c2452f65592dbf6a7812edc07db7b6f8"
pkg=base/"elm-actual-donor-candidate-r2"
if not pkg.exists():
    pkg.mkdir()
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all((pkg/n).resolve().is_relative_to(pkg) for n in z.namelist())
        z.extractall(pkg)
manifest=pkg/"manifest.json";assert H(manifest)=="a5801bbaac1cb71e187e2eafc4b78730a92044de345126f8212ec4d80f743252"
m=json.loads(manifest.read_text()); rows=m["candidate_entries"]; assert len(rows)==10
assert m["all_20_donor_anims_equal_actual_fresh_target"] and not m["target_fresh_animation_header_check_pending"]
expected={"include/constants/event_objects.h","src/data/object_events/object_event_graphics.h","src/data/object_events/object_event_pic_tables.h","src/data/object_events/object_event_graphics_info_pointers.h","src/data/object_events/object_event_graphics_info.h","graphics_file_rules.mk","data/maps/NewBarkTown_ElmsLab/map.json","src/event_object_movement.c","graphics/object_events/pics/people/prof_elm_hns.png","graphics/object_events/palettes/prof_elm_hns.pal"}
assert {x["path"] for x in rows}==expected
for rel,want in m["source_guards"].items():assert H(root/rel)==want,(rel,"guard")
for row in rows:
    rel=row["path"];dst=(root/rel).resolve();src=pkg/"payload"/rel
    assert dst.is_relative_to(root) and H(src)==row["after_sha256"] and src.stat().st_size==row["bytes"]
    assert (H(dst) if dst.exists() else None)==row["before_sha256"],(rel,"before differs")
assert H(root/"pokemonthyl.gba")=="fdd021066ee7ce6fa775407c6be6699ba41583f34d92264e65020bd98950b0f4"
assert H(root/"pokemonthyl.elf")=="7c831da7d91eba1f4132e67a6ce804434003b2249e6abe0af5e19e69d622a53b"
assert H(root/"saves/pokemonthyl_v1.45.sav")=="0949ebf04557a76e2175602e967eefadb7ffb722f2746be8a40ddb1fd66550a9"
saves={str(p.relative_to(root)):H(p) for p in (root/"saves").glob("*.sav")}
result=dict(preflight_pass=True,applied=False,product_inputs=10,source_archive_sha256=H(archive),save_sha256=saves,generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
if args.apply:
    backup=base/"elm-before-integration-r1";assert not backup.exists();backup.mkdir()
    existing=[x["path"] for x in rows if x["before_sha256"] is not None]+["pokemonthyl.gba","pokemonthyl.elf","pokemonthyl.sym","pokemonthyl.map"]
    for rel in existing:
        p=root/rel
        if p.exists():
            q=backup/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    (backup/"baseline.json").write_text(json.dumps(result,indent=2))
    for row in rows:
        dst=root/row["path"];dst.parent.mkdir(parents=True,exist_ok=True);tmp=dst.with_name(dst.name+".elm-donor-temporary");assert not tmp.exists();tmp.write_bytes((pkg/"payload"/row["path"]).read_bytes());tmp.replace(dst)
    assert all(H(root/x["path"])==x["after_sha256"] for x in rows)
    assert all(H(root/p)==h for p,h in saves.items())
    result["applied"]=True;result["backup"]=str(backup)
out=base/("elm-source-application-r1.json" if args.apply else "elm-source-preflight-r1.json");assert not out.exists();out.write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!="save_sha256"}));print("ORIGINAL_SAVES_PRESERVED",len(saves))
