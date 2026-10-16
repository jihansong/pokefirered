#!/usr/bin/env python3
"""Cold normal nurse interactions on a fixed candidate; original flash and campaign inputs are immutable."""
from pathlib import Path
import ast,hashlib,json,os,re,struct,subprocess,sys,tempfile
_boot=Path(__file__).with_name('johto_league_native_bootstrap.py');txt=_boot.read_text()
assert hashlib.sha256(txt.encode()).hexdigest()=='474c1ff4a38f7c8b77b8ef4bc826b9762a5a92ba09977a7616ffda6ad5aec136'
exec(compile(txt,str(_boot),'exec'),globals())
gd.FIELDS.update({'pokemon.hp':('Pokemon','hp'),'pokemon.maxHP':('Pokemon','maxHP'),'pokemon.status':('Pokemon','status')})
gd._OFFSETS=None
assert digest(Path('src/union_room.c').read_bytes())=='6d1c4b0a5ed244ccd931732b4f4f21b1e00d473289f2ff5ff44746604ac56350'
gd.FIELDS.update({'sb2.hoennFlags':('SaveBlock2','hoennFlags'),'sb2.hoennTrainerFlags':('SaveBlock2','hoennTrainerFlags')});gd._OFFSETS=None
def flag_sizes():
 expressions=['sizeof(gSaveBlock1Ptr->flags)','sizeof(gSaveBlock2Ptr->hoennFlags)','sizeof(gSaveBlock2Ptr->hoennTrainerFlags)']
 c='#include "global.h"\nconst u32 qa_flag_sizes[] __attribute__((section(".qa_flag_sizes")))={'+','.join(expressions)+'};\n'
 tool=dka/'bin'
 with tempfile.TemporaryDirectory(prefix='n-letter-flags-') as td:
  f=Path(td)/'a.c';o=Path(td)/'a.o';b=Path(td)/'a.bin';f.write_text(c)
  subprocess.run([str(tool/'arm-none-eabi-gcc'),'-c','-w','-mthumb','-mabi=apcs-gnu','-march=armv4t','-fcommon',
   '-iquote','include','-DLEAFGREEN','-DREVISION=0','-DENGLISH','-DMODERN=1','-o',str(o),str(f)],check=True)
  subprocess.run([str(tool/'arm-none-eabi-objcopy'),'-O','binary','-j','.qa_flag_sizes',str(o),str(b)],check=True)
  raw=b.read_bytes()
 assert len(raw)==12
 return struct.unpack('<3I',raw)
FLAG_SIZES=flag_sizes()

_cold_nurse_flag_trace=[]
_cold_nurse_flag_trace_case=''
_cold_nurse_flag_trace_phase=''
_cold_nurse_flag_names={}
for _cold_nurse_header in [Path('include/constants/flags.h'),Path('include/constants/flags_hoenn_story.h'),Path('include/constants/flags_johto_story.h')]:
 for _cold_nurse_name in re.findall(r'^\s*#define\s+(FLAG_[A-Z0-9_]+)\b',_cold_nurse_header.read_text(),re.M):
  try:_cold_nurse_id=const(_cold_nurse_name)
  except (KeyError,ValueError,AssertionError):continue
  _cold_nurse_flag_names.setdefault(_cold_nurse_id,[]).append(_cold_nurse_name)
def _cold_nurse_trace_flags(e,raw):
 index=len(_cold_nurse_flag_trace)
 fname=_cold_nurse_flag_trace_case+'-snapshot-'+str(index)+'-regional-flags.bin'
 (out/fname).write_bytes(raw)
 changes=[]
 previous=bytes.fromhex(_cold_nurse_flag_trace[-1]['regional_flags_hex']) if _cold_nurse_flag_trace else raw
 assert len(previous)==len(raw)
 for byte_index,(old,new)in enumerate(zip(previous,raw)):
  if old==new:continue
  for bit in range(8):
   if (old^new)&(1<<bit):
    flag_id=const('HOENN_FLAGS_START')+byte_index*8+bit
    changes.append({'byte_index':byte_index,'bit':bit,'flag_id':flag_id,'flag_hex':hex(flag_id),
     'names':sorted(set(_cold_nurse_flag_names.get(flag_id,[]))),'before':bool(old&(1<<bit)),'after':bool(new&(1<<bit))})
 row={'case':_cold_nurse_flag_trace_case,'snapshot_index':index,'phase':_cold_nurse_flag_trace_phase,
  'frame':e.frame(),'location':list(e.location()),'callback2':hex(e.callback2()),
  'save_counter':e.u32(syms['gSaveCounter']),'saveblock1_pointer':hex(e.ptr('gSaveBlock1Ptr')),
  'saveblock2_pointer':hex(e.ptr('gSaveBlock2Ptr')),'regional_flags_size':len(raw),
  'regional_flags_sha256':digest(raw),'regional_flags_hex':raw.hex(),'regional_flags_file':fname,
  'differences_from_previous_snapshot':changes}
 try:
  stored=SaveFile(e.sav_path);saved_raw=bytes(stored.sb2[off('sb2.hoennFlags'):off('sb2.hoennFlags')+FLAG_SIZES[1]])
  row['flash_counter']=stored.counter;row['flash_regional_flags_sha256']=digest(saved_raw)
  row['flash_regional_flags_hex']=saved_raw.hex()
  row['flash_native_different_byte_indices']=[i for i,(a,b)in enumerate(zip(saved_raw,raw))if a!=b]
 except Exception as error:row['flash_read_diagnostic_error']=repr(error)
 _cold_nurse_flag_trace.append(row)
 report={'rom_sha256':digest(rom.read_bytes()),'input_save_sha256':digest(sav.read_bytes()),
  'diagnostic_only':True,'all_preservation_assertions_unchanged':True,'snapshots':_cold_nurse_flag_trace}
 (out/(_cold_nurse_flag_trace_case+'-regional-flag-trace-before-assert.json')).write_text(json.dumps(report,indent=2))

_cold_nurse_previous_snapshot=snapshot
def snapshot(e):
 d=_cold_nurse_previous_snapshot(e);b=blocks(e);fs=off('sb1.flags');hf=off('sb2.hoennFlags');ht=off('sb2.hoennTrainerFlags')
 d['full_normal_flags_without_temp']=bytes(b.sb1[fs+4:fs+FLAG_SIZES[0]])
 d['full_hoenn_johto_flags']=bytes(b.sb2[hf:hf+FLAG_SIZES[1]])
 d['full_hoenn_johto_trainers']=bytes(b.sb2[ht:ht+FLAG_SIZES[2]])
 _cold_nurse_trace_flags(e,d['full_hoenn_johto_flags'])
 return d
def normalize_continue_object_flags(s,room):
 # Only these two new/Hoenn rooms use the observed default Briney/Wanda branches.
 assert room in ('JohtoLeague_PokemonCenter_1F','CeruleanCity_PokemonCenter_1F','PetalburgCity_PokemonCenter_1F')
 if room=='CeruleanCity_PokemonCenter_1F':
  assert map_info(room)['group']<map_info('PetalburgCity')['group']
  return {'applied':False,'reason':'original Kanto room is outside Hoenn Continue setup'}
 assert map_info(room)['group']>=map_info('PetalburgCity')['group']
 before_sb1=bytes(s.sb1);before_sb2=bytes(s.sb2)
 before_flags=bytes(s.sb2[off('sb2.hoennFlags'):off('sb2.hoennFlags')+FLAG_SIZES[1]])
 c=Path('src/field_specials.c').read_text()
 matches=list(re.finditer(r'\bHoennZ3_SetupObjectsOnContinue\s*\(\s*void\s*\)\s*\{',c));assert len(matches)==1
 at=matches[0].end();depth=1;end=at
 while depth:
  assert end<len(c),'unterminated Continue setup function'
  depth+=(c[end]=='{')-(c[end]=='}');end+=1
 body=c[at:end-1]
 assert body.count('HoennZ3_SetupObjects();')==1
 pred=r'gSaveBlock1Ptr->location\.mapGroup\s*(<|>=)\s*MAP_GROUP\s*\(\s*MAP_PETALBURG_CITY\s*\)'
 m=re.search(pred,body);assert m,'actual Continue map-group predicate changed'
 if m.group(1)=='<':
  assert re.search(r'if\s*\(\s*'+pred+r'\s*\)\s*(?:\{\s*)?return\s+FALSE\s*;',body)
  assert body.index('HoennZ3_SetupObjects();')>m.end()
 else:
  assert re.search(r'if\s*\(\s*'+pred+r'\s*\)\s*\{\s*HoennZ3_SetupObjects\s*\(\s*\)\s*;',body)
 expected_lines=[
  'SetHideFlag(FLAG_HIDE_HOENN_BIRCH_LAB, birch == 0);',
  'SetHideFlag(FLAG_HIDE_HOENN_RIVAL_ROUTE103, birch != 2);',
  'SetHideFlag(FLAG_HIDE_HOENN_RIVAL_LAB, birch < 3);',
  'SetHideFlag(FLAG_HIDE_HOENN_RUSTBORO_THIEF, !(devon == 1 && FlagGet(FLAG_HOENN_BADGE01_GET)));',
  'SetHideFlag(FLAG_HIDE_HOENN_RUSTURF_GRUNT, devon != 2);',
  'SetHideFlag(FLAG_HIDE_HOENN_RUSTURF_PEEKO, devon != 2 || peeko);',
  'SetHideFlag(FLAG_HIDE_HOENN_BRINEY, !peeko);',
  'SetHideFlag(FLAG_HIDE_HOENN_WALLY_PETALBURG, wally != 1);',
  'SetHideFlag(FLAG_HIDE_HOENN_WALLY_VERDANTURF, wally < 2);',
  'SetHideFlag(FLAG_HIDE_HOENN_WANDA_BOYFRIEND, !FlagGet(FLAG_HOENN_RUSTURF_OPEN));']
 assert all(c.count(line)==1 for line in expected_lines),'continue object formulas changed'
 assert 'SetHideFlag(FLAG_HIDE_HOENN_ROCKET_WOODS, FlagGet(FLAG_HOENN_ROCKET_WOODS)' in c
 assert '|| !HasTrainerBeenFought(TRAINER_HOENN_GRUNT_PETALBURG_WOODS));' in c
 birch=s.var('VAR_HOENN_SCENE_BIRCH');devon=s.var('VAR_HOENN_SCENE_DEVON');wally=s.var('VAR_HOENN_SCENE_WALLY')
 peeko=s.flag('FLAG_HOENN_PEEKO_RESCUED')
 values={
  'FLAG_HIDE_HOENN_BIRCH_LAB':birch==0,
  'FLAG_HIDE_HOENN_RIVAL_ROUTE103':birch!=2,
  'FLAG_HIDE_HOENN_RUSTBORO_THIEF':not(devon==1 and s.flag('FLAG_HOENN_BADGE01_GET')),
  'FLAG_HIDE_HOENN_RUSTURF_GRUNT':devon!=2,
  'FLAG_HIDE_HOENN_RUSTURF_PEEKO':devon!=2 or peeko,
  'FLAG_HIDE_HOENN_BRINEY':not peeko,
  'FLAG_HIDE_HOENN_WALLY_PETALBURG':wally!=1,
  'FLAG_HIDE_HOENN_WALLY_VERDANTURF':wally<2,
  'FLAG_HIDE_HOENN_WANDA_BOYFRIEND':not s.flag('FLAG_HOENN_RUSTURF_OPEN'),
  'FLAG_HIDE_HOENN_ROCKET_WOODS':s.flag('FLAG_HOENN_ROCKET_WOODS') or not s.trainer_beaten('TRAINER_HOENN_GRUNT_PETALBURG_WOODS'),
  'FLAG_HIDE_HOENN_RIVAL_LAB':birch<3}
 for flag,value in values.items():s.set_flag(flag,value)
 mask=bytearray(FLAG_SIZES[1])
 for flag in values:
  bit=const(flag)-const('HOENN_FLAGS_START');assert 0<=bit<len(mask)*8
  mask[bit//8]|=1<<(bit%8)
 after_flags=bytes(s.sb2[off('sb2.hoennFlags'):off('sb2.hoennFlags')+FLAG_SIZES[1]])
 assert bytes(s.sb1)==before_sb1,'visibility preparation changed normal story data'
 assert all(((a^b)&~m)==0 for a,b,m in zip(before_flags,after_flags,mask)),'unexpected regional flag preparation change'
 expected=bytearray(before_sb2);start=off('sb2.hoennFlags');expected[start:start+FLAG_SIZES[1]]=after_flags
 assert bytes(s.sb2)==bytes(expected),'visibility preparation changed SaveBlock2 outside these bits'
 return {'applied':True,'actual_source_formulas':True,'actual_continue_source_sha256':digest(c.encode()),'flags':values,'normal_story_and_all_other_regional_bits_unchanged':True,
  'before_regional_flags_sha256':digest(before_flags),'after_regional_flags_sha256':digest(after_flags),
  'original_source_save_changed':False,'native_save_assertions_unchanged':True}

def prepare(path,room,count):
 s=SaveFile(str(sav));n=s.sb1[off('sb1.playerPartyCount')];assert n==2,'use actual chain SAVE115 with original two partners'
 old_party=bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+600]);old_pc=bytes(s.blocks['storage'])
 if count==6:
  pool=[i for i in range(n)if not s.party_mon(i).is_egg()]
  assert pool
  for i in range(2,6):
   donor=pool[(i-2)%len(pool)];start=off('sb1.playerParty')
   s.sb1[start+i*100:start+(i+1)*100]=old_party[donor*100:(donor+1)*100]
   s.party_mon(i).set_starter_bit(False)
  s.sb1[off('sb1.playerPartyCount')]=6
 assert bytes(s.sb1[off('sb1.playerParty'):off('sb1.playerParty')+200])==old_party[:200]
 assert bytes(s.blocks['storage'])==old_pc
 s._cold_nurse_derived_visibility=normalize_continue_object_flags(s,room)
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 s.set_var('VAR_HAPPINESS_STEP_COUNTER',0);s.warp(room,7,4);s.save(str(path))
 return s
def verify_healing(before,after,label):
 party_identity(before,after,label)
 for i in range(before['party_count']):
  a=before['party'][100*i:100*(i+1)];b=after['party'][100*i:100*(i+1)]
  old=legal_checksum(a,label+' before').subs();new=legal_checksum(b,label+' after').subs()
  assert a[:28]==b[:28],(label,'identity/header bytes changed',i)
  assert all(old[k]==new[k]for k in ['G','E','M']), (label,'non-PP substructure changed',i)
  assert old['A'][:8]==new['A'][:8],(label,'moves changed',i)
  for j in range(4):
   move=struct.unpack_from('<H',new['A'],j*2)[0]
   pp=0 if move==0 else r.at(syms['gBattleMoves']+move*off('battlemove'),off('battlemove'))[4]
   wanted=pp+pp*((new['G'][8]>>(2*j))&3)//5
   assert new['A'][8+j]==wanted,(label,'PP not restored',i,j,new['A'][8+j],wanted)
  assert struct.unpack_from('<I',b,off('pokemon.status'))[0]==0
  assert struct.unpack_from('<H',b,off('pokemon.hp'))[0]==struct.unpack_from('<H',b,off('pokemon.maxHP'))[0]
def attempt(e,room,count,prepared,label):
 global _cold_nurse_flag_trace,_cold_nurse_flag_trace_case,_cold_nurse_flag_trace_phase
 _cold_nurse_flag_trace=[];_cold_nurse_flag_trace_case=label;_cold_nurse_flag_trace_phase='before-native-heal'
 e.syms=syms;e.boot_continue();settle(e);e.run(60);before=snapshot(e)
 assert before['party_count']==count and before['pc']==bytes(prepared.blocks['storage'])
 name_before=e.read(syms['sUnionRoomPlayerName'],12)
 assert name_before==bytes(12) or name_before[0]==255,(label,'unexpected cold name state',name_before.hex())
 tokens={n:e.read(syms[n],24).split(b'\xff')[0]for n in ['Text_RestoredPkmnToFullHealth','Text_WeHopeToSeeYouAgain']}
 seen=set();oldrun=e.run
 def watch(frames=1):
  oldrun(frames);buf=e.sym_read('gStringVar4',256)
  seen.update(n for n,v in tokens.items()if v in buf)
 e.run=watch
 try:native_face(e,'UP');e.press('A',hold=1,after=12);settle(e)
 finally:e.run=oldrun
 assert seen==set(tokens),(label,'nurse completion dialogue missing',seen)
 assert e.field_idle()and e.location()[2:]==(7,4),(label,'nurse did not release valid field')
 _cold_nurse_flag_trace_phase='after-native-heal'
 after=snapshot(e)
 for key in before:
  if key=='party':continue
  assert before[key]==after[key],(label,'unrelated state changed',key)
 verify_healing(before,after,label)
 assert e.read(syms['sUnionRoomPlayerName'],12)[0]==255
 assert e.u8(syms['gQuestLogState'])in(0,1),'quest-log state damaged'
 e.shot(str(out/(label+'.png')),scale=3)
 _cold_nurse_flag_trace_phase='native-SAVE-and-cold-reload';saved=flash_reload(e,label)
 assert snapshot(e)==after,(label,'native SAVE/cold state differs')
 cold_name=e.read(syms['sUnionRoomPlayerName'],12)
 assert cold_name==bytes(12) or cold_name[0]==255,(label,'unexpected name state after cold reset',cold_name.hex())
 return {'case':label,'map':room,'party_count':count,'cold_name_before':name_before.hex(),'actual_heal_pp_hp_status':True,
  'all_party_identities_non_PP_substructures_and_original_two_preserved':True,
  'full_pc_dex_all_normal_and_regional_flags_and_trainers_preserved':True,'native_SAVE_cold':saved,
  'initial_fixture_extra_legal_nonstarter_slot_copies':4 if count==6 else 0,
  'initial_derived_visibility_fixture':prepared._cold_nurse_derived_visibility,'forced_game_memory_writes':0}
cases=[('JohtoLeague_PokemonCenter_1F',2),('JohtoLeague_PokemonCenter_1F',6),
 ('CeruleanCity_PokemonCenter_1F',2),('PetalburgCity_PokemonCenter_1F',6)]
results=[]
try:
 with tempfile.TemporaryDirectory(prefix='cold-nurse-regression-')as td:
  for room,count in cases:
   label='cold_nurse_'+room+'_'+str(count);path=Path(td)/(label+'.sav');prepared=prepare(path,room,count)
   with ReadOnlyEmu(str(rom),str(path),sym='')as e:row=attempt(e,room,count,prepared,label)
   results.append(row);print(json.dumps(row),flush=True)
finally:
 for path,sha in originals.items():assert digest(path.read_bytes())==sha,('original changed',str(path))
assert len(results)==4
(out/'result.json').write_text(json.dumps({'rom_sha256':digest(rom.read_bytes()),'initial_save_sha256':digest(sav.read_bytes()),
 'cases':results,'all_pass':True,'forced_game_memory_writes':0,'original_files_unchanged':True},indent=2))
