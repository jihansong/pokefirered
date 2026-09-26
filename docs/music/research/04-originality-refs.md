# 04. 독창성 참조 목록: 큐마다 닮으면 안 되는 곡

- 작성: 음악 리서처, 2026-09-26. 음악 감독 브리프 4번 항목
- 용도: 검수자가 새 곡을 비교할 때 쓰는 목록이다. **이름만 적는다.** 선율·악보는 옮기지 않는다
- 표기
  - `mus_*`는 저장소에 MIDI가 있어 기계 비교가 된다(`sound/songs/midi/`)
  - 나머지(GB·NDS·애니 곡)는 저장소에 없으므로 귀로 비교한다. 이 파일들을 저장소에 들이지 않는다
- 원칙(감독 지침): 선율, 베이스 라인, 특징적 리프 어느 것도 빌리지 않는다. 스타일(악기 편성·템포·화성 관습)만 참고한다

## 1. 공통(모든 큐)

- 시리즈 대표 선율: 포켓몬 메인 테마(타이틀·오프닝 계열, `mus_title`, `mus_intro_fight`, 레드·그린 오프닝), 포켓몬센터(`mus_poke_center`), 전당(`mus_hall_of_fame`), 1번 도로(`mus_route1`), 태초마을(`mus_pallet`), 트레이너 조우 3종(`mus_encounter_boy`/`girl`/`rival`), 전투 3종(`mus_vs_wild`/`trainer`/`gym_leader`), 승리 팡파르 3종(`mus_victory_*`), 게임프리크 징글(`mus_game_freak`)
- 애니 주제가(1기~AG): 「めざせポケモンマスター」(1기 오프닝), 영어판 "Pokémon Theme"(Gotta Catch 'Em All), 「ひゃくごじゅういち」·「ポケモンいえるかな?」(1기 엔딩), AG 오프닝 「アドバンス・アドベンチャー」, 영어판 "Unbeatable", 성도편 영어 오프닝 "Pokémon Johto"
- 다른 게임의 유명 곡: 특히 게임·애니 음악 전반의 "모험·승리" 클리셰 선율. 검수자가 귀로 판단한다

## 2. 큐별 목록

| 큐 | 같은 장면을 떠올리게 하는 원작 곡 | 주변 곡(앞뒤로 들리는 곡) | 애니·기타 |
|---|---|---|---|
| R1 트리오 등장 | `mus_encounter_rocket`(현재 곡), 적/수상한 트레이너 시선 곡(레드·그린·옐로), 금·은·크리스탈과 HGSS 로켓단 조우, R/S/E 아쿠아·마그마단 조우 | `mus_rocket_hideout`, `mus_silph`, `mus_game_corner`, `mus_poke_center`, `mus_gym`, `mus_mt_moon`, `mus_ss_anne`, `mus_poke_tower`, `mus_fuchsia`, `mus_cinnabar`, `mus_victory_road`, `mus_poke_mansion`, `mus_vermillion`, `mus_petalburg_woods` | 애니 1기 로켓단 등장(모토) BGM, 로켓단 이미지송 「ロケット団よ永遠に」, 영어판 "Double Trouble" |
| R2 트리오 전투 | `mus_vs_trainer`(현재 곡), `mus_rs_vs_trainer`, 금·은 로켓단 전투, R/S/E 아쿠아·마그마단 전투(`MUS_VS_AQUA_MAGMA`, 미이식), 사카키 전투(`mus_vs_gym_leader` 계열) | `mus_victory_trainer`, R1 | 위와 같음 |
| R3 퇴장 징글 | `mus_too_bad`, `mus_slots_win`, `mus_level_up` | R1, 맵 음악 | 애니 "やなかんじ~" 장면의 효과음·BGM |
| P1 피카츄 동료 팡파르 | `mus_obtain_key_item`(현재 곡), `mus_obtain_item`, `mus_caught`, `mus_evolved`, `mus_obtain_badge` | `mus_oak_lab`, `mus_oak`, `mus_encounter_rival` | 애니 1기 오프닝·엔딩 전부, 피카츄 관련 캐릭터송, 「Let's Go! 피카츄·이브이」 주제곡 |
| P2 볼트태클 | `mus_poke_mansion`(현재 맵 곡), `mus_vs_legend`(썬더 전) | `mus_encounter_gym_leader` | 애니 10만볼트 장면 BGM |
| P3 파도타기 피카츄 | 옐로 「피카츄의 해변」(파도타기 피카츄 미니게임 곡), 포켓몬스타디움 서핑 피카츄, `mus_surf`, `mus_route3`(19번 도로 맵 곡) | `mus_surf` | — |
| O1 오 박사전 | `mus_vs_champion`(현재 곡), `mus_oak`, `mus_oak_lab`, 레드·그린 챔피언전 | `mus_victory_gym_leader` | — |
| S1 은빛산 던전 | 금·은·HGSS 은빛산 관련 곡(동굴·정상), `mus_mt_moon`/`mus_sevii_cave`(현재 곡), `mus_victory_road`, `mus_sealed_chamber` | `mus_poke_center` | — |
| S2 은빛산 정상 전투 | 금·은·HGSS의 레드 대결 곡, `mus_vs_champion`, `mus_vs_trainer`(현재 곡) | S1 | — |
| N1·N2 N 테마 | 블랙·화이트의 N 관련 곡 전부(N의 테마, N의 방, N의 성, 대결! N) | `mus_pewter`, `mus_poke_tower`, `mus_silph`, `mus_fuchsia`, `mus_gym` | — |
| A1 공항 | `mus_net_center`(현재 곡), `mus_poke_center`, `mus_ss_anne`, `MUS_SAILING`(`mus_sailing`), `mus_slateport`(도착지) | `mus_vermillion`(출발지) | — |
| A2 비행 장면 | `mus_sailing`, `mus_surf`, `mus_cycling`, `mus_route24`, 금·은 자석열차 관련 곡 | `mus_net_center`→`mus_slateport` | AG 오프닝(지역을 건너는 이미지) |
| T1·T2 토너먼트 | `mus_gym`(현재 곡), `mus_trainer_tower`, `mus_b_dome`/`mus_b_dome_lobby`(배틀돔 토너먼트), `mus_b_tower`, `mus_b_frontier`, 포켓몬스타디움 토너먼트 곡, 콜로세움 경기장 곡 | `mus_vs_gym_leader`, `mus_vs_champion`, `mus_obtain_badge` | 애니 1기 포켓몬 리그편 |
| SN 스내그 징글 | 포켓몬 콜로세움·XD의 스내그 성공 징글, `mus_caught`/`mus_caught_intro`(현재 계획 곡) | `mus_vs_trainer` 등 전투곡 | — |
| NI 새 섬 | `mus_poke_mansion`(현재 곡), `mus_vs_mewtwo` | R1 | 극장판 「ミュウツーの逆襲」 BGM과 주제가 「風といっしょに」 |
| GC 글리치 시티 | `mus_fuchsia`(현재 곡), `mus_teachy_tv_menu`(노이즈) | — | — |
| C1 칸토 엔딩 | `mus_credits`(현재 곡), `mus_hall_of_fame`, 레드·그린·옐로 엔딩, `mus_title` | `mus_hall_of_fame`(바로 앞) | 애니 1기 엔딩 전부, 「めざせポケモンマスター」 |
| C2 성도 엔딩 | 금·은·크리스탈 엔딩, HGSS 엔딩 | 성도 전당 | 성도편 오프닝·엔딩 |
| C3 호연 엔딩 | 에메랄드 엔딩(`MUS_END`, `MUS_THANKFOR`, 미이식), `mus_hall_of_fame_room` | `mus_hall_of_fame_room` | AG 오프닝·엔딩 |
| OP 오프닝 | `mus_intro_fight`(현재 곡), `mus_game_freak`, `mus_title`, 레드·그린 오프닝 | `mus_title` | 「めざせポケモンマスター」, "Pokémon Theme" |

## 3. 검수 방법 제안

1. **기계 비교(저장소 안 곡)**: `mus_*` 141곡의 MIDI에서 트랙별 "음정 간격 + 길이 비율" n-그램(예: 6음)을 뽑는다. 새 곡의 멜로디·베이스 트랙과 겹치는 비율을 잰다. 곡 전체가 아니라 **8마디 창** 단위로 본다.
   - 조를 옮겨도 잡히도록 음정 간격을 쓴다.
   - 리듬만 같은 흔한 음형은 제외하도록 길이 비율을 같이 쓴다.
   - `analyze.py`의 파서를 그대로 쓸 수 있다. 결과는 곡 이름과 마디 번호만 보고한다.
2. **귀 비교(저장소 밖 곡)**: 위 표의 애니·GB·NDS 곡은 파일을 들이지 않는다. 검수자와 사용자가 기억과 공개 음원으로 판단한다.
3. **모티프 집합 안의 재사용은 허용**: 감독이 정한 썬더옐로우 모티프(피카츄·로켓 트리오·지역 횡단)를 우리 곡끼리 재사용하는 것은 독창성 위반이 아니다. 기계 비교 때 "허용 목록"으로 뺀다.
