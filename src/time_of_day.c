#include "global.h"
#include "event_data.h"
#include "rtc.h"
#include "time_of_day.h"
#include "constants/flags.h"
#include "constants/songs.h"
#include "menu.h"
#include "new_menu_helpers.h"
#include "script.h"
#include "sound.h"
#include "string_util.h"
#include "task.h"
#include "text.h"
#include "window.h"
#include "gflib.h"
#include "overworld.h"
#include "fieldmap.h"
#include "constants/rgb.h"

// Roadmap 2, event 9: a game clock with morning, day and night.
//
// If the cartridge (or emulator) has a working real-time clock, the clock is
// the RTC plus gSaveBlock2Ptr->localTimeOffset, as in R/S/E. FR/LG carts have
// no RTC, so otherwise a virtual clock runs from the play time: one real
// minute is six game minutes, so a game day lasts four real hours. Its offset
// lives in gSaveBlock2Ptr->lastBerryTreeUpdate, which FR/LG never used. Both
// fields already existed in the save block, so its layout is unchanged.

#define GAME_MINUTES_PER_PLAY_MINUTE 6
#define MINUTES_PER_DAY (24 * 60)

static bool8 sUseRtc;

// Reading the clock costs a division, or a serial read from the RTC on a cart
// that has one, and callers ask for it often (the wild encounter tables look it
// up per lookup). The answer only changes every few seconds of play, so it is
// cached and refreshed at most once a second.
#define CLOCK_CACHE_FRAMES 60

static struct Time sCachedTime;
static u32 sCacheStamp;
static bool8 sCacheValid;

void TimeOfDay_InvalidateCache(void)
{
    sCacheValid = FALSE;
}

void TimeOfDay_Init(void)
{
    sCacheValid = FALSE;
    RtcInit();
    sUseRtc = !(RtcGetErrorStatus() & (RTC_INIT_ERROR | RTC_ERR_FLAG_MASK));
}

bool8 TimeOfDay_UsesRtc(void)
{
    return sUseRtc;
}

static s32 GetVirtualClockMinutes(void)
{
    struct Time *offset = &gSaveBlock2Ptr->lastBerryTreeUpdate;
    s32 playMinutes = gSaveBlock2Ptr->playTimeHours * 60 + gSaveBlock2Ptr->playTimeMinutes;
    s32 minutes = playMinutes * GAME_MINUTES_PER_PLAY_MINUTE
                + gSaveBlock2Ptr->playTimeSeconds / (60 / GAME_MINUTES_PER_PLAY_MINUTE);

    minutes += offset->days * MINUTES_PER_DAY + offset->hours * 60 + offset->minutes;
    if (minutes < 0)
        minutes = 0;
    return minutes;
}

static void ReadGameClock(struct Time *time)
{
    if (sUseRtc)
    {
        RtcCalcLocalTime();
        *time = gLocalTime;
        if (time->days < 0)
            time->days = 0;
    }
    else
    {
        s32 minutes = GetVirtualClockMinutes();

        time->days = minutes / MINUTES_PER_DAY;
        time->hours = (minutes % MINUTES_PER_DAY) / 60;
        time->minutes = minutes % 60;
        time->seconds = 0;
    }
}

void GetGameClock(struct Time *time)
{
    u32 now = gMain.vblankCounter2;

    if (!sCacheValid || now - sCacheStamp >= CLOCK_CACHE_FRAMES)
    {
        ReadGameClock(&sCachedTime);
        sCacheStamp = now;
        sCacheValid = TRUE;
    }
    *time = sCachedTime;
}

u8 GetTimeOfDay(void)
{
    struct Time time;

    GetGameClock(&time);
    if (time.hours >= 4 && time.hours < 10)
        return TIME_MORNING;
    if (time.hours >= 10 && time.hours < 20)
        return TIME_DAY;
    return TIME_NIGHT;
}

u16 GetGameClockDay(void)
{
    struct Time time;

    GetGameClock(&time);
    return time.days;
}

u8 GetGameClockDayOfWeek(void)
{
    return GetGameClockDay() % DAYS_PER_WEEK;
}

bool8 IsGameClockSet(void)
{
    return FlagGet(FLAG_GAME_CLOCK_SET);
}

// Sets the clock to the given day of the week and time, never moving the day
// count backwards, so "once a day" records keep working.
void SetGameClock(u8 dayOfWeek, u8 hour, u8 minute)
{
    struct Time now;
    s32 days;

    TimeOfDay_InvalidateCache();
    GetGameClock(&now);
    days = now.days - now.days % DAYS_PER_WEEK + dayOfWeek;
    if (days < now.days)
        days += DAYS_PER_WEEK;

    if (sUseRtc)
    {
        RtcCalcLocalTimeOffset(days, hour, minute, 0);
    }
    else
    {
        struct Time *offset = &gSaveBlock2Ptr->lastBerryTreeUpdate;
        s32 target = days * MINUTES_PER_DAY + hour * 60 + minute;
        s32 current;

        offset->days = offset->hours = offset->minutes = offset->seconds = 0;
        current = GetVirtualClockMinutes();
        target -= current;
        offset->days = target / MINUTES_PER_DAY;
        target %= MINUTES_PER_DAY;
        offset->hours = target / 60;
        offset->minutes = target % 60;
    }
    FlagSet(FLAG_GAME_CLOCK_SET);
    TimeOfDay_InvalidateCache();
}

// ---------------------------------------------------------------------------
// Clock setting window: LEFT/RIGHT picks day, hour or minute, UP/DOWN changes
// it and A sets the clock. Used as a special with waitstate.

static const u8 sDayNameSun[] = _("SUN");
static const u8 sDayNameMon[] = _("MON");
static const u8 sDayNameTue[] = _("TUE");
static const u8 sDayNameWed[] = _("WED");
static const u8 sDayNameThu[] = _("THU");
static const u8 sDayNameFri[] = _("FRI");
static const u8 sDayNameSat[] = _("SAT");
static const u8 *const sDayNames[DAYS_PER_WEEK] = {
    sDayNameSun, sDayNameMon, sDayNameTue, sDayNameWed, sDayNameThu, sDayNameFri, sDayNameSat,
};
static const u8 sText_ClockHelp[] = _("{DPAD_UPDOWN}Change {DPAD_LEFTRIGHT}Move {A_BUTTON}Set");

static const struct WindowTemplate sClockWindowTemplate = {
    .bg = 0,
    .tilemapLeft = 7,
    .tilemapTop = 2,
    .width = 16,
    .height = 4,
    .paletteNum = 15,
    .baseBlock = 0x008
};

#define tField   data[0]
#define tDay     data[1]
#define tHour    data[2]
#define tMinute  data[3]
#define tWindow  data[4]

enum { CLOCK_FIELD_DAY, CLOCK_FIELD_HOUR, CLOCK_FIELD_MINUTE, CLOCK_FIELD_COUNT };

static void PrintClockWindow(struct Task *task)
{
    u8 *str = gStringVar4;
    u8 field;

    FillWindowPixelBuffer(task->tWindow, PIXEL_FILL(1));
    for (field = 0; field < CLOCK_FIELD_COUNT; field++)
    {
        if (field == task->tField)
            *str++ = CHAR_LEFT_ARROW;
        else
            *str++ = CHAR_SPACE;
        if (field == CLOCK_FIELD_DAY)
            str = StringCopy(str, sDayNames[task->tDay]);
        else
            str = ConvertIntToDecimalStringN(str, field == CLOCK_FIELD_HOUR ? task->tHour : task->tMinute, STR_CONV_MODE_LEADING_ZEROS, 2);
        if (field == task->tField)
            *str++ = CHAR_RIGHT_ARROW;
        else
            *str++ = CHAR_SPACE;
        if (field == CLOCK_FIELD_HOUR)
            *str++ = CHAR_COLON;
    }
    *str = EOS;
    AddTextPrinterParameterized(task->tWindow, FONT_NORMAL, gStringVar4, 8, 1, TEXT_SKIP_DRAW, NULL);
    AddTextPrinterParameterized(task->tWindow, FONT_SMALL, sText_ClockHelp, 4, 17, TEXT_SKIP_DRAW, NULL);
    CopyWindowToVram(task->tWindow, COPYWIN_GFX);
}

static void Task_SetGameClock(u8 taskId)
{
    struct Task *task = &gTasks[taskId];
    s16 delta = 0;

    if (JOY_NEW(A_BUTTON))
    {
        PlaySE(SE_SELECT);
        SetGameClock(task->tDay, task->tHour, task->tMinute);
        ClearStdWindowAndFrameToTransparent(task->tWindow, TRUE);
        RemoveWindow(task->tWindow);
        DestroyTask(taskId);
        ScriptContext_Enable();
        return;
    }
    if (JOY_NEW(DPAD_LEFT))
        task->tField = (task->tField + CLOCK_FIELD_COUNT - 1) % CLOCK_FIELD_COUNT;
    else if (JOY_NEW(DPAD_RIGHT))
        task->tField = (task->tField + 1) % CLOCK_FIELD_COUNT;
    else if (JOY_REPT(DPAD_UP))
        delta = 1;
    else if (JOY_REPT(DPAD_DOWN))
        delta = -1;
    else
        return;

    if (task->tField == CLOCK_FIELD_DAY)
        task->tDay = (task->tDay + DAYS_PER_WEEK + delta) % DAYS_PER_WEEK;
    else if (task->tField == CLOCK_FIELD_HOUR)
        task->tHour = (task->tHour + 24 + delta) % 24;
    else
        task->tMinute = (task->tMinute + 60 + delta) % 60;
    PlaySE(SE_SELECT);
    PrintClockWindow(task);
}

// Special: opens the clock window, starting from the current game time
void StartSetGameClock(void)
{
    struct Time now;
    u8 taskId = CreateTask(Task_SetGameClock, 80);
    struct Task *task = &gTasks[taskId];

    GetGameClock(&now);
    task->tField = CLOCK_FIELD_HOUR;
    task->tDay = now.days % DAYS_PER_WEEK;
    task->tHour = now.hours;
    task->tMinute = now.minutes;
    task->tWindow = AddWindow(&sClockWindowTemplate);
    DrawStdWindowFrame(task->tWindow, FALSE);
    PutWindowTilemap(task->tWindow);
    PrintClockWindow(task);
}

// Special: buffers the current day and time ("SUN 12:00") into STR_VAR_1 and
// the time of day into VAR_RESULT
void BufferGameClock(void)
{
    struct Time now;
    u8 *str;

    GetGameClock(&now);
    str = StringCopy(gStringVar1, sDayNames[now.days % DAYS_PER_WEEK]);
    *str++ = CHAR_SPACE;
    str = ConvertIntToDecimalStringN(str, now.hours, STR_CONV_MODE_LEADING_ZEROS, 2);
    *str++ = CHAR_COLON;
    ConvertIntToDecimalStringN(str, now.minutes, STR_CONV_MODE_LEADING_ZEROS, 2);
    gSpecialVar_Result = GetTimeOfDay();
}

// ---------------------------------------------------------------------------
// A small window in the top left corner with the day and time over the time of
// day ("SUN 12:34" / "NIGHT"). The start menu shows it next to the menu, and the
// POKéWATCH while the player reads it. It follows the clock while it is open:
// call UpdateGameClockWindow every frame, it only redraws when the minute changes.
// Only one is ever open, so one remembered minute serves both.

static const u8 sText_TimeMorning[] = _("MORNING");
static const u8 sText_TimeDay[] = _("DAY");
static const u8 sText_TimeNight[] = _("NIGHT");
static const u8 *const sTimeOfDayNames[] = {
    [TIME_MORNING] = sText_TimeMorning,
    [TIME_DAY]     = sText_TimeDay,
    [TIME_NIGHT]   = sText_TimeNight,
};

// Same place and tiles as the SAFARI ZONE's step and ball window, which the
// start menu shows instead there
static const struct WindowTemplate sGameClockWindowTemplate = {
    .bg = 0,
    .tilemapLeft = 1,
    .tilemapTop = 1,
    .width = 10,
    .height = 4,
    .paletteNum = 15,
    .baseBlock = 0x008
};

static s16 sGameClockWindowMinute;

void UpdateGameClockWindow(u8 windowId)
{
    struct Time now;
    u8 text[16];
    u8 *str;

    GetGameClock(&now);
    if (now.hours * 60 + now.minutes == sGameClockWindowMinute)
        return;
    sGameClockWindowMinute = now.hours * 60 + now.minutes;

    // Not gStringVar4: a message may be printing from it underneath
    str = StringCopy(text, sDayNames[now.days % DAYS_PER_WEEK]);
    *str++ = CHAR_SPACE;
    str = ConvertIntToDecimalStringN(str, now.hours, STR_CONV_MODE_LEADING_ZEROS, 2);
    *str++ = CHAR_COLON;
    ConvertIntToDecimalStringN(str, now.minutes, STR_CONV_MODE_LEADING_ZEROS, 2);
    FillWindowPixelBuffer(windowId, PIXEL_FILL(1));
    AddTextPrinterParameterized(windowId, FONT_NORMAL, text, 4, 1, TEXT_SKIP_DRAW, NULL);
    AddTextPrinterParameterized(windowId, FONT_NORMAL, sTimeOfDayNames[GetTimeOfDay()], 4, 16, TEXT_SKIP_DRAW, NULL);
    CopyWindowToVram(windowId, COPYWIN_GFX);
}

u8 AddGameClockWindow(void)
{
    u8 windowId = AddWindow(&sGameClockWindowTemplate);

    DrawStdWindowFrame(windowId, FALSE);
    sGameClockWindowMinute = -1;
    UpdateGameClockWindow(windowId);
    CopyWindowToVram(windowId, COPYWIN_FULL);
    return windowId;
}

void RemoveGameClockWindow(u8 windowId)
{
    ClearStdWindowAndFrameToTransparent(windowId, TRUE);
    RemoveWindow(windowId);
}

#define tWindowId data[0]

static void Task_PokeWatchWindow(u8 taskId)
{
    UpdateGameClockWindow(gTasks[taskId].tWindowId);
}

// Special: the POKéWATCH's clock window, open while its messages show
void OpenPokeWatchWindow(void)
{
    u8 taskId = CreateTask(Task_PokeWatchWindow, 80);

    gTasks[taskId].tWindowId = AddGameClockWindow();
}

// Special
void ClosePokeWatchWindow(void)
{
    u8 taskId = FindTaskIdByFunc(Task_PokeWatchWindow);

    if (taskId == TASK_NONE)
        return;
    RemoveGameClockWindow(gTasks[taskId].tWindowId);
    DestroyTask(taskId);
}

#undef tWindowId

// ---------------------------------------------------------------------------
// Outdoor maps take on a light warm tint in the morning and a dark blue one at
// night. Applied to palettes as the field loads them (the same place the
// Quest Log applies its sepia), so fades and weather start from the tinted
// colors. Returns FALSE if no tint applies now.
bool8 TintPaletteForTimeOfDay(u16 *palette, u16 count)
{
    u8 coeff;
    u16 color;

    if (!IsMapTypeOutdoors(gMapHeader.mapType))
        return FALSE;
    switch (GetTimeOfDay())
    {
    case TIME_MORNING:
        coeff = 3;
        color = RGB(31, 24, 14);
        break;
    case TIME_NIGHT:
        coeff = 7;
        color = RGB(2, 3, 12);
        break;
    default:
        return FALSE;
    }
    while (count--)
    {
        s32 r = GET_R(*palette), g = GET_G(*palette), b = GET_B(*palette);

        r += ((GET_R(color) - r) * coeff) >> 4;
        g += ((GET_G(color) - g) * coeff) >> 4;
        b += ((GET_B(color) - b) * coeff) >> 4;
        *palette++ = RGB(r, g, b);
    }
    return TRUE;
}
