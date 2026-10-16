#!/usr/bin/env python3
"""Prepare the Mahogany investigation chapter; source-only until strict native QA."""
import argparse,copy,datetime,json,re,struct,subprocess,sys
from collections import deque
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_olivine_cianwood as O
C,V=O.C,O.V
Source,enc,sha=O.Source,O.enc,O.sha
OLD=O.OLD+O.NEW
NEW=['EcruteakCity_EastGate','JohtoRoute42','MtMortar_1F','MahoganyTown',
 'MahoganyTown_PokemonCenter_1F','MahoganyTown_PokemonCenter_2F',
 'MahoganyTown_Shop','MahoganyTown_Gym','JohtoRoute43','LakeOfRage',
 'JohtoRocketHQ_B1F','JohtoRocketHQ_B2F','JohtoRocketHQ_B3F']
IDS=['ECRUTEAK_CITY_EAST_GATE','JOHTO_ROUTE42','MT_MORTAR_1F','MAHOGANY_TOWN',
 'MAHOGANY_TOWN_POKEMON_CENTER_1F','MAHOGANY_TOWN_POKEMON_CENTER_2F',
 'MAHOGANY_TOWN_SHOP','MAHOGANY_TOWN_GYM','JOHTO_ROUTE43','LAKE_OF_RAGE',
 'JOHTO_ROCKET_HQ_B1F','JOHTO_ROCKET_HQ_B2F','JOHTO_ROCKET_HQ_B3F']
MID=dict(zip(NEW,['MAP_'+v for v in IDS]))
MARK='JOHTO_MAHOGANY_INVESTIGATION_V1'
# Badge7/8 retain their previously reserved offsets; no SaveBlock growth.
FLAGS={'FLAG_JOHTO_BADGE07_GET':22,'FLAG_JOHTO_RED_GYARADOS_RESOLVED':43,
 'FLAG_JOHTO_LANCE_INVESTIGATION_JOINED':44,'FLAG_JOHTO_RED_SCALE_RECEIVED':45,
 'FLAG_JOHTO_HQ_ELECTRODE1_CLEARED':46,'FLAG_JOHTO_HQ_ELECTRODE2_CLEARED':47,
 'FLAG_JOHTO_HQ_ELECTRODE3_CLEARED':48,'FLAG_JOHTO_ROCKET_HQ_CLEARED':49,
 'FLAG_JOHTO_LANCE_TM24_RECEIVED':50,'FLAG_JOHTO_PRYCE_TM13_RECEIVED':51,
 'FLAG_JOHTO_RADIO_TOWER_CLEARED':52,'FLAG_JOHTO_LANCE_MOVED_TO_HQ':53}
TRAINERS=[
 ('HARRISON','POKEMANIAC','POKEMANIAC','MALE',[('NIDOKING',29),('NIDOQUEEN',29)],827),
 ('MARKUS','HIKER','HIKER','MALE',[('GEODUDE',28),('GRAVELER',30)],828),
 ('TIFFANY','PICNICKER','PICNICKER','FEMALE',[('CLEFAIRY',29)],829),
 ('HQ_GUARD_A','TEAM_ROCKET','ROCKET_GRUNT_M','MALE',[('RATICATE',29),('GOLBAT',29)],830),
 ('HQ_GUARD_B','TEAM_ROCKET','ROCKET_GRUNT_M','MALE',[('GRIMER',29),('RATICATE',30)],831),
 ('HQ_SCIENTIST','SCIENTIST','SCIENTIST','MALE',[('MAGNEMITE',30),('KOFFING',30)],832),
 ('PETREL','TEAM_ROCKET','ROCKET_GRUNT_M','MALE',[('ZUBAT',30),('RATICATE',30),('KOFFING',32)],833),
 ('ARIANA','TEAM_ROCKET','ROCKET_GRUNT_F','FEMALE',[('ARBOK',32),('GLOOM',32),('MURKROW',32)],834),
 ('PRYCE','LEADER','LEADER_BLAINE','MALE',[
  ('SEEL',27,['HEADBUTT','ICY_WIND','AURORA_BEAM','REST']),
  ('DEWGONG',29,['HEADBUTT','ICY_WIND','AURORA_BEAM','REST']),
  ('PILOSWINE',31,['ICY_WIND','MIST','FURY_ATTACK','BLIZZARD'])],835)]
DISPLAY={'HQ_GUARD_A':'GRUNT','HQ_GUARD_B':'GRUNT','HQ_SCIENTIST':'SCIENTIST'}
def ident(n):return IDS[NEW.index(n)]
def warp(x,y,dst,index,elevation=3):
 return {'x':x,'y':y,'elevation':elevation,'dest_map':MID.get(dst,dst),'dest_warp_id':str(index)}
def obj(gfx,x,y,script,**kw):
 flag=kw.pop('flag','0');v=C.obj(gfx,x,y,script,**kw);v['flag']=flag;return v

WILD={
 'JohtoRoute42':(['SPEAROW','MAREEP','FLAAFFY','SPEAROW','MAREEP','FLAAFFY','MANKEY','FEAROW','MANKEY','MARILL','FEAROW','MARILL'],
 ['ZUBAT','MAREEP','FLAAFFY','ZUBAT','MAREEP','FLAAFFY','RATICATE','NOCTOWL','RATICATE','MARILL','GOLBAT','MARILL'],[17,17,18,18,19,20,17,21,19,18,22,20]),
 'JohtoRoute43':(['PIDGEOTTO','MAREEP','FLAAFFY','PIDGEOTTO','MAREEP','FLAAFFY','GIRAFARIG','FARFETCHD','GIRAFARIG','FLAAFFY','PIDGEOTTO','GIRAFARIG'],
 ['NOCTOWL','MAREEP','FLAAFFY','NOCTOWL','MAREEP','FLAAFFY','GIRAFARIG','VENONAT','GIRAFARIG','VENOMOTH','GOLBAT','GIRAFARIG'],[16,16,17,18,18,20,17,20,19,20,22,21]),
 'MtMortar_1F':(['ZUBAT','GEODUDE','MACHOP','RATTATA','ZUBAT','GEODUDE','MACHOP','GRAVELER','RATICATE','GOLBAT','MACHOKE','MARILL'],
 ['ZUBAT','GEODUDE','MACHOP','RATTATA','ZUBAT','GEODUDE','MACHOP','GRAVELER','RATICATE','GOLBAT','MACHOKE','MARILL'],[15,15,16,16,17,17,18,20,19,20,22,18])}
WATER={'JohtoRoute42':(['GOLDEEN','GOLDEEN','SEAKING','SEAKING','SEAKING'],[15,17,20,21,22]),
 'LakeOfRage':(['MAGIKARP','MAGIKARP','GYARADOS','GYARADOS','GYARADOS'],[10,15,20,22,25])}

def mahogany_geometry(s):
 vir=V.layout_array(s,'LAYOUT_VIRIDIAN_CITY')
 pew=V.layout_array(s,'LAYOUT_PEWTER_CITY')
 saff=V.layout_array(s,'LAYOUT_SAFFRON_CITY')
 def land(w,h):
  a=[[0x3001]*w for _ in range(h)]
  for box in [(0,0,w,2),(0,0,2,h),(w-2,0,w,h),(0,h-2,w,h)]:C.fill(a,*box,C.dense)
  return a
 r42=land(48,24);C.fill(r42,0,10,48,14,0x3195)
 for box in [(8,3,19,8),(28,3,39,8)]:C.fill(r42,*box,0x112b)
 for box in [(5,16,15,21),(30,16,42,21)]:C.fill(r42,*box,C.grass)
 route10=V.layout_array(s,'LAYOUT_ROUTE10')
 for x in [8,31]:
  C.paste(r42,V.crop(route10,6,17,5,3),x,4)
  C.fill(r42,x+1,7,x+4,10,0x3195)
 # Gate facade uses the same native General tiles as validated Route38.
 C.paste(r42,V.crop(vir,24,8,5,4),2,6)
 town=land(32,32);C.fill(town,0,15,30,19,0x3195)
 C.fill(town,14,0,18,29,0x3195);C.fill(town,4,24,27,28,0x3195)
 C.paste(town,V.crop(saff,22,34,5,5),5,20)
 C.paste(town,V.crop(saff,21,11,5,4),20,20)
 C.paste(town,V.crop(pew,12,12,7,5),12,4)
 for x,y in [(11,24),(26,23),(21,8)]:town[y][x]=0x0403
 # Native elevation1/collision0 water stays usable by Surf at a level3 shore.
 r43=land(24,32);C.fill(r43,10,0,14,32,0x3195)
 for box in [(3,5,9,14),(16,5,22,14),(3,20,9,28),(16,20,22,28)]:C.fill(r43,*box,C.grass)
 lake=land(40,36);C.fill(lake,18,24,22,36,0x3195)
 C.fill(lake,7,5,33,24,0x112b);C.fill(lake,7,24,33,25,0x3115)
 C.fill(lake,5,26,35,29,0x3195)
 arrays={'EcruteakCity_EastGate':V.layout_array(s,'LAYOUT_ROUTE2_ENTRANCE'),
  'JohtoRoute42':r42,'MtMortar_1F':V.layout_array(s,'LAYOUT_ROCK_TUNNEL_1F'),
  'MahoganyTown':town,'JohtoRoute43':r43,'LakeOfRage':lake}
 shop=V.layout_array(s,'LAYOUT_HOUSE5');floor=shop[6][4]
 C.fill(shop,5,2,9,5,floor);shop[2][7]=0x3275
 arrays['MahoganyTown_Shop']=shop
 arrays['MahoganyTown_Gym']=V.layout_array(s,'LAYOUT_PEWTER_CITY_GYM')
 # All dungeon stairs will be taken from each actual template's warp metadata.
 # No invented staircase metatile or teleport-on-normal-floor is accepted.
 for n,k in [('JohtoRocketHQ_B1F',1),('JohtoRocketHQ_B2F',2),('JohtoRocketHQ_B3F',3)]:
  a=V.layout_array(s,'LAYOUT_SILPH_CO_'+str(k)+'F')
  C.fill(a,3,4,34,20,0x3334);C.fill(a,27,3,32,4,0x3334)
  original=s.json('data/maps/SilphCo_'+str(k)+'F/map.json')
  keep={1:{(8,20),(9,20),(31,2)},2:{(28,2),(30,2)},3:{(28,2)}}[k]
  for wp in original['warp_events']:
   x,y=wp['x'],wp['y']
   if (x,y) not in keep:a[y][x]=0x3334
  arrays[n]=a
 cave=arrays['MtMortar_1F'];old=s.json('data/maps/RockTunnel_1F/map.json')
 for wp in old['warp_events']:
  if (wp['x'],wp['y']) not in {(17,2),(18,37)}:cave[wp['y']][wp['x']]=0x3281
 C.fill(cave,16,3,20,37,0x3281)
 return arrays

def mahogany_story():
 scripts={};texts={}
 def add(n,k,body):
  scripts.setdefault(n,n+'_MapScripts::\n    .byte 0\n')
  scripts[n]+='\n'+n+'_'+k+'::\n'+body.strip()+'\n'
 def say(n,k,lines):
  add(n,k,'    msgbox '+n+'_Text_'+k+', MSGBOX_NPC\n    end')
  texts.setdefault(n,{})[k]=lines
 def trainer(n,k,lines):
  add(n,k,'    trainerbattle_single TRAINER_JOHTO_'+k+', '+n+'_Text_'+k+'Intro, '+n+'_Text_'+k+'Defeat\n    msgbox '+n+'_Text_'+k+'After, MSGBOX_NPC\n    end')
  texts.setdefault(n,{}).update({k+'Intro':[lines[0]],k+'Defeat':[lines[1]],k+'After':[lines[2]]})
 def receipt(n,k,item,flag,before,after):
  add(n,k,'''
    lock
    faceplayer
    goto_if_set '''+flag+', '+n+'_'+k+'''After
    giveitem '''+item+'''
    goto_if_eq VAR_RESULT, FALSE, '''+n+'_'+k+'''Full
    setflag '''+flag+'''
'''+n+'_'+k+'''After::
    msgbox '''+n+'_Text_'+k+'''After
    release
    end
'''+n+'_'+k+'''Full::
    msgbox '''+n+'_Text_'+k+'''Full
    release
    end
''')
  texts.setdefault(n,{})[k+'After']=after
  texts[n][k+'Full']=[before]
 n='EcruteakCity_EastGate'
 add(n,'Officer','''
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_BADGE06_GET, EcruteakCity_EastGate_Before
    msgbox EcruteakCity_EastGate_Text_Open
    release
    end
EcruteakCity_EastGate_Before::
    msgbox EcruteakCity_EastGate_Text_Before
    release
    end
''')
 add(n,'Gate','''
    goto_if_set FLAG_JOHTO_BADGE06_GET, EcruteakCity_EastGate_Allow
    lockall
    msgbox EcruteakCity_EastGate_Text_Before
    applymovement OBJ_EVENT_ID_PLAYER, EcruteakCity_EastGate_Back
    waitmovement 0
    releaseall
    end
EcruteakCity_EastGate_Allow::
    end
EcruteakCity_EastGate_Back:
    walk_down
    step_end
''')
 texts[n]={'Open':["AMPHY's light is back. Good!\nThe eastern road is now safe.",
 "People at LAKE OF RAGE report\nstrange radio interference."],
 'Before':["Help JASMINE restore AMPHY's\nlight. Earn her MINERALBADGE.",
 "Eastern traffic stays closed\nuntil our coastal teams return."]}
 n='JohtoRoute42'
 say(n,'Hiker',["MT. MORTAR's tunnels meet this\nroad on both sides of the lake.",
 "The road leads to MAHOGANY.\nSomething is upsetting the lake."])
 trainer(n,'HARRISON',["My NIDOKING can move mountains!","This road has stronger trainers!","Radio waves reach the mountains,\nbut the lake reacts to them."])
 n='MtMortar_1F'
 trainer(n,'MARKUS',["A mountain battle, here we go!","Your partner is impressive!","A radio hum started only after\nTEAM ROCKET came to MAHOGANY."])
 n='MahoganyTown'
 add(n,'Resident','''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_ROCKET_HQ_CLEARED, MahoganyTown_ResidentAfter
    msgbox MahoganyTown_Text_ResidentBefore
    release
    end
MahoganyTown_ResidentAfter::
    msgbox MahoganyTown_Text_ResidentAfter
    release
    end
''')
 add(n,'EastGuard','''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, MahoganyTown_EastOpen
    goto_if_set FLAG_JOHTO_BADGE07_GET, MahoganyTown_RadioNews
    msgbox MahoganyTown_Text_EastBefore
    release
    end
MahoganyTown_RadioNews::
    msgbox MahoganyTown_Text_RadioNews
    release
    end
MahoganyTown_EastOpen::
    msgbox MahoganyTown_Text_EastOpen
    release
    end
''')
 texts[n]={'ResidentBefore':["PRYCE watches the trouble at\nthe LAKE OF RAGE closely.",
 "Look north before challenging\nhim at the GYM."],
 'ResidentAfter':["The radio signal has stopped.\nPRYCE has returned to his GYM."],
 'EastBefore':["Investigate the lake and earn\nPRYCE's GLACIERBADGE first."],
 'RadioNews':["GOLDENROD's RADIO TOWER called.\nTEAM ROCKET has taken it over!",
 "That same group fled KANTO.\nPlease warn GOLDENROD's staff."],
 'EastOpen':["The RADIO TOWER is safe again.\nThe road to BLACKTHORN is open."]}
 n='JohtoRoute43'
 trainer(n,'TIFFANY',["My CLEFAIRY loves this lake!","I should return home for now.","The lake was peaceful before\nthe strange radio hum started."])
 say(n,'LakeSign',["LAKE OF RAGE lies to the north.\nGYARADOS are behaving strangely."])
 n='LakeOfRage'
 add(n,'RedGyarados','''
    lock
    goto_if_set FLAG_JOHTO_RED_GYARADOS_RESOLVED, LakeOfRage_GyaradosAfter
    msgbox LakeOfRage_Text_Gyarados
    setwildbattle SPECIES_GYARADOS, 30
    special MakeScriptedWildMonShiny
    playmoncry SPECIES_GYARADOS, CRY_MODE_ENCOUNTER
    waitmoncry
    setflag FLAG_SYS_SPECIAL_WILD_BATTLE
    dowildbattle
    clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
    specialvar VAR_RESULT, GetBattleOutcome
    goto_if_eq VAR_RESULT, B_OUTCOME_WON, LakeOfRage_GyaradosClear
    goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, LakeOfRage_GyaradosClear
    release
    end
LakeOfRage_GyaradosClear::
    setflag FLAG_JOHTO_RED_GYARADOS_RESOLVED
    removeobject 1
    msgbox LakeOfRage_Text_GyaradosClear
LakeOfRage_GyaradosAfter::
    release
    end
''')
 add(n,'Lance','''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_ROCKET_HQ_CLEARED, LakeOfRage_LanceAfter
    goto_if_unset FLAG_JOHTO_RED_GYARADOS_RESOLVED, LakeOfRage_LanceBefore
    setflag FLAG_JOHTO_LANCE_INVESTIGATION_JOINED
    goto_if_set FLAG_JOHTO_RED_SCALE_RECEIVED, LakeOfRage_LanceJoined
    giveitem ITEM_RED_SCALE
    goto_if_eq VAR_RESULT, FALSE, LakeOfRage_LanceFull
    setflag FLAG_JOHTO_RED_SCALE_RECEIVED
LakeOfRage_LanceJoined::
    msgbox LakeOfRage_Text_LanceJoined
    release
    end
LakeOfRage_LanceFull::
    msgbox LakeOfRage_Text_LanceFull
    release
    end
LakeOfRage_LanceBefore::
    msgbox LakeOfRage_Text_LanceBefore
    release
    end
LakeOfRage_LanceAfter::
    msgbox LakeOfRage_Text_LanceAfter
    release
    end
''')
 texts[n]={'Gyarados':["The RED GYARADOS is enraged!\nA radio signal echoes nearby."],
 'GyaradosClear':["The lake grows quiet for now.\nLANCE waits on the south bank."],
 'LanceBefore':["LANCE: I recognize your KANTO\npartner. Help that GYARADOS.",
 "This is forced evolution.\nI will trace the radio signal."],
 'LanceJoined':["LANCE: I found a ROCKET base\nunder MAHOGANY's souvenir shop.",
 "Their KANTO operation failed.\nNow they are forcing evolution.",
 "Meet me inside the shop.\nWe will stop their transmitter."],
 'LanceFull':["Keep this RED SCALE as evidence.\nMake room and speak to me again.",
 "Our investigation can continue.\nMeet me at MAHOGANY's shop."],
 'LanceAfter':["LANCE: The transmitter is quiet.\nYou saved the lake's POKEMON.",
 "I will warn the RADIO TOWER.\nROCKET may try one last plan."]}
 n='MahoganyTown_Shop'
 add(n,'Clerk','''
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_LANCE_INVESTIGATION_JOINED, MahoganyTown_Shop_Before
    goto_if_set FLAG_JOHTO_ROCKET_HQ_CLEARED, MahoganyTown_Shop_After
    msgbox MahoganyTown_Shop_Text_Entry
    setflag FLAG_JOHTO_LANCE_MOVED_TO_HQ
    release
    warp MAP_JOHTO_ROCKET_HQ_B1F, -1, 6, 17
    waitstate
    end
MahoganyTown_Shop_Before::
    msgbox MahoganyTown_Shop_Text_Before
    release
    end
MahoganyTown_Shop_After::
    msgbox MahoganyTown_Shop_Text_After
    release
    end
''')
 add(n,'StairGuard','''
    lockall
    goto_if_set FLAG_JOHTO_LANCE_INVESTIGATION_JOINED, MahoganyTown_Shop_StairOpen
    msgbox MahoganyTown_Shop_Text_Before
    applymovement OBJ_EVENT_ID_PLAYER, MahoganyTown_Shop_StairBack
    waitmovement 0
    releaseall
    end
MahoganyTown_Shop_StairOpen::
    setflag FLAG_JOHTO_LANCE_MOVED_TO_HQ
    releaseall
    warp MAP_JOHTO_ROCKET_HQ_B1F, 0
    waitstate
    end
MahoganyTown_Shop_StairBack:
    walk_down
    step_end
''')
 texts[n]={'Before':["Only souvenirs here...\nPlease investigate the lake."],
 'Entry':["LANCE uncovered a hidden stair.\nThe ROCKET base lies below."],
 'After':["The ROCKET base is abandoned.\nMAHOGANY can be peaceful again."]}
 n='JohtoRocketHQ_B1F'
 trainer(n,'HQ_GUARD_A',["You ruined our plans in KANTO!","We still have our transmitter!","Our bosses moved the project\nhere after KANTO fell."])
 trainer(n,'HQ_GUARD_B',["The controls are ours!","I underestimated your partner!","The controls are deeper inside.\nAn executive guards the key."])
 say(n,'Lance',["An officer holds this floor.\nLANCE went to the transmitter.",
 "We cannot let them repeat what\nthey tried in KANTO."])
 n='JohtoRocketHQ_B2F'
 trainer(n,'HQ_SCIENTIST',["Radio waves force evolution!","That result cannot be correct!","The transmitter has three power\nunits on the lowest floor."])
 trainer(n,'PETREL',["GIOVANNI will return for us!","Not this trainer again!","Even if you stop this station,\nour RADIO TOWER plan will work."])
 add(n,'SecurityDoor','''
    lockall
    goto_if_defeated TRAINER_JOHTO_PETREL, JohtoRocketHQ_B2F_Open
    msgbox JohtoRocketHQ_B2F_Text_Closed
    applymovement OBJ_EVENT_ID_PLAYER, JohtoRocketHQ_B2F_Back
    waitmovement 0
    releaseall
    end
JohtoRocketHQ_B2F_Open::
    releaseall
    warp MAP_JOHTO_ROCKET_HQ_B3F, 0
    waitstate
    end
JohtoRocketHQ_B2F_Back:
    walk_down
    step_end
''')
 texts[n].update({'Closed':["An executive holds the key.\nThe transmitter room is locked."],
 'Open':["The executive's key opens the\ntransmitter room."]})
 n='JohtoRocketHQ_B3F'
 trainer(n,'ARIANA',["Our KANTO defeat means nothing!","How can one trainer stop us?","The ELECTRODE still power the\nsignal. Shut them down yourself!"])
 for k,flag,local in [('Electrode1','FLAG_JOHTO_HQ_ELECTRODE1_CLEARED',1),('Electrode2','FLAG_JOHTO_HQ_ELECTRODE2_CLEARED',2),('Electrode3','FLAG_JOHTO_HQ_ELECTRODE3_CLEARED',3)]:
  add(n,k,'''
    lock
    goto_if_set '''+flag+', '+n+'_'+k+'''After
    goto_if_defeated TRAINER_JOHTO_ARIANA, '''+n+'_'+k+'''Battle
    msgbox '''+n+'''_Text_ExecutiveFirst
    release
    end
'''+n+'_'+k+'''Battle::
    setwildbattle SPECIES_ELECTRODE, 23
    playmoncry SPECIES_ELECTRODE, CRY_MODE_ENCOUNTER
    waitmoncry
    setflag FLAG_SYS_SPECIAL_WILD_BATTLE
    dowildbattle
    clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
    specialvar VAR_RESULT, GetBattleOutcome
    goto_if_eq VAR_RESULT, B_OUTCOME_WON, '''+n+'_'+k+'''Clear
    goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, '''+n+'_'+k+'''Clear
    release
    end
'''+n+'_'+k+'''Clear::
    setflag '''+flag+'''
    removeobject '''+str(local)+'''
'''+n+'_'+k+'''After::
    release
    end
''')
 add(n,'Lance','''
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_HQ_ELECTRODE1_CLEARED, JohtoRocketHQ_B3F_NotReady
    goto_if_unset FLAG_JOHTO_HQ_ELECTRODE2_CLEARED, JohtoRocketHQ_B3F_NotReady
    goto_if_unset FLAG_JOHTO_HQ_ELECTRODE3_CLEARED, JohtoRocketHQ_B3F_NotReady
    goto_if_set FLAG_JOHTO_ROCKET_HQ_CLEARED, JohtoRocketHQ_B3F_Reward
    setflag FLAG_JOHTO_ROCKET_HQ_CLEARED
JohtoRocketHQ_B3F_Reward::
    goto_if_set FLAG_JOHTO_RED_SCALE_RECEIVED, JohtoRocketHQ_B3F_TM
    giveitem ITEM_RED_SCALE
    goto_if_eq VAR_RESULT, FALSE, JohtoRocketHQ_B3F_ScaleFull
    setflag FLAG_JOHTO_RED_SCALE_RECEIVED
JohtoRocketHQ_B3F_TM::
    goto_if_set FLAG_JOHTO_LANCE_TM24_RECEIVED, JohtoRocketHQ_B3F_After
    giveitem ITEM_TM24
    goto_if_eq VAR_RESULT, FALSE, JohtoRocketHQ_B3F_Full
    setflag FLAG_JOHTO_LANCE_TM24_RECEIVED
JohtoRocketHQ_B3F_After::
    msgbox JohtoRocketHQ_B3F_Text_After
    release
    end
JohtoRocketHQ_B3F_ScaleFull::
    msgbox JohtoRocketHQ_B3F_Text_ScaleFull
    release
    end
JohtoRocketHQ_B3F_Full::
    msgbox JohtoRocketHQ_B3F_Text_Full
    release
    end
JohtoRocketHQ_B3F_NotReady::
    msgbox JohtoRocketHQ_B3F_Text_NotReady
    release
    end
''')
 texts[n].update({'ExecutiveFirst':["The executive blocks access to\nthe transmitter's power units."],
 'NotReady':["LANCE: Free all three ELECTRODE.\nTheir power feeds the signal."],
 'After':["LANCE: The lake is safe now.\nTake THUNDERBOLT as my thanks.",
 "PRYCE is back at his GYM.\nI will alert the RADIO TOWER."],
 'ScaleFull':["Your RED SCALE is still here.\nMake room and return for it.",
 "The lake is safe, and PRYCE can\nstill test you at the GYM."],
 'Full':["The transmitter is already off.\nMake room for THUNDERBOLT.",
 "PRYCE can still test you.\nReturn for your reward later."]})
 n='MahoganyTown_Gym'
 add(n,'Pryce','''
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_BADGE06_GET, MahoganyTown_Gym_Before
    goto_if_unset FLAG_JOHTO_ROCKET_HQ_CLEARED, MahoganyTown_Gym_Before
    goto_if_defeated TRAINER_JOHTO_PRYCE, MahoganyTown_Gym_Victory
    trainerbattle_single TRAINER_JOHTO_PRYCE, MahoganyTown_Gym_Text_Intro, MahoganyTown_Gym_Text_Defeat, MahoganyTown_Gym_Victory, NO_MUSIC
    goto MahoganyTown_Gym_Victory
MahoganyTown_Gym_Victory::
    setflag FLAG_JOHTO_BADGE07_GET
    goto_if_set FLAG_JOHTO_PRYCE_TM13_RECEIVED, MahoganyTown_Gym_After
    giveitem ITEM_TM13
    goto_if_eq VAR_RESULT, FALSE, MahoganyTown_Gym_Full
    setflag FLAG_JOHTO_PRYCE_TM13_RECEIVED
MahoganyTown_Gym_After::
    msgbox MahoganyTown_Gym_Text_After
    release
    end
MahoganyTown_Gym_Full::
    msgbox MahoganyTown_Gym_Text_Full
    release
    end
MahoganyTown_Gym_Before::
    msgbox MahoganyTown_Gym_Text_Before
    release
    end
''')
 texts[n]={'Before':["PRYCE: Stop the lake's distress.\nThen I will test your resolve."],
 'Intro':["PRYCE: Life's winter taught me\npatience. Show me your strength!"],
 'Defeat':["You have endured my winter.\nYour trust in POKEMON is strong."],
 'After':["PRYCE: Take the GLACIERBADGE\nand the rare TM for ICE BEAM.",
 "TEAM ROCKET may regroup at the\nRADIO TOWER. Warn GOLDENROD."],
 'Full':["The GLACIERBADGE is yours.\nMake room for ICE BEAM.",
 "Your victory is remembered.\nCome back for the TM later."]}
 return scripts,texts

def build(s):
 out={};stats={'chapter':'Mahogany forced-evolution investigation and Johto gym seven',
  'save_layout_changed':False,'native_build_and_emulator':'NOT_RUN_BY_GENERATOR',
  'visual_limits':['Native Kanto tiles and class portraits are reused.','This is the current main-path Mt Mortar chamber, not the entire original cavern.'],
  'not_implemented':['Goldenrod Radio Tower takeover','Blackthorn/Clair/Dragon Den','Johto League','Full Mt Mortar side chambers']}
 groups=s.json('data/maps/map_groups.json');assert groups['gMapGroup_JohtoEntry'] in (OLD,OLD+NEW)
 for k,v in groups.items():
  if k not in ('group_order','gMapGroup_JohtoEntry'):assert not(set(v)&set(NEW))
 groups['gMapGroup_JohtoEntry']=OLD+NEW;out['data/maps/map_groups.json']=enc(groups)
 arrays=mahogany_geometry(s);ls=s.json('data/layouts/layouts.json')
 templates={'EcruteakCity_EastGate':('Building','GenericBuilding2','LAYOUT_ROUTE2_ENTRANCE'),
  'JohtoRoute42':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),
  'MtMortar_1F':('Building','RockTunnel','LAYOUT_ROCK_TUNNEL_1F'),
  'MahoganyTown':('General','SaffronCity','LAYOUT_SAFFRON_CITY'),
  'MahoganyTown_Shop':('Building','GenericBuilding1','LAYOUT_HOUSE5'),
  'MahoganyTown_Gym':('Building','PewterGym','LAYOUT_PEWTER_CITY_GYM'),
  'JohtoRoute43':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),
  'LakeOfRage':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY')}
 for k in [1,2,3]:templates['JohtoRocketHQ_B'+str(k)+'F']=('Building','SilphCo','LAYOUT_SILPH_CO_'+str(k)+'F')
 for n,a in arrays.items():
  primary,secondary,old=templates[n];t=next(v for v in ls['layouts'] if v.get('id')==old)
  row={'id':'LAYOUT_'+ident(n),'name':n+'_Layout','width':len(a[0]),'height':len(a),
   'border_width':2,'border_height':2,'primary_tileset':'gTileset_'+primary,'secondary_tileset':'gTileset_'+secondary,
   'blockdata_filepath':'data/layouts/'+n+'/map.bin','border_filepath':'data/layouts/'+n+'/border.bin'}
  hits=[v for v in ls['layouts'] if v.get('id')==row['id']];assert not hits or hits==[row]
  if not hits:ls['layouts'].append(row)
  out[row['blockdata_filepath']]=C.pack(a);out[row['border_filepath']]=s.read(t['border_filepath'])
 out['data/layouts/layouts.json']=enc(ls);maps={};scripts,rows=mahogany_story();tx={n:C.texts(n,d) for n,d in rows.items()}
 def temp(n,old,section,music=None):
  j=s.json('data/maps/'+old+'/map.json');j.update(id=MID[n],name=n,region_map_section=section,connections=None)
  j.pop('connections_no_include',None)
  if n in arrays:j['layout']='LAYOUT_'+ident(n)
  if music:j['music']=music
  for key in ['object_events','warp_events','coord_events','bg_events']:j[key]=[]
  maps[n]=j;return j
 def coord(x,y,script):
  return {'type':'trigger','x':x,'y':y,'elevation':3,'var':'VAR_TEMP_0','var_value':'0','script':script}
 n='EcruteakCity_EastGate';j=temp(n,'Route2_ViridianForest_NorthEntrance','MAPSEC_ECRUTEAK_CITY')
 j['warp_events']=[warp(x,10,'MAP_ECRUTEAK_CITY',6) for x in (6,7,8)]+[warp(7,1,'JohtoRoute42',0)]
 j['object_events']=[obj('POLICEMAN',9,3,n+'_Officer')];j['coord_events']=[coord(x,3,n+'_Gate') for x in (6,7,8)]
 n='JohtoRoute42';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE42','MUS_ROUTE1')
 j['connections']=[{'map':MID['MahoganyTown'],'direction':'right','offset':-5}]
 j['warp_events']=[warp(3,9,'EcruteakCity_EastGate',3,0),warp(10,6,'MtMortar_1F',0),warp(33,6,'MtMortar_1F',1)]
 j['object_events']=[obj('HIKER',22,14,n+'_Hiker'),obj('MAN',24,12,n+'_HARRISON')]
 n='MtMortar_1F';j=temp(n,'RockTunnel_1F','MAPSEC_MT_MORTAR','MUS_MT_MOON')
 j['requires_flash']=False;j['warp_events']=[warp(17,2,'JohtoRoute42',1),warp(18,37,'JohtoRoute42',2)]
 j['object_events']=[obj('HIKER',18,20,n+'_MARKUS')]
 n='MahoganyTown';j=temp(n,'SaffronCity','MAPSEC_MAHOGANY_TOWN','MUS_CINNABAR')
 j['connections']=[{'map':MID['JohtoRoute42'],'direction':'left','offset':5},{'map':MID['JohtoRoute43'],'direction':'up','offset':4}]
 j['warp_events']=[warp(7,24,'MahoganyTown_PokemonCenter_1F',1,0),warp(21,23,'MahoganyTown_Shop',1,0),warp(15,8,'MahoganyTown_Gym',1,0)]
 j['object_events']=[obj('OLD_MAN_1',12,17,n+'_Resident'),obj('POLICEMAN',26,16,n+'_EastGuard')]
 n='JohtoRoute43';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE43','MUS_ROUTE1')
 j['connections']=[{'map':MID['MahoganyTown'],'direction':'down','offset':-4},{'map':MID['LakeOfRage'],'direction':'up','offset':-8}]
 j['object_events']=[obj('WOMAN_2',15,16,n+'_TIFFANY')];j['bg_events']=[C.bg(8,5,n+'_LakeSign')]
 n='LakeOfRage';j=temp(n,'Route1','MAPSEC_LAKE_OF_RAGE','MUS_ROUTE24')
 j['connections']=[{'map':MID['JohtoRoute43'],'direction':'down','offset':8}]
 j['object_events']=[obj('RED_GYARADOS',20,17,n+'_RedGyarados',local_id='1',elevation=1,flag='FLAG_JOHTO_RED_GYARADOS_RESOLVED'),
  obj('LANCE',22,27,n+'_Lance',local_id='2',flag='FLAG_JOHTO_LANCE_MOVED_TO_HQ')]
 for suf in ['PokemonCenter_1F','PokemonCenter_2F']:
  n='MahoganyTown_'+suf
  rep=lambda t:t.replace('OLIVINE_CITY','MAHOGANY_TOWN').replace('OLIVINE','MAHOGANY').replace('OlivineCity','MahoganyTown')
  j=json.loads(rep(s.text('data/maps/OlivineCity_'+suf+'/map.json')));assert j['id']==MID[n]
  j['region_map_section']='MAPSEC_MAHOGANY_TOWN';maps[n]=j
  scripts[n]=rep(s.text('data/maps/OlivineCity_'+suf+'/scripts.inc'));tx[n]=rep(s.text('data/maps/OlivineCity_'+suf+'/text.inc'))
  if suf=='PokemonCenter_1F':
   j['object_events'][0]['local_id']='LOCALID_MAHOGANY_NURSE'
   for wp in j['warp_events'][:3]:wp['dest_warp_id']='0'
 n='MahoganyTown_Shop';j=temp(n,'SaffronCity_House','MAPSEC_MAHOGANY_TOWN','MUS_CELADON')
 j['warp_events']=[warp(x,7,'MahoganyTown',1) for x in (3,4,5)]+[warp(7,2,'JohtoRocketHQ_B1F',0)]
 j['object_events']=[obj('MAN',3,3,n+'_Clerk')]
 j['coord_events']=[coord(7,2,n+'_StairGuard')]
 n='MahoganyTown_Gym';j=temp(n,'PewterCity_Gym','MAPSEC_MAHOGANY_TOWN','MUS_GYM')
 j['warp_events']=[warp(x,14,'MahoganyTown',2) for x in (5,6,7)]
 j['object_events']=[obj('OLD_MAN_1',6,5,n+'_Pryce')]
 for k in [1,2,3]:
  n='JohtoRocketHQ_B'+str(k)+'F';j=temp(n,'SilphCo_'+str(k)+'F','MAPSEC_JOHTO_ROCKET_HQ','MUS_ROCKET_HIDEOUT')
  if k==1:
   j['warp_events']=[warp(8,20,'MahoganyTown_Shop',3),warp(9,20,'MahoganyTown_Shop',3),warp(31,2,'JohtoRocketHQ_B2F',1)]
   j['object_events']=[obj('ROCKET_M',15,8,n+'_HQ_GUARD_A'),obj('ROCKET_M',26,14,n+'_HQ_GUARD_B'),obj('POLICEMAN',9,10,n+'_Lance')]
  elif k==2:
   j['warp_events']=[warp(28,2,'JohtoRocketHQ_B3F',0),warp(30,2,'JohtoRocketHQ_B1F',2)]
   j['object_events']=[obj('SCIENTIST',8,12,n+'_HQ_SCIENTIST'),obj('ROCKET_M',24,9,n+'_PETREL')]
   j['coord_events']=[coord(28,2,n+'_SecurityDoor')]
  else:
   j['warp_events']=[warp(28,2,'JohtoRocketHQ_B2F',0)]
   j['object_events']=[obj('VOLTORB',10,12,n+'_Electrode1',local_id='1',flag='FLAG_JOHTO_HQ_ELECTRODE1_CLEARED'),
    obj('VOLTORB',16,12,n+'_Electrode2',local_id='2',flag='FLAG_JOHTO_HQ_ELECTRODE2_CLEARED'),
    obj('VOLTORB',22,12,n+'_Electrode3',local_id='3',flag='FLAG_JOHTO_HQ_ELECTRODE3_CLEARED'),
    obj('ROCKET_F',16,8,n+'_ARIANA',local_id='4'),obj('LANCE',8,8,n+'_Lance',local_id='5')]
 for n,j in maps.items():
  out['data/maps/'+n+'/map.json']=enc(j);out['data/maps/'+n+'/scripts.inc']=scripts[n].encode();out['data/maps/'+n+'/text.inc']=tx.get(n,'@ Native shared dialogue.\n').encode()
 p='data/maps/EcruteakCity/map.json';j=s.json(p);wp=warp(36,20,'EcruteakCity_EastGate',1,0)
 assert len(j['warp_events']) in (6,7)
 if len(j['warp_events'])==6:j['warp_events'].append(wp)
 else:assert j['warp_events'][6]==wp
 out[p]=enc(j);layout=next(v for v in ls['layouts'] if v.get('id')==j['layout'])
 a=V.layout_array(s,j['layout'])
 # Read the verified existing chapter's city; preserve every other cell.
 door=V.crop(V.layout_array(s,'LAYOUT_SAFFRON_CITY'),21,11,5,4)
 if MARK not in s.text('include/constants/flags_johto_story.h'):
  assert all(a[y][x] in (0x3001,0x3195,C.dense(x,y)) for y in range(17,21) for x in range(35,40))
 patched=copy.deepcopy(a);C.paste(patched,door,35,17)
 out[layout['blockdata_filepath']]=C.pack(patched)
 heals=s.json('src/data/heal_locations.json')
 v={'id':'HEAL_LOCATION_MAHOGANY_TOWN','map':MID['MahoganyTown'],'x':7,'y':25,
  'respawn_map':MID['MahoganyTown_PokemonCenter_1F'],'respawn_npc':'LOCALID_MAHOGANY_NURSE'}
 hits=[x for x in heals['heal_locations'] if x['id']==v['id']];assert not hits or hits==[v]
 if not hits:heals['heal_locations'].append(v)
 out['src/data/heal_locations.json']=enc(heals)
 shared(s,out);region(s,out);stats.update(new_maps=NEW,new_flags=FLAGS,trainer_ids={v[0]:v[-1] for v in TRAINERS})
 return out,stats

def shared(s,out):
 p='include/constants/flags_johto_story.h';t=s.text(p)
 block='\n// '+MARK+'\n'
 additions=[]
 for n,v in FLAGS.items():
  found=re.findall(r'^#define\s+'+re.escape(n)+r'\s+\(JOHTO_STORY_FLAGS_START\s*\+\s*(0x[0-9a-fA-F]+|\d+)\)\s*$',t,re.M)
  if found:assert len(found)==1 and int(found[0],0)==v,(n,'existing flag offset changed')
  else:additions.append((n,v))
 if MARK not in t:
  used={int(v,0) for v in re.findall(r'JOHTO_STORY_FLAGS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',t)}
  assert not(used&{v for _,v in additions}),('new flag collision',additions)
  block+=''.join('#define '+n+' (JOHTO_STORY_FLAGS_START + '+str(v)+')\n' for n,v in additions)
  idx=t.rfind('#endif');assert idx>=0;t=t[:idx]+block+'\n'+t[idx:]
 else:assert not additions,('incomplete Mahogany flags',additions)
 out[p]=t.encode()
 p='include/constants/opponents_johto_mahogany.h'
 h='#ifndef GUARD_OPPONENTS_JOHTO_MAHOGANY_H\n#define GUARD_OPPONENTS_JOHTO_MAHOGANY_H\n'
 for n,c,pic,gender,party,num in TRAINERS:h+='#define TRAINER_JOHTO_'+n+' (HOENN_TRAINERS_START + '+str(num)+')\n'
 out[p]=(h+'#endif\n').encode()
 for path in (s.root/'include/constants').glob('opponents*.h'):
  rel=path.relative_to(s.root).as_posix()
  if rel==p:continue
  used={int(v,0) for v in re.findall(r'HOENN_TRAINERS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',s.text(rel))}
  assert not(used&{v[-1] for v in TRAINERS}),('trainer collision',rel)
 p='include/constants/opponents.h';anchor='#include "constants/opponents_johto_olivine.h"'
 out[p]=C.once(s.text(p),anchor,anchor+'\n#include "constants/opponents_johto_mahogany.h"','Mahogany trainer include').encode()
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
  display=DISPLAY.get(n,n)
  assert len(display)<=12,'native trainer name overflow'
  trainers+='    [TRAINER_JOHTO_'+n+'] = {\n        .trainerClass = TRAINER_CLASS_'+c+',\n        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_'+gender+(' | F_TRAINER_FEMALE' if gender=='FEMALE' else '')+',\n        .trainerPic = TRAINER_PIC_'+pic+',\n        .trainerName = _("'+display+'"),\n        .items = {},\n        .doubleBattle = FALSE,\n        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,\n        .party = '+('NO_ITEM_CUSTOM_MOVES' if custom else 'NO_ITEM_DEFAULT_MOVES')+'('+sym+'),\n    },\n'
 out['src/data/trainer_parties_johto_mahogany.h']=parties.encode();out['src/data/trainers_johto_mahogany.h']=trainers.encode()
 for p,a,inc in [('src/data/trainers.h','#include "trainers_johto_olivine.h"','#include "trainers_johto_mahogany.h"'),('src/data/trainer_parties.h','#include "trainer_parties_johto_olivine.h"','#include "trainer_parties_johto_mahogany.h"')]:
  out[p]=C.once(s.text(p),a,a+'\n'+inc,'Mahogany trainer data').encode()
 p='data/event_scripts.s';t=s.text(p);block='@ '+MARK+'\n'+''.join('    .include "data/maps/'+n+'/'+f+'"\n' for n in NEW for f in ['scripts.inc','text.inc'])
 if MARK not in t:assert not any('data/maps/'+n+'/' in t for n in NEW);t=t.rstrip()+'\n\n'+block
 else:assert block in t
 out[p]=t.encode()
 p='tools/johto/build_olivine_cianwood.py';t=s.text(p)
 guard=' # MAHOGANY_EXTENSION_GUARD\n if any(n not in OLD + NEW for n in s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]):\n  raise RuntimeError("Mahogany extension exists; use build_mahogany.py")\n'
 if '# MAHOGANY_EXTENSION_GUARD' not in t:
  t,n=re.subn(r'(?m)^def build\(s\):\n',lambda m:m.group(0)+guard,t);assert n==1
 else:assert guard in t
 out[p]=t.encode()
 p='src/data/wild_encounters.json';j=s.json(p)
 gs=[g for g in j['wild_encounter_groups'] if g['label']=='gWildMonHeaders'];assert len(gs)==1 and gs[0]['for_maps']
 for n,(day,night,levels) in WILD.items():
  row={'map':MID[n],'base_label':'s'+n}
  for key,sp in [('land_mons',day),('land_mons_morning',day),('land_mons_night',night)]:
   row[key]={'encounter_rate':10,'mons':[{'min_level':lv,'max_level':lv,'species':'SPECIES_'+name} for name,lv in zip(sp,levels)]}
  if n in WATER:
   species,wl=WATER[n]
   row['water_mons']={'encounter_rate':4,'mons':[{'min_level':lv,'max_level':lv,'species':'SPECIES_'+sp} for sp,lv in zip(species,wl)]}
  out['tools/johto/'+n.lower()+'_wild.json']=enc(row)
  hits=[x for x in gs[0]['encounters'] if x['map']==row['map'] or x['base_label']==row['base_label']]
  assert not hits or hits==[row]
  if not hits:gs[0]['encounters'].append(row)
 out[p]=enc(j)
 for n,(species,levels) in WATER.items():
  if n in WILD:continue
  row={'map':MID[n],'base_label':'s'+n,'water_mons':{'encounter_rate':4,'mons':[{'min_level':lv,'max_level':lv,'species':'SPECIES_'+sp} for sp,lv in zip(species,levels)]}}
  out['tools/johto/'+n.lower()+'_wild.json']=enc(row)
  hits=[v for v in gs[0]['encounters'] if v['map']==row['map'] or v['base_label']==row['base_label']]
  assert not hits or hits==[row]
  if not hits:gs[0]['encounters'].append(row)
 out[p]=enc(j)

def region(s,out):
 p='src/data/region_map/region_map_sections.json';j=s.json(p);original=s.json(p)['map_sections']
 specs=[('JOHTO_ROUTE42','ROUTE 42',6,1,7,1),('MT_MORTAR','MT. MORTAR',9,0,1,1),
  ('MAHOGANY_TOWN','MAHOGANY TOWN',13,1,1,1),('JOHTO_ROUTE43','ROUTE 43',13,0,1,1),
  ('LAKE_OF_RAGE','LAKE OF RAGE',14,0,1,1),('JOHTO_ROCKET_HQ','ROCKET HIDEOUT',14,2,1,1)]
 for key,label,x,y,w,h in specs:
  row={'id':'MAPSEC_'+key,'name':label,'x':x,'y':y,'width':w,'height':h}
  hits=[v for v in j['map_sections'] if v.get('id')==row['id']];assert not hits or hits==[row]
  if not hits:j['map_sections'].append(row)
 assert [v.get('id') for v in j['map_sections'][:len(original)]]==[v.get('id') for v in original]
 assert len(j['map_sections'])<256,'native u8 map-section paths need a separate widening before this append'
 out[p]=enc(j)
 for p in ['src/region_map.c','src/pokemon_summary_screen.c']:
  t=s.text(p);pat=r'(MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP[\s\S]{0,140}?<=\s*)MAPSEC_CIANWOOD_CITY'
  if re.search(pat,t):t,n=re.subn(pat,lambda m:m.group(1)+'MAPSEC_JOHTO_ROCKET_HQ',t);assert n==1
  else:assert re.search(pat.replace('MAPSEC_CIANWOOD_CITY','MAPSEC_JOHTO_ROCKET_HQ'),t)
  out[p]=t.encode()
 p='src/region_map.c';t=out[p].decode()
 if '// MAHOGANY_MAP_GRID_V1' not in t:
  pat=r'(?m)^([ \t]*)// OLIVINE_CIANWOOD_MAP_GRID_V1'
  lines=['// MAHOGANY_MAP_GRID_V1','if (layer != LAYER_MAP)','    return MAPSEC_NONE;',
   'if (x >= 6 && x <= 12 && y == 1)','    return MAPSEC_JOHTO_ROUTE42;',
   'if (x == 9 && y == 0)','    return MAPSEC_MT_MORTAR;',
   'if (x == 13 && y == 1)','    return MAPSEC_MAHOGANY_TOWN;',
   'if (x == 13 && y == 0)','    return MAPSEC_JOHTO_ROUTE43;',
   'if (x == 14 && y == 0)','    return MAPSEC_LAKE_OF_RAGE;',
   'if (x == 14 && y == 2)','    return MAPSEC_JOHTO_ROCKET_HQ;','// OLIVINE_CIANWOOD_MAP_GRID_V1']
  t,n=re.subn(pat,lambda m:'\n'.join(m.group(1)+v for v in lines),t);assert n==1
 # Extend the verified original Fly8 lookup without replacing its immutable table.
 assert '// JOHTO_FLY_DESTINATIONS_V1' in t,'apply and validate Johto Fly support first'
 block='''// MAHOGANY_FLY_DESTINATION_V1
static const struct JohtoFlyDestination sMahoganyFlyDestination = {
    MAPSEC_MAHOGANY_TOWN, FLAG_JOHTO_LANCE_INVESTIGATION_JOINED,
    FLAG_JOHTO_BADGE07_GET, {MAP(MAP_MAHOGANY_TOWN), HEAL_LOCATION_MAHOGANY_TOWN}, 7, 25
};

'''
 anchor='static const struct JohtoFlyDestination *GetJohtoFlyDestination(u16 mapsec)'
 if '// MAHOGANY_FLY_DESTINATION_V1' not in t:t=C.once(t,anchor,block+anchor,'Mahogany Fly constant')
 else:assert block in t
 branch='''    u32 i;
    if (mapsec == MAPSEC_MAHOGANY_TOWN)
        return &sMahoganyFlyDestination;
'''
 t=C.once(t,'    u32 i;\n    for (i = 0; i < NELEMS(sJohtoFlyDestinations); i++)',branch+'    for (i = 0; i < NELEMS(sJohtoFlyDestinations); i++)','Mahogany Fly lookup')
 out[p]=t.encode()
 p='graphics/region_map/johto_entry.bin';a=list(struct.unpack('<600H',s.read(p)))
 for _,_,x,y,w,h in specs:
  for ry in range(y,y+h):
   for rx in range(x,x+w):
    assert 0<=rx+4<30 and 0<=ry+4<16
    a[(ry+4)*30+rx+4]=0x1001 if w==h==1 else 0x100a
 out[p]=struct.pack('<600H',*a)
 extra=[('Route42','johtoRoute42','MAP_JOHTO_ROUTE42'),('Route43','johtoRoute43','MAP_JOHTO_ROUTE43'),
  ('MtMortar','johtoMtMortar','MAP_MT_MORTAR_1F'),('LakeOfRage','johtoLakeOfRage','MAP_LAKE_OF_RAGE')]
 p='src/wild_pokemon_area.c';t=s.text(p)
 if 'bool8 johtoRoute42;' not in t:
  t,n=re.subn(r'(bool8\s+johtoRoute41\s*;)',lambda m:m.group(1)+''.join('\n    bool8 '+f+';' for _,f,_ in extra),t);assert n==1
 if 'MAP_GROUP(MAP_JOHTO_ROUTE42)' not in t:
  pat=r'(?s)(if\s*\(header->mapGroup\s*==\s*MAP_GROUP\(MAP_JOHTO_ROUTE41\)\s*&&\s*header->mapNum\s*==\s*MAP_NUM\(MAP_JOHTO_ROUTE41\)\s*\)\s*\{\s*habitats->johtoRoute41\s*=\s*TRUE;\s*continue;\s*\})'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n            '+m.group(1).replace('MAP_JOHTO_ROUTE41',mn).replace('johtoRoute41',f) for _,f,mn in extra),t);assert n==1
 if 'habitats.johtoRoute42 || habitats.johtoRoute43' not in t:
  t,n=re.subn(r'(if\s*\([^\n]*habitats\.johtoRoute29[^\n]*habitats\.johtoRoute41)\)',lambda m:m.group(1)+' || '+' || '.join('habitats.'+f for _,f,_ in extra)+')',t);assert n==1
 if 'GetJohtoRoute42AreaMarkerSubsprite(areaCount++, subsprites);' not in t:
  pat=r'(if\s*\(habitats\.johtoRoute41\)\s*GetJohtoRoute41AreaMarkerSubsprite\(areaCount\+\+,\s*subsprites\);)'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n        if (habitats.'+f+')\n            GetJohto'+key+'AreaMarkerSubsprite(areaCount++, subsprites);' for key,f,_ in extra),t);assert n==1
 out[p]=t.encode()
 p='include/pokedex_area_markers.h';t=s.text(p)
 if 'GetJohtoRoute42AreaMarkerSubsprite' not in t:
  t,n=re.subn(r'(void GetJohtoRoute41AreaMarkerSubsprite\([^;]*;)',lambda m:m.group(1)+''.join('\nvoid GetJohto'+key+'AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);' for key,_,_ in extra),t);assert n==1
 out[p]=t.encode()
 p='src/pokedex_area_markers.c';t=s.text(p)
 for key,shape,x,y in [('Route42','SmallHorizontal',54,7),('Route43','Circular',74,1),('MtMortar','Circular',54,1),('LakeOfRage','Circular',80,1)]:
  name='GetJohto'+key+'AreaMarkerSubsprite'
  body='void '+name+'(s32 i, struct Subsprite *subsprites)\n{\n    if (subsprites == NULL)\n        return;\n    subsprites[i] = sSubsprite_'+shape+';\n    subsprites[i].x = '+str(x)+' + (HOENN_AREA_MAP_LEFT * 8 - 104);\n    subsprites[i].y = '+str(y)+';\n}'
  if re.search(r'void\s+'+name+r'\(',t):t=C.replace_function(t,name,body,'Mahogany habitat marker')
  else:t=t.rstrip()+'\n\n'+body+'\n'
 out[p]=t.encode()
 p='src/pokedex_screen.c';t=s.text(p)
 labels=[('Mah','MAHO'),('Rage','RAGE'),('Mortar','MT'),('R42','42'),('R43','43'),('HQ','HQ')]
 if 'sText_JohtoMah[]' not in t:
  anchor='static const u8 sText_JohtoCian[] = _("CIAN");\n'
  t=C.once(t,anchor,anchor+''.join('static const u8 sText_Johto'+k+'[] = _("'+v+'");\n' for k,v in labels),'Mahogany habitat labels')
 # Preserve all already verified western cells; append new diagram cells only.
 name='DexScreen_DrawJohtoEntryArea';m=re.search(r'static void '+name+r'\([^{}]*\)\s*\{',t);assert m
 start=m.start();depth=1;i=m.end()
 while depth:
  depth+=(t[i]=='{')-(t[i]=='}');i+=1
 old=t[start:i]
 if '// MAHOGANY_DEX_DIAGRAM_V1' not in old:
  additions='    // MAHOGANY_DEX_DIAGRAM_V1\n'
  for _,_,x,y,w,h in specs:
   x,y,w,h=x*5+9,y*6+1,max(4,(w-1)*5+4),max(4,(h-1)*6+4)
   assert 0<=x and x+w<=122 and 0<=y and y+h<=68
   additions+='    FillWindowPixelRect(windowId, PIXEL_FILL(3), '+', '.join(map(str,[x,y,w,h]))+');\n'
   additions+='    FillWindowPixelRect(windowId, PIXEL_FILL(5), '+', '.join(map(str,[x+1,y+1,max(1,w-2),max(1,h-2)]))+');\n'
  for key,x,y in [('Mah',75,9),('Rage',82,0),('Mortar',56,0),('R42',57,9),('R43',75,0),('HQ',80,15)]:
   additions+='    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_Johto'+key+', '+str(x)+', '+str(y)+', 0);\n'
  t=t[:start]+old[:-1]+additions+'}'+t[i:]
 out[p]=t.encode()

def validate(s,out,stats):
 final=Source(s.root,dict(s.overlay,**out));ls={v['id']:v for v in final.json('data/layouts/layouts.json')['layouts'] if v.get('id')}
 maps={n:final.json('data/maps/'+n+'/map.json') for n in NEW}
 defs=final.text('include/constants/metatile_behaviors.h')
 values={n:int(v,0) for n,v in re.findall(r'^#define\s+(MB_\w+)\s+(0x[0-9A-Fa-f]+|\d+)\b',defs,re.M)}
 warp_b={v for n,v in values.items() if re.search(r'WARP|DOOR|LADDER|ESCALATOR',n)}
 water_b={values[n] for n in ['MB_POND_WATER','MB_DEEP_WATER','MB_OCEAN_WATER']}
 num=int(re.search(r'^#define\s+NUM_METATILES_IN_PRIMARY\s+(\d+)\b',final.text('include/fieldmap.h'),re.M).group(1));assert num==640
 def behavior(l,t):
  t&=0x3ff;kind='primary' if t<num else 'secondary';label=l[kind+'_tileset'].removeprefix('gTileset_')
  assert not label.startswith('Em'),'this chapter must retain native Kanto tiles'
  folder=re.sub(r'([A-Za-z])(\d)',r'\1_\2',re.sub(r'([a-z0-9])([A-Z])',r'\1_\2',label)).lower()
  b=final.read('data/tilesets/'+kind+'/'+folder+'/metatile_attributes.bin');i=t if kind=='primary' else t-num
  assert (i+1)*4<=len(b),(label,t,'metatile attribute bounds')
  return struct.unpack_from('<I',b,i*4)[0]&0x1ff
 starts={'EcruteakCity_EastGate':(7,10),'JohtoRoute42':(3,10),'MtMortar_1F':(17,3),
  'MahoganyTown':(0,16),'MahoganyTown_PokemonCenter_1F':(7,7),'MahoganyTown_Shop':(4,7),
  'MahoganyTown_Gym':(6,13),'JohtoRoute43':(11,31),'LakeOfRage':(19,35),
  'JohtoRocketHQ_B1F':(6,17),'JohtoRocketHQ_B2F':(29,3),'JohtoRocketHQ_B3F':(29,3)}
 checks=[];behavior_maps=dict(maps);behavior_maps['EcruteakCity']=final.json('data/maps/EcruteakCity/map.json')
 checked=0
 for n,m in behavior_maps.items():
  l=ls[m['layout']];w,h=l['width'],l['height'];raw=final.read(l['blockdata_filepath']);assert len(raw)==w*h*2
  assert (w+15)*(h+14)<=0x2800,(n,'field map buffer exceeded')
  a=struct.unpack('<'+'H'*(w*h),raw)
  for wp in m['warp_events']:
   x,y=wp['x'],wp['y'];assert 0<=x<w and 0<=y<h,(n,'warp bounds',wp)
   b=behavior(l,a[y*w+x])
   flank=b==values['MB_NORMAL'] and any(v['dest_map']==wp['dest_map'] and v['dest_warp_id']==wp['dest_warp_id'] and v['y']==y and abs(v['x']-x)==1 and behavior(l,a[y*w+v['x']]) in warp_b for v in m['warp_events'])
   assert b in warp_b or flank,(n,wp,hex(a[y*w+x]),hex(b),'warp lacks native behavior')
   dst_name=next((v for v in NEW if MID[v]==wp['dest_map']),None)
   if dst_name is None:
    assert wp['dest_map']=='MAP_ECRUTEAK_CITY'
    dst=behavior_maps['EcruteakCity']
   else:dst=maps[dst_name]
   di=int(wp['dest_warp_id']);assert 0<=di<len(dst['warp_events']),(n,'invalid destination warp ID',wp)
   checked+=1
  if n not in maps:continue
  def walk(x,y):
   if not(0<=x<w and 0<=y<h):return False
   t=a[y*w+x]
   return (t>>10)&3==0 and ((t>>12)!=1 or behavior(l,t) in water_b)
  start=starts.get(n)
  if start is None:start=next((wp['x'],wp['y']+1) for wp in m['warp_events'] if walk(wp['x'],wp['y']+1))
  assert walk(*start),(n,'start blocked',start,hex(a[start[1]*w+start[0]]))
  # Match native IsElevationMismatchAt/ObjectEventUpdateElevation:
  # elevation0 allows a change; elevation15 retains the previous elevation.
  # Outdoor water additionally admits the native Surf/dismount transition.
  initial_elevation=a[start[1]*w+start[0]]>>12
  if initial_elevation==15:initial_elevation=3
  q=deque([(start[0],start[1],initial_elevation)])
  states=set(q);seen={start}
  while q:
   x,y,current_elevation=q.popleft()
   for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if not walk(xx,yy):continue
    raw=a[yy*w+xx];target_elevation=raw>>12
    water_transition=(behavior(l,raw) in water_b or behavior(l,a[y*w+x]) in water_b) and {current_elevation,target_elevation}<={0,1,3}
    if current_elevation!=0 and target_elevation not in (0,15,current_elevation) and not water_transition:continue
    next_elevation=current_elevation if target_elevation==15 else target_elevation
    state=(xx,yy,next_elevation)
    if state not in states:states.add(state);seen.add((xx,yy));q.append(state)
  outside=n in ['JohtoRoute42','MahoganyTown']
  for wp in m['warp_events']:
   z=(wp['x'],wp['y']+1) if outside else (wp['x'],wp['y'])
   assert z in seen,(n,'unreachable native warp',wp,z)
  for o in m['object_events']:
   x,y=o['x'],o['y'];gfx=o['graphics_id'];assert 0<=x<w and 0<=y<h
   if gfx=='OBJ_EVENT_GFX_NURSE':assert (x,y+2) in seen;continue
   if gfx=='OBJ_EVENT_GFX_CLERK':continue
   assert walk(x,y),(n,'NPC on blocked tile',o,hex(a[y*w+x]))
   assert any(z in seen for z in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),(n,'NPC cannot be faced',o)
  for co in m['coord_events']:assert (co['x'],co['y']) in seen,(n,'unreachable coordinate event',co)
  if n=='JohtoRoute42':assert all((47,y) in seen for y in range(10,14))
  if n=='MahoganyTown':assert all((0,y) in seen for y in range(15,19)) and all((x,0) in seen for x in range(14,18))
  if n=='JohtoRoute43':assert all((x,y) in seen for x in range(10,14) for y in (0,31))
  if n=='LakeOfRage':
   assert all((x,35) in seen for x in range(18,22))
   assert all(behavior(l,a[17*w+x]) in water_b and (a[17*w+x]>>10)&3==0 for x in (19,20,21)),'Gyarados must be approachable while Surfing'
  checks.append({'map':n,'reachable_tiles':len(seen),'buffer_metatiles':(w+15)*(h+14),'native_warps':True})
 before=s.json('data/maps/map_groups.json');after=final.json('data/maps/map_groups.json')
 assert after['gMapGroup_JohtoEntry'][:len(OLD)]==OLD
 assert all(after[k]==v for k,v in before.items() if k!='gMapGroup_JohtoEntry')
 original_layouts=s.json('data/layouts/layouts.json')['layouts'];assert final.json('data/layouts/layouts.json')['layouts'][:len(original_layouts)]==original_layouts
 old=s.json('data/maps/EcruteakCity/map.json');new=final.json('data/maps/EcruteakCity/map.json')
 assert old['warp_events'][:6]==new['warp_events'][:6] and old['connections']==new['connections']
 assert not any(p in out for p in ['include/global.h','include/pokemon.h','src/save.c','src/load_save.c'])
 assert 'def_special MakeScriptedWildMonShiny' in s.text('data/specials.inc'),'native shiny creation helper missing'
 assert 'CreateMon(&gEnemyParty[0]' in s.text('src/field_specials.c'),'native shiny helper must use legal creation'
 cmds=set(re.findall(r'(?m)^\s*\.macro\s+(\w+)',s.text('asm/macros/event.inc')+'\n'+s.text('asm/macros/map.inc')))
 cmds.update(re.findall(r'(?m)^\s*create_movement_action\s+(\w+)',s.text('asm/macros/movement.inc')))
 for p,b in out.items():
  if p.endswith('scripts.inc'):
   t=b.decode();assert not re.search(r'checktrainerflag[^\n]*\n\s*goto_if_eq\s+VAR_RESULT',t)
   for line in t.splitlines():
    v=line.strip()
    if v and not v.startswith(('@','.','#')) and not v.endswith(':'):assert v.split()[0] in cmds,(p,'unknown script command',v)
 headers='\n'.join(final.text('include/constants/'+n) for n in ['species.h','items.h','moves.h','songs.h','event_objects.h','event_object_movement.h','global.h','trainers.h'])+'\n'+s.text('include/battle.h')
 refs=set()
 for p,b in out.items():
  if p.endswith(('.h','.c','.json','scripts.inc')):
   try:refs.update(re.findall(r'\b(?:SPECIES|ITEM|MOVE|MUS|OBJ_EVENT_GFX|TRAINER_CLASS|TRAINER_PIC|TRAINER_ENCOUNTER_MUSIC)_[A-Z0-9_]+',b.decode()))
   except UnicodeDecodeError:pass
 missing=[v for v in refs if not re.search(r'\b'+re.escape(v)+r'\b',headers)];assert not missing,('unknown native constants',missing)
 gym=out['data/maps/MahoganyTown_Gym/scripts.inc'].decode()
 for text in ['MahoganyTown_Gym_Victory, NO_MUSIC','goto MahoganyTown_Gym_Victory','setflag FLAG_JOHTO_BADGE07_GET','giveitem ITEM_TM13','goto_if_eq VAR_RESULT, FALSE, MahoganyTown_Gym_Full']:assert text in gym,('missing explicit native victory/retry path',text)
 for n in set(WILD)|set(WATER):
  row=json.loads(out['tools/johto/'+n.lower()+'_wild.json'])
  if n in WILD:assert all(len(row[k]['mons'])==12 for k in ['land_mons','land_mons_morning','land_mons_night'])
  if n in WATER:assert len(row['water_mons']['mons'])==5
 stats.update(static_checks=checks,native_warp_behaviors_checked=checked,map_sections_max=len(final.json('src/data/region_map/region_map_sections.json')['map_sections'])-1,fly_destinations_total=9)
 return stats
def apply(root,mutate=False):
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 s=Source(root);out,stats=build(s);validate(s,out,stats)
 repeat,_=build(Source(root,dict(s.overlay,**out)));assert repeat==out,'generator output is not idempotent'
 owned=[p for p in out if any(p.startswith('data/maps/'+n+'/') or p.startswith('data/layouts/'+n+'/') for n in NEW)]
 owned+=['include/constants/opponents_johto_mahogany.h','src/data/trainers_johto_mahogany.h','src/data/trainer_parties_johto_mahogany.h']
 owned+=['tools/johto/'+n.lower()+'_wild.json' for n in set(WILD)|set(WATER)]
 for p in owned:
  if s.exists(p):assert s.read(p)==out[p],('owned artifact differs',p)
 changed={p:b for p,b in out.items() if not s.exists(p) or s.read(p)!=b}
 print(json.dumps({'apply':mutate,'files':sorted(changed),'validation':stats},indent=2))
 if not mutate or not changed:return
 for p,b in s.used.items():assert (root/p).read_bytes()==b,('concurrent source edit',p)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=root/'outputs/johto-mahogany-v1'/stamp;dest.mkdir(parents=True,exist_ok=False);manifest={'time':stamp,'validation':stats,'files':{}}
 for p,b in changed.items():
  target=root/p;old=target.read_bytes() if target.exists() else None;manifest['files'][p]={'before':sha(old) if old is not None else None,'after':sha(b)}
  if old is not None:
   backup=dest/'before'/p;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(old)
 (dest/'manifest.json').write_bytes(enc(manifest))
 for p,b in changed.items():
  target=root/p;target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.mahogany.tmp');assert not tmp.exists();tmp.write_bytes(b);tmp.replace(target)
 print('APPLIED',dest/'manifest.json')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root).resolve(),a.apply)
