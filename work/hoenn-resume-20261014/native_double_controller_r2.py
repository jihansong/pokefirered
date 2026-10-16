"""Prepared actual-key single/double QA controller; native testing still required.
No ROM, SAV, RAM write, forced event, or forced battle outcome here.
"""
import ast, re, struct
from pathlib import Path

def install(ctx):
 gd,off,const,syms,report=[ctx[k] for k in ['gd','off','const','syms','report']]
 rows=ctx['actual_rows'];sections=ctx['sections']
 gd.FIELDS.update({
  'dc.hp':('BattlePokemon','hp'),'dc.attack':('BattlePokemon','attack'),
  'dc.spAttack':('BattlePokemon','spAttack'),'dc.defense':('BattlePokemon','defense'),
  'dc.spDefense':('BattlePokemon','spDefense'),
  'dc.power':('BattleMove','power'),'dc.type':('BattleMove','type'),
  'dc.target':('BattleMove','target')})
 gd._OFFSETS=None
 report['compiler_double_offsets']={k:off(k) for k in gd.FIELDS if k.startswith('dc.')}
 def owner(v):return Path(v).name.removesuffix('.o')+'.c' if v.endswith('.o') else Path(v).name
 def bind(name,size=None,tu=None,func=False):
  found=[v for v in rows.get(name,[]) if tu is None or owner(v['translation_unit'])==tu]
  assert len(found)==1,('Missing/ambiguous controller symbol',name,tu,found)
  r=found[0];q=sections[r['section']];v=r['value'];lo=v&~1 if func else v
  assert (r['info']&15)==(2 if func else 1) and r['size']>0
  assert size is None or r['size']==size,(name,r,size)
  assert q[2]&2 and q[3]<=lo and lo+r['size']<=q[3]+q[5]
  if func:assert q[2]&4 and 0x08000000<=lo<0x0a000000
  else:assert ((0x02000000<=v and v+r['size']<=0x02040000)or(0x03000000<=v and v+r['size']<=0x03008000)) and q[2]&1
  syms[name]=lo if func else v;report.setdefault('double_symbol_bindings',{})[name]=r
  return syms[name]
 nbmax=const('MAX_BATTLERS_COUNT');assert nbmax==4
 for name,size in [('gBattlerPositions',4),('gBattlerPartyIndexes',8),('gBattlerControllerFuncs',16),('gBattleControllerExecFlags',4),('gMoveSelectionCursor',4),('gActionSelectionCursor',4),('gMultiUsePlayerCursor',1),('gAbsentBattlerFlags',1),('gBattleMons',4*off('battlemon'))]:bind(name,size)
 callbacks={n:bind(n,tu='battle_controller_player.c',func=True) for n in ['HandleInputChooseAction','HandleInputChooseTarget']}
 # STT_FILE ownership is meaningful for static functions; the exported Move
 # handler is bound by its unique global function row instead.
 move_rows=rows.get('HandleInputChooseMove',[])
 assert len(move_rows)==1 and move_rows[0]['info']>>4==1,('Move handler is not a unique global',move_rows)
 callbacks['HandleInputChooseMove']=bind('HandleInputChooseMove',func=True)
 assert const('B_SIDE_PLAYER')==0 and const('BIT_SIDE')==1
 party_source=(Path(ctx['root'])/'src/party_menu.c').read_text()
 assert re.search(r'^#define\s+MENU_DIR_DOWN\s+1\s*$',party_source,re.M)
 def e():return ctx['e']
 def alive(b):return not(e().u8(syms['gAbsentBattlerFlags'])&(1<<b)) and e().u16(syms['gBattleMons']+b*off('battlemon')+off('dc.hp'))>0
 def player_ids():return [i for i in range(e().u8(syms['gBattlersCount'])) if not(e().u8(syms['gBattlerPositions']+i)&1)]
 def ready(name):
  ids=[b for b in player_ids() if alive(b) and (e().u32(syms['gBattleControllerExecFlags'])&(1<<b)) and (e().u32(syms['gBattlerControllerFuncs']+4*b)&~1)==callbacks[name]]
  assert len(ids)<=1,('Ambiguous native input handler',name,ids)
  return ids
 def nav(target,read_slot,choose_ready,safety_check,*,layout_verified,max_inputs=24):
  assert layout_verified and 0<=target<6
  trace=[]
  for _ in range(max_inputs+1):
   safety_check();assert choose_ready()
   cur=read_slot();trace.append(cur)
   if cur==target:return trace
   assert cur in [0,1,2,3,4,5,7]
   e().press('DOWN',hold=2,after=14)
  raise AssertionError(('Actual party cursor did not reach target',target,trace))
 ctx['navigate_verified_slot']=nav
 text=Path(ctx['__file__']).read_text();tree=ast.parse(text)
 blocks=[n for t in tree.body if isinstance(t,ast.Try) for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='native_send_out'];assert len(blocks)==1
 s=ast.get_source_segment(text,blocks[0])
 def change(a,b):
  nonlocal s
  assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
 change("assert not e.u32(syms['gBattleTypeFlags']) & 1, 'This QA controller supports a single battle only'", "assert not e.u32(syms['gBattleTypeFlags']) & const('BATTLE_TYPE_MULTI'), 'Link/multi party layout not verified'")
 change("assert nb == 2, ('Expected a single battle', nb)", "assert nb in (2,4), ('Expected ordinary single/double battle', nb)")
 change("active = {e.u8(syms['gBattlerPartyIndexes'])}", "active = {e.u16(syms['gBattlerPartyIndexes'] + 2*i) for i in range(nb) if not (e.u8(syms['gBattlerPositions'] + i) & 1)}")
 change('navigate_ui_slot(e, target, slot, choose_ready,', 'navigate_verified_slot(target, slot, choose_ready,')
 change('single_battle_verified=True)', 'layout_verified=True)')
 exec(compile(s,'<verified-r6-native-send-out-single-double>','exec'),ctx)
 report['double_forced_replacement_controller']='Current party_menu.c source; real DOWN/A/SEND OUT, UI HP and both active battle indexes excluded'
 def move(b):
  ppbase=syms['gBattleMons']+b*off('battlemon')
  moves=struct.unpack('<4H',e().read(ppbase+off('battlemon.moves'),8));pps=list(e().read(ppbase+off('battlemon.pp'),4))
  opponents=[i for i in range(e().u8(syms['gBattlersCount'])) if e().u8(syms['gBattlerPositions']+i)&1 and alive(i)]
  assert opponents,('No alive opponent for move',b)
  target=opponents[0];z=syms['gBattleMons']+target*off('battlemon');t1=e().u8(z+off('battlemon.type1'));t2=e().u8(z+off('battlemon.type2'))
  scores=[]
  for mid,pp in zip(moves,pps):
   if not mid or not pp:scores.append(-1);continue
   p=syms['gBattleMoves']+mid*off('battlemove');power=e().u8(p+off('dc.power'));typ=e().u8(p+off('dc.type'))
   atk=e().u16(ppbase+off('dc.spAttack' if typ>9 else 'dc.attack'));defense=max(1,e().u16(z+off('dc.spDefense' if typ>9 else 'dc.defense')))
   scores.append(power*ctx['effectiveness'](typ,t1,t2)*atk/defense)
  assert max(scores)>=0,('No usable PP; unverified Struggle UI',b,moves,pps)
  idx=max(range(4),key=lambda j:scores[j])
  for key in ['UP','LEFT']:e().press(key,hold=3,after=10)
  if idx&1:e().press('RIGHT',hold=3,after=10)
  if idx&2:e().press('DOWN',hold=3,after=10)
  assert e().u8(syms['gMoveSelectionCursor']+b)==idx and ready('HandleInputChooseMove')==[b]
  row={'frame':e().frame(),'battler':b,'move_slot':idx,'move':moves[idx],'PP_before':pps[idx],'opponent_candidate':target,'actual_keys':True}
  e().press('A',hold=3,after=20)
  report.setdefault('double_actions',[]).append(row);ctx['emit']()
 def target_input(b):
  wanted=[i for i in range(e().u8(syms['gBattlersCount'])) if e().u8(syms['gBattlerPositions']+i)&1 and alive(i)][0]
  trace=[]
  for _ in range(8):
   assert ready('HandleInputChooseTarget')==[b]
   cur=e().u8(syms['gMultiUsePlayerCursor']);trace.append(cur)
   if cur==wanted:break
   e().press('RIGHT',hold=2,after=14)
  else:raise AssertionError(('Actual target cursor did not reach opponent',b,wanted,trace))
  assert alive(wanted) and e().u8(syms['gBattlerPositions']+wanted)&1
  e().press('A',hold=3,after=20);report.setdefault('double_targets',[]).append({'battler':b,'target':wanted,'cursor_trace':trace,'actual_keys':True});ctx['emit']()
 def fight():
  start=e().frame();opponent=e().u16(syms['gTrainerBattleOpponent_A']);double=bool(e().u32(syms['gBattleTypeFlags'])&const('BATTLE_TYPE_DOUBLE'));initial_actions=len(report.get('double_actions',[]))
  for tick in range(30000):
   ctx['safe'](e())
   if e().in_overworld() and e().u8(syms['gBattleOutcome'])!=0:
    result=e().u8(syms['gBattleOutcome']);actions=report.get('double_actions',[])[initial_actions:]
    report.setdefault('battles',[]).append({'opponent':opponent,'double':double,'outcome':result,'actions':len(actions),'selected_battlers':sorted({v['battler'] for v in actions}),'actual_keys':True,'start_frame':start,'end_frame':e().frame()});ctx['emit']()
    expected=ctx.get('expected_native_outcome',const('B_OUTCOME_WON'))
    if result!=expected:
     raise AssertionError(('Actual battle outcome differs; progression stopped',result,opponent,expected))
    if double:assert {v['battler'] for v in actions}=={0,2},('Both double actions not observed',actions)
    return result
   if ctx['is_party_menu']():
    if ctx['choose_ready']():ctx['native_send_out']()
    else:e().run(1)
    continue
   if ready('HandleInputChooseAction'):
    b=ready('HandleInputChooseAction')[0]
    for key in ['UP','LEFT','A']:e().press(key,hold=3,after=12)
    for _ in range(240):
     if ready('HandleInputChooseMove')==[b]:break
     ctx['safe'](e());e().run(1)
    else:raise AssertionError(('Real FIGHT did not reach indexed move menu',b))
    move(b);continue
   if ready('HandleInputChooseMove'):move(ready('HandleInputChooseMove')[0]);continue
   if ready('HandleInputChooseTarget'):target_input(ready('HandleInputChooseTarget')[0]);continue
   if tick%20==0:e().press('B',hold=1,after=0)
   else:e().run(1)
  raise AssertionError(('Actual battle exceeded bounded frames',opponent,e().callback2()))
 ctx['fight_native_indexed']=fight
 return fight
