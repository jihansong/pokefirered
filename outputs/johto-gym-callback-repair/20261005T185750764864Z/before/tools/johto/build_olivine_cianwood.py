#!/usr/bin/env python3
"""Append Ecruteak -> Olivine -> Cianwood and the lighthouse rescue; dry run by default."""
import argparse,copy,datetime,json,re,struct,subprocess,sys,textwrap
from collections import deque
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_ecruteak as E
C,V=E.C,E.V
Source,enc,sha=E.Source,E.enc,E.sha
OLD=E.OLD+E.NEW
NEW=['EcruteakCity_WestGate','JohtoRoute38','JohtoRoute39','OlivineCity','OlivineCity_PokemonCenter_1F','OlivineCity_PokemonCenter_2F','OlivineCity_Mart','OlivineCity_Gym']+['OlivineLighthouse_'+str(i)+'F' for i in range(1,7)]+['JohtoRoute40','JohtoRoute41','CianwoodCity','CianwoodCity_PokemonCenter_1F','CianwoodCity_PokemonCenter_2F','CianwoodCity_Pharmacy','CianwoodCity_Gym','OlivineCity_Cafe']
IDS=['ECRUTEAK_CITY_WEST_GATE','JOHTO_ROUTE38','JOHTO_ROUTE39','OLIVINE_CITY','OLIVINE_CITY_POKEMON_CENTER_1F','OLIVINE_CITY_POKEMON_CENTER_2F','OLIVINE_CITY_MART','OLIVINE_CITY_GYM']+['OLIVINE_LIGHTHOUSE_'+str(i)+'F' for i in range(1,7)]+['JOHTO_ROUTE40','JOHTO_ROUTE41','CIANWOOD_CITY','CIANWOOD_CITY_POKEMON_CENTER_1F','CIANWOOD_CITY_POKEMON_CENTER_2F','CIANWOOD_CITY_PHARMACY','CIANWOOD_CITY_GYM','OLIVINE_CITY_CAFE']
MID=dict(zip(NEW,['MAP_'+x for x in IDS]))
MARK='JOHTO_OLIVINE_CIANWOOD_CHAPTER_V1'
FLAGS={'FLAG_JOHTO_BADGE05_GET':20,'FLAG_JOHTO_BADGE06_GET':21,'FLAG_JOHTO_LIGHTHOUSE_MEDICINE_REQUESTED':35,'FLAG_JOHTO_CIANWOOD_MEDICINE_RECEIVED':36,'FLAG_JOHTO_AMPHY_CURED':37,'FLAG_JOHTO_GOT_TM01_FROM_CHUCK':38,'FLAG_JOHTO_FLY_REWARDED':39,'FLAG_JOHTO_GOT_TM23_FROM_JASMINE':40,'FLAG_HIDE_JOHTO_JASMINE_GYM':41,'FLAG_JOHTO_STRENGTH_REWARDED':42}
TRAINERS=[
 ('CHAD','SCHOOL_KID','YOUNGSTER','MALE',[('MR_MIME',22)],817),
 ('DEREK','POKEMANIAC','POKEMANIAC','MALE',[('PIKACHU',23)],818),
 ('PRESTON','GENTLEMAN','GENTLEMAN','MALE',[('GROWLITHE',22),('GROWLITHE',24)],819),
 ('HUEY','SAILOR','SAILOR','MALE',[('POLIWAG',22),('POLIWHIRL',24)],820),
 ('ERNEST','SAILOR','SAILOR','MALE',[('MACHOP',25),('MACHOKE',25),('POLIWHIRL',25)],821),
 ('RANDALL','SWIMMER_M','SWIMMER_M','MALE',[('SHELLDER',24),('WARTORTLE',24)],822),
 ('DENISE','SWIMMER_F','SWIMMER_F','FEMALE',[('SEEL',25)],823),
 ('YOSHI','BLACK_BELT','BLACK_BELT','MALE',[('HITMONLEE',27)],824),
 ('CHUCK','LEADER','BLACK_BELT','MALE',[('PRIMEAPE',27,['LEER','RAGE','KARATE_CHOP','FURY_SWIPES']),('POLIWRATH',30,['HYPNOSIS','SURF','DYNAMIC_PUNCH','BODY_SLAM'])],825),
 ('JASMINE','LEADER','BEAUTY','FEMALE',[('MAGNEMITE',30,['THUNDERBOLT','SUPERSONIC','SONIC_BOOM','THUNDER_WAVE']),('MAGNEMITE',30,['THUNDERBOLT','SUPERSONIC','SONIC_BOOM','THUNDER_WAVE']),('STEELIX',35,['ROCK_THROW','SUNNY_DAY','IRON_TAIL','SCREECH'])],826)]
WILD={
 'JohtoRoute38':(['RATTATA','MEOWTH','MAGNEMITE','FARFETCHD','RATICATE','MEOWTH','MAGNEMITE','TAUROS','MILTANK','SNUBBULL','TAUROS','MILTANK'],['RATTATA','MEOWTH','MAGNEMITE','NOCTOWL','RATICATE','MEOWTH','MAGNEMITE','TAUROS','MILTANK','SNUBBULL','NOCTOWL','MILTANK'],[16,16,16,16,17,17,17,17,17,16,18,18]),
 'JohtoRoute39':(['RATTATA','MEOWTH','MAGNEMITE','FARFETCHD','RATICATE','MEOWTH','MAGNEMITE','TAUROS','MILTANK','PIDGEOTTO','TAUROS','MILTANK'],['RATTATA','MEOWTH','MAGNEMITE','NOCTOWL','RATICATE','MEOWTH','MAGNEMITE','TAUROS','MILTANK','NOCTOWL','TAUROS','MILTANK'],[16,16,16,16,17,17,17,17,17,18,18,18])}
WATER={
 'JohtoRoute40':(['TENTACOOL','TENTACOOL','TENTACOOL','TENTACRUEL','TENTACRUEL'],[20,21,22,25,25]),
 'JohtoRoute41':(['TENTACOOL','TENTACOOL','TENTACOOL','TENTACRUEL','MANTINE'],[20,21,22,25,25])}
def ident(n):return IDS[NEW.index(n)]
def warp(x,y,dst,index,elevation=3):
 return {'x':x,'y':y,'elevation':elevation,'dest_map':MID.get(dst,dst),'dest_warp_id':str(index)}
def obj(gfx,x,y,script,**kw):
 flag=kw.pop('flag','0');v=C.obj(gfx,x,y,script,**kw);v['flag']=flag;return v
def geometry(s):
 vir=V.layout_array(s,'LAYOUT_VIRIDIAN_CITY');pew=V.layout_array(s,'LAYOUT_PEWTER_CITY');saff=V.layout_array(s,'LAYOUT_SAFFRON_CITY')
 def land(w,h):
  a=[[0x3001]*w for _ in range(h)]
  for box in [(0,0,w,2),(0,0,2,h),(w-2,0,w,h),(0,h-2,w,h)]:C.fill(a,*box,C.dense)
  return a
 r38=land(40,24);C.fill(r38,0,10,38,14,0x3195)
 C.paste(r38,V.crop(vir,24,8,5,4),33,6)
 for box in [(5,3,14,9),(18,3,29,9),(7,16,16,21),(24,16,32,21)]:C.fill(r38,*box,C.grass)
 r39=land(24,32);C.fill(r39,8,12,12,32,0x3195);C.fill(r39,8,14,24,18,0x3195)
 for box in [(3,4,7,12),(14,4,21,12),(14,20,21,28)]:C.fill(r39,*box,C.grass)
 C.fill(r39,3,20,7,28,0x3004)
 oliv=land(44,40);C.fill(oliv,18,0,22,34,0x3195);C.fill(oliv,0,24,38,28,0x3195);C.fill(oliv,4,31,38,34,0x3195)
 C.paste(oliv,V.crop(saff,22,34,5,5),5,15);C.paste(oliv,V.crop(vir,34,16,4,4),13,15)
 C.paste(oliv,V.crop(pew,12,12,7,5),25,3)
 C.paste(oliv,V.crop(saff,21,11,5,4),5,5);C.fill(oliv,4,9,20,11,0x3195)
 # Native Silph facade is kept within its own Saffron secondary tileset.
 C.paste(oliv,V.crop(saff,29,16,9,15),28,12)
 C.fill(oliv,3,34,41,40,0x112b);C.fill(oliv,3,33,41,34,0x3115)
 for x,y in [(11,19),(18,18),(33,7),(38,26),(11,8)]:oliv[y][x]=0x0403
 r40=[[0x112b]*24 for _ in range(36)]
 C.fill(r40,19,0,24,25,0x3115);C.fill(r40,21,0,24,25,0x3001)
 C.fill(r40,18,16,24,20,0x3195)
 r41=[[0x112b]*32 for _ in range(28)]
 # Small offshore rest islands do not block the sea route.
 C.fill(r41,9,6,13,9,0x3115);C.fill(r41,22,15,27,18,0x3115)
 cian=land(28,36);C.fill(cian,23,0,28,36,0x112b);C.fill(cian,21,0,23,36,0x3115)
 C.fill(cian,3,14,22,18,0x3195);C.fill(cian,8,3,12,32,0x3195)
 C.paste(cian,V.crop(saff,22,34,5,5),3,20)
 C.paste(cian,V.crop(saff,21,11,5,4),14,20)
 C.paste(cian,V.crop(pew,12,12,7,5),6,3)
 for x,y in [(9,24),(20,23),(14,7)]:cian[y][x]=0x0403
 gate=V.layout_array(s,'LAYOUT_ROUTE2_ENTRANCE')
 arrays={'EcruteakCity_WestGate':copy.deepcopy(gate),'JohtoRoute38':r38,'JohtoRoute39':r39,
 'OlivineCity':oliv,'JohtoRoute40':r40,'JohtoRoute41':r41,'CianwoodCity':cian}
 # Five intermediate floors and a top chamber use native staircase behaviors.
 for i,k in enumerate([1,2,3,4,5,7],1):arrays['OlivineLighthouse_'+str(i)+'F']=V.layout_array(s,'LAYOUT_POKEMON_TOWER_'+str(k)+'F')
 return arrays
def story():
 scripts={};texts={}
 def add(n,k,body):
  scripts.setdefault(n,n+'_MapScripts::\n    .byte 0\n');scripts[n]+='\n'+n+'_'+k+'::\n'+body.strip()+'\n'
 def say(n,k,paras):add(n,k,'    msgbox '+n+'_Text_'+k+', MSGBOX_NPC\n    end');texts.setdefault(n,{})[k]=paras
 def trainer(n,k,lines):
  add(n,k,'    trainerbattle_single TRAINER_JOHTO_'+k+', '+n+'_Text_'+k+'Intro, '+n+'_Text_'+k+'Defeat\n    msgbox '+n+'_Text_'+k+'After, MSGBOX_NPC\n    end')
  texts.setdefault(n,{}).update({k+'Intro':[lines[0]],k+'Defeat':[lines[1]],k+'After':[lines[2]]})
 def hm(n,k,number,alt,receipt,preflag=None):
  body='    lock\n    faceplayer\n    goto_if_set '+receipt+', '+n+'_'+k+'After\n'
  if preflag:body+='    goto_if_unset '+preflag+', '+n+'_'+k+'Before\n'
  body+='    goto_if_set FLAG_GOT_HM'+number+', '+n+'_'+k+'Alternate\n    checkitem ITEM_HM'+number+'\n    goto_if_eq VAR_RESULT, TRUE, '+n+'_'+k+'Alternate\n    checkpcitem ITEM_HM'+number+', 1\n    goto_if_eq VAR_RESULT, TRUE, '+n+'_'+k+'Alternate\n    giveitem ITEM_HM'+number+'\n    goto_if_eq VAR_RESULT, FALSE, '+n+'_'+k+'Full\n    setflag FLAG_GOT_HM'+number+'\n    setflag '+receipt+'\n    msgbox '+n+'_Text_'+k+'HM\n    release\n    end\n'+n+'_'+k+'Alternate::\n    giveitem ITEM_TM'+alt+'\n    goto_if_eq VAR_RESULT, FALSE, '+n+'_'+k+'Full\n    setflag '+receipt+'\n    msgbox '+n+'_Text_'+k+'Alternate\n    release\n    end\n'
  for suffix in ['Before','Full','After']:body+=n+'_'+k+suffix+'::\n    msgbox '+n+'_Text_'+k+suffix+'\n    release\n    end\n'
  add(n,k,body);texts.setdefault(n,{}).update({k+'Before':["Finish CHUCK's GYM challenge.\nThen come back to see me."],k+'Full':["There is no room for this gift.\nMake space and speak to me again."],k+'After':["Travel safely. Your earlier\ntraining is still useful here."]})
 n='EcruteakCity_WestGate'
 say(n,'Officer',["West is OLIVINE, a port town.\nIts lighthouse guides the ferries.","MORTY's BADGE authorizes SURF\nin JOHTO. Learn the move first."])
 n='JohtoRoute38';trainer(n,'CHAD',["I watch how POKeMON learn.","I learned something new!","Your journey has taught them\nmore than my books ever could."])
 say(n,'RouteSign',["ROUTE 38\nECRUTEAK CITY - OLIVINE CITY"])
 n='JohtoRoute39';trainer(n,'DEREK',["My PIKACHU and I train here.","That was a good battle!","Some travelers arrived from\nKANTO. They share what they know."])
 say(n,'FarmHand',["These MILTANK rest between trips.\nThe port needs healthy partners.","JASMINE is caring for a sick\nAMPHAROS at the lighthouse."])
 say(n,'RouteSign',["ROUTE 39\nSouth: OLIVINE CITY"])
 n='OlivineCity'
 say(n,'DockWorker',["The lighthouse has gone dim.\nFerries cannot sail safely.","The west beach leads to ROUTE 40.\nSURF to CIANWOOD for medicine."])
 say(n,'GymGuide',["JASMINE left to tend AMPHY.\nFind her at the lighthouse top."])
 say(n,'CenterSign',["OLIVINE POKeMON CENTER"])
 say(n,'MartSign',["OLIVINE POKeMON MART"])
 say(n,'GymSign',["OLIVINE GYM\nJASMINE - the steel-clad leader"])
 say(n,'LighthouseSign',["OLIVINE LIGHTHOUSE\nKeep the lamp shining."])
 say(n,'CafeSign',["OLIVINE CAFE\nSailors share stories and skills."])
 n='OlivineCity_Cafe';hm(n,'StrengthGift','04','08','FLAG_JOHTO_STRENGTH_REWARDED')
 texts[n].update({'StrengthGiftHM':["A sailor needs strong partners.\nThis HM teaches STRENGTH."],'StrengthGiftAlternate':["You already have STRENGTH. Keep\nyour HM and take TM08 BULK UP!"]})
 for i,k in [(2,'PRESTON'),(3,'HUEY'),(4,'ERNEST')]:
  n='OlivineLighthouse_'+str(i)+'F';trainer(n,k,["We train while the lamp is tended.","Your light shines brightly.","JASMINE is upstairs. AMPHY\nneeds medicine from CIANWOOD."])
 n='OlivineLighthouse_1F';say(n,'Keeper',["Climb the stairs to the top.\nJASMINE is with the lighthouse lamp."])
 n='OlivineLighthouse_5F';say(n,'Sailor',["AMPHY powers the lamp. The light\nconnects the islands to this port.","The pharmacy across the sea can\nhelp. JASMINE will explain."])
 n='OlivineLighthouse_6F'
 add(n,'Jasmine',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_AMPHY_CURED, OlivineLighthouse_6F_JasmineAfter
    goto_if_set FLAG_JOHTO_CIANWOOD_MEDICINE_RECEIVED, OlivineLighthouse_6F_Cure
    showmonpic SPECIES_AMPHAROS, 10, 3
    playmoncry SPECIES_AMPHAROS, CRY_MODE_NORMAL
    waitmoncry
    msgbox OlivineLighthouse_6F_Text_Request
    hidemonpic
    setflag FLAG_JOHTO_LIGHTHOUSE_MEDICINE_REQUESTED
    release
    end
OlivineLighthouse_6F_Cure::
    msgbox OlivineLighthouse_6F_Text_Deliver
    showmonpic SPECIES_AMPHAROS, 10, 3
    playmoncry SPECIES_AMPHAROS, CRY_MODE_NORMAL
    waitmoncry
    msgbox OlivineLighthouse_6F_Text_Healthy
    hidemonpic
    setflag FLAG_JOHTO_AMPHY_CURED
    clearflag FLAG_HIDE_JOHTO_JASMINE_GYM
    msgbox OlivineLighthouse_6F_Text_Return
    removeobject 1
    release
    end
OlivineLighthouse_6F_JasmineAfter::
    msgbox OlivineLighthouse_6F_Text_After
    release
    end
''')
 texts.setdefault(n,{}).update({'Request':["AMPHY is sick. I cannot leave\nwhile the lamp is unwell.","Please ask the CIANWOOD pharmacy\nfor a sealed dose of medicine.","MORTY's BADGE permits SURF here.\nThe west beach is the sea route."],
 'Deliver':["You brought the sealed medicine!\nThank you. I'll give it to AMPHY."],
 'Healthy':["AMPHY: Pharos!","The lighthouse lamp shines again."],
 'Return':["The harbor is safe again.\nI'll return to OLIVINE GYM.","First meet CHUCK across the sea.\nThen we can have our GYM battle."],
 'After':["AMPHY is healthy again.\nI'll be waiting at OLIVINE GYM."]})
 n='JohtoRoute40';trainer(n,'RANDALL',["The sea is our training ground.","A strong current carried you!","The coast goes south to ROUTE 41.\nCIANWOOD is west from there."])
 n='JohtoRoute41';trainer(n,'DENISE',["Can your team cross this sea?","You navigated that battle well.","Land lies to the west. Bring the\nmedicine safely back to OLIVINE."])
 n='CianwoodCity'
 say(n,'Resident',["The pharmacy has medicines\nthat ordinary MARTS do not carry.","Your journey between these ports\nwill restore the lighthouse."])
 say(n,'CenterSign',["CIANWOOD POKeMON CENTER"])
 say(n,'PharmacySign',["CIANWOOD PHARMACY\nMedicine for POKeMON partners"])
 say(n,'GymSign',["CIANWOOD GYM\nCHUCK - his fists do the talking"])
 hm(n,'FlyGift','02','02','FLAG_JOHTO_FLY_REWARDED','FLAG_JOHTO_BADGE05_GET')
 texts[n].update({'FlyGiftHM':["This HM teaches FLY. It will\nmake the return trip easier."],
 'FlyGiftAlternate':["You already have FLY from KANTO.\nKeep that HM. Take DRAGON CLAW!"]})
 n='CianwoodCity_Pharmacy'
 add(n,'Pharmacist',r'''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_AMPHY_CURED, CianwoodCity_Pharmacy_After
    goto_if_set FLAG_JOHTO_CIANWOOD_MEDICINE_RECEIVED, CianwoodCity_Pharmacy_Carrying
    goto_if_unset FLAG_JOHTO_LIGHTHOUSE_MEDICINE_REQUESTED, CianwoodCity_Pharmacy_Before
    msgbox CianwoodCity_Pharmacy_Text_Give
    setflag FLAG_JOHTO_CIANWOOD_MEDICINE_RECEIVED
    release
    end
CianwoodCity_Pharmacy_Carrying::
    msgbox CianwoodCity_Pharmacy_Text_Carrying
    release
    end
CianwoodCity_Pharmacy_Before::
    msgbox CianwoodCity_Pharmacy_Text_Before
    release
    end
CianwoodCity_Pharmacy_After::
    msgbox CianwoodCity_Pharmacy_Text_After
    release
    end
''')
 texts.setdefault(n,{}).update({'Give':["A sick AMPHAROS powers OLIVINE's\nlamp? Take this sealed medicine.","Deliver it straight to JASMINE.\nThe dose is reserved for AMPHY."],
 'Carrying':["You already carry AMPHY's dose.\nPlease deliver it to JASMINE."],
 'Before':["I prepare special medicines.\nTell me which POKeMON needs help."],
 'After':["AMPHY recovered? Wonderful.\nThe islands can travel safely."]})
 for n,k,badge,tm,receipt,prereqs in [
 ('CianwoodCity_Gym','CHUCK','FLAG_JOHTO_BADGE05_GET','01','FLAG_JOHTO_GOT_TM01_FROM_CHUCK',['FLAG_JOHTO_BADGE04_GET']),
 ('OlivineCity_Gym','JASMINE','FLAG_JOHTO_BADGE06_GET','23','FLAG_JOHTO_GOT_TM23_FROM_JASMINE',['FLAG_JOHTO_AMPHY_CURED','FLAG_JOHTO_BADGE05_GET'])]:
  body='    lock\n    faceplayer\n    goto_if_set '+badge+', '+n+'_Reward\n'
  for f in prereqs:body+='    goto_if_unset '+f+', '+n+'_NotReady\n'
  body+='    trainerbattle_single TRAINER_JOHTO_'+k+', '+n+'_Text_Intro, '+n+'_Text_Defeat\n    setflag '+badge+'\n    msgbox '+n+'_Text_Badge\n'+n+'_Reward::\n    goto_if_set '+receipt+', '+n+'_After\n    giveitem ITEM_TM'+tm+'\n    goto_if_eq VAR_RESULT, FALSE, '+n+'_BagFull\n    setflag '+receipt+'\n    msgbox '+n+'_Text_TM\n    release\n    end\n'
  for suffix in ['NotReady','BagFull','After']:body+=n+'_'+suffix+'::\n    msgbox '+n+'_Text_'+suffix+'\n    release\n    end\n'
  add(n,k,body)
  texts.setdefault(n,{}).update({'Intro':["You crossed the sea and helped\nthis region. Show me your strength."],
 'Defeat':["Your partners have true strength."],
 'Badge':["Take this JOHTO GYM BADGE."],
 'TM':["This TM is a gift for your team."],
 'NotReady':["Finish the earlier challenge.\nWe should battle in the right order."],
 'BagFull':["Your BADGE is yours. Make room\nfor the TM and speak to me again."],
 'After':["Your journey connects people\nand POKeMON beyond this port."]})
 texts['CianwoodCity_Gym'].update({'Intro':["So you seek my STORMBADGE?\nMy POKeMON train as hard as I do!"],'Badge':["You earned the STORMBADGE!"],'TM':["TM01 teaches FOCUS PUNCH.\nIt rewards careful timing."],'NotReady':["Earn MORTY's FOGBADGE first.\nThen train with me."]})
 texts['OlivineCity_Gym'].update({'Intro':["Thank you for saving AMPHY.\nNow let my steel partners battle."],'Badge':["You earned the MINERALBADGE!"],'TM':["TM23 teaches IRON TAIL.\nCarry our thanks on your journey."],'NotReady':["AMPHY needs help first.\nThen earn CHUCK's STORMBADGE."]})
 trainer('CianwoodCity_Gym','YOSHI',["Training tempers our spirit.","Your spirit held strong.","CHUCK is waiting at the back."])
 n='OlivineCity_Gym'
 scripts[n]=scripts[n].replace(n+'_MapScripts::\n    .byte 0',n+'_MapScripts::\n    map_script MAP_SCRIPT_ON_LOAD, '+n+'_OnLoad\n    .byte 0',1)
 add(n,'OnLoad',r'''
    goto_if_set FLAG_JOHTO_AMPHY_CURED, OlivineCity_Gym_ShowJasmine
    setflag FLAG_HIDE_JOHTO_JASMINE_GYM
    end
OlivineCity_Gym_ShowJasmine::
    clearflag FLAG_HIDE_JOHTO_JASMINE_GYM
    end
''')
 say(n,'Guide',["JASMINE tends the sick lamp.\nClimb the lighthouse to find her.","Once AMPHY is well and CHUCK's\nchallenge is done, return here."])
 for n in NEW:scripts.setdefault(n,n+'_MapScripts::\n    .byte 0\n');texts.setdefault(n,{})
 # HARBOR_CURED_DIALOGUE_V1
 for n,k,paras in [
  ('OlivineCity','DockWorker',["AMPHY's light guides us again.\nThe harbor is safe. Thank you!","CIANWOOD and OLIVINE worked\ntogether to save the lamp."]),
  ('OlivineCity','GymGuide',["JASMINE returned to her GYM.\nYour help for AMPHY mattered."]),
  ('OlivineLighthouse_1F','Keeper',["AMPHY's light shines again.\nJASMINE returned to her GYM."]),
  ('OlivineCity_Gym','Guide',["JASMINE returned from the lamp.\nYour help will not be forgotten."])]:
  old='msgbox '+n+'_Text_'+k+', MSGBOX_NPC\n    end'
  assert scripts[n].count(old)==1,(n,k,'NPC dialogue anchor')
  new='    goto_if_set FLAG_JOHTO_AMPHY_CURED, '+n+'_'+k+'Restored\n'+old+'\n'+n+'_'+k+'Restored::\n    msgbox '+n+'_Text_'+k+'Restored, MSGBOX_NPC\n    end'
  scripts[n]=scripts[n].replace(old,new,1);texts[n][k+'Restored']=paras
 for n,d in texts.items():
  for k,paras in d.items():
   d[k]=['\n'.join(v for line in p.split('\n') for v in textwrap.wrap(line,width=32,break_long_words=False,break_on_hyphens=False)) for p in paras]
 return scripts,texts
def build(s):
 out={};stats={'chapter':'Olivine lighthouse rescue, Cianwood and Johto gyms five/six','save_layout_changed':False,'native_build_and_emulator':'NOT_RUN_BY_GENERATOR','visual_limits':['Native Kanto tiles and native trainer portraits are reused.','Lighthouse uses a tall Silph facade and Pokemon Tower stairs; Chuck/Jasmine use native class portraits.','AMPHY is shown with its native species portrait and cry during the medicine event.'],'not_implemented':['Johto gyms seven/eight, Radio Tower takeover and Johto League','Whirl Islands, Lugia encounter and extended lighthouse shortcut']}
 groups=s.json('data/maps/map_groups.json');assert groups['gMapGroup_JohtoEntry'] in (OLD,OLD+NEW)
 for k,v in groups.items():
  if k not in ('group_order','gMapGroup_JohtoEntry'):assert not(set(v)&set(NEW))
 groups['gMapGroup_JohtoEntry']=OLD+NEW;out['data/maps/map_groups.json']=enc(groups)
 arrays=geometry(s);ls=s.json('data/layouts/layouts.json')
 tiles={'EcruteakCity_WestGate':('Building','GenericBuilding2','LAYOUT_ROUTE2_ENTRANCE'),
 'JohtoRoute38':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),'JohtoRoute39':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),
 'OlivineCity':('General','SaffronCity','LAYOUT_SAFFRON_CITY'),'JohtoRoute40':('General','CinnabarIsland','LAYOUT_CINNABAR_ISLAND'),
 'JohtoRoute41':('General','CinnabarIsland','LAYOUT_CINNABAR_ISLAND'),'CianwoodCity':('General','SaffronCity','LAYOUT_SAFFRON_CITY')}
 for i,k in enumerate([1,2,3,4,5,7],1):tiles['OlivineLighthouse_'+str(i)+'F']=('Building','PokemonTower','LAYOUT_POKEMON_TOWER_'+str(k)+'F')
 for n,a in arrays.items():
  primary,secondary,old=tiles[n];template=next(v for v in ls['layouts'] if v.get('id')==old)
  item={'id':'LAYOUT_'+ident(n),'name':n+'_Layout','width':len(a[0]),'height':len(a),'border_width':2,'border_height':2,'primary_tileset':'gTileset_'+primary,'secondary_tileset':'gTileset_'+secondary,'blockdata_filepath':'data/layouts/'+n+'/map.bin','border_filepath':'data/layouts/'+n+'/border.bin'}
  hits=[v for v in ls['layouts'] if v.get('id')==item['id']];assert not hits or hits==[item]
  if not hits:ls['layouts'].append(item)
  out[item['blockdata_filepath']]=C.pack(a);out[item['border_filepath']]=s.read(template['border_filepath'])
 out['data/layouts/layouts.json']=enc(ls);maps={}
 def temp(n,old,section,layout=None,music=None):
  j=s.json('data/maps/'+old+'/map.json');j.update(id=MID[n],name=n,region_map_section=section,connections=None)
  j.pop('connections_no_include',None)
  if layout:j['layout']=layout
  if music:j['music']=music
  for key in ['object_events','warp_events','coord_events','bg_events']:j[key]=[]
  maps[n]=j;return j
 n='EcruteakCity_WestGate';j=temp(n,'Route2_ViridianForest_NorthEntrance','MAPSEC_ECRUTEAK_CITY','LAYOUT_ECRUTEAK_CITY_WEST_GATE')
 j['object_events']=[obj('POLICEMAN',9,3,n+'_Officer')]
 j['warp_events']=[warp(x,10,'MAP_ECRUTEAK_CITY',5) for x in (6,7,8)]+[warp(7,1,'JohtoRoute38',0)]
 n='JohtoRoute38';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE38','LAYOUT_JOHTO_ROUTE38','MUS_ROUTE1')
 j['connections']=[{'map':MID['JohtoRoute39'],'direction':'left','offset':-4}]
 j['warp_events']=[warp(34,9,'EcruteakCity_WestGate',3,0)]
 j['object_events']=[obj('YOUNGSTER',17,12,n+'_CHAD',movement='FACE_LEFT')];j['bg_events']=[C.bg(31,14,n+'_RouteSign')]
 n='JohtoRoute39';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE39','LAYOUT_JOHTO_ROUTE39','MUS_ROUTE1')
 j['connections']=[{'map':MID['JohtoRoute38'],'direction':'right','offset':4},{'map':MID['OlivineCity'],'direction':'down','offset':-10}]
 j['object_events']=[obj('MAN',13,17,n+'_DEREK'),obj('WOMAN_2',5,23,n+'_FarmHand')]
 j['bg_events']=[C.bg(7,29,n+'_RouteSign')]
 n='OlivineCity';j=temp(n,'SaffronCity','MAPSEC_OLIVINE_CITY','LAYOUT_OLIVINE_CITY','MUS_VERMILLION')
 j['connections']=[{'map':MID['JohtoRoute39'],'direction':'up','offset':10},{'map':MID['JohtoRoute40'],'direction':'left','offset':8}]
 j['warp_events']=[warp(7,19,'OlivineCity_PokemonCenter_1F',1,0),warp(15,18,'OlivineCity_Mart',1,0),warp(28,7,'OlivineCity_Gym',1,0),warp(32,26,'OlivineLighthouse_1F',0,0),warp(6,8,'OlivineCity_Cafe',1,0)]
 j['object_events']=[obj('SAILOR',24,25,n+'_DockWorker'),obj('GENTLEMAN',28,9,n+'_GymGuide')]
 j['bg_events']=[C.bg(x,y,n+'_'+k) for x,y,k in [(11,19,'CenterSign'),(18,18,'MartSign'),(33,7,'GymSign'),(38,26,'LighthouseSign'),(11,8,'CafeSign')]]
 n='JohtoRoute40';j=temp(n,'Route20','MAPSEC_JOHTO_ROUTE40','LAYOUT_JOHTO_ROUTE40','MUS_ROUTE24')
 j['connections']=[{'map':MID['OlivineCity'],'direction':'right','offset':-8},{'map':MID['JohtoRoute41'],'direction':'down','offset':0}]
 j['object_events']=[obj('SWIMMER_M_WATER',11,22,n+'_RANDALL',elevation=1)]
 n='JohtoRoute41';j=temp(n,'Route20','MAPSEC_JOHTO_ROUTE41','LAYOUT_JOHTO_ROUTE41','MUS_ROUTE24')
 j['connections']=[{'map':MID['JohtoRoute40'],'direction':'up','offset':0},{'map':MID['CianwoodCity'],'direction':'left','offset':-8}]
 j['object_events']=[obj('SWIMMER_F_WATER',16,16,n+'_DENISE',elevation=1)]
 n='CianwoodCity';j=temp(n,'SaffronCity','MAPSEC_CIANWOOD_CITY','LAYOUT_CIANWOOD_CITY','MUS_CINNABAR')
 j['connections']=[{'map':MID['JohtoRoute41'],'direction':'right','offset':8}]
 j['warp_events']=[warp(5,24,'CianwoodCity_PokemonCenter_1F',1,0),warp(15,23,'CianwoodCity_Pharmacy',1,0),warp(9,7,'CianwoodCity_Gym',1,0)]
 j['object_events']=[obj('WOMAN_2',15,10,n+'_FlyGift'),obj('OLD_MAN_1',13,16,n+'_Resident')]
 j['bg_events']=[C.bg(x,y,n+'_'+k) for x,y,k in [(9,24,'CenterSign'),(20,23,'PharmacySign'),(14,7,'GymSign')]]
 scripts,rows=story();tx={n:C.texts(n,d) for n,d in rows.items()}
 for city in ['OlivineCity','CianwoodCity']:
  for suffix in ['PokemonCenter_1F','PokemonCenter_2F']+(['Mart'] if city=='OlivineCity' else []):
   old='EcruteakCity_'+suffix;n=city+'_'+suffix
   rep=lambda t:t.replace('ECRUTEAK_CITY',re.sub(r'(?<!^)(?=[A-Z])','_',city).upper()).replace('ECRUTEAK',city.replace('City','').upper()).replace('EcruteakCity',city)
   j=json.loads(rep(s.text('data/maps/'+old+'/map.json')));assert j['id']==MID[n];j['region_map_section']='MAPSEC_'+city.replace('City','').upper()+'_CITY';maps[n]=j
   scripts[n]=rep(s.text('data/maps/'+old+'/scripts.inc'));tx[n]=rep(s.text('data/maps/'+old+'/text.inc'))
   if suffix=='PokemonCenter_1F':
    j['object_events'][0]['local_id']='LOCALID_'+city.replace('City','').upper()+'_NURSE'
    for w in j['warp_events'][:3]:w['dest_warp_id']='0'
   elif suffix=='Mart':
    for w in j['warp_events']:w['dest_warp_id']='1'
 n='OlivineCity_Cafe';j=temp(n,'SaffronCity_House','MAPSEC_OLIVINE_CITY',music='MUS_CELADON')
 j['object_events']=[obj('SAILOR',5,3,n+'_StrengthGift')];j['warp_events']=[warp(x,7,'OlivineCity',4) for x in (3,4,5)]
 n='CianwoodCity_Pharmacy';j=temp(n,'SaffronCity_House','MAPSEC_CIANWOOD_CITY',music='MUS_CELADON')
 j['object_events']=[obj('SCIENTIST',5,3,n+'_Pharmacist')];j['warp_events']=[warp(x,7,'CianwoodCity',1) for x in (3,4,5)]
 n='CianwoodCity_Gym';j=temp(n,'SaffronCity_Dojo','MAPSEC_CIANWOOD_CITY',music='MUS_GYM')
 j['object_events']=[obj('BLACK_BELT',6,4,n+'_CHUCK'),obj('BLACK_BELT',8,9,n+'_YOSHI',movement='FACE_LEFT')]
 j['warp_events']=[warp(x,14,'CianwoodCity',2) for x in (5,6,7)]
 n='OlivineCity_Gym';j=temp(n,'PewterCity_Gym','MAPSEC_OLIVINE_CITY',music='MUS_GYM')
 j['object_events']=[obj('WOMAN_1',6,4,n+'_JASMINE',flag='FLAG_HIDE_JOHTO_JASMINE_GYM'),obj('GENTLEMAN',3,11,n+'_Guide')]
 j['warp_events']=[warp(x,14,'OlivineCity',2) for x in (5,6,7)]
 for i,k in enumerate([1,2,3,4,5,7],1):
  n='OlivineLighthouse_'+str(i)+'F';j=temp(n,'PokemonTower_'+str(k)+'F','MAPSEC_OLIVINE_LIGHTHOUSE','LAYOUT_'+ident(n),'MUS_POKE_TOWER')
  if i==1:j['warp_events']=[warp(11,18,'OlivineCity',3),warp(18,9,'OlivineLighthouse_2F',1)]
  elif i==2:j['warp_events']=[warp(4,10,'OlivineLighthouse_3F',0),warp(18,10,'OlivineLighthouse_1F',1)]
  elif i==3:j['warp_events']=[warp(4,10,'OlivineLighthouse_2F',0),warp(18,10,'OlivineLighthouse_4F',1)]
  elif i==4:j['warp_events']=[warp(4,10,'OlivineLighthouse_5F',0),warp(18,10,'OlivineLighthouse_3F',1)]
  elif i==5:j['warp_events']=[warp(4,10,'OlivineLighthouse_4F',0),warp(18,10,'OlivineLighthouse_6F',0)]
  else:j['warp_events']=[warp(11,16,'OlivineLighthouse_5F',1)]
  if i==1:j['object_events']=[obj('OLD_MAN_1',7,14,n+'_Keeper')]
  elif i in (2,3,4):
   x,y={2:(14,12),3:(14,11),4:(12,13)}[i]
   j['object_events']=[obj('GENTLEMAN' if i==2 else 'SAILOR',x,y,n+'_'+{2:'PRESTON',3:'HUEY',4:'ERNEST'}[i])]
  elif i==5:j['object_events']=[obj('SAILOR',12,13,n+'_Sailor')]
  else:j['object_events']=[obj('WOMAN_1',12,9,n+'_Jasmine',flag='FLAG_JOHTO_AMPHY_CURED')]
 for n,j in maps.items():
  out['data/maps/'+n+'/map.json']=enc(j);out['data/maps/'+n+'/scripts.inc']=scripts[n].encode();out['data/maps/'+n+'/text.inc']=tx.get(n,'@ Native shared dialogue.\n').encode()
 p='data/maps/EcruteakCity/map.json';j=s.json(p);wp=warp(1,20,'EcruteakCity_WestGate',1,0)
 assert len(j['warp_events']) in (5,6)
 if len(j['warp_events'])==5:j['warp_events'].append(wp)
 else:assert j['warp_events'][5]==wp
 out[p]=enc(j)
 layout=next(v for v in ls['layouts'] if v.get('id')==j['layout']);a=V.layout_array(s,j['layout'])
 base=E.geometry(s)['EcruteakCity'];patched=copy.deepcopy(base)
 C.paste(patched,V.crop(V.layout_array(s,'LAYOUT_SAFFRON_CITY'),21,11,5,4),0,17)
 C.fill(patched,1,21,3,23,0x3195)
 assert a in (base,patched),'Ecruteak west gate independently edited';out[layout['blockdata_filepath']]=C.pack(patched)
 heals=s.json('src/data/heal_locations.json')
 for city,x,y in [('OlivineCity',7,20),('CianwoodCity',5,25)]:
  stem=city.replace('City','').upper()
  v={'id':'HEAL_LOCATION_'+stem+'_CITY','map':MID[city],'x':x,'y':y,'respawn_map':MID[city+'_PokemonCenter_1F'],'respawn_npc':'LOCALID_'+stem+'_NURSE'}
  hits=[z for z in heals['heal_locations'] if z['id']==v['id']];assert not hits or hits==[v]
  if not hits:heals['heal_locations'].append(v)
 out['src/data/heal_locations.json']=enc(heals)
 shared(s,out);region(s,out);stats.update(new_maps=NEW,new_flags=FLAGS,trainer_ids={v[0]:v[-1] for v in TRAINERS})
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
 p='include/constants/opponents_johto_olivine.h'
 h='#ifndef GUARD_OPPONENTS_JOHTO_OLIVINE_H\n#define GUARD_OPPONENTS_JOHTO_OLIVINE_H\n'
 for n,c,pic,gender,party,num in TRAINERS:h+='#define TRAINER_JOHTO_'+n+' (HOENN_TRAINERS_START + '+str(num)+')\n'
 out[p]=(h+'#endif\n').encode()
 for path in (s.root/'include/constants').glob('opponents*.h'):
  rel=path.relative_to(s.root).as_posix()
  if rel==p:continue
  used={int(v,0) for v in re.findall(r'HOENN_TRAINERS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',s.text(rel))}
  assert not(used&{v[-1] for v in TRAINERS}),('trainer collision',rel)
 p='include/constants/opponents.h';anchor='#include "constants/opponents_johto_ecruteak.h"'
 out[p]=C.once(s.text(p),anchor,anchor+'\n#include "constants/opponents_johto_olivine.h"','Olivine trainer include').encode()
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
  display=n
  trainers+='    [TRAINER_JOHTO_'+n+'] = {\n        .trainerClass = TRAINER_CLASS_'+c+',\n        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_'+gender+(' | F_TRAINER_FEMALE' if gender=='FEMALE' else '')+',\n        .trainerPic = TRAINER_PIC_'+pic+',\n        .trainerName = _("'+display+'"),\n        .items = {},\n        .doubleBattle = FALSE,\n        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,\n        .party = '+('NO_ITEM_CUSTOM_MOVES' if custom else 'NO_ITEM_DEFAULT_MOVES')+'('+sym+'),\n    },\n'
 out['src/data/trainer_parties_johto_olivine.h']=parties.encode();out['src/data/trainers_johto_olivine.h']=trainers.encode()
 for p,a,inc in [('src/data/trainers.h','#include "trainers_johto_ecruteak.h"','#include "trainers_johto_olivine.h"'),('src/data/trainer_parties.h','#include "trainer_parties_johto_ecruteak.h"','#include "trainer_parties_johto_olivine.h"')]:
  out[p]=C.once(s.text(p),a,a+'\n'+inc,'Olivine trainer data').encode()
 p='data/event_scripts.s';t=s.text(p);block='@ '+MARK+'\n'+''.join('    .include "data/maps/'+n+'/'+f+'"\n' for n in NEW for f in ['scripts.inc','text.inc'])
 if MARK not in t:assert not any('data/maps/'+n+'/' in t for n in NEW);t=t.rstrip()+'\n\n'+block
 else:assert block in t
 out[p]=t.encode()
 p='tools/johto/build_ecruteak.py';t=s.text(p)
 guard=' # OLIVINE_EXTENSION_GUARD\n if any(n not in OLD + NEW for n in s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]):\n  raise RuntimeError("Olivine extension exists; use build_olivine_cianwood.py")\n'
 if '# OLIVINE_EXTENSION_GUARD' not in t:
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
 for n,(species,levels) in WATER.items():
  row={'map':MID[n],'base_label':'s'+n,'water_mons':{'encounter_rate':4,'mons':[{'min_level':lv,'max_level':lv,'species':'SPECIES_'+sp} for sp,lv in zip(species,levels)]}}
  out['tools/johto/'+n.lower()+'_wild.json']=enc(row)
  hits=[v for v in gs[0]['encounters'] if v['map']==row['map'] or v['base_label']==row['base_label']]
  assert not hits or hits==[row]
  if not hits:gs[0]['encounters'].append(row)
 out[p]=enc(j)
def region(s,out):
 p='src/data/region_map/region_map_sections.json';j=s.json(p);existing={v['id']:v for v in j['map_sections'] if v.get('id')}
 assert 'MAPSEC_ECRUTEAK_CITY' in existing and 'MAPSEC_BURNED_TOWER' in existing
 # Move only the tower's map marker north of Ecruteak to make room for Route 38.
 tower=existing['MAPSEC_BURNED_TOWER'];assert (tower['x'],tower['y']) in [(4,1),(5,0)]
 tower.update(x=5,y=0)
 specs=[('JOHTO_ROUTE38','ROUTE 38',2,1,3,1),('JOHTO_ROUTE39','ROUTE 39',1,1,1,3),
 ('OLIVINE_CITY','OLIVINE CITY',1,4,1,1),('OLIVINE_LIGHTHOUSE','LIGHTHOUSE',0,4,1,1),
 ('JOHTO_ROUTE40','ROUTE 40',1,5,1,1),('JOHTO_ROUTE41','ROUTE 41',1,6,1,1),('CIANWOOD_CITY','CIANWOOD CITY',0,6,1,1)]
 for key,label,x,y,w,h in specs:
  row={'id':'MAPSEC_'+key,'name':label,'x':x,'y':y,'width':w,'height':h}
  hits=[v for v in j['map_sections'] if v.get('id')==row['id']];assert not hits or hits==[row]
  if not hits:j['map_sections'].append(row)
 original=s.json(p)['map_sections'];assert [v.get('id') for v in j['map_sections'][:len(original)]]==[v.get('id') for v in original]
 out[p]=enc(j)
 for p in ['src/region_map.c','src/pokemon_summary_screen.c']:
  t=s.text(p);pat=r'(MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP[\s\S]{0,120}?<=\s*)MAPSEC_BURNED_TOWER'
  if re.search(pat,t):t,n=re.subn(pat,lambda m:m.group(1)+'MAPSEC_CIANWOOD_CITY',t);assert n==1
  else:assert re.search(pat.replace('MAPSEC_BURNED_TOWER','MAPSEC_CIANWOOD_CITY'),t)
  out[p]=t.encode()
 p='src/region_map.c';t=out[p].decode()
 if '// OLIVINE_CIANWOOD_MAP_GRID_V1' not in t:
  pat=r'(?m)^([ \t]*)// ECRUTEAK_MAP_GRID_V1'
  lines=['// OLIVINE_CIANWOOD_MAP_GRID_V1','if (layer != LAYER_MAP)','    return MAPSEC_NONE;',
   'if (x == 5 && y == 0)','    return MAPSEC_BURNED_TOWER;',
   'if (x >= 2 && x <= 4 && y == 1)','    return MAPSEC_JOHTO_ROUTE38;',
   'if (x == 1 && y >= 1 && y <= 3)','    return MAPSEC_JOHTO_ROUTE39;',
   'if (x == 1 && y == 4)','    return MAPSEC_OLIVINE_CITY;',
   'if (x == 0 && y == 4)','    return MAPSEC_OLIVINE_LIGHTHOUSE;',
   'if (x == 1 && y == 5)','    return MAPSEC_JOHTO_ROUTE40;',
   'if (x == 1 && y == 6)','    return MAPSEC_JOHTO_ROUTE41;',
   'if (x == 0 && y == 6)','    return MAPSEC_CIANWOOD_CITY;','// ECRUTEAK_MAP_GRID_V1']
  t,n=re.subn(pat,lambda m:'\n'.join(m.group(1)+v for v in lines),t);assert n==1
  old='if (x == 4 && y == 1)\n';assert t.count(old)==1
  t=t.replace(old,'if (x == 5 && y == 0)\n',1)
 out[p]=t.encode()
 p='graphics/region_map/johto_entry.bin';a=list(struct.unpack('<600H',s.read(p)))
 known={v['id'] for v in j['map_sections'] if v.get('id') and (v['id'].startswith('MAPSEC_JOHTO_') or v['id'] in ['MAPSEC_NEW_BARK_TOWN','MAPSEC_CHERRYGROVE_CITY','MAPSEC_VIOLET_CITY','MAPSEC_AZALEA_TOWN','MAPSEC_SLOWPOKE_WELL','MAPSEC_ILEX_FOREST','MAPSEC_GOLDENROD_CITY','MAPSEC_ECRUTEAK_CITY','MAPSEC_BURNED_TOWER','MAPSEC_OLIVINE_CITY','MAPSEC_OLIVINE_LIGHTHOUSE','MAPSEC_CIANWOOD_CITY'])}
 for row in original:
  if row.get('id') in known:
   for y in range(row['y'],row['y']+row['height']):
    for x in range(row['x'],row['x']+row['width']):a[(y+4)*30+x+4]=5
 for row in j['map_sections']:
  if row.get('id') in known:
   for y in range(row['y'],row['y']+row['height']):
    for x in range(row['x'],row['x']+row['width']):
     assert 0<=x+4<30 and 0<=y+4<16
     a[(y+4)*30+x+4]=0x1001 if row['width']==row['height']==1 else 0x100a
 out[p]=struct.pack('<600H',*a)
 extra=[('Route38','johtoRoute38','MAP_JOHTO_ROUTE38'),('Route39','johtoRoute39','MAP_JOHTO_ROUTE39'),('Route40','johtoRoute40','MAP_JOHTO_ROUTE40'),('Route41','johtoRoute41','MAP_JOHTO_ROUTE41')]
 p='src/wild_pokemon_area.c';t=s.text(p)
 if 'bool8 johtoRoute38;' not in t:
  t,n=re.subn(r'(bool8\s+johtoBurnedTower\s*;)',lambda m:m.group(1)+''.join('\n    bool8 '+f+';' for _,f,_ in extra),t);assert n==1
 if 'MAP_GROUP(MAP_JOHTO_ROUTE38)' not in t:
  pat=r'(?s)(if\s*\(header->mapGroup\s*==\s*MAP_GROUP\(MAP_JOHTO_ROUTE34\)\s*&&\s*header->mapNum\s*==\s*MAP_NUM\(MAP_JOHTO_ROUTE34\)\s*\)\s*\{\s*habitats->johtoRoute34\s*=\s*TRUE;\s*continue;\s*\})'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n            '+m.group(1).replace('MAP_JOHTO_ROUTE34',mn).replace('johtoRoute34',f) for _,f,mn in extra),t);assert n==1
 if 'habitats.johtoRoute38 || habitats.johtoRoute39' not in t:
  t,n=re.subn(r'(if\s*\([^\n]*habitats\.johtoRoute29[^\n]*habitats\.johtoBurnedTower)\)',lambda m:m.group(1)+' || '+' || '.join('habitats.'+f for _,f,_ in extra)+')',t);assert n==1
 if 'GetJohtoRoute38AreaMarkerSubsprite(areaCount++, subsprites);' not in t:
  pat=r'(if\s*\(habitats\.johtoBurnedTower\)\s*GetJohtoBurnedTowerAreaMarkerSubsprite\(areaCount\+\+,\s*subsprites\);)'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n        if (habitats.'+f+')\n            GetJohto'+key+'AreaMarkerSubsprite(areaCount++, subsprites);' for key,f,_ in extra),t);assert n==1
 out[p]=t.encode()
 p='include/pokedex_area_markers.h';t=s.text(p)
 if 'GetJohtoRoute38AreaMarkerSubsprite' not in t:
  t,n=re.subn(r'(void GetJohtoBurnedTowerAreaMarkerSubsprite\([^;]*;)',lambda m:m.group(1)+''.join('\nvoid GetJohto'+key+'AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);' for key,_,_ in extra),t);assert n==1
 out[p]=t.encode()
 p='src/pokedex_area_markers.c';t=s.text(p)
 for key,shape,x,y in [('Route38','SmallHorizontal',24,7),('Route39','SmallVertical',14,13),('Route40','Circular',14,31),('Route41','Circular',14,37),('BurnedTower','Circular',34,1)]:
  name='GetJohto'+key+'AreaMarkerSubsprite';body='void '+name+'(s32 i, struct Subsprite *subsprites)\n{\n    if (subsprites == NULL)\n        return;\n    subsprites[i] = sSubsprite_'+shape+';\n    subsprites[i].x = '+str(x)+' + (HOENN_AREA_MAP_LEFT * 8 - 104);\n    subsprites[i].y = '+str(y)+';\n}'
  if re.search(r'void\s+'+name+r'\(',t):t=C.replace_function(t,name,body,'Olivine habitat marker')
  else:t=t.rstrip()+'\n\n'+body+'\n'
 out[p]=t.encode()
 p='src/pokedex_screen.c';t=s.text(p);labels=[('Oliv','OLIV'),('Light','LAMP'),('Cian','CIAN'),('R38','38'),('R39','39'),('R40','40'),('R41','41')]
 if 'sText_JohtoOliv[]' not in t:
  anchor='static const u8 sText_JohtoBurn[] = _("BURN");\n';assert t.count(anchor)==1
  t=t.replace(anchor,anchor+''.join('static const u8 sText_Johto'+k+'[] = _("'+v+'");\n' for k,v in labels))
 body='static void DexScreen_DrawJohtoEntryArea(u8 windowId)\n{\n    FillWindowPixelBuffer(windowId, PIXEL_FILL(2));\n    FillWindowPixelRect(windowId, PIXEL_FILL(6), 3, 3, 122, 66);\n'
 for row in j['map_sections']:
  if row.get('id') not in known:continue
  x,y,w,h=row['x']*5+9,row['y']*6+1,max(4,(row['width']-1)*5+4),max(4,(row['height']-1)*6+4)
  assert 0<=x and x+w<=122 and 0<=y and y+h<=68
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(3), '+', '.join(map(str,[x,y,w,h]))+');\n'
  body+='    FillWindowPixelRect(windowId, PIXEL_FILL(5), '+', '.join(map(str,[x+1,y+1,max(1,w-2),max(1,h-2)]))+');\n'
 for key,x,y in [('Ecr',40,5),('Burn',40,0),('Park',23,14),('R35',23,22),('R36',23,21),('R37',39,14),('Gold',24,34),('Vio',42,35),('R31',50,26),('R34',24,47),('R32',45,48),('R30',68,48),('CG',68,54),('Ilex',4,61),('Aza',27,61),('Union',40,61),('R29',81,54),('AirShort',60,61),('NewBark',84,61),('Well',24,49),('Oliv',1,22),('Light',1,29),('Cian',1,39),('R38',17,0),('R39',1,10),('R40',16,29),('R41',16,36)]:
  body+='    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_Johto'+key+', '+str(x)+', '+str(y)+', 0);\n'
 body+='}'
 out[p]=C.replace_function(t,'DexScreen_DrawJohtoEntryArea',body,'Olivine habitat diagram').encode()
def validate(s,out,stats):
 final=Source(s.root,dict(s.overlay,**out));ls={v['id']:v for v in final.json('data/layouts/layouts.json')['layouts'] if v.get('id')}
 maps={n:final.json('data/maps/'+n+'/map.json') for n in NEW}
 starts={'EcruteakCity_WestGate':(7,10),'JohtoRoute38':(34,10),'JohtoRoute39':(23,15),'OlivineCity':(19,0),
 'OlivineCity_PokemonCenter_1F':(7,7),'OlivineCity_Mart':(4,7),'OlivineCity_Gym':(6,14),'OlivineCity_Cafe':(4,7),
 'JohtoRoute40':(23,17),'JohtoRoute41':(10,0),'CianwoodCity':(22,15),
 'CianwoodCity_PokemonCenter_1F':(7,7),'CianwoodCity_Pharmacy':(4,7),'CianwoodCity_Gym':(6,14),
 'OlivineLighthouse_1F':(11,17),'OlivineLighthouse_2F':(18,10),'OlivineLighthouse_3F':(4,10),
 'OlivineLighthouse_4F':(18,10),'OlivineLighthouse_5F':(4,10),'OlivineLighthouse_6F':(11,16)}
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
 behavior_maps=dict(maps);behavior_maps['EcruteakCity']=final.json('data/maps/EcruteakCity/map.json')
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
 checks=[];outside={'JohtoRoute38','JohtoRoute39','OlivineCity','CianwoodCity'};sea={'JohtoRoute40','JohtoRoute41'}
 for n,m in maps.items():
  l=ls[m['layout']];w,h=l['width'],l['height'];raw=final.read(l['blockdata_filepath'])
  assert len(raw)==w*h*2;assert (w+15)*(h+14)<=0x2800,(n,'field map buffer overflow')
  vals=struct.unpack('<'+'H'*(w*h),raw)
  def walk(x,y):return 0<=x<w and 0<=y<h and not((vals[y*w+x]>>10)&3) and (n not in outside or vals[y*w+x]>>12!=1)
  solid={(o['x'],o['y']) for o in m['object_events']}
  for o in m['object_events']:
   assert 0<=o['x']<w and 0<=o['y']<h
   if not n.endswith('PokemonCenter_2F'):assert walk(o['x'],o['y']),(n,'NPC tile',o)
  for wp in m['warp_events']:
   dst=next((k for k in NEW if MID[k]==wp['dest_map']),None)
   if dst:
    i=int(wp['dest_warp_id']);other=maps[dst]['warp_events'];assert 0<=i<len(other) and other[i]['dest_map']==m['id'],(n,'non-reciprocal warp',wp)
  if m['connections']:
   assert not m.get('connections_no_include',False),'native connection pointer suppressed'
   opposite={'up':'down','down':'up','left':'right','right':'left'}
   for cn in m['connections']:
    dst=next((k for k in NEW if MID[k]==cn['map']),None);assert dst
    rev=[z for z in maps[dst]['connections'] if z['map']==m['id'] and z['direction']==opposite[cn['direction']]]
    assert len(rev)==1 and rev[0]['offset']==-cn['offset'],(n,'non-reciprocal connection')
  if n not in starts:checks.append({'map':n,'native_CableClub_layout':True});continue
  start=starts[n];assert walk(*start),(n,'spawn',start);seen={start};q=deque([start])
  while q:
   x,y=q.popleft()
   for z in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if z not in seen and z not in solid and walk(*z):seen.add(z);q.append(z)
  for wp in m['warp_events']:
   z=(wp['x'],wp['y']+1) if n in outside else (wp['x'],wp['y'])
   assert z in seen,(n,'unreachable warp',wp,z)
  for o in m['object_events']:
   x,y=o['x'],o['y'];gfx=o['graphics_id']
   if gfx=='OBJ_EVENT_GFX_NURSE':assert (x,y+2) in seen;continue
   if gfx=='OBJ_EVENT_GFX_CLERK':continue
   assert any(z in seen for z in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),(n,'NPC cannot be faced',o)
  if n=='JohtoRoute38':assert all((0,y) in seen for y in range(10,14))
  if n=='JohtoRoute39':assert all((x,31) in seen for x in range(8,12)) and all((23,y) in seen for y in range(14,18))
  if n=='OlivineCity':assert all((x,0) in seen for x in range(18,22)) and all((0,y) in seen for y in range(24,28))
  if n=='JohtoRoute40':assert all((x,35) in seen for x in range(24))
  if n=='JohtoRoute41':assert all((0,y) in seen for y in range(28))
  if n=='CianwoodCity':
   # Ground reaches the western coast; Surf reaches the native sea connection.
   assert all((22,y) in seen for y in range(14,18))
   surfable={int(v,0) for k,v in re.findall(r'^#define\s+(MB_\w+)\s+(0x[0-9A-Fa-f]+|\d+)\b',behavior_defs,re.M) if k in ('MB_POND_WATER','MB_DEEP_WATER','MB_OCEAN_WATER')}
   assert all(behavior(l,vals[y*w+27]) in surfable for y in range(36)), 'Cianwood eastern edge must be surfable'
  checks.append({'map':n,'reachable_tiles':len(seen),'native_warps':True,'buffer_metatiles':(w+15)*(h+14),'surf_route':n in sea})
 before=s.json('data/maps/map_groups.json');after=final.json('data/maps/map_groups.json')
 assert after['gMapGroup_JohtoEntry'][:len(OLD)]==OLD
 assert all(after[k]==v for k,v in before.items() if k!='gMapGroup_JohtoEntry')
 oldlayout=s.json('data/layouts/layouts.json')['layouts'];assert final.json('data/layouts/layouts.json')['layouts'][:len(oldlayout)]==oldlayout
 old=s.json('data/maps/EcruteakCity/map.json');new=final.json('data/maps/EcruteakCity/map.json')
 assert old['warp_events'][:5]==new['warp_events'][:5] and old['connections']==new['connections']
 assert not any(p in out for p in ['include/global.h','include/pokemon.h','src/save.c','src/load_save.c'])
 cmds=set(re.findall(r'(?m)^\s*\.macro\s+(\w+)',s.text('asm/macros/event.inc')+'\n'+s.text('asm/macros/map.inc')))
 cmds.update(re.findall(r'(?m)^\s*create_movement_action\s+(\w+)',s.text('asm/macros/movement.inc')))
 for p,b in out.items():
  if p.endswith('scripts.inc'):
   t=b.decode();assert not re.search(r'checktrainerflag[^\n]*\n\s*goto_if_eq\s+VAR_RESULT',t),'stale trainer flag comparison'
   for line in t.splitlines():
    v=line.strip()
    if v and not v.startswith(('@','.','#')) and not v.endswith(':'):assert v.split()[0] in cmds,(p,'unknown macro',v)
 headers='\n'.join(final.text('include/constants/'+n) for n in ['species.h','items.h','moves.h','songs.h','event_objects.h','event_object_movement.h','global.h','trainers.h'])+'\n'+s.text('include/battle.h')
 refs=set()
 for p,b in out.items():
  if p.endswith(('.h','.c','.json','scripts.inc')):
   try:refs.update(re.findall(r'\b(?:SPECIES|ITEM|MOVE|MUS|OBJ_EVENT_GFX|TRAINER_CLASS|TRAINER_PIC|TRAINER_ENCOUNTER_MUSIC)_[A-Z0-9_]+',b.decode()))
   except UnicodeDecodeError:pass
 missing=[v for v in refs if not re.search(r'\b'+re.escape(v)+r'\b',headers)];assert not missing,('unknown native constant',missing)
 for n in WILD:
  row=json.loads(out['tools/johto/'+n.lower()+'_wild.json'])
  for k in ['land_mons','land_mons_morning','land_mons_night']:assert len(row[k]['mons'])==12
 for n in WATER:assert len(json.loads(out['tools/johto/'+n.lower()+'_wild.json'])['water_mons']['mons'])==5
 for n in ['CianwoodCity_Gym','OlivineCity_Gym']:
  script=out['data/maps/'+n+'/scripts.inc'].decode();assert 'giveitem' in script and 'goto_if_eq VAR_RESULT, FALSE,' in script
 stats['static_checks']=checks;return stats
def apply(root,mutate=False):
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 s=Source(root);out,stats=build(s);validate(s,out,stats)
 repeat,_=build(Source(root,dict(s.overlay,**out)));assert repeat==out,'not idempotent'
 owned=[p for p in out if any(p.startswith('data/maps/'+n+'/') or p.startswith('data/layouts/'+n+'/') for n in NEW)]
 owned+=['include/constants/opponents_johto_olivine.h','src/data/trainers_johto_olivine.h','src/data/trainer_parties_johto_olivine.h']
 owned+=['tools/johto/'+n.lower()+'_wild.json' for n in list(WILD)+list(WATER)]
 for p in owned:
  if s.exists(p):assert s.read(p)==out[p],'owned artifact changed: '+p
 changed={p:b for p,b in out.items() if not s.exists(p) or s.read(p)!=b}
 print(json.dumps({'apply':mutate,'files':sorted(changed),'validation':stats},indent=2))
 if not mutate or not changed:return
 for p,b in s.used.items():assert (root/p).read_bytes()==b,'concurrent edit: '+p
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=root/'outputs/johto-olivine-cianwood-v1'/stamp;dest.mkdir(parents=True,exist_ok=False);manifest={'time':stamp,'validation':stats,'files':{}}
 for p,b in changed.items():
  path=root/p;old=path.read_bytes() if path.exists() else None;manifest['files'][p]={'before':sha(old) if old is not None else None,'after':sha(b)}
  if old is not None:
   bak=dest/'before'/p;bak.parent.mkdir(parents=True,exist_ok=True);bak.write_bytes(old)
 (dest/'manifest.json').write_bytes(enc(manifest))
 for p,b in changed.items():
  target=root/p;target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.olivine.tmp');assert not tmp.exists();tmp.write_bytes(b);tmp.replace(target)
 print('APPLIED',dest/'manifest.json')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root).resolve(),a.apply)
