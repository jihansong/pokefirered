#!/usr/bin/env python3
"""Append the Azalea research/rescue chapter after Violet. Dry run by default."""
import argparse,copy,datetime,json,re,struct,subprocess,sys
from collections import deque
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_cherrygrove as C
import build_violet as V
Source,enc,sha=C.Source,C.enc,C.sha
OLD=V.OLD+V.NEW
NEW=['JohtoRoute32','JohtoUnionCave_1F','JohtoRoute33','AzaleaTown','AzaleaTown_PokemonCenter_1F','AzaleaTown_PokemonCenter_2F','AzaleaTown_Mart','AzaleaTown_KurtsHouse','AzaleaTown_Gym','SlowpokeWell_1F']
IDS=['JOHTO_ROUTE32','JOHTO_UNION_CAVE_1F','JOHTO_ROUTE33','AZALEA_TOWN','AZALEA_TOWN_POKEMON_CENTER_1F','AZALEA_TOWN_POKEMON_CENTER_2F','AZALEA_TOWN_MART','AZALEA_TOWN_KURTS_HOUSE','AZALEA_TOWN_GYM','SLOWPOKE_WELL_1F']
MID=dict(zip(NEW,['MAP_'+n for n in IDS]));MARK='JOHTO_AZALEA_CHAPTER_V1'
FLAGS={'FLAG_JOHTO_KURT_RESCUE_REQUESTED':8,'FLAG_JOHTO_SLOWPOKE_WELL_CLEARED':9,'FLAG_JOHTO_KURT_REPORT_DELIVERED':10,'FLAG_JOHTO_GOT_TM06_FROM_BUGSY':11,'FLAG_JOHTO_GOT_NET_BALLS_FROM_KURT':13,'FLAG_JOHTO_BADGE02_GET':17}
TRAINERS=[
 ('RUSSELL','YOUNGSTER','YOUNGSTER',[('RATTATA',10),('ZUBAT',10)],791),
 ('ANTHONY','HIKER','HIKER',[('GEODUDE',12),('MACHOP',12)],792),
 ('WELL_GRUNT_A','TEAM_ROCKET','ROCKET_GRUNT_M',[('RATTATA',14),('RATTATA',14)],793),
 ('WELL_GRUNT_B','TEAM_ROCKET','ROCKET_GRUNT_M',[('ZUBAT',15),('EKANS',15)],794),
 ('WELL_COMMANDER','TEAM_ROCKET','ROCKET_GRUNT_M',[('KOFFING',17)],795),
 ('AL','BUG_CATCHER','BUG_CATCHER',[('CATERPIE',14),('WEEDLE',14)],796),
 ('BENNY','BUG_CATCHER','BUG_CATCHER',[('WEEDLE',14),('KAKUNA',15),('BEEDRILL',15)],797),
 ('BUGSY','LEADER','BUG_CATCHER',[('METAPOD',16),('KAKUNA',16),('SCYTHER',18)],798)]
WILD={
 'JohtoRoute32':(['BELLSPROUT','MAREEP','RATTATA','HOPPIP','BELLSPROUT','MAREEP','EKANS','HOPPIP','RATTATA','EKANS','MAREEP','HOPPIP'],
 ['WOOPER','RATTATA','ZUBAT','BELLSPROUT','WOOPER','RATTATA','EKANS','BELLSPROUT','ZUBAT','EKANS','WOOPER','ZUBAT'],[6,6,6,6,7,7,7,7,8,8,8,9]),
 'JohtoUnionCave_1F':(['GEODUDE','ZUBAT','GEODUDE','SANDSHREW','ZUBAT','GEODUDE','SANDSHREW','ZUBAT','ONIX','GEODUDE','ONIX','ONIX'],None,[6,6,7,7,7,8,8,8,8,9,9,10]),
 'JohtoRoute33':(['RATTATA','SPEAROW','EKANS','HOPPIP','RATTATA','SPEAROW','EKANS','HOPPIP','SPEAROW','HOPPIP','EKANS','HOPPIP'],
 ['RATTATA','ZUBAT','EKANS','WOOPER','RATTATA','ZUBAT','EKANS','WOOPER','ZUBAT','WOOPER','EKANS','WOOPER'],[6,6,6,6,7,7,7,7,8,8,8,8]),
 'SlowpokeWell_1F':(['ZUBAT','ZUBAT','SLOWPOKE','ZUBAT','ZUBAT','SLOWPOKE','ZUBAT','SLOWPOKE','ZUBAT','SLOWPOKE','SLOWPOKE','SLOWPOKE'],None,[5,5,5,6,6,6,7,7,7,7,8,8])}
def ident(n):return IDS[NEW.index(n)]
def warp(x,y,dst,idx,elevation=3):return {'x':x,'y':y,'elevation':elevation,'dest_map':MID.get(dst,dst),'dest_warp_id':str(idx)}
def obj(gfx,x,y,script,**kw):return C.obj(gfx,x,y,script,**kw)
def cave_room(w,h):
 a=[[0x3281]*w for _ in range(h)]
 for x in range(w):a[0][x]=0x0691;a[1][x]=0x0699;a[h-1][x]=0x0689
 for y in range(h):a[y][0]=0x0690;a[y][w-1]=0x0692
 a[0][0]=0x0688;a[0][w-1]=0x068a;a[1][0]=0x0698;a[1][w-1]=0x069a
 return a
def geometry(s):
 vir=V.layout_array(s,'LAYOUT_VIRIDIAN_CITY');pew=V.layout_array(s,'LAYOUT_PEWTER_CITY')
 r4=V.layout_array(s,'LAYOUT_ROUTE4');mt=V.layout_array(s,'LAYOUT_MT_MOON_1F')
 a=[[0x3001]*24 for _ in range(64)]
 C.fill(a,0,0,24,8,C.dense);C.fill(a,0,0,3,64,C.dense);C.fill(a,21,0,24,64,C.dense);C.fill(a,0,62,24,64,C.dense)
 C.fill(a,8,0,11,18,0x3001);C.fill(a,7,8,13,60,0x3001)
 C.fill(a,3,14,8,24,C.grass);C.fill(a,14,29,20,41,C.grass);C.fill(a,3,43,8,54,C.grass)
 C.paste(a,V.crop(vir,11,26,6,6),14,10);C.paste(a,V.crop(vir,11,26,6,6),14,45)
 C.paste(a,V.crop(r4,18,3,3,4),10,55)
 for x,y in [(12,10),(12,53)]:a[y][x]=0x0403
 b=copy.deepcopy(mt)
 for x,y in [(5,6),(19,14),(31,16)]:b[y][x]=0x3281
 # Retain the native cave walls and two distinct exits.
 C.paste(b,V.crop(mt,17,37,3,2),40,35)
 c=[[0x3001]*36 for _ in range(20)]
 C.fill(c,0,0,36,3,C.dense);C.fill(c,0,17,36,20,C.dense);C.fill(c,33,0,36,20,C.dense)
 C.fill(c,0,11,30,15,0x3001);C.fill(c,24,6,30,14,0x3001)
 C.fill(c,7,4,18,9,C.grass);C.fill(c,20,15,31,17,C.grass)
 C.paste(c,V.crop(r4,18,3,3,4),25,3);c[9][24]=0x0403
 d=[[0x3001]*40 for _ in range(28)]
 for box in [(0,0,40,3),(0,0,2,28),(0,26,40,28),(38,0,40,11),(38,15,40,28)]:C.fill(d,*box,C.dense)
 C.fill(d,3,11,40,15,0x3195);C.fill(d,17,4,22,26,0x3195)
 C.fill(d,4,18,14,25,0x3195);C.fill(d,26,18,35,25,0x3195)
 C.paste(d,V.crop(vir,24,22,5,5),5,18)
 C.paste(d,V.crop(vir,34,16,4,4),28,19)
 C.paste(d,V.crop(vir,24,8,5,4),6,5)
 C.paste(d,V.crop(pew,12,12,7,5),18,5)
 C.paste(d,V.crop(r4,18,3,3,4),31,4)
 for x,y in [(11,22),(33,22),(12,8),(25,9),(30,7)]:d[y][x]=0x0403
 for x,y in [(14,18),(15,18),(14,19),(15,19),(28,15),(29,15)]:d[y][x]=0x3004
 well=cave_room(24,24)
 # Three rock pillars separate the guards without trapping any corridor.
 for x,y in [(5,6),(15,6),(8,13)]:
  C.paste(well,V.crop(mt,27,17,3,6),x,y)
 C.paste(well,V.crop(mt,17,37,3,2),10,21)
 return {'JohtoRoute32':a,'JohtoUnionCave_1F':b,'JohtoRoute33':c,'AzaleaTown':d,'SlowpokeWell_1F':well}


def events():
 scripts={n:n+'_MapScripts::\n    .byte 0\n' for n in NEW};tx={}
 def say(n,k,p):scripts[n]+='\n'+C.npc_script(n,k);tx.setdefault(n,{})[k]=p
 n='JohtoRoute32'
 scripts[n]+=r'''
JohtoRoute32_CheckBadge::
    goto_if_set FLAG_JOHTO_BADGE01_GET, JohtoRoute32_ClearPath
    lockall
    msgbox JohtoRoute32_Text_BadgeNeeded
    applymovement LOCALID_PLAYER, JohtoRoute32_MoveBack
    waitmovement 0
    releaseall
    end
JohtoRoute32_ClearPath::
    setvar VAR_TEMP_0, 1
    end
JohtoRoute32_MoveBack:
    walk_up
    step_end
JohtoRoute32_Russell::
    trainerbattle_single TRAINER_JOHTO_RUSSELL, JohtoRoute32_Text_Intro, JohtoRoute32_Text_Defeat
    msgbox JohtoRoute32_Text_After, MSGBOX_AUTOCLOSE
    end
'''
 tx[n]={'BadgeNeeded':['FALKNER is waiting in VIOLET.\nEarn his badge, then head south.'],
 'Intro':['Let us compare the POKEMON\nwe found along this route!'],'Defeat':['Your research paid off!'],
 'After':['The cave leads toward AZALEA.\nKURT knows the town well.']}
 say(n,'RouteSign',['ROUTE 32\nNorth: VIOLET CITY'])
 say(n,'CaveSign',['UNION CAVE\nSouth passage: ROUTE 33'])
 say(n,'Researcher',['ELM received your first report.\nThe next concern is in AZALEA.',
                     'KURT has seen strangers near\nthe SLOWPOKE WELL.'])
 n='JohtoUnionCave_1F'
 scripts[n]+=r'''
JohtoUnionCave_1F_Anthony::
    trainerbattle_single TRAINER_JOHTO_ANTHONY, JohtoUnionCave_1F_Text_Intro, JohtoUnionCave_1F_Text_Defeat
    msgbox JohtoUnionCave_1F_Text_After, MSGBOX_AUTOCLOSE
    end
'''
 tx[n]={'Intro':['Caves reward a steady pace.\nCan your team keep its footing?'],
 'Defeat':['You found the right path!'],'After':['Both exits lead outside.\nKeep a healthy team with you.']}
 n='JohtoRoute33'
 say(n,'RouteSign',['ROUTE 33\nWest: AZALEA TOWN'])
 say(n,'Traveler',['ROCKET uniforms? I thought\nyou stopped them in KANTO.',
                    'Some of their people must have\ncome here after that defeat.'])
 n='AzaleaTown'
 say(n,'Resident',['The SLOWPOKE have not returned\nfrom their well today.',
                   'KURT lives north of the CENTER.\nHe is trying to find out why.'])
 say(n,'Gardener',['BUGSY studies how small changes\ncan decide a whole battle.'])
 for key,paras in [('CenterSign',['POKEMON CENTER']),('MartSign',['POKEMON MART']),
 ('KurtSign',["KURT'S HOUSE\nPOKE BALL CRAFTSMAN"]),('GymSign',['AZALEA POKEMON GYM\nLEADER: BUGSY']),
 ('WellSign',['SLOWPOKE WELL\nPlease keep the water clean.'])]:say(n,key,paras)
 n='AzaleaTown_KurtsHouse'
 scripts[n]+=r'''
AzaleaTown_KurtsHouse_Kurt::
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_SLOWPOKE_WELL_CLEARED, AzaleaTown_KurtsHouse_Report
    goto_if_set FLAG_JOHTO_KURT_RESCUE_REQUESTED, AzaleaTown_KurtsHouse_Wait
    goto_if_unset FLAG_JOHTO_ELM_REPORT_DELIVERED, AzaleaTown_KurtsHouse_BeforeElm
    msgbox AzaleaTown_KurtsHouse_Text_Request
    setflag FLAG_JOHTO_KURT_RESCUE_REQUESTED
    release
    end
AzaleaTown_KurtsHouse_Report::
    goto_if_set FLAG_JOHTO_KURT_REPORT_DELIVERED, AzaleaTown_KurtsHouse_Reward
    msgbox AzaleaTown_KurtsHouse_Text_Report
    setflag FLAG_JOHTO_KURT_REPORT_DELIVERED
AzaleaTown_KurtsHouse_Reward::
    goto_if_set FLAG_JOHTO_GOT_NET_BALLS_FROM_KURT, AzaleaTown_KurtsHouse_After
    checkitemspace ITEM_NET_BALL, 3
    goto_if_eq VAR_RESULT, FALSE, AzaleaTown_KurtsHouse_BagFull
    giveitem ITEM_NET_BALL, 3
    goto_if_eq VAR_RESULT, FALSE, AzaleaTown_KurtsHouse_BagFull
    setflag FLAG_JOHTO_GOT_NET_BALLS_FROM_KURT
AzaleaTown_KurtsHouse_After::
    msgbox AzaleaTown_KurtsHouse_Text_After
    release
    end
AzaleaTown_KurtsHouse_BagFull::
    msgbox AzaleaTown_KurtsHouse_Text_BagFull
    release
    end
AzaleaTown_KurtsHouse_Wait::
    msgbox AzaleaTown_KurtsHouse_Text_Wait
    release
    end
AzaleaTown_KurtsHouse_BeforeElm::
    msgbox AzaleaTown_KurtsHouse_Text_BeforeElm
    release
    end
'''
 tx[n]={'Request':['ELM told me about your work.\nI need your help at the well.',
 'ROCKET remnants are taking\nSLOWPOKE tails to sell.',
 'They came here after their\nKANTO operation fell apart.',
 'Please stop them, then tell me\nwhether the SLOWPOKE are safe.'],
 'Wait':['The well is in the northeast.\nPlease check on the SLOWPOKE.'],
 'BeforeElm':["Deliver MR. POKEMON's notes\nto ELM before you help me."],
 'Report':['You drove the ROCKETS away!\nThe SLOWPOKE are safe again.',
 'I will send ELM your findings.\nBUGSY will hear of them too.'],
 'After':['The GYM is ready for you now.\nBUGSY is a careful researcher.',
 'NET BALLS suit BUG and WATER\nPOKEMON. Take good care of them.'],
 'BagFull':['Your report has been accepted.\nBUGSY can challenge you now.',
 'Please make room for three\nNET BALLS. I will keep them.']}
 say(n,'Granddaughter',['Grandpa will tell ELM what\nyou learned at the well.'])
 n='SlowpokeWell_1F'
 for tag in ['A','B']:
  scripts[n]+='\n'+n+'_Grunt'+tag+'::\n    trainerbattle_single TRAINER_JOHTO_WELL_GRUNT_'+tag+', '+n+'_Text_GruntIntro, '+n+'_Text_GruntDefeat\n    msgbox '+n+'_Text_GruntAfter, MSGBOX_AUTOCLOSE\n    end\n'
 scripts[n]+=r'''
SlowpokeWell_1F_Commander::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_KURT_RESCUE_REQUESTED, SlowpokeWell_1F_NoRequest
    goto_if_not_defeated TRAINER_JOHTO_WELL_GRUNT_A, SlowpokeWell_1F_Guards
    goto_if_not_defeated TRAINER_JOHTO_WELL_GRUNT_B, SlowpokeWell_1F_Guards
    trainerbattle_single TRAINER_JOHTO_WELL_COMMANDER, SlowpokeWell_1F_Text_Intro, SlowpokeWell_1F_Text_Defeat, SlowpokeWell_1F_Victory, NO_MUSIC
    goto SlowpokeWell_1F_Victory
SlowpokeWell_1F_Victory::
    msgbox SlowpokeWell_1F_Text_Rescue
    setflag FLAG_JOHTO_SLOWPOKE_WELL_CLEARED
    removeobject 1
    removeobject 2
    removeobject 3
    release
    end
SlowpokeWell_1F_NoRequest::
    msgbox SlowpokeWell_1F_Text_NoRequest
    release
    end
SlowpokeWell_1F_Guards::
    msgbox SlowpokeWell_1F_Text_Guards
    release
    end
SlowpokeWell_1F_Slowpoke::
    lock
    faceplayer
    playmoncry SPECIES_SLOWPOKE, 0
    waitmoncry
    goto_if_set FLAG_JOHTO_SLOWPOKE_WELL_CLEARED, SlowpokeWell_1F_Safe
    msgbox SlowpokeWell_1F_Text_SlowpokeWorried
    release
    end
SlowpokeWell_1F_Safe::
    msgbox SlowpokeWell_1F_Text_SlowpokeSafe
    release
    end
'''
 tx[n]={'GruntIntro':['This is ROCKET business.\nStay away from our operation!'],
 'GruntDefeat':['How did you get past me?'],'GruntAfter':['Our commander is still here!'],
 'NoRequest':['Do you even know why you came?\nGo ask that old man KURT.'],
 'Guards':['My guards are still fighting.\nDeal with them before me!'],
 'Intro':['We lost a base in KANTO,\nnot our ambition!',
 'These sales will fund our\nreturn. You cannot stop us!'],
 'Defeat':['We have to pull out!'],
 'Rescue':['The ROCKETS leave the well.\nThe SLOWPOKE are safe.',
 'KURT needs to hear the news.'],
 'SlowpokeWorried':['SLOWPOKE watches you quietly.\nIt seems uneasy.'],
 'SlowpokeSafe':['SLOWPOKE looks calm again.']}
 n='AzaleaTown_Gym'
 scripts[n]+=r'''
AzaleaTown_Gym_Bugsy::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_BADGE01_GET, AzaleaTown_Gym_NotReady
    goto_if_unset FLAG_JOHTO_KURT_REPORT_DELIVERED, AzaleaTown_Gym_NotReady
    goto_if_set FLAG_JOHTO_BADGE02_GET, AzaleaTown_Gym_Reward
    trainerbattle_single TRAINER_JOHTO_BUGSY, AzaleaTown_Gym_Text_Intro, AzaleaTown_Gym_Text_Defeat, AzaleaTown_Gym_Victory, NO_MUSIC
    goto AzaleaTown_Gym_Reward
AzaleaTown_Gym_Victory::
    setflag FLAG_JOHTO_BADGE02_GET
    msgbox AzaleaTown_Gym_Text_Badge
AzaleaTown_Gym_Reward::
    goto_if_set FLAG_JOHTO_GOT_TM06_FROM_BUGSY, AzaleaTown_Gym_After
    checkitemspace ITEM_TM06
    goto_if_eq VAR_RESULT, FALSE, AzaleaTown_Gym_BagFull
    giveitem ITEM_TM06
    goto_if_eq VAR_RESULT, FALSE, AzaleaTown_Gym_BagFull
    setflag FLAG_JOHTO_GOT_TM06_FROM_BUGSY
    msgbox AzaleaTown_Gym_Text_TM
AzaleaTown_Gym_After::
    msgbox AzaleaTown_Gym_Text_After
    release
    end
AzaleaTown_Gym_NotReady::
    msgbox AzaleaTown_Gym_Text_NotReady
    release
    end
AzaleaTown_Gym_BagFull::
    msgbox AzaleaTown_Gym_Text_BagFull
    release
    end
'''
 tx[n]={'Intro':['I am BUGSY. I study the\npotential of BUG POKEMON.',
 'KURT told me about the rescue.\nNow show me your battle skills!'],
 'Defeat':['That is an impressive finding!'],
 'Badge':['You earned the HIVEBADGE!\nYour second JOHTO GYM victory.'],
 'TM':['TM06 teaches TOXIC.\nPatient tactics can win battles.'],
 'After':['Research and training work\nwell when they help each other.'],
 'NotReady':['Earn the VIOLET GYM badge,\nand bring KURT the rescue news.'],
 'BagFull':['Your badge is already earned.\nMake room for the TM reward.']}
 for key,tr in [('Al','AL'),('Benny','BENNY')]:
  scripts[n]+='\n'+n+'_'+key+'::\n    trainerbattle_single TRAINER_JOHTO_'+tr+', '+n+'_Text_StudentIntro, '+n+'_Text_StudentDefeat\n    msgbox '+n+'_Text_StudentAfter, MSGBOX_AUTOCLOSE\n    end\n'
 tx[n].update({'StudentIntro':['BUG POKEMON have many ways\nto surprise an opponent.'],'StudentDefeat':['You understood their strength!'],'StudentAfter':['BUGSY learns from every battle.']})
 say(n,'GymGuy',['KURT can confirm the rescue.\nTell him before the GYM battle.'])
 return scripts,{n:C.texts(n,rows) for n,rows in tx.items()}


def build(s):
 # ILEX_EXTENSION_GUARD
 if any(n not in OLD + NEW for n in s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]):
  raise RuntimeError("Ilex extension exists; use build_ilex.py")
 out={};stats={'chapter':'Azalea','save_layout_changed':False,'visual_limits':['Bugsy uses native BUG_CATCHER portrait until dedicated art exists','Well entrance temporarily reuses a native cave mouth'],'reward_adaptation':'Gen III TM06 TOXIC; the original Gen II TM49 would mean SNATCH in FRLG','not_implemented':['Silver Azalea encounter','Ilex Forest and later Johto towns','Johto League and its ending gate']}
 groups=s.json('data/maps/map_groups.json');assert groups['gMapGroup_JohtoEntry'] in (OLD,OLD+NEW)
 for k,v in groups.items():
  if k not in ('group_order','gMapGroup_JohtoEntry'):assert not(set(v)&set(NEW))
 groups['gMapGroup_JohtoEntry']=OLD+NEW;out['data/maps/map_groups.json']=enc(groups)
 ls=s.json('data/layouts/layouts.json');arrays=geometry(s)
 for name,a in arrays.items():
  outside=name in ['JohtoRoute32','JohtoRoute33','AzaleaTown']
  item={'id':'LAYOUT_'+ident(name),'name':name+'_Layout','width':len(a[0]),'height':len(a),'border_width':2,'border_height':2,'primary_tileset':'gTileset_General','secondary_tileset':'gTileset_ViridianCity' if outside else 'gTileset_Cave','blockdata_filepath':'data/layouts/'+name+'/map.bin','border_filepath':'data/layouts/'+name+'/border.bin'}
  hits=[x for x in ls['layouts'] if x.get('id')==item['id']];assert not hits or hits==[item]
  if not hits:ls['layouts'].append(item)
  out[item['blockdata_filepath']]=C.pack(a);out[item['border_filepath']]=struct.pack('<4H',*((0x414,0x415,0x41c,0x41d) if outside else (0x0691,)*4))
 out['data/layouts/layouts.json']=enc(ls);maps={}
 def temp(n,source,section,layout=None,music=None):
  j=s.json('data/maps/'+source+'/map.json');j.update(id=MID[n],name=n,region_map_section=section,connections=None)
  if layout:j['layout']=layout
  if music:j['music']=music
  for k in ['object_events','warp_events','coord_events','bg_events']:j[k]=[]
  maps[n]=j;return j
 n='JohtoRoute32';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE32','LAYOUT_JOHTO_ROUTE32','MUS_ROUTE1')
 j['connections']=[{'map':'MAP_VIOLET_CITY','direction':'up','offset':-10}]
 j['warp_events']=[warp(11,57,'JohtoUnionCave_1F',0)]
 j['object_events']=[obj('YOUNGSTER',6,28,n+'_Russell',movement='FACE_RIGHT'),obj('SCIENTIST',12,8,n+'_Researcher')]
 j['bg_events']=[C.bg(12,10,n+'_RouteSign'),C.bg(12,53,n+'_CaveSign')]
 j['coord_events']=[{'type':'trigger','x':x,'y':4,'elevation':0,'var':'VAR_TEMP_0','var_value':'0','script':n+'_CheckBadge'} for x in (8,9,10)]
 n='JohtoUnionCave_1F';j=temp(n,'MtMoon_1F','MAPSEC_JOHTO_UNION_CAVE','LAYOUT_JOHTO_UNION_CAVE_1F','MUS_MT_MOON')
 j['warp_events']=[warp(18,37,'JohtoRoute32',0),warp(41,35,'JohtoRoute33',0)]
 j['object_events']=[obj('HIKER',12,10,n+'_Anthony',movement='FACE_RIGHT')]
 n='JohtoRoute33';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE33','LAYOUT_JOHTO_ROUTE33','MUS_ROUTE1')
 j['connections']=[{'map':MID['AzaleaTown'],'direction':'left','offset':0}]
 j['warp_events']=[warp(26,5,'JohtoUnionCave_1F',1)]
 j['object_events']=[obj('HIKER',21,12,n+'_Traveler',movement='FACE_LEFT')]
 j['bg_events']=[C.bg(24,9,n+'_RouteSign')]
 n='AzaleaTown';j=temp(n,'ViridianCity','MAPSEC_AZALEA_TOWN','LAYOUT_AZALEA_TOWN','MUS_PEWTER')
 j['connections']=[{'map':MID['JohtoRoute33'],'direction':'right','offset':0}]
 j['warp_events']=[warp(7,22,'AzaleaTown_PokemonCenter_1F',1,0),warp(30,22,'AzaleaTown_Mart',1,0),warp(7,8,'AzaleaTown_KurtsHouse',1,0),warp(21,9,'AzaleaTown_Gym',1,0),warp(32,6,'SlowpokeWell_1F',0)]
 j['object_events']=[obj('WOMAN_2',16,16,n+'_Resident'),obj('OLD_MAN_2',26,13,n+'_Gardener')]
 j['bg_events']=[C.bg(x,y,n+'_'+k) for x,y,k in [(11,22,'CenterSign'),(33,22,'MartSign'),(12,8,'KurtSign'),(25,9,'GymSign'),(30,7,'WellSign')]]
 scripts,tx=events()
 for suffix in ['PokemonCenter_1F','PokemonCenter_2F','Mart']:
  old='VioletCity_'+suffix;n='AzaleaTown_'+suffix
  j=json.loads(s.text('data/maps/'+old+'/map.json').replace('VIOLET_CITY','AZALEA_TOWN').replace('VIOLET','AZALEA').replace('VioletCity','AzaleaTown'))
  assert j['id']==MID[n];maps[n]=j
  for f,target in [('scripts.inc',scripts),('text.inc',tx)]:
   target[n]=s.text('data/maps/'+old+'/'+f).replace('VIOLET_CITY','AZALEA_TOWN').replace('VIOLET','AZALEA').replace('VioletCity','AzaleaTown')
  if suffix=='PokemonCenter_1F':
   j['object_events'][0]['local_id']='LOCALID_AZALEA_NURSE'
   for wp in j['warp_events'][:3]:wp['dest_warp_id']='0'
  if suffix=='Mart':
   for wp in j['warp_events']:wp['dest_warp_id']='1'
 n='AzaleaTown_KurtsHouse';j=temp(n,'CeruleanCity_House3','MAPSEC_AZALEA_TOWN','LAYOUT_HOUSE1','MUS_PEWTER')
 j['object_events']=[obj('OLD_MAN_1',4,5,n+'_Kurt'),obj('LITTLE_GIRL',7,5,n+'_Granddaughter')]
 j['warp_events']=[warp(x,7,'AzaleaTown',2) for x in (3,4,5)]
 n='AzaleaTown_Gym';j=temp(n,'CeladonCity_Gym','MAPSEC_AZALEA_TOWN',music='MUS_GYM')
 j['object_events']=[obj('BUG_CATCHER',6,4,n+'_Bugsy'),obj('BUG_CATCHER',3,11,n+'_Al',movement='FACE_RIGHT'),obj('BUG_CATCHER',9,10,n+'_Benny',movement='FACE_LEFT'),obj('GYM_GUY',7,16,n+'_GymGuy')]
 j['warp_events']=[warp(x,18,'AzaleaTown',3) for x in (5,6,7)]
 n='SlowpokeWell_1F';j=temp(n,'MtMoon_1F','MAPSEC_SLOWPOKE_WELL','LAYOUT_SLOWPOKE_WELL_1F','MUS_MT_MOON')
 j['warp_events']=[warp(11,21,'AzaleaTown',4)]
 j['object_events']=[obj('ROCKET_M',4,12,n+'_GruntA',movement='FACE_RIGHT'),obj('ROCKET_M',18,13,n+'_GruntB',movement='FACE_LEFT'),obj('ROCKET_M',12,6,n+'_Commander')]
 for o in j['object_events']:o['flag']='FLAG_JOHTO_SLOWPOKE_WELL_CLEARED'
 j['object_events'] += [obj('SLOWPOKE',x,y,n+'_Slowpoke') for x,y in [(4,4),(19,4),(18,18)]]
 for n,j in maps.items():
  out['data/maps/'+n+'/map.json']=enc(j);out['data/maps/'+n+'/scripts.inc']=scripts[n].encode();out['data/maps/'+n+'/text.inc']=tx.get(n,'@ Shared native dialogue.\n').encode()
 p='data/maps/VioletCity/map.json';j=s.json(p);link={'map':MID['JohtoRoute32'],'direction':'down','offset':10}
 assert not [c for c in j['connections'] if c['direction']=='down' and c!=link]
 if link not in j['connections']:j['connections'].append(link)
 out[p]=enc(j);l=next(x for x in ls['layouts'] if x.get('id')==j['layout']);assert (l['width'],l['height'])==(40,32)
 a=list(struct.unpack('<1280H',s.read(l['blockdata_filepath'])))
 for y in (30,31):
  for x in (18,19,20):
   k=y*40+x;assert a[k] in (C.dense(x,y),0x3195);a[k]=0x3195
 for y in range(26,30):
  for x in (18,19,20):assert ((a[y*40+x]>>10)&3)==0
 out[l['blockdata_filepath']]=struct.pack('<1280H',*a)
 sect=s.json('src/data/region_map/region_map_sections.json')
 for sid,name,x,y,w,h in [('JOHTO_ROUTE32','ROUTE 32',2,4,1,4),('JOHTO_UNION_CAVE','UNION CAVE',2,8,1,1),('JOHTO_ROUTE33','ROUTE 33',1,8,1,1),('AZALEA_TOWN','AZALEA TOWN',0,8,1,1),('SLOWPOKE_WELL','SLOWPOKE WELL',0,7,1,1)]:
  v={'id':'MAPSEC_'+sid,'name':name,'x':x,'y':y,'width':w,'height':h}
  hits=[o for o in sect['map_sections'] if o['id']==v['id']];assert not hits or hits==[v]
  if not hits:sect['map_sections'].append(v)
 out['src/data/region_map/region_map_sections.json']=enc(sect)
 heals=s.json('src/data/heal_locations.json');v={'id':'HEAL_LOCATION_AZALEA_TOWN','map':MID['AzaleaTown'],'x':7,'y':23,'respawn_map':MID['AzaleaTown_PokemonCenter_1F'],'respawn_npc':'LOCALID_AZALEA_NURSE'}
 hits=[o for o in heals['heal_locations'] if o['id']==v['id']];assert not hits or hits==[v]
 if not hits:heals['heal_locations'].append(v)
 out['src/data/heal_locations.json']=enc(heals)
 for p,key in [('data/layouts/layouts.json','layouts'),('src/data/region_map/region_map_sections.json','map_sections'),('src/data/heal_locations.json','heal_locations')]:
  old=s.json(p)[key];assert json.loads(out[p])[key][:len(old)]==old
 shared(s,out);areas(s,out);stats['new_maps']=NEW;stats['new_flags']=FLAGS
 return out,stats
def shared(s,out):
 p='include/constants/flags_johto_story.h';t=s.text(p);block='\n// '+MARK+'\n'+''.join('#define '+n+' (JOHTO_STORY_FLAGS_START + '+str(v)+')\n' for n,v in FLAGS.items())
 if MARK not in t:
  used={int(v,0) for v in re.findall(r'JOHTO_STORY_FLAGS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',t)};assert not(used&set(FLAGS.values()))
  assert not any(n in t for n in FLAGS);idx=t.rfind('#endif');assert idx>=0;t=t[:idx]+block+'\n'+t[idx:]
 else:assert block in t
 out[p]=t.encode()
 p='include/constants/opponents_johto_azalea.h';h='#ifndef GUARD_CONSTANTS_OPPONENTS_JOHTO_AZALEA_H\n#define GUARD_CONSTANTS_OPPONENTS_JOHTO_AZALEA_H\n'
 for n,c,pic,party,num in TRAINERS:h+='#define TRAINER_JOHTO_'+n+' (HOENN_TRAINERS_START + '+str(num)+')\n'
 h+='#endif\n';out[p]=h.encode()
 for header in (s.root/'include/constants').glob('opponents*.h'):
  rel=header.relative_to(s.root).as_posix()
  if rel==p:continue
  used={int(v,0) for v in re.findall(r'HOENN_TRAINERS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',s.text(rel))}
  assert not(used&{v[-1] for v in TRAINERS}),('trainer collision',rel)
 p='include/constants/opponents.h';a='#include "constants/opponents_johto.h"';out[p]=C.once(s.text(p),a,a+'\n#include "constants/opponents_johto_azalea.h"','Azalea trainer include').encode()
 parties='// '+MARK+'\n';trainers='// '+MARK+'\n'
 for n,c,pic,party,num in TRAINERS:
  sym='sParty_Johto'+''.join(x.title() for x in n.split('_'))
  parties+='static const struct TrainerMonNoItemDefaultMoves '+sym+'[] = {\n'+''.join('    {.iv = 40, .lvl = '+str(lv)+', .species = SPECIES_'+sp+'},\n' for sp,lv in party)+'};\n\n'
  display=n if n not in ['WELL_GRUNT_A','WELL_GRUNT_B','WELL_COMMANDER'] else 'GRUNT'
  trainers+='    [TRAINER_JOHTO_'+n+'] = {\n        .trainerClass = TRAINER_CLASS_'+c+',\n        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_MALE,\n        .trainerPic = TRAINER_PIC_'+pic+',\n        .trainerName = _("'+display+'"),\n        .items = {},\n        .doubleBattle = FALSE,\n        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,\n        .party = NO_ITEM_DEFAULT_MOVES('+sym+'),\n    },\n'
 out['src/data/trainer_parties_johto_azalea.h']=parties.encode();out['src/data/trainers_johto_azalea.h']=trainers.encode()
 for p,a,inc in [('src/data/trainers.h','#include "trainers_johto.h"','#include "trainers_johto_azalea.h"'),('src/data/trainer_parties.h','#include "trainer_parties_johto.h"','#include "trainer_parties_johto_azalea.h"')]:
  out[p]=C.once(s.text(p),a,a+'\n'+inc,'Azalea trainer data').encode()
 p='data/event_scripts.s';t=s.text(p);block='@ '+MARK+'\n'+''.join('    .include "data/maps/'+n+'/'+f+'"\n' for n in NEW for f in ['scripts.inc','text.inc'])
 if MARK not in t:assert not any('data/maps/'+n+'/' in t for n in NEW);t=t.rstrip()+'\n\n'+block
 else:assert block in t
 out[p]=t.encode()
 p='tools/johto/build_violet.py';t=s.text(p)
 guard=' # AZALEA_EXTENSION_GUARD\n if any(n not in OLD + NEW for n in s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]):\n  raise RuntimeError("Azalea extension exists; use build_azalea.py")\n'
 if '# AZALEA_EXTENSION_GUARD' not in t:
  t,n=re.subn(r'(?m)^def build\(s\):\n',lambda m:m.group(0)+guard,t);assert n==1
 else:assert guard in t
 out[p]=t.encode()
 p='src/data/wild_encounters.json';j=s.json(p);gs=[g for g in j['wild_encounter_groups'] if g['label']=='gWildMonHeaders'];assert len(gs)==1 and gs[0]['for_maps']
 for name,(day,night,levels) in WILD.items():
  row={'map':MID[name],'base_label':'s'+name.replace('_','')}
  for field,sp in [('land_mons',day),('land_mons_morning',day),('land_mons_night',night or day)]:
   row[field]={'encounter_rate':10 if 'Route' in name else 8,'mons':[{'min_level':lv,'max_level':lv,'species':'SPECIES_'+spn} for spn,lv in zip(sp,levels)]}
  out['tools/johto/'+name.lower()+'_wild.json']=enc(row)
  hits=[x for x in gs[0]['encounters'] if x['map']==row['map'] or x['base_label']==row['base_label']];assert not hits or hits==[row]
  if not hits:gs[0]['encounters'].append(row)
 out[p]=enc(j)


def areas(s,out):
 for p in ['src/region_map.c','src/pokemon_summary_screen.c']:
  t=s.text(p);pat=r'(MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP[\s\S]{0,120}?<=\s*)MAPSEC_VIOLET_CITY'
  if re.search(pat,t):t,n=re.subn(pat,lambda m:m.group(1)+'MAPSEC_SLOWPOKE_WELL',t);assert n==1
  else:assert re.search(pat.replace('MAPSEC_VIOLET_CITY','MAPSEC_SLOWPOKE_WELL'),t)
  out[p]=t.encode()
 p='src/region_map.c';t=out[p].decode()
 if '// AZALEA_ROUTE32_MAP_GRID_V1' not in t:
  pat=r'(?m)^([ \t]*)// VIOLET_ROUTE31_MAP_GRID_V1'
  lines=['// AZALEA_ROUTE32_MAP_GRID_V1','if (layer == LAYER_MAP && x == 2 && y >= 4 && y <= 7)','    return MAPSEC_JOHTO_ROUTE32;','if (layer == LAYER_MAP && x == 2 && y == 8)','    return MAPSEC_JOHTO_UNION_CAVE;','if (layer == LAYER_MAP && x == 1 && y == 8)','    return MAPSEC_JOHTO_ROUTE33;','if (layer == LAYER_MAP && x == 0 && y == 8)','    return MAPSEC_AZALEA_TOWN;','if (layer == LAYER_MAP && x == 0 && y == 7)','    return MAPSEC_SLOWPOKE_WELL;','// VIOLET_ROUTE31_MAP_GRID_V1']
  t,n=re.subn(pat,lambda m:'\n'.join(m.group(1)+line for line in lines),t);assert n==1
 out[p]=t.encode()
 p='graphics/region_map/johto_entry.bin';v=list(struct.unpack('<600H',s.read(p)))
 cells={(6,y):0x100a for y in range(8,12)}
 cells.update({(6,12):0x1001,(5,12):0x100a,(4,12):0x1001,(4,11):0x1001})
 for (x,y),new in cells.items():
  k=y*30+x;assert v[k] in (3,5,6,7,new),(x,y,v[k]);v[k]=new
 out[p]=struct.pack('<600H',*v)
 p='src/wild_pokemon_area.c';t=s.text(p)
 extra=[('Route32','johtoRoute32','MAP_JOHTO_ROUTE32'),('UnionCave','johtoUnionCave','MAP_JOHTO_UNION_CAVE_1F'),('Route33','johtoRoute33','MAP_JOHTO_ROUTE33'),('SlowpokeWell','johtoSlowpokeWell','MAP_SLOWPOKE_WELL_1F')]
 if 'bool8 johtoRoute32;' not in t:
  t,n=re.subn(r'(bool8\s+johtoRoute31\s*;)',lambda m:m.group(1)+''.join('\n    bool8 '+f+';' for _,f,_ in extra),t);assert n==1
 if 'MAP_GROUP(MAP_JOHTO_ROUTE32)' not in t:
  pat=r'(?s)(if\s*\(header->mapGroup\s*==\s*MAP_GROUP\(MAP_JOHTO_ROUTE31\)\s*&&\s*header->mapNum\s*==\s*MAP_NUM\(MAP_JOHTO_ROUTE31\)\s*\)\s*\{\s*habitats->johtoRoute31\s*=\s*TRUE;\s*continue;\s*\})'
  def extend(m):return m.group(1)+''.join('\n            '+m.group(1).replace('MAP_JOHTO_ROUTE31',mn).replace('johtoRoute31',f) for _,f,mn in extra)
  t,n=re.subn(pat,extend,t);assert n==1
 old='if (habitats.johtoRoute29 || habitats.johtoRoute30 || habitats.johtoRoute31)'
 new=old[:-1]+''.join(' || habitats.'+f for _,f,_ in extra)+')'
 t=C.once(t,old,new,'Azalea habitat region bit')
 if 'GetJohtoRoute32AreaMarkerSubsprite(areaCount++, subsprites);' not in t:
  pat=r'(if\s*\(habitats\.johtoRoute31\)\s*GetJohtoRoute31AreaMarkerSubsprite\(areaCount\+\+,\s*subsprites\);)'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n        if (habitats.'+f+')\n            GetJohto'+key+'AreaMarkerSubsprite(areaCount++, subsprites);' for key,f,_ in extra),t);assert n==1
 out[p]=t.encode()
 p='include/pokedex_area_markers.h';t=s.text(p)
 if 'GetJohtoRoute32AreaMarkerSubsprite' not in t:
  t,n=re.subn(r'(void GetJohtoRoute31AreaMarkerSubsprite\([^;]*;)',lambda m:m.group(1)+''.join('\nvoid GetJohto'+key+'AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);' for key,_,_ in extra),t);assert n==1
 out[p]=t.encode()
 p='src/pokedex_area_markers.c';t=s.text(p)
 specs=[('Route29','SmallHorizontal',94,50),('Route30','SmallVertical',78,19),('Route31','MediumHorizontal',48,4),('Route32','SmallVertical',32,25),('UnionCave','Circular',31,44),('Route33','SmallHorizontal',16,44),('SlowpokeWell','Circular',12,38)]
 for key,shape,x,y in specs:
  name='GetJohto'+key+'AreaMarkerSubsprite'
  new='void '+name+'(s32 i, struct Subsprite *subsprites)\n{\n    if (subsprites == NULL)\n        return;\n    subsprites[i] = sSubsprite_'+shape+';\n    subsprites[i].x = '+str(x)+' + (HOENN_AREA_MAP_LEFT * 8 - 104);\n    subsprites[i].y = '+str(y)+';\n}'
  if re.search(r'void\s+'+name+r'\(',t):t=C.replace_function(t,name,new,'Azalea habitat marker')
  else:t=t.rstrip()+'\n\n'+new+'\n'
 out[p]=t.encode()
 p='src/pokedex_screen.c';t=s.text(p);decl=''
 for key,label in [('R29','29'),('R30','30'),('R31','31'),('R32','32'),('R33','33'),('Union','UNION'),('Azalea','AZALEA'),('Well','WELL'),('CherryShort','CHERRY')]:
  decl+='static const u8 sText_Johto'+key+'[] = _("'+label+'");\n'
 if 'sText_JohtoR32[]' not in t:
  anchor='static const u8 sText_JohtoRoute31[] = _("ROUTE 31");\n';assert t.count(anchor)==1;t=t.replace(anchor,anchor+decl)
 body='static void DexScreen_DrawJohtoEntryArea(u8 windowId)\n{\n    FillWindowPixelBuffer(windowId, PIXEL_FILL(2));\n    FillWindowPixelRect(windowId, PIXEL_FILL(6), 3, 3, 122, 66);\n'
 for x,y,w,h in [(34,8,48,6),(78,8,6,48),(34,8,6,42),(8,46,32,6),(78,52,42,6),(12,40,4,10)]:
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(3), '+', '.join(map(str,[x,y,w,h]))+');\n'
  if w>h:inside=[x+1,y+2,w-2,2]
  else:inside=[x+2,y+1,2,h-2]
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(5), '+', '.join(map(str,inside))+');\n'
 for x,y in [(34,8),(78,38),(78,52),(114,52),(8,46),(32,46),(12,40)]:
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(2), '+', '.join(map(str,[x,y,6,6]))+');\n'
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(5), '+', '.join(map(str,[x+1,y+1,4,4]))+');\n'
 for key,x,y in [('Violet',12,0),('R31',57,0),('R30',86,20),('CherryShort',86,34),('R29',96,59),('Airstrip',48,61),('NewBark',90,61),('R32',42,25),('Union',37,40),('R33',19,52),('Azalea',2,61),('Well',2,30)]:
  body+='    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_Johto'+key+', '+str(x)+', '+str(y)+', 0);\n'
 body+='}'
 out[p]=C.replace_function(t,'DexScreen_DrawJohtoEntryArea',body,'Azalea habitat diagram').encode()


def validate(s,out,stats):
 allsrc=Source(s.root,dict(s.overlay,**out))
 layouts={x['id']:x for x in allsrc.json('data/layouts/layouts.json')['layouts'] if x.get('id')}
 maps={n:allsrc.json('data/maps/'+n+'/map.json') for n in NEW}
 starts={'JohtoRoute32':(9,0),'JohtoRoute33':(0,13),'AzaleaTown':(39,13),'JohtoUnionCave_1F':(18,37),'SlowpokeWell_1F':(11,21),'AzaleaTown_PokemonCenter_1F':(7,7),'AzaleaTown_Mart':(4,7),'AzaleaTown_KurtsHouse':(4,7),'AzaleaTown_Gym':(6,18)}
 checks=[]
 for n,m in maps.items():
  l=layouts[m['layout']];w,h=l['width'],l['height'];raw=allsrc.read(l['blockdata_filepath']);assert len(raw)==w*h*2
  vals=struct.unpack('<'+'H'*(w*h),raw);outside=n in ('JohtoRoute32','JohtoRoute33','AzaleaTown')
  def walk(x,y):return 0<=x<w and 0<=y<h and not ((vals[y*w+x]>>10)&3) and (not outside or vals[y*w+x]>>12!=1)
  solid={(o['x'],o['y']) for o in m['object_events']}
  for o in m['object_events']:
   assert 0<=o['x']<w and 0<=o['y']<h
   if n!='AzaleaTown_PokemonCenter_2F':assert walk(o['x'],o['y']),(n,'blocked NPC',o)
  for wp in m['warp_events']:
   dst=next((d for d in NEW if MID[d]==wp['dest_map']),None)
   if dst:
    i=int(wp['dest_warp_id']);other=maps[dst]['warp_events']
    assert 0<=i<len(other) and other[i]['dest_map']==m['id'],(n,'non reciprocal',wp)
  if n not in starts:
   checks.append({'map':n,'native_CableClub_layout':True});continue
  start=starts[n];assert walk(*start),(n,start);seen={start};q=deque([start])
  while q:
   x,y=q.popleft()
   for z in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
    if z not in seen and z not in solid and walk(*z):seen.add(z);q.append(z)
  for wp in m['warp_events']:
   z=(wp['x'],wp['y']+1) if outside else (wp['x'],wp['y'])
   assert z in seen,(n,'warp unreachable',wp,z)
  for o in m['object_events']:
   x,y=o['x'],o['y'];gfx=o['graphics_id']
   if gfx=='OBJ_EVENT_GFX_NURSE':assert (x,y+2) in seen;continue
   if gfx=='OBJ_EVENT_GFX_CLERK':continue
   assert any(z in seen for z in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))),(n,'NPC unreachable',o)
  if n=='JohtoRoute32':assert all((x,0) in seen for x in (8,9,10))
  if n=='JohtoRoute33':assert all((0,y) in seen for y in range(11,15))
  if n=='AzaleaTown':assert all((39,y) in seen for y in range(11,15))
  checks.append({'map':n,'walkable_reachable':len(seen),'NPC_and_warps':True})
 cmds=set(re.findall(r'(?m)^\s*\.macro\s+(\w+)',s.text('asm/macros/event.inc')+'\n'+s.text('asm/macros/map.inc')))
 cmds.update(re.findall(r'(?m)^\s*create_movement_action\s+(\w+)',s.text('asm/macros/movement.inc')))
 for p,b in out.items():
  if p.endswith('scripts.inc'):
   for ln in b.decode().splitlines():
    t=ln.strip()
    if not t or t.startswith(('@','.','#')) or t.endswith(':'):continue
    assert t.split()[0] in cmds,(p,'unknown macro',t)
 headers='\n'.join(s.text('include/constants/'+n) for n in ['species.h','items.h','songs.h','event_objects.h','global.h','trainers.h'])+'\n'+s.text('include/battle.h')
 refs=set()
 for p,b in out.items():
  if p.endswith(('.h','.c','.json','scripts.inc')):
   try:refs.update(re.findall(r'\b(?:SPECIES|ITEM|MUS|OBJ_EVENT_GFX|TRAINER_CLASS|TRAINER_PIC|TRAINER_ENCOUNTER_MUSIC)_[A-Z0-9_]+',b.decode()))
   except UnicodeDecodeError:pass
 missing=[v for v in refs if not re.search(r'\b'+re.escape(v)+r'\b',headers)]
 assert not missing,('unknown constants',missing)
 # Make all 12-slot tables and every time-of-day variant explicit.
 for name in WILD:
  j=json.loads(out['tools/johto/'+name.lower()+'_wild.json'])
  for key in ['land_mons','land_mons_morning','land_mons_night']:assert len(j[key]['mons'])==12
 stats['static_checks']=checks;stats['native_build_and_emulator']='NOT_RUN_BY_GENERATOR'
 return stats
def apply(root,mutate=False):
 s=Source(root)
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 out,stats=build(s);validate(s,out,stats)
 again,_=build(Source(root,dict(s.overlay,**out)));assert out==again,'not idempotent'
 owned=[p for p in out if any(p.startswith('data/maps/'+n+'/') or p.startswith('data/layouts/'+n+'/') for n in NEW)]
 owned+=['include/constants/opponents_johto_azalea.h','src/data/trainers_johto_azalea.h','src/data/trainer_parties_johto_azalea.h']+['tools/johto/'+n.lower()+'_wild.json' for n in WILD]
 for p in owned:
  if s.exists(p):assert s.read(p)==out[p],'existing owned artifact differs: '+p
 changed={p:b for p,b in out.items() if not s.exists(p) or s.read(p)!=b}
 print(json.dumps({'apply':mutate,'files':sorted(changed),'validation':stats},indent=2))
 if not mutate or not changed:return
 for p,b in s.used.items():assert (root/p).read_bytes()==b,'concurrent edit '+p
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 bak=root/'outputs/johto-azalea-chapter-v1'/stamp;bak.mkdir(parents=True,exist_ok=False)
 manifest={'time':stamp,'validation':stats,'files':{}}
 for p,b in changed.items():
  target=root/p;old=target.read_bytes() if target.exists() else None
  manifest['files'][p]={'before':sha(old) if old is not None else None,'after':sha(b)}
  if old is not None:
   q=bak/'before'/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(old)
 (bak/'manifest.json').write_bytes(enc(manifest))
 for p,b in changed.items():
  target=root/p;target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.azalea.tmp')
  assert not tmp.exists();tmp.write_bytes(b);tmp.replace(target)
 print('APPLIED',bak/'manifest.json')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root).resolve(),a.apply)
