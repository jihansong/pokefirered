#include "global.h"
#include "surfing_pikachu.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "field_effect.h"
#include "random.h"
#include "script.h"
#include "sound.h"
#include "sprite.h"
#include "starter_pikachu.h"
#include "task.h"
#include "constants/event_object_movement.h"
#include "constants/field_effects.h"
#include "constants/songs.h"

// A simplified take on Yellow's "Pikachu's Beach". The starter PIKACHU floats on
// the water west of the Route 19 beach while waves roll in from the left, each
// one marked by splashes two, one and zero tiles away. Pressing A just as a wave
// reaches PIKACHU makes it jump. Ten waves come in; VAR_RESULT is how many
// PIKACHU cleared. Once the Route 19 surfer is satisfied, the SURF blob is drawn
// in PIKACHU's colors, like a surfboard.

#define NUM_WAVES        10
#define WAVE_STEP_FRAMES 15
#define HIT_FRAME        (3 * WAVE_STEP_FRAMES)
#define HIT_WINDOW_EARLY 6
#define HIT_WINDOW_LATE  6

#define tState    data[0]
#define tTimer    data[1]
#define tWave     data[2]
#define tScore    data[3]
#define tObjId    data[4]
#define tResolved data[5]
#define tDelay    data[6]

#define PAL_TAG_SURFBOARD 0x1129

static const u16 sSurfboardPalette[] = INCBIN_U16("graphics/field_effects/palettes/surfboard.gbapal");

static const struct SpritePalette sSurfboardSpritePalette = {sSurfboardPalette, PAL_TAG_SURFBOARD};

void TryUseSurfboardPalette(struct Sprite *surfBlob)
{
    u8 paletteNum;

    if (!FlagGet(FLAG_SURFING_PIKACHU) || !IsStarterPikachuAliveInParty())
        return;
    paletteNum = LoadSpritePalette(&sSurfboardSpritePalette);
    if (paletteNum != 0xFF)
        surfBlob->oam.paletteNum = paletteNum;
}

u16 GetStarterPikachuPartySlotForScript(void)
{
    return GetStarterPikachuPartySlot();
}

// VAR_RESULT: TRUE if the starter PIKACHU leads the party
void IsStarterPikachuLead(void)
{
    gSpecialVar_Result = (GetStarterPikachuPartySlot() == 0);
}

static void StartSplash(struct ObjectEvent *pikachu, s16 dx, u8 fieldEffect)
{
    gFieldEffectArguments[0] = pikachu->currentCoords.x + dx;
    gFieldEffectArguments[1] = pikachu->currentCoords.y;
    gFieldEffectArguments[2] = pikachu->currentElevation;
    gFieldEffectArguments[3] = 2;
    FieldEffectStart(fieldEffect);
}

void Task_SurfingPikachu(u8 taskId)
{
    s16 *data = gTasks[taskId].data;
    struct ObjectEvent *pikachu = &gObjectEvents[tObjId];

    switch (tState)
    {
    case 0: // pause between waves
        if (tDelay-- > 0)
            break;
        tTimer = 0;
        tResolved = FALSE;
        tState = 1;
        // fallthrough
    case 1:
        if (tTimer == 0 || tTimer == WAVE_STEP_FRAMES || tTimer == 2 * WAVE_STEP_FRAMES)
        {
            StartSplash(pikachu, -3 + tTimer / WAVE_STEP_FRAMES, FLDEFF_JUMP_SMALL_SPLASH);
            PlaySE(SE_PUDDLE);
        }
        if (!tResolved && JOY_NEW(A_BUTTON))
        {
            tResolved = TRUE;
            if (tTimer >= HIT_FRAME - HIT_WINDOW_EARLY && tTimer <= HIT_FRAME + HIT_WINDOW_LATE)
            {
                tScore++;
                PlaySE(SE_LEDGE);
                ObjectEventClearHeldMovementIfActive(pikachu);
                ObjectEventSetHeldMovement(pikachu, MOVEMENT_ACTION_JUMP_IN_PLACE_LEFT);
            }
            else
            {
                tResolved = 2; // jumped at the wrong time
                PlaySE(SE_FAILURE);
            }
        }
        if (tTimer == HIT_FRAME + HIT_WINDOW_LATE && tResolved != TRUE)
        {
            StartSplash(pikachu, 0, FLDEFF_JUMP_BIG_SPLASH);
            PlaySE(SE_M_SURF);
        }
        if (++tTimer > HIT_FRAME + 30)
        {
            if (++tWave >= NUM_WAVES)
            {
                tState = 2;
                tTimer = 0;
            }
            else
            {
                tDelay = 20 + Random() % 40;
                tState = 0;
            }
        }
        break;
    case 2:
        if (++tTimer > 40)
        {
            gSpecialVar_Result = tScore;
            ScriptContext_Enable();
            DestroyTask(taskId);
        }
        break;
    }
}

// VAR_0x8004: local id of the PIKACHU object on the current map
void StartSurfingPikachuMinigame(void)
{
    u8 taskId = CreateTask(Task_SurfingPikachu, 80);
    u8 objId = GetObjectEventIdByLocalIdAndMap(gSpecialVar_0x8004, gSaveBlock1Ptr->location.mapNum, gSaveBlock1Ptr->location.mapGroup);

    gTasks[taskId].data[4] = objId;
    gTasks[taskId].data[6] = 30;
}
