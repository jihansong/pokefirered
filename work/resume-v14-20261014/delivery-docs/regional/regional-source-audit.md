# Regional Pokédex and inter-region story audit, 2026-10-14

Scope: independent review of `current-Dewford-runtime`, followed by the freshly exported `current-inputs/export-manifest.json` snapshot tied to ROM `0845f8cbc1afa5d957a64f76a4ae2700606175dd55bcd101184e6ba2a650b7fa` and ELF `e625069ea9379ea3dc2f83e3014fb741a2e0b7383f41f6d56bc37fc0eae6f17b`. All twelve source/header inputs required by the runner now match that export manifest. This does not assert a fresh-play campaign pass, ROM attachment, battery-save round trip, or DELTA performance result.

The five Pokédex snapshot members below match their download manifest byte-for-byte:

| Source | SHA256 |
| --- | --- |
| `src/pokedex.c` | `aac08b88d35a69cab82df72d6f759cf3d7f4c1620935657f5450ed7f197ba3e4` |
| `src/pokedex_screen.c` | `d7cd34bed4bdee8a2e76950636a093f726eb79268b2aed6b96bf31139c1ea4c7` |
| `src/pokedex_area_markers.c` | `af38f08aec2f388b6833d69c49ab10248dee3da4c17a33b7ae9fa27e97110aca` |
| `include/pokedex.h` | `a7ea835c8327b5f17c5a766090829e49e694e5439b796634d1e1746867b29e8a` |
| `include/pokedex_screen.h` | `62151ddb84111da7ae854403335fe7f2ddc7dce45e947a445713f6d70447d9d4` |

## What is actually present

- `src/pokedex.c:8`: `GetStoryRegionalDex()` reads four existing flags. Birch rescue or Stern meeting selects Hoenn; otherwise Johto arrival briefing or laboratory assistant meeting selects Johto; otherwise Kanto. It writes no flags and adds no save fields. With both regions unlocked, Hoenn stays the default even on an earlier-region revisit. That is the existing highest-unlocked-region policy, not proof of a current-map policy.
- `src/pokedex.c:18`: regional count and both number conversion functions exist. Kanto is identity; Johto uses its own order table; Hoenn uses the existing Hoenn-to-national table.
- `src/pokedex_screen.c:899`: JOHTO/HOENN menu labels and 151/251/202 region titles exist.
- `src/pokedex_screen.c:920`: opening the screen creates a national-to-regional cache. It uses only the active region mapping and is bounded by `NATIONAL_DEX_COUNT`.
- `src/pokedex_screen.c:1071`, `:1296`: returning from the national list re-enters top-menu state 0, which resets `showNationalNumbers` to false. Characteristic searches and categories then use regional filtering.
- `src/pokedex_screen.c:1466`, `:1552`: regional numerical listing and the separate national listing use different orders, while list entries retain internal species identifiers.
- `src/pokedex_screen.c:1571`: an empty regional search supplies one non-selectable `SPECIES_NONE` placeholder row.
- `src/pokedex_screen.c:2311`: number rendering switches between cached regional numbers and national numbers without mutating species.
- `src/pokedex_screen.c:2318`, `:2387`: seen/caught flags remain indexed by national number, including the three original seen mirrors; regional counts read those existing bits through the order mapping.
- `src/pokedex_screen.c:3681`: registration records national seen/caught bits, opens the active regional view for regional catches, and uses national numbers for an unlocked off-region catch.

No product patch is justified by these facts alone. In particular, this snapshot does not support the claim that regional Pokédex source implementation is absent. Runtime proof is still required.

## Concrete unverified contracts

1. The current Johto order table, current Hoenn/species conversion tables, and constants have now been fetched and hash-guarded. Compilation and execution of the generated C remain required before claiming the full mapping/list/number test passed. Older `work/pokefirered` tables were read only to identify dependencies and are not accepted as current results.
2. Fresh `data/maps/KantoAirport/scripts.inc:86` and `:109` gate Hoenn and Johto independently with only `FLAG_SYS_GAME_CLEAR`. Neither clerk checks a Johto league flag. Thus a Kanto champion can visit Hoenn first, and the highest-unlocked-region policy will then keep Hoenn as the default even on the later first Johto visit. This is a concrete missing gate for a strictly linear Kanto→Johto→Hoenn campaign. The current Harbor first-arrival script provides an optional Johto referral, not an enforced order. A future strict-order patch must preserve access for existing Hoenn saves, by retaining a legacy-return path for established Hoenn story flags.
3. Native before/after Johto and Hoenn unlock, regional menu text, numerical list, detail pages, national-list return, empty listing, newly caught off-region registration, and SAVE/cold Continue must be checked in the final ROM. Source or host-unit passes are insufficient for those claims.
4. The highest-unlocked-region default currently persists when revisiting Kanto/Johto after Hoenn. This matches the previously accepted default policy but there is no manual selector for previous regional lists in the inspected menu. Adding such a selector would be a separate UX choice, not a save-compatibility requirement.
5. The region-map marker and encounter sources must be tied to the same final ROM for full map/encounter QA. This review does not repeat previously successful Route29 time-band checks or the completed Devon shipment checks.
6. Fresh `data/maps/NewBarkTown_ElmsLab/scripts.inc:4` has a comment calling the separate Silver story pending, and `:83` comments on a temporary research sprite for Elm. These comments may be historical. They are not sufficient proof of current missing work: fresh Johto constants contain Silver Azalea/Burned Tower/League, Radio Tower, and League/Lance progress flags. Elm's actual interaction at `:89` sets the lab-visit flag, and his follow-up records the delivered Mr. Pokémon report. Fresh Birch interaction at `:98` optionally calls the Johto-referral dialogue. These verified hooks do not establish a complete rival or multi-region campaign. The related actual map scripts, assets, and continuous native events must determine present completion.
7. The follow-up fresh `metadata-preflight` snapshot resolves the actual arrival names: `JohtoCherrygroveAirstrip` and `SlateportCity_Harbor`. The guessed `JohtoAirport`/`HoennAirport` paths must not be cited as actual current sources. `data/scripts/game_clock.inc:90` is the common `EventScript_TakeAirplane` definition.

## Current arrival and travel source facts

- `JohtoCherrygroveAirstrip/scripts.inc:34`: first arrival uses `VAR_TEMP_0` to avoid repeated on-frame work. If already briefed, it ends; if the older lab-visit flag is already set, it records arrival without repeating introductory dialogue. Otherwise it welcomes the player and sets the arrival flag. This is an actual legacy accommodation for existing Elm-visit saves.
- `NewBarkTown_ElmsLab/scripts.inc:8` and `:89`: assistant and professor conversations both mark the existing lab visit. Starter receipt uses separate gift flags.
- `Route101/scripts.inc:80`: Birch rescue is recorded before the wild battle, by design; even a loss leaves Birch waiting in the lab. It also sets scene progress 1 and the hide/show flags. A native loss must therefore be checked against that intended branch, not treated as a rescue-flag corruption.
- `SlateportCity_Harbor/scripts.inc:65`: first Stern arrival welcome sets the Hoenn flag after its dialogue, then stage/scene progress advances without lowering old progress.
- `src/airplane_flight.c:58`: actual destinations are Kanto airport `(12,7)`, Slateport Harbor `(12,13)`, and Johto Cherrygrove Airstrip `(22,12)`.
- `src/airplane_flight.c:300`: out-of-range destination values are bounded to Kanto destination 0 before dereferencing. Exit performs normal `SetWarpDestination`/`WarpIntoMap`/`CB2_LoadMap`, releases scene buffers, and re-enables help.
- `data/scripts/game_clock.inc:90`: common travel stops quest-log replay, fades the field, runs the native flight special, waits for it, and ends. This is not an external MP4 loader.

## Prepared linear-campaign candidate, not applied

`prepare_hoenn_linear_gate_candidate.py` uses the exact current KantoAirport SHA to create a candidate diff under `linear-gate-candidate/`. It requires the existing Johto league-clear flag for a new Hoenn journey, while retaining current Hoenn-return eligibility for established Stern/Birch, any of eight Hoenn badges, or existing stage/Birch/Devon progress. It preserves the original Kanto champion condition and the existing Misty post-champion bridge call even for a denied new flight. It adds no save fields or flags.

The actual candidate script branches have passed 56 combinations of champion state, Johto league state, and independent legacy evidence. The candidate is not assembled, native tested, or applied to product. Actual v1.4 and older Hoenn input evidence must be checked before promotion; a save with another unrecognized form of Hoenn progress must not be blocked merely because two newer arrival flags are unset. No proof of such a save mismatch has been observed in this audit.

## Executable next artifact

`regional_dex_host_audit.py` compiles the actual current C bodies, conversion tables, listing tables, and number-render branch with a small host adapter. It requires a current-source SHA256 manifest, rejects missing/mismatched dependencies, uses ASan/UBSan, and records scope limitations in `validation.json`. It changes neither product source nor a user battery save.

Expected successful coverage is 16 unlock masks, 604 regional mapping/inverse cases, 54 empty/all/sparse listing fixtures, 6,948 internal-species-to-displayed-number cases, and unchanged seen/caught mirrors throughout read-only UI operations. It has passed Python syntax, actual-definition extraction, all twelve current-source hash guards, story flag uniqueness checks, and actual C generation. Generated C SHA256 is `1ddb302a90efb6527e2f7ce10082379fe0b99061f4130c6670ff85628237f834`. Compilation/execution is being performed in the remote Linux host; the local computer has no C compiler available in PATH.

The actual four flag identifiers are Birch rescue `4662`, Stern meeting `4616`, Johto arrival `5376`, and Elm/lab visit `5377`. The runner derives them from current macro definitions instead of supplying invented flag IDs.

Example from the actual remote repository after creating a trusted source snapshot manifest:

```text
python3 regional_dex_host_audit.py --repo /workspaces/pokefirered --guard-manifest /path/to/current-source-sha256.json --out /tmp/regional-dex-source-unit
```

The runner deliberately reports `native_emulator_pass=false`, `rom_attachment_verified=false`, `full_story_playthrough=false`, and `battery_save_tested=false` even when its source-unit checks pass.
