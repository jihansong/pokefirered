#ifndef GUARD_HOENN_SPACE_STORY_H
#define GUARD_HOENN_SPACE_STORY_H

enum SpaceMissionPhase
{
    SPACE_MISSION_NOT_STARTED,
    SPACE_MISSION_BOARDING,
    SPACE_MISSION_IN_FLIGHT,
    SPACE_MISSION_SYSTEMS_READY,
    SPACE_MISSION_RECORDS_READY,
    SPACE_MISSION_LANDED,
    SPACE_MISSION_REPORTED,
};

void HoennSpaceStory_GetPhase(void);
void HoennSpaceStory_PlayFlight(void);
void HoennSpaceStory_CheckJirachiCaught(void);

#endif
