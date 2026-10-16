import hashlib,json,pathlib,sys
from emu import Emu,GameReset
from savefile import SaveFile
import gamedata,native_misty_performance_helper as budget
class ReadOnlyEmu(Emu):
 def write(self,*args):raise AssertionError('field QA must not poke RAM')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def party(s):
 o=gamedata.off('sb1.playerParty');n=6*gamedata.off('pokemon')
 return bytes(s.sb1[o:o+n]),s.party_count()
def dex_records(s):
 n=(gamedata.const('NUM_SPECIES')+7)//8
 return tuple(bytes(b[o:o+n]) for b,o in ((s.sb2,gamedata.off('sb2.pokedex')+gamedata.off('dex.owned')),(s.sb2,gamedata.off('sb2.pokedex')+gamedata.off('dex.seen')),(s.sb1,gamedata.off('sb1.seen1')),(s.sb1,gamedata.off('sb1.seen2'))))
def runtime_dex(e):
 s1=e.ptr('gSaveBlock1Ptr');s2=e.ptr('gSaveBlock2Ptr');n=(gamedata.const('NUM_SPECIES')+7)//8
 return tuple(e.read(o,n) for o in (s2+gamedata.off('sb2.pokedex')+gamedata.off('dex.owned'),s2+gamedata.off('sb2.pokedex')+gamedata.off('dex.seen'),s1+gamedata.off('sb1.seen1'),s1+gamedata.off('sb1.seen2')))
def runtime_regional_flags(e):
 s1=e.ptr('gSaveBlock1Ptr');s2=e.ptr('gSaveBlock2Ptr')
 f=gamedata.off('sb1.flags');end=gamedata.off('sb1.vars')
 t=gamedata.off('sb2.hoennTrainerFlags');h=gamedata.off('sb2.hoennFlags');v=gamedata.off('sb2.hoennVars')
 assert 0<f<end and 0<t<h<v
 return e.read(s1+f,end-f),e.read(s2+t,h-t),e.read(s2+h,v-h)
def one_step(e,key):
 old=e.location();dx=1 if key=='RIGHT' else -1;want=(*old[:2],old[2]+dx,old[3])
 e.hold(key)
 try:
  for _ in range(120):
   e.run(1)
   if e.location()!=old:break
  else:raise TimeoutError(('step did not start',old,key))
 finally:e.hold()
 assert e.location()==want,('step overshot',e.location(),want)
 e.run(32);assert e.location()==want and e.field_idle(),('step did not settle',e.location())
rom,source,user_original,join_proof,out=map(pathlib.Path,sys.argv[1:6]);elf=rom.with_suffix('.elf');sym=rom.with_suffix('.sym')
assert source.resolve()!=user_original.resolve(),'use the actual QA-only joined native SAV, never the user original'
gamedata.FIELDS.update({'misty_sprite.x':('Sprite','x'),'misty_sprite.y':('Sprite','y'),'misty_sprite.x2':('Sprite','x2'),'misty_sprite.y2':('Sprite','y2'),'misty_sprite.cy':('Sprite','centerToCornerVecY')});gamedata._OFFSETS=None
assert elf.is_file() and sym.is_file(),'candidate ELF/SYM must accompany ROM'
proof=json.loads(join_proof.read_text());assert proof['all_pass'] and proof['actual_A_join_tested'] and proof['native_battery_save_and_cold']
proof_save=next(c['save']['qa_save'] for c in proof['checks'] if c['case']=='joined_native_save_cold_trail')
assert pathlib.Path(proof_save).resolve()==source.resolve(),'joined input does not match its native SAVE/cold proof'
cases=[dict(map='PalletTown',save=str(source.resolve()))];expected={'PalletTown':(5,9)}
out.mkdir(parents=True,exist_ok=False);original=sha(source);reference=SaveFile(str(source));reference_party=party(reference);reference_pc=bytes(reference.blocks['storage']);reference_dex=dex_records(reference);results=[]
protected={str(p):sha(p) for p in (rom,elf,sym,source,user_original,join_proof)}
user=SaveFile(str(user_original));assert reference_party==party(user) and reference_pc==bytes(user.blocks['storage']) and reference_dex==dex_records(user),'joined fixture changed original party/PC/dex'
assert reference.flag('FLAG_MISTY_COMPANION_JOINED') and reference.flag('FLAG_HIDE_MISTY_PALLET') and reference.flag('FLAG_RECEIVED_STARTER_PIKACHU')
assert reference.flag('FLAG_SYS_GAME_CLEAR') and all(reference.flag('FLAG_BADGE%02d_GET'%(i+1)) for i in range(8))
m=gamedata.map_info('PalletTown');meta=m['json'];assert len(meta['object_events'])==4
assert meta['object_events'][3]['script']=='PalletTown_EventScript_MistyJoin' and meta['object_events'][3]['flag']=='FLAG_HIDE_MISTY_PALLET'
for kind in ('object_events','warp_events','coord_events','bg_events'):
 assert not any(v.get('y')==9 and 5<=v.get('x',-1)<=10 for v in meta[kind]),('corridor event/object',kind)
layouts=json.loads(pathlib.Path('data/layouts/layouts.json').read_text())['layouts'];rows=[v for v in layouts if v.get('id')==meta['layout']];assert len(rows)==1
raw=pathlib.Path(rows[0]['blockdata_filepath']).read_bytes();width=rows[0]['width']
assert all(int.from_bytes(raw[2*(9*width+x):2*(9*width+x)+2],'little')==0x3296 for x in range(5,11)),'reviewed Pallet long corridor changed'
for c in cases:
 name=c['map'];sav=pathlib.Path(c['save']);assert sav.is_absolute()
 fixture_sha=sha(sav);s=SaveFile(str(sav));assert party(s)==reference_party and bytes(s.blocks['storage'])==reference_pc and dex_records(s)==reference_dex,'fixture changed original Pokemon'
 m=gamedata.map_info(name);want=(m['group'],m['num'],*expected[name]);marks=[]
 with ReadOnlyEmu(str(rom),str(sav),sym=str(sym)) as e:
  def on_menu(em):marks.append((em.frame(),em.u32(em.sym('gMain')+36)))
  e.boot_continue(timeout=3600,on_menu=on_menu,leave_menu_only=True);assert len(marks)==1
  start,vblank=marks[0];first=None;stable=0
  while e.frame()-start<600:
   if e.reset_seen():raise GameReset('reset while loading '+name)
   if e.location()==want and e.field_idle() and not e.quest_log_playing():
    if stable==0:first=e.frame()
    stable+=1
    if stable>=12:break
   else:stable=0
   e.run(1)
  else:raise TimeoutError(('map load',name,e.location(),hex(e.callback2())))
  assert e.u8(e.sym('gPlayerPartyCount'))==reference_party[1],'party count changed on cold load'
  assert e.black_fraction()<=0.97,'black map after cold load'
  assert e.read(e.sym('gPlayerParty'),len(reference_party[0]))==reference_party[0],'party changed on cold load'
  assert e.read(e.ptr('gPokemonStoragePtr'),len(reference_pc))==reference_pc,'PC changed on cold load'
  assert runtime_dex(e)==reference_dex,'dex changed on cold load'
  load=dict(map=name,load_frames=first-start,stable_idle_frames=stable,vblank_delta=(e.u32(e.sym('gMain')+36)-vblank)&0xffffffff,source_save_sha256=original,fixture_sha256=fixture_sha)
  print(json.dumps({'map_load':load}),flush=True);e.shot(str(out/(name+'-cold.png')))
  flags_before=runtime_regional_flags(e)
  for _ in range(3):one_step(e,'RIGHT')
  assert e.location()[2:]==(8,9)
  e.shot(str(out/(name+'-two-companions.png')))
  budget._diag_out=out
  budget.field_budget(name,e,elf,rom,e.syms)
  assert e.read(e.sym('gPlayerParty'),len(reference_party[0]))==reference_party[0] and e.read(e.ptr('gPokemonStoragePtr'),len(reference_pc))==reference_pc and runtime_dex(e)==reference_dex,'original read-only workload changed Pokemon/dex'
  assert runtime_regional_flags(e)==flags_before,'read-only core movement changed regional story/trainer flags'
  results.append(load)
 assert sha(sav)==fixture_sha,'source fixture changed'
assert budget._field_done==set(expected),'missing native field measurements'
assert sha(source)==original,'joined native SAV changed'
for p,h in protected.items():assert sha(p)==h,('original input changed',p)
result=dict(pass_all=True,maps=results,joined_native_source_rom_sha256=proof['rom_sha256'],user_original_save_sha256=sha(user_original),join_proof_sha256=sha(join_proof),active_misty_render_workload=True,companion_coordinates_never_poked=True,rom_sha256=sha(rom),elf_sha256=sha(elf),sym_sha256=sha(sym),source_save_sha256=original,ram_pokes_original=0,party_pc_dex_preserved=True,regional_story_trainer_flags_preserved=True,actual_device_fps_measured=False,workload_frames_per_case=360,workload_count=(1 if __import__('os').environ.get('MISTY_PERF_WORKLOAD')=='walking' else 2),full_campaign_measured=False,temporary_native_fixtures=True)
(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
