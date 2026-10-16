#!/usr/bin/env python3
"""Native Hoenn gauntlet QA. Changes only a TEMPORARY pre-boot save fixture.
All battle outcomes, progress flags, healing and HOF saves must be native.
Not a normal-level battle-balance test. No RAM writes or forced outcomes."""
import argparse, hashlib, json, os, re, struct, subprocess, sys, tempfile, traceback
from pathlib import Path
ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'tools/qa'))
import gamedata as gd
from gamedata import const, off, map_info, Rom
from savefile import SaveFile, Blocks, Mon, checksum
from emu import Emu
gd.FIELDS.update({
 'battlemon':('BattlePokemon',None),'battlemon.moves':('BattlePokemon','moves'),
 'battlemon.pp':('BattlePokemon','pp'),'battlemon.hp':('BattlePokemon','hp'),
 'battlemon.type1':('BattlePokemon','type1'),'battlemon.type2':('BattlePokemon','type2'),
 'battlemove':('BattleMove',None)})
P=argparse.ArgumentParser()
P.add_argument('--rom',required=True); P.add_argument('--elf',required=True)
P.add_argument('--sav',required=True); P.add_argument('--out',required=True)
P.add_argument('--loss',action='store_true',help='Separate one-mon native blackout case')
a=P.parse_args()
rom,sav,elf=map(lambda x:Path(x).resolve(),(a.rom,a.sav,a.elf))
out=Path(a.out).resolve(); out.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
protected={p.resolve() for p in (ROOT/'saves').rglob('*.sav')}|{sav}
before={str(p):sha(p.read_bytes()) for p in protected}
report={'pass':False,'rom_sha256':sha(rom.read_bytes()),'elf_sha256':sha(elf.read_bytes()),
 'save_sha256':before[str(sav)],'mode':'loss' if a.loss else 'five_native_wins',
 'fixture':'temporary copy, level-100 Mewtwo party' if not a.loss else 'temporary copy, one level-1 Magikarp with Splash',
 'ram_writes':0,'forced_battle_outcomes':0,'stages':[]}
dka=Path(os.environ.get('DEVKITARM','/opt/devkitpro/devkitARM'))
table=subprocess.check_output([str(dka/'bin/arm-none-eabi-objdump'),'-t',str(elf)],text=True)
syms={}; sets={}
for line in table.splitlines():
 p=line.split()
 if len(p)>=6 and re.fullmatch('[0-9a-fA-F]{8}',p[0]):
  v=int(p[0],16); name=p[-1]
  syms[name]=v; sets.setdefault(name,set()).add(v&~1)
required=['gMain','gBattlerControllerFuncs','gBattleMons','gPlayerParty',
 'gSaveBlock1Ptr','gSaveBlock2Ptr','gPokemonStoragePtr','CB2_Credits',
 'HandleInputChooseAction','HandleInputChooseMove','gTypeEffectiveness','gBattleMoves']
assert all(n in syms for n in required), [n for n in required if n not in syms]
lib=ROOT/'tools/qa/libqa.so'
assert lib.exists() and lib.stat().st_mtime >= (ROOT/'tools/qa/libqa.c').stat().st_mtime, 'QA runtime rebuild required'
r=Rom.__new__(Rom); r.data=rom.read_bytes(); r.syms=syms
# ROM bytes matching the same ELF function sections are independently checked by root.
assert off('pokemon')==100 and off('boxmon')==80
assert off('battlemon')==88 and off('battlemove') in (9,12)
report['native_abi']={'BattlePokemon':off('battlemon'),'BattleMove':off('battlemove')}
teams=['SIDNEY','PHOEBE','GLACIA','DRAKE','WALLACE']
trainers=['TRAINER_HOENN_'+n for n in teams]
rooms=['EverGrandeCity_'+n for n in ['SidneysRoom','PhoebesRoom','GlaciasRoom','DrakesRoom','ChampionsRoom']]
lobby='EverGrandeCity_PokemonLeague_1F'
progress='VAR_HOENN_LEAGUE_PROGRESS'; cleared='FLAG_HOENN_LEAGUE_CLEAR'
badges=['FLAG_HOENN_BADGE%02d_GET'%i for i in range(1,9)]
cs=const('TOTAL_BOXES_COUNT')*const('IN_BOX_COUNT')*off('boxmon')
boxoff=off('storage.boxes')
source=SaveFile(str(sav)); source_pc=bytes(source.blocks['storage'][boxoff:boxoff+cs])
report['pc_before_sha256']=sha(source_pc)
def digest_dex(b):
 n=off('dex.seen')-off('dex.owned')
 assert n>=49 and n<=64
 vals=[b.sb2[off('sb2.pokedex')+off('dex.owned'):off('sb2.pokedex')+off('dex.owned')+n],
       b.sb2[off('sb2.pokedex')+off('dex.seen'):off('sb2.pokedex')+off('dex.seen')+n],
       b.sb1[off('sb1.seen1'):off('sb1.seen1')+n],b.sb1[off('sb1.seen2'):off('sb1.seen2')+n]]
 return [sha(bytes(x)) for x in vals]
def check_sectors(s):
 got=[]
 for name,sid,size in s.layout:
  pos=s.where[sid]*0x1000
  actual=checksum(s.raw[pos:pos+size]); stored=struct.unpack_from('<H',s.raw,pos+0xff6)[0]
  assert actual==stored,(sid,actual,stored)
  got.append(sid)
 assert sorted(got)==list(range(14))
 return got
def party_valid(data,count):
 for i in range(count):
  mon=Mon(bytearray(data),i*100)
  dec=b''.join(mon.subs()[k] for k in 'GAEM')
  assert sum(struct.unpack('<24H',dec))&65535 == struct.unpack_from('<H',data,i*100+28)[0],('party checksum',i)
class ReadOnlyEmu(Emu):
 def write(self,*args,**kwargs): raise AssertionError('RAM writing is forbidden in this QA')
def blocks(e):
 return Blocks(e.read(e.ptr('gSaveBlock1Ptr'),off('sb1')),e.read(e.ptr('gSaveBlock2Ptr'),off('sb2')))
def pc(e): return e.read(e.ptr('gPokemonStoragePtr')+boxoff,cs)
def loc_is(e,name):
 m=map_info(name); return e.location()[:2]==(m['group'],m['num'])
def photo(e,name):
 e.shot(str(out/(name+'.png')),scale=3)
def safe(e):
 assert not e.reset_seen(),('unexpected reset',hex(e.callback2()))
def mash_until(e,pred,limit=400,key='A'):
 for _ in range(limit):
  if pred(): return
  safe(e); e.press(key,hold=2,after=14)
 raise AssertionError(('timeout',key,e.location(),hex(e.callback2())))
def settle(e):
 mash_until(e,e.field_idle,200)
def go(e,x,y):
 for axis,target,poskey,negkey in [(2,x,'RIGHT','LEFT'),(3,y,'DOWN','UP')]:
  for _ in range(40):
   cur=e.location()[axis]
   if cur==target: break
   old=e.location()
   e.walk(poskey if cur<target else negkey)
   assert e.location()!=old,('blocked route',old,x,y)
  assert e.location()[axis]==target,('walk position',e.location(),x,y)
def facing_up(e):
 e.press('UP',hold=2,after=12)
def ctrl(e,b,name):
 return (e.u32(e.sym('gBattlerControllerFuncs')+4*b)&~1) in sets.get(name,set())
def menu(e):
 for _ in range(120):
  if not e.in_battle(): return False
  if ctrl(e,0,'HandleInputChooseAction'): e.run(20); return True
  e.run(1)
 for _ in range(400):
  if not e.in_battle(): return False
  if ctrl(e,0,'HandleInputChooseAction'): e.run(20); return True
  safe(e); e.press('B',hold=2,after=14)
 raise AssertionError(('no native action menu',hex(e.callback2())))
type_table=r.at(syms['gTypeEffectiveness'],1024)
def effectiveness(t,t1,t2):
 result=1.0
 for j in range(0,len(type_table)-2,3):
  atk,defense,mul=type_table[j:j+3]
  if atk==255: break
  if atk==254: continue
  if atk==t and (defense==t1 or (defense==t2 and t2!=t1)): result*=mul/10.0
 return result
def choose_move(e):
 p=e.sym('gBattleMons'); z=p+off('battlemon')
 moves=struct.unpack('<4H',e.read(p+off('battlemon.moves'),8)); pp=e.read(p+off('battlemon.pp'),4)
 t1=e.u8(z+off('battlemon.type1')); t2=e.u8(z+off('battlemon.type2'))
 scores=[]
 for i,m in enumerate(moves):
  if not m or not pp[i]: scores.append(-1); continue
  raw=r.at(syms['gBattleMoves']+m*off('battlemove'),off('battlemove'))
  power,typ=raw[1],raw[2]
  attack=e.u16(p+(8 if typ>9 else 2)); defense=max(1,e.u16(z+(10 if typ>9 else 4)))
  scores.append(power*effectiveness(typ,t1,t2)*attack/defense)
 assert max(scores)>=0,('all PP empty',moves,list(pp))
 return max(range(4),key=lambda i:scores[i]),moves,pp
def fight_one_turn(e,loss=False):
 for key in ['UP','LEFT','A']: e.press(key,hold=3,after=12)
 for _ in range(200):
  if ctrl(e,0,'HandleInputChooseMove'): break
  e.run(1)
 else: raise AssertionError('FIGHT did not reach move menu')
 idx,moves,pp=(0,(),()) if loss else choose_move(e)
 for key in ['UP','LEFT']: e.press(key,hold=3,after=10)
 if idx&1: e.press('RIGHT',hold=3,after=10)
 if idx&2: e.press('DOWN',hold=3,after=10)
 assert e.u8(e.sym('gMoveSelectionCursor'))==idx
 e.press('A',hold=3,after=20)
 return idx
def battle(e,stage,loss=False):
 mash_until(e,e.in_battle,300)
 assert e.u16(e.sym('gTrainerBattleOpponent_A'))==const(trainers[stage])
 assert not (e.u32(e.sym('gBattleTypeFlags'))&1),'league should be single battles'
 assert menu(e), 'native battle ended before the first action menu'
 enemy_raw=e.read(e.sym('gEnemyParty'),6*off('pokemon'))
 enemy_species=[Mon(enemy_raw,i*off('pokemon')).species() for i in range(6)]
 opponents=sum(sp!=const('SPECIES_NONE') for sp in enemy_species)
 assert opponents==(6 if stage==4 else 5),(stage,opponents)
 row={'trainer':trainers[stage],'start_frame':e.frame(),'enemy_count':opponents,'moves':[]}
 row['enemy_species']=enemy_species
 photo(e,'battle-%d-start'%stage)
 for turn in range(90):
  if not menu(e): break
  row['moves'].append(fight_one_turn(e,loss))
 else: raise AssertionError('battle exceeds 90 selected turns')
 settle(e)
 row['end_frame']=e.frame()
 b=blocks(e)
 if loss:
  assert loc_is(e,lobby),('blackout destination',e.location())
  assert b.var(progress)==0 and not b.flag(cleared)
  assert all(not b.trainer_beaten(t) for t in trainers)
 else:
  assert loc_is(e,rooms[stage])
  assert b.var(progress)==stage+2,(stage,b.var(progress))
  assert not b.flag(cleared),'region completed before native HOF'
  assert [b.trainer_beaten(t) for t in trainers]==[i<=stage for i in range(5)]
 assert pc(e)==source_pc,'PC altered by native battle'
 photo(e,'battle-%d-result'%stage)
 report['stages'].append(row)
 print(json.dumps({'stage_done':row['trainer'],'turns':len(row['moves']),'outcome':'loss' if loss else 'win'}),flush=True)
tmp=None; e=None
try:
 with tempfile.TemporaryDirectory(prefix='hoenn-gauntlet-fixture-') as td:
  tmp=Path(td)/'fixture.sav'
  s=SaveFile(str(sav)); s.fast_battles()
  for i in range(const('QUEST_LOG_SCENE_COUNT')):
   s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
  for f in badges: s.set_flag(f,True)
  for t in trainers: s.set_trainer_beaten(t,False)
  s.set_flag(cleared,False); s.set_var(progress,0)
  s.warp(lobby,9,3)
  assert s.party_count()>0
  owner=struct.unpack_from('<I',s.sb2,off('sb2.playerTrainerId'))[0]
  move_names=['MOVE_AERIAL_ACE','MOVE_THUNDERBOLT','MOVE_ICE_BEAM','MOVE_SHADOW_BALL']
  if a.loss:
   s.keep_party(1); move_names=['MOVE_SPLASH']
  for i in range(s.party_count()):
   m=s.party_mon(i); m.set_otid(owner); m.set_starter_bit(False); m.set_snagged(False)
   m.set_species(const('SPECIES_MAGIKARP' if a.loss else 'SPECIES_MEWTWO'),rom=r)
   sub=m.subs(); sub['E'][:6]=bytes(6); sub['G'][8]=0 if a.loss else 255
   sub['A'][:]=bytes(12)
   for j,n in enumerate(move_names):
    mid=const(n); struct.pack_into('<H',sub['A'],2*j,mid)
    raw=r.at(syms['gBattleMoves']+mid*off('battlemove'),off('battlemove'))
    sub['A'][8+j]=raw[4] if a.loss else raw[4]*8//5
   # Remove egg/bad-egg metadata only in the temporary QA party fixture.
   iv=struct.unpack_from('<I',sub['M'],4)[0]&~(1<<30)
   struct.pack_into('<I',sub['M'],4,iv)
   m.put_subs(sub); m.blk[m.o+19]=(m.blk[m.o+19]&~5)|2
   m.set_held(const('ITEM_NONE' if a.loss else 'ITEM_LEFTOVERS'))
   m.make_strong(1 if a.loss else 100,rom=r)
  assert bytes(s.blocks['storage'][boxoff:boxoff+cs])==source_pc
  s.save(str(tmp)); check_sectors(SaveFile(str(tmp)))
  fixture_counter=s.counter
  e=ReadOnlyEmu(str(rom),str(tmp),sym=''); e.syms=syms
  e.boot_continue(); settle(e)
  assert loc_is(e,lobby) and e.location()[2:]==(9,3)
  assert blocks(e).var(progress)==0
  facing_up(e); e.press('A',hold=3,after=20)
  mash_until(e,lambda:loc_is(e,rooms[0]) and e.field_idle(),400)
  assert blocks(e).var(progress)==1
  for stage in range(1 if a.loss else 5):
   assert loc_is(e,rooms[stage])
   go(e,6,6); facing_up(e); e.press('A',hold=3,after=20)
   battle(e,stage,a.loss)
   if a.loss: break
   # Retalk only after native defeated flag and advance stage are observed.
   e.press('A',hold=3,after=20)
   if stage<4:
    mash_until(e,lambda:loc_is(e,rooms[stage+1]) and e.field_idle(),400)
   else:
    mash_until(e,lambda:(e.callback2()&~1)==syms['CB2_Credits'],900)
  if a.loss:
   report['native_blackout_to_lobby']=True
  else:
   e.run(60)
   b=blocks(e); mgr=e.ptr('sCreditsMgr')
   assert mgr and e.u16(mgr+16)==2,'not Hoenn credits'
   assert b.flag(cleared) and b.var(progress)==7
   assert all(b.trainer_beaten(t) for t in trainers)
   assert pc(e)==source_pc
   live_party=e.read(e.sym('gPlayerParty'),600)
   live_count=e.u8(e.sym('gPlayerPartyCount')); party_valid(live_party,live_count)
   live_dex=digest_dex(b)
   photo(e,'native-hoenn-credits')
   assert Path(e.sav_path).resolve()!=sav and Path(e.sav_path).resolve()!=tmp
   e.run(30); e.lib.qa_close(e.h); e.h=None
   written=Path(e.sav_path).read_bytes()
   flushed=SaveFile(e.sav_path); check_sectors(flushed)
   assert flushed.counter>fixture_counter,'native HOF did not advance flash save counter'
   assert flushed.flag(cleared) and flushed.var(progress)==7
   assert all(flushed.trainer_beaten(t) for t in trainers)
   assert bytes(flushed.blocks['storage'][boxoff:boxoff+cs])==source_pc
   party_off=off('sb1.playerParty')
   assert bytes(flushed.sb1[party_off:party_off+live_count*100])==live_party[:live_count*100], 'saved party differs from native HOF party'
   assert digest_dex(flushed)==live_dex,'saved dex differs from native HOF dex'
   report['native_hof_save']={'counter_before':fixture_counter,'counter_after':flushed.counter,
    'slot':flushed.slot,'valid_sectors':14,'party_count':live_count,'dex_sha256':live_dex,'save_sha256':sha(written)}
   e.h=e.lib.qa_open(str(rom).encode(),str(e.sav_path).encode()); assert e.h
   e.boot_continue(); settle(e)
   b=blocks(e)
   assert loc_is(e,lobby),('HOF continue destination',e.location())
   assert b.flag(cleared) and b.var(progress)==0
   assert all(not b.trainer_beaten(t) for t in trainers),'new league entry reset missing'
   assert pc(e)==source_pc
   assert e.read(e.sym('gPlayerParty'),live_count*100)==live_party[:live_count*100]
   assert digest_dex(b)==live_dex
   photo(e,'hof-save-reopened')
   report['hof_save_reopened_to_hoenn_lobby']=True
   report['pc_after_sha256']=sha(pc(e))
   # Keep the successful mutated QA fixture as evidence, never as the user save.
   (out/'qa-only-hof-result.sav').write_bytes(written)
  report['pass']=True
except Exception as ex:
 report['error']=repr(ex); report['traceback']=traceback.format_exc()
 if e and e.h:
  report['failure_location']=e.location(); report['failure_callback2']=hex(e.callback2())
  photo(e,'failure')
finally:
 if e: e.close()
 after={p:sha(Path(p).read_bytes()) for p in before}
 report['original_saves_unchanged']=before==after
 if before!=after: report['pass']=False; report['original_save_hash_mismatch']={p:[v,after[p]] for p,v in before.items() if v!=after[p]}
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ('traceback','stages')}),flush=True)
sys.exit(0 if report['pass'] else 1)
