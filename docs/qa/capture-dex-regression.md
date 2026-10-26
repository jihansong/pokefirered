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
make leafgreen -j"$(nproc)" COMPARE=0
make GAME_VERSION=LEAFGREEN COMPARE=0 syms
python3 tools/qa/capture_dex_regression.py --built-assets
```

## CI 범위와 도구 고정

`capture-dex.yml`은 `codex/**` push, PR 및 명시적 수동 실행에서 동작한다.
기존 `build.yml`은 같은 검사에 연결하는 수동 진입점이다. 커스텀 ROM을
원본 FireRed/LeafGreen 해시와 비교하던 자동 작업과 symbols 브랜치 쓰기는 제거했다.

도구는 프로젝트의 `docs/INSTALL.md`와 `.devcontainer`에 적힌 다음 기준을 쓴다.

- `devkitpro/devkitarm:20260610` 이미지와 SHA256 digest를 고정한다.
- pret/agbcc는 `da598c1d918402c42c0c0d7128ba14567f3175e9`를 사용한다.
- checkout은 actions/checkout v4.2.2의 전체 커밋을 고정한다.
- LeafGreen revision 0, `COMPARE=0`, ROM과 symbols 생성, 빌드 경고 0을 요구한다.
- 필요한 소스/빌드 입력만 sparse checkout하고 기존 ROM·SAV·work·과거 QA 산출물을
  받지 않는다. GitHub 권한은 `contents: read`이며 파일 업로드와 원격 브랜치 쓰기는 없다.

워크플로는 mGBA를 설치하거나 실행하지 않으며 사용자 SAV를 요구하지 않는다.
성공은 위 빌드와 호스트 C/데이터 검사 범위다. 실제 설치된 iOS Delta 앱,
386종의 실제 포획, 모든 별명·파티/박스 상태·Safari/Snag/통신 조합 또는
SAVE 후 cold reload의 성공으로 확대하지 않는다. 로컬의 별도 Delta 고정 코어
포획 검증은 해당 ROM과 검증 기록에만 연결하며 이 CI 결과로 대체하지 않는다.
