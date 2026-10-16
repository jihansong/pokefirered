from pathlib import Path
import sys,json,struct,hashlib,shutil,time,statistics,traceback
root=Path('/workspaces/pokefirered');out=root/'work/followup-20261013/idle-state';out.mkdir(exist_ok=True)
sav=root/'saves/pokemonthyl_v1.25-items99-iv2x.sav';rom=root/'pokemonthyl.gba';elf=root/'pokemonthyl.elf'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected={str(p):sha(p) for p in list((root/'saves').glob('*.sav'))+[rom,elf]}
assert sha(rom)=='f31b2eea1ae45fd1dd40057c80510a8875936394e5807d00806a90cff1dee73d'
assert sha(sav)=='158e50e370b290fccec6e8a09dda79001cab312c5ebe4de31ee245bb846ecef5'
sys.argv=['idle-state','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
prefix=(root/'tools/qa/native_misty_basic_qa.py').read_text()
assert hashlib.sha256(prefix.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(prefix.split('\nresults=[];rows=[]\n')[0],'<readonly-definitions>','exec'))
report={'pass':False,'rom_sha256':sha(rom),'input_sha256':sha(sav),'scope':'same-ROM native idle and raw core state; not DELTA or full campaign','frames_requested':36000,'rows':[],'ram_writes':0}
def snap(e):
 for name,size in [('gSaveBlock1Ptr',off('sb1')),('gSaveBlock2Ptr',off('sb2')),('gPokemonStoragePtr',33744)]:
  p=e.ptr(name);assert 0x02000000<=p and p+size<=0x02040000,(name,hex(p),size)
 assert not e.reset_seen() and e.field_idle() and not e.in_battle()
 b=record(e)
 return {'location':e.location(),'callback':e.callback2(),'party':digest(b['party']),'PC':digest(b['pc']),'dex':digest(json.dumps(b['dex']).encode()),'count':b['count']}
try:
 with ReadOnlyEmu(str(rom),str(sav),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);e.hold();e.run(60);baseline=snap(e);report['baseline']=baseline
  e.shot(str(out/'before.png'));state=e.save_state();flashhash=sha(Path(e.sav_path));report['state_bytes']=len(state)
  start_frame=e.frame();report['frame_start']=start_frame
  for i in range(60):
   start=time.perf_counter();e.run(600);elapsed=time.perf_counter()-start
   now=snap(e);assert now==baseline,('idle payload or location changed',i,now,baseline)
   row={'requested_frames':(i+1)*600,'hardware_frames':e.frame()-start_frame,'elapsed_seconds':elapsed,'preserved':True}
   assert row['hardware_frames']==row['requested_frames']
   report['rows'].append(row);(out/'progress.json').write_text(json.dumps(row))
  report['median_chunk_seconds']=statistics.median(x['elapsed_seconds'] for x in report['rows'])
  report['native_host_fps']=600/report['median_chunk_seconds'];e.shot(str(out/'after.png'))
  assert sha(Path(e.sav_path))==flashhash
 with ReadOnlyEmu(str(rom),str(sav),sym='') as e:
  e.syms=syms;e.boot_continue();settle(e);assert sha(Path(e.sav_path))==flashhash
  e.load_state(state);report['state_restore_checks']=[]
  for n in (0,60,180):
   if n:e.run(n)
   now=snap(e);assert now==baseline,('same-ROM state restore changed records',n,now,baseline)
   report['state_restore_checks'].append({'additional_frames':n,'payload_and_location_preserved':True,'reset':False})
  assert sha(Path(e.sav_path))==flashhash
  e.shot(str(out/'state-restored.png'))
 report['pass']=True
except Exception as ex:
 report['error']=repr(ex);report['traceback']=traceback.format_exc()
finally:
 report['inputs_unchanged']=all(sha(Path(p))==v for p,v in protected.items())
 if not report['inputs_unchanged']:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
sys.exit(0 if report['pass'] else 1)
