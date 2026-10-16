# 데봉 소포 배달 — 실행 결과 검수

2026-10-01 · **PASS-WITH-NOTES** · 대상 HEAD `658baf740cff568cba7f3300f688b8a626e6f5fc`의 미커밋 패치.

사장의 배달 의뢰 → 기존 항구 STERN에게 소포 전달·다이브볼 3개 → 사장에게 복귀·학습장치 수령 흐름을 원격 빌드와 mGBA 이벤트 검사로 확인했다. 가방 만석 재시도, 이미 진행한 세이브의 기록 복구, 중복 보상 방지, STERN의 기존 스캐너 의뢰 유지도 통과했다.

| 검사 | 실제 결과 |
|---|---|
| canonical 재생성 | 2회 모두 종료 0, 생성물 해시 동일 |
| LeafGreen 빌드 / 심볼 | 종료 0 / 0. 경고는 아래 별도 기록 |
| 신규 배달 이벤트 | **29/29**. 실패해야 통과하는 대조군 1개 포함 |
| 기존 소포 회수·피코 구출 회귀 | **29/29** |
| 원규 보상 회귀 | **10/10** |
| 릴리스 기준 세이브 호환 | **6/6 load IDENTICAL** |
| 원본 저장 파일 보존 | 원격 runner의 전후 해시 비교상 **11개 .sav 모두 동일**. 호환 검사 6개와 별개로 백업 5개 포함 |
| 보호 소스 보존 | `result.json`의 보호 경로 모두 동일, 변경 0. Lavender·타이틀 소스 포함 |
| 맵 스모크 | **2맵 OK**: 데봉 3층·카이나 항구 |
| 맵 무결성 | **0 ERROR, 2 WARN**. 기존 데봉 패치 검사 로그와 바이트 동일 |
| 이벤트 배선 | 적용 전후 로그 바이트 동일. 기존 **91건**, 신규 0 |
| 대사 폭 | 생성된 2파일·36라벨·151줄, **208px 초과 0** |
| Z2 대사 감사 `--fail` | 종료 0, 수정 필요 0 |
| Z3 대사 감사 | 52맵·531대사 중 **167개 재작성 필요**. 전체 Z3 대사 작업은 미완료 |
| 도감 획득 경로 | **386/386**, 정적 검사 통과 |

## 남은 사항과 검증 한계

- **engineer / minor — 기존 빌드 경고**: jobserver 경고 4줄과 RWX LOAD segment 경고 1줄이 남는다. 빌드 성공을 무경고 빌드로 보고하지 않는다. 재현: `make leafgreen -j$(nproc)`.
- **engineer / minor — 기존 점검 경고**: 배선 91건 및 맵 공유 숨김 플래그 경고 2건은 이전과 같다. 신규 배달 패치에서 늘어난 항목은 없다.
- **planner·engineer / major(전체 Z3 완료 기준)**: Z3 대사 167개 재작성은 별도 후속 범위다. 재현: `python3 tools/qa/textaudit.py --zone Z3`. 이 보고서는 소포 배달 구간만 통과 판정한다.
- 사장/항구 이벤트 종료 및 맵 스모크 등 대표 스크린샷 **10장**을 직접 열어 접근 위치와 정상 필드 복귀를 확인했다. 이벤트 캡처는 대화를 닫은 뒤 화면이라 대사·수량 자체의 시각적 증명은 아니다. 지급 수량·플래그·반복 대화 결과는 이벤트 검사 로그로 확인했다.
- 검수 담당은 내려받은 실제 로그·결과·스크린샷을 독립적으로 읽었다. 이번 검수에서 원격 테스트를 다시 실행하거나 원격 세이브를 다시 읽지는 않았다. DELTA 앱 직접 플레이, 배포 ROM 검증, 전체 Z3 플레이 완료를 의미하지 않는다.

## 증거

원격·로컬 공통 상대 경로: `docs/team/qa/codex-z3-devon-delivery-2026-10-01/`

- 실행 판정: `result.json`, `events.log`, `devon-regression.log`, `roxanne-regression.log`, `saves.log`.
- 사장 접근: `events/z3_delivery_stone_accepts_recovered_parcel_result.png`.
- STERN 전달 후: `events/z3_delivery_stern_delivery_three_balls_result.png`.
- 학습장치 수령 후: `events/z3_delivery_stone_exp_share_once_result.png`.
- 만석·기존 의뢰 유지: `events/z3_delivery_stern_full_balls_do_not_block_scanner_result.png`.
- 배선 전후 SHA256 동일: `a79bc270cbd4a9c37116597e3092fda5da45ce30aed050960c152c087b2b3c5a`.
- 맵 무결성 로그는 이전 `codex-z3-devon-2026-10-01/map-integrity.log`와 동일: `6e0f150bbfb9a0ae6ea6701af54991c12ab7d6c128d06788bb39e81e5fd2e77f`.

패키지·게임 소스·세이브·원격 파일은 이 검수에서 수정하지 않았다.
