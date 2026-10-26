#ifndef GUARD_HOENN_PUZZLES_H
#define GUARD_HOENN_PUZZLES_H

void HoennSootopolisResetIce(void);
void HoennSootopolisRestoreIce(void);
void HoennSootopolisIceStep(u8 taskId);
void HoennSkyPillarRestoreFloor(void);
void HoennSkyPillarFloorStep(u8 taskId);
bool8 HoennSkyPillarBikeMove(u8 direction);
void HoennSkyPillarBikeReset(void);
bool8 HoennSkyPillarBikeAtFullSpeed(void);
bool8 TryStartHoennSkyPillarHoleScript(u16 behavior);
void HoennSeafloorMarkPuzzleSave(void);
bool8 HoennSeafloorHasPuzzleSave(void);

#endif
