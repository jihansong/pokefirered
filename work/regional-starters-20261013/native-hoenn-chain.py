from pathlib import Path
import traceback,json
w=Path('work/regional-starters-20261013')
q=(w/'native-v4.py').read_text().split("\ntry:\n assert report['rom_sha256']")[0].replace("out=work/'native-v4'","out=work/'native-hoenn-chain'")
exec(compile(q,'<same-SAV-Hoenn-checkpoints>','exec'))
report['scope']='Same native SAVE across three regional gift checkpoints; preboot position/story eligibility only, no live memory writes; not continuous overworld walking'
try:
 boot(fixture('TORCHIC','pc','hoenn-sequence'));origin=entries(e);gifts=[]
 for n in ['TORCHIC','TREECKO','MUDKIP']:
  old=entries(e);interact(n);gifts.append(verify(old,n,1));assert blocks(e).flag(flags[n])
  live=entries(e);cold=flash_reload(e,'chain-'+n.lower());assert entries(e)==live
  received={x:blocks(e).flag(flags[x]) for x in names}
  report['cases'].append({'case':n,'gift':gifts[-1],'SAVE_cold':cold,'receipts':received,'original_records_preserved':True,'pass':True});emit()
  if n=='MUDKIP':break
  s=SaveFile(cold['qa_save'])
  if n=='TORCHIC':
   s.warp('PetalburgWoods',40,24);s.set_trainer_beaten('TRAINER_HOENN_GRUNT_PETALBURG_WOODS',True);s.set_var('VAR_HOENN_SCENE_DEVON',1)
  else:s.warp('Route104',14,57)
  for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  f=out/('after-'+n.lower()+'-position-only-QA.sav');s.save(str(f));e.close();e=None;boot(f);assert entries(e)==live
 assert all(blocks(e).flag(flags[n]) for n in ['TORCHIC','TREECKO','MUDKIP'])
 assert len(entries(e)[1])==len(origin[1])+3
 for i,v in origin[1].items():assert entries(e)[1][i]==v
 assert entries(e)[0]==origin[0]
 report['pass']=True
except Exception as ex:
 report.update(error=repr(ex),traceback=traceback.format_exc())
 if e and e.h:e.shot(str(out/'failure.png'),scale=3)
finally:
 if e:e.close()
 report['protected_original_inputs_unchanged']=all(digest(p.read_bytes())==v for p,v in protected.items())
 emit();print(json.dumps({k:v for k,v in report.items() if k not in ['cases','battle_paths']}),flush=True)
