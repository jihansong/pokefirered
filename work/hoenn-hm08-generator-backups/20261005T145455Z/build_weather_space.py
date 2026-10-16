#!/usr/bin/env python3
"""Add the Weather Institute -> Space Center story chapter.
Run only from the live repository root after review. No ROM or SAV edits.
"""
from pathlib import Path
import datetime, hashlib, json, re, shutil, subprocess, sys
ROOT=Path.cwd().resolve()
PATCH=Path('tools/hoenn_import/patches')
marker='@ Thunder Yellow weather-space v1'
pending={}
def read(p): return (ROOT/p).read_text(encoding='utf-8')
def stage(p,s):
 assert not Path(p).is_absolute() and '..' not in Path(p).parts
 pending[str(p)]=s.rstrip()+'\n'
def fresh(p,s):
 if (ROOT/p).exists():
  old=read(p)
  assert old.startswith(marker),('Existing unrelated canonical patch',str(p))
 stage(p,marker+'\n'+s)
def insert_definitions(p,lines):
 old=read(p)
 for name,line in lines:
  exists=re.search(r'^#define\s+'+re.escape(name)+r'\s+(.+)$',old,re.M)
  if exists:
   assert exists.group(0).strip()==line.strip(),('Definition mismatch',name)
  else:
   pos=old.rfind('#endif')
   assert pos>=0
   old=old[:pos]+line+'\n'+old[pos:]
 stage(p,old)
flags=[
 ('FLAG_HOENN_WEATHER_RESCUED',105),
 ('FLAG_HOENN_GOT_WEATHER_CASTFORM',106),
 ('FLAG_HOENN_SPACE_CENTER_SECURED',107),
 ('FLAG_HIDE_HOENN_SPACE_RAID',108),
 ('FLAG_HOENN_GOT_HM08_FROM_STEVEN',109)]
fpath=Path('include/constants/flags_hoenn_story.h')
insert_definitions(fpath,[(n,'#define %s (HOENN_STORY_FLAGS_START + %d)'%(n,v)) for n,v in flags])
txt=pending[str(fpath)]
match=re.search(r'(#define\s+HOENN_STORY_FLAGS_USED\s+)(\d+)',txt)
assert match and int(match[2]) in (105,110),('Unexpected flag allocation',match[2] if match else None)
stage(fpath,txt[:match.start(2)]+'110'+txt[match.end(2):])
opath=Path('include/constants/opponents_hoenn_story.h')
insert_definitions(opath,[
 ('TRAINER_HOENN_TABITHA_SPACE_CENTER','#define TRAINER_HOENN_TABITHA_SPACE_CENTER (HOENN_TRAINERS_START + 536)'),
 ('TRAINER_HOENN_MAXIE_SPACE_CENTER','#define TRAINER_HOENN_MAXIE_SPACE_CENTER (HOENN_TRAINERS_START + 537)')])
# Keep the hand-written additions outside the imported trainer block.
tpath=Path('src/data/trainers.h')
tc=read(tpath)
inc='#include "trainers_hoenn_story.h"'
if inc not in tc:
 anchor='#include "trainers_tournament.h"'
 assert tc.count(anchor)==1
 tc=tc.replace(anchor,anchor+'\n'+inc)
stage(tpath,tc)
source=read(Path('src/data/trainers_hoenn.h'))
newteams=[]
for old,new in [
 ('TRAINER_HOENN_TABITHA_MAGMA_HIDEOUT','TRAINER_HOENN_TABITHA_SPACE_CENTER'),
 ('TRAINER_HOENN_MAXIE_MAGMA_HIDEOUT','TRAINER_HOENN_MAXIE_SPACE_CENTER')]:
 block=re.search(r'(?ms)^\s{4}\['+old+r'\]\s*=\s*\n.*?^\s{4}\},',source)
 assert block,old
 newteams.append(block[0].replace(old,new,1))
tp=Path('src/data/trainers_hoenn_story.h')
old=read(tp) if (ROOT/tp).exists() else '// Dedicated Hoenn story encounters; parties and graphics reuse imported assets.\n'
for team,name in zip(newteams,['TRAINER_HOENN_TABITHA_SPACE_CENTER','TRAINER_HOENN_MAXIE_SPACE_CENTER']):
 pat=r'(?ms)^\s{4}\['+name+r'\]\s*=\s*\n.*?^\s{4}\},'
 if re.search(pat,old): old=re.sub(pat,lambda _:team,old)
 else: old=old.rstrip()+'\n'+team+'\n'
# Dedicated parties keep the imported encounters and defeated flags untouched.
party_source=read(Path('src/data/trainer_parties_hoenn.h'))
party_defs=[]
for oldparty,newparty,levels in [
 ('sHoennParty_TabithaMagmaHideout','sHoennParty_TabithaSpaceCenter',[36,38,40,42]),
 ('sHoennParty_MaxieMagmaHideout','sHoennParty_MaxieSpaceCenter',[42,43,44])]:
 block=re.search(r'(?ms)^static const struct TrainerMonNoItemDefaultMoves '+oldparty+r'\[\] = \{.*?^\};',party_source)
 assert block,oldparty
 body=block[0].replace(oldparty,newparty,1)
 assert len(re.findall(r'\.lvl = \d+',body))==len(levels)
 seq=iter(levels)
 body=re.sub(r'(\.lvl = )\d+',lambda m:m[1]+str(next(seq)),body)
 party_defs.append(body)
 old=old.replace(oldparty,newparty)
stage(tp,old)
pp=Path('src/data/trainer_parties_hoenn_story.h')
parts=read(pp) if (ROOT/pp).exists() else '// Hoenn Space Center encounters; native species and graphics.\n'
for body,name in zip(party_defs,['sHoennParty_TabithaSpaceCenter','sHoennParty_MaxieSpaceCenter']):
 pat=r'(?ms)^static const struct TrainerMonNoItemDefaultMoves '+name+r'\[\] = \{.*?^\};'
 if re.search(pat,parts): parts=re.sub(pat,lambda _:body,parts)
 else: parts=parts.rstrip()+'\n'+body+'\n'
stage(pp,parts)
ppmain=Path('src/data/trainer_parties.h')
pc=read(ppmain)
inc='#include "trainer_parties_hoenn_story.h"'
if inc not in pc:
 anchor='#include "trainer_parties_tournament.h"'
 assert pc.count(anchor)==1
 pc=pc.replace(anchor,anchor+'\n'+inc)
stage(ppmain,pc)
W1='Route119_WeatherInstitute_1F'
W2='Route119_WeatherInstitute_2F'
S1='MossdeepCity_SpaceCenter_1F'
S2='MossdeepCity_SpaceCenter_2F'
def obj(g,x,y,script,flag='0'):
 return {'type':'object','graphics_id':g,'x':x,'y':y,'elevation':3,
  'movement_type':'MOVEMENT_TYPE_FACE_DOWN','movement_range_x':0,'movement_range_y':0,
  'trainer_type':'TRAINER_TYPE_NONE','trainer_sight_or_berry_tree_id':'0','script':script,'flag':flag}
def objects(m,overrides,extras=[]):
 data={'object_overrides':overrides}
 if extras:data['object_events']=extras
 p=PATCH/(m+'.json')
 if (ROOT/p).exists():assert json.loads(read(p))==data,('Unexpected existing canonical objects',m)
 stage(p,json.dumps(data,indent=2))
def text_file(m,rows):
 out=[]
 for suffix,paragraphs in rows.items():
  out.append(m+'_Text_'+suffix+'::')
  for pi,para in enumerate(paragraphs):
   lines=para.split('|')
   for li,line in enumerate(lines):
    assert '"' not in line and '\\' not in line
    end='$' if pi==len(paragraphs)-1 and li==len(lines)-1 else (r'\p' if li==len(lines)-1 else (r'\n' if li==0 else r'\l'))
    out.append('\t.string "'+line+end+'"')
  out.append('')
 fresh(PATCH/(m+'.text.inc'),'\n'.join(out))
def script(m,raw):fresh(PATCH/(m+'.scripts.inc'),raw.replace('@M@',m))
def hooks(m):
 fresh(PATCH/(m+'.mapscripts'),'\tmap_script MAP_SCRIPT_ON_TRANSITION, '+m+'_WeatherSpaceOnTransition\n\tmap_script MAP_SCRIPT_ON_RESUME, '+m+'_WeatherSpaceOnResume')
objects(W1,[{'x':14,'y':11,'movement_type':'MOVEMENT_TYPE_FACE_UP','movement_range_x':0,
 'movement_range_y':0,'script':W1+'_EventScript_Shelter'}])
script(W1,r'''
@M@_EventScript_Shelter::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_WEATHER_RESCUED, @M@_EventScript_ShelterAfter
 msgbox @M@_Text_ShelterBefore
 release
 end
@M@_EventScript_ShelterAfter::
 msgbox @M@_Text_ShelterAfter
 release
 end
''')
text_file(W1,{
 'ShelterBefore':['TEAM AQUA took over the upper|floor! The scientist is trapped.',
                  'They came for our readings of|the rain and ocean currents.'],
 'ShelterAfter':['The researchers are safe again!|Thank you for driving AQUA away.',
                'The scientist upstairs wants to|thank you in person.']})
objects(W2,[{'x':18,'y':6,'movement_type':'MOVEMENT_TYPE_FACE_DOWN','movement_range_x':0,
 'movement_range_y':0,'script':W2+'_EventScript_Researcher'}],
 [obj('OBJ_EVENT_GFX_AQUA_MEMBER_F',17,6,W2+'_EventScript_Shelly','FLAG_HOENN_WEATHER_RESCUED')])
hooks(W2)
script(W2,r'''
@M@_WeatherSpaceOnTransition::
 call @M@_EventScript_RescueState
 end
@M@_WeatherSpaceOnResume::
 call @M@_EventScript_RescueState
 goto_if_unset FLAG_HOENN_WEATHER_RESCUED, @M@_EventScript_ResumeEnd
 removeobject 2
@M@_EventScript_ResumeEnd::
 end
@M@_EventScript_RescueState::
 goto_if_defeated TRAINER_HOENN_SHELLY_WEATHER_INSTITUTE, @M@_EventScript_RescueBackfill
 return
@M@_EventScript_RescueBackfill::
 setflag FLAG_HOENN_WEATHER_RESCUED
 return
@M@_EventScript_Shelly::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_WEATHER_RESCUED, EventScript_ReleaseEnd
 trainerbattle_single TRAINER_HOENN_SHELLY_WEATHER_INSTITUTE, @M@_Text_ShellyIntro, @M@_Text_ShellyDefeat, @M@_EventScript_AfterShelly
 goto @M@_EventScript_AfterShelly
@M@_EventScript_AfterShelly::
 setflag FLAG_HOENN_WEATHER_RESCUED
 msgbox @M@_Text_ShellyRetreat
 closemessage
 fadescreen FADE_TO_BLACK
 removeobject 2
 fadescreen FADE_FROM_BLACK
 msgbox @M@_Text_Rescued
 release
 end
@M@_EventScript_Researcher::
 lock
 faceplayer
 goto_if_unset FLAG_HOENN_WEATHER_RESCUED, @M@_EventScript_Hostage
 goto_if_set FLAG_HOENN_GOT_WEATHER_CASTFORM, @M@_EventScript_Report
 msgbox @M@_Text_OfferCastform, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, @M@_EventScript_Report
 setvar VAR_TEMP_1, SPECIES_CASTFORM
 call EventScript_GiveGiftMonLv25
 goto_if_eq VAR_RESULT, FALSE, @M@_EventScript_Report
 setflag FLAG_HOENN_GOT_WEATHER_CASTFORM
 textcolor NPC_TEXT_COLOR_MALE
 goto @M@_EventScript_Report
@M@_EventScript_Hostage::
 msgbox @M@_Text_Hostage
 release
 end
@M@_EventScript_Report::
 goto_if_set FLAG_HOENN_SPACE_CENTER_SECURED, @M@_EventScript_ReportAfterSpace
 msgbox @M@_Text_ResearchReport
 goto_if_unset FLAG_GOT_CASTFORM, EventScript_ReleaseEnd
 msgbox @M@_Text_FourIslandColleague
 release
 end
@M@_EventScript_ReportAfterSpace::
 msgbox @M@_Text_AfterSpace
 release
 end
''')
text_file(W2,{
 'ShellyIntro':['SHELLY: These readings reveal|where the deep currents meet.',
                'TEAM AQUA needs them.|You will not stand in our way!'],
 'ShellyDefeat':['You have washed out our plan!'],
 'ShellyRetreat':['SHELLY: Keep your readings.|We already know where to search.',
                  'The ocean has a secret you have|not even begun to understand!'],
 'Rescued':['The researchers are safe!'],
 'Hostage':['AQUA wants the deep-sea data.|Please help us!'],
 'OfferCastform':['You saved our research team!|Please take this CASTFORM.',
                  'It changes with the weather.|Will you travel with it?'],
 'ResearchReport':['AQUA copied our ocean readings.|STEVEN is tracing the same signal.',
                   'He is at the SPACE CENTER in|MOSSDEEP. Please speak with him.'],
 'FourIslandColleague':['Our colleague on FOUR ISLAND|told us about your travels.',
                        'Your help has reached all the|way from KANTO to HOENN.'],
 'AfterSpace':['STEVEN confirmed the deep-sea|signal using the satellite data.',
               'Please stop the teams before|they disturb its source.']})
objects(S1,[
 {'x':7,'y':2,'script':S1+'_EventScript_MissionControl'},
 {'x':6,'y':6,'script':S1+'_EventScript_Safety'},
 {'x':10,'y':2,'script':S1+'_EventScript_MissionControl'},
 {'x':14,'y':7,'script':S1+'_EventScript_Safety'}])
script(S1,r'''
@M@_EventScript_MissionControl::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_SPACE_CENTER_SECURED, @M@_EventScript_ControlAfter
 goto_if_unset FLAG_HOENN_WEATHER_RESCUED, @M@_EventScript_ControlBefore
 goto_if_unset FLAG_HOENN_BADGE07_GET, @M@_EventScript_ControlPrepare
 msgbox @M@_Text_Raid
 release
 end
@M@_EventScript_ControlBefore::
 msgbox @M@_Text_BeforeResearch
 release
 end
@M@_EventScript_ControlPrepare::
 msgbox @M@_Text_Prepare
 release
 end
@M@_EventScript_ControlAfter::
 msgbox @M@_Text_AfterRaid
 release
 end
@M@_EventScript_Safety::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_SPACE_CENTER_SECURED, @M@_EventScript_SafetyAfter
 goto_if_unset FLAG_HOENN_WEATHER_RESCUED, @M@_EventScript_SafetyBefore
 goto_if_unset FLAG_HOENN_BADGE07_GET, @M@_EventScript_SafetyBefore
 msgbox @M@_Text_SafetyRaid
 release
 end
@M@_EventScript_SafetyBefore::
 msgbox @M@_Text_Safety
 release
 end
@M@_EventScript_SafetyAfter::
 msgbox @M@_Text_SafetyAfter
 release
 end
''')
text_file(S1,{
 'BeforeResearch':['Our satellites observe the|ocean as well as the sky.',
                   'STEVEN is upstairs, waiting for|the WEATHER INSTITUTE report.'],
 'Prepare':['STEVEN is upstairs. He asks you|to prepare at MOSSDEEP GYM first.',
            'The deep-sea signal is growing|stronger by the hour.'],
 'Raid':['TEAM MAGMA has entered upstairs!|They are after our rocket fuel.',
         'STEVEN needs your help!'],
 'AfterRaid':['The rocket fuel is safe.|The launch can proceed.',
              'Our satellite readings will help|STEVEN locate the deep-sea signal.'],
 'Safety':['Rocket fuel is strictly guarded.|Only our staff may handle it.'],
 'SafetyRaid':['Please help STEVEN upstairs.|Keep MAGMA away from the fuel!'],
 'SafetyAfter':['You stopped the fuel theft.|We can all breathe again!']})
objects(S2,[
 {'x':6,'y':2,'script':S2+'_EventScript_Visitor'},
 {'x':11,'y':8,'script':S2+'_EventScript_Visitor'},
 {'x':5,'y':6,'movement_type':'MOVEMENT_TYPE_FACE_DOWN','movement_range_x':0,
  'movement_range_y':0,'script':S2+'_EventScript_Scientist'}],
 [obj('OBJ_EVENT_GFX_STEVEN',14,6,S2+'_EventScript_Steven'),
  obj('OBJ_EVENT_GFX_MAGMA_MEMBER_M',13,7,S2+'_EventScript_Tabitha','FLAG_HIDE_HOENN_SPACE_RAID'),
  obj('OBJ_EVENT_GFX_MAXIE',14,8,S2+'_EventScript_Maxie','FLAG_HIDE_HOENN_SPACE_RAID')])
hooks(S2)
script(S2,r'''
@M@_WeatherSpaceOnTransition::
 call @M@_EventScript_SetRaidState
 end
@M@_WeatherSpaceOnResume::
 call @M@_EventScript_SetRaidState
 goto_if_set FLAG_HIDE_HOENN_SPACE_RAID, @M@_EventScript_RemoveRaid
 addobject 5
 addobject 6
 end
@M@_EventScript_RemoveRaid::
 removeobject 5
 removeobject 6
 end
@M@_EventScript_SetRaidState::
 setflag FLAG_HIDE_HOENN_SPACE_RAID
 goto_if_set FLAG_HOENN_SPACE_CENTER_SECURED, @M@_EventScript_StateReturn
 goto_if_unset FLAG_HOENN_WEATHER_RESCUED, @M@_EventScript_StateReturn
 goto_if_unset FLAG_HOENN_BADGE07_GET, @M@_EventScript_StateReturn
 goto_if_defeated TRAINER_HOENN_MAXIE_SPACE_CENTER, @M@_EventScript_CheckTabithaForClear
 clearflag FLAG_HIDE_HOENN_SPACE_RAID
 return
@M@_EventScript_CheckTabithaForClear::
 goto_if_defeated TRAINER_HOENN_TABITHA_SPACE_CENTER, @M@_EventScript_ClearBackfill
 clearflag FLAG_HIDE_HOENN_SPACE_RAID
 return
@M@_EventScript_ClearBackfill::
 setflag FLAG_HOENN_SPACE_CENTER_SECURED
@M@_EventScript_StateReturn::
 return
@M@_EventScript_Tabitha::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_SPACE_CENTER_SECURED, EventScript_ReleaseEnd
 goto_if_unset FLAG_HOENN_WEATHER_RESCUED, EventScript_ReleaseEnd
 goto_if_unset FLAG_HOENN_BADGE07_GET, EventScript_ReleaseEnd
 goto_if_defeated TRAINER_HOENN_TABITHA_SPACE_CENTER, @M@_EventScript_TabithaAfter
 trainerbattle_single TRAINER_HOENN_TABITHA_SPACE_CENTER, @M@_Text_TabithaIntro, @M@_Text_TabithaDefeat, @M@_EventScript_TabithaAfter
 goto @M@_EventScript_TabithaAfter
@M@_EventScript_TabithaAfter::
 msgbox @M@_Text_TabithaAfter
 release
 end
@M@_EventScript_Maxie::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_SPACE_CENTER_SECURED, EventScript_ReleaseEnd
 goto_if_unset FLAG_HOENN_WEATHER_RESCUED, EventScript_ReleaseEnd
 goto_if_unset FLAG_HOENN_BADGE07_GET, EventScript_ReleaseEnd
 goto_if_defeated TRAINER_HOENN_TABITHA_SPACE_CENTER, @M@_EventScript_MaxieReady
 msgbox @M@_Text_MaxieWait
 release
 end
@M@_EventScript_MaxieReady::
 trainerbattle_single TRAINER_HOENN_MAXIE_SPACE_CENTER, @M@_Text_MaxieIntro, @M@_Text_MaxieDefeat, @M@_EventScript_MaxieAfter
 goto @M@_EventScript_MaxieAfter
@M@_EventScript_MaxieAfter::
 setflag FLAG_HOENN_SPACE_CENTER_SECURED
 setflag FLAG_HIDE_HOENN_SPACE_RAID
 msgbox @M@_Text_MaxieRetreat
 closemessage
 fadescreen FADE_TO_BLACK
 removeobject 5
 removeobject 6
 fadescreen FADE_FROM_BLACK
 msgbox @M@_Text_StevenSaved
 release
 end
@M@_EventScript_Steven::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_SPACE_CENTER_SECURED, @M@_EventScript_StevenAfter
 goto_if_unset FLAG_HOENN_WEATHER_RESCUED, @M@_EventScript_StevenBefore
 goto_if_unset FLAG_HOENN_SURVEY_LETTER_DONE, @M@_EventScript_StevenNoSurvey
 msgbox @M@_Text_SurveyConnection
@M@_EventScript_StevenNoSurvey::
 goto_if_unset FLAG_HOENN_BADGE07_GET, @M@_EventScript_StevenPrepare
 msgbox @M@_Text_StevenRaid
 release
 end
@M@_EventScript_StevenBefore::
 msgbox @M@_Text_StevenBefore
 release
 end
@M@_EventScript_StevenPrepare::
 msgbox @M@_Text_StevenPrepare
 release
 end
@M@_EventScript_StevenAfter::
 goto_if_set FLAG_HOENN_GOT_HM08_FROM_STEVEN, @M@_EventScript_DiveReport
 checkitem ITEM_HM08
 goto_if_eq VAR_RESULT, TRUE, @M@_EventScript_DiveReceived
 msgbox @M@_Text_DiveOffer
 giveitem ITEM_HM08
 goto_if_eq VAR_RESULT, FALSE, @M@_EventScript_DiveNoRoom
@M@_EventScript_DiveReceived::
 setflag FLAG_HOENN_GOT_HM08_FROM_STEVEN
@M@_EventScript_DiveReport::
 msgbox @M@_Text_StevenAfter
 release
 end
@M@_EventScript_DiveNoRoom::
 msgbox @M@_Text_DiveNoRoom
 release
 end
@M@_EventScript_Scientist::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_SPACE_CENTER_SECURED, @M@_EventScript_ScientistAfter
 goto_if_set FLAG_HIDE_HOENN_SPACE_RAID, @M@_EventScript_ScientistBefore
 msgbox @M@_Text_ScientistRaid
 release
 end
@M@_EventScript_ScientistBefore::
 msgbox @M@_Text_ScientistBefore
 release
 end
@M@_EventScript_ScientistAfter::
 msgbox @M@_Text_ScientistAfter
 release
 end
@M@_EventScript_Visitor::
 lock
 faceplayer
 goto_if_set FLAG_HIDE_HOENN_SPACE_RAID, @M@_EventScript_VisitorSafe
 msgbox @M@_Text_VisitorRaid
 release
 end
@M@_EventScript_VisitorSafe::
 msgbox @M@_Text_VisitorSafe
 release
 end
''')
text_file(S2,{
 'TabithaIntro':['TABITHA: This rocket fuel will|feed MT. CHIMNEY.',
                 'MAGMA will remake the land!'],
 'TabithaDefeat':['You broke through our defense!'],
 'TabithaAfter':['TABITHA: MAXIE will finish this!|I will not fight you again.'],
 'MaxieWait':['MAXIE: TABITHA, keep this|trainer away from the fuel!'],
 'MaxieIntro':['MAXIE: AQUA seeks the deep sea.|We will answer with fire.',
               'This fuel will strengthen the|land. You cannot stop us!'],
 'MaxieDefeat':['Even here, our plan has failed!'],
 'MaxieRetreat':['MAXIE: The fuel is yours.|We must reconsider our plans.',
                 'But do not ignore AQUA.|Their search has not ended!'],
 'StevenSaved':['STEVEN: The SPACE CENTER is|safe. Thank you!',
                'Speak with me before you go.|The readings reveal our next lead.'],
 'StevenBefore':['STEVEN: I am studying a signal|far beneath HOENN.',
                  'The WEATHER INSTITUTE on|ROUTE 119 has the missing data.',
                  'Please check on its researchers.'],
 'SurveyConnection':['STEVEN: This matches the gap in|the survey STERN sent us.',
                      'Your journey from the harbor|has brought us to its source.'],
 'StevenPrepare':['STEVEN: Thank you for helping|the WEATHER INSTITUTE.',
                   'Visit TATE and LIZA at the GYM.|Their badge proves your readiness.',
                   'Then return here. I will|compare the satellite readings.'],
 'StevenRaid':['STEVEN: MAGMA wants the rocket|fuel to awaken the volcano.',
               'Please defeat TABITHA, then|MAXIE. I will guard the fuel.',
               'You can leave to heal your team.|I will keep the staff safe.'],
 'DiveOffer':['STEVEN: Take HM08, DIVE.|It will help with the sea search.'],
 'DiveNoRoom':['STEVEN: Please make room in the|TM CASE. I will keep HM08 for you.'],
 'StevenAfter':['STEVEN: Teach DIVE to a partner.|Explore the dark water on ROUTE 128.',
                 'Our lead is the SEAFLOOR CAVERN.|AQUA is searching there.',
                 'The disturbance may reach|SOOTOPOLIS if it continues.'],
 'ScientistBefore':['We compare satellite readings|with the WEATHER INSTITUTE.'],
 'ScientistRaid':['MAGMA is here for the fuel!|STEVEN is protecting the staff.'],
 'ScientistAfter':['The fuel is safe. Our readings|now confirm the deep-sea signal.'],
 'VisitorRaid':['I came to see a rocket launch,|not a fight over its fuel!'],
 'VisitorSafe':['The stars are far away, but|research also protects this world.']})
# Validate all new script labels before writing any file.
for p,s in pending.items():
 if p.endswith('.scripts.inc') or p.endswith('.text.inc'):
  labels=re.findall(r'^(\w+)::',s,re.M)
  assert len(labels)==len(set(labels)),('Duplicate canonical labels',p)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=ROOT/'work/hoenn-weather-space-v1-backups'/stamp
for p,s in pending.items():
 path=ROOT/p
 if path.exists():
  dest=backup/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
for m in [W1,W2,S1,S2]:
 for name in ['map.json','scripts.inc','text.inc']:
  p=Path('data/maps')/m/name
  dest=backup/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,dest)
for p,s in pending.items():
 path=ROOT/p;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(s,encoding='utf-8')
subprocess.run([sys.executable,'tools/hoenn_import/apply_patches.py',W1,W2,S1,S2],check=True)
receipt={'source_only':True,'maps':[W1,W2,S1,S2],'flag_offsets':dict(flags),
 'trainers':{'TABITHA_SPACE_CENTER':536,'MAXIE_SPACE_CENTER':537},
 'files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in pending},
 'backup':str(backup),'save_layout_changed':False,'runtime_validated':False,
 'scope':'Weather rescue and Space Center raid; not the complete Hoenn main story.'}
(backup/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'prepared_files':len(pending),'maps':4,'backup':str(backup),'runtime_validated':False}))
