# QA 보고서 — <단계> #<n> (<날짜>)

대상: <브랜치/커밋 범위> · 판정: **PASS / FAIL / PASS-WITH-NOTES**

## 안정성

| 검사 | 명령 | 결과 |
|---|---|---|
| 빌드 | `make leafgreen` | 경고 0 / … |
| 세이브 호환 | `tools/qa/savetest_all.sh` | 5종 OK (load IDENTICAL) |
| 맵 무결성 | `tools/check_map_integrity.py` | ERROR 0 |
| 이벤트 배선 | `tools/check_event_wiring.py` | 새 빈 약속 0 |
| 맵 스모크 | `tools/qa/mapsmoke.py …` | RESET·BLACK·TIMEOUT·ERROR 0 |
| 이벤트 실행 | `tools/qa/eventcheck.py …` | n/n (대조군 포함) |
| 대사·글자 폭·도감 | `textaudit` / `textwidth` / `dexcheck` | … |

## 플레이 점검

(무엇을 어떻게 해 봤는지, 스크린샷 경로)

## 품질 판단

재미 · 난이도 · 보상 · 차별성 · 서사 일관성 — 각각 한두 줄과 근거.

## 피드백

| # | 담당 | 심각도 | 내용 | 재현 |
|---|---|---|---|---|
| 1 | engineer | blocker | … | `savedit … ; eventcheck …` |

## 확인하지 못한 것

