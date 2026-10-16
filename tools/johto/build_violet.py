#!/usr/bin/env python3
"""Append Route 31 and the Violet chapter after Cherrygrove. Dry run by default."""
import argparse,copy,datetime,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
from collections import deque
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_cherrygrove as C
Source,enc,sha=C.Source,C.enc,C.sha
OLD=C.OLD+C.NEW
NEW=['JohtoRoute31','VioletCity','VioletCity_PokemonCenter_1F','VioletCity_PokemonCenter_2F','VioletCity_Mart','VioletCity_Academy','VioletCity_Gym','SproutTower_1F','SproutTower_2F','SproutTower_3F']
IDS=['JOHTO_ROUTE31','VIOLET_CITY','VIOLET_CITY_POKEMON_CENTER_1F','VIOLET_CITY_POKEMON_CENTER_2F','VIOLET_CITY_MART','VIOLET_CITY_ACADEMY','VIOLET_CITY_GYM','SPROUT_TOWER_1F','SPROUT_TOWER_2F','SPROUT_TOWER_3F']
MID=dict(zip(NEW,['MAP_'+x for x in IDS]))
MARK='JOHTO_VIOLET_CHAPTER_V1'
FLAGS={'FLAG_JOHTO_SPROUT_TOWER_CLEARED':5,'FLAG_JOHTO_GOT_TM40_FROM_FALKNER':6,'FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED':7,'FLAG_JOHTO_BADGE01_GET':16}
TRAINERS=[
 ('WADE','BUG_CATCHER','BUG_CATCHER',[('CATERPIE',10),('WEEDLE',10),('CATERPIE',11)],784),
 ('EDMOND','EXPERT','EXPERT_M',[('BELLSPROUT',11),('BELLSPROUT',11)],785),
 ('NICO','EXPERT','EXPERT_M',[('BELLSPROUT',12)],786),
 ('LI','EXPERT','EXPERT_M',[('BELLSPROUT',13),('HOOTHOOT',14)],787),
 ('ABE','BIRD_KEEPER','BIRD_KEEPER',[('SPEAROW',12)],788),
 ('ROD','BIRD_KEEPER','BIRD_KEEPER',[('PIDGEY',12),('PIDGEY',13)],789),
 ('FALKNER','LEADER','COOLTRAINER_M',[('PIDGEY',14),('PIDGEOTTO',16)],790)]
def ident(name):return IDS[NEW.index(name)]
def warp(x,y,dst,idx,elevation=3):return {'x':x,'y':y,'elevation':elevation,'dest_map':MID.get(dst,dst),'dest_warp_id':str(idx)}
def obj(gfx,x,y,script,**kw):return C.obj(gfx,x,y,script,**kw)
def layout_array(s,ident):
 l=next(x for x in s.json('data/layouts/layouts.json')['layouts'] if x.get('id')==ident)
 v=struct.unpack('<'+'H'*(l['width']*l['height']),s.read(l['blockdata_filepath']))
 return [list(v[y*l['width']:(y+1)*l['width']]) for y in range(l['height'])]
def crop(a,x,y,w,h):return [row[x:x+w] for row in a[y:y+h]]
def geometry(s):
 vir=layout_array(s,'LAYOUT_VIRIDIAN_CITY');pew=layout_array(s,'LAYOUT_PEWTER_CITY')
 a=[[0x3001]*40 for _ in range(20)]
 C.fill(a,0,0,40,3,C.dense);C.fill(a,0,17,40,20,C.dense);C.fill(a,38,0,40,20,C.dense)
 C.fill(a,0,11,30,15,0x3001);C.fill(a,24,11,27,20,0x3001)
 C.fill(a,9,4,15,9,C.grass);C.fill(a,28,8,35,13,C.grass)
 C.paste(a,crop(vir,11,26,6,6),28,2)
 C.fill(a,17,3,19,11,C.dense);C.fill(a,17,15,19,18,C.dense)
 a[15][22]=0x0403
 v=[[0x3001]*40 for _ in range(32)]
 for box in [(0,0,40,3),(0,0,2,32),(0,30,40,32)]:C.fill(v,*box,C.dense)
 C.fill(v,38,0,40,11,C.dense);C.fill(v,38,15,40,32,C.dense)
 C.fill(v,2,11,40,15,0x3195);C.fill(v,17,3,21,30,0x3195)
 C.fill(v,4,19,13,29,0x3195);C.fill(v,25,19,35,29,0x3195)
 C.fill(v,5,5,15,11,0x3195);C.fill(v,26,4,36,11,0x3195)
 C.paste(v,crop(vir,24,22,5,5),5,22)
 C.paste(v,crop(vir,34,16,4,4),29,23)
 C.paste(v,crop(vir,24,8,5,4),27,5)
 C.paste(v,crop(pew,12,12,7,5),5,5)
 # The tower facade reuses native house roof/wall tiles, with two extra floors.
 house=crop(vir,24,8,5,4)
 wall=[house[3][0],house[3][2],house[3][2],house[3][3],house[3][4]]
 tower=[house[0],house[1],house[2],wall,wall,house[3]]
 C.paste(v,tower,19,3);C.fill(v,19,9,24,12,0x3195)
 for x,y in [(12,9),(26,8),(24,9),(11,26),(34,26)]:v[y][x]=0x0403
 C.paste(v,crop(vir,11,26,6,6),3,15)
 for x,y in [(14,19),(15,19),(14,20),(15,20),(33,17),(34,17)]:v[y][x]=0x3004
 dojo=layout_array(s,'LAYOUT_SAFFRON_CITY_DOJO')
 h1=layout_array(s,'LAYOUT_PALLET_TOWN_PLAYERS_HOUSE_1F')
 h2=layout_array(s,'LAYOUT_PALLET_TOWN_PLAYERS_HOUSE_2F')
 floors={}
 for i in range(1,4):
  f=copy.deepcopy(dojo)
  # Clear old gift stands; a wooden central pillar remains as the tower landmark.
  for y in range(3,7):
   for x in range(1,12):f[y][x]=0x32c0
  for y,val in [(3,0x06cd),(4,0x06cd),(5,0x06d5),(6,0x06dd)]:f[y][6]=val
  if i<3:C.paste(f,crop(h1,9,1,3,2),9,3)
  if i>1:C.paste(f,crop(h2,9,1,3,2),2,3)
  if i>1:
   for x in (5,6,7):f[14][x]=0x32c0;f[15][x]=0x0408
  floors['SproutTower_'+str(i)+'F']=f
 return dict({'JohtoRoute31':a,'VioletCity':v},**floors)


def events():
 scripts={n:n+'_MapScripts::\n    .byte 0\n' for n in NEW};tx={}
 def speech(n,k,p):scripts[n]+='\n'+C.npc_script(n,k);tx.setdefault(n,{})[k]=p
 n='JohtoRoute31'
 scripts[n]+=r'''
JohtoRoute31_Wade::
    trainerbattle_single TRAINER_JOHTO_WADE, JohtoRoute31_Text_WadeIntro, JohtoRoute31_Text_WadeDefeat
    msgbox JohtoRoute31_Text_WadeAfter, MSGBOX_AUTOCLOSE
    end
'''
 tx[n]={'WadeIntro':['The tall grass is full of life!\nLet me show you what I found.'],
        'WadeDefeat':['Your team has good instincts!'],
        'WadeAfter':['Small discoveries matter.\nThat is how a POKEDEX grows.']}
 speech(n,'RouteSign',['ROUTE 31','West: VIOLET CITY\nSouth: ROUTE 30'])
 speech(n,'Traveler',['VIOLET has a GYM for trainers\nand a tower for patient study.',
                     'ELM asked the tower sages to\ncompare our research notes.'])
 n='VioletCity'
 speech(n,'Guide',['Welcome to VIOLET CITY!',
                   'SPROUT TOWER stands near the\nnorth road. Visit the elder.',
                   'FALKNER trains bird POKEMON\nat the GYM in the northwest.'])
 speech(n,'Teacher',['Your KANTO records remain.\nJOHTO adds its local order.',
                     'The academy explains how to\ncompare your discoveries.'])
 for k,p in [('GymSign',['VIOLET POKEMON GYM\nLEADER: FALKNER']),
             ('AcademySign',['VIOLET TRAINERS ACADEMY']),
             ('TowerSign',['SPROUT TOWER\nListen, observe, and learn.']),
             ('CenterSign',['POKEMON CENTER']),
             ('MartSign',['POKEMON MART'])]:speech(n,k,p)
 n='VioletCity_Academy'
 speech(n,'Teacher',['OAK, ELM, and BIRCH compare\nreports from three regions.',
                     'A regional POKEDEX changes\nits order, not your partners.',
                     'Your caught and seen records\nremain on the same device.',
                     'Show your JOHTO research to\nthe elder at SPROUT TOWER.'])
 speech(n,'Student',['HOOTHOOT appears at night.\nThat does not mean one hour!',
                     'Study routes throughout the\nmorning, day, and night.'])
 # Tower 1F and 2F use the existing native trainer battle engine.
 for floor,name in [('SproutTower_1F','EDMOND'),('SproutTower_2F','NICO')]:
  title=name.title();scripts[floor]+='\n'+floor+'_'+title+'::\n    trainerbattle_single TRAINER_JOHTO_'+name+', '+floor+'_Text_Intro, '+floor+'_Text_Defeat\n    msgbox '+floor+'_Text_After, MSGBOX_AUTOCLOSE\n    end\n'
  tx[floor]={'Intro':['A strong trainer learns to\nbend without breaking.'],
             'Defeat':['There is more than strength.'],
             'After':['Each region teaches us a new\nway to understand POKEMON.']}
 speech('SproutTower_1F','Visitor',['The central pillar can sway\nwithout bringing us down.',
                                  'The elder studies the notes\nthat ELM received from you.'])
 n='SproutTower_3F'
 scripts[n]+=r'''
SproutTower_3F_Elder::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_ELM_REPORT_DELIVERED, SproutTower_3F_NotReady
    goto_if_set FLAG_JOHTO_SPROUT_TOWER_CLEARED, SproutTower_3F_Reward
    trainerbattle_single TRAINER_JOHTO_LI, SproutTower_3F_Text_Intro, SproutTower_3F_Text_Defeat, SproutTower_3F_Victory, NO_MUSIC
    goto SproutTower_3F_Reward
SproutTower_3F_Victory::
    setflag FLAG_JOHTO_SPROUT_TOWER_CLEARED
    msgbox SproutTower_3F_Text_ResearchComplete
    goto SproutTower_3F_Reward
SproutTower_3F_Reward::
    goto_if_set FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED, SproutTower_3F_After
    goto_if_set FLAG_GOT_HM05, SproutTower_3F_AlternateReward
    checkitem ITEM_HM05
    goto_if_eq VAR_RESULT, TRUE, SproutTower_3F_AlternateReward
    checkpcitem ITEM_HM05
    goto_if_eq VAR_RESULT, TRUE, SproutTower_3F_AlternateReward
    checkitemspace ITEM_HM05
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    giveitem ITEM_HM05
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    setflag FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED
    msgbox SproutTower_3F_Text_Flash
    goto SproutTower_3F_After
SproutTower_3F_AlternateReward::
    checkitemspace ITEM_TM10
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    msgbox SproutTower_3F_Text_KnownFlash
    giveitem ITEM_TM10
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    setflag FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED
    msgbox SproutTower_3F_Text_Alternate
SproutTower_3F_After::
    msgbox SproutTower_3F_Text_After
    release
    end
SproutTower_3F_NotReady::
    msgbox SproutTower_3F_Text_NotReady
    release
    end
SproutTower_3F_BagFull::
    msgbox SproutTower_3F_Text_BagFull
    release
    end
'''
 tx[n]={'Intro':['ELM has shared your report.\nNow let our POKEMON teach us.'],
        'Defeat':['You listened well to them!'],
        'ResearchComplete':['The report is confirmed.\nJOHTO has much left to teach.',
                            'FALKNER can test your skill.\nHis GYM is in VIOLET CITY.'],
        'After':['You understand the tower now.\nMeet FALKNER at the GYM.',
                 'Use what you learned here.\nYour next challenge awaits.'],
        'NotReady':['MR. POKEMON has notes for ELM.\nPlease deliver them first.',
                    'Then we can study those notes\nand train together.'],
        'BagFull':['Please make room for the reward.\nI will keep it until you return.'], 'Flash':['FLASH lights dark places.\nUse it with care.'], 'KnownFlash':['You already received FLASH.\nLet us try something different.'], 'Alternate':['TM10 teaches HIDDEN POWER.\nIts power depends on the user.']}
 n='VioletCity_Gym'
 scripts[n]+=r'''
VioletCity_Gym_Falkner::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_SPROUT_TOWER_CLEARED, VioletCity_Gym_NotReady
    goto_if_set FLAG_JOHTO_BADGE01_GET, VioletCity_Gym_Reward
    trainerbattle_single TRAINER_JOHTO_FALKNER, VioletCity_Gym_Text_Intro, VioletCity_Gym_Text_Defeat, VioletCity_Gym_Victory, NO_MUSIC
    goto VioletCity_Gym_Reward
VioletCity_Gym_Victory::
    setflag FLAG_JOHTO_BADGE01_GET
    msgbox VioletCity_Gym_Text_Badge
    goto VioletCity_Gym_Reward
VioletCity_Gym_Reward::
    goto_if_set FLAG_JOHTO_GOT_TM40_FROM_FALKNER, VioletCity_Gym_After
    checkitemspace ITEM_TM40
    goto_if_eq VAR_RESULT, FALSE, VioletCity_Gym_BagFull
    giveitem ITEM_TM40
    goto_if_eq VAR_RESULT, FALSE, VioletCity_Gym_BagFull
    setflag FLAG_JOHTO_GOT_TM40_FROM_FALKNER
    msgbox VioletCity_Gym_Text_TM
VioletCity_Gym_After::
    msgbox VioletCity_Gym_Text_After
    release
    end
VioletCity_Gym_NotReady::
    msgbox VioletCity_Gym_Text_NotReady
    release
    end
VioletCity_Gym_BagFull::
    msgbox VioletCity_Gym_Text_BagFull
    release
    end
'''
 tx[n]={'Intro':['I am FALKNER, the GYM LEADER.\nBird POKEMON are my partners.',
                 'Even KANTO champions can find\nsomething new in our skies!'],
        'Defeat':['The wind carried you today.'],
        'Badge':['You earned the ZEPHYRBADGE!\nYour first JOHTO GYM victory.'],
        'TM':['TM40 teaches AERIAL ACE.\nIt is a swift flying attack.'],
        'After':['Keep learning from each place.\nThat is how our journey grows.'],
        'NotReady':['Visit the elder at SPROUT\nTOWER before our challenge.',
                    'ELM has research to share.\nHear what the elder learned.'],
        'BagFull':['Your badge is already earned.\nMake room for your TM reward.']}
 for name in ['ABE','ROD']:
  k=name.title();scripts[n]+='\n'+n+'_'+k+'::\n    trainerbattle_single TRAINER_JOHTO_'+name+', '+n+'_Text_'+k+'Intro, '+n+'_Text_'+k+'Defeat\n    msgbox '+n+'_Text_'+k+'After, MSGBOX_AUTOCLOSE\n    end\n'
  tx[n][k+'Intro']=['Can you keep up with our\nbird POKEMON?']
  tx[n][k+'Defeat']=['Your teamwork took flight!']
  tx[n][k+'After']=['FALKNER respects trainers who\nlearn from their partners.']
 speech(n,'GymGuy',['Flying POKEMON dislike strong\nROCK and ELECTRIC attacks.',
                    'Visit SPROUT TOWER first.\nThe elder knows ELM well.'])
 return scripts,{n:C.texts(n,rows) for n,rows in tx.items()}


def build(s):
 # AZALEA_EXTENSION_GUARD
 if any(n not in OLD + NEW for n in s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]):
  raise RuntimeError("Azalea extension exists; use build_azalea.py")
 out={};stats={'chapter':'Violet','save_layout_changed':False,'battle_portrait_limit':'Falkner uses temporary native COOLTRAINER_M art; not final artwork','tm_choice':'Gen III TM40 AERIAL ACE; GSC TM31 would mean BRICK BREAK here'}
 groups=s.json('data/maps/map_groups.json');assert groups['gMapGroup_JohtoEntry'] in (OLD,OLD+NEW)
 for k,v in groups.items():
  if k not in ('group_order','gMapGroup_JohtoEntry'):assert not(set(v)&set(NEW))
 groups['gMapGroup_JohtoEntry']=OLD+NEW;out['data/maps/map_groups.json']=enc(groups)
 arrays=geometry(s);ls=s.json('data/layouts/layouts.json')
 for name,a in arrays.items():
  outdoor=name in ('JohtoRoute31','VioletCity')
  item={'id':'LAYOUT_'+ident(name),'name':name+'_Layout','width':len(a[0]),'height':len(a),'border_width':2,'border_height':2,'primary_tileset':'gTileset_General' if outdoor else 'gTileset_Building','secondary_tileset':'gTileset_ViridianCity' if outdoor else 'gTileset_PewterGym','blockdata_filepath':'data/layouts/'+name+'/map.bin','border_filepath':'data/layouts/'+name+'/border.bin'}
  prior=[x for x in ls['layouts'] if x.get('id')==item['id']];assert not prior or prior==[item]
  if not prior:ls['layouts'].append(item)
  out[item['blockdata_filepath']]=C.pack(a)
  out[item['border_filepath']]=struct.pack('<4H',*((0x414,0x415,0x41c,0x41d) if outdoor else (0x408,)*4))
 out['data/layouts/layouts.json']=enc(ls)
 maps={}
 def temp(name,source,section,layout=None,music=None):
  j=s.json('data/maps/'+source+'/map.json')
  j.update(id=MID[name],name=name,region_map_section=section,connections=None)
  if layout:j['layout']=layout
  if music:j['music']=music
  for k in ('object_events','warp_events','coord_events','bg_events'):j[k]=[]
  maps[name]=j;return j
 n='JohtoRoute31';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE31','LAYOUT_JOHTO_ROUTE31','MUS_ROUTE1')
 j['connections']=[{'map':'MAP_JOHTO_ROUTE30','direction':'down','offset':16},{'map':MID['VioletCity'],'direction':'left','offset':0}]
 j['object_events']=[obj('BUG_CATCHER',16,12,n+'_Wade',movement='FACE_LEFT'),obj('HIKER',23,15,n+'_Traveler')]
 j['bg_events']=[C.bg(22,15,n+'_RouteSign')]
 n='VioletCity';j=temp(n,'ViridianCity','MAPSEC_VIOLET_CITY','LAYOUT_VIOLET_CITY','MUS_PEWTER')
 j['connections']=[{'map':MID['JohtoRoute31'],'direction':'right','offset':0}]
 j['object_events']=[obj('OLD_MAN_2',19,17,n+'_Guide'),obj('WOMAN_2',25,11,n+'_Teacher')]
 j['warp_events']=[warp(7,26,'VioletCity_PokemonCenter_1F',1,0),warp(31,26,'VioletCity_Mart',1,0),warp(28,8,'VioletCity_Academy',1,0),warp(8,9,'VioletCity_Gym',1,0),warp(20,8,'SproutTower_1F',1,0)]
 j['bg_events']=[C.bg(x,y,n+'_'+key) for x,y,key in [(12,9,'GymSign'),(26,8,'AcademySign'),(24,9,'TowerSign'),(11,26,'CenterSign'),(34,26,'MartSign')]]
 scripts,tx=events()
 # Native service interiors and scripts are cloned from the newly validated city.
 for suffix in ('PokemonCenter_1F','PokemonCenter_2F','Mart'):
  source='CherrygroveCity_'+suffix;name='VioletCity_'+suffix
  data=s.text('data/maps/'+source+'/map.json').replace('CHERRYGROVE','VIOLET').replace('Cherrygrove','Violet')
  j=json.loads(data);assert j['id']==MID[name];maps[name]=j
  for f,target in [('scripts.inc',scripts),('text.inc',tx)]:
   target[name]=s.text('data/maps/'+source+'/'+f).replace('CHERRYGROVE','VIOLET').replace('Cherrygrove','Violet')
  if suffix=='PokemonCenter_1F':
   j['object_events'][0]['local_id']='LOCALID_VIOLET_NURSE'
   for wp in j['warp_events'][:3]:wp['dest_warp_id']='0'
  if suffix=='Mart':
   for wp in j['warp_events']:wp['dest_warp_id']='1'
 n='VioletCity_Academy';j=temp(n,'CeruleanCity_House3','MAPSEC_VIOLET_CITY','LAYOUT_HOUSE1','MUS_PEWTER')
 j['object_events']=[obj('SCIENTIST',4,5,n+'_Teacher'),obj('BOY',7,5,n+'_Student')]
 j['warp_events']=[warp(x,7,'VioletCity',2) for x in (3,4,5)]
 n='VioletCity_Gym';j=temp(n,'PewterCity_Gym','MAPSEC_VIOLET_CITY',music='MUS_GYM')
 j['object_events']=[obj('COOLTRAINER_M',6,5,n+'_Falkner'),obj('CAMPER',3,8,n+'_Abe',movement='FACE_RIGHT'),obj('CAMPER',10,10,n+'_Rod',movement='FACE_LEFT'),obj('GYM_GUY',7,12,n+'_GymGuy')]
 j['warp_events']=[warp(x,14,'VioletCity',3) for x in (5,6,7)]
 for i in (1,2,3):
  n='SproutTower_'+str(i)+'F';j=temp(n,'SaffronCity_Dojo','MAPSEC_VIOLET_CITY','LAYOUT_'+ident(n),'MUS_PALLET')
  j['floor_number']=i;j['allow_running']=True
  if i==1:
   j['object_events']=[obj('OLD_MAN_1',3,10,n+'_Edmond',movement='FACE_RIGHT'),obj('OLD_WOMAN',9,12,n+'_Visitor')]
   j['warp_events']=[warp(x,14,'VioletCity',4) for x in (5,6,7)]+[warp(10,4,'SproutTower_2F',0)]
  if i==2:
   j['object_events']=[obj('OLD_MAN_2',4,10,n+'_Nico',movement='FACE_RIGHT')]
   j['warp_events']=[warp(3,4,'SproutTower_1F',3),warp(10,4,'SproutTower_3F',0)]
  if i==3:
   j['object_events']=[obj('OLD_MAN_1',6,8,n+'_Elder')]
   j['warp_events']=[warp(3,4,'SproutTower_2F',1)]
 for n,j in maps.items():
  out['data/maps/'+n+'/map.json']=enc(j)
  out['data/maps/'+n+'/scripts.inc']=scripts[n].encode()
  out['data/maps/'+n+'/text.inc']=tx.get(n,'@ Shared native dialogue.\n').encode()
 # Open just the three-wide northern connection through Route 30's existing trees.
 p='data/maps/JohtoRoute30/map.json';j=s.json(p);link={'map':MID['JohtoRoute31'],'direction':'up','offset':-16}
 assert not [c for c in j['connections'] if c['direction']=='up' and c!=link]
 if link not in j['connections']:j['connections'].append(link)
 out[p]=enc(j)
 l=next(x for x in ls['layouts'] if x.get('id')==j['layout']);assert (l['width'],l['height'])==(24,48)
 a=list(struct.unpack('<1152H',s.read(l['blockdata_filepath'])))
 for y in range(3):
  for x in range(8,11):
   idx=y*24+x;assert a[idx] in (C.dense(x,y),0x3001);a[idx]=0x3001
 for y in range(3,9):
  for x in range(8,11):assert a[y*24+x]==0x3001,(x,y,a[y*24+x])
 out[l['blockdata_filepath']]=struct.pack('<1152H',*a)
 sec=s.json('src/data/region_map/region_map_sections.json')
 for item in [{'id':'MAPSEC_JOHTO_ROUTE31','name':'ROUTE 31','x':3,'y':3,'width':4,'height':1},{'id':'MAPSEC_VIOLET_CITY','name':'VIOLET CITY','x':2,'y':3,'width':1,'height':1}]:
  hits=[v for v in sec['map_sections'] if v['id']==item['id']];assert not hits or hits==[item]
  if not hits:sec['map_sections'].append(item)
 out['src/data/region_map/region_map_sections.json']=enc(sec)
 heals=s.json('src/data/heal_locations.json')
 hi={'id':'HEAL_LOCATION_VIOLET_CITY','map':MID['VioletCity'],'x':7,'y':27,'respawn_map':MID['VioletCity_PokemonCenter_1F'],'respawn_npc':'LOCALID_VIOLET_NURSE'}
 hits=[v for v in heals['heal_locations'] if v['id']==hi['id']];assert not hits or hits==[hi]
 if not hits:heals['heal_locations'].append(hi)
 out['src/data/heal_locations.json']=enc(heals)
 for p,key in [('data/layouts/layouts.json','layouts'),('src/data/region_map/region_map_sections.json','map_sections'),('src/data/heal_locations.json','heal_locations')]:
  prev=s.json(p)[key];assert json.loads(out[p])[key][:len(prev)]==prev
 shared(s,out);areas(s,out)
 stats['new_maps']=NEW;stats['new_flags']=FLAGS;stats['new_trainer_offsets']=[v[-1] for v in TRAINERS]
 return out,stats

def shared(s,out):
 p='include/constants/flags_johto_story.h';t=s.text(p)
 block='\n// '+MARK+'\n'+''.join('#define '+n+' (JOHTO_STORY_FLAGS_START + '+str(v)+')\n' for n,v in FLAGS.items())
 if MARK not in t:
  used={int(v,0) for v in re.findall(r'JOHTO_STORY_FLAGS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',t)};assert not(used&set(FLAGS.values()))
  assert not any(n in t for n in FLAGS);idx=t.rfind('#endif');assert idx>=0;t=t[:idx]+block+'\n'+t[idx:]
 else:assert block in t
 out[p]=t.encode()
 p='include/constants/opponents_johto.h'
 h='#ifndef GUARD_CONSTANTS_OPPONENTS_JOHTO_H\n#define GUARD_CONSTANTS_OPPONENTS_JOHTO_H\n// Existing 1024-bit extended trainer bank; no save-layout growth.\n'
 for name,cls,pic,party,num in TRAINERS:h+='#define TRAINER_JOHTO_'+name+' (HOENN_TRAINERS_START + '+str(num)+')\n'
 h+='#endif\n';out[p]=h.encode()
 for header in (s.root/'include/constants').glob('opponents*.h'):
  rel=header.relative_to(s.root).as_posix()
  if rel==p:continue
  body=s.text(rel)
  nums={int(x,0) for x in re.findall(r'HOENN_TRAINERS_START\s*\+\s*(0x[0-9a-fA-F]+|\d+)',body)}
  assert not(nums&{v[-1] for v in TRAINERS}),('trainer number already reserved',rel)
 p='include/constants/opponents.h';t=s.text(p);anchor='#include "constants/opponents_rocket.h"'
 t=C.once(t,anchor,anchor+'\n#include "constants/opponents_johto.h"','Johto opponents include');out[p]=t.encode()
 parties='// '+MARK+'\n';trainers='// '+MARK+'\n'
 for name,cls,pic,party,num in TRAINERS:
  sym='sParty_Johto'+name.title()
  parties+='static const struct TrainerMonNoItemDefaultMoves '+sym+'[] = {\n'
  for species,level in party:parties+='    {.iv = 40, .lvl = '+str(level)+', .species = SPECIES_'+species+'},\n'
  parties+='};\n\n'
  trainers+='    [TRAINER_JOHTO_'+name+'] = {\n        .trainerClass = TRAINER_CLASS_'+cls+',\n        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_MALE,\n        .trainerPic = TRAINER_PIC_'+pic+',\n        .trainerName = _("'+name+'"),\n        .items = {},\n        .doubleBattle = FALSE,\n        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,\n        .party = NO_ITEM_DEFAULT_MOVES('+sym+'),\n    },\n'
 out['src/data/trainer_parties_johto.h']=parties.encode();out['src/data/trainers_johto.h']=trainers.encode()
 for p,anchor,new in [('src/data/trainers.h','#include "trainers_rocket.h"','#include "trainers_johto.h"'),('src/data/trainer_parties.h','#include "trainer_parties_rocket.h"','#include "trainer_parties_johto.h"')]:
  t=s.text(p);out[p]=C.once(t,anchor,anchor+'\n'+new,'Johto trainer data include').encode()
 p='data/event_scripts.s';t=s.text(p);block='@ '+MARK+'\n'+''.join('    .include "data/maps/'+n+'/'+f+'"\n' for n in NEW for f in ('scripts.inc','text.inc'))
 if MARK not in t:assert not any('data/maps/'+n+'/' in t for n in NEW);t=t.rstrip()+'\n\n'+block
 else:assert block in t
 out[p]=t.encode()
 # A rerun of the earlier chapter generator must not erase the extension.
 p='tools/johto/build_cherrygrove.py';t=s.text(p)
 guard='    # VIOLET_EXTENSION_GUARD\n    _current = s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]\n    if any(_n not in OLD + NEW for _n in _current):\n        raise RuntimeError("Violet extension exists; use build_violet.py")\n'
 if '# VIOLET_EXTENSION_GUARD' not in t:
  t,n=re.subn(r'(?m)^(def build\(s\):\n)',lambda m:m.group(1)+guard,t);assert n==1
 else:assert guard in t
 out[p]=t.encode()
 # Gen II route populations, encoded in the existing day/morning/night schema.
 day=['BELLSPROUT','PIDGEY','CATERPIE','WEEDLE','BELLSPROUT','PIDGEY','CATERPIE','WEEDLE','RATTATA','HOPPIP','METAPOD','KAKUNA']
 night=['HOOTHOOT','SPINARAK','BELLSPROUT','RATTATA','HOOTHOOT','SPINARAK','BELLSPROUT','RATTATA','ZUBAT','POLIWAG','GASTLY','GASTLY']
 levels=[4,4,4,4,5,5,5,5,4,5,6,6]
 row={'map':MID['JohtoRoute31'],'base_label':'sJohtoRoute31'}
 for field,sp in [('land_mons',day),('land_mons_morning',day),('land_mons_night',night)]:
  row[field]={'encounter_rate':10,'mons':[{'min_level':lv,'max_level':lv,'species':'SPECIES_'+name} for name,lv in zip(sp,levels)]}
 out['tools/johto/route31_wild.json']=enc(row)
 p='src/data/wild_encounters.json';j=s.json(p);gs=[g for g in j['wild_encounter_groups'] if g['label']=='gWildMonHeaders'];assert len(gs)==1 and gs[0]['for_maps']
 rows=gs[0]['encounters'];hits=[x for x in rows if x['map']==row['map'] or x['base_label']==row['base_label']];assert not hits or hits==[row]
 if not hits:rows.append(row)
 out[p]=enc(j)


def areas(s,out):
 for p in ('src/region_map.c','src/pokemon_summary_screen.c'):
  t=s.text(p);pat=r'(MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP[\s\S]{0,120}?<=\s*)MAPSEC_JOHTO_ROUTE30'
  if re.search(pat,t):t,n=re.subn(pat,lambda m:m.group(1)+'MAPSEC_VIOLET_CITY',t);assert n==1
  else:assert re.search(pat.replace('MAPSEC_JOHTO_ROUTE30','MAPSEC_VIOLET_CITY'),t)
  out[p]=t.encode()
 p='src/region_map.c';t=out[p].decode()
 block='// VIOLET_ROUTE31_MAP_GRID_V1\n'
 if block not in t:
  pat=r'(?m)^([ \t]*)// CHERRYGROVE_ROUTE30_MAP_GRID_V1'
  def add(m):
   sp=m.group(1)
   return '\n'.join(sp+x for x in ['// VIOLET_ROUTE31_MAP_GRID_V1','if (layer == LAYER_MAP && x == 2 && y == 3)','    return MAPSEC_VIOLET_CITY;','if (layer == LAYER_MAP && x >= 3 && x <= 6 && y == 3)','    return MAPSEC_JOHTO_ROUTE31;','// CHERRYGROVE_ROUTE30_MAP_GRID_V1'])
  t,n=re.subn(pat,add,t);assert n==1,'new city grid anchor'
 out[p]=t.encode()
 p='graphics/region_map/johto_entry.bin';v=list(struct.unpack('<600H',s.read(p)))
 for x in range(6,11):
  idx=7*30+x;new=0x1001 if x==6 else 0x100a
  assert v[idx] in (3,5,6,7,new),(x,7,v[idx]);v[idx]=new
 out[p]=struct.pack('<600H',*v)
 p='src/pokedex_screen.c';t=s.text(p)
 decl='static const u8 sText_JohtoViolet[] = _("VIOLET");\nstatic const u8 sText_JohtoRoute31[] = _("ROUTE 31");\n'
 if 'sText_JohtoViolet[]' not in t:
  anchor='static const u8 sText_JohtoRoute30[] = _("ROUTE 30");\n';assert t.count(anchor)==1;t=t.replace(anchor,anchor+decl)
 new=r'''static void DexScreen_DrawJohtoEntryArea(u8 windowId)
{
    FillWindowPixelBuffer(windowId, PIXEL_FILL(2));
    FillWindowPixelRect(windowId, PIXEL_FILL(6), 3, 3, 122, 66);
    FillWindowPixelRect(windowId, PIXEL_FILL(3), 40, 52, 74, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 42, 54, 70, 4);
    FillWindowPixelRect(windowId, PIXEL_FILL(3), 36, 16, 8, 40);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 38, 18, 4, 36);
    FillWindowPixelRect(windowId, PIXEL_FILL(3), 8, 16, 36, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 10, 18, 32, 4);
    FillWindowPixelRect(windowId, PIXEL_FILL(2), 8, 16, 8, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 10, 18, 4, 4);
    FillWindowPixelRect(windowId, PIXEL_FILL(2), 36, 36, 8, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 38, 38, 4, 4);
    FillWindowPixelRect(windowId, PIXEL_FILL(2), 36, 52, 8, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 38, 54, 4, 4);
    FillWindowPixelRect(windowId, PIXEL_FILL(2), 110, 52, 8, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 112, 54, 4, 4);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoViolet, 2, 2, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoRoute31, 52, 6, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoRoute30, 52, 19, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoCherrygrove, 52, 31, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoRoute29, 60, 43, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoAirstrip, 10, 60, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoNewBark, 86, 60, 0);
}'''
 t=C.replace_function(t,'DexScreen_DrawJohtoEntryArea',new,'Violet habitat diagram');out[p]=t.encode()
 p='src/wild_pokemon_area.c';t=s.text(p)
 if not re.search(r'bool8\s+johtoRoute31\s*;',t):
  t,n=re.subn(r'(bool8\s+johtoRoute30\s*;)',r'\1\n    bool8 johtoRoute31;',t);assert n==1
 if 'MAP_GROUP(MAP_JOHTO_ROUTE31)' not in t:
  pat=r'(?s)(if\s*\(header->mapGroup\s*==\s*MAP_GROUP\(MAP_JOHTO_ROUTE30\)\s*&&\s*header->mapNum\s*==\s*MAP_NUM\(MAP_JOHTO_ROUTE30\)\s*\)\s*\{\s*habitats->johtoRoute30\s*=\s*TRUE;\s*continue;\s*\})'
  t,n=re.subn(pat,lambda m:m.group(1)+'\n            '+m.group(1).replace('MAP_JOHTO_ROUTE30','MAP_JOHTO_ROUTE31').replace('johtoRoute30','johtoRoute31'),t);assert n==1
 old='if (habitats.johtoRoute29 || habitats.johtoRoute30)'
 new='if (habitats.johtoRoute29 || habitats.johtoRoute30 || habitats.johtoRoute31)'
 t=C.once(t,old,new,'Johto habitat region bit')
 if 'GetJohtoRoute31AreaMarkerSubsprite(areaCount++, subsprites);' not in t:
  pat=r'(if\s*\(habitats\.johtoRoute30\)\s*GetJohtoRoute30AreaMarkerSubsprite\(areaCount\+\+,\s*subsprites\);)'
  t,n=re.subn(pat,lambda m:m.group(1)+'\n        if (habitats.johtoRoute31)\n            GetJohtoRoute31AreaMarkerSubsprite(areaCount++, subsprites);',t);assert n==1
 out[p]=t.encode()
 p='include/pokedex_area_markers.h';t=s.text(p)
 if 'GetJohtoRoute31AreaMarkerSubsprite' not in t:
  t,n=re.subn(r'(void GetJohtoRoute30AreaMarkerSubsprite\([^;]*;)',lambda m:m.group(1)+'\nvoid GetJohtoRoute31AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);',t);assert n==1
 out[p]=t.encode()
 p='src/pokedex_area_markers.c';t=s.text(p)
 for route,shape,x,y in [(29,'MediumHorizontal',66,48),(30,'SmallVertical',36,20),(31,'MediumHorizontal',8,12)]:
  name='GetJohtoRoute'+str(route)+'AreaMarkerSubsprite'
  new='void '+name+'(s32 i, struct Subsprite *subsprites)\n{\n    if (subsprites == NULL)\n        return;\n    subsprites[i] = sSubsprite_'+shape+';\n    subsprites[i].x = '+str(x)+' + (HOENN_AREA_MAP_LEFT * 8 - 104);\n    subsprites[i].y = '+str(y)+';\n}'
  if re.search(r'void\s+'+name+r'\(',t):t=C.replace_function(t,name,new,'Violet habitat marker')
  else:t=t.rstrip()+'\n\n'+new+'\n'
 out[p]=t.encode()


def validate(s,out,stats):
 allsrc=Source(s.root,dict(s.overlay,**out))
 ls={x['id']:x for x in allsrc.json('data/layouts/layouts.json')['layouts'] if x.get('id')}
 maps={n:allsrc.json('data/maps/'+n+'/map.json') for n in NEW}
 checks=[]
 starts={'JohtoRoute31':(25,19),'VioletCity':(39,12),'VioletCity_Gym':(6,14),'SproutTower_1F':(6,14),'SproutTower_2F':(4,4),'SproutTower_3F':(4,4),'VioletCity_Academy':(4,7),'VioletCity_Mart':(4,7),'VioletCity_PokemonCenter_1F':(7,7)}
 for n,m in maps.items():
  l=ls[m['layout']];w,h=l['width'],l['height'];raw=allsrc.read(l['blockdata_filepath']);assert len(raw)==w*h*2
  vals=struct.unpack('<'+'H'*(w*h),raw)
  def walk(x,y):return 0<=x<w and 0<=y<h and ((vals[y*w+x]>>10)&3)==0 and (n not in ('JohtoRoute31','VioletCity') or vals[y*w+x]>>12!=1)
  solid={(o['x'],o['y']) for o in m['object_events'] if o['graphics_id']!='0'}
  for o in m['object_events']:
   assert 0<=o['x']<w and 0<=o['y']<h,(n,'NPC bounds',o)
   if n!='VioletCity_PokemonCenter_2F':assert walk(o['x'],o['y']),(n,'blocked NPC',o)
  for wp in m['warp_events']:
   dest=next((other for other in NEW if MID[other]==wp['dest_map']),None)
   if dest:
    d=maps[dest]['warp_events'];idx=int(wp['dest_warp_id'])
    assert 0<=idx<len(d) and d[idx]['dest_map']==m['id'],(n,'warp mismatch',wp)
  if n in starts:
   start=starts[n];assert walk(*start),(n,'spawn collision')
   seen={start};q=deque([start])
   while q:
    x,y=q.popleft()
    for xy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
     if xy not in seen and xy not in solid and walk(*xy):seen.add(xy);q.append(xy)
   for wp in m['warp_events']:
    pos=(wp['x'],wp['y']+1) if n in ('JohtoRoute31','VioletCity') else (wp['x'],wp['y'])
    assert pos in seen,(n,'unreachable warp',wp,pos)
   for o in m['object_events']:
    if o['graphics_id']=='OBJ_EVENT_GFX_NURSE':
     assert (o['x'],o['y']+2) in seen,(n,'nurse counter inaccessible');continue
    if n=='VioletCity_Mart' and o['graphics_id']=='OBJ_EVENT_GFX_CLERK':continue
    x,y=o['x'],o['y'];assert any(xy in seen for xy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))),(n,'unreachable NPC',o)
   if n=='JohtoRoute31':
    assert all((x,19) in seen for x in (24,25,26));assert all((0,y) in seen for y in range(11,15))
   if n=='VioletCity':assert all((39,y) in seen for y in range(11,15))
   checks.append({'map':n,'connected_walkable_cells':len(seen),'doors_and_NPCs_reachable':True})
  else:checks.append({'map':n,'existing_CableClub_layout_reused':True})
 allowed=set(re.findall(r'(?m)^\s*\.macro\s+(\w+)',s.text('asm/macros/event.inc')+'\n'+s.text('asm/macros/map.inc')))
 for p,b in out.items():
  if p.endswith('scripts.inc'):
   for ln in b.decode().splitlines():
    t=ln.strip()
    if not t or t.startswith(('@','.','#')) or t.endswith(':'):continue
    assert t.split()[0] in allowed,(p,'unknown event command',t)
 headers='\n'.join(s.text('include/constants/'+n) for n in ['species.h','items.h','songs.h','event_objects.h','global.h','trainers.h'])+'\n'+s.text('include/battle.h')
 refs=set()
 for p,b in out.items():
  if p.endswith(('.h','.c','.json','scripts.inc')):
   try:refs.update(re.findall(r'\b(?:SPECIES|ITEM|MUS|OBJ_EVENT_GFX|TRAINER_CLASS|TRAINER_PIC|TRAINER_ENCOUNTER_MUSIC)_[A-Z0-9_]+',b.decode()))
   except UnicodeDecodeError:pass
 missing=[v for v in refs if not re.search(r'\b'+re.escape(v)+r'\b',headers)]
 assert not missing,('unknown constants',missing)
 stats['static_checks']=checks;stats['native_build_and_emulator']='NOT_RUN_BY_GENERATOR'
 return stats
def apply(root,mutate=False):
 s=Source(root)
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 out,stats=build(s);validate(s,out,stats)
 again,_=build(Source(root,dict(s.overlay,**out)));assert out==again,'generation not idempotent'
 owned=[p for p in out if any(p.startswith('data/maps/'+n+'/') or p.startswith('data/layouts/'+n+'/') for n in NEW)]
 owned+=['include/constants/opponents_johto.h','src/data/trainers_johto.h','src/data/trainer_parties_johto.h','tools/johto/route31_wild.json']
 for p in owned:
  if s.exists(p):assert s.read(p)==out[p],'existing asset differs: '+p
 changed={p:b for p,b in out.items() if not s.exists(p) or s.read(p)!=b}
 print(json.dumps({'apply':mutate,'files':sorted(changed),'validation':stats},indent=2))
 if not mutate or not changed:return
 for p,b in s.used.items():assert (root/p).read_bytes()==b,'concurrent edit '+p
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');bak=root/'outputs/johto-violet-chapter-v1'/stamp;bak.mkdir(parents=True,exist_ok=False)
 manifest={'time':stamp,'validation':stats,'files':{}}
 for p,b in changed.items():
  target=root/p;old=target.read_bytes() if target.exists() else None
  manifest['files'][p]={'before':sha(old) if old is not None else None,'after':sha(b)}
  if old is not None:
   dest=bak/'before'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(old)
 (bak/'manifest.json').write_bytes(enc(manifest))
 for p,b in changed.items():
  target=root/p;target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.violet.tmp');assert not tmp.exists();tmp.write_bytes(b);tmp.replace(target)
 print('APPLIED',bak/'manifest.json')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--apply',action='store_true');a=ap.parse_args();apply(Path(a.root).resolve(),a.apply)
