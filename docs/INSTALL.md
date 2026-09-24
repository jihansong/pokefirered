# 개발 환경 — Thunder Yellow

이 저장소의 개발 환경과 QA 도구를 한 곳에 적는다. 원래 pret의 빌드 안내(여러 OS에서 devkitARM 설치하기)는 저장소 루트의 `INSTALL.md`에 있고, 이 문서는 **이 프로젝트의 컨테이너에서 무엇이 어디에 있고 어떻게 다시 만드는지**만 다룬다.

## 1. 컨테이너

`.devcontainer/devcontainer.json`이 이미지와 설치 스크립트를 정한다.

| 항목 | 값 |
|---|---|
| 이미지 | `devkitpro/devkitarm:20260610@sha256:116afba8…0bbf5` (devkitARM gcc 16.1.0). `latest`를 쓰지 않는다: 이미지가 바뀌면 빌드 도구가 말없이 바뀐다 |
| 설치 | `postCreateCommand`가 `bash .devcontainer/setup.sh`를 실행한다. 다시 실행해도 된다(있는 것은 건너뜀) |

이미지를 올릴 때는 Docker Hub의 `devkitpro/devkitarm` 태그 중 날짜 태그 하나와 그 digest를 함께 적고, 빌드한 ROM이 이전과 같은지(아래 3절) 확인한 뒤 바꾼다.

### setup.sh가 하는 일

| 무엇 | 어디 | 비고 |
|---|---|---|
| apt 패키지 | 시스템 | `build-essential libpng-dev git-lfs gh python3 python3-pil python3-numpy python3-docx libmgba-dev libreoffice-writer-nogui fonts-noto-cjk poppler-utils` |
| agbcc | `tools/agbcc/` (저장소에 없음, gitignore) | `../agbcc`에 pret/agbcc를 `da598c1d9`로 받아 빌드·설치. 같은 커밋이면 새로 빌드한 것과 기존 것의 컴파일 결과가 같다 |
| pokeemerald | `/root/src/pokeemerald` | `5eff78649` 고정. 호연 이식 스크립트(`tools/hoenn_import/`)와 `tools/qa/textaudit.py`, `tools/hoenn_reachability.py --emerald`가 읽는다 |
| QA 에뮬레이터 래퍼 | `tools/qa/libqa.so` (gitignore) | `tools/qa/build.sh`로 `libqa.c`를 libmgba에 링크 |
| git 설정 | 전역 | `safe.directory '*'` (워크스페이스 소유 uid가 컨테이너 사용자와 다름) |

`git-lfs`는 저장소의 push 훅이 요구한다. 없으면 `git push`가 "git-lfs was not found"로 멈춘다.

### 컨테이너를 다시 만들어도 남는 것 / 사라지는 것

`/workspaces` 아래는 남고, 그 밖(`/root`, 시스템 패키지)은 사라진다. 그래서:

- **남는 것**: 저장소, `baserom_leafgreen.gba`, `saves/`(세이브 5개, gitignore), `qa-base/`(기준 ROM, gitignore), `../agbcc` 소스
- **사라지고 setup.sh가 되살리는 것**: apt 패키지, `/root/src/pokeemerald`
- **직접 다시 해야 하는 것**: 없음. 단 `qa-base/`가 없으면 `tools/qa/refroms.sh`를 한 번 돌린다(아래)

QA 스크립트를 `/root` 아래에 두지 않는다. 2026-09-23에 컨테이너가 다시 만들어지면서 `/root/qa-tools`·`/root/qa-work`의 스크립트가 모두 사라졌고, 문서에 적힌 동작대로 `tools/qa/`에 다시 만들었다(v0.8.0 이전 기록의 `/root/qa-tools/…` 경로는 지금 `tools/qa/…`다).

## 2. 원본 ROM

영문 LeafGreen v1.0 롬을 저장소 루트에 `baserom_leafgreen.gba`로 둔다(sha1 `574fa542ffebb14be69902d1d36f1ec0a4afd71e`). `make clean`은 `poke*.gba`를 지우므로 이름을 바꾸지 않는다. 없으면 `tools/make_bps_patch.py` 첫머리의 방법으로 디컴파일에서 다시 만든다.

## 3. 빌드와 릴리스

```sh
make leafgreen -j$(nproc)                 # pokemonthyl.gba
make GAME_VERSION=LEAFGREEN syms          # pokemonthyl.sym (make leafgreen은 갱신하지 않는다)
python3 tools/make_bps_patch.py           # pokemonthyl.bps, 적용 결과를 검증한 뒤 저장
```

`.sym`은 `make leafgreen`이 갱신하지 않는다. QA 스크립트는 `.sym`이 ROM보다 오래되면 `.elf`에서 다시 만든다(`tools/qa/emu.py`의 `fresh_syms`).

릴리스 절차(v0.7.0·v0.8.0과 같음): 작업 브랜치에서 문서·공략집까지 커밋 → master에 `--no-ff` 머지 → 주석 태그 `vX.Y.Z` → `git push origin master vX.Y.Z` → `gh release create vX.Y.Z --verify-tag`에 `pokemonthyl.bps`와 `docs/Thunder_Yellow_Walkthrough_vX.Y.Z.docx`를 붙인다. 본문 형식은 이전 릴리스(`gh release view v0.8.0`)를 따른다.

## 4. QA 도구 (`tools/qa/`)

모두 저장소 안에 있고 Python 3로 돈다. 에뮬레이터는 libmgba(mGBA 0.10)를 헤드리스로 쓴다. 화면·소리 장치가 필요 없다.

| 스크립트 | 하는 일 |
|---|---|
| `emu.py` | 에뮬레이터 래퍼. ROM+세이브로 켜기, 키 입력, 프레임 진행, 메모리 읽기·쓰기, 스크린샷, `boot_continue()`(타이틀→이어하기, "지난 이야기" 건너뛰기, 이어하기 뒤 리셋 감지) |
| `gamedata.py` | 구조체 오프셋(헤더를 devkitARM gcc로 컴파일해 얻음, `.cache/`에 보관), C 상수(`FLAG_*`·`VAR_*`·`MAP_*`…), 맵 목록, ROM 표(종족값·경험치 표) |
| `savefile.py` / `savedit.py` | 세이브 읽고 쓰기. `savedit.py IN.sav -o OUT.sav warp Route110 @0 flag FLAG_X 1 var VAR_Y 2 trainer TRAINER_Z 1 strong 0 70 day 1 dex PIKACHU coins 2000 info`. v0.9.0에 더함: `lead 5`(그 칸을 선두로), `party 1`(앞 N마리만), `hp 0 1`, `hour 22`(게임 시계를 다음 22:00으로), `money N`, `item ITEM_X N`, `fillitems [ITEM_…]`(도구 칸의 빈칸을 다른 도구로 채움, 적은 도구는 빼고), `fillboxes`(PC 빈칸 전부). 에뮬레이터에는 RTC가 없어 게임 시계는 가상 시계(`lastBerryTreeUpdate` 오프셋)다. `day`·`hour`는 이쪽을 바꾼다 |
| `refroms.sh` | 세이브 검사용 기준 ROM을 태그에서 빌드해 `qa-base/<tag>/`에 둔다. gh로 로그인돼 있으면 그 태그 릴리스의 BPS와 바이트 단위로 대조한다 |
| `savetest.py` / `savetest_all.sh` | 세이브 호환: 세이브를 저장한 릴리스 ROM과 현재 ROM에서 각각 메인 메뉴까지 켜서 SaveBlock1·2·PC 보관함을 바이트 단위로 비교(IDENTICAL), 이어서 현재 ROM으로 이어하기가 제자리에서 도는지 확인 |
| `mapsmoke.py` | 맵 전부(896개)에 세이브를 워프시켜 이어하기 → 멈춤·검은 화면·리셋·다른 맵으로 튕김을 잡는다. 맵의 모든 오브젝트가 한 번씩 화면에 들어오도록 출발점을 여러 개 잡는다(`--quick`은 하나). 약 80분(`-j 2`) |
| `eventcheck.py` | 이벤트 실행 검사. JSON 한 줄에 세이브 수정·키 입력·스크린샷·기대값(플래그·변수·트레이너·맵·전투 여부·돈·가방 수량·알·운명적 만남 비트). `mash N`은 전투·대사가 끝나 조작이 풀릴 때까지 A를 누른다. `"xfail": true`는 실패해야 통과하는 대조군. 예: `cases/z2.jsonl`, `cases/rocket.jsonl` |
| `textaudit.py` | 구역별로 아직 에메랄드 원문 그대로인 대사(도달 가능한 것만)를 센다. 표지판·울음소리처럼 바꿀 필요가 없는 것은 따로 분류 |
| `textwidth.py` | 모든 맵 대사의 한 줄 폭을 게임 글꼴 폭으로 계산해 208px 초과를 찾는다 |
| `dexcheck.py` | 386종이 모두 게임 안에서 얻을 수 있는지 정적으로 확인 |
| `bps.py` | BPS 패치 적용 |

세이브 검사 대상과 기준 릴리스(세이브 날짜와 릴리스 날짜로 정함):

| 세이브 | 기준 |
|---|---|
| `saves/v0.1.0.sav` | v0.1.0 |
| `saves/v0.2.1.sav` | v0.2.1 |
| `saves/pokemonthyl_v3.gba.sav` (사용자 세이브) | v0.3.0 |
| `saves/v0.5.1.sav` | v0.5.1 |
| `saves/hoenn.sav` | v0.7.0 |

### 단계마다 돌리는 것

```sh
tools/qa/savetest_all.sh                       # 5종 모두 OK (load IDENTICAL)
python3 tools/check_map_integrity.py           # ERROR 0
python3 tools/check_event_wiring.py
python3 tools/qa/mapsmoke.py -j $(nproc)       # RESET·BLACK·TIMEOUT·ERROR 0 (BATTLE은 참고)
python3 tools/qa/eventcheck.py tools/qa/cases/z2.jsonl --shots /tmp/ec
python3 tools/qa/eventcheck.py tools/qa/cases/rocket.jsonl --shots /tmp/ec
python3 tools/qa/textaudit.py --zone Z2 --fail
python3 tools/qa/textwidth.py
python3 tools/qa/dexcheck.py
```

도구가 실제로 잡는지 대조군으로 확인해 두었다: v0.2.1 ROM에서 `mapsmoke.py Route104 Route102 Route111`은 셋 다 RESET(나무열매 자리 오브젝트 버그), `savetest.py saves/hoenn.sav:v0.7.0 --rom qa-base/v0.1.0/pokemonthyl.gba`는 FAIL, `cases/z2.jsonl`의 xfail 사례는 실패해야 통과한다.

### 공략집 확인

`soffice --headless --convert-to pdf docs/Thunder_Yellow_Walkthrough_vX.Y.Z.docx`로 PDF를 만들고 `pdftoppm -png`로 쪽 이미지를 뽑아 볼 수 있다. 글꼴은 Malgun Gothic 대신 Noto CJK로 대체되므로 줄바꿈 위치는 Word와 조금 다르다.
