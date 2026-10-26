"""Explicit front-access machine layer correction; no global layer conversion."""
ROOM_PLANS={}
FINISH_ORDER=100

def finish(role,ctx):
 if role!='GameRoom':return []
 records=[]
 for x in range(6,16):
  y=4;ref=ctx['getcell'](x,y);assert ref[:2]==('game',710 if x%2==0 else 788),('Unexpected front machine tile',x,ref)
  attr=ctx['attribute'](ref);assert attr>>29&3==0
  new=(ref[0],ref[1],(attr&~0x60000000)|0x20000000)
  assert ctx['blocked'][y*ctx['w']+x]
  ctx['setcell'](x,y,new,True)
  records.append({'xy':[x,y],'source':list(ref),'replacement':list(new),'pixel_change':False,'collision_change':False,'reason':'Fixed actor approach below blocked machine front; native foreground would cover face. Original Celadon donor has walkable lower cells instead.'})
 ctx['pieces'].append({'label':'explicit_GameRoom_front_access_foreground_correction','cells':records,'blanket_conversion':False,'counter_and_plant_native_layers_unchanged':True})
 return records
