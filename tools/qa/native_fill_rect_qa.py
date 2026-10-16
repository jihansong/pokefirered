import pathlib,sys
src=pathlib.Path(sys.argv[1]).read_text()
assert ' pristine=e.save_state()' in src
prefix=src.split(' pristine=e.save_state()')[0]
sys.argv=[sys.argv[0],sys.argv[2],sys.argv[3]]
tail=r'''
 import random
 snapshot=e.save_state();rng=random.Random(20261006)
 free_window=next(i for i in range(32) if e.u32(sy['gWindows']+i*12+8)==0)
 window_addr=sy['gWindows']+free_window*12;window_before=e.read(window_addr,12)
 allocation=call('Alloc',32864);assert 0x02000000<=allocation<0x02040000-32864
 cases=[]
 for tw,th in [(1,1),(23,16),(32,32)]:
  pw=tw*8;ph=th*8
  rectangles=[(0,0,pw,2),(0,ph-2,pw,9),(0,7,pw,9),(8,1,24,12),(16,0,8,ph),(pw-8,ph-1,24,2),(pw,0,8,8),(0,ph,8,8),(0,0,0,ph),(0,0,pw,0),(1,3,5,7),(3,5,16,12),(0,1,5,6),(2,3,7,7),(0,ph-1,pw+8,8),(65535,65535,8,8)]
  cases += [(tw,th,xx,yy,ww,hh,color,0) for color in [0,1,15,17,165,255] for xx,yy,ww,hh in rectangles]
 cases += [(23,16,0,7,184,2,color,off) for color in [0,1,17,255] for off in [1,2]]
 def reference(raw,tw,th,xx,yy,ww,hh,color):
  target=bytearray(raw)
  for py in range(yy,min(yy+hh,th*8)):
   for px in range(xx,min(xx+ww,tw*8)):
    pos=(px>>3)*32+(py>>3)*tw*32+(py&7)*4+((px&7)>>1)
    if px&1:target[pos]=(target[pos]&15)|((color<<4)&255)
    else:target[pos]=(target[pos]&240)|color
  return bytes(target)
 try:
  for case,(tw,th,xx,yy,ww,hh,color,off) in enumerate(cases):
   size=tw*th*32;original=rng.randbytes(size)
   expected=reference(original,tw,th,xx,yy,ww,hh,color)
   left=bytes([0xA5])*(32+off);right=bytes([0x5A])*32
   e.write(allocation,left+original+right)
   e.write(window_addr,struct.pack('<6BHI',255,0,0,tw,th,0,0,allocation+32+off))
   call('FillWindowPixelRect',free_window,color,xx,yy,ww,hh)
   assert e.read(allocation+32+off,size)==expected,('fill bytes',case,tw,th,xx,yy,ww,hh,color,off)
   assert e.read(allocation,32+off)==left and e.read(allocation+32+off+size,32)==right,('fill guard',case)
  assert len(cases)==296
  emit('native_fill_bytes',dict(cases=len(cases),byte_equal=True,clipping=True,unaligned_fallback=True,guards=True))
 finally:
  e.write(window_addr,window_before);call('Free',allocation);e.load_state(snapshot)
after=saves();after[str(sav)]=h(sav.read_bytes());assert after==old
emit('original_saves_preserved',True)
'''
exec(compile(prefix+tail,'native-fill-qa','exec'))
