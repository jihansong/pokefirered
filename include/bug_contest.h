#ifndef GUARD_BUG_CONTEST_H
#define GUARD_BUG_CONTEST_H

#include "constants/bug_contest.h"

bool8 IsBugContestActiveInForest(void);
bool8 TryGenerateBugContestMon(void);
bool8 TryStartBugContestTimeUpScript(void);
void BugContest_AfterWildBattle(void);
void BugContest_OnWhiteOut(void);

#endif // GUARD_BUG_CONTEST_H
