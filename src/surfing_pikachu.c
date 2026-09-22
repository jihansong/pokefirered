#include "global.h"
#include "surfing_pikachu.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "field_effect.h"
#include "field_weather.h"
#include "palette.h"
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
// PIKACHU cleared. The Route 19 surfer then teaches it SURF and FLY.
// Whenever Oak's PIKACHU is the one that SURFS, the player rides on its back
// (FldEff_SurfBlob).

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

#define PAL_TAG_SURF_PIKACHU 0x1129

extern const u16 gObjectEventPal_NpcBlue[];

// Oak's PIKACHU swimming with the player on its back is drawn in the colors of its
// overworld sprite (the NPC blue palette), loaded under a tag of its own.
static const struct SpritePalette sSurfPikachuPalette = {gObjectEventPal_NpcBlue, PAL_TAG_SURF_PIKACHU};

// Continuing a save made while surfing creates the sprite during the quest log recap,
// and the palette buffers are cleared when the field is entered again while the
// palette tag stays: RefreshSurfPikachuPalette notices and puts the colors back.
#define PIKACHU_YELLOW 5 // a color of the palette that is not black or transparent

// Called when SURF starts, with the party slot of the mon that uses it.
void RecordSurfingMon(u32 partySlot)
{
    u16 onPikachu = partySlot < PARTY_SIZE && IsStarterPikachu(&gPlayerParty[partySlot]);

    VarSet(VAR_SURF_PIKACHU, onPikachu);
}

// For FldEff_SurfBlob: the palette slot for the swimming PIKACHU, or 0xFF to draw
// the usual blob (another mon SURFS, or no sprite palette slot is free). It runs
// again whenever the blob is remade (a map change, continuing a save), so a player
// who saved while surfing on PIKACHU keeps riding it.
u8 TryLoadSurfPikachuPalette(void)
{
    u8 paletteNum;

    if (!VarGet(VAR_SURF_PIKACHU))
        return 0xFF;
    paletteNum = LoadSpritePalette(&sSurfPikachuPalette);
    if (paletteNum != 0xFF)
        UpdateSpritePaletteWithWeather(paletteNum);
    return paletteNum;
}

// Called by the swimming PIKACHU sprite every frame: reload its colors if they are gone.
void RefreshSurfPikachuPalette(struct Sprite *sprite)
{
    u16 offset = OBJ_PLTT_ID(sprite->oam.paletteNum);

    if (gPlttBufferUnfaded[offset + PIKACHU_YELLOW] == gObjectEventPal_NpcBlue[PIKACHU_YELLOW])
        return;
    LoadPalette(gObjectEventPal_NpcBlue, offset, PLTT_SIZE_4BPP);
    UpdateSpritePaletteWithWeather(sprite->oam.paletteNum);
}

// Called once the player is back on land.
void EndSurfPikachu(void)
{
    VarSet(VAR_SURF_PIKACHU, 0);
    FreeSpritePaletteByTag(PAL_TAG_SURF_PIKACHU);
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
