from pathlib import Path
import sys,json,ctypes,struct,hashlib,traceback,subprocess
cfg=json.loads(Path(sys.argv.pop(1)).read_text())
s=Path('tools/qa/hoenn_gauntlet_save_qa.py').read_text().split('tmp=None; e=None\ntry:',1)[0].replace('len(p)>=6','len(p)>=5')
exec(compile(s,'<verified-native-runtime>','exec'))
res={'operation':cfg['operation'],'rom_sha256':sha(rom.read_bytes()),'original_input_sav_sha256':sha(sav.read_bytes()),'scope':'raw mGBA core state, not DELTA frontend state','arbitrary_RAM_writes':0,'native_state_restoration':cfg['operation']=='restore','samples':[]}
def emit():
 (out/'result.json').write_text(json.dumps(res,indent=2)+'\n')
def profile(raw,start,stride,count):
 rows=[]
 for i in range(count):
  o=start+i*stride;pid,ot=struct.unpack_from('<II',raw,o)
  if not(pid or ot):continue
  m=Mon(bytearray(raw[o:o+80]),0);subs=m.subs()
  calculated=sum(x[0] for v in subs.values() for x in struct.iter_unpack('<H',v))&65535
  rows.append({'slot':i,'pid':pid,'ot':ot,'stored_checksum':struct.unpack_from('<H',raw,o+28)[0],'calculated_checksum':calculated,'valid_checksum':calculated==struct.unpack_from('<H',raw,o+28)[0],'bad_flag':bool(raw[o+19]&1),'species':struct.unpack_from('<H',subs['G'],0)[0],'raw_sha256':sha(raw[o:o+80])})
 return rows
def snap(e,tag):
 row={'label':tag,'frame':e.frame(),'callback':hex(e.callback2())}
 ps={}
 for n,size in [('gSaveBlock1Ptr',15720),('gSaveBlock2Ptr',3876),('gPokemonStoragePtr',33744)]:
  v=e.u32(syms[n]);ps[n]={'variable_address':hex(syms[n]),'pointer':hex(v),'valid_EWRAM_range':0x02000000<=v and v+size<=0x02040000}
 row['pointers']=ps
 if cfg.get('fixed_original_pc_pointer'):
  ptr=int(cfg['fixed_original_pc_pointer'],16);assert 0x02000000<=ptr and ptr+33744<=0x02040000
  rawpc=e.read(ptr,33744)
  changed=[i for i,(x,y) in enumerate(zip(rawpc,source_pc)) if x!=y]
  row['fixed_original_pc_body']={'address':hex(ptr),'sha256':sha(rawpc),'same_as_original_sav_pc':rawpc==source_pc,'changed_bytes':len(changed),'first_changed_offsets':changed[:12]}

 if all(p['valid_EWRAM_range'] for p in ps.values()):
  b=blocks(e);party=e.read(e.ptr('gSaveBlock1Ptr')+off('sb1.playerParty'),600);box=pc(e)
  row.update(location=e.location(),field_idle=e.field_idle(),party_sha256=sha(party),pc_sha256=sha(box),dex_sha256=sha(json.dumps(digest_dex(b),sort_keys=True).encode()),party=profile(party,0,100,6),pc=profile(box,4,80,420))
 if cfg.get('old_elf'):
  old={}
  table=subprocess.check_output([str(dka/'bin/arm-none-eabi-objdump'),'-t',cfg['old_elf']],text=True)
  for line in table.splitlines():
   q=line.split()
   if len(q)>=5 and q[-1] in ps:old[q[-1]]=int(q[0],16)
  row['old_pointer_locations']={n:{'variable_address':hex(a),'value':hex(e.u32(a))} for n,a in old.items()}
 res['samples'].append(row);emit()
 if tag!='restore-zero':photo(e,tag)
 return row
e=None
try:
 res['mgba_package']=subprocess.check_output(['dpkg-query','-W','-f=${Version}','libmgba0.10'],text=True).strip()
 f=out/'temporary-position-only.sav';assert not f.exists();sf=SaveFile(str(sav))
 for i in range(const('QUEST_LOG_SCENE_COUNT')):sf.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 sf.warp('JohtoRoute29',18,12);sf.save(str(f))
 e=ReadOnlyEmu(str(rom),str(f),sym='');e.syms=syms;e.boot_continue();settle(e);e.run(120);snap(e,'cold-before-state')
 n=int(e.lib.qa_state_size(e.h));res['state_size']=n;res['phase']='before-core-state-API';emit()
 if cfg['operation']=='capture':
  buf=ctypes.create_string_buffer(n);rc=int(e.lib.qa_save_state(e.h,buf));assert rc!=0;blob=buf.raw
  (out/'native-core-state.bin').write_bytes(blob);res.update(api_return=rc,state_sha256=sha(blob),header_first32=blob[:32].hex(),phase='captured');snap(e,'capture-after');res['pass']=True
 else:
  blob=Path(cfg['state']).read_bytes();res.update(state_sha256=sha(blob),state_input_bytes=len(blob));assert len(blob)==n
  res['phase']='before-native-restore';emit();rc=int(e.lib.qa_load_state(e.h,blob));res.update(api_return=rc,phase='restore-returned');emit()
  if rc:
   snap(e,'restore-zero')
   for amount,label in [(60,'restore-rendered-60'),(180,'restore-rendered-240')]:e.run(amount);snap(e,label)
  res['pass']=True
except Exception as ex:
 res.update(pass_value=False,error=repr(ex),traceback=traceback.format_exc())
finally:
 if e:e.close()
 res['original_saves_unchanged']=before=={p:sha(Path(p).read_bytes()) for p in before};emit();print(json.dumps({k:v for k,v in res.items() if k!='samples'}),flush=True)
