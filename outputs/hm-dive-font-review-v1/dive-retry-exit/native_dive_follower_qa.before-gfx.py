#!/usr/bin/env python3
"""Re-run native Dive route with the SAV's genuine starter companion."""
from pathlib import Path
q=Path('tools/qa/native_dive_qa.py').read_text(encoding='utf-8')
extra=r'''
_localid_header=Path('include/constants/event_objects.h').read_text()
_follower_id=int(re.search(r'#define\s+LOCALID_FOLLOWER\s+(\d+)',_localid_header).group(1))
assert _follower_id==254
assert a.case=='route' and not a.loss
report['follower_checks']=[]
def original_starter_copy(s):
 owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
 name=bytes(s.sb2[off('sb2.playerName'):off('sb2.playerName')+7]).split(b'\xff',1)[0]
 found=[]
 for i in range(s.party_count()):
  m=s.party_mon(i)
  if (m.species()==const('SPECIES_PIKACHU') and m.starter_bit()
      and m.otid==owner and m.ot_name_raw().split(b'\xff',1)[0]==name):
   raw=bytes(m.blk[m.o:m.o+100])
   assert not m.is_egg() and not(raw[19]&1)
   assert struct.unpack_from('<H',raw,86)[0]>0,'starter in source party is fainted'
   found.append((i,raw))
 assert len(found)==1,('expected one genuine live party starter',len(found))
 i,raw=found[0]
 report['follower_original']={'party_index':i,'personality':struct.unpack_from('<I',raw)[0],
  'otid':owner,'box_sha256':sha(raw[:80]),'copied_without_editing':True}
 return raw
def companion_state():
 rows=[]
 for i in range(16):
  b=e.read(syms['gObjectEvents']+i*36,36)
  if b[0]&1 and b[8]==_follower_id:rows.append((i,b))
 assert len(rows)==1,('active follower count',len(rows),e.location())
 i,b=rows[0];g,n,x,y=e.location()
 assert b[9]==n and b[10]==g,('follower map mismatch',list(b[8:11]),g,n)
 assert b[5]==const('OBJ_EVENT_GFX_PIKACHU'),'approved follower graphics replaced'
 assert b[4]<128
 sp=syms['gSprites']+b[4]*68
 assert e.u8(sp+0x3e)&1,'follower sprite inactive'
 return b,sp
def check_companion_visible(previous,label):
 b,sp=companion_state()
 xy=struct.unpack_from('<hh',b,16)
 assert xy==(previous[0]+7,previous[1]+7),('follower did not follow previous tile',xy,previous)
 assert not(int.from_bytes(b[:4],'little')&((1<<13)|(1<<14))),'follower hidden or off screen'
 assert not(e.u8(sp+0x3e)&4),'follower sprite invisible'
 assert e.u8(syms['gPlayerAvatar'])&(SURF|UW),'not in a water avatar mode'
 mon=e.read(syms['gPlayerParty']+100,100);m=Mon(bytearray(mon),0)
 assert m.personality==report['follower_original']['personality']
 assert m.otid==report['follower_original']['otid'] and m.starter_bit()
 assert m.species()==const('SPECIES_PIKACHU') and struct.unpack_from('<H',mon,86)[0]>0
 photo(e,'follower-'+label+'-'+str(len(report['follower_checks'])))
 report['follower_checks'].append({'label':label,'map':e.location()[:2],
  'player_xy':e.location()[2:],'follower_xy':[xy[0]-7,xy[1]-7],
  'visible':True,'native_sprite_active':True,'avatar_flags':e.u8(syms['gPlayerAvatar'])})
def probe_companion(label):
 initial=e.location()
 companion_state()
 walk_tile('RIGHT');await_state(e.field_idle,600);e.run(20)
 assert e.location()==(initial[0],initial[1],initial[2]+1,initial[3]),e.location()
 check_companion_visible(initial[2:],label+'-right')
 previous=e.location()[2:]
 walk_tile('LEFT');await_state(e.field_idle,600);e.run(20)
 assert e.location()==initial,e.location()
 check_companion_visible(previous,label+'-left')
_original_reach=reach
def reach(name,x,y,flag):
 _original_reach(name,x,y,flag)
 probe_companion(name)
_original_save_reopen=native_save_reopen
def native_save_reopen(e,expected_pc):
 _original_save_reopen(e,expected_pc)
 probe_companion('cold-reopen')
'''
def once(old,new):
 global q
 assert q.count(old)==1,('native Dive QA anchor changed',old[:80],q.count(old))
 q=q.replace(old,new,1)
once('e=None\ntry:',extra+'\ne=None\ntry:')
once('s=SaveFile(str(sav));s.fast_battles();s.keep_party(1);s.set_var(\'VAR_REPEL_STEP_COUNT\',250)',
 's=SaveFile(str(sav));original_pika=original_starter_copy(s);s.fast_battles();s.keep_party(1);s.set_var(\'VAR_REPEL_STEP_COUNT\',250)')
anchor='  if a.case==\'teach\':\n   key=s._key()&65535'
fixture="""  base=off('sb1.playerParty')
  s.sb1[base+100:base+200]=original_pika
  s.sb1[off('sb1.playerPartyCount')]=2
  s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
  assert bytes(s.sb1[base+100:base+200])==original_pika
"""
once(anchor,fixture+anchor)
once('  initial=e.location()','  probe_companion(\'surface-before-dive\')\n  initial=e.location()')
exec(compile(q,'tools/qa/native_dive_qa.py','exec'))
