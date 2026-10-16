# Thunder Yellow - Codex project instructions

This is a Pokemon LeafGreen ROM hack based on pret/pokefirered.
Use the existing Codespaces environment and answer the user in Korean.

## Start every development task
- Check `git status --short --branch` and recent commits before editing.
- Preserve the current branch, uncommitted changes, saves, and reference assets.
- Read `docs/team/log.md` for team decisions and the applicable stage plan in `docs/`.
- Read `docs/INSTALL.md` for environment, build, and QA procedures.
- Read the relevant role guidelines in `.claude/agents/`; for code changes, read
  `engineer.md` and `qa.md`. These files remain the shared project references.
- Match recorded decisions against the current code and commits: old pending lists
  may be stale. Do not start unrelated backlog work without a user request.
- Follow the user's current instructions when they supersede older project decisions.

## Preserve game compatibility
- Do not add or reorder fields in SaveBlock1, SaveBlock2, or PokemonStorage.
- Use the documented free flag/variable ranges and respect reserved ranges.
- Append new maps to their groups and new layouts to layouts.json.
- For generated Hoenn map scripts/text, edit `tools/hoenn_import/patches/`
  and use its patch workflow; do not edit only generated data/maps files.

## Verification and handoff
- For game code changes, follow the engineer/QA rules and `docs/INSTALL.md`:
  warning-free `make leafgreen -j$(nproc)`, `make GAME_VERSION=LEAFGREEN syms`,
  save compatibility checks, and the QA cases relevant to the changes.
- Report checks actually run, exact outcomes, and anything unverified.
- Keep existing art/music review and user-approval decisions from the team log.
- Do not push or publish releases without the user's explicit authorization.
- Do not claim that Claude chats or its agent registrations were imported.
