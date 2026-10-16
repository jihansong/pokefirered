# Route116 DEVON 리피트볼 보상 검증

판정: PASS-WITH-NOTES

소포를 회수한 뒤 116번 도로 (46,11)의 데봉 사원에게 리피트볼 1개를 받는다. 수령 기록은 실제 지급 성공 뒤에만 설정한다. 재대화 중복 지급이 없으며 999개 상한에서는 보류하고 공간 확보 후 수령한다. 후기 진행 세이브도 놓친 보상을 받을 수 있다.

원작 좌표를 복원하고 이미 이식된 DEVON_EMPLOYEE 그래픽을 사용했다. 기존 BRINEY 이벤트와 세이브 구조는 유지한다.

| 검사 | 결과 |
|---|---|
| events | 9/9 cases passed |
| devon-regression | 29/29 cases passed |
| save-compat | pokemonthyl_hoenn_QAed.sav       vs v0.8.0  OK  (load IDENTICAL) |
| map-integrity | - NOTE: 896 maps in 76 groups, 735 layouts |
| map-smoke | 1 maps: OK 1 |
| text-width | 0 line(s) over 208 px, 0 to check by hand ({STR_VAR_n}) |
| dex | 386/386 obtainable (leafgreen, Hoenn maps: open, direct sources 256) |
| Build / syms | exit 0 / 0 |
| Original saves / other source changes | unchanged |
| Patch regeneration | idempotent |

기존 ROM에서는 실제 상호작용 뒤 리피트볼 0개 및 수령 플래그 0으로 누락을 재현했다(baseline-reward-only.log). 초기 watch 기반 검사는 새 텍스트 심볼이 없어 기준선으로 쓰지 않았다.

제한: 기존 빌드 경고 5건(jobserver 4, RWX 1), 기존 이벤트 연결 검토 항목 91건은 남아 있다. 신규 연결 경고 0건. Z3 전체 대사 개작과 다른 미완료 작업이 끝났다는 뜻은 아니다. DELTA 실기 확인은 하지 않았다.

화면: shots/z3_repeat_first_and_no_duplicate_result.png (실제 mGBA 240x160; 사원 위치와 캐릭터 표시 확인).
