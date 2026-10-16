"""Actual-input Route116/Rusturf rescue/Stone request, starting from prior QA save.
No preboot state edits, RAM writes, forced event calls, or forced outcomes here.
Prior seed uses an eligibility fixture; this is not full campaign validation.
"""
import argparse, ast, hashlib, json, os, struct, sys, traceback
from collections import deque
from pathlib import Path
R6='0eee66671ba7af7309117d098296a233a58985f9da881b4d4a8a479780f1ea1a'
PRIOR='37966a11833191dc2ad6cb0ee26df2a4226db9f3d7c673c2fe11bd7a66601641'
SEED='888f205f324d696415e9206e55ea2f8dc73d71a7141ff06c3030392270898fb4'
USER='917c24715ca1dd78b22d6350182648fa81f307b771fa5524595d157a0b6a6604'
BASE='work/misty-followup-20261014/'
KEYS={'UP':(0,-1),'DOWN':(0,1),'LEFT':(-1,0),'RIGHT':(1,0)}
FLAGS=['FLAG_HOENN_GOT_DEVON_GOODS','FLAG_HOENN_PEEKO_RESCUED','FLAG_HIDE_HOENN_RUSTURF_GRUNT',
       'FLAG_HIDE_HOENN_RUSTURF_PEEKO','FLAG_HOENN_DEVON_GOODS_DELIVERED','FLAG_HOENN_GOT_EXP_SHARE']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for n in ['root','rom','elf','sav','abi-json','out']:p.add_argument('--'+n,required=True,type=Path)
 for n in ['rom','elf','abi']:p.add_argument('--expect-'+n+'-sha',required=True)
 args=p.parse_args();root=args.root.resolve(strict=True);os.chdir(root)
 args.out=args.out.resolve();assert not args.out.exists() and args.out.is_relative_to(root/'work')
 for n in ['rom','elf','sav','abi_json']:setattr(args,n,getattr(args,n).resolve(strict=True))
 ctl=root/(BASE+'r2-tools/native-devon-v7-r6.py');prior=root/(BASE+'native-v7-r6/validation.json');seed=root/(BASE+'native-v7-r6/scene1-Devon-native-QA-only.sav')
 inputs={ctl:R6,prior:PRIOR,seed:SEED,args.sav:USER,args.rom:args.expect_rom_sha,args.elf:args.expect_elf_sha,args.abi_json:args.expect_abi_sha}
 for f,h in inputs.items():assert len(h)==64 and sha(f)==h,('Input changed',str(f))
 old=json.loads(prior.read_text());case=[c for c in old['cases'] if c['scene_at_boot']==1]
 assert old['pass'] and old['protected_original_inputs_unchanged'] and old['SAV_sha256']==USER
 assert len(case)==1 and case[0]['pass'] and case[0]['actual_Roxanne_win'] and case[0]['continuous_Gym_exit_and_City_coord'] and case[0]['expected_theft']
 assert Path(case[0]['SAVE_cold']['qa_save']).resolve()==seed.resolve()
 text=ctl.read_text();tree=ast.parse(text);tries=[n for n in tree.body if isinstance(n,ast.Try)];assert len(tries)==1
 prefix=tree.body[:tree.body.index(tries[0])];body=[];removed=0
 for n in tries[0].body:
  if isinstance(n,ast.FunctionDef) and n.name=='fixture':break
  if isinstance(n,ast.Assert) and n.msg and isinstance(n.msg,ast.Constant) and n.msg.value=='This v7 is prepared for the approved e156 ROM':removed+=1;continue
  body.append(n)
 assert removed==1 and any(isinstance(n,ast.FunctionDef) and n.name=='native_send_out' for n in body)
 sys.argv=['continuation','--root',str(root),'--rom',str(args.rom),'--elf',str(args.elf),'--sav',str(args.sav),'--expect-rom-sha',args.expect_rom_sha,'--expect-elf-sha',args.expect_elf_sha,'--expect-sav-sha',USER,'--abi-json',str(args.abi_json),'--out',str(args.out)]
 ctx={'__file__':str(ctl),'__name__':'verified_continuation_controller'};e=None;report=None
 try:
  exec(compile(ast.Module(body=prefix+body,type_ignores=[]),'<verified-r6-preflight-controller>','exec'),ctx)
  report=ctx['report'];report.update({'pass':False},status='running',runner_version=8,runner_revision=3,cases=[],stages=[],steps=[],battles=[],
   scope='Actual route/rescue/Stone request from prior native scene2 QA battery save',prior_preboot_eligibility_fixture=True,
   this_test_preboot_save_edits=0,full_Hoenn_campaign_tested=False,Stern_delivery_completed=False,actual_device_fps_measured=False,
   continuation_seed_sha256=SEED,prior_validation_sha256=PRIOR,prior_native_SAVE=case[0]['SAVE_cold'])
  ctx['protected'].update({f.resolve():h for f,h in inputs.items()});gd,off,const,syms=[ctx[n]for n in ['gd','off','const','syms']]
  for h in ['fieldmap.h','constants/metatile_behaviors.h']:
   if h not in gd.CONST_HEADERS:gd.CONST_HEADERS.append(h)
  for typ,fields in {'MapHeader':['mapLayout','events'],'MapLayout':['width','height','primaryTileset','secondaryTileset'],
   'BackupMapLayout':['Xsize','Ysize','map'],'MapEvents':['warpCount','warps'],'WarpEvent':['x','y','mapNum','mapGroup'],
   'Tileset':['isEmerald','metatileAttributes']}.items():
   for f in fields:gd.FIELDS['next.'+typ+'.'+f]=(typ,f)
  gd.FIELDS.update({'next.WarpEvent':('WarpEvent',None),
                   'next.BackupMapLayout':('BackupMapLayout',None),
                   'next.MapHeader':('MapHeader',None)})
  gd._OFFSETS=None
  report['compiler_map_offsets']={k:off(k)for k in gd.FIELDS if k.startswith('next.')}
  map_bindings={}
  sizes={'VMap':off('next.BackupMapLayout'),
         'gMapHeader':off('next.MapHeader'),
         'gObjectEvents':off('misty_obj')*const('OBJECT_EVENTS_COUNT')}
  assert const('OBJECT_EVENTS_COUNT')==16
  for name,wanted_size in sizes.items():
   rows=ctx['actual_rows'].get(name,[])
   assert len(rows)==1,('Missing/ambiguous current ELF map symbol',name,rows)
   row=rows[0]
   assert (row['info']&15)==1 and row['size']==wanted_size,('Map symbol type/size mismatch',name,row,wanted_size)
   value=row['value']
   in_ram=(0x02000000<=value and value+wanted_size<=0x02040000) or (0x03000000<=value and value+wanted_size<=0x03008000)
   assert in_ram,('Map symbol is not RAM data',name,row)
   sec=ctx['sections'][row['section']]
   assert sec[2]&3==3 and sec[3]<=value and value+wanted_size<=sec[3]+sec[5],('Map symbol section containment failed',name,row,sec)
   syms[name]=value
   map_bindings[name]=row
  report['current_ELF_map_symbol_bindings']=map_bindings
  seedfile=ctx['SaveFile'](str(seed))
  assert seedfile.var('VAR_HOENN_SCENE_DEVON')==2 and seedfile.flag('FLAG_HOENN_BADGE01_GET')
  assert seedfile.trainer_beaten('TRAINER_HOENN_ROXANNE_1') and not seedfile.trainer_beaten('TRAINER_HOENN_GRUNT_RUSTURF_TUNNEL')
  assert seedfile.item_count('ITEM_DEVON_GOODS')==0 and not any(seedfile.flag(f)for f in FLAGS[:2]+FLAGS[4:])
  e=ctx['ReadOnlyEmu'](str(args.rom),str(seed),sym='');ctx['e']=e;e.syms=syms;e.boot_continue();ctx['settle'](e);before=ctx['snapshot'](e)
  def state():
   b=ctx['blocks'](e)
   return dict(location=list(e.location()),scene=b.var('VAR_HOENN_SCENE_DEVON'),briney=b.var('VAR_HOENN_BRINEY_STATE'),flags={f:b.flag(f)for f in FLAGS},Goods=b.item_count('ITEM_DEVON_GOODS'),grunt_won=b.trainer_beaten('TRAINER_HOENN_GRUNT_RUSTURF_TUNNEL'),idle=bool(e.field_idle()))
  ctx['state']=state
  def stage(label):
   image=args.out/(label+'.png');e.shot(str(image),scale=3);report['stages'].append(dict(stage=label,frame=e.frame(),image=str(image),**state()));ctx['emit']()
  def fight():
   turns=0;opponent=None
   while ctx['battle_menu_checked']():
    if opponent is None:opponent=e.u16(syms['gTrainerBattleOpponent_A'])
    assert turns<70,'Bounded battle did not finish';ctx['fight_one_turn'](e,loss=False);turns+=1
   outcome=e.u8(syms['gBattleOutcome']);assert outcome==const('B_OUTCOME_WON'),('Actual battle not won',opponent,outcome)
   report['battles'].append(dict(opponent=opponent,turns=turns,outcome=outcome,actual_keys=True));ctx['emit']()
  def idle():
   for _ in range(1800):
    ctx['safe'](e)
    if e.in_battle() or ctx['is_party_menu']():fight();continue
    if e.field_idle():return
    e.press('B',hold=2,after=14)
   raise AssertionError(('Native field event timeout',state()))
  ctx['idle']=idle
  def matches(name):
   m=ctx['map_info'](name);return e.location()[:2]==(m['group'],m['num'])
  def geom():
   layout=e.u32(syms['gMapHeader']+off('next.MapHeader.mapLayout'));w=e.u32(layout+off('next.MapLayout.width'));h=e.u32(layout+off('next.MapLayout.height'))
   bk=syms['VMap'];stride=e.u32(bk+off('next.BackupMapLayout.Xsize'));rows=e.u32(bk+off('next.BackupMapLayout.Ysize'));ptr=e.u32(bk+off('next.BackupMapLayout.map'))
   assert 1<=w<=256 and 1<=h<=256 and stride>=w+14 and rows>=h+14 and 0x02000000<=ptr and ptr+stride*rows*2<=0x02040000
   return layout,w,h,stride,rows,ptr
  def tile(x,y):
   l,w,h,stride,rows,ptr=geom();pad=const('MAP_OFFSET');assert pad==7 and 0<=x+pad<stride and 0<=y+pad<rows
   return e.u16(ptr+2*((y+pad)*stride+x+pad))
  def behavior(x,y):
   l=geom()[0];primary=e.u32(l+off('next.MapLayout.primaryTileset'));secondary=e.u32(l+off('next.MapLayout.secondaryTileset'))
   split=const('EMERALD_NUM_METATILES_IN_PRIMARY'if e.u8(primary+off('next.Tileset.isEmerald'))else'NUM_METATILES_IN_PRIMARY')
   mid=tile(x,y)&1023;ts,index=(primary,mid)if mid<split else(secondary,mid-split);attr=e.u32(ts+off('next.Tileset.metatileAttributes'));assert 0x08000000<=attr<0x0a000000
   return e.u32(attr+4*index)&511
  def warps():
   events=e.u32(syms['gMapHeader']+off('next.MapHeader.events'));n=e.u8(events+off('next.MapEvents.warpCount'));ptr=e.u32(events+off('next.MapEvents.warps'));assert n<=64;rows=[]
   for i in range(n):
    q=ptr+i*off('next.WarpEvent');rows.append(dict(x=struct.unpack('<h',e.read(q+off('next.WarpEvent.x'),2))[0],y=struct.unpack('<h',e.read(q+off('next.WarpEvent.y'),2))[0],group=e.u8(q+off('next.WarpEvent.mapGroup')),num=e.u8(q+off('next.WarpEvent.mapNum'))))
   return rows
  def actors():
   occupied=set()
   for i in range(16):
    q=syms['gObjectEvents']+i*off('misty_obj');flags=e.u32(q)
    if flags&1 and not flags&(1<<16) and e.u8(q+off('misty_obj.local'))not in[253,254]:
     x,y=struct.unpack('<hh',e.read(q+off('misty_obj.coords'),4));occupied.add((x-7,y-7))
   return occupied
  native_step=ctx['step']
  def step(key,dest=None):
   start=e.location();native_step(key,warp=bool(dest));idle()
   if e.location()[:2]!=start[:2]:assert dest and matches(dest),('Unexpected map',start,key,state())
   report['steps'].append(dict(key=key,start=list(start),finish=list(e.location()),frame=e.frame()))
  def walk(goal,allowed=None,dest=None):
   initial=e.location()[:2]
   for _ in range(550):
    idle()
    if e.location()[:2]!=initial:assert dest and matches(dest);return
    start=e.location()[2:]
    if start==goal:return
    l,w,h,st,rows,ptr=geom();grid=e.read(ptr,st*rows*2);occupied=actors();excluded={(v['x'],v['y'])for v in warps()}-({allowed}if allowed else set());queue=deque([start]);parents={start:None}
    while queue and goal not in parents:
     at=queue.popleft()
     for key,(dx,dy)in KEYS.items():
      q=(at[0]+dx,at[1]+dy)
      if q in parents or q in occupied or q in excluded or not(0<=q[0]<w and 0<=q[1]<h):continue
      v=struct.unpack_from('<H',grid,2*((q[1]+7)*st+q[0]+7))[0]
      if ((v>>10)&3)or(v>>12)not in[0,3]or(v&1023)==1023:continue
      parents[q]=(at,key);queue.append(q)
    assert goal in parents,('No actual collision-valid path',start,goal,sorted(occupied));nxt=goal
    while parents[nxt][0]!=start:nxt=parents[nxt][0]
    step(parents[nxt][1],dest)
   raise AssertionError(('Bounded walking did not finish',goal,state()))
  def transition(key,dest):
   start=e.location();e.hold(key)
   try:
    for _ in range(180):
     ctx['safe'](e);e.run(1)
     if e.location()!=start or not e.field_idle():break
    else:raise AssertionError(('Native transition ignored',start,key))
   finally:e.hold()
   idle();e.run(20);idle();assert matches(dest),('Native warp absent',dest,state())
   report['steps'].append(dict(key=key,transition=True,start=list(start),finish=list(e.location()),frame=e.frame()))
  def warp(xy,dest):
   m=ctx['map_info'](dest);rows=[v for v in warps()if(v['x'],v['y'])==xy];assert len(rows)==1 and(rows[0]['group'],rows[0]['num'])==(m['group'],m['num'])
   mb=behavior(*xy);initial=e.location()[:2]
   if mb==const('MB_WARP_DOOR'):walk((xy[0],xy[1]+1));transition('UP',dest);return
   walk(xy,allowed=xy,dest=dest)
   if e.location()[:2]!=initial:assert matches(dest);return
   directions={const('MB_EAST_ARROW_WARP'):'RIGHT',const('MB_WEST_ARROW_WARP'):'LEFT',const('MB_NORTH_ARROW_WARP'):'UP',const('MB_SOUTH_ARROW_WARP'):'DOWN',const('MB_UP_RIGHT_STAIR_WARP'):'RIGHT',const('MB_DOWN_RIGHT_STAIR_WARP'):'RIGHT',const('MB_UP_LEFT_STAIR_WARP'):'LEFT',const('MB_DOWN_LEFT_STAIR_WARP'):'LEFT'}
   assert mb in directions,('Warp tile did not activate',xy,hex(mb),state());transition(directions[mb],dest)
  def interaction_diag(label,local):
   assert off('misty_obj.coords')==16 and off('misty_obj.local')==8
   rows=[]
   for i in range(const('OBJECT_EVENTS_COUNT')):
    q=syms['gObjectEvents']+i*off('misty_obj');raw=e.read(q,off('misty_obj'));flags=struct.unpack_from('<I',raw)[0]
    if not(flags&1):continue
    is_player=bool(flags&(1<<16))
    if not is_player and raw[8]!=local:continue
    x,y=struct.unpack_from('<hh',raw,16);x-=7;y-=7
    rows.append(dict(slot=i,local=raw[8],player=is_player,graphics=raw[5],map=[raw[10],raw[9]],
     xy=[x,y],flags=hex(flags),visible=not bool(flags&((1<<13)|(1<<14))),
     current_elevation=raw[11]&15,previous_elevation=raw[11]>>4,direction=raw[24]&15,
     single_movement_active=bool(flags&(1<<1)),held_movement_active=bool(flags&(1<<6)),
     tile=hex(tile(x,y)),behavior=hex(behavior(x,y))))
   report.setdefault('interaction_diagnostics',[]).append(dict(label=label,frame=e.frame(),requested_local=local,
    location=list(e.location()),LastTalked=e.u16(syms['gSpecialVar_LastTalked']),objects=rows))
   ctx['emit']()
   return rows
  def talk(key,local):
   at=e.location();interaction_diag('before-turn',local)
   e.press(key,hold=4,after=30);rows=interaction_diag('after-turn',local)
   assert e.location()==at,('Turn unexpectedly moved player',at,e.location())
   player=[r for r in rows if r['player']];npc=[r for r in rows if not r['player']]
   assert len(player)==1 and len(npc)==1 and npc[0]['visible'],('Requested NPC absent/invisible',local,rows)
   wanted=const({'LEFT':'DIR_WEST','RIGHT':'DIR_EAST','UP':'DIR_NORTH','DOWN':'DIR_SOUTH'}[key])
   assert player[0]['direction']==wanted,('Native turn not settled',key,rows)
   e.press('A',hold=3,after=12);interaction_diag('after-actual-A',local)
   for _ in range(300):
    ctx['safe'](e)
    if not e.field_idle()or e.in_battle():break
    e.run(1)
   else:raise AssertionError(('Native A did not activate NPC',local,state(),rows))
   assert e.u16(syms['gSpecialVar_LastTalked'])==local;idle()
  assert matches('RustboroCity');stage('00-natural-theft-save');walk((geom()[1]-1,8));transition('RIGHT','Route116');stage('01-route116')
  warp((47,8),'RusturfTunnel');stage('02-rusturf');walk((13,5))
  assert len(ctx['object_rows'](e,4))==1 and len(ctx['object_rows'](e,5))==1
  stage('03-grunt-before-A');n=len(report['battles']);talk('RIGHT',4);b=ctx['blocks'](e)
  assert len(report['battles'])>n and any(v['opponent']==const('TRAINER_HOENN_GRUNT_RUSTURF_TUNNEL')for v in report['battles'][n:])
  assert b.trainer_beaten('TRAINER_HOENN_GRUNT_RUSTURF_TUNNEL')and b.var('VAR_HOENN_SCENE_DEVON')==3 and b.item_count('ITEM_DEVON_GOODS')==1
  assert all(b.flag(f)for f in FLAGS[:4])and not any(b.flag(f)for f in FLAGS[4:])and b.var('VAR_HOENN_BRINEY_STATE')==const('BRINEY_AT_ROUTE104')
  assert not ctx['object_rows'](e,4)and not ctx['object_rows'](e,5);stage('04-Goods-Peeko');report['rescue_party_ledger']=ctx['preserve'](before)
  warp((4,10),'Route116');stage('05-route116-return');walk((0,8));transition('LEFT','RustboroCity');stage('06-city-return')
  warp((11,15),'RustboroCity_DevonCorp_1F');stage('07-devon1F');warp((14,1),'RustboroCity_DevonCorp_2F');stage('08-devon2F');warp((2,1),'RustboroCity_DevonCorp_3F');stage('09-devon3F')
  report['pre_Stone_native_SAVE_cold']=ctx['flash_reload'](e,'pre-Stone-continuous')
  ctx['preserve'](before);ctx['emit']()
  walk((18,5));talk('LEFT',1);b=ctx['blocks'](e)
  assert b.var('VAR_HOENN_SCENE_DEVON')==4 and b.item_count('ITEM_DEVON_GOODS')==1 and not any(b.flag(f)for f in FLAGS[4:])
  stage('10-Stone-request');first=state();talk('LEFT',1);assert state()==first,'Repeat Stone request changed reward/item/story';stage('11-Stone-repeat')
  saved=ctx['snapshot'](e);story=state();report['native_SAVE_cold']=ctx['flash_reload'](e,'continuous-Stone-request')
  assert ctx['snapshot'](e)==saved and state()==story;report['final_party_ledger']=ctx['preserve'](before);stage('12-SAVE-cold')
  report['cases'].append({'case':'Route116-Rusturf-Grunt-Goods-Peeko-Stone-request','pass':True,'native_SAVE_cold':report['native_SAVE_cold']})
  report.update({'pass':True},status='complete',continuous_rescue_Stone_request=True,PC_33744_bytes_preserved=True)
 except Exception as error:
  if report is None:report={'pass':False,'status':'failed','stages':[]};args.out.mkdir(parents=True,exist_ok=True)
  report.update({'pass':False},status='failed',error=repr(error),traceback=traceback.format_exc())
  if e is not None:
   try:report['failure_location']=list(e.location());report['failure_callback']=hex(e.callback2());e.shot(str(args.out/'failure.png'),scale=3)
   except Exception as diagnostic:report['diagnostic_error']=repr(diagnostic)
 finally:
  if e is not None:e.close()
  protected={**inputs,**ctx.get('protected',{})};unchanged=all(f.exists()and sha(f)==h for f,h in protected.items());report['protected_original_inputs_unchanged']=unchanged
  if not unchanged:report.update({'pass':False},status='failed',preservation_error='Protected input changed')
  (args.out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(pass_all=report['pass'],stages=len(report['stages']),error=report.get('error'))),flush=True)
 return 0 if report['pass']else 1
if __name__=='__main__':raise SystemExit(main())
