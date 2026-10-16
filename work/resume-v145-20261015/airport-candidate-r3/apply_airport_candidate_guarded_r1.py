"""Preflight (default) or apply ONLY the reviewed regional airport candidate.

No ROM/SAV writes, build, git commands, remote API, or file removals. All
existing sources must exactly match the candidate's declared input hashes.
"""
import argparse
import hashlib
import json
from pathlib import Path

OLD = {
    "data/layouts/JohtoCherrygroveAirstrip/map.bin",
    "data/maps/JohtoCherrygroveAirstrip/map.json",
    "data/maps/SlateportCity_Harbor/map.json",
    "data/layouts/HoennHarbor/map.bin",
    "tools/hoenn_import/patches/SlateportCity_Harbor.json",
    "tools/hoenn_import/apply_patches.py",
    "data/layouts/layouts.json", "data/maps/map_groups.json",
    "data/event_scripts.s", "src/event_object_movement.c",
}
NEW = {"tools/airports/build_regional_airport_terminals.py"}
for name in ("JohtoAirportTerminal", "HoennAirportExterior", "HoennAirportTerminal"):
    NEW.update("data/maps/"+name+"/"+suffix for suffix in ("map.json","scripts.inc","text.inc"))
    NEW.update("data/layouts/"+name+"/"+suffix for suffix in ("map.bin","border.bin"))


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def safe(root, rel):
    assert not Path(rel).is_absolute() and ".." not in Path(rel).parts
    p=(root/rel).resolve()
    assert p.is_relative_to(root), ("Path escapes root", rel)
    return p


def save_hashes(root):
    return {p.relative_to(root).as_posix():digest(p.read_bytes())
            for p in sorted((root/"saves").rglob("*.sav"))
            if p.is_file() and p.resolve().is_relative_to(root)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--candidate",type=Path,required=True)
    parser.add_argument("--manifest-sha",required=True)
    parser.add_argument("--rom-sha",required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    root=args.root.resolve(strict=True); candidate=args.candidate.resolve(strict=True)
    out=args.out.resolve()
    assert root==Path("/workspaces/pokefirered"), root
    assert out.is_relative_to(root/"work") and not out.exists(), out
    manifest_blob=(candidate/"manifest.json").read_bytes()
    assert digest(manifest_blob)==args.manifest_sha, "Candidate manifest changed"
    manifest=json.loads(manifest_blob)
    assert manifest["kind"]=="unapplied_regional_airport_candidate"
    assert set(manifest["files"])==OLD|NEW, "Candidate target scope changed"
    assert digest((root/"pokemonthyl.gba").read_bytes())==args.rom_sha, "Unexpected current ROM"
    preserved=save_hashes(root)
    assert preserved, "No original SAV files found to protect"
    # Read every input before any product write. A partial upstream rebase or
    # Elm registration change in shared C must fail here, not be overwritten.
    for rel, item in manifest["inputs"].items():
        assert digest(safe(root,rel).read_bytes())==item["sha256"], ("Stale source",rel)
    blobs={}
    for rel,item in manifest["files"].items():
        target=safe(root,rel); source=safe(candidate/"payload",rel)
        blob=source.read_bytes()
        assert len(blob)==item["bytes"] and digest(blob)==item["sha256"], ("Payload changed",rel)
        if rel in OLD:
            assert item["before"] and digest(target.read_bytes())==item["before"]["sha256"]
        else:
            assert item["before"] is None and not target.exists(), ("New file already exists",rel)
        blobs[rel]=blob
    assert save_hashes(root)==preserved
    report=dict(preflight_pass=True, applied=False, native_verified=False,
                canonical_build_performed=False, rom_sha256=args.rom_sha,
                manifest_sha256=args.manifest_sha, protected_saves=preserved,
                target_count=len(blobs), written=[])
    out.mkdir(parents=True)
    if args.apply:
        for rel in sorted(OLD):
            backup=out/"source-backup"/rel
            backup.parent.mkdir(parents=True,exist_ok=True)
            backup.write_bytes(safe(root,rel).read_bytes())
        assert save_hashes(root)==preserved
        for rel in sorted(blobs):
            target=safe(root,rel)
            if rel in OLD:
                assert digest(target.read_bytes())==manifest["files"][rel]["before"]["sha256"]
            else:
                assert not target.exists(), ("Target appeared during preflight",rel)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(blobs[rel])
            assert digest(target.read_bytes())==manifest["files"][rel]["sha256"]
            report["written"].append(rel)
            (out/"application.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
        report["applied"]=True
    assert save_hashes(root)==preserved, "Original SAV files changed"
    assert digest((root/"pokemonthyl.gba").read_bytes())==args.rom_sha
    report["saves_unchanged"]=True
    (out/"application.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("protected_saves","written")},indent=2))


if __name__=="__main__":
    main()
