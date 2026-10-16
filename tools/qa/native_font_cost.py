import ast,pathlib,sys
t=ast.parse(pathlib.Path(sys.argv[1]).read_text())
node=next(n for n in t.body if isinstance(n,ast.Assign) and any(isinstance(q,ast.Name) and q.id=='tail' for q in n.targets))
s=ast.literal_eval(node.value);a=s.index('  cases=[');b=s.index('  for phase',a)
cases="""  sy['GenerateFontHalfRowLookupTable_changed']=sy['GenerateFontHalfRowLookupTable']
  cases=[('ListMenuDummyTask',(0,)),('GenerateFontHalfRowLookupTable',(1,0,3)),('GenerateFontHalfRowLookupTable_changed',(2,0,3))]
  for name,args in [('DecompressGlyph_Normal',(0xD0,0)),('DecompressGlyph_Small',(0xA1,0))]:
   if name in sy:cases.append((name,args))
  if 'sFontNormalLatinGlyphs' in sy:cases.append(('DecompressGlyphTile',(sy['sFontNormalLatinGlyphs']+0xD0*64,sy['gGlyphInfo'])))
"""
s=s[:a]+cases+s[b:]
s=s.replace('  for phase in range(3):\n','  for phase in range(3):\n   call("GenerateFontHalfRowLookupTable",1,0,3)\n')
node.value=ast.Constant(s);sys.argv=[sys.argv[0],*sys.argv[2:]]
exec(compile(ast.fix_missing_locations(t),'font_cost','exec'))
