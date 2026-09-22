#include "global.h"
#include "gflib.h"
#include "event_object_movement.h"
#include "field_camera.h"
#include "field_weather.h"
#include "fieldmap.h"
#include "overworld.h"
#include "script.h"
#include "task.h"
#include "constants/maps.h"

// Every AIRPORT_FLYOVER_INTERVAL frames an airliner crosses the sky over the
// Vermilion City airport, flying north along the runway's centre line with its
// shadow sliding over the ground below it.
//
// The countdown and the flight both run only while the player can move about:
// a menu, a dialogue or any other script stops them, the same way it stops the
// people in the city, and they carry on where they left off afterwards. The
// plane appears below the bottom of the screen and is removed once it and its
// shadow have left the top, and a pass is skipped when the airport is not on
// screen. Leaving the city ends the task; entering it (VermilionCity_OnResume)
// starts a new one, so the first pass comes AIRPORT_FLYOVER_INTERVAL frames
// after arriving.

#define AIRPORT_FLYOVER_INTERVAL 1800   // 30 seconds

#define FLYOVER_SPEED     2    // pixels per frame
#define SHADOW_OFFSET_X  14    // the sun is up and to the left of the plane
#define SHADOW_OFFSET_Y  30
#define SPRITE_HALF      16    // both sprites are 32x32
#define PLANE_HALF       16

// The runway's centre line runs down the left edge of map column 39,
// and the airport grounds fill map rows 0 to 16.
#define RUNWAY_CENTRE_X  39
#define AIRPORT_TOP       0
#define AIRPORT_BOTTOM   16

#define TAG_FLYOVER_PLANE   0x1300
#define TAG_FLYOVER_SHADOW  0x1301
#define TAG_FLYOVER_PAL     0x1300

#define tTimer   data[0]
#define tActive  data[1]
#define tPlane   data[2]
#define tShadow  data[3]

extern const u16 gObjectEventPal_Truck[];

// The plane in the sky is the 30x30 airliner (nose north), half as large again
// as the 20x20 ones parked on the apron, being nearer the viewer; its shadow is
// the parked plane's silhouette. tools/make_airplane_sprite.py draws all three.
static const u16 sPlaneGfx[] = INCBIN_U16("graphics/object_events/pics/misc/airplane_flyover.4bpp");
static const u16 sShadowGfx[] = INCBIN_U16("graphics/object_events/pics/misc/airplane_shadow.4bpp");

static const struct SpriteSheet sPlaneSheet = {
    .data = sPlaneGfx,
    .size = 0x200,
    .tag = TAG_FLYOVER_PLANE,
};

static const struct SpriteSheet sShadowSheet = {
    .data = sShadowGfx,
    .size = 0x200,
    .tag = TAG_FLYOVER_SHADOW,
};

// the airliners' own colours, so the flyover needs no palette of its own
static const struct SpritePalette sPalette = {
    .data = gObjectEventPal_Truck,
    .tag = TAG_FLYOVER_PAL,
};

// In the sky: priority 1 puts it over the map's top layer (BG1, roofs and
// tree tops; a sprite wins a tie) but under BG0, the menus and text boxes.
static const struct OamData sPlaneOam = {
    .shape = SPRITE_SHAPE(32x32),
    .size = SPRITE_SIZE(32x32),
    .priority = 1,
};

// on the ground: over the ground layers (BG2 and BG3), under roofs and tree tops
static const struct OamData sShadowOam = {
    .shape = SPRITE_SHAPE(32x32),
    .size = SPRITE_SIZE(32x32),
    .priority = 2,
};

static const struct SpriteTemplate sPlaneTemplate = {
    .tileTag = TAG_FLYOVER_PLANE,
    .paletteTag = TAG_FLYOVER_PAL,
    .oam = &sPlaneOam,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy,
};

static const struct SpriteTemplate sShadowTemplate = {
    .tileTag = TAG_FLYOVER_SHADOW,
    .paletteTag = TAG_FLYOVER_PAL,
    .oam = &sShadowOam,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy,
};

static void Task_AirportFlyover(u8 taskId);

void StartAirportFlyover(void)
{
    if (FindTaskIdByFunc(Task_AirportFlyover) == TASK_NONE)
        CreateTask(Task_AirportFlyover, 80);
}

static bool8 InVermilionCity(void)
{
    return gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_VERMILION_CITY)
        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_VERMILION_CITY);
}

// Everything waits while the player cannot move: menus, dialogue, scripts,
// screen fades, or another screen (the bag, a battle...) having taken over.
static bool8 IsFieldPaused(void)
{
    return gMain.callback1 != CB1_Overworld
        || ArePlayerFieldControlsLocked()
        || gPaletteFade.active;
}

// Another screen resets the sprites, so a sprite id is only still ours if it
// is in use and was made from our template.
static bool8 OwnsSprite(s16 spriteId, const struct SpriteTemplate *template)
{
    return spriteId < MAX_SPRITES && gSprites[spriteId].inUse && gSprites[spriteId].template == template;
}

static void EndFlight(struct Task *task)
{
    if (OwnsSprite(task->tPlane, &sPlaneTemplate))
        DestroySprite(&gSprites[task->tPlane]);
    if (OwnsSprite(task->tShadow, &sShadowTemplate))
        DestroySprite(&gSprites[task->tShadow]);
    FreeSpriteTilesByTag(TAG_FLYOVER_PLANE);
    FreeSpriteTilesByTag(TAG_FLYOVER_SHADOW);
    FreeSpritePaletteByTag(TAG_FLYOVER_PAL);
    task->tActive = FALSE;
    task->tPlane = MAX_SPRITES;
    task->tShadow = MAX_SPRITES;
}

// Sprites in the field are placed like object events: SetSpritePosToMapCoords
// gives the camera relative position, and gSpriteCoordOffsetX/Y, which the
// field camera keeps up to date, moves them as the view scrolls.
static bool8 IsAirportOnScreen(s16 *runwayX)
{
    s16 x, top, bottom, dummy;

    SetSpritePosToMapCoords(RUNWAY_CENTRE_X + MAP_OFFSET, AIRPORT_TOP + MAP_OFFSET, &x, &top);
    SetSpritePosToMapCoords(RUNWAY_CENTRE_X + MAP_OFFSET, AIRPORT_BOTTOM + 1 + MAP_OFFSET, &dummy, &bottom);
    *runwayX = x;
    x += gSpriteCoordOffsetX;
    top += gSpriteCoordOffsetY;
    bottom += gSpriteCoordOffsetY;
    return x > -PLANE_HALF && x < DISPLAY_WIDTH + PLANE_HALF && bottom > 0 && top < DISPLAY_HEIGHT;
}

static void TryStartFlight(struct Task *task)
{
    s16 x, y;
    u8 palIndex;

    if (!IsAirportOnScreen(&x))
        return;
    palIndex = LoadSpritePalette(&sPalette);
    if (palIndex == 0xFF)
        return;
    UpdateSpritePaletteWithWeather(palIndex);
    if (LoadSpriteSheet(&sPlaneSheet) == 0 || LoadSpriteSheet(&sShadowSheet) == 0)
    {
        EndFlight(task);
        return;
    }
    // start just below the bottom edge of the screen
    y = DISPLAY_HEIGHT + PLANE_HALF - gSpriteCoordOffsetY;
    task->tPlane = CreateSprite(&sPlaneTemplate, x, y, 0);
    task->tShadow = CreateSprite(&sShadowTemplate, x + SHADOW_OFFSET_X, y + SHADOW_OFFSET_Y, 0xFF);
    if (task->tPlane == MAX_SPRITES || task->tShadow == MAX_SPRITES)
    {
        EndFlight(task);
        return;
    }
    gSprites[task->tPlane].coordOffsetEnabled = TRUE;
    gSprites[task->tShadow].coordOffsetEnabled = TRUE;
    task->tActive = TRUE;
}

static void UpdateFlight(struct Task *task)
{
    struct Sprite *plane = &gSprites[task->tPlane];
    struct Sprite *shadow = &gSprites[task->tShadow];

    plane->y -= FLYOVER_SPEED;
    shadow->y -= FLYOVER_SPEED;
    // done once the shadow, the lower of the two, is past the top edge
    if (shadow->y + gSpriteCoordOffsetY < -SPRITE_HALF)
        EndFlight(task);
}

static void Task_AirportFlyover(u8 taskId)
{
    struct Task *task = &gTasks[taskId];

    if (!InVermilionCity())
    {
        EndFlight(task);
        DestroyTask(taskId);
        return;
    }
    if (IsFieldPaused())
        return;
    if (task->tActive)
    {
        if (OwnsSprite(task->tPlane, &sPlaneTemplate) && OwnsSprite(task->tShadow, &sShadowTemplate))
            UpdateFlight(task);
        else
            EndFlight(task);    // another screen cleared the sprites
    }
    else if (++task->tTimer >= AIRPORT_FLYOVER_INTERVAL)
    {
        task->tTimer = 0;
        TryStartFlight(task);
    }
}
