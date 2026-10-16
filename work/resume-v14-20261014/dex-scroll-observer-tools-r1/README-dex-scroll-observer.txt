Actual-key readonly numerical Pokédex observer, r1

Only Python compilation has been checked locally. Compiler ABI and native
gameplay results must be collected by the parent in Codespaces.
No product code, original SAV, game RAM or save-state restoration is modified.

Transfer the bundle into this fresh tools folder:
/workspaces/pokefirered/work/resume-v14-20261014/dex-scroll-observer-tools-r1

1. Derive and authenticate UI offsets, bitfields and local ELF symbols:
python3 /workspaces/pokefirered/work/resume-v14-20261014/dex-scroll-observer-tools-r1/prepare_dex_ui_probe.py --root /workspaces/pokefirered --rom /workspaces/pokefirered/work/hoenn-resume-20261014/fixed-profile-rom/pokemonthyl.gba --elf /workspaces/pokefirered/work/hoenn-resume-20261014/fixed-profile-rom/pokemonthyl.elf --out /workspaces/pokefirered/work/resume-v14-20261014/dex-ui-probe-r1 --source-manifest /workspaces/pokefirered/work/resume-v14-20261014/dex-scroll-observer-tools-r1/dex-ui-source-manifest.json

2. Verify the actual deployed synced candidate path first. The following is
the intended delivery filename; replace --sav with its existing verified path
if root has deployed the same bytes under another name. Do not use v1.4 source
32f4.. or an older v1.25 file for this specific guard.
python3 /workspaces/pokefirered/work/resume-v14-20261014/dex-scroll-observer-tools-r1/native_dex_scroll_observer.py --root /workspaces/pokefirered --rom /workspaces/pokefirered/work/hoenn-resume-20261014/fixed-profile-rom/pokemonthyl.gba --sav /workspaces/pokefirered/outputs/resume-v14-sync-20261014/pokemonthyl_v1.4-synced.sav --abi-json /workspaces/pokefirered/work/resume-v14-20261014/dex-ui-probe-r1/dex-ui-abi.json --out /workspaces/pokefirered/work/resume-v14-20261014/dex-scroll-observe-r1 --expect-sav-sha 99f4100d09961196706282a02e96ee9017a0a591777aa3ca0b40249ec8ae89e8

Both --out folders must be absent. Immutable ROM0845 and ELFe625 are mandatory.
The in-progress Dock rebuild is a separate controlled-comparison input and
must not be substituted into this run.

Outputs: compiler-derived dex-ui-abi.json; actual numerical-list screenshots;
cold-down/reverse-up/warm-down 361 raw snapshots each; validation.json.
ReadKeys heartbeat anomalies are diagnostic candidates, not task invocation
counts or physical DELTA-device FPS. Rendering and cursor movement are actual
UI observations. Opening the regional list follows user input only.

Original party, PC, flags, vars, Hoenn data and all four Dex bit arrays are
verified before/after scrolling. Original SAV files and input ROM hashes are
verified unchanged. This does not certify full campaign completion.
Unresolved Lickitung corruption remains preserved; there is no authenticated
normal donor among the 18 SAV files. No speculative repair is made.
