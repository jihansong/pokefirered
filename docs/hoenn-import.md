# 호연 지역 이식 현황 (regions 브랜치)

pokeemerald에서 호연 전체를 가져오는 작업의 진행 상황이다. 목표는 "원작 맵 그대로,
세이브 호환을 깨지 않고"이며, 모든 단계는 `tools/hoenn_import/`의 스크립트로 재생성된다.

## 재생성 순서

```
python3 tools/hoenn_import/import_objevent_gfx.py   # NPC 스프라이트
python3 tools/hoenn_import/import_music.py          # 음악
python3 tools/hoenn_import/import_trainers.py       # 트레이너 데이터
python3 tools/hoenn_import/import_maps.py           # 맵·레이아웃·타일셋·NPC·아이템·트레이너 배치
python3 tools/hoenn_import/import_tileset_anims.py  # 타일셋 애니메이션 (맵 뒤에)
python3 tools/hoenn_import/import_heal_locations.py # 회복 지점 (맵 뒤에)
rm -f build/leafgreen/data/maps.o build/leafgreen/data/map_events.o build/leafgreen/data/event_scripts.o
make leafgreen -j$(nproc)
```

`make`가 `.incbin`·상수 의존을 추적하지 못해, 임포트 뒤에는 위 오브젝트를 지워야 한다.

## 완료

| 단계 | 내용 | 커밋 |
|---|---|---|
| 1 지형 | 맵 457개, 레이아웃, 연결, 워프, 야생 포켓몬 표, 타일셋 63개(에메랄드 512타일 분할을 엔진이 인식) | abf9b1020 |
| 2-1 스프라이트 | 호연 고유 인물·포켓몬·탈것 59종. `OBJ_EVENT_GFX`가 u8이라 일반 주민은 FRLG 대역 유지 | 74f670c90 |
| 2-2 음악 | 곡 49개와 보이스그룹·키스플릿·샘플. mid2agb가 이름형 보이스그룹도 받도록 수정 | c1b9ba909 |
| 2-3 타일셋 애니 | 물·꽃·분수·깃발·풍선 등 24개 타일셋 | 2c562bd3e |
| 2-4 트레이너 | 트레이너 520명(맵 배치 422명). 격파 플래그는 SaveBlock2 여유 공간 | 89b56b874 |
| 2-5 아이템 | 아이템볼 162개, 숨은 아이템 110개 | 528887779 |
| 2-6 회복 지점 | 회복 지점 22곳, 포켓몬센터 15곳이 리스폰 설정 | 528d368cc |
| 2-7 behavior | 다리·통나무·나무다리 통행, 자전거 지형·비밀기지 자리 정리 | 7c39b6c72 |

## 세이브 호환

`saves/v0.1.0.sav` 로드 테스트는 매 단계 IDENTICAL이다. 새 저장 공간은 모두 FRLG가
쓰지 않던 자리에서 가져왔다.

- 트레이너 격파 플래그: `gSaveBlock2Ptr->hoennTrainerFlags[0x80]` (옛 `filler_B20`)
- 호연 플래그(아이템볼 등): `gSaveBlock2Ptr->hoennFlags[0x100]`, `HOENN_FLAGS_START`부터. `GetFlagAddr`가 처리
- 숨은 아이템: FRLG가 쓰는 191개 뒤의 빈 플래그. 맵 데이터의 id 폭을 8→14비트로 넓혔다(ROM 데이터)
- 회복 지점: 세이브는 맵과 좌표를 저장하므로 표에 추가해도 영향 없음

## 남은 것

- **호연 안에서의 날기**: 호연에서 FLY를 쓰면 칸토 지역 지도가 열려 칸토로 돌아온다.
  호연 도시로 날려면 에메랄드의 지역 지도(8bpp 배경, 자체 타일맵, MAPSEC 배치)를
  이식하고 REGIONMAP_HOENN을 추가해야 한다. 공항 안내원과 카이나 항구 선원이 이
  사실을 알려준다.
- 스토리 이벤트(아쿠아·마그마단, 체육관 배지, 전설 포켓몬)는 아직 없다. 맵의 NPC는
  원작의 첫 대사만 말한다.
- 비밀기지, 컨테스트, 배틀 프런티어 기능, 나무열매 재배는 이식하지 않았다.
