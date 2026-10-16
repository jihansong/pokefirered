import json,pathlib,struct,sys
from gamedata import off
from savefile import DATA_SIZE,SECTOR_SIZE,SECTORS_PER_SLOT,SIGNATURE,checksum

def audit(raw):
 assert len(raw)==131072,('unexpected flash save size',len(raw))
 assert (off('sb1'),off('sb2'),off('storage'),off('pokemon'))==(15720,3876,33744,100),'save ABI changed'
 sizes={0:off('sb2')}
 for start,name in ((1,'sb1'),(5,'storage')):
  total=off(name)
  for i in range((total+DATA_SIZE-1)//DATA_SIZE):sizes[start+i]=min(DATA_SIZE,total-i*DATA_SIZE)
 assert set(sizes)==set(range(SECTORS_PER_SLOT))
 slots=[]
 for slot in range(2):
  ids=[];counters=[];errors=[]
  for sector in range(SECTORS_PER_SLOT):
   pos=(slot*SECTORS_PER_SLOT+sector)*SECTOR_SIZE
   sid,stored,sig,count=struct.unpack_from('<HHII',raw,pos+0xff4)
   if sig!=SIGNATURE:errors.append(dict(sector=sector,error='signature'));continue
   if sid not in sizes:errors.append(dict(sector=sector,error='sector id',id=sid));continue
   ids.append(sid);counters.append(count)
   actual=checksum(raw[pos:pos+sizes[sid]])
   if actual!=stored:errors.append(dict(sector=sector,id=sid,error='checksum',stored=stored,actual=actual))
  if sorted(ids)!=list(range(SECTORS_PER_SLOT)):errors.append(dict(error='incomplete/duplicate sector ids',ids=ids))
  if len(set(counters))!=1:errors.append(dict(error='inconsistent sector counters',counters=counters))
  slots.append(dict(slot=slot,valid=not errors,counter=counters[0] if counters else None,errors=errors))
 return dict(bytes=len(raw),valid_slots=sum(s['valid'] for s in slots),slots=slots)

if __name__=='__main__':
 p=pathlib.Path(sys.argv[1]);raw=p.read_bytes();result=audit(raw)
 import hashlib
 result.update(path=str(p.resolve()),sha256=hashlib.sha256(raw).hexdigest(),native_load_checked=False,pokemon_checksum_checked=False)
 print(json.dumps(result),flush=True)
 assert result['valid_slots']>0,'no complete checksum-valid save slot'
 if '--both' in sys.argv[2:]:assert result['valid_slots']==2,'full-save roundtrip requires two valid slots'
