"""One-tile service-counter endcap correction at Cabin E4 only."""
ROOM_PLANS={}
FINISH_ORDER=120

def finish(role,ctx):
 if role!='Cabin':return []
 P=ctx['P'];h=P['hull'];add=h['_add'];put=ctx['setcell']
 def picture(ref):
  import struct
  p=P[ref[0]];n=ref[1];q=int(n>=p['cut']);i=n-p['cut'] if q else n;out=[[None]*16 for _ in range(16)]
  for k,v in enumerate(struct.unpack_from('<8H',p['mt'][q],i*16)):
   t=v&1023;tq=int(t>=p['cut']);ti=t-p['cut'] if tq else t;raw=p['tiles'][tq][ti*32:(ti+1)*32]
   for y in range(8):
    for x in range(8):
     xx=7-x if v&1024 else x;yy=7-y if v&2048 else y;idx=raw[yy*4+xx//2]>>(4*(xx%2))&15
     if idx:out[k%4//2*8+y][k%2*8+x]=p['pal'][v>>12][idx]
  return out
 floor=picture(ctx['floor']);front=picture(('league',545));back=picture(('league',628));dark=front[8][0];shade=front[5][0];edge=front[15][0]
 # A rounded finished end, using the existing counter's cream top, orange lip,
 # lavender front and dark outline. No furniture or floor palette is recolored.
 for y in range(16):
  tip=13 if y==0 else 15 if y<=7 else 14 if y<=13 else 13 if y==14 else 12
  for x in range(tip+1,16):front[y][x]=floor[y][x]
  if 1<=y<=4:front[y][15]=shade
  if 5<=y<=7:front[y][15]=dark
  if 8<=y<=13:front[y][14]=dark
  if y==15:front[y][12]=edge
 # Match the narrow counter back line to its new finished right edge.
 for y in range(16):
  for x in range(14,16):back[y][x]=floor[y][x]
 assert (18,3) not in ctx['hard'] and ctx['getcell'](18,3)[:2]==('league',545)
 put(17,2,add(back),False);put(17,3,add(front),True)
 put(18,3,ctx['floor'],False);ctx['occupied'].discard((18,3))
 ctx['pieces'].append({'label':'Cabin_E4_counter_endcap_17_full_hatch_18','changed_cells':[[17,2],[17,3],[18,3]],'new_art':'native counter material endcap composite','service_NPC':[16,2],'service_stand':[16,4],'warp':[18,4],'other_rooms_changed':False,'hull_finisher_draws_full_upper_hatch':True})
 return [[17,2],[17,3],[18,3]]
