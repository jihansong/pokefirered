#ifndef GUARD_CONSTANTS_FLAGS_JOHTO_STORY_H
#define GUARD_CONSTANTS_FLAGS_JOHTO_STORY_H
// Existing hoennFlags reservation. No SaveBlock fields or offsets change.
#define JOHTO_STORY_FLAGS_START (HOENN_FLAGS_START + 0x500)
#define FLAG_JOHTO_ARRIVAL_BRIEFED (JOHTO_STORY_FLAGS_START + 0)
#define FLAG_JOHTO_MET_LAB_ASSISTANT (JOHTO_STORY_FLAGS_START + 1)
#if JOHTO_STORY_FLAGS_START + 1 > HOENN_FLAGS_END
#error Johto story flags exceed the existing Hoenn flag array
#endif
#endif
