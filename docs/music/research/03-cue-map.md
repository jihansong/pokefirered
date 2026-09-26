# 03. 큐 지도: 썬더옐로우에만 있는 장면과 지금 나오는 음악

- 작성: 음악 리서처, 2026-09-26. 음악 감독 브리프 3번 항목
- 기준: `rocket-trio` 브랜치 ae609dd5d. 파일은 모두 읽기만 했다
- 문서 근거: `docs/master-plan.md`, `docs/v0.9.0-plan.md`, `docs/v0.10.0-plan.md`, `docs/v0.11.0-plan.md`, `docs/events-roadmap*.md`, `docs/anim/opening-storyboard.md`
- 스크립트 근거: `data/maps/*/scripts.inc`, `data/scripts/*.inc`, `tools/hoenn_import/patches/`, `map.json`의 `"music"`

## 0. 현황 요약

- **오리지널 곡은 아직 0곡이다.** 이 해킹에만 있는 장면은 모두 FR/LG 곡이나 에메랄드 이식곡 49곡(`MUS_ABANDONED_SHIP`~`MUS_VERDANTURF`, 347~395)을 빌려 쓴다.
- 업스트림과 달라진 음악 코드는 두 가지뿐이다.
  - 오 박사 클래스를 챔피언 전투곡과 체육관장 승리곡에 넣었다(`src/pokemon.c:5955`, `src/battle_main.c:3757`).
  - 가이오가·그란돈·레쿠쟈를 전설 전투곡에 넣었다(`src/battle_setup.c:374-376`).
- 전투곡은 **트레이너 클래스**로 정해진다(`src/pokemon.c:5942-5969`).
  - 로켓단 트리오·N·은빛산 트레이너는 일반 트레이너전 곡 `MUS_VS_TRAINER`
  - 토너먼트의 관장·사천왕은 `MUS_VS_GYM_LEADER`, 블루·오 박사는 `MUS_VS_CHAMPION`
- 이벤트 전투는 거의 모두 `trainerbattle_no_intro`/`earlyrival`이다. 그래서 트레이너 데이터의 조우곡은 쓰이지 않는다. **스크립트의 `playbgm`이 실제 조우곡**이다. 새 조우 큐를 넣을 때는 스크립트 한 줄만 바꾸면 된다.

## 1. 큐 표

- 성격: L = 루프, 1 = 1회 재생
- 전환: 이 큐 앞뒤로 무엇이 오는가
- 우선순위: 상(다음 작곡 묶음), 중(해당 릴리스 전), 하(보류 또는 기존 곡으로 충분)

### 1.1 로켓단 트리오(로사·로이·나옹)

14회 구현, 대체 장면 1개, 계획 1개(`docs/v0.9.0-plan.md:33-47`). 트레이너 데이터: `src/data/trainers.h:7325-7487`, `src/data/trainers_rocket.h:4,14`, `src/data/trainers_tournament.h:153`.

| # | 장소(맵) | 스크립트 | 맵 음악 | 장면 음악(지금) | 전투 |
|---|---|---|---|---|---|
| 1 | 상록시티 포켓몬센터 | `ViridianCity_PokemonCenter_1F/scripts.inc:25` | POKE_CENTER | 폭발 SE → 모토(`data/scripts/rocket_trio.inc:5` `playbgm MUS_ENCOUNTER_ROCKET`) → `fadedefaultbgm` :73 → `playfanfare MUS_HEAL` :78 | earlyrival :48 |
| 2 | 달맞이산 B2F | `MtMoon_B2F/scripts.inc:138` | MT_MOON | ENCOUNTER_ROCKET :140, 삐삐 울음, fadedefault :188 | :174 |
| 3 | 블루시티 체육관(물 쇼) | `CeruleanCity_Gym/scripts.inc:16` | GYM | 폭발 SE :21, ENCOUNTER_ROCKET :28 | :44 |
| 4 | 상트앙느호 1층 복도 | `SSAnne_1F_Corridor/scripts.inc:20` | SS_ANNE | ENCOUNTER_ROCKET :39/:128 | :55 |
| 4' | 갈색시티 항구(배가 떠난 뒤) | `VermilionCity/scripts.inc:51` | VERMILLION | ENCOUNTER_ROCKET :56 | :75 |
| 5 | 로켓단 아지트 B4F | `RocketHideout_B4F/scripts.inc:141` | ROCKET_HIDEOUT | ENCOUNTER_ROCKET :143 | :159 |
| 6 | 포켓몬타워 7층 | `PokemonTower_7F/scripts.inc:259` | POKE_TOWER | ENCOUNTER_ROCKET :261 | :282 |
| 7 | 무지개시티 체육관(향수) | `CeladonCity_Gym/scripts.inc:19` | GYM | ENCOUNTER_ROCKET :38/:106 | :65 |
| 8 | 실프주식회사 11층 | `SilphCo_11F/scripts.inc:161` | SILPH | ENCOUNTER_ROCKET :163 | :180 |
| 9 | 연분홍시티 사파리 입구(미뇽) | `FuchsiaCity/scripts.inc:22` | FUCHSIA | ENCOUNTER_ROCKET :36 | :53 |
| 10 | 홍련섬(마그마) | `CinnabarIsland/scripts.inc:367` | CINNABAR | ENCOUNTER_ROCKET :382/:438 | :392 |
| 11 | 상록 체육관(대리 관장) | `ViridianCity_Gym/scripts.inc:33,138` | GYM | ENCOUNTER_ROCKET :45/:199, 모토 :147 | :157 |
| 12 | 석영고원(성화) | `IndigoPlateau_Exterior/scripts.inc:29` | VICTORY_ROAD | ENCOUNTER_ROCKET :50/:142 | :64 더블 |
| 13 | 새 섬(밤, 이 해킹의 맵) | `NewIsland/scripts.inc:18` | POKE_MANSION | ENCOUNTER_ROCKET :35/:114, 모토 :42 | :52 |
| 14 | 토너먼트 홀 | `data/scripts/tournament_battles.inc:115` | GYM | 없음(홀 음악 그대로) | 일반 |
| 15(계획) | 등화숲(호연 Z3) | 미구현, `docs/v0.11.0-plan.md:335-346` | PETALBURG_WOODS | 모토 재사용 예정 | 더블 |

- 모든 전투: `MUS_VS_TRAINER` → `MUS_VICTORY_TRAINER`
- 날아가는 퇴장 `EventScript_RocketTrioBlastOff`(`rocket_trio.inc:20`): 음악 없음, 효과음만
- 과거 결정: `docs/v0.4.0-plan.md:150,199` "전용 테마 대신 `MUS_ENCOUNTER_ROCKET` 재사용"

### 1.2 새 큐 목록과 우선순위

| ID | 큐 | 쓰일 곳 | 지금 음악 | 성격·길이·전환 | 연결 방법 | 우선 | 이유 |
|---|---|---|---|---|---|---|---|
| R1 | **로켓단 트리오 등장(모토) 테마** | 1.1의 #1~13, #15(14~15장면) | MUS_ENCOUNTER_ROCKET(일반 단원과 같은 곡, 142 BPM대, 5마디 루프 6.6초) | L. 1~2초 도입 + 8마디 루프(12~16초). 모토 대사가 길어서 6초 루프는 너무 자주 돈다. 140~160 BPM, 코믹한 악당. 뒤로는 전투곡(R2), 전투 뒤 `fadedefaultbgm` | 스크립트 `playbgm` 교체(`rocket_trio.inc:5`와 각 맵). 코드 불필요 | **상** | 이 게임의 얼굴인 캐릭터. 가장 자주 나오는 고유 장면이고, 지금은 일반 단원과 구별되지 않는다 |
| R2 | **로켓단 트리오 전투곡** | 14전 | MUS_VS_TRAINER | L. 10~15초 도입 + 50~70초 루프, 172~186 BPM(전투 관례). R1 모티프 변주. 앞: R1 또는 전투 진입, 뒤: VICTORY_TRAINER | **코드 필요**: `GetBattleBGM`은 클래스로 고르는데 트리오와 단원이 같은 클래스다. 트레이너 ID 분기나 새 클래스 필요(엔지니어) | **상** | 14번 반복되는 전투. 전용 곡이 없으면 트리오가 일반 단원처럼 느껴진다 |
| R3 | 트리오 퇴장("또 졌다~") 징글 | `EventScript_RocketTrioBlastOff` | 없음(SE만) | 1. 2~3초. 끝나면 `fadedefaultbgm` | 팡파르 표 `sFanfares` 추가 필요(02 문서 6절) | 중 | 매번 반복되는 개그의 끝맺음. 짧고 싸다 |
| P1 | **피카츄 파트너 모티프(동료 팡파르)** | 오 박사 연구소 피카츄 받기(`PalletTown_ProfessorOaksLab/scripts.inc:219`) | `playfanfare MUS_OBTAIN_KEY_ITEM` :232 | 1. 3~5초 팡파르. 뒤로는 MUS_OAK_LAB 복귀 | `sFanfares` 추가 + 스크립트 1줄 | **상** | 게임 전체 모티프(오프닝·엔딩·볼트태클)의 씨앗. 싸고 짧다 |
| P2 | 피카츄 결정적 장면(볼트태클 습득) | 무인발전소 `PowerPlant/scripts.inc:154` | 맵 POKE_MANSION + 번개 SE | 1. 5~8초 스팅 또는 짧은 L | 스크립트 | 중 | P1 모티프의 절정 변주 |
| P3 | 파도타기 피카츄 미니게임 | 19번 도로 `Route19/scripts.inc:11`, `src/surfing_pikachu.c` | 맵 음악 그대로(음악 호출 없음) | L. 20~30초, 밝고 빠르게 | 코드(미니게임 시작 시 `PlayBGM`) | 중 | 옐로의 상징 미니게임인데 지금은 도로 음악이 흐른다. 원판 옐로 곡의 선율은 쓸 수 없으니 새 곡이어야 한다 |
| O1 | 오 박사전(포스트게임) | 연구소 `…OakAnswerChallenge` :1083, 토너먼트 | MUS_VS_CHAMPION → VICTORY_GYM_LEADER | L. 챔피언급 전투 | 코드(클래스 분기가 이미 있으므로 `TRAINER_CLASS_PKMN_PROF`만 새 곡으로) | 중 | 원작에 없는 대결. 분기 코드가 이미 있어 연결이 쉽다 |
| S1 | 은빛산 던전 | `SilverMountain_1F~3F`, `Summit` 4맵 | MUS_SEVII_CAVE(=달맞이산 곡) | L. 60~90초(던전 관례), 눈보라·고독 | map.json 4곳 | 중 | 포스트게임 최종 장소인데 달맞이산 곡이 흐른다 |
| S2 | 은빛산 정상 최강 트레이너 전투 | `SilverMountain_Summit/scripts.inc:18` | 조우곡 없음, MUS_VS_TRAINER | L. 전투곡. 조우는 **무음 유지**를 추천("…" 연출, `docs/events-roadmap-2.md:91`) | 코드(트레이너 ID 분기) | 중 | 게임 최강자인데 일반 트레이너전 곡이 나온다 |
| N1 | N 테마(조우) | 회색시티 :19, 포켓몬타워 7층 :417, 실프 11층 :265, 6섬 오두막 :18, 토너먼트 :110 | 음악 명령 없음(맵 음악 그대로), 전투 VS_TRAINER | L. 도입 없이 8~16마디, 느리고 사색적 | 스크립트 `playbgm` 추가 | 중 | 5장면이 이어지는 인물인데 테마가 없다. 대사 장면이라 조우곡이 필요하다 |
| N2 | N의 오두막 | `SixIsland_WaterPath_Cabin` | MUS_FUCHSIA | L. N1의 잔잔한 편곡 | map.json | 하 | N1 편곡으로 해결 |
| A1 | 칸토 공항 | `KantoAirport` | MUS_NET_CENTER(통신센터 곡) | L. 40~50초, 실내·출발 설렘 | map.json | 중 | 호연(구현)·성도(예정) 여행의 관문. 통신센터 곡은 어색하다 |
| A2 | 비행 장면 | `src/airplane_flight.c` 이륙 170 + 순항 200 + 착륙 190 = **560프레임(9.4초)** | 음악 없음, SE만(착륙 40프레임 전 맵 음악 페이드) | 1. 9.4초 맞춤, 지역 횡단 모티프 | 코드(`DoAirplaneFlightScene` 시작 시 재생) | 중 | "지역을 건너는" 모티프를 들려줄 유일한 자리. 길이가 정해져 있다 |
| T1 | 토너먼트 홀 | `TournamentHall`, 접수 `IndigoPlateau_PokemonCenter_1F/scripts.inc:96` | MUS_GYM | L. 50~60초, 경기장 긴장 | map.json | 중 | 16명 토너먼트의 무대가 체육관 곡이다 |
| T2 | 토너먼트 우승 팡파르 | `TournamentHall_EventScript_Won` :31 | `playfanfare MUS_OBTAIN_BADGE` :33 | 1. 4~6초 | `sFanfares` | 하 | 배지 팡파르로도 뜻이 통한다 |
| SN | 스내그 성공 징글(v0.10.0) | 계획 `docs/v0.10.0-plan.md:199` | 계획은 전투곡을 멈추고 MUS_CAUGHT를 튼 뒤 `snagrestorebgm`으로 전투곡을 처음부터 다시 튼다 | 1. 2~4초. 곧바로 전투곡 재시작 | 스내그 구현 시 같이. 팡파르가 아니라 `PlayBGM` 방식이면 표 불필요 | 중 | 다음 릴리스 기능. 콜로세움식 "빼앗았다"는 결이 잡힌 소리가 필요하다. 루프하는 MUS_CAUGHT(13.9초)는 도중에 끊긴다 |
| NI | 새 섬(밤) | `NewIsland` | MUS_POKE_MANSION | L. 신비·불안 | map.json | 하 | 기존 곡으로 분위기는 맞는다 |
| GC | 글리치 시티 | `GlitchCity` | MUS_FUCHSIA | L. 일부러 깨진 소리(PSG 위주) | map.json | 하 | 재미 요소. 우선순위는 낮다 |
| C1 | 엔딩 크레딧 1(칸토, v0.11.0) | `src/credits.c`, `IndigoPlateau_Exterior/scripts.inc:18` | MUS_CREDITS(249.5초 계산값, 1회) | 1. 크레딧 스크립트 10,450프레임(174초) + 앞의 걷는 장면. 14장면 맞춤 | `playbgm` 교체 | 중 | **계획은 MUS_CREDITS 공용**(`docs/master-plan.md:369`). 새로 쓰면 가장 큰 곡(16KB급)이다. 감독 결정 필요 |
| C2 | 엔딩 크레딧 3(호연, v0.14.0) | `EverGrandeCity_HallOfFame` | 미구현 | 1. 174초 | 같음 | 하 | 릴리스가 멀다. 에메랄드 엔딩 이식도 선택지다 |
| C3 | 엔딩 크레딧 2(성도, v0.19.0) | 성도 전당 | 미구현 | 1. 174초 | 같음 | 하 | 릴리스가 멀다 |
| OP | 오프닝 | `src/intro.c`, 바꿀 구간 F705~F1457(752프레임, 12.53초) | MUS_GAME_FREAK → MUS_INTRO_FIGHT(727→1455, 12.1초, 188 BPM) → MUS_TITLE | 1. 752프레임 안, 장면 컷이 마디 경계(188 BPM 1마디 = 76.6프레임) | intro.c 곡 번호 | 하 | 계획은 "인트로 음악 그대로"(`docs/master-plan.md:14`, 콘티 :107). 바꾸면 콘티 박자 격자도 새로 짜야 한다 |

### 1.3 기존 곡을 옮겨 오면 되는 자리(작곡 대상 아님)

감독 지침: 원작 R/B/Y·FR/LG·R/S/E 곡은 원작이 쓴 자리에 그대로 둔다. 호연 이벤트는 에메랄드에 전용 곡이 있는데 이식되지 않았다. 지금 이식된 49곡은 맵 음악뿐이다. 모두 `/root/src/pokeemerald`에 있다(`import_music.py`의 원본 경로).

| 장면(릴리스) | 에메랄드 원판 | 지금 | 근거 |
|---|---|---|---|
| Z3 E1 101번 도로 털보박사 구출 | `MUS_HELP`(pokeemerald `Route101/scripts.inc:21`) | 계획엔 음악 언급 없음 | `docs/v0.11.0-plan.md` §4 |
| Z3 E3 103번 도로 라이벌, 러스트보로·104번 도로 라이벌 | `MUS_ENCOUNTER_MAY`/`BRENDAN`, 전투 `MUS_VS_RIVAL`(pokeemerald `src/pokemon.c:6465-6470`) | 계획만 | 같음 |
| Z3 E6 등화숲 아쿠아단, Z1 해양박물관 아쿠아단 | `MUS_ENCOUNTER_AQUA`, 전투 `MUS_VS_AQUA_MAGMA` | Z1은 맵 음악 + `MUS_VS_TRAINER` | `SlateportCity_OceanicMuseum_2F` 패치 :11/:16 |
| Z3 E4 노먼, E5 민진의 포획 시연 | `MUS_FOLLOW_ME`(이미 있음, 원판 `PetalburgCity_Gym:175,430`) | 계획만 | — |
| 호연 사천왕·챔피언(v0.14.0) | `MUS_VS_ELITE_FOUR`, `MUS_ENCOUNTER_ELITE_FOUR`, `MUS_ENCOUNTER_CHAMPION` | — | — |
| 칸토 해식동굴의 가이오가·그란돈·레쿠쟈 | `MUS_VS_KYOGRE_GROUDON`, `MUS_VS_RAYQUAZA` | MUS_VS_LEGEND(FR/LG 전설곡) | `src/battle_setup.c:374-376`, `SevenIsland_TanobyRuins_EmbeddedChamber:186` |
| 호연 엔딩(C2 대안) | `MUS_END`, `MUS_THANKFOR` | — | — |
| 전화 등록 | `MUS_REGISTER_MATCH_CALL` | — | Z3 이후 |

→ 이 목록은 작곡이 아니라 `tools/hoenn_import/import_music.py` 확장(엔지니어·작곡가 작업)으로 해결된다. 오리지널 큐보다 싸고 원작 충실도가 오른다.

### 1.4 새 큐가 필요 없는 곳

| 장면 | 지금 | 판단 |
|---|---|---|
| 호연 Z1·Z2의 스턴·스티븐·태호·진희·민진·자전거 경주·트릭하우스·키우미집 등 | 에메랄드 맵 음악 | 원판도 전용 곡이 없거나(맵 음악) 이미 원판 곡이다. 유지 |
| 태호의 피카츄 대사(`DewfordTown_Gym` :36) | GYM | 대사 한 줄. 유지 |
| 빌의 정원(`BillsGarden`, ROUTE24), 숨겨진 동굴(`HiddenGrotto`, VIRIDIAN_FOREST), 포켓몬 저택 B4F·비밀 연구소 | 기존 곡 | 분위기가 맞는다. 유지 |
| 달맞이산 지라치(`MtMoon_B2F` :490) | ENCOUNTER_GYM_LEADER → RS_VS_TRAINER | 하. 원한다면 1.3의 전설곡 이식으로 해결 |
| 따라오는 피카츄, 풍선 피카츄(비행) | 없음 | 필드 연출. 음악 불필요 |
| 성도 챕터(예정, 40~50곡) | — | `docs/events-roadmap-2.md:112`는 "크리스탈 곡을 편곡"이라 한다. 기존 선율 편곡이므로 이 팀의 "오리지널" 범위 밖이다. 감독 결정 필요(질문 참고) |

## 2. 우선순위 제안(요약)

1. **상**(첫 작곡 묶음)
   - R1 트리오 등장 테마, R2 트리오 전투곡, P1 피카츄 동료 팡파르
   - 이유: 가장 자주 나오고 게임 정체성의 핵심이다. 모티프 세트(피카츄·로켓 트리오)의 원천이다. R1과 P1은 코드 없이(P1은 팡파르 표 한 줄) 바로 연결된다.
2. **중**(해당 릴리스 전)
   - SN 스내그 징글(v0.10.0에 맞춤)
   - C1 칸토 엔딩(v0.11.0, 감독이 새 곡으로 결정할 때)
   - A1·A2 공항·비행(지역 횡단 모티프), N1 N 테마, S1·S2 은빛산, T1 토너먼트, O1 오 박사전, P2·P3 피카츄 장면, R3 퇴장 징글
   - 에메랄드 원판 곡 이식 묶음(1.3, v0.11.0 Z3 전)
3. **하**
   - OP(계획상 원판 유지), C2·C3(릴리스가 멀다), T2, N2, NI, GC

## 3. 코드가 필요한 큐(엔지니어 협의)

| 큐 | 필요한 것 |
|---|---|
| R2, S2 | `GetBattleBGM`(`src/pokemon.c:5942`)에 트레이너 ID 분기(또는 새 트레이너 클래스) |
| O1 | 같은 함수의 `TRAINER_CLASS_PKMN_PROF` 분기를 새 곡으로 |
| P1, R3, T2 | `src/sound.c` `sFanfares[]` + `include/constants/sound.h` `FANFARE_*` |
| A2 | `src/airplane_flight.c` 시작 시 `PlayBGM`, 착륙 페이드(:289) 유지 |
| P3 | `src/surfing_pikachu.c` 시작·끝에서 BGM 저장·복원 |
| SN | 스내그 구현 시 같이 설계(징글 → `PlayBattleBGM()`) |
