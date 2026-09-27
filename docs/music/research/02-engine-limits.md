# 02. 엔진 제약: m4a, mid2agb, 곡 표, ROM 여유

- 작성: 음악 리서처, 2026-09-26. 음악 감독 브리프 2번 항목
- 모든 수치는 저장소 파일에서 확인했다. 경로:줄 번호를 같이 적는다

## 1. 빌드 흐름

1. `sound/songs/midi/<곡>.mid`(git에 올림) + `sound/songs/midi/midi.cfg`의 한 줄
2. `audio_rules.mk:27-41`이 cfg 줄마다 `mid2agb <곡>.mid <곡>.s <옵션>` 규칙을 만든다. `.s`는 생성물이다(`.gitignore:47`). cfg에 줄이 없으면 경고만 나오고 링크 단계에서 실패한다(`audio_rules.mk:44-45`)
3. `.s` → `.o` → `ld_script.ld`가 곡 오브젝트를 명시적으로 배치한다. 에메랄드 곡은 `/* BEGIN HOENN MUSIC */` 블록 안에 있다(`ld_script.ld:973-1023`). `ld_script_modern.ld`에는 곡 목록이 없다
4. `sound/song_table.inc`의 `gSongTable` 순서가 곡 번호다. `include/constants/songs.h`의 `MUS_*` 값과 순서가 맞아야 한다

## 2. midi.cfg 옵션(`tools/mid2agb/main.cpp:53-60, 145-185`)

| 옵션 | 뜻 | 저장소 관례 |
|---|---|---|
| `-E` | 정확한 게이트 타임 | 모든 BGM이 쓴다 |
| `-R<n>` | 리버브. `reverb_set+n`으로 곡 헤더에 들어간다(`agb.cpp:58-61`) | 140/141곡이 `-R50`, mus_dummy만 `-R40`. **새 곡도 `-R50`** |
| `-G<n>` 또는 `-G_<이름>` | voicegroup. 숫자는 `voicegroup%03u`(FR/LG), `_이름`은 `voicegroup_<이름>`(에메랄드). 이 해킹에서 mid2agb를 고쳐 둘 다 받는다(`agb.cpp:49-55`) | 곡마다 다름 |
| `-V<n>` | 마스터 음량(0~127). 트랙 VOL에 `n/127`을 곱한다(`agb.cpp:363`) | 중앙값 90, 범위 48~105. 필드곡 79~100, 전투 90, 에메랄드 이식곡 80 전후 |
| `-P<n>` | 곡 우선순위 | BGM은 비움(0). 팡파르 `-P5`, 진화 `-P1`, 효과음 `-P2~5` |
| `-X` | 48클럭/박 | 쓰는 곡 없음. **쓰지 말 것**(24틱/4분음표 관례) |
| `-N` | 압축 끔 | 쓰는 곡 없음 |
| `-L` | 어셈블러 라벨 | 파일 이름을 쓴다(기본값) |

## 3. MIDI에서 쓸 수 있는 것(`tools/mid2agb/midi.cpp`, `agb.cpp`)

- 해상도: **24틱/4분음표**(모든 곡). 96틱이 온음표, 한 마디다
- 템포: 메타 0x51. m4a 헤더에는 `TEMPO , bpm*tbs/2`로 들어간다. 엔진은 **프레임당 bpm/150틱**으로 진행한다(`docs/anim/opening-storyboard.md:66`에 188 BPM 곡으로 실측 검증됨). 그래서 곡 길이(프레임) = 틱 × 150 / BPM이다
- 루프: 텍스트/마커 메타 이벤트 `[`(루프 시작), `]`(끝, 시작으로 GOTO), `][`(끝+새 시작), `:`(라벨)(`midi.cpp:287-294`). **모든 트랙이 같은 `[`/`]` 틱을 공유**한다. 1회 재생곡은 마커 없이 끝나며 FINE이 붙는다
- 컨트롤러: CC1 MOD(비브라토 깊이), CC7 VOL, CC10 PAN, CC20 BENDR(벤드 범위), CC21 LFOS(LFO 속도), CC22 MODT(비브라토 종류), CC24 TUNE, CC26 LFODL(LFO 지연), CC33/39 PRIO, CC30+CC29/31 확장 명령(xIECV/xIECL, 에코), CC12/16+13~15 메모리 조작(`agb.cpp:355-420`). 피치 벤드와 프로그램 체인지도 된다
- **쓸 수 없는 것**: 트랙 중간의 템포 곡선 외 자동화, 샘플 시작 오프셋, 필터·EQ, 곡 안에서 voicegroup 바꾸기(곡당 voicegroup 1개)
- 박자표: 마디 경계 표시(`WholeNoteMark`) 용도. 1/4, 2/8 같은 짧은 마디를 넣어 끝 박을 맞추는 곡이 많다

## 4. 채널과 트랙 상한

| 제약 | 값 | 근거 |
|---|---|---|
| BGM 플레이어 트랙 수 | **10** | `sound/music_player_table.inc:2` `NUM_TRACKS_BGM, 10`. 곡에 트랙이 더 있어도 10개까지만 재생된다 |
| 엔진 절대 상한 | 16 | `include/gba/m4a_internal.h:318` `MAX_MUSICPLAYER_TRACKS 16`(`src/m4a.c:572`) |
| 효과음 플레이어 | SE1 3트랙, SE2 9트랙, SE3 1트랙 | `music_player_table.inc:3-5` |
| 울음소리 플레이어 | 2개(각 2트랙) | `m4a_internal.h:377` `MAX_POKEMON_CRIES 2` |
| **DirectSound(샘플) 동시 발음 수** | **5** | `src/m4a.c:78-81` `m4aSoundInit`이 `5 << SOUND_MODE_MAXCHN_SHIFT`. 버퍼는 12개까지 있지만(`MAX_DIRECTSOUND_CHANNELS 12`) 이 게임은 5로 쓴다 |
| 샘플 믹싱 | 13,379 Hz, 8비트 DA, 마스터 12/15 | `src/m4a.c:78-81` |
| PSG(CGB) 채널 | 사각파1(스윕), 사각파2, 웨이브, 노이즈 각 1음 | GBA 하드웨어. 같은 종류를 쓰는 트랙끼리는 한 번에 한 음만 소리 난다 |

### 4.1 원곡들이 지키는 실제 한도(측정)

- 음표 있는 트랙: 최대 10(24곡이 정확히 10). 분포: 10트랙 24곡, 9트랙 32곡, 8트랙 33곡, 7트랙 26곡
- 동시에 눌린 샘플 음(DS)의 최대치(`max_held_ds`): 4가 70곡, 5가 61곡. 5음 제한에 눌린 음이 잘리는 곡(`held_ds_steals` > 0)이 11곡 있다: credits, hall_of_fame, intro_fight, vermillion, route104, sevii_route, mt_pyre_exterior, b_dome, b_palace, caught_intro, new_game_exit. 측정은 `tools/music/songinfo.py --all`로 했다
- 전투곡(vs_trainer, vs_gym_leader, vs_champion)도 샘플 동시음 5, 트랙 10이다. **전투 화면에서 이 수치가 돌아간다는 것이 실측 근거다.** 여기서 더 늘리면 안 된다
- **검수 기준(채택, 2026-09-26 프로듀서)**: 트랙 ≤ 9, `max_held_ds ≤ 4`, `held_ds_steals = 0`. 1트랙과 샘플 1음을 효과음과 울음소리 몫으로 남긴다. `python3 tools/music/songinfo.py mus_<곡>`이 이 기준을 검사한다(실패하면 종료 코드 1, 팡파르는 `--one-shot`). 화음 패드는 샘플 대신 PSG나 짧은 샘플 스택으로 만든다

### 4.2 무거운 화면

- **전투**: 기술 효과음(`-P4~5`)과 울음소리가 같은 샘플 채널 5개를 나눠 쓴다. BGM은 우선순위 0이라 가장 먼저 빼앗긴다. 배경 화음을 샘플로 길게 끌면 효과음 때 뚝 끊긴다. 전투곡의 긴 음은 PSG(사각파·웨이브)에 두는 편이 원곡 관례다(전투곡 PSG 트랙 평균 4.8개로 장르 중 최다)
- **인트로/오프닝**: 원판 `MUS_INTRO_FIGHT`는 8트랙, 샘플 동시음 5~6, 12.1초 1회 재생이다(727→1455프레임 실측, `docs/anim/opening-storyboard.md:43,57,66`). 장면 전환 효과음(`SE_SHINY`)과 피카츄 울음(1187프레임 부근 계획)이 겹친다
- **CPU**: 믹서 비용은 동시 샘플 채널 수(최대 5로 고정)와 샘플레이트에 비례한다. 이 두 값이 전역으로 고정이므로 새 곡이 CPU를 더 쓰게 만들 방법은 사실상 트랙 수(시퀀서 처리)뿐이다. 10트랙 이하면 원곡과 같은 부담이다. 프로파일링 수단은 없다(05 문서의 에뮬레이터 캡처로 끊김·지연만 확인 가능)

## 5. voicegroup(악기 묶음)

- FR/LG: `sound/voice_groups.inc`에 숫자 voicegroup 77개(`voicegroup000~012`, `127~190`). 각 voicegroup은 **메모리에서 이어지는 12바이트 항목 목록**이다. 프로그램 번호 p는 "라벨 + p번째 항목"이다. 128개를 다 채우지 않은 voicegroup은 다음 voicegroup 항목으로 넘어간다(FR/LG 원본 구조 그대로)
- 에메랄드: `sound/voicegroups/*.inc` 50개(`voice_group <이름>` 매크로), 드럼셋 `sound/voicegroups/drumsets/`(frlg, rs, emerald_1·2, petalburg, route101, route110), 키스플릿 `sound/voicegroups/keysplits/`(piano, strings, trumpet, french_horn, tuba), 키스플릿 표 `sound/hoenn_keysplit_tables.inc`
- 프로그램 0 = 드럼킷(`voice_keysplit_all`). 음 번호가 드럼 종류다
- 키스플릿 표: `sound/keysplit_tables.inc`(FR/LG `KeySplitTable1~`), 에메랄드는 `keysplit`/`split` 매크로(`asm/macros/m4a.inc:26-45`)

### 5.1 새 곡에 쓸 만한 voicegroup(곡이 실제로 쓰는 프로그램 기준)

| VG | 원래 곡 | 쓰는 프로그램(번호=악기) | 쓸 곳 |
|---|---|---|---|
| 133 | rocket_hideout | 0 드럼, 1 피아노(ks), 14 튜블러 벨, 17 오르간2, 24 나일론 기타, 29 오버드라이브, 30 디스토션(고), 38 신스 베이스, 48 현(ks), 56 트럼펫(ks), 60 호른(ks), 78 휘슬, 80~83 사각파, 87·92 웨이브, 120 스크림 드라이브, 126·127 노이즈 | 로켓단 계열 |
| 142 | encounter_rocket | 0 드럼, 17 오르간2, 24 나일론 기타, 38 신스 베이스, 80 사각파1, 81 사각파2, 83 웨이브 | 짧은 악당 조우 |
| 156 | vs_trainer | 0 드럼, 3 웨이브, 5 디튠 EP, 17 오르간2, 21 아코디언, 24 나일론, 29·30·62 기타 3종, 33 사각파2, 48 현, 56 트럼펫, 60 호른, 81·82 사각파1, 120 스크림, 125~127 노이즈 | 트레이너 전투 |
| 158 | vs_champion | 156과 비슷 + 53 합창(ahhs), 47 팀파니, 14 튜블러 벨 | 최종전·은빛산 |
| 157 | vs_wild·legend·mewtwo | 0 드럼, 17 오르간2, 29 오버드라이브, 33 핑거드 베이스, 38 신스 베이스, 48 현, 60 호른, PSG 다수 | 전투 |
| 149 | credits | 0 드럼, 1 피아노, 9 글로켄슈필, 13 실로폰, 14 튜블러 벨, 46 하프, 47 팀파니, 48 현, 56 트럼펫, 58 튜바, 60 호른, 68 오보에, 73 플루트, PSG | 엔딩·감동 장면(가장 풍부) |
| 159 | pallet | 4·5 디튠 EP, 24 나일론, 48 현, 80·81·83 사각파 | 잔잔한 마을·피카츄 |
| 162 | poke_center·net_center | 1 사각파1, 4 EP, 14 튜블러 벨, 17 오르간2, 33 핑거드 베이스, 48 현, 92 웨이브 | 실내·공항 |
| 008 | 팡파르 11곡 | 0 드럼, 1 피아노, 2 메가 베이스, 13 실로폰, 46 하프, 47 팀파니, 48 현, 56 트럼펫, 58 튜바, 60 호른, 73 플루트, 80~101 PSG | 새 팡파르 |
| `_b_frontier`, `_b_tower` | 배틀 프런티어·타워 | 1 드럼, 14 튜블러 벨, 46 하프, 47 팀파니, 48 현, 56 트럼펫, 60 호른, PSG | 토너먼트 |
| `_route119`, `_route120` | 도로 | 현·트럼펫·튜바·호른 키스플릿, 하프, 팀파니, 글로켄 | 여행·비행 |

- 곡별로 쓰는 프로그램과 악기는 `python3 tools/music/songinfo.py mus_<곡> --json`의 `tracks[].programs`로 볼 수 있다
- **새 샘플을 넣지 않는 것을 기본으로 한다.** 기존 voicegroup을 그대로 쓰면 ROM 비용이 0이다. 새 voicegroup(기존 샘플 조합)은 128항목 × 12바이트 = 1.5KB다. 새 샘플은 1개에 중앙값 5KB, 최대 36KB다(`sound/direct_sound_samples`, 197개 파일 9MB는 wav와 bin을 합친 크기)

## 6. 곡 추가 방법(작곡가 체크리스트)

1. `sound/songs/midi/mus_<이름>.mid` 추가
2. `midi.cfg`에 `mus_<이름>.mid: -E -R50 -G<vg> -V<nn>` 한 줄. 팡파르면 `-P5`
3. `include/constants/songs.h`: `MUS_VERDANTURF 395` 다음, `// END HOENN MUSIC` **바깥**에 새 블록(예: `// BEGIN THUNDER YELLOW MUSIC`)으로 396부터 번호를 매긴다
   - 주의: `tools/hoenn_import/import_music.py`는 자기 마커 블록을 통째로 다시 쓴다. 그 블록 안에 넣으면 재실행 때 지워진다
   - 곡 번호는 u16이고 `MUS_NONE`만 0xFFFF다. 번호 공간은 충분하다
4. `sound/song_table.inc` 끝(398행 `song mus_verdanturf, 0, 0` 뒤)에 `song mus_<이름>, 0, 0`. 두 번째 인자는 플레이어다: BGM·팡파르 0, 효과음 1~2. **이 순서가 상수 값과 일치해야 한다**
5. `ld_script.ld`에 `sound/songs/midi/mus_<이름>.o(.rodata);` 줄 추가(HOENN 블록 바깥, 1023행 뒤 권장). `ld_script_rev10.ld`도 같은 목록이 있으면 같이 고친다(현재 rev10에는 Hoenn 곡이 없다. rev10 빌드를 쓰지 않으면 무관)
6. 연결:
   - 맵 음악: `data/maps/<맵>/map.json`의 `"music"`
   - 스크립트: `playbgm MUS_X, 0`, `fadenewbgm`, `savebgm`, `fadedefaultbgm`
   - **팡파르**: `playfanfare`는 `src/sound.c:51-66` `sFanfares[]` 표에 있는 곡만 제대로 튼다. 표에 없으면 **조용히 레벨업 팡파르를 튼다**(`src/sound.c:244-247`). 새 팡파르는 `FANFARE_*` 상수(`include/constants/sound.h`)와 표 항목(곡, 길이 프레임)을 같이 넣어야 한다. 길이는 곡 실제 길이보다 약간 길게(원곡: 배지 5.2초에 340프레임 = 5.7초)
   - 전투곡: `GetBattleBGM`(`src/pokemon.c:5942-5969`)은 트레이너 **클래스**로 고른다. 로켓단 트리오만의 전투곡은 클래스 분기로는 안 되므로(일반 로켓단원과 같은 클래스) 트레이너 ID 분기나 새 클래스가 필요하다. 엔지니어 몫이다
   - 승리곡: `src/battle_main.c:3753-3767`
   - 조우곡: 트레이너 데이터의 `encounterMusic` → `src/battle_setup.c:1078` 부근 switch. 새 조우곡은 새 `TRAINER_ENCOUNTER_MUSIC_*` 값과 case가 필요하다. 다만 이 해킹의 이벤트 전투는 대부분 `trainerbattle_no_intro`/`earlyrival`이라 **스크립트의 `playbgm`이 실제 조우곡**이다(03 문서)

## 7. 음량·리버브 관례

- `-R50` 통일. 곡마다 다르게 하지 말 것(곡 전환 때 리버브가 바뀌어 튄다)
- `-V`: 이웃 곡과 맞춘다. 같은 화면에서 이어지는 곡의 `-V`를 참고한다
  - 조우 → 전투: encounter_rocket 96 → vs_trainer 90
  - 마을 필드: 79~100(pallet 100, route1 79)
  - 에메랄드 이식곡은 80이 기본이고, 이식할 때 원판 값을 그대로 가져왔다
- 트랙 VOL(CC7) 중앙값 108. 멜로디 100~127, 반주 55~90
- PAN: FR/LG 곡은 트랙마다 PAN을 넓게 준다(route1 `c_v+41` 등). PSG는 좌·중·우 세 단계로만 들린다

## 8. ROM 여유

- `pokemonthyl.gba`(2026-09-26 09:31 빌드): 파일은 16MB로 채워져 있다. 실제 사용 15,440,068바이트(14.72MB), **여유 1.275MB**(끝의 0xFF 패딩을 셈)
- 곡 크기(`pokemonthyl.map`, `.rodata`): 141곡 평균 3,271바이트, 중앙값 2,936바이트
  - 필드곡: 2~5KB
  - 전투곡: 4~11KB(vs_trainer 11,124바이트)
  - 크레딧: 16,396바이트
  - 팡파르: 0.2~0.7KB
- FR/LG 곡 합계 255KB, 에메랄드 이식 49곡 합계 206KB(샘플·voicegroup 제외)
- 추정: 오리지널 30곡(평균 4KB)에 크레딧급 3곡(각 16KB)을 더하면 약 170KB로, 여유의 13% 정도다. **샘플을 새로 넣지 않으면 ROM은 제약이 아니다.** 제약은 채널이다
