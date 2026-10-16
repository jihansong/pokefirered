from pathlib import Path
import sys,hashlib,struct,json,traceback,collections
root=Path('/workspaces/pokefirered');out=root/'work/continuation-20261013/pc-ui';out.mkdir(exist_ok=True)
rom=root/'pokemonthyl.gba';elf=root/'pokemonthyl.elf';sav=root/'work/continuation-20261013/capture-pc-current/capture-PC-native-QA-only.sav'
sys.argv=['pc-ui','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
q=(root/'tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<verified-readonly-definitions>','exec'))
status={'pass':False,'ram_writes':0,'direct_script_calls':0,'scope':'captured Flash copied before boot to a center PC; native PC deposit/withdraw then SAVE/cold','stages':[]}
e=None
def emit(): (out/'validation.json').write_text(json.dumps(status,indent=2))
def task(name):
 for i in range(16):
  p=syms['gTasks']+40*i
  if e.u8(p+4) and (e.u32(p)&~1)==(syms[name]&~1):return p
def wait(fn,tag,limit=1600):
 for _ in range(limit):
  assert not e.reset_seen()
  if fn():e.run(20);return
  e.run(1)
 raise AssertionError(('wait failed',tag,e.location(),tasks()))
def tasks():
 return [(i,hex(e.u32(syms['gTasks']+40*i)),list(struct.unpack('<16h',e.read(syms['gTasks']+40*i+8,32)))) for i in range(16) if e.u8(syms['gTasks']+40*i+4)]
def mainmenu(): return task('Task_PCMainMenu') and e.u16(task('Task_PCMainMenu')+8)==2
def storageidle():
 p=e.ptr('gStorage')
 return p and task('Task_PokeStorageMain') and e.u8(p)==0 and not e.u8(syms['sIsMonBeingMoved'])
def records():
 party=e.read(syms['gPlayerParty'],600);p=[]
 for i in range(6):
  raw=party[100*i:100*i+80]
  if Mon(bytearray(raw),0).has_species():p.append(raw)
 boxes=e.read(e.ptr('gPokemonStoragePtr')+off('storage.boxes'),33600)
 b={i:boxes[i*80:(i+1)*80] for i in range(420) if any(boxes[i*80:i*80+8])}
 return p,b
def evidence(raw):
 m=Mon(bytearray(raw),0);s=m.subs()
 return {'pid':m.personality,'ot':m.otid,'species':m.species(),'G':bytes(s['G']).hex(),'A_moves':bytes(s['A'][:8]).hex(),'PP':list(s['A'][8:12]),'E':bytes(s['E']).hex(),'M':bytes(s['M']).hex(),'header':raw[:28].hex()+raw[30:32].hex(),'checksum_ok':sum(x[0] for z in s.values() for x in struct.iter_unpack('<H',z))&65535==struct.unpack_from('<H',raw,28)[0],'bad_egg':bool(raw[19]&1),'raw_sha256':digest(raw)}
def unchanged_core(raw,old):
 a,b=evidence(raw),evidence(old)
 assert all(a[k]==b[k] for k in ['pid','ot','species','G','A_moves','E','M','header'])
 assert a['checksum_ok'] and not a['bad_egg']
def verify(tag,count):
 p,b=records();assert len(p)==count,(tag,len(p),count)
 for slot,old in origboxes.items():
  assert b.get(slot)==old,('original PC changed',tag,slot)
 allmons=p+list(b.values())
 assert len(allmons)==len(baseparty)+len(baseboxes),(tag,'lost or duplicated mon')
 for old in baseparty:
  pid=struct.unpack_from('<II',old)
  matching=[v for v in allmons if struct.unpack_from('<II',v)==pid]
  oldcopies=sum(struct.unpack_from('<II',v)==pid for v in baseparty+list(baseboxes.values()))
  assert len(matching)==oldcopies
  if old==selected:
   assert len(matching)==1;unchanged_core(matching[0],old)
  else:
   assert collections.Counter(matching)==collections.Counter(v for v in baseparty+list(baseboxes.values()) if struct.unpack_from('<II',v)==pid)
 new=[v for v in allmons if struct.unpack_from('<II',v)==newpid];assert len(new)==1 and new[0]==newraw
 assert [blocks(e).dex_state(i) for i in range(1,387)]==basedex
 status['stages'].append({'stage':tag,'party_count':len(p),'PC_count':len(b),'original_PC_records_unchanged':len(origboxes),'new_mon':evidence(new[0]),'selected_original':evidence(next(v for v in allmons if struct.unpack_from('<II',v)==struct.unpack_from('<II',selected)))})
 emit();e.shot(str(out/(tag+'.png')),scale=3)
def chooseoption(option):
 assert mainmenu()
 # Real menu cursor is observed through task data, never written.
 p=task('Task_PCMainMenu')
 old=e.u16(p+10);status['menu_selected_before']=old;emit()
 for _ in range(6):
  if e.u16(task('Task_PCMainMenu')+10)==option:break
  e.press('DOWN',hold=2,after=20)
 else:raise AssertionError(('main option cursor unknown',option,tasks()))
 e.press('A',hold=2,after=30);wait(storageidle,'storage opened')
 assert e.u8(e.ptr('gStorage')+1)==option
def closebox():
 wait(storageidle,'before close');e.press('B',hold=2,after=30)
 wait(lambda:task('Task_OnBPressed') and e.u8(e.ptr('gStorage'))==2,'continue box prompt')
 e.press('B',hold=2,after=30);wait(mainmenu,'PC main menu return')
def partycursor(index):
 assert e.u8(syms['sCursorArea'])==1
 for _ in range(8):
  if e.u8(syms['sCursorPosition'])==index:return
  e.press('DOWN',hold=2,after=30);wait(storageidle,'party cursor moved')
 raise AssertionError('party cursor cannot reach')
def boxcursor(slot):
 assert e.u8(syms['sCursorArea'])==0
 cur=e.u8(syms['sCursorPosition'])
 while cur//6!=slot//6:
  e.press('DOWN' if cur//6<slot//6 else 'UP',hold=2,after=30);wait(storageidle,'box row')
  cur=e.u8(syms['sCursorPosition'])
 while cur%6!=slot%6:
  e.press('RIGHT' if cur%6<slot%6 else 'LEFT',hold=2,after=30);wait(storageidle,'box col')
  cur=e.u8(syms['sCursorPosition'])
 assert cur==slot
def selection():
 e.press('A',hold=2,after=30);wait(lambda:task('Task_OnSelectedMon') and e.u8(e.ptr('gStorage'))==2,'mon selected')
 e.press('A',hold=2,after=30)
def deposit(index,tag):
 partycursor(index);selection()
 wait(lambda:task('Task_DepositMenu') and e.u8(e.ptr('gStorage'))==1,'deposit box prompt')
 start=e.u8(syms['sDepositBoxId'])
 for _ in range((4-start)%14):e.press('RIGHT',hold=2,after=24)
 e.press('A',hold=2,after=30);wait(storageidle,'deposit committed');verify(tag,5)
def withdraw(slot,tag):
 boxcursor(slot);selection();wait(storageidle,'withdraw committed');verify(tag,6)
try:
 assert digest(rom.read_bytes())=='f31b2eea1ae45fd1dd40057c80510a8875936394e5807d00806a90cff1dee73d'
 # Locate the actual PC tile from this ROM tileset attributes.
 layout=next(x for x in json.loads((root/'data/layouts/layouts.json').read_text())['layouts'] if x['id']=='LAYOUT_POKEMON_CENTER_1F')
 tiles=struct.unpack('<150H',(root/layout['blockdata_filepath']).read_bytes())
 pcs=[]
 for i,v in enumerate(tiles):
  mid=v&1023;ts=layout['primary_tileset'] if mid<640 else layout['secondary_tileset'];idx=mid if mid<640 else mid-640
  attrs=struct.unpack('<I',r.at(syms[ts]+20,4))[0];bh=struct.unpack('<I',r.at(attrs+4*idx,4))[0]&255
  if bh==0x83:pcs.append((i%15,i//15))
 assert len(pcs)==1,pcs
 x,y=pcs[0];status['pc_tile']=pcs[0]
 f=SaveFile(str(sav));originalparty=bytes(f.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]);originalboxes=bytes(f.blocks['storage'])
 f.warp('VioletCity_PokemonCenter_1F',x,y+1);fp=out/'center-position-QA-only.sav';assert not fp.exists();f.save(str(fp))
 assert bytes(f.blocks['storage'])==originalboxes
 e=ReadOnlyEmu(str(rom),str(fp),sym='');e.syms=syms;e.boot_continue();settle(e)
 baseparty,baseboxes=records();assert len(baseparty)==6 and len(baseboxes)==121
 selected=baseparty[5];assert Mon(bytearray(selected),0).species()!=const('SPECIES_PIKACHU')
 newraw=baseboxes[120];newpid=struct.unpack_from('<II',newraw);origboxes={k:v for k,v in baseboxes.items() if k!=120};basedex=[blocks(e).dex_state(i) for i in range(1,387)]
 verify('center-before-PC',6);e.press('UP',hold=1,after=20);assert e.location()[2:]==(x,y+1)
 e.press('A',hold=2,after=20)
 for _ in range(500):
  if mainmenu():break
  e.press('A',hold=1,after=12)
 else:raise AssertionError(('real PC did not open',tasks()))
 verify('opened-storage-menu',6)
 chooseoption(1);deposit(5,'original-sixth-deposited');_,b=records();storedslot=next(k for k,v in b.items() if struct.unpack_from('<II',v)==struct.unpack_from('<II',selected))
 assert storedslot//30==4
 closebox();chooseoption(0);assert e.u8(e.ptr('gPokemonStoragePtr'))==4
 withdraw(0,'captured-mon-withdrawn');closebox();chooseoption(1);deposit(5,'captured-mon-redeposited');closebox();chooseoption(0)
 withdraw(storedslot%30,'original-team-restored');closebox()
 # B exits storage main menu then B cancels the access-PC menu.
 for _ in range(500):
  if e.field_idle():break
  e.press('B',hold=1,after=12)
 else:raise AssertionError('PC did not close')
 verify('PC-closed',6);status['native_SAVE_cold']=flash_reload(e,'PC-roundtrip');verify('native-SAVE-cold',6)
 status['pass']=True
except Exception as ex:
 status.update(error=repr(ex),traceback=traceback.format_exc())
 if e and e.h:
  status['failure_tasks']=tasks();status['failure_location']=e.location()
  if e.ptr('gStorage'):status['PSS_state']=e.u8(e.ptr('gStorage'));status['cursor']=[e.u8(syms['sCursorArea']),e.u8(syms['sCursorPosition'])]
  e.shot(str(out/'failure.png'),scale=3)
finally:
 if e:e.close()
 status['inputs_unchanged']=all(digest(p.read_bytes())==h for p,h in originals.items());emit();print(json.dumps(status),flush=True)
