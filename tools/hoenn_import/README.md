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
