import pathlib,sys
src=pathlib.Path(sys.argv[1]).read_text();marker=' pristine=e.save_state()'
assert marker in src
prefix=src.split(marker)[0];sys.argv=[sys.argv[0],sys.argv[2],sys.argv[3]]
tail=r''' snap=e.save_state();checked=0
 try:
  lut=sy['sFontHalfRowLookupTable'];fg=sy['sLastTextFgColor'];bg=sy['sLastTextBgColor'];sh=sy['sLastTextShadowColor']
  assert S+208<=0x02040000
  e.write(lut,bytes(162))
  for q in (fg,bg,sh):e.write(q,b'\0\0')
  offsets=e.read(sy['sFontHalfRowOffsets'],256)
  assert offsets==bytes(sum((((b>>(2*j))&3)%3)*3**j for j in range(4)) for b in range(256)),'halfrow mapping'
  patterns=[(0,0,0),(1,0,3),(15,0,14),(1,2,3),(1,0,3),(0,15,0),(7,7,7),(255,17,165),(0,0,0)]
  for f,bgcolor,s in patterns:
   colors=(bgcolor,f,s)
   expected=struct.pack('<81H',*((((colors[l]<<12)|(colors[k]<<8)|(colors[j]<<4)|colors[i])&65535) for i in range(3) for j in range(3) for k in range(3) for l in range(3)))
   for repeat in range(2):
    call('GenerateFontHalfRowLookupTable',f,bgcolor,s)
    assert e.read(lut,162)==expected,('lookup',f,bgcolor,s,repeat)
    assert (e.u16(fg),e.u16(bg),e.u16(sh))==(f,bgcolor,s)
   def expand(byte):
    return ((colors[(byte&3)%3]<<12)|(colors[((byte>>2)&3)%3]<<8)|(colors[((byte>>4)&3)%3]<<4)|colors[((byte>>6)&3)%3])&65535
   for start in range(0,256,16):
    seq=list(range(start,start+16));source=struct.pack('<8H',*((seq[i]<<8)|seq[i+1] for i in range(0,16,2)))
    expectedPixels=struct.pack('<16H',*(expand(x) for x in seq))
    e.write(S+128,source);e.write(S+152,b'\xa5'*8+b'\xcc'*32+b'\x5a'*8)
    call('DecompressGlyphTile',S+128,S+160)
    assert e.read(S+160,32)==expectedPixels,('decompress',f,bgcolor,s,start)
    assert e.read(S+152,8)==b'\xa5'*8 and e.read(S+192,8)==b'\x5a'*8
    assert e.read(S+128,16)==source
    checked+=1
  emit('font_palette_cache_native',dict(cases=checked,repeated_color_calls=18,all_256_halfrow_patterns=True,initial_bss_zero=True,bytes_and_guards=True))
 finally:e.load_state(snap)
after=saves();after[str(sav)]=h(sav.read_bytes());assert after==old
emit('original_saves_preserved',True)
'''
exec(compile(prefix+tail,'font_palette_cache_qa','exec'))
