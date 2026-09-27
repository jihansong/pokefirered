#ifndef GUARD_INTRO_OPENING_H
#define GUARD_INTRO_OPENING_H

// The Thunder Yellow opening: the thirteen cuts that follow the GAME FREAK logo
// (src/intro_opening.c). src/intro.c calls Opening_Init once, then Opening_Run
// once a frame until it returns 0, and Opening_Free when it leaves for the title
// screen (also when the player skips).

void Opening_Init(void);
u8 Opening_Run(void);   // the cut on screen (1-13), 0 once the opening is over
void Opening_Free(void);

#endif // GUARD_INTRO_OPENING_H
