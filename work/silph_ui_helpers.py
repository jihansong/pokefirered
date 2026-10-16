import struct

def _action_battler(ec,e,rom):
 want=ec.sym_addrs(str(rom),'HandleInputChooseAction')
 funcs=e.sym('gBattlerControllerFuncs')
 return next((b for b in (0,2) if (e.u32(funcs+4*b)&~1) in want),None)

def silph_wait_capture(ec,e,rom,species='LICKITUNG',count=1):
 target=ec.species_id(species);start=e.frame()
 while e.frame()-start<12000:
  mons=[m for m in ec.live_mons(e) if m.species()==target and not m.is_egg()]
  if len(mons)==count:return None
  if len(mons)>count:return 'unexpected capture count: '+str(len(mons))
  if e.reset_seen():return 'reset before capture completed'
  if e.field_idle():return 'battle ended before capture completed'
  if e.in_battle():
   if _action_battler(ec,e,rom) is not None:
    return 'action menu returned before requested capture; inspect actual targets'
   e.press('B',hold=3,after=17)
  else:e.run(1)
 return 'capture did not complete within 12000 frames'

def silph_finish_fight(ec,e,rom,move_index=1):
 start=e.frame();actions=0
 while e.frame()-start<24000:
  if e.reset_seen():return 'reset while finishing Silph battle'
  if e.field_idle():return None
  if e.in_battle():
   b=_action_battler(ec,e,rom)
   if b is None:e.press('B',hold=3,after=17);continue
   slot=e.u16(e.sym('gBattlerPartyIndexes')+2*b)
   if not 0<=slot<6:return 'invalid active party index'
   size=ec.off('pokemon')
   mon=ec.Mon(bytearray(e.read(e.sym('gPlayerParty')+slot*size,size)),0)
   attack=mon.subs()['A'];moves=struct.unpack('<4H',attack[:8])
   if not 1<=move_index<=4:return 'invalid move index'
   if not moves[move_index-1] or not attack[7+move_index]:
    return 'selected move is empty or out of PP for active party slot '+str(slot)
   actions+=1
   if actions>40:return '40 explicit FIGHT actions did not end battle'
   err=ec.fight(e,str(rom),move_index)
   if err:return 'explicit FIGHT failed: '+err
  elif e.in_overworld():e.press('A',hold=3,after=17)
  else:e.run(1)
 return 'FIGHT sequence did not return to idle within 24000 frames'
