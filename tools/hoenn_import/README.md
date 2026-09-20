# Hoenn import (pokeemerald → Thunder Yellow)

Scripts that imported the Hoenn maps from a local clone of pret/pokeemerald
(`/root/src/pokeemerald`). Rerunning them regenerates the imported data.

- `import_tilesets.py`: copies Emerald tilesets as `gTileset_Em<Name>` with
  `isEmerald = TRUE` and converts metatile attributes (u16 → FR/LG u32:
  behavior remap, encounter type, terrain, layer type).
- `import_maps.py`: imports layouts (`LAYOUT_HOENN_*`), maps (groups
  `gMapGroup_Hoenn*`), connections and warps. Only objects with no story flag
  are kept. It generates scripts from Emerald's own text (first message),
  Pokémon Center nurses and marts. Secret bases, link rooms and the event
  islands FR/LG already has are skipped.
- `import_wild.py`: appends Emerald's wild encounter tables.

The engine keeps Emerald's tileset split for these layouts (see
`GetNumMetatilesInPrimary` in `src/fieldmap.c`).

Hand-made additions to imported maps go in `patches/<MapName>.json`
(extra `object_events`/`bg_events`...), `patches/<MapName>.scripts.inc` and
`patches/<MapName>.text.inc`. `import_maps.py` merges them in after every
import, so they survive a re-import (e.g. SLATEPORT harbor's airline counter).

- `import_objevent_gfx.py`: copies the Hoenn-only object event sprites
  (59 of them; the graphics id is a u8 and FR/LG has ~69 free slots, so
  generic townsfolk keep their FR/LG stand-ins).
- `import_music.py`: copies the songs the Hoenn maps ask for with their
  voicegroups, keysplit tables and samples, and appends them to the song
  table. Emerald names its voicegroups while FR/LG numbers them, so
  `tools/mid2agb` now takes either form.

Build note: `make` does not track `.incbin`/constant dependencies for the
generated map data. After an import, delete `build/leafgreen/data/maps.o`
(and `map_events.o`) or the ROM keeps the old map headers.
- `import_tileset_anims.py`: copies the animation frames of the imported
  tilesets and generates their callbacks into
  `src/data/tilesets/hoenn_anims.h`, included at the end of
  `src/tileset_anims.c` so it can use that file's queue and counters. Run it
  after `import_tilesets.py`, which writes the headers it patches.
- `import_trainers.py`: copies the trainers the imported maps battle (their
  party, class, sprite, name, items and AI). FR/LG already has the Hoenn
  trainer classes and front pics under `RS_` names; only JUAN's sprite and
  the WINSTRATE class are added. Run it before `import_maps.py`, which turns
  the Emerald scripts into `trainerbattle_single` scripts for the ids it finds.

Hoenn trainer ids start at `HOENN_TRAINERS_START` (768), past the save's
trainer flag block. `battle_setup.c` keeps their defeated bits in
`gSaveBlock2Ptr->hoennTrainerFlags`, carved out of padding FR/LG never used,
so the save layout is unchanged.

Items: the item balls use flags from `gSaveBlock2Ptr->hoennFlags` (the range
`HOENN_FLAGS_START`, handled in `GetFlagAddr`), generated into
`include/constants/flags_hoenn.h`. Hidden items must be reachable as
`FLAG_HIDDEN_ITEMS_START + id`, so they take the flags right after FR/LG's own
hidden items; the id field in map data was widened from 8 to 14 bits (the item
field needs only 10), which is ROM data and leaves the save untouched.
- `import_heal_locations.py`: appends Emerald's heal locations and gives each
  imported Pokemon Center an OnTransition script that calls `setrespawn`. Run
  it after `import_maps.py`, which rewrites those scripts.

Metatile behaviors: Hoenn's bridges, Pacifidlog's logs and Fortree's walkways
carry their collision and elevation across, so their behaviors become plain
ground and the player walks over them as in Emerald. Emerald's bike terrain
(muddy and bumpy slopes, the Mauville rails), the SKY PILLAR's cracked floor
and the secret base spots also become plain ground: FR/LG has neither the
Mach and Acro bikes nor secret bases. `import_maps.py` prints what is left.

- `import_region_map.py`: converts Emerald's region map (8bpp tiles, one byte
  per tile) into FR/LG's format, writes the mapsec layout, the fly destinations
  and the "visited" flags, and gives each town a script that sets its flag.
  Run it after `import_maps.py`, which rewrites those scripts.
