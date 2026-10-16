#include "global.h"
#include "gflib.h"
#include "pokemon.h"
#include "pokemon_storage_system_internal.h"
#include "task.h"
#include "constants/items.h"
struct Menu
{
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
struct PokemonSummaryScreenData
{
    u16 bg1TilemapBuffer[0x800];
    u16 bg2TilemapBuffer[0x800];
    u16 bg3TilemapBuffer[0x800];
    u8 ALIGNED(4) windowIds[7];

    u8 ALIGNED(4) unk3008;
    u8 ALIGNED(4) ballIconSpriteId;
    u8 ALIGNED(4) monPicSpriteId;
    u8 ALIGNED(4) monIconSpriteId;

    u8 ALIGNED(4) inputHandlerTaskId;
    u8 ALIGNED(4) inhibitPageFlipInput;

    u8 ALIGNED(4) numMonPicBounces;

    bool32 isEnemyParty; /* 0x3024 */

    struct PokeSummary
    {
        u8 ALIGNED(4) speciesNameStrBuf[POKEMON_NAME_LENGTH];
        u8 ALIGNED(4) nicknameStrBuf[POKEMON_NAME_LENGTH + 1];
        u8 ALIGNED(4) otNameStrBuf[12];
        u8 ALIGNED(4) otNameStrBufs[2][12];

        u8 ALIGNED(4) dexNumStrBuf[5];
        u8 ALIGNED(4) unk306C[7];
        u8 ALIGNED(4) itemNameStrBuf[ITEM_NAME_LENGTH + 1];

        u8 ALIGNED(4) genderSymbolStrBuf[3];
        u8 ALIGNED(4) levelStrBuf[7];
        u8 ALIGNED(4) curHpStrBuf[9];
        u8 ALIGNED(4) statValueStrBufs[5][5];

        u8 ALIGNED(4) moveCurPpStrBufs[5][11];
        u8 ALIGNED(4) moveMaxPpStrBufs[5][11];
        u8 ALIGNED(4) moveNameStrBufs[5][MOVE_NAME_LENGTH + 1];
        u8 ALIGNED(4) movePowerStrBufs[5][5];
        u8 ALIGNED(4) moveAccuracyStrBufs[5][5];

        u8 ALIGNED(4) expPointsStrBuf[9];
        u8 ALIGNED(4) expToNextLevelStrBuf[9];

        u8 ALIGNED(4) abilityNameStrBuf[13];
        u8 ALIGNED(4) abilityDescStrBuf[52];
    } summary;

    u8 ALIGNED(4) isEgg; /* 0x3200 */
    u8 ALIGNED(4) isBadEgg; /* 0x3204 */

    u8 ALIGNED(4) mode; /* 0x3208 */
    u8 ALIGNED(4) unk320C; /* 0x320C */
    u8 ALIGNED(4) lastIndex; /* 0x3210 */
    u8 ALIGNED(4) curPageIndex; /* 0x3214 */
    u8 ALIGNED(4) unk3218; /* 0x3218 */
    u8 ALIGNED(4) isBoxMon; /* 0x321C */
    u8 ALIGNED(4) monTypes[2]; /* 0x3220 */

    u8 ALIGNED(4) pageFlipDirection; /* 0x3224 */
    u8 ALIGNED(4) unk3228; /* 0x3228 */
    u8 ALIGNED(4) unk322C; /* 0x322C */
    u8 ALIGNED(4) unk3230; /* 0x3230 */

    u8 ALIGNED(4) lockMovesFlag; /* 0x3234 */

    u8 ALIGNED(4) whichBgLayerToTranslate; /* 0x3238 */
    u8 ALIGNED(4) skillsPageBgNum; /* 0x323C */
    u8 ALIGNED(4) infoAndMovesPageBgNum; /* 0x3240 */
    u8 ALIGNED(4) flippingPages; /* 0x3244 */
    u8 ALIGNED(4) unk3248; /* 0x3248 */
    s16 ALIGNED(4) flipPagesBgHofs; /* 0x324C */

    u16 moveTypes[5]; /* 0x3250 */
    u16 moveIds[5]; /* 0x325A */
    u8 ALIGNED(4) numMoves; /* 0x3264 */
    u8 ALIGNED(4) isSwappingMoves; /* 0x3268 */

    u8 ALIGNED(4) curMonStatusAilment; /* 0x326C */

    u8 ALIGNED(4) state3270; /* 0x3270 */
    u8 ALIGNED(4) summarySetupStep; /* 0x3274 */
    u8 ALIGNED(4) loadBgGfxStep; /* 0x3278 */
    u8 ALIGNED(4) spriteCreationStep; /* 0x327C */
    u8 ALIGNED(4) bufferStringsStep; /* 0x3280 */
    u8 ALIGNED(4) state3284; /* 0x3284 */
    u8 ALIGNED(4) selectMoveInputHandlerState; /* 0x3288 */
    u8 ALIGNED(4) switchMonTaskState; /* 0x328C */

    struct Pokemon currentMon; /* 0x3290 */

    union
    {
        struct Pokemon * mons;
        struct BoxPokemon * boxMons;
    } monList;

    MainCallback savedCallback;
    struct Sprite *markingSprite;

    u8 ALIGNED(4) lastPageFlipDirection; /* 0x3300 */
    u8 ALIGNED(4) unk3304; /* 0x3304 */
};
char qo_0[sizeof(struct PokemonStorageSystemData)+1];
char qo_1[offsetof(struct PokemonStorageSystemData, state)+1];
char qo_2[offsetof(struct PokemonStorageSystemData, boxOption)+1];
char qo_3[offsetof(struct PokemonStorageSystemData, menuItems)+1];
char qo_4[offsetof(struct PokemonStorageSystemData, menuItemsCount)+1];
char qo_5[offsetof(struct PokemonStorageSystemData, displayMonPersonality)+1];
char qo_6[offsetof(struct PokemonStorageSystemData, displayMonSpecies)+1];
char qo_7[offsetof(struct PokemonStorageSystemData, displayMonIsEgg)+1];
char qo_8[offsetof(struct PokemonStorageSystemData, displayMonLevel)+1];
char qo_9[offsetof(struct PokemonStorageSystemData, displayMonNickname)+1];
char qo_10[offsetof(struct PokemonStorageSystemData, summaryCursorPos)+1];
char qo_11[sizeof(struct StorageMenu)+1];
char qo_12[offsetof(struct StorageMenu, textId)+1];
char qo_13[sizeof(struct PokemonSummaryScreenData)+1];
char qo_14[offsetof(struct PokemonSummaryScreenData, isEgg)+1];
char qo_15[offsetof(struct PokemonSummaryScreenData, isBadEgg)+1];
char qo_16[offsetof(struct PokemonSummaryScreenData, isBoxMon)+1];
char qo_17[offsetof(struct PokemonSummaryScreenData, summarySetupStep)+1];
char qo_18[offsetof(struct PokemonSummaryScreenData, currentMon)+1];
char qo_19[offsetof(struct PokemonSummaryScreenData, summary.nicknameStrBuf)+1];
char qo_20[offsetof(struct PokemonSummaryScreenData, summary.speciesNameStrBuf)+1];
char qo_21[sizeof(struct Menu)+1];
char qo_22[offsetof(struct Menu, cursorPos)+1];
char qo_23[offsetof(struct Menu, minCursorPos)+1];
char qo_24[offsetof(struct Menu, maxCursorPos)+1];
char qo_25[sizeof(struct Task)+1];
char qo_26[offsetof(struct Task, func)+1];
char qo_27[offsetof(struct Task, isActive)+1];
char qo_28[offsetof(struct Task, data)+1];
char qc_0[OPTION_MOVE_MONS+1];
char qc_1[MENU_TEXT_SUMMARY+1];
char qc_2[CURSOR_AREA_IN_BOX+1];
char qc_3[CURSOR_AREA_BOX_TITLE+1];
char qc_4[IN_BOX_COLUMNS+1];
char qc_5[IN_BOX_COUNT+1];
char qc_6[TOTAL_BOXES_COUNT+1];
char qc_7[ITEM_ESCAPE_ROPE+1];
char qc_8[NUM_TASKS+1];
