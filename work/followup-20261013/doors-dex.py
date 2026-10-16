from pathlib import Path
import sys,json,struct,hashlib,traceback
root=Path('/workspaces/pokefirered');out=root/'work/followup-20261013/doors-dex';out.mkdir(exist_ok=True)
sav=root/'saves/pokemonthyl_v1.25-items99-iv2x.sav';rom=root/'pokemonthyl.gba';elf=root/'pokemonthyl.elf'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p) for p in [sav,rom,elf]+list((root/'saves').glob('*.sav'))}
assert sha(rom)=='f31b2eea1ae45fd1dd40057c80510a8875936394e5807d00806a90cff1dee73d'
sys.argv=['doors-dex','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
q=(root/'tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<readonly-definitions>','exec'))
report={'pass':False,'rom_sha256':sha(rom),'save_sha256':sha(sav),'ram_writes':0,'scope':'new SAV checkpoint doors and real Pokedex UI; not full travel/story','cases':[]}
unlock=['FLAG_JOHTO_ARRIVAL_BRIEFED','FLAG_JOHTO_MET_LAB_ASSISTANT','FLAG_HOENN_BIRCH_RESCUED','FLAG_HOENN_MET_STERN']
source_save=SaveFile(str(sav));report['source_unlock_flags']={f:source_save.flag(f) for f in unlock};assert not any(report['source_unlock_flags'].values())
e=None
def idle(limit=1200):
 for i in range(limit):
  assert not e.reset_seen() and not e.in_battle()
  if e.field_idle():e.run(20);return
  e.run(1)
 raise AssertionError(('idle timeout',e.location(),e.callback2()))
def hop(key):
 initial=e.location();e.hold(key)
 try:
  for _ in range(120):
   e.run(1)
   if e.location()!=initial:break
  else:raise AssertionError(('blocked step',key,initial))
 finally:e.hold()
 idle();return e.location()
def task(name):
 for i in range(16):
  p=syms['gTasks']+40*i
  if e.u8(p+4) and e.u32(p)&~1==syms[name]&~1:return i
def uiwait(name,state):
 for i in range(900):
  e.run(1);p=e.ptr('sPokedexScreenData')
  if p and task(name) is not None and e.u8(p+1)==state:e.run(24);return e.ptr('sPokedexScreenData')
 raise AssertionError(('UI timeout',name,state))
def close_ui():
 for i in range(1200):
  if e.field_idle():e.run(20);return
  if i%8==0:e.press('B',hold=1,after=1)
  else:e.run(1)
 raise AssertionError('Pokedex could not close')
def dex_ui(region,count,label):
 baseline=record(e);e.press('START',hold=3,after=60);n=e.u8(syms['sNumStartMenuItems']);order=list(e.read(syms['sStartMenuOrder'],n))
 assert 0 in order,('Pokedex missing from real Start menu',order)
 wanted=order.index(0)
 for _ in range(n+1):
  if e.u8(syms['sStartMenuCursorPos'])==wanted:break
  e.press('DOWN',hold=3,after=12)
 assert e.u8(syms['sStartMenuCursorPos'])==wanted
 e.press('A',hold=3,after=20);p=uiwait('Task_PokedexScreen',6)
 assert 0x02000000<=p and p+1048<=0x02040000
 assert e.u8(p+110)==region and not e.u8(p+111),(label,e.u8(p+110),e.u8(p+111))
 inverse=struct.unpack('<387H',e.read(p+112,774));assert inverse[0]==0
 assert sorted(v for v in inverse if v)==list(range(1,count+1))
 if region==0:assert list(inverse[1:152])==list(range(1,152)) and not any(inverse[152:])
 if region==1:
  order_dex=struct.unpack('<251H',e.read(syms['sJohtoToNationalOrder'],502))
  assert all(inverse[n]==i for i,n in enumerate(order_dex,1)) and inverse[25]==22
 if region==2:assert inverse[252]==1 and inverse[25]==156 and inverse[386]==202
 e.shot(str(out/(label+'-menu.png')));e.press('A',hold=3,after=20);p=uiwait('Task_DexScreen_NumericalOrder',6)
 assert e.u8(p+66)==0 and e.u8(p+110)==region and not e.u8(p+111)
 entries=e.u16(p+72);assert 0<entries<=count+1
 e.shot(str(out/(label+'-numerical.png')));close_ui();assert record(e)==baseline
 return {'label':label,'region':region,'dex_count':count,'inverse_entries':count,'numerical_rows':entries,'real_start_menu':True,'party_PC_dex_records_preserved':True}
try:
 for case in ('johto-lab','hoenn-lab'):
  fixture=SaveFile(str(sav));fixture.set_var('VAR_HAPPINESS_STEP_COUNTER',0);fixture.set_var('VAR_REPEL_STEP_COUNT',250)
  if case=='johto-lab':fixture.warp('NewBarkTown',11,10)
  else:
   fixture.set_flag('FLAG_HOENN_BIRCH_RESCUED',True);fixture.set_var('VAR_HOENN_SCENE_BIRCH',1);fixture.warp('LittlerootTown',7,18)
  fp=out/(case+'-input.sav');fixture.save(str(fp));row={'case':case,'temporary_preboot_warp_only':True,'hoenn_unlock_preboot_fixture':case=='hoenn-lab','doors':[],'UI':[]}
  report['current_case']=row
  with ReadOnlyEmu(str(rom),str(fp),sym='') as e:
   e.syms=syms;e.boot_continue();settle(e);baseline=record(e)
   if case=='johto-lab':
    assert e.location()[2:]==(11,10);row['UI'].append(dex_ui(0,151,'before-lab-kanto'))
    hop('UP');position=hop('UP');assert position[:2]==(map_info('NewBarkTown_ElmsLab')['group'],map_info('NewBarkTown_ElmsLab')['num']),position
    row['doors'].append({'label':'entry','position':position})
    # The real professor at (7,8), without accepting the assistant gift.
    while e.location()[3]>9:hop('UP')
    if e.location()[2]==6:hop('RIGHT')
    assert e.location()[2:]==(7,9),e.location()
    e.hold('UP');e.run(4);e.hold();e.run(20);assert e.location()[2:]==(7,9)
    e.press('A',hold=3,after=20)
    for i in range(1200):
     if e.field_idle():break
     if i%8==0:e.press('A',hold=1,after=1)
     else:e.run(1)
    else:raise AssertionError('professor dialogue locked player')
    assert blocks(e).flag('FLAG_JOHTO_MET_LAB_ASSISTANT')
    assert not blocks(e).flag('FLAG_HOENN_BIRCH_RESCUED') and not blocks(e).flag('FLAG_HOENN_MET_STERN')
    assert record(e)==baseline;row['actual_professor_first_visit_unlocked_Johto']=True
    row['UI'].append(dex_ui(1,251,'after-professor-johto'))
    hop('LEFT')
   else:
    row['UI'].append(dex_ui(2,202,'hoenn-checkpoint'))
    hop('UP');position=hop('UP');assert position[:2]==(map_info('LittlerootTown_ProfessorBirchsLab')['group'],map_info('LittlerootTown_ProfessorBirchsLab')['num']),position
    row['doors'].append({'label':'entry','position':position})
   # Exit by the same physical front door, then enter again.
   while e.location()[3]<11:hop('DOWN')
   position=hop('DOWN')
   expected_lab='NewBarkTown_ElmsLab' if case=='johto-lab' else 'LittlerootTown_ProfessorBirchsLab'
   if position[:2]==(map_info(expected_lab)['group'],map_info(expected_lab)['num']):
    assert position[3]==12,('exit is not on south-arrow warp',position)
    position=hop('DOWN')
   town='NewBarkTown' if case=='johto-lab' else 'LittlerootTown'
   assert position[:2]==(map_info(town)['group'],map_info(town)['num']),position
   row['doors'].append({'label':'exit','position':position})
   position=hop('UP');lab='NewBarkTown_ElmsLab' if case=='johto-lab' else 'LittlerootTown_ProfessorBirchsLab'
   assert position[:2]==(map_info(lab)['group'],map_info(lab)['num']),position
   row['doors'].append({'label':'reentry','position':position});assert record(e)==baseline
   row['native_SAVE_cold']=flash_reload(e,case+'-doors-dex');assert record(e)==baseline
   row['UI'].append(dex_ui(1 if case=='johto-lab' else 2,251 if case=='johto-lab' else 202,case+'-cold'))
   row['pass']=True;report['cases'].append(row)
 report['pass']=True
except Exception as ex:
 report['error']=repr(ex);report['traceback']=traceback.format_exc()
 if e and e.h:report['failure_location']=e.location()
finally:
 report['inputs_unchanged']=all(sha(Path(p))==h for p,h in before.items())
 if not report['inputs_unchanged']:report['pass']=False
 (out/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
sys.exit(0 if report['pass'] else 1)
