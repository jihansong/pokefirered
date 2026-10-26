"""Rebuild four private space interiors from unchanged FRLG/Emerald source pixels.

Explicit --write is required; otherwise all derived outputs are checked only.
No script/text/trainer/flag tables, flight assets, primary tiles or save data edited.
"""
from pathlib import Path
import argparse,copy,hashlib,json,struct
NAMES=['HoennSpaceportTerminal','HoennSpacecraftCabin','HoennSpacecraftEngineering','HoennOrbitalObservatory']
FOLDER='data/tilesets/secondary/ty_space_interior_v3'
def jb(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def build(S):
 inputs={};out={}
 def read(rel):
  b=(S/rel).read_bytes();inputs[rel]=hashlib.sha256(b).hexdigest();return b
 def prof(pri,sec,cut,pcut):
  p=f'data/tilesets/primary/{pri}';q=f'data/tilesets/secondary/{sec}'
  pal=[]
  for i in range(13):
   rel=f'{p if i<pcut else q}/palettes/{i:02}.gbapal'
   pal.append(read(rel) if (S/rel).exists() else read(q+'/palettes.gbapal')[i*32:(i+1)*32])
  return {'name':sec,'cut':cut,'tiles':[read(p+'/tiles.4bpp'),read(q+'/tiles.4bpp')],'mt':[read(p+'/metatiles.bin'),read(q+'/metatiles.bin')],'pal':pal}
 base=prof('em_general','ty_space_style_v2_interior',512,6)
 anne=prof('general','ss_anne',640,7);bike=prof('em_general','em_bike_shop',512,6);facility=prof('em_general','em_facility',512,6)
 layouts=json.loads(read('data/layouts/layouts.json'))['layouts']
 maps={n:json.loads(read(f'data/maps/{n}/map.json')) for n in NAMES}
 patch={n:json.loads(read(f'tools/hoenn_import/patches/{n}.json')) if (S/f'tools/hoenn_import/patches/{n}.json').exists() else {} for n in NAMES}
 # The two old battle actors keep their original disguised source graphics.
 maps[NAMES[1]]['object_events'][0]['graphics_id']='OBJ_EVENT_GFX_CAPTAIN'
 maps[NAMES[1]]['object_events'][1]['flag']='FLAG_HOENN_SPACE_CABIN_CLEARED'
 maps[NAMES[2]]['object_events'][0]['flag']='FLAG_HOENN_SPACE_ENGINEERING_CLEARED'
 for name,index,flag in [(NAMES[1],1,'FLAG_HOENN_SPACE_CABIN_CLEARED'),(NAMES[2],0,'FLAG_HOENN_SPACE_ENGINEERING_CLEARED')]:
  o=maps[name]['object_events'][index];ovs=patch[name].setdefault('object_overrides',[])
  ovs[:]=[v for v in ovs if v.get('match_script')!=o['script']]
  ovs.append({'match_script':o['script'],'script':o['script'],'flag':flag})
 ovs=patch[NAMES[1]].setdefault('object_overrides',[]);ovs[:]=[v for v in ovs if v.get('match_script')!='Space_CabinCaptain'];ovs.append({'match_script':'Space_CabinCaptain','script':'Space_CabinCaptain','graphics_id':'OBJ_EVENT_GFX_CAPTAIN'})
 def npc(script,gfx,x,y,face='DOWN',flag='0'):
  return {'type':'object','graphics_id':'OBJ_EVENT_GFX_'+gfx,'x':x,'y':y,'elevation':3,'movement_type':'MOVEMENT_TYPE_FACE_'+face,'movement_range_x':0,'movement_range_y':0,'trainer_type':'TRAINER_TYPE_NONE','trainer_sight_or_berry_tree_id':'0','script':script,'flag':flag}
 added={NAMES[1]:[npc('Space_CabinPilot','SAILOR',12,5),npc('Space_CabinAttendant','CABLE_CLUB_RECEPTIONIST',7,10),npc('Space_CabinPassengerA','MAN',4,9),npc('Space_CabinPassengerB','WOMAN_1',14,12)],NAMES[3]:[npc('Space_JirachiEncounter','MOON_STONE',12,6,flag='FLAG_HIDE_HOENN_ORBITAL_JIRACHI')]}
 for name,items in added.items():
  labels={v['script'] for v in items};maps[name]['object_events']=[v for v in maps[name]['object_events'] if v['script'] not in labels]+items
  patch[name]['object_events']=[v for v in patch[name].get('object_events',[]) if v.get('script') not in labels]+items
 grids={};reports=[]
 for name,m in maps.items():
  l=next(v for v in layouts if v.get('id')==m['layout']);w,h=l['width'],l['height'];g=[0x3400|1004]*(w*h)
  def cell(x,y,n,blocked=False):
   assert 0<=x<w and 0<=y<h,(name,x,y);g[y*w+x]=0x3000|n|(0x400 if blocked else 0)
  def row(x,y,ids,blocked=True):
   for dx,n in enumerate(ids):cell(x+dx,y,n,blocked)
  def rect(x0,y0,x1,y1,n,blocked=False):
   for y in range(y0,y1+1):
    for x in range(x0,x1+1):cell(x,y,n,blocked)
  left,right=(1,w-2) if name==NAMES[0] else (2,w-3)
  rect(left+1,2,right-1,h-3,752)
  row(left,1,[901]+[902]*(right-left-1)+[903]);row(left,h-2,[906]+[907]*(right-left-1)+[908])
  for y in range(2,h-2):cell(left,y,904,True);cell(right,y,905,True)
  if name==NAMES[0]:
   row(5,4,[942,943]);row(8,4,[940,941]);row(16,4,[942,943])
   row(4,11,[940,941]);row(4,12,[942,943])
   for y in [10,12]:
    for x in [15,16,18,19]:cell(x,y,900,True)
   # Leave the registration clerk and both ordinary entrance corridors clear.
   rect(11,2,13,15,752);rect(5,7,20,8,752)
  elif name==NAMES[1]:
   # Forward cockpit / aft passenger service. Native wall/windows are complete.
   row(7,2,[733]*7)
   row(8,3,[944,945,946,944,945,946]);cell(10,4,900,True);cell(12,4,900,True)
   for x in [4,5]:
    for y in [8,10,12]:cell(x,y,900,True)
   for x in [14,15]:
    for y in [11,13]:cell(x,y,900,True)
   row(14,6,[944,945,946]);row(15,7,[940,941])
   # Separate pilot compartment visually without blocking either pilot's front.
   row(3,6,[901,902,903])
   rect(9,5,11,13,752);rect(6,7,16,7,752);rect(6,9,13,9,752)
   cell(10,14,752)  # Existing return trigger: open airlock, not a wall.
  elif name==NAMES[2]:
   row(4,2,[942,943]);row(11,2,[940,941]);row(14,2,[942,943])
   for xx in [3,13]:
    for yy in range(4):row(xx,10+yy,[920+yy*4+dx for dx in range(4)])
   # Four-meter-wide maintenance aisle and two original consoles remain usable.
   rect(8,3,11,13,752);rect(3,6,16,8,752)
   cell(12,4,531,True)
  else:
   # Restore the exact native Earth window, with a broad unobstructed encounter deck.
   for yy in range(4):row(6,1+yy,[850+yy*8+dx for dx in range(8)])
   row(5,0,[901]+[902]*8+[903])
   for yy in range(1,5):cell(5,yy,904,True);cell(14,yy,905,True)
   row(5,5,[906]+[907]*8+[908])
   row(3,7,[942,943]);row(15,7,[942,943])
   rect(10,6,14,7,752);row(11,8,[913,913,913,913],False)
   row(4,13,[900,900]);row(15,13,[900,900]);cell(10,8,531,True)
  # No new event coordinate is shifted. All object footprints are walkable floor.
  for o in m['object_events']:cell(o['x'],o['y'],752)
  for ev in m['coord_events']:cell(ev['x'],ev['y'],752)
  before=struct.unpack('<%dH'%(w*h),read(l['blockdata_filepath']))
  for ev in m['warp_events']:
   x,y=ev['x'],ev['y'];word=before[y*w+x];assert word&1023 in [1000,1001,1002,1003]
   cell(x,y,word&1023)
   inward={1000:(0,-1),1001:(0,1),1002:(-1,0),1003:(1,0)}[word&1023]
   for d in [1,2]:cell(x+inward[0]*d,y+inward[1]*d,752)
  for ev in m['bg_events']:cell(ev['x'],ev['y'],531,True)
  grids[name]=(l,g)
 # Keep all existing referenced source pixel blocks and the black opaque border.
 mt=bytearray(base['mt'][1]);attrs=bytearray(read('data/tilesets/secondary/ty_space_style_v2_interior/metatile_attributes.bin'))
 # Opaque void is background, never a foreground mask over elevation-3 actors.
 struct.pack_into('<I',attrs,(1004-512)*4,0x20000000);tiles=bytearray(base['tiles'][1]);pals=bytearray(read('data/tilesets/secondary/ty_space_style_v2_interior/palettes.gbapal'))
 def native_colors(p,ids,only_palette,upper_only=False):
  colors=set()
  for n in ids:
   vs=struct.unpack_from('<8H',p['mt'][n>=p['cut']],(n-p['cut'] if n>=p['cut'] else n)*16)
   for j,v in enumerate(vs):
    if v>>12!=only_palette or (upper_only and j<4):continue
    tid=v&1023;q=tid>=p['cut'];k=tid-p['cut'] if q else tid;raw=p['tiles'][q][k*32:(k+1)*32];pal=struct.unpack('<16H',p['pal'][only_palette])
    colors|={pal[i] for b in raw for i in [b&15,b>>4] if i or j<4}
  return colors
 reactor=[720,721,722,723,728,729,730,731,736,737,738,739,744,745,746,747]
 shared=native_colors(anne,[651,652,653,654,655],7)|native_colors(anne,[809],7,True)|native_colors(bike,reactor,6)
 assert len(shared)<=15,len(shared)
 # Lossless native index repacking: fifteen original RGB555 colors share one
 # bank. Index0 remains transparent. No pixel/color quantization or repainting.
 pals[7*32:8*32]=struct.pack('<16H',*([0]+sorted(shared)+[0]*(15-len(shared))))
 pals[10*32:11*32]=bike['pal'][10]
 unchanged={n&1023 for _,g in grids.values() for n in g if n&1023<900 or n&1023>=1000}|{531,1000,1001,1002,1003,1004}
 protected={1021}
 for n in unchanged:
  if n>=512:
   protected|={v&1023 for v in struct.unpack_from('<8H',mt,(n-512)*16) if v&1023>=512}
 original_protected=set(protected);tile_proof=[];aliases={};free=[i for i in range(512,1024) if i not in protected]
 def words(p,n):return list(struct.unpack_from('<8H',p['mt'][n>=p['cut']],(n-p['cut'] if n>=p['cut'] else n)*16))
 def copyword(p,v,palette_map,transparent=False):
  old=v&1023;source_raw=p['tiles'][old>=p['cut']][((old-p['cut']) if old>=p['cut'] else old)*32:((old-p['cut']) if old>=p['cut'] else old)*32+32];assert len(source_raw)==32
  srcpal=v>>12;targetpal=palette_map.get(srcpal,srcpal)
  source_colors=struct.unpack('<16H',p['pal'][srcpal]);target_colors=struct.unpack('<16H',pals[targetpal*32:(targetpal+1)*32]);raw=bytearray()
  for b in source_raw:
   new=[]
   for index in [b&15,b>>4]:
    if transparent and index==0:new.append(0)
    else:
     color=source_colors[index];candidates=[i for i,c in enumerate(target_colors) if c==color and (i or not transparent)];assert candidates,(srcpal,targetpal,color)
     new.append(index if index in candidates else candidates[0])
   raw.append(new[0]|(new[1]<<4))
  raw=bytes(raw)
  if old<p['cut'] and p['cut']==512 and raw==base['tiles'][0][old*32:(old+1)*32]:target=old
  elif not any(raw):target=0;assert raw==base['tiles'][0][:32]
  else:
   found=next((t for t in sorted(protected) if bytes(tiles[(t-512)*32:(t-511)*32])==raw),None)
   if found is None:
    target=free.pop(0);protected.add(target);tiles[(target-512)*32:(target-511)*32]=raw
   else:target=found
  assert targetpal<13
  # Native color indices and every 8x8 nibble are unchanged (including index0).
  for sb,tb in zip(source_raw,raw):
   for si,ti in [(sb&15,tb&15),(sb>>4,tb>>4)]:
    assert (si==0 and ti==0) if transparent and si==0 else source_colors[si]==target_colors[ti]
  tile_proof.append({'source_tileset':p['name'],'source_cut':p['cut'],'source_tile':old,'target_tile':target,'source_palette':srcpal,'target_palette':targetpal,'transparent':transparent,'source_raw_sha256':hashlib.sha256(source_raw).hexdigest(),'target_raw_sha256':hashlib.sha256(raw).hexdigest(),'visible_RGB555_and_transparency_exact':True})
  return (v&0xc00)|target|(targetpal<<12)
 def clone(dest,p,src,pm,upper_only=False,vflip=False):
  vals=words(p,src)
  vals=(words(base,752)[:4]+[copyword(p,v,pm,True) for v in vals[4:]]) if upper_only else [copyword(p,v,pm,i>=4) for i,v in enumerate(vals)]
  if vflip:vals=[vals[i]^0x800 for i in [2,3,0,1,6,7,4,5]]
  struct.pack_into('<8H',mt,(dest-512)*16,*vals);struct.pack_into('<I',attrs,(dest-512)*4,0x20000000 if dest in {900, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 940, 941, 942, 943, 944, 945, 946} else 0)
  aliases[dest]={'source_tileset':p['name'],'source_cut':p['cut'],'source_metatile':src,'upper_only':upper_only,'vflip':vflip}
 # Side-wall black source641 is index15 black in SSAnne bank11; exact RGB555
 # matches existing native opaque-black bank12, despite other unused palette colors.
 clone(900,anne,809,{7:7},upper_only=True)
 for dest,src in [(901,651),(902,652),(903,653),(904,654),(905,655)]:clone(dest,anne,src,{7:7,11:12})
 for dest,src in [(906,651),(907,652),(908,653)]:clone(dest,anne,src,{7:7},vflip=True)
 # Existing original yellow caution-edge floor; normal walkable platform.
 clone(913,facility,769,{})
 for yy,ids in enumerate([[720,721,722,723],[728,729,730,731],[736,737,738,739],[744,745,746,747]]):
  for xx,src in enumerate(ids):clone(920+yy*4+xx,bike,src,{6:7,10:10})
 for dest,src in [(940,872),(941,873),(942,880),(943,881)]:clone(dest,facility,src,{})
 for dest,src in [(944,885),(945,886),(946,887)]:clone(dest,facility,src,{})
 # Reject unintended use of donor bank7/8/10 after reassigning those banks.
 for name,(l,g) in grids.items():
  used={n&1023 for n in g}|{1004}
  for n in used:
   if n<512:vs=struct.unpack_from('<8H',base['mt'][0],n*16)
   else:vs=struct.unpack_from('<8H',mt,(n-512)*16)
   assert all(v>>12<13 and v&1023<1024 for v in vs),(name,n)
   if n in unchanged and n<1000:assert not ({v>>12 for v in vs}&{7,10}),(name,n,'old palette dependency')
  raw=struct.pack('<%dH'%len(g),*g)
  out[l['blockdata_filepath']]=raw;out[f'tools/hoenn_import/patches/{name}.blockdata.bin']=raw
  out[l['border_filepath']]=struct.pack('<4H',*([0x3400|1004]*4));out[f'tools/hoenn_import/patches/{name}.space-border.bin']=out[l['border_filepath']]
  out[f'data/maps/{name}/map.json']=jb(maps[name]);out[f'tools/hoenn_import/patches/{name}.json']=jb(patch[name])
  reports.append({'name':name,'width':l['width'],'height':l['height'],'used_metatiles':sorted(used)})
 for n,b in [('tiles.4bpp',tiles),('metatiles.bin',mt),('metatile_attributes.bin',attrs),('palettes.gbapal',pals)]:out[FOLDER+'/'+n]=bytes(b)
 header=read('src/data/tilesets/ty_space_style_v2.h').replace(b'data/tilesets/secondary/ty_space_style_v2_interior/',(FOLDER+'/').encode());out['src/data/tilesets/ty_space_style_v2.h']=header
 registry=json.loads(read('tools/hoenn_import/space_map_styles_v2.json'))
 for rel,expected in registry.get('interior_v3',{}).get('inputs_sha256',{}).items():assert inputs.get(rel)==expected,('original source asset changed',rel)
 registry['profiles']['Interior']['folder']=FOLDER;registry['interior_v3']={'generator':'tools/hoenn_import/build_space_interiors_v3.py','source_pixels_only':True,'primary_palette_0_to_5_unchanged':True,'secondary_banks':[6,7,8,9,10,11,12],'crew_and_encounter_coordinates_preserved':True,'inputs_sha256':{k:v for k,v in inputs.items() if k.startswith('data/tilesets/')}};out['tools/hoenn_import/space_map_styles_v2.json']=jb(registry)
 return out,{'source_inputs_sha256':inputs,'maps':reports,'used_original_pixel_tiles':len(original_protected),'new_copied_native_tiles':len(protected-original_protected),'private_secondary_tiles':512,'highest_palette':12,'tile_copy_proof':tile_proof,'aliases':aliases,'primary_tiles_changed':0,'flight_assets_changed':0,'map_IDs_sizes_warps_changed':0}
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path);p.add_argument('--write',action='store_true');p.add_argument('--report',type=Path);a=p.parse_args();out,proof=build(a.root);target=a.out or a.root
 for rel,raw in out.items():
  dest=target/rel
  if a.write:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
  else:assert dest.read_bytes()==raw,rel
 if a.report:a.report.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'outputs':len(out),'source_pixels_only':True,'new_copied_tiles':proof['new_copied_native_tiles'],'write':a.write}))
if __name__=='__main__':main()
