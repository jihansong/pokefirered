from pathlib import Path
import hashlib,json,time,traceback
q=Path('tools/qa/native_misty_basic_qa.py').read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<verified-native-definitions>','exec'))
d={'pass':False,'rom_sha256':digest(rom.read_bytes()),'fixture_sha256':digest(sav.read_bytes()),'requested_render_frames':600,'requested_warmup_frames':60,'scope':'Host mGBA software renderer; no DELTA device claim'}
try:
 with ReadOnlyEmu(str(rom),str(sav),sym='') as e:
  e.syms=syms;t=time.perf_counter();bf=e.boot_continue();settle(e);d['continue_seconds']=time.perf_counter()-t;d['continue_frame_requests']=bf
  initial=e.location();e.run(60);before=record(e);startframe=e.frame();t=time.perf_counter();e.run(600);seconds=time.perf_counter()-t
  assert e.field_idle() and not e.reset_seen() and e.location()==initial
  same_records(e,before);assert e.ptr('gPokemonStoragePtr')!=0
  d['pass']=True;d.update(location=initial,render_seconds=seconds,wrapper_frame_count_delta=e.frame()-startframe,party_full_PC_Dex_unchanged=True)
except Exception as ex:d.update(error=repr(ex),traceback=traceback.format_exc())
finally:
 d['inputs_unchanged']=all(digest(p.read_bytes())==v for p,v in originals.items());(out/'result.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d),flush=True)
