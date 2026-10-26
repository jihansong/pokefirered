"""Restore the complete native League floor medallion after furniture placement."""
ROOM_PLANS={}
FINISH_ORDER=130

def finish(role,ctx):
 if role!='Cabin':return []
 edits=[(9,4,560,576),(10,4,563,576),(8,9,576,638),(9,10,576,577),(10,10,576,578)]
 for x,y,old,new in edits:
  assert ctx['getcell'](x,y)[:2]==('league',old),(x,y,ctx['getcell'](x,y))
  assert not ctx['blocked'][y*ctx['w']+x],('Floor motif must not change furniture collision',x,y)
  ctx['setcell'](x,y,('league',new),False)
 ctx['pieces'].append({'label':'native_League_complete_6x6_floor_medallion','source_region':[7,4,6,6],'destination_region':[7,5,6,6],'changed_cells':[[x,y] for x,y,_,_ in edits],'native_last_row':[576,576,577,578,576,576],'continuous_center_xy':[160,128],'pixel_reflection_axis_xy':[159.5,127.5],'furniture_collision_or_position_change':False,'method':'Clear duplicate old top tip, restore only erased native arc and missing bottom tip; never repaint whole furniture footprint.'})
 return [[x,y] for x,y,_,_ in edits]
