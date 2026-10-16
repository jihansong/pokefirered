import hashlib,json,struct,re
from pathlib import Path

def make_step_observer(ec,path):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():raise FileExistsError(path)
 size=ec.off('pokemon');boxsize=ec.off('boxmon')
 count=ec.const('TOTAL_BOXES_COUNT')*ec.const('IN_BOX_COUNT')
 def numeric_define(header,name):
  text=(Path(ec.REPO)/'include/constants'/header).read_text(encoding='utf-8')
  values=re.findall(r'^#define[ \t]+'+re.escape(name)+r'[ \t]+([0-9]+)[ \t]*(?://[^\n]*)?$',text,re.M)
  if len(values)!=1:raise ValueError('Numeric header definition changed: '+name)
  return int(values[0])
 communication=numeric_define('battle_script_commands.h','BATTLE_COMMUNICATION_ENTRIES_COUNT')
 battlers=numeric_define('battle.h','MAX_BATTLERS_COUNT')
 assert size>=100 and boxsize==80 and 1<=count<=4096 and 1<=communication<=64 and battlers==4
 previous=None;serial=0
 def mon(raw):
  raw=bytes(raw);m=ec.Mon(bytearray(raw),0)
  out={'raw':raw.hex(),'flags19':raw[19],'pid':int.from_bytes(raw[:4],'little'),'otid':int.from_bytes(raw[4:8],'little')}
  try:
   sub=m.subs();plain=b''.join(bytes(sub[k]) for k in ('G','A','E','M'))
   checksum=sum(struct.unpack('<24H',plain))&65535
   out.update(species=m.species(),has_species=bool(m.has_species()),egg=bool(m.is_egg()),checksum=checksum,stored_checksum=int.from_bytes(raw[28:30],'little'),checksum_ok=checksum==int.from_bytes(raw[28:30],'little'))
   if len(raw)>=100:out.update(hp=int.from_bytes(raw[86:88],'little'),level=raw[84])
  except Exception as ex:out['decode_error']=repr(ex)
  return out
 def observe(e,step,failures):
  nonlocal previous,serial
  serial+=1;frame=e.frame()
  row={'n':serial,'step':step,'frame':frame,'failures_so_far':list(failures),'callback2':hex(e.callback2()),'battle':e.in_battle(),'field_idle':e.field_idle()}
  missing=[]
  def read(name,n):
   if name not in e.syms:missing.append(name);return None
   return bytes(e.read(e.sym(name),n))
  try:
   for name in ('gEnemyParty','gPlayerParty'):
    raw=read(name,6*size)
    if raw is not None:row[name]={'raw':raw.hex(),'slots':[dict(slot=i,**mon(raw[i*size:(i+1)*size])) for i in range(6)]}
   for name in ('gEnemyPartyCount','gPlayerPartyCount','gAbsentBattlerFlags','gActiveBattler','gBattlerAttacker','gBattlerTarget','gEffectBattler','gBattlersCount','gBattleOutcome','gMultiUsePlayerCursor','gCurrentActionFuncId','gCurrentTurnActionNumber'):
    raw=read(name,1)
    if raw is not None:row[name]=raw[0]
   for name in ('gBattleTypeFlags','gBattleControllerExecFlags','gHitMarker','gBattleMainFunc','gBattlescriptCurrInstr'):
    raw=read(name,4)
    if raw is not None:row[name]=int.from_bytes(raw,'little')
   for name,n,fmt in (('gBattlerPartyIndexes',2*battlers,'<4H'),('gBattlerControllerFuncs',4*battlers,'<4I')):
    raw=read(name,n)
    if raw is not None:row[name]=list(struct.unpack(fmt,raw))
   for name,n in (('gBattleCommunication',communication),('gBattlerPositions',battlers),('gBattlerByTurnOrder',battlers),('gActionsByTurnOrder',battlers),('gChosenActionByBattler',battlers),('gActionSelectionCursor',battlers)):
    raw=read(name,n)
    if raw is not None:row[name]=list(raw)
   for name in ('gStringVar4','gDisplayedStringBattle'):
    raw=read(name,128)
    if raw is not None:
     row[name]={'raw':raw.hex(),'text':ec.decode_text(raw)}
   storage=e.ptr('gPokemonStoragePtr')
   assert 0x02000000<=storage<0x02040000,'Unexpected PC storage pointer'
   assert storage+ec.off('storage.boxes')+count*boxsize<=0x02040000,'PC read exceeds EWRAM'
   pc=bytes(e.read(storage+ec.off('storage.boxes'),count*boxsize))
   slots=[mon(pc[i*boxsize:(i+1)*boxsize]) for i in range(count)]
   row['pc_species']=[m.get('species') for m in slots]
   row['pc_bad_checksums']=[i for i,m in enumerate(slots) if not m.get('checksum_ok',False)]
   row['pc_changed']=[dict(index=i,box=i//ec.const('IN_BOX_COUNT'),slot=i%ec.const('IN_BOX_COUNT'),**m) for i,m in enumerate(slots) if (previous is None and (m.get('has_species') or m.get('species'))) or (previous is not None and pc[i*boxsize:(i+1)*boxsize]!=previous[i*boxsize:(i+1)*boxsize])]
   row['pc_raw_sha256']=hashlib.sha256(pc).hexdigest();previous=pc
   row['master_balls']=ec.live_blocks(e).item_count('ITEM_MASTER_BALL')
  except Exception as ex:
   row['observer_error']=repr(ex)
  assert e.frame()==frame,'Observer advanced the emulator'
  row['missing_symbols']=missing
  with path.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
  if row.get('observer_error'):raise RuntimeError('Step observer failed: '+row['observer_error'])
 return observe
