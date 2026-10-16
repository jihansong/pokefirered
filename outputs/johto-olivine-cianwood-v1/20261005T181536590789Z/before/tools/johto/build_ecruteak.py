#!/usr/bin/env python3
"""Append the Goldenrod-to-Ecruteak chapter. Dry run unless --apply."""
import argparse,copy,datetime,json,re,struct,subprocess,sys
from collections import deque
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_cherrygrove as C
import build_violet as V
import build_ilex_goldenrod as I
Source,enc,sha=C.Source,C.enc,C.sha
OLD=I.OLD+I.NEW
NEW=['GoldenrodCity_NorthGate','JohtoRoute35','JohtoRoute35_NationalParkGate','JohtoNationalPark','JohtoNationalPark_Route36Gate','JohtoRoute36','JohtoRoute37','EcruteakCity','EcruteakCity_PokemonCenter_1F','EcruteakCity_PokemonCenter_2F','EcruteakCity_Mart','EcruteakCity_DanceTheater','EcruteakCity_Gym','BurnedTower_1F','BurnedTower_B1F']
IDS=['GOLDENROD_CITY_NORTH_GATE','JOHTO_ROUTE35','JOHTO_ROUTE35_NATIONAL_PARK_GATE','JOHTO_NATIONAL_PARK','JOHTO_NATIONAL_PARK_ROUTE36_GATE','JOHTO_ROUTE36','JOHTO_ROUTE37','ECRUTEAK_CITY','ECRUTEAK_CITY_POKEMON_CENTER_1F','ECRUTEAK_CITY_POKEMON_CENTER_2F','ECRUTEAK_CITY_MART','ECRUTEAK_CITY_DANCE_THEATER','ECRUTEAK_CITY_GYM','BURNED_TOWER_1F','BURNED_TOWER_B1F']
MID=dict(zip(NEW,['MAP_'+x for x in IDS]))
MARK='JOHTO_ECRUTEAK_CHAPTER_V1'
FLAGS={'FLAG_JOHTO_BADGE04_GET':19,'FLAG_JOHTO_SQUIRTBOTTLE_RECEIVED':29,'FLAG_JOHTO_SUDOWOODO_CLEARED':30,'FLAG_JOHTO_BURNED_TOWER_INVESTIGATED':31,'FLAG_JOHTO_SILVER_BURNED_TOWER_DEFEATED':32,'FLAG_JOHTO_GOT_TM30_FROM_MORTY':33,'FLAG_JOHTO_DANCE_SURF_REWARDED':34}
TRAINERS=[
 ('ARNIE','BUG_CATCHER','BUG_CATCHER','MALE',[('VENONAT',18)],806),
 ('IVAN','PSYCHIC','PSYCHIC_M','MALE',[('ABRA',17),('KADABRA',19)],807),
 ('KIMONO_NAOKO','BEAUTY','BEAUTY','FEMALE',[('ESPEON',22,['CONFUSION','QUICK_ATTACK','SAND_ATTACK','SWIFT'])],808),
 ('KIMONO_SAYO','BEAUTY','BEAUTY','FEMALE',[('UMBREON',22,['PURSUIT','QUICK_ATTACK','SAND_ATTACK','CONFUSE_RAY'])],809),
 ('KIMONO_ZUKI','BEAUTY','BEAUTY','FEMALE',[('FLAREON',22,['EMBER','QUICK_ATTACK','SAND_ATTACK','SMOG'])],810),
 ('KIMONO_KUNI','BEAUTY','BEAUTY','FEMALE',[('JOLTEON',22,['THUNDER_SHOCK','QUICK_ATTACK','DOUBLE_KICK','SAND_ATTACK'])],811),
 ('KIMONO_MIKI','BEAUTY','BEAUTY','FEMALE',[('VAPOREON',22,['WATER_GUN','QUICK_ATTACK','SAND_ATTACK','BITE'])],812),
 ('SILVER_BURNED_TOWER','RIVAL_LATE','RIVAL_LATE','MALE',[('HAUNTER',22,['LICK','SPITE','MEAN_LOOK','CURSE']),('MAGNEMITE',20,['THUNDER_SHOCK','SONIC_BOOM','SUPERSONIC','THUNDER_WAVE']),('ZUBAT',20,['LEECH_LIFE','BITE','SUPERSONIC','CONFUSE_RAY']),('CROCONAW',23,['WATER_GUN','BITE','RAGE','SCARY_FACE'])],813),
 ('PING','CHANNELER','CHANNELER','MALE',[('GASTLY',22),('HAUNTER',22)],814),
 ('GRACE','CHANNELER','CHANNELER','FEMALE',[('HAUNTER',23)],815),
 ('MORTY','LEADER','CHANNELER','MALE',[('GASTLY',21,['LICK','SPITE','MEAN_LOOK','CURSE']),('HAUNTER',21,['HYPNOSIS','DREAM_EATER','SPITE','NIGHT_SHADE']),('GENGAR',25,['HYPNOSIS','SHADOW_BALL','MEAN_LOOK','DREAM_EATER']),('HAUNTER',23,['CURSE','MEAN_LOOK','NIGHT_SHADE','SPITE'])],816)]
WILD={
 'JohtoRoute35':(['NIDORAN_F','NIDORAN_M','DROWZEE','PIDGEY','NIDORAN_F','NIDORAN_M','YANMA','ABRA','DITTO','YANMA','DITTO','YANMA'],['NIDORAN_F','NIDORAN_M','DROWZEE','HOOTHOOT','NIDORAN_F','NIDORAN_M','YANMA','ABRA','DITTO','YANMA','DITTO','NOCTOWL'],[12,12,13,12,13,13,12,14,13,14,14,14]),
 'JohtoNationalPark':(['CATERPIE','WEEDLE','PIDGEY','METAPOD','KAKUNA','PIDGEY','SUNKERN','METAPOD','SUNKERN','KAKUNA','BUTTERFREE','BEEDRILL'],['HOOTHOOT','HOOTHOOT','HOOTHOOT','HOOTHOOT','HOOTHOOT','HOOTHOOT','HOOTHOOT','HOOTHOOT','HOOTHOOT','HOOTHOOT','NOCTOWL','NOCTOWL'],[12,12,12,13,13,13,12,14,13,14,14,14]),
 'JohtoRoute36':(['GROWLITHE','NIDORAN_F','NIDORAN_M','PIDGEY','GROWLITHE','NIDORINO','NIDORINA','STANTLER','PIDGEY','STANTLER','NIDORINO','NIDORINA'],['GROWLITHE','NIDORAN_F','NIDORAN_M','HOOTHOOT','GROWLITHE','NIDORINO','NIDORINA','STANTLER','HOOTHOOT','STANTLER','NOCTOWL','STANTLER'],[14,14,14,15,15,15,15,14,15,16,16,16]),
 'JohtoRoute37':(['PIDGEY','LEDYBA','SPINARAK','PIDGEOTTO','STANTLER','PIDGEY','STANTLER','PIDGEOTTO','LEDYBA','STANTLER','PIDGEOTTO','STANTLER'],['HOOTHOOT','SPINARAK','SPINARAK','NOCTOWL','STANTLER','HOOTHOOT','STANTLER','NOCTOWL','SPINARAK','STANTLER','NOCTOWL','STANTLER'],[15,15,15,16,15,15,16,16,16,16,17,17]),
 'BurnedTower_1F':(['RATTATA','ZUBAT','KOFFING','RATTATA','ZUBAT','KOFFING','RATTATA','ZUBAT','KOFFING','MAGMAR','KOFFING','MAGMAR'],['RATTATA','ZUBAT','KOFFING','RATTATA','ZUBAT','KOFFING','RATTATA','ZUBAT','KOFFING','MAGMAR','KOFFING','MAGMAR'],[14,14,14,15,15,15,16,16,16,14,16,16]),
 'BurnedTower_B1F':(['RATTATA','ZUBAT','KOFFING','RATICATE','ZUBAT','KOFFING','RATICATE','ZUBAT','KOFFING','MAGMAR','KOFFING','MAGMAR'],['RATTATA','ZUBAT','KOFFING','RATICATE','ZUBAT','KOFFING','RATICATE','ZUBAT','KOFFING','MAGMAR','KOFFING','MAGMAR'],[15,15,15,16,16,16,17,17,17,15,17,17])}
def ident(n):return IDS[NEW.index(n)]
def warp(x,y,dst,index,elevation=3):
 return {'x':x,'y':y,'elevation':elevation,'dest_map':MID.get(dst,dst),'dest_warp_id':str(index)}
def obj(gfx,x,y,script,**kw):
 flag=kw.pop('flag','0');v=C.obj(gfx,x,y,script,**kw);v['flag']=flag;return v


def geometry(s):
 vir=V.layout_array(s,'LAYOUT_VIRIDIAN_CITY');pew=V.layout_array(s,'LAYOUT_PEWTER_CITY');saff=V.layout_array(s,'LAYOUT_SAFFRON_CITY')
 gate=V.layout_array(s,'LAYOUT_ROUTE2_ENTRANCE')
 def land(w,h):
  a=[[0x3001]*w for _ in range(h)]
  for box in [(0,0,w,2),(0,0,2,h),(w-2,0,w,h),(0,h-2,w,h)]:C.fill(a,*box,C.dense)
  return a
 route35=land(24,36);C.fill(route35,8,3,12,34,0x3195)
 C.paste(route35,V.crop(vir,24,8,5,4),8,0);C.paste(route35,V.crop(vir,24,8,5,4),8,28)
 C.fill(route35,3,9,7,23,C.grass);C.fill(route35,14,9,21,23,C.grass)
 park=land(36,36)
 C.fill(park,14,2,20,34,0x3195);C.fill(park,6,17,33,22,0x3195)
 for box in [(5,4,12,14),(22,4,30,14),(4,24,12,30),(22,24,31,30)]:C.fill(park,*box,C.grass)
 C.paste(park,V.crop(vir,24,8,5,4),14,29);C.paste(park,V.crop(vir,24,8,5,4),30,15)
 for box in [(8,16,12,17),(23,16,27,17),(8,22,12,23),(23,22,27,23)]:C.fill(park,*box,0x3004)
 route36=land(36,24)
 C.fill(route36,3,18,28,21,0x3195);C.fill(route36,24,0,28,21,0x3195)
 C.paste(route36,V.crop(vir,24,8,5,4),2,14)
 C.fill(route36,2,8,25,9,C.dense);C.fill(route36,26,8,34,9,C.dense)
 C.fill(route36,8,11,17,16,C.grass);C.fill(route36,28,11,33,17,C.grass)
 route37=land(24,24);C.fill(route37,8,0,12,24,0x3195)
 C.fill(route37,3,4,7,13,C.grass);C.fill(route37,14,7,21,19,C.grass)
 city=land(40,36);C.fill(city,18,2,22,36,0x3195);C.fill(city,3,17,37,22,0x3195);C.fill(city,6,28,36,32,0x3195)
 C.fill(city,7,6,11,30,0x3195);C.fill(city,31,18,36,30,0x3195)
 C.paste(city,V.crop(saff,22,34,5,5),6,24)
 C.paste(city,V.crop(vir,34,16,4,4),31,24)
 C.paste(city,V.crop(pew,12,12,7,5),26,7)
 C.paste(city,V.crop(saff,21,11,5,4),13,11)
 C.paste(city,V.crop(pew,12,12,7,5),4,2)
 for x,y in [(12,28),(36,27),(34,11),(17,14),(12,6)]:city[y][x]=0x0403
 C.fill(city,24,23,30,27,0x3004)
 tower=[[0x3284]*28 for _ in range(24)]
 cellar=[[0x3284]*28 for _ in range(24)]
 for a in (tower,cellar):
  for box in [(0,0,28,2),(0,0,2,24),(26,0,28,24),(0,22,28,24)]:C.fill(a,*box,0x0408)
  for box in [(6,6,9,10),(18,5,21,9),(7,15,10,18),(18,15,21,18)]:C.fill(a,*box,0x06a2)
 # Native mansion door and staircase behaviors, with clear approach squares.
 tower[22][13]=0x32e9;tower[4][23]=0x32d2;cellar[4][23]=0x3363
 # Silver checkpoint is a single path; the walls cannot be walked around.
 C.fill(tower,2,11,13,12,0x0408);C.fill(tower,14,11,26,12,0x0408)
 return {'GoldenrodCity_NorthGate':copy.deepcopy(gate),'JohtoRoute35':route35,
 'JohtoRoute35_NationalParkGate':copy.deepcopy(gate),'JohtoNationalPark':park,
 'JohtoNationalPark_Route36Gate':copy.deepcopy(gate),'JohtoRoute36':route36,'JohtoRoute37':route37,
 'EcruteakCity':city,'BurnedTower_1F':tower,'BurnedTower_B1F':cellar}


def ecruteak_story():
 scripts={};texts={}
 def add(n,k,body):
  scripts.setdefault(n,n+'_MapScripts::\n    .byte 0\n')
  scripts[n]+='\n'+n+'_'+k+'::\n'+body.strip()+'\n'
 def say(n,k,paras):
  add(n,k,'    msgbox '+n+'_Text_'+k+', MSGBOX_NPC\n    end')
  texts.setdefault(n,{})[k]=paras
 n='GoldenrodCity_NorthGate'
 add(n,'CheckPass',r'''
    goto_if_set FLAG_JOHTO_BADGE03_GET, GoldenrodCity_NorthGate_Pass
    lockall
    msgbox GoldenrodCity_NorthGate_Text_Stop
    applymovement LOCALID_PLAYER, GoldenrodCity_NorthGate_StepBack
    waitmovement 0
    releaseall
    end
GoldenrodCity_NorthGate_Pass::
    setvar VAR_TEMP_0, 1
    end
GoldenrodCity_NorthGate_StepBack:
    walk_down
    step_end
''')
 say(n,'Officer',["ROUTE 35 reaches NATIONAL PARK.\nThe east path leads to ECRUTEAK.",
  "WHITNEY has a message for you.\nCollect your BADGE before going."])
 add(n,'Florist',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_SQUIRTBOTTLE_RECEIVED, GoldenrodCity_NorthGate_FloristAfter
    goto_if_unset FLAG_JOHTO_BADGE03_GET, GoldenrodCity_NorthGate_FloristBefore
    msgbox GoldenrodCity_NorthGate_Text_FloristLend
    setflag FLAG_JOHTO_SQUIRTBOTTLE_RECEIVED
    release
    end
GoldenrodCity_NorthGate_FloristBefore::
    msgbox GoldenrodCity_NorthGate_Text_FloristBefore
    release
    end
GoldenrodCity_NorthGate_FloristAfter::
    msgbox GoldenrodCity_NorthGate_Text_FloristAfter
    release
    end
''')
 texts[n].update({'Stop':["Finish your visit with WHITNEY.\nThe northern trail can wait."],
 'FloristBefore':["A strange tree blocks ROUTE 36.\nWHITNEY knows the forest worker."],
 'FloristLend':["WHITNEY sent you? Take our\nSQUIRTBOTTLE for that odd tree.",
  "It hates water. Please try a\nlittle sprinkle, then be ready!"],
 'FloristAfter':["Use the borrowed SQUIRTBOTTLE\non the strange tree on ROUTE 36."]})
 n='JohtoRoute35'
 say(n,'RouteSign',["ROUTE 35\nGOLDENROD - NATIONAL PARK"])
 n='JohtoRoute35_NationalParkGate'
 say(n,'Officer',["NATIONAL PARK protects JOHTO's\nwildlife. Stay on the paths."])
 n='JohtoNationalPark'
 say(n,'Caretaker',["ELM's research has reached us.\nKANTO's records help our work.",
  "The northern towns have heard\ncries from the old tower."])
 say(n,'ParkSign',["NATIONAL PARK\nEnjoy nature. Let wildlife rest."])
 n='JohtoNationalPark_Route36Gate'
 say(n,'Officer',["ROUTE 36 goes east, then north\nto ROUTE 37 and ECRUTEAK.",
  "A strange tree blocks the north\npath. A gardener may know why."])
 n='JohtoRoute36'
 add(n,'Sudowoodo',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_SUDOWOODO_CLEARED, JohtoRoute36_SudowoodoDone
    goto_if_unset FLAG_JOHTO_SQUIRTBOTTLE_RECEIVED, JohtoRoute36_NeedWater
    msgbox JohtoRoute36_Text_Water
    setwildbattle SPECIES_SUDOWOODO, 20
    waitse
    playmoncry SPECIES_SUDOWOODO, CRY_MODE_ENCOUNTER
    waitmoncry
    setflag FLAG_SYS_SPECIAL_WILD_BATTLE
    dowildbattle
    clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
    specialvar VAR_RESULT, GetBattleOutcome
    goto_if_eq VAR_RESULT, B_OUTCOME_WON, JohtoRoute36_SudowoodoClear
    goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, JohtoRoute36_SudowoodoClear
    release
    end
JohtoRoute36_SudowoodoClear::
    setflag FLAG_JOHTO_SUDOWOODO_CLEARED
    removeobject 1
    msgbox JohtoRoute36_Text_Clear
    release
    end
JohtoRoute36_NeedWater::
    msgbox JohtoRoute36_Text_NeedWater
    release
    end
JohtoRoute36_SudowoodoDone::
    release
    end
''')
 say(n,'Worker',["A POKEMON disguised as a tree!\nELM will want to hear about it.",
  "ECRUTEAK's old tower has more\nmysteries for a careful trainer."])
 texts[n].update({'Water':["You sprinkle water from the\nborrowed SQUIRTBOTTLE.",
  "The strange tree comes to life!\nSUDOWOODO attacks!"],
 'Clear':["The north path is clear now.\nROUTE 37 leads to ECRUTEAK."],
 'NeedWater':["This tree seems to move...\nMaybe it dislikes water."]})
 n='JohtoRoute37'
 say(n,'Traveler',["TEAM ROCKET fled through here.\nThey asked about legendary life.",
  "They talked about their failed\nKANTO plans and a distant sea."])
 say(n,'RouteSign',["ROUTE 37\nECRUTEAK CITY to the north"])
 n='EcruteakCity'
 say(n,'Resident',["ECRUTEAK remembers the old fire.\nThree lives were saved that day.",
  "MORTY went to the BURNED TOWER.\nSpeak to him before the GYM."])
 say(n,'DanceFan',["The KIMONO GIRLS train together.\nTheir dances teach teamwork.",
  "Their patron rewards trainers\nwho can defeat all five girls."])
 for k,paras in [('CenterSign',["ECRUTEAK POKEMON CENTER"]),
 ('MartSign',["ECRUTEAK POKEMON MART"]),('GymSign',["ECRUTEAK GYM\nLeader: MORTY"]),
 ('DanceSign',["ECRUTEAK DANCE THEATER"]),('TowerSign',["BURNED TOWER\nWatch your step inside."])]:
  say(n,k,paras)
 n='EcruteakCity_DanceTheater'
 for k in ['NAOKO','SAYO','ZUKI','KUNI','MIKI']:
  add(n,k,'    trainerbattle_single TRAINER_JOHTO_KIMONO_'+k+', '+n+'_Text_'+k+'Intro, '+n+'_Text_'+k+'Defeat\n    msgbox '+n+'_Text_'+k+'After, MSGBOX_AUTOCLOSE\n    end')
  texts.setdefault(n,{})[k+'Intro']=["Our steps and our POKEMON\nmove as one. Let us battle!"]
  texts[n][k+'Defeat']=["Your team has a lovely rhythm!"]
  texts[n][k+'After']=["We learn by watching each other."]
 add(n,'Patron',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_DANCE_SURF_REWARDED, EcruteakCity_DanceTheater_PatronAfter
    goto_if_not_defeated TRAINER_JOHTO_KIMONO_NAOKO, EcruteakCity_DanceTheater_PatronBefore
    goto_if_not_defeated TRAINER_JOHTO_KIMONO_SAYO, EcruteakCity_DanceTheater_PatronBefore
    goto_if_not_defeated TRAINER_JOHTO_KIMONO_ZUKI, EcruteakCity_DanceTheater_PatronBefore
    goto_if_not_defeated TRAINER_JOHTO_KIMONO_KUNI, EcruteakCity_DanceTheater_PatronBefore
    goto_if_not_defeated TRAINER_JOHTO_KIMONO_MIKI, EcruteakCity_DanceTheater_PatronBefore
    goto_if_set FLAG_GOT_HM03, EcruteakCity_DanceTheater_Alternate
    checkitem ITEM_HM03, 1
    goto_if_eq VAR_RESULT, TRUE, EcruteakCity_DanceTheater_Alternate
    checkpcitem ITEM_HM03, 1
    goto_if_eq VAR_RESULT, TRUE, EcruteakCity_DanceTheater_Alternate
    checkitemspace ITEM_HM03, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_DanceTheater_BagFull
    giveitem ITEM_HM03, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_DanceTheater_BagFull
    setflag FLAG_JOHTO_DANCE_SURF_REWARDED
    msgbox EcruteakCity_DanceTheater_Text_Surf
    release
    end
EcruteakCity_DanceTheater_Alternate::
    checkitemspace ITEM_TM35, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_DanceTheater_BagFull
    msgbox EcruteakCity_DanceTheater_Text_AlreadySurf
    giveitem ITEM_TM35, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_DanceTheater_BagFull
    setflag FLAG_JOHTO_DANCE_SURF_REWARDED
    msgbox EcruteakCity_DanceTheater_Text_Alternate
    release
    end
EcruteakCity_DanceTheater_PatronBefore::
    msgbox EcruteakCity_DanceTheater_Text_PatronBefore
    release
    end
EcruteakCity_DanceTheater_PatronAfter::
    msgbox EcruteakCity_DanceTheater_Text_PatronAfter
    release
    end
EcruteakCity_DanceTheater_BagFull::
    msgbox EcruteakCity_DanceTheater_Text_BagFull
    release
    end
''')
 texts[n].update({'PatronBefore':["Challenge all five KIMONO GIRLS.\nI have a lesson for your team."],
 'PatronAfter':["Your KANTO and JOHTO lessons\ncan help you travel farther."],
 'AlreadySurf':["You already learned the SURF\nlesson on your KANTO journey.",
  "Let me offer a different TM\ninstead of another HM."],
 'Alternate':["TM35 teaches FLAMETHROWER.\nA rare gift for a fine team."],
 'Surf':["HM03 teaches SURF.\nKeep this lesson for the road."],
 'BagFull':["Make room for your lesson.\nYour reward will be waiting."]})
 n='BurnedTower_1F'
 add(n,'Silver',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_SILVER_BURNED_TOWER_DEFEATED, BurnedTower_1F_SilverDone
    goto_if_unset FLAG_JOHTO_BADGE03_GET, BurnedTower_1F_SilverBefore
    trainerbattle_single TRAINER_JOHTO_SILVER_BURNED_TOWER, BurnedTower_1F_Text_Intro, BurnedTower_1F_Text_Defeat, BurnedTower_1F_SilverVictory, NO_MUSIC
    goto BurnedTower_1F_SilverVictory
BurnedTower_1F_SilverVictory::
    setflag FLAG_JOHTO_SILVER_BURNED_TOWER_DEFEATED
    msgbox BurnedTower_1F_Text_After
    removeobject 1
    release
    end
BurnedTower_1F_SilverBefore::
    msgbox BurnedTower_1F_Text_Before
    release
    end
BurnedTower_1F_SilverDone::
    release
    end
''')
 say(n,'Researcher',["We found ROCKET footprints.\nThey searched the lower floor.",
  "Their KANTO leader is gone.\nWho is ordering them now?"])
 texts[n].update({'Intro':["SILVER: Those ROCKETS want the\npower hidden below this tower.",
  "I will stop them myself.\nFirst, prove you can keep up!"],
 'Defeat':["You keep finding strength in\ntrust. I do not understand yet."],
 'After':["SILVER: The ROCKETS mentioned a\nbroadcast from GOLDENROD.",
  "I am going after them. You can\ncheck what is below this floor."],
 'Before':["SILVER: Collect WHITNEY's BADGE.\nFinish your journey here first."]})
 n='BurnedTower_B1F'
 add(n,'Investigate',r'''
    goto_if_set FLAG_JOHTO_BURNED_TOWER_INVESTIGATED, BurnedTower_B1F_InvestigationDone
    goto_if_unset FLAG_JOHTO_SILVER_BURNED_TOWER_DEFEATED, BurnedTower_B1F_InvestigationDone
    lockall
    msgbox BurnedTower_B1F_Text_Awakening
    setvar VAR_0x8004, SPECIES_RAIKOU
    special SetSeenMon
    showmonpic SPECIES_RAIKOU, 10, 3
    playmoncry SPECIES_RAIKOU, 0
    waitmoncry
    hidemonpic
    setvar VAR_0x8004, SPECIES_ENTEI
    special SetSeenMon
    showmonpic SPECIES_ENTEI, 10, 3
    playmoncry SPECIES_ENTEI, 0
    waitmoncry
    hidemonpic
    setvar VAR_0x8004, SPECIES_SUICUNE
    special SetSeenMon
    showmonpic SPECIES_SUICUNE, 10, 3
    playmoncry SPECIES_SUICUNE, 0
    waitmoncry
    hidemonpic
    msgbox BurnedTower_B1F_Text_Escaped
    setflag FLAG_JOHTO_BURNED_TOWER_INVESTIGATED
    setvar VAR_TEMP_0, 1
    releaseall
    end
BurnedTower_B1F_InvestigationDone::
    setvar VAR_TEMP_0, 1
    end
''')
 add(n,'Morty',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_BURNED_TOWER_INVESTIGATED, BurnedTower_B1F_MortyReady
    msgbox BurnedTower_B1F_Text_MortyBefore
    release
    end
BurnedTower_B1F_MortyReady::
    msgbox BurnedTower_B1F_Text_MortyReady
    release
    end
''')
 say(n,'Eusine',["SUICUNE looked at you before\nleaving. I will follow SUICUNE.",
  "Your records from KANTO helped\nus recognize these three lives."])
 texts[n].update({'Awakening':["Three POKEMON stir among the\ncharred stones below the tower."],
 'Escaped':["RAIKOU, ENTEI and SUICUNE rush\nout into the JOHTO countryside.",
  "MORTY: The old story was true.\nMeet me at the GYM."],
 'MortyBefore':["MORTY: Step toward the old\nstones. Something is moving."],
 'MortyReady':["MORTY: Meet me at the GYM.\nWe have much to learn from you."]})
 n='EcruteakCity_Gym'
 add(n,'Morty',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_BADGE04_GET, EcruteakCity_Gym_Reward
    goto_if_unset FLAG_JOHTO_BADGE03_GET, EcruteakCity_Gym_NotReady
    goto_if_unset FLAG_JOHTO_BURNED_TOWER_INVESTIGATED, EcruteakCity_Gym_NotReady
    trainerbattle_single TRAINER_JOHTO_MORTY, EcruteakCity_Gym_Text_Intro, EcruteakCity_Gym_Text_Defeat, EcruteakCity_Gym_MortyVictory, NO_MUSIC
    goto EcruteakCity_Gym_MortyVictory
EcruteakCity_Gym_MortyVictory::
    msgbox EcruteakCity_Gym_Text_Badge
    setflag FLAG_JOHTO_BADGE04_GET
EcruteakCity_Gym_Reward::
    goto_if_set FLAG_JOHTO_GOT_TM30_FROM_MORTY, EcruteakCity_Gym_After
    checkitemspace ITEM_TM30, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_Gym_BagFull
    giveitem ITEM_TM30, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_Gym_BagFull
    setflag FLAG_JOHTO_GOT_TM30_FROM_MORTY
    msgbox EcruteakCity_Gym_Text_TM
    release
    end
EcruteakCity_Gym_After::
    msgbox EcruteakCity_Gym_Text_After
    release
    end
EcruteakCity_Gym_NotReady::
    msgbox EcruteakCity_Gym_Text_NotReady
    release
    end
EcruteakCity_Gym_BagFull::
    msgbox EcruteakCity_Gym_Text_BagFull
    release
    end
''')
 texts[n]={'Intro':["MORTY: KANTO's CHAMPION has\nseen JOHTO's hidden history.",
  "Now show me how your trust\nholds up against GHOST POKEMON!"],
 'Defeat':["I see a bright future in you."],
 'Badge':["MORTY: You earned the FOGBADGE!\nYour fourth JOHTO GYM BADGE."],
 'TM':["TM30 teaches SHADOW BALL.\nCarry this lesson on the road."],
 'After':["The ROCKETS seek power they\ncannot earn through friendship.",
  "We will help you stop their\nplans when the trail is clearer."],
 'NotReady':["MORTY: Earn WHITNEY's BADGE and\ninvestigate the BURNED TOWER.",
  "That story will help you\nunderstand our GYM's challenge."],
 'BagFull':["Keep your FOGBADGE. Make room\nand return for the TM."]}
 for k in ['PING','GRACE']:
  add(n,k,'    trainerbattle_single TRAINER_JOHTO_'+k+', '+n+'_Text_'+k+'Intro, '+n+'_Text_'+k+'Defeat\n    msgbox '+n+'_Text_'+k+'After, MSGBOX_AUTOCLOSE\n    end')
  texts[n][k+'Intro']=["Can you follow the path of\na GHOST you cannot see?"]
  texts[n][k+'Defeat']=["You found your way through."]
  texts[n][k+'After']=["MORTY sees beyond appearances."]
 for n,k in [('JohtoRoute35','ARNIE'),('JohtoRoute36','IVAN')]:
  add(n,k,'    trainerbattle_single TRAINER_JOHTO_'+k+', '+n+'_Text_'+k+'Intro, '+n+'_Text_'+k+'Defeat\n    msgbox '+n+'_Text_'+k+'After, MSGBOX_AUTOCLOSE\n    end')
  texts.setdefault(n,{})[k+'Intro']=["JOHTO is full of surprises.\nLet me show you my POKEMON!"]
  texts[n][k+'Defeat']=["I learned something new today."]
  texts[n][k+'After']=["Every region has its own lesson."]
 return scripts,texts


def build(s):
 out={};stats={'chapter':'Goldenrod, National Park and Ecruteak','save_layout_changed':False,
 'native_build_and_emulator':'NOT_RUN_BY_GENERATOR',
 'visual_limits':['Existing Kanto tiles and native character portraits are reused.',
 'Burned Tower uses mansion interiors and a gym facade; the dance theater uses the native dojo.',
 'Sudowoodo uses its unmodified native menu-icon pixels. Morty and Kimono girls use placeholder portraits.'],
 'not_implemented':['Johto gyms five through eight, Radio Tower takeover and Johto League',
 'Bug-catching contest scheduling and rewards','Roaming legendary encounters after the tower scene']}
 groups=s.json('data/maps/map_groups.json');assert groups['gMapGroup_JohtoEntry'] in (OLD,OLD+NEW)
 for k,v in groups.items():
  if k not in ('group_order','gMapGroup_JohtoEntry'):assert not(set(v)&set(NEW))
 groups['gMapGroup_JohtoEntry']=OLD+NEW;out['data/maps/map_groups.json']=enc(groups)
 arrays=geometry(s);ls=s.json('data/layouts/layouts.json')
 tiles={
 'GoldenrodCity_NorthGate':('Building','GenericBuilding2','LAYOUT_ROUTE2_ENTRANCE'),
 'JohtoRoute35_NationalParkGate':('Building','GenericBuilding2','LAYOUT_ROUTE2_ENTRANCE'),
 'JohtoNationalPark_Route36Gate':('Building','GenericBuilding2','LAYOUT_ROUTE2_ENTRANCE'),
 'JohtoRoute35':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),
 'JohtoNationalPark':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),
 'JohtoRoute36':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),
 'JohtoRoute37':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),
 'EcruteakCity':('General','PewterCity','LAYOUT_PEWTER_CITY'),
 'BurnedTower_1F':('Building','PokemonMansion','LAYOUT_POKEMON_MANSION_1F'),
 'BurnedTower_B1F':('Building','PokemonMansion','LAYOUT_POKEMON_MANSION_B1F')}
 # Match city facade tiles to the same secondary tileset used in Goldenrod.
 tiles['EcruteakCity']=('General','SaffronCity','LAYOUT_SAFFRON_CITY')
 for n,a in arrays.items():
  primary,secondary,old=tiles[n];template=next(x for x in ls['layouts'] if x.get('id')==old)
  item={'id':'LAYOUT_'+ident(n),'name':n+'_Layout','width':len(a[0]),'height':len(a),
   'border_width':2,'border_height':2,'primary_tileset':'gTileset_'+primary,'secondary_tileset':'gTileset_'+secondary,
   'blockdata_filepath':'data/layouts/'+n+'/map.bin','border_filepath':'data/layouts/'+n+'/border.bin'}
  hits=[x for x in ls['layouts'] if x.get('id')==item['id']];assert not hits or hits==[item]
  if not hits:ls['layouts'].append(item)
  out[item['blockdata_filepath']]=C.pack(a);out[item['border_filepath']]=s.read(template['border_filepath'])
 out['data/layouts/layouts.json']=enc(ls);maps={}
 def temp(n,old,section,layout=None,music=None):
  j=s.json('data/maps/'+old+'/map.json')
  j.update(id=MID[n],name=n,region_map_section=section,connections=None)
  j.pop('connections_no_include',None)
  if layout:j['layout']=layout
  if music:j['music']=music
  for key in ['object_events','warp_events','coord_events','bg_events']:j[key]=[]
  maps[n]=j;return j
 n='GoldenrodCity_NorthGate';j=temp(n,'Route2_ViridianForest_NorthEntrance','MAPSEC_GOLDENROD_CITY','LAYOUT_GOLDENROD_CITY_NORTH_GATE')
 j['object_events']=[obj('POLICEMAN',9,3,n+'_Officer'),obj('WOMAN_2',4,6,n+'_Florist')]
 j['warp_events']=[warp(x,10,'MAP_GOLDENROD_CITY',4) for x in (6,7,8)]+[warp(7,1,'JohtoRoute35',0)]
 j['coord_events']=[{'type':'trigger','x':7,'y':2,'elevation':3,'var':'VAR_TEMP_0','var_value':'0','script':n+'_CheckPass'}]
 n='JohtoRoute35';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE35','LAYOUT_JOHTO_ROUTE35','MUS_ROUTE1')
 j['warp_events']=[warp(9,31,'GoldenrodCity_NorthGate',3,0),warp(9,3,'JohtoRoute35_NationalParkGate',1,0)]
 j['object_events']=[obj('BUG_CATCHER',13,17,n+'_ARNIE',movement='FACE_LEFT')]
 j['bg_events']=[C.bg(12,27,n+'_RouteSign')]
 n='JohtoRoute35_NationalParkGate';j=temp(n,'Route2_ViridianForest_NorthEntrance','MAPSEC_JOHTO_NATIONAL_PARK','LAYOUT_JOHTO_ROUTE35_NATIONAL_PARK_GATE')
 j['object_events']=[obj('POLICEMAN',9,3,n+'_Officer')]
 j['warp_events']=[warp(x,10,'JohtoRoute35',1) for x in (6,7,8)]+[warp(7,1,'JohtoNationalPark',0)]
 n='JohtoNationalPark';j=temp(n,'ViridianCity','MAPSEC_JOHTO_NATIONAL_PARK','LAYOUT_JOHTO_NATIONAL_PARK','MUS_PEWTER')
 j['warp_events']=[warp(15,32,'JohtoRoute35_NationalParkGate',3,0),warp(31,18,'JohtoNationalPark_Route36Gate',1,0)]
 j['object_events']=[obj('OLD_MAN_1',11,19,n+'_Caretaker')]
 j['bg_events']=[C.bg(20,22,n+'_ParkSign')]
 n='JohtoNationalPark_Route36Gate';j=temp(n,'Route2_ViridianForest_NorthEntrance','MAPSEC_JOHTO_NATIONAL_PARK','LAYOUT_JOHTO_NATIONAL_PARK_ROUTE36_GATE')
 j['object_events']=[obj('POLICEMAN',9,3,n+'_Officer')]
 j['warp_events']=[warp(x,10,'JohtoNationalPark',1) for x in (6,7,8)]+[warp(7,1,'JohtoRoute36',0)]
 n='JohtoRoute36';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE36','LAYOUT_JOHTO_ROUTE36','MUS_ROUTE1')
 j['connections']=[{'map':MID['JohtoRoute37'],'direction':'up','offset':16}]
 j['warp_events']=[warp(3,17,'JohtoNationalPark_Route36Gate',3,0)]
 j['object_events']=[obj('JOHTO_SUDOWOODO',25,8,n+'_Sudowoodo',flag='FLAG_JOHTO_SUDOWOODO_CLEARED'),
 obj('MAN',21,16,n+'_Worker'),obj('YOUNGSTER',19,18,n+'_IVAN',movement='FACE_UP')]
 n='JohtoRoute37';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE37','LAYOUT_JOHTO_ROUTE37','MUS_ROUTE1')
 j['connections']=[{'map':MID['JohtoRoute36'],'direction':'down','offset':-16},{'map':MID['EcruteakCity'],'direction':'up','offset':-10}]
 j['object_events']=[obj('COOLTRAINER_F',13,12,n+'_Traveler')]
 j['bg_events']=[C.bg(7,19,n+'_RouteSign')]
 n='EcruteakCity';j=temp(n,'SaffronCity','MAPSEC_ECRUTEAK_CITY','LAYOUT_ECRUTEAK_CITY','MUS_PEWTER')
 j['connections']=[{'map':MID['JohtoRoute37'],'direction':'down','offset':10}]
 j['warp_events']=[warp(8,28,'EcruteakCity_PokemonCenter_1F',1,0),warp(33,27,'EcruteakCity_Mart',1,0),
 warp(29,11,'EcruteakCity_Gym',1,0),warp(14,14,'EcruteakCity_DanceTheater',1,0),warp(7,6,'BurnedTower_1F',0,0)]
 j['object_events']=[obj('OLD_MAN_1',23,20,n+'_Resident'),obj('WOMAN_2',16,18,n+'_DanceFan')]
 j['bg_events']=[C.bg(x,y,n+'_'+k) for x,y,k in [(12,28,'CenterSign'),(36,27,'MartSign'),(34,11,'GymSign'),(17,14,'DanceSign'),(12,6,'TowerSign')]]
 scripts,rows=ecruteak_story();tx={n:C.texts(n,d) for n,d in rows.items()}
 for suffix in ['PokemonCenter_1F','PokemonCenter_2F','Mart']:
  old='GoldenrodCity_'+suffix;n='EcruteakCity_'+suffix
  rep=lambda text:text.replace('GOLDENROD_CITY','ECRUTEAK_CITY').replace('GOLDENROD','ECRUTEAK').replace('GoldenrodCity','EcruteakCity')
  j=json.loads(rep(s.text('data/maps/'+old+'/map.json')));assert j['id']==MID[n];maps[n]=j
  scripts[n]=rep(s.text('data/maps/'+old+'/scripts.inc'));tx[n]=rep(s.text('data/maps/'+old+'/text.inc'))
  if suffix=='PokemonCenter_1F':
   j['object_events'][0]['local_id']='LOCALID_ECRUTEAK_NURSE'
   for w in j['warp_events'][:3]:w['dest_warp_id']='0'
  elif suffix=='Mart':
   for w in j['warp_events']:w['dest_warp_id']='1'
 n='EcruteakCity_DanceTheater';j=temp(n,'SaffronCity_Dojo','MAPSEC_ECRUTEAK_CITY',music='MUS_CELADON')
 j['object_events']=[obj('WOMAN_1',x,8,n+'_'+k) for x,k in [(2,'NAOKO'),(4,'SAYO'),(6,'ZUKI'),(8,'KUNI'),(10,'MIKI')]]
 j['object_events'].append(obj('GENTLEMAN',9,11,n+'_Patron'))
 j['warp_events']=[warp(x,14,'EcruteakCity',3) for x in (5,6,7)]
 n='EcruteakCity_Gym';j=temp(n,'CeladonCity_Gym','MAPSEC_ECRUTEAK_CITY',music='MUS_GYM')
 j['object_events']=[obj('GENTLEMAN',6,4,n+'_Morty'),obj('WOMAN_2',3,11,n+'_PING',movement='FACE_RIGHT'),obj('WOMAN_1',9,10,n+'_GRACE',movement='FACE_LEFT')]
 j['warp_events']=[warp(x,18,'EcruteakCity',2) for x in (5,6,7)]
 n='BurnedTower_1F';j=temp(n,'PokemonMansion_1F','MAPSEC_BURNED_TOWER','LAYOUT_BURNED_TOWER_1F','MUS_POKE_TOWER')
 j['object_events']=[obj('BLUE',13,11,n+'_Silver',flag='FLAG_JOHTO_SILVER_BURNED_TOWER_DEFEATED'),obj('SCIENTIST',16,19,n+'_Researcher')]
 j['warp_events']=[warp(13,22,'EcruteakCity',4),warp(23,4,'BurnedTower_B1F',0)]
 n='BurnedTower_B1F';j=temp(n,'PokemonMansion_B1F','MAPSEC_BURNED_TOWER','LAYOUT_BURNED_TOWER_B1F','MUS_POKE_TOWER')
 j['object_events']=[obj('GENTLEMAN',13,9,n+'_Morty'),obj('COOLTRAINER_M',10,9,n+'_Eusine')]
 j['warp_events']=[warp(23,4,'BurnedTower_1F',1)]
 j['coord_events']=[{'type':'trigger','x':13,'y':10,'elevation':3,'var':'VAR_TEMP_0','var_value':'0','script':n+'_Investigate'}]
 for n,j in maps.items():
  out['data/maps/'+n+'/map.json']=enc(j);out['data/maps/'+n+'/scripts.inc']=scripts[n].encode()
  out['data/maps/'+n+'/text.inc']=tx.get(n,'@ Native shared dialogue.\n').encode()
 p='data/maps/GoldenrodCity/map.json';j=s.json(p);newwarp=warp(21,3,'GoldenrodCity_NorthGate',1,0)
 assert len(j['warp_events']) in (4,5)
 if len(j['warp_events'])==4:j['warp_events'].append(newwarp)
 else:assert j['warp_events'][4]==newwarp
 out[p]=enc(j)
 l=next(x for x in ls['layouts'] if x.get('id')==j['layout']);a=V.layout_array(s,j['layout'])
 facade=V.crop(V.layout_array(s,'LAYOUT_SAFFRON_CITY'),21,11,5,4)
 oldfacade=V.crop(V.layout_array(s,'LAYOUT_VIRIDIAN_CITY'),24,8,5,4)
 original=V.crop(I.geometry(s)['GoldenrodCity'],20,0,5,4);current=V.crop(a,20,0,5,4)
 assert current in (original,oldfacade,facade),'Goldenrod north entrance independently edited'
 C.paste(a,facade,20,0);out[l['blockdata_filepath']]=C.pack(a)
 heals=s.json('src/data/heal_locations.json')
 v={'id':'HEAL_LOCATION_ECRUTEAK_CITY','map':MID['EcruteakCity'],'x':8,'y':29,
 'respawn_map':MID['EcruteakCity_PokemonCenter_1F'],'respawn_npc':'LOCALID_ECRUTEAK_NURSE'}
 hits=[x for x in heals['heal_locations'] if x['id']==v['id']];assert not hits or hits==[v]
 if not hits:heals['heal_locations'].append(v)
 out['src/data/heal_locations.json']=enc(heals)
 shared(s,out);region(s,out);sudowoodo(s,out)
 stats['new_maps']=NEW;stats['new_flags']=FLAGS;stats['trainer_ids']={t[0]:t[-1] for t in TRAINERS}
 return out,stats

def shared(s,out):
 p='include/constants/flags_johto_story.h';t=s.text(p)
 block='\n// '+MARK+'\n'+''.join('#define '+n+' (JOHTO_STORY_FLAGS_START + '+str(v)+')\n' for n,v in FLAGS.items())
 if MARK not in t:
  used={int(v,0) for v in re.findall(r'JOHTO_STORY_FLAGS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',t)}
  assert not(used&set(FLAGS.values())) and not any(n in t for n in FLAGS)
  idx=t.rfind('#endif');assert idx>=0;t=t[:idx]+block+'\n'+t[idx:]
 else:assert block in t
 out[p]=t.encode()
 p='include/constants/opponents_johto_ecruteak.h'
 h='#ifndef GUARD_OPPONENTS_JOHTO_ECRUTEAK_H\n#define GUARD_OPPONENTS_JOHTO_ECRUTEAK_H\n'
 for n,c,pic,gender,party,num in TRAINERS:h+='#define TRAINER_JOHTO_'+n+' (HOENN_TRAINERS_START + '+str(num)+')\n'
 out[p]=(h+'#endif\n').encode()
 for path in (s.root/'include/constants').glob('opponents*.h'):
  rel=path.relative_to(s.root).as_posix()
  if rel==p:continue
  used={int(v,0) for v in re.findall(r'HOENN_TRAINERS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',s.text(rel))}
  assert not(used&{v[-1] for v in TRAINERS}),('trainer collision',rel)
 p='include/constants/opponents.h';anchor='#include "constants/opponents_johto_ilex.h"'
 out[p]=C.once(s.text(p),anchor,anchor+'\n#include "constants/opponents_johto_ecruteak.h"','Ecruteak trainer include').encode()
 parties='// '+MARK+'\n';trainers='// '+MARK+'\n'
 for n,c,pic,gender,party,num in TRAINERS:
  sym='sParty_Johto'+''.join(x.title() for x in n.split('_'));custom=len(party[0])==3
  assert all((len(mon)==3)==custom for mon in party)
  kind='CustomMoves' if custom else 'DefaultMoves'
  parties+='static const struct TrainerMonNoItem'+kind+' '+sym+'[] = {\n'
  for mon in party:
   sp,lv=mon[:2]
   moves=', .moves = {'+', '.join('MOVE_'+v for v in mon[2])+'}' if custom else ''
   parties+='    {.iv = 50, .lvl = '+str(lv)+', .species = SPECIES_'+sp+moves+'},\n'
  parties+='};\n\n'
  display='SILVER' if n=='SILVER_BURNED_TOWER' else (n[7:] if n.startswith('KIMONO_') else n)
  trainers+='    [TRAINER_JOHTO_'+n+'] = {\n        .trainerClass = TRAINER_CLASS_'+c+',\n        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_'+gender+(' | F_TRAINER_FEMALE' if gender=='FEMALE' else '')+',\n        .trainerPic = TRAINER_PIC_'+pic+',\n        .trainerName = _("'+display+'"),\n        .items = {},\n        .doubleBattle = FALSE,\n        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,\n        .party = '+('NO_ITEM_CUSTOM_MOVES' if custom else 'NO_ITEM_DEFAULT_MOVES')+'('+sym+'),\n    },\n'
 out['src/data/trainer_parties_johto_ecruteak.h']=parties.encode();out['src/data/trainers_johto_ecruteak.h']=trainers.encode()
 for p,a,inc in [('src/data/trainers.h','#include "trainers_johto_ilex.h"','#include "trainers_johto_ecruteak.h"'),('src/data/trainer_parties.h','#include "trainer_parties_johto_ilex.h"','#include "trainer_parties_johto_ecruteak.h"')]:
  out[p]=C.once(s.text(p),a,a+'\n'+inc,'Ecruteak trainer data').encode()
 p='data/event_scripts.s';t=s.text(p);block='@ '+MARK+'\n'+''.join('    .include "data/maps/'+n+'/'+f+'"\n' for n in NEW for f in ['scripts.inc','text.inc'])
 if MARK not in t:assert not any('data/maps/'+n+'/' in t for n in NEW);t=t.rstrip()+'\n\n'+block
 else:assert block in t
 out[p]=t.encode()
 p='tools/johto/build_ilex_goldenrod.py';t=s.text(p)
 guard=' # ECRUTEAK_EXTENSION_GUARD\n if any(n not in OLD + NEW for n in s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]):\n  raise RuntimeError("Ecruteak extension exists; use build_ecruteak.py")\n'
 if '# ECRUTEAK_EXTENSION_GUARD' not in t:
  t,n=re.subn(r'(?m)^def build\(s\):\n',lambda m:m.group(0)+guard,t);assert n==1
 else:assert guard in t
 out[p]=t.encode()
 p='src/data/wild_encounters.json';j=s.json(p)
 gs=[g for g in j['wild_encounter_groups'] if g['label']=='gWildMonHeaders'];assert len(gs)==1 and gs[0]['for_maps']
 for n,(day,night,levels) in WILD.items():
  row={'map':MID[n],'base_label':'s'+n}
  for key,sp in [('land_mons',day),('land_mons_morning',day),('land_mons_night',night)]:
   row[key]={'encounter_rate':10,'mons':[{'min_level':lv,'max_level':lv,'species':'SPECIES_'+name} for name,lv in zip(sp,levels)]}
  out['tools/johto/'+n.lower()+'_wild.json']=enc(row)
  hits=[x for x in gs[0]['encounters'] if x['map']==row['map'] or x['base_label']==row['base_label']]
  assert not hits or hits==[row]
  if not hits:gs[0]['encounters'].append(row)
 out[p]=enc(j)

def sudowoodo(s,out):
 p='include/constants/event_objects.h';t=s.text(p);marker='OBJ_EVENT_GFX_JOHTO_SUDOWOODO'
 if marker not in t:
  assert re.search(r'#define\s+NUM_OBJ_EVENT_GFX\s+236\b',t)
  t,n=re.subn(r'#define\s+NUM_OBJ_EVENT_GFX\s+236\b','#define '+marker+' 236\n#define NUM_OBJ_EVENT_GFX 237',t);assert n==1
 else:assert re.search(r'#define\s+'+marker+r'\s+236\b',t)
 out[p]=t.encode()
 p='src/event_object_movement.c';t=s.text(p)
 if '#include "graphics.h"' not in t:t=C.once(t,'#include "global.h"','#include "global.h"\n#include "graphics.h"','icon declaration')
 if '#include "pokemon_icon.h"' not in t:t=C.once(t,'#include "global.h"','#include "global.h"\n#include "pokemon_icon.h"','icon palette declaration')
 tag='#define OBJ_EVENT_PAL_TAG_JOHTO_SUDOWOODO 0x1144'
 if 'OBJ_EVENT_PAL_TAG_JOHTO_SUDOWOODO' not in t:
  assert not re.search(r'0x1144\b',t)
  a='#include "data/object_events/object_event_graphics.h"'
  t=C.once(t,a,tag+'\n\n'+a,'Sudowoodo palette tag')
  a='static const struct SpritePalette sObjectEventSpritePalettes[] = {'
  t=C.once(t,a,a+'\n    {gMonIconPalettes[1], OBJ_EVENT_PAL_TAG_JOHTO_SUDOWOODO},','Sudowoodo palette')
 else:assert tag in t and '{gMonIconPalettes[1], OBJ_EVENT_PAL_TAG_JOHTO_SUDOWOODO}' in t
 out[p]=t.encode()
 p='src/data/object_events/object_event_pic_tables.h';t=s.text(p)
 block='\nstatic const struct SpriteFrameImage sPicTable_JohtoSudowoodo[] = {\n    {gMonIcon_Sudowoodo, 512},\n};\n'
 if 'sPicTable_JohtoSudowoodo' not in t:t=t.rstrip()+'\n'+block
 else:assert block in t
 out[p]=t.encode()
 p='src/data/object_events/object_event_graphics_info.h';t=s.text(p)
 block=r'''
const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_JohtoSudowoodo = {
    .tileTag = TAG_NONE,
    .paletteTag = OBJ_EVENT_PAL_TAG_JOHTO_SUDOWOODO,
    .reflectionPaletteTag = OBJ_EVENT_PAL_TAG_NONE,
    .size = 512,
    .width = 32,
    .height = 32,
    .paletteSlot = PALSLOT_NPC_SPECIAL,
    .shadowSize = SHADOW_SIZE_S,
    .inanimate = TRUE,
    .disableReflectionPaletteLoad = TRUE,
    .tracks = TRACKS_NONE,
    .oam = &gObjectEventBaseOam_32x32,
    .subspriteTables = gObjectEventSpriteOamTables_32x32,
    .anims = sAnimTable_Inanimate,
    .images = sPicTable_JohtoSudowoodo,
    .affineAnims = gDummySpriteAffineAnimTable,
};
'''
 if 'gObjectEventGraphicsInfo_JohtoSudowoodo' not in t:t=t.rstrip()+'\n'+block
 else:assert block in t
 out[p]=t.encode()
 p='src/data/object_events/object_event_graphics_info_pointers.h';t=s.text(p)
 decl='const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_JohtoSudowoodo;\n'
 anchor='const struct ObjectEventGraphicsInfo *const gObjectEventGraphicsInfoPointers[NUM_OBJ_EVENT_GFX] = {'
 line='    [OBJ_EVENT_GFX_JOHTO_SUDOWOODO] = &gObjectEventGraphicsInfo_JohtoSudowoodo,'
 if 'OBJ_EVENT_GFX_JOHTO_SUDOWOODO' not in t:t=C.once(t,anchor,decl+'\n'+anchor+'\n'+line,'Sudowoodo gfx pointer')
 else:assert decl in t and line in t
 out[p]=t.encode()




def region(s,out):
 p='src/data/region_map/region_map_sections.json';j=s.json(p)
 oldids=['JOHTO_CHERRYGROVE_AIRSTRIP','JOHTO_ROUTE_29','NEW_BARK_TOWN','CHERRYGROVE_CITY','JOHTO_ROUTE30','JOHTO_ROUTE31','VIOLET_CITY','JOHTO_ROUTE32','JOHTO_UNION_CAVE','JOHTO_ROUTE33','AZALEA_TOWN','SLOWPOKE_WELL','ILEX_FOREST','JOHTO_ROUTE34','GOLDENROD_CITY']
 existing={x['id']:x for x in j['map_sections'] if x.get('id')}
 added='MAPSEC_ECRUTEAK_CITY' in existing
 assert all('MAPSEC_'+x in existing for x in oldids),'Johto section source differs'
 if not added:
  for key in oldids:existing['MAPSEC_'+key]['y']+=2
 specs=[('JOHTO_ROUTE35','ROUTE 35',2,4,1,1),('JOHTO_NATIONAL_PARK','NATIONAL PARK',2,3,1,1),
 ('JOHTO_ROUTE36','ROUTE 36',3,3,3,1),('JOHTO_ROUTE37','ROUTE 37',5,2,1,1),
 ('ECRUTEAK_CITY','ECRUTEAK CITY',5,1,1,1),('BURNED_TOWER','BURNED TOWER',4,1,1,1)]
 for key,label,x,y,w,h in specs:
  row={'id':'MAPSEC_'+key,'name':label,'x':x,'y':y,'width':w,'height':h}
  hits=[v for v in j['map_sections'] if v.get('id')==row['id']];assert not hits or hits==[row]
  if not hits:j['map_sections'].append(row)
 assert [v.get('id') for v in j['map_sections'][:len(s.json(p)['map_sections'])]]==[v.get('id') for v in s.json(p)['map_sections']]
 out[p]=enc(j)
 for p in ['src/region_map.c','src/pokemon_summary_screen.c']:
  t=s.text(p);pat=r'(MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP[\s\S]{0,120}?<=\s*)MAPSEC_GOLDENROD_CITY'
  if re.search(pat,t):t,n=re.subn(pat,lambda m:m.group(1)+'MAPSEC_BURNED_TOWER',t);assert n==1
  else:assert re.search(pat.replace('MAPSEC_GOLDENROD_CITY','MAPSEC_BURNED_TOWER'),t)
  out[p]=t.encode()
 p='src/region_map.c';t=out[p].decode()
 if '// ECRUTEAK_MAP_GRID_V1' not in t:
  pat=r'(?m)^([ \t]*)// ILEX_GOLDENROD_MAP_GRID_V1'
  lines=['// ECRUTEAK_MAP_GRID_V1','if (layer != LAYER_MAP)','    return MAPSEC_NONE;',
   'if (x == 5 && y == 1)','    return MAPSEC_ECRUTEAK_CITY;',
   'if (x == 4 && y == 1)','    return MAPSEC_BURNED_TOWER;',
   'if (x == 5 && y == 2)','    return MAPSEC_JOHTO_ROUTE37;',
   'if (x >= 3 && x <= 5 && y == 3)','    return MAPSEC_JOHTO_ROUTE36;',
   'if (x == 2 && y == 3)','    return MAPSEC_JOHTO_NATIONAL_PARK;',
   'if (x == 2 && y == 4)','    return MAPSEC_JOHTO_ROUTE35;',
   'if (y < 2)','    return MAPSEC_NONE;','y -= 2;','// ILEX_GOLDENROD_MAP_GRID_V1']
  t,n=re.subn(pat,lambda m:'\n'.join(m.group(1)+x for x in lines),t);assert n==1
 out[p]=t.encode()
 p='graphics/region_map/johto_entry.bin';v=list(struct.unpack('<600H',s.read(p)))
 # Clear only tiles that belonged to the old Johto route cells.
 before=s.json('src/data/region_map/region_map_sections.json')
 known={'MAPSEC_'+k for k in oldids}|{'MAPSEC_'+z[0] for z in specs}
 for row in before['map_sections']:
  if row.get('id') not in known:continue
  for y in range(row['y'],row['y']+row['height']):
   for x in range(row['x'],row['x']+row['width']):v[(y+4)*30+x+4]=5
 for row in j['map_sections']:
  if row.get('id') not in known:continue
  for y in range(row['y'],row['y']+row['height']):
   for x in range(row['x'],row['x']+row['width']):
    assert 0<=x+4<30 and 0<=y+4<16
    v[(y+4)*30+x+4]=0x1001 if row['width']==row['height']==1 else 0x100a
 out[p]=struct.pack('<600H',*v)
 extra=[('Route35','johtoRoute35','MAP_JOHTO_ROUTE35'),('NationalPark','johtoNationalPark','MAP_JOHTO_NATIONAL_PARK'),
 ('Route36','johtoRoute36','MAP_JOHTO_ROUTE36'),('Route37','johtoRoute37','MAP_JOHTO_ROUTE37'),
 ('BurnedTower','johtoBurnedTower','MAP_BURNED_TOWER_1F'),('BurnedTower','johtoBurnedTower','MAP_BURNED_TOWER_B1F')]
 unique=list(dict.fromkeys((a,b) for a,b,_ in extra))
 p='src/wild_pokemon_area.c';t=s.text(p)
 if 'bool8 johtoRoute35;' not in t:
  t,n=re.subn(r'(bool8\s+johtoRoute34\s*;)',lambda m:m.group(1)+''.join('\n    bool8 '+f+';' for _,f in unique),t);assert n==1
 if 'MAP_GROUP(MAP_JOHTO_ROUTE35)' not in t:
  pat=r'(?s)(if\s*\(header->mapGroup\s*==\s*MAP_GROUP\(MAP_JOHTO_ROUTE34\)\s*&&\s*header->mapNum\s*==\s*MAP_NUM\(MAP_JOHTO_ROUTE34\)\s*\)\s*\{\s*habitats->johtoRoute34\s*=\s*TRUE;\s*continue;\s*\})'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n            '+m.group(1).replace('MAP_JOHTO_ROUTE34',mn).replace('johtoRoute34',f) for _,f,mn in extra),t);assert n==1
 if 'habitats.johtoRoute35 || habitats.johtoNationalPark' not in t:
  t,n=re.subn(r'(if\s*\([^\n]*habitats\.johtoRoute29[^\n]*habitats\.johtoRoute34)\)',lambda m:m.group(1)+' || '+' || '.join('habitats.'+f for _,f in unique)+')',t);assert n==1
 if 'GetJohtoRoute35AreaMarkerSubsprite(areaCount++, subsprites);' not in t:
  pat=r'(if\s*\(habitats\.johtoRoute34\)\s*GetJohtoRoute34AreaMarkerSubsprite\(areaCount\+\+,\s*subsprites\);)'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n        if (habitats.'+f+')\n            GetJohto'+key+'AreaMarkerSubsprite(areaCount++, subsprites);' for key,f in unique),t);assert n==1
 out[p]=t.encode()
 p='include/pokedex_area_markers.h';t=s.text(p)
 if 'GetJohtoRoute35AreaMarkerSubsprite' not in t:
  t,n=re.subn(r'(void GetJohtoRoute34AreaMarkerSubsprite\([^;]*;)',lambda m:m.group(1)+''.join('\nvoid GetJohto'+key+'AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);' for key,_ in unique),t);assert n==1
 out[p]=t.encode()
 p='src/pokedex_area_markers.c';t=s.text(p)
 oldkeys=['Route29','Route30','Route31','Route32','UnionCave','Route33','SlowpokeWell','IlexForest','Route34']
 if not added:
  for key in oldkeys:
   name='GetJohto'+key+'AreaMarkerSubsprite'
   pat=r'(void\s+'+name+r'\([^)]*\)\s*\{[\s\S]*?subsprites\[i\]\.y\s*=\s*)(\d+)(;)'
   t,n=re.subn(pat,lambda m:m.group(1)+str(int(m.group(2))+12)+m.group(3),t);assert n==1
 for key,shape,x,y in [('Route35','Circular',19,25),('NationalPark','Circular',19,19),('Route36','SmallHorizontal',29,19),('Route37','Circular',34,13),('BurnedTower','Circular',29,7)]:
  name='GetJohto'+key+'AreaMarkerSubsprite'
  body='void '+name+'(s32 i, struct Subsprite *subsprites)\n{\n    if (subsprites == NULL)\n        return;\n    subsprites[i] = sSubsprite_'+shape+';\n    subsprites[i].x = '+str(x)+' + (HOENN_AREA_MAP_LEFT * 8 - 104);\n    subsprites[i].y = '+str(y)+';\n}'
  if re.search(r'void\s+'+name+r'\(',t):t=C.replace_function(t,name,body,'Ecruteak habitat marker')
  else:t=t.rstrip()+'\n\n'+body+'\n'
 out[p]=t.encode()
 p='src/pokedex_screen.c';t=s.text(p)
 labels=[('Ecr','ECR'),('R35','35'),('Park','PARK'),('R36','36'),('R37','37'),('Burn','BURN')]
 if 'sText_JohtoEcr[]' not in t:
  a='static const u8 sText_JohtoR34[] = _("34");\n';assert t.count(a)==1
  t=t.replace(a,a+''.join('static const u8 sText_Johto'+k+'[] = _("'+v+'");\n' for k,v in labels))
 body='static void DexScreen_DrawJohtoEntryArea(u8 windowId)\n{\n    FillWindowPixelBuffer(windowId, PIXEL_FILL(2));\n    FillWindowPixelRect(windowId, PIXEL_FILL(6), 3, 3, 122, 66);\n'
 for x,y,w,h in [(19,19,4,42),(19,17,19,4),(34,7,4,14),(29,7,7,4),(39,31,4,30),(59,31,4,30),(39,31,24,4),(19,59,44,4),(59,59,52,4),(29,55,4,6)]:
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(3), '+', '.join(map(str,[x,y,w,h]))+');\n'
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(5), '+', '.join(map(str,[x+1,y+1,max(1,w-2),max(1,h-2)]))+');\n'
 for x,y in [(19,31),(34,7),(29,7),(39,31),(59,55),(59,61),(107,61),(29,61),(39,61),(29,55)]:
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(2), '+', '.join(map(str,[x,y,6,6]))+');\n    FillWindowPixelRect(windowId, PIXEL_FILL(5), '+', '.join(map(str,[x+1,y+1,4,4]))+');\n'
 for key,x,y in [('Ecr',37,3),('Burn',4,3),('Park',4,11),('R35',4,22),('R36',23,21),('R37',39,14),('Gold',4,35),('Vio',42,35),('R31',50,26),('R34',4,48),('R32',45,48),('R30',68,48),('CG',68,54),('Ilex',4,61),('Aza',27,61),('Union',40,61),('R29',81,54),('AirShort',60,61),('NewBark',84,61),('Well',24,49)]:
  body+='    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_Johto'+key+', '+str(x)+', '+str(y)+', 0);\n'
 body+='}'
 out[p]=C.replace_function(t,'DexScreen_DrawJohtoEntryArea',body,'Ecruteak habitat diagram').encode()


def validate(s,out,stats):
 final=Source(s.root,dict(s.overlay,**out))
 ls={x['id']:x for x in final.json('data/layouts/layouts.json')['layouts'] if x.get('id')}
 maps={n:final.json('data/maps/'+n+'/map.json') for n in NEW}
 starts={'GoldenrodCity_NorthGate':(7,10),'JohtoRoute35':(9,32),'JohtoRoute35_NationalParkGate':(7,10),
 'JohtoNationalPark':(15,33),'JohtoNationalPark_Route36Gate':(7,10),'JohtoRoute36':(3,18),'JohtoRoute37':(9,23),
 'EcruteakCity':(19,35),'EcruteakCity_PokemonCenter_1F':(7,7),'EcruteakCity_Mart':(4,7),
 'EcruteakCity_DanceTheater':(6,14),'EcruteakCity_Gym':(6,18),'BurnedTower_1F':(13,21),'BurnedTower_B1F':(23,5)}
 # Validate native behaviors, not just passable approach squares.
 behavior_defs=final.text('include/constants/metatile_behaviors.h')
 warp_behaviors={int(v,0) for name,v in re.findall(r'^#define\s+(MB_\w+)\s+(0x[0-9A-Fa-f]+|\d+)\b',behavior_defs,re.M) if re.search(r'WARP|DOOR|LADDER|ESCALATOR',name)}
 native_primary=int(re.search(r'^#define\s+NUM_METATILES_IN_PRIMARY\s+(\d+)\b',final.text('include/fieldmap.h'),re.M).group(1))
 assert native_primary==640
 def behavior(l,tile):
  tile&=0x3ff
  kind='primary' if tile<native_primary else 'secondary'
  label=l[kind+'_tileset'].removeprefix('gTileset_')
  assert not label.startswith('Em'),('Emerald tiles need their own primary split',label)
  folder=re.sub(r'([A-Za-z])(\d)',r'\1_\2',re.sub(r'([a-z0-9])([A-Z])',r'\1_\2',label)).lower()
  attrs=final.read('data/tilesets/'+kind+'/'+folder+'/metatile_attributes.bin')
  i=tile if kind=='primary' else tile-native_primary
  assert (i+1)*4<=len(attrs),(label,tile,'attribute table bounds')
  return struct.unpack_from('<I',attrs,i*4)[0]&0x1ff
 behavior_maps=dict(maps);behavior_maps['GoldenrodCity']=final.json('data/maps/GoldenrodCity/map.json')
 checked_warps=0
 for n,m in behavior_maps.items():
  l=ls[m['layout']];w,h=l['width'],l['height'];raw=final.read(l['blockdata_filepath'])
  vals=struct.unpack('<'+'H'*(w*h),raw)
  for wp in m['warp_events']:
   x,y=wp['x'],wp['y'];assert 0<=x<w and 0<=y<h,(n,wp,'warp bounds')
   b=behavior(l,vals[y*w+x])
   # Native three-square exits have normal left/right flanks beside the active arrow.
   flank=(b==0 and any(v['dest_map']==wp['dest_map'] and v['dest_warp_id']==wp['dest_warp_id'] and v['y']==y and abs(v['x']-x)==1 and behavior(l,vals[y*w+v['x']]) in warp_behaviors for v in m['warp_events']))
   assert b in warp_behaviors or flank,(n,wp,hex(vals[y*w+x]),hex(b),'warp on non-warp tile')
   checked_warps+=1
 stats['native_warp_behaviors_checked']=checked_warps
 checks=[]
 outside={'JohtoRoute35','JohtoNationalPark','JohtoRoute36','JohtoRoute37','EcruteakCity'}
 for n,m in maps.items():
  l=ls[m['layout']];w,h=l['width'],l['height'];raw=final.read(l['blockdata_filepath'])
  assert len(raw)==w*h*2;assert (w+15)*(h+14)<=0x2800,(n,'field map buffer overflow')
  vals=struct.unpack('<'+'H'*(w*h),raw)
  def walk(x,y):return 0<=x<w and 0<=y<h and not((vals[y*w+x]>>10)&3) and (n not in outside or vals[y*w+x]>>12!=1)
  objects=m['object_events'];solid={(o['x'],o['y']) for o in objects}
  for o in objects:
   assert 0<=o['x']<w and 0<=o['y']<h
   if n!='EcruteakCity_PokemonCenter_2F':assert walk(o['x'],o['y']),(n,'NPC tile',o)
  for wp in m['warp_events']:
   dst=next((k for k in NEW if MID[k]==wp['dest_map']),None)
   if dst:
    i=int(wp['dest_warp_id']);other=maps[dst]['warp_events']
    assert 0<=i<len(other) and other[i]['dest_map']==m['id'],(n,'non-reciprocal warp',wp)
  if m['connections']:
   assert not m.get('connections_no_include',False),'native connection pointer suppressed'
   opposite={'up':'down','down':'up','left':'right','right':'left'}
   for cn in m['connections']:
    dst=next((k for k in NEW if MID[k]==cn['map']),None);assert dst
    rev=[v for v in maps[dst]['connections'] if v['map']==m['id'] and v['direction']==opposite[cn['direction']]]
    assert len(rev)==1 and rev[0]['offset']==-cn['offset'],(n,'non-reciprocal connection')
  if n not in starts:checks.append({'map':n,'native_CableClub_layout':True});continue
  start=starts[n];assert walk(*start),(n,'spawn',start)
  def bfs(obstacles):
   seen={start};q=deque([start])
   while q:
    x,y=q.popleft()
    for z in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
     if z not in seen and z not in obstacles and walk(*z):seen.add(z);q.append(z)
   return seen
  closed=bfs(solid)
  if n=='JohtoRoute36':
   assert (25,0) not in closed,'Sudowoodo can be bypassed';solid.remove((25,8))
  if n=='BurnedTower_1F':
   assert (23,4) not in closed,'Silver can be bypassed';solid.remove((13,11))
  if n=='GoldenrodCity_NorthGate':assert (7,1) not in bfs(solid|{(7,2)}),'Badge3 checkpoint can be bypassed'
  seen=bfs(solid)
  for wp in m['warp_events']:
   z=(wp['x'],wp['y']+1) if n in outside else (wp['x'],wp['y'])
   assert z in seen,(n,'unreachable warp',wp,z)
  for o in objects:
   x,y=o['x'],o['y'];gfx=o['graphics_id']
   if gfx=='OBJ_EVENT_GFX_NURSE':assert (x,y+2) in seen;continue
   if gfx=='OBJ_EVENT_GFX_CLERK':continue
   assert any(z in seen for z in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),(n,'NPC cannot be faced',o)
  if n=='JohtoRoute36':assert all((x,0) in seen for x in range(24,28))
  if n=='JohtoRoute37':assert all((x,y) in seen for x in range(8,12) for y in (0,23))
  if n=='EcruteakCity':assert all((x,35) in seen for x in range(18,22))
  if n=='BurnedTower_1F':assert vals[22*w+13]==0x32e9 and vals[4*w+23]==0x32d2
  if n=='BurnedTower_B1F':assert vals[4*w+23]==0x3363 and (13,10) in seen
  checks.append({'map':n,'walkable_reachable':len(seen),'NPC_and_warps':True,'buffer_metatiles':(w+15)*(h+14)})
 before=s.json('data/maps/map_groups.json');after=final.json('data/maps/map_groups.json')
 assert after['gMapGroup_JohtoEntry'][:len(OLD)]==OLD
 assert all(after[k]==v for k,v in before.items() if k!='gMapGroup_JohtoEntry')
 oldlayout=s.json('data/layouts/layouts.json')['layouts'];assert final.json('data/layouts/layouts.json')['layouts'][:len(oldlayout)]==oldlayout
 goldbefore=s.json('data/maps/GoldenrodCity/map.json');goldafter=final.json('data/maps/GoldenrodCity/map.json')
 assert goldbefore['warp_events'][:4]==goldafter['warp_events'][:4] and goldbefore['connections']==goldafter['connections']
 assert not any(p in out for p in ['include/global.h','include/pokemon.h','src/save.c','src/load_save.c'])
 cmds=set(re.findall(r'(?m)^\s*\.macro\s+(\w+)',s.text('asm/macros/event.inc')+'\n'+s.text('asm/macros/map.inc')))
 cmds.update(re.findall(r'(?m)^\s*create_movement_action\s+(\w+)',s.text('asm/macros/movement.inc')))
 for p,b in out.items():
  if p.endswith('scripts.inc'):
   text=b.decode()
   assert not re.search(r'checktrainerflag[^\n]*\n\s*goto_if_eq\s+VAR_RESULT',text),'stale trainer flag comparison'
   for line in text.splitlines():
    v=line.strip()
    if v and not v.startswith(('@','.','#')) and not v.endswith(':'):assert v.split()[0] in cmds,(p,'unknown macro',v)
 headers='\n'.join(final.text('include/constants/'+name) for name in ['species.h','items.h','moves.h','songs.h','event_objects.h','event_object_movement.h','global.h','trainers.h'])+'\n'+s.text('include/battle.h')
 headers+='\n'+'\n'.join(re.findall(r'enum\s*(?:\w+)?\s*\{[^}]*\}',out['src/event_object_movement.c'].decode()))
 refs=set()
 for p,b in out.items():
  if p.endswith(('.h','.c','.json','scripts.inc')):
   try:refs.update(re.findall(r'\b(?:SPECIES|ITEM|MOVE|MUS|OBJ_EVENT_GFX|TRAINER_CLASS|TRAINER_PIC|TRAINER_ENCOUNTER_MUSIC)_[A-Z0-9_]+',b.decode()))
   except UnicodeDecodeError:pass
 missing=[v for v in refs if not re.search(r'\b'+re.escape(v)+r'\b',headers)]
 assert not missing,('unknown native constant',missing)
 for n in WILD:
  row=json.loads(out['tools/johto/'+n.lower()+'_wild.json'])
  for k in ['land_mons','land_mons_morning','land_mons_night']:assert len(row[k]['mons'])==12
 for n in ['EcruteakCity_DanceTheater','EcruteakCity_Gym']:
  script=out['data/maps/'+n+'/scripts.inc'].decode();assert 'giveitem' in script and 'goto_if_eq VAR_RESULT, FALSE,' in script
 stats['static_checks']=checks;return stats
def apply(root,mutate=False):
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 s=Source(root);out,stats=build(s);validate(s,out,stats)
 repeat,_=build(Source(root,dict(s.overlay,**out)));assert repeat==out,'not idempotent'
 owned=[p for p in out if any(p.startswith('data/maps/'+n+'/') or p.startswith('data/layouts/'+n+'/') for n in NEW)]
 owned+=['include/constants/opponents_johto_ecruteak.h','src/data/trainers_johto_ecruteak.h','src/data/trainer_parties_johto_ecruteak.h']
 owned+=['tools/johto/'+n.lower()+'_wild.json' for n in WILD]
 # Narrow migration from this generator's exact prior Viridian facade.
 prior=geometry(s)['EcruteakCity']
 C.paste(prior,V.crop(V.layout_array(s,'LAYOUT_VIRIDIAN_CITY'),24,8,5,4),13,11)
 prior[14][17]=0x0403
 migrations={'data/layouts/EcruteakCity/map.bin':C.pack(prior)}
 for p in owned:
  if s.exists(p):assert s.read(p)==out[p] or (p in migrations and s.read(p)==migrations[p]),'owned artifact changed: '+p
 changed={p:b for p,b in out.items() if not s.exists(p) or s.read(p)!=b}
 print(json.dumps({'apply':mutate,'files':sorted(changed),'validation':stats},indent=2))
 if not mutate or not changed:return
 for p,b in s.used.items():assert (root/p).read_bytes()==b,'concurrent edit: '+p
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=root/'outputs/johto-ecruteak-v1'/stamp;dest.mkdir(parents=True,exist_ok=False)
 manifest={'time':stamp,'validation':stats,'files':{}}
 for p,b in changed.items():
  path=root/p;old=path.read_bytes() if path.exists() else None
  manifest['files'][p]={'before':sha(old) if old is not None else None,'after':sha(b)}
  if old is not None:
   bak=dest/'before'/p;bak.parent.mkdir(parents=True,exist_ok=True);bak.write_bytes(old)
 (dest/'manifest.json').write_bytes(enc(manifest))
 for p,b in changed.items():
  target=root/p;target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.ecruteak.tmp')
  assert not tmp.exists();tmp.write_bytes(b);tmp.replace(target)
 print('APPLIED',dest/'manifest.json')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root).resolve(),a.apply)
