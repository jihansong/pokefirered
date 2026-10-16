from pathlib import Path
import sys,hashlib,struct,json,ast,traceback
root=Path('/workspaces/pokefirered');work=root/'work/regional-starters-20261013';out=work/'native-v3';out.mkdir()
rom=work/'candidate/pokemonthyl.gba';elf=work/'candidate/pokemonthyl.elf';sav=root/'saves/pokemonthyl_v1.25-items99-iv2x.sav'
sys.argv=['starters','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
q=(root/'tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<verified-readonly-definitions>','exec'))
node=next(n for n in ast.parse(Path('tools/qa/eventcheck.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='throw_ball')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<native-ball-key-controller>','exec'))
wait_action_menu=lambda e,rom:menu(e)
live_blocks=blocks;item_name=gd.item_name
gd.FIELDS['pokemon.level']=('Pokemon','level');gd._OFFSETS=None
names=['CYNDAQUIL','CHIKORITA','TOTODILE','TORCHIC','TREECKO','MUDKIP']
flags={n:('FLAG_GOT_'+n+'_FROM_AIDE' if n in names[:3] else {'TORCHIC':'FLAG_HOENN_GOT_TORCHIC_FROM_BIRCH','TREECKO':'FLAG_HOENN_GOT_TREECKO_IN_WOODS','MUDKIP':'FLAG_HOENN_GOT_MUDKIP_ON_BEACH'}[n]) for n in names}
report={'pass':False,'rom_sha256':digest(rom.read_bytes()),'RAM_writes':0,'direct_script_calls':0,'forced_battle_outcomes':0,'source_sav':str(sav),'cases':[]}
protected={p:digest(p.read_bytes()) for p in list((root/'saves').rglob('*.sav'))+[root/'pokemonthyl.gba',root/'pokemonthyl.elf']}
e=None
def emit(): (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
def entries(e):
 p=e.read(syms['gPlayerParty'],600);n=e.u8(syms['gPlayerPartyCount']);b=e.read(e.ptr('gPokemonStoragePtr')+off('storage.boxes'),33600)
 return ([p[i*100:i*100+80] for i in range(n)],{i:b[i*80:(i+1)*80] for i in range(420) if any(b[i*80:i*80+8])})
def total(e):
 p,b=entries(e);return len(p)+len(b)
def profile(raw):
 m=Mon(bytearray(raw),0);s=m.subs();iv=struct.unpack_from('<I',s['M'],4)[0]
 return {'species':m.species(),'pid':m.personality,'ot':m.otid,'IVs':[(iv>>(5*i))&31 for i in range(6)],'exp':struct.unpack_from('<I',s['G'],4)[0],'met_level':s['M'][2]&127,'item':struct.unpack_from('<H',s['G'],2)[0],'checksum_ok':sum(v[0] for z in s.values() for v in struct.iter_unpack('<H',z))&65535==struct.unpack_from('<H',raw,28)[0],'egg':bool(iv>>30&1),'bad_egg':bool(raw[19]&1),'raw80':raw.hex()}
def verify(old,name,delta):
 pp,bb=entries(e);op,ob=old
 assert pp[:len(op)]==op,('original party core changed',name)
 for i,raw in ob.items():assert bb.get(i)==raw,('original PC record changed',name,i)
 added=pp[len(op):]+[v for i,v in bb.items() if i not in ob]
 assert len(added)==delta and len(pp)+len(bb)==len(op)+len(ob)+delta,(name,'count',len(added),delta)
 if delta:
  v=profile(added[0]);assert v['species']==const('SPECIES_'+name) and v['IVs']==[31]*6
  assert v['checksum_ok'] and not v['egg'] and not v['bad_egg'] and v['item']==0 and v['met_level']==5
  assert v['ot']==struct.unpack_from('<I',blocks(e).sb2,off('sb2.playerTrainerId'))[0]
  return v
def fixture(name,capacity,tag,scene=1):
 s=SaveFile(str(sav));s.set_flag('FLAG_SYS_GAME_CLEAR',True);s.set_flag('FLAG_JOHTO_ARRIVAL_BRIEFED',True)
 s.set_flag('FLAG_JOHTO_MR_POKEMON_BRIEFED',False);s.set_flag('FLAG_JOHTO_ELM_REPORT_DELIVERED',False)
 for n in names:s.set_flag(flags[n],n in names[:3] and n!=name)
 if capacity=='party':s.keep_party(5)
 if capacity=='full':
  b=s.blocks['storage'];raw=bytes(b[off('storage.boxes'):off('storage.boxes')+80]);assert profile(raw)['checksum_ok']
  for i in range(420):
   o=off('storage.boxes')+80*i
   if not any(b[o:o+8]):b[o:o+80]=raw
 if name in names[:3]:s.warp('NewBarkTown_ElmsLab',5,6)
 elif name=='TORCHIC':
  s.set_flag('FLAG_HOENN_BIRCH_RESCUED',True);s.set_var('VAR_HOENN_SCENE_BIRCH',scene);s.warp('LittlerootTown_ProfessorBirchsLab',6,5)
 elif name=='TREECKO':
  s.set_trainer_beaten('TRAINER_HOENN_GRUNT_PETALBURG_WOODS',True);s.set_var('VAR_HOENN_SCENE_DEVON',1);s.warp('PetalburgWoods',40,24)
 else:s.warp('Route104',14,57)
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 s.set_var('VAR_REPEL_STEP_COUNT',250);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0)
 f=out/(tag+'-before-QA-only.sav');s.save(str(f));return f
def boot(f):
 global e
 e=ReadOnlyEmu(str(rom),str(f),sym='');e.syms=syms;e.boot_continue();settle(e);e.run(50);assert e.field_idle()
def interact(name,expected=1,capture=False,decline=False):
 before=total(e)
 e.press('UP',hold=1,after=20);e.press('A',hold=2,after=8)
 assert not e.field_idle(),('interaction did not start',name,e.location())
 battle=False
 for _ in range(1800):
  safe(e)
  if e.field_idle():return
  if e.in_battle():
   assert name=='TREECKO' and not battle
   assert menu(e);battle=True
   enemy=profile(e.read(syms['gEnemyParty'],80));assert enemy['IVs']==[31]*6 and enemy['species']==const('SPECIES_TREECKO')
   if capture:assert throw_ball(e,str(rom),'ITEM_MASTER_BALL',None) is None
   else:
    for key in ['UP','LEFT','RIGHT','DOWN','A']:e.press(key,hold=2,after=12)
   for __ in range(800):
    if not e.in_battle():break
    e.press('B',hold=2,after=14)
   else:raise AssertionError('Treecko battle did not end')
   report.setdefault('battle_paths',[]).append({'capture':capture,'outcome':e.u8(syms['gBattleOutcome']),'enemy':enemy})
   continue
  e.press('B' if decline or total(e)>before or name not in names[:3] else 'A',hold=2,after=14)
 raise AssertionError(('gift dialog timeout',name,e.location()))
def one(name,capacity,capture=False,scene=1):
 global e
 tag=name.lower()+'-'+capacity+('-capture' if capture else '')+('-late' if scene>1 else '')
 boot(fixture(name,capacity,tag,scene));old=entries(e);prior={n:blocks(e).flag(flags[n]) for n in names};dex0=[blocks(e).dex_state(i) for i in range(1,387)]
 interact(name,0 if capacity=='full' else 1,capture)
 delta=0 if capacity=='full' else 1
 v=verify(old,name,delta)
 assert blocks(e).flag(flags[name])==bool(delta),(tag,'receipt')
 for n in names:
  if n!=name:assert blocks(e).flag(flags[n])==prior[n],(tag,'other receipt changed',n)
 if capacity=='party':assert len(entries(e)[0])==6 and entries(e)[1]==old[1]
 elif capacity=='pc':assert entries(e)[0]==old[0] and len(entries(e)[1])==len(old[1])+1
 if name=='TORCHIC':assert blocks(e).var('VAR_HOENN_SCENE_BIRCH')==(max(scene,2) if delta else scene)
 if not delta:
  dex1=[blocks(e).dex_state(i) for i in range(1,387)]
  if name!='TREECKO':assert dex1==dex0
  else:assert all((x==y or i==251 and x[0]==y[0]) for i,(x,y) in enumerate(zip(dex0,dex1))),('Treecko caught changed after no room')
 row={'case':tag,'capacity':capacity,'party_count':len(entries(e)[0]),'PC_count':len(entries(e)[1]),'receipt':bool(delta),'gift':v,'original_records_preserved':True,'pass':True}
 e.shot(str(out/(tag+'.png')),scale=3)
 if delta:
  got=entries(e);interact(name,expected=0);assert entries(e)==got,(tag,'duplicate received')
  row['repeat_no_duplicate']=True
  live=entries(e);row['SAVE_cold']=flash_reload(e,tag);assert entries(e)==live and blocks(e).flag(flags[name])
  verify(old,name,1)
 report['cases'].append(row);emit();e.close();e=None
try:
 assert report['rom_sha256']=='63904802b37dc5e922ec616361c0be3388f1030e5b2c1a0b7a2949f2a33c1f7c'
 one('TREECKO','full')
 for capacity in ['party','pc','full']:one('MUDKIP',capacity)
 one('TORCHIC','pc',scene=3)
 one('TREECKO','pc',capture=True)
 report['pass']=True
except Exception as ex:
 report.update(error=repr(ex),traceback=traceback.format_exc())
 if e and e.h:e.shot(str(out/'failure.png'),scale=3)
finally:
 if e:e.close()
 report['protected_original_inputs_unchanged']=all(digest(p.read_bytes())==v for p,v in protected.items())
 emit();print(json.dumps({k:v for k,v in report.items() if k not in ['cases','battle_paths']}),flush=True)

