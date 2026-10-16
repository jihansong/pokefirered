Route29 + Misty front/back R2: four-input integration and native QA bundle

PREPARED ONLY. No product edit, build, emulator run, shipment, or natural story
completion is claimed by this local package. Root is the sole remote executor.
The original natural Elm/hatch R1/R2 tools remain separately preserved.

Exact product inputs (all before SHA guarded):
1 data/layouts/JohtoRoute29/map.bin
2 tools/johto/build_entry.py
3 tools/johto/route29_landscape_boundaries.py (must not already exist)
4 graphics/object_events/pics/people/misty_companion_season1.png

Baseline GBA af2677993a75979fb36f0768c390d1bad7424e61f2d569b5054d40702250d2e8
Baseline ELF 2549852a48935c680e06e81719b54663b9c0efa7fdaccd31d1f4683886c5d64e
Uploaded v1.45 SAV 0949ebf04557a76e2175602e967eefadb7ffb722f2746be8a40ddb1fd66550a9

Independent local raw verification:
- Exactly 241 of 960 map words differ. All collision and elevation bits match.
- All 595 original walkable cells, both 2-tile edge buffers, all 12 tall-grass
  cells, all events/warps/connections/scripts/text/border are preserved.
- Full 32-bit metatile attributes are NOT identical: 99 cells differ only in
  bit29 (render layer). All lower29 bits are identical. Do not overclaim this.
- Approved side frames 2/7/8 and every PNG palette byte are unchanged.
- Independent native tile encoding: e095b1cdcb883a0e9ace966ae7a158f225d93ce9a69c6811bc17e53110f66aaf
- Native palette: 3f8a1c94699742cf122ca29a9a8f0a212f518d940795450888834b84712a76da
- Frames3-6 use the bottom pixel row; actual native walk pictures must be
  reviewed for foot clipping. Source equality alone does not approve visuals.

One reviewed root command, after extracting this folder under
/workspaces/pokefirered/work/resume-v145-20261015/ :

python3 work/resume-v145-20261015/route29-misty-integrated-qa-r1/apply_build_route29_misty_r1.py --root /workspaces/pokefirered --sav /workspaces/pokefirered/saves/pokemonthyl_v1.45.sav --out /workspaces/pokefirered/work/resume-v145-20261015/route29-misty-integration-r1 --apply --native --jobs 2

Omit --apply and --native for a read-only preflight. --out must be a new work
folder. Existing source/GBA/ELF/SYM/MAP are copied to backup before four inputs
are changed. All original user SAV hashes, current headers, critical source,
existing helper hashes, and unrelated already-dirty tracked sources are guarded.
No rollback, deletion, push, or public deployment is performed, even on failure.

Build commands: make leafgreen -j2; make GAME_VERSION=LEAFGREEN syms.
Logs are retained; any build warning refuses PASS. The existing gbagfx tool
regenerates a comparison copy only in work. Current header offsets are compiled
in an isolated cache. All ELF/RAM/save symbols and both ELF/ROM load images are
compared. All actual ROM changes must fit only the original 2304B Misty sprite
and 1920B Route29 blockdata allocations. The original Misty asset, player palette,
and actual ROM side-frame bytes2/7/8 must remain identical.

Native helper reuse:
- existing tools/qa/native_misty_basic_qa.py SHA5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6
- existing tools/qa/johto_violet_native_bootstrap_v1.py SHA83c4557b96c344b241fc6f79e9b17722acfc0b0e81e0f9e6d649ff5d8b1c84bb
- R5 adapts the previously verified R4 input-only eight-case walk tool. Critical
  symbols are uniquely rebound to the actual new ELF; no ambiguous-symbol fallback.
- R5 checks 4 directions x walk/run, 3 native VRAM poses per direction, horizontal
  flip, runtime shared player palette slot, SAVE and cold Continue. Native UP/DOWN
  mid-walk screenshots are also captured for front/back/foot review.
- Route29's same safe helpers check 4 native views, 34 real road steps, western
  and eastern connection crossings and returns, native hiker/sign text, and
  existing tall-grass entry with repel. Random wild battle rates are not tested.
- SAVE compares party/count/PC/location/all saved flag and var blocks/four full
  Dex bitmap buffers/DayCare data across live -> stored -> cold states.

These are explicitly labelled preboot visual/story/position QA clones. All
player Pokemon/PC/dex records stay unchanged. An isolated egg step-counter reset
in a QA-only fixture avoids an unrelated hatch; no user SAV record is altered.
This is not a natural story unlock, continuous whole-region route, or DELTA FPS
certification. After native PASS, root must inspect rendered capture images.
A failure keeps logs, backups and candidate artifacts for review.
