"""Separate QA-only preboot HP/Splash fixtures; real double battle, replacement/loss and SAVE. Original SAV/ROM and story/warp flags are never changed."""
import argparse, ast, hashlib, json, os, struct, sys, traceback
from collections import deque
from pathlib import Path
R6='0eee66671ba7af7309117d098296a233a58985f9da881b4d4a8a479780f1ea1a'
PRIOR='37966a11833191dc2ad6cb0ee26df2a4226db9f3d7c673c2fe11bd7a66601641'
SEED='888f205f324d696415e9206e55ea2f8dc73d71a7141ff06c3030392270898fb4'
USER='917c24715ca1dd78b22d6350182648fa81f307b771fa5524595d157a0b6a6604'
BASE='work/misty-followup-20261014/'
CHECKPOINT='work/hoenn-resume-20261014/native-delivery-r1/pre-twins-continuous-native-QA-only.sav'
CHECKPOINT_SHA='a0cde53f90c5d29173669eadb1575b23e9e48b4ff5f017d0bf40f4df100ca17c'
CHECKPOINT_REPORT='work/hoenn-resume-20261014/native-delivery-r1/validation.json'
CHECKPOINT_REPORT_SHA='b0ea3d07009558f6ceb6fe0610050fb58ef8661073d37b595e1c8a126aa88443'
SOURCE_HASHES={'data/maps/PetalburgWoods/scripts.inc': 'fe6b8eef9c01cd6b87cc956b705b5aded3cfb558d413c29d78a4758d2b1480b9', 'data/maps/RustboroCity_DevonCorp_3F/map.json': '04ea081e3cd15a31bc2fd2a284f3d40075f157ebdd8d6a678144421c42cb75c3', 'data/maps/SlateportCity_Harbor/scripts.inc': 'b2662fae38a01e75163a736b4f9a0e05db05e3e505276b8d052cf146503ced95', 'data/layouts/HoennRoute104/border.bin': 'aa298641e3346d9c7ac51454222ff057768946e61980fd82e4db65912df412fe', 'data/maps/RustboroCity_DevonCorp_2F/scripts.inc': '91d529b3199102d53817c6d6449ddd7fe58d82a5db9853f63e2551e72c5e8c0a', 'data/maps/SlateportCity/map.json': '4e768ba910ba8767b99d5c3ce29a02c8e9aaf7d66dd09a703f91edb5cbb33fe4', 'work/hoenn-resume-20261014/native-continuation-r4/validation.json': '090fa55d12da7bf45cb7e769503201208dc25a53fb464afbeda677f582e9298c', 'data/maps/PetalburgWoods/map.json': 'b3ec7e0535734e4abdad38ec298c4a4b695161545d5afb4d7567ae4ba48bdd0e', 'data/maps/RustboroCity_DevonCorp_2F/map.json': 'c76414777e7fea26acccb13c9db35b4ad63b7bafbd0b10963521356a9ff9410b', 'data/layouts/HoennSlateportCity/border.bin': '0c2871e576a63043efd779a5664d84741cc6512c07b03ae39e8deb07b064d3a4', 'data/maps/SlateportCity_Harbor/map.json': '31d2a3475249aaaac9325492938dc572520dfcde2398c8091ea1f59c13e99ae7', 'data/maps/Route104/scripts.inc': 'e09bf6a31f9400c34b386c0c7f68e9722bc975e260d8d2122930f72888792c3c', 'data/layouts/HoennHarbor/map.bin': 'ec418c60c4f5cac3eb4ee9e2a29e1f48709e552411f67086a5352945001afcbc', 'src/field_specials.c': 'f8448fb911ce7fb8d16a28bd58aeda8890d11c1d7f60211793cb279661331a87', 'data/layouts/HoennPetalburgWoods/map.bin': '053fc2e64d7065edaf0bfaa4b7504fef15ad808dc458f8b937cb3a2604495442', 'work/hoenn-resume-20261014/native_devon_continuation_r4.py': '7232e75f505432b542ecaa28310c3ddb4a257958a6f5c826b4711b6718b12978', 'data/layouts/HoennRustboroCity_DevonCorp_1F/border.bin': '9ff63640fa3b4682056532b7924b03250ccc7a832f64ccec3dea79ea8595a24d', 'data/layouts/HoennRustboroCity_DevonCorp_2F/map.bin': '2b6356ff72f7a014080fb98be0a9d59f7c8ecb16264af571d41436d82efec11e', 'data/layouts/HoennRustboroCity_DevonCorp_3F/border.bin': '9ff63640fa3b4682056532b7924b03250ccc7a832f64ccec3dea79ea8595a24d', 'data/layouts/HoennRustboroCity/map.bin': '5d1838e9e5c8f8a3bd519b0f7adaf1f01ef556deb9f8d5b46ec5996b26d51c4d', 'work/hoenn-resume-20261014/native-continuation-r3/pre-Stone-continuous-native-QA-only.sav': '9dbb27eb6951a1f62af50f35c4411b8a49adcf5cf8b682f9231db333ce4ebf93', 'data/maps/Route104/map.json': '113e20ea3e11db734eb88f5b894ed994986e516a4c482ffc4919ef2167f624d8', 'data/layouts/HoennRoute109/map.bin': '4f6c0180928cdc3268eaef6331137696f24626c9e618361b937a1d0b9a664d23', 'work/hoenn-resume-20261014/native-continuation-r4/continuous-Stone-request-native-QA-only.sav': '6db6e30c011568151cbb647be4d4dd92b78489f7c025150c6236df7a0937404c', 'data/maps/RustboroCity/scripts.inc': '70f4a1df10854a9ebe202de377b4a693e3bf9f8e5bf866d377712a1116d7a990', 'data/layouts/layouts.json': '98bf104f2682e018439f22092d0321c3c75b7cb1a0c5d1a45e3135a9076ba75c', 'data/maps/RustboroCity_DevonCorp_1F/scripts.inc': '0b8f42c5311d986a17d2c65fddb19a43e13b48fd53519a1048ac6e3b526c4e7e', 'work/hoenn-resume-20261014/native-continuation-r3/validation.json': 'b3d98bacf4a83f192e6a8a18ae2cafc29cd52ba87c9cfc99e3e80f218ac0a2e1', 'data/maps/Route109/scripts.inc': 'd3543f7f44b7609612e4240cb9e85c7c770fa7e46126f5471658fb29d8e3ded9', 'data/maps/RustboroCity/map.json': 'f0271bcea1cf27c09c8e4b659c07fcc011825ee60f885d904d22f5962e2a3d92', 'data/layouts/HoennHarbor/border.bin': '9ff63640fa3b4682056532b7924b03250ccc7a832f64ccec3dea79ea8595a24d', 'data/layouts/HoennRoute104/map.bin': '4dcbb4276d1010228e45ebe2dd1e3c9c2bd5843ba127ae108968c646d41f4329', 'work/hoenn-resume-20261014/abi-profile/devon-v7-abi.json': 'fb95943ada51c72d99456b5127fe147878593e166c2e9d12a9b46d0a4fb6ffac', 'data/layouts/HoennPetalburgWoods/border.bin': 'aa298641e3346d9c7ac51454222ff057768946e61980fd82e4db65912df412fe', 'data/maps/RustboroCity_DevonCorp_1F/map.json': '1e62fe59520f4e18e98f95140297e7668ed6ac41cae0b2072daf97acd56139bd', 'data/maps/Route109/map.json': '158c191d3c17391be4e8b4ebb4bf772682331ea590180959b11cb7fbc535114d', 'data/layouts/HoennRustboroCity_DevonCorp_2F/border.bin': '9ff63640fa3b4682056532b7924b03250ccc7a832f64ccec3dea79ea8595a24d', 'data/layouts/HoennRustboroCity/border.bin': 'aa298641e3346d9c7ac51454222ff057768946e61980fd82e4db65912df412fe', 'data/layouts/HoennSlateportCity/map.bin': '7094d5feff9cdd39816b71b7aaa31cf9c099c0d06f0a85e9b048d3a801cec136', 'data/layouts/HoennRoute109/border.bin': '0c2871e576a63043efd779a5664d84741cc6512c07b03ae39e8deb07b064d3a4', 'data/maps/RustboroCity_DevonCorp_3F/scripts.inc': 'e5832efa342f5554cbbcf8c46f39d166099c3883baaaed6482707386cd895ba4', 'data/maps/SlateportCity/scripts.inc': 'd824178a79762249d651aa0cbbb01e42c7d5b1d42b6413895ab6b1bd9be53934', 'data/layouts/HoennRustboroCity_DevonCorp_1F/map.bin': '4c5ad76bd2fb5a4d65914978338551c240f2e966c6f8f5a91346db1118bf6cbc', 'data/layouts/HoennRustboroCity_DevonCorp_3F/map.bin': '9805c919da40c085f1347a6b5f22ea3f928d3801204c7fe2aa0a63c4e46b2129', 'src/script_menu.c': '2db6f57f7626596dbe535e0822df38e1dbd5be683e5bda480fd4b7f8b00099d5', 'include/constants/menu.h': '1e4da1925ac7c158c1009ea99f30e85c864ef6bc5bbe6e22b23bc43d7d0f8e42', 'src/battle_controller_player.c': '7b06dd00b081fc88caa550b6533f191a14c2f3f2164cf3e334c31794c1b8d277', 'include/battle_controllers.h': '051ebf096d6538d1cc7ea321dacf5d3e9e54f0d4edc9ddeb29996242de618120', 'include/constants/party_menu.h': 'fc481059b8088c9e64d8a813e93232bd11b0ae31e7853e269c982372b682283f', 'include/battle.h': '9b774f757d1e5aa72f3ebcf4ced3a12c165c28ff848e2bb529d228534a4b206d', 'src/battle_main.c': '2a39e045ff105b9c265173de81d5a88c6ab2146052d5a918a63112b0e3562920', 'work/hoenn-resume-20261014/native_double_controller_r2.py': '30346bab00d76d1b553c6aaffa89212909042fc11a24624c6715a23f850073ec'}
KEYS={'UP':(0,-1),'DOWN':(0,1),'LEFT':(-1,0),'RIGHT':(1,0)}
FLAGS=['FLAG_HOENN_GOT_DEVON_GOODS','FLAG_HOENN_PEEKO_RESCUED','FLAG_HIDE_HOENN_RUSTURF_GRUNT',
       'FLAG_HIDE_HOENN_RUSTURF_PEEKO','FLAG_HOENN_DEVON_GOODS_DELIVERED','FLAG_HOENN_GOT_EXP_SHARE']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for n in ['root','rom','elf','sav','abi-json','out']:p.add_argument('--'+n,required=True,type=Path)
 for n in ['rom','elf','abi']:p.add_argument('--expect-'+n+'-sha',required=True)
 p.add_argument('--fixture-case',required=True,choices=['replacement','loss'])
 args=p.parse_args();root=args.root.resolve(strict=True);os.chdir(root)
 args.out=args.out.resolve();assert not args.out.exists() and args.out.is_relative_to(root/'work')
 for n in ['rom','elf','sav','abi_json']:setattr(args,n,getattr(args,n).resolve(strict=True))
 ctl=root/(BASE+'r2-tools/native-devon-v7-r6.py');prior=root/(BASE+'native-v7-r6/validation.json');seed=root/(BASE+'native-v7-r6/scene1-Devon-native-QA-only.sav')
 checkpoint=root/CHECKPOINT;checkpoint_report=root/CHECKPOINT_REPORT
 inputs={ctl:R6,prior:PRIOR,seed:SEED,checkpoint:CHECKPOINT_SHA,checkpoint_report:CHECKPOINT_REPORT_SHA,args.sav:USER,args.rom:args.expect_rom_sha,args.elf:args.expect_elf_sha,args.abi_json:args.expect_abi_sha}
 inputs.update({root/rel:h for rel,h in SOURCE_HASHES.items()})
 for f,h in inputs.items():assert len(h)==64 and sha(f)==h,('Input changed',str(f))
 old=json.loads(prior.read_text());case=[c for c in old['cases'] if c['scene_at_boot']==1]
 assert old['pass'] and old['protected_original_inputs_unchanged'] and old['SAV_sha256']==USER
 assert len(case)==1 and case[0]['pass'] and case[0]['actual_Roxanne_win'] and case[0]['continuous_Gym_exit_and_City_coord'] and case[0]['expected_theft']
 assert Path(case[0]['SAVE_cold']['qa_save']).resolve()==seed.resolve()
 partial=json.loads(checkpoint_report.read_text())
 assert partial['protected_original_inputs_unchanged'] and partial['ROM_sha256']==args.expect_rom_sha and partial['ELF_sha256']==args.expect_elf_sha and partial['SAV_sha256']==USER
 assert all(partial[k]==0 for k in ['RAM_writes','direct_script_calls','forced_battle_outcomes'])
 assert not partial['pass'] and partial['status']=='failed'
 assert partial['error']=="AssertionError(('Native step blocked', (52, 9, 11, 14), 'UP'))"
 assert partial['battles'] and partial['boat_menus'][0]['actual_keys']
 arrived=[v for v in partial['stages'] if v['stage']=='03-before-twins'];assert len(arrived)==1
 a=arrived[0]
 assert a['location']==[43,19,26,16] and not a['twins_won'] and a['scene']==4 and a['Goods']==1 and a['grunt_won'] and a['idle']
 assert all(a['flags'][f] for f in FLAGS[:4]) and not any(a['flags'][f] for f in FLAGS[4:])
 saved_checkpoint=partial['before_twins_native_SAVE_cold']
 assert Path(saved_checkpoint['qa_save']).resolve()==checkpoint.resolve()
 assert saved_checkpoint['checksummed_sectors']==14 and saved_checkpoint['counter']==[70,71]
 text=ctl.read_text();tree=ast.parse(text);tries=[n for n in tree.body if isinstance(n,ast.Try)];assert len(tries)==1
 prefix=tree.body[:tree.body.index(tries[0])];body=[];removed=0
 for n in tries[0].body:
  if isinstance(n,ast.FunctionDef) and n.name=='fixture':break
  if isinstance(n,ast.Assert) and n.msg and isinstance(n.msg,ast.Constant) and n.msg.value=='This v7 is prepared for the approved e156 ROM':removed+=1;continue
  body.append(n)
 assert removed==1 and any(isinstance(n,ast.FunctionDef) and n.name=='native_send_out' for n in body)
 sys.argv=['continuation','--root',str(root),'--rom',str(args.rom),'--elf',str(args.elf),'--sav',str(args.sav),'--expect-rom-sha',args.expect_rom_sha,'--expect-elf-sha',args.expect_elf_sha,'--expect-sav-sha',USER,'--abi-json',str(args.abi_json),'--out',str(args.out)]
 sys.path.insert(0,str(root/'tools/qa'))
 import gamedata as regression_gamedata
 regression_gamedata.CACHE=str(args.out/'compiler-cache')
 ctx={'__file__':str(ctl),'__name__':'verified_continuation_controller'};e=None;report=None
 try:
  exec(compile(ast.Module(body=prefix+body,type_ignores=[]),'<verified-r6-preflight-controller>','exec'),ctx)
  report=ctx['report'];report.update({'pass':False},status='running',runner_version=9,runner_revision=3,cases=[],stages=[],steps=[],battles=[],
   scope='Separate QA-only HP/status/Splash preboot fixture from natural pre-twins SAVE; actual double replacement or loss; no parcel route replay',prior_preboot_eligibility_fixture=True,
   this_test_preboot_save_edits=True,fixture_case=args.fixture_case,full_Hoenn_campaign_tested=False,Stern_delivery_completed=False,actual_device_fps_measured=False,
   continuation_seed_sha256=CHECKPOINT_SHA,prior_route_seed_sha256=SEED,prior_validation_sha256=PRIOR,prior_native_SAVE=case[0]['SAVE_cold'])
  ctx['protected'].update({f.resolve():h for f,h in inputs.items()});gd,off,const,syms=[ctx[n]for n in ['gd','off','const','syms']]
  for h in ['fieldmap.h','constants/metatile_behaviors.h','constants/menu.h','constants/party_menu.h']:
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
  report.update(checkpoint_sha256=CHECKPOINT_SHA,checkpoint_validation_sha256=CHECKPOINT_REPORT_SHA,prior_partial_delivery_stages=partial['stages'],prior_actual_battles=partial['prior_actual_battles'],prior_checkpoint_SAVE_cold=saved_checkpoint,prior_rescue_and_Devon_exit_replayed_this_run=False,only_twins_replayed_this_run=True)
  assert any(v['opponent']==const('TRAINER_HOENN_GRUNT_RUSTURF_TUNNEL') and v['outcome']==const('B_OUTCOME_WON') and v['actual_keys'] for v in partial['prior_actual_battles'])
  seedfile=ctx['SaveFile'](str(checkpoint))
  assert len(seedfile.layout)==14 and seedfile.counter==71
  for _,sid,size in seedfile.layout:
   pos=seedfile.where[sid]*4096
   assert ctx['checksum'](seedfile.raw[pos:pos+size])==struct.unpack_from('<H',seedfile.raw,pos+0xff6)[0],('Checkpoint sector checksum',sid)
  assert seedfile.var('VAR_HOENN_SCENE_DEVON')==4 and seedfile.flag('FLAG_HOENN_BADGE01_GET')
  assert seedfile.trainer_beaten('TRAINER_HOENN_ROXANNE_1') and seedfile.trainer_beaten('TRAINER_HOENN_GRUNT_RUSTURF_TUNNEL')
  assert seedfile.item_count('ITEM_DEVON_GOODS')==1 and all(seedfile.flag(f)for f in FLAGS[:4]) and not any(seedfile.flag(f)for f in FLAGS[4:])
  gd.FIELDS.update({'reg.hp':('Pokemon','hp'),'reg.maxHP':('Pokemon','maxHP'),'reg.status':('Pokemon','status')});gd._OFFSETS=None
  hp,maxhp,status=[off('reg.'+k)for k in ['hp','maxHP','status']]
  assert hp==ctx['AF']['Pokemon.hp'] and off('pokemon')==100
  report['compiler_fixture_offsets']={'hp':hp,'maxHP':maxhp,'status':status}
  assert seedfile.party_count()==6 and not seedfile.trainer_beaten('TRAINER_HOENN_GINA_AND_MIA_1')
  original_blocks={k:bytes(v)for k,v in seedfile.blocks.items()};allowed=set();ledger=[]
  for i in range(6):
   m=seedfile.party_mon(i);subs=m.subs();raw=bytes(m.blk[m.o:m.o+100]);oldcore=bytes(subs['M'])
   assert m.has_species() and not m.is_egg() and not(raw[19]&1)
   assert (sum(v[0]for sub in subs.values()for v in struct.iter_unpack('<H',sub))&65535)==struct.unpack_from('<H',raw,28)[0]
   weak=args.fixture_case=='loss' or i<2
   if weak:
    struct.pack_into('<4H',subs['A'],0,const('MOVE_SPLASH'),0,0,0);subs['A'][8:12]=bytes([40,0,0,0]);subs['G'][8]=0;m.put_subs(subs)
    allowed.update(range(m.o+28,m.o+30));allowed.update(range(m.o+32,m.o+80))
   else:assert any(mid and pp for mid,pp in zip(struct.unpack_from('<4H',subs['A']),subs['A'][8:12])),('Bench has no usable PP',i)
   wanted=1 if weak else struct.unpack_from('<H',raw,maxhp)[0];assert wanted>0
   struct.pack_into('<H',m.blk,m.o+hp,wanted);struct.pack_into('<I',m.blk,m.o+status,0)
   allowed.update(range(m.o+hp,m.o+hp+2));allowed.update(range(m.o+status,m.o+status+4))
   assert bytes(m.subs()['M'])==oldcore
   ledger.append(dict(slot=i,pid=m.personality,ot=m.otid,species=m.species(),weak=weak,HP_before=struct.unpack_from('<H',raw,hp)[0],HP_fixture=wanted,moves_before=list(struct.unpack_from('<4H',ctx['Mon'](bytearray(raw),0).subs()['A'])),moves_fixture=list(struct.unpack_from('<4H',m.subs()['A'])),status_before=struct.unpack_from('<I',raw,status)[0],status_fixture=0,IV_and_origin_unchanged=True))
  diffs=[i for i,(a,b)in enumerate(zip(original_blocks['sb1'],seedfile.sb1))if a!=b]
  assert diffs and set(diffs)<=allowed and bytes(seedfile.sb2)==original_blocks['sb2'] and bytes(seedfile.blocks['storage'])==original_blocks['storage']
  fixture=args.out/(args.fixture_case+'-PREBOOT-QA-ONLY.sav');assert not fixture.exists();seedfile.save(str(fixture))
  prepared=ctx['SaveFile'](str(fixture));assert prepared.counter==71 and prepared.location()==ctx['SaveFile'](str(checkpoint)).location()
  for _,sid,size in prepared.layout:
   pos=prepared.where[sid]*4096;assert ctx['checksum'](prepared.raw[pos:pos+size])==struct.unpack_from('<H',prepared.raw,pos+0xff6)[0]
  ctx['protected'][fixture.resolve()]=sha(fixture)
  report.update(fixture_sha256=sha(fixture),fixture_party_ledger=ledger,fixture_changed_sb1_offsets=diffs,fixture_sb2_and_PC_unchanged=True)
  e=ctx['ReadOnlyEmu'](str(args.rom),str(fixture),sym='');ctx['e']=e;e.syms=syms;e.boot_continue();ctx['settle'](e);before=ctx['snapshot'](e)
  def state():
   b=ctx['blocks'](e)
   return dict(location=list(e.location()),scene=b.var('VAR_HOENN_SCENE_DEVON'),briney=b.var('VAR_HOENN_BRINEY_STATE'),flags={f:b.flag(f)for f in FLAGS},Goods=b.item_count('ITEM_DEVON_GOODS'),DiveBalls=b.item_count('ITEM_DIVE_BALL'),ExpShare=b.item_count('ITEM_EXP_SHARE'),grunt_won=b.trainer_beaten('TRAINER_HOENN_GRUNT_RUSTURF_TUNNEL'),twins_won=b.trainer_beaten('TRAINER_HOENN_GINA_AND_MIA_1'),idle=bool(e.field_idle()))
  ctx['state']=state
  def stage(label):
   image=args.out/(label+'.png');e.shot(str(image),scale=3);report['stages'].append(dict(stage=label,frame=e.frame(),image=str(image),**state()));ctx['emit']()
  controller_path=root/'work/hoenn-resume-20261014/native_double_controller_r2.py'
  controller_scope={'__file__':str(controller_path)}
  exec(compile(controller_path.read_text(),str(controller_path),'exec'),controller_scope)
  controller_scope['install'](ctx)
  def fight():return ctx['fight_native_indexed']()
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
   start=e.location()
   try:native_step(key,warp=bool(dest))
   except AssertionError as blocked:
    reason=blocked.args[0] if blocked.args else None
    if not isinstance(reason,tuple) or reason[0]!='Native step blocked' or e.field_idle() or not e.in_overworld():raise
    pending=dict(key=key,location=list(e.location()),field_idle=bool(e.field_idle()),frame=e.frame())
    idle();assert e.location()==start,('Pending field event moved player',start,state())
    pending.update(after_actual_dialogue_inputs=list(e.location()),after_frame=e.frame(),retried_once=True)
    report.setdefault('pending_map_event_retries',[]).append(pending);ctx['emit']()
    native_step(key,warp=bool(dest))
   idle()
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
  menu_rows=[v for v in ctx['actual_rows'].get('Task_MultichoiceMenu_HandleInput',[]) if Path(v['translation_unit']).name in ['script_menu.o','script_menu.c']]
  assert len(menu_rows)==1;menu_row=menu_rows[0];menu_sec=ctx['sections'][menu_row['section']];menu_func=menu_row['value']&~1
  assert (menu_row['info']&15)==2 and menu_row['size']>0 and menu_sec[2]&6==6 and menu_sec[3]<=menu_func and menu_func+menu_row['size']<=menu_sec[3]+menu_sec[5]
  assert 0x08000000<=menu_func<0x0a000000
  report['boat_task_symbol_binding']=menu_row
  AF=ctx['AF'];assert AF['Task.size']==40 and ctx['ABI']['task_count']==16 and AF['Menu.cursorPos']==2
  def menu_tasks():
   return [i for i in range(ctx['ABI']['task_count']) if e.u8(syms['gTasks']+i*AF['Task.size']+AF['Task.isActive']) and (e.u32(syms['gTasks']+i*AF['Task.size']+AF['Task.func'])&~1)==menu_func]
  def boat(key,local,choice,dest,wanted_state):
   at=e.location();e.press(key,hold=4,after=30);assert e.location()==at
   e.press('A',hold=3,after=12)
   for _ in range(600):
    ctx['safe'](e)
    if menu_tasks():break
    assert not e.in_battle() and not ctx['is_party_menu']();e.run(1)
   else:raise AssertionError(('Real Briney menu did not open',local,state()))
   assert len(menu_tasks())==1 and e.u16(syms['gSpecialVar_LastTalked'])==local
   tag='boat-menu-'+str(len(report.get('boat_menus',[])));e.shot(str(args.out/(tag+'.png')),scale=3)
   cursor=lambda:e.u8(syms['sMenu']+AF['Menu.cursorPos']);trace=[]
   for _ in range(5):
    assert len(menu_tasks())==1;cur=cursor();trace.append(cur);assert 0<=cur<3
    if cur==choice:break
    e.press('DOWN' if cur<choice else 'UP',hold=2,after=14)
   else:raise AssertionError(('Real boat cursor did not select requested dock',choice,trace))
   assert cursor()==choice;e.press('A',hold=3,after=1)
   for _ in range(120):
    if not menu_tasks():break
    ctx['safe'](e);e.run(1)
   else:raise AssertionError('Real boat menu did not accept A')
   idle();assert matches(dest) and ctx['blocks'](e).var('VAR_HOENN_BRINEY_STATE')==const(wanted_state)
   report.setdefault('boat_menus',[]).append(dict(start=list(at),local=local,choice=choice,cursor_trace=trace,destination=dest,finish=list(e.location()),actual_keys=True));ctx['emit']()
  def scene(expected,goods,delivered,reward):
   b=ctx['blocks'](e)
   assert b.var('VAR_HOENN_SCENE_DEVON')==expected and b.item_count('ITEM_DEVON_GOODS')==goods
   assert all(b.flag(f)for f in FLAGS[:4]) and b.flag(FLAGS[4])==delivered and b.flag(FLAGS[5])==reward
  assert matches('Route104') and e.location()[2:]==(26,16)
  scene(4,1,False,False);stage('00-QA-fixture-boot')
  wanted=const('B_OUTCOME_LOST'if args.fixture_case=='loss'else'B_OUTCOME_WON');ctx['expected_native_outcome']=wanted
  baseline_goods=ctx['blocks'](e).item_count('ITEM_DEVON_GOODS')
  e.hold('RIGHT')
  try:
   for _ in range(120):
    ctx['safe'](e);e.run(1)
    if e.location()[2:]!=(26,16):break
   else:raise AssertionError('Actual RIGHT did not enter twins sight')
  finally:e.hold()
  assert e.location()[:2]==(43,19) and e.location()[2:]==(27,16)
  for _ in range(2400):
   ctx['safe'](e)
   if e.in_battle():break
   e.press('B',hold=2,after=14)
  else:raise AssertionError('Actual twins sight did not enter double battle')
  assert e.u16(syms['gTrainerBattleOpponent_A'])==const('TRAINER_HOENN_GINA_AND_MIA_1') and e.u32(syms['gBattleTypeFlags'])&const('BATTLE_TYPE_DOUBLE')
  stage('01-actual-twins-double-battle')
  result=fight();assert result==wanted;idle()
  assert len(report['battles'])==1 and report['battles'][0]['double'] and report['battles'][0]['selected_battlers']==[0,2]
  b=ctx['blocks'](e);assert b.var('VAR_HOENN_SCENE_DEVON')==4 and b.item_count('ITEM_DEVON_GOODS')==baseline_goods
  assert all(b.flag(f)for f in FLAGS[:4]) and not any(b.flag(f)for f in FLAGS[4:])
  replaced=report.get('replacements',[])
  if args.fixture_case=='replacement':
   assert replaced and b.trainer_beaten('TRAINER_HOENN_GINA_AND_MIA_1') and matches('Route104')
  else:assert not b.trainer_beaten('TRAINER_HOENN_GINA_AND_MIA_1')
  assert all(v['accepted'] and v['selected_ui_slot_verified'] and v['candidate_HP']>0 and v['battle_index'] not in v['active_battle_indexes'] and v['battle_index']!=v['reserved_battle_index'] for v in replaced)
  report['fixture_baseline_party_ledger']=ctx['preserve'](before);stage('02-actual-outcome-settled')
  live=ctx['snapshot'](e);story=state();report['native_SAVE_cold']=ctx['flash_reload'](e,'twins-'+args.fixture_case)
  assert ctx['snapshot'](e)==live and state()==story
  report['final_fixture_party_ledger']=ctx['preserve'](before);stage('03-QA-SAVE-cold')
  report['cases'].append({'case':'twins-'+args.fixture_case,'pass':True,'actual_outcome':result,'replacements':len(replaced),'native_SAVE_cold':report['native_SAVE_cold']})
  report.update({'pass':True},status='complete',only_QA_fixture_inputs_mutated=True,native_Briney_Stern_ExpShare_continuation=False,Stern_delivery_completed=False,PC_33744_bytes_preserved=True,double_replacement_loss_fixture_executed=args.fixture_case)
 except Exception as error:
  if report is None:report={'pass':False,'status':'failed','stages':[]};args.out.mkdir(parents=True,exist_ok=True)
  report.update({'pass':False},status='failed',error=repr(error),traceback=traceback.format_exc())
  if e is not None:
   try:
    report['failure_location']=list(e.location());report['failure_callback']=hex(e.callback2());e.shot(str(args.out/'failure.png'),scale=3)
    if 'tile' in locals():
     x,y=e.location()[2:];rows=[]
     for i in range(const('OBJECT_EVENTS_COUNT')):
      q=syms['gObjectEvents']+i*off('misty_obj');raw=e.read(q,off('misty_obj'));flags=struct.unpack_from('<I',raw)[0]
      if not(flags&1):continue
      xx,yy=struct.unpack_from('<hh',raw,16)
      rows.append(dict(slot=i,local=raw[8],xy=[xx-7,yy-7],flags=hex(flags),elevation=[raw[11]&15,raw[11]>>4],direction=raw[24]&15))
     report['live_failure_before_SAVE']=dict(field_idle=bool(e.field_idle()),objects=rows,tiles={str((xx,yy)):dict(tile=hex(tile(xx,yy)),behavior=hex(behavior(xx,yy)))for xx,yy in [(x,y),(x,y-1),(x+1,y)]})
    if e.in_overworld() and e.field_idle():report['failure_native_SAVE_cold']=ctx['flash_reload'](e,'failed-native-continuation')
   except Exception as diagnostic:report['diagnostic_error']=repr(diagnostic)
 finally:
  if e is not None:e.close()
  protected={**inputs,**ctx.get('protected',{})};unchanged=all(f.exists()and sha(f)==h for f,h in protected.items());report['protected_original_inputs_unchanged']=unchanged
  if not unchanged:report.update({'pass':False},status='failed',preservation_error='Protected input changed')
  (args.out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(pass_all=report['pass'],stages=len(report['stages']),error=report.get('error'))),flush=True)
 return 0 if report['pass']else 1
if __name__=='__main__':raise SystemExit(main())
