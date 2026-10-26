"""Cargo console floor only. Donors/palette sizes/map and object shapes remain fixed.
Protect monitor x2..15/y7..23, desk x1..30/y11..27 and both bottom feet.
Bottom four rows are source floor shaded by the console, not a platform.
"""
from pathlib import Path
import runpy
FINISH_ORDER=140

def _protect(x,y):
 return (2<=x<=15 and 7<=y<=23) or (1<=x<=30 and 11<=y<=27) or (28<=y<=31 and (1<=x<=4 or 27<=x<=30))

def _shadow(dst,base,shade):
 # Preserve each original RGB555 floor->shadow channel decrement, on the new floor.
 out=0
 for shift in (0,5,10):
  decrement=((base>>shift)&31)-((shade>>shift)&31)
  assert decrement>=0
  out |= max(0,((dst>>shift)&31)-decrement)<<shift
 return out

def finish(role,ctx):
 if role!='CargoHold':return []
 native=runpy.run_path(str(Path(__file__).with_name('space_furniture_finish_v18.py')))
 layers,flat,maskfn=native['_layers'],native['_flat'],native['_floor_mask']
 assert tuple(ctx['floor'])==('tidal',525)
 donor=flat(layers(ctx,('facility',752)));floor=flat(layers(ctx,ctx['floor']));profile=native['_Profile'](ctx,'CargoHold21');records=[]
 for x,y,n in [(11,3,867),(12,3,868),(11,4,875),(12,4,876)]:
  ref=ctx['getcell'](x,y);assert ref==('facility',n),(x,y,ref)
  src=layers(ctx,ref);pixels=flat(src);out=[list(src[0]),list(src[1])]
  local=lambda i:((x-11)*16+i%16,(y-3)*16+i//16)
  mask={i for i in maskfn(pixels,donor) if not _protect(*local(i))}
  shadow={i for i in range(256) if local(i)[1]>=28 and not _protect(*local(i))}
  for i in mask:out[0][i]=floor[i];out[1][i]=None
  for i in shadow:
   assert pixels[i] in (21073,15853,13608),(n,i,pixels[i])
   out[0][i]=_shadow(floor[i],{21073:24277,15853:21073,13608:15756}[pixels[i]],pixels[i]);out[1][i]=None
  allowed=mask|shadow;composed=flat(out);changed=[i for i in allowed if pixels[i]!=composed[i]]
  assert all(composed[i]==pixels[i] for i in range(256) if i not in allowed)
  new=profile.add(out,ctx['attribute'](ref));blocked=ctx['blocked'][y*ctx['w']+x];ctx['setcell'](x,y,new,blocked)
  records.append({'xy':[x,y],'source':['facility',n],'donor_floor':['facility',752],'room_floor':['tidal',525],'changed_pixels':changed,'floor_mask_pixels':sorted(mask),'shadow_floor_pixels':sorted(shadow),'preserved_pixels':256-len(allowed),'source_attribute':ctx['attribute'](ref),'collision_unchanged':blocked})
 ctx['pieces'].append({'label':'cargo_console_floor_only_v21','xy':[11,3],'size':[2,2],'new_art':'destination_floor_and_native_shadow_depth_composite_console_and_feet_preserved','floor_pixel_changes':records})
 return records

