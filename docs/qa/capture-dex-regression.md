# 신규 포획 도감 등록: 그림 메모리 인계와 CI

포획 후 신규 도감 화면은 자체 그림과 창을 만든다. 이전 전투의 그림 캐시를
계속 보유하면 작은 힙에서 8192바이트의 임시 그림 버퍼를 확보하지 못한다.
`Cmd_displaydexinfo`의 state 1은 흰색 페이드와 DMA 완료를 기다린 뒤,
비통신 전투의 VBlank 콜백을 해제하고 스프라이트 복사/애니메이션 상태를
초기화한 다음 재생성 가능한 그림 캐시를 해제한다. 창 해제, 원래 도감 등록,
본문 표시, 복귀 state 2~5와 종·OTID·PID 전달은 기존 경로를 유지한다.
통신 전투의 그림 캐시 수명은 유지한다. 저장 구조나 힙 크기는 바꾸지 않는다.

이 변경은 Codespaces에 남은 `dafcb39f781d8fc29e0877f64f6cd9358e5b0c41`
기준 소스(114688바이트 힙)에 적용한 좁은 backport다. 이후 로컬 작업 전체나
미완료 우주/개인화 변경을 포함하지 않는다. CI가 만드는 ROM은 이미 전달한
R23 DexFix ROM의 재빌드가 아니며, 사용자용 새 배포본으로 취급하지 않는다.
기존 ROM·SAV를 읽거나 수정하지 않고 오프닝·타이틀·크레딧 음악 자산을 변경하지 않는다.

## 검사가 실행하는 코드

Linux에서 다음 명령은 저장소의 C 함수와 구조체를 매번 직접 추출해
`gcc -m32`로 컴파일하고 실행한다. 복제한 Python 할당기나 문자열 검사가 아니다.

```sh
python3 tools/qa/capture_dex_regression.py
```

실제 `src/malloc.c`, `InitWindows`/`AddWindow`/`FreeAllWindowBuffers`,
`AllocateMonSpritesGfx`/`FreeMonSpritesGfx`, 도감 자원 로더·분류 창·상세 창·
임시 그림 버퍼·종료 함수와 `Cmd_displaydexinfo` 전체를 사용한다. 32비트
포인터, 16바이트 힙 헤더, 384바이트 전투 그림 캐시 구조를 정적 단언한다.
GPU, 사운드, 작업 스케줄러, 압축 해제 호출은 테스트 대역이다. 렌더링이나
게임 전체 실행을 수행하는 검사가 아니다.

다음 항목을 검사한다.

- 80128바이트와 114688바이트 힙에서 분류 1~4칸과 상세 창의 실제 할당/해제.
  각 조합을 두 번 실행하고 힙 밖 canary와 유지 중인 전투 상태를 확인한다.
- 페이드 또는 DMA가 진행 중이면 state 1, 그림 캐시, 창과 도감 생성이 대기함.
- 콜백 정지→스프라이트 초기화→캐시 해제→도감 생성 순서, 통신 경로의 캐시 유지.
- 도감 종료 시 작업/콜백/페이드 게이트, BG 복사 대기, 복귀 그림의 종·OTID·PID,
  스크립트 재개 및 반복 NULL 해제.
- 새 캐시 해제만 제거한 별도 C 빌드가 80128바이트 힙에서 할당 실패를 검출하고,
  114688바이트 힙에서는 같은 경로를 통과함. 기존 창 해제는 이 대조군에도 남긴다.
- 실제 분류 데이터의 386종·1~4칸 페이지와 front-picture 표의 PNG 경계,
  안농 27개 추가 그림과 캐스퐁 4개 원본 그림의 8192바이트 버퍼 경계.

힙 fixture는 원래 소스의 4배틀러 캐시, 실제 창 함수로 만든 3개 전투 창과
12288바이트의 유지 중 전투 데이터로 구성한다. 특정 R23 정지 프레임의 정확한
할당 trace를 재현한다고 주장하지 않는다. `--native-abi`는 64비트 개발 PC의
보조 검사이며 GBA 헤더 크기 검사를 생략한다. CI는 이 옵션을 사용하지 않는다.

빌드 후에는 `--built-assets`로 생성된 front-picture와 일반/이로치 팔레트
LZ77 스트림을 직접 해제해 길이와 참조 범위도 검사한다.

```sh
make tools COMPARE=0
make generated GAME_VERSION=LEAFGREEN COMPARE=0 SETUP_PREREQS=0 NODEP=1
make leafgreen -j"$(nproc)" COMPARE=0 SETUP_PREREQS=0
make GAME_VERSION=LEAFGREEN COMPARE=0 SETUP_PREREQS=0 syms
python3 tools/qa/capture_dex_regression.py --built-assets
```

## CI 범위와 도구 고정

`capture-dex.yml`은 `codex/**` push, PR 및 명시적 수동 실행에서 동작한다.
기존 `build.yml`은 같은 검사에 연결하는 수동 진입점이다. 커스텀 ROM을
원본 FireRed/LeafGreen 해시와 비교하던 자동 작업과 symbols 브랜치 쓰기는 제거했다.

도구는 프로젝트의 `docs/INSTALL.md`와 `.devcontainer`에 적힌 다음 기준을 쓴다.

- `devkitpro/devkitarm:20260610` 이미지와 SHA256 digest를 고정한다.
- pret/agbcc는 `da598c1d918402c42c0c0d7128ba14567f3175e9`를 사용한다.
- checkout은 Node 24를 사용하는 actions/checkout v5의 전체 커밋을 고정한다.
- LeafGreen revision 0, `COMPARE=0`, ROM과 symbols 생성, 아래 명시한 ELF 진단 대조와 최종 빌드 경고 0을 요구한다.
- 필요한 소스/빌드 입력만 sparse checkout하고 기존 ROM·SAV·work·과거 QA 산출물을
  받지 않는다. GitHub 권한은 `contents: read`이며 파일 업로드와 원격 브랜치 쓰기는 없다.

워크플로는 mGBA를 설치하거나 실행하지 않으며 사용자 SAV를 요구하지 않는다.
성공은 위 빌드와 호스트 C/데이터 검사 범위다. 실제 설치된 iOS Delta 앱,
386종의 실제 포획, 모든 별명·파티/박스 상태·Safari/Snag/통신 조합 또는
SAVE 후 cold reload의 성공으로 확대하지 않는다. 로컬의 별도 Delta 고정 코어
포획 검증은 해당 ROM과 검증 기록에만 연결하며 이 CI 결과로 대체하지 않는다.

## 보존된 원시 미디어 입력

오프닝 2개와 타이틀 3개는 C가 직접 읽는 기존 원시 입력이다. 대응 PNG/PAL을
다시 인코딩하지 않고, 보존된 Codespaces 기준 ROM과 ELF의 심볼 payload 전체와
일치하는 파일을 그대로 추적한다. 기준 ROM SHA256은
`7d66f47ad68e192d9f5916d9ef9bd9c9fb42fd80bcd3e2835b32cd328a208636`,
ELF SHA256은 `fdcb9ec35de57dc4299878af4251193a67c78a6a0d27b2b9bbd03458972207d0`다.

| 원시 입력 | 바이트 | SHA256 |
|---|---:|---|
| `graphics/intro/opening_movie_v7/pixels.8bpp` | 14192640 | `ff8c4e7f91ef541952f638043efdfe396d416777aaa984350869da3e603b66c3` |
| `graphics/intro/opening_movie_v7/palettes.gbapal` | 178688 | `f253176e6ead3f2f5dd55c01de2f33881ce143527c464d076d2786bc348724f7` |
| `graphics/title_screen/thunder_yellow/approved-title-v8.8bpp` | 38400 | `266b8c5764de352fd471c742705cc8744eeff15c16e13c557854b514d6153eff` |
| `graphics/title_screen/thunder_yellow/approved-title-v8-start-roi.8bpp` | 645120 | `65f31390c8c1065dc28a3ea36a2990a8c351cd121d4be5c3e2f2d17c266d1e33` |
| `graphics/title_screen/thunder_yellow/approved-title-v8.gbapal` | 512 | `e4888a4dcd5539808992724f60e9891393a950904ee06c817a601977285ebdd2` |

이 파일들은 새 그림이나 새 음악이 아니다. 파일 변환, 픽셀 수정, ROM/SAV 업로드는
없다. CI는 이 다섯 입력의 크기와 해시를 확인한다. 기존 Rocket96 PNG 변환 도구가
필요로 하는 Pillow만 `python3-pil`로 설치하며, 해당 도구의 기존 입력/출력 해시
검사는 유지한다.

32비트 C 소유권 검사는 의존성 설치 직후, agbcc 및 ROM 빌드 전에 실행한다.
따라서 미디어 빌드 문제와 C 회귀 결과를 구분할 수 있다. 빌드 후 검사는 생성된
그림/팔레트 데이터만 읽어 확인하며 C 실행 검사를 반복하지 않는다.

## 기존 멀티부트 클라이언트 입력

`data/multiboot_*.s`는 저장소에 이미 있던 다음 세 클라이언트를 `.incbin`으로
포함한다. sparse checkout의 `*.gba` 차단 뒤에 세 경로만 명시적으로 허용한다.
체크아웃 검사는 경로·크기·SHA256이 모두 일치해야 허용하고, 다른 게임 ROM과
모든 SAV/SRM 입력의 차단은 유지한다. 새 바이너리 파일은 추가하지 않는다.

| 기존 경로 | 바이트 | SHA256 | 기존 Git blob |
|---|---:|---|---|
| `data/mb_berry_fix.gba` | 15348 | `f3d87e14688faf0190b33e071607887c7783462b45f92f1cb7135eec56260740` | `0afff07f5d2314e2bd35d99de518cbc114009b5e` |
| `data/mb_colosseum.gba` | 163840 | `1c0d4d793ad87df3cb8d2b3d636db63b6255955b27c9927d69728fcc1fdbbe22` | `2ff3f88bcc4a807954e3576f354e88612ef68bf9` |
| `data/mb_ereader.gba` | 14176 | `eee7d18515904336a71335452d9b57c0234eb7208984a152a88345229c97b0a0` | `63d26ca2af53300a62611f46d540c49154d6b8af` |

세 입력의 Git blob은 원본 `dafcb39f781d8fc29e0877f64f6cd9358e5b0c41`의 기록과
일치한다. 파일을 새로 올리거나 확장자를 바꾸지 않고, 기존 소스 입력의
체크아웃만 허용한다. 게임 코드, 도감 회귀 도구와 보존 미디어는 변경하지 않는다.

## 빌드 경고를 구분하는 대조 검사

기존 Makefile은 읽는 도중 `$(shell $(MAKE) ...)`로 도구와 생성 입력을 준비한다.
이 호출이 병렬 make의 jobserver를 전달받지 못해 발생하는 경고는 준비 단계를
직렬로 먼저 실행하고 실제 병렬 빌드에 `SETUP_PREREQS=0`을 전달하여 없앤다.
도구나 생성 입력을 생략하지 않으며 Makefile과 게임 소스는 수정하지 않는다.

고정 도구의 새 GNU ld는 기존 GBA 링크 스크립트가 만드는 비어 있지 않은 ELF
LOAD 구간의 RWX 속성을 경고한다. 먼저 `--warn-rwx-segments`로 게임을 빌드하여
`../../pokemonthyl.elf`에 대한 그 경고 정확히 한 줄만 허용한다. 준비/컴파일의
다른 경고는 실패다. 그때 ROM·ELF·SYM·MAP 전체 해시를 기록한다.
다음으로 링크 스크립트의 내용은 그대로 두고 시각만 갱신하여
`--no-warn-rwx-segments`로 다시 링크한다. 원래 `LDFLAGS`와 맵 출력은 유지한다.
최종 로그의 경고는 0이어야 하고 네 산출물의 바이트는 대조 빌드와 완전히
같아야 한다. 이 결과를 provenance에 남긴다. 경고를 일반적으로 무시하거나
게임의 메모리 배치·권한·픽셀을 변경하는 절차가 아니다.

해당 옵션이 제어하는 진단 범위는 [GNU ld 공식 문서](https://sourceware.org/binutils/docs/ld/Options.html#index-_002d_002dwarn_002drwx_002dsegments)에 따른다.
이 정책은 이 GBA bare-metal 링크에만 적용한다. 별도로 설치하는 예전 agbcc
자체의 호스트 빌드까지 경고가 없다는 주장은 하지 않는다.

고정 컨테이너의 ARM linker는 `${DEVKITARM}/bin/arm-none-eabi-ld`로 명시하고 실행 가능 여부를 먼저 확인한다. Makefile 내부에서만 확장되는 PATH에 셸의 `command -v` 결과를 의존하지 않는다.
