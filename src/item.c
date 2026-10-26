#include "global.h"
#include "gflib.h"
#include "berry.h"
#include "event_data.h"
#include "item.h"
#include "item_use.h"
#include "load_save.h"
#include "quest_log.h"
#include "strings.h"
#include "constants/hold_effects.h"
#include "constants/items.h"
#include "constants/maps.h"

EWRAM_DATA struct BagPocket gBagPockets[NUM_BAG_POCKETS] = {};

#define BAG_EXTRA_SLOT_COUNT 186
#define BAG_EXTRA_SB1_SLOTS 100
#define BAG_EXTRA_SB2_SLOTS (BAG_EXTRA_SLOT_COUNT - BAG_EXTRA_SB1_SLOTS)
#define BAG_EXTENSION_MAGIC1 0x32425954
#define BAG_EXTENSION_MAGIC2 0x31545845
#define BAG_EXTENSION_VERSION 1

struct BagExtensionHeader
{
    u32 magic1;
    u32 magic2;
    u32 quantityKey;
    u16 version;
    u16 totalSlots;
    u16 pocketCapacity[NUM_BAG_POCKETS];
    u8 reserved[14];
};

static const u8 sBagCapacities[NUM_BAG_POCKETS] =
{
    BAG_ITEMS_COUNT, BAG_KEYITEMS_COUNT, BAG_POKEBALLS_COUNT,
    BAG_TMHM_COUNT, BAG_BERRIES_COUNT
};

static const u8 sBagLegacyCapacities[NUM_BAG_POCKETS] =
{
    BAG_ITEMS_COUNT_LEGACY, BAG_KEYITEMS_COUNT_LEGACY, BAG_POKEBALLS_COUNT_LEGACY,
    BAG_TMHM_COUNT_LEGACY, BAG_BERRIES_COUNT_LEGACY
};

static const u16 sBagExtraOffsets[NUM_BAG_POCKETS] =
{
    0,
    BAG_ITEMS_COUNT_LEGACY,
    BAG_ITEMS_COUNT_LEGACY + BAG_KEYITEMS_COUNT_LEGACY,
    BAG_ITEMS_COUNT_LEGACY + BAG_KEYITEMS_COUNT_LEGACY + BAG_POKEBALLS_COUNT_LEGACY,
    BAG_ITEMS_COUNT_LEGACY + BAG_KEYITEMS_COUNT_LEGACY + BAG_POKEBALLS_COUNT_LEGACY + BAG_TMHM_COUNT_LEGACY
};

STATIC_ASSERT(sizeof(struct ItemSlot) == 4, BagSlotSizeUnchanged);
STATIC_ASSERT(sizeof(struct BagExtensionHeader) == 40, BagExtensionHeaderSize);
STATIC_ASSERT(sizeof(((struct SaveBlock1 *)0)->unused_348C) == BAG_EXTRA_SB1_SLOTS * sizeof(struct ItemSlot), BagExtraSb1Fits);
STATIC_ASSERT(sizeof(((struct SaveBlock2 *)0)->filler_DA0) == BAG_EXTRA_SB2_SLOTS * sizeof(struct ItemSlot) + sizeof(struct BagExtensionHeader), BagExtraSb2Fits);
STATIC_ASSERT(BAG_ITEMS_COUNT + BAG_KEYITEMS_COUNT + BAG_POKEBALLS_COUNT + BAG_TMHM_COUNT + BAG_BERRIES_COUNT == BAG_EXTRA_SLOT_COUNT * 2, BagExtraCapacityMatches);

static struct ItemSlot *GetExtraBagItemSlot(u16 index)
{
    if (index < BAG_EXTRA_SB1_SLOTS)
        return (struct ItemSlot *)gSaveBlock1Ptr->unused_348C + index;
    return (struct ItemSlot *)gSaveBlock2Ptr->filler_DA0 + index - BAG_EXTRA_SB1_SLOTS;
}

static struct BagExtensionHeader *GetBagExtensionHeader(void)
{
    return (struct BagExtensionHeader *)(gSaveBlock2Ptr->filler_DA0 + BAG_EXTRA_SB2_SLOTS * sizeof(struct ItemSlot));
}

bool8 HasBagExtension(void)
{
    struct BagExtensionHeader *header = GetBagExtensionHeader();

    return header->magic1 == BAG_EXTENSION_MAGIC1 || header->magic2 == BAG_EXTENSION_MAGIC2;
}

bool8 ValidateBagExtensionForLoad(void)
{
    struct BagExtensionHeader *header = GetBagExtensionHeader();
    u16 i;

    // A missing marker is an old save. A recognized but damaged/unsupported
    // extension must be rejected by the save loader, never silently erased.
    if (header->magic1 != BAG_EXTENSION_MAGIC1 && header->magic2 != BAG_EXTENSION_MAGIC2)
        return TRUE;
    if (header->magic1 != BAG_EXTENSION_MAGIC1 || header->magic2 != BAG_EXTENSION_MAGIC2
     || header->version != BAG_EXTENSION_VERSION || header->totalSlots != BAG_EXTRA_SLOT_COUNT
     || header->quantityKey != gSaveBlock2Ptr->encryptionKey)
        return FALSE;
    for (i = 0; i < NUM_BAG_POCKETS; i++)
        if (header->pocketCapacity[i] != sBagCapacities[i])
            return FALSE;
    return TRUE;
}

static void EnsureBagExtension(void)
{
    struct BagExtensionHeader *header = GetBagExtensionHeader();
    u16 i;

    if (header->magic1 == BAG_EXTENSION_MAGIC1 || header->magic2 == BAG_EXTENSION_MAGIC2)
        return;

    // Old saves have no extension header. Only the former padding is initialized;
    // legacy items and their existing quantity encryption are left untouched.
    for (i = 0; i < BAG_EXTRA_SLOT_COUNT; i++)
    {
        struct ItemSlot *slot = GetExtraBagItemSlot(i);
        slot->itemId = ITEM_NONE;
        SetBagItemQuantity(&slot->quantity, 0);
    }
    CpuFill16(0, header, sizeof(*header));
    header->quantityKey = gSaveBlock2Ptr->encryptionKey;
    header->version = BAG_EXTENSION_VERSION;
    header->totalSlots = BAG_EXTRA_SLOT_COUNT;
    for (i = 0; i < NUM_BAG_POCKETS; i++)
        header->pocketCapacity[i] = sBagCapacities[i];
    header->magic1 = BAG_EXTENSION_MAGIC1;
    header->magic2 = BAG_EXTENSION_MAGIC2;
}

bool8 PrepareBagExtensionForSave(void)
{
    if (!ValidateBagExtensionForLoad())
        return FALSE;
    EnsureBagExtension();
    return HasBagExtension() && ValidateBagExtensionForLoad();
}

struct ItemSlot *GetBagItemSlot(u8 pocket, u16 index)
{
    if (pocket >= NUM_BAG_POCKETS || index >= gBagPockets[pocket].capacity)
        return NULL;
    EnsureBagExtension();
    if (index < sBagLegacyCapacities[pocket])
        return &gBagPockets[pocket].itemSlots[index];
    return GetExtraBagItemSlot(sBagExtraOffsets[pocket] + index - sBagLegacyCapacities[pocket]);
}

struct ItemSlot *GetBagPocketSlot(struct BagPocket *pocket, u16 index)
{
    return GetBagItemSlot(pocket - gBagPockets, index);
}

void CopyBagPocketToBuffer(u8 pocket, struct ItemSlot *buffer)
{
    u16 i;

    for (i = 0; i < gBagPockets[pocket].capacity; i++)
        buffer[i] = *GetBagItemSlot(pocket, i);
}

void CopyBagPocketFromBuffer(u8 pocket, const struct ItemSlot *buffer)
{
    u16 i;

    for (i = 0; i < gBagPockets[pocket].capacity; i++)
        *GetBagItemSlot(pocket, i) = buffer[i];
}

void ClearBagPocket(u8 pocket)
{
    u16 i;

    for (i = 0; i < gBagPockets[pocket].capacity; i++)
    {
        struct ItemSlot *slot = GetBagItemSlot(pocket, i);
        slot->itemId = ITEM_NONE;
        SetBagItemQuantity(&slot->quantity, 0);
    }
}

void MoveBagItemSlotInList(u8 pocket, u32 from, u32 to)
{
    s16 i;
    struct ItemSlot first;

    if (from == to || pocket >= NUM_BAG_POCKETS || from >= gBagPockets[pocket].capacity || to > gBagPockets[pocket].capacity)
        return;
    first = *GetBagItemSlot(pocket, from);
    if (to > from)
    {
        to--;
        for (i = from; i < to; i++)
            *GetBagItemSlot(pocket, i) = *GetBagItemSlot(pocket, i + 1);
    }
    else
    {
        for (i = from; i > to; i--)
            *GetBagItemSlot(pocket, i) = *GetBagItemSlot(pocket, i - 1);
    }
    *GetBagItemSlot(pocket, to) = first;
}

void SortAndCompactBagPocket(struct BagPocket * pocket);

// Item descriptions and data
#include "data/items.h"

u16 GetBagItemQuantity(u16 * ptr)
{
    return gSaveBlock2Ptr->encryptionKey ^ *ptr;
}

void SetBagItemQuantity(u16 * ptr, u16 value)
{
    *ptr = value ^ gSaveBlock2Ptr->encryptionKey;
}

u16 GetPcItemQuantity(u16 * ptr)
{
    return 0 ^ *ptr;
}

void SetPcItemQuantity(u16 * ptr, u16 value)
{
    *ptr = value ^ 0;
}

void ApplyNewEncryptionKeyToBagItems(u32 key)
{
    u32 i, j;

    EnsureBagExtension();
    for (i = 0; i < NUM_BAG_POCKETS; i++)
    {
        for (j = 0; j < gBagPockets[i].capacity; j++)
        {
            ApplyNewEncryptionKeyToHword(&(*GetBagItemSlot(i, j)).quantity, key);
        }
    }
    GetBagExtensionHeader()->quantityKey = key;
}

void ApplyNewEncryptionKeyToBagItems_(u32 key)
{
    ApplyNewEncryptionKeyToBagItems(key);
}

void SetBagPocketsPointers(void)
{
    gBagPockets[POCKET_ITEMS - 1].itemSlots = gSaveBlock1Ptr->bagPocket_Items;
    gBagPockets[POCKET_ITEMS - 1].capacity = BAG_ITEMS_COUNT;
    gBagPockets[POCKET_KEY_ITEMS - 1].itemSlots = gSaveBlock1Ptr->bagPocket_KeyItems;
    gBagPockets[POCKET_KEY_ITEMS - 1].capacity = BAG_KEYITEMS_COUNT;
    gBagPockets[POCKET_POKE_BALLS - 1].itemSlots = gSaveBlock1Ptr->bagPocket_PokeBalls;
    gBagPockets[POCKET_POKE_BALLS - 1].capacity = BAG_POKEBALLS_COUNT;
    gBagPockets[POCKET_TM_CASE - 1].itemSlots = gSaveBlock1Ptr->bagPocket_TMHM;
    gBagPockets[POCKET_TM_CASE - 1].capacity = BAG_TMHM_COUNT;
    gBagPockets[POCKET_BERRY_POUCH - 1].itemSlots = gSaveBlock1Ptr->bagPocket_Berries;
    gBagPockets[POCKET_BERRY_POUCH - 1].capacity = BAG_BERRIES_COUNT;
}

void CopyItemName(u16 itemId, u8 * dest)
{
    if (itemId == ITEM_ENIGMA_BERRY)
    {
        StringCopy(dest, GetBerryInfo(ITEM_TO_BERRY(ITEM_ENIGMA_BERRY))->name);
        StringAppend(dest, gText_Berry);
    }
    else
    {
        StringCopy(dest, ItemId_GetName(itemId));
    }
}

s8 BagPocketGetFirstEmptySlot(u8 pocketId)
{
    u16 i;

    for (i = 0; i < gBagPockets[pocketId].capacity; i++)
    {
        if ((*GetBagItemSlot(pocketId, i)).itemId == ITEM_NONE)
            return i;
    }

    return -1;
}

bool8 IsPocketNotEmpty(u8 pocketId)
{
    u8 i;

    for (i = 0; i < gBagPockets[pocketId - 1].capacity; i++)
    {
        if ((*GetBagItemSlot(pocketId - 1, i)).itemId != ITEM_NONE)
            return TRUE;
    }

    return FALSE;
}

bool8 CheckBagHasItem(u16 itemId, u16 count)
{
    u8 i;
    u8 pocket;

    if (ItemId_GetPocket(itemId) == 0)
        return FALSE;

    pocket = ItemId_GetPocket(itemId) - 1;
    // Check for item slots that contain the item
    for (i = 0; i < gBagPockets[pocket].capacity; i++)
    {
        if ((*GetBagItemSlot(pocket, i)).itemId == itemId)
        {
            u16 quantity;
            // Does this item slot contain enough of the item?
            quantity = GetBagItemQuantity(&(*GetBagItemSlot(pocket, i)).quantity);
            if (quantity >= count)
                return TRUE;
                // RS and Emerald check whether there is enough of the
                // item across all stacks.
                // For whatever reason, FR/LG assume there's only one
                // stack of the item.
            else
                return FALSE;
        }
    }
    return FALSE;
}

bool8 HasAtLeastOneBerry(void)
{
    u8 itemId;
    bool8 exists;

    exists = CheckBagHasItem(ITEM_BERRY_POUCH, 1);
    if (!exists)
    {
        gSpecialVar_Result = FALSE;
        return FALSE;
    }
    for (itemId = FIRST_BERRY_INDEX; itemId <= LAST_BERRY_INDEX; itemId++)
    {
        exists = CheckBagHasItem(itemId, 1);
        if (exists)
        {
            gSpecialVar_Result = TRUE;
            return TRUE;
        }
    }

    gSpecialVar_Result = FALSE;
    return FALSE;
}

bool8 CheckBagHasSpace(u16 itemId, u16 count)
{
    u8 i;
    u8 pocket;

    if (ItemId_GetPocket(itemId) == 0)
        return FALSE;

    pocket = ItemId_GetPocket(itemId) - 1;
    // Check for item slots that contain the item
    for (i = 0; i < gBagPockets[pocket].capacity; i++)
    {
        if ((*GetBagItemSlot(pocket, i)).itemId == itemId)
        {
            u16 quantity;
            // Does this stack have room for more??
            quantity = GetBagItemQuantity(&(*GetBagItemSlot(pocket, i)).quantity);
            if (quantity + count <= 999)
                return TRUE;
            // RS and Emerald check whether there is enough of the
            // item across all stacks.
            // For whatever reason, FR/LG assume there's only one
            // stack of the item.
            else
                return FALSE;
        }
    }

    if (BagPocketGetFirstEmptySlot(pocket) != -1)
        return TRUE;

    return FALSE;
}

bool8 AddBagItem(u16 itemId, u16 count)
{
    u8 i;
    u8 pocket;
    s8 idx;

    if (ItemId_GetPocket(itemId) == 0)
        return FALSE;

    pocket = ItemId_GetPocket(itemId) - 1;
    for (i = 0; i < gBagPockets[pocket].capacity; i++)
    {
        if ((*GetBagItemSlot(pocket, i)).itemId == itemId)
        {
            u16 quantity;
            // Does this stack have room for more??
            quantity = GetBagItemQuantity(&(*GetBagItemSlot(pocket, i)).quantity);
            if (quantity + count <= 999)
            {
                quantity += count;
                SetBagItemQuantity(&(*GetBagItemSlot(pocket, i)).quantity, quantity);
                return TRUE;
            }
            // RS and Emerald check whether there is enough of the
            // item across all stacks.
            // For whatever reason, FR/LG assume there's only one
            // stack of the item.
            else
                return FALSE;
        }
    }

    if (pocket == POCKET_TM_CASE - 1 && !CheckBagHasItem(ITEM_TM_CASE, 1))
    {
        idx = BagPocketGetFirstEmptySlot(POCKET_KEY_ITEMS - 1);
        if (idx == -1)
            return FALSE;
        (*GetBagItemSlot(POCKET_KEY_ITEMS - 1, idx)).itemId = ITEM_TM_CASE;
        SetBagItemQuantity(&(*GetBagItemSlot(POCKET_KEY_ITEMS - 1, idx)).quantity, 1);
    }

    if (pocket == POCKET_BERRY_POUCH - 1 && !CheckBagHasItem(ITEM_BERRY_POUCH, 1))
    {
        idx = BagPocketGetFirstEmptySlot(POCKET_KEY_ITEMS - 1);
        if (idx == -1)
            return FALSE;
        (*GetBagItemSlot(POCKET_KEY_ITEMS - 1, idx)).itemId = ITEM_BERRY_POUCH;
        SetBagItemQuantity(&(*GetBagItemSlot(POCKET_KEY_ITEMS - 1, idx)).quantity, 1);
        FlagSet(FLAG_SYS_GOT_BERRY_POUCH);
    }

    if (itemId == ITEM_BERRY_POUCH)
        FlagSet(FLAG_SYS_GOT_BERRY_POUCH);

    idx = BagPocketGetFirstEmptySlot(pocket);
    if (idx == -1)
        return FALSE;

    (*GetBagItemSlot(pocket, idx)).itemId = itemId;
    SetBagItemQuantity(&(*GetBagItemSlot(pocket, idx)).quantity, count);
    return TRUE;
}

bool8 RemoveBagItem(u16 itemId, u16 count)
{
    u8 i;
    u8 pocket;

    if (ItemId_GetPocket(itemId) == 0)
        return FALSE;

    if (itemId == ITEM_NONE)
        return FALSE;

    pocket = ItemId_GetPocket(itemId) - 1;
    // Check for item slots that contain the item
    for (i = 0; i < gBagPockets[pocket].capacity; i++)
    {
        if ((*GetBagItemSlot(pocket, i)).itemId == itemId)
        {
            u16 quantity;
            // Does this item slot contain enough of the item?
            quantity = GetBagItemQuantity(&(*GetBagItemSlot(pocket, i)).quantity);
            if (quantity >= count)
            {
                quantity -= count;
                SetBagItemQuantity(&(*GetBagItemSlot(pocket, i)).quantity, quantity);
                if (quantity == 0)
                    (*GetBagItemSlot(pocket, i)).itemId = ITEM_NONE;
                return TRUE;
            }
            // RS and Emerald check whether there is enough of the
            // item across all stacks.
            // For whatever reason, FR/LG assume there's only one
            // stack of the item.
            else
                return FALSE;
        }
    }
    return FALSE;
}

u8 GetPocketByItemId(u16 itemId)
{
    return ItemId_GetPocket(itemId); // wow such important
}

void ClearItemSlots(struct ItemSlot * slots, u8 capacity)
{
    u16 i;

    for (i = 0; i < capacity; i++)
    {
        slots[i].itemId = ITEM_NONE;
        SetBagItemQuantity(&slots[i].quantity, 0);
    }
}

void ClearPCItemSlots(void)
{
    u16 i;

    for (i = 0; i < PC_ITEMS_COUNT; i++)
    {
        gSaveBlock1Ptr->pcItems[i].itemId = ITEM_NONE;
        SetPcItemQuantity(&gSaveBlock1Ptr->pcItems[i].quantity, 0);
    }
}

void ClearBag(void)
{
    u16 i;

    for (i = 0; i < NUM_BAG_POCKETS; i++)
    {
        ClearBagPocket(i);
    }
}

s8 PCItemsGetFirstEmptySlot(void)
{
    s8 i;

    for (i = 0; i < PC_ITEMS_COUNT; i++)
    {
        if (gSaveBlock1Ptr->pcItems[i].itemId == ITEM_NONE)
            return i;
    }

    return -1;
}

u8 CountItemsInPC(void)
{
    u8 count = 0;
    u8 i;

    for (i = 0; i < PC_ITEMS_COUNT; i++)
    {
        if (gSaveBlock1Ptr->pcItems[i].itemId != ITEM_NONE)
            count++;
    }

    return count;
}

bool8 CheckPCHasItem(u16 itemId, u16 count)
{
    u8 i;
    u16 quantity;

    for (i = 0; i < PC_ITEMS_COUNT; i++)
    {
        if (gSaveBlock1Ptr->pcItems[i].itemId == itemId)
        {
            quantity = GetPcItemQuantity(&gSaveBlock1Ptr->pcItems[i].quantity);
            if (quantity >= count)
                return TRUE;
        }
    }

    return FALSE;
}

bool8 AddPCItem(u16 itemId, u16 count)
{
    u8 i;
    u16 quantity;
    s8 idx;

    for (i = 0; i < PC_ITEMS_COUNT; i++)
    {
        if (gSaveBlock1Ptr->pcItems[i].itemId == itemId)
        {
            quantity = GetPcItemQuantity(&gSaveBlock1Ptr->pcItems[i].quantity);
            if (quantity + count <= 999)
            {
                quantity += count;
                SetPcItemQuantity(&gSaveBlock1Ptr->pcItems[i].quantity, quantity);
                return TRUE;
            }
            else
                return FALSE;
        }
    }

    idx = PCItemsGetFirstEmptySlot();
    if (idx == -1)
        return FALSE;

    gSaveBlock1Ptr->pcItems[idx].itemId = itemId;
    SetPcItemQuantity(&gSaveBlock1Ptr->pcItems[idx].quantity, count);
    return TRUE;
}

void RemovePCItem(u16 itemId, u16 count)
{
    u32 i;
    u16 quantity;

    if (itemId == ITEM_NONE)
        return;

    for (i = 0; i < PC_ITEMS_COUNT; i++)
    {
        if (gSaveBlock1Ptr->pcItems[i].itemId == itemId)
            break;
    }

    if (i != PC_ITEMS_COUNT)
    {
        quantity = GetPcItemQuantity(&gSaveBlock1Ptr->pcItems[i].quantity) - count;
        SetPcItemQuantity(&gSaveBlock1Ptr->pcItems[i].quantity, quantity);
        if (quantity == 0)
            gSaveBlock1Ptr->pcItems[i].itemId = ITEM_NONE;
    }
}

void ItemPcCompaction(void)
{
    u16 i, j;
    struct ItemSlot tmp;

    for (i = 0; i < PC_ITEMS_COUNT - 1; i++)
    {
        for (j = i + 1; j < PC_ITEMS_COUNT; j++)
        {
            if (gSaveBlock1Ptr->pcItems[i].itemId == ITEM_NONE)
            {
                tmp = gSaveBlock1Ptr->pcItems[i];
                gSaveBlock1Ptr->pcItems[i] = gSaveBlock1Ptr->pcItems[j];
                gSaveBlock1Ptr->pcItems[j] = tmp;
            }
        }
    }
}

void RegisteredItemHandleBikeSwap(void)
{
    switch (gSaveBlock1Ptr->registeredItem)
    {
    case ITEM_MACH_BIKE:
        gSaveBlock1Ptr->registeredItem = ITEM_ACRO_BIKE;
        break;
    case ITEM_ACRO_BIKE:
        gSaveBlock1Ptr->registeredItem = ITEM_MACH_BIKE;
        break;
    }
}

void SwapItemSlots(struct ItemSlot * a, struct ItemSlot * b)
{
    struct ItemSlot c;
    c = *a;
    *a = *b;
    *b = c;
}

void BagPocketCompaction(struct BagPocket *pocket)
{
    u16 i, j;

    for (i = 0; i + 1 < pocket->capacity; i++)
        for (j = i + 1; j < pocket->capacity; j++)
            if (GetBagItemQuantity(&GetBagPocketSlot(pocket, i)->quantity) == 0)
                SwapItemSlots(GetBagPocketSlot(pocket, i), GetBagPocketSlot(pocket, j));
}

void SortPocketAndPlaceHMsFirst(struct BagPocket *pocket)
{
    u16 i, count = 0;
    struct ItemSlot *buffer;

    SortAndCompactBagPocket(pocket);
    buffer = Alloc(pocket->capacity * sizeof(struct ItemSlot));
    if (buffer == NULL)
        return;
    // Keep encrypted quantities intact while partitioning HMs ahead of TMs.
    for (i = 0; i < pocket->capacity; i++)
    {
        struct ItemSlot *slot = GetBagPocketSlot(pocket, i);
        if (slot->itemId >= ITEM_HM01 && GetBagItemQuantity(&slot->quantity) != 0)
            buffer[count++] = *slot;
    }
    for (i = 0; i < pocket->capacity; i++)
    {
        struct ItemSlot *slot = GetBagPocketSlot(pocket, i);
        if (slot->itemId < ITEM_HM01 || GetBagItemQuantity(&slot->quantity) == 0)
            buffer[count++] = *slot;
    }
    for (i = 0; i < pocket->capacity; i++)
        *GetBagPocketSlot(pocket, i) = buffer[i];
    Free(buffer);
}

void SortAndCompactBagPocket(struct BagPocket * pocket)
{
    u16 i, j;

    for (i = 0; i < pocket->capacity; i++)
    {
        for (j = i + 1; j < pocket->capacity; j++)
        {
            if (GetBagItemQuantity(&(*GetBagPocketSlot(pocket, i)).quantity) == 0 || (GetBagItemQuantity(&(*GetBagPocketSlot(pocket, j)).quantity) != 0 && (*GetBagPocketSlot(pocket, i)).itemId > (*GetBagPocketSlot(pocket, j)).itemId))
                SwapItemSlots(&(*GetBagPocketSlot(pocket, i)), &(*GetBagPocketSlot(pocket, j)));
        }
    }
}

u16 BagGetItemIdByPocketPosition(u8 pocketId, u16 slotId)
{
    struct ItemSlot *slot = GetBagItemSlot(pocketId - 1, slotId);
    return slot == NULL ? ITEM_NONE : slot->itemId;
}

u16 BagGetQuantityByPocketPosition(u8 pocketId, u16 slotId)
{
    struct ItemSlot *slot = GetBagItemSlot(pocketId - 1, slotId);
    return slot == NULL ? 0 : GetBagItemQuantity(&slot->quantity);
}

u16 BagGetQuantityByItemId(u16 itemId)
{
    u16 i;
    struct BagPocket * pocket = &gBagPockets[ItemId_GetPocket(itemId) - 1];

    for (i = 0; i < pocket->capacity; i++)
    {
        if ((*GetBagPocketSlot(pocket, i)).itemId == itemId)
            return GetBagItemQuantity(&(*GetBagPocketSlot(pocket, i)).quantity);
    }

    return 0;
}

void TrySetObtainedItemQuestLogEvent(u16 itemId)
{
    // Only some key items trigger this event
    if (itemId == ITEM_OAKS_PARCEL
     || itemId == ITEM_POKE_FLUTE
     || itemId == ITEM_SECRET_KEY
     || itemId == ITEM_BIKE_VOUCHER
     || itemId == ITEM_GOLD_TEETH
     || itemId == ITEM_OLD_AMBER
     || itemId == ITEM_CARD_KEY
     || itemId == ITEM_LIFT_KEY
     || itemId == ITEM_HELIX_FOSSIL
     || itemId == ITEM_DOME_FOSSIL
     || itemId == ITEM_SILPH_SCOPE
     || itemId == ITEM_BICYCLE
     || itemId == ITEM_TOWN_MAP
     || itemId == ITEM_VS_SEEKER
     || itemId == ITEM_TEACHY_TV
     || itemId == ITEM_RAINBOW_PASS
     || itemId == ITEM_TEA
     || itemId == ITEM_POWDER_JAR
     || itemId == ITEM_RUBY
     || itemId == ITEM_SAPPHIRE)
    {
        if (itemId != ITEM_TOWN_MAP || (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_PALLET_TOWN_RIVALS_HOUSE) && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_PALLET_TOWN_RIVALS_HOUSE)))
        {
            struct QuestLogEvent_StoryItem * data = malloc(sizeof(*data));
            data->itemId = itemId;
            data->mapSec = gMapHeader.regionMapSectionId;
            SetQuestLogEvent(QL_EVENT_OBTAINED_STORY_ITEM, (const u16 *)data);
            free(data);
        }
    }
}

u16 SanitizeItemId(u16 itemId)
{
    if (itemId >= ITEMS_COUNT)
        return ITEM_NONE;
    return itemId;
}

const u8 * ItemId_GetName(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].name;
}

// Unused
u16 ItemId_GetId(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].itemId;
}

u16 ItemId_GetPrice(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].price;
}

u8 ItemId_GetHoldEffect(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].holdEffect;
}

u8 ItemId_GetHoldEffectParam(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].holdEffectParam;
}

const u8 * ItemId_GetDescription(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].description;
}

u8 ItemId_GetImportance(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].importance;
}

// Unused
u8 ItemId_GetRegistrability(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].registrability;
}

u8 ItemId_GetPocket(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].pocket;
}

u8 ItemId_GetType(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].type;
}

ItemUseFunc ItemId_GetFieldFunc(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].fieldUseFunc;
}

bool8 ItemId_GetBattleUsage(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].battleUsage;
}

ItemUseFunc ItemId_GetBattleFunc(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].battleUseFunc;
}

u8 ItemId_GetSecondaryId(u16 itemId)
{
    return gItems[SanitizeItemId(itemId)].secondaryId;
}
