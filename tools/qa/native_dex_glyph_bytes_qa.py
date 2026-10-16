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
 buf=call('Alloc',size+160);assert 0x02000000<=buf<0x02040000-size-160
 printer=buf+size+96;gp=sy['gGlyphInfo'];gb=e.read(gp,130)
 shapes=[(1,1),(5,8),(6,12),(7,14),(8,8),(8,16),(9,9),(16,16)]
 cases=[(w,h,x,y,0,'phase') for w,h in shapes for x in range(8) for y in range(8)]
 edges=[(183,127),(184,1),(1,128),(185,129),(177,121),(178,122),(180,125),(181,124)]
 cases += [(w,h,x,y,0,'edge') for w,h in [(1,1),(7,14),(9,9),(16,16)] for x,y in edges]
 cases += [(w,h,3,5,off,'fallback') for w,h in [(1,1),(7,14),(9,9),(16,16)] for off in [1,2]]
 def reference(raw,g,w,h,x,y):
  q=bytearray(raw)
  for row in range(max(0,min(h,128-y))):
   for col in range(max(0,min(w,184-x))):
    a=(col>>3)*32+(row>>3)*64+(row&7)*4+((col&7)>>1)
    v=(g[a]>>(4*(col&1)))&15
    if v:
     X=x+col;Y=y+row;b=(X>>3)*32+(Y>>3)*23*32+(Y&7)*4+((X&7)>>1)
     shift=(X&1)*4;q[b]=(q[b]&~(15<<shift))|(v<<shift)
  return bytes(q)
 totals={'phase':0,'edge':0,'fallback':0}
 try:
  for number,(glyph_width,height,x,y,off,label) in enumerate(cases):
   raw=rng.randbytes(size);g=bytes(128) if number%4==0 else rng.randbytes(128)
   expected=reference(raw,g,glyph_width,height,x,y);left=bytes([0xA5])*(32+off);right=bytes([0x5A])*32
   e.write(buf,left+raw+right)
   e.write(wa,struct.pack('<6BHI',255,0,0,23,16,0,0,buf+32+off))
   template=bytearray(36);template[4]=slot;template[8]=x;template[9]=y
   e.write(printer,template);e.write(gp,g+bytes([glyph_width,height]))
   call('CopyGlyphToWindow',printer)
   assert e.read(buf+32+off,size)==expected,('glyph bytes',number,glyph_width,height,x,y,off)
   assert e.read(buf,32+off)==left and e.read(buf+32+off+size,32)==right,('glyph guard',number)
   assert e.read(printer,36)==bytes(template) and e.read(gp,130)==g+bytes([glyph_width,height]),'glyph input mutation'
   totals[label]+=1
  assert totals=={'phase':512,'edge':32,'fallback':8}
  emit('native_glyph_bytes',dict(cases=totals,byte_equal=True,transparency=True,clipping=True,guards=True))
 finally:
  e.write(wa,wb);e.write(gp,gb);call('Free',buf);e.load_state(snap)
after=saves();after[str(sav)]=h(sav.read_bytes());assert after==old
emit('original_saves_preserved',True)
'''
exec(compile(prefix+tail,'native-glyph-qa','exec'))
