import ast,pathlib,sys
tree=ast.parse(pathlib.Path(sys.argv[1]).read_text())
helper=pathlib.Path(sys.argv[2]).read_text()
n=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='extra' for t in n.targets))
extra=ast.literal_eval(n.value)
needle=" check_companion_visible(previous,label+'-left')"
assert extra.count(needle)==1
n.value=ast.Constant(helper+'\n'+extra.replace(needle,needle+'\n water_budget(label)'))
sys.argv=[sys.argv[0],*sys.argv[3:]]
try:
 exec(compile(ast.fix_missing_locations(tree),'water_performance_wrapper','exec'))
except SystemExit as ex:
 if ex.code not in (None,0):raise
 assert _water_done=={'Route128','Underwater_Route128'},('missing water cases',_water_done)
 raise
assert _water_done=={'Route128','Underwater_Route128'},('missing water cases',_water_done)
