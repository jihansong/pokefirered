Regional airport terminal candidate r3 — unapplied
================================================

This is a source candidate, not a built or emulator-verified update.
The root agent alone may apply it to the existing Codespace.

Concrete changes
----------------

- JohtoCherrygroveAirstrip expands 32x24 -> 44x24 eastward. Every original
  32-column cell is byte-identical; existing landing (22,12), NPCs, sign,
  city connection and region return scripts remain. New door: (37,10).
- JohtoAirportTerminal appends to group 76 at map 124. Its 33x10 layout is
  byte-identical to the current approved Kanto lounge, with the current return
  clerk script and separate information NPCs. Its two exits use the new door.
- HoennAirportExterior is a compact new 32x24 field, group 52 map 14, with the
  current approved Kanto facade and bound General/Vermilion tilesets.
  Door: (25,10); south gate: (22,23)/(23,23).
- HoennAirportTerminal appends to group 52 map 15 and clones the same approved
  lounge. Its clerk calls the existing Harbor return-flight script.
- Slateport Harbor gains two south exit mats, (2,14)/(3,14), leading to the
  exterior. Original four warp entries and four NPCs retain their exact IDs,
  coordinates, scripts and ordering. Existing flights still land at (12,13),
  so STERN's arrival story, ships, badges, museum and harbor are not bypassed.
- A narrowly limited canonical importer hook retains the two Harbor mats;
  its JSON mirror contains the complete six-warps list to preserve old IDs.
- The existing airport window foreground rule is extended to the two new
  terminals. People remain in front of glass, the plane stays behind it.
- Three layouts append as IDs 838/839/840. Existing map group and layout
  numbers, save fields, story flags, flight destination table and music remain.

Source evidence and static verification
--------------------------------------

Fresh snapshots: user-bugs-v145-fresh-20261015, -r3, -r4, all member SHA checked.
The parent verified current importer SHA:
50021b65d020d3d6ad40d858d04b0a53d5a5fdc4a53659b0616d67e3f12882bc.
All four source landscape binaries occur unchanged in current af267 ROM.
The Kanto building crop (31,5,8,8) is the current doubled-height facade,
not the obsolete short facade in the old cache.

The two new exteriors render with fresh bound tiles and have zero range errors.
Their doors, public approaches and old Johto exits pass collision flood checks.
The reused terminal has a continuous static path to the counters and window.
These checks do not prove actual collision elevation, warp timing or flight.

The first draft's copied Pallet pavement ID would have rendered as a cliff
with Vermilion's secondary set. It was caught visually and replaced with
the actual current Vermilion pedestrian ground at (8,9), raw 0x3115.

The canonical Harbor patch was run twice in an independent source fixture.
Only binary byte offsets 676 and 678 changed. Its generated JSON exactly
matches the candidate after host CRLF/LF normalization; the binary is exact.
Second import output is byte-identical. A changed upstream floor cell is
rejected before either layout cell is written.

Application boundary
--------------------

Use the separate apply_airport_candidate_guarded_r1.py tool with the exact
manifest SHA and a fresh current ROM SHA. It defaults to preflight only.
It checks all source hashes, all 26 allowed target paths, original SAV hashes
and current ROM before any product write; it backs up the ten existing files.
Route29 and Misty assets are not targets. Shared event_object_movement.c must
be rebased if an Elm registration change is applied first; the hash guard
will reject a stale copy. It never writes a ROM, ELF, SAV or Git state.

Do not rerun historical full region importers as an application step. These
candidate changes append existing group/layout arrays directly. Only the
narrow individual canonical Harbor patch reapplication was verified here;
historical full importers can reconstruct group tables and need a separate
compatibility review before use with existing saves.

Required native checks after canonical build
--------------------------------------------

1. From a copy of a natural Johto arrival SAVE, walk through original north
   and Route29 routes, enter (37,10), exit through both lounge mats, and
   confirm no door loop or coordinate drift. Check people at window rows2/3.
2. From a copy of a natural Harbor SAVE, use both new mats to reach (52,14),
   enter door (25,10) to (52,15), exit and return to the Harbor. Confirm the
   four original NPCs and original city/ship exits still work.
3. Use the real return desk and flight animation/menu in each new terminal;
   verify existing Kanto unlock conditions, original landing and no extra
   story rewards/flags. Do not inject warps, call scripts or force flags.
4. Save normally to new QA-only files, cold-load and re-enter each terminal.
   Compare party/PC checksums, species, IVs, PP, bag and regional dex progress;
   original user SAV files remain unchanged. Record fresh ROM/ELF and ABI.
5. Measure frame delivery in the same original and new map contexts. No
   performance result, native PASS or final release is claimed in this folder.

No broad bag/Mew/delivery/dock replay is required for this narrow candidate.
