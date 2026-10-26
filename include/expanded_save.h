#ifndef GUARD_EXPANDED_SAVE_H
#define GUARD_EXPANDED_SAVE_H

#include "global.h"

#define EXPANDED_SAVE_SIGNATURE       0x38325954
#define EXPANDED_SAVE_COMMIT_MAGIC    0x43535954
#define EXPANDED_SAVE_VERSION         1
#define EXPANDED_SAVE_SECTOR_COUNT    23
#define EXPANDED_SAVE_EXTRA_START     14
#define EXPANDED_SAVE_COMMIT_SECTOR   27
#define EXPANDED_SAVE_COMMIT_ID       0xFFFE
#define EXPANDED_SAVE_COMMIT_BEGIN    0
#define EXPANDED_SAVE_COMMIT_COMPLETE 1
#define EXPANDED_SAVE_LEGACY_PC_SIZE  33744
#define EXPANDED_SAVE_EXTRA_PC_SIZE   33740

struct ExpandedSaveCommit
{
    u32 magic;
    u32 version;
    u32 sectorCount;
    u32 counter;
    u32 state;
    u32 aggregateSum;
    u32 legacySize;
    u32 extraSize;
};

STATIC_ASSERT(sizeof(struct ExpandedSaveCommit) == 32, ExpandedSaveCommitSize);

#endif
