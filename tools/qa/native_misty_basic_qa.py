#!/usr/bin/env python3
"""Misty eligibility/growth/trail native QA. Actual duel/HM routes are separate."""
from pathlib import Path
import ast,hashlib,json,struct,sys
sys.path.insert(0,str(Path.cwd()/'tools/qa'))
base=Path('tools/qa/johto_violet_native_bootstrap_v1.py').read_text()
assert hashlib.sha256(base.encode()).hexdigest()=='83c4557b96c344b241fc6f79e9b17722acfc0b0e81e0f9e6d649ff5d8b1c84bb'
assert base.count('\nresults=[]\n')==1
exec(compile(base.split('\nresults=[]\n')[0],'<verified-native-bootstrap-definitions-only>','exec'))
if 'constants/battle.h' not in gd.CONST_HEADERS:gd.CONST_HEADERS.append('constants/battle.h')
gd.FIELDS.update({'misty_obj':('ObjectEvent',None),'misty_obj.coords':('ObjectEvent','currentCoords'),'misty_obj.local':('ObjectEvent','localId'),'misty_obj.sprite':('ObjectEvent','spriteId'),'misty_sprite':('Sprite',None),'misty_sprite.x':('Sprite','x'),'misty_sprite.y':('Sprite','y'),'misty_sprite.x2':('Sprite','x2'),'misty_sprite.y2':('Sprite','y2'),'misty_sprite.cy':('Sprite','centerToCornerVecY')});gd._OFFSETS=None
assert off('misty_obj')==36 and off('misty_sprite')==68
elf_raw=elf.read_bytes();eh=struct.unpack_from('<16sHHIIIIIHHHHHH',elf_raw)
sections=[struct.unpack_from('<10I',elf_raw,eh[6]+i*eh[11]) for i in range(eh[12])]
for q in sections:
 if q[2]&2 and q[1]!=8 and 0x08000000<=q[3]<0x0a000000 and q[5]:assert r.data[q[3]-0x08000000:q[3]-0x08000000+q[5]]==elf_raw[q[4]:q[4]+q[5]],'ELF/ROM mismatch'
S=(max(q[3]+q[5] for q in sections if q[2]&2 and 0x02000000<=q[3]<0x02040000)+3)&~3
assert S+96<=0x02040000,'native QA scratch does not fit'
def call(e,name,*args):
 assert len(args)<=6 and name in syms
 prev=e.callback2();backup=e.read(S,96)
 vals={'cb':syms['gMain']+4,'prev':prev,**{'a'+str(i):v for i,v in enumerate(list(args)+[0]*(6-len(args)))},'ret':S+35,'fn':syms[name]|1,'res':S+88}
 ins=[0xb510,0xb082,('l',4,'cb'),('l',0,'prev'),0x6020,('l',0,'a0'),('l',1,'a1'),('l',2,'a2'),('l',3,'a3'),('l',4,'a4'),0x9400,('l',4,'a5'),0x9401,('l',4,'ret'),0x46a6,('l',4,'fn'),0x4720,('l',4,'res'),0x6020,0xb002,0xbd10,0x46c0]
 keys=list(vals)
 for i,q in enumerate(ins):
  if isinstance(q,tuple):
   disp=S+44+4*keys.index(q[2])-((S+2*i+4)&~3);assert 0<=disp<=1020 and disp%4==0
   ins[i]=0x4800+(q[1]<<8)+disp//4
 code=struct.pack('<22H',*ins)+struct.pack('<11I',*vals.values());assert len(code)==88
 try:
  e.write(S,code+struct.pack('<I',0xdecafbad));e.write(syms['gMain']+4,struct.pack('<I',S|1));e.run(1)
  for _ in range(20):
   v=e.u32(S+88)
   if v!=0xdecafbad:return v
   e.run(1)
  raise AssertionError('native call did not return: '+name)
 finally:e.write(S,backup)
def flag(e,name,on):call(e,'FlagSet' if on else 'FlagClear',const(name))
join='FLAG_MISTY_COMPANION_JOINED';hide='FLAG_HIDE_MISTY_PALLET';growth=['FLAG_JOHTO_BADGE02_GET','FLAG_JOHTO_BADGE06_GET','FLAG_HOENN_BIRCH_RESCUED','FLAG_HOENN_BADGE07_GET']
def identity(p,n):
 rows=[]
 for i in range(n):
  m=Mon(bytearray(p),i*100);raw=p[i*100:(i+1)*100]
  assert sum(v[0] for s in m.subs().values() for v in struct.iter_unpack('<H',s))&65535==struct.unpack_from('<H',raw,28)[0]
  assert not raw[19]&1,'Bad Egg in native party'
  rows.append((m.personality,m.otid,m.species()))
 return rows
def record(e):
 b=blocks(e);n=e.u8(e.sym('gPlayerPartyCount'));p=e.read(e.sym('gPlayerParty'),600)
 return dict(party=p,count=n,identity=identity(p,n),pc=e.read(e.ptr('gPokemonStoragePtr'),33744),dex=[b.dex_state(i) for i in range(1,387)])
def same_records(e,b):assert record(e)==b,'native QA changed user Pokemon/PC/Dex'
def one_tile(e,key,run=False):
 before=e.location();delta={'RIGHT':(1,0),'LEFT':(-1,0),'DOWN':(0,1),'UP':(0,-1)}[key]
 want=(*before[:2],before[2]+delta[0],before[3]+delta[1]);e.hold(*(([key,'B']) if run else [key]))
 try:
  for _ in range(120):
   e.run(1)
   if e.location()!=before:
    if run:assert e.u8(e.sym('gPlayerAvatar'))&128,'B input did not enter native DASH'
    break
  else:raise AssertionError(('native step blocked',before,key))
 finally:e.hold()
 assert e.location()==want,('native step overshot',want,e.location())
 for _ in range(90):
  safe(e)
  if e.field_idle():break
  e.run(1)
 else:raise AssertionError('native step did not settle')
 e.run(20);assert e.location()==want
 return before
def object_rows(e,local):
 rows=[]
 for i in range(16):
  p=e.sym('gObjectEvents')+i*off('misty_obj');b=e.read(p,off('misty_obj'))
  if b[0]&1 and b[off('misty_obj.local')]==local:
   sid=b[off('misty_obj.sprite')];assert sid<64
   sp=e.sym('gSprites')+sid*off('misty_sprite');assert e.u8(sp+0x3e)&1
   xy=struct.unpack_from('<hh',b,off('misty_obj.coords'))
   visible=not (struct.unpack_from('<I',b)[0]&(1<<13|1<<14)) and not e.u8(sp+0x3e)&4
   x=struct.unpack('<h',e.read(sp+off('misty_sprite.x'),2))[0]+struct.unpack('<h',e.read(sp+off('misty_sprite.x2'),2))[0]
   y=struct.unpack('<h',e.read(sp+off('misty_sprite.y'),2))[0]+struct.unpack('<h',e.read(sp+off('misty_sprite.y2'),2))[0]-struct.unpack('<b',e.read(sp+off('misty_sprite.cy'),1))[0]
   rows.append(dict(ptr=p,slot=i,xy=xy,sprite=sid,visible=visible,feet=(x,y)))
 assert len(rows)<=1,('duplicate companion',local,len(rows))
 return rows
def trail(e,label,need_visible=False):
 ms=object_rows(e,253);pk=object_rows(e,254);assert len(ms)==1
 tasks=[i for i in range(16) if e.u8(e.sym('gTasks')+40*i+4) and e.u32(e.sym('gTasks')+40*i)&~1==syms['Task_FollowerPikachu']&~1]
 assert len(tasks)==1 and e.u8(e.sym('gTasks')+40*tasks[0]+7)==80
 p=call(e,'GetPlayerAvatarObjectId');assert p<16
 pp=e.sym('gObjectEvents')+p*36;ps=e.u8(pp+off('misty_obj.sprite'));assert ps<64
 sp=e.sym('gSprites')+ps*68
 player=dict(xy=struct.unpack('<hh',e.read(pp+off('misty_obj.coords'),4)),feet=(struct.unpack('<h',e.read(sp+off('misty_sprite.x'),2))[0]+struct.unpack('<h',e.read(sp+off('misty_sprite.x2'),2))[0],struct.unpack('<h',e.read(sp+off('misty_sprite.y'),2))[0]+struct.unpack('<h',e.read(sp+off('misty_sprite.y2'),2))[0]-struct.unpack('<b',e.read(sp+off('misty_sprite.cy'),1))[0]))
 if ms[0]['visible']:
  for o in [player]+pk:
   assert ms[0]['xy']!=o['xy'] and sum(abs(a-b) for a,b in zip(ms[0]['feet'],o['feet']))>=16,('visible overlap',label,ms,pk,player)
 if need_visible:assert ms[0]['visible'],('Misty not visible after trail cleared',label,ms,pk,player)
 row=dict(label=label,player=player,misty=ms,pikachu=pk,follower_tasks=tasks);rows.append(row)
 return row
results=[];rows=[]
try:
 with Emu(str(rom),str(sav),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.run(30)
  pristine=e.save_state();before=record(e)
  for sys_clear,badges,want in [(False,0,False),(True,0,False),(False,8,False),(True,7,False),(True,8,True)]:
   e.load_state(pristine);flag(e,'FLAG_SYS_GAME_CLEAR',sys_clear)
   flag(e,'FLAG_HOENN_LEAGUE_CLEAR',True)
   for i in range(8):flag(e,'FLAG_BADGE%02d_GET'%(i+1),i<badges)
   assert bool(call(e,'CanMistyJoin'))==want
   flag(e,join,False);call(e,'MistyJoin');e.run(4)
   assert blocks(e).flag(join)==want
   same_records(e,before);results.append(dict(case='eligibility',system_clear=sys_clear,kanto_badges=badges,hoenn_hof=True,expected_join=want,pass_all=True))
  e.load_state(pristine);before=record(e);normal=e.save_state()
  expected=[['STARMIE','PSYDUCK','HORSEA'],['STARMIE','PSYDUCK','HORSEA','POLIWHIRL'],['STARMIE','GOLDUCK','SEADRA','POLIWHIRL','CORSOLA'],['STARMIE','GOLDUCK','KINGDRA','POLITOED','CORSOLA','AZUMARILL'],['STARMIE','GOLDUCK','KINGDRA','POLITOED','CORSOLA','AZUMARILL']]
  for stage in range(5):
   e.load_state(normal)
   for i,f in enumerate(growth):flag(e,f,i<stage)
   assert call(e,'MistyGetGrowthStage')==stage
   e.write(e.sym('gBattleTypeFlags'),struct.pack('<I',const('BATTLE_TYPE_TRAINER')))
   n=call(e,'CreateNPCTrainerParty',e.sym('gEnemyParty'),const('TRAINER_MISTY_COMPANION_STAGE%d'%stage))
   raw=e.read(e.sym('gEnemyParty'),600);mons=identity(raw,n)
   assert n==[3,4,5,6,6][stage] and [v[2] for v in mons]==[const('SPECIES_'+s) for s in expected[stage]]
   assert all(raw[100*i+84]==[48,52,56,60,66][stage] for i in range(n))
   same_records(e,before)
   # Lower regional flags can disappear from the UI context without lowering a retained milestone.
   if stage:
    for f in growth[:stage-1]:flag(e,f,False)
    assert call(e,'MistyGetGrowthStage')==stage
   results.append(dict(case='native_enemy_team_growth',stage=stage,count=n,species=[v[2] for v in mons],player_party_replaced=False,pass_all=True))
  e.load_state(normal)
  for f in K:flag(e,f,True)
  flag(e,'FLAG_SYS_GAME_CLEAR',True);call(e,'MistyJoin');e.run(30)
  for j in range(5):one_tile(e,'RIGHT');trail(e,'walk-right-'+str(j),need_visible=j>=2)
  for j in range(5):one_tile(e,'LEFT',run=True);trail(e,'run-reverse-left-'+str(j),need_visible=False)
  for j in range(5):one_tile(e,'RIGHT',run=True);trail(e,'run-right-'+str(j),need_visible=j>=2)
  for j in range(5):one_tile(e,'LEFT');trail(e,'walk-reverse-left-'+str(j))
  same_records(e,before)
  # Exercise the absent-Pikachu branch without removing or editing any party Pokemon.
  flag(e,'FLAG_RECEIVED_STARTER_PIKACHU',False);e.run(30);assert not object_rows(e,254)
  for j in range(4):one_tile(e,'RIGHT');trail(e,'without-pikachu-'+str(j),need_visible=j>=1)
  same_records(e,before)
  e.load_state(pristine);assert record(e)==before
finally:
 for f,h in originals.items():assert digest(f.read_bytes())==h,('original file changed',str(f))
(out/'basic-result.json').write_text(json.dumps(dict(all_pass=True,rom_sha256=digest(rom.read_bytes()),input_sav_sha256=originals[sav],checks=results,trail_samples=rows,original_party_pc_dex_preserved=True,temporary_native_ram_fixture=True,native_battery_save_tested=False,actual_device_fps_measured=False,friendly_duel_tested=False,real_surf_dive_ascend_tested=False),indent=2))
