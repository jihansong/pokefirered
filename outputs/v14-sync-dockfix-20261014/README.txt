Thunder Yellow v1.4 sync + verified Dewford dock fix
Created UTC: 2026-10-14T10:40:25.927072+00:00
Created Korea time: 2026-10-14T19:40:25.927072+09:00
ZIP display timestamps are explicitly written in Korea time; ZIP itself has no timezone field.

Use pokemonthyl_v1.4.gba with the included pokemonthyl_v1.4.sav.
Original saves/pokemonthyl_v1.4.sav and previous sync99f4100d are preserved.
The SAV c06ad053 reapplies physical PC sorting and opens BOX1 instead of BOX5.
It repairs the remaining damaged Lickitung in both banks using the unique plausible minimum-bit model.
All other Pokemon records match99f4. The deployed copy is saves/pokemonthyl_v1.4-synced-recovered.sav.
The GBA is newer (af267799...).
In DELTA, import the battery save and use the game's CONTINUE. An older Save State may replace these edits.

Confirmed: v1.4 native CONTINUE/SAVE/cold restart (counter78 to79), party/PC/dex/story preserved;
old stranded Dewford counter74 automatically resumes on land, actual boat roundtrip/new land arrival,
native SAVE/cold restart (counter74 to75), all original user saves unchanged.
The supplied SAV is the user's synced v1.4; no QA progression SAV is substituted.

Save edits: Master Ball/Rare Candy/TinyMushroom/PP UP 99; prior player-owned doubled IVs retained,
not doubled again. Dragonair evolved to Dragonite with its retained IVs. Healthy PC entries sorted
by National number and duplicate level. Authenticated Lapras restoration; healthy Togepi egg preserved.
Lickitung is reconstructed as Lv39/EXP59319 by reversing one primary bit plus engine Bad Egg markings.
Its original checksum30838, identity, IVs/EVs, moves, PP and capture data are preserved. No checksum masking.
There is no healthy same-identity donor, so this is an inferred reconstruction within a single-bit model,
not a donor-authenticated exact-original restoration. Multi-bit corruption/checksum collisions remain possible.
Both banks contain zero invalid PC Pokemon records after recovery; the healthy Togepi egg is preserved.
Bad Egg corruption's exact DELTA Save State cause is not proven without that State/matching ROM.

Regional UI and scroll evidence use the preserved pre-dock ROM0845. Current v1.4 is Kanto-unlocked;
no Johto/Hoenn story flags were forced. All three regions/full campaign/physical DELTA FPS remain unverified.
Brawly progression is not certified by the dock-only test. Previous actual QA battle loss is preserved.
Only the dock scripts and their importer mirrors changed in this GBA; existing art and save layout remain.
