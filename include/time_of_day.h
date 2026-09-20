#ifndef GUARD_TIME_OF_DAY_H
#define GUARD_TIME_OF_DAY_H

#include "constants/time_of_day.h"

void TimeOfDay_Init(void);
void TimeOfDay_InvalidateCache(void);
bool8 TimeOfDay_UsesRtc(void);
void GetGameClock(struct Time *time);
u8 GetTimeOfDay(void);
u16 GetGameClockDay(void);
u8 GetGameClockDayOfWeek(void);
void SetGameClock(u8 dayOfWeek, u8 hour, u8 minute);
bool8 IsGameClockSet(void);
bool8 TintPaletteForTimeOfDay(u16 *palette, u16 count);

#endif // GUARD_TIME_OF_DAY_H
