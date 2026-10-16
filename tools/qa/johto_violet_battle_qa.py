#!/usr/bin/env python3
"""Native Violet battles and menu-save QA. Input ROM/SAV are immutable."""
from pathlib import Path
import argparse,ast,hashlib,json,os,re,struct,subprocess,sys,tempfile
p=argparse.ArgumentParser()
for name in ['rom','elf','sav','out']:p.add_argument('--'+name,required=True)
a=p.parse_args();rom,elf,sav,out=[Path(getattr(a,n)).resolve() for n in ['rom','elf','sav','out']]
out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(Path.cwd()/'tools/qa'))
from emu import Emu
import gamedata as gd
from gamedata import const,off,map_info,Rom
from savefile import SaveFile,Mon,Blocks,checksum
gd.FIELDS.update({'battlemon':('BattlePokemon',None),'battlemon.moves':('BattlePokemon','moves'),'battlemon.pp':('BattlePokemon','pp'),'battlemon.type1':('BattlePokemon','type1'),'battlemon.type2':('BattlePokemon','type2'),'battlemove':('BattleMove',None)})
gd._OFFSETS=None
dka=Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))
table=subprocess.check_output([str(dka/'bin/arm-none-eabi-objdump'),'-t',str(elf)],text=True)
syms={};sets={}
for line in table.splitlines():
 v=line.split()
 if len(v)>=5 and re.fullmatch('[0-9a-fA-F]{8}',v[0]):
  addr=int(v[0],16);syms[v[-1]]=addr;sets.setdefault(v[-1],set()).add(addr&~1)
r=Rom.__new__(Rom);r.data=rom.read_bytes();r.syms=syms
assert off('pokemon')==100 and off('boxmon')==80 and off('battlemon')==88
assert off('battlemove') in (9,12)
lib=Path('tools/qa/libqa.so')
assert lib.exists() and lib.stat().st_mtime >= Path('tools/qa/libqa.c').stat().st_mtime
# Reuse the already executed controller and native move-selection helpers only.
helper=Path('tools/qa/hoenn_gauntlet_save_qa.py').read_text()
wanted={'safe','mash_until','settle','ctrl','menu','effectiveness','choose_move','fight_one_turn'}
nodes=[n for n in ast.parse(helper).body if isinstance(n,ast.FunctionDef) and n.name in wanted]
assert {n.name for n in nodes}==wanted,'helper API differs; inspect before running'
type_table=r.at(syms['gTypeEffectiveness'],1024)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<executed-gauntlet-helpers>','exec'),globals())
class ReadOnlyEmu(Emu):
 def write(self,*a,**k):raise AssertionError('No native memory writes in this test')
def digest(b):return hashlib.sha256(b).hexdigest()
originals={f:digest(f.read_bytes()) for f in set([sav,rom,elf]+list(Path('saves').glob('*.sav')))}
def blocks(e):return Blocks(e.read(e.ptr('gSaveBlock1Ptr'),off('sb1')),e.read(e.ptr('gSaveBlock2Ptr'),off('sb2')))
A='FLAG_JOHTO_ARRIVAL_BRIEFED';L='FLAG_JOHTO_MET_LAB_ASSISTANT';E='FLAG_JOHTO_ELM_REPORT_DELIVERED'
T='FLAG_JOHTO_SPROUT_TOWER_CLEARED';H='FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED'
B='FLAG_JOHTO_BADGE01_GET';M='FLAG_JOHTO_GOT_TM40_FROM_FALKNER'
K=[f'FLAG_BADGE{i:02d}_GET' for i in range(1,9)]
def fixture(path,name,loss):
 s=SaveFile(str(sav));s.fast_battles();s.keep_party(1)
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 for f in [A,L,E]+K:s.set_flag(f,True)
 for f in [T,H,B,M]:s.set_flag(f,False)
 for tr in ['LI','FALKNER']:s.set_trainer_beaten('TRAINER_JOHTO_'+tr,False)
 if name=='LI':s.warp('SproutTower_3F',6,9)
 else:s.warp('VioletCity_Gym',6,6);s.set_flag(T,True)
 for item in ['ITEM_HM05','ITEM_TM40']:s.set_item(item,0)
 s.set_item('ITEM_TM_CASE',1)
 m=s.party_mon(0);owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
 m.set_otid(owner);m.set_starter_bit(False);m.set_snagged(False)
 m.set_species(const('SPECIES_MAGIKARP' if loss else 'SPECIES_MEWTWO'),rom=r)
 sub=m.subs();sub['E'][:6]=bytes(6);sub['A'][:]=bytes(12)
 moves=['SPLASH'] if loss else ['AERIAL_ACE','THUNDERBOLT','ICE_BEAM','SHADOW_BALL']
 for i,n in enumerate(moves):
  mid=const('MOVE_'+n);struct.pack_into('<H',sub['A'],2*i,mid)
  pp=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))[4]
  sub['A'][8+i]=pp if loss else pp*8//5
 sub['G'][8]=0 if loss else 255
 struct.pack_into('<I',sub['M'],4,struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30))
 m.put_subs(sub);m.blk[m.o+19]=(m.blk[m.o+19]&~5)|2
 m.set_held(const('ITEM_NONE' if loss else 'ITEM_LEFTOVERS'));m.make_strong(1 if loss else 100,rom=r)
 s.save(str(path))
 return s
def snapshot(e):
 b=blocks(e);party=e.read(e.sym('gPlayerParty'),6*off('pokemon'))
 n=e.u8(e.sym('gPlayerPartyCount'));pc=e.read(e.ptr('gPokemonStoragePtr'),off('storage'))
 for i in range(n):
  mon=Mon(bytearray(party),i*100)
  total=sum(v[0] for sub in mon.subs().values() for v in struct.iter_unpack('<H',sub))&65535
  assert total==struct.unpack_from('<H',party,i*100+28)[0]
  assert not (party[i*100+19]&1),'new Bad Egg'
 return {'party':party,'party_count':n,'pc':pc,
  'dex':[b.dex_state(i) for i in range(1,387)],
  'flags':{f:b.flag(f) for f in [A,L,E,T,H,B,M]+K},
  'trainers':{n:b.trainer_beaten('TRAINER_JOHTO_'+n) for n in ['LI','FALKNER']}}
def native_save(e):
 before=e.u32(e.sym('gSaveCounter'));e.press('START',hold=3,after=60)
 count=e.u8(e.sym('sNumStartMenuItems'));order=list(e.read(e.sym('sStartMenuOrder'),count))
 assert 4 in order;target=order.index(4)
 for _ in range(count+1):
  if e.u8(e.sym('sStartMenuCursorPos'))==target:break
  e.press('DOWN',hold=3,after=12)
 else:raise AssertionError('SAVE cursor not reached')
 e.press('A',hold=3,after=30)
 for _ in range(600):
  if e.u32(e.sym('gSaveCounter'))>before and e.field_idle():break
  safe(e);e.press('A',hold=2,after=14)
 else:raise AssertionError('native menu save did not finish')
 assert e.u8(e.sym('gSaveAttemptStatus'))==1
 return before,e.u32(e.sym('gSaveCounter'))
def flash_reload(e,name):
 counters=native_save(e);live=snapshot(e);e.run(30)
 e.lib.qa_close(e.h);e.h=None
 stored=SaveFile(e.sav_path)
 for _,sid,size in stored.layout:
  pos=stored.where[sid]*4096
  assert checksum(stored.raw[pos:pos+size])==struct.unpack_from('<H',stored.raw,pos+0xff6)[0]
 assert stored.counter>counters[0]
 assert bytes(stored.blocks['storage'])==live['pc']
 assert stored.party_count()==live['party_count']
 assert bytes(stored.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600])==live['party']
 assert [stored.dex_state(i) for i in range(1,387)]==live['dex']
 for f,v in live['flags'].items():assert stored.flag(f)==v
 for n,v in live['trainers'].items():assert stored.trainer_beaten('TRAINER_JOHTO_'+n)==v
 dst=out/(name+'-native-QA-only.sav');assert not dst.exists()
 dst.write_bytes(Path(e.sav_path).read_bytes())
 e.h=e.lib.qa_open(str(rom).encode(),str(e.sav_path).encode());assert e.h
 e.boot_continue();settle(e);cold=snapshot(e)
 assert cold==live,('cold-load differs',[k for k in cold if cold[k]!=live[k]])
 return {'counter':counters,'checksummed_sectors':len(stored.layout),'qa_save':str(dst)}
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='violet-native-') as td:
  for name in ['LI','FALKNER']:
   for loss in [False,True]:
    tag=name.lower()+('_loss' if loss else '_win')
    f=Path(td)/(tag+'.sav');prepared=fixture(f,name,loss)
    expected={const('SPECIES_'+n) for n in (['BELLSPROUT','HOOTHOOT'] if name=='LI' else ['PIDGEY','PIDGEOTTO'])}
    with ReadOnlyEmu(str(rom),str(f),sym='') as e:
     e.syms=syms;e.boot_continue();settle(e);e.run(60)
     baseline=snapshot(e);e.walk('UP',1);e.run(30);e.press('A',hold=3,after=12)
     mash_until(e,e.in_battle,300);assert menu(e)
     assert e.u16(e.sym('gTrainerBattleOpponent_A'))==const('TRAINER_JOHTO_'+name)
     enemies=e.read(e.sym('gEnemyParty'),600)
     actual=[Mon(bytearray(enemies),i*100).species() for i in range(6) if Mon(bytearray(enemies),i*100).has_species()]
     assert len(actual)==2 and set(actual)==expected,actual
     turns=0
     while menu(e):
      assert turns<90,'battle did not finish'
      fight_one_turn(e,loss=loss);turns+=1
     settle(e);after=snapshot(e)
     assert all(after['flags'][k]==baseline['flags'][k] for k in K)
     assert after['pc']==baseline['pc']==bytes(prepared.blocks['storage'])
     for old,new in zip(baseline['dex'],after['dex']):
      assert old[0]==new[0] and all(not x or y for x,y in zip(old,new))
     assert after['trainers'][name]==(not loss)
     if name=='LI':
      assert after['flags'][T]==(not loss) and after['flags'][H]==(not loss)
      assert blocks(e).item_count('ITEM_HM05')==(0 if loss else 1)
      assert after['flags'][B]==False and after['flags'][M]==False
     else:
      assert after['flags'][T] and after['flags'][B]==(not loss) and after['flags'][M]==(not loss)
      assert blocks(e).item_count('ITEM_TM40')==(0 if loss else 1)
     row={'case':tag,'turns':turns,'enemies':actual,'pc_preserved':True,'kanto_badges_preserved':True}
     e.shot(str(out/(tag+'.png')),scale=3)
     if not loss:row['save']=flash_reload(e,tag)
     results.append(row);print(json.dumps(row),flush=True)
finally:
 for f,sha in originals.items():assert digest(f.read_bytes())==sha,('original changed',str(f))
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'helper_sha256':digest(helper.encode()),'input_sav_sha256':originals[sav],'cases':results,'all_pass':len(results)==4},indent=2))
