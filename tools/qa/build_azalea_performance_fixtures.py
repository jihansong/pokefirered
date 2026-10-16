import hashlib,json,pathlib,struct,sys
from savefile import SaveFile
from gamedata import const,off
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def preserved(s):
 assert off('pokemon')==100 and len(s.blocks['storage'])==33744,'save ABI changed'
 o=off('sb1.playerParty');party=bytes(s.sb1[o:o+600])
 dex=bytes(int(v) for n in range(1,387) for v in s.dex_state(n))
 return party,s.party_count(),bytes(s.blocks['storage']),dex
base,out=map(pathlib.Path,sys.argv[1:3]);source_sha=sha(base);reference=SaveFile(str(base));before=preserved(reference)
starters=[]
for slot in range(reference.party_count()):
 m=reference.party_mon(slot);raw=bytes(m.blk[m.o:m.o+100])
 if m.species()==const('SPECIES_PIKACHU') and m.starter_bit() and not m.is_egg() and struct.unpack_from('<H',raw,86)[0]>0:
  assert not raw[19]&1,'starter is flagged Bad Egg'
  subs=m.subs();checksum=sum(struct.unpack('<24H',b''.join(subs[k] for k in 'GAEM')))&65535
  assert checksum==struct.unpack_from('<H',raw,28)[0],'starter checksum mismatch'
  starters.append(dict(slot=slot,personality=m.personality,otid=m.otid,box_sha256=hashlib.sha256(raw[:80]).hexdigest(),party_sha256=hashlib.sha256(raw).hexdigest()))
assert len(starters)==1 and (starters[0]['personality'],starters[0]['otid'])==(3742077845,2839214970),'original genuine starter not found'
flags=('FLAG_JOHTO_ARRIVAL_BRIEFED','FLAG_JOHTO_MET_LAB_ASSISTANT','FLAG_JOHTO_ELM_REPORT_DELIVERED','FLAG_JOHTO_BADGE01_GET')
original_starter_flag=reference.flag('FLAG_RECEIVED_STARTER_PIKACHU')
out.mkdir(parents=True,exist_ok=False);cases=[]
for name,x,y in (('JohtoRoute32',9,16),('AzaleaTown',18,17)):
 s=SaveFile(str(base))
 for i in range(const('QUEST_LOG_SCENE_COUNT')):s.sb1[off('sb1.questLog')+i*off('questlogscene')]=0
 for flag in flags:s.set_flag(flag,True)
 s.set_flag('FLAG_RECEIVED_STARTER_PIKACHU',True)
 s.set_var('VAR_REPEL_STEP_COUNT',250);s.warp(name,x,y)
 assert preserved(s)==before,'fixture edits touched original Pokemon/dex'
 p=out/(name+'-performance.sav');s.save(str(p))
 assert preserved(SaveFile(str(p)))==before,'fixture serialization touched original Pokemon/dex'
 cases.append(dict(map=name,save=p.name,sha256=sha(p)))
assert sha(base)==source_sha,'original source SAV changed'
(out/'fixture-manifest.json').write_text(json.dumps(cases,indent=2))
report=dict(source=str(base.resolve()),source_sha256=source_sha,genuine_starter=starters[0],original_starter_flag=bool(original_starter_flag),fixture_starter_flag=True,story_flags=list(flags),repel=250,party_pc_dex_preserved=True,fixtures=cases)
(out/'fixture-provenance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
