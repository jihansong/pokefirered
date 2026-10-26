#ifndef GUARD_ROTATING_GATE_H
#define GUARD_ROTATING_GATE_H

void RotatingGate_InitPuzzle(void);
void RotatingGate_InitPuzzleAndGraphics(void);
void RotatingGatePuzzleCameraUpdate(s16 deltaX, s16 deltaY);
bool32 CheckForRotatingGatePuzzleCollision(u8 direction, s16 x, s16 y);
bool32 CheckForRotatingGatePuzzleCollisionWithoutAnimation(u8 direction, s16 x, s16 y);
void RotatingGate_Cleanup(void);

#endif // GUARD_ROTATING_GATE_H