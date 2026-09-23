# 도감 서식지·도감 정보 정리

Thunder Yellow(leafgreen 빌드)의 도감에서 (1) 야생에서 잡을 수 있는 포켓몬은 모두 분포(서식지) 화면에 나오게 하고, (2) 도감에 등록된 포켓몬은 키·몸무게·분류·설명·특성을 보여 주고, (3) 이 해킹이 새로 야생에 넣은 포켓몬이 아무 데나 흩어져 나오지 않도록 원작을 근거로 서식지를 다시 정한 작업의 기록이다. 새 야생 배치의 목록은 `docs/dex-completion.md` 5·6절을 대신한다.

## 1. 현황 (작업 전, v0.4.0)

### 1.1 분포 화면

FR/LG의 분포 화면(`src/wild_pokemon_area.c`)은 `gWildMonHeaders`(v0.3부터 아침·밤 표 포함)를 훑어 그 맵의 MAPSEC을 칸토·세비 제도 지도의 표시 칸(DEX_AREA)으로 바꾼다. 이 방식으로는 다음 포켓몬의 서식지가 나오지 않았다.

| 원인 | 해당 포켓몬 |
|---|---|
| 호연 맵(에메랄드 야생표 457맵)은 칸토 지도에 대응 칸이 없어 전부 무시됨. 야생표가 호연에만 있는 26종은 "서식지 불명" | Altaria, Banette, Cascoon, Claydol, Electrode, Hariyama, Lairon, Linoone, Lombre, Loudred, Manectric, Mightyena, Minun, Nuzleaf, Octillery, Pelipper, Pikachu, Plusle, Quagsire, Sharpedo, Silcoon, Swellow, Wailord, Whiscash, Wynaut, Xatu (호연에도 사는 98종은 칸토 쪽만 표시) |
| 알터링 동굴은 "오늘의 세트" 하나만 검사함. 순환 세트의 8종은 자기 차례인 날 말고는 서식지 불명 | Aipom, Houndour, Mareep, Pineco, Shuckle, Smeargle, Stantler, Teddiursa |
| 숨겨진 공터(Hidden Grotto)·벌레잡기 대회는 야생표 밖이라 검사 안 됨 | Mr. Mime(공터에서만), Butterfree(대회에서만). 공터·대회에만 있는 서식지(상록숲 공터의 Scyther 등)도 빠짐 |
| 4~7의섬이 열리기 전에는 그 섬의 서식지를 그리지 않음(원작 동작) | Bagon, Baltoy, Delibird, Heracross, Hoppip, Lapras, Larvitar, Luvdisc, Murkrow, Qwilfish, Sableye, Skarmory, Sudowoodo, Surskit, Wooper 등 30종이 섬이 열리기 전에는 불명 |
| 낚시표를 12칸(풀숲 크기)으로 읽는 원작 버그(`BUGFIX` 미정의) | 10칸 뒤의 엉뚱한 메모리를 읽어 드물게 잘못된 표시가 생길 수 있음 |

배회 전설(라이코·앤테이·스이쿤·라티오스·라티아스)은 원작처럼 지금 있는 위치 하나만 표시되며, 이번 작업에서도 그대로 둔다.

### 1.2 도감 설명 페이지

- 분류·키·몸무게는 **잡은** 포켓몬만 보이고, 본 것만 있으면 `?????`·`??'??"`·`????.? lbs`로 나온다. 설명문도 잡은 포켓몬만 나온다.
- 분포 페이지의 타입 아이콘과 크기 비교(트레이너와 나란히 선 실루엣)도 잡은 포켓몬만 나온다.
- 특성은 도감 어디에도 나오지 않는다.

v0.4.0에서는 전국도감 1~386번이 모두 게임 안에서 입수 가능하므로(`docs/dex-completion.md`), "입수 가능한 포켓몬"은 도감에 나오는 모든 종이다(미싱노는 도감에 등록되지 않는다).

### 1.3 이 해킹이 새로 야생에 넣은 포켓몬

`docs/dex-completion.md` 5·6절(61+23칸)과 시간대 시스템(로드맵 2의 9번)의 아침·밤 표를 v0.4.0의 `src/data/wild_encounters.json`과 비교했다. 문제는 두 가지였다.

- **칸토 5절**: 맵마다 한 종씩, 대부분 4%(가끔 1%) 칸에 넣어서 원작의 흔함·드묾과 상관없이 모두 비슷한 확률이었다(예: 101번 도로에서 가장 흔한 지그제구리도, 1% 희귀종인 에나비도 4%). 원작에서 칸토에 살던 2세대 포켓몬(블루, 해너츠 등)도 HGSS·크리스탈의 칸토 위치가 아닌 곳에 있거나, 낮 전용인데 밤에도 나왔다.
- **아침·밤 표**: 레디바가 칸토 15개 도로의 아침 1% 칸과 상록숲 아침 45%에, 부우부·야부엉이 14개 도로의 밤에 들어가 있었는데, HGSS·크리스탈에서 레디바는 2번 도로 아침에만, 부우부는 1·2·5·25번 도로와 상록숲 밤에만 나온다. 페이검도 원작의 2번 도로가 아닌 상록숲에 있었다.

## 2. 방침

1. 칸토 맵의 낮 표는 옐로 표를 그대로 둔다. 새 종은 **같은 표 안에 같은 종이 또 있는 칸**만 차지하므로 옐로에 있던 종은 모두 그대로 나온다(도구가 검사한다). 세비 제도·불씨산은 리프그린 표에서 기존 종을 모두 남기는 선에서 바꾼다.
2. 2세대 포켓몬은 HGSS(없으면 크리스탈)의 **칸토** 위치·시간대를 따른다. 아침·밤 표는 HGSS처럼 낮 표의 일부 칸만 바꾼 사본이다(예: 밤에는 구구 칸이 부우부).
3. 옐로에 없던 1세대 포켓몬은 레드·그린·블루·파이어레드·리프그린의 위치를 따른다.
4. 3세대 포켓몬(칸토 맵에 원작 위치가 없음)은 직접 정한다. 원작 서식지와 **닮은 지형**(숲 ↔ Petalburg Woods, 터널 ↔ Rusturf Tunnel, 묘지 탑 ↔ Mt. Pyre, 얼음 동굴 ↔ Shoal Cave, 유성의 산 ↔ Meteor Falls 등)에, **비슷한 레벨대**로, 원작에서 흔했으면 9~15%, 보통이면 4~5%, 드물었으면 1%로 넣는다. HGSS "호연의 소리"(라디오)로 칸토에 나오는 종은 그 위치를 근거로 쓴다.
5. 전설·환상은 야생표에 넣지 않는다(1회성 이벤트 유지). 호연 맵의 에메랄드 야생표는 바꾸지 않는다.
6. 필드 현상(흔들리는 풀숲·물보라·먼지, `src/wild_encounter.c`)에서만 나오는 종이 없어야 한다. 필드 현상의 종은 이브이·켄타로스(풀숲), 미뇽·잉어킹(물), 럭키(먼지)이며, 모두 아래 표나 원래 표에 일반 서식지가 있다(이브이 7·8번 도로·5의섬 목초지, 켄타로스·럭키·미뇽 사파리존, 잉어킹 낚시 전역).

배치의 원본은 `tools/dex_habitat/habitats.py`이고, `tools/dex_habitat/apply_habitats.py`가 칸토·세비 제도의 표를 작업 전(dex 완성 전) 옐로·리프그린 표로 되돌린 뒤 이 목록을 다시 적용해 `src/data/wild_encounters.json`을 만든다(`--table`로 아래 표를 출력).

## 3. 새 서식지 표

칸 번호와 확률: 풀숲 0~11 = 20·20·10·10·10·10·5·5·4·4·1·1%, 파도타기·바위깨기 0~4 = 60·30·5·4·1%, 낚시 0~1 낡은낚싯대(70·30%), 2~4 좋은낚싯대(60·20·20%), 5~9 대단한낚싯대(40·40·15·4·1%). "칸 그대로"는 원래 칸의 레벨을 쓴다는 뜻이다. 근거 칸의 "직접 선택"은 2절 4번 규칙으로 고른 것이고, 뒤의 게임·장소·확률은 그 선택의 참고가 된 원작 서식지다.

| 포켓몬 | 맵 | 방식 | 시간대 | 칸(확률) | 레벨 | 근거 |
|---|---|---|---|---|---|---|
| Wurmple | `VIRIDIAN_FOREST` | 풀숲/동굴 | 하루 종일 | 6,9 (9%) | 칸 그대로 | 직접 선택: 숲 = Emerald Petalburg Woods 25%, Route 101 45% |
| Shroomish | `VIRIDIAN_FOREST` | 풀숲/동굴 | 하루 종일 | 8 (4%) | 6 | 직접 선택: Emerald Petalburg Woods 15% |
| Slakoth | `VIRIDIAN_FOREST` | 풀숲/동굴 | 하루 종일 | 11 (1%) | 6 | 직접 선택: Emerald Petalburg Woods 5%(드묾) |
| Hoothoot | `VIRIDIAN_FOREST` | 풀숲/동굴 | 밤 | 0,4,5 (40%) | 칸 그대로 | HGSS Viridian Forest 밤 80% |
| Noctowl | `VIRIDIAN_FOREST` | 풀숲/동굴 | 밤 | 10 (1%) | 칸 그대로 | HGSS Viridian Forest 밤 15% |
| Zigzagoon | `ROUTE1` | 풀숲/동굴 | 하루 종일 | 7,9 (9%) | 3 | 직접 선택: 첫 도로 = Emerald Route 101-103 10-20% |
| Hoothoot | `ROUTE1` | 풀숲/동굴 | 밤 | 0,1,4,5,6,8,10,11 (71%) | 칸 그대로 | HGSS·Crystal Route 1 밤 45%(밤에는 구구 자리) |
| Poochyena | `ROUTE2` | 풀숲/동굴 | 하루 종일 | 2,9 (14%) | 3-4 | 직접 선택: Emerald Route 104 40% |
| Taillow | `ROUTE2` | 풀숲/동굴 | 아침·낮 | 8,11 (5%) | 5 | 직접 선택: Emerald Route 104 10%(낮에 나는 새) |
| Ledyba | `ROUTE2` | 풀숲/동굴 | 아침 | 1,5 (30%) | 칸 그대로 | SoulSilver·Crystal Route 2 아침 30% |
| Hoothoot | `ROUTE2` | 풀숲/동굴 | 밤 | 1,5,8 (34%) | 칸 그대로 | HGSS·Crystal Route 2 밤 50-60% |
| Noctowl | `ROUTE2` | 풀숲/동굴 | 밤 | 10,11 (2%) | 7 | HGSS·Crystal Route 2 밤 14-15% |
| Spinarak | `ROUTE2` | 풀숲/동굴 | 밤 | 3,4 (20%) | 칸 그대로 | HeartGold·Crystal Route 2 밤 30% |
| Nincada | `ROUTE3` | 풀숲/동굴 | 하루 종일 | 7,9 (9%) | 9-10 | 직접 선택: 회색시티 동쪽 = Emerald Route 116(Rustboro 동쪽) 20% |
| Skitty | `ROUTE3` | 풀숲/동굴 | 하루 종일 | 11 (1%) | 9 | 직접 선택: Emerald Route 116 2%(드묾) |
| Ekans | `ROUTE4` | 풀숲/동굴 | 하루 종일 | 9,11 (5%) | 10-12 | Red·FireRed Route 4 25%, SoulSilver·Crystal 20% |
| Snubbull | `ROUTE5` | 풀숲/동굴 | 아침·낮 | 4 (10%) | 14-16 | Crystal Route 5 아침·낮 30% |
| Hoothoot | `ROUTE5` | 풀숲/동굴 | 밤 | 0,3,5 (40%) | 칸 그대로 | Crystal Route 5 밤 30% |
| Noctowl | `ROUTE5` | 풀숲/동굴 | 밤 | 6 (5%) | 칸 그대로 | Crystal Route 5 밤 20% |
| Snubbull | `ROUTE6` | 풀숲/동굴 | 아침·낮 | 4 (10%) | 14-16 | Crystal Route 6 아침·낮 30% |
| Lotad | `ROUTE6` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 14 | 직접 선택: 연못가 풀숲 = Sapphire Route 102(연못) 20%·114 30% |
| Barboach | `ROUTE6` | 대단한낚싯대 | 하루 종일 | 7 (15%) | 15-20 | 직접 선택: 연못 = Emerald Route 111·114 낚시(흔함) |
| Vulpix | `ROUTE7` | 풀숲/동굴 | 하루 종일 | 7,9 (9%) | 18-20 | LeafGreen Route 7 10%, SoulSilver 25% |
| Eevee | `ROUTE7` | 풀숲/동굴 | 하루 종일 | 11 (1%) | 22 | 직접 선택(원작 야생 없음): 무지개시티(이브이 선물) 옆 도로 1% |
| Murkrow | `ROUTE7` | 풀숲/동굴 | 밤 | 0 (20%) | 칸 그대로 | HeartGold Route 7 밤 35%, Crystal 30% |
| Houndour | `ROUTE7` | 풀숲/동굴 | 밤 | 1 (20%) | 칸 그대로 | Crystal Route 7 밤 20%, SoulSilver 5% |
| Snubbull | `ROUTE8` | 풀숲/동굴 | 아침·낮 | 7,9 (9%) | 17-20 | Crystal Route 8 아침·낮 30% |
| Vulpix | `ROUTE8` | 풀숲/동굴 | 하루 종일 | 4 (10%) | 15-18 | LeafGreen Route 8 20%, SoulSilver 10% |
| Eevee | `ROUTE8` | 풀숲/동굴 | 하루 종일 | 11 (1%) | 22 | 직접 선택(원작 야생 없음): 무지개시티 옆 도로 1% |
| Noctowl | `ROUTE8` | 풀숲/동굴 | 밤 | 0,5 (30%) | 칸 그대로 | HeartGold Route 8 밤 40%, Crystal 30% |
| Gulpin | `ROUTE9` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 18 | 직접 선택: Emerald Route 110 15% |
| Electrike | `ROUTE10` | 풀숲/동굴 | 하루 종일 | 3,9 (14%) | 16-18 | 직접 선택: 무인발전소 앞 = Emerald Route 110·118(Mauville 근처) 30% |
| Ekans | `ROUTE11` | 풀숲/동굴 | 하루 종일 | 2,9 (14%) | 15-17 | FireRed Route 11 40%, Red Route 11 |
| Noctowl | `ROUTE11` | 풀숲/동굴 | 밤 | 6,7 (10%) | 칸 그대로 | Crystal Route 11 밤 10% |
| Carvanha | `ROUTE12` | 대단한낚싯대 | 하루 종일 | 7 (15%) | 25-30 | 직접 선택: Emerald Route 118·119 낚시(흔함) |
| Qwilfish | `ROUTE12` | 대단한낚싯대 | 하루 종일 | 8 (4%) | 30 | HGSS Route 12 대단한낚싯대 4% |
| Qwilfish | `ROUTE13` | 대단한낚싯대 | 하루 종일 | 8 (4%) | 25 | HGSS Route 13 대단한낚싯대 4% |
| Noctowl | `ROUTE13` | 풀숲/동굴 | 밤 | 2,9 (14%) | 칸 그대로 | HGSS·Crystal Route 13 밤 20% |
| Volbeat | `ROUTE14` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 25 | 직접 선택: 꽃밭 도로 = Sapphire Route 117 18%(Ruby·Emerald 1%) |
| Noctowl | `ROUTE14` | 풀숲/동굴 | 밤 | 3 (10%) | 칸 그대로 | HGSS·Crystal Route 14 밤 20% |
| Illumise | `ROUTE15` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 25 | 직접 선택: Ruby·Emerald Route 117 18%(볼비트의 짝이라 이웃 도로) |
| Noctowl | `ROUTE15` | 풀숲/동굴 | 밤 | 3 (10%) | 칸 그대로 | HGSS·Crystal Route 15 밤 20% |
| Zangoose | `ROUTE16` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 24 | 직접 선택: Ruby Route 114 19%(세비퍼와 맞수라 사이클링 로드 양 끝) |
| Murkrow | `ROUTE16` | 풀숲/동굴 | 밤 | 4 (10%) | 칸 그대로 | HGSS Route 16 밤 10%, Crystal 15% |
| Seviper | `ROUTE18` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 24 | 직접 선택: Sapphire Route 114 19%, Emerald 9% |
| Wingull | `ROUTE19` | 파도타기 | 하루 종일 | 2,3 (9%) | 25-30 | 직접 선택: Emerald 바닷길 파도타기 35% |
| Corsola | `ROUTE19` | 대단한낚싯대 | 하루 종일 | 7 (15%) | 30 | HGSS Route 19 좋은·대단한낚싯대 4-40% |
| Wailmer | `ROUTE20` | 파도타기 | 하루 종일 | 3 (4%) | 30 | 직접 선택: Emerald 바닷길 |
| Chinchou | `ROUTE20` | 대단한낚싯대 | 하루 종일 | 8,9 (5%) | 30 | HGSS Route 20 좋은낚싯대 16%·대단한낚싯대 40% |
| Chinchou | `ROUTE21_NORTH` | 대단한낚싯대 | 하루 종일 | 7 (15%) | 30 | HGSS Route 21 좋은낚싯대 16%·대단한낚싯대 40% |
| Chinchou | `ROUTE21_SOUTH` | 대단한낚싯대 | 하루 종일 | 7 (15%) | 30 | HGSS Route 21 좋은낚싯대 16%·대단한낚싯대 40% |
| Seedot | `ROUTE22` | 풀숲/동굴 | 하루 종일 | 6,9 (9%) | 3-5 | 직접 선택: 상록시티 서쪽 = Ruby Route 102 20%(Petalburg City 동쪽) |
| Ralts | `ROUTE22` | 풀숲/동굴 | 하루 종일 | 11 (1%) | 4 | 직접 선택: Ruby·Sapphire·Emerald Route 102 4%(드묾) |
| Absol | `ROUTE23` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 38 | 직접 선택: Emerald Route 120 8%(산기슭 풀숲) |
| Sunkern | `ROUTE24` | 풀숲/동굴 | 낮 | 5,9 (14%) | 13-15 | HGSS·Crystal Route 24 낮 30% |
| Roselia | `ROUTE25` | 풀숲/동굴 | 하루 종일 | 7,9 (9%) | 14-16 | 직접 선택: 꽃밭 = Ruby·Sapphire Route 117 30% |
| Swablu | `ROUTE25` | 풀숲/동굴 | 하루 종일 | 8 (4%) | 14 | 직접 선택: Emerald Route 114·115 30-40% |
| Hoothoot | `ROUTE25` | 풀숲/동굴 | 밤 | 2,5 (20%) | 칸 그대로 | Crystal Route 25 밤 30% |
| Noctowl | `ROUTE25` | 풀숲/동굴 | 밤 | 10,11 (2%) | 칸 그대로 | Crystal Route 25 밤 15% |
| Feebas | `VIRIDIAN_CITY` | 대단한낚싯대 | 하루 종일 | 9 (1%) | 20 | 직접 선택: Emerald Route 119의 몇 칸에서만 낚이는 희귀종 → 작은 연못 1% |
| Corphish | `CELADON_CITY` | 대단한낚싯대 | 하루 종일 | 7 (15%) | 15-20 | 직접 선택: 도시 연못 = Emerald Petalburg City·Route 102 연못(흔함) |
| Makuhita | `MT_MOON_1F` | 풀숲/동굴 | 하루 종일 | 7,9 (9%) | 10-11 | HGSS Mt. Moon 호연의 소리(라디오), Emerald Granite Cave 50% |
| Aron | `MT_MOON_B1F` | 풀숲/동굴 | 하루 종일 | 5,9 (14%) | 10-11 | 직접 선택: Emerald Granite Cave B1F 40% |
| Lunatone | `MT_MOON_B2F` | 풀숲/동굴 | 하루 종일 | 6,9 (9%) | 12-13 | 직접 선택: Sapphire Meteor Falls 20-35%(유성이 떨어진 산) |
| Whismur | `ROCK_TUNNEL_1F` | 풀숲/동굴 | 하루 종일 | 6,9 (9%) | 17-19 | 직접 선택: 터널 = Emerald Rusturf Tunnel 100% |
| Nosepass | `ROCK_TUNNEL_B1F` | 바위깨기 | 하루 종일 | 1 (30%) | 15-20 | 직접 선택: Emerald Granite Cave B2F 바위깨기 30% |
| Trapinch | `DIGLETTS_CAVE_B1F` | 풀숲/동굴 | 하루 종일 | 7,9 (9%) | 20-21 | 직접 선택: 모래 굴 = Emerald Route 111 사막 35% |
| Spheal | `SEAFOAM_ISLANDS_B1F` | 풀숲/동굴 | 하루 종일 | 3,9 (14%) | 28-30 | 직접 선택: 얼음 동굴 = Emerald Shoal Cave 50% |
| Snorunt | `SEAFOAM_ISLANDS_B2F` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 30 | 직접 선택: Emerald Shoal Cave 얼음방 10% |
| Meditite | `VICTORY_ROAD_1F` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 38 | 직접 선택: Ruby·Sapphire Victory Road 5%(Mt. Pyre 바깥 30%) |
| Mawile | `VICTORY_ROAD_2F` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 40 | 직접 선택: Ruby Victory Road B2F 35%, Emerald 5% |
| Beldum | `CERULEAN_CAVE_B1F` | 풀숲/동굴 | 하루 종일 | 11 (1%) | 50 | 직접 선택(원작은 성호의 선물): 가장 깊은 동굴 1% |
| Shuppet | `POKEMON_TOWER_3F` | 풀숲/동굴 | 하루 종일 | 3,9 (14%) | 20-22 | 직접 선택: 묘지 탑 = Emerald Mt. Pyre 90-100% |
| Shuppet | `POKEMON_TOWER_4F` | 풀숲/동굴 | 하루 종일 | 3,9 (14%) | 20-22 | 직접 선택: Emerald Mt. Pyre |
| Duskull | `POKEMON_TOWER_5F` | 풀숲/동굴 | 하루 종일 | 7,9 (9%) | 24-27 | 직접 선택: Emerald Mt. Pyre 4F 이상 10-13% |
| Duskull | `POKEMON_TOWER_6F` | 풀숲/동굴 | 하루 종일 | 7,9 (9%) | 24-27 | 직접 선택: Emerald Mt. Pyre |
| Chimecho | `POKEMON_TOWER_7F` | 풀숲/동굴 | 하루 종일 | 11 (1%) | 26 | 직접 선택: Emerald Mt. Pyre 정상 2%(드묾) |
| Koffing | `POKEMON_MANSION_1F` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 30 | Red·Blue·LeafGreen Pokémon Mansion(LeafGreen 5%) |
| Koffing | `POKEMON_MANSION_2F` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 32 | Red·Blue·LeafGreen Pokémon Mansion |
| Koffing | `POKEMON_MANSION_3F` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 34 | Red·Blue·LeafGreen Pokémon Mansion |
| Electabuzz | `POWER_PLANT` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 33 | Red·FireRed Power Plant 5% |
| Girafarig | `SAFARI_ZONE_CENTER` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 25 | 직접 선택: Emerald Safari Zone 20% |
| Miltank | `SAFARI_ZONE_EAST` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 25 | 직접 선택: Emerald Safari Zone 5% |
| Gligar | `SAFARI_ZONE_NORTH` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 25 | 직접 선택: Emerald Safari Zone 5% |
| Cacnea | `SAFARI_ZONE_WEST` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 25 | 직접 선택: Emerald Route 111 사막 6% |
| Numel | `MT_EMBER_EXTERIOR` | 풀숲/동굴 | 하루 종일 | 6 (5%) | 33 | 직접 선택: 화산 = Emerald Route 112·Fiery Path 30-75% |
| Spoink | `MT_EMBER_EXTERIOR` | 풀숲/동굴 | 하루 종일 | 7 (5%) | 33 | 직접 선택: 화산 = Emerald Jagged Pass 20% |
| Spinda | `MT_EMBER_EXTERIOR` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 35 | 직접 선택: 화산재 풀숲 = Emerald Route 113 70% |
| Torkoal | `MT_EMBER_SUMMIT_PATH_1F` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 35 | 직접 선택: Emerald Fiery Path 18% |
| Solrock | `MT_EMBER_SUMMIT_PATH_3F` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 37 | 직접 선택: Ruby Meteor Falls 20-35%(해 = 불씨산, 달 = 달맞이산 루나톤) |
| Tropius | `THREE_ISLAND_BERRY_FOREST` | 풀숲/동굴 | 하루 종일 | 8 (4%) | 35 | 직접 선택: 열매 숲 = Emerald Route 119(밀림) 9% |
| Kecleon | `THREE_ISLAND_BERRY_FOREST` | 풀숲/동굴 | 하루 종일 | 11 (1%) | 35 | 직접 선택: Emerald Route 118-123 1%(드묾) |
| Wooper | `FOUR_ISLAND_ICEFALL_CAVE_ENTRANCE` | 파도타기 | 하루 종일 | 3 (4%) | 15-25 | FireRed Icefall Cave 입구 파도타기 5% |
| Delibird | `FOUR_ISLAND_ICEFALL_CAVE_1F` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 30 | FireRed Icefall Cave 1F 5% |
| Delibird | `FOUR_ISLAND_ICEFALL_CAVE_B1F` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 30 | FireRed Icefall Cave B1F 5% |
| Surskit | `SIX_ISLAND_PATTERN_BUSH` | 풀숲/동굴 | 하루 종일 | 11 (1%) | 20 | 직접 선택: Ruby·Sapphire Route 102·114·117·120 풀숲 1%(드묾) |
| Sableye | `FIVE_ISLAND_LOST_CAVE_ROOM1` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 35 | 직접 선택: 어두운 동굴 = Sapphire·Emerald Granite Cave·Victory Road 10-35% |
| Murkrow | `FIVE_ISLAND_LOST_CAVE_ROOM2` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 22 | FireRed Lost Cave 5% |
| Clamperl | `ONE_ISLAND_TREASURE_BEACH` | 대단한낚싯대 | 하루 종일 | 6 (40%) | 20-30 | 직접 선택: Emerald Route 124·126 해저 65% |
| Swablu | `TWO_ISLAND_CAPE_BRINK` | 풀숲/동굴 | 하루 종일 | 9 (4%) | 32 | 직접 선택: Emerald Route 115(해변 절벽) 30% |
| Luvdisc | `FIVE_ISLAND_RESORT_GORGEOUS` | 대단한낚싯대 | 하루 종일 | 5 (40%) | 20-30 | 직접 선택: Emerald Route 128·Ever Grande City 낚시 60% |
| Eevee | `FIVE_ISLAND_MEADOW` | 풀숲/동굴 | 하루 종일 | 8 (4%) | 40 | 직접 선택(원작 야생 없음): 목초지 4% |
| Qwilfish | `SIX_ISLAND_OUTCAST_ISLAND` | 대단한낚싯대 | 하루 종일 | 5 (40%) | 20-30 | FireRed 5·6·7의섬 바다 낚시 40% |
| Relicanth | `SIX_ISLAND_OUTCAST_ISLAND` | 파도타기 | 하루 종일 | 4 (1%) | 35-40 | 직접 선택: Emerald Route 124·126 해저(다이빙) 5% → 파도타기 1%(드묾) |
| Baltoy | `SIX_ISLAND_RUIN_VALLEY` | 풀숲/동굴 | 하루 종일 | 8 (4%) | 35 | 직접 선택: 유적 = Emerald Route 111 사막(Desert Ruins 근처) 24% |
| Sudowoodo | `SEVEN_ISLAND_SEVAULT_CANYON_ENTRANCE` | 풀숲/동굴 | 하루 종일 | 11 (1%) | 35 | 직접 선택(원작은 고정 전투): 바위 협곡 입구 1% |
| Skarmory | `SEVEN_ISLAND_SEVAULT_CANYON` | 풀숲/동굴 | 하루 종일 | 7 (5%) | 30 | FireRed Sevault Canyon 5% |
| Bagon | `SEVEN_ISLAND_SEVAULT_CANYON` | 풀숲/동굴 | 하루 종일 | 11 (1%) | 35 | 직접 선택: 깊은 협곡 = Emerald Meteor Falls B1F 25% |

### 3.1 바뀐 점 (v0.4.0 → 이번 작업, 칸토·세비 제도만)

"아침"·"밤"은 그 시간대 표의 확률, 표시가 없으면 낮 표다(아침·밤 표가 따로 없는 맵은 하루 종일 같다).

| 포켓몬 | 이전 | 이후 |
|---|---|---|
| Wurmple | VIRIDIAN_FOREST 4%/아침4%/밤4% | VIRIDIAN_FOREST 9%/밤9% |
| Shroomish | VIRIDIAN_FOREST 1%/아침1%/밤1% | VIRIDIAN_FOREST 4%/밤4% |
| Slakoth | ROUTE21_NORTH 4%/아침4%/밤4%, ROUTE21_SOUTH 4%/아침4%/밤4% | VIRIDIAN_FOREST 1%/밤1% |
| Hoothoot | VIRIDIAN_FOREST 밤24%, ROUTE1 밤71%, ROUTE2 밤35%, ROUTE5 밤40%, ROUTE6 밤40%, ROUTE7 밤40%, ROUTE8 밤40%, ROUTE11 밤30%, ROUTE12 밤14%, ROUTE13 밤10%, ROUTE21_NORTH 밤50%, ROUTE21_SOUTH 밤50%, ROUTE24 1%/밤25%, ROUTE25 밤24% | VIRIDIAN_FOREST 밤40%, ROUTE1 밤71%, ROUTE2 밤34%, ROUTE5 밤40%, ROUTE25 밤20% |
| Noctowl | VIRIDIAN_FOREST 밤1%, ROUTE5 밤5%, ROUTE6 밤5%, ROUTE7 밤10%, ROUTE8 밤10%, ROUTE11 밤10%, ROUTE12 밤10%, ROUTE13 밤14%, ROUTE14 밤10%, ROUTE15 밤10%, ROUTE21_NORTH 밤11%, ROUTE21_SOUTH 밤11%, ROUTE24 밤1%, ROUTE25 밤1% | VIRIDIAN_FOREST 밤1%, ROUTE2 밤2%, ROUTE5 밤5%, ROUTE8 밤30%, ROUTE11 밤10%, ROUTE13 밤14%, ROUTE14 밤10%, ROUTE15 밤10%, ROUTE25 밤2% |
| Zigzagoon | ROUTE1 4%/아침4%/밤4% | ROUTE1 9%/밤9% |
| Poochyena | ROUTE2 4%/밤4% | ROUTE2 14%/아침14%/밤14% |
| Taillow | ROUTE2 1%/밤1% | ROUTE2 5%/아침5% |
| Ledyba | VIRIDIAN_FOREST 아침45%, SIX_ISLAND_PATTERN_BUSH 30%, ROUTE1 아침1%, ROUTE4 아침1%, ROUTE5 아침1%, ROUTE6 아침1%, ROUTE9 아침1%, ROUTE10 아침1%, ROUTE11 아침1%, ROUTE14 아침1%, ROUTE15 아침1%, ROUTE16 아침1%, ROUTE17 아침1%, ROUTE18 아침1%, ROUTE21_NORTH 아침1%, ROUTE21_SOUTH 아침1%, ROUTE22 아침1% | SIX_ISLAND_PATTERN_BUSH 30%, ROUTE2 아침30% |
| Spinarak | VIRIDIAN_FOREST 밤45%, SIX_ISLAND_PATTERN_BUSH 5% | SIX_ISLAND_PATTERN_BUSH 5%, ROUTE2 밤20% |
| Nincada | ROUTE3 1% | ROUTE3 9% |
| Skitty | ROUTE3 4% | ROUTE3 1% |
| Ekans | ROUTE4 4%/아침4%, ROUTE11 4%/아침4%/밤4% | ROUTE4 5%, ROUTE11 14%/밤14% |
| Snubbull | ROUTE8 4%/밤4% | ROUTE5 10%, ROUTE6 10%, ROUTE8 9% |
| Lotad | ROUTE6 4%/아침4%/밤4% | ROUTE6 4%/밤4% |
| Barboach | ROUTE6 낚시1% | ROUTE6 낚시15% |
| Vulpix | ROUTE7 4%/밤4% | ROUTE7 9%/밤9%, ROUTE8 10%/밤10% |
| Eevee | FIVE_ISLAND_MEADOW 4%, ROUTE7 1%/밤1%, ROUTE8 1%/밤1% | FIVE_ISLAND_MEADOW 4%, ROUTE7 1%/밤1%, ROUTE8 1%/밤1% |
| Murkrow | FIVE_ISLAND_LOST_CAVE_ROOM2 4% | FIVE_ISLAND_LOST_CAVE_ROOM2 4%, ROUTE7 밤20%, ROUTE16 밤10% |
| Houndour | - | ROUTE7 밤20%, SIX_ISLAND_ALTERING_CAVE 100% |
| Gulpin | ROUTE9 4%/아침4% | ROUTE9 4% |
| Electrike | ROUTE10 4%/아침4% | ROUTE10 14% |
| Carvanha | ROUTE12 낚시1% | ROUTE12 낚시15% |
| Qwilfish | SIX_ISLAND_OUTCAST_ISLAND 낚시40% | SIX_ISLAND_OUTCAST_ISLAND 낚시40%, ROUTE12 낚시4%, ROUTE13 낚시4% |
| Volbeat | ROUTE14 4%/아침4%/밤4% | ROUTE14 4%/밤4% |
| Illumise | ROUTE15 4%/아침4%/밤4% | ROUTE15 4%/밤4% |
| Zangoose | ROUTE16 4%/아침4% | ROUTE16 4%/밤4% |
| Seviper | ROUTE18 4%/아침4% | ROUTE18 4% |
| Wingull | ROUTE19 파도4% | ROUTE19 파도9% |
| Corsola | ROUTE20 낚시1% | ROUTE19 낚시15% |
| Wailmer | ROUTE13 낚시1%, ROUTE20 파도4% | ROUTE20 파도4% |
| Chinchou | ROUTE19 낚시1% | ROUTE20 낚시5%, ROUTE21_NORTH 낚시15%, ROUTE21_SOUTH 낚시15% |
| Seedot | ROUTE22 4%/아침4% | ROUTE22 9% |
| Ralts | ROUTE5 4%/아침4%/밤4% | ROUTE22 1% |
| Absol | ROUTE23 4% | ROUTE23 4% |
| Sunkern | ROUTE24 4%/밤4% | ROUTE24 14% |
| Roselia | ROUTE25 4%/밤4% | ROUTE25 9%/밤9% |
| Swablu | TWO_ISLAND_CAPE_BRINK 4%, ROUTE25 1%/밤1% | TWO_ISLAND_CAPE_BRINK 4%, ROUTE25 4%/밤4% |
| Feebas | VIRIDIAN_CITY 낚시1% | VIRIDIAN_CITY 낚시1% |
| Corphish | CELADON_CITY 낚시1% | CELADON_CITY 낚시15% |
| Makuhita | MT_MOON_1F 4% | MT_MOON_1F 9% |
| Aron | MT_MOON_B1F 4% | MT_MOON_B1F 14% |
| Lunatone | MT_MOON_B2F 4% | MT_MOON_B2F 9% |
| Whismur | ROCK_TUNNEL_1F 4% | ROCK_TUNNEL_1F 9% |
| Nosepass | ROCK_TUNNEL_B1F 4% | ROCK_TUNNEL_B1F 바위30% |
| Trapinch | DIGLETTS_CAVE_B1F 4% | DIGLETTS_CAVE_B1F 9% |
| Spheal | SEAFOAM_ISLANDS_B1F 4% | SEAFOAM_ISLANDS_B1F 14% |
| Snorunt | SEAFOAM_ISLANDS_B2F 4% | SEAFOAM_ISLANDS_B2F 4% |
| Meditite | VICTORY_ROAD_1F 4% | VICTORY_ROAD_1F 4% |
| Mawile | VICTORY_ROAD_2F 4% | VICTORY_ROAD_2F 4% |
| Beldum | CERULEAN_CAVE_B1F 1% | CERULEAN_CAVE_B1F 1% |
| Shuppet | POKEMON_TOWER_3F 4%, POKEMON_TOWER_4F 4% | POKEMON_TOWER_3F 14%, POKEMON_TOWER_4F 14% |
| Duskull | POKEMON_TOWER_5F 4%, POKEMON_TOWER_6F 4% | POKEMON_TOWER_5F 9%, POKEMON_TOWER_6F 9% |
| Chimecho | POKEMON_TOWER_7F 4% | POKEMON_TOWER_7F 1% |
| Koffing | POKEMON_MANSION_1F 4%, POKEMON_MANSION_2F 4%, POKEMON_MANSION_3F 4% | POKEMON_MANSION_1F 4%, POKEMON_MANSION_2F 4%, POKEMON_MANSION_3F 4% |
| Electabuzz | POWER_PLANT 4% | POWER_PLANT 4% |
| Girafarig | SAFARI_ZONE_CENTER 4% | SAFARI_ZONE_CENTER 4% |
| Miltank | SAFARI_ZONE_EAST 4% | SAFARI_ZONE_EAST 4% |
| Gligar | SAFARI_ZONE_NORTH 4% | SAFARI_ZONE_NORTH 4% |
| Cacnea | SAFARI_ZONE_WEST 4% | SAFARI_ZONE_WEST 4% |
| Numel | MT_EMBER_EXTERIOR 5% | MT_EMBER_EXTERIOR 5% |
| Spoink | MT_EMBER_EXTERIOR 5% | MT_EMBER_EXTERIOR 5% |
| Spinda | MT_EMBER_EXTERIOR 4% | MT_EMBER_EXTERIOR 4% |
| Torkoal | MT_EMBER_SUMMIT_PATH_1F 4% | MT_EMBER_SUMMIT_PATH_1F 4% |
| Solrock | MT_EMBER_SUMMIT_PATH_3F 4% | MT_EMBER_SUMMIT_PATH_3F 4% |
| Tropius | THREE_ISLAND_BERRY_FOREST 4% | THREE_ISLAND_BERRY_FOREST 4% |
| Kecleon | THREE_ISLAND_BERRY_FOREST 4% | THREE_ISLAND_BERRY_FOREST 1% |
| Wooper | FOUR_ISLAND_ICEFALL_CAVE_ENTRANCE 파도4% | FOUR_ISLAND_ICEFALL_CAVE_ENTRANCE 파도4% |
| Delibird | FOUR_ISLAND_ICEFALL_CAVE_1F 4%, FOUR_ISLAND_ICEFALL_CAVE_B1F 4% | FOUR_ISLAND_ICEFALL_CAVE_1F 4%, FOUR_ISLAND_ICEFALL_CAVE_B1F 4% |
| Surskit | SIX_ISLAND_PATTERN_BUSH 4% | SIX_ISLAND_PATTERN_BUSH 1% |
| Sableye | FIVE_ISLAND_LOST_CAVE_ROOM1 4% | FIVE_ISLAND_LOST_CAVE_ROOM1 4% |
| Clamperl | ONE_ISLAND_TREASURE_BEACH 낚시40% | ONE_ISLAND_TREASURE_BEACH 낚시40% |
| Luvdisc | FIVE_ISLAND_RESORT_GORGEOUS 낚시40% | FIVE_ISLAND_RESORT_GORGEOUS 낚시40% |
| Relicanth | SIX_ISLAND_OUTCAST_ISLAND 낚시1% | SIX_ISLAND_OUTCAST_ISLAND 파도1% |
| Baltoy | SIX_ISLAND_RUIN_VALLEY 1% | SIX_ISLAND_RUIN_VALLEY 4% |
| Sudowoodo | SEVEN_ISLAND_SEVAULT_CANYON_ENTRANCE 1% | SEVEN_ISLAND_SEVAULT_CANYON_ENTRANCE 1% |
| Skarmory | SEVEN_ISLAND_SEVAULT_CANYON 5% | SEVEN_ISLAND_SEVAULT_CANYON 5% |
| Bagon | SEVEN_ISLAND_SEVAULT_CANYON 1% | SEVEN_ISLAND_SEVAULT_CANYON 1% |

## 4. 분포 화면 개편 (결과)

- 검사 대상(`src/wild_pokemon_area.c`의 `FindSpeciesHabitats`): 모든 야생표(풀숲·파도타기·바위깨기·낚시)의 낮·아침·밤 세 벌, 알터링 동굴의 9세트 전부(날짜와 상관없이 항상 알터링 동굴에 표시), 숨겨진 공터 4곳의 포켓몬(`IsHiddenGrottoSpecies`: 상록숲·11번·13번·15번 도로), 벌레잡기 대회의 포켓몬(`IsBugContestSpecies`: 상록숲). 낚시표는 10칸만 읽는다(원작 버그 수정). 같은 표시 칸이 여러 번 찍히지 않도록 칸마다 한 번만 그린다.
- 세비 제도: 열린 섬에 더해 그 포켓몬이 사는 섬도 그린다. 원작처럼 4~7의섬 중 하나라도 그리면 칸토 지도가 위로 붙는다.
- 호연 페이지: `tools/dex_habitat/make_hoenn_area_map.py`가 FLY용 호연 지도(`graphics/region_map/hoenn.png`·`hoenn_tilemap.bin`)에서 땅·바다를 읽고, 에메랄드의 MAPSEC 격자(`tools/dex_habitat/hoenn_map_sections.json`, pokeemerald `region_map_sections.json`에서 이 저장소에 있는 MAPSEC만)로 도로·마을을 칸토 분포 지도(`map_kanto.png`)와 같은 색·모양으로 그려 `graphics/pokedex/map_hoenn.png`(128×72)와 표시 위치 표 `src/data/pokedex_area_hoenn.h`를 만든다. 표시는 MAPSEC마다 하나, 칸 수에 맞는 모양(원·가로·세로)이다. 에메랄드의 알터링 동굴(103번 도로)은 FR/LG와 같은 `MAPSEC_ALTERING_CAVE`를 쓰므로 따로 처리하고, 호연에서는 실제로 쓰이는 첫 세트(주뱃)만 센다.
- 조작: 분포 화면에서 **SELECT**로 칸토 ↔ 호연을 바꾼다(기본 버튼 모드에서 L·R은 도움말을 열기 때문). 아래 조작 줄에 `SELECT REGION`, 지도 위 제목에 `KANTO AREA`/`HOENN AREA`를 표시한다. 처음에는 칸토에 서식지가 있으면 칸토, 호연에만 있으면 호연을 보여 준다.
- 배회 전설은 원작 동작(칸토 페이지에 현재 위치 하나), 서식지가 없는 종은 두 페이지 모두 "AREA UNKNOWN".
- 이제 서식지가 안 보이는 입수 가능 종은 서식지 자체가 없는 종(선물·교환·전설 이벤트·진화 전용)뿐이다.

| 확인(에뮬레이터) | 스크린샷 |
|---|---|
| 칸토: 블루(5·6·8번 도로) | `docs/screenshots/dex_area_kanto_snubbull.png` |
| 세비 제도: 딜리버드(4의섬 얼음폭포동굴, 섬이 아직 안 열린 세이브) | `docs/screenshots/dex_area_sevii_delibird.png` |
| 호연 전용: 포챠나의 진화형 그라에나(처음부터 호연 페이지) | `docs/screenshots/dex_area_hoenn_mightyena.png` |
| 호연 페이지로 바꾼 지그제구리(101-103·118·119번 도로) | `docs/screenshots/dex_area_hoenn_page_zigzagoon.png` |
| 알터링 동굴 순환: 메리프(6의섬) | `docs/screenshots/dex_area_altering_cave_mareep.png` |
| 숨겨진 공터: 마임맨(11번 도로) | `docs/screenshots/dex_area_grotto_mr_mime.png` |
| 서식지 없음: 뮤 | `docs/screenshots/dex_area_unknown_mew.png` |

## 5. 도감 설명 페이지 개편 (결과)

- 조건: 도감에 본 것(SEEN) 또는 잡은 것(CAUGHT)으로 등록되면 분류·키·몸무게·발자국·설명·특성을 보여 준다(`DexScreen_ShowsMonData`). 도감에 나오는 1~386번은 모두 게임 안에서 입수 가능하므로 입수 가능 여부는 따로 검사하지 않는다. 분포 페이지의 타입 아이콘·크기 비교도 같은 조건이다. 목록 화면(몬스터볼 표시·타입 아이콘)은 원작처럼 잡은 포켓몬만.
- 특성: 설명 페이지 왼쪽 위 칸의 몸무게 아래에 `ABILITY` 줄을 넣었다. 특성 1을 같은 줄에, 특성 2가 있으면 그 아래 줄에 게임 표기(영어 대문자, `gAbilityNames`)로 적는다. 자리를 만들려고 번호·이름·분류·키·몸무게 줄 간격을 FR/LG보다 3~4픽셀씩 좁히고 발자국을 키 줄 오른쪽으로 옮겼다(창 크기·VRAM 배치는 그대로).

| 확인(에뮬레이터, 본 것만 있는 세이브) | 스크린샷 |
|---|---|
| 1세대: 아보(특성 2개) | `docs/screenshots/dex_entry_gen1_ekans.png` |
| 2세대: 블루(특성 2개) | `docs/screenshots/dex_entry_gen2_snubbull.png` |
| 3세대: 지그제구리(특성 1개) | `docs/screenshots/dex_entry_gen3_zigzagoon.png` |
| 본 것만 있는 종의 분포 페이지(타입·크기 비교 표시) | `docs/screenshots/dex_area_seen_only_zigzagoon.png` |

## 6. 게임 안 단서 확인

바뀐 배치 뒤에도 단서 NPC의 말이 맞는지 확인했다(대사는 바꾸지 않음).

| NPC | 대사 | 확인 |
|---|---|---|
| 무지개시티 소문 수집가 20번 | 밤에는 부우부·페이검, 아침에는 레디바 | 부우부 1·2·5·25번 도로·상록숲 밤, 페이검 2번 도로 밤, 레디바 2번 도로 아침 |
| 무지개시티 소문 수집가 21번 | 이브이가 7·8번 도로에 산다 | 7·8번 도로 1% 유지 |
| 1의섬 소문 수집가 5번 | 알터링 동굴의 포켓몬이 매일 바뀐다 | 유지. 분포 화면은 9세트 모두 알터링 동굴에 표시 |
| 1의섬 소문 수집가 10번 | 호연 포켓몬이 세비 제도와 칸토에도 나타나니 도감 AREA에서 확인하라 | 칸토·세비 제도에 3세대 종 유지, AREA에 모두 표시(호연 페이지는 화면 아래 `SELECT REGION` 안내) |
| 오박사 연구소 조수(포켓워치) | 밤에만 나오는 포켓몬(부우부) | 유지 |

## 7. 참고 자료

| 게임 | 자료 |
|---|---|
| 레드·블루(그린) | pret/pokered `data/wild/maps/*.asm` |
| 옐로 | pret/pokeyellow `data/wild/maps/*.asm`(칸토 표의 기준, v0.1에서 옮김) |
| 골드·실버·크리스탈 | pret/pokecrystal `data/wild/kanto_grass.asm`·`johto_grass.asm`·`*_water.asm`(아침·낮·밤) |
| 하트골드·소울실버 | pret/pokeheartgold `files/fielddata/encountdata/gs_enc_data.json`(아침·낮·밤, 호연의 소리 목록, 맵 코드는 `include/constants/maps.h`) |
| 루비·사파이어 | pret/pokeruby `src/data/wild_encounters.json` |
| 에메랄드 | pret/pokeemerald(이 해킹의 호연 맵 야생표와 같음), `src/data/region_map/region_map_sections.json` |
| 파이어레드·리프그린 | pret/pokefirered 원본 `src/data/wild_encounters.json`(FireRed·LeafGreen 표) |
| 블랙·화이트 | 이번 대상 종 중 블랙·화이트 서식지가 필요한 종은 없었다(대상 종이 모두 1~3세대 게임에 서식지가 있거나 원작 야생이 없음) |

원작 야생이 없는 종(이브이, 메탕, 꼬지모 등)은 2절 4번 규칙으로 정했다.

## 추가 (v0.6.0): 상록숲의 야생 피카츄·뿔충이·단데기

사용자 요청으로 상록숲 표에 옐로처럼 피카츄(9번 칸 4%, Lv3~5), 뿔충이(2번 칸 10%, Lv3~4), 단데기(3번 칸 10%, Lv4~5)를 넣었다. 밤 표도 같다. 밀려난 칸은 모두 같은 표에 다른 칸이 남아 있는 종(캐터피·아이완)이라 사라지는 종은 없다. 이 전에는 야생 피카츄가 칸토 어디에도 없어 마스코트의 도감 분포가 호연 지도로 열렸다.
