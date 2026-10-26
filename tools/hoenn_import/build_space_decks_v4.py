"""Seventeen private GBA ship interiors from exact original source pixels.

Pure build(root, contract) returns asset/block/border outputs. No map event,
script, layout/group registration, save, flight asset or primary tiles changed.
CLI requires --write for output. All secondary profiles use Emerald512/6 split.
"""
from pathlib import Path
from collections import deque
import argparse,copy,hashlib,json,struct

def jb(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def build(S,contract=None):
 S=Path(S);inputs={};out={};reports=[];allcopies=[]
 def read(rel):
  b=(S/rel).read_bytes();inputs[rel]=hashlib.sha256(b).hexdigest();return b
 if contract is None:contract=json.loads(read('tools/hoenn_import/space_deck_v4_contract.json'))
 def prof(name,pri,sec,em):
  p='data/tilesets/primary/'+pri;q='data/tilesets/secondary/'+sec;pc=6 if em else 7;pals=[]
  for i in range(13):
   rel=f'{p if i<pc else q}/palettes/{i:02}.gbapal';raw=read(rel) if (S/rel).exists() else read(q+'/palettes.gbapal')[i*32:(i+1)*32];pals.append(struct.unpack('<16H',raw))
  return {'name':name,'cut':512 if em else 640,'tiles':[read(p+'/tiles.4bpp'),read(q+'/tiles.4bpp')],'mt':[read(p+'/metatiles.bin'),read(q+'/metatiles.bin')],'attr':[read(p+'/metatile_attributes.bin'),read(q+'/metatile_attributes.bin')],'pal':pals}
 P={};P['v3']=prof('v3','em_general','ty_space_interior_v3',True);P['anne']=prof('anne','general','ss_anne',False);P['tidal']=prof('tidal','em_general','em_inside_ship',True);P['facility']=prof('facility','em_general','em_facility',True);P['pc']=prof('pc','building','pokemon_center',False);P['game']=prof('game','building','game_corner',False);P['power']=prof('power','building','power_plant',False);P['arena']=prof('arena','em_building','em_battle_arena',True);P['mart']=prof('mart','building','mart',False)
 layouts=json.loads(read('data/layouts/layouts.json'))['layouts']
 def words(ref):
  fam,n=ref[:2];p=P[fam];q=int(n>=p['cut']);i=n-p['cut'] if q else n;return struct.unpack_from('<8H',p['mt'][q],i*16)
 def attribute(ref):
  fam,n=ref[:2];p=P[fam];q=int(n>=p['cut']);i=n-p['cut'] if q else n;v=struct.unpack_from('<I',p['attr'][q],i*4)[0]
  return v if len(ref)<3 or ref[2] is None else ref[2]
 def tile_raw(p,v):
  n=v&1023;q=int(n>=p['cut']);i=n-p['cut'] if q else n;raw=p['tiles'][q][i*32:(i+1)*32];assert len(raw)==32;return raw
 def packcolors(groups):
  # Whole source palette usage stays together; exact nonzero RGB555 colors.
  keys=sorted(groups,key=lambda k:(-len(groups[k]),str(k)));bins=[];assign={};nodes=[0]
  def solve(i):
   nodes[0]+=1
   assert nodes[0]<2000000,'Exact palette search budget exceeded; reduce mixed donors'
   if i==len(keys):return True
   k=keys[i];c=groups[k];choices=sorted(range(len(bins)),key=lambda j:(len(bins[j]|c)-len(bins[j]),j));seen=set()
   for j in choices:
    sig=tuple(sorted(bins[j]));union=bins[j]|c
    if sig in seen or len(union)>15:continue
    seen.add(sig);old=bins[j];bins[j]=union;assign[k]=j
    if solve(i+1):return True
    bins[j]=old;assign.pop(k)
   if len(bins)<7:
    bins.append(set(c));assign[k]=len(bins)-1
    if solve(i+1):return True
    bins.pop();assign.pop(k)
   return False
  assert solve(0),('Palette7 exact packing impossible',[(k,len(v)) for k,v in groups.items()])
  return bins,assign,nodes[0]
 for cfg in contract['maps']:
  role=cfg['role'];name=cfg['map'];w,h=cfg['size'];m=json.loads(read(f'data/maps/{name}/map.json'));l=next(v for v in layouts if v.get('id')==m['layout']);assert [l['width'],l['height']]==[w,h]
  # One private profile per room: coherent donors never compete with other rooms.
  folder='data/tilesets/secondary/ty_space_v4_'+role.lower();grid=[('v3',1004)]*(w*h);blocked=[True]*(w*h);occupied=set();pieces=[]
  floor={'Cabin':('pc',641),'CaptainsOffice':('anne',664),'CrewQuarters':('anne',796),'CrewMess':('anne',665),'FoodCourt':('tidal',568),'Lounge':('game',657),'GameRoom':('game',657),'BattleDeck':('arena',514),'CabinCorridor':('anne',664),'GuestRoom1':('anne',796),'GuestRoom2':('anne',796),'GuestRoom3':('anne',796),'CargoHold':('tidal',525),'Engineering':('power',671)}.get(role,('facility',752))
  hard={tuple(a) for a in cfg['must_open']};targets={tuple(a['target']) for a in cfg['interaction_tiles']}
  def setcell(x,y,ref,collision=True):
   assert 0<=x<w and 0<=y<h,(role,x,y);grid[y*w+x]=tuple(ref);blocked[y*w+x]=collision
  for y in range(2,h-2):
   for x in range(2,w-2):setcell(x,y,floor,False)
  for x in range(1,w-1):setcell(x,1,('v3',901 if x==1 else 903 if x==w-2 else 902));setcell(x,h-2,('v3',906 if x==1 else 908 if x==w-2 else 907))
  for y in range(2,h-2):setcell(1,y,('v3',904));setcell(w-2,y,('v3',905))
  # Room silhouettes follow their purpose without changing registered dimensions.
  # Bridge narrows into its aft entry; the cabin corridor is actually a corridor.
  if role in ['Cockpit','CabinCorridor','CaptainsOffice']:
   for y in range(h):
    for x in range(w):setcell(x,y,('v3',1004),True)
   def hull(x0,y0,x1,y1):
    for yy in range(y0+1,y1):
     for xx in range(x0+1,x1):setcell(xx,yy,floor,False)
    for xx in range(x0,x1+1):setcell(xx,y0,('v3',901 if xx==x0 else 903 if xx==x1 else 902));setcell(xx,y1,('v3',906 if xx==x0 else 908 if xx==x1 else 907))
    for yy in range(y0+1,y1):setcell(x0,yy,('v3',904));setcell(x1,yy,('v3',905))
   if role=='Cockpit':
    hull(2,1,17,8);hull(7,7,13,14)
    for yy in [7,8]:
     for xx in range(8,13):setcell(xx,yy,floor,False)
    # Remove the two union-rectangle caps inside the bridge floor.
    for xx in [7,13]:setcell(xx,7,floor,False)
   elif role=='CabinCorridor':hull(1,1,w-2,6)
   else:hull(2,1,13,11)
  if role=='FoodCourt':
   # Deliberate full-width service apron, not small donor-floor rectangles.
   for yy in range(2,6):
    for xx in range(2,w-2):setcell(xx,yy,('anne',665),False)
  if role=='Cabin':
   for yy in range(2,7):
    for xx in range(2,9):setcell(xx,yy,('mart',641),False)
  if role=='Engineering':
   for x0 in [2,13]:
    for yy in range(8,14):
     for xx in range(x0,x0+6):setcell(xx,yy,('power',708),False)
  if role=='BattleDeck':
   for yy in [3,4]:
    for xx in range(2,w-2):setcell(xx,yy,('pc',641),False)
   for yy in [12,13]:
    for xx in list(range(2,8))+list(range(17,w-2)):setcell(xx,yy,('pc',641),False)
  def place(label,fam,rows,x,y,required=True,collision=True):
   hh=len(rows);ww=len(rows[0]);cells={(x+xx,y+yy) for yy in range(hh) for xx in range(ww)}
   valid=all(1<=xx<w-1 and 1<=yy<h-1 for xx,yy in cells) and not(cells&hard) and not(cells&occupied)
   if not valid and not required:
    choices=sorted([(xx,yy) for yy in range(2,h-hh-1) for xx in range(2,w-ww-1)],key=lambda a:(abs(a[0]-x)+abs(a[1]-y),a[1],a[0]))
    found=next(((xx,yy) for xx,yy in choices if not({(xx+dx,yy+dy) for dy in range(hh) for dx in range(ww)}&(hard|occupied))),None)
    assert found,('No complete furniture position',role,label)
    x,y=found;cells={(x+xx,y+yy) for yy in range(hh) for xx in range(ww)};valid=True
   assert valid,('Required furniture hits actor/entry',role,label,x,y,sorted(cells&hard),sorted(cells&occupied))
   for yy,row in enumerate(rows):
    for xx,n in enumerate(row):setcell(x+xx,y+yy,(fam,n),collision)
   occupied.update(cells);pieces.append({'label':label,'source_profile':fam,'metatile_rows':rows,'xy':[x,y],'complete_shape':True,'blocked':collision})
  bed=[[808,809,810],[816,817,818]];desk=[[773,774,775],[781,782,783]];roundtable=[[598,599],[606,607]];science=[[867,868],[875,876]];chair=[ [820] ]
  if role.startswith('GuestRoom'):
   place('complete3x2_bed','anne',bed,3,3);place('complete_desk','anne',[[824,825],[832,833],[840,841]],7,2,False);place('real_chair','anne',chair,6,7,False);place('plant','anne',[[811],[819]],9,2,False)
  elif role=='CrewQuarters':
   for x,y in [(3,3),(12,3),(3,10),(12,10)]:place('complete3x2_bed','anne',bed,x,y,False)
   place('crew_desk','anne',[[824,825],[832,833],[840,841]],6,2,False);place('real_chair','anne',chair,7,10,False)
   for x in list(range(2,7))+list(range(12,18)):
    if (x,6) not in hard:setcell(x,6,('v3',901 if x in [2,12] else 903 if x in [6,17] else 902),True)
  elif role=='CaptainsOffice':
   place('captains_book_desk','anne',desk,4,3,False);place('bookshelf','anne',[[762],[770]],12,2,False);place('wall_map','anne',[[755,756]],10,2,False);place('office_chair','anne',[[771]],11,8,False)
  elif role in ['Cockpit','Navigation']:
   if role=='Cockpit':
    place('forward_window_bank','facility',[[760]*8,[768]*8,[870]*8],5,1,False)
    for x in [5,12]:place('complete_flight_console','facility',science,x,3,False)
    for x in [7,13]:place('real_control_stool','facility',[[865]],x,5,False)
   else:
    for x in [3,14]:place('forward_window_bank','facility',[[760]*3,[768]*3,[870]*3],x,1,False)
    place('communications_desk','facility',science,4,4,False);place('navigation_console','facility',science,12,3);place('navigation_display','facility',[[885,886,887]],13,10,False);place('communications_stool','facility',[[865]],5,7,False)
  elif role=='Cabin':
   # Preserve existing eight actor positions. Separate counter/medical service.
   place('complete_merchandise_shelves','mart',[[658,659,660],[666,667,668],[674,675,676]],4,1,False)
   place('complete_healing_station','pc',[[681,682,683],[689,690,691],[697,700,700]],13,4,False)
   place('boarding_status_desk','facility',science,9,3,False)
   for x,y in [(4,11),(5,11),(15,11),(16,11)]:place('waiting_chair','pc',[[757]],x,y,False)
   # Full PC vertical appliance: cap/middle/base. Base is original walkable front.
   setcell(3,3,('pc',645),True);setcell(3,4,('pc',98),True);setcell(3,5,('pc',661),False)
   pieces.append({'label':'complete_PC_with_reserved_off_on_middle','source_profile':'pc','metatile_rows':[[645],[98],[661]],'xy':[3,3],'complete_shape':True,'blocked':'middle/cap only; native front base walkable'})
  elif role=='Lounge':
   # Complete original green service counter, not dining-room kitchen units.
   place('complete_native_bar_counter','game',[[664]+[665]*6+[666],[672]+[673]*6+[674]],7,3)
   for xx in [8,10,12,14]:place('native_bar_stool','facility',[[865]],xx,6)
   for xx in [12,13,15,16]:place('native_waiting_seat','pc',[[757]],xx,12,False)
   place('bar_back_service_shelf','anne',[[762],[770]],4,2)
  elif role in ['CrewMess','FoodCourt']:
   # Variable-length original kitchen units retain complete top/body/end caps.
   place('complete_short_sink_worktop','anne',[[712,713],[722,723],[730,731]],3,2,False)
   place('complete_short_food_worktop','anne',[[712,713],[720,721],[728,729]],13,2,False)
   for x,y in [(3,10),(13,10)]:
    place('complete_dining_table','tidal',roundtable,x,y,False);place('native_dining_chair','tidal',[[608]],x-1,y+1,False);place('native_dining_chair','tidal',[[609]],x+2,y+1,False)
  elif role=='GameRoom':
   place('complete_front_slot_machine','game',[[645,646],[653,654],[710,788]],10,2)
   place('complete_front_slot_machine','game',[[645,646],[653,654],[710,788]],14,2,False)
   # Original game-room chairs are walkable standing/sitting approach tiles.
   for x in [10,14]:setcell(x,5,('game',683),False)
  elif role=='BattleDeck':
   # Emerald's complete8x6 arena/platform, copied including its lower edge.
   arena=[[552+yy*8+xx for xx in range(8)] for yy in range(5)]+[[541,551,551,542,541,551,551,542]]
   for yy,row in enumerate(arena):
    for xx,n in enumerate(row):setcell(8+xx,5+yy,('arena',n),False)
   pieces.append({'label':'complete_original_Emerald_battle_platform','source_profile':'arena','metatile_rows':arena,'xy':[8,5],'complete_shape':True,'blocked':False})
   for x,y in [(4,4),(6,4),(17,4),(19,4),(4,12),(6,12)]:place('spectator_chair','pc',[[757]],x,y,False)
  elif role=='CabinCorridor':
   for x in [6,11,16,21]:place('porthole_trim','anne',[[826]],x,1,False)
   for x in [6,15]:place('corridor_chair','anne',[[771]],x,5,False)
  elif role=='CargoHold':
   cargo=[[736,737,738,736,737,738],[747,748,749,744,745,746],[755,756,757,752,753,754],[743,743,743,743,743,758]]
   for x,y in [(3,2),(15,2),(3,11),(15,11)]:place('complete_crate_group','tidal',cargo,x,y,False)
  elif role=='Engineering':
   #744..746 are source background wall, not part of the generator silhouette.
   machine=[[752,753,754],[760,761,762],[768,769,770]]
   for x,y in [(3,9),(14,9)]:place('complete_PowerPlant_generator','power',machine,x,y,False)
   place('complete_service_panel','power',[[751,750],[759,758]],12,3)
  elif role=='Observatory':
   place('exact_existing_Earth_window','v3',[[850+yy*8+x for x in range(8)] for yy in range(4)],6,1,False)
   # Four sides of the viewport are complete hull pieces, including bottom frame.
   place('viewport_lower_frame','v3',[[906]+[907]*8+[908]],5,5,False)
   for xx in range(5,15):setcell(xx,0,('v3',901 if xx==5 else 903 if xx==14 else 902),True)
   for yy in range(1,5):setcell(5,yy,('v3',904),True);setcell(14,yy,('v3',905),True)
   place('observation_console','facility',science,9,7)
   for x in [4,5,6,14,15,16]:place('observation_stool','facility',[[865]],x,13,False)
  # Interaction targets which denote physical furniture must not be open floors.
  for a in cfg['interaction_tiles']:
   x,y=a['target']
   if role=='CrewMess':
    # A complete native communal table; target10,8 is its bottom-left tile.
    for yy,row in enumerate(roundtable):
     for xx,n in enumerate(row):
      assert (10+xx,7+yy) not in hard;setcell(10+xx,7+yy,('tidal',n),True)
    pieces.append({'label':'communal_rest_table','source_profile':'tidal','metatile_rows':roundtable,'xy':[10,7],'complete_shape':True,'blocked':True})
   elif role in ['CrewQuarters','GuestRoom1','GuestRoom2','GuestRoom3']:
    assert blocked[y*w+x],(role,'rest target must be bed')
   elif role=='CargoHold':assert blocked[y*w+x],(role,'cargo clue must be crate')
   else:assert blocked[y*w+x],(role,'missing actual console',a)
  # Arrow portals occupy the actual contract rows; no auto door-step trap.
  warp_refs={}
  for a in cfg['warps']:
   x,y=a['xy'];direction=a['outward'];dx,dy={'N':(0,1),'S':(0,-1),'E':(-1,0),'W':(1,0)}[direction]
   for t in range(3):setcell(x+dx*t,y+dy*t,floor,False)
   for t in [1,2]:
    xx,yy=x+dx*t,y+dy*t
    if direction in ['N','S'] and (xx+1,yy) not in occupied:setcell(xx+1,yy,floor,False)
    elif direction in ['E','W'] and (xx,yy+1) not in occupied:setcell(xx,yy+1,floor,False)
   behavior={'S':0x65,'N':0x64,'E':0x62,'W':0x63}[direction];ref=('anne',959) if direction in ['N','S'] else floor;ref=(*ref,0x20000000|behavior);setcell(x,y,ref,False);warp_refs[1000+{'S':0,'N':1,'E':2,'W':3}[direction]]=ref
  for x,y in hard:
   if not any(a['xy']==[x,y] for a in cfg['warps']):
    assert (x,y) not in occupied,(role,'hard footprint hidden by furniture',x,y)
    if blocked[y*w+x]:setcell(x,y,floor,False)
  # Deliberate source-pixel-preserving layer variants wherever an actor may stand
  # below NORMAL/SPLIT foreground. Untouched inaccessible walls retain donors.
  layer_variants=[]
  for i,isblocked in enumerate(list(blocked)):
   if isblocked:continue
   x,y=i%w,i//w
   for yy in [y-1,y]:
    if yy<0:continue
    j=yy*w+x;ref=grid[j];v=attribute(ref);kind=v>>29&3
    if kind in [0,2] and any(any(b for b in tile_raw(P[ref[0]],n)) for n in words(ref)[4:]):
     replacement=(*ref[:2],(v&~0x60000000)|0x20000000);grid[j]=replacement;layer_variants.append({'xy':[x,yy],'source':ref,'variant':replacement,'reason':'walkable_actor_foot_or_head_foreground_clearance'})
  # Reserve legacy scripts and new scoped-PC animation IDs.
  reserved={1004:('v3',1004,0x20000000),**warp_refs}
  if role=='Engineering':reserved[531]=grid[4*w+12]
  if role=='Observatory':reserved[531]=grid[8*w+10]
  if role=='Cabin':reserved[1005]=grid[4*w+3];reserved[1006]=('pc',99,0x20000000|(attribute(('pc',99))&~0x60000000))
  refs=set(grid)|set(reserved.values());groups={}
  for ref in refs:
   pp=P[ref[0]]
   for v in words(ref):
    key=(ref[0],v>>12);raw=tile_raw(pp,v);groups.setdefault(key,set()).update(pp['pal'][v>>12][n] for b in raw for n in [b&15,b>>4] if n)
  bins,assignment,nodes=packcolors(groups);pals=bytearray().join(struct.pack('<16H',*p) for p in P['v3']['pal']);pals=bytearray(pals)
  for i in range(7):
   colors=sorted(bins[i]) if i<len(bins) else [];struct.pack_into('<16H',pals,(6+i)*32,0,*colors,*([0]*(15-len(colors))))
  tiles=bytearray(512*32);mts=bytearray(512*16);attrs=bytearray(512*4);tile_ids={bytes(32):512};copied=[]
  def copyword(ref,v):
   pp=P[ref[0]];raw=tile_raw(pp,v);bank=6+assignment[(ref[0],v>>12)];colors=struct.unpack_from('<16H',pals,bank*32);dest=bytearray()
   for b in raw:
    ns=[]
    for index in [b&15,b>>4]:
     n=0 if index==0 else next(k for k in range(1,16) if colors[k]==pp['pal'][v>>12][index]);ns.append(n)
    dest.append(ns[0]|ns[1]<<4)
   dest=bytes(dest)
   if dest not in tile_ids:
    tid=512+len(tile_ids);assert tid<1024,(role,'512 tile budget');tile_ids[dest]=tid;tiles[(tid-512)*32:(tid-511)*32]=dest
   tid=tile_ids[dest]
   for a,b in zip(raw,dest):
    for si,ti in [(a&15,b&15),(a>>4,b>>4)]:assert (si==ti==0) or si!=0 and ti!=0 and pp['pal'][v>>12][si]==colors[ti]
   copied.append({'source':ref[:2],'source_tile':v&1023,'source_palette':v>>12,'target_tile':tid,'target_palette':bank,'source_raw_sha256':hashlib.sha256(raw).hexdigest(),'target_raw_sha256':hashlib.sha256(dest).hexdigest(),'RGB555_alpha_exact':True})
   return tid|(v&0xc00)|(bank<<12)
  reserved_ids=set(reserved);ref_id={};ids={}
  for n,ref in sorted(reserved.items()):ids[n]=ref;ref_id.setdefault(ref,n)
  free=iter(n for n in range(512,1000) if n not in reserved_ids)
  for ref in sorted(refs,key=str):
   if ref not in ref_id:n=next(free);ids[n]=ref;ref_id[ref]=n
  for n,ref in ids.items():struct.pack_into('<8H',mts,(n-512)*16,*[copyword(ref,v) for v in words(ref)]);struct.pack_into('<I',attrs,(n-512)*4,attribute(ref))
  rawwords=[]
  for i,ref in enumerate(grid):rawwords.append(0x3000|(0x400 if blocked[i] else 0)|ref_id[ref])
  # Exact fixed target aliases, not just a matching picture under another ID.
  for n,xy in ([(531,[12,4])] if role=='Engineering' else [(531,[10,8])] if role=='Observatory' else [(1005,[3,4])] if role=='Cabin' else []):rawwords[xy[1]*w+xy[0]]=(rawwords[xy[1]*w+xy[0]]&~1023)|n
  for a in cfg['warps']:
   x,y=a['xy'];n=1000+{'S':0,'N':1,'E':2,'W':3}[a['outward']];rawwords[y*w+x]=0x3000|n
  # All hard footprints and adjacent standing tiles must be in one real graph.
  passable={i for i,v in enumerate(rawwords) if not(v>>10&3)};start=cfg['safe_anchor'][1]*w+cfg['safe_anchor'][0];seen={start};q=deque([start])
  while q:
   i=q.popleft();x,y=i%w,i//w
   for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    j=yy*w+xx
    if 0<=xx<w and 0<=yy<h and j in passable and j not in seen:seen.add(j);q.append(j)
  assert all(y*w+x in seen for x,y in hard),(role,'unreachable hard cell')
  block=struct.pack('<%dH'%len(rawwords),*rawwords);border=struct.pack('<4H',*([0x3400|1004]*4))
  out[l['blockdata_filepath']]=block;out[l['border_filepath']]=border;out[f'tools/hoenn_import/patches/{name}.blockdata.bin']=block;out[f'tools/hoenn_import/patches/{name}.space-border.bin']=border
  for fn,b in [('tiles.4bpp',tiles),('metatiles.bin',mts),('metatile_attributes.bin',attrs),('palettes.gbapal',pals)]:out[folder+'/'+fn]=bytes(b)
  reports.append({'role':role,'map':name,'size':[w,h],'secondary_symbol':cfg['secondary_tileset'],'folder':folder,'used_private_tiles':len(tile_ids),'palette_banks_used':len(bins),'palette_search_nodes':nodes,'metatile_count':len(ids),'pieces':pieces,'layer_clearance_variants':layer_variants,'passable_tiles':len(passable),'reachable_tiles':len(seen),'hard_footprints':len(hard),'all_hard_BFS_reachable':True,'metatile_source_map':{str(n):ref for n,ref in ids.items()},'tile_copy_proof':copied})
  allcopies.extend(copied)
 # Emit definitions fragment only. Parent integrates its include/registrations.
 header=['// Exact original pixel profiles for three ship decks;512/6 split.\n']
 for r in reports:
  tag=r['secondary_symbol'];folder=r['folder']
  for typ,suffix,fn in [('u32','Tiles','tiles.4bpp'),('u16','Palettes','palettes.gbapal'),('u16','Metatiles','metatiles.bin'),('u32','Attributes','metatile_attributes.bin')]:header.append(f'static const {typ} s{tag}{suffix}'+('[][16]' if suffix=='Palettes' else '[]')+f' = INCBIN_{"U32" if typ=="u32" else "U16"}("{folder}/{fn}");\n')
  header.append(f'const struct Tileset {tag} = {{ .isCompressed=FALSE, .isSecondary=TRUE, .isEmerald=TRUE, .tiles=s{tag}Tiles, .palettes=s{tag}Palettes, .metatiles=s{tag}Metatiles, .metatileAttributes=s{tag}Attributes, .callback=NULL }};\n')
 out['src/data/tilesets/ty_space_deck_v4.h']=''.join(header).encode()
 return out,{'status':'V4_STAGED_ORIGINAL_PIXEL_MAPS_ONLY_RUNTIME_PENDING','source_inputs_sha256':inputs,'maps':reports,'profiles':17,'maps_metadata_written':0,'flight_assets_changed':0,'primary_assets_changed':0,'RGB555_alpha_exact_tile_copies':len(allcopies),'new_art':0,'native_runs':0}

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--contract',type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--write',action='store_true');p.add_argument('--report',type=Path);a=p.parse_args();contract=json.loads(a.contract.read_text()) if a.contract else None;out,proof=build(a.root,contract)
 for rel,b in out.items():
  f=a.out/rel
  if a.write:f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
  else:assert f.read_bytes()==b,rel
 if a.report:a.report.write_bytes(jb(proof))
 print(json.dumps({'maps':17,'outputs':len(out),'write':a.write,'new_art':0}))
if __name__=='__main__':main()
