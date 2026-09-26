#include "global.h"
#include "battle_setup.h"
#include "daycare.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "field_camera.h"
#include "item.h"
#include "money.h"
#include "script.h"
#include "script_pokemon_util.h"
#include "sound.h"
#include "sprite.h"
#include "string_util.h"
#include "task.h"
#include "text.h"
#include "constants/flags.h"
#include "constants/items.h"
#include "constants/opponents.h"
#include "constants/pokemon.h"
#include "constants/rocket_trio.h"
#include "constants/songs.h"
#include "constants/species.h"
#include "constants/vars.h"

// JESSIE, JAMES and MEOWTH blasting off after a defeat: a bang, the screen shakes, and
// the three of them fly up and out of sight, each drifting its own way, ending on a
// twinkle. VAR_0x8008, VAR_0x8009 and VAR_0x800A hold their local ids (0 for one who
// is not there). The script waits (waitstate) until they are gone, then removes the
// objects itself (removeobject), which keeps them hidden.

#define BLAST_OFF_FRAMES 48
#define SHAKE_FRAMES     16
#define NUM_TRIO          3

#define tTimer   data[0]
#define tObjId   data[1]     // data[1..3]

static void Task_RocketTrioBlastOff(u8 taskId);

static const s8 sDrift[NUM_TRIO] = {-1, 1, 0};

void RocketTrioBlastOff(void)
{
    u16 localIds[NUM_TRIO] = {gSpecialVar_0x8008, gSpecialVar_0x8009, gSpecialVar_0x800A};
    u8 taskId = CreateTask(Task_RocketTrioBlastOff, 80);
    u8 objectEventId;
    u8 i;

    for (i = 0; i < NUM_TRIO; i++)
    {
        gTasks[taskId].data[1 + i] = OBJECT_EVENTS_COUNT;
        if (localIds[i] != 0
         && !TryGetObjectEventIdByLocalIdAndMap(localIds[i], gSaveBlock1Ptr->location.mapNum, gSaveBlock1Ptr->location.mapGroup, &objectEventId))
            gTasks[taskId].data[1 + i] = objectEventId;
    }
    SetCameraPanningCallback(NULL);
    PlaySE(SE_M_EXPLOSION);
}

static void Task_RocketTrioBlastOff(u8 taskId)
{
    struct Task *task = &gTasks[taskId];
    struct Sprite *sprite;
    u8 i;

    task->tTimer++;
    if (task->tTimer <= SHAKE_FRAMES)
    {
        s16 shake = (task->tTimer & 2) ? 2 : -2;
        SetCameraPanning(shake, shake);
        if (task->tTimer == SHAKE_FRAMES)
        {
            SetCameraPanning(0, 0);
            InstallCameraPanAheadCallback();
        }
    }
    for (i = 0; i < NUM_TRIO; i++)
    {
        if (task->data[1 + i] >= OBJECT_EVENTS_COUNT)
            continue;
        sprite = &gSprites[gObjectEvents[task->data[1 + i]].spriteId];
        // slow at first, then faster and faster
        sprite->y2 -= 1 + task->tTimer / 12;
        if (task->tTimer & 1)
            sprite->x2 += sDrift[i];
        if (task->tTimer == BLAST_OFF_FRAMES)
            sprite->invisible = TRUE;
    }
    if (task->tTimer == BLAST_OFF_FRAMES)
    {
        PlaySE(SE_SHINY);   // the twinkle as they vanish into the sky
        DestroyTask(taskId);
        ScriptContext_Enable();
    }
}

// v0.9.0: which of the trio's rewards the player has had (constants/rocket_trio.h).
// Scripts have no bit operations, so these take the bit in VAR_0x8004: 0..15
// are VAR_ROCKET_BONUS_GIVEN, 16..31 are VAR_ROCKET_REWARD_HELD.
static u16 *GetRocketRewardVar(u16 *mask)
{
    u16 bit = gSpecialVar_0x8004;

    if (bit >= ROCKET_HELD_FIRST)
    {
        *mask = 1 << ((bit - ROCKET_HELD_FIRST) & 15);
        return GetVarPointer(VAR_ROCKET_REWARD_HELD);
    }
    *mask = 1 << (bit & 15);
    return GetVarPointer(VAR_ROCKET_BONUS_GIVEN);
}

void CheckRocketRewardBit(void)
{
    u16 mask;

    gSpecialVar_Result = (*GetRocketRewardVar(&mask) & mask) != 0;
}

void SetRocketRewardBit(void)
{
    u16 mask;

    *GetRocketRewardVar(&mask) |= mask;
}

void ClearRocketRewardBit(void)
{
    u16 mask;

    *GetRocketRewardVar(&mask) &= ~mask;
}

// MEOWTH's PAY DAY coins: VAR_0x8004 of them (addmoney takes only a constant).
// The script opens the money box first and updates it after this, so the
// player sees the amount go up.
void AddRocketMeowthCoins(void)
{
    AddMoney(&gSaveBlock1Ptr->money, gSpecialVar_0x8004);
}

// The OFFICER at the VIRIDIAN POKéMON CENTER hands over the trio's rewards a
// save is owed: new ones for events played before v0.9.0 (bonus bit clear)
// and old ones the bag had no room for (held bit set). This special gives
// them all at once, in event order: each item that fits goes into the bag and
// each EGG that fits into the party or the PC, and is marked; one that doesn't
// stays owed, and the rest still go on. Out:
//   gRocketOfficerText  "PLAYER received: A, B ×2, EGG ×2!" wrapped to the
//                       message box (\n, then \l), for the script to print
//                       once, plus a line when an EGG went to the PC
//   VAR_0x8005          how many rewards were handed over
//   VAR_0x8006          TRUE if the bag had no room for an item
//   VAR_0x8007          TRUE if the party and PC had no room for an EGG

#define OFFICER_TEXT_WIDTH 208      // the field message box
#define OFFICER_MAX_KINDS  20
#define OFFICER_EGG        ITEM_NONE    // stands for an EGG in the list

enum {
    REWARD_IF_FLAG,         // the event's flag is set
    REWARD_IF_BEATEN,       // the trio's trainer there has been beaten
    REWARD_IF_MEW_GONE,     // NEW ISLAND: RARE CANDY when MEW is gone...
    REWARD_IF_MEW_HERE,     // ...or the MEW EGG while MEW is under the truck
    REWARD_HELD,            // an old reward: owed only while its held bit is set
};

struct RocketReward
{
    u8 bit;
    u8 test;
    u16 id;                 // the flag or trainer the test reads
    u16 item;               // OFFICER_EGG: count is 0, the EGG is given apart
    u8 count;
};

static const struct RocketReward sRocketRewards[] =
{
    {ROCKET_BONUS_WATER_STONE,    REWARD_IF_FLAG,     FLAG_ROCKET_CERULEAN_GYM,            ITEM_WATER_STONE,   1},
    {ROCKET_BONUS_SS_ANNE_CANDY,  REWARD_IF_FLAG,     FLAG_ROCKET_SS_ANNE,                 ITEM_RARE_CANDY,    1},
    {ROCKET_BONUS_THUNDER_STONE,  REWARD_IF_BEATEN,   TRAINER_JESSIE_JAMES_ROCKET_HIDEOUT, ITEM_THUNDER_STONE, 1},
    {ROCKET_BONUS_CLEANSE_TAG,    REWARD_IF_BEATEN,   TRAINER_JESSIE_JAMES_POKEMON_TOWER,  ITEM_CLEANSE_TAG,   1},
    {ROCKET_BONUS_LEAF_STONE,     REWARD_IF_FLAG,     FLAG_ROCKET_CELADON_GYM,             ITEM_LEAF_STONE,    1},
    {ROCKET_BONUS_UP_GRADE,       REWARD_IF_BEATEN,   TRAINER_JESSIE_JAMES_SILPH_CO,       ITEM_UP_GRADE,      1},
    {ROCKET_BONUS_DRAGON_SCALE,   REWARD_IF_FLAG,     FLAG_ROCKET_SAFARI_DRATINI,          ITEM_DRAGON_SCALE,  1},
    {ROCKET_BONUS_CINNABAR_CANDY, REWARD_IF_FLAG,     FLAG_ROCKET_CINNABAR,                ITEM_RARE_CANDY,    2},
    {ROCKET_BONUS_GYM_CANDY,      REWARD_IF_FLAG,     FLAG_ROCKET_VIRIDIAN_GYM,            ITEM_RARE_CANDY,    3},
    {ROCKET_BONUS_EEVEE_EGG,      REWARD_IF_FLAG,     FLAG_ROCKET_VIRIDIAN_GYM,            OFFICER_EGG,        0},
    {ROCKET_BONUS_FIRE_STONE,     REWARD_IF_FLAG,     FLAG_ROCKET_INDIGO_TORCH,            ITEM_FIRE_STONE,    1},
    {ROCKET_BONUS_NEW_ISLAND,     REWARD_IF_MEW_GONE, FLAG_ROCKET_NEW_ISLAND,              ITEM_RARE_CANDY,    3},
    {ROCKET_BONUS_NEW_ISLAND,     REWARD_IF_MEW_HERE, FLAG_ROCKET_NEW_ISLAND,              OFFICER_EGG,        0},
    {ROCKET_HELD_MYSTIC_WATER,    REWARD_HELD,        0,                                   ITEM_MYSTIC_WATER,  1},
    {ROCKET_HELD_NUGGET,          REWARD_HELD,        0,                                   ITEM_NUGGET,        1},
    {ROCKET_HELD_MIRACLE_SEED,    REWARD_HELD,        0,                                   ITEM_MIRACLE_SEED,  1},
    {ROCKET_HELD_DRAGON_FANG,     REWARD_HELD,        0,                                   ITEM_DRAGON_FANG,   1},
    {ROCKET_HELD_FULL_RESTORE,    REWARD_HELD,        0,                                   ITEM_FULL_RESTORE,  1},
    {ROCKET_HELD_CARGO_TAG,       REWARD_HELD,        0,                                   ITEM_CARGO_TAG,     1},
};

static const u8 sText_Received[] = _(" received:");
static const u8 sText_Space[] = _(" ");
static const u8 sText_Times[] = _(" ×");
static const u8 sText_Egg[] = _("EGG");
static const u8 sText_EggToPC[] = _("(The EGG went to the PC.)");
static const u8 sText_EggsToPC[] = _("(The EGGS went to the PC.)");

EWRAM_DATA u8 gRocketOfficerText[256] = {0};

static bool8 IsRocketRewardOwed(const struct RocketReward *reward)
{
    u16 mask;
    bool8 bitSet;

    gSpecialVar_0x8004 = reward->bit;
    bitSet = (*GetRocketRewardVar(&mask) & mask) != 0;
    switch (reward->test)
    {
    case REWARD_HELD:
        return bitSet;
    case REWARD_IF_BEATEN:
        return !bitSet && HasTrainerBeenFought(reward->id);
    case REWARD_IF_MEW_GONE:
        return !bitSet && FlagGet(reward->id) && FlagGet(FLAG_FOUGHT_MEW);
    case REWARD_IF_MEW_HERE:
        return !bitSet && FlagGet(reward->id) && !FlagGet(FLAG_FOUGHT_MEW);
    default:
        return !bitSet && FlagGet(reward->id);
    }
}

// Adds a word to the text, on a new line when it would not fit on this one.
static u8 *AppendOfficerWord(u8 *end, const u8 *word, u16 *lineWidth, u8 *lines)
{
    u16 width = GetStringWidth(FONT_NORMAL, word, 0);
    u16 space = GetStringWidth(FONT_NORMAL, sText_Space, 0);

    if (*lineWidth + space + width > OFFICER_TEXT_WIDTH)
    {
        *end++ = (*lines == 0) ? CHAR_NEWLINE : CHAR_PROMPT_SCROLL;
        (*lines)++;
        *lineWidth = 0;
    }
    else
    {
        end = StringCopy(end, sText_Space);
        *lineWidth += space;
    }
    end = StringCopy(end, word);
    *lineWidth += width;
    return end;
}

void GiveRocketOfficerRewards(void)
{
    u16 kindItem[OFFICER_MAX_KINDS];
    u8 kindCount[OFFICER_MAX_KINDS];
    u8 word[ITEM_NAME_LENGTH + 8];
    u8 kinds = 0, given = 0, lines = 0, eggsToPC = 0;
    u16 lineWidth;
    bool8 bagFull = FALSE, boxesFull = FALSE;
    u8 *end, *w;
    u8 i, j;

    for (i = 0; i < ARRAY_COUNT(sRocketRewards); i++)
    {
        const struct RocketReward *reward = &sRocketRewards[i];

        if (!IsRocketRewardOwed(reward))
            continue;
        if (reward->item == OFFICER_EGG)
        {
            u8 result = (reward->bit == ROCKET_BONUS_NEW_ISLAND) ? GiveMewEgg() : ScriptGiveEgg(SPECIES_EEVEE);

            if (result == MON_CANT_GIVE)
            {
                boxesFull = TRUE;
                continue;
            }
            if (result == MON_GIVEN_TO_PC)
                eggsToPC++;
            if (reward->bit == ROCKET_BONUS_NEW_ISLAND)
            {
                // one MEW per game: none under the VERMILION truck any more
                FlagSet(FLAG_FOUGHT_MEW);
                FlagSet(FLAG_GOT_MEW_EGG);
            }
        }
        else if (!AddBagItem(reward->item, reward->count))
        {
            bagFull = TRUE;
            continue;
        }
        gSpecialVar_0x8004 = reward->bit;
        if (reward->test == REWARD_HELD)
            ClearRocketRewardBit();
        else
            SetRocketRewardBit();
        given++;
        // the same item from several events is listed once, with the total
        for (j = 0; j < kinds && kindItem[j] != reward->item; j++)
            ;
        if (j == kinds)
        {
            kindItem[kinds] = reward->item;
            kindCount[kinds++] = 0;
        }
        kindCount[j] += (reward->item == OFFICER_EGG) ? 1 : reward->count;
    }

    end = StringCopy(gRocketOfficerText, gSaveBlock2Ptr->playerName);
    end = StringCopy(end, sText_Received);
    lineWidth = GetStringWidth(FONT_NORMAL, gRocketOfficerText, 0);
    for (i = 0; i < kinds; i++)
    {
        if (kindItem[i] == OFFICER_EGG)
            StringCopy(word, sText_Egg);
        else
            CopyItemName(kindItem[i], word);
        w = word + StringLength(word);
        if (kindCount[i] > 1)
        {
            w = StringCopy(w, sText_Times);
            w = ConvertIntToDecimalStringN(w, kindCount[i], STR_CONV_MODE_LEFT_ALIGN, 2);
        }
        *w++ = (i == kinds - 1) ? CHAR_EXCL_MARK : CHAR_COMMA;
        *w = EOS;
        end = AppendOfficerWord(end, word, &lineWidth, &lines);
    }
    if (eggsToPC != 0)
    {
        *end++ = (lines == 0) ? CHAR_NEWLINE : CHAR_PROMPT_SCROLL;
        end = StringCopy(end, eggsToPC > 1 ? sText_EggsToPC : sText_EggToPC);
    }
    *end = EOS;

    gSpecialVar_0x8005 = given;
    gSpecialVar_0x8006 = bagFull;
    gSpecialVar_0x8007 = boxesFull;
}
