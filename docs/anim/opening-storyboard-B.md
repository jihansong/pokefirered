# 오프닝 안 B: 저장소 안의 공식 그래픽만 (2026-09-26, 예술감독 판정 전)

사용자 방향 전환(2026-09-26): 코드로 새로 그린 그림은 쓰지 않는다. **이 저장소에 이미 있는 게임 그래픽만** 쓰고, 코드는 배치·스크롤·확대(아핀)·팔레트 블렌드·타이밍만 한다. 그림에 가하는 변경은 팔레트 재색(칠색조 금빛 실루엣) 하나뿐. `/root/src/pokeemerald` 그래픽과 외부 일러스트는 쓰지 않는다.

목업: `tools/make_intro_opening_official_mock.py` → `docs/anim/drafts/official-B2/`(예술감독 판정 `docs/team/art/v0.11.1-opening-B.md`의 필수 1~8·권고 9 반영, 2026-09-26; 이전 판 `official-B/`) (컷별 key 프레임 1배·3배, `compare.png`·`compare_x3.png`: 왼쪽이 FR/LG 원판 캡처). 타일맵·타일셋 디코더는 `tools/official_gfx.py`(그리지 않고 하드웨어처럼 풀기만 한다).

## 1. 쓸 수 있는 공식 자원 (저장소 경로)

| 종류 | 경로 | 크기·프레임 | 쓰임 |
|---|---|---|---|
| 맵 타일셋·레이아웃 | `data/tilesets/primary/general`, `data/tilesets/secondary/pallet_town`, `data/layouts/PalletTown/map.bin`(24×20 블록), `data/layouts/Route1/map.bin`(24×40) | 16×16 메타타일, 팔레트 13개 | C1 태초마을→1번도로 |
| 필드 스프라이트 | `graphics/object_events/pics/people/red_normal.png` | 16×32 × 9(정지·걷기 4방향) | C1 레드 |
| | `graphics/object_events/pics/pokemon/pikachu.png` | 16×16 × 9 | C1 따라오는 피카츄 |
| | `graphics/object_events/pics/pokemon/spearow.png` | 16×16 × 3(날갯짓) | C3 먼 깨비참 떼 |
| | `graphics/object_events/pics/pokemon/ho_oh.png` | 32×32 × 2 | (예비) C5 먼 칠색조 |
| 트레이너 그림 | `graphics/trainers/back_pics/red_back_pic.png` | 64×64 × 5(던지기 동작) | C2 볼 던지기, C5 뒷모습 |
| | `graphics/trainers/front_pics/red_front_pic.png` | 64×64 × 1 | (예비) |
| 포켓몬 전투 그림 | `graphics/pokemon/pikachu/front.png`, `back.png` | 64×64 × 1씩 | C2·C4 앞모습, C5 뒷모습 |
| | `graphics/pokemon/spearow/front.png`, `fearow/front.png` | 64×64 × 1 | C3·C4 |
| | `graphics/pokemon/ho_oh/front.png` | 64×64 × 1 | C5 (팔레트 재색 실루엣) |
| 크레딧 | `graphics/credits/player_male.png` | 64×64 × 6(달리기 주기) | C3 빗속을 달리는 레드 |
| | `graphics/credits/pikachu_1.png`, `pikachu_2.png` | 80×80, 96×96(창 그림) | (예비) 마무리 |
| | `graphics/credits/ground_grass.png` | 64×256(달리는 땅 스프라이트 띠) | (예비) |
| FR/LG 인트로 | `graphics/intro/scene_3/bg.png`+`bg.bin` | 32×20 타일 맵(숲), 팔레트 2 | C3 숲(어둡게) |
| | `graphics/intro/scene_2/bg.png`+`bg.bin`, `plants.png`+`plants.bin` | 64×32 맵, 32×20 맵 | (예비) 숲 원경·앞 풀 |
| | `graphics/intro/scene_1/bg`, `grass` (+`.bin`) | 64×32 맵 | (예비) 풀숲 터널 |
| | `graphics/intro/game_freak/sparkles_small.png`, `sparkles_big.png`, `star.png` | 반짝이·별 | (예비) C5 반짝이 |
| 전투 배경 | `graphics/battle_terrain/grass/terrain.png`+`terrain.bin` | 64×32 맵, 팔레트 3 | C2 |
| 전투 애니 배경 | `graphics/battle_anims/backgrounds/thunder.png`+`thunder.bin` | 32×32 맵, 팔레트 1 | C4 |
| | `.../backgrounds/in_air`, `aurora`, `cosmic` (+`.bin`) | 32×32 맵 | (예비) |
| 전투 애니 스프라이트 | `graphics/battle_anims/sprites/electricity.png`(팔레트 `electric_orbs.gbapal`) | 32×32 × 4 | C2·C4 전기 |
| | `.../lightning.png`(팔레트 `lightning_2.gbapal`) | 32×32 × 5 | C3·C4 번개 |
| | `.../spark_2.png`, `shock.png`, `shock_4.png` | 16×16 × 3, 32×32 × 6, 16×16 × 6 | 전기 보조 |
| | `.../gold_stars.png` | 16×8 × 3 | C5 반짝이 꼬리 |
| | `.../rain_drops.png`, `impact.png`, `white_feather.png` | 16×16 × 14, 32×32, 32×32 × 2 | (예비) |
| 볼 | `graphics/interface/ball/poke.png` | 16×16 × 3(회전) | C2 |
| 날씨 | `graphics/weather/rain.png`(팔레트 `default.gbapal`) | 16×32 × 6 | C3 비 |
| | `graphics/weather/cloud.png`(`cloud.gbapal`) | 64×64 | C5 구름 |
| 타이틀 | `graphics/title_screen/leafgreen/*` | — | 마무리(기존 흐름 그대로) |

쓰지 않는 것: `graphics/trainers/front_pics/jessie_james_front_pic.png`(팀이 FR 조무래기 그림으로 다시 짠 그림이라 "공식 그림"이 아니다), `graphics/pikachu_emotions/*`(팀 제작), `graphics/intro/opening/*`(안 A의 코드 그림).

**필요 후보(저장소에 없음, 쓰지 않음)**: 에메랄드 인트로 하늘·구름·숲·풀 층(`graphics/intro/scene_2/clouds_bg`, `clouds`, `trees`, `grass` + 맵), 에메랄드 인트로 번개·레쿠쟈 구름(`scene_3/lightning`, `rayquaza_clouds`), 에메랄드 2프레임 앞모습(`anim_front.png`: 피카츄·깨비참·칠색조). 이식하면 C3·C5의 하늘과 C2·C4 포켓몬 움직임이 좋아진다. 무지개 그림은 공식 자원 어디에도 없다.

## 2. 콘티 (595프레임 = 9.9초)

코드 t0 = F706(게임프리크 로고가 끝난 다음, 지금과 같음). 컷은 모두 `MUS_INTRO_FIGHT` 마디 경계(t59·136·212·289·365·442·519·595)에 맞춘다. 화면은 원판처럼 240×96 레터박스(y 32~127).

| 컷 | t (코드) | F | 길이 | 화면·움직임 | 공식 그림(저장소 경로) | 이펙트 | 음악 |
|---|---|---|---|---|---|---|---|
| C1 출발 | 0~135 | 706~841 | 136 | t0~23 위에서 내려오는 세로 팬(72px, ease)으로 레드 집 문 앞에 닿는다(새벽 블렌드 4/16→0, 24프레임). t8부터 레드가 걸어 나가 동쪽 길을 돌아 북쪽 1번도로 입구로. 카메라는 따라가다 t100에 멈춘다. 피카츄는 11프레임 뒤를 따라오다 t110에 멈춰 돌아본다(화면 안, 잘리지 않음). 레드는 위로 빠져나간다 | `data/layouts/PalletTown/map.bin`, `data/layouts/Route1/map.bin`, `data/tilesets/primary/general/*`, `data/tilesets/secondary/pallet_town/*`; `graphics/object_events/pics/people/red_normal.png`; `graphics/object_events/pics/pokemon/pikachu.png` | 새벽 주황 블렌드; 맵 스트리밍 | 전주 + 마디 1 |
| C2 볼이 싫은 피카츄 | 136~211 | 842~917 | 76 | 전투 무대. 레드 뒷모습 던지기를 FR/LG `sAnimCmd_Red_1` 간격 그대로(프레임 1 20, 2 6, 3 6, 4 24, 그다음 0; t4부터). 볼은 프레임 3(t32)에 손을 떠나 16프레임 포물선(키 t40), t48 피카츄에 닿아 전기가 튀고(키 t50) 레드 머리 위로 튕겨 날아간다(t48~69, 키 t60). 피카츄는 t44~57 한 번 뛴다 | `graphics/battle_terrain/grass/terrain.png`·`terrain.bin`·`terrain.gbapal`; `graphics/trainers/back_pics/red_back_pic.png`; `graphics/pokemon/pikachu/front.png`·`normal.pal`; `graphics/interface/ball/poke.png`(회전 2프레임); `graphics/battle_anims/sprites/electricity.png`+`electric_orbs.gbapal` | 흰 번쩍임 2프레임(1회); 피카츄 울음 | 마디 2 |
| C3 폭우와 깨비참 | 212~364 | 918~1070 | 153 | 원판 숲을 어둡게(9/16) 4px/프레임 가로 스크롤, 레드가 크레딧 달리기 주기로 달린다. 먼 하늘 깨비참 떼 9마리 날갯짓. 가까운 깨비참이 26프레임 궤적으로 화면 밖에서 비스듬히 들어와 레드 머리 위를 스치고 나간다(t20 오른쪽→왼쪽, t60 왼쪽→오른쪽 좌우반전, t110 다시; 1배). 비 14개 | `graphics/intro/scene_3/bg.png`·`bg.bin`·`bg.gbapal`; `graphics/credits/player_male.png`; `graphics/object_events/pics/pokemon/spearow.png`; `graphics/pokemon/spearow/front.png`·`normal.pal`; `graphics/weather/rain.png`+`default.gbapal`; `graphics/battle_anims/sprites/lightning.png`+`lightning_2.gbapal` | 전체 어둡게 9/16; 번개 1초에 1회, 회색 씻김 2프레임만 | 마디 3~4 |
| C4 10만볼트 | 365~518 | 1071~1224 | 154 | 번개 배경의 구름 줄(위 64줄)만 이어 세로로 흐르게(2px/프레임) 하고 전투처럼 어둡게 9/16. 피카츄는 **1배 고정**, t0~30 아래에서 가운데로 올라온다. 전기 고리 4개. 양옆 깨비참(1배, 왼쪽은 좌우반전) 위로 t48~55 노랑 번개가 내리치고, t50~61 흰 실루엣 3회 깜빡인 뒤 t62부터 같은 방향 그대로 아래로 떨어져 나간다. 회전 없음. t50~61 피카츄 ±1px 흔들림 | `graphics/battle_anims/backgrounds/thunder.png`·`thunder.bin`·`thunder.gbapal`(위 8타일 줄만); `graphics/pokemon/pikachu/front.png`; `graphics/pokemon/spearow/front.png`; `graphics/battle_anims/sprites/electricity.png`+`electric_orbs.gbapal`; `graphics/battle_anims/sprites/lightning.png` 프레임 0·2 + `lightning_2.gbapal`(노랑·흰색, 게임의 짝) | 어둡게 9/16; 흰 번쩍임 2프레임(t50); 흔들림 | 마디 5~6 |
| C5 갠 하늘과 칠색조 | 519~594 | 1225~1300 | 76 | 흰 화면에서 풀리면 맑은 하늘(배경색을 8줄마다 바꾼 12단). 날씨 구름 3개 2층(먼 층 1개 0.25px/프레임, 가까운 층 2개 0.75px/프레임, 좌우반전으로 변화). 칠색조 필드 스프라이트(1배, 2프레임 날갯짓, 금빛 재색)가 위 1/3을 3.6px/프레임으로 가로지르고 금빛 별 3개가 18px 간격으로 따른다. 아래 1/3 선에 레드 뒷모습(x40)과 피카츄 뒷모습(x120)이 겹치지 않게 머리를 둔다 | `graphics/weather/cloud.png`+`cloud.gbapal`; `graphics/object_events/pics/pokemon/ho_oh.png`(팔레트만 금빛 재색); `graphics/battle_anims/sprites/gold_stars.png`+`gold_stars.gbapal`; `graphics/trainers/back_pics/red_back_pic.png`; `graphics/pokemon/pikachu/back.png`·`normal.pal` | 흰색 16→0 페이드; 줄별 배경색 12단 | 마디 7 |
| → 타이틀 | 595 | 1301 | — | 마디 8 첫 박에서 타이틀로 | 기존 타이틀 | — | 타이틀 음악 |

컷 수 5, 합계 595프레임(9.92초). 원판 오프닝 구간(752프레임)보다 157프레임 짧다.

### 전원→타이틀 전체 흐름
저작권 화면(F0~) → 게임프리크 로고(~F705, 그대로) → 새 오프닝 C1~C5(F706~1300) → 타이틀(F1302 캡처 기준, 원판 F1459). 전원→타이틀 **약 21.7초**(원판 24.3초).

### 음악 (음악 감독 확인 필요)
`MUS_INTRO_FIGHT`는 t20(F726)에 시작하고, 마디 8 첫 박(t595)에서 타이틀로 넘어간다. 곡의 574프레임(9.6초, 12.1초 중)만 쓴다.
- 안 1(추천): 마디 8 첫 박에 곡을 끊고, 같은 프레임에 타이틀 곡을 시작한다(박 위의 컷이라 자연스럽다).
- 안 2: 마디 7 동안(C5) 곡을 페이드아웃하고 타이틀 곡을 시작한다.
- 안 3: 곡을 t0에 시작해(20프레임 앞당김) 마디 경계를 20프레임 당긴다. 원판 도입이 달라지므로 비추천.

### 연출 밀도 (원판 대비)
원판: 두 층 숲 가로 스크롤, 줌 1회, 흔들림, 흰 화면 전환, 포켓몬 둘. 안 B: 매 컷 2~3층(맵·스프라이트·날씨/전기), 세로 팬 1회, 가로 고속 스크롤 1회, 세로 흐름 1회, 아핀 확대·회전, 흔들림, 번쩍임, 등장 포켓몬 셋(피카츄·깨비참·칠색조)과 레드. 원판 이상.

## 3. 솔직한 평가 (목업 기준)
B2(2026-09-26): 아래 C4·C5 지적은 예술감독 필수 1~6으로 고쳤다(피카츄 1배 고정, 번개 노랑, 구름 줄만 어둡게, 깨비참 회전 없음, 칠색조 필드 스프라이트 1배, 하늘 12단, 구름 3개 2층). 남은 약점: C5 칠색조 필드 스프라이트는 정면을 보는 그림이라 옆으로 날아가도 몸이 정면이다. C3 가까운 깨비참은 1프레임 그림이라 날갯짓이 없다(궤적으로만 움직인다).

- C1·C2는 게임 그림 그대로라 원판과 나란히 두어도 품질 차이가 없다. 다만 C1은 오버월드 화면이라 "인트로"보다 게임 플레이처럼 보인다.
- C3은 어두운 숲·비·달리는 레드로 분위기가 난다. 64px 깨비참 앞모습이 한 방향으로만 떠 있어 "공격"이 약하다(에메랄드 2프레임 그림이 있으면 낫다).
- C4가 가장 약하다. 번개 배경의 분홍빛 팔레트가 폭풍처럼 보이지 않고(전투에서는 화면을 어둡게 블렌드한 위에 뜬다: ROM에서 같은 블렌드를 걸 것), 피카츄를 1.25배 넘게 키우면 아핀 확대로 픽셀이 뭉개진다. 확대는 1.25배까지만.
- C5는 칠색조 0.5배 축소가 거칠고, 하늘 그라데이션 4단이 딱딱하다. 대안: 0.5배 대신 필드 스프라이트 `ho_oh.png`(32×32 2프레임)를 실루엣으로, 하늘은 8단 이상.
- 무지개는 공식 그림이 없어 뺐다.

## 4. 예상 작업량 (예술감독·사용자 승인 뒤)
- 표 구동 플레이어 재사용. 추가: 맵 스트리밍(C1, 세로 팬 중 행 복사), 아핀 OBJ 트랙(C4·C5), 줄별 배경색(HBlank, C5), 전투 배경 슬라이드(C2).
- 컷별 생성기(공식 그림 → 타일 dedupe·팔레트 배치·키 표) 5개. 라운드 추정: 조립 2, 수정 2.
