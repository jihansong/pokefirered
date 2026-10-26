"""Explicit 16px native-palette hull strokes, directional hatches and join caps."""
import struct

def image(P,ref):
 fam,n=ref[:2];p=P[fam];q=int(n>=p['cut']);i=n-p['cut'] if q else n;ws=struct.unpack_from('<8H',p['mt'][q],i*16);a=[[None]*16 for _ in range(16)]
 for k,v in enumerate(ws):
  tid=v&1023;tq=int(tid>=p['cut']);ti=tid-p['cut'] if tq else tid;raw=p['tiles'][tq][ti*32:(ti+1)*32]
  for y in range(8):
   for x in range(8):
    xx=7-x if v&1024 else x;yy=7-y if v&2048 else y;b=raw[yy*4+xx//2];idx=(b>>(4*(xx%2)))&15
    if idx:a[(k%4//2)*8+y][k%2*8+x]=p['pal'][v>>12][idx]
 return a

def make_profile(P):
 colors=sorted({c for n in range(901,909) for row in image(P,('v3',n)) for c in row if c},key=lambda c:sum(c>>s&31 for s in (0,5,10)))
 dark,gray,light,white=colors[0],colors[-3],colors[-2],colors[-1]
 tiles=bytearray(512*32);mts=bytearray(512*16);attrs=bytearray(512*4);pals=[[0]*16 for _ in range(16)];banks=[];tileids={};pictures={};proof=[]
 profile={'name':'hull','cut':512,'tiles':[bytes(512*32),tiles],'mt':[bytes(512*16),mts],'attr':[bytes(512*4),attrs],'pal':pals}
 def add(a):
  key=tuple(tuple(row) for row in a)
  if key in pictures:return ('hull',pictures[key])
  mi=512+len(pictures);assert mi<1000
  words=[]
  for k in range(4):
   tx=k%2*8;ty=k//2*8;pixels=[a[ty+y][tx+x] for y in range(8) for x in range(8)];cs=set(pixels);assert None not in cs and len(cs)<=15
   bank=next((i for i,s in enumerate(banks) if cs<=s),None)
   if bank is None:bank=len(banks);assert bank<16;banks.append(cs);pals[bank]=[0]+sorted(cs)+[0]*(15-len(cs))
   ix=[pals[bank].index(c,1) for c in pixels];raw=bytes(ix[i]|ix[i+1]<<4 for i in range(0,64,2))
   if raw not in tileids:
    tid=512+len(tileids);assert tid<1024;tileids[raw]=tid;tiles[(tid-512)*32:(tid-511)*32]=raw
   words.append(tileids[raw]|bank<<12)
  struct.pack_into('<8H',mts,(mi-512)*16,*words,*([0]*4));struct.pack_into('<I',attrs,(mi-512)*4,0x20000000);pictures[key]=mi;return ('hull',mi)
 def rect(a,x0,y0,x1,y1,c):
  for y in range(max(0,y0),min(16,y1+1)):
   for x in range(max(0,x0),min(16,x1+1)):a[y][x]=c
 def rail(connections):
  a=[[gray]*16 for _ in range(16)]
  for width,c in [(11,dark),(9,light),(5,white),(1,light)]:
   r=width//2
   for d in connections:
    x,y={'N':(7,0),'S':(7,15),'W':(0,7),'E':(15,7)}[d];rect(a,min(7,x)-r,min(7,y)-r,max(7,x)+r,max(7,y)+r,c)
  return add(a)
 def door(direction,floor):
  f=image(P,floor);f=[[gray if c is None else c for c in row] for row in f];a=[[gray]*16 for _ in range(16)];b=[r[:] for r in f]
  # Closed metal hatch reads vertically, while its threshold opens toward the room.
  for im in [a,b]:
   rect(im,1,0,14,15,dark);rect(im,2,0,13,15,white);rect(im,4,0,11,15,gray);rect(im,5,0,10,15,light);rect(im,7,0,7,15,dark)
  rect(a,1,0,14,2,white);rect(a,3,3,12,4,dark);rect(a,5,5,10,8,light)
  rect(b,1,6,14,8,dark);rect(b,2,7,13,7,white)
  for y in range(9,16):b[y]=f[y][:]
  rect(b,2,9,13,10,light);rect(b,2,11,13,11,dark)
  # Small native-white directional notch belongs to the threshold, not the panel.
  if direction in ['W','E']:
   xx=12 if direction=='W' else 3
   for dy,ww in [(0,1),(1,2),(2,3)]:rect(b,xx-(ww-1) if direction=='W' else xx,12+dy,xx if direction=='W' else xx+ww-1,12+dy,white)
  if direction=='S':
   a=list(reversed(a));b=list(reversed(b))
   for y in range(0,5):b[y]=f[y][:]
  return add(a),add(b)
 profile['_add']=add;profile['_rail']=rail;profile['_door']=door;profile['_gray']=gray
 return profile,proof

def finish(role,ctx,cfg):
 P=ctx['P'];p=P['hull'];g=ctx['grid'];w,h=ctx['w'],ctx['h'];put=ctx['setcell'];hard=ctx['hard'];occupied=ctx['occupied']
 if role in ('Cockpit','Navigation') and any(piece.get('label')=='bridge18_design_contract' for piece in ctx['pieces']):
  x0,x1=(2,17) if role=='Cockpit' else (1,18)
  for x in range(x0,x1+1):put(x,0,('v3',901 if x==x0 else 903 if x==x1 else 902),True)
  put(x0,1,('v3',904),True);put(x1,1,('v3',905),True)
 def structural(ref):return ref[0]=='v3' and 901<=ref[1]<=908
 wall={(i%w,i//w) for i,ref in enumerate(g) if structural(ref)}
 inside={(i%w,i//w) for i,ref in enumerate(g) if not structural(ref) and not(ref[0]=='v3' and ref[1]==1004)}
 # Restore the narrow backboard above the existing navigation display.
 if role=='Navigation' and any(piece.get('label')=='mess_branch_wall_navigation_display' for piece in ctx['pieces']):
  for x in range(5,8):wall.add((x,9))
 # A missing end cap is inferred from the actual surviving partition, not its requested length.
 if role=='CrewQuarters':
  for x in [2,6,12,15]:wall.add((x,6))
 # Native League reception frontage remains a donor; only its side joins are finished.
 if role=='Cabin':
  for y in range(5,h):
   for x in [0,w-1]:
    put(x,y,('v3',1004),True)
  for x in range(w):put(x,h-1,('v3',1004),True)
  wall={(x,y) for x,y in wall if 1<=x<=w-2 and y<=h-2}
  for y in range(4,h-1):wall.update([(1,y),(w-2,y)])
  for x in range(1,w-1):wall.add((x,h-2))
 dirs={'N':(0,-1),'E':(1,0),'S':(0,1),'W':(-1,0)}
 for x,y in sorted(wall):
  if (x,y) in hard:continue
  faces={d for d,(dx,dy) in dirs.items() if (x+dx,y+dy) in inside and (x+dx,y+dy) not in occupied}
  if len(faces)==1:
   f=next(iter(faces));con='WE' if f in 'NS' else 'NS'
  elif faces=={'N','E'}:con='WS'
  elif faces=={'E','S'}:con='NW'
  elif faces=={'S','W'}:con='NE'
  elif faces=={'W','N'}:con='SE'
  elif faces=={'N','S'}:con='WE'
  elif faces=={'E','W'}:con='NS'
  elif len(faces)>=3:
   con=''.join(d for d,(dx,dy) in dirs.items() if (x+dx,y+dy) in wall) or 'WE'
  else:
   con=''.join(d for d,(dx,dy) in dirs.items() if (x+dx,y+dy) in wall)
   if not con:con='WE'
  if role=='Cabin':
   con=('NE' if x==1 else 'NW') if y==h-2 and x in (1,w-2) else 'NS' if x in (1,w-2) else 'WE'
  old=g[y*w+x]
  if y==1 and structural(old) and old[1]==902:con='WE'
  if role=='CrewQuarters' and y==6:
   con='E' if x in [2,12] else 'W' if x in [6,15] else 'WE'
  put(x,y,p['_rail'](con),True)
 # Exact script warp cells remain the bottom of a recognizable framed hatch.
 door_records=[]
 for a in cfg['warps']:
  x,y=a['xy'];d=a['outward'];top,bottom=p['_door'](d,ctx['floor'])
  if role=='Cabin' and d=='N':continue
  # Keep old approaches and all occupied furniture intact.
  if d=='S' and y+1<h:put(x,y+1,top,True)
  elif y>0 and (x,y-1) not in occupied and (x,y-1) not in hard:put(x,y-1,top,True)
  put(x,y,bottom,False);door_records.append({'xy':[x,y],'direction':d,'native_16px_frame':True})
 if role=='Cabin':
  # Original return-floor trigger is retained as a second framed southern opening.
  body,threshold=p['_door']('S',ctx['floor']);put(10,14,threshold,False);put(10,15,body,True)
 ctx['pieces'].append({'label':'v18_continuous_hull_directional_hatches','wall_cells':[list(v) for v in sorted(wall)],'doors':door_records,'native_palette_only':True})
 return door_records
