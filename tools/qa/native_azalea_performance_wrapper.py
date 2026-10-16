import hashlib,json,pathlib,sys
from emu import Emu,GameReset
from savefile import SaveFile
import gamedata,native_land_budget_helper as budget
class ReadOnlyEmu(Emu):
 def write(self,*args):raise AssertionError('field QA must not poke RAM')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def party(s):
 o=gamedata.off('sb1.playerParty');n=6*gamedata.off('pokemon')
 return bytes(s.sb1[o:o+n]),s.party_count()
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
rom,source,manifest,out=map(pathlib.Path,sys.argv[1:5]);elf=rom.with_suffix('.elf');sym=rom.with_suffix('.sym')
assert elf.is_file() and sym.is_file(),'candidate ELF/SYM must accompany ROM'
cases=json.loads(manifest.read_text());expected={'JohtoRoute32':(9,16),'AzaleaTown':(18,17)}
assert isinstance(cases,list) and len(cases)==2 and {c['map'] for c in cases}==set(expected)
out.mkdir(parents=True,exist_ok=False);original=sha(source);reference=SaveFile(str(source));reference_party=party(reference);reference_pc=bytes(reference.blocks['storage']);results=[]
for c in cases:
 name=c['map'];sav=pathlib.Path(c['save']);sav=sav if sav.is_absolute() else manifest.parent/sav
 fixture_sha=sha(sav);s=SaveFile(str(sav));assert party(s)==reference_party and bytes(s.blocks['storage'])==reference_pc,'fixture changed original Pokemon'
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
  load=dict(map=name,load_frames=first-start,stable_idle_frames=stable,vblank_delta=(e.u32(e.sym('gMain')+36)-vblank)&0xffffffff,source_save_sha256=original,fixture_sha256=fixture_sha)
  print(json.dumps({'map_load':load}),flush=True);e.shot(str(out/(name+'-cold.png')))
  one_step(e,'RIGHT');one_step(e,'LEFT');e.shot(str(out/(name+'-follower.png')))
  budget.field_budget(name,e,elf,rom,e.syms);results.append(load)
 assert sha(sav)==fixture_sha,'source fixture changed'
assert budget._field_done==set(expected),'missing native field measurements'
assert sha(source)==original,'original SAV changed'
result=dict(pass_all=True,maps=results,rom_sha256=sha(rom),elf_sha256=sha(elf),sym_sha256=sha(sym),source_save_sha256=original,ram_pokes_original=0,actual_device_fps_measured=False)
(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
