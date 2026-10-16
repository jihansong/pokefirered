# 호연 Z3 데봉 도난·피코 구출 패치 사전 검토

판정: **정적 검사 통과 / ROM 실행 검증 대기**. 이 문서는 에뮬레이터 통과 보고가 아니다.

기준 커밋은 `658baf740cff568cba7f3300f688b8a626e6f5fc`이다. 원규 보상과 Lavender 수정은 별도 작업이며 이 패키지에서 덮어쓰지 않는다.

| 검사 | 실제 결과 |
|---|---|
| canonical patch 재생성 | 3맵에 2회 적용한 결과 동일 |
| git apply --check | 전달받은 최신 9개 맵 파일에 적용 가능 |
| 기존 맵 보존 | 기존 오브젝트 순서·좌표, 워프, 연결, 레이아웃 보존; 새 바위 없음 |
| 새 대사 폭 | 15라벨·43줄, 208px 초과 0; 로컬 v0.10.0 글꼴 표 기준 |
| 스크립트 참조 | 새 참조 32개, 미해결 0; 생성된 라벨 중복 0 |
| 지급 실패 분기 | 용량 부족 시 퀘스트 완료/수령 플래그를 기록하지 않음 |
| 배 위치 호환 | 피코를 이미 구한 세이브의 기존 배 위치는 유지 |
| 실행 테스트 | JSONL 29개 작성, 아직 실행하지 않음 |

`z3_devon.jsonl`은 체육관/숲 미완료, 도난·재진입, 오래된 승리 기록, 물건 중복, 키 아이템 주머니 만석 및 빈칸 1개 재시도, 전투 승리·패배·전투 전 미지급, 네 방향에서 단원에게 말 걸기, 슈퍼볼 만석/재시도/중복, 기존 하기노인 배 조건과 음성 대조군을 포함한다.

실제 `saves/hoenn.sav`의 파티 1번은 이상해풀이고 기술 순서는 잎날가르기(75), 덩굴채찍(22), 풀베기(15), 달콤한향기(230)임을 원격 조회로 확인했다. 승리 fixture는 이 개체를 100레벨로 강화하고 선두로 옮긴다. 기술을 바꾸지 않으며 종족과 잎날가르기 보유를 테스트에서 검사한다. 이것만으로 승리가 검증된 것은 아니다.

`fillitems`는 일반 도구 주머니만 채우므로 데봉 소포 검사에 사용하지 않는다. `prepare_z3_devon.py`는 원본을 변경하지 않고 `tools/qa/.cache/z3_devon/`에 실제 키 아이템으로 주머니를 채운 복사 세이브 두 개를 만든다. 원본 SHA-256 불변과 다시 읽은 빈칸 수를 확인한다.

원격 적용 후 필요한 실행:

```sh
make leafgreen -j$(nproc)
make GAME_VERSION=LEAFGREEN syms
tools/qa/savetest_all.sh
python3 tools/qa/prepare_z3_devon.py
python3 tools/qa/eventcheck.py tools/qa/cases/z3_devon.jsonl --shots docs/team/qa/codex-z3-devon-2026-10-01
python3 tools/qa/mapsmoke.py RustboroCity Route116 RusturfTunnel
python3 tools/check_map_integrity.py
python3 tools/check_event_wiring.py
python3 tools/qa/textwidth.py data/maps/RustboroCity data/maps/Route116 data/maps/RusturfTunnel
python3 tools/qa/dexcheck.py
```

실제 화면에서 도난 이동, 단원 도주, 피코 귀환, 모든 접근 방향의 조작 복귀를 확인해야 한다. 기존 경고와 새 경고는 적용 전후를 대조한다. 현재 세 맵의 미각색 대사는 남아 있으므로 Z3 전체 textaudit를 완료했다고 보고하지 않는다.

다음 이야기인 데봉 사장 의뢰 → STERN 선장 배달 → 학습장치, Wanda와 남자친구의 재회 장면, 116번도로 리피트볼 보상은 이 패키지에서 아직 구현하지 않았다.
