"""Fresh requested maps/capture code plus any completed R7 outputs, no game writes."""
import hashlib
import importlib.util
import json
from pathlib import Path

base = Path(__file__).with_name("collect_heartbeat_sources_r1.py")
assert hashlib.sha256(base.read_bytes()).hexdigest() == "d025b709972680c7841d6afca9b874b244ffe41dce52d455dda20e431e8c5902"
spec = importlib.util.spec_from_file_location("heartbeat_readonly_export", base)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
root = Path("/workspaces/pokefirered")
module.FILES += [
    "src/region_map.c", "src/party_menu.c", "src/data/party_menu.h",
    "include/party_menu.h", "src/menu.c", "include/constants/maps.h",
    "src/fieldmap.c", "src/metatile_behavior.c", "include/fieldmap.h",
    "include/global.fieldmap.h", "include/constants/metatile_behaviors.h",
    "include/constants/region_map_sections.h", "data/maps/map_groups.json",
    "data/layouts/layouts.json",
    "tools/hoenn_import/patches/SlateportCity_OceanicMuseum_2F.scripts.inc",
    "work/heartbeat-20261014T112944Z/r7-execution.log",
]
wanted = {"RuinsValley", "VermilionCity", "KantoAirport", "JohtoCherrygroveAirstrip",
          "CherrygroveCity", "Route29", "NewBarkTown", "NewBarkTown_ElmsLab"}
layouts = json.loads((root / "data/layouts/layouts.json").read_text())["layouts"]
for folder in (root / "data/maps").iterdir():
    if not folder.is_dir() or not (folder.name in wanted or
        "ElmsLab" in folder.name or "CherrygroveAirstrip" in folder.name):
        continue
    map_path = folder / "map.json"
    if not map_path.is_file():
        continue
    data = json.loads(map_path.read_text())
    for name in ("map.json", "scripts.inc", "text.inc"):
        candidate = folder / name
        if candidate.is_file():
            module.FILES.append(str(candidate.relative_to(root)))
    matches = [entry for entry in layouts if entry["id"] == data["layout"]]
    assert len(matches) == 1, (folder.name, data["layout"])
    for key in ("border_filepath", "blockdata_filepath"):
        rel = matches[0][key]
        assert (root / rel).resolve().is_relative_to(root)
        module.FILES.append(rel)
for rel, pattern in [
    ("work/hoenn-resume-20261014/native-dewford-heal-brawly-r7", "*.json"),
    ("work/hoenn-resume-20261014/native-dewford-heal-brawly-r7", "*.png"),
    ("work/hoenn-resume-20261014/native-dewford-heal-brawly-r7", "*.sav"),
    ("work/heartbeat-20261012T1131", "*.py"),
]:
    for candidate in (root / rel).glob(pattern):
        if candidate.is_file() and candidate.resolve().is_relative_to(root):
            module.FILES.append(str(candidate.relative_to(root)))
module.FILES = list(dict.fromkeys(module.FILES))
if __name__ == "__main__":
    module.main()
