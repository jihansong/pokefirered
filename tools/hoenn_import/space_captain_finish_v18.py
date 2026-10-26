"""SSAnne_CaptainsOffice-inspired private office; fixed captain/event positions."""
ROOM_PLANS={}
FLOOR_OVERRIDES={'CaptainsOffice':('facility',752)}
def decorate_override(role,ctx):
 if role!='CaptainsOffice':return False
 put=ctx['setcell'];w,h=ctx['w'],ctx['h'];floor=ctx['floor'];place=ctx['place']
 for y in range(h):
  for x in range(w):put(x,y,('v3',1004),True)
 for y in range(2,12):
  for x in range(3,14):put(x,y,floor,False)
 for x in range(2,15):
  put(x,1,('v3',901 if x==2 else 903 if x==14 else 902),True);put(x,12,('v3',906 if x==2 else 908 if x==14 else 907),True)
 for y in range(2,12):put(2,y,('v3',904),True);put(14,y,('v3',905),True)
 place('SSAnne_captains_open_book_desk','anne',[[773,774,775],[781,782,783]],3,3)
 place('SSAnne_captains_reference_shelf','anne',[[762],[770]],3,1)
 place('SSAnne_captains_wall_map','anne',[[755,756]],4,1)
 for y in [8,9]:place('SSAnne_captains_visitor_chair_'+str(y),'anne',[[771]],11,y)
 place('captains_complete_existing_earth_viewport','v3',[[850+y*8+x for x in range(8)] for y in range(4)],7,1)
 for x in range(6,16):put(x,0,('v3',901 if x==6 else 903 if x==15 else 902),True);put(x,5,('v3',906 if x==6 else 908 if x==15 else 907),True)
 for y in range(1,5):put(6,y,('v3',904),True);put(15,y,('v3',905),True)
 ctx['pieces'].append({'label':'SSAnne_CaptainsOffice_reference','source_map':'SSAnne_CaptainsOffice','fixed_captain':[5,5],'fixed_talk':[5,6],'fixed_west_warp':[1,6],'role':'집무실·응접 공간, 조종실 아님'})
 return True
