This is an input-only native GBA check, not a repair or a DELTA Save State claim.

Inputs are locked to current ROM af267799... / ELF 2549852a... / actual v1.45
save 0949ebf0.... Existing saves and product inputs must remain unchanged.
The emulator makes its own disposable battery clone. Escape Rope consumption
and walking are permitted only in that clone. Never deliver its incidental
location/item changes as the user's requested synchronized save.

1. Prepare the PC/Summary private ABI from current source and the current
   source collection manifest (file paths must be repository relative).

python3 outputs/v145-native-PC-tools-r1/prepare_v145_PC_summary_abi_r1.py \
 --root /workspaces/pokefirered --rom pokemonthyl.gba --elf pokemonthyl.elf \
 --guard-manifest CURRENT_SOURCE_MANIFEST.json \
 --elf-helper outputs/v145-native-PC-tools-r1/prepare_regional_native_abi_r2.py \
 --out /workspaces/pokefirered/work/v145-PC-abi-r1

2. Start the persistent emulator in the background with hidden/noninteractive
   terminal output redirected to work/v145-PC-observer.log. The --out path
   must be new. The command queue file may initially be absent or empty.

python3 outputs/v145-native-PC-tools-r1/native_v145_PC_input_observer_r1.py \
 --root /workspaces/pokefirered --rom pokemonthyl.gba --elf pokemonthyl.elf \
 --sav saves/pokemonthyl_v1.45.sav \
 --out /workspaces/pokefirered/work/v145-PC-observer-r1 \
 --abi-json work/hoenn-resume-20261014/dock-fix-rebound-abi-r1.json \
 --ui-abi work/v145-PC-abi-r1/PC-summary-abi.json \
 --base-helper outputs/v145-native-PC-tools-r1/native_v14_save_cold_r3.py \
 --commands /workspaces/pokefirered/work/v145-PC-commands-r1.jsonl

3. Send normal input actions by appending JSON lines to the commands file.
   Example actions:
   {"op":"press","key":"START","after":90}
   {"op":"press","key":"DOWN","after":30}
   {"op":"press","key":"A","after":180}
   {"op":"run","frames":120}
   {"op":"observe"}
   Each action records a 4x screenshot, actual tasks/callback, location,
   menu cursor, PC cursor/box/menu IDs when relevant, and original Lapras80.
   The validation.json and last observation show current UI status.

4. Real starting location is RocketWarehouse (map group1 number114), x14 y11.
   Do not blindly press A/right: an adjacent Rocket grunt is at15,11.
   Use the normal Bag/Escape Rope UI (ITEM_ESCAPE_ROPE is compiler-derived).
   Then walk normally from FiveIsland_Meadow through FiveIsland to its Center.
   Go to the actual PC, choose Pokemon PC, then MOVE POKEMON (compiler-derived
   OPTION_MOVE_MONS), since party6 prevents WITHDRAW. Do not pick up/move,
   release/deposit/withdraw any Pokemon. The observer halts if a mon is in hand.

5. After entering normal MOVE POKEMON with the cursor in the box grid, append
   {"op":"open-Lapras-summary"} to let the observer reach BOX3 cell11 and choose
   SUMMARY using only normal keys and observed cursor/menu IDs. It refuses
   multi-move or a Pokemon in hand. Manual navigation is also supported:
   Open BOX3 cell11 (zero-based box2/cell10), Lapras PID2245990591 OT2839214970.
   In the selected-mon menu choose compiler-derived MENU_TEXT_SUMMARY, not
   MOVE/RELEASE. While actual Lapras Summary is visible, append:
   {"op":"summary-check"}
   This reads Summary's isBadEgg/isEgg fields filled by the actual C getters
   and verifies the displayed Pokemon identity. It does not call C directly.

6. Exit Summary/PC normally until the player is free in the Center. Append:
   {"op":"save-cold-check"}
   This uses normal game SAVE, expects84->85, closes/reopens the emulator,
   continues from battery and compares all PC records and relevant save data.
   Append {"op":"stop"} after completion. pass_all requires both actual
   Summary and native SAVE/cold checks; partial navigation never counts as pass.

Limit: Native mGBA reproduction cannot prove what the actual DELTA State
contains. The user's observed Bad Egg after in-game Save must be reconciled
with actual v1.45 battery bytes, which independently contain healthy Lapras.
