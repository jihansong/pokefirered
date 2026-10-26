#include "global.h"
#include "gflib.h"
#include "bike.h"
#include "event_data.h"
#include "field_camera.h"
#include "field_player_avatar.h"
#include "fieldmap.h"
#include "hoenn_puzzles.h"
#include "metatile_behavior.h"
#include "overworld.h"
#include "script.h"
#include "sound.h"
#include "task.h"
#include "constants/flags.h"
#include "constants/maps.h"
#include "constants/metatile_behaviors.h"
#include "constants/songs.h"

// Adapted from pokeemerald 5eff78649e7170a877b961ef0b3da13b81a16038.
// Hoenn's map-local counter leaves FRLG's saved Icefall Cave counter alone.
#define ICE_COUNT VAR_TEMP_0
#define ICE_CRACKED 0x20E
#define ICE_BROKEN 0x206
#define ICE_STAIRS 0x207
#define SKY_CRACKED 0x236
#define SKY_HOLE 0x237
#define ICE_STATE_MARKER 0x4943

static const u16 sIceRowVars[] =
{
    0, 0, 0, 0, 0, 0,
    VAR_TEMP_1, VAR_TEMP_2, VAR_TEMP_3, VAR_TEMP_4,
    0, 0,
    VAR_TEMP_5, VAR_TEMP_6, VAR_TEMP_7,
    0, 0,
    VAR_TEMP_8, VAR_TEMP_9, VAR_TEMP_A
};

static const u16 sSkyClean1[] = INCBIN_U16("data/hoenn_puzzles/sky_pillar_1f_clean.bin");
static const u16 sSkyClean2[] = INCBIN_U16("data/hoenn_puzzles/sky_pillar_2f_clean.bin");
static const u16 sSkyClean3[] = INCBIN_U16("data/hoenn_puzzles/sky_pillar_3f_clean.bin");
static const u16 sSkyClean4[] = INCBIN_U16("data/hoenn_puzzles/sky_pillar_4f_clean.bin");
static const u16 sSkyClean5[] = INCBIN_U16("data/hoenn_puzzles/sky_pillar_5f_clean.bin");
static const u16 sSkyCleanTop[] = INCBIN_U16("data/hoenn_puzzles/sky_pillar_top_clean.bin");

extern const u8 SkyPillar_2F_TY_Fall[];
extern const u8 SkyPillar_4F_TY_Fall[];

static bool8 IsSkyPillarFloor(void)
{
    return gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_SKY_PILLAR_1F)
        && (gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SKY_PILLAR_1F)
         || gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SKY_PILLAR_2F)
         || gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SKY_PILLAR_3F)
         || gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SKY_PILLAR_4F)
         || gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SKY_PILLAR_5F));
}

void HoennSootopolisResetIce(void)
{
    u16 var;

    VarSet(ICE_COUNT, FlagGet(FLAG_HOENN_BADGE08_GET) ? 68 : 1);
    VarSet(VAR_TEMP_F, ICE_STATE_MARKER);
    for (var = VAR_TEMP_1; var <= VAR_TEMP_A; var++)
        VarSet(var, 0);
}

static bool8 IceCoordInBounds(s16 x, s16 y)
{
    return (u16)(x - 3) < 11 && (u16)y < ARRAY_COUNT(sIceRowVars) && sIceRowVars[y] != 0;
}

static void OpenIceStairs(u16 count)
{
    if (count >= 8)
    {
        MapGridSetMetatileIdAt(8 + MAP_OFFSET, 15 + MAP_OFFSET, ICE_STAIRS);
        MapGridSetMetatileIdAt(8 + MAP_OFFSET, 16 + MAP_OFFSET, ICE_STAIRS);
    }
    if (count >= 28)
    {
        MapGridSetMetatileIdAt(8 + MAP_OFFSET, 10 + MAP_OFFSET, ICE_STAIRS);
        MapGridSetMetatileIdAt(8 + MAP_OFFSET, 11 + MAP_OFFSET, ICE_STAIRS);
    }
    if (count >= 67)
    {
        MapGridSetMetatileIdAt(8 + MAP_OFFSET, 4 + MAP_OFFSET, ICE_STAIRS);
        MapGridSetMetatileIdAt(8 + MAP_OFFSET, 5 + MAP_OFFSET, ICE_STAIRS);
    }
}

void HoennSootopolisRestoreIce(void)
{
    static const u8 stairsY[] = {4, 5, 10, 11, 15, 16};
    s16 x, y;
    u16 count = VarGet(ICE_COUNT);

    // An old save in this room has no Hoenn ice counter yet.
    if (VarGet(VAR_TEMP_F) != ICE_STATE_MARKER || count > 132)
        HoennSootopolisResetIce();
    if (FlagGet(FLAG_HOENN_BADGE08_GET) && VarGet(ICE_COUNT) < 68)
        VarSet(ICE_COUNT, 68);
    // Continue restores a cached view before this callback. Rebuild the
    // stairs from puzzle progress, including old saves with all stairs open.
    for (y = 0; y < ARRAY_COUNT(stairsY); y++)
    {
        u16 entry = gMapHeader.mapLayout->map[stairsY[y] * gMapHeader.mapLayout->width + 8];
        MapGridSetMetatileEntryAt(8 + MAP_OFFSET, stairsY[y] + MAP_OFFSET, entry);
    }
    for (y = 0; y < ARRAY_COUNT(sIceRowVars); y++)
        for (x = 3; x <= 13; x++)
            if (IceCoordInBounds(x, y) && (VarGet(sIceRowVars[y]) & (1 << (x - 3))))
                MapGridSetMetatileIdAt(x + MAP_OFFSET, y + MAP_OFFSET, ICE_CRACKED);
    OpenIceStairs(VarGet(ICE_COUNT));
}

void HoennSootopolisIceStep(u8 taskId)
{
    s16 x, y;
    u16 behavior;
    s16 *data = gTasks[taskId].data;

    switch (data[1])
    {
    case 0:
        PlayerGetDestCoords(&data[2], &data[3]);
        data[1] = 1;
        break;
    case 1:
        PlayerGetDestCoords(&x, &y);
        if (x == data[2] && y == data[3])
            return;
        data[2] = x;
        data[3] = y;
        behavior = MapGridGetMetatileBehaviorAt(x, y);
        if (MetatileBehavior_IsThinIce(behavior))
        {
            VarSet(ICE_COUNT, VarGet(ICE_COUNT) + 1);
            data[1] = 2;
        }
        else if (MetatileBehavior_IsCrackedIce(behavior))
        {
            VarSet(ICE_COUNT, 0);
            data[1] = 3;
        }
        else
            return;
        data[4] = x;
        data[5] = y;
        data[6] = 4;
        break;
    case 2:
    case 3:
        if (data[6] != 0)
            data[6]--;
        else
        {
            x = data[4];
            y = data[5];
            if (data[1] == 2)
            {
                PlaySE(SE_ICE_CRACK);
                MapGridSetMetatileIdAt(x, y, ICE_CRACKED);
                x -= MAP_OFFSET;
                y -= MAP_OFFSET;
                if (IceCoordInBounds(x, y))
                    VarSet(sIceRowVars[y], VarGet(sIceRowVars[y]) | (1 << (x - 3)));
            }
            else
            {
                PlaySE(SE_ICE_BREAK);
                MapGridSetMetatileIdAt(x, y, ICE_BROKEN);
            }
            CurrentMapDrawMetatileAt(data[4], data[5]);
            data[1] = 1;
        }
        break;
    }
}

void HoennSkyPillarRestoreFloor(void)
{
    s16 x, y;
    const u16 *clean = NULL;
    u8 map = gSaveBlock1Ptr->location.mapNum;

    if (!IsSkyPillarFloor()
     && !(gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_SKY_PILLAR_TOP)
       && map == MAP_NUM(MAP_SKY_PILLAR_TOP)))
        return;
    if (!FlagGet(FLAG_HOENN_RAYQUAZA_AWAKENED))
    {
        if (map == MAP_NUM(MAP_SKY_PILLAR_1F)) clean = sSkyClean1;
        if (map == MAP_NUM(MAP_SKY_PILLAR_2F)) clean = sSkyClean2;
        if (map == MAP_NUM(MAP_SKY_PILLAR_3F)) clean = sSkyClean3;
        if (map == MAP_NUM(MAP_SKY_PILLAR_4F)) clean = sSkyClean4;
        if (map == MAP_NUM(MAP_SKY_PILLAR_5F)) clean = sSkyClean5;
        if (map == MAP_NUM(MAP_SKY_PILLAR_TOP)) clean = sSkyCleanTop;
        if (clean != NULL)
            for (y = 0; y < gMapHeader.mapLayout->height; y++)
                for (x = 0; x < gMapHeader.mapLayout->width; x++)
                    MapGridSetMetatileEntryAt(x + MAP_OFFSET, y + MAP_OFFSET, clean[y * gMapHeader.mapLayout->width + x]);
    }
    else if (map == MAP_NUM(MAP_SKY_PILLAR_4F))
    {
        // Replace the previous progression-only stair workaround with the
        // original late puzzle's rock, including a legacy cached map view.
        MapGridSetMetatileEntryAt(8 + MAP_OFFSET, 2 + MAP_OFFSET, gMapHeader.mapLayout->map[2 * gMapHeader.mapLayout->width + 8]);
    }
}

void HoennSkyPillarFloorStep(u8 taskId)
{
    s16 x, y, i;
    s16 *data = gTasks[taskId].data;

    PlayerGetDestCoords(&x, &y);
    for (i = 4; i <= 7; i += 3)
        if (data[i] != 0 && --data[i] == 0)
        {
            MapGridSetMetatileIdAt(data[i + 1], data[i + 2], SKY_HOLE);
            CurrentMapDrawMetatileAt(data[i + 1], data[i + 2]);
        }
    // Also fall when a rider stops on a floor that breaks beneath them.
    if (MapGridGetMetatileBehaviorAt(x, y) == MB_FALL_WARP)
        VarSet(VAR_TEMP_0, 0);
    if (data[1] == 0)
    {
        data[2] = x;
        data[3] = y;
        data[1] = 1;
        return;
    }
    if (x == data[2] && y == data[3])
        return;
    data[2] = x;
    data[3] = y;
    if (MapGridGetMetatileIdAt(x, y) == SKY_CRACKED)
    {
        if (!HoennSkyPillarBikeAtFullSpeed())
            VarSet(VAR_TEMP_0, 0);
        for (i = 4; i <= 7; i += 3)
            if (data[i] == 0)
            {
                // This callback runs before the player's coordinate update.
                // A true Mach tile takes four updates; the legacy Sky adapter
                // takes two. Do not collapse under a still-departing Mach rider.
                data[i] = Bike_GetMode() == BIKE_MODE_MACH ? 4 : 3;
                data[i + 1] = x;
                data[i + 2] = y;
                break;
            }
    }
}

void HoennSkyPillarBikeReset(void)
{
    if (IsSkyPillarFloor())
        gPlayerAvatar.bikeSpeed = 0;
}

bool8 HoennSkyPillarBikeAtFullSpeed(void)
{
    return IsSkyPillarFloor()
        && (gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_MACH_BIKE)
        && (Bike_GetMode() == BIKE_MODE_MACH
            ? gPlayerAvatar.bikeFrameCounter == 2
            : Bike_GetMode() == BIKE_MODE_LEGACY && gPlayerAvatar.bikeSpeed >= 3);
}

bool8 HoennSkyPillarBikeMove(u8 direction)
{
    if (Bike_GetMode() != BIKE_MODE_LEGACY || !IsSkyPillarFloor() || !(gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_MACH_BIKE))
        return FALSE;
    if (gPlayerAvatar.bikeSpeed == 0)
        PlayerWalkNormal(direction);
    else if (gPlayerAvatar.bikeSpeed == 1)
        PlayerWalkFast(direction);
    else
        PlayerRideBikeFastest(direction);
    if (gPlayerAvatar.bikeSpeed < 3)
        gPlayerAvatar.bikeSpeed++;
    return TRUE;
}

bool8 TryStartHoennSkyPillarHoleScript(u16 behavior)
{
    if (!IsSkyPillarFloor() || behavior != MB_FALL_WARP)
        return FALSE;
    if (gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SKY_PILLAR_2F))
        ScriptContext_SetupScript(SkyPillar_2F_TY_Fall);
    else if (gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SKY_PILLAR_4F))
        ScriptContext_SetupScript(SkyPillar_4F_TY_Fall);
    else
        return FALSE;
    return TRUE;
}

static bool8 IsSeafloorRockPuzzle(void)
{
    if (gSaveBlock1Ptr->location.mapGroup != MAP_GROUP(MAP_SEAFLOOR_CAVERN_ROOM1))
        return FALSE;
    switch (gSaveBlock1Ptr->location.mapNum)
    {
    case MAP_NUM(MAP_SEAFLOOR_CAVERN_ROOM1):
    case MAP_NUM(MAP_SEAFLOOR_CAVERN_ROOM2):
    case MAP_NUM(MAP_SEAFLOOR_CAVERN_ROOM3):
    case MAP_NUM(MAP_SEAFLOOR_CAVERN_ROOM5):
    case MAP_NUM(MAP_SEAFLOOR_CAVERN_ROOM8):
        return TRUE;
    }
    return FALSE;
}

void HoennSeafloorMarkPuzzleSave(void)
{
    u16 flag;

    if (IsSeafloorRockPuzzle())
    {
        if (VarGet(VAR_TEMP_F) != 0x5346)
            for (flag = FLAG_TEMP_11; flag <= FLAG_TEMP_1C; flag++)
                FlagClear(flag);
        VarSet(VAR_TEMP_F, 0x5346);
    }
}

bool8 HoennSeafloorHasPuzzleSave(void)
{
    return IsSeafloorRockPuzzle() && VarGet(VAR_TEMP_F) == 0x5346;
}
