"""Habitats of the species Thunder Yellow added to the Kanto and Sevii wild tables.

Every row puts one species into one or more slots of a map's table. The rules
(docs/dex-habitat.md):
- Kanto maps keep Pokemon Yellow's day tables. A new species only takes slots
  whose species also sits in another slot of the same table, so every Yellow
  species still appears.
- Sevii Islands and Mt. Ember keep LeafGreen's tables and every species in them.
- Morning and night tables start as copies of the day table.

Row fields:
    map      MAP_* constant
    table    land / water / fishing / rock_smash
    when     all       day, morning and night
             daymorn   day and morning (reverted to the Yellow slot at night)
             day       day only (reverted in the morning and at night)
             morning   morning table only
             night     night table only
    slots    slot indices (land: 20 20 10 10 10 10 5 5 4 4 1 1 %,
             water/rock smash: 60 30 5 4 1 %, fishing: old 70 30,
             good 60 20 20, super 40 40 15 4 1 %)
    species  SPECIES_* constant
    levels   (min, max) or None to keep the slot's levels
    source   where the placement comes from
"""

HGSS = "HGSS"
CRYSTAL = "Crystal"

HABITATS = [
    # --- Viridian Forest: HGSS night owls; Petalburg Woods (Emerald) residents ---
    ("MAP_VIRIDIAN_FOREST", "land", "all", [6, 9], "SPECIES_WURMPLE", None, "직접 선택: 숲 = Emerald Petalburg Woods 25%, Route 101 45%"),
    ("MAP_VIRIDIAN_FOREST", "land", "all", [8], "SPECIES_SHROOMISH", (6, 6), "직접 선택: Emerald Petalburg Woods 15%"),
    ("MAP_VIRIDIAN_FOREST", "land", "all", [11], "SPECIES_SLAKOTH", (6, 6), "직접 선택: Emerald Petalburg Woods 5%(드묾)"),
    ("MAP_VIRIDIAN_FOREST", "land", "night", [0, 4, 5], "SPECIES_HOOTHOOT", None, "HGSS Viridian Forest 밤 80%"),
    ("MAP_VIRIDIAN_FOREST", "land", "night", [10], "SPECIES_NOCTOWL", None, "HGSS Viridian Forest 밤 15%"),

    # --- Route 1 ---
    ("MAP_ROUTE1", "land", "all", [7, 9], "SPECIES_ZIGZAGOON", (3, 3), "직접 선택: 첫 도로 = Emerald Route 101-103 10-20%"),
    ("MAP_ROUTE1", "land", "night", [0, 1, 4, 5, 6, 8, 10, 11], "SPECIES_HOOTHOOT", None, "HGSS·Crystal Route 1 밤 45%(밤에는 구구 자리)"),

    # --- Route 2 ---
    ("MAP_ROUTE2", "land", "all", [2, 9], "SPECIES_POOCHYENA", (3, 4), "직접 선택: Emerald Route 104 40%"),
    ("MAP_ROUTE2", "land", "daymorn", [8, 11], "SPECIES_TAILLOW", (5, 5), "직접 선택: Emerald Route 104 10%(낮에 나는 새)"),
    ("MAP_ROUTE2", "land", "morning", [1, 5], "SPECIES_LEDYBA", None, "SoulSilver·Crystal Route 2 아침 30%"),
    ("MAP_ROUTE2", "land", "night", [1, 5, 8], "SPECIES_HOOTHOOT", None, "HGSS·Crystal Route 2 밤 50-60%"),
    ("MAP_ROUTE2", "land", "night", [10, 11], "SPECIES_NOCTOWL", (7, 7), "HGSS·Crystal Route 2 밤 14-15%"),
    ("MAP_ROUTE2", "land", "night", [3, 4], "SPECIES_SPINARAK", None, "HeartGold·Crystal Route 2 밤 30%"),

    # --- Route 3 ---
    ("MAP_ROUTE3", "land", "all", [7, 9], "SPECIES_NINCADA", (9, 10), "직접 선택: 회색시티 동쪽 = Emerald Route 116(Rustboro 동쪽) 20%"),
    ("MAP_ROUTE3", "land", "all", [11], "SPECIES_SKITTY", (9, 9), "직접 선택: Emerald Route 116 2%(드묾)"),

    # --- Route 4 ---
    ("MAP_ROUTE4", "land", "all", [9, 11], "SPECIES_EKANS", (10, 12), "Red·FireRed Route 4 25%, SoulSilver·Crystal 20%"),

    # --- Route 5 / 6 (Crystal Snubbull, owls at night on Route 5) ---
    ("MAP_ROUTE5", "land", "daymorn", [4], "SPECIES_SNUBBULL", (14, 16), "Crystal Route 5 아침·낮 30%"),
    ("MAP_ROUTE5", "land", "night", [0, 3, 5], "SPECIES_HOOTHOOT", None, "Crystal Route 5 밤 30%"),
    ("MAP_ROUTE5", "land", "night", [6], "SPECIES_NOCTOWL", None, "Crystal Route 5 밤 20%"),
    ("MAP_ROUTE6", "land", "daymorn", [4], "SPECIES_SNUBBULL", (14, 16), "Crystal Route 6 아침·낮 30%"),
    ("MAP_ROUTE6", "land", "all", [9], "SPECIES_LOTAD", (14, 14), "직접 선택: 연못가 풀숲 = Sapphire Route 102(연못) 20%·114 30%"),
    ("MAP_ROUTE6", "fishing", "all", [7], "SPECIES_BARBOACH", (15, 20), "직접 선택: 연못 = Emerald Route 111·114 낚시(흔함)"),

    # --- Route 7 ---
    ("MAP_ROUTE7", "land", "all", [7, 9], "SPECIES_VULPIX", (18, 20), "LeafGreen Route 7 10%, SoulSilver 25%"),
    ("MAP_ROUTE7", "land", "all", [11], "SPECIES_EEVEE", (22, 22), "직접 선택(원작 야생 없음): 무지개시티(이브이 선물) 옆 도로 1%"),
    ("MAP_ROUTE7", "land", "night", [0], "SPECIES_MURKROW", None, "HeartGold Route 7 밤 35%, Crystal 30%"),
    ("MAP_ROUTE7", "land", "night", [1], "SPECIES_HOUNDOUR", None, "Crystal Route 7 밤 20%, SoulSilver 5%"),

    # --- Route 8 ---
    ("MAP_ROUTE8", "land", "daymorn", [7, 9], "SPECIES_SNUBBULL", (17, 20), "Crystal Route 8 아침·낮 30%"),
    ("MAP_ROUTE8", "land", "all", [4], "SPECIES_VULPIX", (15, 18), "LeafGreen Route 8 20%, SoulSilver 10%"),
    ("MAP_ROUTE8", "land", "all", [11], "SPECIES_EEVEE", (22, 22), "직접 선택(원작 야생 없음): 무지개시티 옆 도로 1%"),
    ("MAP_ROUTE8", "land", "night", [0, 5], "SPECIES_NOCTOWL", None, "HeartGold Route 8 밤 40%, Crystal 30%"),

    # --- Route 9 / 10 ---
    ("MAP_ROUTE9", "land", "all", [9], "SPECIES_GULPIN", (18, 18), "직접 선택: Emerald Route 110 15%"),
    ("MAP_ROUTE10", "land", "all", [3, 9], "SPECIES_ELECTRIKE", (16, 18), "직접 선택: 무인발전소 앞 = Emerald Route 110·118(Mauville 근처) 30%"),

    # --- Route 11 ---
    ("MAP_ROUTE11", "land", "all", [2, 9], "SPECIES_EKANS", (15, 17), "FireRed Route 11 40%, Red Route 11"),
    ("MAP_ROUTE11", "land", "night", [6, 7], "SPECIES_NOCTOWL", None, "Crystal Route 11 밤 10%"),

    # --- Routes 12-15 ---
    ("MAP_ROUTE12", "fishing", "all", [7], "SPECIES_CARVANHA", (25, 30), "직접 선택: Emerald Route 118·119 낚시(흔함)"),
    ("MAP_ROUTE12", "fishing", "all", [8], "SPECIES_QWILFISH", (30, 30), "HGSS Route 12 대단한낚싯대 4%"),
    ("MAP_ROUTE13", "fishing", "all", [8], "SPECIES_QWILFISH", (25, 25), "HGSS Route 13 대단한낚싯대 4%"),
    ("MAP_ROUTE13", "land", "night", [2, 9], "SPECIES_NOCTOWL", None, "HGSS·Crystal Route 13 밤 20%"),
    ("MAP_ROUTE14", "land", "all", [9], "SPECIES_VOLBEAT", (25, 25), "직접 선택: 꽃밭 도로 = Sapphire Route 117 18%(Ruby·Emerald 1%)"),
    ("MAP_ROUTE14", "land", "night", [3], "SPECIES_NOCTOWL", None, "HGSS·Crystal Route 14 밤 20%"),
    ("MAP_ROUTE15", "land", "all", [9], "SPECIES_ILLUMISE", (25, 25), "직접 선택: Ruby·Emerald Route 117 18%(볼비트의 짝이라 이웃 도로)"),
    ("MAP_ROUTE15", "land", "night", [3], "SPECIES_NOCTOWL", None, "HGSS·Crystal Route 15 밤 20%"),

    # --- Routes 16-18 (Cycling Road) ---
    ("MAP_ROUTE16", "land", "all", [9], "SPECIES_ZANGOOSE", (24, 24), "직접 선택: Ruby Route 114 19%(세비퍼와 맞수라 사이클링 로드 양 끝)"),
    ("MAP_ROUTE16", "land", "night", [4], "SPECIES_MURKROW", None, "HGSS Route 16 밤 10%, Crystal 15%"),
    ("MAP_ROUTE18", "land", "all", [9], "SPECIES_SEVIPER", (24, 24), "직접 선택: Sapphire Route 114 19%, Emerald 9%"),

    # --- Sea routes ---
    ("MAP_ROUTE19", "water", "all", [2, 3], "SPECIES_WINGULL", (25, 30), "직접 선택: Emerald 바닷길 파도타기 35%"),
    ("MAP_ROUTE19", "fishing", "all", [7], "SPECIES_CORSOLA", (30, 30), "HGSS Route 19 좋은·대단한낚싯대 4-40%"),
    ("MAP_ROUTE20", "water", "all", [3], "SPECIES_WAILMER", (30, 30), "직접 선택: Emerald 바닷길"),
    ("MAP_ROUTE20", "fishing", "all", [8, 9], "SPECIES_CHINCHOU", (30, 30), "HGSS Route 20 좋은낚싯대 16%·대단한낚싯대 40%"),
    ("MAP_ROUTE21_NORTH", "fishing", "all", [7], "SPECIES_CHINCHOU", (30, 30), "HGSS Route 21 좋은낚싯대 16%·대단한낚싯대 40%"),
    ("MAP_ROUTE21_SOUTH", "fishing", "all", [7], "SPECIES_CHINCHOU", (30, 30), "HGSS Route 21 좋은낚싯대 16%·대단한낚싯대 40%"),

    # --- Route 22 / 23 ---
    ("MAP_ROUTE22", "land", "all", [6, 9], "SPECIES_SEEDOT", (3, 5), "직접 선택: 상록시티 서쪽 = Ruby Route 102 20%(Petalburg City 동쪽)"),
    ("MAP_ROUTE22", "land", "all", [11], "SPECIES_RALTS", (4, 4), "직접 선택: Ruby·Sapphire·Emerald Route 102 4%(드묾)"),
    ("MAP_ROUTE23", "land", "all", [9], "SPECIES_ABSOL", (38, 38), "직접 선택: Emerald Route 120 8%(산기슭 풀숲)"),

    # --- Routes 24 / 25 ---
    ("MAP_ROUTE24", "land", "day", [5, 9], "SPECIES_SUNKERN", (13, 15), "HGSS·Crystal Route 24 낮 30%"),
    ("MAP_ROUTE25", "land", "all", [7, 9], "SPECIES_ROSELIA", (14, 16), "직접 선택: 꽃밭 = Ruby·Sapphire Route 117 30%"),
    ("MAP_ROUTE25", "land", "all", [8], "SPECIES_SWABLU", (14, 14), "직접 선택: Emerald Route 114·115 30-40%"),
    ("MAP_ROUTE25", "land", "night", [2, 5], "SPECIES_HOOTHOOT", None, "Crystal Route 25 밤 30%"),
    ("MAP_ROUTE25", "land", "night", [10, 11], "SPECIES_NOCTOWL", None, "Crystal Route 25 밤 15%"),

    # --- Town fishing ---
    ("MAP_VIRIDIAN_CITY", "fishing", "all", [9], "SPECIES_FEEBAS", (20, 20), "직접 선택: Emerald Route 119의 몇 칸에서만 낚이는 희귀종 → 작은 연못 1%"),
    ("MAP_CELADON_CITY", "fishing", "all", [7], "SPECIES_CORPHISH", (15, 20), "직접 선택: 도시 연못 = Emerald Petalburg City·Route 102 연못(흔함)"),

    # --- Caves ---
    ("MAP_MT_MOON_1F", "land", "all", [7, 9], "SPECIES_MAKUHITA", (10, 11), "HGSS Mt. Moon 호연의 소리(라디오), Emerald Granite Cave 50%"),
    ("MAP_MT_MOON_B1F", "land", "all", [5, 9], "SPECIES_ARON", (10, 11), "직접 선택: Emerald Granite Cave B1F 40%"),
    ("MAP_MT_MOON_B2F", "land", "all", [6, 9], "SPECIES_LUNATONE", (12, 13), "직접 선택: Sapphire Meteor Falls 20-35%(유성이 떨어진 산)"),
    ("MAP_ROCK_TUNNEL_1F", "land", "all", [6, 9], "SPECIES_WHISMUR", (17, 19), "직접 선택: 터널 = Emerald Rusturf Tunnel 100%"),
    ("MAP_ROCK_TUNNEL_B1F", "rock_smash", "all", [1], "SPECIES_NOSEPASS", (15, 20), "직접 선택: Emerald Granite Cave B2F 바위깨기 30%"),
    ("MAP_DIGLETTS_CAVE_B1F", "land", "all", [7, 9], "SPECIES_TRAPINCH", (20, 21), "직접 선택: 모래 굴 = Emerald Route 111 사막 35%"),
    ("MAP_SEAFOAM_ISLANDS_B1F", "land", "all", [3, 9], "SPECIES_SPHEAL", (28, 30), "직접 선택: 얼음 동굴 = Emerald Shoal Cave 50%"),
    ("MAP_SEAFOAM_ISLANDS_B2F", "land", "all", [9], "SPECIES_SNORUNT", (30, 30), "직접 선택: Emerald Shoal Cave 얼음방 10%"),
    ("MAP_VICTORY_ROAD_1F", "land", "all", [9], "SPECIES_MEDITITE", (38, 38), "직접 선택: Ruby·Sapphire Victory Road 5%(Mt. Pyre 바깥 30%)"),
    ("MAP_VICTORY_ROAD_2F", "land", "all", [9], "SPECIES_MAWILE", (40, 40), "직접 선택: Ruby Victory Road B2F 35%, Emerald 5%"),
    ("MAP_CERULEAN_CAVE_B1F", "land", "all", [11], "SPECIES_BELDUM", (50, 50), "직접 선택(원작은 성호의 선물): 가장 깊은 동굴 1%"),

    # --- Pokemon Tower = Mt. Pyre ---
    ("MAP_POKEMON_TOWER_3F", "land", "all", [3, 9], "SPECIES_SHUPPET", (20, 22), "직접 선택: 묘지 탑 = Emerald Mt. Pyre 90-100%"),
    ("MAP_POKEMON_TOWER_4F", "land", "all", [3, 9], "SPECIES_SHUPPET", (20, 22), "직접 선택: Emerald Mt. Pyre"),
    ("MAP_POKEMON_TOWER_5F", "land", "all", [7, 9], "SPECIES_DUSKULL", (24, 27), "직접 선택: Emerald Mt. Pyre 4F 이상 10-13%"),
    ("MAP_POKEMON_TOWER_6F", "land", "all", [7, 9], "SPECIES_DUSKULL", (24, 27), "직접 선택: Emerald Mt. Pyre"),
    ("MAP_POKEMON_TOWER_7F", "land", "all", [11], "SPECIES_CHIMECHO", (26, 26), "직접 선택: Emerald Mt. Pyre 정상 2%(드묾)"),

    # --- Mansion / Power Plant / Safari Zone ---
    ("MAP_POKEMON_MANSION_1F", "land", "all", [9], "SPECIES_KOFFING", (30, 30), "Red·Blue·LeafGreen Pokémon Mansion(LeafGreen 5%)"),
    ("MAP_POKEMON_MANSION_2F", "land", "all", [9], "SPECIES_KOFFING", (32, 32), "Red·Blue·LeafGreen Pokémon Mansion"),
    ("MAP_POKEMON_MANSION_3F", "land", "all", [9], "SPECIES_KOFFING", (34, 34), "Red·Blue·LeafGreen Pokémon Mansion"),
    ("MAP_POWER_PLANT", "land", "all", [9], "SPECIES_ELECTABUZZ", (33, 33), "Red·FireRed Power Plant 5%"),
    ("MAP_SAFARI_ZONE_CENTER", "land", "all", [9], "SPECIES_GIRAFARIG", (25, 25), "직접 선택: Emerald Safari Zone 20%"),
    ("MAP_SAFARI_ZONE_EAST", "land", "all", [9], "SPECIES_MILTANK", (25, 25), "직접 선택: Emerald Safari Zone 5%"),
    ("MAP_SAFARI_ZONE_NORTH", "land", "all", [9], "SPECIES_GLIGAR", (25, 25), "직접 선택: Emerald Safari Zone 5%"),
    ("MAP_SAFARI_ZONE_WEST", "land", "all", [9], "SPECIES_CACNEA", (25, 25), "직접 선택: Emerald Route 111 사막 6%"),

    # --- Mt. Ember (LeafGreen) ---
    ("MAP_MT_EMBER_EXTERIOR", "land", "all", [6], "SPECIES_NUMEL", (33, 33), "직접 선택: 화산 = Emerald Route 112·Fiery Path 30-75%"),
    ("MAP_MT_EMBER_EXTERIOR", "land", "all", [7], "SPECIES_SPOINK", (33, 33), "직접 선택: 화산 = Emerald Jagged Pass 20%"),
    ("MAP_MT_EMBER_EXTERIOR", "land", "all", [9], "SPECIES_SPINDA", (35, 35), "직접 선택: 화산재 풀숲 = Emerald Route 113 70%"),
    ("MAP_MT_EMBER_SUMMIT_PATH_1F", "land", "all", [9], "SPECIES_TORKOAL", (35, 35), "직접 선택: Emerald Fiery Path 18%"),
    ("MAP_MT_EMBER_SUMMIT_PATH_3F", "land", "all", [9], "SPECIES_SOLROCK", (37, 37), "직접 선택: Ruby Meteor Falls 20-35%(해 = 불씨산, 달 = 달맞이산 루나톤)"),

    # --- Sevii Islands (LeafGreen) ---
    ("MAP_THREE_ISLAND_BERRY_FOREST", "land", "all", [8], "SPECIES_TROPIUS", (35, 35), "직접 선택: 열매 숲 = Emerald Route 119(밀림) 9%"),
    ("MAP_THREE_ISLAND_BERRY_FOREST", "land", "all", [11], "SPECIES_KECLEON", (35, 35), "직접 선택: Emerald Route 118-123 1%(드묾)"),
    ("MAP_FOUR_ISLAND_ICEFALL_CAVE_ENTRANCE", "water", "all", [3], "SPECIES_WOOPER", (15, 25), "FireRed Icefall Cave 입구 파도타기 5%"),
    ("MAP_FOUR_ISLAND_ICEFALL_CAVE_1F", "land", "all", [9], "SPECIES_DELIBIRD", (30, 30), "FireRed Icefall Cave 1F 5%"),
    ("MAP_FOUR_ISLAND_ICEFALL_CAVE_B1F", "land", "all", [9], "SPECIES_DELIBIRD", (30, 30), "FireRed Icefall Cave B1F 5%"),
    ("MAP_SIX_ISLAND_PATTERN_BUSH", "land", "all", [11], "SPECIES_SURSKIT", (20, 20), "직접 선택: Ruby·Sapphire Route 102·114·117·120 풀숲 1%(드묾)"),
    ("MAP_FIVE_ISLAND_LOST_CAVE_ROOM1", "land", "all", [9], "SPECIES_SABLEYE", (35, 35), "직접 선택: 어두운 동굴 = Sapphire·Emerald Granite Cave·Victory Road 10-35%"),
    ("MAP_FIVE_ISLAND_LOST_CAVE_ROOM2", "land", "all", [9], "SPECIES_MURKROW", (22, 22), "FireRed Lost Cave 5%"),
    ("MAP_ONE_ISLAND_TREASURE_BEACH", "fishing", "all", [6], "SPECIES_CLAMPERL", (20, 30), "직접 선택: Emerald Route 124·126 해저 65%"),
    ("MAP_TWO_ISLAND_CAPE_BRINK", "land", "all", [9], "SPECIES_SWABLU", (32, 32), "직접 선택: Emerald Route 115(해변 절벽) 30%"),
    ("MAP_FIVE_ISLAND_RESORT_GORGEOUS", "fishing", "all", [5], "SPECIES_LUVDISC", (20, 30), "직접 선택: Emerald Route 128·Ever Grande City 낚시 60%"),
    ("MAP_FIVE_ISLAND_MEADOW", "land", "all", [8], "SPECIES_EEVEE", (40, 40), "직접 선택(원작 야생 없음): 목초지 4%"),
    ("MAP_SIX_ISLAND_OUTCAST_ISLAND", "fishing", "all", [5], "SPECIES_QWILFISH", (20, 30), "FireRed 5·6·7의섬 바다 낚시 40%"),
    ("MAP_SIX_ISLAND_OUTCAST_ISLAND", "water", "all", [4], "SPECIES_RELICANTH", (35, 40), "직접 선택: Emerald Route 124·126 해저(다이빙) 5% → 파도타기 1%(드묾)"),
    ("MAP_SIX_ISLAND_RUIN_VALLEY", "land", "all", [8], "SPECIES_BALTOY", (35, 35), "직접 선택: 유적 = Emerald Route 111 사막(Desert Ruins 근처) 24%"),
    ("MAP_SEVEN_ISLAND_SEVAULT_CANYON_ENTRANCE", "land", "all", [11], "SPECIES_SUDOWOODO", (35, 35), "직접 선택(원작은 고정 전투): 바위 협곡 입구 1%"),
    ("MAP_SEVEN_ISLAND_SEVAULT_CANYON", "land", "all", [7], "SPECIES_SKARMORY", (30, 30), "FireRed Sevault Canyon 5%"),
    ("MAP_SEVEN_ISLAND_SEVAULT_CANYON", "land", "all", [11], "SPECIES_BAGON", (35, 35), "직접 선택: 깊은 협곡 = Emerald Meteor Falls B1F 25%"),
]
