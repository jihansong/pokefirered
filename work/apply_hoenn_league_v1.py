#!/usr/bin/env python3
"""Apply Hoenn late-gym, league and native-credits candidate. Run from repo root.
No ROM build, original SAV mutation or publication. Existing files are backed up.
"""
from pathlib import Path
import json,re,subprocess,datetime,hashlib
R=Path('/workspaces/pokefirered'); P=R/'tools/hoenn_import/patches'
MARK='@ THYL_LEAGUE_V1'
pending={}
def read(p): return pending.get(p,p.read_text() if p.exists() else '')
def put(p,s): pending[p]=s
def replace(p,a,b):
 s=read(p);assert s.count(a)==1,(str(p),a[:90],s.count(a));put(p,s.replace(a,b,1))
def patch(name,kind,body):
 p=P/(name+'.'+kind);s=read(p);assert MARK not in s,str(p)
 labels=set(re.findall(r'^(\w+)::?\s*$',body,re.M))
 matches=list(re.finditer(r'^(\w+)::?[ \t]*\n',s,re.M))
 for i in range(len(matches)-1,-1,-1):
  m=matches[i]
  if m.group(1) in labels:
   end=matches[i+1].start() if i+1<len(matches) else len(s)
   s=s[:m.start()]+s[end:]
 put(p,s.rstrip()+'\n\n'+MARK+'\n'+body.strip()+'\n')
def mapscript(name,kind,label):
 p=P/(name+'.mapscripts');s=read(p);assert kind not in s,str(p)
 put(p,s.rstrip()+'\n\tmap_script '+kind+', '+label+'\n')
def objects(name,entries):
 p=P/(name+'.json');d=json.loads(read(p) or '{}')
 d.setdefault('object_overrides',[]).extend(entries);put(p,json.dumps(d,indent=2)+'\n')
def text(label,lines):
 out=label+'::\n'
 for i,line in enumerate(lines):
  last=i==len(lines)-1
  quote=json.dumps(line+('$' if last else ''),ensure_ascii=False)
  control='' if last else ('\\n' if i%2==0 else '\\p')
  out+='\t.string '+quote[:-1]+control+'"\n'
 return out+'\n'
def mid(name): return json.loads((R/'data/maps'/name/'map.json').read_text())['id']
flags=R/'include/constants/flags_hoenn_story.h'
s=read(flags)
assert re.search(r'#define\s+HOENN_STORY_FLAGS_USED\s+102\b',s)
assert 'FLAG_HOENN_LEAGUE_CLEAR' not in s
s,n=re.subn(r'#define\s+HOENN_STORY_FLAGS_USED\s+102\b',
'''#define FLAG_HOENN_LEAGUE_CLEAR (HOENN_STORY_FLAGS_START + 102)
#define FLAG_HOENN_GOT_TM04 (HOENN_STORY_FLAGS_START + 103)
#define FLAG_HOENN_GOT_TM03 (HOENN_STORY_FLAGS_START + 104)
#define HOENN_STORY_FLAGS_USED 105''',s)
assert n==1;put(flags,s)
varsfile=R/'include/constants/vars_hoenn.h';s=read(varsfile)
assert 'VAR_HOENN_LEAGUE_PROGRESS' not in s
assert re.search(r'#define\s+VAR_HOENN_0x29\s+\(HOENN_VARS_START \+ 41\)',s)
put(varsfile,s.replace('#endif','#define VAR_HOENN_LEAGUE_PROGRESS VAR_HOENN_0x29\n\n#endif',1))
maps=[]
def done(name):
 if name not in maps:maps.append(name)
# Backfill a legitimately won old save; the item flag is committed only on success.
for name,tr,badge,tm,flag,double in [
 ('MossdeepCity_Gym','TRAINER_HOENN_TATE_AND_LIZA_1','FLAG_HOENN_BADGE07_GET','ITEM_TM04','FLAG_HOENN_GOT_TM04',True),
 ('SootopolisCity_Gym_1F','TRAINER_HOENN_JUAN_1','FLAG_HOENN_BADGE08_GET','ITEM_TM03','FLAG_HOENN_GOT_TM03',False)]:
 q=name+'_TY'
 body=''.join(f'{name}_EventScript_H{i}::\n\tgoto {q}_Boss\n\n' for i in ([0,8] if double else [0]))
 if double:
  battle=f'\ttrainerbattle_double {tr}, {name}_Text_H0_0, {name}_Text_H0_1, {q}_TooFew, {q}_Reward\n'
 else:
  battle=f'\ttrainerbattle_single {tr}, {name}_Text_H0_0, {name}_Text_H0_1, {q}_Reward\n'
 body+=f'''{q}_Boss::
\tgoto_if_defeated {tr}, {q}_Reward
{battle}\tgoto {q}_Reward

{q}_Reward::
\tlock
\tfaceplayer
\tgoto_if_not_defeated {tr}, {q}_Done
\tsetflag {badge}
\tgoto_if_set {flag}, {q}_Post
\tmsgbox {q}_Badge
\tcheckitemspace {tm}
\tgoto_if_eq VAR_RESULT, FALSE, {q}_Full
\tgiveitem {tm}
\tgoto_if_eq VAR_RESULT, FALSE, {q}_Full
\tsetflag {flag}
{q}_Post::
\tmsgbox {name}_Text_H0_2
{q}_Done::
\trelease
\tend

{q}_Full::
\tmsgbox {q}_BagFull
\trelease
\tend
'''
 patch(name,'scripts.inc',body)
 badge_name='MIND BADGE' if double else 'RAIN BADGE'
 patch(name,'text.inc',text(q+'_Badge',['You earned the '+badge_name+'!','Take this TM as well.'])+
  text(q+'_BagFull',['Make room for the TM, then','speak to me again. Keep the BADGE!'])+
  text(q+'_TooFew',['Bring two POK챕MON that can battle','to challenge us together!']))
 done(name)
L='EverGrandeCity_PokemonLeague_1F'
rooms=[('EverGrandeCity_SidneysRoom','SIDNEY'),('EverGrandeCity_PhoebesRoom','PHOEBE'),('EverGrandeCity_GlaciasRoom','GLACIA'),('EverGrandeCity_DrakesRoom','DRAKE'),('EverGrandeCity_ChampionsRoom','WALLACE')]
trainers=['TRAINER_HOENN_'+n for _,n in rooms]
reset=''.join(f'\tcleartrainerflag {t}\n' for t in trainers)
checks=''.join(f'\tgoto_if_unset FLAG_HOENN_BADGE{i:02d}_GET, TYHoennLeague_NoBadges\n' for i in range(1,9))
patch(L,'scripts.inc',f'''{L}_OnTransition::
\tsetobjectxyperm 3, 9, 2
\tsetobjectxyperm 4, 10, 2
\tsetvar VAR_HOENN_LEAGUE_PROGRESS, 0
{reset}\tend

{L}_EventScript_H1::
\tgoto TYHoennLeague_Enter

{L}_EventScript_H2::
\tgoto TYHoennLeague_Enter

TYHoennLeague_CheckBadges::
{checks}\tsetvar VAR_RESULT, TRUE
\treturn

TYHoennLeague_NoBadges::
\tsetvar VAR_RESULT, FALSE
\treturn

TYHoennLeague_Enter::
\tlockall
\tcall TYHoennLeague_CheckBadges
\tgoto_if_eq VAR_RESULT, FALSE, TYHoennLeague_NeedBadges
\tmsgbox TYHoennLeague_Text_Challenge, MSGBOX_YESNO
\tgoto_if_eq VAR_RESULT, NO, TYHoennLeague_Release
{reset}\tsetvar VAR_HOENN_LEAGUE_PROGRESS, 1
\tsetrespawn HEAL_LOCATION_HOENN_EVER_GRANDE_CITY_POKEMON_LEAGUE
\twarp {mid(rooms[0][0])}, 6, 10
\twaitstate
\treleaseall
\tend

TYHoennLeague_NeedBadges::
\tmsgbox TYHoennLeague_Text_NeedBadges
TYHoennLeague_Release::
\treleaseall
\tend

TYHoennLeague_InvalidEntry::
\tlockall
\tmsgbox TYHoennLeague_Text_Invalid
\twarp {mid(L)}, 9, 6
\twaitstate
\treleaseall
\tend
''')
patch(L,'text.inc',
 text('TYHoennLeague_Text_Challenge',['All eight HOENN BADGES checked.','Challenge the ELITE FOUR?','Use items between battles, then','speak to each member to continue.'])+
 text('TYHoennLeague_Text_NeedBadges',['Only challengers with all eight','HOENN BADGES may enter.'])+
 text('TYHoennLeague_Text_Invalid',['Start your challenge at the','LEAGUE reception. Please return.']))
done(L)
intros=[
 ['SIDNEY: You came far from KANTO.','Show me your own battle style!'],
 ['PHOEBE: Your bond with POK챕MON','has carried you here. Show me!'],
 ['GLACIA: Crossing regions must','have tempered your resolve.'],
 ['DRAKE: More than strength, a','TRAINER needs trust in the team.'],
 ["WALLACE: You faced HOENN's trials","with partners from your journey.",'Now show me the strength','of a CHAMPION!']]
defeats=['You have the spirit to go on!','Your bond shines brightly!','A splendid and determined battle!','That is the trust I hoped to see!','Your team has earned this victory!']
for i,(name,who) in enumerate(rooms):
 q=name+'_TY';tr=trainers[i];stage=i+1;nxt=i+2
 dest='EverGrandeCity_HallOfFame' if i==4 else rooms[i+1][0]
 xy='7, 10' if i==4 else '6, 10'
 prior=''.join(f'\tgoto_if_not_defeated {t}, TYHoennLeague_InvalidEntry\n' for t in trainers[:i])
 mapscript(name,'MAP_SCRIPT_ON_FRAME_TABLE',q+'_OnFrame')
 mapscript(name,'MAP_SCRIPT_ON_TRANSITION',q+'_OnTransition')
 objects(name,[{'x':6,'y':5,'script':q+'_Boss'}])
 patch(name,'scripts.inc',f'''{q}_OnTransition::
\tsetvar VAR_TEMP_1, 0
\tend

{q}_OnFrame::
\tmap_script_2 VAR_TEMP_1, 0, {q}_Validate
\t.2byte 0

{q}_Validate::
\tsetvar VAR_TEMP_1, 1
\tcall TYHoennLeague_CheckBadges
\tgoto_if_eq VAR_RESULT, FALSE, TYHoennLeague_InvalidEntry
\tgoto_if_lt VAR_HOENN_LEAGUE_PROGRESS, {stage}, TYHoennLeague_InvalidEntry
\tgoto_if_gt VAR_HOENN_LEAGUE_PROGRESS, 6, TYHoennLeague_InvalidEntry
{prior}\tend

{q}_Boss::
\tlock
\tfaceplayer
\tcall TYHoennLeague_CheckBadges
\tgoto_if_eq VAR_RESULT, FALSE, TYHoennLeague_InvalidEntry
\tgoto_if_lt VAR_HOENN_LEAGUE_PROGRESS, {stage}, TYHoennLeague_InvalidEntry
\tgoto_if_gt VAR_HOENN_LEAGUE_PROGRESS, 6, TYHoennLeague_InvalidEntry
{prior}\tgoto_if_defeated {tr}, {q}_Advance
\tmsgbox {q}_Intro
\ttrainerbattle_no_intro {tr}, {q}_Defeat
\tgoto_if_not_defeated {tr}, {q}_Release
\tgoto_if_ge VAR_HOENN_LEAGUE_PROGRESS, {nxt}, {q}_Won
\tsetvar VAR_HOENN_LEAGUE_PROGRESS, {nxt}
{q}_Won::
\tmsgbox {q}_Victory
{q}_Release::
\trelease
\tend

{q}_Advance::
\tgoto_if_ge VAR_HOENN_LEAGUE_PROGRESS, {nxt}, {q}_Ready
\tsetvar VAR_HOENN_LEAGUE_PROGRESS, {nxt}
{q}_Ready::
\tmsgbox {q}_GoOn, MSGBOX_YESNO
\tgoto_if_eq VAR_RESULT, NO, {q}_Release
\twarp {mid(dest)}, {xy}
\twaitstate
\treleaseall
\tend
''')
 patch(name,'text.inc',text(q+'_Intro',intros[i])+text(q+'_Defeat',[defeats[i]])+
  text(q+'_Victory',['You have won. Prepare your team,','then speak to me to continue.'])+
  text(q+'_GoOn',['Enter the HALL OF FAME now?'] if i==4 else ['Are you ready to face the next','member of the ELITE FOUR?']))
 done(name)
H='EverGrandeCity_HallOfFame';q=H+'_TY'
mapscript(H,'MAP_SCRIPT_ON_TRANSITION',q+'_Position')
mapscript(H,'MAP_SCRIPT_ON_FRAME_TABLE',q+'_OnFrame')
objects(H,[{'x':6,'y':16,'script':q+'_Greeting','movement_type':'MOVEMENT_TYPE_FACE_DOWN'}])
prior=''.join(f'\tgoto_if_not_defeated {t}, TYHoennLeague_InvalidEntry\n' for t in trainers)
patch(H,'scripts.inc',f'''{q}_Position::
\tsetobjectxyperm 1, 6, 5
\tsetvar VAR_TEMP_1, 0
\tend

{q}_OnFrame::
\tmap_script_2 VAR_TEMP_1, 0, {q}_Record
\t.2byte 0

{q}_Record::
\tsetvar VAR_TEMP_1, 1
\tlockall
\tcall TYHoennLeague_CheckBadges
\tgoto_if_eq VAR_RESULT, FALSE, TYHoennLeague_InvalidEntry
\tgoto_if_ne VAR_HOENN_LEAGUE_PROGRESS, 6, TYHoennLeague_InvalidEntry
{prior}\tmsgbox {q}_Welcome
\tsetflag FLAG_HOENN_LEAGUE_CLEAR
\tsetvar VAR_HOENN_LEAGUE_PROGRESS, 7
\tsetrespawn HEAL_LOCATION_HOENN_EVER_GRANDE_CITY_POKEMON_LEAGUE
\tfadescreen FADE_TO_BLACK
\tspecial EnterHallOfFame
\twaitstate
\tend

{q}_Greeting::
\tmsgbox {q}_Welcome, MSGBOX_NPC
\tend
''')
patch(H,'text.inc',text(q+'_Welcome',["WALLACE: Welcome to HOENN's",'HALL OF FAME!','From KANTO to these far shores,','your partners stood beside you.','We will record this team and','this victory for all time!']))
done(H)
# Native region-specific credits: existing heap filler; no static RAM growth.
c=R/'src/credits.c'
replace(c,'#include "constants/sound.h"','#include "constants/sound.h"\n#include "constants/songs.h"\n#include "sound.h"')
replace(c,'    CREDITSSCENE_TERMINATE,','    CREDITSSCENE_TERMINATE,\n    CREDITSSCENE_HOENN_INIT,\n    CREDITSSCENE_HOENN_PROLOGUE,')
replace(c,'static void LoadPlayerOrRivalSprite(u8 a0);','static void LoadPlayerOrRivalSprite(u8 a0);\nstatic u16 GetCreditsMonSpecies(u8 whichMon);')
scenes=['SlateportCity','Route101','LittlerootTown_ProfessorBirchsLab','MauvilleCity','MtChimney','Route119_WeatherInstitute_2F','SeafloorCavern_Room9','SkyPillar_Top','SootopolisCity','EverGrandeCity','EverGrandeCity_ChampionsRoom','EverGrandeCity_HallOfFame','SlateportCity']
layouts={d['id']:d for d in json.loads((R/'data/layouts/layouts.json').read_text())['layouts'] if d.get('id')}
block='\n/* THYL_LEAGUE_V1: existing native maps and pictures; no movie raster. */\n';cameras=[]
for i,name in enumerate(scenes):
 m=json.loads((R/'data/maps'/name/'map.json').read_text());l=layouts[m['layout']]
 w,h=int(l['width']),int(l['height']);x=w//2;y=max(0,min(h-1,h-6));distance=min(160,max(0,(h-12)*16))
 if h<12:y=h//2
 block+=f'''static const struct CreditsOverworldCmd sHoennCreditsScene{i}[] = {{
    CREDITSOVWLDLOADMAP({m['id']}, {x}, {y}, 1),
    CREDITSOVWLDSCROLL(0, {-1 if distance else 0}, {distance if distance else 1}),
    CREDITSOVWLDEND,
}};
'''
 cameras.append({'map':name,'x':x,'y':y,'pan_steps':distance})
block+='static const struct CreditsOverworldCmd *const sHoennOverworldMapScenes[] = {\n'+''.join(f'    sHoennCreditsScene{i},\n' for i in range(13))+'};\n'
block+='static const u8 sHoennCreditsTitle[] = _("POK챕MON THUNDER YELLOW\\nHOENN STAFF");\n'
replace(c,'static const struct CreditsTextHeader sCreditsTexts[] = {',block+'\nstatic const struct CreditsTextHeader sCreditsTexts[] = {')
replace(c,'''void DoCredits(void)
{
    sCreditsMgr = AllocZeroed(sizeof(*sCreditsMgr));
    ResetTasks();
    sCreditsMgr->taskId = TASK_NONE;
    sCreditsMgr->unk_1D = 0;
    ResetSpriteData();
    SetMainCallback2(CB2_Credits);
}''','''static void StartRegionalCredits(u8 region)
{
    sCreditsMgr = AllocZeroed(sizeof(*sCreditsMgr));
    ResetTasks();
    sCreditsMgr->taskId = TASK_NONE;
    sCreditsMgr->unk_1D = 0;
    sCreditsMgr->filler_10[0] = region;
    if (region == 2)
        sCreditsMgr->mainseqno = CREDITSSCENE_HOENN_INIT;
    ResetSpriteData();
    SetMainCallback2(CB2_Credits);
}

void DoCredits(void)
{
    StartRegionalCredits(0);
}

void DoHoennCredits(void)
{
    StartRegionalCredits(2);
}''')
replace(c,'sOverworldMapScenes[sCreditsMgr->whichMon], QL_TINT_NONE)','(sCreditsMgr->filler_10[0] == 2 ? sHoennOverworldMapScenes : sOverworldMapScenes)[sCreditsMgr->whichMon], QL_TINT_NONE)')
replace(c,'    case CREDITSSCENE_INIT_WIN0:\n','''    case CREDITSSCENE_HOENN_INIT:
        if (!DoOverworldMapScrollScene(0))
            return 0;
        PlayBGM(MUS_CREDITS);
        LoadPlayerOrRivalSprite(0);
        sCreditsMgr->timer = 1440;
        sCreditsMgr->mainseqno = CREDITSSCENE_HOENN_PROLOGUE;
        return 1;
    case CREDITSSCENE_HOENN_PROLOGUE:
        if (sCreditsMgr->timer != 0)
        {
            sCreditsMgr->timer--;
            return 1;
        }
        SetGpuReg(REG_OFFSET_WIN0V, WIN_RANGE(DISPLAY_HEIGHT / 2 - 1, DISPLAY_HEIGHT / 2 + 1));
        sCreditsMgr->mainseqno = CREDITSSCENE_OPEN_WIN0;
        return 0;
    case CREDITSSCENE_INIT_WIN0:
''')
replace(c,'sTextColor_Header, 0, TITLE_TEXT);','sTextColor_Header, 0, sCreditsMgr->filler_10[0] == 2 ? sHoennCreditsTitle : TITLE_TEXT);')
replace(c,'''static void LoadCreditsMonPic(u8 whichMon)
{
    switch (whichMon)''','''static void LoadCreditsMonPic(u8 whichMon)
{
    if (sCreditsMgr->filler_10[0] == 2)
    {
        InitWindows(sWindowTemplates_Pikachu);
        FillWindowPixelBuffer(0, PIXEL_FILL(0));
        FillWindowPixelBuffer(1, PIXEL_FILL(0));
        FillWindowPixelBuffer(2, PIXEL_FILL(0));
        LoadMonPicInWindow(GetCreditsMonSpecies(whichMon), SHINY_ODDS, 0, TRUE, 10, 0);
        CopyWindowToVram(0, COPYWIN_GFX);
        CopyWindowToVram(1, COPYWIN_GFX);
        CopyWindowToVram(2, COPYWIN_GFX);
        return;
    }
    switch (whichMon)''')
replace(c,'''static u16 GetCreditsMonSpecies(u8 whichMon)
{
    switch (whichMon)''','''static u16 GetCreditsMonSpecies(u8 whichMon)
{
    if (sCreditsMgr->filler_10[0] == 2)
    {
        static const u16 species[] = {SPECIES_BLAZIKEN, SPECIES_SCEPTILE, SPECIES_SWAMPERT, SPECIES_RAYQUAZA};
        return whichMon < ARRAY_COUNT(species) ? species[whichMon] : SPECIES_NONE;
    }
    switch (whichMon)''')
replace(c,'''                PutWindowTilemap(sCreditsMgr->unk_0E);
                CopyBgTilemapBufferToVram(0);''','''                if (sCreditsMgr->filler_10[0] != 2)
                {
                    PutWindowTilemap(sCreditsMgr->unk_0E);
                    CopyBgTilemapBufferToVram(0);
                }''')
header=R/'include/credits.h'
replace(header,'extern bool8 gHasHallOfFameRecords;','extern bool8 gHasHallOfFameRecords;\nvoid DoHoennCredits(void);')
hof=R/'src/hall_of_fame.c'
replace(hof,'static void SetWarpsToRollCredits(void)\n{','''static void SetWarpsToRollCredits(void)
{
    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_EVER_GRANDE_CITY_HALL_OF_FAME)
     && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_EVER_GRANDE_CITY_HALL_OF_FAME))
    {
        DoHoennCredits();
        return;
    }
''')
post=R/'src/post_battle_event_funcs.c'
if '#include "constants/maps.h"' not in read(post):replace(post,'#include "constants/items.h"','#include "constants/items.h"\n#include "constants/maps.h"')
replace(post,'    SetContinueGameWarpToHealLocation(HEAL_LOCATION_PALLET_TOWN);','''    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_EVER_GRANDE_CITY_HALL_OF_FAME)
     && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_EVER_GRANDE_CITY_HALL_OF_FAME))
        SetContinueGameWarpToHealLocation(HEAL_LOCATION_HOENN_EVER_GRANDE_CITY_POKEMON_LEAGUE);
    else
        SetContinueGameWarpToHealLocation(HEAL_LOCATION_PALLET_TOWN);''')
# All source anchors resolved before any write. Back up source and generated files.
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=R/'work/hoenn-league-v1-backups'/stamp
assert not backup.exists();backup.mkdir(parents=True)
oldfiles=set(pending)
for name in maps:
 for k in ['map.json','scripts.inc','text.inc']:oldfiles.add(R/'data/maps'/name/k)
evidence={}
for f in sorted(oldfiles):
 rel=str(f.relative_to(R))
 if f.exists():
  raw=f.read_bytes();dest=backup/f.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
  evidence[rel]=hashlib.sha256(raw).hexdigest()
 else:evidence[rel]=None
(backup/'manifest.json').write_text(json.dumps({'before':evidence,'maps':maps,'cameras_need_review':cameras,'save_abi_changed':False,'status':'candidate-not-built'},indent=2)+'\n')
for p,s in pending.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
subprocess.run(['python3','tools/hoenn_import/apply_patches.py',*maps],cwd=R,check=True)
print(json.dumps({'backup':str(backup),'maps':maps,'source_files':len(pending),'status':'source-candidate-needs-build-and-runtime-QA'},indent=2))
