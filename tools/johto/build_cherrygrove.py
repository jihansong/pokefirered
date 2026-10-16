#!/usr/bin/env python3
"""Append Cherrygrove services/Route 30 and Elm's research follow-up.
No save-layout changes. Dry run by default; --apply backs up every changed file.
"""
import argparse, copy, datetime, hashlib, json, re, struct, subprocess
from collections import deque
from pathlib import Path

OLD = ['JohtoCherrygroveAirstrip','JohtoRoute29','NewBarkTown',
       'NewBarkTown_ElmsLab','NewBarkTown_RestHouse','NewBarkTown_NeighborsHouse']
NEW = ['CherrygroveCity','CherrygroveCity_PokemonCenter_1F',
       'CherrygroveCity_PokemonCenter_2F','CherrygroveCity_Mart',
       'CherrygroveCity_GuideHouse','JohtoRoute30','JohtoRoute30_MrPokemonsHouse']
IDS = ['CHERRYGROVE_CITY','CHERRYGROVE_CITY_POKEMON_CENTER_1F',
       'CHERRYGROVE_CITY_POKEMON_CENTER_2F','CHERRYGROVE_CITY_MART',
       'CHERRYGROVE_CITY_GUIDE_HOUSE','JOHTO_ROUTE30','JOHTO_ROUTE30_MR_POKEMONS_HOUSE']
MID = dict(zip(NEW, ['MAP_'+s for s in IDS]))
FLAGS = ['FLAG_JOHTO_MET_CHERRYGROVE_GUIDE',
         'FLAG_JOHTO_MR_POKEMON_BRIEFED','FLAG_JOHTO_ELM_REPORT_DELIVERED']
MARK = '@ JOHTO_CHERRYGROVE_ROUTE30_V1'
def enc(v):
    return (json.dumps(v, ensure_ascii=False, indent=2)+'\n').encode()
def sha(b): return hashlib.sha256(b).hexdigest()
class Source:
    def __init__(self, root, overlay=None):
        self.root = Path(root); self.overlay = overlay or {}; self.used = {}
    def read(self, name):
        if name in self.overlay: b=self.overlay[name]
        else: b=(self.root/name).read_bytes()
        self.used[name]=b
        return b
    def text(self,name): return self.read(name).decode('utf-8')
    def json(self,name): return json.loads(self.read(name))
    def exists(self,name): return name in self.overlay or (self.root/name).exists()
def once(text,old,new,label):
    if new in text:
        assert text.count(new)==1, label+' repeated new anchor'
        return text
    assert text.count(old)==1, label+' expected exactly one original anchor'
    return text.replace(old,new,1)
def obj(gfx,x,y,script,elevation=3,movement='FACE_DOWN',local_id=None):
    v={'type':'object','graphics_id':'OBJ_EVENT_GFX_'+gfx,'x':x,'y':y,
       'elevation':elevation,'movement_type':'MOVEMENT_TYPE_'+movement,
       'movement_range_x':0,'movement_range_y':0,
       'trainer_type':'TRAINER_TYPE_NONE','trainer_sight_or_berry_tree_id':'0',
       'script':script,'flag':'0'}
    if local_id: v['local_id']=local_id
    return v
def warp(x,y,dest,wid,elevation=3):
    return {'x':x,'y':y,'elevation':elevation,'dest_map':MID.get(dest,dest),
            'dest_warp_id':str(wid)}
def bg(x,y,script):
    return {'type':'sign','x':x,'y':y,'elevation':0,
            'player_facing_dir':'BG_EVENT_PLAYER_FACING_ANY','script':script}
def npc_script(name, key, text=None):
    return name+'_'+key+'::\n    msgbox '+name+'_Text_'+(text or key)+', MSGBOX_NPC\n    end\n'
def texts(name, rows):
    s=''
    for key, paras in rows.items():
        s+=name+'_Text_'+key+'::\n'
        for pi,p in enumerate(paras):
            lines=p.split('\n')
            for li,line in enumerate(lines):
                assert len(line)<=32, (name,key,line)
                end='$' if pi==len(paras)-1 and li==len(lines)-1 else ('\\p' if li==len(lines)-1 else '\\n')
                s+='    .string "'+line.replace('"','\\"')+end+'"\n'
        s+='\n'
    return s
def fill(a,x0,y0,x1,y1,v):
    for y in range(y0,y1):
        for x in range(x0,x1): a[y][x]=v(x,y) if callable(v) else v
def paste(a,b,x,y):
    for j,row in enumerate(b):
        for i,v in enumerate(row): a[y+j][x+i]=v
def dense(x,y): return (0x0414,0x0415,0x041c,0x041d)[(y%2)*2+x%2]
def grass(x,y): return (0x300a,0x300b,0x300c,0x300d)[(y%2)*2+x%2]
def pack(a): return struct.pack('<'+'H'*sum(map(len,a)),*(v for row in a for v in row))
def layouts(s):
    ls=s.json('data/layouts/layouts.json')['layouts']
    l=next(x for x in ls if x.get('id')=='LAYOUT_VIRIDIAN_CITY')
    sv=struct.unpack('<'+'H'*(l['width']*l['height']),s.read(l['blockdata_filepath']))
    def crop(x,y,w,h): return [[sv[(y+j)*l['width']+x+i] for i in range(w)] for j in range(h)]
    a=[[0x3001]*36 for _ in range(28)]
    fill(a,0,0,7,28,0x01d9);fill(a,7,0,8,28,0x112c);fill(a,8,0,10,28,0x3115);fill(a,10,0,11,28,0x31df)
    fill(a,11,0,36,3,dense);fill(a,11,24,36,28,dense);fill(a,34,0,36,28,dense)
    fill(a,11,12,34,16,0x3195);fill(a,18,0,22,16,0x3195)
    fill(a,23,3,30,10,0x3195);fill(a,25,9,28,16,0x3195)
    fill(a,11,17,18,23,0x3195);fill(a,12,15,15,23,0x3195)
    fill(a,25,17,32,23,0x3195);fill(a,27,15,30,23,0x3195)
    fill(a,22,15,25,28,0x3195)
    paste(a,crop(24,22,5,5),24,4);paste(a,crop(34,16,4,4),26,18);paste(a,crop(24,8,5,4),12,18)
    for x,y in [(12,5),(13,5),(12,6),(13,6),(31,5),(32,5),(31,6),(32,6),(29,23),(30,23)]: a[y][x]=0x3004
    for x,y in [(32,17),(16,21),(22,8)]: a[y][x]=0x0403
    b=[[0x3001]*24 for _ in range(48)]
    fill(b,0,0,24,3,dense);fill(b,0,0,2,48,dense);fill(b,22,0,24,48,dense)
    fill(b,2,33,6,35,dense);fill(b,10,33,22,35,dense)
    fill(b,2,19,14,21,dense);fill(b,18,19,22,21,dense)
    fill(b,2,9,11,11,dense);fill(b,15,9,22,11,dense)
    fill(b,11,36,18,41,grass);fill(b,7,23,11,29,grass);fill(b,15,12,20,18,grass)
    fill(b,0,46,24,48,dense);fill(b,6,45,10,48,0x3001)
    paste(b,crop(24,8,5,4),14,3)
    paste(b,crop(11,26,6,6),2,12);paste(b,crop(11,26,6,6),15,25)
    for x,y in [(3,5),(4,5),(3,6),(4,6),(18,31),(19,31)]: b[y][x]=0x3004
    b[44][10]=0x0403;b[8][13]=0x0403
    return {'CherrygroveCity':a,'JohtoRoute30':b}


def events():
    scripts={}; tx={}
    n='CherrygroveCity'
    scripts[n]=n+'_MapScripts::\n    .byte 0\n\n'+r'''
CherrygroveCity_Guide::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_MET_LAB_ASSISTANT, CherrygroveCity_GuideBeforeLab
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, CherrygroveCity_GuideReportDone
    goto_if_set FLAG_JOHTO_MET_CHERRYGROVE_GUIDE, CherrygroveCity_GuideAgain
    msgbox CherrygroveCity_Text_GuideRequest
    setflag FLAG_JOHTO_MET_CHERRYGROVE_GUIDE
    release
    end
CherrygroveCity_GuideBeforeLab::
    msgbox CherrygroveCity_Text_GuideBeforeLab
    release
    end
CherrygroveCity_GuideAgain::
    msgbox CherrygroveCity_Text_GuideAgain
    release
    end
CherrygroveCity_GuideReportDone::
    msgbox CherrygroveCity_Text_GuideReportDone
    release
    end
'''
    for key in ['Girl','Fisher','CenterSign','MartSign','GuideSign']:
        scripts[n]+='\n'+npc_script(n,key)
    tx[n]=texts(n,{
      'GuideRequest':['Welcome to CHERRYGROVE!\nYou are helping ELM, are you?',
                      'MR. POKEMON has a research\nreport for his lab.',
                      'His house is on ROUTE 30,\nnorth of town.',
                      'The red roof is our CENTER.\nStock up at the blue MART.'],
      'GuideBeforeLab':['Welcome! The airstrip is south,\nand ROUTE 30 is north.',
                        'If you came to help ELM,\nfollow ROUTE 29 east.',
                        'His lab is in NEW BARK TOWN.\nVisit his research team first.'],
      'GuideAgain':['Follow ROUTE 30 north to\nMR. POKEMON on the hill.',
                    'Take his report back to ELM\nin NEW BARK TOWN.'],
      'GuideReportDone':['You brought the report to ELM!\nThanks for helping our region.',
                         'Keep comparing your POKEDEX\nas you explore JOHTO.'],
      'Girl':['From the airstrip, ROUTE 29\nleads east to NEW BARK TOWN.',
              'CHERRYGROVE is the town just\nnorth of the airstrip.'],
      'Fisher':['The sea links our regions.\nTrainers arrive from KANTO.',
                'Even familiar POKEMON can\nlive differently in JOHTO.'],
      'CenterSign':['POKEMON CENTER\nRest and recover here.'],
      'MartSign':['POKEMON MART\nTravel supplies sold here.'],
      'GuideSign':['THE GUIDE GENT LIVES HERE.']
    })
    n='CherrygroveCity_PokemonCenter_1F'
    scripts[n]=n+'_MapScripts::\n    map_script MAP_SCRIPT_ON_TRANSITION, '+n+'_OnTransition\n    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume\n    .byte 0\n\n'+n+'_OnTransition::\n    setrespawn HEAL_LOCATION_CHERRYGROVE_CITY\n    end\n\n'+n+'_Nurse::\n    lock\n    faceplayer\n    call EventScript_PkmnCenterNurse\n    release\n    end\n\n'
    for key in ['Traveler','Hiker']: scripts[n]+=npc_script(n,key)+'\n'
    tx[n]=texts(n,{'Traveler':['Your team can rest here before\nthe walk to NEW BARK TOWN.'],
                  'Hiker':['Different POKEMON appear on\nthe routes after sunset.',
                           'Keep your POKEDEX handy!']})
    n='CherrygroveCity_PokemonCenter_2F'
    scripts[n]=n+'_MapScripts::\n    map_script MAP_SCRIPT_ON_FRAME_TABLE, CableClub_OnFrame\n    map_script MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE, CableClub_OnWarp\n    map_script MAP_SCRIPT_ON_LOAD, CableClub_OnLoad\n    map_script MAP_SCRIPT_ON_TRANSITION, CableClub_OnTransition\n    .byte 0\n'
    tx[n]='@ Shared Cable Club dialogue.\n'
    n='CherrygroveCity_Mart'
    scripts[n]=n+'_MapScripts::\n    .byte 0\n\n'+r'''
CherrygroveCity_Mart_Clerk::
    goto_if_questlog EventScript_ReleaseEnd
    lock
    faceplayer
    message Text_MayIHelpYou
    waitmessage
    pokemart CherrygroveCity_Mart_Items
    msgbox Text_PleaseComeAgain
    release
    end

    .align 2
CherrygroveCity_Mart_Items::
    .2byte ITEM_POKE_BALL
    .2byte ITEM_GREAT_BALL
    .2byte ITEM_SUPER_POTION
    .2byte ITEM_ANTIDOTE
    .2byte ITEM_PARALYZE_HEAL
    .2byte ITEM_AWAKENING
    .2byte ITEM_REPEL
    .2byte ITEM_NONE

'''
    for key in ['Customer','Traveler']: scripts[n]+=npc_script(n,key)+'\n'
    tx[n]=texts(n,{'Customer':['REPEL helps you travel through\ngrass without interruptions.'],
                  'Traveler':['I keep supplies for the trip\nback to the airstrip.']})
    n='CherrygroveCity_GuideHouse'
    scripts[n]=n+'_MapScripts::\n    .byte 0\n\n'+npc_script(n,'Resident')
    tx[n]=texts(n,{'Resident':['The GUIDE GENT is outside,\nhelping visitors find their way.',
                              'MR. POKEMON lives north of here.\nHe and ELM share their research.']})
    n='JohtoRoute30'
    scripts[n]=n+'_MapScripts::\n    .byte 0\n\n'
    for key in ['Youngster','Fisher','RouteSign','HouseSign']:
        scripts[n]+=npc_script(n,key)+'\n'
    tx[n]=texts(n,{'Youngster':['I watch the grass in daylight\nand listen for birds at night.',
                               'That is how I find POKEMON\nI missed on earlier walks.'],
                  'Fisher':['MR. POKEMON studies unusual\nfinds from across the regions.',
                             'His house is up on the hill.'],
                  'RouteSign':['ROUTE 30\nSouth: CHERRYGROVE CITY'],
                  'HouseSign':["MR. POKEMON'S HOUSE"]})
    n='JohtoRoute30_MrPokemonsHouse'
    scripts[n]=n+'_MapScripts::\n    .byte 0\n\n'+r'''
JohtoRoute30_MrPokemonsHouse_Researcher::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_MET_CHERRYGROVE_GUIDE, JohtoRoute30_MrPokemonsHouse_BeforeReferral
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, JohtoRoute30_MrPokemonsHouse_AfterReport
    goto_if_set FLAG_JOHTO_MR_POKEMON_BRIEFED, JohtoRoute30_MrPokemonsHouse_Repeat
    msgbox JohtoRoute30_MrPokemonsHouse_Text_ResearchReport
    setflag FLAG_JOHTO_MR_POKEMON_BRIEFED
    release
    end
JohtoRoute30_MrPokemonsHouse_BeforeReferral::
    msgbox JohtoRoute30_MrPokemonsHouse_Text_BeforeReferral
    release
    end
JohtoRoute30_MrPokemonsHouse_Repeat::
    msgbox JohtoRoute30_MrPokemonsHouse_Text_Repeat
    release
    end
JohtoRoute30_MrPokemonsHouse_AfterReport::
    msgbox JohtoRoute30_MrPokemonsHouse_Text_AfterReport
    release
    end
JohtoRoute30_MrPokemonsHouse_OaksAide::
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, JohtoRoute30_MrPokemonsHouse_AideAfterReport
    msgbox JohtoRoute30_MrPokemonsHouse_Text_OaksAide
    release
    end
JohtoRoute30_MrPokemonsHouse_AideAfterReport::
    msgbox JohtoRoute30_MrPokemonsHouse_Text_AideAfterReport
    release
    end
'''
    tx[n]=texts(n,{
      'BeforeReferral':['Welcome! I am MR. POKEMON.\nI am preparing a report for ELM.',
                        'Speak with the GUIDE GENT in\nCHERRYGROVE about helping out.'],
      'ResearchReport':['You are the visitor helping ELM!\nThe GUIDE GENT sent you, then.',
                        'A POKEMON EGG found in JOHTO\ncan teach us something new.',
                        'I will keep the EGG safe here.\nPlease take my notes to ELM.',
                        'His lab team can compare them\nwith the records from KANTO.',
                        'Tell his assistant in NEW BARK\nthat my report is ready.'],
      'Repeat':['My report is ready for ELM.\nSpeak with his lab assistant.',
                'The EGG stays here for study.\nThank you for carrying the news.'],
      'AfterReport':['ELM received the report!\nOur research can move forward.',
                     'Records from different regions\nhelp us understand POKEMON.'],
      'OaksAide':['PROF. OAK sent me from KANTO\nto compare research with ELM.',
                  'PROF. BIRCH is studying POKEMON\nin HOENN as well.',
                  'A region changes the order of\nits POKEDEX, not your records.'],
      'AideAfterReport':['Thank you for linking our work!\nOAK will be glad to hear of it.',
                        'Your discoveries stay with you\nwhen another region is unlocked.']
    })
    return scripts,tx
ELM_FOLLOWUP=r'''
@ JOHTO_CHERRYGROVE_ROUTE30_V1
NewBarkTown_ElmsLab_ResearchFollowup::
    goto_if_unset FLAG_JOHTO_MR_POKEMON_BRIEFED, NewBarkTown_ElmsLab_ResearchFollowupEnd
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, NewBarkTown_ElmsLab_ResearchFollowupEnd
    msgbox NewBarkTown_ElmsLab_Text_ResearchReportDelivered
    setflag FLAG_JOHTO_ELM_REPORT_DELIVERED
NewBarkTown_ElmsLab_ResearchFollowupEnd::
    return
'''
ELM_TEXT=texts('NewBarkTown_ElmsLab',{
 'ResearchReportDelivered':['MR. POKEMON has new findings?\nThanks for bringing his report.',
                            'I will send these notes to ELM.\nThey add to the KANTO records.',
                            'OAK and BIRCH can compare their\nregional research with ours.',
                            'The GUIDE GENT can help you\ncontinue exploring JOHTO.']})


def patch_shared(s,out,scripts,tx):
    fp='include/constants/flags_johto_story.h'
    h=s.text(fp)
    block='\n// Cherrygrove / Route 30 research steps. Reserved Johto story bits.\n'+''.join(
        '#define '+name+' (JOHTO_STORY_FLAGS_START + '+str(i+2)+')\n' for i,name in enumerate(FLAGS))
    if block not in h:
        assert not any(re.search(r'^\s*#define\s+'+n+r'\b',h,re.M) for n in FLAGS), 'flag already defined'
        used=[int(x,0) for x in re.findall(r'JOHTO_STORY_FLAGS_START\s*\+\s*(0x[0-9a-fA-F]+|\d+)',h)]
        assert not set(used)&{2,3,4}, 'reserved story bits already used'
        idx=h.rfind('#endif');assert idx>=0, 'missing header guard'
        h=h[:idx]+block+'\n'+h[idx:]
    out[fp]=h.encode()
    # Carry the report independently of the existing Cyndaquil gift choices.
    # The original gift, capacity failure, refusal and already-received paths remain intact.
    sp='tools/johto/patches/NewBarkTown_ElmsLab/scripts.inc'
    tp='tools/johto/patches/NewBarkTown_ElmsLab/text.inc'
    old=s.text(sp)
    anchor='    setflag FLAG_JOHTO_MET_LAB_ASSISTANT\n'
    new=anchor+'    call NewBarkTown_ElmsLab_ResearchFollowup\n'
    st=once(old,anchor,new,'Elm research call')
    if MARK not in st:st=st.rstrip()+'\n'+ELM_FOLLOWUP
    else:assert ELM_FOLLOWUP.strip() in st, 'changed Elm followup'
    tt=s.text(tp)
    if 'NewBarkTown_ElmsLab_Text_ResearchReportDelivered::' not in tt:tt=tt.rstrip()+'\n\n'+ELM_TEXT
    else:assert ELM_TEXT.strip() in tt, 'changed Elm report text'
    for canonical,generated,value in [
        (sp,'data/maps/NewBarkTown_ElmsLab/scripts.inc',st),
        (tp,'data/maps/NewBarkTown_ElmsLab/text.inc',tt)]:
        current=s.text(generated)
        assert current in (s.text(canonical),value), 'generated Elm diverges from canonical '+generated
        out[canonical]=value.encode();out[generated]=value.encode()
    # Existing generator must refuse to rebuild the old six-map layout over this extension.
    gp='tools/johto/build_entry.py';g=s.text(gp)
    guard='    # CHERRYGROVE_EXTENSION_GUARD\n    _jg = json.loads((r / "data/maps/map_groups.json").read_bytes()).get("gMapGroup_JohtoEntry", [])\n    if any(_name not in NAMES for _name in _jg):\n        raise RuntimeError("Johto has additional maps; use tools/johto/build_cherrygrove.py; do not overwrite the extension")\n'
    if '# CHERRYGROVE_EXTENSION_GUARD' not in g:
        g,n=re.subn(r'(?m)^(def build\(r\):\s*\n)',lambda m:m.group(1)+guard,g)
        assert n==1, 'unexpected build_entry build(r) definition'
    else:assert guard in g, 'different entry regeneration guard'
    out[gp]=g.encode()
    ep='data/event_scripts.s';e=s.text(ep)
    includes=MARK+'\n'+''.join('    .include "data/maps/'+n+'/'+f+'"\n' for n in NEW for f in ('scripts.inc','text.inc'))
    if MARK not in e:
        assert not any('data/maps/'+n+'/' in e for n in NEW), 'partial new script includes'
        e=e.rstrip()+'\n\n'+includes
    else:assert includes in e, 'new scripts include block differs'
    out[ep]=e.encode()
    # Time-of-day schema matches the verified Route 29 canonical entry.
    day=['CATERPIE','PIDGEY','WEEDLE','SENTRET','CATERPIE','PIDGEY','WEEDLE','SENTRET','RATTATA','HOPPIP','METAPOD','KAKUNA']
    night=['HOOTHOOT','SPINARAK','RATTATA','HOOTHOOT','SPINARAK','HOOTHOOT','RATTATA','HOOTHOOT','RATTATA','SPINARAK','POLIWAG','ZUBAT']
    levels=[3,3,3,3,4,4,4,4,3,4,5,5]
    entry={'map':'MAP_JOHTO_ROUTE30','base_label':'sJohtoRoute30'}
    for field,species in [('land_mons',day),('land_mons_morning',day),('land_mons_night',night)]:
        entry[field]={'encounter_rate':10,'mons':[{'min_level':lv,'max_level':lv,'species':'SPECIES_'+mon} for mon,lv in zip(species,levels)]}
    r29=s.json('tools/johto/route29_wild.json')
    assert set(r29)==set(entry), 'Route 29 canonical wild schema changed'
    for field in ('land_mons','land_mons_morning','land_mons_night'):
        assert set(r29[field])=={'encounter_rate','mons'} and len(r29[field]['mons'])==12
        assert set(r29[field]['mons'][0])=={'min_level','max_level','species'}
    out['tools/johto/route30_wild.json']=enc(entry)
    wp='src/data/wild_encounters.json';w=s.json(wp)
    wg=[g for g in w['wild_encounter_groups'] if g['label']=='gWildMonHeaders']
    assert len(wg)==1 and wg[0]['for_maps'] is True
    rows=wg[0]['encounters'];hits=[i for i,x in enumerate(rows) if x['map']==entry['map'] or x['base_label']==entry['base_label']]
    assert len(hits)<=1, 'duplicate Route 30 encounter entry'
    if hits:
        assert rows[hits[0]]==entry, 'existing Route 30 wild data differs'
    else:rows.append(entry)
    out[wp]=enc(w)


def replace_function(text,name,new,label):
    # All targeted definitions are top-level C functions; leave prototypes alone.
    pat=r'(?ms)^(?:static\s+)?(?:void|bool8|u32|u8|s32)\s+'+re.escape(name)+r'\([^;{}]*\)\s*\{.*?^\}'
    hits=list(re.finditer(pat,text))
    assert len(hits)==1, (label,'function match',len(hits))
    m=hits[0];return text[:m.start()]+new.rstrip()+text[m.end():]
def patch_areas(s,out):
    for p in ('src/pokemon_summary_screen.c','src/region_map.c'):
        t=s.text(p)
        pat=r'(MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP[\s\S]{0,120}?<=\s*)MAPSEC_NEW_BARK_TOWN'
        if re.search(pat,t):t,n=re.subn(pat,lambda m:m.group(1)+'MAPSEC_JOHTO_ROUTE30',t);assert n==1,(p,'Johto range matches',n)
        else:assert re.search(r'MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP[\s\S]{0,120}?<=\s*MAPSEC_JOHTO_ROUTE30',t),(p,'no known Johto range')
        out[p]=t.encode()
    p='src/pokedex_screen.c';t=s.text(p)
    declarations='static const u8 sText_JohtoCherrygrove[] = _("CHERRYGROVE");\nstatic const u8 sText_JohtoRoute30[] = _("ROUTE 30");\n'
    if 'sText_JohtoCherrygrove[]' not in t:
        pattern=r'(?m)^(static const u8 sText_JohtoNewBark\[\]\s*=\s*_\("NEW BARK"\);\s*\n)'
        t,n=re.subn(pattern,lambda m:m.group(1)+declarations,t);assert n==1,'Johto area labels'
    else:assert declarations.strip() in t
    new=r'''static void DexScreen_DrawJohtoEntryArea(u8 windowId)
{
    FillWindowPixelBuffer(windowId, PIXEL_FILL(2));
    FillWindowPixelRect(windowId, PIXEL_FILL(6), 3, 3, 122, 66);
    // Airport -> Route 29 -> New Bark; north to Cherrygrove and Route 30.
    FillWindowPixelRect(windowId, PIXEL_FILL(3), 24, 42, 80, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 24, 44, 80, 4);
    FillWindowPixelRect(windowId, PIXEL_FILL(3), 20, 8, 8, 38);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 22, 8, 4, 38);
    FillWindowPixelRect(windowId, PIXEL_FILL(2), 20, 42, 8, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 22, 44, 4, 4);
    FillWindowPixelRect(windowId, PIXEL_FILL(2), 20, 25, 8, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 22, 27, 4, 4);
    FillWindowPixelRect(windowId, PIXEL_FILL(2), 100, 42, 8, 8);
    FillWindowPixelRect(windowId, PIXEL_FILL(5), 102, 44, 4, 4);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoRoute30, 34, 4, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoCherrygrove, 34, 22, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoRoute29, 47, 35, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoAirstrip, 5, 54, 0);
    DexScreen_AddTextPrinterParameterized(windowId, FONT_SMALL, sText_JohtoNewBark, 80, 54, 0);
}'''
    t=replace_function(t,'DexScreen_DrawJohtoEntryArea',new,'Johto habitat page')
    out[p]=t.encode()
    p='src/wild_pokemon_area.c';t=s.text(p)
    if not re.search(r'bool8\s+johtoRoute30\s*;',t):
        t,n=re.subn(r'(bool8\s+johtoRoute29\s*;)',r'\1\n    bool8 johtoRoute30;',t)
        assert n==1,'habitat struct member'
    # Both routes are handled before the Hoenn/Kanto area classifiers.
    if 'MAP_GROUP(MAP_JOHTO_ROUTE30)' not in t:
        pat=r'(?s)(if\s*\(header->mapGroup\s*==\s*MAP_GROUP\(MAP_JOHTO_ROUTE29\)\s*&&\s*header->mapNum\s*==\s*MAP_NUM\(MAP_JOHTO_ROUTE29\)\s*\)\s*\{\s*habitats->johtoRoute29\s*=\s*TRUE;\s*continue;\s*\})'
        def add_route(m):
            return m.group(1)+'\n            '+m.group(1).replace('MAP_JOHTO_ROUTE29','MAP_JOHTO_ROUTE30').replace('johtoRoute29','johtoRoute30')
        t,n=re.subn(pat,add_route,t);assert n==1,('habitat route classifier',n)
    t,n=re.subn(r'if\s*\(habitats\.johtoRoute29\)\s*(regions\s*\|=\s*1\s*<<\s*DEX_AREA_REGION_JOHTO;)',
                r'if (habitats.johtoRoute29 || habitats.johtoRoute30)\n        \1',t)
    if n==0:assert re.search(r'if\s*\(habitats\.johtoRoute29\s*\|\|\s*habitats\.johtoRoute30\)',t)
    else:assert n==1
    if 'GetJohtoRoute30AreaMarkerSubsprite(areaCount++, subsprites);' not in t:
        pat=r'(if\s*\(habitats\.johtoRoute29\)\s*GetJohtoRoute29AreaMarkerSubsprite\(areaCount\+\+,\s*subsprites\);)'
        t,n=re.subn(pat,lambda m:m.group(1)+'\n        if (habitats.johtoRoute30)\n            GetJohtoRoute30AreaMarkerSubsprite(areaCount++, subsprites);',t)
        assert n==1,('Route 30 habitat marker call',n)
    out[p]=t.encode()
    p='include/pokedex_area_markers.h';t=s.text(p)
    decl='void GetJohtoRoute30AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);'
    if 'GetJohtoRoute30AreaMarkerSubsprite' not in t:
        t,n=re.subn(r'(void GetJohtoRoute29AreaMarkerSubsprite\([^;]*;)',lambda m:m.group(1)+'\n'+decl,t)
        assert n==1,'marker prototype'
    out[p]=t.encode()
    p='src/pokedex_area_markers.c';t=s.text(p)
    new=r'''void GetJohtoRoute29AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites)
{
    if (subsprites == NULL)
        return;
    subsprites[i] = sSubsprite_MediumHorizontal;
    subsprites[i].x = 48 + (HOENN_AREA_MAP_LEFT * 8 - 104);
    subsprites[i].y = 38;
}'''
    t=replace_function(t,'GetJohtoRoute29AreaMarkerSubsprite',new,'Route 29 marker')
    new=r'''void GetJohtoRoute30AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites)
{
    if (subsprites == NULL)
        return;
    subsprites[i] = sSubsprite_SmallVertical;
    subsprites[i].x = 20 + (HOENN_AREA_MAP_LEFT * 8 - 104);
    subsprites[i].y = 9;
}'''
    assert 'static const struct Subsprite sSubsprite_SmallVertical' in t
    if 'void GetJohtoRoute30AreaMarkerSubsprite' not in t:t=t.rstrip()+'\n\n'+new+'\n'
    else:t=replace_function(t,'GetJohtoRoute30AreaMarkerSubsprite',new,'Route 30 marker')
    out[p]=t.encode()


def build(s):
    # VIOLET_EXTENSION_GUARD
    _current = s.json("data/maps/map_groups.json")["gMapGroup_JohtoEntry"]
    if any(_n not in OLD + NEW for _n in _current):
        raise RuntimeError("Violet extension exists; use build_violet.py")
    out={}; stats={}
    groups=s.json('data/maps/map_groups.json')
    assert groups['gMapGroup_JohtoEntry'] in [OLD,OLD+NEW], 'unexpected Johto group contents'
    for group,names in groups.items():
        if group not in ('gMapGroup_JohtoEntry','group_order'):
            assert not any(n in names for n in NEW), 'new map name already belongs to another group'
    groups['gMapGroup_JohtoEntry']=OLD+NEW
    out['data/maps/map_groups.json']=enc(groups)
    ls=s.json('data/layouts/layouts.json'); arrays=layouts(s)
    for n in ('CherrygroveCity','JohtoRoute30'):
        a=arrays[n]; ident='LAYOUT_'+IDS[NEW.index(n)]
        item={'id':ident,'name':n+'_Layout','width':len(a[0]),'height':len(a),
              'border_width':2,'border_height':2,'primary_tileset':'gTileset_General',
              'secondary_tileset':'gTileset_ViridianCity',
              'border_filepath':'data/layouts/'+n+'/border.bin',
              'blockdata_filepath':'data/layouts/'+n+'/map.bin'}
        prev=[x for x in ls['layouts'] if x.get('id')==ident]
        assert not prev or prev==[item], 'conflicting layout '+n
        if not prev: ls['layouts'].append(item)
        out[item['blockdata_filepath']]=pack(a)
        out[item['border_filepath']]=struct.pack('<4H',0x414,0x415,0x41c,0x41d)
    out['data/layouts/layouts.json']=enc(ls)
    sec=s.json('src/data/region_map/region_map_sections.json')
    additions=[{'id':'MAPSEC_CHERRYGROVE_CITY','name':'CHERRYGROVE CITY','x':6,'y':7,'width':1,'height':1},
               {'id':'MAPSEC_JOHTO_ROUTE30','name':'ROUTE 30','x':6,'y':4,'width':1,'height':3}]
    for item in additions:
        prev=[x for x in sec['map_sections'] if x['id']==item['id']]
        assert not prev or prev==[item], 'conflicting map section'
        if not prev: sec['map_sections'].append(item)
    out['src/data/region_map/region_map_sections.json']=enc(sec)
    maps={}
    def template(name,source,section,layout=None,music=None):
        j=s.json('data/maps/'+source+'/map.json')
        j.update(id=MID[name],name=name,region_map_section=section)
        if layout:j['layout']=layout
        if music:j['music']=music
        j['connections']=None
        for key in ('object_events','warp_events','coord_events','bg_events'):j[key]=[]
        maps[name]=j;return j
    n='CherrygroveCity'
    j=template(n,'ViridianCity','MAPSEC_CHERRYGROVE_CITY','LAYOUT_CHERRYGROVE_CITY','MUS_PALLET')
    j['connections']=[{'map':'MAP_JOHTO_CHERRYGROVE_AIRSTRIP','direction':'down','offset':0},
                      {'map':MID['JohtoRoute30'],'direction':'up','offset':12}]
    j['object_events']=[obj('OLD_MAN_2',31,14,n+'_Guide'),
                       obj('LITTLE_GIRL',15,9,n+'_Girl'),obj('FISHER',9,20,n+'_Fisher')]
    j['warp_events']=[warp(26,8,'CherrygroveCity_PokemonCenter_1F',1,0),
                      warp(28,21,'CherrygroveCity_Mart',1,0),
                      warp(13,21,'CherrygroveCity_GuideHouse',1,0)]
    j['bg_events']=[bg(22,8,n+'_CenterSign'),bg(32,17,n+'_MartSign'),bg(16,21,n+'_GuideSign')]
    n='CherrygroveCity_PokemonCenter_1F'
    j=template(n,'VermilionCity_PokemonCenter_1F','MAPSEC_CHERRYGROVE_CITY')
    j['object_events']=[obj('NURSE',7,2,n+'_Nurse',local_id='LOCALID_CHERRYGROVE_NURSE'),
                       obj('MAN',4,6,n+'_Traveler'),obj('HIKER',12,5,n+'_Hiker')]
    j['warp_events']=[warp(x,8,'CherrygroveCity',0) for x in (6,7,8)]+[warp(1,6,'CherrygroveCity_PokemonCenter_2F',0,4)]
    n='CherrygroveCity_PokemonCenter_2F'
    original=s.json('data/maps/VermilionCity_PokemonCenter_2F/map.json')
    j=template(n,'VermilionCity_PokemonCenter_2F','MAPSEC_CHERRYGROVE_CITY')
    j['object_events']=copy.deepcopy(original['object_events'])
    j['warp_events']=copy.deepcopy(original['warp_events'])
    j['warp_events'][0]['dest_map']=MID['CherrygroveCity_PokemonCenter_1F']
    n='CherrygroveCity_Mart'
    j=template(n,'VermilionCity_Mart','MAPSEC_CHERRYGROVE_CITY')
    j['object_events']=[obj('CLERK',2,3,n+'_Clerk',0,'FACE_RIGHT'),
                       obj('COOLTRAINER_F',4,2,n+'_Customer',3,'FACE_LEFT'),
                       obj('BALDING_MAN',9,4,n+'_Traveler')]
    j['warp_events']=[warp(x,7,'CherrygroveCity',1) for x in (3,4,5)]
    n='CherrygroveCity_GuideHouse'
    j=template(n,'CeruleanCity_House3','MAPSEC_CHERRYGROVE_CITY','LAYOUT_HOUSE1','MUS_PALLET')
    j['object_events']=[obj('OLD_WOMAN',4,5,n+'_Resident')]
    j['warp_events']=[warp(x,7,'CherrygroveCity',2) for x in (3,4,5)]
    n='JohtoRoute30'
    j=template(n,'Route1','MAPSEC_JOHTO_ROUTE30','LAYOUT_JOHTO_ROUTE30','MUS_ROUTE1')
    j['connections']=[{'map':MID['CherrygroveCity'],'direction':'down','offset':-12}]
    j['object_events']=[obj('YOUNGSTER',5,40,n+'_Youngster'),
                       obj('FISHER',10,15,n+'_Fisher',3,'FACE_LEFT')]
    j['warp_events']=[warp(15,6,'JohtoRoute30_MrPokemonsHouse',1,0)]
    j['bg_events']=[bg(10,44,n+'_RouteSign'),bg(13,8,n+'_HouseSign')]
    n='JohtoRoute30_MrPokemonsHouse'
    j=template(n,'CeruleanCity_House3','MAPSEC_JOHTO_ROUTE30','LAYOUT_HOUSE1','MUS_PALLET')
    j['object_events']=[obj('OLD_MAN_1',4,5,n+'_Researcher'),
                       obj('SCIENTIST',7,5,n+'_OaksAide')]
    j['warp_events']=[warp(x,7,'JohtoRoute30',0) for x in (3,4,5)]
    scripts,tx=events()
    for name,j in maps.items():
        out['data/maps/'+name+'/map.json']=enc(j)
        out['data/maps/'+name+'/scripts.inc']=scripts[name].encode()
        out['data/maps/'+name+'/text.inc']=tx[name].encode()
    airpath='data/maps/JohtoCherrygroveAirstrip/map.json'
    air=s.json(airpath)
    link={'map':MID['CherrygroveCity'],'direction':'up','offset':0}
    ac=air['connections'] or []
    assert not [c for c in ac if c['direction']=='up' and c!=link], 'Airstrip north already used'
    if link not in ac:ac.append(link)
    air['connections']=ac;out[airpath]=enc(air)
    al=next(x for x in ls['layouts'] if x.get('id')==air['layout'])
    assert (al['width'],al['height'])==(32,24)
    raw=s.read(al['blockdata_filepath']); tiles=list(struct.unpack('<768H',raw))
    allowed={(22,0):0x41c,(23,0):0x41d,(24,0):0x41c,(22,1):0x414,(23,1):0x415,(24,1):0x414}
    changed=[]
    for (x,y),old in allowed.items():
        assert tiles[y*32+x] in (old,0x3001), ('Airstrip changed',x,y)
        if tiles[y*32+x]!=0x3001:changed.append([x,y,tiles[y*32+x],0x3001])
        tiles[y*32+x]=0x3001
    for y in range(2,9):
        assert all(tiles[y*32+x]==0x3001 for x in range(22,25)), 'Airstrip road below corridor not clear'
    newraw=struct.pack('<768H',*tiles)
    diffs=[i for i,(a,b) in enumerate(zip(raw,newraw)) if a!=b]
    assert all((i//2%32,i//2//32) in allowed for i in diffs)
    out[al['blockdata_filepath']]=newraw
    stats['airstrip_changed_cells']=changed
    heals=s.json('src/data/heal_locations.json')
    hi={'id':'HEAL_LOCATION_CHERRYGROVE_CITY','map':MID['CherrygroveCity'],'x':26,'y':9,
        'respawn_map':MID['CherrygroveCity_PokemonCenter_1F'],'respawn_npc':'LOCALID_CHERRYGROVE_NURSE'}
    hits=[h for h in heals['heal_locations'] if h['id']==hi['id']]
    assert not hits or hits==[hi], 'conflicting heal location'
    if not hits:heals['heal_locations'].append(hi)
    out['src/data/heal_locations.json']=enc(heals)
    # Existing map, section and heal indices are only appended, never reordered.
    for name,key in [('data/layouts/layouts.json','layouts'),
                     ('src/data/region_map/region_map_sections.json','map_sections'),
                     ('src/data/heal_locations.json','heal_locations')]:
        old=s.json(name)[key];new=json.loads(out[name])[key]
        assert new[:len(old)]==old, 'append-only index invariant '+name
    patch_shared(s,out,scripts,tx)
    patch_areas(s,out)
    stats['map_count']=len(maps);stats['old_johto_maps_preserved']=OLD
    stats['new_maps']=NEW;stats['no_save_layout_change']=True
    stats['new_flags']={k:hex(0x1502+i) for i,k in enumerate(FLAGS)}
    return out,stats


def validate(s,out,stats):
    combined=Source(s.root,dict(s.overlay,**out))
    ls=combined.json('data/layouts/layouts.json')['layouts']
    bylayout={x['id']:x for x in ls if 'id' in x}
    attrs={}
    for typ,path in [('gTileset_General','data/tilesets/primary/general'),
                     ('gTileset_ViridianCity','data/tilesets/secondary/viridian_city')]:
        raw=s.read(path+'/metatile_attributes.bin')
        attrs[typ]=[x[0]&255 for x in struct.iter_unpack('<I',raw)]
    checks=[]
    for name in NEW:
        m=combined.json('data/maps/'+name+'/map.json')
        l=bylayout[m['layout']];w=l['width'];h=l['height']
        raw=combined.read(l['blockdata_filepath']);assert len(raw)==w*h*2,(name,'size')
        tiles=struct.unpack('<'+'H'*(w*h),raw)
        def cell(x,y):return tiles[y*w+x]
        def walkable(x,y):
            if not(0<=x<w and 0<=y<h):return False
            v=cell(x,y)
            if (v>>10)&3:return False
            # The outdoor path graph excludes the water surfaces (elevation 1).
            if name in ('CherrygroveCity','JohtoRoute30') and (v>>12)==1:return False
            return True
        for o in m['object_events']:
            assert 0<=o['x']<w and 0<=o['y']<h,(name,'NPC bounds',o)
            assert not ((cell(o['x'],o['y'])>>10)&3),(name,'NPC on blocked cell',o)
        for wp in m['warp_events']:
            assert 0<=wp['x']<w and 0<=wp['y']<h
            dm=next((n for n in NEW if MID[n]==wp['dest_map']),None)
            if dm:
                dest=combined.json('data/maps/'+dm+'/map.json')
                index=int(wp['dest_warp_id'])
                assert 0<=index<len(dest['warp_events'])
                assert dest['warp_events'][index]['dest_map']==m['id'],(name,'nonreciprocal warp',wp)
        if name in ('CherrygroveCity','JohtoRoute30'):
            start=(23,h-1) if name=='CherrygroveCity' else (7,h-1)
            assert walkable(*start)
            solid={(o['x'],o['y']) for o in m['object_events']}
            q=deque([start]);seen={start}
            while q:
                x,y=q.popleft()
                for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if p not in seen and p not in solid and walkable(*p):seen.add(p);q.append(p)
            for wp in m['warp_events']:assert (wp['x'],wp['y']+1) in seen,(name,'door inaccessible',wp)
            for o in m['object_events']:
                x,y=o['x'],o['y']
                assert any(p in seen for p in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]),(name,'NPC inaccessible',o)
            for o in m['bg_events']:
                assert (o['x'],o['y']+1) in seen,(name,'sign inaccessible',o)
            if name=='CherrygroveCity':
                assert all((x,0) in seen for x in range(18,22))
                assert all((x,h-1) in seen for x in range(22,25))
            if name=='JohtoRoute30':
                grasscount=sum(1 for x,y in seen if (cell(x,y)&1023)<640 and attrs['gTileset_General'][cell(x,y)&1023]==2)
                assert grasscount>70, ('reachable tall grass',grasscount)
                stats['route30_reachable_grass_cells']=grasscount
            checks.append({'map':name,'walkable_component_cells':len(seen),'doors_reachable':True,'NPCs_reachable':True})
        else:
            # Indoor templates are unchanged binary data; verify NPC placement above.
            checks.append({'map':name,'native_layout_reused':l['id'],'NPC_floor_cells_valid':True})
    a=combined.json('data/maps/JohtoCherrygroveAirstrip/map.json')
    c=combined.json('data/maps/CherrygroveCity/map.json')
    r=combined.json('data/maps/JohtoRoute30/map.json')
    assert {'map':MID['CherrygroveCity'],'direction':'up','offset':0} in a['connections']
    assert {'map':'MAP_JOHTO_CHERRYGROVE_AIRSTRIP','direction':'down','offset':0} in c['connections']
    assert {'map':MID['JohtoRoute30'],'direction':'up','offset':12} in c['connections']
    assert {'map':MID['CherrygroveCity'],'direction':'down','offset':-12} in r['connections']
    # All emitted event commands must be known native assembly macros.
    allowed=set(re.findall(r'(?m)^\s*\.macro\s+(\w+)',s.text('asm/macros/event.inc')+'\n'+s.text('asm/macros/map.inc')))
    for p,b in out.items():
        if p.endswith('scripts.inc'):
            for line in b.decode().splitlines():
                t=line.strip()
                if not t or t.startswith(('@','.','#')) or t.endswith(':'):continue
                cmd=t.split()[0]
                assert cmd in allowed,(p,'unknown script command',cmd)
    # No missing species/items/songs/object graphics in the target tree.
    headertext='\n'.join(s.text('include/constants/'+n) for n in ['species.h','items.h','songs.h','event_objects.h','global.h'])
    refs=set()
    for p,b in out.items():
        if not p.endswith(('.bin',)):
            try:refs |= set(re.findall(r'\b(?:SPECIES|ITEM|MUS|OBJ_EVENT_GFX)_[A-Z0-9_]+',b.decode()))
            except UnicodeDecodeError:pass
    missing=[n for n in refs if not re.search(r'\b'+re.escape(n)+r'\b',headertext)]
    # wild_encounters includes all prior species; they must remain known as well.
    assert not missing, ('unknown constants',missing)
    stats['static_checks']=checks
    stats['native_build_and_emulator']='NOT_RUN_BY_GENERATOR'
    return stats

def apply(root,apply_changes=False):
    s=Source(root)
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()
    assert branch=='hoenn-z3', 'unexpected branch '+branch
    out,stats=build(s);validate(s,out,stats)
    out2,_=build(Source(root,out))
    assert out==out2,'generation is not idempotent'
    # New artifacts must be absent or byte-identical; never replace another author's map.
    owned=[p for p in out if any(p.startswith('data/maps/'+n+'/') or p.startswith('data/layouts/'+n+'/') for n in NEW)]
    owned+=['tools/johto/route30_wild.json']
    for p in owned:
        if s.exists(p):assert s.read(p)==out[p],'existing generated artifact differs: '+p
    changes={p:b for p,b in out.items() if not s.exists(p) or s.read(p)!=b}
    print(json.dumps({'apply':apply_changes,'changed_files':sorted(changes),'checks':stats},ensure_ascii=False,indent=2))
    if not apply_changes or not changes:return
    # Recheck every source read immediately before any mutation.
    for p,b in s.used.items():assert (root/p).read_bytes()==b,'concurrent edit: '+p
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup=root/'outputs/johto-cherrygrove-route30-v1'/stamp
    backup.mkdir(parents=True,exist_ok=False)
    manifest={'created_utc':stamp,'branch':branch,'files':{},'validation':stats}
    for p,b in changes.items():
        target=root/p;old=target.read_bytes() if target.exists() else None
        manifest['files'][p]={'old_sha256':sha(old) if old is not None else None,'new_sha256':sha(b)}
        if old is not None:
            dest=backup/'before'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(old)
    (backup/'manifest.json').write_bytes(enc(manifest))
    for p,b in changes.items():
        target=root/p;target.parent.mkdir(parents=True,exist_ok=True)
        temp=target.with_name(target.name+'.johto-cherrygrove.tmp')
        assert not temp.exists(), 'unexpected temp file '+str(temp)
        temp.write_bytes(b);temp.replace(target)
    assert all((root/p).read_bytes()==b for p,b in out.items())
    (backup/'source-validation.json').write_bytes(enc(stats))
    print('APPLIED '+str(backup/'manifest.json'))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',default='.')
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    apply(Path(args.root).resolve(),args.apply)
