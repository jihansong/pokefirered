from pathlib import Path
import sys,json,struct,hashlib,shutil,collections,datetime
r=Path('/workspaces/pokefirered');sys.path.insert(0,str(r/'tools/qa'))
from savefile import SaveFile,Mon,checksum,SIGNATURE
from gamedata import off,const,Rom
out=r/'work/save-edit-v125-20261013';out.mkdir(exist_ok=True)
src=r/'saves/pokemonthyl_v1.25.sav'
sha=lambda x:hashlib.sha256(x).hexdigest()
original=src.read_bytes();expected='53d923bf4668373724b19c9d3c8526b002701606ab7ac082d657ee990e23d7b3'
assert sha(original)==expected,'Input changed, stop'
backup=out/'pokemonthyl_v1.25-original.sav'
if backup.exists():assert backup.read_bytes()==original
else:backup.write_bytes(original)
s=SaveFile(str(src));rom=Rom(str(r/'pokemonthyl.gba'))
before={k:bytes(v) for k,v in s.blocks.items()}
targets={const('SPECIES_'+x):x for x in ['BLASTOISE','VENUSAUR','CHARIZARD','DRAGONAIR']}
def allmons(z):
 for i in range(z.party_count()):yield 'party',i,z.party_mon(i),100
 for i in range(420):
  m=Mon(z.blocks['storage'],off('storage.boxes')+i*80)
  if m.has_species():yield 'box',i,m,80
def valid(m):
 dec=b''.join(m.subs()[c] for c in 'GAEM')
 return (sum(v[0] for v in struct.iter_unpack('<H',dec))&65535)==struct.unpack_from('<H',m.blk,m.o+28)[0]
def inv(z):
 res=collections.Counter()
 for item in ['ITEM_POTION','ITEM_BICYCLE','ITEM_MASTER_BALL','ITEM_TM05','ITEM_ORAN_BERRY']:
  for o in z._slots(item):
   iid,q=struct.unpack_from('<HH',z.sb1,o)
   if iid:res[iid]+=q^(z._key()&65535)
 return dict(res)
items_before=inv(s);allowed_sb1=set();allowed_storage=set();ledger=[];bad_before=[]
for place,i,m,size in allmons(s):
 raw=bytes(m.blk[m.o:m.o+size])
 if not valid(m):bad_before.append({'place':place,'index':i,'sha256':sha(raw[:80]),'species':m.species()})
 if m.species() not in targets:continue
 assert valid(m) and not (raw[19]&1) and not m.is_egg(),'Damaged/egg target; stop'
 subs=m.subs();bsubs={k:bytes(v) for k,v in subs.items()};word=struct.unpack_from('<I',subs['M'],4)[0]
 ivs=[(word>>(5*k))&31 for k in range(6)];newivs=[min(31,v*2) for v in ivs]
 newword=(word&0xc0000000)|sum(v<<(5*k) for k,v in enumerate(newivs))
 struct.pack_into('<I',subs['M'],4,newword);m.put_subs(subs)
 row={'place':place,'index':i,'name':targets[m.species()],'pid':m.personality,'ot':m.otid,'iv_before':ivs,'iv_after':newivs,'ev':list(subs['E'][:6]),'experience':struct.unpack_from('<I',subs['G'],4)[0],'nature':m.personality%25,'base':rom.species_info(m.species())['base']}
 if place=='party':
  level=m.level();info=rom.species_info(m.species());growth=info['growthRate'];xp=row['experience']
  assert rom.exp_for_level(growth,level)<=xp and (level==100 or xp<rom.exp_for_level(growth,level+1)),'Cached level disagrees with experience'
  oldstats=list(struct.unpack_from('<7H',raw,86));base=info['base'];ev=row['ev'];nature=row['nature'];up,down=nature//5,nature%5
  stats=[(2*base[0]+newivs[0]+ev[0]//4)*level//100+level+10]
  for k in range(1,6):
   v=(2*base[k]+newivs[k]+ev[k]//4)*level//100+5
   if up!=down:
    if k-1==up:v=v*110//100
    elif k-1==down:v=v*90//100
   stats.append(v)
  hp=0 if oldstats[0]==0 else oldstats[0]+stats[0]-oldstats[1]
  assert 0<=hp<=stats[0]
  struct.pack_into('<7H',m.blk,m.o+86,hp,*stats)
  row.update(level=level,stats_before=oldstats,stats_after=[hp,*stats])
 after=bytes(m.blk[m.o:m.o+size]);after_sub=m.subs()
 assert raw[:28]==after[:28] and raw[30:32]==after[30:32]
 for k in 'GAE':assert bsubs[k]==bytes(after_sub[k])
 assert bsubs['M'][:4]==bytes(after_sub['M'][:4]) and bsubs['M'][8:]==bytes(after_sub['M'][8:])
 assert word&0xc0000000==struct.unpack_from('<I',after_sub['M'],4)[0]&0xc0000000
 assert valid(m)
 if place=='party':assert raw[80:86]==after[80:86]
 allowed=allowed_sb1 if place=='party' else allowed_storage
 allowed.update(range(m.o+28,m.o+30));allowed.update(range(m.o+32,m.o+80))
 if place=='party':allowed.update(range(m.o+86,m.o+100))
 row['header_before']=raw[:32].hex();row['header_after']=after[:32].hex();row['sub_before']={k:v.hex() for k,v in bsubs.items()};row['sub_after']={k:bytes(v).hex() for k,v in after_sub.items()}
 ledger.append(row)
for item in ['ITEM_MASTER_BALL','ITEM_RARE_CANDY']:
 allowed_sb1.update(n for o in s._slots(item) for n in range(o,o+4));s.set_item(item,99)
afterinv=inv(s);expectedinv=dict(items_before)
for item in ['ITEM_MASTER_BALL','ITEM_RARE_CANDY']:expectedinv[const(item)]=99
assert afterinv==expectedinv
assert bytes(s.sb2)==before['sb2']
for key,allowed in [('sb1',allowed_sb1),('storage',allowed_storage)]:
 diffs={i for i,(a,b) in enumerate(zip(before[key],s.blocks[key])) if a!=b}
 assert diffs<=allowed,(key,sorted(diffs-allowed))
candidate=out/'pokemonthyl_v1.25-items99-iv2x.sav';s.save(str(candidate))
reload=SaveFile(str(candidate));assert reload.slot==s.slot and reload.counter==s.counter
for k in before:assert reload.blocks[k]==s.blocks[k]
bad_after=[{'place':place,'index':i,'sha256':sha(bytes(m.blk[m.o:m.o+80])),'species':m.species()} for place,i,m,size in allmons(reload) if not valid(m)]
assert bad_after==bad_before
for name,sid,size in reload.layout:
 phys=reload.where[sid];raw=reload.raw[phys*4096:(phys+1)*4096]
 assert struct.unpack_from('<H',raw,0xff6)[0]==checksum(raw[:size])
 assert struct.unpack_from('<I',raw,0xff8)[0]==SIGNATURE
assert src.read_bytes()==original and len(candidate.read_bytes())==len(original)
manifest={'input':str(src),'input_sha256':sha(original),'backup':str(backup),'candidate':str(candidate),'candidate_sha256':sha(candidate.read_bytes()),'rom_sha256':sha(rom.data),'bytes':len(original),'items_before':{x:SaveFile(str(src)).item_count(x) for x in ['ITEM_MASTER_BALL','ITEM_RARE_CANDY']},'items_after':{x:reload.item_count(x) for x in ['ITEM_MASTER_BALL','ITEM_RARE_CANDY']},'matches':ledger,'missing_species':[n for sid,n in targets.items() if not any(x['name']==n for x in ledger)],'known_corrupt_unchanged':bad_after,'non_target_blocks_preserved':True,'sb2_preserved':True,'all_non_target_records_preserved':True,'active_sector_checksums_valid':14,'inactive_bank_preserved':True,'counter_before_after':[s.counter,reload.counter],'hp_policy':'native CalculateMonStats maxHP delta; fainted zero preserved','native_verified':False}
for place,i,m,size in allmons(reload):
 if any(x['place']==place and x['index']==i for x in ledger):continue
 oldblk=before['sb1' if place=='party' else 'storage']
 assert bytes(m.blk[m.o:m.o+size])==oldblk[m.o:m.o+size]
slot=s.slot
assert candidate.read_bytes()[(1-slot)*14*4096:(2-slot)*14*4096]==original[(1-slot)*14*4096:(2-slot)*14*4096]
(out/'edit-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'candidate':str(candidate),'sha256':manifest['candidate_sha256'],'items':manifest['items_after'],'matches':[{'name':x['name'],'ivs_before':x['iv_before'],'ivs_after':x['iv_after'],'hp_stats_before':x.get('stats_before'),'hp_stats_after':x.get('stats_after')} for x in ledger],'missing':manifest['missing_species'],'corrupt_unchanged':bad_after,'pass':True}))
