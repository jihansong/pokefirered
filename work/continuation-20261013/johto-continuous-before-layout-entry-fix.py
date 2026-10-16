from pathlib import Path
import sys,hashlib,json,struct,traceback,collections
root=Path('/workspaces/pokefirered');out=root/'work/continuation-20261013/johto-continuous';out.mkdir(exist_ok=True)
rom=root/'pokemonthyl.gba';elf=root/'pokemonthyl.elf';sav=root/'saves/pokemonthyl_v1.25-items99-iv2x.sav'
sys.argv=['continuous','--rom',str(rom),'--elf',str(elf),'--sav',str(sav),'--out',str(out)]
q=(root/'tools/qa/native_misty_basic_qa.py').read_text();assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<verified-readonly-definitions>','exec'))
fs=['FLAG_JOHTO_ARRIVAL_BRIEFED','FLAG_JOHTO_MET_LAB_ASSISTANT','FLAG_JOHTO_MET_CHERRYGROVE_GUIDE','FLAG_JOHTO_MR_POKEMON_BRIEFED','FLAG_JOHTO_ELM_REPORT_DELIVERED']
report={'pass':False,'rom_sha256':digest(rom.read_bytes()),'sav_sha256':digest(sav.read_bytes()),'ram_writes':0,'direct_script_calls':0,'mid_run_warps':0,'mid_run_flag_sets':0,'scope':'Preboot champion eligibility fixture, actual Kanto flight and first Johto walk to professor; not genuine prior league win or entire campaign','stages':[],'walk_steps':[]}
layouts={x['id']:x for x in json.loads((root/'data/layouts/layouts.json').read_text())['layouts']}
e=None
def emit(): (out/'validation.json').write_text(json.dumps(report,indent=2))
def named(name):
 d=map_info(name);return (d['group'],d['num'])
def idle():
 for i in range(1200):
  safe(e);assert not e.in_battle()
  if e.field_idle():e.run(12);return
  if i%10==0:e.press('A',hold=1,after=1)
  else:e.run(1)
 raise AssertionError(('not idle',e.location()))
def hop(key):
 prev=e.location();e.hold(key)
 try:
  for i in range(160):
   e.run(1)
   if e.location()!=prev:break
  else:return False
 finally:e.hold()
 idle();report['walk_steps'].append({'key':key,'from':prev,'to':e.location()});return True
def grid(name):
 d=json.loads((root/'data/maps'/name/'map.json').read_text());l=layouts[d['layout']]
 b=struct.unpack('<'+str(l['width']*l['height'])+'H',(root/l['blockdata_filepath']).read_bytes())
 return d,l,{(i%l['width'],i//l['width']) for i,v in enumerate(b) if not v&0xc00}
def walkto(name,target):
 d,l,passable=grid(name);blocked={(o['x'],o['y']) for o in d['object_events']}|{(w['x'],w['y']) for w in d['warp_events'] if (w['x'],w['y'])!=tuple(target)}
 failures=set()
 for _ in range(1200):
  assert e.location()[:2]==named(name),(name,e.location())
  start=e.location()[2:]
  if start==tuple(target):return
  queue=collections.deque([start]);paths={start:[]}
  while queue:
   cur=queue.popleft()
   if cur==tuple(target):break
   for key,dx,dy in [('UP',0,-1),('DOWN',0,1),('LEFT',-1,0),('RIGHT',1,0)]:
    nxt=(cur[0]+dx,cur[1]+dy)
    if nxt in passable and nxt not in blocked|failures and nxt not in paths:
     paths[nxt]=paths[cur]+[key];queue.append(nxt)
  assert tuple(target) in paths,('no source path',name,start,target,list(failures))
  key=paths[tuple(target)][0];dx,dy={'UP':(0,-1),'DOWN':(0,1),'LEFT':(-1,0),'RIGHT':(1,0)}[key]
  if not hop(key):failures.add((start[0]+dx,start[1]+dy))
 raise AssertionError('path exceeded step budget')
def connection(src,dst,direction):
 _,l,a=grid(src);_,m,b=grid(dst)
 candidates=[]
 if direction=='right':
  for y in range(min(l['height'],m['height'])):
   if (l['width']-1,y) in a and (0,y) in b:candidates.append((l['width']-1,y))
 else:
  for x in range(min(l['width'],m['width'])):
   if (x,0) in a and (x,m['height']-1) in b:candidates.append((x,0))
 assert candidates,('no shared ground connection',src,dst)
 errors=[]
 for target in sorted(candidates,key=lambda v:abs(v[0]-e.location()[2])+abs(v[1]-e.location()[3])):
  try:walkto(src,target)
  except AssertionError as ex:errors.append(str(ex));continue
  if hop('RIGHT' if direction=='right' else 'UP') and e.location()[:2]==named(dst):return
 raise AssertionError(('native connection cannot traverse',src,dst,errors))
def party_preserved():
 now=e.read(syms['gPlayerParty'],600);assert identity(now,6)==identity(baseparty,6)
 for i in range(6):
  a=Mon(bytearray(now),i*100);b=Mon(bytearray(baseparty),i*100);x=a.subs();y=b.subs()
  x['G'][9]=y['G'][9]
  assert all(bytes(x[k])==bytes(y[k]) for k in x),('party core changed beyond walking friendship',i)
 assert e.read(e.ptr('gPokemonStoragePtr'),33744)==basepc
 assert [blocks(e).dex_state(i) for i in range(1,387)]==basedex
def stage(label):
 party_preserved();b=blocks(e)
 objs=e.objects();row={'stage':label,'position':e.location(),'flags':{f:b.flag(f) for f in fs},'Misty_joined':b.flag(join),'Misty_objects':len([o for o in objs if o.get('local_id')==253]),'Pikachu_objects':len([o for o in objs if o.get('local_id')==254]),'party_PC_Dex_preserved':True}
 report['stages'].append(row);emit();e.shot(str(out/(label+'.png')),scale=3)
def first_dex():
 baseline=record(e);e.press('START',hold=2,after=60)
 n=e.u8(syms['sNumStartMenuItems']);order=list(e.read(syms['sStartMenuOrder'],n));wanted=order.index(0)
 for _ in range(n+1):
  if e.u8(syms['sStartMenuCursorPos'])==wanted:break
  e.press('DOWN',hold=2,after=12)
 e.press('A',hold=2,after=25)
 for _ in range(1000):
  p=e.ptr('sPokedexScreenData')
  if p and e.u8(p+1)==6:break
  e.run(1)
 else:raise AssertionError('actual first-arrival Dex menu absent')
 assert e.u8(p+110)==1 and not e.u8(p+111)
 vals=struct.unpack('<387H',e.read(p+112,774));assert sorted(x for x in vals if x)==list(range(1,252))
 report['arrival_dex_count']=251;e.shot(str(out/'first-arrival-dex-251.png'),scale=3)
 for _ in range(600):
  if e.field_idle():break
  e.press('B',hold=1,after=5)
 else:raise AssertionError('Dex close failed')
 assert record(e)==baseline
try:
 assert report['rom_sha256']=='f31b2eea1ae45fd1dd40057c80510a8875936394e5807d00806a90cff1dee73d'
 s=SaveFile(str(sav));assert not s.flag('FLAG_SYS_GAME_CLEAR');assert not any(s.flag(f) for f in fs)
 s.set_flag('FLAG_SYS_GAME_CLEAR',True);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0);s.set_var('VAR_REPEL_STEP_COUNT',250)
 for j in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+j*off('questlogscene')]=0
 s.sb2[off('sb2.specialSaveWarpFlags')]&=~1;s.warp('KantoAirport',10,7)
 fp=out/'champion-airport-QA-only.sav';assert not fp.exists();s.save(str(fp))
 report['preboot_fixture_changes']=['Champion eligibility true (source was false)','Position KantoAirport 10,7 and quest log cleared','Happiness-step counter zero and Repel250'];emit()
 e=ReadOnlyEmu(str(rom),str(fp),sym='');e.syms=syms;e.boot_continue();idle()
 baseparty=e.read(syms['gPlayerParty'],600);basepc=e.read(e.ptr('gPokemonStoragePtr'),33744);basedex=[blocks(e).dex_state(i) for i in range(1,387)]
 stage('before-flight');e.press('UP',hold=1,after=20);e.press('A',hold=2,after=25)
 for i in range(6000):
  safe(e);assert not e.in_battle()
  if e.location()[:2]==named('JohtoCherrygroveAirstrip') and e.field_idle() and blocks(e).flag(fs[0]):break
  if i%8==0:e.press('A',hold=1,after=1)
  else:e.run(1)
 else:raise AssertionError(('Johto flight did not finish',e.location()))
 assert blocks(e).flag(join) and not any(blocks(e).flag(f) for f in fs[1:])
 stage('actual-flight-arrival');first_dex()
 connection('JohtoCherrygroveAirstrip','JohtoRoute29','right');stage('actual-Route29-entry')
 connection('JohtoRoute29','NewBarkTown','right');stage('actual-NewBark-entry')
 walkto('NewBarkTown',(11,8));assert e.location()[:2]==named('NewBarkTown_ElmsLab'),e.location()
 # Door warp occurs on entry; it may already have transitioned in walkto.
 walkto('NewBarkTown_ElmsLab',(7,9));e.press('UP',hold=1,after=20);e.press('A',hold=2,after=20)
 assert e.u16(syms['gSpecialVar_LastTalked'])==const('LOCALID_NEWBARKTOWN_ELMSLAB_PROFESSORELM')
 idle();assert blocks(e).flag(fs[1]) and not any(blocks(e).flag(f) for f in fs[2:])
 stage('actual-professor-first-visit');report['native_SAVE_cold']=flash_reload(e,'continuous-first-lab');stage('native-SAVE-cold')
 report['pass']=True
except Exception as ex:
 report.update(error=repr(ex),traceback=traceback.format_exc())
 if e and e.h:report['failure_location']=e.location();e.shot(str(out/'failure.png'),scale=3)
finally:
 if e:e.close()
 report['inputs_unchanged']=all(digest(p.read_bytes())==h for p,h in originals.items());emit();print(json.dumps(report),flush=True)
