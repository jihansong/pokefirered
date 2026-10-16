import pathlib
base=pathlib.Path('outputs/regional-dex-story-v1/regional_ui_qa.py').read_text().split(' pristine=e.save_state()')[0].replace('for _ in range(20):','for _ in range(900):')
tail=r'''
 pristine=e.save_state()
 def mons(raw,start,stride,count):
  bad=[]
  for i in range(count):
   q=raw[start+i*stride:start+i*stride+80];pid,ot=struct.unpack_from('<II',q);key=pid^ot;secure=struct.pack('<12I',*[x^key for x in struct.unpack_from('<12I',q,32)]);want=struct.unpack_from('<H',q,28)[0];got=sum(struct.unpack('<24H',secure))&65535
   if q[19]&1 or want!=got:bad.append(dict(index=i,record_sha=h(q),stored=want,calculated=got,flags=q[19]))
  return bad
 def payloads(raw,sz):
  assert len(raw)==131072;groups={}
  for i in range(28):
   q=raw[i*4096:(i+1)*4096];sid,cs,magic,counter=struct.unpack_from('<HHII',q,4084);assert sid<14 and magic==0x08012025,('save footer',i,sid,hex(magic));size=sz[sid];sm=sum(struct.unpack('<'+'I'*(size//4),q[:size]))&0xffffffff;assert ((sm>>16)+sm)&65535==cs,('section checksum',i,sid);assert sid not in groups.setdefault(counter,{});groups[counter][sid]=q[:size]
  complete={k:v for k,v in groups.items() if set(v)==set(range(14))};assert len(complete)==2,('incomplete slots',list(groups));return complete[max(complete)],sorted(complete)
 sz=[e.u16(sy['sSaveSlotLayout']+i*4+2) for i in range(14)];assert sz==[3876,3968,3968,3968,3816]+[3968]*8+[2000],sz
 original_pc=e.read(e.ptr('gPokemonStoragePtr'),33744);original_party=e.read(sy['gPlayerParty'],600);original_dex=e.read(e.ptr('gSaveBlock2Ptr')+0x18,120);known_bad=mons(original_pc,4,80,420);party_bad=mons(original_party,0,100,e.u8(sy['gPlayerPartyCount']));assert not party_bad,party_bad
 emit('copied_save_before',dict(box_records=420,box_bad=known_bad,party_bad=party_bad,save_layout=sz))
 for r in range(3):
  e.load_state(pristine);region(r);assert e.read(e.ptr('gPokemonStoragePtr'),33744)==original_pc;assert e.read(sy['gPlayerParty'],600)==original_party;assert e.read(e.ptr('gSaveBlock2Ptr')+0x18,120)==original_dex;assert pathlib.Path(e.sav_path).resolve()!=sav
  assert call('TrySavingData',0)==1,'native save failed';e.run(30);e.lib.qa_close(e.h);e.h=None;written=pathlib.Path(e.sav_path).read_bytes();slot,counters=payloads(written,sz);pc=b''.join(slot[i] for i in range(5,14));sb1=b''.join(slot[i] for i in range(1,5))
  assert pc==original_pc,'stored PC changed';assert sb1[56:656]==original_party,'stored party changed';assert slot[0][0x18:0x90]==original_dex,'stored dex record changed';assert mons(pc,4,80,420)==known_bad,'Bad Egg set changed'
  e.h=e.lib.qa_open(str(rom).encode(),str(e.sav_path).encode());assert e.h;e.boot_continue();e.run(30);assert call('GetStoryRegionalDex')==r,'story profile lost after reload';assert e.read(e.ptr('gPokemonStoragePtr'),33744)==original_pc;assert e.read(sy['gPlayerParty'],600)==original_party;assert e.read(e.ptr('gSaveBlock2Ptr')+0x18,120)==original_dex
  call('CB2_OpenPokedexFromStartMenu');p=wait('Task_PokedexScreen',6);assert e.u8(p+110)==r
  emit('native_save_reload',dict(profile=r,valid_slots=2,counters=counters,pc_records_preserved=420,party_records_preserved=e.u8(sy['gPlayerPartyCount']),dex_records_unchanged=True,existing_bad_egg_unchanged=known_bad,pass_all=True))
 e.load_state(pristine)
emit('save_compat_complete',True)
'''
assert 'def number' in base;exec(compile(base+tail,'regional_save_compat','exec'))
