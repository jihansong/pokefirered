import ast,pathlib,sys
profile_path=pathlib.Path(sys.argv[1]);tree=ast.parse(profile_path.read_text())
assign=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='tail' for t in n.targets));tail=ast.literal_eval(assign.value)
pairs=[("'tm':tm,**","'tm':tm,'keyreg':sy['gMain']+48,**"),("0x6020,('l',4,'tm'),0x2000","0x6020,('l',4,'keyreg'),(0x2080 if name=='CB2_PokedexScreen_DOWN' else 0x2000),0x8020,('l',4,'tm'),0x2000"),("  sy['BlitMenuInfoIcon_type']=sy['BlitMenuInfoIcon']","  sy['CB2_PokedexScreen_DOWN']=sy['CB2_PokedexScreen']\n  cases=[('ListMenuDummyTask',(0,)),('ListMenuChangeSelection',(lm,1,1,1)),('CB2_PokedexScreen_DOWN',()),('CB2_PokedexScreen',()),('RunTextPrinters',()),('AnimateSprites',()),('BuildOamBuffer',()),('MapMusicMain',())]")]
for before,after in pairs:
 assert tail.count(before)==1,before;tail=tail.replace(before,after)
assign.value=ast.Constant(tail);ast.fix_missing_locations(tree);sys.argv=[str(profile_path),*sys.argv[2:]];exec(compile(tree,'profile-whole-callback','exec'))
