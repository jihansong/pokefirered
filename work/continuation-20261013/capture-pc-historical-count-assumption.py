from pathlib import Path
import ast,hashlib,json,struct,ctypes,traceback
q=Path('tools/qa/native_misty_basic_qa.py').read_text()
assert hashlib.sha256(q.encode()).hexdigest()=='5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6'
exec(compile(q.split('\nresults=[];rows=[]\n')[0],'<verified-native-definitions>','exec'))
node=next(n for n in ast.parse(Path('tools/qa/eventcheck.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='throw_ball')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<verified-ball-key-controller>','exec'))
gd.FIELDS['pokemon.level']=('Pokemon','level');gd._OFFSETS=None
wait_action_menu=lambda e,rom:menu(e)
live_blocks=blocks
item_name=gd.item_name
protected={p:digest(p.read_bytes()) for p in Path('saves').rglob('*.sav')}
status={'pass':False,'arbitrary_RAM_writes':0,'direct_script_calls':0,'forced_battle_outcomes':0,'rom_sha256':digest(rom.read_bytes()),'scope':'Native full-party static wild capture to PC; game SAVE/cold vs same-ROM raw core state restore. Capture to PC and native SAVE/cold on f31 edited v1.25. PC UI is a following separate linked checkpoint.','stages':[]}
assert digest(rom.read_bytes())=='f31b2eea1ae45fd1dd40057c80510a8875936394e5807d00806a90cff1dee73d'
assert digest(sav.read_bytes())=='158e50e370b290fccec6e8a09dda79001cab312c5ebe4de31ee245bb846ecef5'
O='FLAG_JOHTO_SUDOWOODO_CLEARED';W='FLAG_JOHTO_SQUIRTBOTTLE_RECEIVED'
def rows(boxes):
 result={}
 for i in range(420):
  raw=boxes[i*80:(i+1)*80];pid,ot=struct.unpack_from('<II',raw)
  if pid or ot:result[i]=raw
 return result
def monprofile(raw):
 m=Mon(bytearray(raw),0);sub=m.subs();calc=sum(x[0] for z in sub.values() for x in struct.iter_unpack('<H',z))&65535
 return {'pid':m.personality,'ot':m.otid,'species':m.species(),'checksum_valid':calc==struct.unpack_from('<H',raw,28)[0],'bad_egg':bool(raw[19]&1),'is_egg':bool(raw[19]&4),'has_species':m.has_species(),'met_level':sub['M'][2]&127,'experience_hex':bytes(sub['G'][4:8]).hex(),'raw_sha256':digest(raw)}
def boxdata(e):return e.read(e.ptr('gPokemonStoragePtr')+off('storage.boxes'),420*80)
def initial(e):
 b=blocks(e);party=e.read(e.ptr('gSaveBlock1Ptr')+off('sb1.playerParty'),600)
 return {'party_count':e.u8(e.sym('gPlayerPartyCount')),'party_identity':identity(party,6),'pc_rows':rows(boxdata(e)),'dex':[b.dex_state(i) for i in range(1,387)]}
def verify(e,tag):
 safe(e);assert e.field_idle()
 now=initial(e);assert now['party_count']==6 and now['party_identity']==baseline['party_identity']
 for i,raw in baseline['pc_rows'].items():assert now['pc_rows'].get(i)==raw,('existing boxed record changed',tag,i)
 added={i:raw for i,raw in now['pc_rows'].items() if i not in baseline['pc_rows']}
 assert len(now['pc_rows'])==120 and len(added)==1,(tag,len(now['pc_rows']),list(added))
 slot,raw=next(iter(added.items()));mp=monprofile(raw)
 assert mp['checksum_valid'] and not mp['bad_egg'] and not mp['is_egg'] and mp['has_species']
 assert mp['species']==const('SPECIES_SUDOWOODO') and mp['pid']==enemy_pid and mp['experience_hex']==enemy_exp and mp['met_level']==20
 assert mp['ot']==player_ot
 if captured:assert (slot,raw)==captured[0]
 else:captured.append((slot,raw))
 for old,new in zip(baseline['dex'],now['dex']):assert all((not a) or z for a,z in zip(old,new)),('Dex bit lost',tag)
 assert all(now['dex'][184]) and blocks(e).flag(O) and blocks(e).item_count('ITEM_MASTER_BALL')==98
 row={'stage':tag,'party_count':6,'original_box_records_unchanged':119,'new_slot':slot,'new_pokemon':mp,'pointer':hex(e.ptr('gPokemonStoragePtr')),'same_original_bad_egg_retained':True,'location':e.location()}
 status['stages'].append(row);emit();return row
def emit(): (out/'validation.json').write_text(json.dumps(status,indent=2)+'\n')
def finish(e):
 for _ in range(1200):
  safe(e)
  if e.field_idle():return
  e.press('B',hold=2,after=14)
 raise AssertionError('Capture/nickname dialogue did not release to field')
e=None
captured=[]
try:
 f=out/'capture-before-QA-only.sav';assert not f.exists();s=SaveFile(str(sav));assert s.party_count()==6
 s.set_flag(W,True);s.set_flag(O,False);assert s.item_count('ITEM_MASTER_BALL')==99;s.set_var('VAR_REPEL_STEP_COUNT',250)
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 s.sb2[off('sb2.specialSaveWarpFlags')]&=~1;s.warp('JohtoRoute36',25,9);s.save(str(f))
 fixture_sha=digest(f.read_bytes());status['preboot_fixture_changes']=['Position/quest log','SquirtBottle story flag true and Sudowoodo clear false','Master Ball 99 unchanged until actual capture','Repel250']
 e=ReadOnlyEmu(str(rom),str(f),sym='');e.syms=syms;e.boot_continue();settle(e);e.run(60)
 baseline=initial(e);assert baseline['party_count']==6 and len(baseline['pc_rows'])==119
 assert sum(not monprofile(raw)['checksum_valid'] or monprofile(raw)['bad_egg'] for raw in baseline['pc_rows'].values())==1
 player_ot=struct.unpack_from('<I',blocks(e).sb2,off('sb2.playerTrainerId'))[0]
 e.press('UP',hold=1,after=20);e.press('A',hold=3,after=12);mash_until(e,e.in_battle,300);assert menu(e)
 assert not e.u32(e.sym('gBattleTypeFlags'))&const('BATTLE_TYPE_TRAINER')
 enemy=e.read(e.sym('gEnemyParty'),100);em=Mon(bytearray(enemy),0)
 assert em.species()==const('SPECIES_SUDOWOODO') and enemy[off('pokemon.level')]==20
 enemy_pid=em.personality;enemy_exp=bytes(em.subs()['G'][4:8]).hex()
 e.shot(str(out/'native-wild-before-capture.png'),scale=3)
 assert throw_ball(e,str(rom),'ITEM_MASTER_BALL',None) is None
 finish(e);assert e.u8(e.sym('gBattleOutcome'))==const('B_OUTCOME_CAUGHT')
 verify(e,'capture-to-PC');e.shot(str(out/'native-capture-PC-message-field.png'),scale=3)
 status['native_save_cold']=flash_reload(e,'capture-PC');verify(e,'native-SAVE-cold')
 status['capture_flash']=e.sav_path
 status['new_bad_egg_observed']=False;status['pass']=True
except Exception as ex:
 status.update(error=repr(ex),traceback=traceback.format_exc())
 if e and e.h:e.shot(str(out/'failure.png'),scale=3)
finally:
 if e:e.close()
 status.update(original_all_SAVs_unchanged=all(digest(p.read_bytes())==h for p,h in protected.items()),original_inputs_unchanged=all(digest(p.read_bytes())==h for p,h in originals.items()),original_v12_hash=digest(sav.read_bytes()),current_ROM_unchanged=digest(rom.read_bytes())==status['rom_sha256'])
 emit();print(json.dumps({k:v for k,v in status.items() if k!='stages'}),flush=True)
