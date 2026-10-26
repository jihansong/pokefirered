# Linux Delta-core runner and synthetic TY28 fixtures

This directory contains source and public recipes. It contains no game ROM,
existing save, save state, Windows executable, private trainer information or
personal path. Building the host does not execute a game. Compiling the schema
does not execute ARM code. A constructed fixture is not a boot verification.

## Official core and clean Linux build

The official Delta `.gitmodules` points to `rileytestut/GBADeltaCore`; that
repository's [`.gitmodules`](https://github.com/rileytestut/GBADeltaCore/blob/master/.gitmodules)
identifies `https://github.com/visualboyadvance-m/visualboyadvance-m.git`.
Use commit `453fa0decf179360926fb417725a794aa496d6e3`. The build refuses a different
commit, modified core source, a non-Linux compiler or a non-x86_64 Linux host.

```sh
git clone https://github.com/visualboyadvance-m/visualboyadvance-m.git core
git -C core checkout --detach 453fa0decf179360926fb417725a794aa496d6e3
install -d -m 700 "$RUNNER_TEMP/ty28-runtime"
python3 tools/qa/build_delta_host.py --source "$PWD/core" \
  --artifact-dir "$RUNNER_TEMP/ty28-runtime" --output delta-core-host
```

Dependencies: native `g++`, zlib development headers/library, Python 3 and the
project's GBA ARM GCC for schema export. The host build has 30 unchanged core/APU
translation units plus one host, matching the reviewed host07 receipt's actual
31-unit list. CPU, BIOS, DMA, GPU, APU and linker definitions remain unchanged.
The host gives the video buffer `4 * 241 * 162` bytes, matching the pinned file
loader capacity before any frame. It does not alter guest memory or renderer code.

## Source-bound GBA ABI and fixture creation

Build the candidate game/source first so generated map/layout headers exist.

```sh
python3 tools/qa/derive_schema.py --source "$CANDIDATE_SOURCE" \
  --artifact-dir "$RUNNER_TEMP/ty28-runtime" --output ty28-schema.json \
  --arm-cc "$DEVKITARM/bin/arm-none-eabi-gcc"
python3 tools/qa/make_ty28_fixture.py --source "$CANDIDATE_SOURCE" \
  --schema "$RUNNER_TEMP/ty28-runtime/ty28-schema.json" \
  --recipe tools/qa/space-terminal-start.json \
  --artifact-dir "$RUNNER_TEMP/ty28-runtime" --output terminal-fixture.sav
```

The schema compiler reads the supplied game's real headers and source tables.
It writes ARM ELF32 constants for `sizeof`, `offsetof`, save/sector/PC/bag IDs,
and field masks from initialized bitfield probes. Python reads that object.
It exports PlayerAvatar/ObjectEvent/Main layouts for a controller using fresh
symbols, including ObjectEvent active/elevation/facing masks and `MAP_OFFSET`.
Species stats, experience, natures, move PP, item pockets, all 24 PKM substructure
permutations, national-dex mapping and text glyphs come from the supplied source.
Source hashes bind the schema; a stale source is rejected before serialization.

The fixture writer starts SaveBlock1, SaveBlock2, both 14-box structures and every
PKM from new zero buffers. It creates 23 TY28 payload sectors and the committed
generation record at the source-defined commit sector, with native folded
word checksums and aggregate sum. The remaining flash starts erased. It does not
reuse a legacy 14-sector writer or read an input save. PKM80/PKM100 checksums,
PID/OT encryption, PC28 mapping and bag quantity/header encryption are explicit.
The pure validator checks all 23 sectors, commit, every party/PC PKM and bag key;
an altered payload byte must be rejected before the fixture is written.

`CI_TEST` is the public fixture identity. The source has no underscore glyph, so
the in-game trainer is `CI TEST`. Trainer ID, encryption key and PIDs are newly
chosen public recipe constants. `parents` is empty and `save_inputs_read` is zero.
The sidecar records recipe/schema/source hashes and the output hash. It does not
claim that a normal SAVE or cold Continue has run.

Recipes accept a source `MAP_*` token and local x/y, party/moves/IVs/EVs, named
flags/variables, items, and PC current box/explicit mons or `fill_all` state.
All changes are preboot synthetic setup. `continue_warp:true` sets the source's
normal Continue-warp flag so an initially empty object/cache state is rebuilt by
the normal map loader; the game clears that flag during Continue.

`space-terminal-start.json` starts at terminal [8,7], center secured, mission
phase 0, other space progress clear, six public strong Pokémon and Master Balls.
`space-cabin-tour.json` is a separate preboot tour with phase 2/enrolled/intrusion
started explicitly set. Its state does not demonstrate mission completion.

## Host protocol and new battery output

The artifact directory must already exist, have mode 0700 and belong to the
caller. Inputs must be regular absolute paths without caller-controlled symlinks
or parent components. Output names are new basenames inside that directory.

```sh
"$RUNNER_TEMP/ty28-runtime/delta-core-host" \
  --rom "$CANDIDATE_ROM" --seed "$RUNNER_TEMP/ty28-runtime/terminal-fixture.sav" \
  --artifact-dir "$RUNNER_TEMP/ty28-runtime" --output after-normal-save-unique.sav
```

Alternatively, `--blank-flash` replaces `--seed` for a new game from erased flash.
The pinned core initializes that flash. The host does not inject new-game state.

- `step KEYMASK FRAMES`: normal joypad input; at most 12000 frames. Check the JSON
  `complete/requested/actual` fields. A timeout or partial step is not a pass.
- `read ADDRESS_HEX LENGTH_HEX`: at most 4096 read-only bytes in mapped hardware
  regions. The controller resolves game state from the candidate's fresh SYM.
- `ppm unique-name.ppm`: exclusively creates a new 240×160 PPM in the artifact directory.
- `status`: frame/CPU/IRQ/DMA/key information only; no fixed game-RAM meanings.
- Optional `--video-fd N` accepts only an inherited dedicated O_WRONLY pipe/FIFO.
  `video on` / `video off` toggle RGB24 capture of each real rendered 240×160 frame.
  `video finish` permanently stops capture and closes the inherited pipe; later
  `video on` is rejected. The controller can close its writer and await ffmpeg
  completion while normal game input/SAVE continues in the same host process.
  The controller can pipe those frames into ffmpeg at 60 fps and omit boot/title
  capture. The host opens no video filesystem path. `video_frames` counts complete
  frame writes; broken pipes, partial-write failure and SIGPIPE become
  `video_error:true` and an incomplete step. A controller must reject that result.
- `battery normal-save-complete`: the controller calls this only after observing
  normal in-game SAVE completion. It exports once to the startup `--output` name.
- `quit`: releases keys and exits without an automatic battery write.

There is no write-memory, script, warp, save-state, cheat or reset command. Startup
uses the core's normal power-on reset. Battery export atomically reserves a new
inode with `openat(O_EXCL|O_NOFOLLOW)`, then calls official `CPUWriteBatteryFile`
through the host-owned Linux descriptor. This internal descriptor is independent
of caller paths. Existing files, the input seed and external paths cannot be
selected as output. EOF/errors/quit never flush a battery automatically.

For cold Continue, terminate the first process and start a fresh host with the
new battery as `--seed` and a different new output basename. The controller must
validate the TY28 file and observe Continue/field state; process startup alone
does not establish a successful reload. No tool here uploads any artifact. The
caller controls encryption, retention and presentation of build/runtime results.
