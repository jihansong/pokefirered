#include "global.h"
#include "gflib.h"
#include "main.h"
#include "task.h"
#include "party_menu.h"
#include "pokemon.h"
#include "battle.h"
#include "palette.h"
struct PartyMenuInternal {
    TaskFunc task;
    MainCallback exitCallback;
    u32 chooseMultiple:1;
    u32 lastSelectedSlot:3;  // Used to return to same slot when going left/right bewtween columns
    u32 spriteIdConfirmPokeball:7;
    u32 spriteIdCancelPokeball:7;
    u32 messageId:14;
    u8 windowId[3];
    u8 actions[8];
    u8 numActions;
    u16 palBuffer[BG_PLTT_SIZE / sizeof(u16)];
    s16 data[16];

};
struct Menu {
    u8 left;
    u8 top;
    s8 cursorPos;
    s8 minCursorPos;
    s8 maxCursorPos;
    u8 windowId;
    u8 fontId;
    u8 optionWidth;
    u8 optionHeight;
    u8 columns;
    u8 rows;
    bool8 APressMuted;

};
struct DevonCursorOption {
    const u8 *text;
    TaskFunc func;

};
char devon_abi_PartyMenu_slotId[(__builtin_offsetof(struct PartyMenu, slotId)) + 1];
char devon_abi_PartyMenu_action[(__builtin_offsetof(struct PartyMenu, action)) + 1];
char devon_abi_Task_size[(sizeof(struct Task)) + 1];
char devon_abi_Task_func[(__builtin_offsetof(struct Task, func)) + 1];
char devon_abi_Task_isActive[(__builtin_offsetof(struct Task, isActive)) + 1];
char devon_abi_Pokemon_hp[(__builtin_offsetof(struct Pokemon, hp)) + 1];
char devon_abi_PartyMenuInternal_actions[(__builtin_offsetof(struct PartyMenuInternal, actions)) + 1];
char devon_abi_PartyMenuInternal_numActions[(__builtin_offsetof(struct PartyMenuInternal, numActions)) + 1];
char devon_abi_Menu_cursorPos[(__builtin_offsetof(struct Menu, cursorPos)) + 1];
char devon_abi_BattleStruct_playerPartyIdx[(__builtin_offsetof(struct BattleStruct, playerPartyIdx)) + 1];
char devon_abi_CursorOption_size[(sizeof(struct DevonCursorOption)) + 1];
char devon_abi_CursorOption_text[(__builtin_offsetof(struct DevonCursorOption, text)) + 1];
char devon_abi_CursorOption_func[(__builtin_offsetof(struct DevonCursorOption, func)) + 1];
char devon_abi_PartyMenu_size[(sizeof(struct PartyMenu)) + 1];
char devon_abi_Menu_size[(sizeof(struct Menu)) + 1];
char devon_abi_Pokemon_size[(sizeof(struct Pokemon)) + 1];
char devon_abi_PaletteFade_size[(sizeof(struct PaletteFadeControl)) + 1];
char devon_abi_task_count[(NUM_TASKS) + 1];
struct PaletteFadeControl devon_abi_palette_zero __attribute__((section(".abi_data"), used)) = {0};
struct PaletteFadeControl devon_abi_palette_active __attribute__((section(".abi_data"), used)) = {.active = 1};
