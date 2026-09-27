# 03. 큐 지도: (A) 새 곡이 필요한 장면 / (B) 기존 곡으로 충분한 장면

- 작성: 음악 리서처, 2026-09-26. 음악 감독 브리프 3번 항목, 프로듀서 지시로 두 목록으로 다시 썼다
- 기준: `docs/team/log.md:54`(2026-09-26 사용자 조정 2). 오리지널 곡은 FR/LG·에메랄드 곡 중 어울리는 것이 **정말 없는** 장면에만 만든다. 나머지는 기존 곡을 배정한다. 사용자가 승인한 장면만 작곡하고, 작곡한 곡은 WAV 미리 듣기로 먼저 보인다.
- 판정 규칙(엄격): 기존 곡으로 버틸 수 있으면 (B)다. (A)에는 후보로 검토한 기존 곡과 탈락 이유를 적는다.
- "기존 곡"의 범위
  - 롬에 있는 FR/LG 곡과 에메랄드 이식 49곡(`include/constants/songs.h`)
  - 아직 이식하지 않은 에메랄드 곡(`/root/src/pokeemerald`)도 포함한다. 이식은 `tools/hoenn_import/import_music.py` 확장으로 한다
- 근거: 스크립트와 `map.json` `"music"`(브랜치 `rocket-trio` ae609dd5d), 계획 문서(`docs/master-plan.md`, `docs/v0.9.0-plan.md`, `docs/v0.10.0-plan.md`, `docs/v0.11.0-plan.md`, `docs/events-roadmap*.md`, `docs/anim/opening-storyboard.md`)

## 0. 현황

- 오리지널 곡은 0곡이다. 이 해킹에만 있는 장면은 모두 기존 곡을 빌려 쓴다.
- 전투곡은 트레이너 **클래스**로 정해진다(`src/pokemon.c:5942-5969`). 이벤트 전투는 대부분 `trainerbattle_no_intro`/`earlyrival`이므로, 조우곡은 스크립트의 `playbgm`이다.
- 원판 옐로의 전례
  - 옐로가 레드·그린에 새로 더한 곡은 파도타기 피카츄 미니게임 곡 정도다.
  - 로사·로이 조우와 전투, 타이틀, 엔딩은 기존 곡을 그대로 썼다.
  - 이 사실이 아래 (B) 판정의 큰 근거다. 원판 옐로 곡 목록은 저장소에 없어 리서처의 기억에 기댄 것이다. 사용자나 검수자가 확인해 주면 좋다.

---

## (A) 새 곡이 필요한 장면 — 1건

| ID | 장면 | 쓰일 곳·시점 | 지금 | 검토한 기존 곡과 탈락 이유 | 새 곡의 성격 |
|---|---|---|---|---|---|
| A1 | **성도(2세대) 엔딩 크레딧** | 성도 전당 뒤 `src/credits.c`의 두 번째 스크립트, v0.19.0(`docs/master-plan.md:371-376`) | 미구현. 계획은 `MUS_CREDITS` 공용(`docs/master-plan.md:369`) | `MUS_CREDITS`(FR/LG): 칸토 엔딩 곡이다. 칸토 엔딩과 똑같아져 "세대별 엔딩"의 뜻이 사라진다(아래 B-E1이 이 곡을 쓴다)<br>에메랄드 `MUS_CREDITS`(원래 이름 THANKFOR)·`MUS_END`: 호연 엔딩 곡이라 B-E2가 쓴다. 성도 장면(칠색조·방울탑·라디오탑)에 호연 선율은 맞지 않는다<br>`MUS_HALL_OF_FAME`: 27초 루프 곡이라 174초 영상의 단조로운 반복이 된다<br>FR/LG·에메랄드에는 성도 곡이 한 곡도 없다 | 1회 재생, 크레딧 스크립트 길이(약 10,450프레임 = 174초)에 맞춤. 약 14장면 전환에 맞춘 구간 구성. 크레딧급 규모(`MUS_CREDITS` 16KB). 채널 규칙: 02 문서 4절 |

- 우선순위: **하**(릴리스가 v0.19.0이다). 성도 전당이 생기기 전에는 부를 곳이 없다.
- 사용자가 "세대마다 같은 곡이어도 된다"고 하면 (B)로 내린다(`MUS_CREDITS` 공용, 계획 원안).

---

## (B) 기존 곡으로 충분한 장면

- 배정 곡은 상수 이름이다. "현행 유지"는 지금 이미 그 곡이라는 뜻이다.
- "연결"은 바꿀 때 필요한 작업이다: map.json / 스크립트 / 코드(엔지니어) / 이식(에메랄드 곡 추가)

### B-R. 로켓단 트리오(로사·로이·나옹): 14전 + 대체 장면 1 + 계획 1

장면 목록: `docs/v0.9.0-plan.md:33-47`. 트레이너 데이터: `src/data/trainers.h:7325-7487`, `src/data/trainers_rocket.h:4,14`, `src/data/trainers_tournament.h:153`.

| # | 장소 | 스크립트 | 맵 음악 | 조우(모토) | 전투 → 승리 |
|---|---|---|---|---|---|
| 1 | 상록시티 포켓몬센터 | `ViridianCity_PokemonCenter_1F/scripts.inc:25` | POKE_CENTER | MUS_ENCOUNTER_ROCKET(`data/scripts/rocket_trio.inc:5`) | VS_TRAINER → VICTORY_TRAINER, 뒤에 `playfanfare MUS_HEAL` :78 |
| 2 | 달맞이산 B2F | `MtMoon_B2F/scripts.inc:138` | MT_MOON | ENCOUNTER_ROCKET :140 | 같음 |
| 3 | 블루시티 체육관 | `CeruleanCity_Gym/scripts.inc:16` | GYM | :28 | 같음 |
| 4 | 상트앙느호 1층 복도 | `SSAnne_1F_Corridor/scripts.inc:20` | SS_ANNE | :39/:128 | 같음 |
| 4' | 갈색시티 항구(배가 떠난 뒤) | `VermilionCity/scripts.inc:51` | VERMILLION | :56 | 같음 |
| 5 | 로켓단 아지트 B4F | `RocketHideout_B4F/scripts.inc:141` | ROCKET_HIDEOUT | :143 | 같음 |
| 6 | 포켓몬타워 7층 | `PokemonTower_7F/scripts.inc:259` | POKE_TOWER | :261 | 같음 |
| 7 | 무지개시티 체육관 | `CeladonCity_Gym/scripts.inc:19` | GYM | :38/:106 | 같음 |
| 8 | 실프 11층 | `SilphCo_11F/scripts.inc:161` | SILPH | :163 | 같음 |
| 9 | 연분홍시티 사파리 입구 | `FuchsiaCity/scripts.inc:22` | FUCHSIA | :36 | 같음 |
| 10 | 홍련섬 | `CinnabarIsland/scripts.inc:367` | CINNABAR | :382/:438 | 같음 |
| 11 | 상록 체육관 | `ViridianCity_Gym/scripts.inc:33,138` | GYM | :45/:199 | 같음 |
| 12 | 석영고원 성화 | `IndigoPlateau_Exterior/scripts.inc:29` | VICTORY_ROAD | :50/:142 | 같음(더블) |
| 13 | 새 섬(밤) | `NewIsland/scripts.inc:18` | POKE_MANSION | :35/:114 | 같음 |
| 14 | 토너먼트 홀 | `data/scripts/tournament_battles.inc:115` | GYM(→ B-T에서 B_DOME) | 없음 | 같음 |
| 15(계획) | 등화숲(Z3) | `docs/v0.11.0-plan.md:335-346` | PETALBURG_WOODS | 모토 재사용 예정 | 더블 |

| 큐 | 배정 곡 | 이유 | 연결 |
|---|---|---|---|
| 트리오 조우(모토) | **MUS_ENCOUNTER_ROCKET — 현행 유지** | 로켓단 곡이라 장면과 딱 맞는다. 원판 옐로에서도 로사·로이 조우는 로켓단 곡이었다. 루프가 6.6초로 짧지만 원판 조우곡 모두 5~7초 루프다(01 문서 2.4) | — |
| 트리오 전투 | **MUS_VS_TRAINER — 현행 유지** | 원판 옐로·FR/LG의 로켓단전 곡이다. 전용 곡을 쓰려면 코드 분기도 필요하다(같은 클래스) | — |
| 트리오 퇴장(날아가기) | **음악 없음 — 현행 유지**(효과음만, `rocket_trio.inc:20`) | 효과음 개그로 충분하다. 끝나면 `fadedefaultbgm`으로 맵 음악이 돌아온다 | — |
| 나옹 동전 | 현행 유지(`SE_SHOP`, `playfanfare MUS_OBTAIN_ITEM` :89) | 아이템 획득 관례 그대로 | — |

### B-P. 오 박사와 피카츄

| 장면 | 스크립트 | 배정 곡 | 이유 |
|---|---|---|---|
| 오 박사가 막아섬 | `PalletTown/scripts.inc:181` | MUS_OAK — 현행 유지 | 원작과 같은 장면 |
| 피카츄 받기 | `PalletTown_ProfessorOaksLab/scripts.inc:219` | MUS_OBTAIN_KEY_ITEM — 현행 유지(:232) | 중요한 것을 얻는 팡파르다. 원판 옐로도 피카츄를 받을 때 전용 곡이 없었다 |
| 라이벌 이브이, 라이벌전, 퇴장 | 같은 파일 :262, :315, :384 | OBTAIN_KEY_ITEM / ENCOUNTER_RIVAL / VS_TRAINER / RIVAL_EXIT — 현행 유지 | 원작과 같다 |
| 볼트태클 습득 | `PowerPlant/scripts.inc:154` | 맵 음악 MUS_POKE_MANSION + 번개 SE — 현행 유지 | 짧은 연출이라 효과음이 주인공이다 |
| 파도타기 피카츄 미니게임 | `Route19/scripts.inc:11`, `src/surfing_pikachu.c`(음악 호출 없음, 맵 음악 MUS_ROUTE3가 흐름) | **MUS_POKE_JUMP**(변경) | FR/LG의 미니게임 곡(포켓몬 점프)이라 밝고 경쾌하다. 도로 곡이 흐르는 것보다 낫다. 대안은 MUS_SURF(물 위지만 느리다). 원판 옐로의 전용 곡은 FR/LG·에메랄드에 없다 |
| 따라오는 피카츄, 풍선 비행 | `data/scripts/follower_pikachu.inc` | 음악 없음 — 현행 유지 | 필드 연출 |
| 오 박사전(포스트게임, 토너먼트) | `…OakAnswerChallenge` :1083 | MUS_VS_CHAMPION → MUS_VICTORY_GYM_LEADER — 현행 유지(`src/pokemon.c:5955`) | 최강급 상대에 맞는 곡이다 |

- 파도타기 피카츄의 연결은 코드다: 미니게임 시작 때 `PlayBGM(MUS_POKE_JUMP)`, 끝날 때 맵 음악 복원.

### B-N. N(5장면)

| 장면 | 스크립트 | 배정 곡 | 이유 |
|---|---|---|---|
| 회색시티 박물관 앞 | `PewterCity/scripts.inc:19` | 맵 음악 MUS_PEWTER — 현행 유지 | 대화 장면이다. 원작도 대화 조우는 맵 음악을 유지하는 경우가 많다. 조용한 인물이라 조우 팡파르가 없는 편이 성격에 맞는다 |
| 포켓몬타워 7층 | `PokemonTower_7F/scripts.inc:417` | MUS_POKE_TOWER — 현행 유지 | 같음 |
| 실프 11층 | `SilphCo_11F/scripts.inc:265` | MUS_SILPH — 현행 유지 | 같음 |
| 6섬 물길 오두막(마지막) | `SixIsland_WaterPath_Cabin/scripts.inc:18` | MUS_FUCHSIA — 현행 유지 | 같은 물길의 다른 집(`SixIsland_WaterPath_House1`)도 MUS_FUCHSIA다. 원작 관례와 일치한다 |
| 토너먼트 | `tournament_battles.inc:110` | 홀 음악(B-T) | — |
| N 전투 | 전부 | MUS_VS_TRAINER — 현행 유지 | 일반 트레이너 클래스다 |

### B-S. 은빛산

| 장면 | 곳 | 배정 곡 | 이유 | 연결 |
|---|---|---|---|---|
| 던전 4맵 | `SilverMountain_1F/2F/3F/Summit` | **MUS_VICTORY_ROAD**(변경, 지금은 MUS_SEVII_CAVE = 달맞이산 곡) | 달맞이산 곡은 초반 동굴 곡이라 포스트게임 최종 던전과 무게가 맞지 않는다. 챔피언로드 곡은 "마지막 관문 동굴"의 긴장이 있다. 대안: MUS_CAVE_OF_ORIGIN(신비 쪽), MUS_SEALED_CHAMBER | map.json 4곳 |
| 정상 조우 | `SilverMountain_Summit/scripts.inc:18` | 조우곡 없음 — 현행 유지 | "말없이 서 있는 최강 트레이너"(`docs/events-roadmap-2.md:91`) 연출에는 무음이 맞다 | — |
| 정상 전투 | 같음 | **MUS_VS_CHAMPION**(변경, 지금은 MUS_VS_TRAINER) → MUS_VICTORY_GYM_LEADER | 게임 최강자라 챔피언전 곡이 맞는다 | 코드(`GetBattleBGM`, `src/battle_main.c:3753` 승리곡 분기에 트레이너 ID) |

### B-A. 공항과 비행

| 장면 | 곳 | 배정 곡 | 이유 | 연결 |
|---|---|---|---|---|
| 칸토 공항 | `KantoAirport` | MUS_NET_CENTER — 현행 유지 | 밝고 현대적인 실내 시설 곡이라 공항 로비에 무리가 없다. 대안 MUS_SS_ANNE(출항)은 배의 인상이 강하다 | — |
| 비행 장면 | `src/airplane_flight.c`, 이륙 170 + 순항 200 + 착륙 190 = 560프레임(9.4초) | **MUS_SAILING**(변경, 지금은 음악 없음) | 에메랄드에서 브리니 배로 바다를 건널 때 쓰는 "지역 이동" 곡이다(이미 이식됨). 장면이 9.4초라 도입부만 들리고, 착륙 40프레임 전 페이드(:289)가 그대로 끝을 맡는다. 음악 없이 효과음만 두는 현행도 가능하다 | 코드(장면 시작 때 `PlayBGM`) |
| 호연 도착(카이나 항구) | `SlateportCity_Harbor` 패치 :54 | MUS_SLATEPORT — 현행 유지 | 도착지 곡 | — |

### B-T. 토너먼트

| 장면 | 곳 | 배정 곡 | 이유 | 연결 |
|---|---|---|---|---|
| 토너먼트 홀 | `TournamentHall`(접수 `IndigoPlateau_PokemonCenter_1F/scripts.inc:96`) | **MUS_B_DOME**(변경, 지금은 MUS_GYM) | 에메랄드 배틀돔은 **토너먼트 시설**이고 곡도 그 무대용이다(`BattleFrontier_BattleDomeBattleRoom`). 체육관 곡보다 대회 분위기가 뚜렷하다. 대안 MUS_B_DOME_LOBBY(같은 곡의 조용한 판, -V056) | map.json |
| 경기 전투 | `trainers_tournament.h` | 클래스별 현행 유지(관장·사천왕 VS_GYM_LEADER, 블루·오 박사 VS_CHAMPION, N·트리오 VS_TRAINER) | 원작 관례 | — |
| 우승 | `TournamentHall_EventScript_Won` :31 | MUS_OBTAIN_BADGE — 현행 유지(:33) | 우승 보상 팡파르로 뜻이 통한다 | — |

### B-X. 이 해킹의 다른 새 장소

| 곳 | 배정 곡 | 이유 |
|---|---|---|
| 새 섬(`NewIsland`) | MUS_POKE_MANSION — 현행 유지 | 뮤츠·연구소 계열 분위기가 맞는다 |
| 글리치 시티(`GlitchCity`) | MUS_FUCHSIA — 현행 유지 | 원조 글리치 시티(사파리 존 버그)가 연분홍시티에서 생기므로 뜻이 맞는다 |
| 숨겨진 동굴(`HiddenGrotto`) | MUS_VIRIDIAN_FOREST — 현행 유지 | 숲속 공간 |
| 빌의 정원(`BillsGarden`) | MUS_ROUTE24 — 현행 유지 | 빌의 집 쪽 도로 곡 |
| 포켓몬 저택 B4F·비밀 연구소 | MUS_POKE_MANSION — 현행 유지 | 같은 건물 |
| 7섬 유적 안 방(가이오가·그란돈·레쿠쟈) | 조우 ENCOUNTER_GYM_LEADER → MUS_VS_LEGEND — 현행 유지. 선택: 에메랄드 `MUS_VS_KYOGRE_GROUDON`·`MUS_VS_RAYQUAZA` 이식(원작 충실) | 현행으로도 전설 전투로 통한다 |
| 달맞이산 지라치 | ENCOUNTER_GYM_LEADER → RS_VS_TRAINER — 현행 유지 | — |
| 라벤더 증후군(`src/field_specials.c:3137`) | MUS_LAVENDER 피치 변조 — 현행 유지 | 기존 곡을 쓴 연출 |

### B-H. 호연 Z1·Z2(구현됨)와 Z3(계획)

| 장면 | 배정 곡 | 이유 | 연결 |
|---|---|---|---|
| Z1·Z2 전체: 스턴 항구 도착과 의뢰, 해양박물관, 태호(피카츄 대사 포함), 스티븐, 버려진 배, 해변의 집, 자전거 경주, 자전거 가게, 전기 체육관, 뉴모빌, 트릭하우스, 진희, 키우미집, 게임코너 | 각 맵의 에메랄드 음악 — 현행 유지 | 에메랄드 원판도 맵 음악이거나 원판 곡이다 | — |
| Z1 해양박물관 아쿠아단 전투 | 선택: `MUS_ENCOUNTER_AQUA` → `MUS_VS_AQUA_MAGMA`(이식). 지금은 맵 음악 + VS_TRAINER | 원작 장면의 원작 곡 | 이식 + 스크립트 + 코드(클래스) |
| Z3 E1 101번 도로 털보박사 구출 | **`MUS_HELP`(이식)** | 에메랄드 원판 곡(pokeemerald `Route101/scripts.inc:21`) | 이식 + 스크립트 |
| Z3 E3 103번 도로·러스트보로·104번 도로 라이벌 | **`MUS_ENCOUNTER_MAY`/`MUS_ENCOUNTER_BRENDAN`(이식)**, 전투 `MUS_VS_RIVAL`(이식) | 원판 곡(pokeemerald `Route103/scripts.inc:30,44`, `src/pokemon.c:6465-6470`) | 이식 + 스크립트 + 코드 |
| Z3 E4 노먼, E5 민진의 포획 시연 | MUS_FOLLOW_ME(이미 있음) | 원판 `PetalburgCity_Gym/scripts.inc:175,430` | 스크립트 |
| Z3 E6 등화숲 아쿠아단 | **`MUS_ENCOUNTER_AQUA`(이식)** → `MUS_VS_AQUA_MAGMA`(이식) | 원판 `PetalburgWoods/scripts.inc:10,39` | 이식 + 스크립트 + 코드 |
| Z3 E6' 등화숲 로켓단 트리오 #15 | MUS_ENCOUNTER_ROCKET → VS_TRAINER | B-R과 같다 | 스크립트 |
| Z3 E2·E7~E11(연구소, 원석, 데봉 물건, 브리니 배, 진희 재회, 물짱이) | 각 맵 음악, 배는 MUS_SAILING(이미 있음), 팡파르 OBTAIN_ITEM | 원판 그대로 | — |
| 전화 등록(Z3 이후) | `MUS_REGISTER_MATCH_CALL`(이식, 팡파르) | 원판 | 이식 + `sFanfares` |
| 호연 사천왕·챔피언(v0.14.0) | `MUS_ENCOUNTER_ELITE_FOUR`, `MUS_VS_ELITE_FOUR`, `MUS_ENCOUNTER_CHAMPION`, `MUS_VICTORY_LEAGUE`(이식) | 원판 | 이식 + 코드 |

### B-E. 오프닝·타이틀·엔딩·스내그

| 장면 | 배정 곡 | 이유 | 연결 |
|---|---|---|---|
| 오프닝(F705~F1457, 752프레임) | MUS_INTRO_FIGHT — 현행 유지 | 계획이 "인트로 음악 그대로"다(`docs/master-plan.md:14`). 콘티 컷이 이 곡의 마디 격자(188 BPM, 1마디 76.6프레임)에 맞춰 짜여 있다(`docs/anim/opening-storyboard.md:64-122`). 원판 옐로도 레드·그린과 같은 오프닝 곡이었다 | — |
| 타이틀 | MUS_TITLE — 현행 유지 | 시리즈 대표 곡이다. 원판 옐로도 레드·그린과 같은 타이틀 곡이었다. 화면(피카츄 그림)만 바뀌어도 충분히 옐로답다 | — |
| B-E1 칸토 엔딩(v0.11.0) | MUS_CREDITS — 현행 유지(`IndigoPlateau_Exterior/scripts.inc:18`) | 칸토 엔딩 곡 그 자체다. 계획도 이 곡이다(`docs/master-plan.md:369`) | — |
| B-E2 호연 엔딩(v0.14.0) | **에메랄드 크레딧 곡(pokeemerald `MUS_CREDITS`, 원래 이름 THANKFOR) + `MUS_END`(이식)** | 호연 엔딩의 원판 곡이다(pokeemerald `src/credits.c:448,686`). 상수 이름이 FR/LG `MUS_CREDITS`와 겹치므로 `MUS_RS_CREDITS` 같은 새 이름이 필요하다 | 이식 + 크레딧 코드 |
| 스내그 성공(v0.10.0) | MUS_CAUGHT — 계획대로(`docs/v0.10.0-plan.md:199`) | "잡았다" 장면의 기존 곡이다. 루프 곡이지만 문구 뒤 `snagrestorebgm`이 전투곡을 다시 틀기 때문에 도입부(약 2~4초)만 들린다. 대안: `playfanfare MUS_OBTAIN_KEY_ITEM`(1회 2.6초) | 스내그 구현 때 |

---

## 1. 요약

- (A) **1건**: 성도 엔딩 크레딧(v0.19.0, 우선순위 하)
- (B) 나머지 전부
  - 현행 유지: 대부분
  - 기존 곡으로 바꾸기 5건: 파도타기 피카츄 → POKE_JUMP, 은빛산 → VICTORY_ROAD, 은빛산 정상 전투 → VS_CHAMPION, 비행 장면 → SAILING, 토너먼트 홀 → B_DOME
  - 에메랄드 원판 곡 이식: 호연 Z3·사천왕·엔딩(HELP, ENCOUNTER_MAY/BRENDAN, VS_RIVAL, ENCOUNTER_AQUA, VS_AQUA_MAGMA, REGISTER_MATCH_CALL, 에메랄드 크레딧·END 등)
- 작곡할 곡은 당장 없다. 음악 팀의 가까운 일은 (B)의 변경 5건 연결과 에메랄드 곡 이식이다. 둘 다 사용자 승인 뒤, 코드 부분은 엔지니어와 함께 한다.

## 2. 사용자에게 올릴 질문(리서처 추천 포함)

1. **성도 엔딩(A1)**: 새 곡으로 만들까요, 칸토와 같은 `MUS_CREDITS`를 쓸까요?
   - 추천: 새 곡. 다만 제작은 v0.19.0 가까이로 미룬다.
   - 참고: 2026-09-26 결정으로 오프닝과 엔딩 셋은 공식 수준의 연속 애니메이션이 된다(`docs/team/log.md:56`). 애니메이션을 곡의 박자와 구간에 맞춰 짜야 하므로, 엔딩 곡을 정하는 일이 애니메이터 작업보다 먼저다. 칸토(`MUS_CREDITS`)와 호연(에메랄드 크레딧 곡)은 기존 곡이라 지금 바로 기준 길이를 잴 수 있다.
   - 참고: 칸토 엔딩은 `MUS_CREDITS`다. MIDI 계산 길이는 249.5초(실측 250.6초, 06 문서)이고 크레딧 스크립트 합계는 174초다 — 엔딩 길이 기준은 2026-09-26부터 250.6초로 통일. 곡이 석영고원 바깥 장면에서 먼저 시작해 차이를 덮는 것으로 보인다. v0.11.0 칸토 엔딩 작업 때 `tools/qa/audiocap.py`로 실측한다.
2. **오프닝·타이틀**: 기존 곡(MUS_INTRO_FIGHT, MUS_TITLE)을 유지할까요?
   - 추천: 유지. 원판 옐로의 전례가 있고, 오프닝 콘티가 이 곡의 박자에 맞춰 짜여 있다.
3. **파도타기 피카츄**: MUS_POKE_JUMP로 바꿀까요?
   - 추천: 바꾼다(코드 두 줄).
   - 참고: 원판 옐로의 전용 곡을 GBA로 옮기는 것은 FR/LG·에메랄드 곡이 아니므로 이번 범위 밖이다.
4. **에메랄드 원판 곡 이식 묶음**(B-H, B-E2)은 누가 할까요?
   - 추천: 엔지니어가 `import_music.py`를 확장하고, 음악 검수자가 음량과 루프를 확인한다. Z3(v0.11.0) 전에 한다.
5. **은빛산 정상 조우**: 무음을 유지하고 전투만 MUS_VS_CHAMPION으로 할까요?
   - 추천: 그렇게 한다.
6. **(B)의 변경 5건**(POKE_JUMP, VICTORY_ROAD, VS_CHAMPION, SAILING, B_DOME)과 선택 이식(아쿠아단 Z1, 가이오가·그란돈·레쿠쟈 전투곡)을 승인할까요?
   - 추천: 변경 5건은 승인한다. 선택 이식은 Z3 이식 묶음에 같이 넣는다.
