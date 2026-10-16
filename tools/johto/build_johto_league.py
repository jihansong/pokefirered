#!/usr/bin/env python3
"""Append Johto's independent Indigo challenge without changing saved structs."""
import argparse,copy,datetime,json,re,struct,subprocess,sys
from pathlib import Path
from collections import deque
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_blackthorn as B
R,M,C,V=B.R,B.M,B.C,B.V
Source,enc,sha=B.Source,B.enc,B.sha
OLD=B.OLD+B.NEW
NEW=['JohtoRoute27','TohjoFalls','JohtoRoute26','JohtoVictoryRoad_1F','JohtoIndigoPlateau',
 'JohtoLeague_PokemonCenter_1F','JohtoLeague_WillsRoom','JohtoLeague_KogasRoom',
 'JohtoLeague_BrunosRoom','JohtoLeague_KarensRoom','JohtoLeague_LancesRoom','JohtoLeague_HallOfFame']
IDS=['JOHTO_ROUTE27','TOHJO_FALLS','JOHTO_ROUTE26','JOHTO_VICTORY_ROAD_1F','JOHTO_INDIGO_PLATEAU',
 'JOHTO_LEAGUE_POKEMON_CENTER_1F','JOHTO_LEAGUE_WILLS_ROOM','JOHTO_LEAGUE_KOGAS_ROOM',
 'JOHTO_LEAGUE_BRUNOS_ROOM','JOHTO_LEAGUE_KARENS_ROOM','JOHTO_LEAGUE_LANCES_ROOM','JOHTO_LEAGUE_HALL_OF_FAME']
MID=dict(zip(NEW,['MAP_'+v for v in IDS]))
MARK='JOHTO_LEAGUE_INDEPENDENT_HOF_V1'
FLAGS={'FLAG_JOHTO_SILVER_LEAGUE_RESOLVED':63,'FLAG_JOHTO_WILL_CLEARED':64,
 'FLAG_JOHTO_KOGA_CLEARED':65,'FLAG_JOHTO_BRUNO_CLEARED':66,'FLAG_JOHTO_KAREN_CLEARED':67,
 'FLAG_JOHTO_LANCE_CHAMPION_CLEARED':68,'FLAG_JOHTO_LEAGUE_CLEARED':69,'FLAG_JOHTO_LEAGUE_ARRIVED':70}
TRAINERS=[
 ('SILVER_VICTORY_ROAD','RIVAL_LATE','RIVAL_LATE','MALE',[
  ('SNEASEL',43,['ICE_PUNCH','FAINT_ATTACK','SLASH','QUICK_ATTACK']),
  ('CROBAT',44,['WING_ATTACK','BITE','CONFUSE_RAY','TOXIC']),
  ('MAGNETON',43,['THUNDERBOLT','THUNDER_WAVE','SONIC_BOOM','SWIFT']),
  ('GENGAR',43,['SHADOW_BALL','HYPNOSIS','DREAM_EATER','CONFUSE_RAY']),
  ('ALAKAZAM',43,['PSYCHIC','RECOVER','REFLECT','FUTURE_SIGHT']),
  ('FERALIGATR',46,['SURF','ICE_PUNCH','CRUNCH','SLASH'])],880),
 ('WILL','ELITE_FOUR','PSYCHIC_M','MALE',[
  ('XATU',40,['PSYCHIC','CONFUSE_RAY','QUICK_ATTACK','FUTURE_SIGHT']),
  ('JYNX',41,['PSYCHIC','ICE_PUNCH','LOVELY_KISS','DOUBLE_SLAP']),
  ('EXEGGUTOR',41,['PSYCHIC','REFLECT','LEECH_SEED','EGG_BOMB']),
  ('SLOWBRO',41,['PSYCHIC','SURF','AMNESIA','CURSE']),
  ('XATU',42,['PSYCHIC','CONFUSE_RAY','QUICK_ATTACK','FUTURE_SIGHT'])],881),
 ('KOGA','ELITE_FOUR','LEADER_KOGA','MALE',[
  ('ARIADOS',40,['SPIDER_WEB','BATON_PASS','DOUBLE_TEAM','GIGA_DRAIN']),
  ('VENOMOTH',41,['PSYCHIC','TOXIC','SUPERSONIC','GUST']),
  ('FORRETRESS',43,['SPIKES','PROTECT','SWIFT','EXPLOSION']),
  ('MUK',42,['MINIMIZE','ACID_ARMOR','SLUDGE_BOMB','TOXIC']),
  ('CROBAT',44,['WING_ATTACK','TOXIC','DOUBLE_TEAM','QUICK_ATTACK'])],882),
 ('BRUNO','ELITE_FOUR','ELITE_FOUR_BRUNO','MALE',[
  ('HITMONTOP',42,['DIG','QUICK_ATTACK','DETECT','TRIPLE_KICK']),
  ('HITMONLEE',42,['HI_JUMP_KICK','FORESIGHT','DOUBLE_KICK','SWAGGER']),
  ('HITMONCHAN',42,['THUNDER_PUNCH','ICE_PUNCH','FIRE_PUNCH','MACH_PUNCH']),
  ('ONIX',43,['ROCK_SLIDE','EARTHQUAKE','SANDSTORM','BIND']),
  ('MACHAMP',46,['CROSS_CHOP','ROCK_SLIDE','FORESIGHT','VITAL_THROW'])],883),
 ('KAREN','ELITE_FOUR','COOLTRAINER_F','FEMALE',[
  ('UMBREON',42,['FAINT_ATTACK','CONFUSE_RAY','SAND_ATTACK','MEAN_LOOK']),
  ('VILEPLUME',42,['PETAL_DANCE','STUN_SPORE','ACID','MOONLIGHT']),
  ('MURKROW',44,['FAINT_ATTACK','WHIRLWIND','PURSUIT','QUICK_ATTACK']),
  ('GENGAR',45,['SHADOW_BALL','DESTINY_BOND','LICK','SPITE']),
  ('HOUNDOOM',47,['FLAMETHROWER','CRUNCH','ROAR','PURSUIT'])],884),
 ('LANCE_CHAMPION','CHAMPION','ELITE_FOUR_LANCE','MALE',[
  ('GYARADOS',44,['SURF','HYPER_BEAM','DRAGON_RAGE','RAIN_DANCE']),
  ('DRAGONITE',47,['HYPER_BEAM','THUNDER_WAVE','TWISTER','THUNDER']),
  ('DRAGONITE',47,['HYPER_BEAM','THUNDER_WAVE','TWISTER','BLIZZARD']),
  ('AERODACTYL',46,['ROCK_SLIDE','HYPER_BEAM','WING_ATTACK','ANCIENT_POWER']),
  ('CHARIZARD',46,['FLAMETHROWER','HYPER_BEAM','WING_ATTACK','SLASH']),
  ('DRAGONITE',50,['FIRE_BLAST','HYPER_BEAM','OUTRAGE','SAFEGUARD'])],885)]
DISPLAY={'SILVER_VICTORY_ROAD':'SILVER','LANCE_CHAMPION':'LANCE'}
WILD={
 'JohtoRoute27':(['PONYTA','DODUO','ARBOK','PONYTA','DODUO','SANDSLASH','DODRIO','SANDSLASH','ARBOK','DODRIO','SANDSLASH','DODRIO'],
  ['PONYTA','NOCTOWL','ARBOK','PONYTA','NOCTOWL','SANDSLASH','NOCTOWL','SANDSLASH','ARBOK','NOCTOWL','SANDSLASH','NOCTOWL'],[28,28,29,29,30,30,30,31,31,32,32,33]),
 'JohtoRoute26':(['PONYTA','DODRIO','QUAGSIRE','RATICATE','DODRIO','QUAGSIRE','SANDSLASH','RATICATE','DODRIO','QUAGSIRE','SANDSLASH','DODRIO'],
  ['PONYTA','NOCTOWL','QUAGSIRE','RATICATE','NOCTOWL','QUAGSIRE','SANDSLASH','RATICATE','NOCTOWL','QUAGSIRE','SANDSLASH','NOCTOWL'],[30,30,30,31,31,32,32,32,33,33,34,34]),
 'TohjoFalls':(['ZUBAT','ZUBAT','SLOWPOKE','GOLBAT','RATICATE','SLOWPOKE','GOLBAT','RATICATE','GOLBAT','RATICATE','GOLBAT','RATICATE'],
  ['ZUBAT','ZUBAT','SLOWPOKE','GOLBAT','RATICATE','SLOWPOKE','GOLBAT','RATICATE','GOLBAT','RATICATE','GOLBAT','RATICATE'],[24,25,24,26,27,26,28,28,29,29,30,30]),
 'JohtoVictoryRoad_1F':(['GRAVELER','GOLBAT','RHYHORN','GRAVELER','DONPHAN','RHYHORN','GOLBAT','DONPHAN','RHYHORN','DONPHAN','RHYDON','URSARING'],
  ['GRAVELER','GOLBAT','RHYHORN','GRAVELER','DONPHAN','RHYHORN','GOLBAT','DONPHAN','RHYHORN','DONPHAN','RHYDON','URSARING'],[32,32,33,33,34,34,35,35,36,36,37,37])}
WATER={'TohjoFalls':(['GOLDEEN','GOLDEEN','SEAKING','SEAKING','SLOWPOKE'],[20,25,25,30,30])}
def ident(n):return IDS[NEW.index(n)]
def warp(x,y,dst,index,elevation=3):
 return {'x':x,'y':y,'elevation':elevation,'dest_map':MID.get(dst,dst),'dest_warp_id':str(index)}
def obj(gfx,x,y,script,**kw):
 flag=kw.pop('flag','0');v=C.obj(gfx,x,y,script,**kw);v['flag']=flag
 if 'local_id' in v:assert re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',v['local_id'])
 return v


def johto_league_geometry(s):
 """New Johto challenge maps; original Kanto layout bytes are only read."""
 def land(w,h):
  a=[[0x3001]*w for _ in range(h)]
  for box in [(0,0,w,2),(0,0,2,h),(w-2,0,w,h),(0,h-2,w,h)]:C.fill(a,*box,C.dense)
  return a
 route27=land(44,26);C.fill(route27,0,18,12,22,0x3195);C.fill(route27,9,7,13,21,0x3195)
 C.fill(route27,11,7,37,11,0x3195);C.fill(route27,33,7,37,21,0x3195)
 C.fill(route27,25,14,35,20,C.grass)
 cliff=V.layout_array(s,'LAYOUT_ROUTE10')
 C.paste(route27,V.crop(cliff,6,17,5,3),31,3);C.fill(route27,32,6,36,8,0x3195)
 # Route27's cave entrance (33,5) leads through a real native Surf/Waterfall route.
 tohjo=[[0x0691]*26 for _ in range(22)];C.fill(tohjo,2,2,24,20,0x3281)
 C.fill(tohjo,4,6,22,17,0x133a)
 C.fill(tohjo,4,7,10,11,0x0691);C.fill(tohjo,12,7,22,11,0x0691)
 C.fill(tohjo,10,7,12,11,lambda x,y:0x131b if x%2==0 else 0x131c)
 ice=V.layout_array(s,'LAYOUT_FOUR_ISLAND_ICEFALL_CAVE_1F')
 tohjo[18][10]=ice[17][3];tohjo[3][10]=ice[6][3]
 route26=land(36,36);C.fill(route26,8,23,12,34,0x3195);C.fill(route26,8,21,28,25,0x3195)
 C.fill(route26,24,7,28,25,0x3195);C.fill(route26,13,9,24,15,C.grass)
 C.paste(route26,V.crop(cliff,6,17,5,3),23,3);C.fill(route26,24,6,28,8,0x3195)
 route26[32][10]=0x3179
 victory=[[0x0691]*32 for _ in range(28)];C.fill(victory,2,2,30,26,0x3281)
 # Silver blocks neither the return route nor the native north exit.
 victory[25][15]=ice[17][3];victory[3][15]=ice[6][3]
 plateau=V.layout_array(s,'LAYOUT_INDIGO_PLATEAU_EXTERIOR')
 C.fill(plateau,10,17,13,19,0x3195);plateau[18][11]=0x31ff
 # Keep the original Indigo facade, with this new southern exit path.
 pc=V.layout_array(s,'LAYOUT_POKEMON_CENTER_1F')
 lorelei=V.layout_array(s,'LAYOUT_POKEMON_LEAGUE_LORELEIS_ROOM')
 bruno=V.layout_array(s,'LAYOUT_POKEMON_LEAGUE_BRUNOS_ROOM')
 agatha=V.layout_array(s,'LAYOUT_POKEMON_LEAGUE_AGATHAS_ROOM')
 rooms=[]
 for source in [lorelei,agatha,bruno,agatha,lorelei]:
  a=[row[:] for row in source]
  # New challenge rooms use direct interaction; no inherited lighting/door scenes.
  C.fill(a,1,2,12,11,0x3290)
  a[11][6]=0x3013
  rooms.append(a)
 hof=V.layout_array(s,'LAYOUT_POKEMON_LEAGUE_HALL_OF_FAME')
 assert len(hof)==13 and len(hof[0])==11 and hof[12][5]==0x32b0,'native Hall-of-Fame layout preimage changed'
 hof[12][5]=0x3013  # Building primary MB_SOUTH_ARROW_WARP, collision0/elevation3.
 return {'JohtoRoute27':route27,'TohjoFalls':tohjo,'JohtoRoute26':route26,
  'JohtoVictoryRoad_1F':victory,'JohtoIndigoPlateau':plateau,
  'JohtoLeague_PokemonCenter_1F':pc,'JohtoLeague_WillsRoom':rooms[0],
  'JohtoLeague_KogasRoom':rooms[1],'JohtoLeague_BrunosRoom':rooms[2],
  'JohtoLeague_KarensRoom':rooms[3],'JohtoLeague_LancesRoom':rooms[4],
  'JohtoLeague_HallOfFame':hof}


def johto_league_story():
 """First Johto league challenge, explicit win callbacks and retained first-clear record.
 Prepared fragment only; map builder/HOF-context integration/native QA are separate.
 """
 scripts={};texts={}
 west='JohtoRoute27'
 scripts[west]=f'''{west}_MapScripts::
    .byte 0

{west}_LeagueWarden::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_BADGE08_GET, {west}_NotReady
    goto_if_unset FLAG_JOHTO_RADIO_TOWER_CLEARED, {west}_NotReady
    msgbox {west}_Text_Ready
    release
    end
{west}_NotReady::
    msgbox {west}_Text_NotReady
    release
    end
{west}_LeagueGate::
    lockall
    goto_if_unset FLAG_JOHTO_BADGE08_GET, {west}_GateClosed
    goto_if_unset FLAG_JOHTO_RADIO_TOWER_CLEARED, {west}_GateClosed
    setvar VAR_TEMP_0, 1
    releaseall
    end
{west}_GateClosed::
    msgbox {west}_Text_NotReady
    applymovement LOCALID_PLAYER, {west}_PushBack
    waitmovement 0
    releaseall
    end
{west}_PushBack::
    walk_left
    step_end
'''
 texts[west]={
 'Ready':["CLAIR recognized you, and the","ROCKET broadcast is silent.",
          "TOHJO FALLS leads toward the","JOHTO LEAGUE challenge."],
 'NotReady':["Earn all eight JOHTO BADGES and","stop the ROCKET broadcast first."]}
 silver='JohtoVictoryRoad_1F'
 scripts[silver]=f'''{silver}_MapScripts::
    .byte 0

{silver}_Silver::
    lock
    faceplayer
    goto_if_defeated TRAINER_JOHTO_SILVER_VICTORY_ROAD, {silver}_Silver_Victory
    trainerbattle_single TRAINER_JOHTO_SILVER_VICTORY_ROAD, {silver}_Text_SilverIntro, {silver}_Text_SilverLoss, {silver}_Silver_Victory, NO_MUSIC
    release
    end
{silver}_Silver_Victory::
    setflag FLAG_JOHTO_SILVER_LEAGUE_RESOLVED
    msgbox {silver}_Text_SilverAfter
    release
    end
{silver}_LeagueExit::
    lockall
    goto_if_unset FLAG_JOHTO_SILVER_LEAGUE_RESOLVED, {silver}_SilverWait
    warp MAP_JOHTO_INDIGO_PLATEAU, 1
    waitstate
    releaseall
    end
{silver}_SilverWait::
    msgbox {silver}_Text_SilverWaiting
    applymovement LOCALID_PLAYER, {silver}_PushBack
    waitmovement 0
    releaseall
    end
{silver}_PushBack::
    walk_down
    step_end
'''
 texts[silver]={
 'SilverIntro':["I used to think power meant","taking whatever I wanted.",
                "You and LANCE stopped ROCKET.","My partners stayed beside me.",
                "GOLBAT became CROBAT when I","finally learned to trust it.",
                "Now face the team we built","together!"],
 'SilverLoss':["So this is your real strength..."],
 'SilverAfter':["Stealing never made me stronger.","My partners did.",
                "I will make amends with ELM.","Go on. LANCE is waiting."],
 'SilverWaiting':["SILVER is waiting at the end of","the road. Settle your rivalry."]}
 pc='JohtoLeague_PokemonCenter_1F'
 scripts[pc]=f'''{pc}_MapScripts::
    .byte 0

{pc}_Nurse::
    lock
    faceplayer
    call EventScript_PkmnCenterNurse
    release
    end
{pc}_Receptionist::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_BADGE08_GET, {pc}_NotReady
    goto_if_unset FLAG_JOHTO_RADIO_TOWER_CLEARED, {pc}_NotReady
    goto_if_unset FLAG_JOHTO_SILVER_LEAGUE_RESOLVED, {pc}_NotReady
    msgbox {pc}_Text_Challenge, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, {pc}_Later
    cleartrainerflag TRAINER_JOHTO_WILL
    cleartrainerflag TRAINER_JOHTO_KOGA
    cleartrainerflag TRAINER_JOHTO_BRUNO
    cleartrainerflag TRAINER_JOHTO_KAREN
    cleartrainerflag TRAINER_JOHTO_LANCE_CHAMPION
    clearflag FLAG_JOHTO_WILL_CLEARED
    clearflag FLAG_JOHTO_KOGA_CLEARED
    clearflag FLAG_JOHTO_BRUNO_CLEARED
    clearflag FLAG_JOHTO_KAREN_CLEARED
    clearflag FLAG_JOHTO_LANCE_CHAMPION_CLEARED
    closemessage
    warp MAP_JOHTO_LEAGUE_WILLS_ROOM, 0
    waitstate
    release
    end
{pc}_NotReady::
    msgbox {pc}_Text_NotReady
    release
    end
{pc}_Later::
    msgbox {pc}_Text_Later
    release
    end
'''
 texts[pc]={
 'Challenge':["This is the JOHTO LEAGUE.","Begin a new challenge?",
              "Once inside, face all four ELITE","trainers before Champion LANCE."],
 'NotReady':["Eight JOHTO BADGES, quiet radio,","and your rival's respect.",
             "Complete that journey before","entering the challenge."],
 'Later':["Prepare your partners carefully.","We will be waiting."]}
 rooms=[
  ('JohtoLeague_WillsRoom','WILL','WILL','MAP_JOHTO_LEAGUE_KOGAS_ROOM',None),
  ('JohtoLeague_KogasRoom','KOGA','KOGA','MAP_JOHTO_LEAGUE_BRUNOS_ROOM','WILL'),
  ('JohtoLeague_BrunosRoom','BRUNO','BRUNO','MAP_JOHTO_LEAGUE_KARENS_ROOM','KOGA'),
  ('JohtoLeague_KarensRoom','KAREN','KAREN','MAP_JOHTO_LEAGUE_LANCES_ROOM','BRUNO'),
  ('JohtoLeague_LancesRoom','LANCE_CHAMPION','LANCE_CHAMPION','MAP_JOHTO_LEAGUE_HALL_OF_FAME','KAREN')]
 for name,trainer,flag,dest,prior in rooms:
  prior_check='' if prior is None else f'    goto_if_unset FLAG_JOHTO_{prior}_CLEARED, {name}_PriorNotReady\n'
  champion=''
  scripts[name]=f'''{name}_MapScripts::
    .byte 0

{name}_Leader::
    lock
    faceplayer
{prior_check}    goto_if_defeated TRAINER_JOHTO_{trainer}, {name}_Victory
    trainerbattle_single TRAINER_JOHTO_{trainer}, {name}_Text_Intro, {name}_Text_Loss, {name}_Victory, NO_MUSIC
    release
    end
{name}_Victory::
    setflag FLAG_JOHTO_{flag}_CLEARED
{champion}    msgbox {name}_Text_After
    release
    end
{name}_NextRoom::
    lockall
    goto_if_unset FLAG_JOHTO_{flag}_CLEARED, {name}_GateClosed
    warp {dest}, 0
    waitstate
    releaseall
    end
{name}_GateClosed::
    msgbox {name}_Text_GateClosed
    applymovement LOCALID_PLAYER, {name}_PushBack
    waitmovement 0
    releaseall
    end
{name}_PriorNotReady::
    msgbox {name}_Text_PriorNotReady
    release
    end
{name}_PushBack::
    walk_down
    step_end
'''
  intros={
   'WILL':["I am WILL. My journey taught me","to see beyond appearances.",
           "Show me what your travels","through JOHTO have taught you!"],
   'KOGA':["My daughter guards FUCHSIA now.","Here, I face JOHTO challengers.",
           "Discipline and poison!","Let the battle begin!"],
   'BRUNO':["KANTO was the beginning of your","journey. JOHTO tested your bond.",
            "My partners and I trained","together. Show us your strength!"],
   'KAREN':["Strong POKeMON. Weak POKeMON.","Those are easy labels.",
            "A great TRAINER wins with the","partners they believe in."],
   'LANCE_CHAMPION':["We stood together at the lake","and stopped ROCKET's machine.",
                     "KANTO and JOHTO share a league","tradition, but this is your",
                     "JOHTO challenge. Face me with","all your partners learned!"]}
  after={
   'WILL':["Your vision is clear. Continue","to KOGA's chamber."],
   'KOGA':["Your bond survived every trick.","BRUNO waits beyond the door."],
   'BRUNO':["Our strength met your courage.","Now face KAREN."],
   'KAREN':["You trusted your partners.","LANCE will recognize that."],
   'LANCE_CHAMPION':["You are the JOHTO Champion!","Our investigation is complete.",
                     "Come record the partners who","carried you on this journey."]}
  texts[name]={'Intro':intros[trainer],'Loss':["Your partners fought as one..."],
               'After':after[trainer],'GateClosed':["Win this challenge before","entering the next chamber."],
               'PriorNotReady':["Finish the previous ELITE","challenge before facing me."]}

 n='JohtoLeague_HallOfFame'
 scripts[n]=f'''{n}_MapScripts::
    .byte 0

{n}_Record::
    lock
    faceplayer
    goto_if_unset FLAG_SYS_GAME_CLEAR, {n}_NotReady
    goto_if_unset FLAG_JOHTO_LANCE_CHAMPION_CLEARED, {n}_NotReady
    goto_if_unset FLAG_JOHTO_WILL_CLEARED, {n}_NotReady
    goto_if_unset FLAG_JOHTO_KOGA_CLEARED, {n}_NotReady
    goto_if_unset FLAG_JOHTO_BRUNO_CLEARED, {n}_NotReady
    goto_if_unset FLAG_JOHTO_KAREN_CLEARED, {n}_NotReady
    msgbox {n}_Text_Record, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, {n}_Later
    closemessage
    dofieldeffect FLDEFF_HALL_OF_FAME_RECORD
    waitfieldeffect FLDEFF_HALL_OF_FAME_RECORD
    delay 40
    setflag FLAG_JOHTO_LEAGUE_CLEARED
    fadescreenspeed FADE_TO_BLACK, 24
    special EnterHallOfFame
    waitstate
    release
    end
{n}_NotReady::
    msgbox {n}_Text_NotReady
    release
    end
{n}_Later::
    msgbox {n}_Text_Later
    release
    end
'''
 texts[n]={'Record':["You are JOHTO's new Champion.","Record your partners now?"],
  'NotReady':["Finish the KANTO and JOHTO","league challenges first."],
  'Later':["Return when you are ready.","Your partners earned this honor."]}
 n='JohtoIndigoPlateau'
 scripts[n]=f'''{n}_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, {n}_OnTransition
    .byte 0
{n}_OnTransition::
    setflag FLAG_JOHTO_LEAGUE_ARRIVED
    end
{n}_Official::
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_LEAGUE_CLEARED, {n}_Champion
    msgbox {n}_Text_Challenge
    release
    end
{n}_Champion::
    msgbox {n}_Text_Champion
    release
    end
'''
 texts[n]={'Challenge':["Welcome to the JOHTO circuit.","Your partners carried you far."],
  'Champion':["JOHTO has a new Champion!","Both regions honor your journey."]}
 scripts['JohtoLeague_PokemonCenter_1F']=scripts['JohtoLeague_PokemonCenter_1F'].replace(
 '    .byte 0\n','    map_script MAP_SCRIPT_ON_TRANSITION, JohtoLeague_PokemonCenter_1F_OnTransition\n    .byte 0\n\nJohtoLeague_PokemonCenter_1F_OnTransition::\n    setrespawn HEAL_LOCATION_JOHTO_INDIGO_PLATEAU\n    end\n',1)
 for name,key in [('JohtoRoute27','LeagueWarden'),('JohtoRoute27','LeagueGate'),('JohtoLeague_PokemonCenter_1F','Receptionist')]:
  anchor=name+'_'+key+'::\n    lock'+('all' if key=='LeagueGate' else '')+'\n'
  if key!='LeagueGate':anchor+='    faceplayer\n'
  target=name+('_GateClosed' if key=='LeagueGate' else '_NotReady')
  assert scripts[name].count(anchor)==1
  scripts[name]=scripts[name].replace(anchor,anchor+'    goto_if_unset FLAG_SYS_GAME_CLEAR, '+target+'\n',1)
  if key in ('LeagueGate','Receptionist'):
   badge_guards=''.join('    goto_if_unset FLAG_BADGE%02d_GET, '%i+target+'\n' for i in range(1,9))
   scripts[name]=scripts[name].replace(anchor,anchor+badge_guards,1)
 hof_name='JohtoLeague_HallOfFame'
 hof_anchor='    goto_if_unset FLAG_SYS_GAME_CLEAR, '+hof_name+'_NotReady\n'
 assert scripts[hof_name].count(hof_anchor)==1
 scripts[hof_name]=scripts[hof_name].replace(hof_anchor,hof_anchor+''.join(
  '    goto_if_unset FLAG_BADGE%02d_GET, '%i+hof_name+'_NotReady\n' for i in range(1,9)),1)

 texts={name:{key:['\n'.join(lines[i:i+2]) for i in range(0,len(lines),2)] for key,lines in rows.items()} for name,rows in texts.items()}
 return scripts,texts


def connect_new_bark_coast(s,out):
 """Only eight previously blocked coastal cells become the League surf corridor."""
 p='data/maps/NewBarkTown/map.json';j=s.json(p)
 con={'map':MID['JohtoRoute27'],'direction':'right','offset':0}
 connections=j.get('connections') or []
 rights=[v for v in connections if v['direction']=='right']
 assert not rights or rights==[con],('existing New Bark east route',rights)
 if con not in connections:connections.append(con)
 j['connections']=connections;j.pop('connections_no_include',None);out[p]=enc(j)
 layouts=[v for v in s.json('data/layouts/layouts.json')['layouts'] if v.get('id')==j['layout']]
 assert len(layouts)==1
 layout=layouts[0];assert (layout['width'],layout['height'])==(36,28)
 assert layout['primary_tileset']=='gTileset_General' and layout['secondary_tileset']=='gTileset_PalletTown'
 p=layout['blockdata_filepath'];old=s.read(p);a=V.layout_array(s,j['layout'])
 stock=[0x3001,0x3001,0x34f4,0x152b,0x152b,0x152b]
 changed=[0x3001,0x3001,0x3115,0x112c,0x01d9,0x01d9]
 for y in range(18,24):
  want=(stock,changed) if y in (20,21) else (stock,)
  assert a[y][30:36] in want,('New Bark owned coastal guard',y,a[y][30:36])
 before=copy.deepcopy(a)
 for y in (20,21):a[y][32:36]=changed[2:]
 actual={(x,y) for y in range(28) for x in range(36) if before[y][x]!=a[y][x]}
 allowed={(x,y) for y in (20,21) for x in range(32,36)}
 assert actual<=allowed and len(old)==36*28*2,'coast modification exceeded eight cells'
 out[p]=C.pack(a)
 # A re-run of the old entry generator must never silently erase this new route.
 p='tools/johto/build_blackthorn.py';t=out.get(p,s.read(p)).decode()
 assert '# JOHTO_LEAGUE_EXTENSION_GUARD' in t or 'gMapGroup_JohtoEntry' in t


def build(s):
 out={};stats={'chapter':'Johto independent Indigo challenge','save_layout_changed':False,
  'native_build_and_emulator':'NOT_RUN_BY_GENERATOR','visual_limits':['Reused native Kanto tiles and class portraits.'],
  'not_implemented':['Optional Route45/46 loop','Whirl Islands and Bell Tower side quests']}
 groups=s.json('data/maps/map_groups.json');assert groups['gMapGroup_JohtoEntry'] in (OLD,OLD+NEW)
 assert len(OLD+NEW)<=128 and len(groups['group_order'])<=128,'native signed WarpData capacity exceeded'
 for k,v in groups.items():
  if k not in ('group_order','gMapGroup_JohtoEntry'):assert not(set(v)&set(NEW))
 groups['gMapGroup_JohtoEntry']=OLD+NEW;out['data/maps/map_groups.json']=enc(groups)
 arrays=johto_league_geometry(s);ls=s.json('data/layouts/layouts.json')
 templates={'JohtoRoute27':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),
  'JohtoRoute26':('General','ViridianCity','LAYOUT_VIRIDIAN_CITY'),
  'TohjoFalls':('General','SeafoamIslands','LAYOUT_FOUR_ISLAND_ICEFALL_CAVE_1F'),
  'JohtoVictoryRoad_1F':('General','SeafoamIslands','LAYOUT_FOUR_ISLAND_ICEFALL_CAVE_1F'),
  'JohtoIndigoPlateau':('General','IndigoPlateau','LAYOUT_INDIGO_PLATEAU_EXTERIOR'),
  'JohtoLeague_PokemonCenter_1F':('Building','PokemonCenter','LAYOUT_POKEMON_CENTER_1F'),
  'JohtoLeague_HallOfFame':('Building','HallOfFame','LAYOUT_POKEMON_LEAGUE_HALL_OF_FAME')}
 for n in ['JohtoLeague_WillsRoom','JohtoLeague_KogasRoom','JohtoLeague_BrunosRoom','JohtoLeague_KarensRoom','JohtoLeague_LancesRoom']:
  templates[n]=('Building','PokemonLeague','LAYOUT_POKEMON_LEAGUE_LORELEIS_ROOM')
 for n,a in arrays.items():
  primary,secondary,old=templates[n];hits=[v for v in ls['layouts'] if v.get('id')==old];assert len(hits)==1
  t=hits[0];row={'id':'LAYOUT_'+ident(n),'name':n+'_Layout','width':len(a[0]),'height':len(a),
   'border_width':2,'border_height':2,'primary_tileset':'gTileset_'+primary,'secondary_tileset':'gTileset_'+secondary,
   'blockdata_filepath':'data/layouts/'+n+'/map.bin','border_filepath':'data/layouts/'+n+'/border.bin'}
  hits=[v for v in ls['layouts'] if v.get('id')==row['id']];assert not hits or hits==[row]
  if not hits:ls['layouts'].append(row)
  out[row['blockdata_filepath']]=C.pack(a);out[row['border_filepath']]=s.read(t['border_filepath'])
 out['data/layouts/layouts.json']=enc(ls);maps={};scripts,rows=johto_league_story();tx={n:C.texts(n,d) for n,d in rows.items()}
 def temp(n,old,section,music=None):
  j=s.json('data/maps/'+old+'/map.json');j.update(id=MID[n],name=n,layout='LAYOUT_'+ident(n),region_map_section=section,connections=None)
  j.pop('connections_no_include',None)
  if music:j['music']=music
  for key in ['object_events','warp_events','coord_events','bg_events']:j[key]=[]
  maps[n]=j;return j
 def coord(x,y,script):
  return {'type':'trigger','x':x,'y':y,'elevation':0,'var':'VAR_TEMP_0','var_value':'0','script':script}
 n='JohtoRoute27';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE27','MUS_ROUTE1')
 j['connections']=[{'map':'MAP_NEW_BARK_TOWN','direction':'left','offset':0}]
 j['warp_events']=[warp(33,5,'TohjoFalls',0,0)]
 j['object_events']=[obj('POLICEMAN',8,17,n+'_LeagueWarden')]
 j['coord_events']=[coord(1,y,n+'_LeagueGate') for y in range(18,22)]
 n='TohjoFalls';j=temp(n,'FourIsland_IcefallCave_1F','MAPSEC_TOHJO_FALLS','MUS_MT_MOON')
 j['requires_flash']=False;j['map_type']='MAP_TYPE_UNDERGROUND'
 j['warp_events']=[warp(10,18,'JohtoRoute27',0,0),warp(10,3,'JohtoRoute26',0)]
 n='JohtoRoute26';j=temp(n,'Route1','MAPSEC_JOHTO_ROUTE26','MUS_ROUTE1')
 j['warp_events']=[warp(10,32,'TohjoFalls',1),warp(25,5,'JohtoVictoryRoad_1F',0,0)]
 n='JohtoVictoryRoad_1F';j=temp(n,'FourIsland_IcefallCave_1F','MAPSEC_JOHTO_VICTORY_ROAD','MUS_VICTORY_ROAD')
 j['requires_flash']=False;j['map_type']='MAP_TYPE_UNDERGROUND'
 j['warp_events']=[warp(15,25,'JohtoRoute26',1,0),warp(15,3,'JohtoIndigoPlateau',1)]
 j['object_events']=[obj('BLUE',16,7,n+'_Silver')]
 j['coord_events']=[coord(15,3,n+'_LeagueExit')]
 n='JohtoIndigoPlateau';j=temp(n,'IndigoPlateau_Exterior','MAPSEC_JOHTO_INDIGO_PLATEAU','MUS_VICTORY_ROAD')
 j['warp_events']=[warp(11,6,'JohtoLeague_PokemonCenter_1F',1,0),warp(11,18,'JohtoVictoryRoad_1F',1)]
 j['object_events']=[obj('GENTLEMAN',9,9,n+'_Official')]
 n='JohtoLeague_PokemonCenter_1F';j=temp(n,'SaffronCity_PokemonCenter_1F','MAPSEC_JOHTO_INDIGO_PLATEAU','MUS_POKE_CENTER')
 j['warp_events']=[warp(x,8,'JohtoIndigoPlateau',0) for x in [6,7,8]]
 j['object_events']=[obj('NURSE',7,2,n+'_Nurse',local_id='LOCALID_JOHTO_LEAGUE_NURSE'),
  obj('GENTLEMAN',4,6,n+'_Receptionist')]
 # Keep the native PC terminal and its correct shared dialogue.
 original=s.json('data/maps/SaffronCity_PokemonCenter_1F/map.json')
 j['bg_events']=copy.deepcopy(original.get('bg_events',[]))
 for n,trainer in [('JohtoLeague_WillsRoom','WILL'),('JohtoLeague_KogasRoom','KOGA'),
  ('JohtoLeague_BrunosRoom','BRUNO'),('JohtoLeague_KarensRoom','KAREN'),('JohtoLeague_LancesRoom','LANCE_CHAMPION')]:
  j=temp(n,'PokemonLeague_LoreleisRoom','MAPSEC_JOHTO_INDIGO_PLATEAU','MUS_GYM')
  j['warp_events']=[warp(6,11,'JohtoLeague_PokemonCenter_1F',1)]
  gfx={'WILL':'MAN','KOGA':'KOGA','BRUNO':'BRUNO','KAREN':'COOLTRAINER_F','LANCE_CHAMPION':'LANCE'}[trainer]
  j['object_events']=[obj(gfx,6,5,n+'_Leader')]
  j['coord_events']=[coord(6,2,n+'_NextRoom')]
 n='JohtoLeague_HallOfFame';j=temp(n,'PokemonLeague_HallOfFame','MAPSEC_JOHTO_INDIGO_PLATEAU','MUS_SLOW_PALLET')
 j['warp_events']=[warp(5,12,'JohtoLeague_LancesRoom',0)]
 j['object_events']=[obj('LANCE',6,4,n+'_Record')]
 for n,j in maps.items():
  out['data/maps/'+n+'/map.json']=enc(j)
  out['data/maps/'+n+'/scripts.inc']=scripts.get(n,n+'_MapScripts::\n    .byte 0\n').encode()
  out['data/maps/'+n+'/text.inc']=tx.get(n,'@ Native shared dialogue.\n').encode()
 # Remove only the inactive stair graphic from this NEW plain league center.
 pc=arrays['JohtoLeague_PokemonCenter_1F'];pc[6][1]=0x3281
 out['data/layouts/JohtoLeague_PokemonCenter_1F/map.bin']=C.pack(pc)
 connect_new_bark_coast(s,out)
 heals=s.json('src/data/heal_locations.json')
 row={'id':'HEAL_LOCATION_JOHTO_INDIGO_PLATEAU','map':MID['JohtoIndigoPlateau'],'x':11,'y':7,
  'respawn_map':MID['JohtoLeague_PokemonCenter_1F'],'respawn_npc':'LOCALID_JOHTO_LEAGUE_NURSE'}
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
 else:assert not additions,('incomplete Johto league flags',additions)
 out[p]=t.encode()
 p='include/constants/opponents_johto_league.h'
 h='#ifndef GUARD_OPPONENTS_JOHTO_LEAGUE_H\n#define GUARD_OPPONENTS_JOHTO_LEAGUE_H\n'
 for n,c,pic,gender,party,num in TRAINERS:h+='#define TRAINER_JOHTO_'+n+' (HOENN_TRAINERS_START + '+str(num)+')\n'
 out[p]=(h+'#endif\n').encode()
 for path in (s.root/'include/constants').glob('opponents*.h'):
  rel=path.relative_to(s.root).as_posix()
  if rel==p:continue
  used={int(v,0) for v in re.findall(r'HOENN_TRAINERS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)',s.text(rel))}
  assert not(used&{v[-1] for v in TRAINERS}),('trainer collision',rel)
 p='include/constants/opponents.h';anchor='#include "constants/opponents_johto_blackthorn.h"'
 out[p]=C.once(s.text(p),anchor,anchor+'\n#include "constants/opponents_johto_league.h"','Johto league trainer include').encode()
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
 out['src/data/trainer_parties_johto_league.h']=parties.encode();out['src/data/trainers_johto_league.h']=trainers.encode()
 for p,a,inc in [('src/data/trainers.h','#include "trainers_johto_blackthorn.h"','#include "trainers_johto_league.h"'),('src/data/trainer_parties.h','#include "trainer_parties_johto_blackthorn.h"','#include "trainer_parties_johto_league.h"')]:
  out[p]=C.once(s.text(p),a,a+'\n'+inc,'Johto league trainer data').encode()
 p='data/event_scripts.s';t=s.text(p);block='@ '+MARK+'\n'+''.join('    .include "data/maps/'+n+'/'+f+'"\n' for n in NEW for f in ['scripts.inc','text.inc'])
 if MARK not in t:assert not any('data/maps/'+n+'/' in t for n in NEW);t=t.rstrip()+'\n\n'+block
 else:assert block in t
 out[p]=t.encode()

 p='tools/johto/build_blackthorn.py';t=s.text(p)
 guard=' # JOHTO_LEAGUE_EXTENSION_GUARD\n if any(n not in OLD + NEW for n in s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]):\n  raise RuntimeError("Johto League extension exists; use build_johto_league.py")\n'
 if '# JOHTO_LEAGUE_EXTENSION_GUARD' not in t:
  t,n=re.subn(r'(?m)^def build\(s\):\n',lambda m:m.group(0)+guard,t);assert n==1
 else:assert guard in t
 out[p]=t.encode()
 # Select Johto only from its own actual champion/Hall-of-Fame context.
 # Existing Kanto and Hoenn Hall-of-Fame behavior remains the default branch.
 p='include/hall_of_fame.h';t=s.text(p)
 anchor='void CB2_DoHallOfFameScreen(void);'
 declaration='bool8 IsJohtoHallOfFameContext(void);'
 if declaration not in t:t=C.once(t,anchor,anchor+'\n'+declaration,'Johto HOF context declaration')
 out[p]=t.encode()
 p='src/hall_of_fame.c';t=s.text(p)
 for inc in ['#include "event_data.h"','#include "constants/maps.h"','#include "constants/flags.h"']:
  if inc not in t:t=C.once(t,'#include "hall_of_fame.h"','#include "hall_of_fame.h"\n'+inc,'Johto HOF include '+inc)
 context='''// JOHTO_HOF_ACTUAL_CHAMPION_CONTEXT_V1
bool8 IsJohtoHallOfFameContext(void)
{
    return gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_JOHTO_LEAGUE_HALL_OF_FAME)
        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_JOHTO_LEAGUE_HALL_OF_FAME)
        && FlagGet(FLAG_JOHTO_LANCE_CHAMPION_CLEARED)
        && FlagGet(FLAG_JOHTO_LEAGUE_CLEARED);
}

'''
 if '// JOHTO_HOF_ACTUAL_CHAMPION_CONTEXT_V1' not in t:
  t=C.once(t,'static void SetWarpsToRollCredits(void)\n{',context+'static void SetWarpsToRollCredits(void)\n{','Johto HOF actual map context')
 else:assert context in t
 anchor='static void SetWarpsToRollCredits(void)\n{\n'
 gate='''    // JOHTO_HOF_CREDITS_DISPATCH_V1
    if (IsJohtoHallOfFameContext())
    {
        DoJohtoCredits();
        return;
    }

'''
 if '// JOHTO_HOF_CREDITS_DISPATCH_V1' not in t:t=C.once(t,anchor,anchor+gate,'Johto actual HOF credits selection')
 else:assert gate in t
 assert 'DoJohtoCredits' in s.text('include/credits.h'),'native Johto credits review must be staged before league dispatch'
 out[p]=t.encode()
 p='src/post_battle_event_funcs.c';t=s.text(p)
 anchor='    else\n        SetContinueGameWarpToHealLocation(HEAL_LOCATION_PALLET_TOWN);'
 gate='''    else if (IsJohtoHallOfFameContext())
        SetContinueGameWarpToHealLocation(HEAL_LOCATION_JOHTO_INDIGO_PLATEAU);
    else
        SetContinueGameWarpToHealLocation(HEAL_LOCATION_PALLET_TOWN); // JOHTO_HOF_CONTINUE_DESTINATION_V1'''
 if '// JOHTO_HOF_CONTINUE_DESTINATION_V1' not in t:t=C.once(t,anchor,gate,'Johto HOF continue destination')
 else:assert gate in t
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
 p='src/data/region_map/region_map_sections.json';j=s.json(p);original=j['map_sections'][:]
 specs=[('JOHTO_ROUTE27','ROUTE 27',16,8,4,1),('TOHJO_FALLS','TOHJO FALLS',20,8,1,1),
  ('JOHTO_ROUTE26','ROUTE 26',21,6,1,3),('JOHTO_VICTORY_ROAD','VICTORY ROAD',21,5,1,1),
  ('JOHTO_INDIGO_PLATEAU','JOHTO LEAGUE',21,4,1,1)]
 for key,label,x,y,w,h in specs:
  row={'id':'MAPSEC_'+key,'name':label,'x':x,'y':y,'width':w,'height':h}
  hits=[v for v in j['map_sections'] if v.get('id')==row['id']];assert not hits or hits==[row]
  if not hits:j['map_sections'].append(row)
 assert [v.get('id') for v in j['map_sections'][:len(original)]]==[v.get('id') for v in original]
 assert len(j['map_sections'])<256,'native u8 mapsection limit'
 out[p]=enc(j)
 for p in ['src/region_map.c','src/pokemon_summary_screen.c']:
  t=s.text(p);pat=r'(MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP[\s\S]{0,140}?<=\s*)MAPSEC_DRAGON_DEN'
  if re.search(pat,t):t,n=re.subn(pat,lambda m:m.group(1)+'MAPSEC_JOHTO_INDIGO_PLATEAU',t);assert n==1
  else:assert re.search(pat.replace('MAPSEC_DRAGON_DEN','MAPSEC_JOHTO_INDIGO_PLATEAU'),t)
  out[p]=t.encode()
 p='src/region_map.c';t=out[p].decode()
 if '// JOHTO_LEAGUE_MAP_GRID_V1' not in t:
  pat=r'(?m)^([ \t]*)// BLACKTHORN_MAP_GRID_V1'
  lines=['// JOHTO_LEAGUE_MAP_GRID_V1','if (layer != LAYER_MAP)','    return MAPSEC_NONE;',
   'if (x >= 16 && x <= 19 && y == 8)','    return MAPSEC_JOHTO_ROUTE27;',
   'if (x == 20 && y == 8)','    return MAPSEC_TOHJO_FALLS;',
   'if (x == 21 && y >= 6 && y <= 8)','    return MAPSEC_JOHTO_ROUTE26;',
   'if (x == 21 && y == 5)','    return MAPSEC_JOHTO_VICTORY_ROAD;',
   'if (x == 21 && y == 4)','    return MAPSEC_JOHTO_INDIGO_PLATEAU;','// BLACKTHORN_MAP_GRID_V1']
  t,n=re.subn(pat,lambda m:'\n'.join(m.group(1)+v for v in lines),t);assert n==1
 block='''// JOHTO_LEAGUE_FLY_DESTINATION_V1
static const struct JohtoFlyDestination sJohtoLeagueFlyDestination = {
    MAPSEC_JOHTO_INDIGO_PLATEAU, FLAG_JOHTO_LEAGUE_ARRIVED,
    FLAG_JOHTO_LEAGUE_CLEARED, {MAP(MAP_JOHTO_INDIGO_PLATEAU), HEAL_LOCATION_JOHTO_INDIGO_PLATEAU}, 11, 7
};

'''
 anchor='static const struct JohtoFlyDestination *GetJohtoFlyDestination(u16 mapsec)'
 if '// JOHTO_LEAGUE_FLY_DESTINATION_V1' not in t:t=C.once(t,anchor,block+anchor,'Johto League Fly destination')
 else:assert block in t
 anchor='''    if (mapsec == MAPSEC_BLACKTHORN_CITY)
        return &sBlackthornFlyDestination;
'''
 t=C.once(t,anchor,anchor+'''    if (mapsec == MAPSEC_JOHTO_INDIGO_PLATEAU)
        return &sJohtoLeagueFlyDestination;
''','Johto League Fly lookup')
 out[p]=t.encode()
 p='graphics/region_map/johto_entry.bin';a=list(struct.unpack('<600H',s.read(p)))
 for _,_,x,y,w,h in specs:
  for ry in range(y,y+h):
   for rx in range(x,x+w):a[ry*30+rx]=0x312
 out[p]=struct.pack('<600H',*a)
 areas=[('Route27','johtoRoute27',['MAP_JOHTO_ROUTE27']),
  ('Tohjo','johtoTohjoFalls',['MAP_TOHJO_FALLS']),('Route26','johtoRoute26',['MAP_JOHTO_ROUTE26']),
  ('Victory','johtoVictoryRoad',['MAP_JOHTO_VICTORY_ROAD_1F'])]
 p='src/wild_pokemon_area.c';t=s.text(p)
 if 'bool8 johtoRoute27;' not in t:
  t,n=re.subn(r'(bool8\s+johtoDragonDen\s*;)',lambda m:m.group(1)+''.join('\n    bool8 '+f+';' for _,f,_ in areas),t);assert n==1
 if 'MAP_GROUP(MAP_JOHTO_ROUTE27)' not in t:
  pat=r'(?s)(if\s*\(header->mapGroup\s*==\s*MAP_GROUP\(MAP_DRAGON_DEN_1F\)\s*&&\s*header->mapNum\s*==\s*MAP_NUM\(MAP_DRAGON_DEN_1F\)\s*\)\s*\{\s*habitats->johtoDragonDen\s*=\s*TRUE;\s*continue;\s*\})'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n            '+m.group(1).replace('MAP_DRAGON_DEN_1F',mn).replace('johtoDragonDen',f) for _,f,maps in areas for mn in maps),t);assert n==1
 if 'habitats.johtoRoute27 || habitats.johtoTohjoFalls' not in t:
  t,n=re.subn(r'(if\s*\([^\n]*habitats\.johtoRoute29[^\n]*habitats\.johtoDragonDen)\)',lambda m:m.group(1)+' || '+' || '.join('habitats.'+f for _,f,_ in areas)+')',t);assert n==1
 if 'GetJohtoRoute27AreaMarkerSubsprite(areaCount++, subsprites);' not in t:
  pat=r'(if\s*\(habitats\.johtoDragonDen\)\s*GetJohtoDragonDenAreaMarkerSubsprite\(areaCount\+\+,\s*subsprites\);)'
  t,n=re.subn(pat,lambda m:m.group(1)+''.join('\n        if (habitats.'+f+')\n            GetJohto'+key+'AreaMarkerSubsprite(areaCount++, subsprites);' for key,f,_ in areas),t);assert n==1
 out[p]=t.encode()
 p='include/pokedex_area_markers.h';t=s.text(p)
 if 'GetJohtoRoute27AreaMarkerSubsprite' not in t:
  t,n=re.subn(r'(void GetJohtoDragonDenAreaMarkerSubsprite\([^;]*;)',lambda m:m.group(1)+''.join('\nvoid GetJohto'+key+'AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);' for key,_,_ in areas),t);assert n==1
 out[p]=t.encode()
 p='src/pokedex_area_markers.c';t=s.text(p)
 for key,shape,x,y in [('Route27','SmallHorizontal',90,47),('Tohjo','Circular',107,47),('Route26','SmallVertical',112,37),('Victory','Circular',112,29)]:
  name='GetJohto'+key+'AreaMarkerSubsprite'
  body='void '+name+'(s32 i, struct Subsprite *subsprites)\n{\n    if (subsprites == NULL)\n        return;\n    subsprites[i] = sSubsprite_'+shape+';\n    subsprites[i].x = '+str(x)+' + (HOENN_AREA_MAP_LEFT * 8 - 104);\n    subsprites[i].y = '+str(y)+';\n}'
  if re.search(r'void\s+'+name+r'\(',t):t=C.replace_function(t,name,body,'Johto League habitat marker')
  else:t=t.rstrip()+'\n\n'+body+'\n'
 out[p]=t.encode()
 p='src/pokedex_screen.c';t=s.text(p)
 labels=[('R27','27'),('Tohjo','TOHJO'),('R26','26'),('Road','ROAD'),('League','LEAG')]
 if 'sText_JohtoLeague[]' not in t:
  anchor='static const u8 sText_JohtoR44[] = _("44");\n'
  t=C.once(t,anchor,anchor+''.join('static const u8 sText_Johto'+k+'[] = _("'+v+'");\n' for k,v in labels),'Johto League map labels')
 name='DexScreen_DrawJohtoEntryArea';m=re.search(r'static void '+name+r'\([^{}]*\)\s*\{',t);assert m
 start=m.start();depth=1;i=m.end()
 while depth:
  depth+=(t[i]=='{')-(t[i]=='}');i+=1
 old=t[start:i]
 if '// JOHTO_LEAGUE_DEX_DIAGRAM_V1' not in old:
  assert 'DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoR44,' in old
  additions='    // JOHTO_LEAGUE_DEX_DIAGRAM_V1\n'
  for _,_,x,y,w,h in specs:
   x,y,w,h=x*5+9,y*6+1,max(4,(w-1)*5+4),max(4,(h-1)*6+4)
   assert 0<=x and x+w<=122 and 0<=y and y+h<=68
   additions+='    FillWindowPixelRect(windowId, PIXEL_FILL(3), '+', '.join(map(str,[x,y,w,h]))+');\n'
   additions+='    FillWindowPixelRect(windowId, PIXEL_FILL(5), '+', '.join(map(str,[x+1,y+1,max(1,w-2),max(1,h-2)]))+');\n'
  for key,x,y in [('R27',83,53),('Tohjo',96,53),('R26',107,40),('Road',102,34),('League',101,27)]:
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
 starts={'JohtoRoute27':(0,20),'TohjoFalls':(10,17),'JohtoRoute26':(10,31),
  'JohtoVictoryRoad_1F':(15,24),'JohtoIndigoPlateau':(11,7),
  'JohtoLeague_PokemonCenter_1F':(7,7),'JohtoLeague_HallOfFame':(5,11)}
 for n in ['JohtoLeague_WillsRoom','JohtoLeague_KogasRoom','JohtoLeague_BrunosRoom','JohtoLeague_KarensRoom','JohtoLeague_LancesRoom']:starts[n]=(6,10)
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
    allowed=[]
    matches=[final.json('data/maps/'+name+'/map.json') for name in allowed if final.json('data/maps/'+name+'/map.json')['id']==wp['dest_map']]
    assert len(matches)==1,(n,'unknown preserved destination',wp);dst=matches[0]
   else:dst=maps[dst_name]
   assert 0<=int(wp['dest_warp_id'])<len(dst['warp_events']),(n,'invalid destination warp ID',wp);checked+=1
  inherited_objects=[];inherited_portals=[]
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
   loc=(wp['x'],wp['y']+1) if (n in ('JohtoRoute27','JohtoRoute26') or(n=='JohtoIndigoPlateau' and wp['y']==6)) else (wp['x'],wp['y'])
   assert loc in seen or wp in inherited_portals,(n,'native warp inaccessible',wp,loc)
  for o in m['object_events']:
   x,y=o['x'],o['y'];assert 0<=x<w and 0<=y<h
   if o in inherited_objects:continue
   if o['graphics_id']=='OBJ_EVENT_GFX_NURSE':
    assert (x,y+2) in seen and behavior(l,a[(y+1)*w+x])==values['MB_COUNTER'],'native nurse counter inaccessible'
    continue
   if o['graphics_id']=='OBJ_EVENT_GFX_CLERK':
    assert (x+2,y) in seen and behavior(l,a[y*w+x+1])==values['MB_COUNTER'],'native shop counter inaccessible';continue
   assert walk(x,y) and any(pos in seen for pos in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),(n,'NPC inaccessible',o)
   if 'local_id' in o:assert isinstance(o['local_id'],str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',o['local_id'])
  for co in m['coord_events']:assert (co['x'],co['y']) in seen,(n,'coordinate gate inaccessible',co)
  if n=='JohtoRoute27':assert all((0,y) in seen for y in range(18,22))
  if n.startswith('IcePath'):
   forbidden={values[n] for n in ['MB_THIN_ICE','MB_CRACKED_ICE','MB_FALL_WARP']}
   assert not any(behavior(l,t) in forbidden for t in a),'Ice Path requires no unsupported falling-ice map callbacks'
  checks.append({'map':n,'reachable_tiles':len(seen),'buffer_metatiles':(w+15)*(h+14),'native_warps':len(m['warp_events'])})
 before=s.json('data/maps/map_groups.json');after=final.json('data/maps/map_groups.json')
 assert after['gMapGroup_JohtoEntry']==OLD+NEW
 assert all(after[k]==v for k,v in before.items() if k!='gMapGroup_JohtoEntry')
 old_ls=s.json('data/layouts/layouts.json')['layouts'];assert final.json('data/layouts/layouts.json')['layouts'][:len(old_ls)]==old_ls
 old=s.json('data/maps/NewBarkTown/map.json');new=final.json('data/maps/NewBarkTown/map.json')
 assert all(old[k]==new[k] for k in old if k not in ('connections','connections_no_include'))
 con={'map':MID['JohtoRoute27'],'direction':'right','offset':0}
 oldcons=old.get('connections') or [];want=oldcons if con in oldcons else oldcons+[con]
 assert new['connections']==want
 l=ls[old['layout']];a0=s.read(l['blockdata_filepath']);a1=final.read(l['blockdata_filepath'])
 assert len(a0)==len(a1)==36*28*2
 for y in range(28):
  for x in range(36):
   i=(y*36+x)*2
   assert a0[i:i+2]==a1[i:i+2] or(x in range(32,36) and y in(20,21)),'New Bark terrain changed outside eight-cell coastal corridor'
 for y in(20,21):
  vals=struct.unpack_from('<4H',a1,2*(y*36+32))
  assert vals==(0x3115,0x112c,0x01d9,0x01d9)
  assert behavior(l,vals[0])==values['MB_SAND']
  assert all(behavior(l,v) in water_b and((v>>10)&3)==0 for v in vals[1:])
 assert not any(p in out for p in ['include/global.h','include/pokemon.h','src/save.c','src/load_save.c','src/title_screen.c','src/intro.c'])
 cmds=set(re.findall(r'(?m)^\s*\.macro\s+(\w+)',s.text('asm/macros/event.inc')+'\n'+s.text('asm/macros/map.inc')))
 cmds.update(re.findall(r'(?m)^\s*create_movement_action\s+(\w+)',s.text('asm/macros/movement.inc')))
 for p,b in out.items():
  if p.endswith('scripts.inc'):
   t=b.decode();assert not re.search(r'checktrainerflag[^\n]*\n\s*goto_if_eq\s+VAR_RESULT',t)
   for line in t.splitlines():
    z=line.strip()
    if z and not z.startswith(('@','.','#')) and not z.endswith(':'):assert z.split()[0] in cmds,(p,'unknown script command',z)
 headers='\n'.join(final.text('include/constants/'+n) for n in ['species.h','items.h','moves.h','songs.h','event_objects.h','event_object_movement.h','global.h','trainers.h'])
 party_macros=final.text('include/battle.h')
 for macro in ('ITEM_CUSTOM_MOVES','ITEM_DEFAULT_MOVES'):
  definitions=re.findall(r'^#define\s+'+re.escape(macro)+r'\([^)]*\)[^\n]*$',party_macros,re.M)
  assert len(definitions)==1,('native trainer party macro missing',macro)
  headers+='\n'+definitions[0]
 refs=set()
 for p,b in out.items():
  if p.endswith(('.inc','.h')):
   try:refs.update(re.findall(r'\b(?:SPECIES|ITEM|MOVE|MUS|OBJ_EVENT_GFX|TRAINER_CLASS|TRAINER_PIC|TRAINER_ENCOUNTER_MUSIC)_[A-Z0-9_]+',b.decode()))
   except UnicodeDecodeError:pass
 assert all(re.search(r'\b'+re.escape(z)+r'\b',headers) for z in refs),('unknown native constants',[z for z in refs if not re.search(r'\b'+re.escape(z)+r'\b',headers)])
 for p,b in out.items():
  if p.endswith('scripts.inc'):
   t=b.decode();used=[]
   for line in t.splitlines():
    if 'trainerbattle_single' not in line:continue
    args=line.strip().split(None,1)[1].split(',')
    assert len(args)==5 and args[3].strip().endswith('_Victory') and args[4].strip()=='NO_MUSIC',(p,'explicit victory callback',line)
    assert args[3].strip()+'::' in t,(p,'missing callback label')
 for n in ['JohtoLeague_WillsRoom','JohtoLeague_KogasRoom','JohtoLeague_BrunosRoom','JohtoLeague_KarensRoom','JohtoLeague_LancesRoom']:
  t=final.text('data/maps/'+n+'/scripts.inc')
  assert 'goto_if_defeated TRAINER_JOHTO_' in t and 'goto_if_unset FLAG_JOHTO_' in t
 hof=final.text('data/maps/JohtoLeague_HallOfFame/scripts.inc')
 assert 'goto_if_unset FLAG_SYS_GAME_CLEAR' in hof
 assert hof.index('setflag FLAG_JOHTO_LEAGUE_CLEARED')<hof.index('special EnterHallOfFame')
 assert 'FLAG_SYS_GAME_CLEAR' in hof and 'setflag FLAG_SYS_GAME_CLEAR' not in hof
 c=final.text('src/hall_of_fame.c')
 assert 'IsJohtoHallOfFameContext' in c and 'gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_JOHTO_LEAGUE_HALL_OF_FAME)' in c
 assert 'if (IsJohtoHallOfFameContext())\n    {\n        DoJohtoCredits();\n        return;' in c
 for n in WILD:
  row=json.loads(out['tools/johto/'+n.lower()+'_wild.json'])
  assert all(len(row[k]['mons'])==12 for k in ['land_mons','land_mons_morning','land_mons_night'])
 assert len(OLD+NEW)==124 and max(v[-1] for v in TRAINERS)==885
 glob=final.text('include/global.h')
 trainer_bytes=int(re.search(r'u8\s+hoennTrainerFlags\[(0x[0-9A-Fa-f]+|\d+)\]',glob).group(1),0)
 story_bytes=int(re.search(r'u8\s+hoennFlags\[(0x[0-9A-Fa-f]+|\d+)\]',glob).group(1),0)
 offset=int(re.search(r'JOHTO_STORY_FLAGS_START\s+\(HOENN_FLAGS_START\s*\+\s*(0x[0-9A-Fa-f]+|\d+)\)',final.text('include/constants/flags_johto_story.h')).group(1),0)
 assert max(v[-1] for v in TRAINERS)<trainer_bytes*8 and offset+max(FLAGS.values())<story_bytes*8
 for p,b in final.used.items():
  if p not in out and p not in s.overlay:s.used[p]=b
 stats.update(static_checks=checks,native_warp_behaviors_checked=checked,
  map_section_count=len(final.json('src/data/region_map/region_map_sections.json')['map_sections']),
  signed_map_num_max=len(OLD+NEW)-1,fly_destinations_total=11)
 return stats


def apply(root,mutate=False):
 assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='hoenn-z3'
 s=Source(root);out,stats=build(s);validate(s,out,stats)
 repeat,_=build(Source(root,dict(s.overlay,**out)));assert repeat==out,'Johto League generator output is not idempotent'
 owned=[p for p in out if any(p.startswith('data/maps/'+n+'/') or p.startswith('data/layouts/'+n+'/') for n in NEW)]
 owned+=['include/constants/opponents_johto_league.h','src/data/trainers_johto_league.h','src/data/trainer_parties_johto_league.h']
 for p in owned:
  if s.exists(p):assert s.read(p)==out[p],('owned Johto League artifact differs',p)
 changed={p:b for p,b in out.items() if not s.exists(p) or s.read(p)!=b}
 print(json.dumps({'apply':mutate,'files':sorted(changed),'validation':stats},indent=2))
 if not mutate or not changed:return
 for p,b in s.used.items():assert (root/p).read_bytes()==b,('concurrent source edit',p)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=root/'outputs/johto-league-v1'/stamp;dest.mkdir(parents=True,exist_ok=False);manifest={'time':stamp,'validation':stats,'files':{}}
 for p,b in changed.items():
  target=root/p;old=target.read_bytes() if target.exists() else None
  manifest['files'][p]={'before':sha(old) if old is not None else None,'after':sha(b)}
  if old is not None:
   backup=dest/'before'/p;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(old)
 (dest/'manifest.json').write_bytes(enc(manifest))
 for p,b in changed.items():
  target=root/p;target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.league.tmp')
  assert not tmp.exists();tmp.write_bytes(b);tmp.replace(target)
 print('APPLIED',dest/'manifest.json')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--apply',action='store_true');a=p.parse_args();apply(Path(a.root).resolve(),a.apply)
