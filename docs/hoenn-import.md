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
| 2-8 지역 지도·날기 | 호연 지역 지도(28×15 격자)와 호연 안에서의 FLY, 도시 방문 플래그 | (이 커밋) |

## 세이브 호환

`saves/v0.1.0.sav` 로드 테스트는 매 단계 IDENTICAL이다. 새 저장 공간은 모두 FRLG가
쓰지 않던 자리에서 가져왔다.

- 트레이너 격파 플래그: `gSaveBlock2Ptr->hoennTrainerFlags[0x80]` (옛 `filler_B20`)
- 호연 플래그(아이템볼 등): `gSaveBlock2Ptr->hoennFlags[0x100]`, `HOENN_FLAGS_START`부터. `GetFlagAddr`가 처리
- 숨은 아이템: FRLG가 쓰는 191개 뒤의 빈 플래그. 맵 데이터의 id 폭을 8→14비트로 넓혔다(ROM 데이터)
- 회복 지점: 세이브는 맵과 좌표를 저장하므로 표에 추가해도 영향 없음

## 지역 지도와 날기

- `tools/hoenn_import/import_region_map.py`가 에메랄드의 8bpp 지도를 FRLG 형식
  (4bpp 타일 + 30×20 타일맵 + 팔레트 5개)으로 변환한다. FRLG 코드가 팔레트 0번
  색과 2번 팔레트를 덮어쓰기 때문에, 지도 색은 각 팔레트의 1~14번에만 넣는다.
- `src/region_map.c`에 `REGIONMAP_HOENN`을 추가했다. 지도마다 격자 크기·화면
  원점·CANCEL 버튼 칸이 다르므로 `sRegionMapGeometry` 표로 분리했다(칸토 22×15,
  호연 28×15). CANCEL 버튼은 FRLG 것을 호연 남동쪽 바다에 옮겨 그렸다.
- 도시에 발을 들이면 `FLAG_HOENN_WORLD_MAP_*`가 서고, 그 도시가 날기 목적지가
  된다. 이 플래그는 호연 플래그 영역 위쪽(`HOENN_FLAGS_START + 0x400`)에 있어
  아이템 플래그와 겹치지 않는다.

## 남은 것

- 지역을 넘는 이동은 여전히 비행기뿐이다(설계). 호연 지도에는 칸토 목적지가 없고
  칸토 지도에도 호연이 없다. 공항 안내원과 카이나 항구 선원이 이를 알려준다.
- 스토리 이벤트(아쿠아·마그마단, 체육관 배지, 전설 포켓몬)는 아직 없다. 맵의 NPC는
  원작의 첫 대사만 말한다.
- 비밀기지, 컨테스트, 배틀 프런티어 기능, 나무열매 재배는 이식하지 않았다.

## 릴리스 패치 만들기

`pokemonthyl.bps`는 정품 LeafGreen(영문 v1.0)에서 이 빌드로 가는 차이분이다.
기준 ROM은 `baserom_leafgreen.gba`로 둔다 — `make clean`이 `poke*.gba`를 모두
지우므로 `pokeleafgreen.gba`라는 이름으로 두면 빌드 산출물과 함께 사라진다.

기준 ROM이 없으면 디컴파일 자체로 다시 만들 수 있다. pret/pokefirered는 정품
카트리지를 바이트 단위로 재현하기 때문이다.

```
git worktree add /tmp/base upstream/master
ln -s "$PWD/tools/agbcc" /tmp/base/tools/agbcc
make -C /tmp/base leafgreen -j"$(nproc)"
(cd /tmp/base && sha1sum -c leafgreen.sha1)     # pokeleafgreen.gba: OK
cp /tmp/base/pokeleafgreen.gba baserom_leafgreen.gba
python3 tools/make_bps_patch.py
```
