#include "global.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "field_player_avatar.h"
#include "follower_pikachu.h"
#include "link.h"
#include "quest_log.h"
#include "starter_pikachu.h"
#include "task.h"
#include "constants/event_object_movement.h"
#include "constants/event_objects.h"
#include "constants/quest_log.h"

// The starter PIKACHU walks behind the player, like in Yellow.
//
// It is a special object event (LOCALID_FOLLOWER) with no movement type of its own.
// Whenever the player object is given a movement action that changes its position,
// PIKACHU is sent to the tile the player is leaving at the same speed. That one hook
// covers keypad movement, forced movement (ice, spinners), door exits and scripted
// applymovement alike, so PIKACHU also follows through cutscenes.
//
// A per-frame field task spawns PIKACHU when it should be out (starter PIKACHU alive
// in the party, player on foot) and removes it otherwise. After a warp PIKACHU starts
// hidden on the player's tile and comes out once the player steps away.

// Set while a trainer checks its line of sight, so PIKACHU standing in the way
// doesn't hide the player.
bool8 gIgnoreFollowerPikachuCollision;

// Set by the HideFollowerPikachu special; cleared on map load or by ShowFollowerPikachu.
static EWRAM_DATA bool8 sHiddenByScript = FALSE;

struct ObjectEvent *GetFollowerPikachuObject(void)
{
    u8 i;

    for (i = 0; i < OBJECT_EVENTS_COUNT; i++)
    {
        if (gObjectEvents[i].active && gObjectEvents[i].localId == LOCALID_FOLLOWER)
            return &gObjectEvents[i];
    }
    return NULL;
}

bool8 IsFollowerPikachuObject(struct ObjectEvent *objectEvent)
{
    return objectEvent->active && objectEvent->localId == LOCALID_FOLLOWER;
}

bool8 ShouldIgnoreCollisionWithFollower(struct ObjectEvent *mover, struct ObjectEvent *other)
{
    if (other->localId != LOCALID_FOLLOWER)
        return FALSE;
    // The player walks through PIKACHU (they swap places), and so do trainers' lines of sight.
    return mover->isPlayer || gIgnoreFollowerPikachuCollision;
}

static bool8 ShouldFollowerExist(void)
{
    if (!FlagGet(FLAG_RECEIVED_STARTER_PIKACHU))
        return FALSE;
    if (QL_IS_PLAYBACK_STATE)
        return FALSE;
    if (InUnionRoom() == TRUE)
        return FALSE;
    // Like Yellow, PIKACHU goes back in its Poké Ball while the player bikes or surfs.
    if (TestPlayerAvatarFlags(PLAYER_AVATAR_FLAG_MACH_BIKE | PLAYER_AVATAR_FLAG_ACRO_BIKE
                            | PLAYER_AVATAR_FLAG_SURFING | PLAYER_AVATAR_FLAG_UNDERWATER))
        return FALSE;
    return IsStarterPikachuAliveInParty();
}

static void SpawnFollower(void)
{
    struct ObjectEvent *player = &gObjectEvents[gPlayerAvatar.objectEventId];
    struct ObjectEvent *follower;
    u8 objectEventId;

    objectEventId = SpawnSpecialObjectEventParameterized(OBJ_EVENT_GFX_PIKACHU, MOVEMENT_TYPE_NONE, LOCALID_FOLLOWER,
                                                         player->currentCoords.x, player->currentCoords.y,
                                                         player->currentElevation);
    if (objectEventId >= OBJECT_EVENTS_COUNT)
        return;
    follower = &gObjectEvents[objectEventId];
    ObjectEventTurn(follower, player->facingDirection);
    // Hidden under the player until they step away.
    follower->invisible = TRUE;
}

static void RemoveFollower(struct ObjectEvent *follower)
{
    RemoveObjectEventWithoutFlag(follower);
}

void FollowerPikachu_OnMapLoad(void)
{
    sHiddenByScript = FALSE;
    FollowerPikachu_Update();
}

static bool8 IsOnPlayerTile(struct ObjectEvent *follower)
{
    struct ObjectEvent *player = &gObjectEvents[gPlayerAvatar.objectEventId];

    return follower->currentCoords.x == player->currentCoords.x
        && follower->currentCoords.y == player->currentCoords.y;
}

// Whether the player's sprite has walked far enough off PIKACHU for it to come out
// without being drawn over the player. A player's step moves their coords at once,
// but their sprite only gets there over the next 16 frames.
static bool8 HasPlayerSpriteLeftFollower(struct ObjectEvent *follower)
{
    struct Sprite *playerSprite = &gSprites[gObjectEvents[gPlayerAvatar.objectEventId].spriteId];
    struct Sprite *followerSprite = &gSprites[follower->spriteId];
    s16 dx = (playerSprite->x + playerSprite->x2) - (followerSprite->x + followerSprite->x2);
    // Compare the sprites' bottom edges: the player is taller than PIKACHU.
    s16 dy = (playerSprite->y + playerSprite->y2 - playerSprite->centerToCornerVecY)
           - (followerSprite->y + followerSprite->y2 - followerSprite->centerToCornerVecY);

    if (dx < 0)
        dx = -dx;
    if (dy < 0)
        dy = -dy;
    return dx + dy >= 16;
}

void FollowerPikachu_Update(void)
{
    struct ObjectEvent *follower = GetFollowerPikachuObject();
    bool8 shouldExist = ShouldFollowerExist();

    if (follower != NULL && !shouldExist)
    {
        RemoveFollower(follower);
    }
    else if (follower == NULL && shouldExist)
    {
        SpawnFollower();
    }
    else if (follower != NULL)
    {
        if (sHiddenByScript)
            follower->invisible = TRUE;
        else if (follower->invisible && !IsOnPlayerTile(follower) && HasPlayerSpriteLeftFollower(follower))
            follower->invisible = FALSE;
    }
}

void Task_FollowerPikachu(u8 taskId)
{
    FollowerPikachu_Update();
}

void CreateFollowerPikachuTask(void)
{
    if (!FuncIsActiveTask(Task_FollowerPikachu))
        CreateTask(Task_FollowerPikachu, 80);
}

void HideFollowerPikachu(void)
{
    sHiddenByScript = TRUE;
    FollowerPikachu_Update();
}

// PIKACHU reappears behind the player the next time they step.
void ShowFollowerPikachu(void)
{
    struct ObjectEvent *follower = GetFollowerPikachuObject();
    struct ObjectEvent *player = &gObjectEvents[gPlayerAvatar.objectEventId];

    sHiddenByScript = FALSE;
    if (follower != NULL)
    {
        ObjectEventClearHeldMovementIfActive(follower);
        MoveObjectEventToMapCoords(follower, player->currentCoords.x, player->currentCoords.y);
        follower->invisible = TRUE;
    }
}

enum {
    FOLLOW_SPEED_NONE,
    FOLLOW_SPEED_SLOWEST,
    FOLLOW_SPEED_SLOWER,
    FOLLOW_SPEED_SLOW,
    FOLLOW_SPEED_NORMAL,
    FOLLOW_SPEED_FAST,
    FOLLOW_SPEED_FASTER,
    FOLLOW_SPEED_SLIDE,
};

// First action (facing down) of the walk used for each speed. The other directions
// follow in down, up, left, right order.
static const u8 sWalkActionsBySpeed[] = {
    [FOLLOW_SPEED_SLOWEST] = MOVEMENT_ACTION_WALK_SLOWEST_DOWN,
    [FOLLOW_SPEED_SLOWER]  = MOVEMENT_ACTION_WALK_SLOWER_DOWN,
    [FOLLOW_SPEED_SLOW]    = MOVEMENT_ACTION_WALK_SLOW_DOWN,
    [FOLLOW_SPEED_NORMAL]  = MOVEMENT_ACTION_WALK_NORMAL_DOWN,
    [FOLLOW_SPEED_FAST]    = MOVEMENT_ACTION_WALK_FAST_DOWN,
    [FOLLOW_SPEED_FASTER]  = MOVEMENT_ACTION_WALK_FASTER_DOWN,
    [FOLLOW_SPEED_SLIDE]   = MOVEMENT_ACTION_SLIDE_DOWN,
};

#define ACTION_IN_RANGE(action, first) ((action) >= (first) && (action) < (first) + 4)

// How fast PIKACHU should move to keep up with a player movement action,
// or FOLLOW_SPEED_NONE if the action doesn't move the player.
static u8 GetFollowSpeed(u8 action)
{
    if (ACTION_IN_RANGE(action, MOVEMENT_ACTION_WALK_SLOWEST_DOWN))
        return FOLLOW_SPEED_SLOWEST;
    if (ACTION_IN_RANGE(action, MOVEMENT_ACTION_WALK_SLOWER_DOWN))
        return FOLLOW_SPEED_SLOWER;
    if (ACTION_IN_RANGE(action, MOVEMENT_ACTION_WALK_SLOW_DOWN))
        return FOLLOW_SPEED_SLOW;
    if (ACTION_IN_RANGE(action, MOVEMENT_ACTION_WALK_NORMAL_DOWN)
     || ACTION_IN_RANGE(action, MOVEMENT_ACTION_JUMP_2_DOWN)
     || ACTION_IN_RANGE(action, MOVEMENT_ACTION_PLAYER_RUN_DOWN_SLOW)
     || ACTION_IN_RANGE(action, MOVEMENT_ACTION_JUMP_SPECIAL_DOWN)
     || ACTION_IN_RANGE(action, MOVEMENT_ACTION_JUMP_DOWN)
     || ACTION_IN_RANGE(action, MOVEMENT_ACTION_JUMP_SPECIAL_WITH_EFFECT_DOWN)
     || action == MOVEMENT_ACTION_WALK_DOWN_AFFINE)
        return FOLLOW_SPEED_NORMAL;
    if (ACTION_IN_RANGE(action, MOVEMENT_ACTION_WALK_FAST_DOWN)
     || ACTION_IN_RANGE(action, MOVEMENT_ACTION_PLAYER_RUN_DOWN)
     || ACTION_IN_RANGE(action, MOVEMENT_ACTION_SPIN_DOWN)
     || ACTION_IN_RANGE(action, MOVEMENT_ACTION_GLIDE_DOWN)
     || ACTION_IN_RANGE(action, MOVEMENT_ACTION_RIDE_WATER_CURRENT_DOWN))
        return FOLLOW_SPEED_FAST;
    if (ACTION_IN_RANGE(action, MOVEMENT_ACTION_WALK_FASTER_DOWN))
        return FOLLOW_SPEED_FASTER;
    if (ACTION_IN_RANGE(action, MOVEMENT_ACTION_SLIDE_DOWN))
        return FOLLOW_SPEED_SLIDE;
    return FOLLOW_SPEED_NONE;
}

// Direction of a movement action from one of the ranges GetFollowSpeed accepts.
static u8 GetMovingActionDirection(u8 action)
{
    static const u8 sFirstActions[] = {
        MOVEMENT_ACTION_WALK_SLOWEST_DOWN, MOVEMENT_ACTION_WALK_SLOWER_DOWN, MOVEMENT_ACTION_WALK_SLOW_DOWN,
        MOVEMENT_ACTION_WALK_NORMAL_DOWN, MOVEMENT_ACTION_JUMP_2_DOWN, MOVEMENT_ACTION_PLAYER_RUN_DOWN_SLOW,
        MOVEMENT_ACTION_JUMP_SPECIAL_DOWN, MOVEMENT_ACTION_JUMP_DOWN, MOVEMENT_ACTION_JUMP_SPECIAL_WITH_EFFECT_DOWN,
        MOVEMENT_ACTION_WALK_FAST_DOWN, MOVEMENT_ACTION_PLAYER_RUN_DOWN, MOVEMENT_ACTION_SPIN_DOWN,
        MOVEMENT_ACTION_GLIDE_DOWN, MOVEMENT_ACTION_RIDE_WATER_CURRENT_DOWN, MOVEMENT_ACTION_WALK_FASTER_DOWN,
        MOVEMENT_ACTION_SLIDE_DOWN,
    };
    u8 i;

    if (action == MOVEMENT_ACTION_WALK_DOWN_AFFINE)
        return DIR_SOUTH;
    for (i = 0; i < ARRAY_COUNT(sFirstActions); i++)
    {
        if (ACTION_IN_RANGE(action, sFirstActions[i]))
            return action - sFirstActions[i] + DIR_SOUTH;
    }
    return DIR_NONE;
}

// Tucks PIKACHU away on the player's tile until the player's next step.
static void HideFollowerUnderPlayer(struct ObjectEvent *follower)
{
    struct ObjectEvent *player = &gObjectEvents[gPlayerAvatar.objectEventId];

    ObjectEventClearHeldMovementIfActive(follower);
    MoveObjectEventToMapCoords(follower, player->currentCoords.x, player->currentCoords.y);
    follower->invisible = TRUE;
}

// Called whenever an object other than the player is given a new movement action.
// Scripts don't know PIKACHU is there, so if someone is about to walk onto it
// (the rival coming up for a battle, a trainer approaching), PIKACHU gets out of the way.
void FollowerPikachu_OnObjectMovement(struct ObjectEvent *objectEvent, u8 movementActionId)
{
    struct ObjectEvent *follower = GetFollowerPikachuObject();
    u8 direction;
    s16 x, y;

    if (follower == NULL || objectEvent == follower || follower->invisible)
        return;
    direction = GetMovingActionDirection(movementActionId);
    if (direction == DIR_NONE)
        return;

    x = objectEvent->currentCoords.x;
    y = objectEvent->currentCoords.y;
    MoveCoords(direction, &x, &y);
    if (x != follower->currentCoords.x || y != follower->currentCoords.y)
    {
        if (!ACTION_IN_RANGE(movementActionId, MOVEMENT_ACTION_JUMP_2_DOWN))
            return;
        MoveCoords(direction, &x, &y);
        if (x != follower->currentCoords.x || y != follower->currentCoords.y)
            return;
    }
    HideFollowerUnderPlayer(follower);
}

static u8 GetDirectionFromDelta(s16 dx, s16 dy)
{
    if (dx > 0)
        return DIR_EAST;
    if (dx < 0)
        return DIR_WEST;
    if (dy > 0)
        return DIR_SOUTH;
    return DIR_NORTH;
}

// Called whenever the player object is given a new movement action.
void FollowerPikachu_OnPlayerMovement(u8 movementActionId)
{
    struct ObjectEvent *player = &gObjectEvents[gPlayerAvatar.objectEventId];
    struct ObjectEvent *follower = GetFollowerPikachuObject();
    u8 speed = GetFollowSpeed(movementActionId);
    s16 dx, dy, distance;
    u8 direction;

    if (follower == NULL || speed == FOLLOW_SPEED_NONE)
        return;

    // Normally PIKACHU finished its last step together with the player. If it's
    // somehow still walking, finish that step now so both stay on the grid.
    if (ObjectEventIsMovementOverridden(follower) && !ObjectEventClearHeldMovementIfFinished(follower))
    {
        ObjectEventClearHeldMovementIfActive(follower);
        MoveObjectEventToMapCoords(follower, follower->currentCoords.x, follower->currentCoords.y);
    }

    // The player hasn't left its tile yet, so currentCoords is where PIKACHU goes.
    dx = player->currentCoords.x - follower->currentCoords.x;
    dy = player->currentCoords.y - follower->currentCoords.y;
    distance = (dx < 0 ? -dx : dx) + (dy < 0 ? -dy : dy);
    if (distance == 0)
        return;

    direction = GetDirectionFromDelta(dx, dy);
    if (distance == 1)
    {
        ObjectEventSetHeldMovement(follower, sWalkActionsBySpeed[speed] + direction - 1);
    }
    else if (distance == 2 && (dx == 0 || dy == 0))
    {
        // The player jumped a ledge on their last move.
        ObjectEventSetHeldMovement(follower, GetJump2MovementAction(direction));
    }
    else
    {
        // The player was moved somewhere else (e.g. setobjectxy). Start over from under them.
        HideFollowerUnderPlayer(follower);
    }
}
