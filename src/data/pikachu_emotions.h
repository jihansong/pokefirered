// Generated from pret/pokeyellow: data/pikachu/pikachu_emotions.asm, data/pikachu/pikachu_pic_animation.asm,
// data/pikachu/pikachu_pic_objects.asm and data/pikachu/pikachu_pic_tilemaps.asm.
// Yellow composites each expression from tiles every 3 frames; here every tick is pre-rendered
// into graphics/pikachu_emotions/portraits.png (61 frames, 40x40 each, 8 per row).

#define PIKACHU_PORTRAIT_FRAMES_PER_ROW 8
#define PIKACHU_PORTRAIT_SHEET_ROWS 8

static const struct PikachuPortraitCmd sPikachuPortrait0[] = {
    PORTRAIT_FRAME(0, 1),
    PORTRAIT_VOICE(PIKACHU_VOICE_03),
    PORTRAIT_FRAME(0, 1),
    PORTRAIT_FRAME(1, 4),
    PORTRAIT_FRAME(0, 8),
    PORTRAIT_FRAME(1, 4),
    PORTRAIT_FRAME(0, 22),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait1[] = {
    PORTRAIT_FRAME(0, 1),
    PORTRAIT_VOICE(PIKACHU_VOICE_03),
    PORTRAIT_FRAME(0, 1),
    PORTRAIT_FRAME(1, 4),
    PORTRAIT_FRAME(0, 8),
    PORTRAIT_FRAME(1, 4),
    PORTRAIT_FRAME(0, 22),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait2[] = {
    PORTRAIT_FRAME(2, 4),
    PORTRAIT_FRAME(3, 4),
    PORTRAIT_FRAME(2, 4),
    PORTRAIT_FRAME(3, 4),
    PORTRAIT_FRAME(2, 8),
    PORTRAIT_FRAME(3, 4),
    PORTRAIT_FRAME(2, 8),
    PORTRAIT_FRAME(3, 4),
    PORTRAIT_FRAME(2, 4),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait3[] = {
    PORTRAIT_FRAME(4, 1),
    PORTRAIT_FRAME(5, 1),
    PORTRAIT_FRAME(4, 1),
    PORTRAIT_FRAME(5, 64),
    PORTRAIT_FRAME(4, 1),
    PORTRAIT_FRAME(5, 12),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait4[] = {
    PORTRAIT_FRAME(6, 8),
    PORTRAIT_FRAME(7, 8),
    PORTRAIT_FRAME(6, 20),
    PORTRAIT_FRAME(7, 8),
    PORTRAIT_FRAME(6, 8),
    PORTRAIT_FRAME(7, 8),
    PORTRAIT_FRAME(6, 10),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait5[] = {
    PORTRAIT_FRAME(8, 2),
    PORTRAIT_FRAME(9, 2),
    PORTRAIT_FRAME(8, 2),
    PORTRAIT_FRAME(9, 26),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait6[] = {
    PORTRAIT_FRAME(10, 1),
    PORTRAIT_VOICE(PIKACHU_VOICE_38),
    PORTRAIT_FRAME(10, 7),
    PORTRAIT_FRAME(11, 42),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait7[] = {
    PORTRAIT_FRAME(12, 8),
    PORTRAIT_FRAME(13, 2),
    PORTRAIT_FRAME(12, 8),
    PORTRAIT_FRAME(13, 2),
    PORTRAIT_FRAME(12, 16),
    PORTRAIT_FRAME(13, 2),
    PORTRAIT_FRAME(12, 8),
    PORTRAIT_FRAME(13, 2),
    PORTRAIT_FRAME(12, 10),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait8[] = {
    PORTRAIT_FRAME(14, 4),
    PORTRAIT_FRAME(15, 8),
    PORTRAIT_FRAME(14, 4),
    PORTRAIT_FRAME(15, 28),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait9[] = {
    PORTRAIT_FRAME(16, 2),
    PORTRAIT_FRAME(17, 2),
    PORTRAIT_FRAME(16, 2),
    PORTRAIT_FRAME(17, 2),
    PORTRAIT_FRAME(16, 20),
    PORTRAIT_FRAME(17, 2),
    PORTRAIT_FRAME(16, 2),
    PORTRAIT_FRAME(17, 2),
    PORTRAIT_FRAME(16, 2),
    PORTRAIT_FRAME(17, 2),
    PORTRAIT_FRAME(16, 18),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait10[] = {
    PORTRAIT_FRAME(18, 8),
    PORTRAIT_FRAME(19, 3),
    PORTRAIT_FRAME(20, 5),
    PORTRAIT_FRAME(19, 3),
    PORTRAIT_FRAME(18, 13),
    PORTRAIT_FRAME(19, 3),
    PORTRAIT_FRAME(20, 5),
    PORTRAIT_FRAME(19, 3),
    PORTRAIT_FRAME(18, 13),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait11[] = {
    PORTRAIT_FRAME(21, 20),
    PORTRAIT_FRAME(22, 8),
    PORTRAIT_FRAME(21, 20),
    PORTRAIT_FRAME(22, 8),
    PORTRAIT_FRAME(21, 20),
    PORTRAIT_FRAME(22, 8),
    PORTRAIT_FRAME(21, 16),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait12[] = {
    PORTRAIT_FRAME(23, 1),
    PORTRAIT_VOICE(PIKACHU_VOICE_25),
    PORTRAIT_FRAME(23, 12),
    PORTRAIT_FRAME(24, 12),
    PORTRAIT_FRAME(23, 25),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait13[] = {
    PORTRAIT_FRAME(25, 5),
    PORTRAIT_FRAME(26, 5),
    PORTRAIT_FRAME(25, 5),
    PORTRAIT_FRAME(26, 5),
    PORTRAIT_FRAME(25, 30),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait14[] = {
    PORTRAIT_FRAME(27, 2),
    PORTRAIT_FRAME(28, 2),
    PORTRAIT_FRAME(27, 2),
    PORTRAIT_FRAME(28, 2),
    PORTRAIT_FRAME(27, 2),
    PORTRAIT_FRAME(28, 2),
    PORTRAIT_FRAME(27, 2),
    PORTRAIT_FRAME(28, 2),
    PORTRAIT_FRAME(27, 2),
    PORTRAIT_FRAME(28, 2),
    PORTRAIT_FRAME(27, 2),
    PORTRAIT_FRAME(28, 2),
    PORTRAIT_FRAME(27, 2),
    PORTRAIT_FRAME(28, 2),
    PORTRAIT_FRAME(27, 2),
    PORTRAIT_FRAME(28, 2),
    PORTRAIT_FRAME(27, 2),
    PORTRAIT_FRAME(28, 2),
    PORTRAIT_FRAME(27, 2),
    PORTRAIT_FRAME(28, 2),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait15[] = {
    PORTRAIT_FRAME(29, 5),
    PORTRAIT_FRAME(30, 5),
    PORTRAIT_FRAME(29, 5),
    PORTRAIT_FRAME(30, 5),
    PORTRAIT_FRAME(29, 5),
    PORTRAIT_FRAME(30, 5),
    PORTRAIT_FRAME(29, 5),
    PORTRAIT_FRAME(30, 5),
    PORTRAIT_FRAME(29, 5),
    PORTRAIT_FRAME(30, 5),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait16[] = {
    PORTRAIT_FRAME(31, 8),
    PORTRAIT_FRAME(32, 24),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait17[] = {
    PORTRAIT_FRAME(33, 10),
    PORTRAIT_FRAME(34, 3),
    PORTRAIT_FRAME(33, 3),
    PORTRAIT_FRAME(34, 3),
    PORTRAIT_FRAME(33, 81),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait18[] = {
    PORTRAIT_FRAME(35, 1),
    PORTRAIT_VOICE(PIKACHU_VOICE_18),
    PORTRAIT_FRAME(35, 2),
    PORTRAIT_FRAME(36, 29),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait19[] = {
    PORTRAIT_FRAME(37, 6),
    PORTRAIT_FRAME(38, 6),
    PORTRAIT_FRAME(37, 6),
    PORTRAIT_FRAME(38, 6),
    PORTRAIT_FRAME(37, 6),
    PORTRAIT_FRAME(38, 6),
    PORTRAIT_FRAME(37, 6),
    PORTRAIT_FRAME(38, 2),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait20[] = {
    PORTRAIT_FRAME(39, 8),
    PORTRAIT_FRAME(40, 12),
    PORTRAIT_FRAME(39, 8),
    PORTRAIT_FRAME(40, 12),
    PORTRAIT_FRAME(39, 8),
    PORTRAIT_FRAME(40, 2),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait21[] = {
    PORTRAIT_FRAME(41, 1),
    PORTRAIT_VOICE(PIKACHU_VOICE_20),
    PORTRAIT_FRAME(41, 7),
    PORTRAIT_FRAME(42, 2),
    PORTRAIT_FRAME(43, 1),
    PORTRAIT_FRAME(44, 1),
    PORTRAIT_FRAME(45, 28),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait22[] = {
    PORTRAIT_FRAME(46, 8),
    PORTRAIT_FRAME(47, 32),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait23[] = {
    PORTRAIT_FRAME(48, 16),
    PORTRAIT_FRAME(49, 16),
    PORTRAIT_FRAME(48, 16),
    PORTRAIT_FRAME(49, 16),
    PORTRAIT_FRAME(48, 6),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait24[] = {
    PORTRAIT_FRAME(50, 6),
    PORTRAIT_FRAME(51, 6),
    PORTRAIT_FRAME(50, 6),
    PORTRAIT_FRAME(51, 6),
    PORTRAIT_FRAME(50, 36),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait25[] = {
    PORTRAIT_FRAME(52, 6),
    PORTRAIT_FRAME(53, 6),
    PORTRAIT_FRAME(54, 3),
    PORTRAIT_THUNDERBOLT,
    PORTRAIT_FRAME(54, 1),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait26[] = {
    PORTRAIT_FRAME(21, 20),
    PORTRAIT_FRAME(22, 8),
    PORTRAIT_FRAME(21, 20),
    PORTRAIT_FRAME(22, 8),
    PORTRAIT_FRAME(55, 8),
    PORTRAIT_FRAME(56, 36),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait27[] = {
    PORTRAIT_FRAME(57, 4),
    PORTRAIT_FRAME(58, 26),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait28[] = {
    PORTRAIT_FRAME(59, 12),
    PORTRAIT_FRAME(60, 12),
    PORTRAIT_FRAME(59, 12),
    PORTRAIT_FRAME(60, 28),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd sPikachuPortrait29[] = {
    PORTRAIT_FRAME(0, 1),
    PORTRAIT_VOICE(PIKACHU_VOICE_03),
    PORTRAIT_FRAME(0, 1),
    PORTRAIT_FRAME(1, 4),
    PORTRAIT_FRAME(0, 8),
    PORTRAIT_FRAME(1, 4),
    PORTRAIT_FRAME(0, 22),
    PORTRAIT_END,
};

static const struct PikachuPortraitCmd *const sPikachuPortraits[] = {
    [PIKACHU_PORTRAIT_0] = sPikachuPortrait0,
    [PIKACHU_PORTRAIT_1] = sPikachuPortrait1,
    [PIKACHU_PORTRAIT_2] = sPikachuPortrait2,
    [PIKACHU_PORTRAIT_3] = sPikachuPortrait3,
    [PIKACHU_PORTRAIT_4] = sPikachuPortrait4,
    [PIKACHU_PORTRAIT_5] = sPikachuPortrait5,
    [PIKACHU_PORTRAIT_6] = sPikachuPortrait6,
    [PIKACHU_PORTRAIT_7] = sPikachuPortrait7,
    [PIKACHU_PORTRAIT_8] = sPikachuPortrait8,
    [PIKACHU_PORTRAIT_9] = sPikachuPortrait9,
    [PIKACHU_PORTRAIT_10] = sPikachuPortrait10,
    [PIKACHU_PORTRAIT_11] = sPikachuPortrait11,
    [PIKACHU_PORTRAIT_12] = sPikachuPortrait12,
    [PIKACHU_PORTRAIT_13] = sPikachuPortrait13,
    [PIKACHU_PORTRAIT_14] = sPikachuPortrait14,
    [PIKACHU_PORTRAIT_15] = sPikachuPortrait15,
    [PIKACHU_PORTRAIT_16] = sPikachuPortrait16,
    [PIKACHU_PORTRAIT_17] = sPikachuPortrait17,
    [PIKACHU_PORTRAIT_18] = sPikachuPortrait18,
    [PIKACHU_PORTRAIT_19] = sPikachuPortrait19,
    [PIKACHU_PORTRAIT_20] = sPikachuPortrait20,
    [PIKACHU_PORTRAIT_21] = sPikachuPortrait21,
    [PIKACHU_PORTRAIT_22] = sPikachuPortrait22,
    [PIKACHU_PORTRAIT_23] = sPikachuPortrait23,
    [PIKACHU_PORTRAIT_24] = sPikachuPortrait24,
    [PIKACHU_PORTRAIT_25] = sPikachuPortrait25,
    [PIKACHU_PORTRAIT_26] = sPikachuPortrait26,
    [PIKACHU_PORTRAIT_27] = sPikachuPortrait27,
    [PIKACHU_PORTRAIT_28] = sPikachuPortrait28,
    [PIKACHU_PORTRAIT_29] = sPikachuPortrait29,
};

static const u8 sPikachuEmotion0[] = {
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion1[] = {
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_1,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion2[] = {
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_SMILE,
    PIKAEMOTE_VOICE, PIKACHU_VOICE_35,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_2,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion3[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_40,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_3,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion4[] = {
    PIKAEMOTE_MOVEMENT, PIKACHU_MOVEMENT_HOP_TWICE_SLOW,
    PIKAEMOTE_VOICE, PIKACHU_VOICE_29,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_4,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion5[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_31,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_5,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion6[] = {
    PIKAEMOTE_MOVEMENT, PIKACHU_MOVEMENT_TURN,
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_SKULL,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_6,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion7[] = {
    PIKAEMOTE_MOVEMENT, PIKACHU_MOVEMENT_HOP_TWICE_FAST,
    PIKAEMOTE_VOICE, PIKACHU_VOICE_01,
    PIKAEMOTE_MOVEMENT, PIKACHU_MOVEMENT_HOP_TWICE_FAST,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_7,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion8[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_39,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_8,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion9[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_06,
    PIKAEMOTE_MOVEMENT, PIKACHU_MOVEMENT_SPIN,
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_SKULL,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_9,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion10[] = {
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_HEART,
    PIKAEMOTE_VOICE, PIKACHU_VOICE_05,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_10,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion11[] = {
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_ZZZ,
    PIKAEMOTE_VOICE, PIKACHU_VOICE_37,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_11,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion12[] = {
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_12,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion13[] = {
    PIKAEMOTE_MOVEMENT, PIKACHU_MOVEMENT_TURN,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_13,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion14[] = {
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_BOLT,
    PIKAEMOTE_VOICE, PIKACHU_VOICE_10,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_14,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion15[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_34,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_15,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion16[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_33,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_16,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion17[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_13,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_17,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion18[] = {
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_18,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion19[] = {
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_HEART,
    PIKAEMOTE_VOICE, PIKACHU_VOICE_33,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_19,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion20[] = {
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_HEART,
    PIKAEMOTE_VOICE, PIKACHU_VOICE_05,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_20,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion21[] = {
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_FISH,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_21,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion22[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_04,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_22,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion23[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_19,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_23,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion24[] = {
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_EXCLAMATION,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_24,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion25[] = {
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_BOLT,
    PIKAEMOTE_VOICE, PIKACHU_VOICE_35,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_25,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion26[] = {
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_ZZZ,
    PIKAEMOTE_VOICE, PIKACHU_VOICE_37,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_26,
    PIKAEMOTE_TURN_AWAY_IF_ASLEEP_IN_POKECENTER, 0,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion27[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_09,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_27,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion28[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_15,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_28,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion29[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_05,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_10,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion30[] = {
    PIKAEMOTE_TURN_AWAY, 0,
    PIKAEMOTE_BUBBLE, EMOTE_BUBBLE_HEART,
    PIKAEMOTE_VOICE, PIKACHU_VOICE_05,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_20,
    PIKAEMOTE_TURN_AWAY_IF_IN_FAN_CLUB, 0,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion31[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_19,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_23,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion32[] = {
    PIKAEMOTE_VOICE, PIKACHU_VOICE_26,
    PIKAEMOTE_PORTRAIT, PIKACHU_PORTRAIT_23,
    PIKAEMOTE_END,
};

static const u8 sPikachuEmotion33[] = {
    PIKAEMOTE_END,
};

// Length of each voice clip in frames, used as the cry note length.
static const u8 sPikachuVoiceLengths[] = {
    [PIKACHU_VOICE_01] = 53,
    [PIKACHU_VOICE_02] = 40,
    [PIKACHU_VOICE_03] = 59,
    [PIKACHU_VOICE_04] = 91,
    [PIKACHU_VOICE_05] = 93,
    [PIKACHU_VOICE_06] = 103,
    [PIKACHU_VOICE_07] = 79,
    [PIKACHU_VOICE_08] = 96,
    [PIKACHU_VOICE_09] = 76,
    [PIKACHU_VOICE_10] = 181,
    [PIKACHU_VOICE_11] = 42,
    [PIKACHU_VOICE_12] = 78,
    [PIKACHU_VOICE_13] = 111,
    [PIKACHU_VOICE_14] = 140,
    [PIKACHU_VOICE_15] = 117,
    [PIKACHU_VOICE_16] = 117,
    [PIKACHU_VOICE_17] = 49,
    [PIKACHU_VOICE_18] = 86,
    [PIKACHU_VOICE_19] = 126,
    [PIKACHU_VOICE_20] = 181,
    [PIKACHU_VOICE_21] = 181,
    [PIKACHU_VOICE_22] = 143,
    [PIKACHU_VOICE_23] = 85,
    [PIKACHU_VOICE_24] = 159,
    [PIKACHU_VOICE_25] = 82,
    [PIKACHU_VOICE_26] = 78,
    [PIKACHU_VOICE_27] = 66,
    [PIKACHU_VOICE_28] = 104,
    [PIKACHU_VOICE_29] = 70,
    [PIKACHU_VOICE_30] = 29,
    [PIKACHU_VOICE_31] = 44,
    [PIKACHU_VOICE_32] = 33,
    [PIKACHU_VOICE_33] = 73,
    [PIKACHU_VOICE_34] = 120,
    [PIKACHU_VOICE_35] = 104,
    [PIKACHU_VOICE_36] = 158,
    [PIKACHU_VOICE_37] = 80,
    [PIKACHU_VOICE_38] = 72,
    [PIKACHU_VOICE_39] = 100,
    [PIKACHU_VOICE_40] = 86,
    [PIKACHU_VOICE_41] = 137,
    [PIKACHU_VOICE_42] = 122,
};

static const u8 *const sPikachuEmotions[] = {
    [PIKACHU_EMOTION_0] = sPikachuEmotion0,
    [PIKACHU_EMOTION_1] = sPikachuEmotion1,
    [PIKACHU_EMOTION_2] = sPikachuEmotion2,
    [PIKACHU_EMOTION_3] = sPikachuEmotion3,
    [PIKACHU_EMOTION_4] = sPikachuEmotion4,
    [PIKACHU_EMOTION_5] = sPikachuEmotion5,
    [PIKACHU_EMOTION_6] = sPikachuEmotion6,
    [PIKACHU_EMOTION_7] = sPikachuEmotion7,
    [PIKACHU_EMOTION_8] = sPikachuEmotion8,
    [PIKACHU_EMOTION_9] = sPikachuEmotion9,
    [PIKACHU_EMOTION_10] = sPikachuEmotion10,
    [PIKACHU_EMOTION_11] = sPikachuEmotion11,
    [PIKACHU_EMOTION_12] = sPikachuEmotion12,
    [PIKACHU_EMOTION_13] = sPikachuEmotion13,
    [PIKACHU_EMOTION_14] = sPikachuEmotion14,
    [PIKACHU_EMOTION_15] = sPikachuEmotion15,
    [PIKACHU_EMOTION_16] = sPikachuEmotion16,
    [PIKACHU_EMOTION_17] = sPikachuEmotion17,
    [PIKACHU_EMOTION_18] = sPikachuEmotion18,
    [PIKACHU_EMOTION_19] = sPikachuEmotion19,
    [PIKACHU_EMOTION_20] = sPikachuEmotion20,
    [PIKACHU_EMOTION_21] = sPikachuEmotion21,
    [PIKACHU_EMOTION_22] = sPikachuEmotion22,
    [PIKACHU_EMOTION_23] = sPikachuEmotion23,
    [PIKACHU_EMOTION_24] = sPikachuEmotion24,
    [PIKACHU_EMOTION_25] = sPikachuEmotion25,
    [PIKACHU_EMOTION_26] = sPikachuEmotion26,
    [PIKACHU_EMOTION_27] = sPikachuEmotion27,
    [PIKACHU_EMOTION_28] = sPikachuEmotion28,
    [PIKACHU_EMOTION_29] = sPikachuEmotion29,
    [PIKACHU_EMOTION_30] = sPikachuEmotion30,
    [PIKACHU_EMOTION_31] = sPikachuEmotion31,
    [PIKACHU_EMOTION_32] = sPikachuEmotion32,
    [PIKACHU_EMOTION_33] = sPikachuEmotion33,
};
