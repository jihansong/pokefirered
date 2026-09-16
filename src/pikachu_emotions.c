#include "global.h"
#include "gflib.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "field_player_avatar.h"
#include "follower_pikachu.h"
#include "menu.h"
#include "new_menu_helpers.h"
#include "pikachu_emotions.h"
#include "script.h"
#include "starter_pikachu.h"
#include "task.h"
#include "trig.h"
#include "constants/battle.h"
#include "constants/event_object_movement.h"
#include "constants/maps.h"
#include "constants/pikachu_emotions.h"
#include "constants/songs.h"

// Talking to the following starter PIKACHU, ported from Pokémon Yellow.
//
// PIKACHU picks one of Yellow's emotions from where the player is, its condition,
// what just happened (VAR_PIKACHU_EMOTION_MODIFIER) and otherwise its mood and
// friendship. An emotion is a short list of commands: an emote bubble over PIKACHU,
// one of its voice clips, a little hop or spin, and a window with an animated
// portrait of its face. The portraits are Yellow's, pre-rendered frame by frame from
// its tile-based animation scripts (see src/data/pikachu_emotions.h).

enum {
    PORTRAIT_OP_END,
    PORTRAIT_OP_FRAME,
    PORTRAIT_OP_VOICE,
    PORTRAIT_OP_THUNDERBOLT,
};

struct PikachuPortraitCmd
{
    u8 op;
    u8 arg;
    u8 ticks;
};

#define PORTRAIT_FRAME(frame, numTicks) {PORTRAIT_OP_FRAME, frame, numTicks}
#define PORTRAIT_VOICE(voice)           {PORTRAIT_OP_VOICE, voice, 0}
#define PORTRAIT_THUNDERBOLT            {PORTRAIT_OP_THUNDERBOLT, 0, 0}
#define PORTRAIT_END                    {PORTRAIT_OP_END, 0, 0}

// Emotion commands. Every command but PIKAEMOTE_END takes one argument byte.
enum {
    PIKAEMOTE_END,
    PIKAEMOTE_BUBBLE,
    PIKAEMOTE_VOICE,
    PIKAEMOTE_MOVEMENT,
    PIKAEMOTE_PORTRAIT,
    PIKAEMOTE_TURN_AWAY,
    PIKAEMOTE_WAIT_BUTTON,
    PIKAEMOTE_TURN_AWAY_IF_ASLEEP_IN_POKECENTER,
    PIKAEMOTE_TURN_AWAY_IF_IN_FAN_CLUB,
};

// In the order of graphics/pikachu_emotions/emote_bubbles.png
enum {
    EMOTE_BUBBLE_EXCLAMATION,
    EMOTE_BUBBLE_QUESTION,
    EMOTE_BUBBLE_SMILE,
    EMOTE_BUBBLE_SKULL,
    EMOTE_BUBBLE_HEART,
    EMOTE_BUBBLE_BOLT,
    EMOTE_BUBBLE_ZZZ,
    EMOTE_BUBBLE_FISH,
    EMOTE_BUBBLE_COUNT,
};

enum {
    PIKACHU_MOVEMENT_SPIN,
    PIKACHU_MOVEMENT_TURN,
    PIKACHU_MOVEMENT_HOP_TWICE_FAST,
    PIKACHU_MOVEMENT_HOP_TWICE_SLOW,
};

#include "data/pikachu_emotions.h"

// Yellow redraws the portrait every 3 frames and steps PIKACHU's movements every 2.
#define FRAMES_PER_PORTRAIT_TICK 3
#define FRAMES_PER_MOVEMENT_TICK 2
#define BUBBLE_FRAMES            60
#define PORTRAIT_SIZE            40
#define PORTRAIT_SHEET_WIDTH     (PORTRAIT_SIZE * PIKACHU_PORTRAIT_FRAMES_PER_ROW)
#define PORTRAIT_PALETTE         13
#define TAG_EMOTE_BUBBLE         0x5A5A

static const u8 sPortraitSheet[] = INCBIN_U8("graphics/pikachu_emotions/portraits.4bpp");
static const u16 sPortraitPalette[] = INCBIN_U16("graphics/pikachu_emotions/portraits.gbapal");
static const u8 sEmoteBubbleGfx[] = INCBIN_U8("graphics/pikachu_emotions/emote_bubbles.4bpp");
static const u16 sEmoteBubblePalette[] = INCBIN_U16("graphics/pikachu_emotions/emote_bubbles.gbapal");

#define BUBBLE_TILE_BYTES (16 * 16 / 2)

static const struct SpriteFrameImage sEmoteBubbleImages[] = {
    {sEmoteBubbleGfx + BUBBLE_TILE_BYTES * EMOTE_BUBBLE_EXCLAMATION, BUBBLE_TILE_BYTES},
    {sEmoteBubbleGfx + BUBBLE_TILE_BYTES * EMOTE_BUBBLE_QUESTION,    BUBBLE_TILE_BYTES},
    {sEmoteBubbleGfx + BUBBLE_TILE_BYTES * EMOTE_BUBBLE_SMILE,       BUBBLE_TILE_BYTES},
    {sEmoteBubbleGfx + BUBBLE_TILE_BYTES * EMOTE_BUBBLE_SKULL,       BUBBLE_TILE_BYTES},
    {sEmoteBubbleGfx + BUBBLE_TILE_BYTES * EMOTE_BUBBLE_HEART,       BUBBLE_TILE_BYTES},
    {sEmoteBubbleGfx + BUBBLE_TILE_BYTES * EMOTE_BUBBLE_BOLT,        BUBBLE_TILE_BYTES},
    {sEmoteBubbleGfx + BUBBLE_TILE_BYTES * EMOTE_BUBBLE_ZZZ,         BUBBLE_TILE_BYTES},
    {sEmoteBubbleGfx + BUBBLE_TILE_BYTES * EMOTE_BUBBLE_FISH,        BUBBLE_TILE_BYTES},
};

static const union AnimCmd sAnim_Bubble0[] = { ANIMCMD_FRAME(0, 1), ANIMCMD_END };
static const union AnimCmd sAnim_Bubble1[] = { ANIMCMD_FRAME(1, 1), ANIMCMD_END };
static const union AnimCmd sAnim_Bubble2[] = { ANIMCMD_FRAME(2, 1), ANIMCMD_END };
static const union AnimCmd sAnim_Bubble3[] = { ANIMCMD_FRAME(3, 1), ANIMCMD_END };
static const union AnimCmd sAnim_Bubble4[] = { ANIMCMD_FRAME(4, 1), ANIMCMD_END };
static const union AnimCmd sAnim_Bubble5[] = { ANIMCMD_FRAME(5, 1), ANIMCMD_END };
static const union AnimCmd sAnim_Bubble6[] = { ANIMCMD_FRAME(6, 1), ANIMCMD_END };
static const union AnimCmd sAnim_Bubble7[] = { ANIMCMD_FRAME(7, 1), ANIMCMD_END };

static const union AnimCmd *const sAnims_EmoteBubble[] = {
    sAnim_Bubble0, sAnim_Bubble1, sAnim_Bubble2, sAnim_Bubble3,
    sAnim_Bubble4, sAnim_Bubble5, sAnim_Bubble6, sAnim_Bubble7,
};

static const struct OamData sOam_EmoteBubble = {
    .size = SPRITE_SIZE(16x16),
    .shape = SPRITE_SHAPE(16x16),
    .priority = 1,
};

static const struct SpriteTemplate sSpriteTemplate_EmoteBubble = {
    .tileTag = TAG_NONE,
    .paletteTag = TAG_EMOTE_BUBBLE,
    .oam = &sOam_EmoteBubble,
    .anims = sAnims_EmoteBubble,
    .images = sEmoteBubbleImages,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy,
};

static const struct SpritePalette sSpritePalette_EmoteBubble = {sEmoteBubblePalette, TAG_EMOTE_BUBBLE};

enum {
    STATE_NEXT_COMMAND,
    STATE_WAIT_BUBBLE,
    STATE_WAIT_VOICE,
    STATE_MOVEMENT,
    STATE_WAIT_BUTTON,
    STATE_PORTRAIT_NEXT,
    STATE_PORTRAIT_SHOW_FRAME,
    STATE_PORTRAIT_WAIT_VOICE,
    STATE_PORTRAIT_THUNDERBOLT,
    STATE_PORTRAIT_CLOSE,
};

#define tState           data[0]
#define tTimer           data[1]
#define tWindowId        data[2]
#define tBubbleSpriteId  data[3]
#define tMovement        data[4]
#define tMovementTick    data[5]
#define tMovementFrame   data[6]
#define tPortraitTicks   data[7]
#define tFlashes         data[8]
#define tWindowShown     data[9]

static EWRAM_DATA const u8 *sEmotionCmd = NULL;
static EWRAM_DATA const struct PikachuPortraitCmd *sPortraitCmd = NULL;

static bool8 IsPlayerInMap(u16 map)
{
    return gSaveBlock1Ptr->location.mapGroup == (map >> 8) && gSaveBlock1Ptr->location.mapNum == (map & 0xFF);
}

static bool8 IsPlayerInPokemonTower(void)
{
    return gSaveBlock1Ptr->location.mapGroup == (MAP_POKEMON_TOWER_1F >> 8)
        && gSaveBlock1Ptr->location.mapNum >= (MAP_POKEMON_TOWER_1F & 0xFF)
        && gSaveBlock1Ptr->location.mapNum <= (MAP_POKEMON_TOWER_7F & 0xFF);
}

// Yellow's MapSpecificPikachuExpression followed by GetPikaPicAnimationScriptIndex.
static u8 ChooseStarterPikachuEmotion(void)
{
    static const u8 sModifierEmotions[] = {
        [PIKACHU_MODIFIER_CAUGHT_MON - 1]      = PIKACHU_EMOTION_18,
        [PIKACHU_MODIFIER_FISHING - 1]         = PIKACHU_EMOTION_21,
        [PIKACHU_MODIFIER_UNUSED - 1]          = PIKACHU_EMOTION_23,
        [PIKACHU_MODIFIER_REFUSED_STONE - 1]   = PIKACHU_EMOTION_24,
        [PIKACHU_MODIFIER_LEARNED_THUNDER - 1] = PIKACHU_EMOTION_25,
    };
    // Mood columns, then one row per friendship threshold.
    static const u8 sMoodThresholds[] = {40, 127, 128, 210, 255};
    static const u8 sFriendshipThresholds[] = {50, 100, 130, 160, 200, 250, 255};
    static const u8 sMoodEmotions[][5] = {
        {PIKACHU_EMOTION_14, PIKACHU_EMOTION_14, PIKACHU_EMOTION_6,  PIKACHU_EMOTION_13, PIKACHU_EMOTION_13},
        {PIKACHU_EMOTION_9,  PIKACHU_EMOTION_9,  PIKACHU_EMOTION_5,  PIKACHU_EMOTION_12, PIKACHU_EMOTION_12},
        {PIKACHU_EMOTION_3,  PIKACHU_EMOTION_3,  PIKACHU_EMOTION_1,  PIKACHU_EMOTION_8,  PIKACHU_EMOTION_8},
        {PIKACHU_EMOTION_3,  PIKACHU_EMOTION_3,  PIKACHU_EMOTION_4,  PIKACHU_EMOTION_15, PIKACHU_EMOTION_15},
        {PIKACHU_EMOTION_17, PIKACHU_EMOTION_17, PIKACHU_EMOTION_7,  PIKACHU_EMOTION_2,  PIKACHU_EMOTION_2},
        {PIKACHU_EMOTION_17, PIKACHU_EMOTION_17, PIKACHU_EMOTION_16, PIKACHU_EMOTION_10, PIKACHU_EMOTION_10},
        {PIKACHU_EMOTION_17, PIKACHU_EMOTION_17, PIKACHU_EMOTION_19, PIKACHU_EMOTION_20, PIKACHU_EMOTION_20},
    };
    u8 slot = GetStarterPikachuPartySlot();
    u32 status = slot != PARTY_SIZE ? GetMonData(&gPlayerParty[slot], MON_DATA_STATUS, NULL) : 0;
    u8 modifier = GetPikachuEmotionModifier();
    u8 mood, friendship, column, row;

    // FR/LG's fan club has no PIKACHU event, so PIKACHU just loves the attention.
    if (IsPlayerInMap(MAP_VERMILION_CITY_POKEMON_FAN_CLUB))
        return PIKACHU_EMOTION_30;
    // The Jigglypuff in Pewter's Pokémon Center sings PIKACHU to sleep.
    if (IsPlayerInMap(MAP_PEWTER_CITY_POKEMON_CENTER_1F))
        return PIKACHU_EMOTION_26;
    // Puzzled by Bill as a Pokémon, happy once he's back to normal.
    if (IsPlayerInMap(MAP_ROUTE25_SEA_COTTAGE))
        return FlagGet(FLAG_HELPED_BILL_IN_SEA_COTTAGE) ? PIKACHU_EMOTION_27 : PIKACHU_EMOTION_23;
    if (status & STATUS1_SLEEP)
        return PIKACHU_EMOTION_11;
    if (status != 0)
        return PIKACHU_EMOTION_28;
    if (IsPlayerInPokemonTower())
        return PIKACHU_EMOTION_22;
    if (modifier != PIKACHU_MODIFIER_NONE && modifier - 1 < ARRAY_COUNT(sModifierEmotions))
        return sModifierEmotions[modifier - 1];

    mood = GetPikachuMood();
    friendship = GetStarterPikachuFriendship();
    for (column = 0; column < ARRAY_COUNT(sMoodThresholds) - 1 && sMoodThresholds[column] < mood; column++)
        ;
    for (row = 0; row < ARRAY_COUNT(sFriendshipThresholds) - 1 && sFriendshipThresholds[row] < friendship; row++)
        ;
    return sMoodEmotions[row][column];
}

static void TurnFollowerToward(u8 direction)
{
    struct ObjectEvent *follower = GetFollowerPikachuObject();

    if (follower == NULL)
        return;
    ObjectEventClearHeldMovementIfActive(follower);
    ObjectEventSetHeldMovement(follower, GetFaceDirectionFastMovementAction(direction));
}

static void TurnFollowerAwayFromPlayer(void)
{
    TurnFollowerToward(GetPlayerFacingDirection());
}

static void CreateEmoteBubble(u8 taskId, u8 bubble)
{
    struct ObjectEvent *follower = GetFollowerPikachuObject();
    struct Sprite *followerSprite;
    u8 spriteId;

    gTasks[taskId].tBubbleSpriteId = MAX_SPRITES;
    if (follower == NULL || bubble >= EMOTE_BUBBLE_COUNT)
        return;
    followerSprite = &gSprites[follower->spriteId];
    LoadSpritePalette(&sSpritePalette_EmoteBubble);
    spriteId = CreateSprite(&sSpriteTemplate_EmoteBubble, followerSprite->x, followerSprite->y - 16, 0);
    if (spriteId == MAX_SPRITES)
        return;
    gSprites[spriteId].coordOffsetEnabled = TRUE;
    gSprites[spriteId].oam.priority = followerSprite->oam.priority;
    StartSpriteAnim(&gSprites[spriteId], bubble);
    gTasks[taskId].tBubbleSpriteId = spriteId;
}

static void DestroyEmoteBubble(u8 taskId)
{
    if (gTasks[taskId].tBubbleSpriteId != MAX_SPRITES)
        DestroySprite(&gSprites[gTasks[taskId].tBubbleSpriteId]);
    FreeSpritePaletteByTag(TAG_EMOTE_BUBBLE);
}

// Yellow's PikachuMovementData_fd218/fd21e (turn clockwise every tick, then hold still)
// and fd224/fd230 (two hops, each half a sine wave).
static bool8 UpdatePikachuMovement(u8 taskId)
{
    static const u8 sClockwise[] = {[DIR_SOUTH] = DIR_WEST, [DIR_WEST] = DIR_NORTH, [DIR_NORTH] = DIR_EAST, [DIR_EAST] = DIR_SOUTH};
    s16 *data = gTasks[taskId].data;
    struct ObjectEvent *follower = GetFollowerPikachuObject();
    struct Sprite *sprite;
    u8 turns, hopTicks, angleStep;
    s16 hopTick;

    if (follower == NULL)
        return TRUE;
    sprite = &gSprites[follower->spriteId];
    if (++tMovementFrame < FRAMES_PER_MOVEMENT_TICK)
        return FALSE;
    tMovementFrame = 0;
    tMovementTick++;

    switch (tMovement)
    {
    case PIKACHU_MOVEMENT_SPIN:
    case PIKACHU_MOVEMENT_TURN:
        turns = tMovement == PIKACHU_MOVEMENT_SPIN ? 2 : 1;
        if (tMovementTick <= turns)
            TurnFollowerToward(sClockwise[follower->facingDirection]);
        return tMovementTick >= turns + 31;
    default:
        if (tMovement == PIKACHU_MOVEMENT_HOP_TWICE_FAST)
        {
            hopTicks = 8;
            angleStep = 4;
        }
        else
        {
            hopTicks = 16;
            angleStep = 2;
        }
        hopTick = (tMovementTick - 1) % hopTicks + 1;
        // 16 * sin(angle * pi / 32), upward
        sprite->y2 = -((16 * gSineTable[hopTick * angleStep * 4]) >> 8);
        if (tMovementTick >= hopTicks * 2)
        {
            sprite->y2 = 0;
            return TRUE;
        }
        return FALSE;
    }
}

static void DrawPortraitFrame(u8 taskId, u8 frame)
{
    u8 windowId = gTasks[taskId].tWindowId;
    bool8 firstFrame = !gTasks[taskId].tWindowShown;

    // The window only goes on screen once it has a frame to show, so it never flashes blank.
    // Its border is drawn first because drawing the border clears the window.
    if (firstFrame)
    {
        PutWindowTilemap(windowId);
        SetStdWindowBorderStyle(windowId, FALSE);
        gTasks[taskId].tWindowShown = TRUE;
    }
    BlitBitmapRectToWindow(windowId, sPortraitSheet,
                           (frame % PIKACHU_PORTRAIT_FRAMES_PER_ROW) * PORTRAIT_SIZE,
                           (frame / PIKACHU_PORTRAIT_FRAMES_PER_ROW) * PORTRAIT_SIZE,
                           PORTRAIT_SHEET_WIDTH, PORTRAIT_SIZE * PIKACHU_PORTRAIT_SHEET_ROWS,
                           0, 0, PORTRAIT_SIZE, PORTRAIT_SIZE);
    CopyWindowToVram(windowId, firstFrame ? COPYWIN_FULL : COPYWIN_GFX);
}

static void OpenPortraitWindow(u8 taskId, u8 portrait)
{
    struct WindowTemplate template = SetWindowTemplateFields(0, 12, 5, 5, 5, PORTRAIT_PALETTE, 0x038);
    u8 windowId = AddWindow(&template);

    gTasks[taskId].tWindowId = windowId;
    LoadPalette(sPortraitPalette, BG_PLTT_ID(PORTRAIT_PALETTE), PLTT_SIZE_4BPP);
    FillWindowPixelBuffer(windowId, PIXEL_FILL(1));
    gTasks[taskId].tWindowShown = FALSE;
    sPortraitCmd = sPikachuPortraits[portrait];
    gTasks[taskId].tPortraitTicks = 0;
}

static void ClosePortraitWindow(u8 taskId)
{
    u8 windowId = gTasks[taskId].tWindowId;

    if (gTasks[taskId].tWindowShown)
    {
        ClearWindowTilemap(windowId);
        ClearStdWindowAndFrameToTransparent(windowId, TRUE);
    }
    RemoveWindow(windowId);
}

static void Task_StarterPikachuEmotion(u8 taskId)
{
    s16 *data = gTasks[taskId].data;
    u8 op, arg;

    switch (tState)
    {
    case STATE_NEXT_COMMAND:
        op = *sEmotionCmd++;
        if (op == PIKAEMOTE_END)
        {
            DestroyTask(taskId);
            ScriptContext_Enable();
            return;
        }
        arg = *sEmotionCmd++;
        switch (op)
        {
        case PIKAEMOTE_BUBBLE:
            CreateEmoteBubble(taskId, arg);
            tTimer = BUBBLE_FRAMES;
            tState = STATE_WAIT_BUBBLE;
            break;
        case PIKAEMOTE_VOICE:
            PlayPikachuVoice(arg, sPikachuVoiceLengths[arg]);
            tState = STATE_WAIT_VOICE;
            break;
        case PIKAEMOTE_MOVEMENT:
            tMovement = arg;
            tMovementTick = 0;
            tMovementFrame = 0;
            tState = STATE_MOVEMENT;
            break;
        case PIKAEMOTE_PORTRAIT:
            OpenPortraitWindow(taskId, arg);
            tState = STATE_PORTRAIT_NEXT;
            break;
        case PIKAEMOTE_TURN_AWAY:
            TurnFollowerAwayFromPlayer();
            break;
        case PIKAEMOTE_WAIT_BUTTON:
            tState = STATE_WAIT_BUTTON;
            break;
        case PIKAEMOTE_TURN_AWAY_IF_ASLEEP_IN_POKECENTER:
            if (IsPlayerInMap(MAP_PEWTER_CITY_POKEMON_CENTER_1F))
                TurnFollowerAwayFromPlayer();
            break;
        case PIKAEMOTE_TURN_AWAY_IF_IN_FAN_CLUB:
            if (IsPlayerInMap(MAP_VERMILION_CITY_POKEMON_FAN_CLUB))
                TurnFollowerAwayFromPlayer();
            break;
        }
        break;
    case STATE_WAIT_BUBBLE:
        if (--tTimer == 0)
        {
            DestroyEmoteBubble(taskId);
            tState = STATE_NEXT_COMMAND;
        }
        break;
    case STATE_WAIT_VOICE:
        if (IsCryFinished())
            tState = STATE_NEXT_COMMAND;
        break;
    case STATE_MOVEMENT:
        if (UpdatePikachuMovement(taskId))
            tState = STATE_NEXT_COMMAND;
        break;
    case STATE_WAIT_BUTTON:
        if (JOY_NEW(A_BUTTON | B_BUTTON))
            tState = STATE_NEXT_COMMAND;
        break;
    case STATE_PORTRAIT_NEXT:
        switch (sPortraitCmd->op)
        {
        case PORTRAIT_OP_END:
            tState = STATE_PORTRAIT_CLOSE;
            break;
        case PORTRAIT_OP_FRAME:
            DrawPortraitFrame(taskId, sPortraitCmd->arg);
            tTimer = sPortraitCmd->ticks * FRAMES_PER_PORTRAIT_TICK;
            tState = STATE_PORTRAIT_SHOW_FRAME;
            break;
        case PORTRAIT_OP_VOICE:
            // Yellow's voice clips stop everything else while they play.
            PlayPikachuVoice(sPortraitCmd->arg, sPikachuVoiceLengths[sPortraitCmd->arg]);
            tState = STATE_PORTRAIT_WAIT_VOICE;
            break;
        case PORTRAIT_OP_THUNDERBOLT:
            PlaySE(SE_M_THUNDERBOLT);
            tFlashes = 0;
            tTimer = 0;
            tState = STATE_PORTRAIT_THUNDERBOLT;
            break;
        }
        sPortraitCmd++;
        break;
    case STATE_PORTRAIT_SHOW_FRAME:
        // Like Yellow, A or B closes the portrait early (but not on its first tick).
        if (tPortraitTicks > 0 && JOY_NEW(A_BUTTON | B_BUTTON))
        {
            tState = STATE_PORTRAIT_CLOSE;
            break;
        }
        if (--tTimer % FRAMES_PER_PORTRAIT_TICK == 0)
            tPortraitTicks++;
        if (tTimer <= 0)
            tState = STATE_PORTRAIT_NEXT;
        break;
    case STATE_PORTRAIT_WAIT_VOICE:
        if (IsCryFinished())
            tState = STATE_PORTRAIT_NEXT;
        break;
    case STATE_PORTRAIT_THUNDERBOLT:
        // The screen flashes every 4 frames, 10 times.
        if (tFlashes < 20)
        {
            if (tTimer++ % 4 == 0)
            {
                BlendPalettes(PALETTES_BG, (tFlashes % 2 == 0) ? 12 : 0, RGB_WHITE);
                tFlashes++;
            }
        }
        else if (!IsSEPlaying())
        {
            BlendPalettes(PALETTES_BG, 0, RGB_WHITE);
            tState = STATE_PORTRAIT_NEXT;
        }
        break;
    case STATE_PORTRAIT_CLOSE:
        ClosePortraitWindow(taskId);
        tState = STATE_NEXT_COMMAND;
        break;
    }
}

void PlayStarterPikachuVoice(u8 voiceId)
{
    PlayPikachuVoice(voiceId, sPikachuVoiceLengths[voiceId]);
}

// Special for talking to the following PIKACHU; the script waits with waitstate.
void DoStarterPikachuEmotion(void)
{
    u8 taskId;

    sEmotionCmd = sPikachuEmotions[ChooseStarterPikachuEmotion()];
    taskId = CreateTask(Task_StarterPikachuEmotion, 80);
    gTasks[taskId].tState = STATE_NEXT_COMMAND;
    gTasks[taskId].tBubbleSpriteId = MAX_SPRITES;
}
