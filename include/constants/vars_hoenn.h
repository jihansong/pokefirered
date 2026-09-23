#ifndef GUARD_CONSTANTS_VARS_HOENN_H
#define GUARD_CONSTANTS_VARS_HOENN_H

// Vars for the Hoenn story, numbered past VARS_END and stored in
// gSaveBlock2Ptr->hoennVars (see GetVarPointer). Adding names here never moves
// anything in the save, so old saves keep loading.

#define VAR_HOENN_STAGE1_PROGRESS      (HOENN_VARS_START + 0)  // 카이나 1단계 전체 진행도 (0=도착 전, 7=1단계 완료)
#define VAR_HOENN_SCENE_HARBOR         (HOENN_VARS_START + 1)  // 이벤트 1 항구 도착과 안내
#define VAR_HOENN_SCENE_MUSEUM         (HOENN_VARS_START + 2)  // 이벤트 2 해양박물관 소동
#define VAR_HOENN_SCENE_DEWFORD_GYM    (HOENN_VARS_START + 3)  // 이벤트 3 Dewford 체육관
#define VAR_HOENN_SCENE_GRANITE_CAVE   (HOENN_VARS_START + 4)  // 이벤트 4 Granite Cave의 성호
#define VAR_HOENN_SCENE_SHIP           (HOENN_VARS_START + 5)  // 이벤트 5 버려진 배의 스캐너
#define VAR_HOENN_ROUTE109_BROTHERS    (HOENN_VARS_START + 6)  // 이벤트 6 바닷가 집 3연전에서 이긴 수
#define VAR_HOENN_PIKACHU_SCENES       (HOENN_VARS_START + 7)  // 이벤트 7 피카츄 분기 3곳을 본 기록 (비트 0~2)
#define VAR_HOENN_RUMOR_STATE          (HOENN_VARS_START + 8)  // 카이나 소문 수집가가 말할 다음 소문
#define VAR_HOENN_STERN_REQUEST        (HOENN_VARS_START + 9)  // STERN 선장 의뢰 단계
#define VAR_HOENN_DEEP_SEA_ITEM        (HOENN_VARS_START + 10)  // 심해 도구 선택 기록 (0=미선택, 1=이빨, 2=비늘)
#define VAR_HOENN_BADGE_NPC_STATE      (HOENN_VARS_START + 11)  // 배지 기록처 NPC가 마지막으로 알려 준 배지 수

// Still free: the rest of the block, named so scripts can use them as they go.
#define VAR_HOENN_MAUVILLE_GYM_STATE   (HOENN_VARS_START + 12)  // 무한 체육관 배리어 퍼즐: 마지막으로 밟은 스위치(0~4)
#define VAR_HOENN_SCENE_MAUVILLE       (HOENN_VARS_START + 13)  // 2단계 무한시티 진행
#define VAR_HOENN_CYCLING_RECORD       (HOENN_VARS_START + 14)  // 자전거 도로 최고 기록(초)
#define VAR_HOENN_CYCLING_STATE        (HOENN_VARS_START + 15)  // 타임트라이얼 상태(0 없음, 1 달리는 중)
#define VAR_HOENN_TRICK_HOUSE_STAGE    (HOENN_VARS_START + 16)  // 트릭하우스 진행(0~8)
#define VAR_HOENN_TRICK_HOUSE_FOUND    (HOENN_VARS_START + 17)  // 이번 퍼즐에서 트릭 마스터를 찾았는지
#define VAR_HOENN_NEW_MAUVILLE_STATE   (HOENN_VARS_START + 18)  // 뉴 무한 발전기 진행
#define VAR_HOENN_TRICK_BEING_WATCHED_STATE (HOENN_VARS_START + 19)  // 트릭하우스
#define VAR_HOENN_TRICK_ENTER_FROM_CORRIDOR (HOENN_VARS_START + 20)  // 트릭하우스
#define VAR_HOENN_TRICK_ENTRANCE_STATE (HOENN_VARS_START + 21)  // 트릭하우스
#define VAR_HOENN_TRICK_FOUND_TRICK_MASTER (HOENN_VARS_START + 22)  // 트릭하우스
#define VAR_HOENN_TRICK_LEVEL          (HOENN_VARS_START + 23)  // 트릭하우스
#define VAR_HOENN_TRICK_PRIZE_PICKUP   (HOENN_VARS_START + 24)  // 트릭하우스
#define VAR_HOENN_TRICK_PUZZLE_1_STATE (HOENN_VARS_START + 25)  // 트릭하우스
#define VAR_HOENN_TRICK_PUZZLE_2_STATE (HOENN_VARS_START + 26)  // 트릭하우스
#define VAR_HOENN_TRICK_PUZZLE_3_STATE (HOENN_VARS_START + 27)  // 트릭하우스
#define VAR_HOENN_TRICK_PUZZLE_4_STATE (HOENN_VARS_START + 28)  // 트릭하우스
#define VAR_HOENN_TRICK_PUZZLE_5_STATE (HOENN_VARS_START + 29)  // 트릭하우스
#define VAR_HOENN_TRICK_PUZZLE_6_STATE (HOENN_VARS_START + 30)  // 트릭하우스
#define VAR_HOENN_TRICK_PUZZLE_7_STATE (HOENN_VARS_START + 31)  // 트릭하우스
#define VAR_HOENN_TRICK_PUZZLE_7_STATE_2 (HOENN_VARS_START + 32)  // 트릭하우스
#define VAR_HOENN_TRICK_PUZZLE_8_STATE (HOENN_VARS_START + 33)  // 트릭하우스
#define VAR_HOENN_CYCLING_START        (HOENN_VARS_START + 34)  // 타임트라이얼 시작 시각(초, u16)
#define VAR_HOENN_0x23                 (HOENN_VARS_START + 35)
#define VAR_HOENN_0x24                 (HOENN_VARS_START + 36)
#define VAR_HOENN_0x25                 (HOENN_VARS_START + 37)
#define VAR_HOENN_0x26                 (HOENN_VARS_START + 38)
#define VAR_HOENN_0x27                 (HOENN_VARS_START + 39)
#define VAR_HOENN_0x28                 (HOENN_VARS_START + 40)
#define VAR_HOENN_0x29                 (HOENN_VARS_START + 41)
#define VAR_HOENN_0x2A                 (HOENN_VARS_START + 42)
#define VAR_HOENN_0x2B                 (HOENN_VARS_START + 43)
#define VAR_HOENN_0x2C                 (HOENN_VARS_START + 44)
#define VAR_HOENN_0x2D                 (HOENN_VARS_START + 45)
#define VAR_HOENN_0x2E                 (HOENN_VARS_START + 46)
#define VAR_HOENN_0x2F                 (HOENN_VARS_START + 47)
#define VAR_HOENN_0x30                 (HOENN_VARS_START + 48)
#define VAR_HOENN_0x31                 (HOENN_VARS_START + 49)
#define VAR_HOENN_0x32                 (HOENN_VARS_START + 50)
#define VAR_HOENN_0x33                 (HOENN_VARS_START + 51)
#define VAR_HOENN_0x34                 (HOENN_VARS_START + 52)
#define VAR_HOENN_0x35                 (HOENN_VARS_START + 53)
#define VAR_HOENN_0x36                 (HOENN_VARS_START + 54)
#define VAR_HOENN_0x37                 (HOENN_VARS_START + 55)
#define VAR_HOENN_0x38                 (HOENN_VARS_START + 56)
#define VAR_HOENN_0x39                 (HOENN_VARS_START + 57)
#define VAR_HOENN_0x3A                 (HOENN_VARS_START + 58)
#define VAR_HOENN_0x3B                 (HOENN_VARS_START + 59)
#define VAR_HOENN_0x3C                 (HOENN_VARS_START + 60)
#define VAR_HOENN_0x3D                 (HOENN_VARS_START + 61)
#define VAR_HOENN_0x3E                 (HOENN_VARS_START + 62)
#define VAR_HOENN_0x3F                 (HOENN_VARS_START + 63)
#define VAR_HOENN_0x40                 (HOENN_VARS_START + 64)
#define VAR_HOENN_0x41                 (HOENN_VARS_START + 65)
#define VAR_HOENN_0x42                 (HOENN_VARS_START + 66)
#define VAR_HOENN_0x43                 (HOENN_VARS_START + 67)
#define VAR_HOENN_0x44                 (HOENN_VARS_START + 68)
#define VAR_HOENN_0x45                 (HOENN_VARS_START + 69)
#define VAR_HOENN_0x46                 (HOENN_VARS_START + 70)
#define VAR_HOENN_0x47                 (HOENN_VARS_START + 71)
#define VAR_HOENN_0x48                 (HOENN_VARS_START + 72)
#define VAR_HOENN_0x49                 (HOENN_VARS_START + 73)
#define VAR_HOENN_0x4A                 (HOENN_VARS_START + 74)
#define VAR_HOENN_0x4B                 (HOENN_VARS_START + 75)
#define VAR_HOENN_0x4C                 (HOENN_VARS_START + 76)
#define VAR_HOENN_0x4D                 (HOENN_VARS_START + 77)
#define VAR_HOENN_0x4E                 (HOENN_VARS_START + 78)
#define VAR_HOENN_0x4F                 (HOENN_VARS_START + 79)
#define VAR_HOENN_0x50                 (HOENN_VARS_START + 80)
#define VAR_HOENN_0x51                 (HOENN_VARS_START + 81)
#define VAR_HOENN_0x52                 (HOENN_VARS_START + 82)
#define VAR_HOENN_0x53                 (HOENN_VARS_START + 83)
#define VAR_HOENN_0x54                 (HOENN_VARS_START + 84)
#define VAR_HOENN_0x55                 (HOENN_VARS_START + 85)
#define VAR_HOENN_0x56                 (HOENN_VARS_START + 86)
#define VAR_HOENN_0x57                 (HOENN_VARS_START + 87)
#define VAR_HOENN_0x58                 (HOENN_VARS_START + 88)
#define VAR_HOENN_0x59                 (HOENN_VARS_START + 89)
#define VAR_HOENN_0x5A                 (HOENN_VARS_START + 90)
#define VAR_HOENN_0x5B                 (HOENN_VARS_START + 91)
#define VAR_HOENN_0x5C                 (HOENN_VARS_START + 92)
#define VAR_HOENN_0x5D                 (HOENN_VARS_START + 93)
#define VAR_HOENN_0x5E                 (HOENN_VARS_START + 94)
#define VAR_HOENN_0x5F                 (HOENN_VARS_START + 95)
#define VAR_HOENN_0x60                 (HOENN_VARS_START + 96)
#define VAR_HOENN_0x61                 (HOENN_VARS_START + 97)
#define VAR_HOENN_0x62                 (HOENN_VARS_START + 98)
#define VAR_HOENN_0x63                 (HOENN_VARS_START + 99)
#define VAR_HOENN_0x64                 (HOENN_VARS_START + 100)
#define VAR_HOENN_0x65                 (HOENN_VARS_START + 101)
#define VAR_HOENN_0x66                 (HOENN_VARS_START + 102)
#define VAR_HOENN_0x67                 (HOENN_VARS_START + 103)
#define VAR_HOENN_0x68                 (HOENN_VARS_START + 104)
#define VAR_HOENN_0x69                 (HOENN_VARS_START + 105)
#define VAR_HOENN_0x6A                 (HOENN_VARS_START + 106)
#define VAR_HOENN_0x6B                 (HOENN_VARS_START + 107)
#define VAR_HOENN_0x6C                 (HOENN_VARS_START + 108)
#define VAR_HOENN_0x6D                 (HOENN_VARS_START + 109)
#define VAR_HOENN_0x6E                 (HOENN_VARS_START + 110)
#define VAR_HOENN_0x6F                 (HOENN_VARS_START + 111)
#define VAR_HOENN_0x70                 (HOENN_VARS_START + 112)
#define VAR_HOENN_0x71                 (HOENN_VARS_START + 113)
#define VAR_HOENN_0x72                 (HOENN_VARS_START + 114)
#define VAR_HOENN_0x73                 (HOENN_VARS_START + 115)
#define VAR_HOENN_0x74                 (HOENN_VARS_START + 116)
#define VAR_HOENN_0x75                 (HOENN_VARS_START + 117)
#define VAR_HOENN_0x76                 (HOENN_VARS_START + 118)
#define VAR_HOENN_0x77                 (HOENN_VARS_START + 119)
#define VAR_HOENN_0x78                 (HOENN_VARS_START + 120)
#define VAR_HOENN_0x79                 (HOENN_VARS_START + 121)
#define VAR_HOENN_0x7A                 (HOENN_VARS_START + 122)
#define VAR_HOENN_0x7B                 (HOENN_VARS_START + 123)
#define VAR_HOENN_0x7C                 (HOENN_VARS_START + 124)
#define VAR_HOENN_0x7D                 (HOENN_VARS_START + 125)
#define VAR_HOENN_0x7E                 (HOENN_VARS_START + 126)
#define VAR_HOENN_0x7F                 (HOENN_VARS_START + 127)

#endif // GUARD_CONSTANTS_VARS_HOENN_H
