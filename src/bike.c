#include "global.h"
#include "bike.h"
#include "hoenn_puzzles.h"
#include "field_player_avatar.h"
#include "metatile_behavior.h"
#include "event_object_movement.h"
#include "fieldmap.h"
#include "field_camera.h"
#include "overworld.h"
#include "constants/map_types.h"
#include "constants/songs.h"
#include "event_data.h"
#include "quest_log.h"
#include "sound.h"
#include "task.h"
#include "constants/vars.h"

struct BikeHistoryInputInfo
{
    u32 dirHistoryMatch; // the direction you need to press
    u32 abStartSelectHistoryMatch; // the button you need to press
    u32 dirHistoryMask; // mask applied so that way only the recent nybble (the recent input) is checked
    u32 abStartSelectHistoryMask; // mask applied so that way only the recent nybble (the recent input) is checked
    const u8 *dirTimerHistoryList; // list of timers to check for direction before the button+dir combination can be verified.
    const u8 *abStartSelectHistoryList; // list of timers to check for buttons before the button+dir combination can be verified.
    u32 direction; // direction to jump
};

static void MovePlayerOnMachBike(u8, u16, u16);
static u8 GetMachBikeTransition(u8 *);
static void MachBikeTransition_FaceDirection(u8);
static void MachBikeTransition_TurnDirection(u8);
static void MachBikeTransition_TrySpeedUp(u8);
static void MachBikeTransition_TrySlowDown(u8);
static void MovePlayerOnAcroBike(u8, u16, u16);
static u8 CheckMovementInputAcroBike(u8 *, u16, u16);
static u8 AcroBikeHandleInputNormal(u8 *, u16, u16);
static u8 AcroBikeHandleInputTurning(u8 *, u16, u16);
static u8 AcroBikeHandleInputWheelieStanding(u8 *, u16, u16);
static u8 AcroBikeHandleInputBunnyHop(u8 *, u16, u16);
static u8 AcroBikeHandleInputWheelieMoving(u8 *, u16, u16);
static u8 AcroBikeHandleInputSidewaysJump(u8 *, u16, u16);
static u8 AcroBikeHandleInputTurnJump(u8 *, u16, u16);
static void AcroBikeTransition_FaceDirection(u8);
static void AcroBikeTransition_TurnDirection(u8);
static void AcroBikeTransition_Moving(u8);
static void AcroBikeTransition_NormalToWheelie(u8);
static void AcroBikeTransition_WheelieToNormal(u8);
static void AcroBikeTransition_WheelieIdle(u8);
static void AcroBikeTransition_WheelieHoppingStanding(u8);
static void AcroBikeTransition_WheelieHoppingMoving(u8);
static void AcroBikeTransition_SideJump(u8);
static void AcroBikeTransition_TurnJump(u8);
static void AcroBikeTransition_WheelieMoving(u8);
static void AcroBikeTransition_WheelieRisingMoving(u8);
static void AcroBikeTransition_WheelieLoweringMoving(u8);
static void AcroBike_TryHistoryUpdate(u16, u16);
static u8 AcroBike_GetJumpDirection(void);
static void Bike_UpdateDirTimerHistory(u8);
static void Bike_UpdateABStartSelectHistory(u8);
static u8 Bike_DPadToDirection(u16);
static bool8 WillPlayerCollideWithCollision(u8, u8);

static void Task_BikeInputContext(u8 taskId);
static u8 *GetBikeInputTimers(bool8 create);
static bool8 HasPlayerInputTakenLongerThanList(const u8 *, const u8 *);
static void ResetBikeInputHistory(u32 directionHistory, u32 buttonHistory);
static bool8 BikeCollisionHandledElsewhere(u8 collision);
static void BikeMoveWithSpeed(void (*move)(u8), u8 direction, u8 collision);
static bool8 Bike_TryCyclingRoadMovement(u8 direction, u16 heldKeys);

static void (*const sMachBikeTransitions[])(u8) =
{
    MachBikeTransition_FaceDirection, // Face vs Turn: Face has no anim while Turn does. Turn checks for collision because if you turn right as opposed to face right, if there is a wall there, turn will make a bonk sound effect while face will not.
    MachBikeTransition_TurnDirection,
    MachBikeTransition_TrySpeedUp,
    MachBikeTransition_TrySlowDown,
};

// bikeFrameCounter is input which is represented by sMachBikeSpeeds in order
static void (*const sMachBikeSpeedCallbacks[])(u8) =
{
    PlayerWalkNormal,
    PlayerWalkFast,
    PlayerWalkFaster,
};

static void (*const sAcroBikeTransitions[])(u8) =
{
    AcroBikeTransition_FaceDirection,
    AcroBikeTransition_TurnDirection,
    AcroBikeTransition_Moving,
    AcroBikeTransition_NormalToWheelie,
    AcroBikeTransition_WheelieToNormal,
    AcroBikeTransition_WheelieIdle,
    AcroBikeTransition_WheelieHoppingStanding,
    AcroBikeTransition_WheelieHoppingMoving,
    AcroBikeTransition_SideJump,
    AcroBikeTransition_TurnJump,
    AcroBikeTransition_WheelieMoving,
    AcroBikeTransition_WheelieRisingMoving,
    AcroBikeTransition_WheelieLoweringMoving,
};

static u8 (*const sAcroBikeInputHandlers[])(u8 *, u16, u16) =
{
    AcroBikeHandleInputNormal,
    AcroBikeHandleInputTurning,
    AcroBikeHandleInputWheelieStanding,
    AcroBikeHandleInputBunnyHop,
    AcroBikeHandleInputWheelieMoving,
    AcroBikeHandleInputSidewaysJump,
    AcroBikeHandleInputTurnJump,
};

// used with bikeFrameCounter from mach bike

// this is a list of timers to compare against later, terminated with 0. the only timer being compared against is 4 frames in this list.
static const u8 sAcroBikeJumpTimerList[] = {4, 0};

// this is a list of history inputs to do in order to do the check to retrieve a jump direction for acro bike. it seems to be an extensible list, so its possible that Game Freak may have intended for the Acro Bike to have more complex tricks at some point. The final list only has the acro jump.
static const struct BikeHistoryInputInfo sAcroBikeTricksList[] =
{
    // the 0xF is a mask performed with each byte of the array in order to perform the check on only the last entry of the history list, otherwise the check wouldn't work as there can be 0xF0 as opposed to 0x0F.
    {DIR_SOUTH, B_BUTTON, 0xF, 0xF, sAcroBikeJumpTimerList, sAcroBikeJumpTimerList, DIR_SOUTH},
    {DIR_NORTH, B_BUTTON, 0xF, 0xF, sAcroBikeJumpTimerList, sAcroBikeJumpTimerList, DIR_NORTH},
    {DIR_WEST, B_BUTTON, 0xF, 0xF, sAcroBikeJumpTimerList, sAcroBikeJumpTimerList, DIR_WEST},
    {DIR_EAST, B_BUTTON, 0xF, 0xF, sAcroBikeJumpTimerList, sAcroBikeJumpTimerList, DIR_EAST},
};


static u8 GetBikeTransitionId(u8 *, u16, u16);
static void Bike_SetBikeStill(void);
static u8 CanBikeFaceDirectionOnRail(u8 direction, u8 metatileBehavior);
static u8 GetBikeCollision(u8);
static u8 GetBikeCollisionAt(struct ObjectEvent *playerObjEvent, s16 x, s16 y, u8 direction, u8 metatileBehavior);
static bool8 MetatileBehaviorForbidsBiking(u8);
static void BikeTransition_FaceDirection(u8);
static void BikeTransition_TurnDirection(u8);
static void BikeTransition_MoveDirection(u8);
static void BikeTransition_Downhill(u8);
static void BikeTransition_Uphill(u8);
static u8 BikeInputHandler_Normal(u8 *, u16, u16);
static u8 BikeInputHandler_Turning(u8 *, u16, u16);
static u8 BikeInputHandler_Slope(u8 *, u16, u16);

static void (*const sBikeTransitions[])(u8) =
{
    [BIKE_TRANS_FACE_DIRECTION] = BikeTransition_FaceDirection,
    [BIKE_TRANS_TURNING]        = BikeTransition_TurnDirection,
    [BIKE_TRANS_MOVE]           = BikeTransition_MoveDirection,
    [BIKE_TRANS_DOWNHILL]       = BikeTransition_Downhill,
    [BIKE_TRANS_UPHILL]         = BikeTransition_Uphill,
};

static u8 (*const sBikeInputHandlers[])(u8 *, u16, u16) =
{
    [BIKE_STATE_NORMAL]  = BikeInputHandler_Normal,
    [BIKE_STATE_TURNING] = BikeInputHandler_Turning,
    [BIKE_STATE_SLOPE]   = BikeInputHandler_Slope,
};

void MovePlayerOnBike(u8 direction, u16 newKeys, u16 heldKeys)
{
    if (Bike_TryCyclingRoadMovement(direction, heldKeys))
        return;
    if (gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_ACRO_BIKE)
        MovePlayerOnAcroBike(direction, newKeys, heldKeys);
    else if (Bike_GetMode() == BIKE_MODE_MACH)
        MovePlayerOnMachBike(direction, newKeys, heldKeys);
    else
        sBikeTransitions[GetBikeTransitionId(&direction, newKeys, heldKeys)](direction);
}

static u8 GetBikeTransitionId(u8 *direction, u16 newKeys, u16 heldKeys)
{
    return sBikeInputHandlers[gPlayerAvatar.acroBikeState](direction, newKeys, heldKeys);
}

static u8 BikeInputHandler_Normal(u8 *direction_p, u16 newKeys, u16 heldKeys)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];
    u8 direction = GetPlayerMovementDirection();

    gPlayerAvatar.bikeFrameCounter = 0;
    if (MetatileBehavior_IsCyclingRoadPullDownTile(playerObjEvent->currentMetatileBehavior) == TRUE)
    {
        if (!JOY_HELD(B_BUTTON))
        {
            gPlayerAvatar.acroBikeState = BIKE_STATE_SLOPE;
            gPlayerAvatar.runningState = MOVING;
            if (*direction_p < DIR_NORTH)
                return BIKE_TRANS_DOWNHILL;
            else
                return BIKE_TRANS_UPHILL;
        }
        else
        {
            if (*direction_p != DIR_NONE)
            {
                gPlayerAvatar.acroBikeState = BIKE_STATE_SLOPE;
                gPlayerAvatar.runningState = MOVING;
                return BIKE_TRANS_UPHILL;
            }
        }
    }
    if (*direction_p == DIR_NONE)
    {
        *direction_p = direction;
        gPlayerAvatar.runningState = NOT_MOVING;
        return BIKE_TRANS_FACE_DIRECTION;
    }
    else
    {
        if (*direction_p != direction && gPlayerAvatar.runningState != MOVING)
        {
            gPlayerAvatar.acroBikeState = BIKE_STATE_TURNING;
            gPlayerAvatar.newDirBackup = *direction_p;
            gPlayerAvatar.runningState = NOT_MOVING;
            return GetBikeTransitionId(direction_p, newKeys, heldKeys);
        }
        else
        {
            gPlayerAvatar.runningState = MOVING;
            return BIKE_TRANS_MOVE;
        }
    }
}

static u8 BikeInputHandler_Turning(u8 *direction_p, u16 newKeys, u16 heldKeys)
{
    *direction_p = gPlayerAvatar.newDirBackup;
    gPlayerAvatar.runningState = TURN_DIRECTION;
    gPlayerAvatar.acroBikeState = BIKE_STATE_NORMAL;
    Bike_SetBikeStill();
    return BIKE_TRANS_TURNING;
}

static u8 BikeInputHandler_Slope(u8 *direction_p, u16 newKeys, u16 heldKeys)
{
    u8 direction = GetPlayerMovementDirection();
    u8 playerObjEventId = gPlayerAvatar.objectEventId;
    if (MetatileBehavior_IsCyclingRoadPullDownTile(playerObjEventId[gObjectEvents].currentMetatileBehavior) == TRUE)
    {
        if (*direction_p != direction)
        {
            gPlayerAvatar.acroBikeState = BIKE_STATE_TURNING;
            gPlayerAvatar.newDirBackup = *direction_p;
            gPlayerAvatar.runningState = NOT_MOVING;
            return GetBikeTransitionId(direction_p, newKeys, heldKeys);
        }
        else
        {
            gPlayerAvatar.runningState = MOVING;
            gPlayerAvatar.acroBikeState = BIKE_STATE_SLOPE;
            if (*direction_p < DIR_NORTH)
                return BIKE_TRANS_DOWNHILL;
            else
                return BIKE_TRANS_UPHILL;
        }
    }
    gPlayerAvatar.acroBikeState = BIKE_STATE_NORMAL;
    if (*direction_p == DIR_NONE)
    {
        *direction_p = direction;
        gPlayerAvatar.runningState = NOT_MOVING;
        return BIKE_TRANS_FACE_DIRECTION;
    }
    else
    {
        gPlayerAvatar.runningState = MOVING;
        return BIKE_TRANS_MOVE;
    }
}

static void BikeTransition_FaceDirection(u8 direction)
{
    HoennSkyPillarBikeReset();
    PlayerFaceDirection(direction);
}

static void BikeTransition_TurnDirection(u8 direction)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (!CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior))
        direction = playerObjEvent->movementDirection;
    HoennSkyPillarBikeReset();
    PlayerFaceDirection(direction);
}

static void BikeTransition_MoveDirection(u8 direction)
{
    struct ObjectEvent *playerObjEvent;
    
    playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];
    if (!CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior))
    {
        BikeTransition_FaceDirection(playerObjEvent->movementDirection);
    }
    else
    {
        u8 collision = GetBikeCollision(direction);

        if (collision > COLLISION_NONE && collision <= COLLISION_ISOLATED_HORIZONTAL_RAIL)
        {
            HoennSkyPillarBikeReset();
            if (collision == COLLISION_LEDGE_JUMP)
                PlayerJumpLedge(direction);
            else if (collision != COLLISION_STOP_SURFING
                  && collision != COLLISION_LEDGE_JUMP
                  && collision != COLLISION_PUSHED_BOULDER
                  && collision != COLLISION_DIRECTIONAL_STAIR_WARP)
                PlayerOnBikeCollide(direction);
        }
        else
        {
            
            if (collision == COLLISION_COUNT)
                PlayerWalkFast(direction);
            else if (PlayerIsMovingOnRockStairs(direction))
                PlayerWalkFast(direction);
            else if (!HoennSkyPillarBikeMove(direction))
                PlayerRideWaterCurrent(direction);
        }
    }
}

static void BikeTransition_Downhill(u8 v)
{
    u8 collision = GetBikeCollision(DIR_SOUTH);

    if (collision == COLLISION_NONE)
        PlayerWalkFaster(DIR_SOUTH);
    else if (collision == COLLISION_LEDGE_JUMP)
        PlayerJumpLedge(DIR_SOUTH);
}

static void BikeTransition_Uphill(u8 direction)
{
    if (GetBikeCollision(direction) == COLLISION_NONE)
        PlayerWalkNormal(direction);
}

static bool8 Bike_TryCyclingRoadMovement(u8 direction, u16 heldKeys)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];
    u8 *buttonTimers;

    if (Bike_GetMode() == BIKE_MODE_LEGACY
     || !MetatileBehavior_IsCyclingRoadPullDownTile(playerObjEvent->currentMetatileBehavior))
        return FALSE;

    // The FRLG slope is terrain policy, separate from the Acro state machine.
    gPlayerAvatar.acroBikeState = ACRO_STATE_NORMAL;
    gPlayerAvatar.newDirBackup = DIR_NONE;
    Bike_SetBikeStill();
    ResetBikeInputHistory(0, 0);
    buttonTimers = GetBikeInputTimers(FALSE);
    if (buttonTimers != NULL)
        memset(buttonTimers, 0, 8);

    if ((heldKeys & B_BUTTON) && direction == DIR_NONE)
    {
        gPlayerAvatar.runningState = NOT_MOVING;
        PlayerFaceDirection(GetPlayerMovementDirection());
    }
    else
    {
        gPlayerAvatar.runningState = MOVING;
        if (!(heldKeys & B_BUTTON) && direction < DIR_NORTH)
            BikeTransition_Downhill(direction);
        else
            BikeTransition_Uphill(direction);
        // A blocked rider must not retain a wheelie pose from the approach.
        PlayerFaceDirection(GetPlayerMovementDirection());
    }
    return TRUE;
}

static u8 GetBikeCollision(u8 direction)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];
    s16 x, y;
    u8 metatileBehavior;

    x = playerObjEvent->currentCoords.x;
    y = playerObjEvent->currentCoords.y;
    MoveCoords(direction, &x, &y);
    metatileBehavior = MapGridGetMetatileBehaviorAt(x, y);
    return GetBikeCollisionAt(playerObjEvent, x, y, direction, metatileBehavior);
}

static u8 GetBikeCollisionAt(struct ObjectEvent *playerObjEvent, s16 x, s16 y, u8 direction, u8 metatileBehavior)
{
    u8 retVal = CheckForObjectEventCollision(playerObjEvent, x, y, direction, metatileBehavior);

    if (retVal <= COLLISION_OBJECT_EVENT)
    {
        bool8 isCrackedIce = MetatileBehavior_IsCrackedIce(metatileBehavior);
        if (isCrackedIce == TRUE)
            return COLLISION_COUNT;
        if (retVal == COLLISION_NONE && MetatileBehaviorForbidsBiking(metatileBehavior))
            retVal = COLLISION_IMPASSABLE;
    }
    return retVal;
}

bool8 RS_IsRunningDisallowed(u8 r0)
{
    if (MetatileBehaviorForbidsBiking(r0))
        return TRUE;
    if (gMapHeader.mapType != MAP_TYPE_INDOOR)
        return FALSE;
    else
        return TRUE;
}

bool32 IsRunningDisallowed(u8 metatileBehavior)
{
    if (!gMapHeader.allowRunning)
        return TRUE;
    if (MetatileBehaviorForbidsBiking(metatileBehavior) != TRUE)
        return FALSE;
    else
        return TRUE;
}

static bool8 MetatileBehaviorForbidsBiking(u8 metatileBehavior)
{
    if (MetatileBehavior_IsRunningDisallowed(metatileBehavior))
        return TRUE;
    if (!MetatileBehavior_IsFortreeBridge(metatileBehavior))
        return FALSE;
    if (PlayerGetElevation() & 1)
        return FALSE;
    return TRUE;
}

static bool8 CanBikeFaceDirectionOnRail(u8 direction, u8 metatileBehavior)
{
    if (direction == DIR_EAST || direction == DIR_WEST)
    {
        if (MetatileBehavior_IsIsolatedVerticalRail(metatileBehavior) || MetatileBehavior_IsVerticalRail(metatileBehavior))
            return FALSE;
    }
    else
    {
        if (MetatileBehavior_IsIsolatedHorizontalRail(metatileBehavior) || MetatileBehavior_IsHorizontalRail(metatileBehavior))
            return FALSE;
    }
    return TRUE;
}

bool8 IsBikingDisallowedByPlayer(void)
{
    s16 x, y;
    u8 metatileBehavior;

    if (!(gPlayerAvatar.flags & (PLAYER_AVATAR_FLAG_UNDERWATER | PLAYER_AVATAR_FLAG_SURFING)))
    {
        PlayerGetDestCoords(&x, &y);
        metatileBehavior = MapGridGetMetatileBehaviorAt(x, y);
        if (!MetatileBehaviorForbidsBiking(metatileBehavior))
            return FALSE;
    }
    return TRUE;
}

bool8 IsPlayerNotUsingAcroBikeOnBumpySlope(void)
{
    if (TestPlayerAvatarFlags(PLAYER_AVATAR_FLAG_ACRO_BIKE))
    {
        if (MetatileBehavior_IsBumpySlope(gObjectEvents[gPlayerAvatar.objectEventId].currentMetatileBehavior))
            return FALSE;
    }
    return TRUE;
}

void GetOnOffBike(u8 flags)
{
    gBikeCameraAheadPanback = FALSE;
    if (gPlayerAvatar.flags & (PLAYER_AVATAR_FLAG_MACH_BIKE | PLAYER_AVATAR_FLAG_ACRO_BIKE))
    {
        SetPlayerAvatarTransitionFlags(PLAYER_AVATAR_FLAG_ON_FOOT);
        Overworld_ClearSavedMusic();
        Overworld_PlaySpecialMapMusic();
    }
    else
    {
        SetPlayerAvatarTransitionFlags(flags);
        if (Overworld_MusicCanOverrideMapMusic(MUS_CYCLING))
        {
            Overworld_SetSavedMusic(MUS_CYCLING);
            Overworld_ChangeMusicTo(MUS_CYCLING);
        }
    }
}

void BikeClearState(u32 directionHistory, u32 abStartSelectHistory)
{
    Bike_ResetTransientState();
    ResetBikeInputHistory(directionHistory, abStartSelectHistory);
    gPlayerAvatar.lastSpinTile = 0;
}

void Bike_UpdateBikeCounterSpeed(u8 counter)
{
    gPlayerAvatar.bikeFrameCounter = counter;
    gPlayerAvatar.bikeSpeed = counter + (gPlayerAvatar.bikeFrameCounter >> 1);
}

static void Bike_SetBikeStill(void)
{
    gPlayerAvatar.bikeFrameCounter = 0;
    gPlayerAvatar.bikeSpeed = PLAYER_SPEED_STANDING;
}

s16 GetPlayerSpeed(void)
{
    s16 machBikeSpeeds[] = { PLAYER_SPEED_NORMAL, PLAYER_SPEED_FAST, PLAYER_SPEED_FASTEST };

    if (Bike_GetMode() == BIKE_MODE_LEGACY && HoennSkyPillarBikeAtFullSpeed())
        return PLAYER_SPEED_FASTEST;
    if (gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_MACH_BIKE)
        return machBikeSpeeds[gPlayerAvatar.bikeFrameCounter < NELEMS(machBikeSpeeds) ? gPlayerAvatar.bikeFrameCounter : 0];
    else if (gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_ACRO_BIKE)
        return PLAYER_SPEED_FASTER;
    else if (gPlayerAvatar.flags & (PLAYER_AVATAR_FLAG_SURFING | PLAYER_AVATAR_FLAG_UNDERWATER | PLAYER_AVATAR_FLAG_DASH))
        return PLAYER_SPEED_FAST;
    else
        return PLAYER_SPEED_NORMAL;
}

void Bike_HandleBumpySlopeJump(void)
{
    s16 x, y;
    u8 tileBehavior;

    if (gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_ACRO_BIKE)
    {
        PlayerGetDestCoords(&x, &y);
        tileBehavior = MapGridGetMetatileBehaviorAt(x, y);
        if (MetatileBehavior_IsBumpySlope(tileBehavior))
        {
            gPlayerAvatar.acroBikeState = ACRO_STATE_WHEELIE_STANDING;
            PlayerUseAcroBikeOnBumpySlope(GetPlayerMovementDirection());
        }
    }
}


u8 Bike_GetMode(void)
{
    u16 mode = VarGet(VAR_HOENN_BIKE_MODE);

    if (mode > BIKE_MODE_ACRO)
        return BIKE_MODE_LEGACY;
    return mode;
}

void Bike_SetMode(u8 mode)
{
    if (gQuestLogState == QL_STATE_PLAYBACK || gQuestLogState == QL_STATE_PLAYBACK_LAST)
        return;
    if (mode > BIKE_MODE_ACRO)
        mode = BIKE_MODE_LEGACY;
    if (Bike_GetMode() != mode)
        Bike_ResetTransientState();
    VarSet(VAR_HOENN_BIKE_MODE, mode);
}

static void Task_BikeInputContext(u8 taskId)
{
    if (!(gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_ACRO_BIKE))
        DestroyTask(taskId);
}

static void ResetBikeInputHistory(u32 directionHistory, u32 buttonHistory)
{
    gPlayerAvatar.directionHistory = directionHistory;
    gPlayerAvatar.abStartSelectHistory = buttonHistory;
    memset(gPlayerAvatar.dirTimerHistory, 0, sizeof(gPlayerAvatar.dirTimerHistory));
}

static u8 *GetBikeInputTimers(bool8 create)
{
    u8 taskId = FindTaskIdByFunc(Task_BikeInputContext);
    u8 i;

    if (taskId == TASK_NONE && create)
    {
        ResetBikeInputHistory(0, 0);
        for (i = 0; i < NUM_TASKS; i++)
        {
            if (!gTasks[i].isActive)
                break;
        }
        if (i == NUM_TASKS)
            return NULL;
        taskId = CreateTask(Task_BikeInputContext, 0xFF);
    }
    if (taskId == TASK_NONE)
        return NULL;
    return (u8 *)gTasks[taskId].data;
}

void Bike_ResetTransientState(void)
{
    u8 taskId = FindTaskIdByFunc(Task_BikeInputContext);

    if (taskId != TASK_NONE)
        DestroyTask(taskId);
    gPlayerAvatar.acroBikeState = ACRO_STATE_NORMAL;
    gPlayerAvatar.newDirBackup = DIR_NONE;
    gPlayerAvatar.bikeFrameCounter = 0;
    gPlayerAvatar.bikeSpeed = PLAYER_SPEED_STANDING;
    ResetBikeInputHistory(0, 0);
}

static bool8 BikeCollisionHandledElsewhere(u8 collision)
{
    return collision == COLLISION_STOP_SURFING
        || collision == COLLISION_LEDGE_JUMP
        || collision == COLLISION_PUSHED_BOULDER
        || collision == COLLISION_DIRECTIONAL_STAIR_WARP;
}

static void BikeMoveWithSpeed(void (*move)(u8), u8 direction, u8 collision)
{
    if (collision == COLLISION_COUNT || PlayerIsMovingOnRockStairs(direction))
        PlayerWalkFast(direction);
    else
        move(direction);
}

static void MovePlayerOnMachBike(u8 direction, u16 newKeys, u16 heldKeys)
{
    if (gPlayerAvatar.bikeFrameCounter >= NELEMS(sMachBikeSpeedCallbacks))
        Bike_SetBikeStill();
    sMachBikeTransitions[GetMachBikeTransition(&direction)](direction);
}

static u8 GetMachBikeTransition(u8 *dirTraveling)
{
    // if the dir updated before this function, get the relevent new direction to check later.
    u8 direction = GetPlayerMovementDirection();

    // is the player standing still?
    if (*dirTraveling == 0)
    {
        *dirTraveling = direction; // update the direction, since below we either faced a direction or we started moving.
        if (gPlayerAvatar.bikeSpeed == PLAYER_SPEED_STANDING)
        {
            gPlayerAvatar.runningState = NOT_MOVING;
            return MACH_TRANS_FACE_DIRECTION;
        }
        gPlayerAvatar.runningState = MOVING;
        return MACH_TRANS_START_MOVING;
    }

    // we need to check if the last traveled direction changed from the new direction as well as ensuring that we dont update the state while the player is moving: see the else check.
    if (*dirTraveling != direction && gPlayerAvatar.runningState != MOVING)
    {
        if (gPlayerAvatar.bikeSpeed != PLAYER_SPEED_STANDING)
        {
            *dirTraveling = direction; // implement the new direction
            gPlayerAvatar.runningState = MOVING;
            return MACH_TRANS_START_MOVING;
        }
        // if you didnt start moving but your dir was different, do a turn direction instead.
        gPlayerAvatar.runningState = TURN_DIRECTION;
        return MACH_TRANS_TURN_DIRECTION;
    }
    else // the player is either going in the current direction and hasnt changed or their state is currently moving.
    {
        gPlayerAvatar.runningState = MOVING;
        return MACH_TRANS_KEEP_MOVING;
    }
}

static void MachBikeTransition_FaceDirection(u8 direction)
{
    PlayerFaceDirection(direction);
    Bike_SetBikeStill();
}

static void MachBikeTransition_TurnDirection(u8 direction)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior))
    {
        PlayerTurnInPlace(direction);
        Bike_SetBikeStill();
    }
    else
    {
        MachBikeTransition_FaceDirection(playerObjEvent->facingDirection);
    }
}

static void MachBikeTransition_TrySpeedUp(u8 direction)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];
    u8 collision;

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior) == FALSE)
    {
        // we cannot go forward, so either slow down or, if we are stopped, idle face direction.
        if (gPlayerAvatar.bikeSpeed)
            MachBikeTransition_TrySlowDown(playerObjEvent->movementDirection);
        else
            MachBikeTransition_FaceDirection(playerObjEvent->movementDirection);
    }
    else
    {
        collision = GetBikeCollision(direction);
        if (collision > 0 && collision < COLLISION_VERTICAL_RAIL)
        {
            // we hit a solid object, but check to see if its a ledge and then jump.
            if (collision == COLLISION_LEDGE_JUMP)
            {
                PlayerJumpLedge(direction);
            }
            else
            {
                // we hit a solid object that is not a ledge, so perform the collision.
                Bike_SetBikeStill();
                if (!BikeCollisionHandledElsewhere(collision))
                    PlayerOnBikeCollide(direction);
            }
        }
        else
        {
            // we did not hit anything that can slow us down, so perform the advancement callback depending on the bikeFrameCounter and try to increase the mach bike's speed.
            BikeMoveWithSpeed(sMachBikeSpeedCallbacks[gPlayerAvatar.bikeFrameCounter], direction, collision);
            gPlayerAvatar.bikeSpeed = gPlayerAvatar.bikeFrameCounter + (gPlayerAvatar.bikeFrameCounter >> 1); // same as dividing by 2, but compiler is insistent on >> 1
            if (gPlayerAvatar.bikeFrameCounter < 2) // do not go faster than the last element in the mach bike array
                gPlayerAvatar.bikeFrameCounter++;
        }
    }
}

static void MachBikeTransition_TrySlowDown(u8 direction)
{
    u8 collision;

    if (gPlayerAvatar.bikeSpeed != PLAYER_SPEED_STANDING)
        gPlayerAvatar.bikeFrameCounter = --gPlayerAvatar.bikeSpeed;

    collision = GetBikeCollision(direction);

    if (collision > 0 && collision < COLLISION_VERTICAL_RAIL)
    {
        if (collision == COLLISION_LEDGE_JUMP)
        {
            PlayerJumpLedge(direction);
        }
        else
        {
            Bike_SetBikeStill();
            if (!BikeCollisionHandledElsewhere(collision))
                PlayerOnBikeCollide(direction);
        }
    }
    else
    {
        BikeMoveWithSpeed(sMachBikeSpeedCallbacks[gPlayerAvatar.bikeFrameCounter], direction, collision);
    }
}

static void MovePlayerOnAcroBike(u8 newDirection, u16 newKeys, u16 heldKeys)
{
    sAcroBikeTransitions[CheckMovementInputAcroBike(&newDirection, newKeys, heldKeys)](newDirection);
}

static u8 CheckMovementInputAcroBike(u8 *newDirection, u16 newKeys, u16 heldKeys)
{
    if (gPlayerAvatar.acroBikeState >= NELEMS(sAcroBikeInputHandlers))
        Bike_ResetTransientState();
    return sAcroBikeInputHandlers[gPlayerAvatar.acroBikeState](newDirection, newKeys, heldKeys);
}

static u8 AcroBikeHandleInputNormal(u8 *newDirection, u16 newKeys, u16 heldKeys)
{
    u8 direction = GetPlayerMovementDirection();

    gPlayerAvatar.bikeFrameCounter = 0;
    if (*newDirection == DIR_NONE)
    {
        if (newKeys & B_BUTTON)
        {
            //We're standing still with the B button held.
            //Do a wheelie.
            *newDirection = direction;
            gPlayerAvatar.runningState = NOT_MOVING;
            gPlayerAvatar.acroBikeState = ACRO_STATE_WHEELIE_STANDING;
            return ACRO_TRANS_NORMAL_TO_WHEELIE;
        }
        else
        {
            *newDirection = direction;
            gPlayerAvatar.runningState = NOT_MOVING;
            return ACRO_TRANS_FACE_DIRECTION;
        }
    }
    if (*newDirection == direction && (heldKeys & B_BUTTON) && gPlayerAvatar.bikeSpeed == PLAYER_SPEED_STANDING)
    {
        gPlayerAvatar.bikeSpeed++;
        gPlayerAvatar.acroBikeState = ACRO_STATE_WHEELIE_MOVING;
        return ACRO_TRANS_WHEELIE_RISING_MOVING;
    }
    if (*newDirection != direction && gPlayerAvatar.runningState != MOVING)
    {
        gPlayerAvatar.acroBikeState = ACRO_STATE_TURNING;
        gPlayerAvatar.newDirBackup = *newDirection;
        gPlayerAvatar.runningState = NOT_MOVING;
        return CheckMovementInputAcroBike(newDirection, newKeys, heldKeys);
    }
    gPlayerAvatar.runningState = MOVING;
    return ACRO_TRANS_MOVING;
}

static u8 AcroBikeHandleInputTurning(u8 *newDirection, u16 newKeys, u16 heldKeys)
{
    u8 direction;

    *newDirection = gPlayerAvatar.newDirBackup;
    gPlayerAvatar.bikeFrameCounter++;

    // Wait 6 frames before actually changing direction
    if (gPlayerAvatar.bikeFrameCounter > 6) // ... because it takes 6 frames to advance 1 tile.
    {
        gPlayerAvatar.runningState = TURN_DIRECTION;
        gPlayerAvatar.acroBikeState = ACRO_STATE_NORMAL;
        Bike_SetBikeStill();
        return ACRO_TRANS_TURN_DIRECTION;
    }
    direction = GetPlayerMovementDirection();
    if (*newDirection == AcroBike_GetJumpDirection())
    {
        Bike_SetBikeStill(); // Bike_SetBikeStill sets speed to standing, but the next line immediately overrides it. could have just reset acroBikeState to 0 here instead of wasting a jump.
        gPlayerAvatar.bikeSpeed = PLAYER_SPEED_NORMAL;
        if (*newDirection == GetOppositeDirection(direction))
        {
            // do a turn jump.
            // no need to update runningState, didnt move.
            gPlayerAvatar.acroBikeState = ACRO_STATE_TURN_JUMP;
            return ACRO_TRANS_TURN_JUMP;
        }
        else
        {
            // do a sideways jump.
            gPlayerAvatar.runningState = MOVING; // we need to move, set state to moving.
            gPlayerAvatar.acroBikeState = ACRO_STATE_SIDE_JUMP;
            return ACRO_TRANS_SIDE_JUMP;
        }
    }
    *newDirection = direction;
    return ACRO_TRANS_FACE_DIRECTION;
}

static u8 AcroBikeHandleInputWheelieStanding(u8 *newDirection, u16 newKeys, u16 heldKeys)
{
    u8 direction;
    struct ObjectEvent *playerObjEvent;

    direction = GetPlayerMovementDirection();
    playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];
    gPlayerAvatar.runningState = NOT_MOVING;

    if (heldKeys & B_BUTTON)
    {
        gPlayerAvatar.bikeFrameCounter++;
    }
    else
    {
        // B button was released.
        gPlayerAvatar.bikeFrameCounter = 0;
        if (!MetatileBehavior_IsBumpySlope(playerObjEvent->currentMetatileBehavior))
        {
            // Go back to normal on flat ground
            *newDirection = direction;
            gPlayerAvatar.acroBikeState = ACRO_STATE_NORMAL;
            Bike_SetBikeStill();
            return ACRO_TRANS_WHEELIE_TO_NORMAL;
        }
    }
    if (gPlayerAvatar.bikeFrameCounter >= 40)
    {
        *newDirection = direction;
        gPlayerAvatar.acroBikeState = ACRO_STATE_BUNNY_HOP;
        Bike_SetBikeStill();
        return ACRO_TRANS_WHEELIE_HOPPING_STANDING;
    }
    if (*newDirection == direction)
    {
        gPlayerAvatar.runningState = MOVING;
        gPlayerAvatar.acroBikeState = ACRO_STATE_WHEELIE_MOVING;
        Bike_SetBikeStill();
        return ACRO_TRANS_WHEELIE_MOVING;
    }
    if (*newDirection == 0)
    {
        *newDirection = direction;
        return ACRO_TRANS_WHEELIE_IDLE;
    }
    gPlayerAvatar.runningState = TURN_DIRECTION;
    return ACRO_TRANS_WHEELIE_IDLE;
}

static u8 AcroBikeHandleInputBunnyHop(u8 *newDirection, u16 newKeys, u16 heldKeys)
{
    u8 direction;
    struct ObjectEvent *playerObjEvent;

    direction = GetPlayerMovementDirection();
    playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];
    if (!(heldKeys & B_BUTTON))
    {
        // B button was released
        Bike_SetBikeStill();
        if (MetatileBehavior_IsBumpySlope(playerObjEvent->currentMetatileBehavior))
        {
            // even though B was released, dont undo the wheelie on the bumpy slope.
            gPlayerAvatar.acroBikeState = ACRO_STATE_WHEELIE_STANDING;
            return CheckMovementInputAcroBike(newDirection, newKeys, heldKeys);
        }
        else
        {
            // .. otherwise, go back to normal on flat ground
            *newDirection = direction;
            gPlayerAvatar.runningState = NOT_MOVING;
            gPlayerAvatar.acroBikeState = ACRO_STATE_NORMAL;
            return ACRO_TRANS_WHEELIE_TO_NORMAL;
        }
    }

    // B Button is still held

    if (*newDirection == DIR_NONE)
    {
        // we did not move, so keep hopping in place without moving.
        *newDirection = direction;
        gPlayerAvatar.runningState = NOT_MOVING;
        return ACRO_TRANS_WHEELIE_HOPPING_STANDING;
    }
    if (*newDirection != direction && gPlayerAvatar.runningState != MOVING)
    {
        // we changed direction, so turn but do not move hop.
        gPlayerAvatar.runningState = TURN_DIRECTION;
        return ACRO_TRANS_WHEELIE_HOPPING_STANDING;
    }
    // otherwise, we started moving while hopping
    gPlayerAvatar.runningState = MOVING;
    return ACRO_TRANS_WHEELIE_HOPPING_MOVING;
}

static u8 AcroBikeHandleInputWheelieMoving(u8 *newDirection, u16 newKeys, u16 heldKeys)
{
    u8 direction;
    struct ObjectEvent *playerObjEvent;

    direction = GetPlayerFacingDirection();
    playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];
    if (!(heldKeys & B_BUTTON))
    {
        // we were moving on a wheelie, but we let go while moving. reset bike still status
        Bike_SetBikeStill();
        if (!MetatileBehavior_IsBumpySlope(playerObjEvent->currentMetatileBehavior))
        {
            // we let go of B and arent on a bumpy slope, set state to normal because now we need to handle this
            gPlayerAvatar.acroBikeState = ACRO_STATE_NORMAL;
            if (*newDirection == DIR_NONE)
            {
                // we stopped moving but are turning, still try to lower the wheelie in place.
                *newDirection = direction;
                gPlayerAvatar.runningState = NOT_MOVING;
                return ACRO_TRANS_WHEELIE_TO_NORMAL;
            }
            if (*newDirection != direction && gPlayerAvatar.runningState != MOVING)
            {
                // we did not turn while lowering wheelie, so do so without turning.
                gPlayerAvatar.runningState = NOT_MOVING;
                return ACRO_TRANS_WHEELIE_TO_NORMAL;
            }
            // if we are moving while lowering wheelie, put the acro into a lowering state while moving.
            gPlayerAvatar.runningState = MOVING;
            return ACRO_TRANS_WHEELIE_LOWERING_MOVING;
        }
        // please do not undo the wheelie on a bumpy slope
        gPlayerAvatar.acroBikeState = ACRO_STATE_WHEELIE_STANDING;
        return CheckMovementInputAcroBike(newDirection, newKeys, heldKeys);
    }
    // we are still holding B.
    if (*newDirection == DIR_NONE)
    {
        // idle the wheelie in place because we're holding B without moving.
        *newDirection = direction;
        gPlayerAvatar.acroBikeState = ACRO_STATE_WHEELIE_STANDING;
        gPlayerAvatar.runningState = NOT_MOVING;
        Bike_SetBikeStill();
        return ACRO_TRANS_WHEELIE_IDLE;
    }
    if (direction != *newDirection && gPlayerAvatar.runningState != MOVING)
    {
        gPlayerAvatar.runningState = NOT_MOVING;
        return ACRO_TRANS_WHEELIE_IDLE;
    }
    gPlayerAvatar.runningState = MOVING;
    return ACRO_TRANS_WHEELIE_MOVING;
}

static u8 AcroBikeHandleInputSidewaysJump(u8 *ptr, u16 newKeys, u16 heldKeys)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    playerObjEvent->facingDirectionLocked = 0;
    SetObjectEventDirection(playerObjEvent, playerObjEvent->facingDirection);
    gPlayerAvatar.acroBikeState = ACRO_STATE_NORMAL;
    return CheckMovementInputAcroBike(ptr, newKeys, heldKeys);
}

static u8 AcroBikeHandleInputTurnJump(u8 *ptr, u16 newKeys, u16 heldKeys)
{
    gPlayerAvatar.acroBikeState = ACRO_STATE_NORMAL;
    return CheckMovementInputAcroBike(ptr, newKeys, heldKeys);
}

static void AcroBikeTransition_FaceDirection(u8 direction)
{
    PlayerFaceDirection(direction);
}

static void AcroBikeTransition_TurnDirection(u8 direction)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior) == 0)
        direction = playerObjEvent->movementDirection;
    PlayerFaceDirection(direction);
}

static void AcroBikeTransition_Moving(u8 direction)
{
    u8 collision;
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior) == 0)
    {
        AcroBikeTransition_FaceDirection(playerObjEvent->movementDirection);
        return;
    }
    collision = GetBikeCollision(direction);
    if (collision > 0 && collision < COLLISION_VERTICAL_RAIL)
    {
        if (collision == COLLISION_LEDGE_JUMP)
            PlayerJumpLedge(direction);
        else
                if (!BikeCollisionHandledElsewhere(collision))
            PlayerOnBikeCollide(direction);
    }
    else
    {
        BikeMoveWithSpeed(PlayerRideWaterCurrent, direction, collision);
    }
}

static void AcroBikeTransition_NormalToWheelie(u8 direction)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior) == 0)
        direction = playerObjEvent->movementDirection;
    PlayerStartWheelie(direction);
}

static void AcroBikeTransition_WheelieToNormal(u8 direction)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior) == 0)
        direction = playerObjEvent->movementDirection;
    PlayerEndWheelie(direction);
}

static void AcroBikeTransition_WheelieIdle(u8 direction)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior) == 0)
        direction = playerObjEvent->movementDirection;
    PlayerIdleWheelie(direction);
}

static void AcroBikeTransition_WheelieHoppingStanding(u8 direction)
{
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior) == 0)
        direction = playerObjEvent->movementDirection;
    PlayerStandingHoppingWheelie(direction);
}

static void AcroBikeTransition_WheelieHoppingMoving(u8 direction)
{
    u8 collision;
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior) == 0)
    {
        AcroBikeTransition_WheelieHoppingStanding(playerObjEvent->movementDirection);
        return;
    }
    collision = GetBikeCollision(direction);
    if (collision && collision != COLLISION_WHEELIE_HOP)
    {
        if (collision == COLLISION_LEDGE_JUMP)
        {
            PlayerLedgeHoppingWheelie(direction);
            return;
        }
        if (BikeCollisionHandledElsewhere(collision))
        {
            return;
        }
        if (collision < COLLISION_VERTICAL_RAIL)
        {
            AcroBikeTransition_WheelieHoppingStanding(direction);
            return;
        }
    }
    PlayerMovingHoppingWheelie(direction);
}

static void AcroBikeTransition_SideJump(u8 direction)
{
    u8 collision;

    collision = GetBikeCollision(direction);
    if (collision)
    {
        if (collision == COLLISION_PUSHED_BOULDER)
            return;
        if (collision < COLLISION_ISOLATED_VERTICAL_RAIL)
        {
            AcroBikeTransition_TurnDirection(direction);
            return;
        }
        if (WillPlayerCollideWithCollision(collision, direction) == FALSE)
        {
            AcroBikeTransition_TurnDirection(direction);
            return;
        }
    }
    PlayerAcroSideJump(direction);
}

static void AcroBikeTransition_TurnJump(u8 direction)
{
    PlayerAcroTurnJump(direction);
}

static void AcroBikeTransition_WheelieMoving(u8 direction)
{
    u8 collision;
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior) == 0)
    {
        PlayerIdleWheelie(playerObjEvent->movementDirection);
        return;
    }
    collision = GetBikeCollision(direction);
    if (collision > 0 && collision < COLLISION_VERTICAL_RAIL)
    {
        if (collision == COLLISION_LEDGE_JUMP)
        {
            PlayerLedgeHoppingWheelie(direction);
        }
        else if (collision == COLLISION_WHEELIE_HOP)
        {
            PlayerIdleWheelie(direction);
        }
        else if (collision < COLLISION_STOP_SURFING)
        {
            if (MetatileBehavior_IsBumpySlope(playerObjEvent->currentMetatileBehavior))
                PlayerIdleWheelie(direction);
            else
                PlayerAcroWheelieCollide(direction);  //hit wall?
        }
        return;
    }
    PlayerAcroWheelieMove(direction);
    gPlayerAvatar.runningState = MOVING;
}

static void AcroBikeTransition_WheelieRisingMoving(u8 direction)
{
    u8 collision;
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior) == 0)
    {
        PlayerStartWheelie(playerObjEvent->movementDirection);
        return;
    }
    collision = GetBikeCollision(direction);
    if (collision > 0 && collision < COLLISION_VERTICAL_RAIL)
    {
        if (collision == COLLISION_LEDGE_JUMP)
        {
            PlayerLedgeHoppingWheelie(direction);
        }
        else if (collision == COLLISION_WHEELIE_HOP)
        {
            PlayerIdleWheelie(direction);
        }
        else if (collision < COLLISION_STOP_SURFING)
        {
            if (MetatileBehavior_IsBumpySlope(playerObjEvent->currentMetatileBehavior))
                PlayerIdleWheelie(direction);
            else
                PlayerAcroWheelieCollide(direction);  //hit wall?
        }
        return;
    }
    PlayerAcroPopWheelie(direction);
    gPlayerAvatar.runningState = MOVING;
}

static void AcroBikeTransition_WheelieLoweringMoving(u8 direction)
{
    u8 collision;
    struct ObjectEvent *playerObjEvent = &gObjectEvents[gPlayerAvatar.objectEventId];

    if (CanBikeFaceDirectionOnRail(direction, playerObjEvent->currentMetatileBehavior) == 0)
    {
        PlayerEndWheelie(playerObjEvent->movementDirection);
        return;
    }
    collision = GetBikeCollision(direction);
    if (collision > 0 && collision < COLLISION_VERTICAL_RAIL)
    {
        if (collision == COLLISION_LEDGE_JUMP)
            PlayerJumpLedge(direction);
        else if (!BikeCollisionHandledElsewhere(collision))
            PlayerEndWheelie(direction);
        return;
    }
    PlayerAcroEndWheelieMove(direction);
}

void Bike_TryAcroBikeHistoryUpdate(u16 newKeys, u16 heldKeys)
{
    if ((gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_ACRO_BIKE) && GetBikeInputTimers(TRUE) != NULL)
        AcroBike_TryHistoryUpdate(newKeys, heldKeys);
}

static void AcroBike_TryHistoryUpdate(u16 newKeys, u16 heldKeys) // newKeys is unused
{
    u8 direction = Bike_DPadToDirection(heldKeys);
    u8 *buttonTimers = GetBikeInputTimers(FALSE);

    if (direction == (gPlayerAvatar.directionHistory & 0xF))
    {
        // increment the timer for direction history since last input.
        if (gPlayerAvatar.dirTimerHistory[0] < 0xFF)
            gPlayerAvatar.dirTimerHistory[0]++;
    }
    else
    {
        Bike_UpdateDirTimerHistory(direction);
        gPlayerAvatar.bikeSpeed = PLAYER_SPEED_STANDING;
    }

    direction = heldKeys & (A_BUTTON | B_BUTTON | SELECT_BUTTON | START_BUTTON); // directions is reused for some reason.
    if (direction == (gPlayerAvatar.abStartSelectHistory & 0xF))
    {
        if (buttonTimers[0] < 0xFF)
            buttonTimers[0]++;
    }
    else
    {
        Bike_UpdateABStartSelectHistory(direction);
        gPlayerAvatar.bikeSpeed = PLAYER_SPEED_STANDING;
    }
}

static bool8 HasPlayerInputTakenLongerThanList(const u8 *dirTimerList, const u8 *abStartSelectTimerList)
{
    u8 i;
    u8 *buttonTimers = GetBikeInputTimers(FALSE);

    if (buttonTimers == NULL)
        return FALSE;

    for (i = 0; dirTimerList[i] != 0; i++)
    {
        if (gPlayerAvatar.dirTimerHistory[i] > dirTimerList[i])
            return FALSE;
    }
    for (i = 0; abStartSelectTimerList[i] != 0; i++)
    {
        if (buttonTimers[i] > abStartSelectTimerList[i])
            return FALSE;
    }
    return TRUE;
}

static u8 AcroBike_GetJumpDirection(void)
{
    u32 i;

    for (i = 0; i < NELEMS(sAcroBikeTricksList); i++)
    {
        const struct BikeHistoryInputInfo *historyInputInfo = &sAcroBikeTricksList[i];
        u32 dirHistory = gPlayerAvatar.directionHistory;
        u32 abStartSelectHistory = gPlayerAvatar.abStartSelectHistory;

        dirHistory &= historyInputInfo->dirHistoryMask;
        abStartSelectHistory &= historyInputInfo->abStartSelectHistoryMask;
        if (dirHistory == historyInputInfo->dirHistoryMatch && abStartSelectHistory == historyInputInfo->abStartSelectHistoryMatch && HasPlayerInputTakenLongerThanList(historyInputInfo->dirTimerHistoryList, historyInputInfo->abStartSelectHistoryList))
            return historyInputInfo->direction;
    }
    return 0;
}

static void Bike_UpdateDirTimerHistory(u8 dir)
{
    u8 i;

    gPlayerAvatar.directionHistory = (gPlayerAvatar.directionHistory << 4) | (dir & 0xF);

    for (i = NELEMS(gPlayerAvatar.dirTimerHistory) - 1; i != 0; i--)
        gPlayerAvatar.dirTimerHistory[i] = gPlayerAvatar.dirTimerHistory[i - 1];
    gPlayerAvatar.dirTimerHistory[0] = 1;
}

static void Bike_UpdateABStartSelectHistory(u8 input)
{
    u8 i;
    u8 *buttonTimers = GetBikeInputTimers(FALSE);

    gPlayerAvatar.abStartSelectHistory = (gPlayerAvatar.abStartSelectHistory << 4) | (input & 0xF);

    for (i = 8 - 1; i != 0; i--)
        buttonTimers[i] = buttonTimers[i - 1];
    buttonTimers[0] = 1;
}

static u8 Bike_DPadToDirection(u16 heldKeys)
{
    if (heldKeys & DPAD_UP)
        return DIR_NORTH;
    if (heldKeys & DPAD_DOWN)
        return DIR_SOUTH;
    if (heldKeys & DPAD_LEFT)
        return DIR_WEST;
    if (heldKeys & DPAD_RIGHT)
        return DIR_EAST;
    return DIR_NONE;
}

static bool8 WillPlayerCollideWithCollision(u8 newTileCollision, u8 direction)
{
    if (direction == DIR_NORTH || direction == DIR_SOUTH)
    {
        if (newTileCollision == COLLISION_ISOLATED_VERTICAL_RAIL || newTileCollision == COLLISION_VERTICAL_RAIL)
            return FALSE;
    }
    else if (newTileCollision == COLLISION_ISOLATED_HORIZONTAL_RAIL || newTileCollision == COLLISION_HORIZONTAL_RAIL)
    {
        return FALSE;
    }

    return TRUE;
}
