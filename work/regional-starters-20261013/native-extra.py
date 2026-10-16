from pathlib import Path
import traceback,json,struct
w=Path('work/regional-starters-20261013')
q=(w/'native-v4.py').read_text().split("\ntry:\n assert report['rom_sha256']")[0].replace("out=work/'native-v4'","out=work/'native-extra'")
exec(compile(q,'<native-extra-reused-readonly-controller>','exec'))
report['scope']='Sequential Johto gifts; decline; full-storage native SAVE then free synthetic slot in preboot QA copy and retry; original Continue idle'
try:
 f=fixture('CYNDAQUIL','pc','johto-sequence');s=SaveFile(str(f))
 for n in names[:3]:s.set_flag(flags[n],False)
 s.save(str(f));boot(f);origin=entries(e);gifts=[]
 for n in names[:3]:
  old=entries(e);interact(n);gifts.append(verify(old,n,1));assert blocks(e).flag(flags[n])
 live=entries(e);interact('CYNDAQUIL',expected=0);assert entries(e)==live
 cold=flash_reload(e,'johto-all-three');assert entries(e)==live and all(blocks(e).flag(flags[n]) for n in names[:3])
 interact('CYNDAQUIL',expected=0);assert entries(e)==live
 report['cases'].append({'case':'Johto-all-three-in-sequence','pass':True,'gifts':gifts,'SAVE_cold':cold,'repeat_no_duplicate':True})
 emit();e.close();e=None
 boot(fixture('CYNDAQUIL','party','decline'));old=entries(e);interact('CYNDAQUIL',decline=True);verify(old,'CYNDAQUIL',0);assert not blocks(e).flag(flags['CYNDAQUIL'])
 interact('CYNDAQUIL');v=verify(old,'CYNDAQUIL',1)
 report['cases'].append({'case':'Johto-decline-then-retry','pass':True,'gift':v});emit();e.close();e=None
 for n in names:
  tag=n.lower()+'-full-retry';boot(fixture(n,'full',tag));old=entries(e);interact(n);verify(old,n,0);assert not blocks(e).flag(flags[n])
  saved=flash_reload(e,tag);assert entries(e)==old and not blocks(e).flag(flags[n])
  s=SaveFile(str(saved['qa_save']));o=off('storage.boxes')+419*80
  assert bytes(s.blocks['storage'][o:o+80])==old[1][419]
  s.blocks['storage'][o:o+80]=bytes(80)
  f=out/(tag+'-synthetic-space-QA-only.sav');s.save(str(f));e.close();e=None;boot(f);old=entries(e);assert len(old[1])==419
  interact(n);v=verify(old,n,1);assert blocks(e).flag(flags[n])
  report['cases'].append({'case':tag,'pass':True,'full_failed_without_receipt':True,'native_SAVE_cold':saved,'preboot_change':'freed one synthetic fixture box record; no real user file modified','gift':v});emit();e.close();e=None
 boot(sav);old=entries(e);loc=e.location();start=e.frame();e.run(3600)
 assert e.frame()==start+3600 and not e.reset_seen() and e.location()==loc and entries(e)==old
 report['cases'].append({'case':'unedited-v125-Continue-and-3600-native-frames','pass':True,'position':loc,'frames':3600,'original_records_preserved':True})
 report['pass']=True
except Exception as ex:
 report.update(error=repr(ex),traceback=traceback.format_exc())
 if e and e.h:e.shot(str(out/'failure.png'),scale=3)
finally:
 if e:e.close()
 report['protected_original_inputs_unchanged']=all(digest(p.read_bytes())==v for p,v in protected.items())
 emit();print(json.dumps({k:v for k,v in report.items() if k not in ['cases','battle_paths']}),flush=True)
