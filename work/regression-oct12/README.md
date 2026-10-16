# Thunder Yellow regression repair, 2026-10-12

Current main ROM: SHA256 2bafd6478fef5bbda56c6b4bec9c8dec1a4e0f060252fc219dbcc834411509f7, 32 MiB, BPGE.
Main GBA/ELF/SYM/MAP replaced from an exact frozen, verified four-file candidate. Previous Q8 four-file bundle and status snapshot preserved in the release rollback folder. See promotion-receipt.json for exact paths.

## Verified repairs

- Confirmed actual main Q8 lacked MistyJoin and MistyCompanion_Update despite Q9 source having been prepared. New main includes the invitation/update code.
- Misty: Update precedes Prepare on map load; queued invitations wait for original Oak scenes; pending invitation survives the native Oak/national-dex laboratory sequence and actual exit. A new independent decline flag (0x228, unused across scanned sources and zero in all 14 originals) prevents repeated prompts and manual acceptance clears it. Both KantoAirport clerks offer the return-only invitation before their normal flight prompt.
- Professor Elm previously had no named NPC; the original scientist was explicitly an assistant. Added a second named professor with introduction, report and completed-report branches, using existing story flags and original assistant/gift behavior. Report completion takes precedence for legacy flag combinations. Professor still uses a temporary Scientist sprite; a dedicated Elm portrait/overworld sprite is unfinished.
- Confirmed MtMortar_1F declared Building+RockTunnel while its donor uses General+RockTunnel. Fixed both canonical builder tuple and actual layout primary reference without executing the map generators.
- Fixed mixed indentation in the Johto entry generator guard; AST parsing succeeds and the guard protecting all 124 expanded maps remains. No map generator was run.

## Executed native QA on this exact candidate

All runtime tests prohibit game RAM writes/direct story dispatch. Temporary preboot eligibility/position fixtures are documented and are never delivered as player saves. Actual Champion battle was not replayed.

- Actual KantoAirport clerk A / flight ticket / airplane / airport arrival followed by continuous walking across Route29 and NewBarkTown and an actual ElmLab doorway warp and professor A dialogue: PASS. Visually inspected native contact sheet; first four areas are clean.
- Elm actual NPC four dialogue cases: PASS, including completed report without briefing flag.
- Misty airport four cases: PASS, invitation YES/NO, both destinations, received-starter-follower flag disabled case; actual menu SAVE, 14 sector checksums, cold CONTINUE and visible following. Original full party/PC/Dex preserved.
- Misty Pallet two cases: PASS, Oak scene completion and natural national-dex laboratory return; NO persistence and manual YES, actual menu SAVE/cold CONTINUE and native following.
- Eight independent cold map visual fixtures: PASS, including native MtMortar and its RockTunnel donor. MtMortar actual ROM primary/secondary pointer pair verified.
- Native cold nurse regression four cases: PASS using exact previously executed campaign-chain SAVE115 (QA-only input), two/six legal partners, Johto League/Kanto/Hoenn. Healing, full PC/Dex/normal and regional story state, menu SAVE and cold reload verified. Not a replacement user save.
- Native land->Surf->Waterfall->land->Tohjo north exit->Route26 and SAVE/cold: PASS.
- Approved resident title/opening/Rocket/voice assets 24/24 exactly preserved; all ROM-resident ELF sections match; existing SaveBlock1 15720, SaveBlock2 3876, PC storage 33744 bytes and 14-sector ABI unchanged.
- Existing six reference saves plus user v1.1/v1.2: eight IDENTICAL load comparisons PASS. All 14 original/backup saves remain byte-for-byte unchanged.
- Map integrity, touched text width/audit, 386-entry dex check PASS. Map-integrity warnings retained. Global event-wiring checker still fails with 96 preexisting findings; log is exactly identical to the prior candidate, so it is not recorded as passing. Touched KantoAirport has one preexisting unused text label.
- Source-only 124 Johto layout/coordinate/generator pairing audit: no errors, parse errors or warnings. Corrected the collector to honor literal unconditional subscript overrides; the former Ecruteak warning was a tool false positive, not a map change.

## Limits and retained failures

The player's reported entire airport/town/lab tile corruption has not been reproduced in main Q8 cold/actual flight or the new candidate. Exact DELTA ROM and startup method remain unconfirmed. Do not describe it as a resolved cause, or blame Save State without evidence. Actual DELTA device performance and old-ROM Save State compatibility are unverified.

Whole Johto/Hoenn campaign, N/space expansion, NPC allied battle and preexisting Bad Egg recovery remain incomplete. Original Bad Egg record is preserved rather than guessed or silently checksum-repaired. The scoped repair is not full-campaign completion.

Early attempts are retained: numeric Elm local_id build failure fixed with a symbolic local ID; walking QA first 8-frame input consumed facing only, corrected to release on observed position change; Pallet test paths crossed a fence, changed only QA walking paths; two additional QA invocations lacked required arguments/input fixture, then rerun using the verified original interface/input. No production workaround or preservation assertion weakening was used.

The deliverable ZIP contains only ROM, readme and provenance. It contains no player SAV. Keep original .sav and Save States; game CONTINUE from the battery save matches the verified startup path.

Approved title v8, Rocket v11 and full-FRLG-music opening were preserved; no art/voice/redraw approval step was reopened.

## Cross-ROM raw state investigation

The old Q8 raw mGBA core state is accepted by the current ROM but reboots to copyright/intro within60frames. Two same-ROM controls retain native field execution, party, PC and Dex at0/60/240frames. The corrected full33744-byte storage comparison is unchanged atzero; after reboot the prior RAM body is cleared/changed and storage pointer is0, so it is not interpreted as newly corrupted Pokemon. All original SAVs and the deployed ROM are unchanged. Actual DELTA frontend SaveState was not supplied; neither the reported initial tile corruption nor original BadEgg cause is established. See state-compatibility-audit.json. Original offset/length diagnostic mistakes are retained and explicitly excluded.

## Early research progression followup

Promoted b46fb32bb67f89d5a48dfbfdf41ddd4977cc4a2d60dbbe6c72e1bc0281c5606d after native Professor/Guide/Visitor 5-case verification, text checks, 24 approved assets/SaveABI preservation and both user SAV identical loads. Professor visit marks the existing research-team flag; Cyndaquil receipt stays separate. Sprout1F Visitor now follows the Elm report state. Exact old four files are backed up in /workspaces/pokefirered/outputs/rom-johto-research-followup-20261012T111059Z/rollback-oct12-first-repair. Full regional campaign remains unfinished. Earlier wrong assistant NPC fixture position is retained as a failed QA attempt; actual map position5,5 was used for the corrected test. No production workaround or original SAV edit.

## Remaining story and reward work

The semantic event audit preserves warnings for actual player rewards, removes three NPC-report false positives and exposes two previously masked promises. Route114 TM05 receipt is not implemented; Sootopolis House6 decoration script commands currently do no storage work, so macro/file presence is not delivery evidence. These rewards are excluded from the promoted scope. Next region segment: Route32, Union Cave, Azalea/Kurt/Slowpoke Well/Bugsy, checking prior completion records first. Full regional campaign, N/space story and allied battle remain unfinished.
