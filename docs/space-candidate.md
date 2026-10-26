# Space interior candidate

This source candidate contains three decks and seventeen interiors, with
fourteen appended maps. Existing maps, layouts, save structures, opening,
title and credits music remain preserved inputs. Original game pixels and
palettes supply the private interior tilesets.

The public candidate selects the previously distributed R23 Pokemon logic.
Private save personalization remains a separate local workstream. No private
save, party identity, personal path or complete game ROM is an input to this
public verification workflow. The three original embedded multiboot source
payloads under data/ are exact path-and-Git-blob exceptions.

The current generic forty-choice relearner buffer and forty-one-slot UI remain
present. The private extra-twenty-move branch is inactive because the selected
Pokemon logic is exact public R23. Its generic UI impact remains a separate
regression check; no save field or layout is rearranged.

The source generator returns 137 asset outputs without writing them unless
explicitly requested. Source checks verify seventeen interiors, sixteen
reciprocal door pairs, private PC metatiles and foreground masks for the
player, Pikachu and Misty. Offline source models are separate from gameplay.

Use `tools/qa/verify_space_candidate.py` with explicit `--source`,
`--artifact-dir`, `--out` and `--reference-manifest` paths. `--source-only`
performs no compiled checks. A compiled result requires the exact Linux
provenance bundle, candidate ELF/ROM/MAP/SYM, target ABI probe and candidate
object files. No prior Windows objects or missing preparation files are used.

Keep the native raw inputs listed in the producer allow-manifest, including
files normally ignored by Git. Build in a fresh isolated checkout without
`make clean`. The ROM-only build must not install or run mGBA or its wrappers.
The prepared public snapshot is an update allowlist, not a deletion list.

`tools/qa/produce_space_build.py --source . --reference-manifest
tools/qa/space_reference_manifest.json --out /tmp/space-build-bundle` is the
Linux producer entry point. It records actual source hashes before and after,
candidate objects, target ABI facts, output hashes and complete command logs.
Workflow, transport, synthetic fixture and host helpers have separate pins
outside the source-input mapping. Privacy checks cover this sparse mapping,
with no claim about unrelated existing repository files or history.

Actual room walkthroughs, NPC and follower placement, facilities, mission
branches, battles, Jirachi, reward retries and normal SAVE followed by a new
process Continue remain separately recorded runtime gates.
