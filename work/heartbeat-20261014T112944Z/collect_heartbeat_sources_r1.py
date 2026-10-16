"""Snapshot only requested current sources and version provenance; no game edits."""
import argparse
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

FILES = [
    "AGENTS.md", "docs/team/log.md", "docs/INSTALL.md",
    ".claude/agents/engineer.md", ".claude/agents/qa.md",
    "work/animation-recreation-status.json",
    "data/maps/KantoAirport/scripts.inc",
    "data/maps/SlateportCity_Harbor/scripts.inc",
    "src/pokedex.c", "src/pokedex_screen.c", "src/airplane_flight.c",
    "src/pokemon.c", "src/battle_script_commands.c", "src/battle_util.c",
    "include/pokemon.h", "include/constants/pokemon.h",
    "include/constants/flags.h", "include/constants/vars.h",
    "work/hoenn-resume-20261014/native-dewford-dock-r6/validation.json",
]
for floor in ("1F", "2F"):
    for name in ("map.json", "scripts.inc"):
        FILES.append(f"data/maps/SlateportCity_OceanicMuseum_{floor}/{name}")
    for name in ("map.bin", "border.bin"):
        FILES.append(f"data/layouts/HoennSlateportCity_OceanicMuseum_{floor}/{name}")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    out = args.out.resolve()
    assert root == Path("/workspaces/pokefirered"), root
    assert out.is_relative_to(root / "work") and not out.exists(), out
    state = {"created_utc": datetime.now(timezone.utc).isoformat(),
             "product_edits": False, "emulator_executed": False,
             "files": {}, "missing": [], "versions": {}, "preserved_inputs": {}}
    loaded = {}
    for rel in FILES:
        source = root / rel
        if not source.is_file():
            state["missing"].append(rel)
            continue
        assert source.resolve().is_relative_to(root), source
        blob = source.read_bytes()
        loaded[rel] = blob
        state["files"][rel] = {"sha256": sha(blob), "bytes": len(blob)}
    for rel in ("pokemonthyl.gba", "pokemonthyl.elf",
                "saves/pokemonthyl_v1.4.sav",
                "saves/pokemonthyl_v1.4-synced-recovered.sav",
                "work/hoenn-resume-20261014/dock-fix-rebound-abi-r1.json",
                "work/hoenn-resume-20261014/native-dewford-dock-r6/continuous-Dewford-dock-only-native-QA-only.sav"):
        source = root / rel
        if source.is_file():
            state["versions"][rel] = {"sha256": sha(source.read_bytes()),
                                      "bytes": source.stat().st_size}
        else:
            state["missing"].append(rel)
    state["preserved_inputs"] = {
        str(p.relative_to(root)): sha(p.read_bytes())
        for p in (root / "saves").glob("*.sav") if p.is_file()
    }
    loaded["git-status.txt"] = subprocess.check_output(
        ["git", "status", "--short", "--branch"], cwd=root)
    loaded["git-recent.txt"] = subprocess.check_output(
        ["git", "log", "-5", "--oneline"], cwd=root)
    assert all(sha((root / rel).read_bytes()) == item["sha256"]
               for rel, item in state["files"].items())
    assert state["preserved_inputs"] == {
        str(p.relative_to(root)): sha(p.read_bytes())
        for p in (root / "saves").glob("*.sav") if p.is_file()
    }
    out.mkdir(parents=True)
    manifest = json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8")
    (out / "manifest.json").write_bytes(manifest)
    archive = out / "heartbeat-current-sources-r1.zip"
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as z:
        for rel, blob in loaded.items():
            z.writestr(rel, blob)
        z.writestr("manifest.json", manifest)
    print(json.dumps({"archive": str(archive), "bytes": archive.stat().st_size,
                      "sha256": sha(archive.read_bytes()), "missing": state["missing"],
                      "versions": state["versions"], "saves_unchanged": True}, indent=2))


if __name__ == "__main__":
    main()
