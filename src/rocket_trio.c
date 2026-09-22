#include "global.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "field_camera.h"
#include "script.h"
#include "sound.h"
#include "sprite.h"
#include "task.h"
#include "constants/songs.h"

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
