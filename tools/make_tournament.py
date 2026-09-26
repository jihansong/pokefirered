#!/usr/bin/env python3
"""The INDIGO PLATEAU champion tournament (Thunder Yellow v0.6.0).

Sixteen entrants - the eight GYM LEADERS, the ELITE FOUR, the RIVAL, PROF. OAK,
N and TEAM ROCKET's JESSIE & JAMES - wait for a draw of three. Their trainer
numbers sit after the imported Hoenn trainers (FR/LG's own 768 are nearly full),
so their "defeated" bits land in SaveBlock2.hoennTrainerFlags. The tournament
clears those bits before every match, so entrants can be met again.

Writes the constants, trainer entries, parties and the per-entrant battle
branches. Run it again after changing ENTRANTS."""
import os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BASE = 520  # offset past the imported Hoenn trainers

# name, class, pic, music, doubles, [(species, level[, [moves]])]
# An entrant whose POKéMON list moves gets a custom-move party (all four
# moves for every one of them: the engine sets that per party, not per POKéMON).
ENTRANTS = [
 ('BROCK', 'LEADER', 'LEADER_BROCK', 'MALE', False,
  [('ONIX', 66), ('GOLEM', 68), ('RHYDON', 68), ('AERODACTYL', 69), ('STEELIX', 70)]),
 ('MISTY', 'LEADER', 'LEADER_MISTY', 'FEMALE', False,
  [('GOLDUCK', 66), ('LAPRAS', 68), ('GYARADOS', 69), ('VAPOREON', 68), ('STARMIE', 70)]),
 ('LT.SURGE', 'LEADER', 'LEADER_LT_SURGE', 'MALE', False,
  [('ELECTRODE', 66), ('MAGNETON', 67), ('MANECTRIC', 68), ('JOLTEON', 69), ('RAICHU', 70)]),
 ('ERIKA', 'LEADER', 'LEADER_ERIKA', 'FEMALE', False,
  [('TANGELA', 66), ('BELLOSSOM', 68), ('BRELOOM', 68), ('VILEPLUME', 69), ('VICTREEBEL', 70)]),
 ('KOGA', 'LEADER', 'LEADER_KOGA', 'MALE', False,
  [('ARIADOS', 66), ('VENOMOTH', 67), ('MUK', 68), ('WEEZING', 69), ('CROBAT', 70)]),
 ('SABRINA', 'LEADER', 'LEADER_SABRINA', 'FEMALE', False,
  [('MR_MIME', 66), ('SLOWBRO', 67), ('ESPEON', 68), ('GARDEVOIR', 69), ('ALAKAZAM', 71)]),
 ('BLAINE', 'LEADER', 'LEADER_BLAINE', 'MALE', False,
  [('MAGCARGO', 66), ('RAPIDASH', 67), ('HOUNDOOM', 68), ('MAGMAR', 69), ('ARCANINE', 71)]),
 ('GIOVANNI', 'LEADER', 'LEADER_GIOVANNI', 'MALE', False,
  [('DUGTRIO', 67), ('PERSIAN', 67), ('NIDOQUEEN', 69), ('NIDOKING', 70), ('RHYDON', 71)]),
 ('LORELEI', 'ELITE_FOUR', 'ELITE_FOUR_LORELEI', 'FEMALE', False,
  [('DEWGONG', 68), ('CLOYSTER', 69), ('JYNX', 70), ('GLALIE', 70), ('LAPRAS', 72)]),
 ('BRUNO', 'ELITE_FOUR', 'ELITE_FOUR_BRUNO', 'MALE', False,
  [('HITMONLEE', 68), ('HITMONCHAN', 69), ('HARIYAMA', 70), ('ONIX', 70), ('MACHAMP', 72)]),
 ('AGATHA', 'ELITE_FOUR', 'ELITE_FOUR_AGATHA', 'FEMALE', False,
  [('GOLBAT', 68), ('BANETTE', 69), ('ARBOK', 70), ('HAUNTER', 70), ('GENGAR', 72)]),
 ('LANCE', 'ELITE_FOUR', 'ELITE_FOUR_LANCE', 'MALE', False,
  [('GYARADOS', 69), ('AERODACTYL', 70), ('KINGDRA', 71), ('SALAMENCE', 72), ('DRAGONITE', 74)]),
 ('BLUE', 'CHAMPION', 'CHAMPION_RIVAL', 'MALE', False,
  [('PIDGEOT', 70), ('RHYDON', 71), ('ARCANINE', 71), ('EXEGGUTOR', 72), ('ALAKAZAM', 73), ('BLASTOISE', 75)]),
 ('OAK', 'PKMN_PROF', 'PROFESSOR_OAK', 'MALE', False,
  [('TAUROS', 70), ('EXEGGUTOR', 71), ('ARCANINE', 72), ('LAPRAS', 72), ('GYARADOS', 73), ('VENUSAUR', 75)]),
 ('N', 'PKMN_TRAINER', 'N', 'MALE', False,
  [('MIGHTYENA', 69), ('SWELLOW', 70), ('SHIFTRY', 71), ('BANETTE', 71), ('GARDEVOIR', 73)]),
 # v0.9.0: MEOWTH last and highest (the prize reads the last one's level)
 ('JESSIE&JAMES', 'TEAM_ROCKET', 'JESSIE_JAMES', 'AQUA', True,
  [('ARBOK', 70, ['SLUDGE_BOMB', 'BITE', 'GLARE', 'IRON_TAIL']),
   ('WEEZING', 70, ['SLUDGE_BOMB', 'FLAMETHROWER', 'THUNDERBOLT', 'SHADOW_BALL']),
   ('VICTREEBEL', 70, ['GIGA_DRAIN', 'SLUDGE_BOMB', 'RAZOR_LEAF', 'SLEEP_POWDER']),
   ('GYARADOS', 71, ['HYDRO_PUMP', 'BITE', 'DRAGON_DANCE', 'HYPER_BEAM']),
   ('WOBBUFFET', 71, ['COUNTER', 'MIRROR_COAT', 'SAFEGUARD', 'DESTINY_BOND']),
   ('MEOWTH', 73, ['PAY_DAY', 'SLASH', 'FAKE_OUT', 'SHADOW_BALL'])]),
]


def ident(name):
    return ''.join(c for c in name.upper().replace('.', '').replace('&', '_').replace(' ', '_') if c.isalnum() or c == '_')


def camel(name):
    return ''.join(p.capitalize() for p in ident(name).split('_'))


consts = ''.join('#define TRAINER_TOURNEY_%-22s (HOENN_TRAINERS_START + %d)\n' % (ident(n), BASE + i)
                 for i, (n, *_rest) in enumerate(ENTRANTS))
open(R + '/include/constants/opponents_tournament.h', 'w').write(
    '#ifndef GUARD_CONSTANTS_OPPONENTS_TOURNAMENT_H\n#define GUARD_CONSTANTS_OPPONENTS_TOURNAMENT_H\n\n'
    '// The INDIGO PLATEAU tournament entrants (tools/make_tournament.py). They sit\n'
    '// after the imported Hoenn trainers, so their flags live in hoennTrainerFlags.\n\n'
    + consts + '\n#define TOURNEY_ENTRANT_COUNT %d\n\n' % len(ENTRANTS)
    + '#endif  // GUARD_CONSTANTS_OPPONENTS_TOURNAMENT_H\n')

parties = '// Tournament parties (tools/make_tournament.py)\n\n'
trainers = '// Tournament entrants (tools/make_tournament.py)\n\n'
for name, cls, pic, music, doubles, mons in ENTRANTS:
    label = 'sParty_Tourney' + camel(name)
    custom = any(len(m) > 2 for m in mons)
    parties += 'static const struct TrainerMonNoItem%sMoves %s[] = {\n' % ('Custom' if custom else 'Default', label)
    for mon in mons:
        species, lvl = mon[:2]
        parties += '    {\n        .iv = 255,\n        .lvl = %d,\n        .species = SPECIES_%s,\n' % (lvl, species)
        if custom:
            moves = (list(mon[2]) + ['NONE'] * 4)[:4]
            parties += '        .moves = {%s},\n' % ', '.join('MOVE_' + m for m in moves)
        parties += '    },\n'
    parties += '};\n\n'
    trainers += '''    [TRAINER_TOURNEY_%s] = {
        .trainerClass = TRAINER_CLASS_%s,
        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_%s,
        .trainerPic = TRAINER_PIC_%s,
        .trainerName = _("%s"),
        .items = {ITEM_FULL_RESTORE, ITEM_FULL_RESTORE},
        .doubleBattle = %s,
        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,
        .party = NO_ITEM_%s_MOVES(%s),
    },
''' % (ident(name), cls, music, pic, name, 'TRUE' if doubles else 'FALSE', 'CUSTOM' if custom else 'DEFAULT', label)
open(R + '/src/data/trainer_parties_tournament.h', 'w').write(parties)
open(R + '/src/data/trainers_tournament.h', 'w').write(trainers)

# One battle branch per entrant: the tournament picks an index, the script jumps here.
s = '''@ The INDIGO PLATEAU tournament's matches (tools/make_tournament.py).
@ Tournament_SetUpMatch puts the entrant's index in VAR_0x8008 and their name in
@ STR_VAR_2, then this switch runs that entrant's battle.

EventScript_TourneyBattle::
\tswitch VAR_0x8008
'''
for i, (name, *_rest) in enumerate(ENTRANTS):
    s += '\tcase %d, EventScript_TourneyBattle%s\n' % (i, camel(name))
s += '\tend\n'
for name, *_rest in ENTRANTS:
    s += '''
EventScript_TourneyBattle%s::
\tcleartrainerflag TRAINER_TOURNEY_%s
\ttrainerbattle_no_intro TRAINER_TOURNEY_%s, Text_TourneyDefeat
\tcleartrainerflag TRAINER_TOURNEY_%s
\treturn
''' % (camel(name), ident(name), ident(name), ident(name))
s += '''
Text_TourneyDefeat::
\t.string "A fine battle. The tournament\\n"
\t.string "belongs to the strong!$"
'''
open(R + '/data/scripts/tournament_battles.inc', 'w').write(s)
print('ok: %d entrants' % len(ENTRANTS))
