#!/usr/bin/env python3
"""Append-only Johto Ice Path and Blackthorn final badge chapter."""
import argparse,copy,datetime,json,re,struct,subprocess,sys
from collections import deque
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_radio_tower as R
M,C,V=R.M,R.C,R.V
Source,enc,sha=R.Source,R.enc,R.sha
OLD=R.OLD+R.NEW
NEW=['JohtoRoute44','IcePath_1F','IcePath_B1F','IcePath_B2F','BlackthornCity',
 'BlackthornCity_PokemonCenter_1F','BlackthornCity_PokemonCenter_2F','BlackthornCity_Mart','BlackthornCity_Gym','DragonDen_1F','DragonDen_Shrine']
IDS=['JOHTO_ROUTE44','ICE_PATH_1F','ICE_PATH_B1F','ICE_PATH_B2F','BLACKTHORN_CITY',
 'BLACKTHORN_CITY_POKEMON_CENTER_1F','BLACKTHORN_CITY_POKEMON_CENTER_2F','BLACKTHORN_CITY_MART','BLACKTHORN_CITY_GYM','DRAGON_DEN_1F','DRAGON_DEN_SHRINE']
MID=dict(zip(NEW,['MAP_'+v for v in IDS]))
MARK='JOHTO_BLACKTHORN_FINAL_BADGE_V1'
FLAGS={'FLAG_JOHTO_BADGE08_GET':23,'FLAG_JOHTO_CLAIR_DEFEATED':59,
 'FLAG_JOHTO_DRAGON_TRIAL_CLEARED':60,'FLAG_JOHTO_CLAIR_TM02_RECEIVED':61,
 'FLAG_JOHTO_ICE_PATH_WATERFALL_REWARDED':62}
TRAINERS=[
 ('WILTON','FISHERMAN','FISHERMAN','MALE',[('GOLDEEN',28),('SEAKING',30)],846),
 ('VANCE','BIRD_KEEPER','BIRD_KEEPER','MALE',[('PIDGEOTTO',29),('FEAROW',30)],847),
 ('ALLEN','COOLTRAINER','COOLTRAINER_M','MALE',[('DRATINI',32),('DRAGONAIR',34)],848),
 ('FRAN','COOLTRAINER','COOLTRAINER_F','FEMALE',[('SEADRA',33),('DRAGONAIR',35)],849),
 ('CLAIR','LEADER','LEADER_MISTY','FEMALE',[('DRAGONAIR',37,['DRAGON_RAGE','THUNDER_WAVE','SLAM','SURF']),
  ('DRAGONAIR',37,['DRAGON_RAGE','THUNDER_WAVE','SLAM','ICE_BEAM']),
  ('KINGDRA',40,['SURF','DRAGON_BREATH','SMOKESCREEN','HYPER_BEAM'])],850)]
DISPLAY={}
WILD={'JohtoRoute44':(['TANGELA','BELLSPROUT','WEEPINBELL','TANGELA','BELLSPROUT','WEEPINBELL','LICKITUNG','TANGELA','LICKITUNG','WEEPINBELL','LICKITUNG','TANGELA'],
 ['TANGELA','BELLSPROUT','WEEPINBELL','NOCTOWL','BELLSPROUT','WEEPINBELL','LICKITUNG','TANGELA','LICKITUNG','NOCTOWL','LICKITUNG','TANGELA'],[24,24,25,25,26,27,25,27,26,28,28,27])}
for _n in ['IcePath_1F','IcePath_B1F','IcePath_B2F']:
 WILD[_n]=(['ZUBAT','SWINUB','JYNX','ZUBAT','SWINUB','GOLBAT','SNEASEL','JYNX','SNEASEL','SWINUB','JYNX','SNEASEL'],
 ['ZUBAT','SWINUB','JYNX','ZUBAT','SWINUB','GOLBAT','SNEASEL','JYNX','SNEASEL','SWINUB','JYNX','SNEASEL'],[22,22,23,24,24,25,25,26,26,27,28,29])
WILD['DragonDen_1F']=(['ZUBAT','ZUBAT','GOLBAT','ZUBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT'],
 ['ZUBAT','ZUBAT','GOLBAT','ZUBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT','GOLBAT'],[24,24,25,26,26,27,28,28,29,29,30,30])
WATER={'DragonDen_1F':(['MAGIKARP','MAGIKARP','DRATINI','DRATINI','DRAGONAIR'],[15,20,20,25,30])}
def ident(n):return IDS[NEW.index(n)]
def warp(x,y,dst,index,elevation=3):
 return {'x':x,'y':y,'elevation':elevation,'dest_map':MID.get(dst,dst),'dest_warp_id':str(index)}
def obj(gfx,x,y,script,**kw):
 flag=kw.pop('flag','0');v=C.obj(gfx,x,y,script,**kw);v['flag']=flag
 if 'local_id' in v:assert re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',v['local_id'])
 return v


def blackthorn_geometry(s):
 vir=V.layout_array(s,'LAYOUT_VIRIDIAN_CITY');pew=V.layout_array(s,'LAYOUT_PEWTER_CITY')
 saff=V.layout_array(s,'LAYOUT_SAFFRON_CITY');route10=V.layout_array(s,'LAYOUT_ROUTE10')
 def land(w,h):
  a=[[0x3001]*w for _ in range(h)]
  for box in [(0,0,w,2),(0,0,2,h),(w-2,0,w,h),(0,h-2,w,h)]:C.fill(a,*box,C.dense)
  return a
 r44=land(48,24);C.fill(r44,0,15,22,19,0x3195);C.fill(r44,18,7,22,19,0x3195)
 C.fill(r44,18,7,43,11,0x3195);C.fill(r44,39,7,43,14,0x3195)
 for box in [(5,4,15,10),(27,15,39,21)]:C.fill(r44,*box,C.grass)
 C.paste(r44,V.crop(route10,6,17,5,3),38,3);C.fill(r44,39,6,42,8,0x3195)
 town=land(32,32);C.fill(town,4,22,29,26,0x3195);C.fill(town,13,6,17,28,0x3195)
 C.fill(town,13,12,29,16,0x3195)
 C.paste(town,V.crop(saff,22,34,5,5),5,18)
 C.paste(town,V.crop(saff,38,17,5,5),22,17)
 C.paste(town,V.crop(route10,6,17,5,3),2,24);C.fill(town,3,27,7,28,0x3195)
 C.paste(town,V.crop(pew,12,12,7,5),20,8)
 C.paste(town,V.crop(route10,6,17,5,3),12,3);C.fill(town,13,6,16,8,0x3195)
 # ICE PATH has solid snow around short native sliding strips; no falling-ice scripts.
 icebase=V.layout_array(s,'LAYOUT_FOUR_ISLAND_ICEFALL_CAVE_1F')
 def cave(w,h):
  a=[[0x0691]*w for _ in range(h)];C.fill(a,2,2,w-2,h-2,0x3281);return a
 one=cave(28,24)
 C.fill(one,7,10,21,13,0x334b);C.fill(one,7,9,21,10,0x0691)
 C.fill(one,7,13,21,14,0x0691)
 one[21][4]=icebase[17][3];one[3][22]=icebase[12][12]
 lower=cave(28,24)
 C.fill(lower,7,10,21,13,0x334b);C.fill(lower,7,9,21,10,0x0691)
 C.fill(lower,7,13,21,14,0x0691)
 lower[3][22]=0x3296;lower[20][4]=0x32af
 deepest=cave(28,24);deepest[3][22]=0x3296;deepest[21][4]=icebase[17][3]
 # Clear native invisible-walls in the central dragon training area.
 gym=V.layout_array(s,'LAYOUT_FUCHSIA_CITY_GYM')
 C.fill(gym,1,3,14,20,0x3281)
 den=cave(30,26)
 C.fill(den,7,6,23,18,0x133a);C.fill(den,13,4,17,22,0x3281)
 C.fill(den,20,7,22,10,lambda x,y:0x131b if x%2==0 else 0x131c)
 C.fill(den,3,19,27,22,0x3281);den[23][15]=icebase[17][3]
 den[5][15]=icebase[6][3]
 shrine=V.layout_array(s,'LAYOUT_SAFARI_ZONE_SECRET_HOUSE')
 return {'JohtoRoute44':r44,'IcePath_1F':one,'IcePath_B1F':lower,'IcePath_B2F':deepest,
  'BlackthornCity':town,'BlackthornCity_Gym':gym,'DragonDen_1F':den,'DragonDen_Shrine':shrine}

def blackthorn_story():
 scripts={};texts={}
 def add(n,k,body):
  scripts.setdefault(n,n+'_MapScripts::\n    .byte 0\n')
  scripts[n]+='\n'+n+'_'+k+'::\n'+body.strip()+'\n'
 def say(n,k,paras):
  add(n,k,'    msgbox '+n+'_Text_'+k+', MSGBOX_NPC\n    end')
  texts.setdefault(n,{})[k]=paras
 def trainer(n,k,intro,defeat,after):
  add(n,k,'    trainerbattle_single TRAINER_JOHTO_'+k+', '+n+'_Text_'+k+'Intro, '+n+'_Text_'+k+'Defeat\n    msgbox '+n+'_Text_'+k+'After, MSGBOX_NPC\n    end')
  texts.setdefault(n,{}).update({k+'Intro':[intro],k+'Defeat':[defeat],k+'After':[after]})
 n='JohtoRoute44'
 add(n,'WestGate','''
    lockall
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, JohtoRoute44_WestGateOpen
    msgbox JohtoRoute44_Text_WestGateClosed
    applymovement OBJ_EVENT_ID_PLAYER, JohtoRoute44_WestGateBack
    waitmovement 0
    releaseall
    end
JohtoRoute44_WestGateOpen::
    setvar VAR_TEMP_0, 1
    releaseall
    end
JohtoRoute44_WestGateBack:
    walk_left
    step_end
''')
 say(n,'Warden',["The ROCKET broadcast has ended.\nLANCE checked this eastern road.",
  "ICE PATH links us to BLACKTHORN.\nCarry healing supplies with you."])
 texts[n]['WestGateClosed']=["LANCE needs your help first.\nPlease clear the RADIO TOWER."]
 trainer(n,'WILTON',"The lake is peaceful again.\nLet's see your POKEMON!","That was a strong partnership!","The dragons beyond ICE PATH\nneed patient training.")
 trainer(n,'VANCE',"My bird has crossed every\nmountain path in JOHTO!","Your partner outpaced my bird!","BLACKTHORN's GYM uses dragons.\nIce attacks can help you.")
 n='IcePath_B2F'
 add(n,'WaterfallKeeper','''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_ICE_PATH_WATERFALL_REWARDED, IcePath_B2F_WaterfallAfter
    goto_if_unset FLAG_JOHTO_RADIO_TOWER_CLEARED, IcePath_B2F_WaterfallBefore
    checkitem ITEM_HM07
    goto_if_eq VAR_RESULT, TRUE, IcePath_B2F_WaterfallAlternate
    checkpcitem ITEM_HM07
    goto_if_eq VAR_RESULT, TRUE, IcePath_B2F_WaterfallAlternate
    goto_if_set FLAG_HIDE_FOUR_ISLAND_ICEFALL_CAVE_1F_HM07, IcePath_B2F_WaterfallAlternate
    goto_if_set FLAG_HOENN_GOT_WALLACE_WATERFALL_REWARD, IcePath_B2F_WaterfallAlternate
    giveitem ITEM_HM07
    goto_if_eq VAR_RESULT, FALSE, IcePath_B2F_WaterfallFull
    setflag FLAG_JOHTO_ICE_PATH_WATERFALL_REWARDED
    msgbox IcePath_B2F_Text_WaterfallNew
    release
    end
IcePath_B2F_WaterfallAlternate::
    giveitem ITEM_TM50
    goto_if_eq VAR_RESULT, FALSE, IcePath_B2F_WaterfallFull
    setflag FLAG_JOHTO_ICE_PATH_WATERFALL_REWARDED
    msgbox IcePath_B2F_Text_WaterfallAlternate
    release
    end
IcePath_B2F_WaterfallBefore::
    msgbox IcePath_B2F_Text_WaterfallBefore
    release
    end
IcePath_B2F_WaterfallAfter::
    msgbox IcePath_B2F_Text_WaterfallAfter
    release
    end
IcePath_B2F_WaterfallFull::
    msgbox IcePath_B2F_Text_WaterfallFull
    release
    end
''')
 texts[n]={'WaterfallNew':["You helped clear RADIO TOWER.\nPlease take WATERFALL with you.",
  "JOHTO's RISINGBADGE permits its\nuse outside battle."],
 'WaterfallAlternate':["You already received WATERFALL.\nHere is OVERHEAT instead.",
  "You do not need another copy\nof the same Hidden Machine."],
 'WaterfallBefore':["LANCE is checking the east road.\nPlease clear the RADIO TOWER."],
 'WaterfallAfter':["WATERFALL can scale the rapids\nwith JOHTO's RISINGBADGE."],
 'WaterfallFull':["There is no room for this gift.\nI will keep it until you return."]}
 n='BlackthornCity'
 say(n,'DragonGuide',["CLAIR trains in the dragon GYM.\nHer elder lives in DRAGON'S DEN.",
  "A victory proves your strength.\nThe elder tests your care."])
 say(n,'LeagueGuide',["JOHTO's final badge is awarded\nafter the DRAGON'S DEN trial.",
  "Finish this challenge first.\nThe LEAGUE follows beyond JOHTO."])
 n='BlackthornCity_Gym'
 trainer(n,'ALLEN',"Can your partner handle a\nwell-trained dragon?","Your trust made the difference!","CLAIR will test that trust\nagainst her KINGDRA.")
 trainer(n,'FRAN',"Our dragons train for years.\nShow me your resolve!","Your partner refused to give up!","The elder values your choices\nas much as your battle skills.")
 add(n,'Clair','''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_BADGE08_GET, BlackthornCity_Gym_ClairAfter
    goto_if_set FLAG_JOHTO_CLAIR_DEFEATED, BlackthornCity_Gym_ClairTrial
    goto_if_unset FLAG_JOHTO_BADGE07_GET, BlackthornCity_Gym_ClairBefore
    goto_if_unset FLAG_JOHTO_RADIO_TOWER_CLEARED, BlackthornCity_Gym_ClairBefore
    goto_if_defeated TRAINER_JOHTO_CLAIR, BlackthornCity_Gym_ClairVictory
    trainerbattle_single TRAINER_JOHTO_CLAIR, BlackthornCity_Gym_Text_ClairIntro, BlackthornCity_Gym_Text_ClairDefeat, BlackthornCity_Gym_ClairVictory, NO_MUSIC
    goto BlackthornCity_Gym_ClairVictory
BlackthornCity_Gym_ClairVictory::
    setflag FLAG_JOHTO_CLAIR_DEFEATED
BlackthornCity_Gym_ClairTrial::
    msgbox BlackthornCity_Gym_Text_ClairTrial
    release
    end
BlackthornCity_Gym_ClairBefore::
    msgbox BlackthornCity_Gym_Text_ClairBefore
    release
    end
BlackthornCity_Gym_ClairAfter::
    msgbox BlackthornCity_Gym_Text_ClairAfter
    release
    end
''')
 texts.setdefault(n,{}).update({'ClairIntro':["CLAIR: You silenced the ROCKETS.\nNow face my dragon partners!",
  "This final GYM challenge will\ntest the bond you have built."],
 'ClairDefeat':["You won... But a trainer needs\nmore than strength alone."],
 'ClairTrial':["Meet the elder in DRAGON'S DEN.\nAccept his test with honesty.",
  "After his approval, I will\nrecognize your final badge."],
 'ClairBefore':["Finish PRYCE's GYM challenge.\nThen silence the RADIO TOWER."],
 'ClairAfter':["The elder recognized your bond.\nYou earned the RISINGBADGE.",
  "Stay worthy of the trust your\nPOKEMON place in you."]})
 n='DragonDen_1F'
 add(n,'TrialGate','''
    lockall
    goto_if_set FLAG_JOHTO_CLAIR_DEFEATED, DragonDen_1F_TrialGateOpen
    msgbox DragonDen_1F_Text_TrialGateClosed
    applymovement OBJ_EVENT_ID_PLAYER, DragonDen_1F_TrialGateBack
    waitmovement 0
    releaseall
    end
DragonDen_1F_TrialGateOpen::
    releaseall
    warp MAP_DRAGON_DEN_SHRINE, 1
    waitstate
    end
DragonDen_1F_TrialGateBack:
    walk_down
    step_end
''')
 texts[n]={'TrialGateClosed':["The elder accepts challengers\nafter CLAIR acknowledges them."]}
 n='DragonDen_Shrine'
 add(n,'DragonMaster','''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_DRAGON_TRIAL_CLEARED, DragonDen_Shrine_DragonMasterReward
    goto_if_unset FLAG_JOHTO_CLAIR_DEFEATED, DragonDen_Shrine_DragonMasterBefore
    msgbox DragonDen_Shrine_Text_DragonMasterQuestion, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, FALSE, DragonDen_Shrine_DragonMasterReflect
    setflag FLAG_JOHTO_DRAGON_TRIAL_CLEARED
    setflag FLAG_JOHTO_BADGE08_GET
    msgbox DragonDen_Shrine_Text_DragonMasterAccepted
DragonDen_Shrine_DragonMasterReward::
    goto_if_set FLAG_JOHTO_CLAIR_TM02_RECEIVED, DragonDen_Shrine_DragonMasterAfter
    giveitem ITEM_TM02
    goto_if_eq VAR_RESULT, FALSE, DragonDen_Shrine_DragonMasterFull
    setflag FLAG_JOHTO_CLAIR_TM02_RECEIVED
DragonDen_Shrine_DragonMasterAfter::
    msgbox DragonDen_Shrine_Text_DragonMasterAfter
    release
    end
DragonDen_Shrine_DragonMasterBefore::
    msgbox DragonDen_Shrine_Text_DragonMasterBefore
    release
    end
DragonDen_Shrine_DragonMasterReflect::
    msgbox DragonDen_Shrine_Text_DragonMasterReflect
    release
    end
DragonDen_Shrine_DragonMasterFull::
    msgbox DragonDen_Shrine_Text_DragonMasterFull
    release
    end
''')
 texts[n]={'DragonMasterQuestion':["You traveled through KANTO and\nstood against the ROCKETS here.",
  "Will you listen to your POKEMON\nand care for them as partners?"],
 'DragonMasterAccepted':["Your answer honors your partner.\nCLAIR accepts my judgment.",
  "You earned JOHTO's RISINGBADGE.\nAll eight badges are now yours."],
 'DragonMasterReflect':["Think about your partner's care.\nThen answer me honestly again."],
 'DragonMasterBefore':["First meet CLAIR in the GYM.\nA battle begins this final test."],
 'DragonMasterAfter':["DRAGON CLAW is CLAIR's gift.\nKeep your promise to your team.",
  "The LEAGUE judges your battles.\nYour partner recalls your care."],
 'DragonMasterFull':["Your RISINGBADGE is yours.\nMake room for DRAGON CLAW.",
  "I will keep the TM safe.\nYou do not need another battle."]}
 return scripts,texts

def build(s):
 # JOHTO_LEAGUE_EXTENSION_GUARD
 if any(n not in OLD + NEW for n in s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]):
  raise RuntimeError("Johto League extension exists; use build_johto_league.py")
 out={};stats={'chapter':'Ice Path and Blackthorn final badge trial',
  'save_layout_changed':False,'native_build_and_emulator':'NOT_RUN_BY_GENERATOR',
  'visual_limits':['Native Kanto tiles and class portraits are reused.','ICE PATH contains a compact main route and short native sliding strips; the original falling-ice puzzle is not reproduced.'],
  'not_implemented':['Johto League','Route45/46 optional southern return route','Full original Ice Path boulder puzzle']}
 groups=s.json('data/maps/map_groups.json');assert groups['gMapGroup_JohtoEntry'] in (OLD,OLD+NEW)
 for k,v in groups.items():
  if k not in ('group_order','gMapGroup_JohtoEntry'):assert not(set(v)&set(NEW))
 assert len(OLD+NEW)<=128 and len(groups['group_order'])<=128,'native signed WarpData map IDs exhausted; append another group without changing the save ABI'
 groups['gMapGroup_JohtoEntry']=OLD+NEW;out['data/maps/map_groups.json']=enc(groups)
 arrays=blackthorn_geometry(s);ls=s.json('data/layouts/layouts.json')
 templates={'JohtoRoute44':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),
  'BlackthornCity':('General','SaffronCity','LAYOUT_SAFFRON_CITY'),
  'BlackthornCity_Gym':('Building','FuchsiaGym','LAYOUT_FUCHSIA_CITY_GYM'),
  'DragonDen_Shrine':('Building','SafariZoneBuilding','LAYOUT_SAFARI_ZONE_SECRET_HOUSE')}
 for n in ['IcePath_1F','IcePath_B1F','IcePath_B2F','DragonDen_1F']:
  templates[n]=('General','SeafoamIslands','LAYOUT_FOUR_ISLAND_ICEFALL_CAVE_1F')
 for n,a in arrays.items():
  primary,secondary,old=templates[n];t=next(v for v in ls['layouts'] if v.get('id')==old)
  row={'id':'LAYOUT_'+ident(n),'name':n+'_Layout','width':len(a[0]),'height':len(a),
   'border_width':2,'border_height':2,'primary_tileset':'gTileset_'+primary,'secondary_tileset':'gTileset_'+secondary,
   'blockdata_filepath':'data/layouts/'+n+'/map.bin','border_filepath':'data/layouts/'+n+'/border.bin'}
  hits=[v for v in ls['layouts'] if v.get('id')==row['id']];assert not hits or hits==[row]
  if not hits:ls['layouts'].append(row)
  out[row['blockdata_filepath']]=C.pack(a);out[row['border_filepath']]=s.read(t['border_filepath'])
 out['data/layouts/layouts.json']=enc(ls);maps={};scripts,rows=blackthorn_story();tx={n:C.texts(n,d) for n,d in rows.items()}
 def temp(n,old,section,music=None):
  j=s.json('data/maps/'+old+'/map.json');j.update(id=MID[n],name=n,region_map_section=section,connections=None)
  j.pop('connections_no_include',None)
  if n in arrays:j['layout']='LAYOUT_'+ident(n)
  if music:j['music']=music
  for key in ['object_events','warp_events','coord_events','bg_events']:j[key]=[]
  maps[n]=j;return j
 def coord(x,y,script):
  return {'type':'trigger','x':x,'y':y,'elevation':0,'var':'VAR_TEMP_0','var_value':'0','script':script}
 n='JohtoRoute44';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE44','MUS_ROUTE1')
 j['connections']=[{'map':'MAP_MAHOGANY_TOWN','direction':'left','offset':0}]
 j['warp_events']=[warp(40,5,'IcePath_1F',0,0)]
 j['object_events']=[obj('POLICEMAN',5,17,n+'_Warden'),obj('MAN',12,12,n+'_WILTON'),obj('MAN',31,11,n+'_VANCE')]
 j['coord_events']=[coord(1,y,n+'_WestGate') for y in range(15,19)]
 for n,old in [('IcePath_1F','FourIsland_IcefallCave_1F'),('IcePath_B1F','FourIsland_IcefallCave_B1F'),('IcePath_B2F','FourIsland_IcefallCave_B1F')]:
  j=temp(n,old,'MAPSEC_ICE_PATH','MUS_MT_MOON')
  j['requires_flash']=False;j['map_type']='MAP_TYPE_UNDERGROUND'
  if n=='IcePath_1F':j['warp_events']=[warp(4,21,'JohtoRoute44',0,0),warp(22,3,'IcePath_B1F',0)]
  elif n=='IcePath_B1F':j['warp_events']=[warp(22,3,'IcePath_1F',1),warp(4,20,'IcePath_B2F',0)]
  else:
   j['warp_events']=[warp(22,3,'IcePath_B1F',1),warp(4,21,'BlackthornCity',3,0)]
   j['object_events']=[obj('HIKER',10,17,n+'_WaterfallKeeper')]
 n='BlackthornCity';j=temp(n,'SaffronCity','MAPSEC_BLACKTHORN_CITY','MUS_LAVENDER')
 j['warp_events']=[warp(7,22,'BlackthornCity_PokemonCenter_1F',1,0),warp(24,21,'BlackthornCity_Mart',1,0),
  warp(23,12,'BlackthornCity_Gym',1,0),warp(4,26,'IcePath_B2F',1,0),warp(14,5,'DragonDen_1F',0,0)]
 j['object_events']=[obj('OLD_MAN_1',12,18,n+'_DragonGuide'),obj('MAN',18,24,n+'_LeagueGuide')]
 for suf in ['PokemonCenter_1F','PokemonCenter_2F']:
  n='BlackthornCity_'+suf
  rep=lambda t:t.replace('MAHOGANY_TOWN','BLACKTHORN_CITY').replace('MAHOGANY','BLACKTHORN').replace('MahoganyTown','BlackthornCity')
  j=json.loads(rep(s.text('data/maps/MahoganyTown_'+suf+'/map.json')));assert j['id']==MID[n]
  j['region_map_section']='MAPSEC_BLACKTHORN_CITY';maps[n]=j
  scripts[n]=rep(s.text('data/maps/MahoganyTown_'+suf+'/scripts.inc'));tx[n]=rep(s.text('data/maps/MahoganyTown_'+suf+'/text.inc'))
  if suf=='PokemonCenter_1F':
   j['object_events'][0]['local_id']='LOCALID_BLACKTHORN_NURSE'
   for wp in j['warp_events'][:3]:wp['dest_warp_id']='0'
 n='BlackthornCity_Mart';j=temp(n,'SaffronCity_Mart','MAPSEC_BLACKTHORN_CITY','MUS_POKE_CENTER')
 j['warp_events']=[warp(x,7,'BlackthornCity',1) for x in (3,4,5)]
 j['object_events']=[obj('CLERK',2,3,n+'_Clerk',elevation=0,movement='FACE_RIGHT')]
 scripts[n]=n+'_MapScripts::\n    .byte 0\n\n'+n+'_Clerk::\n    lock\n    faceplayer\n    message Text_MayIHelpYou\n    waitmessage\n    pokemart '+n+'_Items\n    msgbox Text_PleaseComeAgain, MSGBOX_DEFAULT\n    release\n    end\n'+n+'_Items:\n    .2byte ITEM_ULTRA_BALL\n    .2byte ITEM_HYPER_POTION\n    .2byte ITEM_FULL_HEAL\n    .2byte ITEM_REVIVE\n    .2byte ITEM_MAX_REPEL\n    .2byte ITEM_NONE\n    .align 2\n'
 n='BlackthornCity_Gym';j=temp(n,'FuchsiaCity_Gym','MAPSEC_BLACKTHORN_CITY','MUS_GYM')
 j['warp_events']=[warp(x,21,'BlackthornCity',2) for x in (6,7,8)]
 j['object_events']=[obj('COOLTRAINER_M',4,12,n+'_ALLEN'),obj('COOLTRAINER_F',10,10,n+'_FRAN'),obj('WOMAN_1',7,5,n+'_Clair')]
 n='DragonDen_1F';j=temp(n,'FourIsland_IcefallCave_1F','MAPSEC_DRAGON_DEN','MUS_MT_MOON')
 j['requires_flash']=False;j['map_type']='MAP_TYPE_UNDERGROUND'
 j['warp_events']=[warp(15,23,'BlackthornCity',4,0),warp(15,5,'DragonDen_Shrine',1)]
 j['coord_events']=[coord(15,5,n+'_TrialGate')]
 n='DragonDen_Shrine';j=temp(n,'SafariZone_SecretHouse','MAPSEC_DRAGON_DEN','MUS_PALLET')
 j['warp_events']=[warp(x,9,'DragonDen_1F',1) for x in (3,4,5)]
 j['object_events']=[obj('OLD_MAN_1',6,5,n+'_DragonMaster')]
 for n,j in maps.items():
  out['data/maps/'+n+'/map.json']=enc(j);out['data/maps/'+n+'/scripts.inc']=scripts.get(n,n+'_MapScripts::\n    .byte 0\n').encode()
  out['data/maps/'+n+'/text.inc']=tx.get(n,'@ Native shared dialogue.\n').encode()
 # Extend only the existing east road; preserve every previous Mahogany object and warp.
 p='data/maps/MahoganyTown/map.json';town=s.json(p);con={'map':MID['JohtoRoute44'],'direction':'right','offset':0}
 assert not town.get('connections_no_include')
 if con not in town['connections']:
  assert not any(v['direction']=='right' for v in town['connections']);town['connections'].append(con)
 out[p]=enc(town);layout=next(v for v in ls['layouts'] if v.get('id')==town['layout'])
 a=V.layout_array(s,town['layout']);base=M.mahogany_geometry(s)['MahoganyTown'];patched=copy.deepcopy(base)
 C.fill(patched,28,15,32,19,0x3195);assert a in (base,patched),'Existing Mahogany terrain changed outside this owned corridor'
 out[layout['blockdata_filepath']]=C.pack(patched)
 heals=s.json('src/data/heal_locations.json')
 row={'id':'HEAL_LOCATION_BLACKTHORN_CITY','map':MID['BlackthornCity'],'x':7,'y':23,
  'respawn_map':MID['BlackthornCity_PokemonCenter_1F'],'respawn_npc':'LOCALID_BLACKTHORN_NURSE'}
 hits=[v for v in heals['heal_locations'] if v['id']==row['id']];assert not hits or hits==[row]
 if not hits:heals['heal_locations'].append(row)
 out['src/data/heal_locations.json']=enc(heals)
 shared(s,out);region(s,out)
 stats.update(new_maps=NEW,new_flags=FLAGS,trainer_ids={v[0]:v[-1] for v in TRAINERS},johto_map_count=len(OLD+NEW))
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
 else:assert not additions,('incomplete Blackthorn flags',additions)
 out[p]=t.encode()
 p='include/constants/opponents_johto_blackthorn.h'
 h='#ifndef GUARD_OPPONENTS_JOHTO_BLACKTHORN_H\n#define GUARD_OPPONENTS_JOHTO_BLACKTHORN_H\n'
 for n,c,pic,gender,party,num in TRAINERS:h+='#define TRAINER_JOHTO_'+n+' (HOENN_TRAINERS_START + '+str(num)+')\n'
 out[p]=(h+'#endif\n').encode()
 for path in (s.root/'include/constants').glob('opponents*.h'):
  rel=path.relative_to(s.root).as_posix()
  if rel==p:continue
  used={int(v,0) for v in re.findall(r'HOENN_TRAINERS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',s.text(rel))}
  assert not(used&{v[-1] for v in TRAINERS}),('trainer collision',rel)
 p='include/constants/opponents.h';anchor='#include "constants/opponents_johto_radio_tower.h"'
 out[p]=C.once(s.text(p),anchor,anchor+'\n#include "constants/opponents_johto_blackthorn.h"','Blackthorn trainer include').encode()
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
 out['src/data/trainer_parties_johto_blackthorn.h']=parties.encode();out['src/data/trainers_johto_blackthorn.h']=trainers.encode()
 for p,a,inc in [('src/data/trainers.h','#include "trainers_johto_radio_tower.h"','#include "trainers_johto_blackthorn.h"'),('src/data/trainer_parties.h','#include "trainer_parties_johto_radio_tower.h"','#include "trainer_parties_johto_blackthorn.h"')]:
  out[p]=C.once(s.text(p),a,a+'\n'+inc,'Blackthorn trainer data').encode()
 p='data/event_scripts.s';t=s.text(p);block='@ '+MARK+'\n'+''.join('    .include "data/maps/'+n+'/'+f+'"\n' for n in NEW for f in ['scripts.inc','text.inc'])
 if MARK not in t:assert not any('data/maps/'+n+'/' in t for n in NEW);t=t.rstrip()+'\n\n'+block
 else:assert block in t
 out[p]=t.encode()
 p='tools/johto/build_radio_tower.py';t=s.text(p)
 guard=' # BLACKTHORN_EXTENSION_GUARD\n if any(n not in OLD + NEW for n in s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]):\n  raise RuntimeError("Blackthorn extension exists; use build_blackthorn.py")\n'
 if '# BLACKTHORN_EXTENSION_GUARD' not in t:
  t,n=re.subn(r'(?m)^def build\(s\):\n',lambda m:m.group(0)+guard,t);assert n==1
 else:assert guard in t
 out[p]=t.encode()
 # Enable the actual next road only after this chapter has its maps and guarded access.
 p='tools/johto/build_mahogany.py';t=s.text(p)
 before='The RADIO TOWER is safe again.\nLANCE is checking the east road.'
 after='The RADIO TOWER is safe again.\nThe road to BLACKTHORN is open.'
 t=C.once(t,json.dumps(before),json.dumps(after),'Blackthorn road source')
 out[p]=t.encode()
 p='data/maps/MahoganyTown/text.inc'
 out[p]=C.once(s.text(p),C.texts('MahoganyTown',{'EastOpen':[before]}),C.texts('MahoganyTown',{'EastOpen':[after]}),'Blackthorn road dialogue').encode()
 # The older Radio generator also owns that dialogue: stop it after this append.
 # Waterfall outside battle now uses the newly earned Johto badge, preserving both legacy regions.
 p='src/field_control_avatar.c';t=s.text(p)
 old='''bool8 CanUseWaterfallAtCurrentMap(void)
{
    if (IsNamedHoennMapSec(gMapHeader.regionMapSectionId))
        return FlagGet(FLAG_HOENN_BADGE08_GET);
    return FlagGet(FLAG_BADGE07_GET);
}'''
 new='''bool8 CanUseWaterfallAtCurrentMap(void)
{
    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_NEW_BARK_TOWN))
        return FlagGet(FLAG_JOHTO_BADGE08_GET);
    if (IsNamedHoennMapSec(gMapHeader.regionMapSectionId))
        return FlagGet(FLAG_HOENN_BADGE08_GET);
    return FlagGet(FLAG_BADGE07_GET);
}'''
 out[p]=C.once(t,old,new,'Johto final Waterfall badge').encode()
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
 specs=[('JOHTO_ROUTE44','ROUTE 44',14,1,5,1),('ICE_PATH','ICE PATH',19,1,1,1),
  ('BLACKTHORN_CITY','BLACKTHORN CITY',20,1,1,1),('DRAGON_DEN',"DRAGON'S DEN",20,0,1,1)]
 for key,label,x,y,w,h in specs:
  row={'id':'MAPSEC_'+key,'name':label,'x':x,'y':y,'width':w,'height':h}
  hits=[v for v in j['map_sections'] if v.get('id')==row['id']];assert not hits or hits==[row]
  if not hits:j['map_sections'].append(row)
 assert [v.get('id') for v in j['map_sections'][:len(original)]]==[v.get('id') for v in original]
 assert len(j['map_sections'])<256,'native u8 map-section paths need a separate widening before this append'
 out[p]=enc(j)
 for p in ['src/region_map.c','src/pokemon_summary_screen.c']:
  t=s.text(p);pat=r'(MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP[\s\S]{0,140}?<=\s*)MAPSEC_JOHTO_ROCKET_HQ'
  if re.search(pat,t):t,n=re.subn(pat,lambda m:m.group(1)+'MAPSEC_DRAGON_DEN',t);assert n==1
  else:assert re.search(pat.replace('MAPSEC_JOHTO_ROCKET_HQ','MAPSEC_DRAGON_DEN'),t)
  out[p]=t.encode()
 p='src/region_map.c';t=out[p].decode()
 if '// BLACKTHORN_MAP_GRID_V1' not in t:
  pat=r'(?m)^([ \t]*)// MAHOGANY_MAP_GRID_V1'
  lines=['// BLACKTHORN_MAP_GRID_V1','if (layer != LAYER_MAP)','    return MAPSEC_NONE;',
   'if (x >= 14 && x <= 18 && y == 1)','    return MAPSEC_JOHTO_ROUTE44;',
   'if (x == 19 && y == 1)','    return MAPSEC_ICE_PATH;',
   'if (x == 20 && y == 1)','    return MAPSEC_BLACKTHORN_CITY;',
   'if (x == 20 && y == 0)','    return MAPSEC_DRAGON_DEN;','// MAHOGANY_MAP_GRID_V1']
  t,n=re.subn(pat,lambda m:'\n'.join(m.group(1)+v for v in lines),t);assert n==1
 assert '// MAHOGANY_FLY_DESTINATION_V1' in t,'verified Mahogany Fly support must precede Blackthorn'
 block='''// BLACKTHORN_FLY_DESTINATION_V1
static const struct JohtoFlyDestination sBlackthornFlyDestination = {
    MAPSEC_BLACKTHORN_CITY, FLAG_JOHTO_CLAIR_DEFEATED,
    FLAG_JOHTO_BADGE08_GET, {MAP(MAP_BLACKTHORN_CITY), HEAL_LOCATION_BLACKTHORN_CITY}, 7, 23
};

'''
 anchor='static const struct JohtoFlyDestination *GetJohtoFlyDestination(u16 mapsec)'
 if '// BLACKTHORN_FLY_DESTINATION_V1' not in t:t=C.once(t,anchor,block+anchor,'Blackthorn Fly constant')
 else:assert block in t
 anchor='''    if (mapsec == MAPSEC_MAHOGANY_TOWN)
        return &sMahoganyFlyDestination;
'''
 branch=anchor+'''    if (mapsec == MAPSEC_BLACKTHORN_CITY)
        return &sBlackthornFlyDestination;
'''
 t=C.once(t,anchor,branch,'Blackthorn Fly lookup');out[p]=t.encode()
 p='graphics/region_map/johto_entry.bin';a=list(struct.unpack('<600H',s.read(p)))
 for _,_,x,y,w,h in specs:
  for ry in range(y,y+h):
   for rx in range(x,x+w):
    assert 0<=rx+4<30 and 0<=ry+4<16
    a[(ry+4)*30+rx+4]=0x1001 if w==h==1 else 0x100a
 out[p]=struct.pack('<600H',*a)
 areas=[('Route44','johtoRoute44',['MAP_JOHTO_ROUTE44']),
  ('IcePath','johtoIcePath',['MAP_ICE_PATH_1F','MAP_ICE_PATH_B1F','MAP_ICE_PATH_B2F']),
  ('DragonDen','johtoDragonDen',['MAP_DRAGON_DEN_1F'])]
 p='src/wild_pokemon_area.c';t=s.text(p)
 if 'bool8 johtoRoute44;' not in t:
  t,n=re.subn(r'(bool8\s+johtoLakeOfRage\s*;)',lambda m:m.group(1)+''.join('\n    bool8 '+f+';' for _,f,_ in areas),t);assert n==1
 if 'MAP_GROUP(MAP_JOHTO_ROUTE44)' not in t:
  pat=r'(?s)(if\s*\(header->mapGroup\s*==\s*MAP_GROUP\(MAP_LAKE_OF_RAGE\)\s*&&\s*header->mapNum\s*==\s*MAP_NUM\(MAP_LAKE_OF_RAGE\)\s*\)\s*\{\s*habitats->johtoLakeOfRage\s*=\s*TRUE;\s*continue;\s*\})'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n            '+m.group(1).replace('MAP_LAKE_OF_RAGE',mn).replace('johtoLakeOfRage',f) for _,f,maps in areas for mn in maps),t);assert n==1
 if 'habitats.johtoRoute44 || habitats.johtoIcePath' not in t:
  t,n=re.subn(r'(if\s*\([^\n]*habitats\.johtoRoute29[^\n]*habitats\.johtoLakeOfRage)\)',lambda m:m.group(1)+' || '+' || '.join('habitats.'+f for _,f,_ in areas)+')',t);assert n==1
 if 'GetJohtoRoute44AreaMarkerSubsprite(areaCount++, subsprites);' not in t:
  pat=r'(if\s*\(habitats\.johtoLakeOfRage\)\s*GetJohtoLakeOfRageAreaMarkerSubsprite\(areaCount\+\+,\s*subsprites\);)'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n        if (habitats.'+f+')\n            GetJohto'+key+'AreaMarkerSubsprite(areaCount++, subsprites);' for key,f,_ in areas),t);assert n==1
 out[p]=t.encode()
 p='include/pokedex_area_markers.h';t=s.text(p)
 if 'GetJohtoRoute44AreaMarkerSubsprite' not in t:
  t,n=re.subn(r'(void GetJohtoLakeOfRageAreaMarkerSubsprite\([^;]*;)',lambda m:m.group(1)+''.join('\nvoid GetJohto'+key+'AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);' for key,_,_ in areas),t);assert n==1
 out[p]=t.encode()
 p='src/pokedex_area_markers.c';t=s.text(p)
 for key,shape,x,y in [('Route44','SmallHorizontal',96,7),('IcePath','Circular',114,7),('DragonDen','Circular',120,1)]:
  name='GetJohto'+key+'AreaMarkerSubsprite'
  body='void '+name+'(s32 i, struct Subsprite *subsprites)\n{\n    if (subsprites == NULL)\n        return;\n    subsprites[i] = sSubsprite_'+shape+';\n    subsprites[i].x = '+str(x)+' + (HOENN_AREA_MAP_LEFT * 8 - 104);\n    subsprites[i].y = '+str(y)+';\n}'
  if re.search(r'void\s+'+name+r'\(',t):t=C.replace_function(t,name,body,'Blackthorn habitat marker')
  else:t=t.rstrip()+'\n\n'+body+'\n'
 out[p]=t.encode()
 p='src/pokedex_screen.c';t=s.text(p)
 labels=[('Black','BLACK'),('Ice','ICE'),('Den','DEN'),('R44','44')]
 if 'sText_JohtoBlack[]' not in t:
  anchor='static const u8 sText_JohtoHQ[] = _("HQ");\n'
  t=C.once(t,anchor,anchor+''.join('static const u8 sText_Johto'+k+'[] = _("'+v+'");\n' for k,v in labels),'Blackthorn habitat labels')
 name='DexScreen_DrawJohtoEntryArea';m=re.search(r'static void '+name+r'\([^{}]*\)\s*\{',t);assert m
 start=m.start();depth=1;i=m.end()
 while depth:
  depth+=(t[i]=='{')-(t[i]=='}');i+=1
 old=t[start:i]
 if '// BLACKTHORN_DEX_DIAGRAM_V1' not in old:
  additions='    // BLACKTHORN_DEX_DIAGRAM_V1\n'
  for _,_,x,y,w,h in specs:
   x,y,w,h=x*5+9,y*6+1,max(4,(w-1)*5+4),max(4,(h-1)*6+4)
   assert 0<=x and x+w<=122 and 0<=y and y+h<=68
   additions+='    FillWindowPixelRect(windowId, PIXEL_FILL(3), '+', '.join(map(str,[x,y,w,h]))+');\n'
   additions+='    FillWindowPixelRect(windowId, PIXEL_FILL(5), '+', '.join(map(str,[x+1,y+1,max(1,w-2),max(1,h-2)]))+');\n'
  for key,x,y in [('Black',94,18),('Ice',104,9),('Den',102,0),('R44',84,9)]:
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
  assert not label.startswith('Em'),'Blackthorn maps retain native Kanto tiles'
  folder=re.sub(r'([A-Za-z])(\d)',r'\1_\2',re.sub(r'([a-z0-9])([A-Z])',r'\1_\2',label)).lower()
  b=final.read('data/tilesets/'+kind+'/'+folder+'/metatile_attributes.bin');i=t if kind=='primary' else t-num
  assert (i+1)*4<=len(b),(label,t,'metatile attribute bounds')
  return struct.unpack_from('<I',b,i*4)[0]&0x1ff
 starts={'JohtoRoute44':(0,16),'IcePath_1F':(4,20),'IcePath_B1F':(22,4),
  'IcePath_B2F':(22,4),'BlackthornCity':(7,23),'BlackthornCity_PokemonCenter_1F':(7,7),
  'BlackthornCity_Mart':(4,7),'BlackthornCity_Gym':(7,20),'DragonDen_1F':(15,22),'DragonDen_Shrine':(4,8)}
 checks=[];checked=0
 for n,m in maps.items():
  l=ls[m['layout']];w,h=l['width'],l['height'];raw=final.read(l['blockdata_filepath']);assert len(raw)==w*h*2
  assert (w+15)*(h+14)<=0x2800,(n,'field map buffer exceeded')
  assert not m.get('connections_no_include'),'native connections must not be disabled'
  a=struct.unpack('<'+'H'*(w*h),raw)
  for wp in m['warp_events']:
   x,y=wp['x'],wp['y'];assert 0<=x<w and 0<=y<h,(n,'warp bounds',wp)
   b=behavior(l,a[y*w+x])
   flank=b==values['MB_NORMAL'] and any(v['dest_map']==wp['dest_map'] and v['dest_warp_id']==wp['dest_warp_id'] and v['y']==y and abs(v['x']-x)==1 and behavior(l,a[y*w+v['x']]) in warp_b for v in m['warp_events'])
   assert b in warp_b or flank,(n,wp,hex(a[y*w+x]),hex(b),'warp lacks native behavior')
   dst_name=next((v for v in NEW if MID[v]==wp['dest_map']),None)
   if dst_name is None:
    allowed=['UnionRoom','TradeCenter'] if n.endswith('PokemonCenter_2F') else ['MahoganyTown']
    matches=[final.json('data/maps/'+name+'/map.json') for name in allowed if final.json('data/maps/'+name+'/map.json')['id']==wp['dest_map']]
    assert len(matches)==1,(n,'unknown preserved destination',wp);dst=matches[0]
   else:dst=maps[dst_name]
   assert 0<=int(wp['dest_warp_id'])<len(dst['warp_events']),(n,'invalid destination warp ID',wp);checked+=1
  inherited_objects=[];inherited_portals=[]
  if n.endswith('PokemonCenter_2F'):
   old_pc=s.json('data/maps/MahoganyTown_PokemonCenter_2F/map.json')
   assert m['layout']==old_pc['layout'];old_layout=ls[old_pc['layout']]
   assert raw==s.read(old_layout['blockdata_filepath']),'native link-room geometry changed'
   rep=lambda t:t.replace('MAHOGANY_TOWN','BLACKTHORN_CITY').replace('MAHOGANY','BLACKTHORN').replace('MahoganyTown','BlackthornCity')
   expected=json.loads(rep(json.dumps(old_pc)));expected['region_map_section']='MAPSEC_BLACKTHORN_CITY'
   assert m==expected,'native link-room map metadata/events changed'
   for file in ['scripts.inc','text.inc']:
    assert final.text('data/maps/'+n+'/'+file)==rep(s.text('data/maps/MahoganyTown_PokemonCenter_2F/'+file)),'native service source changed'
   inherited_objects=expected['object_events'];inherited_portals=[p for p in expected['warp_events'] if p['dest_map'] in ('MAP_UNION_ROOM','MAP_TRADE_CENTER')]
   assert len(inherited_portals)==2
  def walk(x,y):
   if not(0<=x<w and 0<=y<h):return False
   t=a[y*w+x];return (t>>10)&3==0
  start=starts.get(n)
  if start is None:start=next((wp['x'],wp['y']+1) for wp in m['warp_events'] if walk(wp['x'],wp['y']+1))
  assert walk(*start),(n,'start blocked',start)
  elev=a[start[1]*w+start[0]]>>12;elev=3 if elev==15 else elev
  blocked={(o['x'],o['y']) for o in m['object_events']}
  q=deque([(start[0],start[1],elev)]);states=set(q);seen={start}
  while q:
   x,y,z=q.popleft()
   for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if not walk(xx,yy) or (xx,yy) in blocked:continue
    t=a[yy*w+xx];ez=t>>12
    surf=(behavior(l,t) in water_b or behavior(l,a[y*w+x]) in water_b) and {z,ez}<={0,1,3}
    if z!=0 and ez not in (0,15,z) and not surf:continue
    nz=z if ez==15 else ez;state=(xx,yy,nz)
    if state not in states:states.add(state);seen.add((xx,yy));q.append(state)
  for wp in m['warp_events']:
   loc=(wp['x'],wp['y']+1) if n in ('JohtoRoute44','BlackthornCity') else (wp['x'],wp['y'])
   assert loc in seen or wp in inherited_portals,(n,'native warp inaccessible',wp,loc)
  for o in m['object_events']:
   x,y=o['x'],o['y'];assert 0<=x<w and 0<=y<h
   if o in inherited_objects:continue
   if o['graphics_id']=='OBJ_EVENT_GFX_NURSE':assert (x,y+2) in seen;continue
   if o['graphics_id']=='OBJ_EVENT_GFX_CLERK':
    assert (x+2,y) in seen and behavior(l,a[y*w+x+1])==values['MB_COUNTER'],'native shop counter inaccessible';continue
   assert walk(x,y) and any(pos in seen for pos in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),(n,'NPC inaccessible',o)
   if 'local_id' in o:assert isinstance(o['local_id'],str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',o['local_id'])
  for co in m['coord_events']:assert (co['x'],co['y']) in seen,(n,'coordinate gate inaccessible',co)
  if n=='JohtoRoute44':assert all((0,y) in seen for y in range(15,19))
  if n.startswith('IcePath'):
   forbidden={values[n] for n in ['MB_THIN_ICE','MB_CRACKED_ICE','MB_FALL_WARP']}
   assert not any(behavior(l,t) in forbidden for t in a),'Ice Path requires no unsupported falling-ice map callbacks'
  checks.append({'map':n,'reachable_tiles':len(seen),'buffer_metatiles':(w+15)*(h+14),'native_warps':len(m['warp_events'])})
 before=s.json('data/maps/map_groups.json');after=final.json('data/maps/map_groups.json')
 assert after['gMapGroup_JohtoEntry']==OLD+NEW
 assert all(after[k]==v for k,v in before.items() if k!='gMapGroup_JohtoEntry')
 old_ls=s.json('data/layouts/layouts.json')['layouts'];assert final.json('data/layouts/layouts.json')['layouts'][:len(old_ls)]==old_ls
 old=s.json('data/maps/MahoganyTown/map.json');new=final.json('data/maps/MahoganyTown/map.json')
 assert all(old[k]==new[k] for k in old if k!='connections')
 con={'map':MID['JohtoRoute44'],'direction':'right','offset':0}
 assert new['connections']==old['connections'] if con in old['connections'] else new['connections']==old['connections']+[con]
 l=ls[old['layout']];a0=s.read(l['blockdata_filepath']);a1=final.read(l['blockdata_filepath'])
 for y in range(l['height']):
  for x in range(l['width']):
   i=(y*l['width']+x)*2
   assert a0[i:i+2]==a1[i:i+2] or (28<=x<32 and 15<=y<19),'existing Mahogany terrain changed outside eastern corridor'
 assert not any(p in out for p in ['include/global.h','include/pokemon.h','src/save.c','src/load_save.c','src/title_screen.c','src/intro.c'])
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
 glob=final.text('include/global.h')
 trainer_bytes=int(re.search(r'u8\s+hoennTrainerFlags\[(0x[0-9A-Fa-f]+|\d+)\]',glob).group(1),0)
 story_bytes=int(re.search(r'u8\s+hoennFlags\[(0x[0-9A-Fa-f]+|\d+)\]',glob).group(1),0)
 offset=int(re.search(r'JOHTO_STORY_FLAGS_START\s+\(HOENN_FLAGS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)\)',final.text('include/constants/flags_johto_story.h')).group(1),0)
 assert max(v[-1] for v in TRAINERS)<trainer_bytes*8 and offset+max(FLAGS.values())<story_bytes*8
 gym=out['data/maps/BlackthornCity_Gym/scripts.inc'].decode()
 assert 'BlackthornCity_Gym_ClairVictory, NO_MUSIC' in gym and 'goto BlackthornCity_Gym_ClairVictory' in gym
 assert 'setflag FLAG_JOHTO_BADGE08_GET' not in gym and 'setflag FLAG_JOHTO_CLAIR_DEFEATED' in gym
 trial=out['data/maps/DragonDen_Shrine/scripts.inc'].decode()
 assert trial.index('setflag FLAG_JOHTO_BADGE08_GET')<trial.index('giveitem ITEM_TM02')
 assert 'goto_if_eq VAR_RESULT, FALSE, DragonDen_Shrine_DragonMasterFull\n    setflag FLAG_JOHTO_CLAIR_TM02_RECEIVED' in trial
 waterfall=out['data/maps/IcePath_B2F/scripts.inc'].decode()
 assert all(token in waterfall for token in ['checkitem ITEM_HM07','checkpcitem ITEM_HM07','FLAG_HIDE_FOUR_ISLAND_ICEFALL_CAVE_1F_HM07','FLAG_HOENN_GOT_WALLACE_WATERFALL_REWARD','giveitem ITEM_TM50'])
 assert waterfall.count('setflag FLAG_JOHTO_ICE_PATH_WATERFALL_REWARDED')==2
 for n in set(WILD)|set(WATER):
  row=json.loads(out['tools/johto/'+n.lower()+'_wild.json'])
  if n in WILD:assert all(len(row[k]['mons'])==12 for k in ['land_mons','land_mons_morning','land_mons_night'])
  if n in WATER:assert len(row['water_mons']['mons'])==5
 for p,b in final.used.items():
  if p not in out and p not in s.overlay:s.used[p]=b
 stats.update(static_checks=checks,native_warp_behaviors_checked=checked,
  map_sections_max=len(final.json('src/data/region_map/region_map_sections.json')['map_sections'])-1,
  fly_destinations_total=10,saved_story_last_offset=offset+max(FLAGS.values()),saved_trainer_last_offset=max(v[-1] for v in TRAINERS))
 return stats


def apply(root,mutate=False):
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 s=Source(root);out,stats=build(s);validate(s,out,stats)
 repeat,_=build(Source(root,dict(s.overlay,**out)));assert repeat==out,'Blackthorn generator output is not idempotent'
 owned=[p for p in out if any(p.startswith('data/maps/'+n+'/') or p.startswith('data/layouts/'+n+'/') for n in NEW)]
 owned+=['include/constants/opponents_johto_blackthorn.h','src/data/trainers_johto_blackthorn.h','src/data/trainer_parties_johto_blackthorn.h']
 for p in owned:
  if s.exists(p):assert s.read(p)==out[p],('owned Blackthorn artifact differs',p)
 changed={p:b for p,b in out.items() if not s.exists(p) or s.read(p)!=b}
 print(json.dumps({'apply':mutate,'files':sorted(changed),'validation':stats},indent=2))
 if not mutate or not changed:return
 for p,b in s.used.items():assert (root/p).read_bytes()==b,('concurrent source edit',p)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=root/'outputs/johto-blackthorn-v1'/stamp;dest.mkdir(parents=True,exist_ok=False);manifest={'time':stamp,'validation':stats,'files':{}}
 for p,b in changed.items():
  target=root/p;old=target.read_bytes() if target.exists() else None
  manifest['files'][p]={'before':sha(old) if old is not None else None,'after':sha(b)}
  if old is not None:
   backup=dest/'before'/p;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(old)
 (dest/'manifest.json').write_bytes(enc(manifest))
 for p,b in changed.items():
  target=root/p;target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.blackthorn.tmp')
  assert not tmp.exists();tmp.write_bytes(b);tmp.replace(target)
 print('APPLIED',dest/'manifest.json')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root).resolve(),a.apply)
