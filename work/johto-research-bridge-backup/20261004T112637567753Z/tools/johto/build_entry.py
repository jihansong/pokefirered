#!/usr/bin/env python3
"""Johto entry: deterministic FR/LG layouts, reciprocal travel, no save fields."""
import argparse,copy,hashlib,json,pathlib,re,struct,subprocess,datetime
NAMES=['JohtoCherrygroveAirstrip','JohtoRoute29','NewBarkTown','NewBarkTown_ElmsLab','NewBarkTown_RestHouse','NewBarkTown_NeighborsHouse']
IDS=['JOHTO_CHERRYGROVE_AIRSTRIP','JOHTO_ROUTE29','NEW_BARK_TOWN','NEW_BARK_TOWN_ELMS_LAB','NEW_BARK_TOWN_REST_HOUSE','NEW_BARK_TOWN_NEIGHBORS_HOUSE']
SECS=['MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP','MAPSEC_JOHTO_ROUTE_29','MAPSEC_NEW_BARK_TOWN'];GROUP='gMapGroup_JohtoEntry'
def enc(j):return(json.dumps(j,indent=2,ensure_ascii=False)+'\n').encode()
def patch(t,old,new):
 if new in t:
  assert t.count(new)==1,'Duplicate already-applied anchor';return t
 assert t.count(old)==1,'Fresh source anchor changed: '+old[:90]
 return t.replace(old,new,1)
def build(r):
 out={}
 def read(p):return(r/p).read_text(encoding='utf-8')
 def put(p,v):out[p]=v.encode()if isinstance(v,str)else v
 def srcmap(n):return json.loads(read('data/maps/'+n+'/map.json'))
 layouts=json.loads(read('data/layouts/layouts.json'));groups=json.loads(read('data/maps/map_groups.json'));sections=json.loads(read('src/data/region_map/region_map_sections.json'))
 oldlayout=copy.deepcopy(layouts['layouts']);oldgroups=copy.deepcopy(groups);src={}
 for n in['PalletTown','PalletTown_ProfessorOaksLab','PalletTown_RivalsHouse']:
  m=srcmap(n);l=next(l for l in oldlayout if l.get('id')==m['layout'])
  vals=struct.unpack('<'+'H'*(l['width']*l['height']),(r/l['blockdata_filepath']).read_bytes())
  src[n]=(l,[list(vals[y*l['width']:(y+1)*l['width']])for y in range(l['height'])])
 def grid(w,h):return[[0x3001 for x in range(w)]for y in range(h)]
 def rect(a,x0,y0,w,h,v):
  for y in range(y0,y0+h):
   for x in range(x0,x0+w):a[y][x]=v(x,y)if callable(v)else v
 def trees(a):
  w,h=len(a[0]),len(a)
  for y in range(h):
   for x in range(w):
    if x<2 or x>=w-2 or y<2 or y>=h-2:a[y][x]=0x400+((28,29)if y%2==0 else(20,21))[x%2]
 def paste(a,b,sx,sy,w,h,dx,dy):
  for y in range(h):
   for x in range(w):a[dy+y][dx+x]=b[sy+y][sx+x]
 town=grid(36,28);trees(town);rect(town,0,11,32,3,0x3296);rect(town,9,8,4,16,0x3296);rect(town,21,13,4,11,0x3296)
 p=src['PalletTown'][1]
 paste(town,p,12,9,9,6,7,4);paste(town,p,3,2,8,7,8,15);paste(town,p,12,2,8,7,20,15)
 for x in range(3,30,3):town[24][x]=0x3004
 rect(town,33,2,3,24,0x152B);rect(town,32,2,1,24,0x34F4);town[10][3]=0x3402
 route=grid(40,24);trees(route);rect(route,0,11,40,3,0x3001)
 for x in range(3,37):route[12][x]=0x3008 if x%2 else 0x3011
 for x0,y0,w,h in[(5,3,8,4),(22,4,10,4),(8,17,8,4),(27,17,8,4)]:rect(route,x0,y0,w,h,lambda x,y:0x400+((28,29)if y%2==0 else(20,21))[x%2])
 for x in[3,4,15,16,34,35]:route[9][x]=0x3004;route[15][x]=0x3004
 route[10][36]=0x3402
 ns={'__file__':str(r/'tools/make_runway_tiles.py'),'__name__':'johto_runway_source'}
 exec(compile(read('tools/make_runway_tiles.py'),ns['__file__'],'exec'),ns)
 mt={n:ns['SECONDARY_TILE_BASE']+ns['FIRST_METATILE']+i for i,(n,_)in enumerate(ns['METATILES'])}
 air=grid(32,24);trees(air);rect(air,0,2,5,20,0x152B);rect(air,5,2,1,20,0x34F4);rect(air,16,11,16,3,0x3001)
 for y in range(3,19):
  rr=(['CORNER_TL','EDGE_T','EDGE_T','CORNER_TR']if y==3 else['CORNER_BL','EDGE_B','EDGE_B','CORNER_BR']if y==18 else['EDGE_L','THRESHOLD','THRESHOLD','EDGE_R']if y in(4,17)else['EDGE_L','NUM_0','NUM_1','EDGE_R']if y==5 else['EDGE_L','ASPHALT','DASH'if y%2==0 else'ASPHALT','EDGE_R'])
  for dx,v in enumerate(rr):air[y][9+dx]=0x400|mt[v]
 rect(air,15,2,1,20,0x34F4);air[10][25]=0x3402
 def obj(i,g,x,y,script):return dict(local_id="LOCALID_"+script.upper(),type='object',graphics_id='OBJ_EVENT_GFX_'+g,x=x,y=y,elevation=3,movement_type='MOVEMENT_TYPE_FACE_DOWN',movement_range_x=0,movement_range_y=0,trainer_type='TRAINER_TYPE_NONE',trainer_sight_or_berry_tree_id='0',script=script,flag='0')
 def warp(x,y,d,i,e=3):return dict(x=x,y=y,elevation=e,dest_map='MAP_'+IDS[d],dest_warp_id=str(i))
 def sign(x,y,label):return dict(type='sign',x=x,y=y,elevation=0,player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',script=label)
 maps=[]
 for i,n in enumerate(NAMES):
  m=copy.deepcopy(srcmap('PalletTown'if i<3 else'PalletTown_RivalsHouse'))
  m.update(id='MAP_'+IDS[i],name=n,layout='LAYOUT_'+IDS[i],region_map_section=SECS[min(i,2)],music='MUS_PALLET'if i>=2 else'MUS_ROUTE1',connections=None,object_events=[],warp_events=[],coord_events=[],bg_events=[],show_map_name=i<3,map_type='MAP_TYPE_ROUTE'if i==1 else'MAP_TYPE_TOWN'if i<3 else'MAP_TYPE_INDOOR',allow_running=True,allow_cycling=i<3,weather='WEATHER_SUNNY'if i<3 else'WEATHER_NONE');maps.append(m)
 maps[0]['connections']=[dict(map='MAP_'+IDS[1],offset=0,direction='right')]
 maps[1]['connections']=[dict(map='MAP_'+IDS[0],offset=0,direction='left'),dict(map='MAP_'+IDS[2],offset=0,direction='right')]
 maps[2]['connections']=[dict(map='MAP_'+IDS[1],offset=0,direction='left')]
 maps[0]['object_events']=[obj(1,'CLERK',22,10,NAMES[0]+'_ReturnClerk'),obj(2,'SAILOR',26,15,NAMES[0]+'_Guide')]
 maps[0]['bg_events']=[sign(25,10,NAMES[0]+'_Sign')]
 maps[1]['object_events']=[obj(1,'MAN',18,10,NAMES[1]+'_Hiker')];maps[1]['bg_events']=[sign(36,10,NAMES[1]+'_Sign')]
 maps[2]['object_events']=[obj(1,'WOMAN_1',18,12,NAMES[2]+'_Resident')];maps[2]['bg_events']=[sign(3,10,NAMES[2]+'_Sign')]
 maps[2]['warp_events']=[warp(11,8,3,0,0),warp(11,20,4,0,0),warp(23,20,5,0,0)]
 maps[3]['object_events']=[obj(1,'SCIENTIST',5,5,NAMES[3]+'_Researcher')];maps[3]['warp_events']=[warp(x,12,2,0)for x in(6,7,5)]
 maps[4]['object_events']=[obj(1,'WOMAN_2',8,6,NAMES[4]+'_Host')];maps[5]['object_events']=[obj(1,'MAN',8,6,NAMES[5]+'_Resident')]
 for i in(4,5):maps[i]['warp_events']=[warp(x,8,2,i-3)for x in(4,5,3)]
 blobs=[air,route,town,src['PalletTown_ProfessorOaksLab'][1],src['PalletTown_RivalsHouse'][1],src['PalletTown_RivalsHouse'][1]]
 for i,(n,a,m)in enumerate(zip(NAMES,blobs,maps)):
  if i<3:
   l=dict(id='LAYOUT_'+IDS[i],name=n+'_Layout',width=len(a[0]),height=len(a),border_width=2,border_height=2,primary_tileset='gTileset_General',secondary_tileset='gTileset_VermilionCity'if i==0 else'gTileset_PalletTown');border=struct.pack('<4H',0x41c,0x41d,0x414,0x415)
  else:
   sl=src['PalletTown_ProfessorOaksLab'if i==3 else'PalletTown_RivalsHouse'][0];l=copy.deepcopy(sl);l.update(id='LAYOUT_'+IDS[i],name=n+'_Layout');border=(r/sl['border_filepath']).read_bytes()
  l.update(border_filepath=f'data/layouts/{n}/border.bin',blockdata_filepath=f'data/layouts/{n}/map.bin')
  old=next((v for v in layouts['layouts']if v.get('id')==l['id']),None)
  if old is None:layouts['layouts'].append(l)
  else:assert old==l,'Existing Johto layout differs'
  put(l['border_filepath'],border);put(l['blockdata_filepath'],struct.pack('<'+'H'*(len(a)*len(a[0])),*[v for row in a for v in row]))
  put(f'data/maps/{n}/map.json',enc(m));put(f'data/maps/{n}/scripts.inc',n+'_MapScripts::\n\t.byte 0\n\n');put(f'data/maps/{n}/text.inc','')
 if GROUP in groups:assert groups[GROUP]==NAMES and groups['group_order'][-1]==GROUP
 else:
  assert all(n not in sum([groups[g]for g in groups['group_order']],[])for n in NAMES)
  groups['group_order'].append(GROUP);groups[GROUP]=NAMES
 assert len(groups['group_order'])<128
 put('data/maps/map_groups.json',enc(groups));put('data/layouts/layouts.json',enc(layouts))
 se=sections['map_sections']
 if not any(v['id']=='MAPSEC_NONE'for v in se):
  assert len(se)==197 and se[-1]['id']=='MAPSEC_SPECIAL_AREA';se.append(dict(id='MAPSEC_NONE'))
  for id,name,x,w in[(SECS[0],'CHERRYGROVE',6,1),(SECS[1],'ROUTE 29',7,8),(SECS[2],'NEW BARK TOWN',15,1)]:se.append(dict(id=id,name=name,x=x,y=8,width=w,height=1))
 assert se[197]['id']=='MAPSEC_NONE'and[se[i]['id']for i in range(198,201)]==SECS and len(se)<253
 put('src/data/region_map/region_map_sections.json',enc(sections))
 p='src/data/region_map/region_map_sections.constants.json.txt';put(p,patch(read(p),'## endfor\n    MAPSEC_NONE,\n    MAPSEC_COUNT','## endfor\n    MAPSEC_COUNT'))
 p='src/region_map.c';t=read(p)
 t=patch(t,'    REGIONMAP_HOENN,\n    REGIONMAP_COUNT','    REGIONMAP_HOENN,\n    REGIONMAP_JOHTO_ENTRY,\n    REGIONMAP_COUNT')
 line='    [REGIONMAP_HOENN]    = {HOENN_MAP_WIDTH, MAP_HEIGHT, 12, 20, 26, 13, NO_BUTTON, NO_BUTTON},'
 t=patch(t,line,line+'\n    [REGIONMAP_JOHTO_ENTRY] = {MAP_WIDTH, MAP_HEIGHT, 36, 36, CANCEL_BUTTON_X, CANCEL_BUTTON_Y, NO_BUTTON, NO_BUTTON},')
 line='static const u32 sKanto_Tilemap[] = INCBIN_U32("graphics/region_map/kanto.bin.lz");'
 t=patch(t,line,line+'\nstatic const u32 sJohtoEntry_Tilemap[] = INCBIN_U32("graphics/region_map/johto_entry.bin.lz");')
 line='    if (gMapHeader.regionMapSectionId < KANTO_MAPSEC_START)'
 t=patch(t,line,'    if (gMapHeader.regionMapSectionId >= MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP\n     && gMapHeader.regionMapSectionId <= MAPSEC_NEW_BARK_TOWN)\n    {\n        sRegionMap->permissions[MAPPERM_HAS_SWITCH_BUTTON] = FALSE;\n        sRegionMap->selectedRegion = REGIONMAP_JOHTO_ENTRY;\n        sRegionMap->playersRegion = REGIONMAP_JOHTO_ENTRY;\n        return;\n    }\n'+line)
 line='        LZ77UnCompWram(sHoenn_Tilemap, sRegionMap->layouts[REGIONMAP_HOENN]);'
 t=patch(t,line,line+'\n        LZ77UnCompWram(sJohtoEntry_Tilemap, sRegionMap->layouts[REGIONMAP_JOHTO_ENTRY]);')
 line='    case REGIONMAP_HOENN:\n        return sRegionMapSections_Hoenn[layer][y][x];'
 t=patch(t,line,line+'\n    case REGIONMAP_JOHTO_ENTRY:\n        if (layer != LAYER_MAP || y != 8)\n            return MAPSEC_NONE;\n        if (x == 6)\n            return MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP;\n        if (x >= 7 && x <= 14)\n            return MAPSEC_JOHTO_ROUTE_29;\n        if (x == 15)\n            return MAPSEC_NEW_BARK_TOWN;\n        return MAPSEC_NONE;')
 t=patch(t,'else if ((idx = mapsec - KANTO_MAPSEC_START) < MAPSEC_NONE - KANTO_MAPSEC_START)','else if (mapsec != MAPSEC_NONE\n          && (idx = mapsec - KANTO_MAPSEC_START) < MAPSEC_COUNT - KANTO_MAPSEC_START\n          && sMapNames[idx] != NULL)');put(p,t)
 p='src/pokemon_summary_screen.c';line='    if (mapSec >= KANTO_MAPSEC_START && mapSec < MAPSEC_NONE)'
 put(p,patch(read(p),line,'    // Native Johto encounters also have named locations in this game.\n    if (mapSec >= MAPSEC_JOHTO_CHERRYGROVE_AIRSTRIP && mapSec <= MAPSEC_NEW_BARK_TOWN)\n        return TRUE;\n'+line))
 old=struct.unpack('<600H',(r/'graphics/region_map/kanto.bin').read_bytes());mini=[3]*600
 coast=[13,13,14,14,13,13,14,14,15,15,14,13,13,13,13,14,14,13,12,12,13,13,12,11]
 for x,bottom in enumerate(coast,3):
  for y in range(2,bottom+1):mini[y*30+x]=7 if y==bottom or x in(3,26)else 5
 for x0,y0,w,h in[(5,3,5,4),(16,3,7,4),(11,7,5,2)]:
  for y in range(y0,y0+h):
   for x in range(x0,x0+w):mini[y*30+x]=6 if(x+y)%3 else 7
 for x in range(10,20):mini[12*30+x]=0x100A
 mini[12*30+10]=mini[12*30+19]=0x1001
 for y in range(16,19):
  for x in range(24,27):mini[y*30+x]=old[y*30+x]
 put('graphics/region_map/johto_entry.bin',struct.pack('<600H',*mini))
 p='include/constants/airplane.h';put(p,patch(read(p),'#define AIRPLANE_DEST_COUNT 2','#define AIRPLANE_DEST_JOHTO 2 // CHERRYGROVE AIRSTRIP\n#define AIRPLANE_DEST_COUNT 3'))
 p='src/airplane_flight.c';line='    [AIRPLANE_DEST_HOENN] = {MAP(MAP_SLATEPORT_CITY_HARBOR), 12, 13},'
 put(p,patch(read(p),line,line+'\n    [AIRPLANE_DEST_JOHTO] = {MAP(MAP_JOHTO_CHERRYGROVE_AIRSTRIP), 22, 12},'))
 p='data/maps/KantoAirport/scripts.inc';old='KantoAirport_EventScript_JohtoClerk::\n\tmsgbox KantoAirport_Text_JohtoSoon, MSGBOX_NPC\n\tend'
 new='KantoAirport_EventScript_JohtoClerk::\n    lock\n    faceplayer\n    goto_if_unset FLAG_SYS_GAME_CLEAR, KantoAirport_EventScript_JohtoNotChampion\n    msgbox KantoAirport_Text_FlyToJohto, MSGBOX_YESNO\n    goto_if_eq VAR_RESULT, NO, KantoAirport_EventScript_ComeAgain\n    msgbox KantoAirport_Text_Boarding\n    closemessage\n    setvar VAR_0x8004, AIRPLANE_DEST_JOHTO\n    goto EventScript_TakeAirplane\n    end\n\nKantoAirport_EventScript_JohtoNotChampion::\n    msgbox KantoAirport_Text_JohtoChampionsOnly\n    release\n    end'
 put(p,patch(read(p),old,new))
 p='data/maps/KantoAirport/text.inc';t=read(p)
 if 'KantoAirport_Text_FlyToJohto::'not in t:t+='\nKantoAirport_Text_FlyToJohto::\n    .string "Fly to CHERRYGROVE in JOHTO?\\n"\n    .string "The return flight is free, too.$"\n'
 if 'KantoAirport_Text_JohtoChampionsOnly::'not in t:t+='\nKantoAirport_Text_JohtoChampionsOnly::\n    .string "The JOHTO service is open to\\n"\n    .string "POKéMON LEAGUE CHAMPIONS.$"\n'
 put(p,t);p='data/event_scripts.s';t=read(p)
 for n in NAMES:
  for f in['scripts.inc','text.inc']:
   line=f'\t.include "data/maps/{n}/{f}"'
   if line not in t:t+='\n'+line+'\n'
 put(p,t)
 def script(i,s):put(f'data/maps/{NAMES[i]}/scripts.inc',out[f'data/maps/{NAMES[i]}/scripts.inc']+s.encode())
 def text(i,labels):put(f'data/maps/{NAMES[i]}/text.inc','\n\n'.join(NAMES[i]+'_Text_'+key+'::\n    .string "'+value+'$"'for key,value in labels.items())+'\n')
 def npc(i,key):return NAMES[i]+'_'+key+'::\n\tmsgbox '+NAMES[i]+'_Text_'+key+', MSGBOX_NPC\n\tend\n\n'
 script(0,NAMES[0]+'_ReturnClerk::\n\tlock\n\tfaceplayer\n\tmsgbox '+NAMES[0]+'_Text_Return, MSGBOX_YESNO\n\tgoto_if_eq VAR_RESULT, NO, '+NAMES[0]+'_Cancel\n\tclosemessage\n\tsetvar VAR_0x8004, AIRPLANE_DEST_KANTO\n\tgoto EventScript_TakeAirplane\n\tend\n\n'+NAMES[0]+'_Cancel::\n\tmsgbox '+NAMES[0]+'_Text_Cancel\n\trelease\n\tend\n\n'+npc(0,'Guide')+npc(0,'Sign'))
 text(0,dict(Return='Fly back to VERMILION AIRPORT?\\nThere is no fare.',Cancel='The return desk stays open.\\nCome back whenever you like.',Guide='Welcome to the CHERRYGROVE coast!\\pFollow ROUTE 29 east to reach\\nNEW BARK TOWN.',Sign='CHERRYGROVE AIRSTRIP\\nEast: ROUTE 29 and NEW BARK TOWN'))
 script(1,npc(1,'Hiker')+npc(1,'Sign'));text(1,dict(Hiker='NEW BARK TOWN is east of here.\\pThe western path leads back to\\nthe CHERRYGROVE airstrip.',Sign='ROUTE 29\\nEast: NEW BARK TOWN'))
 script(2,npc(2,'Resident')+npc(2,'Sign'));text(2,dict(Resident='Welcome to NEW BARK TOWN!\\pThe house southwest of here\\nwelcomes tired travelers.',Sign='NEW BARK TOWN\\nThe Town Where Winds Begin'))
 put("data/maps/NewBarkTown_ElmsLab/scripts.inc",(r/"tools/johto/patches/NewBarkTown_ElmsLab/scripts.inc").read_bytes())
 put("data/maps/NewBarkTown_ElmsLab/text.inc",(r/"tools/johto/patches/NewBarkTown_ElmsLab/text.inc").read_bytes())
 script(4,NAMES[4]+'_Host::\n\tlock\n\tfaceplayer\n\tmsgbox '+NAMES[4]+'_Text_Offer, MSGBOX_YESNO\n\tgoto_if_eq VAR_RESULT, NO, '+NAMES[4]+'_Cancel\n\tclosemessage\n\tfadescreen FADE_TO_BLACK\n\tspecial HealPlayerParty\n\tplayfanfare MUS_HEAL\n\twaitfanfare\n\tfadescreen FADE_FROM_BLACK\n\tmsgbox '+NAMES[4]+'_Text_Done\n\trelease\n\tend\n\n'+NAMES[4]+'_Cancel::\n\tmsgbox '+NAMES[4]+'_Text_Cancel\n\trelease\n\tend\n')
 text(4,dict(Offer='You and your POKéMON look tired.\\nWould you like to rest here?',Done='There! Your POKéMON are rested.\\nHave a pleasant journey!',Cancel="You're welcome to rest anytime."))
 script(5,npc(5,'Resident'));text(5,dict(Resident="The sea breeze reaches all the\\nway to ELM's laboratory.\\pThe airstrip is west along ROUTE 29.\\nThat's your way back to KANTO."))
 return out,dict(maps=maps,grids=blobs,old_groups=oldgroups,old_layouts=oldlayout)

import collections,importlib.util

def verify(r,out,meta):
 counts={};maps=meta['maps'];grids=meta['grids']
 goals=[[(22,12),(31,12),(22,11)],[(0,12),(39,12),(18,11)],[(0,12),(11,9),(11,21),(23,21),(11,10)],[(6,11),(5,6)],[(4,7),(8,7)],[(4,7),(8,7)]]
 for i,(m,g)in enumerate(zip(maps,grids)):
  w,h=len(g[0]),len(g);blocked={(o['x'],o['y'])for o in m['object_events']}
  ok=lambda x,y:0<=x<w and 0<=y<h and(g[y][x]&0xc00)==0 and(g[y][x]>>12)==3 and(x,y)not in blocked
  q=collections.deque([goals[i][0]]);seen=set(q);assert ok(*q[0]),(m['name'],'spawn blocked')
  while q:
   x,y=q.popleft()
   for xy in[(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if xy not in seen and ok(*xy):seen.add(xy);q.append(xy)
  assert all(p in seen for p in goals[i]),(m['name'],'unreachable',goals[i])
  for o in m['object_events']:
   assert 0<=o['x']<w and 0<=o['y']<h
   assert(g[o['y']][o['x']]&0xc00)==0,(m['name'],'object on solid',o)
  for warp in m['warp_events']:
   target=maps[IDS.index(warp['dest_map'][4:])];back=target['warp_events'][int(warp['dest_warp_id'])]
   assert back['dest_map']==m['id'],(m['name'],'non-reciprocal door')
  counts[m['name']]=len(seen)
 for a,b in[(0,1),(1,2)]:
  for y in(11,12,13):
   assert grids[a][y][-1]==grids[a][y][-1]&~0xc00
   assert(grids[a][y][-1]>>12)==(grids[b][y][0]>>12)==3
 assert all(m['name']not in sum([meta['old_groups'][g]for g in meta['old_groups']['group_order']if g!=GROUP],[])for m in maps)
 newg=json.loads(out['data/maps/map_groups.json'])
 for g in meta['old_groups']['group_order']:
  assert newg['group_order'].index(g)==meta['old_groups']['group_order'].index(g)and newg[g]==meta['old_groups'][g]
 newl=json.loads(out['data/layouts/layouts.json'])['layouts'];assert newl[:len(meta['old_layouts'])]==meta['old_layouts']
 for p in out:assert not p.startswith('saves/')and p not in('include/global.h','include/pokemon_storage_system.h')
 s='\n'.join(out[f'data/maps/{n}/scripts.inc'].decode()for n in NAMES);labels=re.findall(r'^(\w+)::',s,re.M)
 texts='\n'.join(out[f'data/maps/{n}/text.inc'].decode()for n in NAMES);tl=re.findall(r'^(\w+)::',texts,re.M)
 assert len(labels+tl)==len(set(labels+tl));refs=re.findall(r'\bmsgbox\s+(\w+)',s);assert set(refs)<=set(tl)
 macros='\n'.join(p.read_text(encoding='utf-8')for p in(r/'asm/macros').glob('*.inc'))
 cmds={x.strip().split()[0]for x in s.splitlines()if x.startswith('\t')and not x.strip().startswith('.')}
 assert not cmds-set(re.findall(r'\.macro\s+(\w+)',macros)),cmds
 spec=importlib.util.spec_from_file_location('johto_textwidth',r/'tools/qa/textwidth.py');tw=importlib.util.module_from_spec(spec);spec.loader.exec_module(tw);font=tw.Font(10)
 pieces=[];widths=[]
 for line in texts.splitlines():
  if line.endswith('::')and pieces:widths+=list(tw.split_lines(pieces,font));pieces=[]
  q=re.match(r'\s*\.string "(.*)"$',line)
  if q:pieces.append((len(pieces)+1,q[1]))
 if pieces:widths+=list(tw.split_lines(pieces,font))
 assert not font.unknown,font.unknown;assert all(x[2]<=208 for x in widths),[x for x in widths if x[2]>208]
 newsecs=json.loads(out['src/data/region_map/region_map_sections.json'])['map_sections']
 for sec in newsecs[198:]:assert len(sec.get('name','').encode('ascii'))<=18,('region name overflows mapName[19]',sec)
 assert newsecs[197]['id']=='MAPSEC_NONE'
 assert [s['id']for s in newsecs[198:201]]==SECS
 pg=(r/'data/tilesets/primary/general/metatile_attributes.bin').read_bytes();sp=(r/'data/tilesets/secondary/pallet_town/metatile_attributes.bin').read_bytes()
 pg=struct.unpack('<'+'I'*(len(pg)//4),pg);sp=struct.unpack('<'+'I'*(len(sp)//4),sp)
 doors=set()
 for y,row in enumerate(grids[2]):
  for x,v in enumerate(row):
   n=v&1023;attr=pg[n]if n<640 else sp[n-640]
   if(attr&0xff)==0x69:doors.add((x,y))
 assert doors=={(w['x'],w['y'])for w in maps[2]['warp_events']},('drawn doors/warps',doors)
 return dict(reachable_ground=counts,labels=len(labels+tl),text_lines=len(widths),max_text_width=max(x[2]for x in widths),runtime='NOT RUN')
def qa_cases():
 result=[]
 def case(name,ed,st,xfail=False):
  c=dict(name='johto_entry_'+name,base='saves/hoenn.sav',edit=['noquestlog']+ed,steps=st)
  if xfail:c['xfail']=True
  result.append(c)
 airport=['warp KantoAirport 10 6','flag FLAG_SYS_GAME_CLEAR 1']
 case('champion_gate',['warp KantoAirport 10 6','flag FLAG_SYS_GAME_CLEAR 0'],['UP','A','mash 30','expect map KantoAirport','expect overworld'])
 case('outbound',airport,['UP','A*6','wait 850','mash 20','expect map JohtoCherrygroveAirstrip','expect overworld','shot arrived'])
 case('outbound_cancel',airport,['UP','A*2','wait 30','B','mash 20','wait 650','expect map KantoAirport','expect overworld'])
 case('champion_gate_negative',['warp KantoAirport 10 6','flag FLAG_SYS_GAME_CLEAR 0'],['UP','A*6','wait 850','expect map JohtoCherrygroveAirstrip'],True)
 back=['warp JohtoCherrygroveAirstrip 22 11','flag FLAG_SYS_GAME_CLEAR 0']
 case('return_without_champion_flag',back,['UP','A*5','wait 850','expect map KantoAirport','expect overworld'])
 case('return_cancel',back,['UP','A*2','wait 30','B','mash 20','wait 650','expect map JohtoCherrygroveAirstrip','expect overworld'])
 for n,a,x,y,key,d in[('airstrip_to_route',NAMES[0],30,12,'RIGHT 2',NAMES[1]),('route_to_airstrip',NAMES[1],1,12,'LEFT 2',NAMES[0]),('route_to_town',NAMES[1],38,12,'RIGHT 2',NAMES[2]),('town_to_route',NAMES[2],1,12,'LEFT 2',NAMES[1])]:case(n,[f'warp {a} {x} {y}'],[key,'wait 90','expect map '+d,'expect overworld'])
 for n,x,y,inside,dx,dy in[('lab',11,9,NAMES[3],6,11),('rest',11,21,NAMES[4],4,7),('neighbor',23,21,NAMES[5],4,7)]:
  case('door_'+n,[f'warp NewBarkTown {x} {y}'],['UP','wait 180','expect map '+inside,'expect overworld'])
  case('exit_'+n,[f'warp {inside} {dx} {dy}'],['DOWN','wait 180','expect map NewBarkTown','expect overworld'])
 case('rest_heals',['warp NewBarkTown_RestHouse 8 7','hp 0 1'],['UP','A*5','wait 300','mash 20','expect hp 0 = full','expect overworld'])
 case('rest_cancel',['warp NewBarkTown_RestHouse 8 7','hp 0 1'],['UP','A*2','wait 30','B','mash 20','expect hp 0 = 1','expect overworld'])
 for n in NAMES:
  x,y=(22,12)if n==NAMES[0]else(4,12)if n in NAMES[1:3]else(6,11)if n==NAMES[3]else(4,7)
  case('town_map_'+n,[f'warp {n} {x} {y}'],['special ShowTownMap wait','wait 90','shot town_map','B','wait 120','expect map '+n,'expect overworld'])
 case('hoenn_flight_preserved',['warp KantoAirport 6 6','flag FLAG_SYS_GAME_CLEAR 1'],['UP','A*6','wait 850','expect map SlateportCity_Harbor','expect overworld'])
 return result
EXPECTED={
'include/constants/airplane.h':'d7adff3aa835dd7d9df39ee02b6841eb045fb8ae299a1b6d46baf2de091a5940',
'src/airplane_flight.c':'2c855193ae595c90eab43477ad506d85438ef062ad61102efd400aac69224fa8',
'data/maps/KantoAirport/scripts.inc':'1121466acdbfc011662eb35b468589e1aa0629c4fde7ddc01fcf937379af5f9b',
'data/maps/KantoAirport/text.inc':'9f0379aa79bbdfd05227b56412e60e584d696af91d61dc042b3386c808b6a1f6',
'data/maps/map_groups.json':'f43a28a73088fbe792ae3c343c862d9e897a08e0897900107547fc445afe2afd',
'data/layouts/layouts.json':'f5a934164b16937f68bbd6c9ee5a44c1f477772dce93bb2a71993877c8d59f77',
'src/region_map.c':'0e7815f3146413731c9d6d2e98e41d62cbba5936912e9ef5de881241f1ce09ad',
'src/pokemon_summary_screen.c':'a0e2eccdee094e2ab18e1c5db2af398734da86d7db00a43cef457b569af7db71',
'data/event_scripts.s':'4ac1b4bbb3b0766f726124b7527843e7df45e5ddba7e84061505e04462f18f54',
'src/data/region_map/region_map_sections.json':'82e456cbe86a57ebc4bd0d88d6e000e83e28340895ac038079c38d415bc6de5f',
'src/data/region_map/region_map_sections.constants.json.txt':'84346d3ffc7572aab79273d7f048521f384e77e78c20a6c8b852966949d182d5',
'data/layouts/PalletTown/map.bin':'b709c6d47d6006ff6402026496a9d0d9caab19a4515b02517eaf049c5f7bf2e0',
'data/layouts/PalletTown_ProfessorOaksLab/map.bin':'a1ca472215cd91f5128360af49880035be67b82fb43120758826a21e6a8d803f',
'data/layouts/PalletTown_RivalsHouse/map.bin':'d7622458849c723663b8240434f78881cf9a68705a5545ad31ccc2e264117a6d',
'graphics/region_map/kanto.bin':'c9f38c5d52099958c18efe737a45ba04ce8101b0eb349e9d2243bf8324d82b49'}
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=pathlib.Path,default=pathlib.Path('/workspaces/pokefirered'));ap.add_argument('--apply',action='store_true');a=ap.parse_args();r=a.root.resolve()
 assert subprocess.check_output(['git','branch','--show-current'],cwd=r,text=True).strip()=='hoenn-z3'
 inputs=list(EXPECTED)
 for n in['PalletTown','PalletTown_ProfessorOaksLab','PalletTown_RivalsHouse']:
  inputs.append(f'data/maps/{n}/map.json');m=json.loads((r/inputs[-1]).read_text())
  l=next(v for v in json.loads((r/'data/layouts/layouts.json').read_text())['layouts']if v.get('id')==m['layout']);inputs.append(l['border_filepath'])
 inputs+=['tools/make_runway_tiles.py','asm/macros/event.inc','data/specials.inc','include/global.h']
 before={p:(r/p).read_bytes()for p in inputs};out,meta=build(r);report=verify(r,out,meta)
 for p,h in EXPECTED.items():assert digest(before[p])==h or(p in out and before[p]==out[p]),'Source hash differs: '+p
 class Overlay:
  def __init__(self,p):self.p=p
  def __truediv__(self,x):return Overlay(self.p/x)
  def __str__(self):return str(self.p)
  def read_bytes(self):
   k=self.p.relative_to(r).as_posix();return out[k]if k in out else self.p.read_bytes()
  def read_text(self,encoding='utf-8'):return self.read_bytes().decode(encoding)
 again,_=build(Overlay(r));assert out==again,'Generator is not idempotent'
 cases=qa_cases();cp='tools/qa/cases/johto_entry.jsonl'
 out[cp]=('# Johto entry pilot; original saves unchanged; runtime NOT RUN.\n'+''.join(json.dumps(c)+'\n'for c in cases)).encode()
 dp='docs/team/qa/codex-johto-entry-20261004/README.md'
 if not(r/dp).exists():out[dp]=b'''# Johto entry pilot - runtime validation pending

Six actual maps: Cherrygrove coast airstrip, Route 29, New Bark Town,
research laboratory, rest house and neighbor house. Uses existing FR/LG
metatiles in new outdoor arrangements and native interior layouts.
No claim of completed Johto gyms, starters, rivals or league.
Champion outbound flight; unconditional return avoids stranding imported saves.
Reciprocal doors, rest-house heal, map overview. No new save fields/flags.
Map/layout IDs append only; MAPSEC_NONE stays197. Regional ending pending.
Builder checks reachability, collisions, doors, seams, macros, text width,
source hashes and idempotency. Runtime NOT RUN; 25 cases must run against ROM.
Original-save load, in-map SAVE/reload and DELTA device checks required.
'''
 for p,b in out.items():
  existing=(r/p).read_bytes()if(r/p).exists()else None
  if p not in EXPECTED and existing is not None:assert existing==b,'Existing owned artifact differs; merge explicitly: '+p
  before.setdefault(p,existing)
 changed={p:b for p,b in out.items()if before[p]!=b}
 report.update(files=len(changed),new_maps=NAMES,runtime_cases=len(cases),canonical_idempotent=True,new_bark_sha256=digest(out['data/layouts/NewBarkTown/map.bin']),applied=False)
 if not a.apply:print(json.dumps(report,indent=2));return
 for p,b in before.items():
  now=(r/p).read_bytes()if(r/p).exists()else None
  assert now==b,'Concurrent modification: '+p
 if not changed:print(json.dumps(report,indent=2));return
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');backup=r/('.qa-johto-entry-before-'+stamp);backup.mkdir(exist_ok=False)
 for p,b in before.items():
  if b is not None:
   dest=backup/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
 manifest=dict(utc=stamp,before={p:digest(b)if b is not None else None for p,b in before.items()},after={p:digest(b)for p,b in out.items()},report=report)
 (backup/'manifest.json').write_bytes(enc(manifest))
 for p,b in changed.items():
  dest=r/p;assert dest.resolve().is_relative_to(r);dest.parent.mkdir(parents=True,exist_ok=True)
  temp=dest.with_name(dest.name+'.johto-'+stamp+'.tmp');assert not temp.exists();temp.write_bytes(b);temp.replace(dest)
 report.update(applied=True,backup=str(backup));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
