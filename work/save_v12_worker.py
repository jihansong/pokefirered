from pathlib import Path
import datetime,hashlib,importlib.util,json,subprocess,sys,traceback
sys.dont_write_bytecode=True
R=Path.cwd();rom=R/'pokemonthyl.gba';sym=R/'pokemonthyl.sym';v=R/'saves/pokemonthyl_v1.2.sav'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
romsha='1375cdba01ad0c893cb04f71522871b2d964ae695319ecd2763d5e7247214625';symsha='f7be9a16817c374d5ef975a1653172d71262a119308880eb98846471c10e3e72';vsha='73733902ec36e7ec13fc74d734c773b66077620d63febe1399cae9f759ef6a85'
assert sha(rom)==romsha and sha(sym)==symsha and sha(v)==vsha
out=R/'work'/('save-v12-native-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));out.mkdir();(R/'work/save-v12-native-latest.txt').write_text(str(out))
pins={p:sha(p) for p in (R/'saves').rglob('*.sav')};pins.update({rom:romsha,sym:symsha})
def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o);return o
A=module(R/'work/save-integrity-audit/readonly_audit.py','v12readonly')
args=[(str(p),h) for p,h in pins.items() if p.suffix=='.sav'];ar=A.audit(args,None);(out/'readonly-audit.json').write_text(json.dumps(ar,indent=2))
prior=json.loads((Path((R/'work/region-save-validation-latest.txt').read_text().strip())/'result.json').read_text())
argv=[sys.executable,'-B','work/save-integrity-audit/native_continue_check.py','--rom',str(rom),romsha,'--sym',str(sym),symsha,'--audit','work/save-integrity-audit/readonly_audit.py']
for p,h in prior['save_sha256'].items():argv+=['--save',p,h]
with (out/'healthy-seven-diagnostics.json').open('w') as f: rc=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT).returncode
print('HEALTHY_SEVEN_DIAGNOSTICS',rc,flush=True)
r={'rom_sha256':romsha,'v12_sha256':vsha,'native_load_completed':False,'save_integrity_healthy':False,'code_injection':False,'memory_writes':False,'save_requested':False}
try:
 raw=v.read_bytes();slots=[A.slot_audit(raw,i,None)[0] for i in [0,1]];selected=A.select_slot(slots);chosen=selected['strict_slot'];assert chosen==selected['engine_model_slot'] and chosen is not None
 where={s['id']:s['physical'] for s in slots[chosen]['sectors']};chunks=[raw[where[k]*4096:where[k]*4096+A.SIZES[k]] for k in range(14)];storage=b''.join(chunks[5:]);sb1=b''.join(chunks[1:5]);party=[sb1[56+i*100:136+i*100] for i in range(sb1[52])]
 def anomalies(data):return [{'index':i,'box':i//30+1,'slot':i%30+1,'mon':A.inspect_mon(data[4+i*80:84+i*80])[0]} for i in range(420) if A.inspect_mon(data[4+i*80:84+i*80])[0]['errors']]
 original=anomalies(storage);assert [x['index'] for x in original]==[51];r.update(slot=chosen,counter=slots[chosen]['counter'],original_anomalies=original)
 sys.path.insert(0,str(R/'tools/qa'));from emu import Emu
 with Emu(str(rom),str(v),sym=str(sym)) as e:
  assert Path(e.sav_path).resolve()!=v.resolve() and sha(Path(e.sav_path))==vsha
  r['boot_frames']=e.boot_continue(timeout=6000);phases=[]
  for label,idle in [('after_continue',0),('after_idle_180',180)]:
   if idle:e.run(idle)
   data=e.read(e.ptr('gPokemonStoragePtr'),33744);count=e.u8(e.sym('gPlayerPartyCount'));pr=e.read(e.sym('gPlayerParty'),600);nativeparty=[pr[i*100:i*100+80] for i in range(count)]
   phases.append({'phase':label,'pc_all_bytes_equal':data==storage,'party_all_raw80_equal':nativeparty==party,'anomalies':anomalies(data),'pc_sha256':hashlib.sha256(data).hexdigest(),'frame':e.frame(),'location':e.location()})
  r.update(native_load_completed=True,phases=phases,no_new_pc_corruption=all(x['pc_all_bytes_equal'] for x in phases),party_preserved=all(x['party_all_raw80_equal'] for x in phases))
except Exception as ex:r.update(error=repr(ex),traceback=traceback.format_exc())
r['originals_unchanged']=all(sha(p)==h for p,h in pins.items());(out/'result.json').write_text(json.dumps(r,indent=2));print(json.dumps({'output':str(out),'native_load_completed':r['native_load_completed'],'originals_unchanged':r['originals_unchanged']}),flush=True)
