# 05. 미리 듣기 수단: MIDI → WAV와 에뮬레이터 오디오 캡처

- 작성: 음악 리서처, 2026-09-26. 음악 감독 브리프 5번 항목
- 결론: **두 방법 다 이 환경에서 실제로 돌아간다.** 둘 다 시험해 봤다.
  - (A) 파이썬 간이 m4a 렌더러: 게임의 실제 샘플을 쓰고 몇 초 만에 끝난다. 작곡 중 반복 확인용
  - (B) libmgba 오디오 캡처: 실제 ROM 소리를 그대로 담는다. 최종 검수와 길이 확인용

## 1. 설치된 도구 조사

| 도구 | 상태 |
|---|---|
| fluidsynth, timidity | 없음 |
| sox, ffmpeg, lame | 없음 |
| GM 사운드폰트(.sf2/.sf3) | 없음(파일 시스템 전체 검색) |
| Python | 3.11.2. numpy 1.24.2 있음. scipy·mido 없음 |
| pip | 있음. PyPI 접근도 됨(`mido` 휠 받기 성공, 설치는 하지 않음) |
| libmgba | `libmgba-dev` 0.10.1(Debian). 헤더 `/usr/include/mgba/`, `tools/qa/libqa.so`가 이미 링크해 쓴다 |

- fluidsynth나 timidity를 apt로 설치할 수는 있다. 그래도 GM 사운드폰트 소리는 GBA 소리(8비트 13kHz 샘플 + PSG)와 전혀 다르다. 음량·채널 부족·음색 판단에 쓸 수 없으므로 **권하지 않는다.**

## 2. (A) 파이썬 간이 m4a 렌더러(시험 구현 완료)

- 위치: scratchpad `render.py`(분석기 `analyze.py`를 불러 쓴다). 저장소에는 넣지 않았다. 작곡가·검수자가 쓰려면 `tools/music/`로 옮기는 것을 제안한다(감독 결정).
- 사용법: `python3 render.py mus_route1 out.wav 2`
  - 세 번째 인자는 루프 반복 횟수다.
  - `--no-limit`를 붙이면 채널 제한을 끈다.
- 하는 일:
  - `midi.cfg`의 `-G`·`-V`를 읽는다.
  - `sound/voice_groups.inc`(include 포함)와 키스플릿 표(`sound/keysplit_tables.inc`, `sound/hoenn_keysplit_tables.inc`)로 프로그램 번호를 실제 악기에 대응시킨다.
  - **게임의 실제 샘플**(`sound/direct_sound_samples/*.wav`)을 쓴다. wav 파일 안의 `smpl` 루프 지점, 기준음 60, 원 샘플레이트를 그대로 쓴다.
  - 샘플 음: 프레임(60Hz) 단위 ADSR을 흉내 낸다.
  - PSG: 사각파(듀티 12.5/25/50/75%), 웨이브(`sound/programmable_wave_samples/*.pcm`의 4비트 32샘플), 노이즈를 흉내 낸다.
  - VOL·PAN·벨로시티·`-V`를 반영하고, `[`/`]` 루프를 펼친다.
  - **샘플 동시 발음 5개 제한과 빼앗기**(놓은 음 먼저, 다음은 오래된 음), PSG 채널당 1음을 흉내 낸다.
- 통계 모드(소리를 만들지 않음):
  - `render(name, loops, limit, stats_only=True)`가 `max_held_ds`(한 순간 눌린 샘플 음의 최대 수)와 `held_ds_steals`(눌린 음을 빼앗긴 횟수)를 준다.
  - 02 문서의 "원곡은 샘플 동시음 4~5" 수치가 여기서 나왔다. **새 곡 검수 기준으로 바로 쓸 수 있다**(권장: `max_held_ds ≤ 4`, `held_ds_steals = 0`).
- 속도: route1 2회 반복(51.9초 분량) 3.1초, vs_trainer(103.9초 분량) 6.6초. 출력은 26,758Hz 16비트 스테레오.
- 정확도 검증: 같은 곡 `mus_intro_fight`를 에뮬레이터 캡처(B)와 비교했다.
  - 0.1초 창 RMS 음량 곡선의 상관계수가 **0.93**이다(지연 0). 타이밍과 강약 흐름은 맞다.
  - 스펙트럼 중심은 에뮬레이터 3,686Hz, 렌더러 4,446Hz다. 렌더러가 조금 밝다(보간 없는 리샘플링, 리버브·저역 필터 없음).
- 하지 않는 것:
  - 리버브(`-R50`), MOD/LFO 비브라토, 피치 벤드, 사각파 스윕
  - 정확한 CGB 엔벨로프, m4a 리샘플러 음질, 효과음과의 경합
  - 그래서 **최종 판정에는 (B)를 쓴다.**

## 3. (B) 에뮬레이터 오디오 캡처(시험 구현 완료)

- `tools/qa/libqa.c`는 지금 오디오를 다루지 않는다(1~5행 주석 "no audio"). 헤더를 확인해 보니 libmgba 0.10은 오디오를 꺼낼 수 있다.
  - `struct mCore`의 `getAudioChannel(core, 0|1)`이 좌·우 `blip_t*`를 준다. `setAudioBufferSize`도 있다(`/usr/include/mgba/core/core.h:76-78`).
  - `blip_set_rates`, `blip_samples_avail`, `blip_read_samples`가 `/usr/include/mgba/core/blip_buf.h`에 있다. 모두 `libmgba.so`가 내보낸다(`nm -D`로 확인).
  - `core->frequency(core)`(core.h:113)가 CPU 클럭 16,777,216Hz를 준다.
- 시험 프로그램: scratchpad `audiocap.c`(40행)
  - 빌드: `cc -O2 -o audiocap audiocap.c -lmgba`
  - 흐름: ROM 사본을 켜고 매 프레임 `runFrame` 뒤에 두 채널에서 샘플을 읽어 32,768Hz 16비트 스테레오 WAV로 쓴다.
  - 결과: 1,500프레임(25.1초)을 **7.7초**(CPU 2.4초)에 캡처했다. 3초부터 게임프리크 징글, 12초부터 인트로 음악 음량이 잡혔다.
  - ROM은 scratchpad에 복사해서 썼다. 메인 트리 ROM과 세이브는 건드리지 않았다.
- libqa에 넣을 때의 모양(엔지니어 몫, `docs/team/log.md:62`에 이미 할 일로 올라 있음):
  - `qa_audio_start(qa, rate)`: `setAudioBufferSize` + `blip_set_rates`
  - `qa_audio_read(qa, short *buf, int max)`: 매 `qa_frame` 뒤 호출
  - `emu.py`: `record_wav(path, frames)`
- **특정 곡을 트는 방법**(에뮬레이터는 게임이 트는 곡만 들린다)
  1. **미리 듣기 빌드(권장)**: worktree에서 새 곡을 `MUS_TITLE` 자리에 잠시 연결해 빌드한다. 세이브 없이 켜서 타이틀(1,465프레임부터, `docs/anim/opening-storyboard.md:44`)을 캡처한다. 메인 트리 ROM과 충돌하지 않는다.
  2. **실전 확인**: 곡을 실제 맵·스크립트에 연결한 빌드와, 그 장면 직전 세이브(`tools/qa/savedit.py`, `savefile.py`로 만들 수 있음)로 장면을 재생해 캡처한다. 전투 효과음·울음소리와의 채널 경합, 전환(`fadedefaultbgm` 등), 루프 이음새를 여기서만 확인할 수 있다.
  3. 길이 확인: 크레딧·오프닝·비행 장면처럼 길이가 고정된 큐는 캡처한 WAV의 곡 시작·끝 프레임을 재서 목표(174초, 752프레임, 560프레임)와 비교한다.

## 4. 제안하는 작업 흐름

1. 작곡가: MIDI를 쓰면 (A)로 바로 렌더링해 듣고, 통계 모드로 `max_held_ds ≤ 4`인지 확인한다.
2. 검수자:
   - (A) 통계와 04 문서의 n-그램 비교로 기술·독창성을 1차 검사한다.
   - (B) 미리 듣기 빌드 캡처로 최종 소리, 길이, 루프 이음새를 확인한다.
   - 사용자에게는 (B) WAV를 건넨다.
3. 사용자 전달: WAV는 크다(100초에 약 13MB). 필요하면 파이썬 표준 라이브러리로 22kHz 모노로 줄인다. MP3 인코더는 없다.
