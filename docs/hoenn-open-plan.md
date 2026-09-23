# 호연 전면 개방 계획 (hoenn-open-plan)

pokeemerald에서 가져온 호연 지역(맵 457개, 트레이너·아이템·야생표 포함, `docs/hoenn-import.md`)을 버리지 않고, 구역별로 나누어 **한 단계 = 한 릴리스**로 차례차례 여는 계획이다. 이 문서는 계획만 담으며 게임 코드·데이터·맵·스크립트는 바꾸지 않았다. 새로 넣은 것은 분석 스크립트 둘(`tools/hoenn_reachability.py`, `tools/check_map_integrity.py`)과 공용 모듈(`tools/mapdata_common.py`)뿐이다.

## 다시 만들기

```
python3 tools/hoenn_reachability.py --emerald /root/src/pokeemerald   # 부록 A (맵 전체 표, 마크다운)
python3 tools/hoenn_reachability.py --zones                           # 부록 B (구역 요약·경계)
python3 tools/hoenn_reachability.py --format json --all               # 칸토 포함 전체를 JSON으로
python3 tools/check_map_integrity.py --limit 12 --no-fail             # 부록 C (무결성 검사)
```

- 둘 다 저장소를 읽기만 한다. `--emerald`는 원작 오브젝트·좌표 이벤트 수 비교용 열(em_obj/em_coord)을 더한다(없어도 된다).
- `check_map_integrity.py`는 ERROR가 있으면 종료 코드 1을 낸다(`--no-fail`로 끔). 업스트림 비교는 `upstream/master`(pret/pokefirered)를 `git show`로 읽고, 없으면 건너뛴다.
- 이 문서의 숫자는 master `2481685e2`(v0.6.0 계획 커밋) 기준이다.

---

## 0. 요약

- **호연 맵 457개 중 칸토(태초마을)에서 이어지는 맵은 282개**, 다이빙이 있어야 이어지는 맵 10개, 스크립트가 열어 줘야 하는 워프 칸 뒤의 맵 25개, 전혀 이어지지 않는 맵 140개다. 칸토→호연 입구는 공항 창구의 비행기 하나뿐이다(`KantoAirport` → `SlateportCity_Harbor`, `src/airplane_flight.c:58-61`). 비행기는 **카이나시티(슬레이트포트) 항구**에 내린다. 의뢰문의 "Lilycove 항구"와 다르다(6절 Q1).
- 전당등록만 하면 지금도 호연 282개 맵을 자유롭게 돌아다닐 수 있다. 단계별 개방은 "새로 여는" 작업이면서 동시에 "지금 열려 있는 곳을 닫는" 작업이 된다(6절 Q3).
- **이미 릴리스에 들어 있는 결함 두 가지**(v0.2.0부터, 코드 근거와 에뮬레이터 확인 포함, 1.5절):
  1. 호연 도로 15곳의 나무열매 나무 자리 오브젝트 87개가 콜백이 `NULL`인 이동 타입을 써서, **화면에 들어오면 게임이 타이틀 화면으로 리셋된다**(111번 도로 등. 104번 도로 (36,9)와 102번 도로 (24,5)에서 확인).
  2. 호연 숨은 아이템 110개의 플래그(0x4A7~0x514)가 칸토 관장 격파 플래그 13개(0x4B0~0x4BC), 트레이너 플래그 21개(0x500~0x514), "빈" 플래그 76개와 겹친다. 챔피언 세이브에서는 호연 숨은 아이템 13개가 영영 나오지 않고, 칸토 문서가 센 "빈 플래그 531개" 중 67개는 이미 쓰이고 있다.
- 엔진: 트레이너·아이템·NPC·전설 전투·배회·에메랄드 날씨 전 종류·시계는 이미 된다. 다이빙은 코드 절반이 남아 있어 "중" 정도의 이식이 필요하다. 나무열매 재배·컨테스트·비밀기지·배틀프런티어·마하/곡예 자전거·2대1 배틀·포켓내비는 없다. 4세대 이후 규칙(물리/특수 분리, 4세대 이후 특성·종)은 불가능하다(2절).
- 단계: 구역 8개(Z1~Z8)를 8단계로 연다(4절). **1단계 추천은 Z1 "카이나 항구권"**(비행기 도착지, 차단 지점 4곳, 공통 선행 작업 말고는 새 C 코드 없음, 나무열매 나무 0개). 대안은 Z2 "Mauville 전기권", Z3 "남서부 시작의 땅"(7절).
- 모순·결정 질문 12개(6절). 특히 **v0.6.0 자리를 누가 쓰는가**(Q2)와 **칸토에 이미 있는 호연 전설을 어떻게 할 것인가**(Q4)는 1단계 착수 전에 정해야 한다.

---

## 1. 현황 인벤토리

### 1.1 방법

`tools/hoenn_reachability.py`는 맵 단위 그래프를 만든 뒤 `MAP_PALLET_TOWN`에서 너비 우선으로 따라간다. 간선은 다음과 같다.

| 간선 | 출처 | 비고 |
|---|---|---|
| 맵 연결 | `map.json`의 `connections` (상하좌우) | 선언된 방향만 따라간다 |
| 다이빙 연결 | `connections`의 `dive`/`emerge` | 엔진에서 다이빙을 쓸 수 없어(2절) 따로 센다 → 표의 `D` |
| 워프 | `map.json`의 `warp_events` | 워프 칸의 메타타일 행동값을 읽어, 문·계단·사다리·동굴 입구·화살표 칸(`src/field_control_avatar.c:952` `IsWarpMetatileBehavior` 등)이 아니면 **닫힌 워프**로 따로 센다 → 표의 `W` |
| 스크립트 워프 | `warp`·`warpsilent`·`warpdoor`·`warphole`·`warpteleport`·`warpspinenter`와 `setwarp`·`setdynamicwarp`·`setdivewarp`·`setholewarp` | 맵 스크립트에서 goto/call/이어지는 라벨을 따라 공용 `data/scripts/*.inc`까지 추적한다. 표의 `via`에 `script`로 표시 |
| C 스페셜 워프 | `special DoAirplaneFlightScene`(목적지 표 `sDestinations`), `special DoSeagallopFerryScene`(`sSeagallopSpawnTable`) | 목적지는 C 소스의 `MAP(MAP_X)`에서 읽는다 → `special` |

- 닫힌 워프 판정 검증: 같은 방법으로 칸토를 보면 사천왕 방, 루비 길, 로켓 창고, 저택 B4F처럼 **스크립트가 메타타일을 바꿔야 열리는 곳만** 걸러진다. 호연에서는 Ever Grande 사천왕 방, Sky Pillar, Terra Cave, 알터링 동굴(원작도 전당등록 뒤 스크립트로 개방), Trick House 퍼즐 문이 여기에 든다. 원작 에메랄드의 같은 칸도 같은 행동값이다(대조 결과 121개 중 Trick House 문 8개·Sky Pillar 문 1개·Shoal Cave 입구 1개만 에메랄드 전용 행동값이 `MB_NORMAL`로 바뀐 것).
- 한계: 스토리 플래그, 비전머신, 맵 안에서 워프가 어느 섬에 있는지는 보지 않는다. "Y"는 "이어져 있다"는 뜻이지 "지금 걸어갈 수 있다"는 뜻이 아니다. 비행기는 `FLAG_SYS_GAME_CLEAR`가 있어야 탄다(`data/maps/KantoAirport/scripts.inc:80-92`). 호연 FLY는 이미 발을 들인 마을로만 가므로 새 맵을 열지 않는다.
- 같은 스크립트로 칸토를 재면 칸토·세비 맵 433개 중 423개가 이어진다. 빠지는 10개는 프로토타입 섬 4개, 쓰지 않는 집 4개, 레코드 코너, 글리치 시티(C 코드가 보내는 가짜 맵)로 모두 원래 갈 수 없는 곳이다.

### 1.2 결과

| 구분 | 맵 수 | 설명 |
|---|---|---|
| Y | 282 | 칸토에서 비행기 → 카이나 항구로 이어짐 |
| D | 10 | 다이빙 연결 뒤(해저 도로 7, 해저 Sootopolis, 해저 Seafloor Cavern 입구, 해저 Marine Cave 입구) |
| W | 25 | 닫힌 워프 칸 뒤(Ever Grande 사천왕 방·전당 9, Sky Pillar 8, Terra Cave 2, Trick House 3, 알터링 동굴, Meteor Falls 성호의 동굴, Mossdeep 게임코너 B1F) |
| - | 140 | 이어지지 않음(아래 1.4) |

- 호연 맵의 오브젝트: 대화만 하는 NPC 692, 트레이너 429(스크립트 기준, `TRAINER_HOENN_*` 520명 중), 아이템볼 162, 간호순·점원 39, 나무열매 나무 자리 87, 표지판 318, 숨은 아이템 110. 좌표 이벤트(트리거)는 **0개**다.
- 원작 대비: 에메랄드의 같은 맵에는 오브젝트 2,471개와 좌표 이벤트 362개가 있다. 이식 때 스토리 플래그가 붙은 오브젝트(라이벌·악의 조직·관장 일부·전설 등)는 모두 빠졌고(`tools/hoenn_import/import_maps.py:257`), 좌표 이벤트는 통째로 비웠다(`import_maps.py:291`). 그래서 호연 이벤트 대부분은 "다시 배치"가 아니라 "새로 쓰기"다.
- 야생표가 있는 호연 맵 116개, 회복 지점 22곳(맵 20개).
- 관장 중 지금 싸울 수 있는 사람: ROXANNE, BRAWLY, FLANNERY, WINONA, TATE&LIZA(더블), JUAN(Sootopolis라 도달 불가). 이기면 대사만 나오고 배지·기술머신은 없다. WATTSON, NORMAN, 사천왕·챔피언, 라이벌, 아쿠아·마그마단은 **트레이너 데이터만 있고 맵에 없다**(`include/constants/opponents.h`에 `TRAINER_HOENN_WATTSON_1`, `TRAINER_HOENN_SIDNEY`, `TRAINER_HOENN_GRUNT_MUSEUM_1` 등).

### 1.3 구역별 요약

구역 정의는 4.2절, 맵 목록은 부록 B. `reach Y`는 지금 이어진 맵 수, `bt`는 나무열매 나무 자리(리셋 원인) 수다.

| 구역 | 이름 | 맵 | reach Y | NPC | 트레이너 | 아이템볼 | 숨은 | bt | 야생표 맵 | 회복 |
|---|---|---|---|---|---|---|---|---|---|---|
| Z1 | 카이나 항구권 | 41 | 37 | 72 | 49 | 18 | 16 | 0 | 12 | 2 |
| Z2 | Mauville 전기권 | 35 | 25 | 59 | 60 | 21 | 8 | 9 | 5 | 2 |
| Z3 | 남서부 시작의 땅 | 52 | 50 | 110 | 62 | 28 | 15 | 24 | 11 | 6 |
| Z4 | 화산·사막권 | 55 | 54 | 62 | 56 | 26 | 11 | 11 | 24 | 2 |
| Z5 | 날개·항구권 | 68 | 64 | 152 | 76 | 40 | 28 | 43 | 20 | 2 |
| Z6 | 바다권 | 94 | 39 | 75 | 106 | 22 | 24 | 0 | 38 | 3 |
| Z7 | Ever Grande 리그 | 19 | 10 | 13 | 11 | 5 | 3 | 0 | 4 | 1 |
| Z8 | 포스트게임 시설 | 93 | 3 | 149 | 9 | 2 | 5 | 0 | 2 | 2 |

### 1.4 이어지지 않는 맵(140개)과 이유

| 맵 | 개수 | 이유 |
|---|---|---|
| Sootopolis와 실내 16, Seafloor Cavern 10, Cave of Origin 6(미사용 3 포함), Sealed Chamber 2와 해저 입구 1, 해저 134번 도로, 버려진 배 수중·숨은 층 4 | 40 | 원작은 해저 맵의 `MAP_SCRIPT_ON_DIVE_WARP`에서 `setdivewarp`로 떠오를 곳을 정하는데, 이식된 맵 스크립트는 `.byte 0`뿐이라 떠오를 곳이 없다(에메랄드에서 `setdivewarp`를 쓰는 맵 15곳). 다이빙 이식(2.2절)과 함께 해결 |
| 배틀프런티어 시설·라운지 47, 배틀 피라미드 방 16, 배틀텐트 복도·전투실 6 | 69 | 원작은 S.S. TIDAL와 시설 C 코드로 이동. 배틀텐트 로비만 마을에서 이어진다 |
| 컨테스트 홀 6, Mauville 트럭 안, S.S. TIDAL 3, Southern Island 2, Faraway Island 2, Artisan Cave 2, Marine Cave 2, Shoal Cave 만조 방 2, Lilycove 미사용 마트, Trick House 퍼즐 2~8(7), 아쿠아 아지트 루비 미사용 맵 3 | 31 | 배·티켓·C 스페셜·물때로만 들어가거나 원작에서도 쓰지 않는 맵 |

### 1.5 이미 릴리스된 결함

**(1) 나무열매 나무 자리 = 리셋**

- 이식 스크립트는 에메랄드 나무열매 나무를 스크립트 없는 `OBJ_EVENT_GFX_MAN` 오브젝트로 옮기면서 이동 타입 `MOVEMENT_TYPE_BERRY_TREE_GROWTH`를 그대로 두었다. FR/LG에서는 이 타입의 스프라이트 콜백이 `NULL`이다(`src/event_object_movement.c:244`). 스프라이트 콜백은 매 프레임 호출되므로(`src/sprite.c:313`) 오브젝트가 생성되는 순간 주소 0으로 뛰어 리셋된다.
- 에뮬레이터 확인: `saves/pokemonthyl_v3.gba.sav`를 104번 도로 (36,9)(나무 (34~36,6) 바로 아래)로 옮겨 이어하기 → 640프레임 뒤 `gMain.callback2`가 `CB2_TitleScreenRun`. 같은 맵 (17,50)에서는 정상 필드. 102번 도로 (24,5)도 리셋.
- 대상: 102·103·104·110·111·112·114·115·116·117·118·119·120·121·123번 도로, 87개(부록 C).
- 고치는 방법(데이터만으로 가능): 이식 스크립트에서 해당 오브젝트를 빼거나 이동 타입을 `MOVEMENT_TYPE_FACE_DOWN`으로 바꾼다. 나무열매 재배를 이식할 때 다시 넣는다. **다음 릴리스와 상관없이 핫픽스 대상**이다(6절 Q12).

**(2) 호연 숨은 아이템 플래그 겹침**

- 숨은 아이템은 `FLAG_HIDDEN_ITEMS_START(1000) + id` 플래그를 쓰고, 이식 스크립트는 FR/LG 숨은 아이템 191개 뒤를 "아무도 쓰지 않는다"고 보고 이어 붙였다(`tools/hoenn_import/import_maps.py:56, 115`). 그러나 1191~1300(0x4A7~0x514)은 비어 있지 않다(`include/constants/flags.h:1225-1319`, `include/constants/flags_hoenn.h:170-279`).

| 호연 숨은 아이템 | 플래그 | 겹치는 것 | 영향 |
|---|---|---|---|
| 0~8 | 0x4A7~0x4AF | `FLAG_UNUSED_0x4A7~4AF` | "빈" 플래그가 실제로는 사용 중 |
| 9~21 (104·105·106·108·109번 도로의 13개, 108번 도로 이상한사탕 포함) | 0x4B0~0x4BC | `FLAG_DEFEATED_BROCK`~`FLAG_DEFEATED_CHAMP` | 챔피언 세이브에서는 이미 켜져 있어 **절대 주울 수 없음** |
| 22~88 | 0x4BD~0x4FF | `FLAG_0x4BD~0x4FF`(이름상 빈 플래그 67개) | 칸토 새 이벤트가 이 번호를 쓰면 호연 아이템과 충돌 |
| 89~109 | 0x500~0x514 | 트레이너 0~20번의 격파 플래그(`TRAINER_NONE`, 쓰지 않는 RS 자리 트레이너) | 지금은 무해. 빈 트레이너 번호로 재사용하면 충돌 |

- 고치는 방법(C 코드, 세이브 구조는 그대로): id 191 이상인 숨은 아이템의 플래그를 `hoennFlags` 블록(0x1000~, `src/event_data.c:262`)으로 옮기고, 이미 주운 세이브를 위해 1회 이전(0x4A7~0x4AF·0x4BD~0x514의 비트 복사 후 지움, 이전 완료 플래그 1개)을 한다. 0x4B0~0x4BC 13개는 원래 주울 수 없었으므로 이전할 것이 없다.

**(3) 그 밖에 지금 열려 있는 것**

- 아쿠아단 아지트 B1F 아이템볼의 **마스터볼**(`data/maps/AquaHideout_B1F/scripts.inc:9`)을 챔피언이면 지금 주울 수 있다. 칸토 실프 사장의 마스터볼과 중복이다.
- 트레이너가 스토리 없이 모두 배치돼 있어, 1단계에서 닫는 구역의 트레이너를 이미 이긴 세이브가 있다(격파 기록은 `hoennTrainerFlags`에 남는다).
- 호연 트레이너 레벨: 파티 975마리 평균 Lv26, 최저 3, 최고 78(`src/data/trainer_parties_hoenn.h`). 비행기는 챔피언만 타므로 대부분 너무 약하다(6절 Q9).

---

## 2. 엔진 한계

> **메모리 여유 (2026-09-22 빌드 기준, 확인함)**: EWRAM 261,604 / 262,144바이트(99.79%, 남은 540바이트), IWRAM 29,900 / 32,768바이트(91.25%), ROM 15.4MB / 32MB(46%). 즉 **롬 공간은 넉넉하지만 EWRAM은 사실상 꽉 찼다.** 콘테스트·비밀기지·배틀프론티어처럼 큰 작업용 버퍼가 필요한 기능은 EWRAM을 먼저 확보해야 한다(쓰지 않는 링크·유니온룸·퀘스트로그 버퍼 정리 등). 이벤트·대사·맵 위주의 단계(1단계 A안 포함)는 EWRAM을 거의 쓰지 않는다.
>
> **맵 스크립트 주의**: `MAP_SCRIPT_ON_TRANSITION` 안에서는 `specialvar VAR_RESULT, X` 뒤의 `call_if_eq`·`goto_if_eq`가 기대대로 동작하지 않았다(v0.6.0 작업에서 확인). 오브젝트를 조건부로 숨길 때는 C 쪽 special이 직접 `FlagSet`/`FlagClear` 하도록 만든다(`OldTimer_Setup`·`SummitTrainer_Setup`·`SilverMountain_SetBlizzardGate` 참고).


### 2.1 이미 되는 것

| 기능 | 상태 | 근거 |
|---|---|---|
| 호연 맵·타일셋·타일 애니·음악·지역 지도·호연 안 FLY | 됨 | `docs/hoenn-import.md`, `src/region_map.c`(`sHoennFlyDestinations`), `include/constants/flags_hoenn_map.h` |
| 호연 트레이너 전투(싱글·더블) | 됨. 520명, 격파 기록은 `SaveBlock2.hoennTrainerFlags`(1024비트, 504비트 남음) | `src/battle_setup.c:696`, `include/global.h:357` |
| 아이템볼·숨은 아이템 | 됨(숨은 아이템은 1.5절 결함) | `include/constants/flags_hoenn.h` |
| 대화 NPC·표지판·마트·간호순·회복 지점 | 됨(원작 첫 대사만) | `import_maps.py` `script_for` |
| 야생 포켓몬(풀·물·바위깨기·낚시, 아침·밤 표 선택 필드) | 됨. 호연 맵 116개 | `src/data/wild_encounters.json` |
| 전설 고정 전투 | 됨. `BATTLE_TYPE_LEGENDARY`·`KYOGRE_GROUDON`·`REGI`가 남아 있고, 칸토 이벤트가 이미 가이오가·그란돈·레쿠쟈·레지 3마리를 `setwildbattle`로 쓴다 | `include/constants/battle.h:59-62`, `data/maps/SevenIsland_TanobyRuins_*` |
| 배회 포켓몬 | 됨. 슬롯 3개(전설의 개 1 + 라티 2) | `src/roamer.c`, `include/constants/vars.h:202` |
| 날씨 | FR/LG에 에메랄드 날씨 콜백이 모두 남아 있다: 구름·맑음·비·눈·뇌우·가로 안개·화산재·모래바람·대각선 안개·그늘·가뭄·폭우·물거품. 좌표 이벤트로 날씨 바꾸기와 119·123번 도로 순환도 있다 | `src/field_weather.c:68-83`, `src/coord_event_weather.c:34`, `src/field_weather_util.c:87`. 단 "가뭄"은 필드에서 깨진다는 주석(`include/constants/weather.h:16`) |
| 시계(RTC 또는 가상 시계)·아침/낮/밤 | 됨(로드맵 2 · 9번) | `src/rtc.c`, `src/siirtc.c`, `src/time_of_day.c` |
| 맵 스크립트 종류 | `MAP_SCRIPT_ON_DIVE_WARP`까지 있다(FR/LG는 안 씀) | `include/constants/map_scripts.h:9`, `src/script.c:458` |
| 필드 기술 | 풀베기·공중날기·괴력·파도타기·바위깨기·폭포오르기·플래시 등 | `include/constants/party_menu.h:37-49` |
| 얼음·회전 바닥 | `MB_ICE`·`MB_THIN_ICE`·`MB_CRACKED_ICE`, `MB_SPIN_*`가 있다(Sootopolis 체육관 얼음, Mossdeep 체육관 회전판 재현에 쓸 수 있음) | `include/constants/metatile_behaviors.h:30-33, 66-69` |
| 점자 글자 | 있음(유적의 골짜기) | `src/braille_text.c` |
| 사파리존·키우미집·전당 | 칸토용으로 있음. 호연 사파리·117번 도로 키우미집은 같은 코드·같은 저장 공간을 공유하게 된다 | `src/safari_zone.c`, `src/daycare.c`, `src/hall_of_fame.c` |
| 포획 시범 전투 | FR/LG 노인 시범과 에메랄드 WALLY 시범이 같은 비트 | `include/constants/battle.h:56` |
| 호연 인물 필드 그림 | 59종 이식(아쿠아·마그마 단원, 관장 전원, 사천왕, 성호, WALLY, 털보박사, 라이벌, 브리니 배 등) | `include/constants/event_objects.h` 170~231번대 |
| 호연 키 아이템 데이터 | 데봉 소포·편지·스캐너·데봉스코프·고글·재 주머니·마하/곡예 자전거 등 아이템 번호와 이름은 있다(기능은 아래) | `include/constants/items.h:270-299` |

### 2.2 이식하거나 새로 만들어야 하는 것

| 기능 | 현재 | 필요한 일 | 규모 | 필요한 구역 |
|---|---|---|---|---|
| **다이빙** | `FldEff_UseDive`(`src/field_effect.c:1688`), `dive_warp`·`TrySetDiveWarp`(`src/field_control_avatar.c:1169-1210`), `SetDiveWarp`(`src/overworld.c:725`), 수중 아바타 상태(`src/field_player_avatar.c:695`)는 있다. 파티 메뉴 필드 기술에 다이빙이 없고(`party_menu.h:37-49`), A/B로 잠수·부상하는 입력 처리가 호출되지 않으며(`TrySetDiveWarp`는 정의만 있음), 수중 주인공 그림이 없다 | 파티 메뉴 항목, 입력 처리, 수중 주인공 남·여 그림 2장(그림 번호 2칸 사용), 15개 맵의 `ON_DIVE_WARP` 스크립트 | 중 | Z6, Z8 일부 |
| **나무열매 재배** | `src/fldeff_berrytree.c`는 빈 함수("From R/S, removed"), `src/berry.c`는 열매 데이터뿐, SaveBlock1에 나무 배열이 없다 | 나무 상태 저장 공간(예: `SaveBlock1.unused_348C[400]`), 성장 로직, 물주기·수확 스크립트. 또는 "하루 1회 줍기" 같은 단순판 | 중~상 | Z2~Z5 도로(87그루) |
| **컨테스트** | 없음. 컨테스트 홀 맵 6개는 이식됐으나 도달 불가 | 에메랄드 `contest*.c` 약 13,300줄 + 포켓블록·블렌더 | 상 | Z5(Lilycove), Z2·Z4 로비 |
| **비밀기지** | 없음. 비밀기지 맵은 이식에서 제외(`import_maps.py:12` `EXCLUDE`), 비밀의 힘 자리 행동값은 평지로 바꿈 | `secret_base.c`·`decoration.c` 약 5,000줄, 맵·레이아웃 추가(그룹 끝·`layouts.json` 끝), 세이브 공간 | 상 | 전 구역(Z8로 묶음) |
| **배틀프런티어** | 없음. `src/battle_tower.c`는 RS 배틀타워의 잔재. 프런티어 맵 49개+피라미드 16개 도달 불가 | 에메랄드 시설 코드 약 27,000줄, 프런티어 패스·BP. 축소판(배틀타워만)도 가능 | 상 | Z8 |
| **마하·곡예 자전거** | 아바타 플래그 흔적만 있음(`src/bike.c:304-380`). 진흙 비탈·외나무 레일은 이식 때 평지로 바꿈 | 자전거 물리 이식 또는 해당 퍼즐을 다른 방식으로 대체 | 중 | Z2(사이클링로드), Z4, Z5 |
| **2대1 배틀·동료와 함께 싸우기** | FR/LG는 에메랄드의 `BATTLE_TYPE_TWO_OPPONENTS` 비트를 유령 전투(`BATTLE_TYPE_GHOST`)로 쓴다(`battle.h:63`). 동료(INGAME_PARTNER) 없음 | 원작의 단원 2명 동시 전투·성호와의 태그배틀(Mossdeep 우주센터)은 더블배틀 1인 파티로 각색하거나 전투 코드 확장 | 중~상 | Z4, Z6 |
| **좌표 이벤트 전반** | 이식 때 362개 모두 삭제 | 필요한 것만 새로 씀(모래바람 날씨 경계, 라이벌 등장 트리거 등) | 단계마다 | 전 구역 |
| **케이블카** | `src/cable_car_util.c`만 있음 | 에메랄드 케이블카 화면 이식 또는 페이드 워프로 대체 | 하~중 | Z4 |
| **회전문(Fortree 체육관)·Mirage Tower 붕괴·Trick House 장치** | 없음(`rotating_gate.c`, `mirage_tower.c` 없음). Trick House·Sky Pillar 문 행동값은 평지로 바뀜 | 이식 또는 퍼즐 재설계 | 중 | Z5, Z4, Z2 |
| **포켓내비·매치콜·TV·레코드 믹싱·유행어·Mauville 노인** | 없음. 저장 구조의 자리는 남아 있다(`include/global.h:803-804` `oldMan`, `dewfordTrends` "unused") | 필요하면 대사형 NPC로 대체(추천) | — | Z1, Z2 |
| **호연 배지 표시** | 트레이너 카드는 칸토 배지 8개만 | 호연 배지 플래그(`hoennFlags`)와 표시 방식(키 아이템 "배지 케이스" 대사, 또는 카드 뒷면 새 화면) | 하~중 | Z1부터 |
| **닫힌 구역 FLY 막기** | 방문 플래그만 보면 날 수 있다(`src/region_map.c:3021-3023`) | 구역 개방 플래그도 함께 보게 하는 C 수정(4.0절) | 하 | 1단계부터 |

### 2.3 불가능하거나 하지 않는 것

| 항목 | 이유 |
|---|---|
| 4세대 이후 포켓몬·폼 | 종 번호는 3세대까지(`include/constants/species.h:422-424`, `NUM_SPECIES` = 알 412). 프로젝트 규칙도 1~3세대만 |
| 물리/특수 분리(4세대 규칙) | 3세대 엔진은 타입으로 가른다(`include/battle.h:475-476`, `src/pokemon.c:2496, 2550`) |
| 3세대 이후 특성 | 특성은 78개(`include/constants/abilities.h:83`) |
| 페어리 타입, 메가진화·원시회귀·Z기술, ORAS 하늘 날기·도감 내비 | 전투·필드 엔진 전면 개편이 필요. ORAS 요소는 "구조적 아이디어"로만 쓴다(3절) |
| 실기 카트리지 RTC | 정품 FR/LG 카트리지에 시계 칩이 없다. 가상 시계로 자동 대체(로드맵 2 · 9번) |
| SaveBlock 구조 변경 | 프로젝트 규칙. 새 기록은 빈 플래그·변수·패딩(`hoennFlags`, `hoennTrainerFlags`, `SaveBlock2.filler_CA0[0x280]`, SaveBlock1의 `unused_348C[400]` 등)에만 |
| 오브젝트 그림 번호 대폭 추가 | `graphicsId`가 u8이고 세이브의 오브젝트 구조에도 u8로 들어간다(`include/global.fieldmap.h:117, 247`). 번호 232~239의 **8칸만 남았다**(`include/constants/event_objects.h:241-246`, 240부터는 VAR 그림). 새 그림은 재색칠+VAR 그림 공유로 아껴 써야 한다 |

### 2.4 저장 공간 현황 (검사기 실측)

| 자원 | 사용 / 한도 | 여유 | 비고 |
|---|---|---|---|
| 칸토 플래그(이름이 FLAG_0x·UNUSED) | — | **464** | 이름 수는 531이지만 67개(+UNUSED 9개)는 호연 숨은 아이템이 사용 중 |
| 호연 플래그 블록 `hoennFlags` | 180 / 2048비트 | 1868 | 아이템 0x000~0x0A1, FLY 0x400~0x411. 호연 스토리 플래그는 여기에 둔다 |
| 저장 변수 `VAR_0x40xx` | — | 56 | 호연 스토리에는 부족. 대안은 4.1절 P3 |
| FR/LG 트레이너 번호 | 753 / 768 | 15 | v0.6.0 계획이 이미 이 여유를 쓴다 |
| 호연 트레이너 번호(`hoennTrainerFlags`) | 520 / 1024 | 504 | v0.6.0 토너먼트 파티도 여기 뒤를 쓴다(6절 Q10) |
| 오브젝트 그림 번호 | 232 / 240 | 8 | 위 2.3 |
| 맵 그룹 | 76그룹, 맵 890 | 그룹당 255 | 새 맵은 해당 그룹 끝에 |

---

## 3. 이벤트 설계 규칙

1. **기본은 RSE·ORAS 원작 이벤트의 각색이다.** 호연 맵마다 루비·사파이어·에메랄드(필요하면 오메가루비·알파사파이어)의 원래 이벤트를 장소·순서·보상 위주로 살리고, 이야기는 이 해킹의 옐로식 흐름에 맞춘다: 주인공은 칸토 챔피언이고 오박사의 피카츄가 따라다니며, 분위기는 애니메이션풍으로 가볍다. 로켓단 3인조(`data/scripts/rocket_trio.inc`)는 개그 담당으로 등장할 수 있다(6절 Q11).
2. **칸토에서 이미 일어난 일은 이야기가 인정한다.** 예: 가이오가를 유적의 골짜기에서 이미 잡은 세이브라면 Seafloor Cavern 사건에서 "그 포켓몬이 반응한다"는 식으로 분기한다(5.3절).
3. **4~8세대와 팬게임은 구조적 아이디어로만** 쓴다(예: 동행 NPC 구간, 시설의 규칙 형식, 소문 수집 방식). 4세대 이후 포켓몬·기술·특성·메가진화 같은 메커니즘은 넣지 않는다.
4. **팬게임의 스크립트·대사·그래픽·데이터 복사 금지.** 참고한 경우에도 결과물은 새로 쓴다.
5. **대사는 모두 새로 쓴다.** 지금 호연 NPC가 말하는 에메랄드 첫 대사(이식 자동 생성)는 임시로 보고, 구역을 열 때 그 구역 NPC 대사를 새로 쓴다(범위는 6절 Q6).
6. **그림은 FR/LG 화풍.** 가능하면 기존 그림 재색칠. 새 그림은 승인 뒤 FR/LG 명암·외곽선 규칙으로(이식된 에메랄드 그림의 처리는 6절 Q7).
7. **1~3세대 포켓몬만.** 파티·야생·선물 모두.
8. **이벤트마다 힌트 NPC.** 호연용 소문 수집가를 카이나시티 포켓몬센터에 새로 두고(칸토의 무지개시티·1의섬 방식), 이벤트 근처 NPC 대사로도 알린다.
9. **세이브 호환.** SaveBlock 구조·순서 변경 금지. 새 플래그는 `hoennFlags`, 새 변수는 4.1절 P3 방식, 새 맵은 그룹 끝, 새 레이아웃은 `layouts.json` 끝. 호연 트레이너 격파는 `hoennTrainerFlags`. 단계마다 `savetest_all.sh`와 `check_map_integrity.py`.
10. **이식 스크립트와의 관계.** 호연 맵은 `tools/hoenn_import/import_maps.py`가 다시 만들므로, 손으로 고친 이벤트는 `tools/hoenn_import/patches/<Map>.*`에 두거나(현재 방식), 구역을 연 맵은 이식 대상에서 빼는 목록을 둔다(1단계 착수 때 결정).
11. **원작 참조 기록.** 각 단계의 구현 기록에 원작 이벤트 이름·원작 값·바꾼 점을 `docs/events-roadmap.md` 구현 기록 형식으로 남긴다.

---

## 4. 단계별 개방 로드맵

### 4.0 공통 규칙: 차단과 막다른 길

- **차단 방식**: 구역 경계(부록 B의 "Cross-zone edges")마다 차단 NPC를 둔다. 도로 연결은 경계 칸 바로 앞에 선 NPC(말을 걸면 이유를 말하고 한 칸 되돌림), 건물·동굴은 입구 앞 NPC나 "공사 중" 표지판. NPC는 해당 단계의 개방 플래그가 서면 사라진다(`hoennFlags`의 구역 플래그로 숨김).
- **막다른 길 금지**:
  - 차단은 "들어가는 쪽"에만 둔다. 길을 막는 오브젝트 대신 경계 한 칸 안쪽(열린 구역 쪽)에 좌표 이벤트를 두어 열린 구역에서 걸어 들어올 때만 대사 후 한 칸 되돌리고, 안내 NPC는 길 옆에 세운다. 닫힌 구역 쪽에서 걸어 나오는 플레이어는 막지 않는다.
  - 이미 닫힌 구역 안에서 저장한 세이브(v0.2.0~v0.5.0에서는 호연 282개 맵이 열려 있었다)는 이어하기 때 그 맵의 `ON_TRANSITION`에서 "아직 조사 중인 지역" 대사 뒤 카이나 항구로 보낸다. 대상 맵은 닫힌 구역 전체(`hoenn_reachability.py --zones`의 맵 목록).
  - 닫힌 구역의 FLY 목적지: 지금은 방문 플래그만 보고 날 수 있다(`src/region_map.c:3021-3023`). 구역 개방 플래그를 함께 보게 고친다(2.2절). 이 수정 전에는 v0.5.0 세이브가 이미 방문한 먼 도시로 날아가 차단을 건너뛸 수 있다.
  - 비행기 도착지(카이나 항구)는 항상 1단계 구역 안에 둔다. 회복 지점·리스폰도 열린 구역 안에만 있다.
- **구역을 열 때마다**: `hoenn_reachability.py --zones`로 새 경계를 확인하고, 열린 구역의 경계 목록과 차단 NPC 목록이 일치하는지 본다. 막다른 길 검사는 "열린 구역 → 닫힌 구역" 간선이 모두 차단되어 있는지, "닫힌 구역 → 열린 구역" 간선이 막히지 않았는지 두 방향 모두 본다.

### 4.1 선행 작업(0단계, 1단계 릴리스에 함께 또는 그 전에)

| # | 작업 | 종류 | 비고 |
|---|---|---|---|
| P1 | 나무열매 나무 자리 87개 리셋 수정 | 데이터(이식 스크립트) | 1.5절 (1). 핫픽스 권장 |
| P2 | 호연 숨은 아이템 플래그를 `hoennFlags`로 이전 + 1회 이전 | C 소량 + 이식 스크립트 | 1.5절 (2). Z1에 영향받는 13개 중 9개(106·108·109번 도로)가 있다 |
| P3 | 호연 스토리용 저장 공간 규칙 | 설계 + C 소량 | 플래그는 `hoennFlags` 0x200~0x3FF(512비트)를 스토리용으로 예약. 변수는 (a) 플래그 2~3비트 묶음을 읽는 스페셜, 또는 (b) `SaveBlock2.filler_CA0[0x280]`에 `VAR_HOENN_*`(u16 최대 320개)을 두고 `GetVarPointer`가 처리(`GetFlagAddr`의 `hoennFlags`와 같은 방식). 결정 필요(6절 Q10) |
| P4 | 구역 개방 플래그 8개와 차단 NPC 공용 스크립트, 닫힌 구역 추방 스크립트, FLY 막기 | 스크립트 + C 소량 | 4.0절 |
| P5 | 호연 소문 수집가(카이나시티 포켓몬센터) | 스크립트 | 모든 단계의 힌트를 여기에 누적 |
| P6 | 호연 배지 8개 플래그와 표시 방식 | 플래그 + (선택) UI | 2.2절 |
| P7 | 레벨 정책 적용 방식 | 데이터 | 6절 Q9 결정에 따라 `trainer_parties_hoenn.h`·야생표 조정 스크립트 |
| P8 | 트레이너 번호 배분 | 설계 | 호연 트레이너 뒤 504칸을 v0.6.0 토너먼트·호연 스토리·재대결로 나누어 예약(6절 Q10) |

### 4.2 구역 정의

`tools/hoenn_reachability.py`의 `ZONE_BY_SECTION`·`ZONE_BY_NAME`과 같다. 맵 목록은 부록 B.

| 구역 | 포함 MAPSEC | 경계(차단 지점) |
|---|---|---|
| Z1 카이나 항구권 | 카이나시티, 109·106·107·108번 도로, Dewford, Granite Cave, 버려진 배 | 카이나→110번 도로(북), 카이나→134번 도로(동), 106→105번 도로(북), 카이나 배틀텐트 |
| Z2 Mauville 전기권 | 110번 도로(Trick House 포함), Mauville, New Mauville, 117번 도로, Verdanturf, 118번 도로 | Mauville→111번 도로, 110→103번 도로, 118→119·123번 도로, Verdanturf→116번 도로·Rusturf Tunnel, Verdanturf 배틀텐트 |
| Z3 남서부 시작의 땅 | Littleroot, Oldale, Petalburg, Rustboro, 101~105·115·116번 도로, Petalburg Woods, Rusturf Tunnel, 알터링 동굴 | 115→114번 도로·Meteor Falls, 105→Island Cave(레지아이스) |
| Z4 화산·사막권 | 111~114번 도로, Fiery Path, Mt. Chimney, Jagged Pass, Lavaridge, Fallarbor, Meteor Falls, Desert Ruins, Mirage Tower, 마그마단 아지트 | 111→Mauville(열린 쪽), Terra Cave 워프(닫힌 칸) |
| Z5 날개·항구권 | 119~123번 도로, Fortree, 사파리존, Lilycove(컨테스트 로비·홀은 들어가되 접수 중지), Mt. Pyre, 아쿠아단 아지트, Scorched Slab, Ancient Tomb | Lilycove→124번 도로, Lilycove 항구(S.S. TIDAL), 컨테스트 홀 |
| Z6 바다권 | 124~134번 도로, Mossdeep, Shoal Cave, Pacifidlog, Sootopolis, Seafloor Cavern, Cave of Origin, Sky Pillar, Sealed Chamber, 해저 도로, Island Cave | 128→Ever Grande, 해저 Marine Cave 워프 |
| Z7 Ever Grande 리그 | Ever Grande, 호연 Victory Road | — |
| Z8 포스트게임 시설 | 배틀프런티어, Southern Island, Faraway Island, Terra·Marine Cave, Artisan Cave, S.S. TIDAL, 컨테스트 홀, 배틀텐트, 트럭 안 | — |

(호연 지명·인물은 `docs/dex-habitat.md`처럼 원작 영어 이름으로 적었다. 카이나시티·성호·털보박사·휘웅/봄이처럼 기존 문서에 한국어 이름이 있는 것만 한국어로 썼다. 맵 이름은 부록 B.)

### 4.3 단계표

번호는 사용자 결정(5.9절 2번)에 따라 1단계가 **v0.7.0**이다. v0.6.0은 "최강을 향한 길"로 나갔다.

**1단계는 2026-09-23에 구현을 마쳤다.** 실제로 들어간 내용과 원안에서 달라진 점은 `docs/v0.7.0-plan.md` 10절에 있다. 요약하면: 선행 작업 P3·P5~P8 완료(P4 차단 스크립트는 사용자 결정으로 하지 않음), 이벤트 7개 전부 구현, Z1 트레이너 48명을 Lv45~55로, 카이나 쪽 대사 88개와 도로·Dewford·Granite Cave·버려진 배 대사를 새로 씀, 안내판 2개와 항구 선원 대사로 미개방 방향 안내. Dewford 체육관의 어둠 연출은 이식하지 않았다.

#### 1단계 (v0.7.0, 구현 완료) — Z1 카이나 항구권

| 항목 | 내용 |
|---|---|
| 여는 맵 | 41개(지금 Y 37개, 카이나 → 109 → 108 → 107번 도로 → Dewford → 106번 도로가 파도타기로 이어짐). 카이나시티와 실내 11(항구, 해양박물관 1·2층, STERN 조선소 1·2층, 팬클럽, 이름짓기 집, 민가, 마트, 포켓몬센터 1·2층), 109번 도로와 바닷가 집, Dewford와 체육관·회관·민가, Granite Cave 4층(성호의 방 포함), 106·107·108번 도로, 버려진 배 9개(수중 2·숨은 층 2는 다이빙 뒤) |
| 진입 조건 | 전당등록(지금 비행기 조건) + P1~P6 |
| 핵심 이벤트 | ① 항구 도착 환영(STERN 선장 소개, 호연 소문 수집가 안내) ② 해양박물관(Oceanic Museum) 아쿠아단 소동(원작 RSE 박물관, 데이터 있는 `TRAINER_HOENN_GRUNT_MUSEUM_1·2`, ARCHIE 첫 등장) ③ Dewford 체육관 BRAWLY(원작 2번째 체육관, 배지 1개, 기술머신08 벌크업) ④ Granite Cave 성호 만남(원작 편지 전달을 "STERN 선장의 해저 조사 의뢰서"로 각색, 기술머신47 강철날개) ⑤ 버려진 배 스캐너 → STERN 선장에게 전달(원작 보상: 심해의이빨/심해의비늘 중 하나) ⑥ 109번 도로 바닷가 집 3연전(원작 사이코소다 보상) ⑦ 피카츄 연출: 박물관의 "전기 조류" 전시 등 대사 분기 |
| 새 트레이너 | 0~2명(박물관 단원·ARCHIE는 데이터 있음. ARCHIE 전투를 넣을지 결정). 기존 49명 레벨 조정 |
| 아이템 | 기존 아이템볼 18·숨은 16(P2 뒤 9개가 다시 주울 수 있게 됨). 새 보상: 기술머신08·47, 심해 도구 1 |
| 전설·희귀 | 없음 |
| 차단 | 4곳: 카이나 북쪽(110번 도로 입구, "사이클링로드 점검 중"), 카이나 동쪽 바다(134번 도로, "해류 경보" 선원), 106번 도로 북쪽 바다(105번 도로, BRINEY 씨 배 대신 "소용돌이" 선원), 카이나 배틀텐트("준비 중") |
| 새 그림 | 0(호연 인물 그림 이식됨). 배지 표시를 UI로 하면 배지 아이콘 |
| 새 C 코드 | P2·P3·P4의 소량만 |
| 점검 | 플래그: 스토리 플래그 약 15~20개 `hoennFlags` 0x200~, 변수 0~2개 / 중복: 마스터볼(아쿠아 아지트)은 Z5라 이 단계에서 닫힘 확인 / 서사: 칸토 1의섬 셀리오의 "털보박사가 보낸 스타터" 대사와 모순 없음 / 도감: Z1 야생표 12맵은 그대로 |

#### 2단계 (v0.7.0) — Z2 Mauville 전기권

| 항목 | 내용 |
|---|---|
| 여는 맵 | 35개(지금 Y 25). 110번 도로·사이클링로드 게이트, Mauville와 실내, New Mauville 2, 117번 도로·키우미집, Verdanturf와 실내, 118번 도로. Trick House는 입구만(퍼즐은 Z8) |
| 진입 조건 | 1단계 배지(BRAWLY) |
| 핵심 이벤트 | ① WATTSON 체육관 재배치(오브젝트가 빠져 있음, `TRAINER_HOENN_WATTSON_1` 데이터 있음). 전기 체육관이라 피카츄 대사 분기 ② New Mauville 발전기 폭주(원작 에메랄드: WATTSON 의뢰, 지하열쇠). 찌리리공·레어코일 고정 전투 ③ 110번 도로 라이벌전(원작 휘웅/봄이(BRENDAN/MAY), 스타터 파티 데이터 있음 → 6절 Q5) ④ Mauville WALLY 전투(`TRAINER_HOENN_WALLY_MAUVILLE`) ⑤ Verdanturf Rusturf Tunnel 이야기(개통은 3단계) |
| 새 트레이너 | 0~2. 기존 60명 레벨 조정 |
| 아이템·희귀 | 기술머신34 전격파, 지하열쇠(키 아이템, 이미 번호 있음) / 전설 없음 |
| 차단 | Mauville→111번 도로("모래바람" 안내), 110→103번 도로(바다 쪽 선원), 118→119·123번 도로, Verdanturf→116번 도로·Rusturf Tunnel("낙석"), Verdanturf 배틀텐트 |
| 선행 | P1 필수(110·117·118번 도로에 나무 9그루) |
| 점검 | 117번 도로 키우미집이 4의섬 키우미집과 같은 저장 공간을 쓰는 문제(설정으로 "연결된 키우미집" 처리 또는 닫아 둠) / 전기 체육관 보상과 v0.4.0 피카츄 전용 기술 가르침(볼트태클 등)과의 중복 확인 |

#### 3단계 (v0.8.0) — Z3 남서부 시작의 땅

| 항목 | 내용 |
|---|---|
| 여는 맵 | 52개(지금 Y 50). Littleroot·털보박사 연구소, 101~105·115·116번 도로, Petalburg Woods, Petalburg·체육관, Rustboro(데봉), Rusturf Tunnel, BRINEY 씨 집 |
| 진입 조건 | 2단계 완료(Rusturf Tunnel 개통) 또는 BRINEY 씨 배(카이나↔Dewford↔104번 도로) |
| 핵심 이벤트 | ① 털보박사와 스타터(칸토 셀리오 지급과 충돌 → 6절 Q5) ② ROXANNE 체육관(배치돼 있음, 배지 처리 추가) ③ 데봉 사장·데봉 소포(원작 Petalburg Woods 아쿠아단) ④ Petalburg 체육관 NORMAN(오브젝트 빠짐, `TRAINER_HOENN_NORMAN_1` 있음)과 WALLY 포획 시범(시범 전투 비트 공유) ⑤ BRINEY 씨 배 이동(`OBJ_EVENT_GFX_MR_BRINEYS_BOAT` 있음, 스크립트 이동+워프) |
| 새 트레이너 | 0~3. 기존 62명 |
| 전설·희귀 | 없음(Island Cave 레지아이스는 Z6). 알터링 동굴은 6의섬 알터링 동굴과 같은 `MAPSEC_ALTERING_CAVE` |
| 차단 | 115→114번 도로·Meteor Falls, 105번 도로 Island Cave |
| 선행 | P1(나무 24그루) |
| 점검 | 스타터·라이벌 파티(스타터 종에 따라 나뉜 데이터)와 셀리오 지급 플래그 `FLAG_GOT_*_FROM_CELIO` 연동 / 도감 서식지 문서의 "Petalburg Woods 닮은 지형" 근거와 충돌 없음 |

#### 4단계 (v0.9.0) — Z4 화산·사막권

| 항목 | 내용 |
|---|---|
| 여는 맵 | 55개. 111~114번 도로, Fiery Path, Mt. Chimney, Jagged Pass, Lavaridge·체육관, Fallarbor, Meteor Falls, Desert Ruins, Mirage Tower, 마그마단 아지트 |
| 핵심 이벤트 | Mt. Chimney 마그마단(원작 운석), FLANNERY 체육관, 사막 모래바람(좌표 날씨 이벤트 재작성 + 고글), 113번 도로 화산재(재 주머니·유리공방: 행동값 확인 필요), Meteor Falls 아쿠아·마그마 대치, Mirage Tower 화석 |
| 전설·희귀 | 레지락(Desert Ruins) → 칸토 유적의 골짜기와 중복(Q4). 뿌리·발톱 화석 → 칸토 홍련섬 복원과 중복. 그란돈(마그마 아지트, 에메랄드 흐름) → 중복 |
| 엔진 | 케이블카(2.2), 2대1 배틀 각색, 좌표 날씨 |
| 선행 | P1(나무 11그루) |

#### 5단계 (v0.10.0) — Z5 날개·항구권

| 항목 | 내용 |
|---|---|
| 여는 맵 | 68개. 119~123번 도로(Weather Institute), Fortree·체육관, 사파리존, Lilycove(백화점·모텔·미술관, 컨테스트는 접수 중지), Mt. Pyre, 아쿠아단 아지트, Scorched Slab, Ancient Tomb |
| 핵심 이벤트 | Weather Institute 아쿠아단, 켈리몬과 데봉스코프, WINONA 체육관(회전문 → 재설계), Mt. Pyre 구슬 도난, 아쿠아 아지트, Lilycove 라이벌 |
| 전설·희귀 | 캐스퐁(Weather Institute) → 4의섬 선물과 중복. 남색·주홍 구슬 → 칸토 유적의 골짜기 벽화와 같은 아이템. 레지스틸(Ancient Tomb) 중복. **마스터볼**(아쿠아 아지트 B1F) → 실프 마스터볼과 중복 |
| 선행 | P1(나무 43그루), 사파리존 코드가 호연 사파리 맵을 다루는지 확인 |

#### 6단계 (v0.11.0) — Z6 바다권 + 다이빙

| 항목 | 내용 |
|---|---|
| 여는 맵 | 94개(지금 Y 39). 124~134번 도로, Mossdeep(우주센터·성호의 집), Shoal Cave(물때: 시계 사용), Pacifidlog, Sootopolis, Seafloor Cavern, Cave of Origin, Sky Pillar, Sealed Chamber, 해저 도로, Island Cave |
| 핵심 이벤트 | TATE&LIZA 체육관, 우주센터 마그마단(원작 성호와 태그배틀 → 각색), Seafloor Cavern·Sootopolis 기상 이변·Sky Pillar(원작 클라이맥스), JUAN/WALLACE 체육관, Sealed Chamber 점자 |
| 엔진 | **다이빙 이식**(2.2), `ON_DIVE_WARP` 스크립트 15맵, Sootopolis 체육관 얼음 행동값, 가뭄·폭우 날씨 |
| 전설·희귀 | 가이오가·그란돈·레쿠쟈·레지 3마리 → 칸토와 중복(Q4). 메탕(성호의 집) → 칸토 야생 1%와 중복 |

#### 7단계 (v0.12.0) — Z7 Ever Grande 리그

| 항목 | 내용 |
|---|---|
| 여는 맵 | 19개(사천왕 방은 문 메타타일을 스크립트로 열기) |
| 핵심 이벤트 | 호연 배지 8개 → Victory Road → 사천왕(`TRAINER_HOENN_SIDNEY` 등 데이터 있음)·챔피언(성호 또는 WALLACE, 원작 선택) → 호연 전당 |
| 점검 | FR/LG 전당 기록(`src/hall_of_fame.c`)을 호연 전당도 같이 쓸지, v0.6.0 토너먼트 참가자에 호연 관장을 넣을지 |

#### 8단계 (v0.13.0~) — Z8 포스트게임 시설

- Southern Island(라티아스·라티오스, 칸토 배회와 중복), Faraway Island(뮤, 칸토 트럭 뮤와 중복), Terra·Marine Cave(그란돈·가이오가 재도전), Artisan Cave, S.S. TIDAL, Trick House 퍼즐, 배틀텐트, 컨테스트, 비밀기지, 배틀프런티어.
- 엔진 이식 규모가 커서(2.2) 8a(섬·동굴·배), 8b(배틀텐트·축소 배틀타워), 8c(컨테스트), 8d(비밀기지)처럼 다시 나눌 것을 제안한다.

---

## 5. 충돌·중복 점검

### 5.1 자동 검사기 `tools/check_map_integrity.py`

| 검사 | 기준 | 결과(부록 C) |
|---|---|---|
| 워프 목적지 | 없는 맵, 목적지 워프 번호 초과(`WARP_ID_DYNAMIC` 제외), 스크립트 워프의 없는 맵 | **오류 0**. 되돌아오지 않는 워프 85개는 INFO(구멍·한 방향 문·여러 문이 한 방으로, 로스트케이브 등 원래 구조) |
| 닫힌 워프 칸 | 워프 칸의 행동값이 워프 행동값이 아님 | INFO: 190맵 389개(호연 121개). 대부분 도착 전용 자리나 스크립트가 여는 입구. 호연에서 에메랄드 전용 행동값이 평지로 바뀐 곳은 Trick House 문 8·Sky Pillar 문 1·Shoal Cave 입구 1 |
| 맵 연결 | 없는 맵, 반대편 연결 없음·오프셋 불일치 | 오류 0. 불일치 8개는 모두 업스트림 FR/LG에 원래 있는 것(노랑시티 연결 맵, 프로토타입 섬) |
| 플래그·변수 번호 중복 | 같은 값의 이름 2개 이상. `#define A B` 별칭과 업스트림에 원래 있는 쌍은 INFO로 구분, "빈" 이름과 사용 중인 이름이 겹치면 ERROR. 트레이너 격파 플래그(`TRAINER_FLAGS_START + id`)와 주석의 변수 범위("0x4094-0x40A7", "array of 4")도 포함 | **ERROR 110**: 모두 호연 숨은 아이템 플래그(1.5절 (2)). 변수는 중복 0, 명시 별칭·업스트림 별칭 0 |
| 오브젝트·숨은 아이템 플래그 재사용 | 여러 맵에서 같은 플래그. 아이템볼·숨은 아이템이 공유하면 ERROR, 나머지 숨김 플래그는 업스트림과 같으면 INFO | 오류 0. 공유 7개는 모두 업스트림 그대로(`FLAG_HIDE_SILPH_ROCKETS` 등) |
| 이동 타입 | 콜백이 NULL인 이동 타입을 쓰는 오브젝트 | **ERROR 15맵(87개)**: 1.5절 (1) |
| 트레이너 | 여러 맵에서 같은 트레이너(격파 플래그 공유), 호연 트레이너 수 대 `hoennTrainerFlags` 용량 | 공유 0. 호연 520/1024, FR/LG 753/768 |
| 레이아웃·그룹 | 없는 레이아웃, 그룹당 255 초과 | 오류 0(맵 890, 그룹 76, 레이아웃 731) |

단계마다 구현 전·후에 돌려 ERROR 수가 늘지 않는지 본다(P1·P2가 끝나면 0이 되어야 한다).

### 5.2 단계 공통 체크리스트

각 단계 기록에 아래를 표로 남긴다.

- [ ] **플래그**: 새 플래그는 `hoennFlags`의 스토리 예약 구간(P3)에서만. `FLAG_0x4BD~0x4FF`·`FLAG_UNUSED_0x4A7~4AF`는 P2 전까지 쓰지 않는다. 검사기 "flag numbers" ERROR 증가 0.
- [ ] **변수**: 새 변수 수와 위치(P3 방식). `VAR_0x40xx`를 쓰면 남은 수(현재 56)를 기록.
- [ ] **트레이너 번호**: P8 배분표 안에서. 새 트레이너 파티는 이식 스크립트가 덮어쓰지 않는 별도 파일.
- [ ] **오브젝트 그림 번호**: 새 번호를 쓰면 남은 수(현재 8) 기록. 가능하면 VAR 그림.
- [ ] **전설·희귀 도구**: 5.3 표에서 해당 줄의 처리 방침(Q4)을 따랐는가. 같은 포켓몬을 두 번 받을 수 있게 되면 그 사실을 기록.
- [ ] **서사**: 칸토에서 이미 일어난 일(아래 표)과 대사가 모순되지 않는가.
- [ ] **도감 완성 계획**(`docs/dex-completion.md`): 386종 입수 경로를 줄이지 않았는가. 호연 개방으로 새 입수처가 생긴 종을 기록. 전설·환상은 야생표에 넣지 않는다는 방침 유지.
- [ ] **도감 서식지**(`docs/dex-habitat.md`): 호연 분포 페이지가 닫힌 구역을 보여 주는지(6절 Q8), 야생표를 바꿨다면 도구를 다시 돌렸는가.
- [ ] **막다른 길**: `hoenn_reachability.py --zones`의 경계 간선이 모두 차단 목록에 있는가, 닫힌 구역 세이브 추방·FLY 막기 확인.
- [ ] **힌트 NPC**: 이벤트마다 1곳 이상, 호연 소문 수집가에 추가.
- [ ] **세이브**: `savetest_all.sh` 4종 IDENTICAL, 호연 안에서 저장한 세이브 1개 추가 권장.

### 5.3 칸토에 이미 있는 호연 전설·선물·희귀 도구

| 대상 | 호연 원작 장소 | 이 해킹의 칸토 입수처 | 근거 | 겹치는 단계 |
|---|---|---|---|---|
| 가이오가·그란돈 | Seafloor Cavern·Cave of Origin(RS), 마그마·아쿠아 흐름(E), Terra·Marine Cave(E 전당 뒤) | 7의섬 매몰된 석실, 구슬 조건, Lv50 | `docs/events-roadmap.md` 구현 기록 16, `data/maps/SevenIsland_TanobyRuins_EmbeddedChamber/scripts.inc` | 4·6·8 |
| 레쿠쟈 | Sky Pillar | 같은 석실, 두 마리 뒤 Lv50 | 같음 | 6 |
| 레지락·레지아이스·레지스틸 | Desert Ruins·Island Cave·Ancient Tomb(Sealed Chamber 점자) | 유적의 골짜기 석실 3곳, 고래왕·시라칸 조건, Lv40 | `docs/dex-completion.md` 1절 | 4·5·6 |
| 라티아스·라티오스 | Southern Island(무한티켓)·배회 | 칸토 배회(에니그마 스톤) Lv35 | `docs/events-roadmap.md` 구현 기록 7, `src/roamer.c` | 8 |
| 지라치 | (배포) | 달맞이산 B2F 별똥별 | `data/maps/MtMoon_B2F/scripts.inc` | — |
| 데오키시스 | 탄생의 섬(배포) | 빌의 오로라티켓 → 탄생의 섬(이식 제외 맵) | `docs/dex-completion.md` 1절 | — |
| 뮤 | Faraway Island(배포) | 갈색시티 트럭 밑 | `data/maps/VermilionCity/scripts.inc` | 8 |
| 나무지기·아차모·물짱이 | 털보박사 | 1의섬 셀리오 | `data/maps/OneIsland_PokemonCenter_1F/scripts.inc`, `docs/dex-completion.md` 2절 | 3 |
| 캐스퐁 | Weather Institute | 4의섬 날씨 연구원 | `data/maps/FourIsland_House2/scripts.inc` | 5 |
| 메탕 | 성호의 집 | 블루시티 동굴 B1F 야생 1% | `docs/dex-completion.md` 5절 | 6 |
| 릴링·아노딥 | Mirage Tower 화석 | 홍련섬 연구소 복원(뿌리·발톱 화석) | `data/maps/CinnabarIsland_PokemonLab_ExperimentRoom/scripts.inc` | 4 |
| 켈리몬 | 119·120번 도로 고정 | 3의섬 열매숲 야생 | `docs/dex-completion.md` 6절 | 5 |
| 남색구슬·주홍구슬 | Mt. Pyre | 유적의 골짜기 벽화 | `docs/events-roadmap.md` 구현 기록 16 | 5 |
| 마스터볼 | 악의 조직 아지트(RS 아쿠아·마그마, E 마그마) | 실프주식회사 사장 | 1.5절 (3) | 5(지금 열려 있음) |

### 5.4 칸토 이벤트와의 서사 충돌 후보

- 1의섬 셀리오: "털보박사가 보낸 스타터"(`docs/dex-completion.md` 2절). 3단계에서 털보박사가 직접 등장하면 연결 대사 필요.
- 유적의 골짜기 매몰된 석실: "구슬이 전설을 부른다"는 설정. 5단계의 구슬 도난 사건과 같은 아이템을 쓴다.
- 2·3세대 연계 챕터 기획(`docs/postgame-gen23-chapter.md`): 털보박사·휘웅/봄이·마그마·아쿠아 조사원을 세비 제도 새 섬에 등장시키는 안. 호연 본토 개방과 인물이 겹친다(6절 Q5).
- v0.6.0 계획: N 최종전 전설 후보가 레지 계열·라티(`docs/v0.6.0-plan.md` 결정 3), 토너먼트 참가자에 호연 인물 없음. 7단계 호연 리그와 겹칠 수 있다.
- 로켓단 3인조: v0.5.0에서 뉴아일랜드 후일담으로 칸토 이야기를 마쳤다. 호연 등장은 새 이야기로 이어야 한다(Q11).

---

## 5.9 확정된 결정 (사용자, 2026-09-22)

| # | 질문 | 결정 |
|---|---|---|
| Q1 | 비행기 도착지 | **카이나(잔모래시티) 유지**. 호연 관문으로 확정하고, 리듬시티(Lilycove)는 나중 단계에서 배편으로 잇는다. |
| Q2 | v0.6.0 자리 | **(a)** v0.6.0은 "최강을 향한 길" 그대로(항목 4·5까지 마무리). 호연 1단계는 **v0.7.0**. |
| Q3 | 지금 열려 있는 호연 | **(b) 차단하지 않는다.** 세이브 호환이 우선이므로 지형은 지금처럼 열어 두고 이벤트만 단계별로 채운다. 미개방 구역에는 **최소 안전 점검만** 한다: 워프가 유효한 목적지로 가는지, 스크립트 없는 문·계단에 갇히거나 크래시가 나는 곳이 없는지(`tools/check_map_integrity.py`). 필요하면 길을 막지 않는 "정비 중" 안내판 정도만 둔다. |
| Q4 | 칸토에 이미 있는 호연 전설 | **한 플레이에 한 번만.** 칸토(셀리오 포함)의 기존 획득 경로는 세이브 호환 때문에 그대로 둔다. 호연 원래 장소(하늘기둥·각성의 사당·레지 유적·남쪽 섬 등)는 플래그를 보고 갈린다: 이미 칸토에서 얻었으면 **그 포켓몬과 이어지는 서사 이벤트**(특별 장면·보상), 아직이면 **그곳이 조우 장소**가 되고 칸토 쪽에는 서사만 남는다. |
| Q5 | 스타터 | 호연 스타터를 **두 번 주지 않는다**. 셀리오 지급 유지, **오달박사 연구소는 다른 역할**(호연 도감 평가·별도 보상)로 기획한다. |
| Q6 | 대사 | **(a)** 구역을 열 때 그 구역 NPC·표지판 대사를 **전부 새로 쓴다**(에메랄드 원문 이식 금지, 공항으로 건너온 칸토 챔피언이라는 옐로 맥락). 미개방 구역은 차례가 올 때까지 그대로 둔다. |

나머지 질문은 아래 기본안으로 진행한다(Q5의 연계 챕터·Q10·Q11·Q12는 따로 승인을 받는다).

| # | 기본안 |
|---|---|
| Q7 | (a) 이미 이식된 에메랄드 그림·타일셋은 그대로 쓰고, **새로 그리는 것만** FR/LG 화풍으로 한다. |
| Q8 | (a) 도감 분포는 지금처럼 전부 표시한다(지형을 열어 두므로 가릴 이유가 없다). |
| Q9 | (b) 구역을 열 때 그 구역 트레이너 레벨을 일괄 상향한다(1단계 Lv45~55). 칸토 챔피언이 건너오는 전제에 맞춘다. |

---

## 6. 기존 문서와의 모순과 질문

각 항목은 근거와 선택지만 적었다. 어느 쪽을 따를지 정해 주면 계획에 반영한다.

**Q1. 비행기 도착지: 카이나(슬레이트포트)인가, Lilycove인가**
- 의뢰문: "Lilycove 항구 도착". 실제: `src/airplane_flight.c:60` `MAP_SLATEPORT_CITY_HARBOR`, `docs/postgame-gen23-chapter.md` 8절, 공항 대사(`data/maps/KantoAirport/text.inc` "lands at SLATEPORT"), 귀국 창구는 `tools/hoenn_import/patches/SlateportCity_Harbor.*`.
- 선택지: (a) 카이나 유지(이 문서의 1단계 추천은 이 전제) / (b) Lilycove로 옮김(1단계 후보가 Z5 쪽으로 바뀜, 창구 패치·공항 대사 수정) / (c) 단계에 따라 도착지를 바꿈(처음 카이나, 5단계 뒤 Lilycove 노선 추가).

**Q2. v0.6.0 자리**
- `docs/v0.6.0-plan.md`(승인됨): v0.6.0 = 옛 트레이너·N·은빛산·토너먼트·유지보수, "호연 스토리 이식"은 다음 버전 이후로 미룸(64행). 새 방향: 호연 1단계를 v0.6.0부터.
- 선택지: (a) v0.6.0은 기존 계획 그대로, 호연 1단계는 v0.7.0 / (b) v0.6.0 = 기존 계획 + 호연 1단계(규모 약 2배) / (c) v0.6.0 = 호연 1단계, 기존 계획은 v0.7.0 / (d) v0.6.0 = 기존 계획의 작은 항목(1 옛 트레이너, 5 유지보수) + 호연 1단계, N·은빛산·토너먼트는 v0.7.0. 어느 경우든 P1(리셋)은 v0.5.1 핫픽스로 따로 낼 수 있다.

**Q3. 지금 열려 있는 호연을 닫을 것인가**
- `docs/hoenn-import.md`: 호연 전체를 원작 맵 그대로 연 상태(챔피언이면 282개 맵 이동 가능, v0.2.0부터 릴리스). 새 방향: 단계별로 연다.
- 선택지: (a) 1단계 때 Z2~Z8을 차단(4.0절 추방·FLY 막기 포함) / (b) 지형은 계속 열어 두고 이벤트만 단계별로 추가(차단 없음, 막다른 길 문제 없음, 대신 순서가 흐트러짐) / (c) 절충: 트레이너·아이템이 많은 구역만 닫고 도시·도로는 열어 둠.

**Q4. 칸토에 이미 있는 호연 전설(5.3절)**
- `docs/events-roadmap.md` 1부-6·7, `docs/dex-completion.md` 1절: 가이오가·그란돈·레쿠쟈·레지·라티를 칸토에서 이미 준다. `docs/dex-completion.md` 방침 1: 전설은 "전용 장소의 1회성 이벤트".
- 선택지: (a) 호연에서는 다시 주지 않고 이야기에서 칸토의 개체를 활용(예: 이미 잡은 가이오가가 반응) / (b) 칸토에서 아직 싸우지 않은 세이브만 호연에서 만날 수 있게(칸토 플래그·`VAR_EMBEDDED_CHAMBER_LEGEND` 확인) / (c) 호연에서도 따로 줌(한 세이브에 두 마리 가능) / (d) 호연 원작 장소에서는 전투 없이 연출만.

**Q5. 스타터와 라이벌, 2·3세대 연계 챕터**
- `docs/dex-completion.md` 2절: 호연 스타터는 셀리오. `docs/postgame-gen23-chapter.md`: 털보박사·휘웅/봄이를 세비 제도 "9섬"에 두는 안(추천 A+C), 성도·호연 본토는 등장하지 않는다는 전제, "본토 전체로 넓히면 플래그 약 1,000개 → 세이브 구조 확장 필요"(6절). 실제로는 `hoennFlags` 2048비트가 이미 있어 이 전제는 바뀌었다.
- 선택지: (a) 연계 챕터 기획을 폐기하고 호연 인물은 호연 본토에서만 / (b) 연계 챕터는 성도 전용으로 줄이고 호연 부분만 본토로 옮김 / (c) 둘 다 유지(인물 중복 허용). 스타터: (가) 셀리오 지급 유지, 털보박사는 "이미 보냈다" 대사 / (나) 셀리오 지급을 없애고 Littleroot로 옮김(기존 플래그 재사용) / (다) 둘 다.

**Q6. 대사 새로 쓰기의 범위**
- 새 규칙: 모든 대사 새로 작성. `docs/events-roadmap.md` 구현 기록: 원작 대사를 그대로 옮긴 사례가 있다(1 장로 퀴즈 "크리스탈 그대로", 6 편지 배달 거절 대사 그대로). 호연 NPC 692명·표지판 318개는 지금 에메랄드 원문 첫 대사.
- 선택지: (a) 구역을 열 때 그 구역의 NPC·표지판 대사 전부 새로 씀 / (b) 이벤트 대사만 새로 쓰고 일반 주민은 원작 유지 / (c) 일반 주민은 원작 유지하되 표지판·지명만 한국어판 기준 정리.

**Q7. 이식된 에메랄드 그림과 "FR/LG 화풍" 규칙**
- 새 규칙: 새 그림은 FR/LG 화풍. `docs/events-roadmap.md` 1·2: 재색칠 원칙. 실제: 호연 인물 59종·타일셋 63개는 에메랄드 그림 그대로 이식(`docs/hoenn-import.md` 2-1).
- 선택지: (a) 이식된 에메랄드 그림은 예외로 그대로 씀 / (b) 구역을 열 때 인물 그림을 FR/LG 명암으로 손봄 / (c) 새로 그리는 것만 FR/LG 화풍.

**Q8. 도감 호연 분포 페이지와 닫힌 구역**
- `docs/dex-habitat.md`: 호연 야생표 전부를 분포에 표시, "호연 맵의 에메랄드 야생표는 바꾸지 않는다". 단계 개방이면 닫힌 구역(예: Sootopolis·Seafloor Cavern)이 분포에 나온다.
- 선택지: (a) 그대로 표시 / (b) 구역 개방 플래그로 가림 / (c) 방문한 MAPSEC만 표시.

**Q9. 호연 레벨**
- 원작 호연 트레이너 평균 Lv26(최고 78), 진입은 칸토 챔피언. 문서 규정 없음.
- 선택지: (a) 원작 레벨 유지 / (b) 구역별 일괄 상향(예: 1단계 Lv45~55) / (c) 플레이어 배지·전당 횟수에 맞춘 단계별 파티(데이터 여러 벌).

**Q10. 트레이너 번호와 세이브 공간 배분**
- `docs/v0.6.0-plan.md` 공통 규칙: 칸토 번호 15칸 뒤에는 호연 트레이너 뒤에 붙인다. 호연 스토리·재대결도 같은 뒤쪽 504칸을 쓴다. 변수 56개도 공유.
- 선택지: (a) 번호 구간 예약(예: +520~+559 v0.6.0 토너먼트, +560~ 호연 스토리) / (b) 먼저 쓰는 쪽이 이어 붙임. 변수: (a) P3 (a) 플래그 묶음 / (b) P3 (b) `filler_CA0` 호연 변수.

**Q11. 로켓단 3인조와 옐로식 이야기**
- `docs/events-roadmap.md` v0.5.0 기록: 3인조 이야기는 뉴아일랜드에서 마무리. `docs/postgame-gen23-chapter.md` 4절: 로켓단 잔당을 연계 챕터 악역으로.
- 선택지: (a) 호연에도 3인조가 따라와 개그 담당 / (b) 호연은 아쿠아·마그마단만 / (c) 특정 단계에만 카메오.

**Q12. 문서 정정과 핫픽스**
- `docs/hoenn-import.md` "숨은 아이템: FRLG가 쓰는 191개 뒤의 빈 플래그"와 "나무열매 재배는 이식하지 않았다"(실제로는 리셋 원인이 되는 자리 오브젝트가 남음), `docs/v0.6.0-plan.md`·`docs/postgame-gen23-chapter.md`의 빈 플래그 수(531, 559: 실제 464), `docs/events-roadmap.md` 공통 전제 "시계 없음"(로드맵 2 · 9번으로 이미 시계가 있음).
- 선택지: (a) P1·P2를 v0.5.1 핫픽스로 내고 문서도 그때 정정 / (b) 다음 릴리스에 함께 / (c) 문서만 먼저 정정.

---

## 7. 1단계 구역 후보와 추천

규모 단위: v0.5.0 로켓단 확장(이벤트 11개, 새 트레이너 9명, 새 맵 1개)을 1.0으로 본 상대값.

| 항목 | A. Z1 카이나 항구권 | B. 카이나 + Z2 Mauville 전기권 | C. 카이나 + Z3 남서부 시작의 땅 |
|---|---|---|---|
| 여는 맵 | 41 | 12(카이나) + 35 = 47 | 12 + 52 + 이동 수단 = 64 이상 |
| 비행기 도착지와의 관계 | 도착지 그대로 | 도착지에서 북쪽으로 바로 이어짐 | 카이나와 바로 붙어 있지 않음(110번 도로나 106번 도로를 함께 열거나 BRINEY 씨 배 필요) |
| 핵심 이벤트 수 | 6~8 | 7~9 | 10~14 |
| 기존 트레이너(레벨 조정) | 49 | 약 60 | 약 62 |
| 새 트레이너 | 0~2 | 0~2(WATTSON·WALLY·라이벌 데이터 있음) | 0~3(NORMAN·라이벌 데이터 있음) |
| 차단 지점 | 4 | 7~8 | 8 이상 |
| 나무열매 나무 자리(P1 필수 여부) | 0(P1은 핫픽스로만) | 9(필수) | 24(필수) |
| 새 그림 | 0(배지 UI를 하면 아이콘) | 0 | 0~1 |
| 새 C 코드 | P2~P4 소량 | P2~P4 소량 | P2~P4 + 시범 포획 각색·배 이동 소량 |
| 결정이 먼저 필요한 질문 | Q2, Q3, Q9 | Q2, Q3, Q5(라이벌 스타터), Q9 | Q2, Q3, Q5(스타터 이전), Q9 |
| 상대 규모 | **약 1.0** | 약 1.4 | 약 2.2 |
| 장점 | 도착지 중심이라 동선이 자연스럽고, 새 시스템 없이 끝난다. 원작 "바다의 도시" 이벤트(박물관·STERN 선장·버려진 배)가 한데 모여 있다 | "썬더 옐로"와 가장 잘 맞는 전기 체육관·발전기 이야기. 피카츄 연출 여지 큼 | 원작의 "새 여행 시작" 느낌. 털보박사·스타터 이야기를 제대로 씀 |
| 단점 | 규모가 작아 "호연에 왔다"는 인상은 약하다. 체육관이 원작 2번째(BRAWLY)부터 시작 | 1단계치고 차단이 많고 110번 도로 사이클링로드(자전거 퍼즐 없음)를 설명해야 한다 | 스타터 중복 결정(Q5)이 먼저 필요하고 이동 수단까지 만들어야 해서 가장 크다 |

**추천: A (Z1 카이나 항구권)**, 선행 작업 P1(리셋)은 v0.5.1 핫픽스로 먼저 내고 P2~P6을 1단계에 포함한다. 2단계에 B(Mauville 전기권)를 이어 붙이면 "항구 → 전기 도시" 순서가 되어, 원작 순서(Dewford → Slateport → Mauville)와도 같다. B를 1단계로 하고 싶다면 A의 Dewford·Granite Cave·버려진 배를 2단계로 미루는 "카이나 + Mauville" 조합도 가능하다(규모 약 1.4).

---

## 부록 A. 호연 맵 인벤토리 전체

`python3 tools/hoenn_reachability.py --emerald /root/src/pokeemerald`의 출력 그대로다(457개 맵, 맵 그룹 순서).

열: `reach` Y = 이어짐, D = 다이빙 연결이 더 필요, W = 닫힌 워프 칸이 더 필요, - = 이어지지 않음 / `via` 처음 도달한 간선(출발 맵과 종류) / `conn` 연결 수, `dive` 그중 다이빙·부상 / `warp` 워프 수, `in` 다른 맵에서 들어오는 간선 수 / `npc` 대화만 하는 NPC, `trn` 트레이너, `item` 아이템볼, `svc` 간호순·점원, `other` 그 밖의 스크립트 오브젝트, `bt` 나무열매 나무 자리(리셋 원인), `sign` 표지판, `hid` 숨은 아이템, `coord` 좌표 이벤트 / `wild` L 풀·동굴, W 파도타기, R 바위깨기, F 낚시 / `heal` 회복 지점 / `em_obj`·`em_coord` 에메랄드 원작의 오브젝트·좌표 이벤트 수.

Start: `PalletTown`. Hoenn maps: 457; reachable (Y): 282; only through DIVE (D): 10; only through a closed warp tile (W): 25; not connected (-): 140.

Edges from non-Hoenn maps into Hoenn:

- `KantoAirport` -> `SlateportCity_Harbor` (special: special DoAirplaneFlightScene (EventScript_TakeAirplane))

Totals over Hoenn maps: npc 692, trn 429, item 162, svc 39, other 1, bt 87, sign 318, hid 110, coord 0, maps with wild data 116, heal locations 20.

| map | group | type | reach | via | conn | dive | warp | in | npc | trn | item | svc | other | bt | sign | hid | coord | wild | heal | em_obj | em_coord |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PetalburgCity | HoennTownsAndRoutes | CITY | Y | Route102 (conn) | 2 | 0 | 6 | 14 | 3 | 0 | 2 | 0 | 0 | 0 | 3 | 1 | 0 | WF | Y | 9 | 8 |
| SlateportCity | HoennTownsAndRoutes | CITY | Y | SlateportCity_Harbor (warp) | 3 | 0 | 11 | 23 | 18 | 0 | 0 | 1 | 0 | 0 | 8 | 0 | 0 | WF | Y | 35 | 1 |
| MauvilleCity | HoennTownsAndRoutes | CITY | Y | Route110 (conn) | 4 | 0 | 7 | 18 | 6 | 0 | 1 | 0 | 0 | 0 | 4 | 0 | 0 |  | Y | 11 | 0 |
| RustboroCity | HoennTownsAndRoutes | CITY | Y | Route116 (conn) | 3 | 0 | 12 | 25 | 11 | 0 | 1 | 0 | 0 | 0 | 6 | 0 | 0 |  | Y | 16 | 21 |
| FortreeCity | HoennTownsAndRoutes | CITY | Y | Route119 (conn) | 2 | 0 | 9 | 20 | 6 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  | Y | 7 | 0 |
| LilycoveCity | HoennTownsAndRoutes | CITY | Y | Route121 (conn) | 2 | 0 | 14 | 30 | 15 | 0 | 1 | 0 | 0 | 0 | 8 | 3 | 0 | WF | Y | 22 | 0 |
| MossdeepCity | HoennTownsAndRoutes | CITY | Y | Route124 (conn) | 3 | 0 | 10 | 23 | 10 | 0 | 1 | 0 | 0 | 0 | 4 | 0 | 0 | WF | Y | 17 | 10 |
| SootopolisCity | HoennTownsAndRoutes | CITY | - |  | 0 | 0 | 13 | 25 | 5 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | WF | Y | 18 | 0 |
| EverGrandeCity | HoennTownsAndRoutes | CITY | Y | Route128 (conn) | 1 | 0 | 4 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | WF | Y | 0 | 11 |
| LittlerootTown | HoennTownsAndRoutes | TOWN | Y | Route101 (conn) | 1 | 0 | 3 | 7 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  | Y | 8 | 9 |
| OldaleTown | HoennTownsAndRoutes | TOWN | Y | Route103 (conn) | 3 | 0 | 4 | 11 | 3 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  | Y | 4 | 4 |
| DewfordTown | HoennTownsAndRoutes | TOWN | Y | Route107 (conn) | 2 | 0 | 5 | 12 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | WF | Y | 5 | 0 |
| LavaridgeTown | HoennTownsAndRoutes | TOWN | Y | Route112 (conn) | 1 | 0 | 6 | 12 | 7 | 0 | 0 | 0 | 0 | 0 | 3 | 1 | 0 |  | Y | 9 | 1 |
| FallarborTown | HoennTownsAndRoutes | TOWN | Y | Route113 (conn) | 2 | 0 | 5 | 12 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 1 | 0 |  | Y | 4 | 0 |
| VerdanturfTown | HoennTownsAndRoutes | TOWN | Y | Route117 (conn) | 2 | 0 | 7 | 15 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |  | Y | 4 | 0 |
| PacifidlogTown | HoennTownsAndRoutes | TOWN | Y | Route132 (conn) | 2 | 0 | 6 | 14 | 3 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | WF | Y | 3 | 0 |
| Route101 | HoennTownsAndRoutes | ROUTE | Y | OldaleTown (conn) | 2 | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | L |  | 6 | 9 |
| Route102 | HoennTownsAndRoutes | ROUTE | Y | OldaleTown (conn) | 2 | 0 | 0 | 2 | 2 | 4 | 1 | 0 | 0 | 2 | 2 | 0 | 0 | LWF |  | 9 | 0 |
| Route103 | HoennTownsAndRoutes | ROUTE | Y | Route110 (conn) | 2 | 0 | 1 | 3 | 2 | 9 | 2 | 0 | 0 | 3 | 1 | 0 | 0 | LWF |  | 20 | 0 |
| Route104 | HoennTownsAndRoutes | ROUTE | Y | PetalburgCity (conn) | 3 | 0 | 8 | 13 | 7 | 8 | 4 | 0 | 0 | 10 | 5 | 5 | 0 | LWF |  | 34 | 1 |
| Route105 | HoennTownsAndRoutes | ROUTE | Y | Route106 (conn) | 3 | 1 | 1 | 4 | 0 | 7 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | WF |  | 8 | 0 |
| Route106 | HoennTownsAndRoutes | ROUTE | Y | DewfordTown (conn) | 2 | 0 | 1 | 3 | 0 | 4 | 1 | 0 | 0 | 0 | 1 | 3 | 0 | WF |  | 5 | 0 |
| Route107 | HoennTownsAndRoutes | ROUTE | Y | Route108 (conn) | 2 | 0 | 0 | 2 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 7 | 0 |
| Route108 | HoennTownsAndRoutes | ROUTE | Y | Route109 (conn) | 2 | 0 | 1 | 4 | 0 | 6 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | WF |  | 7 | 0 |
| Route109 | HoennTownsAndRoutes | ROUTE | Y | SlateportCity (conn) | 2 | 0 | 1 | 4 | 6 | 14 | 2 | 0 | 0 | 0 | 2 | 6 | 0 | WF |  | 24 | 0 |
| Route110 | HoennTownsAndRoutes | ROUTE | Y | SlateportCity (conn) | 3 | 0 | 6 | 14 | 8 | 14 | 3 | 0 | 0 | 3 | 11 | 4 | 0 | LWF |  | 36 | 9 |
| Route111 | HoennTownsAndRoutes | ROUTE | Y | MauvilleCity (conn) | 3 | 0 | 5 | 11 | 4 | 17 | 4 | 0 | 0 | 4 | 7 | 3 | 0 | LWRF |  | 46 | 34 |
| Route112 | HoennTownsAndRoutes | ROUTE | Y | Route111 (conn) | 3 | 0 | 6 | 9 | 1 | 6 | 1 | 0 | 0 | 4 | 3 | 0 | 0 | L |  | 14 | 0 |
| Route113 | HoennTownsAndRoutes | ROUTE | Y | Route111 (conn) | 3 | 0 | 3 | 5 | 2 | 11 | 3 | 0 | 0 | 0 | 4 | 2 | 0 | L |  | 16 | 19 |
| Route114 | HoennTownsAndRoutes | ROUTE | Y | FallarborTown (conn) | 2 | 0 | 5 | 7 | 3 | 13 | 3 | 0 | 0 | 3 | 3 | 2 | 0 | LWRF |  | 27 | 0 |
| Route115 | HoennTownsAndRoutes | ROUTE | Y | Route114 (conn) | 2 | 0 | 3 | 3 | 1 | 10 | 6 | 0 | 0 | 5 | 2 | 1 | 0 | LWF |  | 23 | 0 |
| Route116 | HoennTownsAndRoutes | ROUTE | Y | VerdanturfTown (conn) | 2 | 0 | 5 | 6 | 0 | 10 | 5 | 0 | 0 | 4 | 5 | 2 | 0 | L |  | 28 | 1 |
| Route117 | HoennTownsAndRoutes | ROUTE | Y | MauvilleCity (conn) | 2 | 0 | 1 | 4 | 3 | 10 | 2 | 0 | 0 | 3 | 3 | 1 | 0 | LWF |  | 24 | 0 |
| Route118 | HoennTownsAndRoutes | ROUTE | Y | MauvilleCity (conn) | 3 | 0 | 2 | 3 | 2 | 7 | 1 | 0 | 0 | 3 | 2 | 2 | 0 | LWF |  | 21 | 3 |
| Route119 | HoennTownsAndRoutes | ROUTE | Y | Route118 (conn) | 2 | 0 | 2 | 6 | 3 | 17 | 9 | 0 | 0 | 7 | 3 | 4 | 0 | LWF |  | 43 | 23 |
| Route120 | HoennTownsAndRoutes | ROUTE | Y | FortreeCity (conn) | 2 | 0 | 2 | 4 | 1 | 13 | 5 | 0 | 0 | 10 | 2 | 4 | 0 | LWF |  | 44 | 19 |
| Route121 | HoennTownsAndRoutes | ROUTE | Y | Route122 (conn) | 3 | 0 | 1 | 5 | 1 | 11 | 3 | 0 | 0 | 8 | 2 | 4 | 0 | LWF |  | 29 | 4 |
| Route122 | HoennTownsAndRoutes | ROUTE | Y | Route123 (conn) | 2 | 0 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 0 | 0 |
| Route123 | HoennTownsAndRoutes | ROUTE | Y | Route118 (conn) | 2 | 0 | 1 | 4 | 1 | 16 | 5 | 0 | 0 | 18 | 3 | 5 | 0 | LWF |  | 43 | 22 |
| Route124 | HoennTownsAndRoutes | OCEAN_ROUTE | Y | LilycoveCity (conn) | 5 | 1 | 1 | 7 | 0 | 9 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | WF |  | 12 | 0 |
| Route125 | HoennTownsAndRoutes | OCEAN_ROUTE | Y | Route124 (conn) | 3 | 1 | 1 | 4 | 0 | 9 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 10 | 0 |
| Route126 | HoennTownsAndRoutes | OCEAN_ROUTE | Y | Route124 (conn) | 3 | 1 | 0 | 3 | 0 | 8 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 9 | 0 |
| Route127 | HoennTownsAndRoutes | OCEAN_ROUTE | Y | Route128 (conn) | 4 | 1 | 0 | 4 | 0 | 8 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 11 | 0 |
| Route128 | HoennTownsAndRoutes | OCEAN_ROUTE | Y | Route129 (conn) | 4 | 1 | 0 | 4 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | WF |  | 10 | 0 |
| Route129 | HoennTownsAndRoutes | OCEAN_ROUTE | Y | Route130 (conn) | 3 | 1 | 0 | 3 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 5 | 0 |
| Route130 | HoennTownsAndRoutes | OCEAN_ROUTE | Y | Route131 (conn) | 2 | 0 | 0 | 2 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | LWF |  | 4 | 0 |
| Route131 | HoennTownsAndRoutes | OCEAN_ROUTE | Y | PacifidlogTown (conn) | 2 | 0 | 1 | 3 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 8 | 0 |
| Route132 | HoennTownsAndRoutes | OCEAN_ROUTE | Y | Route133 (conn) | 2 | 0 | 0 | 2 | 0 | 8 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 10 | 0 |
| Route133 | HoennTownsAndRoutes | OCEAN_ROUTE | Y | Route134 (conn) | 2 | 0 | 0 | 2 | 0 | 7 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 10 | 0 |
| Route134 | HoennTownsAndRoutes | OCEAN_ROUTE | Y | SlateportCity (conn) | 2 | 0 | 0 | 2 | 0 | 9 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 11 | 0 |
| Underwater_Route124 | HoennTownsAndRoutes | UNDERWATER | D | Route124 (dive) | 2 | 1 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | W |  | 0 | 0 |
| Underwater_Route126 | HoennTownsAndRoutes | UNDERWATER | D | Route126 (dive) | 3 | 1 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | W |  | 0 | 0 |
| Underwater_Route127 | HoennTownsAndRoutes | UNDERWATER | D | Route127 (dive) | 3 | 1 | 2 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |  |  | 0 | 0 |
| Underwater_Route128 | HoennTownsAndRoutes | UNDERWATER | D | Route128 (dive) | 2 | 1 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |  |  | 0 | 0 |
| Underwater_Route129 | HoennTownsAndRoutes | UNDERWATER | D | Route129 (dive) | 1 | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| Underwater_Route105 | HoennTownsAndRoutes | UNDERWATER | D | Route105 (dive) | 1 | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| Underwater_Route125 | HoennTownsAndRoutes | UNDERWATER | D | Route125 (dive) | 1 | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| LittlerootTown_BrendansHouse_1F | HoennIndoorLittleroot | INDOOR | Y | LittlerootTown (warp) | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 4 |
| LittlerootTown_BrendansHouse_2F | HoennIndoorLittleroot | INDOOR | Y | LittlerootTown_BrendansHouse_1F (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  | Y | 16 | 0 |
| LittlerootTown_MaysHouse_1F | HoennIndoorLittleroot | INDOOR | Y | LittlerootTown (warp) | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 4 |
| LittlerootTown_MaysHouse_2F | HoennIndoorLittleroot | INDOOR | Y | LittlerootTown_MaysHouse_1F (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  | Y | 16 | 0 |
| LittlerootTown_ProfessorBirchsLab | HoennIndoorLittleroot | INDOOR | Y | LittlerootTown (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 15 | 0 | 0 |  |  | 6 | 0 |
| OldaleTown_House1 | HoennIndoorOldale | INDOOR | Y | OldaleTown (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| OldaleTown_House2 | HoennIndoorOldale | INDOOR | Y | OldaleTown (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| OldaleTown_PokemonCenter_1F | HoennIndoorOldale | INDOOR | Y | OldaleTown (warp) | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| OldaleTown_PokemonCenter_2F | HoennIndoorOldale | INDOOR | Y | OldaleTown_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| OldaleTown_Mart | HoennIndoorOldale | INDOOR | Y | OldaleTown (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| DewfordTown_House1 | HoennIndoorDewford | INDOOR | Y | DewfordTown (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| DewfordTown_PokemonCenter_1F | HoennIndoorDewford | INDOOR | Y | DewfordTown (warp) | 0 | 0 | 3 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| DewfordTown_PokemonCenter_2F | HoennIndoorDewford | INDOOR | Y | DewfordTown_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| DewfordTown_Gym | HoennIndoorDewford | INDOOR | Y | DewfordTown (warp) | 0 | 0 | 2 | 1 | 1 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 8 | 0 |
| DewfordTown_Hall | HoennIndoorDewford | INDOOR | Y | DewfordTown (warp) | 0 | 0 | 2 | 1 | 6 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 9 | 0 |
| DewfordTown_House2 | HoennIndoorDewford | INDOOR | Y | DewfordTown (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| LavaridgeTown_HerbShop | HoennIndoorLavaridge | INDOOR | Y | LavaridgeTown (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| LavaridgeTown_Gym_1F | HoennIndoorLavaridge | INDOOR | Y | LavaridgeTown (warp) | 0 | 0 | 26 | 25 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 6 | 0 |
| LavaridgeTown_Gym_B1F | HoennIndoorLavaridge | INDOOR | Y | LavaridgeTown_Gym_1F (warp) | 0 | 0 | 24 | 24 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| LavaridgeTown_House | HoennIndoorLavaridge | INDOOR | Y | LavaridgeTown (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| LavaridgeTown_Mart | HoennIndoorLavaridge | INDOOR | Y | LavaridgeTown (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| LavaridgeTown_PokemonCenter_1F | HoennIndoorLavaridge | INDOOR | Y | LavaridgeTown (warp) | 0 | 0 | 4 | 3 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| LavaridgeTown_PokemonCenter_2F | HoennIndoorLavaridge | INDOOR | Y | LavaridgeTown_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| FallarborTown_Mart | HoennIndoorFallarbor | INDOOR | Y | FallarborTown (warp) | 0 | 0 | 2 | 1 | 4 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| FallarborTown_BattleTentLobby | HoennIndoorFallarbor | INDOOR | Y | FallarborTown (warp) | 0 | 0 | 2 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 5 | 0 |
| FallarborTown_BattleTentCorridor | HoennIndoorFallarbor | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| FallarborTown_BattleTentBattleRoom | HoennIndoorFallarbor | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| FallarborTown_PokemonCenter_1F | HoennIndoorFallarbor | INDOOR | Y | FallarborTown (warp) | 0 | 0 | 3 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| FallarborTown_PokemonCenter_2F | HoennIndoorFallarbor | INDOOR | Y | FallarborTown_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| FallarborTown_CozmosHouse | HoennIndoorFallarbor | INDOOR | Y | FallarborTown (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| FallarborTown_MoveRelearnersHouse | HoennIndoorFallarbor | INDOOR | Y | FallarborTown (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| VerdanturfTown_BattleTentLobby | HoennIndoorVerdanturf | INDOOR | Y | VerdanturfTown (warp) | 0 | 0 | 2 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 6 | 0 |
| VerdanturfTown_BattleTentCorridor | HoennIndoorVerdanturf | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| VerdanturfTown_BattleTentBattleRoom | HoennIndoorVerdanturf | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| VerdanturfTown_Mart | HoennIndoorVerdanturf | INDOOR | Y | VerdanturfTown (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| VerdanturfTown_PokemonCenter_1F | HoennIndoorVerdanturf | INDOOR | Y | VerdanturfTown (warp) | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| VerdanturfTown_PokemonCenter_2F | HoennIndoorVerdanturf | INDOOR | Y | VerdanturfTown_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| VerdanturfTown_WandasHouse | HoennIndoorVerdanturf | INDOOR | Y | VerdanturfTown (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| VerdanturfTown_FriendshipRatersHouse | HoennIndoorVerdanturf | INDOOR | Y | VerdanturfTown (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| VerdanturfTown_House | HoennIndoorVerdanturf | INDOOR | Y | VerdanturfTown (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| PacifidlogTown_PokemonCenter_1F | HoennIndoorPacifidlog | INDOOR | Y | PacifidlogTown (warp) | 0 | 0 | 3 | 2 | 4 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| PacifidlogTown_PokemonCenter_2F | HoennIndoorPacifidlog | INDOOR | Y | PacifidlogTown_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| PacifidlogTown_House1 | HoennIndoorPacifidlog | INDOOR | Y | PacifidlogTown (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| PacifidlogTown_House2 | HoennIndoorPacifidlog | INDOOR | Y | PacifidlogTown (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| PacifidlogTown_House3 | HoennIndoorPacifidlog | INDOOR | Y | PacifidlogTown (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| PacifidlogTown_House4 | HoennIndoorPacifidlog | INDOOR | Y | PacifidlogTown (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| PacifidlogTown_House5 | HoennIndoorPacifidlog | INDOOR | Y | PacifidlogTown (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| PetalburgCity_WallysHouse | HoennIndoorPetalburg | INDOOR | Y | PetalburgCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| PetalburgCity_Gym | HoennIndoorPetalburg | INDOOR | Y | PetalburgCity (warp) | 0 | 0 | 38 | 1 | 0 | 7 | 0 | 0 | 0 | 0 | 12 | 0 | 0 |  |  | 11 | 0 |
| PetalburgCity_House1 | HoennIndoorPetalburg | INDOOR | Y | PetalburgCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| PetalburgCity_House2 | HoennIndoorPetalburg | INDOOR | Y | PetalburgCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| PetalburgCity_PokemonCenter_1F | HoennIndoorPetalburg | INDOOR | Y | PetalburgCity (warp) | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| PetalburgCity_PokemonCenter_2F | HoennIndoorPetalburg | INDOOR | Y | PetalburgCity_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| PetalburgCity_Mart | HoennIndoorPetalburg | INDOOR | Y | PetalburgCity (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| SlateportCity_SternsShipyard_1F | HoennIndoorSlateport | INDOOR | Y | SlateportCity (warp) | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| SlateportCity_SternsShipyard_2F | HoennIndoorSlateport | INDOOR | Y | SlateportCity_SternsShipyard_1F (warp) | 0 | 0 | 1 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| SlateportCity_BattleTentLobby | HoennIndoorSlateport | INDOOR | Y | SlateportCity (warp) | 0 | 0 | 2 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 5 | 0 |
| SlateportCity_BattleTentCorridor | HoennIndoorSlateport | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| SlateportCity_BattleTentBattleRoom | HoennIndoorSlateport | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| SlateportCity_NameRatersHouse | HoennIndoorSlateport | INDOOR | Y | SlateportCity (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| SlateportCity_PokemonFanClub | HoennIndoorSlateport | INDOOR | Y | SlateportCity (warp) | 0 | 0 | 2 | 1 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 9 | 0 |
| SlateportCity_OceanicMuseum_1F | HoennIndoorSlateport | INDOOR | Y | SlateportCity (warp) | 0 | 0 | 3 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 0 |  |  | 14 | 2 |
| SlateportCity_OceanicMuseum_2F | HoennIndoorSlateport | INDOOR | Y | SlateportCity_OceanicMuseum_1F (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 21 | 0 | 0 |  |  | 7 | 0 |
| SlateportCity_Harbor | HoennIndoorSlateport | INDOOR | Y | KantoAirport (special DoAirplaneFlightScene) | 0 | 0 | 4 | 3 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |  |  | 8 | 4 |
| SlateportCity_House | HoennIndoorSlateport | INDOOR | Y | SlateportCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| SlateportCity_PokemonCenter_1F | HoennIndoorSlateport | INDOOR | Y | SlateportCity (warp) | 0 | 0 | 3 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| SlateportCity_PokemonCenter_2F | HoennIndoorSlateport | INDOOR | Y | SlateportCity_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| SlateportCity_Mart | HoennIndoorSlateport | INDOOR | Y | SlateportCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| MauvilleCity_Gym | HoennIndoorMauville | INDOOR | Y | MauvilleCity (warp) | 0 | 0 | 2 | 1 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 4 |
| MauvilleCity_BikeShop | HoennIndoorMauville | INDOOR | Y | MauvilleCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  |  | 2 | 0 |
| MauvilleCity_House1 | HoennIndoorMauville | INDOOR | Y | MauvilleCity (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| MauvilleCity_GameCorner | HoennIndoorMauville | INDOOR | Y | MauvilleCity (warp) | 0 | 0 | 2 | 1 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 12 | 0 |
| MauvilleCity_House2 | HoennIndoorMauville | INDOOR | Y | MauvilleCity (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| MauvilleCity_PokemonCenter_1F | HoennIndoorMauville | INDOOR | Y | MauvilleCity (warp) | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| MauvilleCity_PokemonCenter_2F | HoennIndoorMauville | INDOOR | Y | MauvilleCity_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| MauvilleCity_Mart | HoennIndoorMauville | INDOOR | Y | MauvilleCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| RustboroCity_DevonCorp_1F | HoennIndoorRustboro | INDOOR | Y | RustboroCity (warp) | 0 | 0 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  |  | 3 | 0 |
| RustboroCity_DevonCorp_2F | HoennIndoorRustboro | INDOOR | Y | RustboroCity_DevonCorp_1F (warp) | 0 | 0 | 2 | 2 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 6 | 0 |
| RustboroCity_DevonCorp_3F | HoennIndoorRustboro | INDOOR | Y | RustboroCity_DevonCorp_2F (warp) | 0 | 0 | 1 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  |  | 3 | 0 |
| RustboroCity_Gym | HoennIndoorRustboro | INDOOR | Y | RustboroCity (warp) | 0 | 0 | 2 | 1 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| RustboroCity_PokemonSchool | HoennIndoorRustboro | INDOOR | Y | RustboroCity (warp) | 0 | 0 | 2 | 1 | 6 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |  |  | 7 | 0 |
| RustboroCity_PokemonCenter_1F | HoennIndoorRustboro | INDOOR | Y | RustboroCity (warp) | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| RustboroCity_PokemonCenter_2F | HoennIndoorRustboro | INDOOR | Y | RustboroCity_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| RustboroCity_Mart | HoennIndoorRustboro | INDOOR | Y | RustboroCity (warp) | 0 | 0 | 2 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| RustboroCity_Flat1_1F | HoennIndoorRustboro | INDOOR | Y | RustboroCity (warp) | 0 | 0 | 3 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| RustboroCity_Flat1_2F | HoennIndoorRustboro | INDOOR | Y | RustboroCity_Flat1_1F (warp) | 0 | 0 | 1 | 1 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 8 | 0 |
| RustboroCity_House1 | HoennIndoorRustboro | INDOOR | Y | RustboroCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| RustboroCity_CuttersHouse | HoennIndoorRustboro | INDOOR | Y | RustboroCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| RustboroCity_House2 | HoennIndoorRustboro | INDOOR | Y | RustboroCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| RustboroCity_Flat2_1F | HoennIndoorRustboro | INDOOR | Y | RustboroCity (warp) | 0 | 0 | 3 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| RustboroCity_Flat2_2F | HoennIndoorRustboro | INDOOR | Y | RustboroCity_Flat2_1F (warp) | 0 | 0 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| RustboroCity_Flat2_3F | HoennIndoorRustboro | INDOOR | Y | RustboroCity_Flat2_2F (warp) | 0 | 0 | 1 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| RustboroCity_House3 | HoennIndoorRustboro | INDOOR | Y | RustboroCity (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| FortreeCity_House1 | HoennIndoorFortree | INDOOR | Y | FortreeCity (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| FortreeCity_Gym | HoennIndoorFortree | INDOOR | Y | FortreeCity (warp) | 0 | 0 | 2 | 1 | 1 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 8 | 0 |
| FortreeCity_PokemonCenter_1F | HoennIndoorFortree | INDOOR | Y | FortreeCity (warp) | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| FortreeCity_PokemonCenter_2F | HoennIndoorFortree | INDOOR | Y | FortreeCity_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| FortreeCity_Mart | HoennIndoorFortree | INDOOR | Y | FortreeCity (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| FortreeCity_House2 | HoennIndoorFortree | INDOOR | Y | FortreeCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| FortreeCity_House3 | HoennIndoorFortree | INDOOR | Y | FortreeCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| FortreeCity_House4 | HoennIndoorFortree | INDOOR | Y | FortreeCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| FortreeCity_House5 | HoennIndoorFortree | INDOOR | Y | FortreeCity (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| FortreeCity_DecorationShop | HoennIndoorFortree | INDOOR | Y | FortreeCity (warp) | 0 | 0 | 2 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| LilycoveCity_CoveLilyMotel_1F | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 1 |
| LilycoveCity_CoveLilyMotel_2F | HoennIndoorLilycove | INDOOR | Y | LilycoveCity_CoveLilyMotel_1F (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| LilycoveCity_LilycoveMuseum_1F | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 3 | 3 | 5 | 0 | 0 | 0 | 0 | 0 | 16 | 0 | 0 |  |  | 10 | 0 |
| LilycoveCity_LilycoveMuseum_2F | HoennIndoorLilycove | INDOOR | Y | LilycoveCity_LilycoveMuseum_1F (warp) | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 0 |  |  | 4 | 0 |
| LilycoveCity_ContestLobby | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 4 | 5 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 25 | 0 |
| LilycoveCity_ContestHall | HoennIndoorLilycove | INDOOR | Y | LilycoveCity_ContestLobby (warp) | 0 | 0 | 4 | 2 | 32 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 |  |  | 32 | 0 |
| LilycoveCity_PokemonCenter_1F | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 3 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| LilycoveCity_PokemonCenter_2F | HoennIndoorLilycove | INDOOR | Y | LilycoveCity_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| LilycoveCity_UnusedMart | HoennIndoorLilycove | INDOOR | - |  | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| LilycoveCity_PokemonTrainerFanClub | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 2 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 9 | 0 |
| LilycoveCity_Harbor | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| LilycoveCity_MoveDeletersHouse | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| LilycoveCity_House1 | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| LilycoveCity_House2 | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| LilycoveCity_House3 | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 6 | 0 |
| LilycoveCity_House4 | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| LilycoveCity_DepartmentStore_1F | HoennIndoorLilycove | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 4 | 2 | 6 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 6 | 0 |
| LilycoveCity_DepartmentStore_2F | HoennIndoorLilycove | INDOOR | Y | LilycoveCity_DepartmentStore_1F (warp) | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| LilycoveCity_DepartmentStore_3F | HoennIndoorLilycove | INDOOR | Y | LilycoveCity_DepartmentStore_2F (warp) | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| LilycoveCity_DepartmentStore_4F | HoennIndoorLilycove | INDOOR | Y | LilycoveCity_DepartmentStore_3F (warp) | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| LilycoveCity_DepartmentStore_5F | HoennIndoorLilycove | INDOOR | Y | LilycoveCity_DepartmentStore_4F (warp) | 0 | 0 | 3 | 2 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| LilycoveCity_DepartmentStoreRooftop | HoennIndoorLilycove | INDOOR | Y | LilycoveCity_DepartmentStore_5F (warp) | 0 | 0 | 1 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  |  | 4 | 0 |
| LilycoveCity_DepartmentStoreElevator | HoennIndoorLilycove | INDOOR | Y | LilycoveCity_DepartmentStore_1F (warp) | 0 | 0 | 2 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| MossdeepCity_Gym | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity (warp) | 0 | 0 | 14 | 1 | 1 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 36 | 9 |
| MossdeepCity_House1 | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| MossdeepCity_House2 | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| MossdeepCity_PokemonCenter_1F | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity (warp) | 0 | 0 | 3 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| MossdeepCity_PokemonCenter_2F | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| MossdeepCity_Mart | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| MossdeepCity_House3 | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| MossdeepCity_StevensHouse | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity (warp) | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |  |  | 3 | 0 |
| MossdeepCity_House4 | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| MossdeepCity_SpaceCenter_1F | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity (warp) | 0 | 0 | 3 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 11 | 0 |
| MossdeepCity_SpaceCenter_2F | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity_SpaceCenter_1F (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 9 | 0 |
| MossdeepCity_GameCorner_1F | HoennIndoorMossdeep | INDOOR | Y | MossdeepCity (warp) | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 2 | 0 |
| MossdeepCity_GameCorner_B1F | HoennIndoorMossdeep | INDOOR | W | MossdeepCity_GameCorner_1F (inert) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| SootopolisCity_Gym_1F | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 3 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| SootopolisCity_Gym_B1F | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 1 | 1 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 10 | 0 |
| SootopolisCity_PokemonCenter_1F | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| SootopolisCity_PokemonCenter_2F | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| SootopolisCity_Mart | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| SootopolisCity_House1 | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| SootopolisCity_House2 | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| SootopolisCity_House3 | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| SootopolisCity_House4 | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| SootopolisCity_House5 | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| SootopolisCity_House6 | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| SootopolisCity_House7 | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| SootopolisCity_LotadAndSeedotHouse | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  |  | 2 | 0 |
| SootopolisCity_MysteryEventsHouse_1F | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| SootopolisCity_MysteryEventsHouse_B1F | HoennIndoorSootopolis | INDOOR | - |  | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| EverGrandeCity_SidneysRoom | HoennIndoorEverGrande | INDOOR | Y | EverGrandeCity_Hall5 (warp) | 0 | 0 | 2 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| EverGrandeCity_PhoebesRoom | HoennIndoorEverGrande | INDOOR | W | EverGrandeCity_Hall1 (warp) | 0 | 0 | 2 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| EverGrandeCity_GlaciasRoom | HoennIndoorEverGrande | INDOOR | W | EverGrandeCity_Hall2 (warp) | 0 | 0 | 2 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| EverGrandeCity_DrakesRoom | HoennIndoorEverGrande | INDOOR | W | EverGrandeCity_Hall3 (warp) | 0 | 0 | 2 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| EverGrandeCity_ChampionsRoom | HoennIndoorEverGrande | INDOOR | W | EverGrandeCity_Hall4 (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| EverGrandeCity_Hall1 | HoennIndoorEverGrande | INDOOR | W | EverGrandeCity_SidneysRoom (inert) | 0 | 0 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| EverGrandeCity_Hall2 | HoennIndoorEverGrande | INDOOR | W | EverGrandeCity_PhoebesRoom (inert) | 0 | 0 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| EverGrandeCity_Hall3 | HoennIndoorEverGrande | INDOOR | W | EverGrandeCity_GlaciasRoom (inert) | 0 | 0 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| EverGrandeCity_Hall4 | HoennIndoorEverGrande | INDOOR | W | EverGrandeCity_DrakesRoom (inert) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| EverGrandeCity_Hall5 | HoennIndoorEverGrande | INDOOR | Y | EverGrandeCity_PokemonLeague_1F (warp) | 0 | 0 | 4 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| EverGrandeCity_PokemonLeague_1F | HoennIndoorEverGrande | INDOOR | Y | EverGrandeCity (warp) | 0 | 0 | 5 | 5 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| EverGrandeCity_HallOfFame | HoennIndoorEverGrande | INDOOR | W | EverGrandeCity_ChampionsRoom (inert) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| EverGrandeCity_PokemonCenter_1F | HoennIndoorEverGrande | INDOOR | Y | EverGrandeCity (warp) | 0 | 0 | 3 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| EverGrandeCity_PokemonCenter_2F | HoennIndoorEverGrande | INDOOR | Y | EverGrandeCity_PokemonCenter_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| EverGrandeCity_PokemonLeague_2F | HoennIndoorEverGrande | INDOOR | Y | EverGrandeCity_PokemonLeague_1F (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| Route104_MrBrineysHouse | HoennIndoorRoute104 | INDOOR | Y | Route104 (warp) | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| Route104_PrettyPetalFlowerShop | HoennIndoorRoute104 | INDOOR | Y | Route104 (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| Route111_WinstrateFamilysHouse | HoennIndoorRoute111 | INDOOR | Y | Route111 (warp) | 0 | 0 | 2 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| Route111_OldLadysRestStop | HoennIndoorRoute111 | INDOOR | Y | Route111 (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| Route112_CableCarStation | HoennIndoorRoute112 | INDOOR | Y | Route112 (warp) | 0 | 0 | 2 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| MtChimney_CableCarStation | HoennIndoorRoute112 | INDOOR | Y | MtChimney (warp) | 0 | 0 | 2 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| Route114_FossilManiacsHouse | HoennIndoorRoute114 | INDOOR | Y | Route114 (warp) | 0 | 0 | 3 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |  |  | 1 | 0 |
| Route114_FossilManiacsTunnel | HoennIndoorRoute114 | INDOOR | Y | Route114_FossilManiacsHouse (warp) | 0 | 0 | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 2 |
| Route114_LanettesHouse | HoennIndoorRoute114 | INDOOR | Y | Route114 (warp) | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |  |  | 1 | 0 |
| Route116_TunnelersRestHouse | HoennIndoorRoute116 | INDOOR | Y | Route116 (warp) | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| Route117_PokemonDayCare | HoennIndoorRoute117 | INDOOR | Y | Route117 (warp) | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| Route121_SafariZoneEntrance | HoennIndoorRoute121 | INDOOR | Y | Route121 (warp) | 0 | 0 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 1 |
| MeteorFalls_1F_1R | HoennDungeons | UNDERGROUND | Y | Route114 (warp) | 0 | 0 | 6 | 6 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | LWF |  | 10 | 1 |
| MeteorFalls_1F_2R | HoennDungeons | UNDERGROUND | Y | MeteorFalls_1F_1R (warp) | 0 | 0 | 4 | 4 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | LWF |  | 3 | 0 |
| MeteorFalls_B1F_1R | HoennDungeons | UNDERGROUND | Y | MeteorFalls_1F_1R (warp) | 0 | 0 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | LWF |  | 0 | 0 |
| MeteorFalls_B1F_2R | HoennDungeons | UNDERGROUND | Y | MeteorFalls_B1F_1R (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | LWF |  | 1 | 0 |
| RusturfTunnel | HoennDungeons | UNDERGROUND | Y | VerdanturfTown (warp) | 0 | 0 | 3 | 3 | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 10 | 5 |
| Underwater_SootopolisCity | HoennDungeons | UNDERWATER | D | Underwater_Route126 (warp) | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| DesertRuins | HoennDungeons | UNDERGROUND | Y | Route111 (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| GraniteCave_1F | HoennDungeons | UNDERGROUND | Y | Route106 (warp) | 0 | 0 | 4 | 4 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 2 | 0 |
| GraniteCave_B1F | HoennDungeons | UNDERGROUND | Y | GraniteCave_1F (warp) | 0 | 0 | 7 | 7 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 1 | 0 |
| GraniteCave_B2F | HoennDungeons | UNDERGROUND | Y | GraniteCave_B1F (warp) | 0 | 0 | 5 | 5 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | LR |  | 9 | 0 |
| GraniteCave_StevensRoom | HoennDungeons | UNDERGROUND | Y | GraniteCave_1F (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 1 | 0 |
| PetalburgWoods | HoennDungeons | ROUTE | Y | Route104 (warp) | 0 | 0 | 6 | 6 | 3 | 2 | 4 | 0 | 0 | 0 | 2 | 4 | 0 | L |  | 13 | 2 |
| MtChimney | HoennDungeons | ROUTE | Y | JaggedPass (warp) | 0 | 0 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  |  | 30 | 0 |
| JaggedPass | HoennDungeons | ROUTE | Y | Route112 (warp) | 0 | 0 | 5 | 5 | 0 | 5 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | L |  | 7 | 10 |
| FieryPath | HoennDungeons | UNDERGROUND | Y | Route112 (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 8 | 0 |
| MtPyre_1F | HoennDungeons | INDOOR | Y | Route122 (warp) | 0 | 0 | 6 | 4 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 3 | 0 |
| MtPyre_2F | HoennDungeons | INDOOR | Y | MtPyre_1F (warp) | 0 | 0 | 5 | 5 | 2 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 8 | 0 |
| MtPyre_3F | HoennDungeons | INDOOR | Y | MtPyre_2F (warp) | 0 | 0 | 6 | 6 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 4 | 0 |
| MtPyre_4F | HoennDungeons | INDOOR | Y | MtPyre_3F (warp) | 0 | 0 | 6 | 6 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 2 | 0 |
| MtPyre_5F | HoennDungeons | INDOOR | Y | MtPyre_4F (warp) | 0 | 0 | 5 | 5 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 2 | 0 |
| MtPyre_6F | HoennDungeons | INDOOR | Y | MtPyre_5F (warp) | 0 | 0 | 2 | 2 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 3 | 0 |
| MtPyre_Exterior | HoennDungeons | ROUTE | Y | MtPyre_1F (warp) | 0 | 0 | 3 | 5 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | L |  | 2 | 5 |
| MtPyre_Summit | HoennDungeons | ROUTE | Y | MtPyre_Exterior (warp) | 0 | 0 | 3 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | L |  | 8 | 6 |
| AquaHideout_1F | HoennDungeons | INDOOR | Y | LilycoveCity (warp) | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| AquaHideout_B1F | HoennDungeons | INDOOR | Y | AquaHideout_1F (warp) | 0 | 0 | 25 | 5 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 9 | 0 |
| AquaHideout_B2F | HoennDungeons | INDOOR | Y | AquaHideout_B1F (warp) | 0 | 0 | 10 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 6 | 2 |
| Underwater_SeafloorCavern | HoennDungeons | UNDERWATER | D | Underwater_Route128 (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| SeafloorCavern_Entrance | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 2 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 1 | 0 |
| SeafloorCavern_Room1 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 5 | 0 |
| SeafloorCavern_Room2 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 8 | 0 |
| SeafloorCavern_Room3 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 9 | 0 |
| SeafloorCavern_Room4 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 4 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 2 | 0 |
| SeafloorCavern_Room5 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 6 | 0 |
| SeafloorCavern_Room6 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | LWF |  | 0 | 0 |
| SeafloorCavern_Room7 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | LWF |  | 0 | 0 |
| SeafloorCavern_Room8 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 12 | 0 |
| SeafloorCavern_Room9 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 1 |
| CaveOfOrigin_Entrance | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| CaveOfOrigin_1F | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 2 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| CaveOfOrigin_UnusedRubySapphireMap1 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| CaveOfOrigin_UnusedRubySapphireMap2 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| CaveOfOrigin_UnusedRubySapphireMap3 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| CaveOfOrigin_B1F | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| HoennVictoryRoad_1F | HoennDungeons | UNDERGROUND | Y | EverGrandeCity (warp) | 0 | 0 | 5 | 5 | 5 | 0 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | L |  | 9 | 2 |
| VictoryRoad_B1F | HoennDungeons | UNDERGROUND | Y | HoennVictoryRoad_1F (warp) | 0 | 0 | 7 | 7 | 0 | 5 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | LR |  | 21 | 0 |
| VictoryRoad_B2F | HoennDungeons | UNDERGROUND | Y | VictoryRoad_B1F (warp) | 0 | 0 | 4 | 4 | 0 | 6 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | LWF |  | 7 | 0 |
| ShoalCave_LowTideEntranceRoom | HoennDungeons | UNDERGROUND | Y | Route125 (warp) | 0 | 0 | 4 | 4 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | LWF |  | 2 | 0 |
| ShoalCave_LowTideInnerRoom | HoennDungeons | UNDERGROUND | Y | ShoalCave_LowTideEntranceRoom (warp) | 0 | 0 | 8 | 8 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | LWF |  | 1 | 0 |
| ShoalCave_LowTideStairsRoom | HoennDungeons | UNDERGROUND | Y | ShoalCave_LowTideInnerRoom (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 1 | 0 |
| ShoalCave_LowTideLowerRoom | HoennDungeons | UNDERGROUND | Y | ShoalCave_LowTideInnerRoom (warp) | 0 | 0 | 4 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 2 | 0 |
| ShoalCave_HighTideEntranceRoom | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| ShoalCave_HighTideInnerRoom | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| NewMauville_Entrance | HoennDungeons | UNDERGROUND | Y | Route110 (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 1 |
| NewMauville_Inside | HoennDungeons | UNDERGROUND | Y | NewMauville_Entrance (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 5 | 0 | 0 | 0 | 8 | 0 | 0 | L |  | 8 | 10 |
| AbandonedShip_Deck | HoennDungeons | UNDERGROUND | Y | Route108 (warp) | 0 | 0 | 5 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| AbandonedShip_Corridors_1F | HoennDungeons | UNDERGROUND | Y | AbandonedShip_Deck (warp) | 0 | 0 | 12 | 13 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| AbandonedShip_Rooms_1F | HoennDungeons | UNDERGROUND | Y | AbandonedShip_Corridors_1F (warp) | 0 | 0 | 6 | 4 | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| AbandonedShip_Corridors_B1F | HoennDungeons | UNDERGROUND | Y | AbandonedShip_Corridors_1F (warp) | 0 | 0 | 8 | 11 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 2 | 0 |
| AbandonedShip_Rooms_B1F | HoennDungeons | UNDERGROUND | Y | AbandonedShip_Corridors_B1F (warp) | 0 | 0 | 3 | 3 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | WF |  | 2 | 0 |
| AbandonedShip_Rooms2_B1F | HoennDungeons | UNDERGROUND | Y | AbandonedShip_Corridors_B1F (warp) | 0 | 0 | 4 | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| AbandonedShip_Underwater1 | HoennDungeons | UNDERWATER | - |  | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| AbandonedShip_Room_B1F | HoennDungeons | UNDERGROUND | Y | AbandonedShip_Corridors_B1F (warp) | 0 | 0 | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| AbandonedShip_Rooms2_1F | HoennDungeons | UNDERGROUND | Y | AbandonedShip_Corridors_1F (warp) | 0 | 0 | 3 | 2 | 0 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| AbandonedShip_CaptainsOffice | HoennDungeons | UNDERGROUND | Y | AbandonedShip_Deck (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| AbandonedShip_Underwater2 | HoennDungeons | UNDERWATER | - |  | 0 | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| AbandonedShip_HiddenFloorCorridors | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 6 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | WF |  | 0 | 0 |
| AbandonedShip_HiddenFloorRooms | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 9 | 6 | 0 | 0 | 4 | 0 | 0 | 0 | 6 | 4 | 0 |  |  | 4 | 0 |
| IslandCave | HoennDungeons | UNDERGROUND | Y | Route105 (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| AncientTomb | HoennDungeons | UNDERGROUND | Y | Route120 (warp) | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| Underwater_Route134 | HoennDungeons | UNDERWATER | - |  | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| Underwater_SealedChamber | HoennDungeons | UNDERWATER | - |  | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| SealedChamber_OuterRoom | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| SealedChamber_InnerRoom | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| ScorchedSlab | HoennDungeons | UNDERGROUND | Y | Route120 (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| AquaHideout_UnusedRubyMap1 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| AquaHideout_UnusedRubyMap2 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| AquaHideout_UnusedRubyMap3 | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| SkyPillar_Entrance | HoennDungeons | UNDERGROUND | W | Route131 (inert) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| SkyPillar_Outside | HoennDungeons | ROUTE | W | SkyPillar_Entrance (warp) | 0 | 0 | 2 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| SkyPillar_1F | HoennDungeons | UNDERGROUND | W | SkyPillar_Outside (inert) | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| SkyPillar_2F | HoennDungeons | UNDERGROUND | W | SkyPillar_1F (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| SkyPillar_3F | HoennDungeons | UNDERGROUND | W | SkyPillar_2F (warp) | 0 | 0 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| SkyPillar_4F | HoennDungeons | UNDERGROUND | W | SkyPillar_3F (warp) | 0 | 0 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| ShoalCave_LowTideIceRoom | HoennDungeons | UNDERGROUND | Y | ShoalCave_LowTideLowerRoom (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 2 | 0 |
| SkyPillar_5F | HoennDungeons | UNDERGROUND | W | SkyPillar_4F (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| SkyPillar_Top | HoennDungeons | ROUTE | W | SkyPillar_5F (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 1 |
| MagmaHideout_1F | HoennDungeons | UNDERGROUND | Y | JaggedPass (warp) | 0 | 0 | 4 | 4 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 6 | 0 |
| MagmaHideout_2F_1R | HoennDungeons | UNDERGROUND | Y | MagmaHideout_1F (warp) | 0 | 0 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 4 | 0 |
| MagmaHideout_2F_2R | HoennDungeons | UNDERGROUND | Y | MagmaHideout_1F (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 6 | 0 |
| MagmaHideout_3F_1R | HoennDungeons | UNDERGROUND | Y | MagmaHideout_2F_1R (warp) | 0 | 0 | 3 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 3 | 0 |
| MagmaHideout_3F_2R | HoennDungeons | UNDERGROUND | Y | MagmaHideout_3F_1R (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 2 | 0 |
| MagmaHideout_4F | HoennDungeons | UNDERGROUND | Y | MagmaHideout_3F_1R (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 8 | 0 |
| MagmaHideout_3F_3R | HoennDungeons | UNDERGROUND | Y | MagmaHideout_2F_3R (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 1 | 0 |
| MagmaHideout_2F_3R | HoennDungeons | UNDERGROUND | Y | MagmaHideout_1F (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| MirageTower_1F | HoennDungeons | UNDERGROUND | Y | Route111 (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| MirageTower_2F | HoennDungeons | UNDERGROUND | Y | MirageTower_1F (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| MirageTower_3F | HoennDungeons | UNDERGROUND | Y | MirageTower_2F (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 2 | 0 |
| MirageTower_4F | HoennDungeons | UNDERGROUND | Y | MirageTower_3F (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 3 | 0 |
| DesertUnderpass | HoennDungeons | UNDERGROUND | Y | Route114_FossilManiacsTunnel (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 1 | 0 |
| ArtisanCave_B1F | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 4 | 0 | L |  | 1 | 0 |
| ArtisanCave_1F | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 1 | 0 |
| Underwater_MarineCave | HoennDungeons | UNDERWATER | D | Underwater_Route105 (warp) | 0 | 0 | 1 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| MarineCave_Entrance | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| MarineCave_End | HoennDungeons | UNDERGROUND | - |  | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 1 |
| TerraCave_Entrance | HoennDungeons | UNDERGROUND | W | Route118 (inert) | 0 | 0 | 2 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| TerraCave_End | HoennDungeons | UNDERGROUND | W | TerraCave_Entrance (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 1 |
| AlteringCave | HoennDungeons | UNDERGROUND | W | Route103 (inert) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 0 | 0 |
| MeteorFalls_StevensCave | HoennDungeons | UNDERGROUND | W | MeteorFalls_1F_1R (inert) | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 1 | 0 |
| ContestHall | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 15 | 0 |
| ContestHallBeauty | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 15 | 0 |
| ContestHallTough | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 15 | 0 |
| ContestHallCool | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 15 | 0 |
| ContestHallSmart | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 15 | 0 |
| ContestHallCute | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 15 | 0 |
| InsideOfTruck | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |  |  | 3 | 3 |
| SSTidalCorridor | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 9 | 13 | 2 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 0 |  |  | 5 | 0 |
| SSTidalLowerDeck | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 1 | 1 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |  |  | 2 | 0 |
| SSTidalRooms | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 12 | 8 | 0 | 7 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  |  | 8 | 0 |
| BattlePyramidSquare01 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare02 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare03 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare04 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare05 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare06 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare07 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare08 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare09 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare10 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare11 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare12 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare13 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare14 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare15 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattlePyramidSquare16 | HoennIndoorDynamic | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| SafariZone_Northwest | HoennSpecialArea | ROUTE | Y | HoennSafariZone_North (conn) | 2 | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | LWF |  | 2 | 0 |
| HoennSafariZone_North | HoennSpecialArea | ROUTE | Y | SafariZone_South (conn) | 3 | 0 | 0 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | LR |  | 9 | 0 |
| SafariZone_Southwest | HoennSpecialArea | ROUTE | Y | SafariZone_South (conn) | 2 | 0 | 1 | 4 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | LWF |  | 2 | 0 |
| SafariZone_South | HoennSpecialArea | ROUTE | Y | Route121_SafariZoneEntrance (warp) | 3 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | L |  | 6 | 0 |
| BattleFrontier_OutsideWest | HoennSpecialArea | ROUTE | - |  | 1 | 0 | 11 | 23 | 21 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |  |  | 24 | 0 |
| BattleFrontier_BattleTowerLobby | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 3 | 3 | 7 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 9 | 0 |
| BattleFrontier_BattleTowerElevator | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| BattleFrontier_BattleTowerCorridor | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| BattleFrontier_BattleTowerBattleRoom | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| SouthernIsland_Exterior | HoennSpecialArea | ROUTE | - |  | 0 | 0 | 2 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  | Y | 2 | 0 |
| SouthernIsland_Interior | HoennSpecialArea | ROUTE | - |  | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| SafariZone_RestHouse | HoennSpecialArea | INDOOR | Y | SafariZone_Southwest (warp) | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| SafariZone_Northeast | HoennSpecialArea | ROUTE | Y | HoennSafariZone_North (conn) | 2 | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | LR |  | 9 | 0 |
| SafariZone_Southeast | HoennSpecialArea | ROUTE | Y | SafariZone_South (conn) | 2 | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | LWF |  | 5 | 0 |
| BattleFrontier_OutsideEast | HoennSpecialArea | ROUTE | - |  | 1 | 0 | 14 | 23 | 25 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 |  | Y | 26 | 0 |
| BattleFrontier_BattleTowerMultiPartnerRoom | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 9 | 0 |
| BattleFrontier_BattleTowerMultiCorridor | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| BattleFrontier_BattleTowerMultiBattleRoom | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 6 | 0 |
| BattleFrontier_BattleDomeLobby | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 6 | 0 |
| BattleFrontier_BattleDomeCorridor | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| BattleFrontier_BattleDomePreBattleRoom | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| BattleFrontier_BattleDomeBattleRoom | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 15 | 0 |
| BattleFrontier_BattlePalaceLobby | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 3 | 3 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 6 | 0 |
| BattleFrontier_BattlePalaceCorridor | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 4 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| BattleFrontier_BattlePalaceBattleRoom | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| BattleFrontier_BattlePyramidLobby | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 1 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 4 | 0 |
| BattleFrontier_BattlePyramidFloor | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 16 | 0 |
| BattleFrontier_BattlePyramidTop | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 1 |
| BattleFrontier_BattleArenaLobby | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 1 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 5 | 0 |
| BattleFrontier_BattleArenaCorridor | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| BattleFrontier_BattleArenaBattleRoom | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 9 | 0 |
| BattleFrontier_BattleFactoryLobby | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 6 | 0 |
| BattleFrontier_BattleFactoryPreBattleRoom | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| BattleFrontier_BattleFactoryBattleRoom | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 8 | 0 |
| BattleFrontier_BattlePikeLobby | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 3 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 4 | 0 |
| BattleFrontier_BattlePikeCorridor | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| BattleFrontier_BattlePikeThreePathRoom | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 9 |
| BattleFrontier_BattlePikeRoomNormal | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 7 |
| BattleFrontier_BattlePikeRoomFinal | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| BattleFrontier_BattlePikeRoomWildMons | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 7 |
| BattleFrontier_RankingHall | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 |  |  | 3 | 0 |
| BattleFrontier_Lounge1 | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 1 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| BattleFrontier_ExchangeServiceCorner | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 3 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 9 | 0 |
| BattleFrontier_Lounge2 | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| BattleFrontier_Lounge3 | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 1 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| BattleFrontier_Lounge4 | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 1 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| BattleFrontier_ScottsHouse | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| BattleFrontier_Lounge5 | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| BattleFrontier_Lounge6 | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| BattleFrontier_Lounge7 | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 1 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| BattleFrontier_ReceptionGate | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 2 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| BattleFrontier_Lounge8 | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 1 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 3 | 0 |
| BattleFrontier_Lounge9 | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| BattleFrontier_PokemonCenter_1F | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 3 | 2 | 4 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 0 |
| BattleFrontier_PokemonCenter_2F | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| BattleFrontier_Mart | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 1 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| FarawayIsland_Entrance | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 2 | 3 |
| FarawayIsland_Interior | HoennSpecialArea | INDOOR | - |  | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| TrainerHill_Entrance | HoennSpecialArea | INDOOR | Y | Route111 (warp) | 0 | 0 | 3 | 2 | 3 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 1 |
| TrainerHill_1F | HoennSpecialArea | INDOOR | Y | TrainerHill_Entrance (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| TrainerHill_2F | HoennSpecialArea | INDOOR | Y | TrainerHill_1F (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| TrainerHill_3F | HoennSpecialArea | INDOOR | Y | TrainerHill_2F (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| TrainerHill_4F | HoennSpecialArea | INDOOR | Y | TrainerHill_3F (warp) | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| TrainerHill_Roof | HoennSpecialArea | INDOOR | Y | TrainerHill_4F (warp) | 0 | 0 | 2 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| TrainerHill_Elevator | HoennSpecialArea | INDOOR | Y | TrainerHill_Roof (warp) | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 0 |
| Route109_SeashoreHouse | HoennIndoorRoute109 | INDOOR | Y | Route109 (warp) | 0 | 0 | 2 | 1 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| Route110_TrickHouseEntrance | HoennIndoorRoute110 | INDOOR | Y | Route110 (warp) | 0 | 0 | 3 | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 4 |
| Route110_TrickHouseEnd | HoennIndoorRoute110 | INDOOR | W | Route110_TrickHousePuzzle1 (inert) | 0 | 0 | 2 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |  |  | 1 | 1 |
| Route110_TrickHouseCorridor | HoennIndoorRoute110 | INDOOR | W | Route110_TrickHouseEnd (warp) | 0 | 0 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 0 | 0 |
| Route110_TrickHousePuzzle1 | HoennIndoorRoute110 | INDOOR | W | Route110_TrickHouseEntrance (inert) | 0 | 0 | 3 | 2 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 15 | 0 |
| Route110_TrickHousePuzzle2 | HoennIndoorRoute110 | INDOOR | - |  | 0 | 0 | 3 | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 4 |
| Route110_TrickHousePuzzle3 | HoennIndoorRoute110 | INDOOR | - |  | 0 | 0 | 3 | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 4 |
| Route110_TrickHousePuzzle4 | HoennIndoorRoute110 | INDOOR | - |  | 0 | 0 | 3 | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 14 | 0 |
| Route110_TrickHousePuzzle5 | HoennIndoorRoute110 | INDOOR | - |  | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 5 | 22 |
| Route110_TrickHousePuzzle6 | HoennIndoorRoute110 | INDOOR | - |  | 0 | 0 | 3 | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| Route110_TrickHousePuzzle7 | HoennIndoorRoute110 | INDOOR | - |  | 0 | 0 | 13 | 0 | 0 | 6 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 9 | 4 |
| Route110_TrickHousePuzzle8 | HoennIndoorRoute110 | INDOOR | - |  | 0 | 0 | 3 | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 4 | 0 |
| Route110_SeasideCyclingRoadSouthEntrance | HoennIndoorRoute110 | INDOOR | Y | Route110 (warp) | 0 | 0 | 4 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 2 |
| Route110_SeasideCyclingRoadNorthEntrance | HoennIndoorRoute110 | INDOOR | Y | Route110 (warp) | 0 | 0 | 4 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 1 | 2 |
| Route113_GlassWorkshop | HoennIndoorRoute113 | INDOOR | Y | Route113 (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| Route123_BerryMastersHouse | HoennIndoorRoute123 | INDOOR | Y | Route123 (warp) | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 2 | 0 |
| Route119_WeatherInstitute_1F | HoennIndoorRoute119 | INDOOR | Y | Route119 (warp) | 0 | 0 | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |  |  | 5 | 0 |
| Route119_WeatherInstitute_2F | HoennIndoorRoute119 | INDOOR | Y | Route119_WeatherInstitute_1F (warp) | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 8 | 0 |
| Route119_House | HoennIndoorRoute119 | INDOOR | Y | Route119 (warp) | 0 | 0 | 2 | 1 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  | 7 | 0 |
| Route124_DivingTreasureHuntersHouse | HoennIndoorRoute124 | INDOOR | Y | Route124 (warp) | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  | 1 | 0 |

## 부록 B. 구역 요약과 경계

`python3 tools/hoenn_reachability.py --zones`의 출력. "Cross-zone edges"가 차단 NPC·스토리 관문이 있어야 할 자리다(`inert`는 닫힌 워프 칸이라 지금은 통과할 수 없음).

| zone | maps | reach Y | npc | trn | item | hid | bt | sign | wild maps | heal |
|---|---|---|---|---|---|---|---|---|---|---|
| Z1 | 41 | 37 | 72 | 49 | 18 | 16 | 0 | 60 | 12 | 2 |
| Z2 | 35 | 25 | 59 | 60 | 21 | 8 | 9 | 34 | 5 | 2 |
| Z3 | 52 | 50 | 110 | 62 | 28 | 15 | 24 | 70 | 11 | 6 |
| Z4 | 55 | 54 | 62 | 56 | 26 | 11 | 11 | 32 | 24 | 2 |
| Z5 | 68 | 64 | 152 | 76 | 40 | 28 | 43 | 61 | 20 | 2 |
| Z6 | 94 | 39 | 75 | 106 | 22 | 24 | 0 | 16 | 38 | 3 |
| Z7 | 19 | 10 | 13 | 11 | 5 | 3 | 0 | 3 | 4 | 1 |
| Z8 | 93 | 3 | 149 | 9 | 2 | 5 | 0 | 42 | 2 | 2 |

Cross-zone edges (where a blocker or a story gate has to sit):

- Z7 -> Z6: `EverGrandeCity` -> `Route128` (conn left)
- Z4 -> Z8: `FallarborTown` -> `FallarborTown_BattleTentLobby` (warp warp 1)
- Z8 -> Z4: `FallarborTown_BattleTentLobby` -> `FallarborTown` (warp warp 0)
- Z8 -> Z4: `FallarborTown_BattleTentLobby` -> `FallarborTown` (warp warp 1)
- Z6 -> Z3: `IslandCave` -> `Route105` (warp warp 0)
- Z5 -> Z6: `LilycoveCity` -> `Route124` (conn right)
- Z2 -> Z4: `MauvilleCity` -> `Route111` (conn up)
- Z4 -> Z3: `MeteorFalls_1F_1R` -> `Route115` (warp warp 1)
- Z3 -> Z2: `Route103` -> `Route110` (conn right)
- Z3 -> Z1: `Route105` -> `Route106` (conn down)
- Z3 -> Z6: `Route105` -> `IslandCave` (warp warp 0)
- Z1 -> Z3: `Route106` -> `Route105` (conn up)
- Z2 -> Z1: `Route110` -> `SlateportCity` (conn down)
- Z2 -> Z3: `Route110` -> `Route103` (conn left)
- Z4 -> Z2: `Route111` -> `MauvilleCity` (conn down)
- Z4 -> Z8: `Route113` -> `TerraCave_Entrance` (inert warp 1)
- Z4 -> Z8: `Route113` -> `TerraCave_Entrance` (inert warp 2)
- Z4 -> Z3: `Route114` -> `Route115` (conn left)
- Z4 -> Z8: `Route114` -> `TerraCave_Entrance` (inert warp 3)
- Z4 -> Z8: `Route114` -> `TerraCave_Entrance` (inert warp 4)
- Z3 -> Z4: `Route115` -> `Route114` (conn right)
- Z3 -> Z4: `Route115` -> `MeteorFalls_1F_1R` (warp warp 0)
- Z3 -> Z8: `Route115` -> `TerraCave_Entrance` (inert warp 1)
- Z3 -> Z8: `Route115` -> `TerraCave_Entrance` (inert warp 2)
- Z3 -> Z2: `Route116` -> `VerdanturfTown` (conn down)
- Z3 -> Z8: `Route116` -> `TerraCave_Entrance` (inert warp 3)
- Z3 -> Z8: `Route116` -> `TerraCave_Entrance` (inert warp 4)
- Z2 -> Z5: `Route118` -> `Route119` (conn up)
- Z2 -> Z5: `Route118` -> `Route123` (conn right)
- Z2 -> Z8: `Route118` -> `TerraCave_Entrance` (inert warp 0)
- Z2 -> Z8: `Route118` -> `TerraCave_Entrance` (inert warp 1)
- Z5 -> Z2: `Route119` -> `Route118` (conn down)
- Z5 -> Z2: `Route123` -> `Route118` (conn left)
- Z6 -> Z5: `Route124` -> `LilycoveCity` (conn left)
- Z6 -> Z7: `Route128` -> `EverGrandeCity` (conn right)
- Z6 -> Z1: `Route134` -> `SlateportCity` (conn left)
- Z3 -> Z2: `RusturfTunnel` -> `VerdanturfTown` (warp warp 1)
- Z1 -> Z2: `SlateportCity` -> `Route110` (conn up)
- Z1 -> Z6: `SlateportCity` -> `Route134` (conn right)
- Z1 -> Z8: `SlateportCity` -> `SlateportCity_BattleTentLobby` (warp warp 3)
- Z8 -> Z1: `SlateportCity_BattleTentLobby` -> `SlateportCity` (warp warp 0)
- Z8 -> Z1: `SlateportCity_BattleTentLobby` -> `SlateportCity` (warp warp 1)
- Z3 -> Z8: `Underwater_Route105` -> `Underwater_MarineCave` (warp warp 0)
- Z3 -> Z8: `Underwater_Route105` -> `Underwater_MarineCave` (warp warp 1)
- Z6 -> Z8: `Underwater_Route125` -> `Underwater_MarineCave` (warp warp 0)
- Z6 -> Z8: `Underwater_Route125` -> `Underwater_MarineCave` (warp warp 1)
- Z6 -> Z8: `Underwater_Route127` -> `Underwater_MarineCave` (warp warp 0)
- Z6 -> Z8: `Underwater_Route127` -> `Underwater_MarineCave` (warp warp 1)
- Z6 -> Z8: `Underwater_Route129` -> `Underwater_MarineCave` (warp warp 0)
- Z6 -> Z8: `Underwater_Route129` -> `Underwater_MarineCave` (warp warp 1)
- Z2 -> Z3: `VerdanturfTown` -> `Route116` (conn up)
- Z2 -> Z8: `VerdanturfTown` -> `VerdanturfTown_BattleTentLobby` (warp warp 0)
- Z2 -> Z3: `VerdanturfTown` -> `RusturfTunnel` (warp warp 4)
- Z8 -> Z2: `VerdanturfTown_BattleTentLobby` -> `VerdanturfTown` (warp warp 0)
- Z8 -> Z2: `VerdanturfTown_BattleTentLobby` -> `VerdanturfTown` (warp warp 1)

Maps per zone:

- Z1: AbandonedShip_CaptainsOffice, AbandonedShip_Corridors_1F, AbandonedShip_Corridors_B1F, AbandonedShip_Deck, AbandonedShip_HiddenFloorCorridors, AbandonedShip_HiddenFloorRooms, AbandonedShip_Room_B1F, AbandonedShip_Rooms2_1F, AbandonedShip_Rooms2_B1F, AbandonedShip_Rooms_1F, AbandonedShip_Rooms_B1F, AbandonedShip_Underwater1, AbandonedShip_Underwater2, DewfordTown, DewfordTown_Gym, DewfordTown_Hall, DewfordTown_House1, DewfordTown_House2, DewfordTown_PokemonCenter_1F, DewfordTown_PokemonCenter_2F, GraniteCave_1F, GraniteCave_B1F, GraniteCave_B2F, GraniteCave_StevensRoom, Route106, Route107, Route108, Route109, Route109_SeashoreHouse, SlateportCity, SlateportCity_Harbor, SlateportCity_House, SlateportCity_Mart, SlateportCity_NameRatersHouse, SlateportCity_OceanicMuseum_1F, SlateportCity_OceanicMuseum_2F, SlateportCity_PokemonCenter_1F, SlateportCity_PokemonCenter_2F, SlateportCity_PokemonFanClub, SlateportCity_SternsShipyard_1F, SlateportCity_SternsShipyard_2F
- Z2: MauvilleCity, MauvilleCity_BikeShop, MauvilleCity_GameCorner, MauvilleCity_Gym, MauvilleCity_House1, MauvilleCity_House2, MauvilleCity_Mart, MauvilleCity_PokemonCenter_1F, MauvilleCity_PokemonCenter_2F, NewMauville_Entrance, NewMauville_Inside, Route110, Route110_SeasideCyclingRoadNorthEntrance, Route110_SeasideCyclingRoadSouthEntrance, Route110_TrickHouseCorridor, Route110_TrickHouseEnd, Route110_TrickHouseEntrance, Route110_TrickHousePuzzle1, Route110_TrickHousePuzzle2, Route110_TrickHousePuzzle3, Route110_TrickHousePuzzle4, Route110_TrickHousePuzzle5, Route110_TrickHousePuzzle6, Route110_TrickHousePuzzle7, Route110_TrickHousePuzzle8, Route117, Route117_PokemonDayCare, Route118, VerdanturfTown, VerdanturfTown_FriendshipRatersHouse, VerdanturfTown_House, VerdanturfTown_Mart, VerdanturfTown_PokemonCenter_1F, VerdanturfTown_PokemonCenter_2F, VerdanturfTown_WandasHouse
- Z3: AlteringCave, LittlerootTown, LittlerootTown_BrendansHouse_1F, LittlerootTown_BrendansHouse_2F, LittlerootTown_MaysHouse_1F, LittlerootTown_MaysHouse_2F, LittlerootTown_ProfessorBirchsLab, OldaleTown, OldaleTown_House1, OldaleTown_House2, OldaleTown_Mart, OldaleTown_PokemonCenter_1F, OldaleTown_PokemonCenter_2F, PetalburgCity, PetalburgCity_Gym, PetalburgCity_House1, PetalburgCity_House2, PetalburgCity_Mart, PetalburgCity_PokemonCenter_1F, PetalburgCity_PokemonCenter_2F, PetalburgCity_WallysHouse, PetalburgWoods, Route101, Route102, Route103, Route104, Route104_MrBrineysHouse, Route104_PrettyPetalFlowerShop, Route105, Route115, Route116, Route116_TunnelersRestHouse, RustboroCity, RustboroCity_CuttersHouse, RustboroCity_DevonCorp_1F, RustboroCity_DevonCorp_2F, RustboroCity_DevonCorp_3F, RustboroCity_Flat1_1F, RustboroCity_Flat1_2F, RustboroCity_Flat2_1F, RustboroCity_Flat2_2F, RustboroCity_Flat2_3F, RustboroCity_Gym, RustboroCity_House1, RustboroCity_House2, RustboroCity_House3, RustboroCity_Mart, RustboroCity_PokemonCenter_1F, RustboroCity_PokemonCenter_2F, RustboroCity_PokemonSchool, RusturfTunnel, Underwater_Route105
- Z4: DesertRuins, DesertUnderpass, FallarborTown, FallarborTown_CozmosHouse, FallarborTown_Mart, FallarborTown_MoveRelearnersHouse, FallarborTown_PokemonCenter_1F, FallarborTown_PokemonCenter_2F, FieryPath, JaggedPass, LavaridgeTown, LavaridgeTown_Gym_1F, LavaridgeTown_Gym_B1F, LavaridgeTown_HerbShop, LavaridgeTown_House, LavaridgeTown_Mart, LavaridgeTown_PokemonCenter_1F, LavaridgeTown_PokemonCenter_2F, MagmaHideout_1F, MagmaHideout_2F_1R, MagmaHideout_2F_2R, MagmaHideout_2F_3R, MagmaHideout_3F_1R, MagmaHideout_3F_2R, MagmaHideout_3F_3R, MagmaHideout_4F, MeteorFalls_1F_1R, MeteorFalls_1F_2R, MeteorFalls_B1F_1R, MeteorFalls_B1F_2R, MeteorFalls_StevensCave, MirageTower_1F, MirageTower_2F, MirageTower_3F, MirageTower_4F, MtChimney, MtChimney_CableCarStation, Route111, Route111_OldLadysRestStop, Route111_WinstrateFamilysHouse, Route112, Route112_CableCarStation, Route113, Route113_GlassWorkshop, Route114, Route114_FossilManiacsHouse, Route114_FossilManiacsTunnel, Route114_LanettesHouse, TrainerHill_1F, TrainerHill_2F, TrainerHill_3F, TrainerHill_4F, TrainerHill_Elevator, TrainerHill_Entrance, TrainerHill_Roof
- Z5: AncientTomb, AquaHideout_1F, AquaHideout_B1F, AquaHideout_B2F, AquaHideout_UnusedRubyMap1, AquaHideout_UnusedRubyMap2, AquaHideout_UnusedRubyMap3, FortreeCity, FortreeCity_DecorationShop, FortreeCity_Gym, FortreeCity_House1, FortreeCity_House2, FortreeCity_House3, FortreeCity_House4, FortreeCity_House5, FortreeCity_Mart, FortreeCity_PokemonCenter_1F, FortreeCity_PokemonCenter_2F, HoennSafariZone_North, LilycoveCity, LilycoveCity_ContestHall, LilycoveCity_ContestLobby, LilycoveCity_CoveLilyMotel_1F, LilycoveCity_CoveLilyMotel_2F, LilycoveCity_DepartmentStoreElevator, LilycoveCity_DepartmentStoreRooftop, LilycoveCity_DepartmentStore_1F, LilycoveCity_DepartmentStore_2F, LilycoveCity_DepartmentStore_3F, LilycoveCity_DepartmentStore_4F, LilycoveCity_DepartmentStore_5F, LilycoveCity_Harbor, LilycoveCity_House1, LilycoveCity_House2, LilycoveCity_House3, LilycoveCity_House4, LilycoveCity_LilycoveMuseum_1F, LilycoveCity_LilycoveMuseum_2F, LilycoveCity_MoveDeletersHouse, LilycoveCity_PokemonCenter_1F, LilycoveCity_PokemonCenter_2F, LilycoveCity_PokemonTrainerFanClub, LilycoveCity_UnusedMart, MtPyre_1F, MtPyre_2F, MtPyre_3F, MtPyre_4F, MtPyre_5F, MtPyre_6F, MtPyre_Exterior, MtPyre_Summit, Route119, Route119_House, Route119_WeatherInstitute_1F, Route119_WeatherInstitute_2F, Route120, Route121, Route121_SafariZoneEntrance, Route122, Route123, Route123_BerryMastersHouse, SafariZone_Northeast, SafariZone_Northwest, SafariZone_RestHouse, SafariZone_South, SafariZone_Southeast, SafariZone_Southwest, ScorchedSlab
- Z6: CaveOfOrigin_1F, CaveOfOrigin_B1F, CaveOfOrigin_Entrance, CaveOfOrigin_UnusedRubySapphireMap1, CaveOfOrigin_UnusedRubySapphireMap2, CaveOfOrigin_UnusedRubySapphireMap3, IslandCave, MossdeepCity, MossdeepCity_GameCorner_1F, MossdeepCity_GameCorner_B1F, MossdeepCity_Gym, MossdeepCity_House1, MossdeepCity_House2, MossdeepCity_House3, MossdeepCity_House4, MossdeepCity_Mart, MossdeepCity_PokemonCenter_1F, MossdeepCity_PokemonCenter_2F, MossdeepCity_SpaceCenter_1F, MossdeepCity_SpaceCenter_2F, MossdeepCity_StevensHouse, PacifidlogTown, PacifidlogTown_House1, PacifidlogTown_House2, PacifidlogTown_House3, PacifidlogTown_House4, PacifidlogTown_House5, PacifidlogTown_PokemonCenter_1F, PacifidlogTown_PokemonCenter_2F, Route124, Route124_DivingTreasureHuntersHouse, Route125, Route126, Route127, Route128, Route129, Route130, Route131, Route132, Route133, Route134, SeafloorCavern_Entrance, SeafloorCavern_Room1, SeafloorCavern_Room2, SeafloorCavern_Room3, SeafloorCavern_Room4, SeafloorCavern_Room5, SeafloorCavern_Room6, SeafloorCavern_Room7, SeafloorCavern_Room8, SeafloorCavern_Room9, SealedChamber_InnerRoom, SealedChamber_OuterRoom, ShoalCave_HighTideEntranceRoom, ShoalCave_HighTideInnerRoom, ShoalCave_LowTideEntranceRoom, ShoalCave_LowTideIceRoom, ShoalCave_LowTideInnerRoom, ShoalCave_LowTideLowerRoom, ShoalCave_LowTideStairsRoom, SkyPillar_1F, SkyPillar_2F, SkyPillar_3F, SkyPillar_4F, SkyPillar_5F, SkyPillar_Entrance, SkyPillar_Outside, SkyPillar_Top, SootopolisCity, SootopolisCity_Gym_1F, SootopolisCity_Gym_B1F, SootopolisCity_House1, SootopolisCity_House2, SootopolisCity_House3, SootopolisCity_House4, SootopolisCity_House5, SootopolisCity_House6, SootopolisCity_House7, SootopolisCity_LotadAndSeedotHouse, SootopolisCity_Mart, SootopolisCity_MysteryEventsHouse_1F, SootopolisCity_MysteryEventsHouse_B1F, SootopolisCity_PokemonCenter_1F, SootopolisCity_PokemonCenter_2F, Underwater_Route124, Underwater_Route125, Underwater_Route126, Underwater_Route127, Underwater_Route128, Underwater_Route129, Underwater_Route134, Underwater_SeafloorCavern, Underwater_SealedChamber, Underwater_SootopolisCity
- Z7: EverGrandeCity, EverGrandeCity_ChampionsRoom, EverGrandeCity_DrakesRoom, EverGrandeCity_GlaciasRoom, EverGrandeCity_Hall1, EverGrandeCity_Hall2, EverGrandeCity_Hall3, EverGrandeCity_Hall4, EverGrandeCity_Hall5, EverGrandeCity_HallOfFame, EverGrandeCity_PhoebesRoom, EverGrandeCity_PokemonCenter_1F, EverGrandeCity_PokemonCenter_2F, EverGrandeCity_PokemonLeague_1F, EverGrandeCity_PokemonLeague_2F, EverGrandeCity_SidneysRoom, HoennVictoryRoad_1F, VictoryRoad_B1F, VictoryRoad_B2F
- Z8: ArtisanCave_1F, ArtisanCave_B1F, BattleFrontier_BattleArenaBattleRoom, BattleFrontier_BattleArenaCorridor, BattleFrontier_BattleArenaLobby, BattleFrontier_BattleDomeBattleRoom, BattleFrontier_BattleDomeCorridor, BattleFrontier_BattleDomeLobby, BattleFrontier_BattleDomePreBattleRoom, BattleFrontier_BattleFactoryBattleRoom, BattleFrontier_BattleFactoryLobby, BattleFrontier_BattleFactoryPreBattleRoom, BattleFrontier_BattlePalaceBattleRoom, BattleFrontier_BattlePalaceCorridor, BattleFrontier_BattlePalaceLobby, BattleFrontier_BattlePikeCorridor, BattleFrontier_BattlePikeLobby, BattleFrontier_BattlePikeRoomFinal, BattleFrontier_BattlePikeRoomNormal, BattleFrontier_BattlePikeRoomWildMons, BattleFrontier_BattlePikeThreePathRoom, BattleFrontier_BattlePyramidFloor, BattleFrontier_BattlePyramidLobby, BattleFrontier_BattlePyramidTop, BattleFrontier_BattleTowerBattleRoom, BattleFrontier_BattleTowerCorridor, BattleFrontier_BattleTowerElevator, BattleFrontier_BattleTowerLobby, BattleFrontier_BattleTowerMultiBattleRoom, BattleFrontier_BattleTowerMultiCorridor, BattleFrontier_BattleTowerMultiPartnerRoom, BattleFrontier_ExchangeServiceCorner, BattleFrontier_Lounge1, BattleFrontier_Lounge2, BattleFrontier_Lounge3, BattleFrontier_Lounge4, BattleFrontier_Lounge5, BattleFrontier_Lounge6, BattleFrontier_Lounge7, BattleFrontier_Lounge8, BattleFrontier_Lounge9, BattleFrontier_Mart, BattleFrontier_OutsideEast, BattleFrontier_OutsideWest, BattleFrontier_PokemonCenter_1F, BattleFrontier_PokemonCenter_2F, BattleFrontier_RankingHall, BattleFrontier_ReceptionGate, BattleFrontier_ScottsHouse, BattlePyramidSquare01, BattlePyramidSquare02, BattlePyramidSquare03, BattlePyramidSquare04, BattlePyramidSquare05, BattlePyramidSquare06, BattlePyramidSquare07, BattlePyramidSquare08, BattlePyramidSquare09, BattlePyramidSquare10, BattlePyramidSquare11, BattlePyramidSquare12, BattlePyramidSquare13, BattlePyramidSquare14, BattlePyramidSquare15, BattlePyramidSquare16, ContestHall, ContestHallBeauty, ContestHallCool, ContestHallCute, ContestHallSmart, ContestHallTough, FallarborTown_BattleTentBattleRoom, FallarborTown_BattleTentCorridor, FallarborTown_BattleTentLobby, FarawayIsland_Entrance, FarawayIsland_Interior, InsideOfTruck, MarineCave_End, MarineCave_Entrance, SSTidalCorridor, SSTidalLowerDeck, SSTidalRooms, SlateportCity_BattleTentBattleRoom, SlateportCity_BattleTentCorridor, SlateportCity_BattleTentLobby, SouthernIsland_Exterior, SouthernIsland_Interior, TerraCave_End, TerraCave_Entrance, Underwater_MarineCave, VerdanturfTown_BattleTentBattleRoom, VerdanturfTown_BattleTentCorridor, VerdanturfTown_BattleTentLobby

## 부록 C. 무결성 검사 출력

`python3 tools/check_map_integrity.py --limit 12 --no-fail`의 출력(수준·절마다 12줄까지). 전체는 `--limit 0`.

### check_map_integrity: 125 ERROR, 0 WARN, 290 INFO

#### warps (INFO 85)

- INFO: SeafoamIslands_B3F warp 5 -> SeafoamIslands_B2F warp 7, which leads to MAP_SEAFOAM_ISLANDS_B1F (not back)
- INFO: SeafoamIslands_B3F warp 6 -> SeafoamIslands_B2F warp 8, which leads to MAP_SEAFOAM_ISLANDS_B1F (not back)
- INFO: SixIsland_DottedHole_B2F warp 1 -> SixIsland_DottedHole_1F warp 3, which leads to MAP_SIX_ISLAND_DOTTED_HOLE_B1F (not back)
- INFO: SixIsland_DottedHole_B2F warp 2 -> SixIsland_DottedHole_1F warp 3, which leads to MAP_SIX_ISLAND_DOTTED_HOLE_B1F (not back)
- INFO: SixIsland_DottedHole_B2F warp 3 -> SixIsland_DottedHole_1F warp 3, which leads to MAP_SIX_ISLAND_DOTTED_HOLE_B1F (not back)
- INFO: SixIsland_DottedHole_B3F warp 1 -> SixIsland_DottedHole_1F warp 3, which leads to MAP_SIX_ISLAND_DOTTED_HOLE_B1F (not back)
- INFO: SixIsland_DottedHole_B3F warp 3 -> SixIsland_DottedHole_1F warp 3, which leads to MAP_SIX_ISLAND_DOTTED_HOLE_B1F (not back)
- INFO: SixIsland_DottedHole_B3F warp 4 -> SixIsland_DottedHole_1F warp 3, which leads to MAP_SIX_ISLAND_DOTTED_HOLE_B1F (not back)
- INFO: SixIsland_DottedHole_B4F warp 1 -> SixIsland_DottedHole_1F warp 3, which leads to MAP_SIX_ISLAND_DOTTED_HOLE_B1F (not back)
- INFO: SixIsland_DottedHole_B4F warp 2 -> SixIsland_DottedHole_1F warp 3, which leads to MAP_SIX_ISLAND_DOTTED_HOLE_B1F (not back)
- INFO: SixIsland_DottedHole_B4F warp 4 -> SixIsland_DottedHole_1F warp 3, which leads to MAP_SIX_ISLAND_DOTTED_HOLE_B1F (not back)
- INFO: FiveIsland_LostCave_Room1 warp 4 -> FiveIsland_LostCave_Room1 warp 2, which leads to MAP_FIVE_ISLAND_LOST_CAVE_ROOM2 (not back)
- INFO: ... 73 more (use --limit 0)

#### inert warps (INFO 190, NOTE 1)

- INFO: Hoenn AbandonedShip_HiddenFloorCorridors: 0->ABANDONED_SHIP_HIDDEN_FLOOR_ROOMS [MB_NORMAL], 1->ABANDONED_SHIP_HIDDEN_FLOOR_ROOMS [MB_NORMAL], 3->ABANDONED_SHIP_HIDDEN_FLOOR_ROOMS [MB_INDOOR_ENCOUNTER], 5->ABANDONED_SHIP_HIDDEN_FLOOR_ROOMS [MB_INDOOR_ENCOUNTER]
- INFO: Hoenn AquaHideout_1F: 1->LILYCOVE_CITY [MB_OCEAN_WATER]
- INFO: Hoenn BattleFrontier_BattlePalaceBattleRoom: 0->BATTLE_FRONTIER_BATTLE_PALACE_CORRIDOR [MB_NORMAL], 1->BATTLE_FRONTIER_BATTLE_PALACE_CORRIDOR [MB_NORMAL]
- INFO: Hoenn BattleFrontier_BattleTowerBattleRoom: 1->BATTLE_FRONTIER_BATTLE_TOWER_LOBBY [MB_NORMAL]
- INFO: Hoenn BattleFrontier_Lounge9: 0->BATTLE_FRONTIER_OUTSIDE_EAST [MB_NORMAL], 1->BATTLE_FRONTIER_OUTSIDE_EAST [MB_NORMAL]
- INFO: Hoenn BattleFrontier_OutsideEast: 11->BATTLE_FRONTIER_LOUNGE9 [MB_NORMAL]
- INFO: Kanto CeladonCity: 10->CELADON_CITY_CONDOMINIUMS_1F [MB_NORMAL], 12->CELADON_CITY_CONDOMINIUMS_1F [MB_NORMAL]
- INFO: Kanto CeladonCity_Condominiums_1F: 0->CELADON_CITY [MB_NORMAL], 2->CELADON_CITY [MB_NORMAL]
- INFO: Kanto CeladonCity_Condominiums_RoofRoom: 0->CELADON_CITY_CONDOMINIUMS_ROOF [MB_NORMAL], 2->CELADON_CITY_CONDOMINIUMS_ROOF [MB_NORMAL]
- INFO: Kanto CeladonCity_DepartmentStore_1F: 0->CELADON_CITY [MB_NORMAL], 2->CELADON_CITY [MB_NORMAL], 3->CELADON_CITY [MB_NORMAL], 5->CELADON_CITY [MB_NORMAL]
- INFO: Kanto CeladonCity_DepartmentStore_Elevator: 1->DYNAMIC [MB_NORMAL]
- INFO: Kanto CeladonCity_GameCorner: 1->CELADON_CITY [MB_NORMAL], 2->CELADON_CITY [MB_NORMAL]
- INFO: ... 178 more (use --limit 0)
- NOTE: warp events on a non-warp tile: 389 on 190 maps (Hoenn 121); most are arrival-only spots or entrances a script opens

#### connections (INFO 8)

- INFO: SaffronCity --up--> Route5: Route5 has no down connection back (same in upstream)
- INFO: SaffronCity --down--> Route6: Route6 has no up connection back (same in upstream)
- INFO: SaffronCity --left--> Route7: Route7 has no right connection back (same in upstream)
- INFO: SaffronCity --right--> Route8: Route8 has no left connection back (same in upstream)
- INFO: SaffronCity_Connection --down offset 12--> Route6: back offset 0 (expected -12) (same in upstream)
- INFO: Route6 --up offset 0--> SaffronCity_Connection: back offset 12 (expected 0) (same in upstream)
- INFO: Prototype_SeviiIsle_6 --up--> ThreeIsland: ThreeIsland has no down connection back (same in upstream)
- INFO: Prototype_SeviiIsle_7 --up--> ThreeIsland: ThreeIsland has no down connection back (same in upstream)

#### flag numbers (ERROR 110, NOTE 2)

- ERROR: 0x4A7: "free" FLAG_UNUSED_0x4A7 is in use by FLAG_HOENN_HIDDEN_0 -- FLAG_UNUSED_0x4A7 (flags.h:1225), FLAG_HOENN_HIDDEN_0 (flags_hoenn.h:170)
- ERROR: 0x4A8: "free" FLAG_UNUSED_0x4A8 is in use by FLAG_HOENN_HIDDEN_1 -- FLAG_UNUSED_0x4A8 (flags.h:1226), FLAG_HOENN_HIDDEN_1 (flags_hoenn.h:171)
- ERROR: 0x4A9: "free" FLAG_UNUSED_0x4A9 is in use by FLAG_HOENN_HIDDEN_2 -- FLAG_UNUSED_0x4A9 (flags.h:1227), FLAG_HOENN_HIDDEN_2 (flags_hoenn.h:172)
- ERROR: 0x4AA: "free" FLAG_UNUSED_0x4AA is in use by FLAG_HOENN_HIDDEN_3 -- FLAG_UNUSED_0x4AA (flags.h:1228), FLAG_HOENN_HIDDEN_3 (flags_hoenn.h:173)
- ERROR: 0x4AB: "free" FLAG_UNUSED_0x4AB is in use by FLAG_HOENN_HIDDEN_4 -- FLAG_UNUSED_0x4AB (flags.h:1229), FLAG_HOENN_HIDDEN_4 (flags_hoenn.h:174)
- ERROR: 0x4AC: "free" FLAG_UNUSED_0x4AC is in use by FLAG_HOENN_HIDDEN_5 -- FLAG_UNUSED_0x4AC (flags.h:1230), FLAG_HOENN_HIDDEN_5 (flags_hoenn.h:175)
- ERROR: 0x4AD: "free" FLAG_UNUSED_0x4AD is in use by FLAG_HOENN_HIDDEN_6 -- FLAG_UNUSED_0x4AD (flags.h:1231), FLAG_HOENN_HIDDEN_6 (flags_hoenn.h:176)
- ERROR: 0x4AE: "free" FLAG_UNUSED_0x4AE is in use by FLAG_HOENN_HIDDEN_7 -- FLAG_UNUSED_0x4AE (flags.h:1232), FLAG_HOENN_HIDDEN_7 (flags_hoenn.h:177)
- ERROR: 0x4AF: "free" FLAG_UNUSED_0x4AF is in use by FLAG_HOENN_HIDDEN_8 -- FLAG_UNUSED_0x4AF (flags.h:1233), FLAG_HOENN_HIDDEN_8 (flags_hoenn.h:178)
- ERROR: 0x4B0: FLAG_DEFEATED_BROCK (flags.h:1236), FLAG_HOENN_HIDDEN_9 (flags_hoenn.h:179)
- ERROR: 0x4B1: FLAG_DEFEATED_MISTY (flags.h:1237), FLAG_HOENN_HIDDEN_10 (flags_hoenn.h:180)
- ERROR: 0x4B2: FLAG_DEFEATED_LT_SURGE (flags.h:1238), FLAG_HOENN_HIDDEN_11 (flags_hoenn.h:181)
- ERROR: ... 98 more (use --limit 0)
- NOTE: flags named free (FLAG_0x*/FLAG_UNUSED_*) that nothing else shares: 464
- NOTE: hoennFlags: 180 named Hoenn-block flags, highest offset 0x411 of 0x800

#### var numbers (NOTE 1)

- NOTE: save vars named free (VAR_0x40xx) that nothing else shares: 56

#### object/hidden-item flags (INFO 7)

- INFO: ['FLAG_HIDE_MISC_KANTO_ROCKETS'] on 5 maps (as upstream): MtMoon_B2F, RocketHideout_B1F, RocketHideout_B2F, RocketHideout_B3F, RocketHideout_B4F
- INFO: ['FLAG_HIDE_SAFFRON_CIVILIANS'] on 2 maps (as upstream): SaffronCity, SilphCo_1F
- INFO: ['FLAG_HIDE_SILPH_ROCKETS'] on 10 maps (as upstream): SilphCo_10F, SilphCo_11F, SilphCo_2F, SilphCo_3F, SilphCo_4F, SilphCo_5F, SilphCo_6F, SilphCo_7F, SilphCo_8F, SilphCo_9F
- INFO: ['FLAG_HIDE_FIVE_ISLAND_ROCKETS'] on 3 maps (as upstream): FiveIsland_Meadow, FiveIsland_RocketWarehouse, SixIsland_OutcastIsland
- INFO: ['FLAG_HIDE_POSTGAME_GOSSIPERS'] on 11 maps (as upstream): CeladonCity_DepartmentStore_2F, CeruleanCity_PokemonCenter_1F, CinnabarIsland_PokemonCenter_1F, FiveIsland_PokemonCenter_1F, FuchsiaCity, IndigoPlateau_PokemonCenter_1F, LavenderTown_PokemonCenter_1F, OneIsland_KindleRoad_EmberSpa, SaffronCity, SaffronCity_PokemonTrainerFanClub, SevenIsland_PokemonCenter_1F
- INFO: ['FLAG_HIDE_THREE_ISLAND_BIKERS'] on 2 maps (as upstream): ThreeIsland, ThreeIsland_Port
- INFO: ['FLAG_HIDE_MG_DELIVERYMEN'] on 19 maps (as upstream): CeladonCity_PokemonCenter_2F, CeruleanCity_PokemonCenter_2F, CinnabarIsland_PokemonCenter_2F, FiveIsland_PokemonCenter_2F, FourIsland_PokemonCenter_2F, FuchsiaCity_PokemonCenter_2F, IndigoPlateau_PokemonCenter_2F, LavenderTown_PokemonCenter_2F, OneIsland_PokemonCenter_2F, PewterCity_PokemonCenter_2F, Route10_PokemonCenter_2F, Route4_PokemonCenter_2F, SaffronCity_PokemonCenter_2F, SevenIsland_PokemonCenter_2F, SixIsland_PokemonCenter_2F, ThreeIsland_PokemonCenter_2F, TwoIsland_PokemonCenter_2F, VermilionCity_PokemonCenter_2F, ViridianCity_PokemonCenter_2F

#### movement types (ERROR 15, NOTE 1)

- ERROR: Route102: 2 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 7@(24,2), 8@(25,2)
- ERROR: Route103: 3 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 6@(58,5), 7@(59,5), 8@(60,5)
- ERROR: Route104: 10 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 8@(34,6), 9@(35,6), 10@(36,6), 11@(22,41), 12@(23,41), 13@(24,41), 15@(3,22), 16@(3,23), 17@(3,24), 18@(3,25)
- ERROR: Route110: 3 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 16@(5,11), 17@(6,11), 18@(7,11)
- ERROR: Route111: 4 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 2@(22,5), 3@(23,5), 11@(18,5), 12@(19,5)
- ERROR: Route112: 4 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 5@(27,6), 6@(28,6), 7@(29,6), 8@(30,6)
- ERROR: Route114: 3 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 1@(31,43), 2@(31,44), 8@(31,45)
- ERROR: Route115: 5 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 4@(12,5), 5@(13,5), 6@(14,5), 13@(31,64), 14@(31,65)
- ERROR: Route116: 4 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 1@(18,2), 2@(19,2), 7@(20,2), 8@(21,2)
- ERROR: Route117: 3 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 11@(41,13), 12@(42,13), 13@(43,13)
- ERROR: Route118: 3 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 1@(35,5), 2@(36,5), 3@(37,5)
- ERROR: Route119: 7 object(s) with MOVEMENT_TYPE_BERRY_TREE_GROWTH (NULL callback): 1@(24,5), 2@(25,5), 3@(26,5), 23@(8,23), 24@(9,23), 25@(29,90), 26@(30,90)
- ERROR: ... 3 more (use --limit 0)
- NOTE: NULL callbacks: MOVEMENT_TYPE_BERRY_TREE_GROWTH; objects using them: 87

#### trainers (NOTE 2)

- NOTE: Hoenn trainers: 520 ids, highest offset 519, hoennTrainerFlags holds 1024 bits (504 free after the last)
- NOTE: FR/LG trainers: NUM_TRAINERS 753 of MAX_TRAINERS_COUNT 768 (15 free)

#### layouts/groups (NOTE 1)

- NOTE: 890 maps in 76 groups, 731 layouts
