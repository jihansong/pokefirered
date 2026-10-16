import pathlib,sys
src=pathlib.Path(sys.argv[1]).read_text()
assert ' pristine=e.save_state()' in src
prefix=src.split(' pristine=e.save_state()')[0]
sys.argv=[sys.argv[0],sys.argv[2],sys.argv[3]]
tail=r'''
 import random
 snap=e.save_state();rng=random.Random(20261006)
 slot=next(i for i in range(32) if e.u32(sy['gWindows']+i*12+8)==0)
 wa=sy['gWindows']+slot*12;wb=e.read(wa,12);size=23*16*32
 buf=call('Alloc',size+64);assert 0x02000000<=buf<0x02040000-size-64
 guard=bytes(range(32));gfx=e.read(sy['gMenuInfoElements_Gfx'],8192)
 table=[struct.unpack('<BBH',e.read(sy['sMenuInfoIcons']+i*4,4)) for i in range(24)]
 def ref(raw,icon,x,y):
  q=bytearray(raw);wid,hei,off=table[icon];src=gfx[off*32:]
  for syy in range(max(0,min(hei,128-y))):
   for sxx in range(max(0,min(wid,184-x))):
    dy=y+syy;dx=x+sxx
    a=((sxx>>1)&3)+(sxx>>3)*32+(syy>>3)*512+(syy&7)*4
    v=(src[a]>>(4*(sxx&1)))&15
    if v:
     b=((dx>>1)&3)+(dx>>3)*32+(dy>>3)*23*32+(dy&7)*4
     shift=4*(dx&1);q[b]=(q[b]&~(15<<shift))|(v<<shift)
  return bytes(q)
 totals={'aligned':0,'unaligned':0,'clipped':0}
 try:
  for icon in range(24):
   cases=[(40 if icon%2==0 else 120,y,'aligned') for y in range(8)]
   cases += [(3,5,'unaligned'),(176,125,'clipped')]
   for x,y,label in cases:
    raw=rng.randbytes(size);want=ref(raw,icon,x,y)
    e.write(buf,guard+raw+guard)
    e.write(wa,struct.pack('<6BHI',255,0,0,23,16,0,0,buf+32))
    call('BlitMenuInfoIcon',slot,icon,x,y)
    assert e.read(buf+32,size)==want,('icon mismatch',icon,x,y)
    assert e.read(buf,32)==guard and e.read(buf+32+size,32)==guard,'icon guard changed'
    totals[label]+=1
  assert totals=={'aligned':192,'unaligned':24,'clipped':24}
  emit('native_icon_bytes',dict(cases=totals,byte_equal=True,transparency_preserved=True,guards_preserved=True))
 finally:
  e.write(wa,wb);call('Free',buf);e.load_state(snap)
after=saves();after[str(sav)]=h(sav.read_bytes());assert after==old
emit('original_saves_preserved',True)
'''
exec(compile(prefix+tail,'native-icon-qa','exec'))
