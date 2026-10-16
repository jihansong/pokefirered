#!/usr/bin/env python3
"""Append the Ilex/Goldenrod entrance chapter; dry run unless --apply."""
import argparse,copy,datetime,json,re,struct,subprocess,sys
from collections import deque
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_cherrygrove as C
import build_violet as V
import build_azalea as A
Source,enc,sha=C.Source,C.enc,C.sha
OLD=A.OLD+A.NEW
NEW=['IlexForest_AzaleaGate','IlexForest','IlexForest_Route34Gate','JohtoRoute34','JohtoRoute34_DayCare','GoldenrodCity','GoldenrodCity_PokemonCenter_1F','GoldenrodCity_PokemonCenter_2F','GoldenrodCity_Mart','GoldenrodCity_RadioTower_1F','GoldenrodCity_Gym']
IDS=['ILEX_FOREST_AZALEA_GATE','ILEX_FOREST','ILEX_FOREST_ROUTE34_GATE','JOHTO_ROUTE34','JOHTO_ROUTE34_DAY_CARE','GOLDENROD_CITY','GOLDENROD_CITY_POKEMON_CENTER_1F','GOLDENROD_CITY_POKEMON_CENTER_2F','GOLDENROD_CITY_MART','GOLDENROD_CITY_RADIO_TOWER_1F','GOLDENROD_CITY_GYM']
MID=dict(zip(NEW,['MAP_'+v for v in IDS]))
MARK='JOHTO_ILEX_GOLDENROD_CHAPTER_V1'
FLAGS={'FLAG_JOHTO_SILVER_AZALEA_DEFEATED':12,'FLAG_JOHTO_ILEX_FARFETCHD_RETURNED':14,'FLAG_JOHTO_ILEX_CUT_BRIEFED':15,'FLAG_JOHTO_BADGE03_GET':18,'FLAG_JOHTO_ILEX_HELP_REQUESTED':24,'FLAG_JOHTO_GOLDENROD_RESEARCH_REGISTERED':26,'FLAG_JOHTO_WHITNEY_ENCOURAGED':27,'FLAG_JOHTO_GOT_TM45_FROM_WHITNEY':28}
TRAINERS=[
 ('SILVER_AZALEA','RIVAL_LATE','RIVAL_LATE','MALE',[('GASTLY',16,['LICK','SPITE','MEAN_LOOK','CURSE']),('ZUBAT',18,['LEECH_LIFE','SUPERSONIC','BITE','CONFUSE_RAY']),('CROCONAW',20,['WATER_GUN','BITE','RAGE','LEER'])],799),
 ('TODD','CAMPER','CAMPER','MALE',[('PSYDUCK',16)],800),
 ('GINA','PICNICKER','PICNICKER','FEMALE',[('HOPPIP',16),('BULBASAUR',17)],801),
 ('BRANDON','POKEMANIAC','POKEMANIAC','MALE',[('SNUBBULL',18)],802),
 ('VICTORIA','BEAUTY','BEAUTY','FEMALE',[('SENTRET',18),('FURRET',19)],803),
 ('SAMANTHA','LASS','LASS','FEMALE',[('MEOWTH',19),('JIGGLYPUFF',19)],804),
 ('WHITNEY','LEADER','LASS','FEMALE',[('CLEFAIRY',18,['DOUBLE_SLAP','ENCORE','MIMIC','METRONOME']),('MILTANK',20,['STOMP','ROLLOUT','ATTRACT','MILK_DRINK'])],805)]
WILD={
 'IlexForest':(['CATERPIE','METAPOD','WEEDLE','KAKUNA','PARAS','CATERPIE','PARAS','METAPOD','ODDISH','PARAS','ODDISH','BUTTERFREE'],
 ['HOOTHOOT','ODDISH','PARAS','VENONAT','HOOTHOOT','ODDISH','PARAS','VENONAT','ZUBAT','PARAS','ZUBAT','NOCTOWL'],[5,5,5,5,6,6,6,6,6,7,7,7]),
 'JohtoRoute34':(['DROWZEE','RATTATA','DROWZEE','PIDGEY','DROWZEE','ABRA','DITTO','RATTATA','PIDGEY','ABRA','DITTO','DITTO'],
 ['DROWZEE','RATTATA','DROWZEE','HOOTHOOT','DROWZEE','ABRA','DITTO','RATTATA','HOOTHOOT','ABRA','DITTO','DITTO'],[10,10,11,11,11,12,10,12,12,12,11,12])}
def ident(n):return IDS[NEW.index(n)]
def warp(x,y,dst,index,elevation=3):
 return {'x':x,'y':y,'elevation':elevation,'dest_map':MID.get(dst,dst),'dest_warp_id':str(index)}
def obj(gfx,x,y,script,**kw):
 flag=kw.pop('flag','0');v=C.obj(gfx,x,y,script,**kw);v['flag']=flag;return v
def geometry(s):
 forest=V.layout_array(s,'LAYOUT_VIRIDIAN_FOREST')
 vir=V.layout_array(s,'LAYOUT_VIRIDIAN_CITY');pew=V.layout_array(s,'LAYOUT_PEWTER_CITY')
 saff=V.layout_array(s,'LAYOUT_SAFFRON_CITY')
 a=[[0x3001]*40 for _ in range(48)]
 for box in [(0,0,40,4),(0,0,3,48),(37,0,40,48),(0,45,40,48),(11,3,26,13),(12,13,24,22),(3,28,14,36),(20,25,31,32),(29,14,37,24),(4,37,17,45)]:C.fill(a,*box,C.dense)
 # The two native forest gates retain their original warp metatile behavior.
 C.paste(a,V.crop(forest,0,2,11,11),1,0)
 C.paste(a,V.crop(forest,23,58,13,11),22,37)
 C.fill(a,5,11,10,27,0x3001)
 C.fill(a,7,24,20,28,0x3001);C.fill(a,16,26,20,38,0x3001)
 C.fill(a,18,34,31,38,0x3001);C.fill(a,26,34,31,42,0x3001)
 # A single clear tile between tree clusters is blocked by the native CUT tree.
 C.fill(a,3,17,7,19,C.dense);C.fill(a,8,17,12,19,C.dense)
 C.fill(a,21,5,26,9,C.grass);C.fill(a,30,25,36,32,C.grass)
 C.fill(a,4,23,8,27,C.grass);C.fill(a,20,38,26,44,C.grass)
 # Small east grove for the lost FARFETCH'D; every exit stays reachable after CUT.
 C.fill(a,24,9,29,14,0x3001);C.fill(a,26,12,36,16,0x3001);C.fill(a,33,14,37,27,0x3001)
 a[31][31]=0x0403
 b=[[0x3001]*24 for _ in range(48)]
 for box in [(0,0,3,48),(21,0,24,48),(0,46,24,48)]:C.fill(b,*box,C.dense)
 C.fill(b,8,0,12,46,0x3195);C.fill(b,3,7,8,18,C.grass);C.fill(b,14,21,20,35,C.grass)
 C.paste(b,V.crop(vir,24,8,5,4),14,9)
 # Native gate facade opens south into the forest checkpoint.
 C.paste(b,V.crop(vir,24,8,5,4),8,38)
 b[12][20]=0x0403;b[29][13]=0x0403
 city=[[0x3001]*48 for _ in range(40)]
 for box in [(0,0,48,3),(0,0,3,40),(45,0,48,40),(0,37,48,40)]:C.fill(city,*box,C.dense)
 C.fill(city,20,2,24,40,0x3195);C.fill(city,3,15,45,20,0x3195);C.fill(city,7,28,42,33,0x3195)
 C.fill(city,7,18,12,32,0x3195);C.fill(city,37,18,42,32,0x3195)
 C.paste(city,V.crop(saff,22,34,5,5),6,24)
 C.paste(city,V.crop(vir,34,16,4,4),37,25)
 C.paste(city,V.crop(pew,12,12,7,5),30,6)
 # Radio research reception uses the native large city building facade.
 C.paste(city,V.crop(saff,29,16,9,15),7,3)
 for x,y in [(12,28),(42,28),(38,10),(17,18)]:city[y][x]=0x0403
 for box in [(25,23,34,27),(26,30,34,34),(7,19,16,22)]:C.fill(city,*box,0x3004)
 gate=V.layout_array(s,'LAYOUT_ROUTE2_ENTRANCE')
 radio=copy.deepcopy(gate)
 for x in (6,7,8):radio[0][x]=0x687;radio[1][x]=0x6ea
 return {'IlexForest':a,'JohtoRoute34':b,'GoldenrodCity':city,'IlexForest_AzaleaGate':gate,'GoldenrodCity_RadioTower_1F':radio}


def ilex_story():
 scripts={};texts={}
 def add(n,k,body):
  scripts.setdefault(n,n+'_MapScripts::\n    .byte 0\n')
  scripts[n]+='\n'+n+'_'+k+'::\n'+body.strip()+'\n'
 def say(n,k,paras):
  add(n,k,'    msgbox '+n+'_Text_'+k+', MSGBOX_NPC\n    end')
  texts.setdefault(n,{})[k]=paras
 n='IlexForest_AzaleaGate'
 add(n,'Silver',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_SILVER_AZALEA_DEFEATED, IlexForest_AzaleaGate_SilverDone
    goto_if_unset FLAG_JOHTO_BADGE02_GET, IlexForest_AzaleaGate_SilverNotReady
    trainerbattle_single TRAINER_JOHTO_SILVER_AZALEA, IlexForest_AzaleaGate_Text_SilverIntro, IlexForest_AzaleaGate_Text_SilverDefeat, IlexForest_AzaleaGate_SilverVictory, NO_MUSIC
    goto IlexForest_AzaleaGate_SilverVictory
IlexForest_AzaleaGate_SilverVictory::
    msgbox IlexForest_AzaleaGate_Text_SilverAfter
    setflag FLAG_JOHTO_SILVER_AZALEA_DEFEATED
    removeobject 1
    release
    end
IlexForest_AzaleaGate_SilverNotReady::
    msgbox IlexForest_AzaleaGate_Text_SilverNotReady
    release
    end
IlexForest_AzaleaGate_SilverDone::
    release
    end
''')
 texts[n]={'SilverIntro':["SILVER: The KANTO CHAMPION?\nI heard you stopped TEAM ROCKET.",
   "And now you spend your time\nhelping strangers and SLOWPOKE?",
   "Show me the strength that made\nyou a CHAMPION!"],
 'SilverDefeat':["You fought for your POKEMON,\nnot just for yourself..."],
 'SilverAfter':["SILVER: Those ROCKETS scattered\nafter their defeat in KANTO.",
   "Someone is still giving them\norders. I am going to GOLDENROD.",
   "I will find their leader.\nStay out of my way!"],
 'SilverNotReady':["SILVER: Finish what you started\nin AZALEA. Then face me here."]}
 add(n,'CheckPass',r'''
    goto_if_set FLAG_JOHTO_SILVER_AZALEA_DEFEATED, IlexForest_AzaleaGate_Pass
    lockall
    msgbox IlexForest_AzaleaGate_Text_Stop
    applymovement LOCALID_PLAYER, IlexForest_AzaleaGate_StepBack
    waitmovement 0
    releaseall
    end
IlexForest_AzaleaGate_Pass::
    setvar VAR_TEMP_0, 1
    end
IlexForest_AzaleaGate_StepBack:
    walk_down
    step_end
''')
 texts[n]['Stop']=["SILVER is waiting for a battle.\nSpeak to him before going on."]
 say(n,'Officer',["ILEX FOREST is beyond this gate.\nThe north path reaches ROUTE 34.",
    "The forest workers use CUT to\nclear fallen branches."])
 n='IlexForest'
 scripts[n]=n+'_MapScripts::\n    map_script MAP_SCRIPT_ON_TRANSITION, IlexForest_OnTransition\n    .byte 0\n'
 add(n,'OnTransition',r'''
    goto_if_unset FLAG_JOHTO_ILEX_FARFETCHD_RETURNED, IlexForest_KeepWildPosition
    setobjectxyperm 2, 26, 35
    end
IlexForest_KeepWildPosition::
    end
''')
 add(n,'Apprentice',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_ILEX_FARFETCHD_RETURNED, IlexForest_ApprenticeThanks
    goto_if_set FLAG_JOHTO_ILEX_HELP_REQUESTED, IlexForest_ApprenticeWait
    msgbox IlexForest_Text_ApprenticeRequest
    setflag FLAG_JOHTO_ILEX_HELP_REQUESTED
    release
    end
IlexForest_ApprenticeWait::
    msgbox IlexForest_Text_ApprenticeWait
    release
    end
IlexForest_ApprenticeThanks::
    msgbox IlexForest_Text_ApprenticeThanks
    release
    end
''')
 add(n,'Farfetchd',r'''
    lock
    faceplayer
    playmoncry SPECIES_FARFETCHD, 0
    waitmoncry
    goto_if_set FLAG_JOHTO_ILEX_FARFETCHD_RETURNED, IlexForest_FarfetchdHome
    goto_if_unset FLAG_JOHTO_ILEX_HELP_REQUESTED, IlexForest_FarfetchdShy
    showmonpic SPECIES_FARFETCHD, 10, 3
    msgbox IlexForest_Text_FarfetchdReturn
    hidemonpic
    applymovement 2, IlexForest_FarfetchdHop
    waitmovement 0
    fadescreen FADE_TO_BLACK
    setflag FLAG_JOHTO_ILEX_FARFETCHD_RETURNED
    setobjectxy 2, 26, 35
    setobjectxyperm 2, 26, 35
    fadescreen FADE_FROM_BLACK
    msgbox IlexForest_Text_FarfetchdBack
    release
    end
IlexForest_FarfetchdHome::
    msgbox IlexForest_Text_FarfetchdHome
    release
    end
IlexForest_FarfetchdShy::
    msgbox IlexForest_Text_FarfetchdShy
    release
    end
IlexForest_FarfetchdHop:
    jump_in_place_down
    step_end
''')
 add(n,'Master',r'''
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_ILEX_FARFETCHD_RETURNED, IlexForest_MasterBefore
    goto_if_set FLAG_JOHTO_ILEX_CUT_BRIEFED, IlexForest_MasterAfter
    goto_if_set FLAG_GOT_HM01, IlexForest_MasterAlreadyHasCut
    checkitem ITEM_HM01, 1
    goto_if_eq VAR_RESULT, TRUE, IlexForest_MasterAlreadyHasCut
    checkpcitem ITEM_HM01, 1
    goto_if_eq VAR_RESULT, TRUE, IlexForest_MasterAlreadyHasCut
    checkitemspace ITEM_HM01, 1
    goto_if_eq VAR_RESULT, FALSE, IlexForest_MasterBagFull
    giveitem ITEM_HM01, 1
    goto_if_eq VAR_RESULT, FALSE, IlexForest_MasterBagFull
    setflag FLAG_JOHTO_ILEX_CUT_BRIEFED
    msgbox IlexForest_Text_MasterCut
    release
    end
IlexForest_MasterAlreadyHasCut::
    checkitemspace ITEM_TM48, 1
    goto_if_eq VAR_RESULT, FALSE, IlexForest_MasterBagFull
    msgbox IlexForest_Text_MasterAlreadyHasCut
    giveitem ITEM_TM48, 1
    goto_if_eq VAR_RESULT, FALSE, IlexForest_MasterBagFull
    setflag FLAG_JOHTO_ILEX_CUT_BRIEFED
    msgbox IlexForest_Text_MasterAlternate
    release
    end
IlexForest_MasterAfter::
    msgbox IlexForest_Text_MasterAfter
    release
    end
IlexForest_MasterBefore::
    msgbox IlexForest_Text_MasterBefore
    release
    end
IlexForest_MasterBagFull::
    msgbox IlexForest_Text_MasterBagFull
    release
    end
''')
 texts[n]={'ApprenticeRequest':["Some people rushed past us.\nThey frightened our FARFETCH'D!",
   "It ran into the eastern grove.\nPlease help me bring it back."],
 'ApprenticeWait':["FARFETCH'D knows my whistle.\nCall gently if you find it."],
 'ApprenticeThanks':["You brought it back!\nMy master wants to thank you."],
 'FarfetchdReturn':["FARFETCH'D recognizes the call!\nIt heads back to the apprentice."],
 'FarfetchdHome':["FARFETCH'D stays close to its\nowner. It looks happy again."],
 'FarfetchdBack':["FARFETCH'D has safely returned."],
 'FarfetchdShy':["FARFETCH'D seems frightened.\nIts owner may be nearby."],
 'MasterBefore':["My apprentice is worried about\nour missing FARFETCH'D."],
 'MasterAlreadyHasCut':["You already received CUT!\nHere is a different lesson."],
 'MasterAlternate':["TM48 teaches SKILL SWAP.\nIt exchanges both ABILITIES."],
 'MasterCut':["HM01 teaches CUT.\nUse it to clear small trees."],
 'MasterAfter':["The north path reaches ROUTE 34.\nTake care of your POKEMON."],
 'MasterBagFull':["Please make room for the reward.\nI will keep it safe for you."]}
 say(n,'ForestSign',["ILEX FOREST\nRespect the forest and its life."])
 n='IlexForest_Route34Gate'
 say(n,'Officer',["ROUTE 34 leads to GOLDENROD.\nThe RADIO TOWER is easy to find."])
 say(n,'Traveler',["Some POKEMON in this forest\nappear only at night.",
    "ELM studies how those patterns\nchange across JOHTO."])
 n='JohtoRoute34'
 for key in ['Todd','Gina','Brandon']:
  add(n,key,'    trainerbattle_single TRAINER_JOHTO_'+key.upper()+', '+n+'_Text_'+key+'Intro, '+n+'_Text_'+key+'Defeat\n    msgbox '+n+'_Text_'+key+'After, MSGBOX_AUTOCLOSE\n    end')
 texts[n]={'ToddIntro':["A new route means new rivals!"],'ToddDefeat':["You have traveled a long way!"],'ToddAfter':["GOLDENROD is just to the north."],
 'GinaIntro':["My POKEMON love this grass!"],'GinaDefeat':["Your team works together!"],'GinaAfter':["The forest has different kinds\nof POKEMON from this route."],
 'BrandonIntro':["Training needs some patience."],'BrandonDefeat':["And a good plan, too!"],'BrandonAfter':["The DAY CARE can help raise\na POKEMON while you travel."]}
 say(n,'RouteSign',["ROUTE 34\nNorth: GOLDENROD CITY"])
 say(n,'DayCareSign',["POKEMON DAY CARE\nPartner branch of KANTO ROUTE 5"])
 n='JohtoRoute34_DayCare'
 say(n,'Reception',["Our branches share one nursery.\nPOKEMON left on KANTO ROUTE 5\ncan be collected here, too.",
   "We raise one POKEMON at a time.\nSpeak to the keeper at the desk."])
 n='GoldenrodCity'
 say(n,'Resident',["This city connects JOHTO's\ntravelers, shops, and radio.",
    "The RADIO TOWER is taking\nreports about unusual signals."])
 say(n,'GymFan',["WHITNEY's POKEMON look cute.\nTheir strength may surprise you!"])
 for k,p in [('CenterSign',["POKEMON CENTER"]),('MartSign',["POKEMON MART"]),
             ('GymSign',["GOLDENROD POKEMON GYM\nLEADER: WHITNEY"]),
             ('RadioSign',["GOLDENROD RADIO TOWER\nVisitor and research reception"])]:say(n,k,p)
 n='GoldenrodCity_RadioTower_1F'
 add(n,'ResearchDesk',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_GOLDENROD_RESEARCH_REGISTERED, GoldenrodCity_RadioTower_1F_Registered
    goto_if_unset FLAG_JOHTO_ELM_REPORT_DELIVERED, GoldenrodCity_RadioTower_1F_BeforeElm
    msgbox GoldenrodCity_RadioTower_1F_Text_Register
    setflag FLAG_JOHTO_GOLDENROD_RESEARCH_REGISTERED
    release
    end
GoldenrodCity_RadioTower_1F_Registered::
    msgbox GoldenrodCity_RadioTower_1F_Text_Registered
    release
    end
GoldenrodCity_RadioTower_1F_BeforeElm::
    msgbox GoldenrodCity_RadioTower_1F_Text_BeforeElm
    release
    end
''')
 texts[n]={'Register':["ELM's field researcher?\nWe received his introduction.",
  "Reports from KANTO and JOHTO\nmention the same ROCKET groups.",
  "We will compare your field\nnotes with our radio records.",
  "WHITNEY asked us to welcome you.\nHer GYM is taking challengers."],
 'Registered':["Keep recording what you find.\nELM and our staff share reports."],
 'BeforeElm':["Please report your findings to\nELM before joining the study."]}
 say(n,'Reception',["Welcome to the RADIO TOWER.\nThe research desk is here."])
 n='GoldenrodCity_Gym'
 add(n,'Whitney',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_BADGE03_GET, GoldenrodCity_Gym_Reward
    goto_if_unset FLAG_JOHTO_BADGE02_GET, GoldenrodCity_Gym_NotReady
    goto_if_unset FLAG_JOHTO_GOLDENROD_RESEARCH_REGISTERED, GoldenrodCity_Gym_NotReady
    goto_if_defeated TRAINER_JOHTO_WHITNEY, GoldenrodCity_Gym_AfterBattle
    trainerbattle_single TRAINER_JOHTO_WHITNEY, GoldenrodCity_Gym_Text_Intro, GoldenrodCity_Gym_Text_Defeat, GoldenrodCity_Gym_WhitneyVictory, NO_MUSIC
    goto GoldenrodCity_Gym_AfterBattle
GoldenrodCity_Gym_WhitneyVictory::
    msgbox GoldenrodCity_Gym_Text_Upset
    release
    end
GoldenrodCity_Gym_AfterBattle::
    goto_if_unset FLAG_JOHTO_WHITNEY_ENCOURAGED, GoldenrodCity_Gym_Upset
    msgbox GoldenrodCity_Gym_Text_Badge
    setflag FLAG_JOHTO_BADGE03_GET
GoldenrodCity_Gym_Reward::
    goto_if_set FLAG_JOHTO_GOT_TM45_FROM_WHITNEY, GoldenrodCity_Gym_After
    checkitemspace ITEM_TM45, 1
    goto_if_eq VAR_RESULT, FALSE, GoldenrodCity_Gym_BagFull
    giveitem ITEM_TM45, 1
    goto_if_eq VAR_RESULT, FALSE, GoldenrodCity_Gym_BagFull
    setflag FLAG_JOHTO_GOT_TM45_FROM_WHITNEY
    msgbox GoldenrodCity_Gym_Text_TM
    release
    end
GoldenrodCity_Gym_After::
    msgbox GoldenrodCity_Gym_Text_After
    release
    end
GoldenrodCity_Gym_Upset::
    msgbox GoldenrodCity_Gym_Text_Upset
    release
    end
GoldenrodCity_Gym_NotReady::
    msgbox GoldenrodCity_Gym_Text_NotReady
    release
    end
GoldenrodCity_Gym_BagFull::
    msgbox GoldenrodCity_Gym_Text_BagFull
    release
    end
''')
 add(n,'Assistant',r'''
    lock
    faceplayer
    goto_if_not_defeated TRAINER_JOHTO_WHITNEY, GoldenrodCity_Gym_AssistantBefore
    goto_if_set FLAG_JOHTO_BADGE03_GET, GoldenrodCity_Gym_AssistantAfter
    msgbox GoldenrodCity_Gym_Text_AssistantEncourage
    setflag FLAG_JOHTO_WHITNEY_ENCOURAGED
    release
    end
GoldenrodCity_Gym_AssistantBefore::
    msgbox GoldenrodCity_Gym_Text_AssistantBefore
    release
    end
GoldenrodCity_Gym_AssistantAfter::
    msgbox GoldenrodCity_Gym_Text_AssistantAfter
    release
    end
''')
 for k in ['Victoria','Samantha']:
  add(n,k,'    trainerbattle_single TRAINER_JOHTO_'+k.upper()+', '+n+'_Text_'+k+'Intro, '+n+'_Text_'+k+'Defeat\n    msgbox '+n+'_Text_'+k+'After, MSGBOX_AUTOCLOSE\n    end')
 texts[n]={'Intro':["WHITNEY: Welcome! I heard about\nyour trip from KANTO.",
    "My POKEMON and I love a good\nbattle. Let us see your team!"],
 'Defeat':["No! My team tried so hard!"],
 'Upset':["WHITNEY: I... I need a moment."],
 'Badge':["WHITNEY: Sorry about that.\nYou won fair and square.",
    "Here is the PLAINBADGE!\nYour third JOHTO GYM BADGE."],
 'TM':["TM45 teaches ATTRACT.\nTiming can turn a battle around."],
 'After':["WHITNEY: Keep getting stronger.\nI will work hard with my team!"],
 'NotReady':["WHITNEY: Visit our RADIO TOWER\nafter earning BUGSY's BADGE.",
    "They are expecting ELM's\nresearcher. Then let us battle!"],
 'BagFull':["Your BADGE is yours already.\nMake room and collect the TM."],
 'AssistantBefore':["WHITNEY loves her team.\nGet ready for a tough battle."],
 'AssistantEncourage':["She gets upset when she loses.\nShe will be fine in a moment.",
    "Go speak to her again.\nYou earned that BADGE."],
 'AssistantAfter':["Good luck with your next GYM!"],
 'VictoriaIntro':["A cute face can hide real power!"],'VictoriaDefeat':["You looked past appearances."],'VictoriaAfter':["WHITNEY's MILTANK is strong."],
 'SamanthaIntro':["Can you handle my POKEMON?"],'SamanthaDefeat':["That was a fair battle."],'SamanthaAfter':["Every team has its own rhythm."]}
 return scripts,texts


def build(s):
 out={};stats={'chapter':'Ilex and Goldenrod entrance','save_layout_changed':False,
 'native_build_and_emulator':'NOT_RUN_BY_GENERATOR',
 'visual_limits':['Native Kanto tilesets are reused; the radio exterior uses the Silph facade.',
 'Silver and Whitney use native placeholder portraits. FARFETCHD reuses its exact native menu-icon pixels.'],
 'not_implemented':['Goldenrod upper radio floors, underground and department-store floors','Gyms four through eight and Johto League']}
 groups=s.json('data/maps/map_groups.json')
 assert groups['gMapGroup_JohtoEntry'] in (OLD,OLD+NEW)
 for k,v in groups.items():
  if k not in ('group_order','gMapGroup_JohtoEntry'):assert not(set(v)&set(NEW))
 groups['gMapGroup_JohtoEntry']=OLD+NEW;out['data/maps/map_groups.json']=enc(groups)
 arrays=geometry(s);ls=s.json('data/layouts/layouts.json')
 tiles={
 'IlexForest':('General','ViridianForest','LAYOUT_VIRIDIAN_FOREST'),
 'JohtoRoute34':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),
 'GoldenrodCity':('General','SaffronCity','LAYOUT_SAFFRON_CITY'),
 'IlexForest_AzaleaGate':('Building','GenericBuilding2','LAYOUT_ROUTE2_ENTRANCE'),
 'GoldenrodCity_RadioTower_1F':('Building','GenericBuilding2','LAYOUT_ROUTE2_ENTRANCE')}
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
  if layout:j['layout']=layout
  if music:j['music']=music
  for key in ['object_events','warp_events','coord_events','bg_events']:j[key]=[]
  maps[n]=j;return j
 n='IlexForest_AzaleaGate';j=temp(n,'Route2_ViridianForest_SouthEntrance','MAPSEC_ILEX_FOREST','LAYOUT_ILEX_FOREST_AZALEA_GATE')
 j['object_events']=[obj('BLUE',7,5,n+'_Silver',flag='FLAG_JOHTO_SILVER_AZALEA_DEFEATED'),obj('POLICEMAN',9,3,n+'_Officer')]
 j['warp_events']=[warp(x,10,'MAP_AZALEA_TOWN',5) for x in (6,7,8)]+[warp(7,1,'IlexForest',0)]
 j['coord_events']=[{'type':'trigger','x':7,'y':2,'elevation':3,'var':'VAR_TEMP_0','var_value':'0','script':n+'_CheckPass'}]
 n='IlexForest';j=temp(n,'ViridianForest','MAPSEC_ILEX_FOREST','LAYOUT_ILEX_FOREST')
 j['allow_cycling']=False
 j['warp_events']=[warp(28,41,'IlexForest_AzaleaGate',3)]+[warp(x,7,'IlexForest_Route34Gate',1) for x in (5,6,7)]
 j['object_events']=[obj('YOUNGSTER',25,35,n+'_Apprentice'),obj('JOHTO_FARFETCHD',34,13,n+'_Farfetchd'),
  obj('WORKER_M',29,35,n+'_Master'),obj('CUT_TREE',7,17,'EventScript_CutTree',flag='FLAG_TEMP_1')]
 j['bg_events']=[C.bg(31,31,n+'_ForestSign')]
 n='IlexForest_Route34Gate';j=temp(n,'Route2_ViridianForest_NorthEntrance','MAPSEC_ILEX_FOREST')
 j['object_events']=[obj('POLICEMAN',9,3,n+'_Officer'),obj('WOMAN_2',4,6,n+'_Traveler')]
 j['warp_events']=[warp(x,10,'IlexForest',2) for x in (6,7,8)]+[warp(7,1,'JohtoRoute34',0)]
 n='JohtoRoute34';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE34','LAYOUT_JOHTO_ROUTE34','MUS_ROUTE1')
 j['connections']=[{'map':MID['GoldenrodCity'],'direction':'up','offset':-12}]
 j['warp_events']=[warp(9,41,'IlexForest_Route34Gate',3,0),warp(15,12,'JohtoRoute34_DayCare',1,0)]
 j['object_events']=[obj('YOUNGSTER',5,20,n+'_Todd',movement='FACE_RIGHT'),obj('LASS',17,37,n+'_Gina'),obj('POKE_MANIAC',13,18,n+'_Brandon',movement='FACE_LEFT')]
 j['bg_events']=[C.bg(13,29,n+'_RouteSign'),C.bg(20,12,n+'_DayCareSign')]
 n='JohtoRoute34_DayCare';j=temp(n,'Route5_PokemonDayCare','MAPSEC_JOHTO_ROUTE34')
 j['object_events']=[obj('GENTLEMAN',4,4,'Route5_PokemonDayCare_EventScript_DaycareMan'),obj('WOMAN_2',6,5,n+'_Reception',movement='FACE_LEFT')]
 j['warp_events']=[warp(x,7,'JohtoRoute34',1,0) for x in (3,4,5)]
 n='GoldenrodCity';j=temp(n,'SaffronCity','MAPSEC_GOLDENROD_CITY','LAYOUT_GOLDENROD_CITY','MUS_CELADON')
 j['connections']=[{'map':MID['JohtoRoute34'],'direction':'down','offset':12}]
 j['warp_events']=[warp(8,28,'GoldenrodCity_PokemonCenter_1F',1,0),warp(39,28,'GoldenrodCity_Mart',1,0),warp(33,10,'GoldenrodCity_Gym',1,0),warp(11,17,'GoldenrodCity_RadioTower_1F',1,0)]
 j['object_events']=[obj('WOMAN_2',27,19,n+'_Resident'),obj('LITTLE_GIRL',30,13,n+'_GymFan')]
 j['bg_events']=[C.bg(x,y,n+'_'+k) for x,y,k in [(12,28,'CenterSign'),(42,28,'MartSign'),(38,10,'GymSign'),(17,18,'RadioSign')]]
 scripts,rows=ilex_story();tx={n:C.texts(n,d) for n,d in rows.items()}
 for suffix in ['PokemonCenter_1F','PokemonCenter_2F','Mart']:
  old='AzaleaTown_'+suffix;n='GoldenrodCity_'+suffix
  rep=lambda text:text.replace('AZALEA_TOWN','GOLDENROD_CITY').replace('AZALEA','GOLDENROD').replace('AzaleaTown','GoldenrodCity')
  j=json.loads(rep(s.text('data/maps/'+old+'/map.json')));assert j['id']==MID[n];maps[n]=j
  scripts[n]=rep(s.text('data/maps/'+old+'/scripts.inc'));tx[n]=rep(s.text('data/maps/'+old+'/text.inc'))
  if suffix=='PokemonCenter_1F':
   j['object_events'][0]['local_id']='LOCALID_GOLDENROD_NURSE'
   for w in j['warp_events'][:3]:w['dest_warp_id']='0'
  elif suffix=='Mart':
   for w in j['warp_events']:w['dest_warp_id']='1'
 n='GoldenrodCity_RadioTower_1F';j=temp(n,'Route2_ViridianForest_SouthEntrance','MAPSEC_GOLDENROD_CITY','LAYOUT_GOLDENROD_CITY_RADIO_TOWER_1F','MUS_CELADON')
 j['allow_cycling']=False
 j['object_events']=[obj('SCIENTIST',9,3,n+'_ResearchDesk'),obj('WOMAN_2',4,6,n+'_Reception')]
 j['warp_events']=[warp(x,10,'GoldenrodCity',3) for x in (6,7,8)]
 n='GoldenrodCity_Gym';j=temp(n,'CeladonCity_Gym','MAPSEC_GOLDENROD_CITY',music='MUS_GYM')
 j['object_events']=[obj('LASS',6,4,n+'_Whitney'),obj('WOMAN_1',3,11,n+'_Victoria',movement='FACE_RIGHT'),
  obj('LASS',9,10,n+'_Samantha',movement='FACE_LEFT'),obj('WOMAN_2',7,16,n+'_Assistant')]
 j['warp_events']=[warp(x,18,'GoldenrodCity',2) for x in (5,6,7)]
 for n,j in maps.items():
  out['data/maps/'+n+'/map.json']=enc(j);out['data/maps/'+n+'/scripts.inc']=scripts[n].encode()
  out['data/maps/'+n+'/text.inc']=tx.get(n,'@ Native shared dialogue.\n').encode()
 # Add a real checkpoint entrance at the west end without changing existing warps.
 p='data/maps/AzaleaTown/map.json';j=s.json(p);newwarp=warp(4,14,'IlexForest_AzaleaGate',1,0)
 assert len(j['warp_events']) in (5,6)
 if len(j['warp_events'])==5:j['warp_events'].append(newwarp)
 else:assert j['warp_events'][5]==newwarp
 out[p]=enc(j)
 l=next(x for x in ls['layouts'] if x.get('id')==j['layout']);a=V.layout_array(s,j['layout'])
 facade=V.crop(V.layout_array(s,'LAYOUT_VIRIDIAN_CITY'),24,8,5,4)
 current=V.crop(a,3,11,5,4);old=V.crop(A.geometry(s)['AzaleaTown'],3,11,5,4)
 assert current in (old,facade),'Azalea west entrance was independently edited'
 C.paste(a,facade,3,11)
 out[l['blockdata_filepath']]=C.pack(a)
 heals=s.json('src/data/heal_locations.json');v={'id':'HEAL_LOCATION_GOLDENROD_CITY','map':MID['GoldenrodCity'],'x':8,'y':29,
 'respawn_map':MID['GoldenrodCity_PokemonCenter_1F'],'respawn_npc':'LOCALID_GOLDENROD_NURSE'}
 hits=[x for x in heals['heal_locations'] if x['id']==v['id']];assert not hits or hits==[v]
 if not hits:heals['heal_locations'].append(v)
 out['src/data/heal_locations.json']=enc(heals)
 shared(s,out);region(s,out);farfetchd(s,out)
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
 p='include/constants/opponents_johto_ilex.h'
 h='#ifndef GUARD_OPPONENTS_JOHTO_ILEX_H\n#define GUARD_OPPONENTS_JOHTO_ILEX_H\n'
 for n,c,pic,gender,party,num in TRAINERS:h+='#define TRAINER_JOHTO_'+n+' (HOENN_TRAINERS_START + '+str(num)+')\n'
 out[p]=(h+'#endif\n').encode()
 for path in (s.root/'include/constants').glob('opponents*.h'):
  rel=path.relative_to(s.root).as_posix()
  if rel==p:continue
  used={int(v,0) for v in re.findall(r'HOENN_TRAINERS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',s.text(rel))}
  assert not(used&{v[-1] for v in TRAINERS}),('trainer collision',rel)
 p='include/constants/opponents.h';anchor='#include "constants/opponents_johto_azalea.h"'
 out[p]=C.once(s.text(p),anchor,anchor+'\n#include "constants/opponents_johto_ilex.h"','Ilex trainer include').encode()
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
  display='SILVER' if n=='SILVER_AZALEA' else n
  trainers+='    [TRAINER_JOHTO_'+n+'] = {\n        .trainerClass = TRAINER_CLASS_'+c+',\n        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_'+gender+(' | F_TRAINER_FEMALE' if gender=='FEMALE' else '')+',\n        .trainerPic = TRAINER_PIC_'+pic+',\n        .trainerName = _("'+display+'"),\n        .items = {},\n        .doubleBattle = FALSE,\n        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,\n        .party = '+('NO_ITEM_CUSTOM_MOVES' if custom else 'NO_ITEM_DEFAULT_MOVES')+'('+sym+'),\n    },\n'
 out['src/data/trainer_parties_johto_ilex.h']=parties.encode();out['src/data/trainers_johto_ilex.h']=trainers.encode()
 for p,a,inc in [('src/data/trainers.h','#include "trainers_johto_azalea.h"','#include "trainers_johto_ilex.h"'),('src/data/trainer_parties.h','#include "trainer_parties_johto_azalea.h"','#include "trainer_parties_johto_ilex.h"')]:
  out[p]=C.once(s.text(p),a,a+'\n'+inc,'Ilex trainer data').encode()
 p='data/event_scripts.s';t=s.text(p);block='@ '+MARK+'\n'+''.join('    .include "data/maps/'+n+'/'+f+'"\n' for n in NEW for f in ['scripts.inc','text.inc'])
 if MARK not in t:assert not any('data/maps/'+n+'/' in t for n in NEW);t=t.rstrip()+'\n\n'+block
 else:assert block in t
 out[p]=t.encode()
 p='tools/johto/build_azalea.py';t=s.text(p)
 guard=' # ILEX_EXTENSION_GUARD\n if any(n not in OLD + NEW for n in s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]):\n  raise RuntimeError("Ilex extension exists; use build_ilex.py")\n'
 if '# ILEX_EXTENSION_GUARD' not in t:
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
def farfetchd(s,out):
 p='include/constants/event_objects.h';t=s.text(p);marker='OBJ_EVENT_GFX_JOHTO_FARFETCHD'
 if marker not in t:
  assert re.search(r'#define\s+NUM_OBJ_EVENT_GFX\s+235\b',t)
  t,n=re.subn(r'#define\s+NUM_OBJ_EVENT_GFX\s+235\b','#define '+marker+' 235\n#define NUM_OBJ_EVENT_GFX 236',t);assert n==1
 else:assert re.search(r'#define\s+'+marker+r'\s+235\b',t)
 out[p]=t.encode()
 p='src/event_object_movement.c';t=s.text(p)
 if '#include "graphics.h"' not in t:t=C.once(t,'#include "global.h"','#include "global.h"\n#include "graphics.h"','icon declaration')
 if '#include "pokemon_icon.h"' not in t:t=C.once(t,'#include "global.h"','#include "global.h"\n#include "pokemon_icon.h"','icon palette declaration')
 tag='#define OBJ_EVENT_PAL_TAG_JOHTO_FARFETCHD 0x1143'
 if 'OBJ_EVENT_PAL_TAG_JOHTO_FARFETCHD' not in t:
  assert not re.search(r'0x1143\b',t)
  a='#include "data/object_events/object_event_graphics.h"'
  t=C.once(t,a,tag+'\n\n'+a,'Farfetchd palette tag')
  a='static const struct SpritePalette sObjectEventSpritePalettes[] = {'
  t=C.once(t,a,a+'\n    {gMonIconPalettes[1], OBJ_EVENT_PAL_TAG_JOHTO_FARFETCHD},','Farfetchd palette')
 else:assert tag in t and '{gMonIconPalettes[1], OBJ_EVENT_PAL_TAG_JOHTO_FARFETCHD}' in t
 out[p]=t.encode()
 p='src/data/object_events/object_event_pic_tables.h';t=s.text(p)
 block='\nstatic const struct SpriteFrameImage sPicTable_JohtoFarfetchd[] = {\n    {gMonIcon_Farfetchd, 512},\n};\n'
 if 'sPicTable_JohtoFarfetchd' not in t:t=t.rstrip()+'\n'+block
 else:assert block in t
 out[p]=t.encode()
 p='src/data/object_events/object_event_graphics_info.h';t=s.text(p)
 block=r'''
const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_JohtoFarfetchd = {
    .tileTag = TAG_NONE,
    .paletteTag = OBJ_EVENT_PAL_TAG_JOHTO_FARFETCHD,
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
    .images = sPicTable_JohtoFarfetchd,
    .affineAnims = gDummySpriteAffineAnimTable,
};
'''
 if 'gObjectEventGraphicsInfo_JohtoFarfetchd' not in t:t=t.rstrip()+'\n'+block
 else:assert block in t
 out[p]=t.encode()
 p='src/data/object_events/object_event_graphics_info_pointers.h';t=s.text(p)
 decl='const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_JohtoFarfetchd;\n'
 anchor='const struct ObjectEventGraphicsInfo *const gObjectEventGraphicsInfoPointers[NUM_OBJ_EVENT_GFX] = {'
 line='    [OBJ_EVENT_GFX_JOHTO_FARFETCHD] = &gObjectEventGraphicsInfo_JohtoFarfetchd,'
 if 'OBJ_EVENT_GFX_JOHTO_FARFETCHD' not in t:t=C.once(t,anchor,decl+'\n'+anchor+'\n'+line,'Farfetchd gfx pointer')
 else:assert decl in t and line in t
 out[p]=t.encode()


def region(s,out):
 p='src/data/region_map/region_map_sections.json';j=s.json(p)
 oldids=['JOHTO_CHERRYGROVE_AIRSTRIP','JOHTO_ROUTE_29','NEW_BARK_TOWN','CHERRYGROVE_CITY','JOHTO_ROUTE30','JOHTO_ROUTE31','VIOLET_CITY','JOHTO_ROUTE32','JOHTO_UNION_CAVE','JOHTO_ROUTE33','AZALEA_TOWN','SLOWPOKE_WELL']
 existing={x['id']:x for x in j['map_sections'] if x.get('id')}
 added='MAPSEC_GOLDENROD_CITY' in existing
 assert all('MAPSEC_'+v in existing for v in oldids),'Johto section source differs'
 # Make room to the west while preserving every section ID and array position.
 if not added:
  for v in oldids:existing['MAPSEC_'+v]['x']+=4
 specs=[('ILEX_FOREST','ILEX FOREST',2,8,2,1),('JOHTO_ROUTE34','ROUTE 34',2,4,1,4),('GOLDENROD_CITY','GOLDENROD CITY',2,3,1,1)]
 for name,label,x,y,w,h in specs:
  row={'id':'MAPSEC_'+name,'name':label,'x':x,'y':y,'width':w,'height':h}
  hits=[v for v in j['map_sections'] if v.get('id')==row['id']];assert not hits or hits==[row]
  if not hits:j['map_sections'].append(row)
 assert [v.get('id') for v in j['map_sections'][:len(s.json(p)['map_sections'])]]==[v.get('id') for v in s.json(p)['map_sections']]
 out[p]=enc(j)
 for p in ['src/region_map.c','src/pokemon_summary_screen.c']:
  t=s.text(p);pat=r'(MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP[\s\S]{0,120}?<=\s*)MAPSEC_SLOWPOKE_WELL'
  if re.search(pat,t):t,n=re.subn(pat,lambda m:m.group(1)+'MAPSEC_GOLDENROD_CITY',t);assert n==1
  else:assert re.search(pat.replace('MAPSEC_SLOWPOKE_WELL','MAPSEC_GOLDENROD_CITY'),t)
  out[p]=t.encode()
 p='src/region_map.c';t=out[p].decode()
 if '// ILEX_GOLDENROD_MAP_GRID_V1' not in t:
  pat=r'(?m)^([ \t]*)// AZALEA_ROUTE32_MAP_GRID_V1'
  lines=['// ILEX_GOLDENROD_MAP_GRID_V1','if (layer != LAYER_MAP)','    return MAPSEC_NONE;',
   'if (x == 2 && y == 3)','    return MAPSEC_GOLDENROD_CITY;',
   'if (x == 2 && y >= 4 && y <= 7)','    return MAPSEC_JOHTO_ROUTE34;',
   'if (x >= 2 && x <= 3 && y == 8)','    return MAPSEC_ILEX_FOREST;',
   'if (x < 4)','    return MAPSEC_NONE;',
   'x -= 4;','// AZALEA_ROUTE32_MAP_GRID_V1']
  t,n=re.subn(pat,lambda m:'\n'.join(m.group(1)+v for v in lines),t);assert n==1
 out[p]=t.encode()
 p='graphics/region_map/johto_entry.bin';v=list(struct.unpack('<600H',s.read(p)))
 # This mini-map is dedicated to Johto; the CANCEL button and other regions remain unchanged.
 for y in range(6,14):
  for x in range(4,25):v[y*30+x]=5
 for row in j['map_sections']:
  if row.get('id') not in {'MAPSEC_'+v for v in oldids}|{'MAPSEC_'+z[0] for z in specs}:continue
  for y in range(row['y'],row['y']+row['height']):
   for x in range(row['x'],row['x']+row['width']):
    assert 0<=x+4<30 and 0<=y+4<16
    v[(y+4)*30+x+4]=0x1001 if row['width']==row['height']==1 else 0x100a
 out[p]=struct.pack('<600H',*v)
 p='src/wild_pokemon_area.c';t=s.text(p)
 extra=[('IlexForest','johtoIlexForest','MAP_ILEX_FOREST'),('Route34','johtoRoute34','MAP_JOHTO_ROUTE34')]
 if 'bool8 johtoIlexForest;' not in t:
  t,n=re.subn(r'(bool8\s+johtoSlowpokeWell\s*;)',lambda m:m.group(1)+''.join('\n    bool8 '+f+';' for _,f,_ in extra),t);assert n==1
 if 'MAP_GROUP(MAP_ILEX_FOREST)' not in t:
  pat=r'(?s)(if\s*\(header->mapGroup\s*==\s*MAP_GROUP\(MAP_SLOWPOKE_WELL_1F\)\s*&&\s*header->mapNum\s*==\s*MAP_NUM\(MAP_SLOWPOKE_WELL_1F\)\s*\)\s*\{\s*habitats->johtoSlowpokeWell\s*=\s*TRUE;\s*continue;\s*\})'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n            '+m.group(1).replace('MAP_SLOWPOKE_WELL_1F',mn).replace('johtoSlowpokeWell',f) for _,f,mn in extra),t);assert n==1
 if 'habitats.johtoIlexForest || habitats.johtoRoute34' not in t:
  t,n=re.subn(r'(if\s*\([^\n]*habitats\.johtoRoute29[^\n]*habitats\.johtoSlowpokeWell)\)',lambda m:m.group(1)+' || habitats.johtoIlexForest || habitats.johtoRoute34)',t);assert n==1
 if 'GetJohtoIlexForestAreaMarkerSubsprite(areaCount++, subsprites);' not in t:
  pat=r'(if\s*\(habitats\.johtoSlowpokeWell\)\s*GetJohtoSlowpokeWellAreaMarkerSubsprite\(areaCount\+\+,\s*subsprites\);)'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n        if (habitats.'+f+')\n            GetJohto'+key+'AreaMarkerSubsprite(areaCount++, subsprites);' for key,f,_ in extra),t);assert n==1
 out[p]=t.encode()
 p='include/pokedex_area_markers.h';t=s.text(p)
 if 'GetJohtoIlexForestAreaMarkerSubsprite' not in t:
  t,n=re.subn(r'(void GetJohtoSlowpokeWellAreaMarkerSubsprite\([^;]*;)',lambda m:m.group(1)+''.join('\nvoid GetJohto'+key+'AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);' for key,_,_ in extra),t);assert n==1
 out[p]=t.encode()
 p='src/pokedex_area_markers.c';t=s.text(p)
 markers=[('Route29','MediumHorizontal',72,47),('Route30','SmallVertical',59,26),('Route31','SmallHorizontal',47,19),('Route32','SmallVertical',39,28),('UnionCave','Circular',39,49),('Route33','Circular',34,49),('SlowpokeWell','Circular',29,43),('IlexForest','SmallHorizontal',19,49),('Route34','SmallVertical',19,28)]
 for key,shape,x,y in markers:
  name='GetJohto'+key+'AreaMarkerSubsprite'
  body='void '+name+'(s32 i, struct Subsprite *subsprites)\n{\n    if (subsprites == NULL)\n        return;\n    subsprites[i] = sSubsprite_'+shape+';\n    subsprites[i].x = '+str(x)+' + (HOENN_AREA_MAP_LEFT * 8 - 104);\n    subsprites[i].y = '+str(y)+';\n}'
  if re.search(r'void\s+'+name+r'\(',t):t=C.replace_function(t,name,body,'Ilex habitat marker')
  else:t=t.rstrip()+'\n\n'+body+'\n'
 out[p]=t.encode()
 p='src/pokedex_screen.c';t=s.text(p)
 labels=[('Gold','GOLD'),('Vio','VIO'),('R34','34'),('Ilex','ILEX'),('Aza','AZA'),('CG','CG'),('AirShort','AIR')]
 decl=''.join('static const u8 sText_Johto'+key+'[] = _("'+label+'");\n' for key,label in labels)
 if 'sText_JohtoR34[]' not in t:
  a='static const u8 sText_JohtoR33[] = _("33");\n';assert t.count(a)==1;t=t.replace(a,a+decl)
 body='static void DexScreen_DrawJohtoEntryArea(u8 windowId)\n{\n    FillWindowPixelBuffer(windowId, PIXEL_FILL(2));\n    FillWindowPixelRect(windowId, PIXEL_FILL(6), 3, 3, 122, 66);\n'
 for x,y,w,h in [(20,20,4,34),(40,20,4,34),(60,20,4,34),(40,20,24,4),(20,50,44,4),(60,50,52,4),(30,44,4,10)]:
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(3), '+', '.join(map(str,[x,y,w,h]))+');\n'
  inner=[x+1,y+1,w-2,h-2]
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(5), '+', '.join(map(str,inner))+');\n'
 for x,y in [(19,19),(39,19),(59,43),(59,49),(107,49),(29,49),(39,49),(29,43)]:
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(2), '+', '.join(map(str,[x,y,6,6]))+');\n    FillWindowPixelRect(windowId, PIXEL_FILL(5), '+', '.join(map(str,[x+1,y+1,4,4]))+');\n'
 for key,x,y in [('Gold',7,7),('Vio',37,7),('R31',50,12),('R34',6,31),('R32',46,31),('R30',68,31),('CG',68,42),('Ilex',5,56),('Aza',30,62),('Union',39,56),('R29',83,42),('AirShort',60,62),('NewBark',84,62),('Well',24,39)]:
  body+='    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_Johto'+key+', '+str(x)+', '+str(y)+', 0);\n'
 body+='}'
 out[p]=C.replace_function(t,'DexScreen_DrawJohtoEntryArea',body,'Ilex habitat diagram').encode()


def validate(s,out,stats):
 final=Source(s.root,dict(s.overlay,**out))
 ls={x['id']:x for x in final.json('data/layouts/layouts.json')['layouts'] if x.get('id')}
 maps={n:final.json('data/maps/'+n+'/map.json') for n in NEW}
 starts={'IlexForest_AzaleaGate':(7,10),'IlexForest':(28,40),'IlexForest_Route34Gate':(7,10),'JohtoRoute34':(9,42),
 'JohtoRoute34_DayCare':(4,7),'GoldenrodCity':(22,39),'GoldenrodCity_PokemonCenter_1F':(7,7),'GoldenrodCity_Mart':(4,7),
 'GoldenrodCity_RadioTower_1F':(7,10),'GoldenrodCity_Gym':(6,18)}
 checks=[]
 for n,m in maps.items():
  l=ls[m['layout']];w,h=l['width'],l['height'];raw=final.read(l['blockdata_filepath'])
  assert len(raw)==w*h*2;vals=struct.unpack('<'+'H'*(w*h),raw)
  outside=n in ('IlexForest','JohtoRoute34','GoldenrodCity')
  def walk(x,y):return 0<=x<w and 0<=y<h and not((vals[y*w+x]>>10)&3) and (not outside or vals[y*w+x]>>12!=1)
  objects=m['object_events'];solid={(o['x'],o['y']) for o in objects}
  for o in objects:
   assert 0<=o['x']<w and 0<=o['y']<h
   if n!='GoldenrodCity_PokemonCenter_2F':assert walk(o['x'],o['y']),(n,'NPC tile',o)
  for wp in m['warp_events']:
   dst=next((k for k in NEW if MID[k]==wp['dest_map']),None)
   if dst:
    i=int(wp['dest_warp_id']);other=maps[dst]['warp_events']
    assert 0<=i<len(other) and other[i]['dest_map']==m['id'],(n,'non-reciprocal warp',wp)
  if n not in starts:
   checks.append({'map':n,'native_CableClub_layout':True});continue
  start=starts[n];assert walk(*start),(n,'spawn',start)
  def bfs(obstacles):
   seen={start};q=deque([start])
   while q:
    x,y=q.popleft()
    for z in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
     if z not in seen and z not in obstacles and walk(*z):seen.add(z);q.append(z)
   return seen
  closed=bfs(solid)
  if n=='IlexForest':
   assert (6,7) not in closed,'CUT tree can be bypassed'
   solid.remove((7,17))
  seen=bfs(solid)
  for wp in m['warp_events']:
   z=(wp['x'],wp['y']+1) if n in ('JohtoRoute34','GoldenrodCity') else (wp['x'],wp['y'])
   assert z in seen,(n,'unreachable warp',wp,z)
  for o in objects:
   x,y=o['x'],o['y'];gfx=o['graphics_id']
   if gfx=='OBJ_EVENT_GFX_NURSE':assert (x,y+2) in seen;continue
   if gfx=='OBJ_EVENT_GFX_CLERK':continue
   assert any(z in seen for z in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),(n,'NPC cannot be faced',o)
  if n=='IlexForest':
   assert (26,35) in seen and (25,34) in closed and (29,34) in closed and (34,14) in closed
  if n=='IlexForest_AzaleaGate':
   assert (7,1) not in bfs(solid|{(7,2)}),'Silver checkpoint can be bypassed'
  if n=='GoldenrodCity':assert all((x,39) in seen for x in range(20,24))
  if n=='JohtoRoute34':assert all((x,0) in seen for x in range(8,12))
  checks.append({'map':n,'walkable_reachable':len(seen),'NPC_and_warps':True})
 # Append-only map/layout IDs, existing native map transitions and save ABI.
 before=s.json('data/maps/map_groups.json')
 after=final.json('data/maps/map_groups.json')
 assert after['gMapGroup_JohtoEntry'][:len(OLD)]==OLD
 assert all(after[k]==v for k,v in before.items() if k!='gMapGroup_JohtoEntry')
 oldlayout=s.json('data/layouts/layouts.json')['layouts'];assert final.json('data/layouts/layouts.json')['layouts'][:len(oldlayout)]==oldlayout
 azbefore=s.json('data/maps/AzaleaTown/map.json');azafter=final.json('data/maps/AzaleaTown/map.json')
 assert azbefore['warp_events'][:5]==azafter['warp_events'][:5]
 assert not any(p in out for p in ['include/global.h','include/pokemon.h','src/save.c','src/load_save.c'])
 cmds=set(re.findall(r'(?m)^\s*\.macro\s+(\w+)',s.text('asm/macros/event.inc')+'\n'+s.text('asm/macros/map.inc')))
 cmds.update(re.findall(r'(?m)^\s*create_movement_action\s+(\w+)',s.text('asm/macros/movement.inc')))
 for p,b in out.items():
  if p.endswith('scripts.inc'):
   for line in b.decode().splitlines():
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
 for n in ['IlexForest','GoldenrodCity_Gym']:
  script=out['data/maps/'+n+'/scripts.inc'].decode()
  assert 'giveitem' in script and 'goto_if_eq VAR_RESULT, FALSE,' in script
 native=out['src/event_object_movement.c'].decode()
 assert native.index('#define OBJ_EVENT_PAL_TAG_JOHTO_FARFETCHD')<native.index('#include "data/object_events/object_event_graphics_info.h"')
 stats['static_checks']=checks;return stats
def apply(root,mutate=False):
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 s=Source(root);out,stats=build(s);validate(s,out,stats)
 repeat,_=build(Source(root,dict(s.overlay,**out)));assert repeat==out,'not idempotent'
 owned=[p for p in out if any(p.startswith('data/maps/'+n+'/') or p.startswith('data/layouts/'+n+'/') for n in NEW)]
 owned += ['include/constants/opponents_johto_ilex.h','src/data/trainers_johto_ilex.h','src/data/trainer_parties_johto_ilex.h']
 owned += ['tools/johto/'+n.lower()+'_wild.json' for n in WILD]
 for p in owned:
  if s.exists(p):
   prior=s.read(p)
   if p=='data/maps/GoldenrodCity_Gym/scripts.inc' and sha(prior)=='c54b7885feff3fdba9023881c9f2fe66fdcd432b27bfa8ed6c65640d8e067761':
    corrected=prior.replace(b'    checktrainerflag TRAINER_JOHTO_WHITNEY\n    goto_if_eq VAR_RESULT, TRUE, GoldenrodCity_Gym_AfterBattle',b'    goto_if_defeated TRAINER_JOHTO_WHITNEY, GoldenrodCity_Gym_AfterBattle').replace(b'    checktrainerflag TRAINER_JOHTO_WHITNEY\n    goto_if_eq VAR_RESULT, FALSE, GoldenrodCity_Gym_AssistantBefore',b'    goto_if_not_defeated TRAINER_JOHTO_WHITNEY, GoldenrodCity_Gym_AssistantBefore')
    assert corrected==out[p],'unexpected Whitney migration'
   else:assert prior==out[p],'owned artifact changed: '+p
 changed={p:b for p,b in out.items() if not s.exists(p) or s.read(p)!=b}
 print(json.dumps({'apply':mutate,'files':sorted(changed),'validation':stats},indent=2))
 if not mutate or not changed:return
 for p,b in s.used.items():assert (root/p).read_bytes()==b,'concurrent edit: '+p
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=root/'outputs/johto-ilex-goldenrod-v1'/stamp;dest.mkdir(parents=True,exist_ok=False)
 manifest={'time':stamp,'validation':stats,'files':{}}
 for p,b in changed.items():
  path=root/p;old=path.read_bytes() if path.exists() else None
  manifest['files'][p]={'before':sha(old) if old is not None else None,'after':sha(b)}
  if old is not None:
   bak=dest/'before'/p;bak.parent.mkdir(parents=True,exist_ok=True);bak.write_bytes(old)
 (dest/'manifest.json').write_bytes(enc(manifest))
 for p,b in changed.items():
  target=root/p;target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.ilex.tmp')
  assert not tmp.exists();tmp.write_bytes(b);tmp.replace(target)
 print('APPLIED',dest/'manifest.json')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root).resolve(),a.apply)
