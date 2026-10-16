from pathlib import Path
import sys,json,hashlib,struct,traceback,time
root=Path('/workspaces/pokefirered');work=root/'work/save-inventory-pp-20261013';out=work/'native-v1';out.mkdir(exist_ok=True)
rom=work/'candidate/pokemonthyl.gba';elf=work/'candidate/pokemonthyl.elf';sav=work/'candidate/pokemonthyl_v1.25-items99-iv2x-pp15.sav'
build=json.loads((work/'build-result-v3.json').read_text());assert build['exit_code']==0 and build['main_ROM_unchanged']
sys.argv=['pp','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
q=(root/'tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<verified-native-definitions>','exec'))
report={'pass':False,'ROM_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'RAM_writes':0,'direct_script_calls':0,'forced_battle_outcomes':0,'native_heal_slots_verified':0,'cases':[],'whole_regional_campaign_complete':False,'actual_DELTA_tested':False}
protected={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in list((root/'saves').rglob('*.sav'))+[root/'pokemonthyl.gba',sav]}
e=None;t0=time.monotonic();rr=gd.Rom(str(rom));stride=json.loads((work/'facts.json').read_text())['offsets']['battlemove']
def emit():
 report['elapsed_seconds']=round(time.monotonic()-t0,2);(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
def current():
 raw=e.read(syms['gPlayerParty'],600);ans=[]
 for i in range(e.u8(syms['gPlayerPartyCount'])):
  m=Mon(bytearray(raw[i*100:(i+1)*100]),0);s=m.subs();assert (sum(z[0] for b in s.values() for z in struct.iter_unpack('<H',b))&65535)==struct.unpack_from('<H',raw,i*100+28)[0]
  ans.append({'raw':raw[i*100:(i+1)*100],'species':m.species(),'moves':struct.unpack_from('<4H',s['A'],0),'pp':list(s['A'][8:12]),'bonus':s['G'][8],'core':s})
 return ans
base=lambda move:rr.at(rr.syms['gBattleMoves']+move*stride+4,1)[0]
def maxpp(row,j):
 move=row['moves'][j]
 if not move:return 0
 b=base(move);ups=(row['bonus']>>(2*j))&3
 if row['species']==const('SPECIES_PIKACHU'):return max(b,15)*(5+ups)//5
 return max(b*(5+ups)//5,15) if ups==3 and b>=5 else b*(5+ups)//5

def boot(path):
 global e
 e=ReadOnlyEmu(str(rom),str(path),sym='');e.syms=syms;e.boot_continue();settle(e);e.run(30);assert e.field_idle()
def fixture(tag,moves=None,ups=0):
 s=SaveFile(str(sav));s.warp('PewterCity_PokemonCenter_1F',7,4)
 for z in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+z*off('questlogscene')]=0
 s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
 if moves is not None:
  original=bytes(s.sb1[off('sb1.playerParty')+300:off('sb1.playerParty')+400])
  for i in range(6):s.sb1[off('sb1.playerParty')+100*i:off('sb1.playerParty')+100*(i+1)]=original
 for i in range(6):
  m=s.party_mon(i);sub=m.subs()
  for j in range(4):
   move=(moves[i*4+j] if i*4+j<len(moves) else 0) if moves is not None else struct.unpack_from('<H',sub['A'],2*j)[0]
   if moves is not None:struct.pack_into('<H',sub['A'],2*j,move)
   sub['A'][8+j]=1 if move else 0
  if moves is not None:sub['G'][8]=sum(ups<<(j*2) for j in range(4))
  m.put_subs(sub)
 path=out/(tag+'-QA-only.sav');s.save(str(path));return path

def nurse(tag):
 before=current();pc=e.read(e.ptr('gPokemonStoragePtr'),off('storage'))
 e.press('UP',hold=1,after=20);e.press('A',hold=2,after=12);assert not e.field_idle(),('nurse not reached',tag,e.location())
 for _ in range(1600):
  safe(e)
  if e.field_idle():break
  e.press('A',hold=2,after=14)
 else:raise AssertionError(('nurse timeout',tag))
 after=current();assert e.read(e.ptr('gPokemonStoragePtr'),off('storage'))==pc
 for old,new in zip(before,after):
  assert old['moves']==new['moves'] and old['bonus']==new['bonus']
  for field in ['G','E','M']:assert old['core'][field]==new['core'][field],('core changed',tag,field)
  for j in range(4):
   expected=maxpp(new,j);assert new['pp'][j]==expected,(tag,new['species'],new['moves'][j],new['pp'][j],expected);report['native_heal_slots_verified']+=1
 return after
try:
 boot(sav);rows=current();assert len(rows)==6
 assert all(row['pp'][j]>=15 for row in rows for j in range(4) if row['moves'][j])
 for item in ['ITEM_MASTER_BALL','ITEM_RARE_CANDY','ITEM_TINY_MUSHROOM','ITEM_PP_UP']:assert blocks(e).item_count(item)==99
 e.shot(str(out/'original-SAV-continue.png'),scale=3);report['cases'].append({'case':'actual edited SAV CONTINUE','pass':True});e.close();e=None;emit()
 boot(fixture('original-party-center'));after=nurse('original-party-center');e.shot(str(out/'center-healed.png'),scale=3);report['cases'].append({'case':'original party center healing','pp':[x['pp'] for x in after],'pass':True})
 row={'case':'in-game SAVE and cold reload','receipt':flash_reload(e,'party-pp-center'),'pass':True};assert [x['pp'] for x in current()]==[x['pp'] for x in after];report['cases'].append(row);e.close();e=None;emit()
 count=const('MOVES_COUNT');assert count==356
 # Execute the actual ROM's healing loop for every valid move, including custom 355.
 ids=list(range(1,count))+[0]
 for ups in range(4):
  for n in range(0,len(ids),24):
   tag='pika-all-moves-up'+str(ups)+'-batch'+str(n//24);boot(fixture(tag,ids[n:n+24],ups));after=nurse(tag)
   report['cases'].append({'case':tag,'moves':[x['moves'] for x in after],'PP':[x['pp'] for x in after],'pass':True});e.close();e=None;emit()
 report['all_valid_Pikachu_moves_and_PP_Up_stages_native_heal_verified']=True;report['pass']=True
except Exception as ex:
 report.update(error=repr(ex),traceback=traceback.format_exc())
 if e and e.h:e.shot(str(out/'failure.png'),scale=3)
finally:
 if e:e.close()
 report['all_protected_inputs_unchanged']=all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in protected.items());emit();print(json.dumps({k:v for k,v in report.items() if k!='cases'}),flush=True)
