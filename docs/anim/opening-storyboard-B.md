# 오프닝 안 B: 저장소 안의 공식 그래픽만 (2026-09-26, 예술감독 판정 전)

사용자 방향 전환(2026-09-26): 코드로 새로 그린 그림은 쓰지 않는다. **이 저장소에 이미 있는 게임 그래픽만** 쓰고, 코드는 배치·스크롤·확대(아핀)·팔레트 블렌드·타이밍만 한다. 그림에 가하는 변경은 팔레트 재색(칠색조 금빛 실루엣) 하나뿐. `/root/src/pokeemerald` 그래픽과 외부 일러스트는 쓰지 않는다.

목업: `tools/make_intro_opening_official_mock.py` → `docs/anim/drafts/official-B/` (컷별 key 프레임 1배·3배, `compare.png`·`compare_x3.png`: 왼쪽이 FR/LG 원판 캡처). 타일맵·타일셋 디코더는 `tools/official_gfx.py`(그리지 않고 하드웨어처럼 풀기만 한다).

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
| C1 출발 | 0~135 | 706~841 | 136 | 새벽의 태초마을. 레드가 집에서 나와 걸어가고, 카메라가 따라가며 1번도로 입구까지 북쪽으로 팬(세로 스크롤, 1~2px/프레임). 피카츄가 1칸 뒤에서 따라오다 t110에 멈춰 앉아 돌아본다(가기 싫다) | `data/layouts/PalletTown`·`Route1` + `data/tilesets/primary/general`·`secondary/pallet_town`; `graphics/object_events/pics/people/red_normal.png`; `graphics/object_events/pics/pokemon/pikachu.png` | 새벽 주황 블렌드 2/16→0; 맵 스트리밍(오버월드처럼 행 복사) | 전주 + 마디 1 |
| C2 볼이 싫은 피카츄 | 136~211 | 842~917 | 76 | 전투 무대. 배경이 양옆에서 밀려 들어오고(FR 전투 시작처럼), 레드 뒷모습이 던지기 5프레임, 볼이 포물선으로 날아간다. 피카츄가 튀어 오르며(t30~45) 전기를 튀기고 볼이 튕겨 나간다. 레드는 마지막 프레임에서 굳는다 | `graphics/battle_terrain/grass/terrain.png`+`.bin`; `graphics/trainers/back_pics/red_back_pic.png`; `graphics/pokemon/pikachu/front.png`; `graphics/interface/ball/poke.png`; `graphics/battle_anims/sprites/electricity.png` | 흰 번쩍임 2프레임(1회); 피카츄 울음(게임 기본) | 마디 2 |
| C3 폭우와 깨비참 | 212~364 | 918~1070 | 153 | 원판 인트로의 숲이 어두워진 채 빠르게 가로 스크롤(4px/프레임), 레드가 크레딧 달리기 주기로 달린다. 먼 하늘에 깨비참 떼(필드 스프라이트 9마리 날갯짓), 가까이 깨비참 둘이 내리꽂는다(아핀 0.75~1배). 비 스프라이트 14개가 대각선으로 | `graphics/intro/scene_3/bg.png`+`.bin`; `graphics/credits/player_male.png`; `graphics/object_events/pics/pokemon/spearow.png`; `graphics/pokemon/spearow/front.png`; `graphics/weather/rain.png`; `graphics/battle_anims/sprites/lightning.png` | 전체 어둡게 9/16; 번개 번쩍임 1초에 1회(2프레임, 8/16); 흔들림 ±1px | 마디 3~4 |
| C4 10만볼트 | 365~518 | 1071~1224 | 154 | 전투 애니의 번개 배경이 세로로 흐르고, 피카츄가 가운데로 다가온다(아핀 1→1.25배, 원판 F1376 줌처럼). 전기 고리가 돌고, t50부터 번개가 내리쳐 깨비참 둘이 흰 실루엣으로 깜빡이다 돌며 떨어진다 | `graphics/battle_anims/backgrounds/thunder.png`+`.bin`; `graphics/pokemon/pikachu/front.png`; `graphics/pokemon/spearow/front.png`; `graphics/battle_anims/sprites/electricity.png`, `lightning.png` | 흰 번쩍임 ≤3/초(20프레임 간격); 흔들림; 깨비참 흰색 블렌드 | 마디 5~6 |
| C5 갠 하늘과 칠색조 | 519~594 | 1225~1300 | 76 | 흰 화면에서 풀리면 맑은 하늘(배경색을 줄마다 바꾼 단계 그라데이션), 날씨 구름이 흐르고, 칠색조 금빛 실루엣(0.5배)이 멀리 가로지르며 금빛 별 꼬리를 남긴다. 아래에 레드와 피카츄의 뒷모습이 함께 올려다본다 | `graphics/weather/cloud.png`; `graphics/pokemon/ho_oh/front.png`(팔레트만 금빛으로 재색); `graphics/battle_anims/sprites/gold_stars.png`; `graphics/trainers/back_pics/red_back_pic.png`; `graphics/pokemon/pikachu/back.png` | 흰색 16→0 페이드; 줄별 배경색 | 마디 7 |
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
- C1·C2는 게임 그림 그대로라 원판과 나란히 두어도 품질 차이가 없다. 다만 C1은 오버월드 화면이라 "인트로"보다 게임 플레이처럼 보인다.
- C3은 어두운 숲·비·달리는 레드로 분위기가 난다. 64px 깨비참 앞모습이 한 방향으로만 떠 있어 "공격"이 약하다(에메랄드 2프레임 그림이 있으면 낫다).
- C4가 가장 약하다. 번개 배경의 분홍빛 팔레트가 폭풍처럼 보이지 않고(전투에서는 화면을 어둡게 블렌드한 위에 뜬다: ROM에서 같은 블렌드를 걸 것), 피카츄를 1.25배 넘게 키우면 아핀 확대로 픽셀이 뭉개진다. 확대는 1.25배까지만.
- C5는 칠색조 0.5배 축소가 거칠고, 하늘 그라데이션 4단이 딱딱하다. 대안: 0.5배 대신 필드 스프라이트 `ho_oh.png`(32×32 2프레임)를 실루엣으로, 하늘은 8단 이상.
- 무지개는 공식 그림이 없어 뺐다.

## 4. 예상 작업량 (예술감독·사용자 승인 뒤)
- 표 구동 플레이어 재사용. 추가: 맵 스트리밍(C1, 세로 팬 중 행 복사), 아핀 OBJ 트랙(C4·C5), 줄별 배경색(HBlank, C5), 전투 배경 슬라이드(C2).
- 컷별 생성기(공식 그림 → 타일 dedupe·팔레트 배치·키 표) 5개. 라운드 추정: 조립 2, 수정 2.
