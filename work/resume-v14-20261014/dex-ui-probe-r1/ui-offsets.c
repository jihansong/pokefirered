#include "global.h"
#include "main.h"
#include "palette.h"
#include "task.h"
#include "list_menu.h"
#include "constants/pokedex.h"
#include "pokedex_screen.h"
struct PokedexScreenData
{
    u8 taskId;
    u8 state;
    u8 data[2];
    u8 areaMarkersTaskId;
    u32 unlockedCategories;
    u32 modeSelectInput;
    u16 modeSelectItemsAbove;
    u16 modeSelectCursorPos;
    u8 modeSelectWindowId;
    u8 selectionIconWindowId;
    u8 dexCountsWindowId;
    u8 modeSelectListMenuId;
    u16 pageSpecies[4];
    u8 categoryMonWindowIds[4];
    u8 categoryMonInfoWindowIds[4];
    u8 category;
    u8 firstPageInCategory;
    u8 lastPageInCategory;
    u8 pageNum;
    u8 numMonsOnPage;
    u8 categoryCursorPosInPage;
    u8 categoryPageSelectionCursorTimer;
    u8 parentOfCategoryMenu;
    u32 characteristicMenuInput;
    u16 kantoOrderMenuItemsAbove;
    u16 kantoOrderMenuCursorPos;
    u16 characteristicOrderMenuItemsAbove;
    u16 characteristicOrderMenuCursorPos;
    u16 nationalOrderMenuItemsAbove;
    u16 nationalOrderMenuCursorPos;
    u8 numericalOrderWindowId;
    u8 orderedListMenuTaskId;
    u8 dexOrderId;
    struct ListMenuItem * listItems;
    u16 orderedDexCount;
    u8 windowIds[0x10];
    u16 dexSpecies;
    u16 * bgBufsMem;
    u8 scrollArrowsTaskId;
    u8 categoryPageCursorTaskId;
    u16 modeSelectCursorPosBak;
    u8 unlockedSeviiAreas;
    u8 areaRegion; // DEX_AREA_REGION_*, or DEX_AREA_REGION_COUNT for the species' home
    u16 numSeenKanto;
    u16 numOwnedKanto;
    u16 numSeenNational;
    u16 numOwnedNational;
    u8 regionalDex;
    bool8 showNationalNumbers;
    u16 regionalNumberByNational[NATIONAL_DEX_COUNT + 1];
    struct ListMenuItem modeSelectItems[20];
};
char qa_shape_0[sizeof(struct PokedexScreenData)+1];
char qa_shape_1[offsetof(struct PokedexScreenData, taskId)+1];
char qa_shape_2[offsetof(struct PokedexScreenData, state)+1];
char qa_shape_3[offsetof(struct PokedexScreenData, modeSelectListMenuId)+1];
char qa_shape_4[offsetof(struct PokedexScreenData, orderedListMenuTaskId)+1];
char qa_shape_5[offsetof(struct PokedexScreenData, dexOrderId)+1];
char qa_shape_6[offsetof(struct PokedexScreenData, orderedDexCount)+1];
char qa_shape_7[offsetof(struct PokedexScreenData, regionalDex)+1];
char qa_shape_8[offsetof(struct PokedexScreenData, showNationalNumbers)+1];
char qa_shape_9[sizeof(struct ListMenu)+1];
char qa_shape_10[offsetof(struct ListMenu, cursorPos)+1];
char qa_shape_11[offsetof(struct ListMenu, itemsAbove)+1];
char qa_shape_12[offsetof(struct ListMenu, template)+1];
char qa_shape_13[sizeof(struct ListMenuTemplate)+1];
char qa_shape_14[offsetof(struct ListMenuTemplate, items)+1];
char qa_shape_15[offsetof(struct ListMenuTemplate, totalItems)+1];
char qa_shape_16[offsetof(struct ListMenuTemplate, maxShowed)+1];
char qa_shape_17[sizeof(struct ListMenuItem)+1];
char qa_shape_18[offsetof(struct ListMenuItem, index)+1];
char qa_shape_19[sizeof(struct Task)+1];
char qa_shape_20[offsetof(struct Task, func)+1];
char qa_shape_21[offsetof(struct Task, isActive)+1];
char qa_shape_22[offsetof(struct Task, data)+1];
char qa_shape_23[sizeof(struct Main)+1];
char qa_shape_24[offsetof(struct Main, callback2)+1];
char qa_shape_25[offsetof(struct Main, vblankCounter2)+1];
char qa_shape_26[offsetof(struct Main, heldKeysRaw)+1];
char qa_shape_27[offsetof(struct Main, newAndRepeatedKeys)+1];
char qa_shape_28[offsetof(struct Main, keyRepeatCounter)+1];
char qa_shape_29[sizeof(struct PaletteFadeControl)+1];
char qa_numeric_menu_value[DEX_MODE(NUMERICAL_KANTO)+1];
const struct PaletteFadeControl qa_palette_active_mask = {.active = 1};
