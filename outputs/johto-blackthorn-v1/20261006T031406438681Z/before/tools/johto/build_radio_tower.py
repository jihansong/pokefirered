#!/usr/bin/env python3
"""Goldenrod broadcast rescue chapter, append-only and source-only until native QA."""
import argparse,copy,datetime,json,re,struct,subprocess,sys
from collections import deque
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_mahogany as M
C,V=M.C,M.V
Source,enc,sha=M.Source,M.enc,M.sha
OLD=M.OLD+M.NEW
LEGACY_FIRST='GoldenrodCity_RadioTower_1F'
NEW=['GoldenrodCity_RadioTower_'+str(i)+'F' for i in range(2,6)]+['GoldenrodUnderground','GoldenrodUnderground_Basement','GoldenrodWarehouse']
IDS=['GOLDENROD_CITY_RADIO_TOWER_'+str(i)+'F' for i in range(2,6)]+['GOLDENROD_UNDERGROUND','GOLDENROD_UNDERGROUND_BASEMENT','GOLDENROD_WAREHOUSE']
MID=dict(zip(NEW,['MAP_'+v for v in IDS]));MID[LEGACY_FIRST]='MAP_GOLDENROD_CITY_RADIO_TOWER_1F'
MARK='JOHTO_RADIO_TOWER_RESCUE_V1'
LEGACY_MAP=json.loads("{\"id\":\"MAP_GOLDENROD_CITY_RADIO_TOWER_1F\",\"name\":\"GoldenrodCity_RadioTower_1F\",\"layout\":\"LAYOUT_GOLDENROD_CITY_RADIO_TOWER_1F\",\"music\":\"MUS_CELADON\",\"region_map_section\":\"MAPSEC_GOLDENROD_CITY\",\"requires_flash\":false,\"weather\":\"WEATHER_NONE\",\"map_type\":\"MAP_TYPE_INDOOR\",\"allow_cycling\":false,\"allow_escaping\":false,\"allow_running\":true,\"show_map_name\":false,\"floor_number\":0,\"battle_scene\":\"MAP_BATTLE_SCENE_NORMAL\",\"connections\":null,\"object_events\":[{\"type\":\"object\",\"graphics_id\":\"OBJ_EVENT_GFX_SCIENTIST\",\"x\":9,\"y\":3,\"elevation\":3,\"movement_type\":\"MOVEMENT_TYPE_FACE_DOWN\",\"movement_range_x\":0,\"movement_range_y\":0,\"trainer_type\":\"TRAINER_TYPE_NONE\",\"trainer_sight_or_berry_tree_id\":\"0\",\"script\":\"GoldenrodCity_RadioTower_1F_ResearchDesk\",\"flag\":\"0\"},{\"type\":\"object\",\"graphics_id\":\"OBJ_EVENT_GFX_WOMAN_2\",\"x\":4,\"y\":6,\"elevation\":3,\"movement_type\":\"MOVEMENT_TYPE_FACE_DOWN\",\"movement_range_x\":0,\"movement_range_y\":0,\"trainer_type\":\"TRAINER_TYPE_NONE\",\"trainer_sight_or_berry_tree_id\":\"0\",\"script\":\"GoldenrodCity_RadioTower_1F_Reception\",\"flag\":\"0\"}],\"warp_events\":[{\"x\":6,\"y\":10,\"elevation\":3,\"dest_map\":\"MAP_GOLDENROD_CITY\",\"dest_warp_id\":\"3\"},{\"x\":7,\"y\":10,\"elevation\":3,\"dest_map\":\"MAP_GOLDENROD_CITY\",\"dest_warp_id\":\"3\"},{\"x\":8,\"y\":10,\"elevation\":3,\"dest_map\":\"MAP_GOLDENROD_CITY\",\"dest_warp_id\":\"3\"}],\"coord_events\":[],\"bg_events\":[]}")
LEGACY_LAYOUT=json.loads("{\"id\":\"LAYOUT_GOLDENROD_CITY_RADIO_TOWER_1F\",\"name\":\"GoldenrodCity_RadioTower_1F_Layout\",\"width\":15,\"height\":12,\"border_width\":2,\"border_height\":2,\"primary_tileset\":\"gTileset_Building\",\"secondary_tileset\":\"gTileset_GenericBuilding2\",\"blockdata_filepath\":\"data/layouts/GoldenrodCity_RadioTower_1F/map.bin\",\"border_filepath\":\"data/layouts/GoldenrodCity_RadioTower_1F/border.bin\"}")
LEGACY_TERRAIN_SHA="91502b668ca0d321e9611ac0ebf1ba50382b827dd2b6dc314fff33bd9f645186"
LEGACY_SCRIPT_SHA="e8a56698f9bfd2fd687380af24adce467784e577d5fcfb06470b69b8f4e421e9"
LEGACY_TEXT_SHA="451d34833fcad086c6e247eb89b9f9bbf1bb88b996c51849ffcd341310553d68"
FLAGS={'FLAG_JOHTO_RADIO_BASEMENT_ACCESS':54,'FLAG_JOHTO_RADIO_DIRECTOR_RESCUED':55,
 'FLAG_JOHTO_RADIO_GOT_TM11':56,'FLAG_HIDE_JOHTO_RADIO_SILVER':57,'FLAG_HIDE_JOHTO_RADIO_PETREL':58}
TRAINERS=[
 ('RADIO_GRUNT_A','TEAM_ROCKET','ROCKET_GRUNT_M','MALE',[('RATICATE',30),('GOLBAT',30)],836),
 ('RADIO_GRUNT_B','TEAM_ROCKET','ROCKET_GRUNT_M','MALE',[('GRIMER',30),('MUK',32)],837),
 ('RADIO_SCIENTIST','SCIENTIST','SCIENTIST','MALE',[('MAGNEMITE',30),('MAGNETON',32)],838),
 ('PETREL_RADIO','TEAM_ROCKET','ROCKET_GRUNT_M','MALE',[('KOFFING',30),('KOFFING',30),('KOFFING',30),('WEEZING',32)],839),
 ('SILVER_UNDERGROUND','RIVAL_LATE','RIVAL_LATE','MALE',[('GOLBAT',30),('MAGNEMITE',28),('HAUNTER',30),('SNEASEL',32),('FERALIGATR',32)],840),
 ('WAREHOUSE_GRUNT_A','TEAM_ROCKET','ROCKET_GRUNT_M','MALE',[('RATICATE',31),('KOFFING',31)],841),
 ('WAREHOUSE_GRUNT_B','TEAM_ROCKET','ROCKET_GRUNT_M','MALE',[('GLOOM',32),('GOLBAT',32)],842),
 ('WAREHOUSE_SCIENTIST','SCIENTIST','SCIENTIST','MALE',[('MAGNEMITE',31),('MAGNETON',33)],843),
 ('ARIANA_RADIO','TEAM_ROCKET','ROCKET_GRUNT_F','FEMALE',[('ARBOK',32),('GLOOM',32),('MURKROW',32)],844),
 ('ARCHER','TEAM_ROCKET','ROCKET_GRUNT_M','MALE',[('HOUNDOUR',33),('KOFFING',33),('HOUNDOOM',35)],845)]
DISPLAY={'RADIO_GRUNT_A':'GRUNT','RADIO_GRUNT_B':'GRUNT','RADIO_SCIENTIST':'SCIENTIST',
 'PETREL_RADIO':'PETREL','SILVER_UNDERGROUND':'SILVER','WAREHOUSE_GRUNT_A':'GRUNT',
 'WAREHOUSE_GRUNT_B':'GRUNT','WAREHOUSE_SCIENTIST':'SCIENTIST','ARIANA_RADIO':'ARIANA'}
def ident(n):return IDS[NEW.index(n)]
def warp(x,y,dst,index,elevation=3):
 return {'x':x,'y':y,'elevation':elevation,'dest_map':MID.get(dst,dst),'dest_warp_id':str(index)}
def obj(gfx,x,y,script,**kw):
 flag=kw.pop('flag','0');v=C.obj(gfx,x,y,script,**kw);v['flag']=flag
 if 'local_id' in v:assert re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',v['local_id'])
 return v

def radio_geometry(s):
 arrays={};source_templates={}
 specs=[('GoldenrodCity_RadioTower_'+str(k)+'F',k) for k in range(2,6)]+[
  ('GoldenrodUnderground',1),('GoldenrodUnderground_Basement',2),('GoldenrodWarehouse',3)]
 for n,k in specs:
  old='SilphCo_'+str(k)+'F';a=V.layout_array(s,'LAYOUT_SILPH_CO_'+str(k)+'F')
  # Native corporate floor/stair tiles keep their native Building/SilphCo attributes.
  C.fill(a,3,4,34,20,0x3334);C.fill(a,27,3,32,4,0x3334)
  keep={(28,2),(30,2)} if k in (2,3,4) else ({(8,20),(9,20),(31,2)} if k==1 else {(28,2)})
  if n=='GoldenrodWarehouse':keep={(28,2)}
  for wp in s.json('data/maps/'+old+'/map.json')['warp_events']:
   x,y=wp['x'],wp['y']
   if (x,y) not in keep:a[y][x]=0x3334
  # Guarded stairs are native stairs written after all general floor painting.
  src=V.layout_array(s,'LAYOUT_SILPH_CO_'+str(k)+'F')
  for x,y in keep:a[y][x]=src[y][x]
  arrays[n]=a;source_templates[n]=old
 return arrays,source_templates

def radio_story():
 scripts={};texts={}
 def add(n,k,body):
  scripts.setdefault(n,n+'_MapScripts::\n    .byte 0\n')
  scripts[n]+='\n'+n+'_'+k+'::\n'+body.strip()+'\n'
 def say(n,k,paras):
  add(n,k,'    msgbox '+n+'_Text_'+k+', MSGBOX_NPC\n    end')
  texts.setdefault(n,{})[k]=paras
 def trainer(n,k,paras):
  add(n,k,'    trainerbattle_single TRAINER_JOHTO_'+k+', '+n+'_Text_'+k+'Intro, '+n+'_Text_'+k+'Defeat\n    msgbox '+n+'_Text_'+k+'After, MSGBOX_NPC\n    end')
  texts.setdefault(n,{}).update({k+'Intro':[paras[0]],k+'Defeat':[paras[1]],k+'After':[paras[2]]})
 def gate(n,k,conditions,dest,warp_id,back,closed):
  branch='\n'.join('    '+condition+', '+n+'_'+k+'Closed' for condition in conditions)
  add(n,k,'''
    lockall
'''+branch+'''
    releaseall
    warp '''+MID[dest]+', '+str(warp_id)+'''
    waitstate
    end
'''+n+'_'+k+'''Closed::
    msgbox '''+n+'_Text_'+k+'''Closed
    applymovement OBJ_EVENT_ID_PLAYER, '''+n+'_'+k+'''Back
    waitmovement 0
    releaseall
    end
'''+n+'_'+k+'''Back:
    '''+back+'''
    step_end
''')
  texts.setdefault(n,{})[k+'Closed']=closed
 n='GoldenrodCity_RadioTower_1F'
 add(n,'BroadcastClerk','''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, GoldenrodCity_RadioTower_1F_BroadcastClerkAfter
    goto_if_unset FLAG_JOHTO_BADGE07_GET, GoldenrodCity_RadioTower_1F_BroadcastClerkBefore
    msgbox GoldenrodCity_RadioTower_1F_Text_BroadcastClerkAlarm
    release
    end
GoldenrodCity_RadioTower_1F_BroadcastClerkBefore::
    msgbox GoldenrodCity_RadioTower_1F_Text_BroadcastClerkBefore
    release
    end
GoldenrodCity_RadioTower_1F_BroadcastClerkAfter::
    msgbox GoldenrodCity_RadioTower_1F_Text_BroadcastClerkAfter
    release
    end
''')
 texts[n]={'BroadcastClerkBefore':["Welcome to the RADIO TOWER.\nOur studios are on the air.",
 "Travel through JOHTO. Report\nany strange signals to LANCE."],
 'BroadcastClerkAlarm':["TEAM ROCKET seized our studios!\nThey called for GIOVANNI.",
 "LANCE traced their lake signal.\nNow they control this station.",
 "Someone posing as our director\nwaits in the third-floor studio."],
 'BroadcastClerkAfter':["Our broadcast is normal again.\nThank you and your partner!",
 "The director is coordinating\nrepairs from the warehouse."]}
 gate(n,'UpperGate',['goto_if_unset FLAG_JOHTO_BADGE07_GET'],'GoldenrodCity_RadioTower_2F',1,'walk_right',
 ["The studios are recording.\nOnly staff may use the stairs."])
 say(n,'RadioNotice',["JOHTO RADIO NETWORK\nLocal news and POKEMON reports."])
 n='GoldenrodCity_RadioTower_2F'
 trainer(n,'RADIO_GRUNT_A',["A KANTO trainer, here again?","Our bosses are upstairs!","We lost the SILPH operation.\nThis broadcast brings us back."])
 trainer(n,'RADIO_GRUNT_B',["GIOVANNI will hear our call!","The station is still ours!","We cannot force the lake now.\nWe will summon our old leader."])
 n='GoldenrodCity_RadioTower_3F'
 trainer(n,'RADIO_SCIENTIST',["This signal reaches all JOHTO!","My amplification failed!","The real director has codes\nfor the upper-floor transmitter."])
 add(n,'Petrel','''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_BASEMENT_ACCESS, GoldenrodCity_RadioTower_3F_PetrelAfter
    goto_if_unset FLAG_JOHTO_BADGE07_GET, GoldenrodCity_RadioTower_3F_PetrelBefore
    goto_if_defeated TRAINER_JOHTO_PETREL_RADIO, GoldenrodCity_RadioTower_3F_PetrelVictory
    trainerbattle_single TRAINER_JOHTO_PETREL_RADIO, GoldenrodCity_RadioTower_3F_Text_PetrelIntro, GoldenrodCity_RadioTower_3F_Text_PetrelDefeat, GoldenrodCity_RadioTower_3F_PetrelVictory, NO_MUSIC
    goto GoldenrodCity_RadioTower_3F_PetrelVictory
GoldenrodCity_RadioTower_3F_PetrelVictory::
    setflag FLAG_JOHTO_RADIO_BASEMENT_ACCESS
    msgbox GoldenrodCity_RadioTower_3F_Text_PetrelAfter
    setflag FLAG_HIDE_JOHTO_RADIO_PETREL
    removeobject LOCALID_RADIO_PETREL
    release
    end
GoldenrodCity_RadioTower_3F_PetrelBefore::
    msgbox GoldenrodCity_RadioTower_3F_Text_PetrelBefore
    release
    end
GoldenrodCity_RadioTower_3F_PetrelAfter::
    msgbox GoldenrodCity_RadioTower_3F_Text_PetrelAfter
    release
    end
''')
 texts.setdefault(n,{}).update({'PetrelIntro':["PETREL: The director? Me?\nYou fell for it again!"],
 'PetrelDefeat':["Fine! The director is locked\nin the underground warehouse."],
 'PetrelAfter':["The warehouse access code is\nwritten in PETREL's notes.",
 "Use the UNDERGROUND entrance\non GOLDENROD's western side.",
 "Find the director. His code\nopens the upper studio doors."],
 'PetrelBefore':["The director is recording.\nPlease come back another day."]})
 gate(n,'UpperGate',['goto_if_unset FLAG_JOHTO_RADIO_DIRECTOR_RESCUED'],'GoldenrodCity_RadioTower_4F',1,'walk_left',
 ["The upper studio is sealed.\nRescue the real director first."])
 n='GoldenrodUnderground'
 add(n,'Worker','''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, GoldenrodUnderground_WorkerAfter
    goto_if_set FLAG_JOHTO_RADIO_BASEMENT_ACCESS, GoldenrodUnderground_WorkerCode
    msgbox GoldenrodUnderground_Text_WorkerBefore
    release
    end
GoldenrodUnderground_WorkerCode::
    msgbox GoldenrodUnderground_Text_WorkerCode
    release
    end
GoldenrodUnderground_WorkerAfter::
    msgbox GoldenrodUnderground_Text_WorkerAfter
    release
    end
''')
 texts[n]={'WorkerBefore':["The warehouse gate is locked.\nThe RADIO TOWER staff know why."],
 'WorkerCode':["You found the access code!\nThe warehouse lies downstairs.",
 "A red-haired trainer went in\nto challenge TEAM ROCKET."],
 'WorkerAfter':["Our warehouse can reopen now.\nThe RADIO TOWER is safe."]}
 gate(n,'BasementGate',['goto_if_unset FLAG_JOHTO_RADIO_BASEMENT_ACCESS'],'GoldenrodUnderground_Basement',1,'walk_left',
 ["A coded lock seals the stair.\nThe false director has the code."])
 n='GoldenrodUnderground_Basement'
 add(n,'Silver','''
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_RADIO_BASEMENT_ACCESS, GoldenrodUnderground_Basement_SilverBefore
    goto_if_defeated TRAINER_JOHTO_SILVER_UNDERGROUND, GoldenrodUnderground_Basement_SilverVictory
    trainerbattle_single TRAINER_JOHTO_SILVER_UNDERGROUND, GoldenrodUnderground_Basement_Text_SilverIntro, GoldenrodUnderground_Basement_Text_SilverDefeat, GoldenrodUnderground_Basement_SilverVictory, NO_MUSIC
    goto GoldenrodUnderground_Basement_SilverVictory
GoldenrodUnderground_Basement_SilverVictory::
    msgbox GoldenrodUnderground_Basement_Text_SilverAfter
    setflag FLAG_HIDE_JOHTO_RADIO_SILVER
    removeobject LOCALID_RADIO_SILVER
    release
    end
GoldenrodUnderground_Basement_SilverBefore::
    msgbox GoldenrodUnderground_Basement_Text_SilverBefore
    release
    end
''')
 texts[n]={'SilverIntro':["SILVER: You again! I will crush\nTEAM ROCKET with raw strength.",
 "You keep talking about trust.\nShow me what that means!"],
 'SilverDefeat':["Why does your partner keep\nanswering you with such power?"],
 'SilverAfter':["SILVER: Maybe strength alone\nis not enough. Go on.",
 "The director is ahead. I will\nkeep these ROCKETS from fleeing."],
 'SilverBefore':["Find the false director first.\nThis warehouse gate is sealed."]}
 gate(n,'WarehouseGate',['goto_if_not_defeated TRAINER_JOHTO_SILVER_UNDERGROUND'],'GoldenrodWarehouse',0,'walk_right',
 ["SILVER blocks the warehouse.\nSettle your rivalry first."])
 n='GoldenrodWarehouse'
 trainer(n,'WAREHOUSE_GRUNT_A',["No one leaves this warehouse!","You found our hiding place!","The director knows the code\nfor our sealed studio doors."])
 trainer(n,'WAREHOUSE_GRUNT_B',["The director stays right here!","The guards could not stop you!","ARIANA guards the transmitter.\nARCHER waits above her."])
 trainer(n,'WAREHOUSE_SCIENTIST',["The station will call GIOVANNI!","The link to KANTO is failing!","Without the director's code,\nthe upper studios remain shut."])
 add(n,'Director','''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, GoldenrodWarehouse_DirectorReward
    goto_if_set FLAG_JOHTO_RADIO_DIRECTOR_RESCUED, GoldenrodWarehouse_DirectorWaiting
    goto_if_not_defeated TRAINER_JOHTO_WAREHOUSE_GRUNT_A, GoldenrodWarehouse_DirectorBefore
    goto_if_not_defeated TRAINER_JOHTO_WAREHOUSE_GRUNT_B, GoldenrodWarehouse_DirectorBefore
    goto_if_not_defeated TRAINER_JOHTO_WAREHOUSE_SCIENTIST, GoldenrodWarehouse_DirectorBefore
    setflag FLAG_JOHTO_RADIO_DIRECTOR_RESCUED
    msgbox GoldenrodWarehouse_Text_DirectorRescued
    release
    end
GoldenrodWarehouse_DirectorBefore::
    msgbox GoldenrodWarehouse_Text_DirectorBefore
    release
    end
GoldenrodWarehouse_DirectorWaiting::
    msgbox GoldenrodWarehouse_Text_DirectorWaiting
    release
    end
GoldenrodWarehouse_DirectorReward::
    goto_if_set FLAG_JOHTO_RADIO_GOT_TM11, GoldenrodWarehouse_DirectorAfter
    giveitem ITEM_TM11
    goto_if_eq VAR_RESULT, FALSE, GoldenrodWarehouse_DirectorFull
    setflag FLAG_JOHTO_RADIO_GOT_TM11
GoldenrodWarehouse_DirectorAfter::
    goto_if_set FLAG_HOENN_RAYQUAZA_AWAKENED, GoldenrodWarehouse_DirectorHoennCalm
    goto_if_set FLAG_HOENN_SEAFLOOR_CLEARED, GoldenrodWarehouse_DirectorHoennStorm
    msgbox GoldenrodWarehouse_Text_DirectorAfter
    release
    end
GoldenrodWarehouse_DirectorHoennCalm::
    msgbox GoldenrodWarehouse_Text_DirectorHoennCalm
    release
    end
GoldenrodWarehouse_DirectorHoennStorm::
    msgbox GoldenrodWarehouse_Text_DirectorHoennStorm
    release
    end
GoldenrodWarehouse_DirectorFull::
    msgbox GoldenrodWarehouse_Text_DirectorFull
    release
    end
''')
 texts.setdefault(n,{}).update({'DirectorBefore':["The guards hold the studio code.\nPlease defeat all three guards."],
 'DirectorRescued':["You saved me! Use my studio code\nto reach the fourth floor.",
 "Their lake signal and this call\nare the same ROCKET operation.",
 "Stop their leaders. I will\ncoordinate the repairs here."],
 'DirectorWaiting':["The upper studio door is open.\nARIANA and ARCHER are upstairs.",
 "My staff are still trapped.\nPlease stop their broadcast."],
 'DirectorAfter':["SUNNY DAY is my thanks to you.\nOur staff can broadcast again.",
 "LANCE linked the KANTO thefts\nto their JOHTO radio project.",
 "HOENN's coastal stations sent\nreports of unusual weather.",
 "Finish JOHTO's LEAGUE challenge.\nThen meet HOENN's coastal teams."],
 'DirectorHoennStorm':["SUNNY DAY is my thanks to you.\nOur staff can broadcast again.",
 "HOENN's sea legend has awakened.\nCoastal storms are still raging.",
 "LANCE will share our news with\nHOENN's coastal rescue teams."],
 'DirectorHoennCalm':["SUNNY DAY is my thanks to you.\nOur staff can broadcast again.",
 "HOENN thanked you for calming\nthe storms with RAYQUAZA.",
 "The KANTO and JOHTO stations\ncan exchange their news safely."],
 'DirectorFull':["The radio signal is already off.\nYour victory is remembered.",
 "Make room for SUNNY DAY.\nI will keep your TM safe."]})
 n='GoldenrodCity_RadioTower_4F'
 trainer(n,'ARIANA_RADIO',["You stopped our lake project.\nNow you threaten our broadcast!","Your bond keeps defeating us!","ARCHER waits on the next floor.\nHe thinks GIOVANNI still hears."])
 gate(n,'UpperGate',['goto_if_not_defeated TRAINER_JOHTO_ARIANA_RADIO'],'GoldenrodCity_RadioTower_5F',0,'walk_right',
 ["ARIANA guards the final studio.\nDefeat her to reach the studio."])
 n='GoldenrodCity_RadioTower_5F'
 add(n,'Archer','''
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, GoldenrodCity_RadioTower_5F_ArcherAfter
    goto_if_unset FLAG_JOHTO_RADIO_DIRECTOR_RESCUED, GoldenrodCity_RadioTower_5F_ArcherBefore
    goto_if_not_defeated TRAINER_JOHTO_ARIANA_RADIO, GoldenrodCity_RadioTower_5F_ArcherBefore
    goto_if_defeated TRAINER_JOHTO_ARCHER, GoldenrodCity_RadioTower_5F_ArcherVictory
    trainerbattle_single TRAINER_JOHTO_ARCHER, GoldenrodCity_RadioTower_5F_Text_ArcherIntro, GoldenrodCity_RadioTower_5F_Text_ArcherDefeat, GoldenrodCity_RadioTower_5F_ArcherVictory, NO_MUSIC
    goto GoldenrodCity_RadioTower_5F_ArcherVictory
GoldenrodCity_RadioTower_5F_ArcherVictory::
    setflag FLAG_JOHTO_RADIO_TOWER_CLEARED
    msgbox GoldenrodCity_RadioTower_5F_Text_ArcherAfter
    removeobject LOCALID_RADIO_ARCHER
    release
    end
GoldenrodCity_RadioTower_5F_ArcherBefore::
    msgbox GoldenrodCity_RadioTower_5F_Text_ArcherBefore
    release
    end
GoldenrodCity_RadioTower_5F_ArcherAfter::
    msgbox GoldenrodCity_RadioTower_5F_Text_ArcherAfter
    release
    end
''')
 texts[n]={'ArcherIntro':["ARCHER: Our KANTO leader will\nhear this call and return!",
 "You stopped us there and at\nthe lake. I will stop you here!"],
 'ArcherDefeat':["GIOVANNI... Why did you not\nanswer us? Our plan is over."],
 'ArcherAfter':["The ROCKET call falls silent.\nJOHTO's normal news returns.",
 "The director awaits belowground.\nLANCE will check the east road."],
 'ArcherBefore':["The transmitter is protected.\nRescue the director first."]}
 return scripts,texts

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
 else:assert not additions,('incomplete Radio Tower flags',additions)
 out[p]=t.encode()
 p='include/constants/opponents_johto_radio_tower.h'
 h='#ifndef GUARD_OPPONENTS_JOHTO_RADIO_TOWER_H\n#define GUARD_OPPONENTS_JOHTO_RADIO_TOWER_H\n'
 for n,c,pic,gender,party,num in TRAINERS:h+='#define TRAINER_JOHTO_'+n+' (HOENN_TRAINERS_START + '+str(num)+')\n'
 out[p]=(h+'#endif\n').encode()
 for path in (s.root/'include/constants').glob('opponents*.h'):
  rel=path.relative_to(s.root).as_posix()
  if rel==p:continue
  used={int(v,0) for v in re.findall(r'HOENN_TRAINERS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',s.text(rel))}
  assert not(used&{v[-1] for v in TRAINERS}),('trainer collision',rel)
 p='include/constants/opponents.h';anchor='#include "constants/opponents_johto_mahogany.h"'
 out[p]=C.once(s.text(p),anchor,anchor+'\n#include "constants/opponents_johto_radio_tower.h"','Radio Tower trainer include').encode()
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
 out['src/data/trainer_parties_johto_radio_tower.h']=parties.encode();out['src/data/trainers_johto_radio_tower.h']=trainers.encode()
 for p,a,inc in [('src/data/trainers.h','#include "trainers_johto_mahogany.h"','#include "trainers_johto_radio_tower.h"'),('src/data/trainer_parties.h','#include "trainer_parties_johto_mahogany.h"','#include "trainer_parties_johto_radio_tower.h"')]:
  out[p]=C.once(s.text(p),a,a+'\n'+inc,'Radio Tower trainer data').encode()
 p='data/event_scripts.s';t=s.text(p);block='@ '+MARK+'\n'+''.join('    .include "data/maps/'+n+'/'+f+'"\n' for n in NEW for f in ['scripts.inc','text.inc'])
 if MARK not in t:assert not any('data/maps/'+n+'/' in t for n in NEW);t=t.rstrip()+'\n\n'+block
 else:assert block in t
 out[p]=t.encode()
 p='tools/johto/build_mahogany.py';t=s.text(p)
 guard=' # RADIO_TOWER_EXTENSION_GUARD\n if any(n not in OLD + NEW for n in s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]):\n  raise RuntimeError("Radio Tower extension exists; use build_radio_tower.py")\n'
 if '# RADIO_TOWER_EXTENSION_GUARD' not in t:
  t,n=re.subn(r'(?m)^def build\(s\):\n',lambda m:m.group(0)+guard,t);assert n==1
 else:assert guard in t
 # No Blackthorn route exists in this chapter; do not claim that it is open.
 before='The RADIO TOWER is safe again.\nThe road to BLACKTHORN is open.'
 after='The RADIO TOWER is safe again.\nLANCE is checking the east road.'
 old_literal=json.dumps(before);new_literal=json.dumps(after)
 assert old_literal in t or new_literal in t,'Mahogany eastern-road text source changed.'
 t=C.once(t,old_literal,new_literal,'Radio follow-up eastern road status')
 out[p]=t.encode()
 p='data/maps/MahoganyTown/text.inc'
 out[p]=C.once(s.text(p),C.texts('MahoganyTown',{'EastOpen':[before]}),C.texts('MahoganyTown',{'EastOpen':[after]}),'Radio follow-up eastern road dialogue').encode()

def build(s):
 out={};stats={'chapter':'Goldenrod Radio Tower rescue','save_layout_changed':False,
  'native_build_and_emulator':'NOT_RUN_BY_GENERATOR',
  'visual_limits':['Existing native Kanto corporate tiles and trainer portraits are reused.','The director coordinates repairs from the warehouse after the rescue.'],
  'not_implemented':['Route44/IcePath/Blackthorn/Clair/DragonDen','Johto League','Full original Underground side services']}
 groups=s.json('data/maps/map_groups.json');assert groups['gMapGroup_JohtoEntry'] in (OLD,OLD+NEW)
 assert LEGACY_FIRST in OLD,'The original Radio research lobby must already exist.'
 for k,v in groups.items():
  if k not in ('group_order','gMapGroup_JohtoEntry'):assert not(set(v)&set(NEW))
 groups['gMapGroup_JohtoEntry']=OLD+NEW;out['data/maps/map_groups.json']=enc(groups)
 arrays,templates=radio_geometry(s);ls=s.json('data/layouts/layouts.json')
 for n,a in arrays.items():
  base=next(v for v in ls['layouts'] if v.get('id')=='LAYOUT_SILPH_CO_'+templates[n].split('_')[-1])
  row={'id':'LAYOUT_'+ident(n),'name':n+'_Layout','width':len(a[0]),'height':len(a),
   'border_width':2,'border_height':2,'primary_tileset':'gTileset_Building','secondary_tileset':'gTileset_SilphCo',
   'blockdata_filepath':'data/layouts/'+n+'/map.bin','border_filepath':'data/layouts/'+n+'/border.bin'}
  hits=[v for v in ls['layouts'] if v.get('id')==row['id']];assert not hits or hits==[row]
  if not hits:ls['layouts'].append(row)
  out[row['blockdata_filepath']]=C.pack(a);out[row['border_filepath']]=s.read(base['border_filepath'])
 city=s.json('data/maps/GoldenrodCity/map.json');prior_warps=copy.deepcopy(city['warp_events'])
 assert len(city['warp_events']) in (5,6)
 assert city['warp_events'][3]=={'x':11,'y':17,'elevation':0,'dest_map':MID[LEGACY_FIRST],'dest_warp_id':'1'},'Existing Radio entrance changed.'
 city_layout=next(v for v in ls['layouts'] if v.get('id')==city['layout'])
 assert city_layout['primary_tileset']=='gTileset_General' and city_layout['secondary_tileset']=='gTileset_SaffronCity'
 w,h=city_layout['width'],city_layout['height'];raw=s.read(city_layout['blockdata_filepath'])
 city_a=[list(struct.unpack_from('<'+'H'*w,raw,y*w*2)) for y in range(h)]
 facade=V.crop(V.layout_array(s,'LAYOUT_SAFFRON_CITY'),21,11,5,4)
 n='GoldenrodUnderground';hits=[(i,v) for i,v in enumerate(city['warp_events']) if v['dest_map']==MID[n]]
 assert len(hits)<=1,'Duplicate Underground entrance.'
 protected=[(v['x'],v['y']) for kind in ['object_events','warp_events','coord_events','bg_events'] for v in city[kind] if v.get('dest_map')!=MID[n]]
 if hits:
  index,entry=hits[0];x,y=entry['x']-1,entry['y']-3
  assert index==5 and entry['dest_warp_id']=='0'
  assert V.crop(city_a,x,y,5,4)==facade,'Owned Underground city facade changed.'
 else:
  assert len(city['warp_events'])==5
  choices=[(x,y) for x,y in [(3,29),(13,25),(16,20)] if x>=2 and y>=2 and x+5<w-2 and y+5<h-2
   and not any(x<=xx<x+5 and y<=yy<y+5 for xx,yy in protected)
   and all(cell in (0x3001,0x3195) for row in V.crop(city_a,x,y,5,5) for cell in row)]
  assert choices,'No unoccupied safe western Underground facade plot.'
  x,y=choices[0];index=len(city['warp_events'])
  city['warp_events'].append(warp(x+1,y+3,n,0,elevation=0))
  C.paste(city_a,facade,x,y);city_a[y+4][x+1]=0x3195
 added={n:index,LEGACY_FIRST:3}
 assert city['warp_events'][:len(prior_warps)]==prior_warps,'Existing Goldenrod warp IDs changed.'
 out['data/maps/GoldenrodCity/map.json']=enc(city);out[city_layout['blockdata_filepath']]=C.pack(city_a)
 out['data/layouts/layouts.json']=enc(ls)
 maps={};scripts,rows=radio_story();tx={n:C.texts(n,d) for n,d in rows.items()}
 def coord(x,y,label):return {'type':'trigger','x':x,'y':y,'elevation':0,'var':'VAR_TEMP_0','var_value':'0','script':label}
 # Preserve the original 15x12 research reception, both NPCs and all three exits.
 first=s.json('data/maps/'+LEGACY_FIRST+'/map.json');l=next(v for v in ls['layouts'] if v.get('id')==first['layout'])
 assert l==LEGACY_LAYOUT,'Original Radio lobby layout metadata changed.'
 new_first=copy.deepcopy(LEGACY_MAP)
 new_first['object_events'].append(obj('WORKER_F',3,8,LEGACY_FIRST+'_BroadcastClerk'))
 new_first['warp_events'].append(warp(12,3,'GoldenrodCity_RadioTower_2F',1))
 new_first['coord_events'].append(coord(12,3,LEGACY_FIRST+'_UpperGate'))
 assert first in (LEGACY_MAP,new_first),'Original Radio lobby metadata or objects changed.'
 raw=s.read(l['blockdata_filepath']);assert len(raw)==15*12*2
 original=bytearray(raw);original[(3*15+12)*2:(3*15+12)*2+2]=struct.pack('<H',0x3281)
 assert sha(bytes(original))==LEGACY_TERRAIN_SHA,'Original Radio lobby terrain changed outside the new stair.'
 assert struct.unpack_from('<H',raw,(3*15+12)*2)[0] in (0x3281,0x3274)
 final_first=bytearray(original);struct.pack_into('<H',final_first,(3*15+12)*2,0x3274)
 out[l['blockdata_filepath']]=bytes(final_first)
 for filename,expected,addition in [('scripts.inc',LEGACY_SCRIPT_SHA,scripts[LEGACY_FIRST].split('    .byte 0\n',1)[1]),('text.inc',LEGACY_TEXT_SHA,tx[LEGACY_FIRST])]:
  p='data/maps/'+LEGACY_FIRST+'/'+filename;old=s.text(p);mark='@ '+MARK+' LOBBY\n'
  if mark in old:
   head,tail=old.split(mark,1);assert tail==addition,'Owned lobby script/text extension differs.'
  else:head=old
  assert sha(head.encode())==expected,('Original Radio lobby source changed.',filename)
  out[p]=(head+mark+addition).encode()
 out['data/maps/'+LEGACY_FIRST+'/map.json']=enc(new_first);maps[LEGACY_FIRST]=new_first
 def temp(n,old):
  j=s.json('data/maps/'+old+'/map.json');j.update(id=MID[n],name=n,layout='LAYOUT_'+ident(n),region_map_section='MAPSEC_GOLDENROD_CITY',connections=None)
  j.pop('connections_no_include',None);j['music']='MUS_SILPH'
  for key in ['object_events','warp_events','coord_events','bg_events']:j[key]=[]
  maps[n]=j;return j
 for k in range(2,6):
  n='GoldenrodCity_RadioTower_'+str(k)+'F';j=temp(n,'SilphCo_'+str(k)+'F')
  if k==2:
   j['warp_events']=[warp(28,2,'GoldenrodCity_RadioTower_3F',0),warp(30,2,LEGACY_FIRST,3)]
   j['object_events']=[obj('ROCKET_M',10,8,n+'_RADIO_GRUNT_A',flag='FLAG_JOHTO_RADIO_TOWER_CLEARED'),obj('ROCKET_M',22,12,n+'_RADIO_GRUNT_B',flag='FLAG_JOHTO_RADIO_TOWER_CLEARED')]
  elif k==3:
   j['warp_events']=[warp(28,2,'GoldenrodCity_RadioTower_2F',0),warp(30,2,'GoldenrodCity_RadioTower_4F',1)]
   j['object_events']=[obj('SCIENTIST',9,12,n+'_RADIO_SCIENTIST',flag='FLAG_JOHTO_RADIO_TOWER_CLEARED'),
    obj('OLD_MAN_1',16,8,n+'_Petrel',local_id='LOCALID_RADIO_PETREL',flag='FLAG_HIDE_JOHTO_RADIO_PETREL')]
   j['coord_events']=[coord(30,2,n+'_UpperGate')]
  elif k==4:
   j['warp_events']=[warp(28,2,'GoldenrodCity_RadioTower_5F',0),warp(30,2,'GoldenrodCity_RadioTower_3F',1)]
   j['object_events']=[obj('ROCKET_F',16,8,n+'_ARIANA_RADIO',flag='FLAG_JOHTO_RADIO_TOWER_CLEARED')]
   j['coord_events']=[coord(28,2,n+'_UpperGate')]
  else:
   j['warp_events']=[warp(28,2,'GoldenrodCity_RadioTower_4F',0)]
   j['object_events']=[obj('ROCKET_M',16,8,n+'_Archer',local_id='LOCALID_RADIO_ARCHER',flag='FLAG_JOHTO_RADIO_TOWER_CLEARED')]
 n='GoldenrodUnderground';j=temp(n,'SilphCo_1F')
 j['warp_events']=[warp(8,20,'MAP_GOLDENROD_CITY',added[n]),warp(31,2,'GoldenrodUnderground_Basement',1)]
 j['object_events']=[obj('WORKER_M',10,8,n+'_Worker')];j['coord_events']=[coord(31,2,n+'_BasementGate')]
 n='GoldenrodUnderground_Basement';j=temp(n,'SilphCo_2F')
 j['warp_events']=[warp(28,2,'GoldenrodWarehouse',0),warp(30,2,'GoldenrodUnderground',1)]
 j['object_events']=[obj('BLUE',16,8,n+'_Silver',local_id='LOCALID_RADIO_SILVER',flag='FLAG_HIDE_JOHTO_RADIO_SILVER')]
 j['coord_events']=[coord(28,2,n+'_WarehouseGate')]
 n='GoldenrodWarehouse';j=temp(n,'SilphCo_3F')
 j['warp_events']=[warp(28,2,'GoldenrodUnderground_Basement',0)]
 j['object_events']=[obj('ROCKET_M',9,8,n+'_WAREHOUSE_GRUNT_A',flag='FLAG_JOHTO_RADIO_TOWER_CLEARED'),
  obj('ROCKET_M',23,8,n+'_WAREHOUSE_GRUNT_B',flag='FLAG_JOHTO_RADIO_TOWER_CLEARED'),
  obj('SCIENTIST',16,12,n+'_WAREHOUSE_SCIENTIST',flag='FLAG_JOHTO_RADIO_TOWER_CLEARED'),
  obj('GENTLEMAN',16,16,n+'_Director')]
 for n,j in maps.items():
  if n==LEGACY_FIRST:continue
  out['data/maps/'+n+'/map.json']=enc(j);out['data/maps/'+n+'/scripts.inc']=scripts[n].encode();out['data/maps/'+n+'/text.inc']=tx[n].encode()
 shared(s,out)
 stats.update(map_count=len(NEW),new_trainer_ids=[v[-1] for v in TRAINERS],radio_clear_flag_preexisting_offset=52,new_flag_offsets=FLAGS,city_warp_ids=added,
  preserved_research_lobby={'map_id':LEGACY_MAP['id'],'dimensions':[15,12],'original_objects':2,'original_warps':3,'added_stair_warp':3,'terrain_changed_cells':1},
  johto_map_count=len(OLD+NEW),map_section_growth=0,bag_or_pokemon_struct_growth=0)
 return out,stats

def validate(s,out,stats):
 final=Source(s.root,dict(s.overlay,**out));ls={v['id']:v for v in final.json('data/layouts/layouts.json')['layouts'] if v.get('id')}
 maps={n:final.json('data/maps/'+n+'/map.json') for n in [LEGACY_FIRST]+NEW}
 defs=final.text('include/constants/metatile_behaviors.h')
 values={n:int(v,0) for n,v in re.findall(r'^#define\s+(MB_\w+)\s+(0x[0-9A-Fa-f]+|\d+)\b',defs,re.M)}
 warp_b={v for n,v in values.items() if re.search(r'WARP|DOOR|LADDER|ESCALATOR',n)}
 num=int(re.search(r'^#define\s+NUM_METATILES_IN_PRIMARY\s+(\d+)\b',final.text('include/fieldmap.h'),re.M).group(1));assert num==640
 def behavior(l,t):
  t&=0x3ff;kind='primary' if t<num else 'secondary';label=l[kind+'_tileset'].removeprefix('gTileset_')
  assert not label.startswith('Em'),'Radio maps retain native Kanto tiles'
  folder=re.sub(r'([A-Za-z])(\d)',r'\1_\2',re.sub(r'([a-z0-9])([A-Z])',r'\1_\2',label)).lower()
  b=final.read('data/tilesets/'+kind+'/'+folder+'/metatile_attributes.bin')
  index=t if kind=='primary' else t-num
  return struct.unpack_from('<I',b,index*4)[0]&0x1ff
 checks=[];checked=0
 for n,m in maps.items():
  l=ls[m['layout']];w,h=l['width'],l['height'];assert(w+15)*(h+14)<=0x2800,(n,'map view buffer overflow')
  b=final.read(l['blockdata_filepath']);assert len(b)==w*h*2;a=struct.unpack('<'+'H'*(w*h),b)
  assert not m.get('connections_no_include') and m['connections'] is None
  assert m['region_map_section']=='MAPSEC_GOLDENROD_CITY'
  def walk(x,y):return 0<=x<w and 0<=y<h and (a[y*w+x]>>10)&3==0
  blocked={(o['x'],o['y']) for o in m['object_events']}
  seed=(7,9) if n==LEGACY_FIRST else (16,18)
  q=deque([seed]);seen={seed};assert walk(*seed)
  while q:
   x,y=q.popleft()
   for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if (xx,yy) not in seen and (xx,yy) not in blocked and walk(xx,yy):
     seen.add((xx,yy));q.append((xx,yy))
  for wp in m['warp_events']:
   x,y=wp['x'],wp['y'];assert (x,y) in seen,(n,'native warp inaccessible',wp)
   preserved_side_pad=n==LEGACY_FIRST and wp in (LEGACY_MAP['warp_events'][0],LEGACY_MAP['warp_events'][2])
   if preserved_side_pad:assert behavior(l,a[y*w+x])==values['MB_NORMAL'],'Original Radio side landing pad behavior changed.'
   else:assert behavior(l,a[y*w+x]) in warp_b,(n,'warp on non-warp native tile',wp,hex(a[y*w+x]))
   dst=wp['dest_map'];assert dst in set(MID.values())|{'MAP_GOLDENROD_CITY'},(n,'foreign/unimplemented warp destination',dst)
   target=next((m2 for m2 in maps.values() if m2['id']==dst),final.json('data/maps/GoldenrodCity/map.json'))
   assert 0<=int(wp['dest_warp_id'])<len(target['warp_events'])
   checked+=not preserved_side_pad
  for o in m['object_events']:
   x,y=o['x'],o['y'];assert walk(x,y),(n,'NPC on blocked tile',o)
   assert any(z in seen for z in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),(n,'NPC cannot be faced',o)
   if 'local_id' in o:assert isinstance(o['local_id'],str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',o['local_id'])
  for co in m['coord_events']:assert (co['x'],co['y']) in seen,(n,'unreachable gate',co)
  checks.append({'map':n,'reachable_tiles':len(seen),'buffer_metatiles':(w+15)*(h+14),'native_warps_checked':len(m['warp_events'])})
 before=s.json('data/maps/map_groups.json');after=final.json('data/maps/map_groups.json')
 assert after['gMapGroup_JohtoEntry']==OLD+NEW
 assert all(after[k]==v for k,v in before.items() if k!='gMapGroup_JohtoEntry')
 original=s.json('data/layouts/layouts.json')['layouts'];assert final.json('data/layouts/layouts.json')['layouts'][:len(original)]==original
 city_old=s.json('data/maps/GoldenrodCity/map.json');city_new=final.json('data/maps/GoldenrodCity/map.json')
 assert city_new['warp_events'][:len(city_old['warp_events'])]==city_old['warp_events']
 for key in city_old:
  if key!='warp_events':assert city_old[key]==city_new[key],('original Goldenrod metadata changed',key)
 assert not any(p in out for p in ['include/global.h','include/pokemon.h','src/save.c','src/load_save.c','src/data/wild_encounters.json','src/region_map.c','src/title_screen.c','src/intro.c'])
 first=maps[LEGACY_FIRST];base=copy.deepcopy(first)
 assert first['object_events'][-1]==obj('WORKER_F',3,8,LEGACY_FIRST+'_BroadcastClerk')
 assert first['warp_events'][-1]==warp(12,3,'GoldenrodCity_RadioTower_2F',1)
 assert first['coord_events']==[{'type':'trigger','x':12,'y':3,'elevation':0,'var':'VAR_TEMP_0','var_value':'0','script':LEGACY_FIRST+'_UpperGate'}]
 base['object_events']=base['object_events'][:-1];base['warp_events']=base['warp_events'][:-1];base['coord_events']=[]
 assert base==LEGACY_MAP,'Original research lobby metadata/object/warp contract changed.'
 assert ls[first['layout']]==LEGACY_LAYOUT
 data=bytearray(final.read(LEGACY_LAYOUT['blockdata_filepath']))
 assert struct.unpack_from('<H',data,(3*15+12)*2)[0]==0x3274
 struct.pack_into('<H',data,(3*15+12)*2,0x3281)
 assert sha(bytes(data))==LEGACY_TERRAIN_SHA
 for f,hsh in [('scripts.inc',LEGACY_SCRIPT_SHA),('text.inc',LEGACY_TEXT_SHA)]:
  body=final.text('data/maps/'+LEGACY_FIRST+'/'+f);prefix=body.split('@ '+MARK+' LOBBY\n',1)[0]
  assert sha(prefix.encode())==hsh,'Original research source prefix changed.'
 assert city_new['warp_events'][3]['dest_map']==MID[LEGACY_FIRST] and city_new['warp_events'][3]['dest_warp_id']=='1'
 assert city_new['warp_events'][5]['dest_map']==MID['GoldenrodUnderground'] and len(city_new['warp_events'])==6
 # Only the new 5x4 facade and its one approach tile may alter the existing city.
 cl=ls[city_new['layout']];oldraw=s.read(cl['blockdata_filepath']);newraw=final.read(cl['blockdata_filepath'])
 door=city_new['warp_events'][5];xx,yy=door['x']-1,door['y']-3
 allowed={(x,y) for y in range(yy,yy+4) for x in range(xx,xx+5)}|{(xx+1,yy+4)}
 for y in range(cl['height']):
  for x in range(cl['width']):
   i=(y*cl['width']+x)*2
   assert oldraw[i:i+2]==newraw[i:i+2] or (x,y) in allowed,('City terrain changed outside the Underground plot.',x,y)
 assert behavior(cl,struct.unpack_from('<H',newraw,(door['y']*cl['width']+door['x'])*2)[0]) in warp_b
 global_text=final.text('include/global.h')
 trainer_bytes=int(re.search(r'u8\s+hoennTrainerFlags\[(0x[0-9A-Fa-f]+|\d+)\]',global_text).group(1),0)
 story_bytes=int(re.search(r'u8\s+hoennFlags\[(0x[0-9A-Fa-f]+|\d+)\]',global_text).group(1),0)
 assert max(v[-1] for v in TRAINERS)<trainer_bytes*8,'native saved trainer bitfield exhausted'
 story_start=re.search(r'JOHTO_STORY_FLAGS_START\s+\(HOENN_FLAGS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)\)',final.text('include/constants/flags_johto_story.h'))
 assert story_start and int(story_start.group(1),0)+max(FLAGS.values())<story_bytes*8,'native saved story bitfield exhausted'
 stats['saved_bitfield_bounds']={'last_trainer_offset':max(v[-1] for v in TRAINERS),'trainer_bits':trainer_bytes*8,'last_hoenn_story_offset':int(story_start.group(1),0)+max(FLAGS.values()),'story_bits':story_bytes*8}
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
 assert all(re.search(r'\b'+re.escape(v)+r'\b',headers) for v in refs),('unknown native constants',sorted(v for v in refs if not re.search(r'\b'+re.escape(v)+r'\b',headers)))
 for n,k,trainer_id in [('GoldenrodCity_RadioTower_3F','Petrel','PETREL_RADIO'),('GoldenrodUnderground_Basement','Silver','SILVER_UNDERGROUND'),('GoldenrodCity_RadioTower_5F','Archer','ARCHER')]:
  body=out['data/maps/'+n+'/scripts.inc'].decode()
  assert n+'_'+k+'Victory, NO_MUSIC' in body and 'goto '+n+'_'+k+'Victory' in body,(n,'missing explicit victory callback')
  assert 'goto_if_defeated TRAINER_JOHTO_'+trainer_id in body
 reward=out['data/maps/GoldenrodWarehouse/scripts.inc'].decode()
 assert reward.index('goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED')<reward.index('giveitem ITEM_TM11')
 assert 'goto_if_eq VAR_RESULT, FALSE, GoldenrodWarehouse_DirectorFull\n    setflag FLAG_JOHTO_RADIO_GOT_TM11' in reward
 archer=out['data/maps/GoldenrodCity_RadioTower_5F/scripts.inc'].decode()
 assert archer.count('setflag FLAG_JOHTO_RADIO_TOWER_CLEARED')==1
 for p,b in final.used.items():
  if p not in out and p not in s.overlay:s.used[p]=b
 stats.update(static_checks=checks,native_warp_behaviors_checked=checked,preserved_original_side_landing_pads=2,map_sections_max=len(final.json('src/data/region_map/region_map_sections.json')['map_sections'])-1)
 return stats

def apply(root,mutate=False):
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 s=Source(root);out,stats=build(s);validate(s,out,stats)
 repeat,_=build(Source(root,dict(s.overlay,**out)));assert repeat==out,'Radio generator output is not idempotent'
 owned=[p for p in out if any(p.startswith('data/maps/'+n+'/') or p.startswith('data/layouts/'+n+'/') for n in NEW)]
 owned+=['include/constants/opponents_johto_radio_tower.h','src/data/trainers_johto_radio_tower.h','src/data/trainer_parties_johto_radio_tower.h']
 for p in owned:
  if s.exists(p):assert s.read(p)==out[p],('owned Radio artifact differs',p)
 changed={p:b for p,b in out.items() if not s.exists(p) or s.read(p)!=b}
 print(json.dumps({'apply':mutate,'files':sorted(changed),'validation':stats},indent=2))
 if not mutate or not changed:return
 for p,b in s.used.items():assert (root/p).read_bytes()==b,('concurrent source edit',p)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=root/'outputs/johto-radio-tower-v1'/stamp;dest.mkdir(parents=True,exist_ok=False);manifest={'time':stamp,'validation':stats,'files':{}}
 for p,b in changed.items():
  target=root/p;old=target.read_bytes() if target.exists() else None
  manifest['files'][p]={'before':sha(old) if old is not None else None,'after':sha(b)}
  if old is not None:
   backup=dest/'before'/p;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(old)
 (dest/'manifest.json').write_bytes(enc(manifest))
 for p,b in changed.items():
  target=root/p;target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.radio.tmp')
  assert not tmp.exists();tmp.write_bytes(b);tmp.replace(target)
 print('APPLIED',dest/'manifest.json')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root).resolve(),a.apply)
