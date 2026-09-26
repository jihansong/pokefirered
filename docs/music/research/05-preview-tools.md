# 05. 미리 듣기 수단: MIDI → WAV와 에뮬레이터 오디오 캡처

- 작성: 음악 리서처, 2026-09-26. 음악 감독 브리프 5번 항목. 프로듀서 지시로 도구를 저장소에 넣었다(커밋 전)
- 원칙(`docs/team/log.md:54`): 작곡한 곡은 **반드시 WAV 미리 듣기로 사용자에게 먼저 들려준다.** 사용자가 승인하기 전에는 게임에 넣지 않는다.
- 도구 세 가지
  - `tools/music/songinfo.py`: 수치와 엔진 규칙 검사. 표준 라이브러리만 쓴다
  - `tools/music/render.py`: MIDI → WAV 간이 렌더러. numpy를 쓴다
  - `tools/qa/audiocap.py`: 실제 ROM 소리 녹음. `tools/qa/libqa.c`와 `emu.py`에 오디오 기능을 더했다

## 1. 설치된 도구 조사

| 도구 | 상태 |
|---|---|
| fluidsynth, timidity | 없음 |
| sox, ffmpeg, lame | 없음 |
| GM 사운드폰트(.sf2/.sf3) | 없음(파일 시스템 전체 검색) |
| Python | 3.11.2, numpy 1.24.2(`.devcontainer/setup.sh`가 설치). scipy·mido 없음 |
| libmgba | `libmgba-dev` 0.10.1, 헤더는 `/usr/include/mgba/` |

- fluidsynth나 timidity를 설치할 수는 있다. 하지만 GM 사운드폰트 소리는 GBA 소리(8비트 13kHz 샘플 + PSG)와 전혀 다르다. 음량·채널 부족·음색 판단에 쓸 수 없으므로 쓰지 않는다.

## 2. 검수 기준(채택)

- 트랙 ≤ 9
- `max_held_ds ≤ 4`: 한 순간에 눌린 샘플 음이 4개를 넘지 않는다
- `held_ds_steals = 0`: 엔진의 샘플 채널 5개 제한 때문에 눌린 음이 잘리는 일이 없다
- 그 밖에: `midi.cfg` 줄, `-R50`, 24틱/4분음표, 루프 마커(팡파르는 `--one-shot`)
- 근거: 02 문서 4절. `songinfo.py`가 이 기준을 자동으로 검사한다.

```
python3 tools/music/songinfo.py mus_<곡>            # 요약 + 검사(실패 시 종료 코드 1)
python3 tools/music/songinfo.py mus_<곡> --one-shot # 팡파르·징글
python3 tools/music/songinfo.py mus_<곡> --json     # 모든 수치
python3 tools/music/songinfo.py --all > songs.json  # 전곡(01 문서 통계의 원자료)
```

- 기존 곡에 돌려 본 결과: `mus_route1`과 `mus_encounter_rocket`은 통과한다. `mus_vs_trainer`는 10트랙, `max_held_ds` 5로 걸린다. 원곡 중 가장 무거운 축이라 새 곡은 이보다 한 단계 가볍게 쓰라는 뜻이다.

## 3. (A) 간이 렌더러: `tools/music/render.py`

```
python3 tools/music/render.py mus_route1 /tmp/route1.wav                  # 루프 2번
python3 tools/music/render.py mus_route1 /tmp/route1.wav --loops 3
python3 tools/music/render.py work/new.mid /tmp/new.wav --cfg "-E -R50 -G133 -V090"  # cfg 줄 없는 새 곡
python3 tools/music/render.py mus_route1 /tmp/r.wav --no-limit            # 5음 제한 끄고 비교
```

- 게임의 실제 악기로 소리를 낸다.
  - 곡의 voicegroup과 키스플릿 표로 프로그램 번호를 악기에 대응시킨다.
  - `sound/direct_sound_samples/*.wav`의 실제 샘플을 쓴다. 파일 안의 `smpl` 루프 지점, 기준음 60, 원 샘플레이트를 그대로 쓴다.
  - 웨이브는 `sound/programmable_wave_samples`를 쓰고, 사각파(듀티)와 노이즈를 흉내 낸다.
- 반영하는 것
  - VOL·PAN·벨로시티·`-V`, `[`/`]` 루프
  - 프레임 단위 ADSR
  - **샘플 동시 발음 5개 제한과 빼앗기**, PSG 채널당 1음(`songinfo.channel_plan`)
- 속도: 50초 분량 3초, 100초 분량 약 7초. 출력은 26,758Hz 16비트 스테레오다.
- 정확도: `mus_intro_fight`를 ROM 녹음과 비교했다.
  - 0.1초 창 음량 곡선의 상관계수가 0.93이다(지연 0). 박자와 강약은 맞다.
  - 스펙트럼 중심은 ROM 3,686Hz, 렌더러 4,446Hz다. 렌더러가 조금 밝다.
- 하지 않는 것: 리버브, 비브라토(MOD/LFO), 피치 벤드, 스윕, 정확한 CGB 엔벨로프, 효과음과의 경합.
- 용도: **작곡 중 반복 확인용**이다. 사용자에게 들려줄 최종본은 (B)로 만든다.

## 4. (B) ROM 녹음: `tools/qa/audiocap.py`

- `tools/qa/libqa.c`에 두 함수를 더했다.
  - `qa_audio_start(qa, rate)`: 출력 샘플레이트를 정하고 버퍼를 비운다
  - `qa_run_audio(qa, frames, out, max)`: 프레임을 돌리면서 매 프레임 좌·우 버퍼를 비워 16비트 스테레오로 쌓는다
  - 둘 다 libmgba의 `getAudioChannel`, `blip_set_rates`, `blip_read_samples`를 쓴다(`/usr/include/mgba/core/core.h:76-78`, `blip_buf.h`)
  - `qa_audio_start`를 부르지 않으면 이전과 똑같이 동작한다
- `tools/qa/emu.py`에 메서드 세 개를 더했다: `audio_start(rate=32768)`, `run_audio(frames)`(PCM 바이트), `record_wav(path, frames)`. 오디오 바인딩은 처음 쓸 때 한다. 그래서 오디오 함수가 없는 옛 `libqa.so`도 다른 QA 스크립트에서 그대로 로드된다.
- 빌드는 그대로 `tools/qa/build.sh`를 쓴다(`-lmgba`만으로 링크된다). `emu.py`는 `libqa.c`가 `.so`보다 새로우면 스스로 다시 빌드한다.

```
# 전원을 켜고 1500프레임(로고·인트로) 녹음
python3 tools/qa/audiocap.py pokemonthyl.gba /tmp/intro.wav --frames 1500
# 세이브로 CONTINUE → 30프레임에 A → 40초 녹음
python3 tools/qa/audiocap.py pokemonthyl.gba /tmp/scene.wav --sav saves/x.sav --continue --press A@30 --seconds 40
# 1465프레임을 녹음 없이 넘겨 타이틀 화면부터 60초, 전달용 22kHz 모노
python3 tools/qa/audiocap.py preview.gba /tmp/title.wav --skip 1465 --seconds 60 --small
```

- 녹음이 끝나면 길이와 **소리가 시작·끝나는 초와 프레임**(-50dBFS 넘는 50ms 창)을 출력한다. 크레딧(174초), 오프닝(752프레임), 비행 장면(560프레임)처럼 길이가 정해진 큐를 이 값으로 잰다.
- `--continue`는 ROM 옆에 `.sym` 파일이 있어야 한다(`make syms`, 또는 ROM과 함께 `pokemonthyl.sym`을 복사).
- 시험 결과(scratchpad에 복사한 ROM, 메인 트리 ROM은 쓰지 않음)
  - 전원 켜고 1,500프레임을 5.9초에 녹음했다. 소리가 **206프레임**에서 시작해 콘티의 실측값(209프레임 `MUS_GAME_FREAK`, `docs/anim/opening-storyboard.md:25`)과 맞았다.
  - 1,465프레임을 넘긴 뒤 타이틀 곡 20초를 `--small`로 녹음했다: 0.88MB.
  - `saves/hoenn.sav`로 CONTINUE한 뒤 START·B를 누르며 8초를 녹음했다: 정상.
- 특정 곡을 틀려면(에뮬레이터는 게임이 트는 곡만 들린다)
  1. **미리 듣기 빌드**(사용자 승인 전 권장): worktree에서 새 곡을 `MUS_TITLE` 자리에 잠시 연결해 빌드한다. `--skip 1465`로 타이틀부터 녹음한다. 이 빌드는 게임에 넣는 것이 아니라 들려주기용이다.
  2. **실전 확인**(승인 뒤): 곡을 실제 맵·스크립트에 연결한 빌드와 그 장면 직전 세이브로 녹음한다. 효과음·울음소리와의 채널 경합, 전환(`fadedefaultbgm`), 루프 이음새를 여기서만 확인할 수 있다.

## 5. 작업 흐름

1. 작곡가: MIDI를 쓸 때마다 `render.py`로 듣고 `songinfo.py`로 검사한다(기준 통과 필수).
2. 검수자:
   - `songinfo.py` 검사와 04 문서의 선율 비교로 1차 판정한다.
   - 미리 듣기 빌드를 `audiocap.py`로 녹음해 소리·길이·루프 이음새를 확인한다.
   - 그 WAV(`--small`)를 사용자에게 건넨다.
3. 사용자 승인 뒤에만 곡을 실제 맵·스크립트에 연결한다(`docs/team/log.md:54`).
4. 파일 크기: 32kHz 스테레오는 100초에 13MB, `--small`(22kHz 모노)은 4.4MB다. MP3 인코더는 없다.
