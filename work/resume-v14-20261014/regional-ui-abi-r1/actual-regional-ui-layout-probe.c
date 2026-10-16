#include "global.h"
#include "pokedex_screen.h"
#include "task.h"
#include "list_menu.h"
#include "constants/pokedex.h"
#include "constants/species.h"
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
enum StartMenuOption
{
    STARTMENU_POKEDEX = 0,
    STARTMENU_POKEMON,
    STARTMENU_BAG,
    STARTMENU_PLAYER,
    STARTMENU_SAVE,
    STARTMENU_OPTION,
    STARTMENU_EXIT,
    STARTMENU_RETIRE,
    STARTMENU_PLAYER2,
    MAX_STARTMENU_ITEMS
};
char qa_0[sizeof(struct PokedexScreenData) + 1];
char qa_1[sizeof(struct Task) + 1];
char qa_2[offsetof(struct Task, func) + 1];
char qa_3[offsetof(struct Task, isActive) + 1];
char qa_4[offsetof(struct Task, data) + 1];
char qa_5[sizeof(struct ListMenu) + 1];
char qa_6[offsetof(struct ListMenu, template) + 1];
char qa_7[offsetof(struct ListMenu, cursorPos) + 1];
char qa_8[offsetof(struct ListMenu, itemsAbove) + 1];
char qa_9[sizeof(struct ListMenuTemplate) + 1];
char qa_10[offsetof(struct ListMenuTemplate, items) + 1];
char qa_11[offsetof(struct ListMenuTemplate, totalItems) + 1];
char qa_12[sizeof(struct ListMenuItem) + 1];
char qa_13[offsetof(struct ListMenuItem, index) + 1];
char qa_14[offsetof(struct ListMenuItem, label) + 1];
char qa_15[offsetof(struct PokedexScreenData, taskId) + 1];
char qa_16[offsetof(struct PokedexScreenData, state) + 1];
char qa_17[offsetof(struct PokedexScreenData, regionalDex) + 1];
char qa_18[offsetof(struct PokedexScreenData, showNationalNumbers) + 1];
char qa_19[offsetof(struct PokedexScreenData, regionalNumberByNational) + 1];
char qa_20[offsetof(struct PokedexScreenData, listItems) + 1];
char qa_21[offsetof(struct PokedexScreenData, orderedDexCount) + 1];
char qa_22[offsetof(struct PokedexScreenData, dexOrderId) + 1];
char qa_23[offsetof(struct PokedexScreenData, modeSelectListMenuId) + 1];
char qa_24[offsetof(struct PokedexScreenData, orderedListMenuTaskId) + 1];
char qa_25[offsetof(struct PokedexScreenData, dexSpecies) + 1];
char qa_26[offsetof(struct PokedexScreenData, modeSelectItems) + 1];
char qa_27[offsetof(struct PokedexScreenData, numSeenKanto) + 1];
char qa_28[offsetof(struct PokedexScreenData, numOwnedKanto) + 1];
char qa_29[offsetof(struct PokedexScreenData, numSeenNational) + 1];
char qa_30[offsetof(struct PokedexScreenData, numOwnedNational) + 1];
char qc_0[STARTMENU_POKEDEX + 1];
char qc_1[MAX_STARTMENU_ITEMS + 1];
char qc_2[DEX_ORDER_NUMERICAL_KANTO + 1];
char qc_3[DEX_ORDER_NUMERICAL_NATIONAL + 1];
char qc_4[DEX_CATEGORY_COUNT + 1];
char qc_5[NATIONAL_DEX_COUNT + 1];
char qc_6[JOHTO_DEX_COUNT + 1];
char qc_7[HOENN_DEX_COUNT + 1];
char qc_8[KANTO_DEX_COUNT + 1];
char qc_9[NUM_SPECIES + 1];
char qc_10[NUM_TASKS + 1];
