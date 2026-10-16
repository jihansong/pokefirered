"""Compare follower lookup on baseline/patched ROMs using disposable emulator data."""
import argparse, hashlib, json, os, struct, subprocess, tempfile
from pathlib import Path
from emu import Emu
ORDERS=('GAEM','GAME','GEAM','GEMA','GMAE','GMEA','AGEM','AGME','AEGM','AEMG','AMGE','AMEG','EGAM','EGMA','EAGM','EAMG','EMGA','EMAG','MGAE','MGEA','MAGE','MAEG','MEGA','MEAG')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def idle(e):
 for _ in range(600):
  if e.field_idle(): return
  e.run(1)
 raise AssertionError('Overworld did not become idle')
def native(e,name):
 assert name in ('GetStarterPikachuPartySlot','IsStarterPikachuAliveInParty')
 idle(e); base=e.sym('gDecompressionBuffer'); ctx=e.sym('sGlobalScriptContext'); result=ctx+112
 assert 0x02000000<=base<0x0203FF00 and 0x03000000<=ctx<0x03007F80
 cache=getattr(e,'_follower_thunks',{})
 if name not in cache:
  asm='\n'.join(['.syntax unified','.thumb','.text','.align 2','.global entry','.thumb_func','entry:','push {r4, lr}','ldr r3, =%d'%(e.sym(name)|1),'bl invoke','ldr r3, =%d'%result,'str r0, [r3]','pop {r4, pc}','.thumb_func','invoke:','bx r3','.ltorg',''])
  dka=Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))/'bin'
  with tempfile.TemporaryDirectory(prefix='qa-follower-thunk-') as tmp:
   p=Path(tmp); (p/'call.s').write_text(asm)
   for cmd in [[str(dka/'arm-none-eabi-as'),'-mthumb','-march=armv4t','-o',str(p/'call.o'),str(p/'call.s')],[str(dka/'arm-none-eabi-ld'),'-Ttext',hex(base),'-e','entry','-o',str(p/'call.elf'),str(p/'call.o')],[str(dka/'arm-none-eabi-objcopy'),'-O','binary',str(p/'call.elf'),str(p/'call.bin')]]: subprocess.run(cmd,check=True,capture_output=True)
   cache[name]=(p/'call.bin').read_bytes()
  e._follower_thunks=cache
 code=cache[name]; assert len(code)<0x100
 e.write(base,code); e.write(ctx+100,(b'\x23'+struct.pack('<I',base|1)+b'\x6b\x02').ljust(16,b'\0'))
 e.write(result,b'\xfe'*4); e.write(ctx,struct.pack('<BBBxII',0,1,0,0,ctx+100))
 e.write(ctx+92,struct.pack('<II',e.sym('gScriptCmdTable'),e.sym('gScriptCmdTableEnd')))
 e.write(e.sym('sGlobalScriptContextStatus'),b'\0')
 for _ in range(60):
  e.run(1)
  if e.u32(result)!=0xFEFEFEFE and e.field_idle(): return e.u32(result)
 raise AssertionError('Native harness did not return: '+name)
def decrypted(record):
 pid,ot=struct.unpack_from('<II',record)
 data=b''.join(struct.pack('<I',v^pid^ot) for (v,) in struct.iter_unpack('<I',record[32:80]))
 assert sum(struct.unpack('<24H',data))&65535==struct.unpack_from('<H',record,28)[0]
 return pid,ot,data
def species(record):
 pid,_,data=decrypted(record)
 return struct.unpack_from('<H',data,ORDERS[pid%24].index('G')*12)[0]
def variant(record,foreign=False,egg=False):
 r=bytearray(record); pid,ot,data=decrypted(r); data=bytearray(data)
 if egg:
  at=ORDERS[pid%24].index('M')*12+4
  struct.pack_into('<I',data,at,struct.unpack_from('<I',data,at)[0]|(1<<30)); r[19]|=4
 if foreign: ot^=0x01010101
 struct.pack_into('<I',r,4,ot); struct.pack_into('<H',r,28,sum(struct.unpack('<24H',data))&65535)
 r[32:80]=b''.join(struct.pack('<I',v^pid^ot) for (v,) in struct.iter_unpack('<I',data))
 return bytes(r)
def fixtures(original,slot):
 if slot==6: return [],'No own starter; actual-party comparison only'
 own=original[slot*100:(slot+1)*100]
 if struct.unpack_from('<H',own,86)[0]==0: return [],'Starter fainted; actual-party comparison only'
 normal=None
 for i in range(6):
  r=original[i*100:(i+1)*100]
  if i!=slot and not r[19]&16 and species(r) not in (0,25): normal=r; break
 if normal is None: return [],'No suitable unmarked non-Pikachu fixture'
 wild=bytearray(own); wild[19]&=~16
 faint=bytearray(own); struct.pack_into('<H',faint,86,0)
 marked=bytearray(normal); marked[19]|=16
 damaged=bytearray(normal); damaged[32]^=4
 tests=[]
 for pos in range(6):
  rows=[normal]*6; rows[pos]=own; tests.append(('own_slot_'+str(pos),b''.join(rows),pos,True))
 tests += [('absent',normal*6,6,False),('wild_pikachu',bytes(wild)+normal*5,6,False),('foreign_starter',variant(own,foreign=True)+normal*5,6,False),('egg',variant(own,egg=True)+normal*5,6,False),('marked_other_species',bytes(marked)+normal*5,6,False),('first_starter_fainted',bytes(faint)+own+normal*4,0,False),('damaged_unmarked_read_only',bytes(damaged)*6,6,False),('immediate_return',normal+own+normal*4,1,True)]
 return tests,None
def run_rom(rom,sym,save,label,tests=None):
 rows=[]
 with Emu(str(rom),str(save),sym=sym) as e:
  e.boot_continue(); idle(e); addr=e.sym('gPlayerParty'); original=e.read(addr,600); pc=e.read(e.ptr('gPokemonStoragePtr'),33744)
  actual=(native(e,'GetStarterPikachuPartySlot'),bool(native(e,'IsStarterPikachuAliveInParty')))
  assert e.read(addr,600)==original,(label,'actual party changed')
  skip=None
  if tests is None: tests,skip=fixtures(original,actual[0])
  for name,fixture,want_slot,want_alive in tests:
   e.write(addr,fixture); got=(native(e,'GetStarterPikachuPartySlot'),bool(native(e,'IsStarterPikachuAliveInParty')))
   assert got==(want_slot,want_alive),(label,name,got)
   unchanged=e.read(addr,600)==fixture
   if name=='damaged_unmarked_read_only' and label=='baseline': assert not unchanged,'Baseline expected getter write absent'
   else: assert unchanged,(label,name,'party bytes changed')
   assert e.read(e.ptr('gPokemonStoragePtr'),33744)==pc,(label,name,'PC bytes changed')
   rows.append({'case':name,'slot':got[0],'alive':got[1],'party_unchanged':unchanged})
  e.write(addr,original)
  assert (native(e,'GetStarterPikachuPartySlot'),bool(native(e,'IsStarterPikachuAliveInParty')))==actual
  assert e.read(addr,600)==original and e.read(e.ptr('gPokemonStoragePtr'),33744)==pc
 return {'actual':actual,'cases':rows,'fixture_limit':skip},tests
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--baseline',required=True); ap.add_argument('--patched',required=True); ap.add_argument('--baseline-sym'); ap.add_argument('--patched-sym'); ap.add_argument('--saves',nargs='+',required=True); ap.add_argument('--out')
 a=ap.parse_args(); saves=[Path(p).resolve() for p in a.saves]; hashes={str(p):sha(p) for p in saves}; reports=[]
 try:
  for p in saves:
   before,tests=run_rom(a.baseline,a.baseline_sym,p,'baseline'); after,_=run_rom(a.patched,a.patched_sym,p,'patched',tests)
   assert before['actual']==after['actual'],(str(p),'actual-party result changed')
   assert [(v['case'],v['slot'],v['alive']) for v in before['cases']]==[(v['case'],v['slot'],v['alive']) for v in after['cases']]
   reports.append({'save':str(p),'baseline':before,'patched':after}); print('SAVE_PASS',p.name,len(before['cases']),flush=True)
 finally: assert all(sha(p)==hashes[str(p)] for p in saves),'Original source save changed'
 report={'source_saves_unchanged':True,'source_sha256':hashes,'baseline_rom_sha256':sha(a.baseline),'patched_rom_sha256':sha(a.patched),'results':reports,'timing_measured':False,'delta_measured':False,'flagged_corrupt_mon_getter_behavior_changed':False}
 output=json.dumps(report,indent=2)
 if a.out:
  dest=Path(a.out).resolve(); assert dest not in saves and not dest.exists(),'Use a new report path'; dest.write_text(output+chr(10))
 print(output)
if __name__=='__main__': main()
