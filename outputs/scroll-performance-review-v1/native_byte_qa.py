import pathlib,sys
prefix=pathlib.Path('outputs/regional-dex-story-v1/regional_ui_qa.py').read_text().split(' pristine=e.save_state()')[0]
assert 'def call(' in prefix and 'with Emu(' in prefix
tail=r'''
 import random
 rng=random.Random(20261005);snap=e.save_state()
 slot=next(i for i in range(32) if e.u32(sy['gWindows']+i*12+8)==0)
 wa=sy['gWindows']+slot*12;wb=e.read(wa,12)
 buf=call('Alloc',32832)
 assert 0x02000000<=buf<0x02040000-32832,'temporary allocation failed'
 guard=bytes(range(32))
 def ref(raw,width,direction,distance,fill):
  q=bytearray(raw);size=len(q);v=bytes([fill])*4
  if direction not in (0,1):return bytes(q)
  for i in range(0,size,32):
   for j in range(8):
    d=distance+j;src=i+((width*(d&~7)|(d&7))*4);dst=i+j*4
    if direction==0:q[dst:dst+4]=q[src:src+4] if src<size else v
    else:
     dd=size-4-dst;ss=size-4-src
     q[dd:dd+4]=q[ss:ss+4] if src<size else v
  return bytes(q)
 totals={'aligned':0,'unaligned':0,'noop':0}
 try:
  for width,height in ((1,1),(1,32),(23,16),(30,20),(32,32)):
   size=width*height*32
   cases=[(d,n,'aligned') for d in (0,1) for n in range(0,256,8)]
   cases += [(d,n,'unaligned') for d in (0,1) for n in (1,7,9,15,17,31,127,255)]
   cases += [(2,16,'noop')]
   for direction,distance,label in cases:
    raw=rng.randbytes(size);fill=rng.randrange(256);want=ref(raw,width,direction,distance,fill)
    e.write(buf,guard+raw+guard)
    e.write(wa,struct.pack('<6BHI',255,0,0,width,height,0,0,buf+32))
    call('ScrollWindow',slot,direction,distance,fill)
    got=e.read(buf+32,size)
    assert got==want,('ScrollWindow bytes',width,height,direction,distance)
    assert e.read(buf,32)==guard and e.read(buf+32+size,32)==guard,'guard changed'
    totals[label]+=1
  assert totals=={'aligned':320,'unaligned':80,'noop':5}
  emit('native_scroll_bytes',dict(cases=totals,byte_equal=True,guards_preserved=True))
 finally:
  e.write(wa,wb);call('Free',buf);e.load_state(snap)
after=saves();after[str(sav)]=h(sav.read_bytes())
assert after==old,'original SAV changed'
emit('original_saves_preserved',True)
'''
exec(compile(prefix+tail,'native-scroll-qa','exec'))
