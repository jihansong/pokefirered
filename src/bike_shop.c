#include "global.h"
#include "bike.h"
#include "bike_shop.h"
#include "event_data.h"
#include "field_player_avatar.h"
#include "item.h"
#include "constants/items.h"
#include "constants/flags.h"

u16 GetRydelBikeState(void)
{
    gSpecialVar_Result = (CheckBagHasItem(ITEM_MACH_BIKE, 1) ? 1 : 0)
         | (CheckBagHasItem(ITEM_ACRO_BIKE, 1) ? 2 : 0);
    return gSpecialVar_Result;
}

static u16 TryCommitRydelBike(void)
{
    struct ItemSlot before[BAG_KEYITEMS_COUNT];
    u16 desired = gSpecialVar_0x8004;
    u16 old;
    u16 state = GetRydelBikeState();

    if (desired != ITEM_MACH_BIKE && desired != ITEM_ACRO_BIKE)
        return 0;
    if (CheckBagHasItem(desired, 1))
        return 2;
    if (state == 0 && FlagGet(FLAG_HOENN_RYDEL_BIKE_RECEIVED))
        return 0;

    old = desired == ITEM_MACH_BIKE ? ITEM_ACRO_BIKE : ITEM_MACH_BIKE;
    // Preserve the encrypted pocket exactly if the replacement cannot be added.
    CopyBagPocketToBuffer(POCKET_KEY_ITEMS - 1, before);
    if (state != 0 && !RemoveBagItem(old, 1))
        return 0;
    if (!AddBagItem(desired, 1))
    {
        CopyBagPocketFromBuffer(POCKET_KEY_ITEMS - 1, before);
        return 0;
    }
    if (state != 0 && gSaveBlock1Ptr->registeredItem == old)
        RegisteredItemHandleBikeSwap();
    FlagSet(FLAG_HOENN_RYDEL_BIKE_RECEIVED);
    Bike_SetMode(desired == ITEM_MACH_BIKE ? BIKE_MODE_MACH : BIKE_MODE_ACRO);
    // The shop normally forces dismount on entry; keep scripted exchanges safe too.
    if (gPlayerAvatar.flags & (PLAYER_AVATAR_FLAG_MACH_BIKE | PLAYER_AVATAR_FLAG_ACRO_BIKE))
        SetPlayerAvatarTransitionFlags(desired == ITEM_MACH_BIKE ? PLAYER_AVATAR_FLAG_MACH_BIKE : PLAYER_AVATAR_FLAG_ACRO_BIKE);
    return 1;
}

u16 CommitRydelBike(void)
{
    gSpecialVar_Result = TryCommitRydelBike();
    return gSpecialVar_Result;
}
