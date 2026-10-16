# Winona reward bridge — implementation awaiting runtime QA

The imported gym previously recorded a trainer victory but never awarded the
FEATHER BADGE or TM40. The victory callback and post-victory conversation now
share one recovery path. TM40 is committed only after AddBagItem succeeds;
a full stack leaves its receipt flag clear, and revisiting retries the gift.
Owning a TM40 from another source does not consume this reward.

Changed: canonical gym script/text, generated script/text, one existing-array
flag bit at HOENN_STORY_FLAGS_START+100, and fourteen event cases.
Unchanged: save structures/offsets, map/object/trainer IDs, maps and tiles,
trainer parties/levels, other gym badges, global bag code, user save files.
This is a reward fix; it does not complete Hoenn Z5 or its league.

Checks performed by apply script: source SHA guards, flag allocation guards,
canonical regeneration twice, duplicate labels, map unchanged, concurrent
source guards and exact before-file backup.

Runtime status: NOT RUN. Build/syms and these commands are still required:
- python3 tools/qa/eventcheck.py tools/qa/cases/z5_winona.jsonl --shots docs/team/qa/codex-z5-winona-20261004/shots
- python3 tools/qa/eventcheck.py tools/qa/cases/z4_flannery.jsonl
- python3 tools/qa/eventcheck.py tools/qa/cases/z3_roxanne.jsonl
- python3 tools/qa/textwidth.py tools/hoenn_import/patches/FortreeCity_Gym.text.inc
- Existing save-compatibility and map-smoke checks.

The fourteen cases cover a new victory, a pre-Z5 victory, another TM40 source,
full-stack failure, retry after space is made, duplicate/used rewards, badge
recovery, no repeated badge text, before-victory and loss paths, unrelated
badges, and two negative controls. They work on copies of saves/hoenn.sav.
Save/reload persistence and a real Delta device check remain separate runtime
checks; no local/in-memory preparation is reported as those checks passing.
