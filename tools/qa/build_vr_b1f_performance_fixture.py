import hashlib,json,pathlib,struct,sys
from savefile import SaveFile
from gamedata import const,off,map_info,Rom
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def preserved(s):
 assert off('pokemon')==100 and len(s.blocks['storage'])==33744,'save ABI changed'
 o=off('sb1.playerParty');party=bytes(s.sb1[o:o+600])
 dex=bytes(int(v) for n in range(1,387) for v in s.dex_state(n))
 f=off('sb1.flags');end=off('sb1.vars');n=end-f
 assert 0<n and end<=len(s.sb1),'compiled story flag span invalid'
 sb2=bytearray(s.sb2);sb2[off('sb2.specialSaveWarpFlags')]&=~1
 return party,s.party_count(),bytes(s.blocks['storage']),dex,bytes(s.sb1[f:f+n]),bytes(sb2)
base,rom,out=map(pathlib.Path,sys.argv[1:4]);source_sha=sha(base);reference=SaveFile(str(base));before=preserved(reference)
starters=[]
for slot in range(reference.party_count()):
 m=reference.party_mon(slot);raw=bytes(m.blk[m.o:m.o+100])
 if m.species()==const('SPECIES_PIKACHU') and m.starter_bit() and not m.is_egg() and struct.unpack_from('<H',raw,86)[0]>0:
  assert not raw[19]&1,'starter is flagged Bad Egg'
  subs=m.subs();checksum=sum(struct.unpack('<24H',b''.join(subs[k] for k in 'GAEM')))&65535
  assert checksum==struct.unpack_from('<H',raw,28)[0],'starter checksum mismatch'
  starters.append(dict(slot=slot,personality=m.personality,otid=m.otid,box_sha256=hashlib.sha256(raw[:80]).hexdigest(),party_sha256=hashlib.sha256(raw).hexdigest()))
assert len(starters)==1 and (starters[0]['personality'],starters[0]['otid'])==(3742077845,2839214970),'original genuine starter not found'
assert reference.flag('FLAG_RECEIVED_STARTER_PIKACHU'),'original starter follower flag absent; do not change story flags for this QA'
# Read the exact candidate's three native encounter tables using the same
# 20/8/4-byte ARM layout already checked by audit_wild_header_regions.py.
assert rom.is_file() and rom.with_suffix('.elf').is_file() and rom.with_suffix('.sym').is_file()
r=Rom(str(rom));mi=map_info('VictoryRoad_B1F');pair=(mi['group'],mi['num'])
assert len(mi['json']['object_events'])==21,'original 14 B1F obstacles are not restored in source'
lead=None
for slot in range(reference.party_count()):
 m=reference.party_mon(slot);raw=bytes(m.blk[m.o:m.o+100])
 if struct.unpack_from('<H',raw,86)[0]>0 and not m.is_egg():
  assert not raw[19]&1,'native Repel lead is Bad Egg'
  actual=sum(struct.unpack('<24H',b''.join(m.subs()[k] for k in 'GAEM')))&65535
  assert actual==struct.unpack_from('<H',raw,28)[0],'native Repel lead checksum mismatch'
  lead={'slot':slot,'level':raw[84],'personality':m.personality,'otid':m.otid};break
assert lead and lead['level']>0,'no eligible original Repel lead; do not edit party'
encounters=[]
for table in ['gWildMonHeaders','gWildMonHeadersMorning','gWildMonHeadersNight']:
 assert table in r.syms,('candidate native encounter table missing',table)
 address=r.syms[table];found=[];ended=False
 for i in range(1024):
  raw=r.at(address+i*20,20);assert len(raw)==20,'wild table ROM bounds'
  g,n=raw[:2]
  if (g,n)==(255,255):ended=True;break
  if (g,n)!=pair:continue
  land=struct.unpack_from('<I',raw,4)[0]
  assert land and land%4==0,'native B1F land header missing'
  info=r.at(land,8);assert len(info)==8 and info[0]>0,'native land info bounds/rate'
  mons=struct.unpack_from('<I',info,4)[0];assert mons%2==0
  slots=r.at(mons,12*4);assert len(slots)==48,'native land slots ROM bounds'
  maximum=max(slots[j*4+1] for j in range(12))
  assert all(0<slots[j*4]<=slots[j*4+1]<=100 for j in range(12))
  found.append({'table':table,'maximum_level':maximum,'native_rate':info[0]})
 assert ended and len(found)==1,('native B1F wild header must be unique',table,found)
 encounters.extend(found)
assert all(lead['level']>q['maximum_level'] for q in encounters),'Repel does not guarantee no encounters; keep original party and report blocker'

out.mkdir(parents=True,exist_ok=False);cases=[]
for name,x,y in (('VictoryRoad_B1F',25,7),):
 s=SaveFile(str(base))
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 s.set_var('VAR_REPEL_STEP_COUNT',250);s.set_var('VAR_HAPPINESS_STEP_COUNTER',0);s.warp(name,x,y)
 assert preserved(s)==before,'fixture edits touched original Pokemon/dex/story flags'
 p=out/(name+'-performance.sav');s.save(str(p))
 assert preserved(SaveFile(str(p)))==before,'fixture serialization touched original Pokemon/dex/story flags'
 cases.append(dict(map=name,save=p.name,sha256=sha(p)))
assert sha(base)==source_sha,'original source SAV changed'
(out/'fixture-manifest.json').write_text(json.dumps(cases,indent=2))
report=dict(source=str(base.resolve()),source_sha256=source_sha,genuine_starter=starters[0],story_flags_preserved=True,repel=250,happiness_step_counter=0,candidate_rom_sha256=sha(rom),native_repel_lead=lead,native_encounter_tables=encounters,template_count=21,native_object_capacity=16,party_pc_dex_preserved=True,fixtures=cases)
(out/'fixture-provenance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
