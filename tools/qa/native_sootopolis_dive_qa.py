#!/usr/bin/env python3
"""Native Sootopolis Dive round trips, cold saves and legacy escape; no RAM writes."""
from pathlib import Path
import ast
def adapt(src):
 old="R='Route128';U='Underwater_Route128';C='Underwater_SeafloorCavern';E='SeafloorCavern_Entrance'"
 new="R='SootopolisCity';U='Underwater_SootopolisCity';C=U;E=R"
 assert src.count(old)==1
 src=src.replace(old,new)
 for old,new,count in [("s.warp(C,6,6)","s.warp(C,9,6)",1),
  ("s.warp(R,38,27)","s.warp(R,31,54)",1),
  ("a_dive();reach(E,10,16,SURF)","a_dive();reach(E,31,54,SURF)",2)]:
  assert src.count(old)==count,(old,src.count(old),count)
  src=src.replace(old,new)
 tree=ast.parse(src)
 choices=[n for n in ast.walk(tree) if isinstance(n,ast.Assign)
  and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute)
  and n.value.func.attr=='replace' and len(n.value.args)==2
  and isinstance(n.value.args[0],ast.Constant)
  and n.value.args[0].value=="choices=['weather-party','weather-pc','space']"]
 assert len(choices)==1
 n=choices[0];lines=src.splitlines(keepends=True)
 lo=sum(map(len,lines[:n.lineno-1]));hi=sum(map(len,lines[:n.end_lineno]))
 src=src[:lo]+"head=head.replace(\"choices=['weather-party','weather-pc','space']\",\"choices=['route','legacy']\")\n"+src[hi:]
 tree=ast.parse(src)
 nodes=[n for n in ast.walk(tree) if isinstance(n,ast.If)
  and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Attribute)
  and n.test.left.attr=='case' and len(n.test.comparators)==1
  and isinstance(n.test.comparators[0],ast.Tuple)
  and ast.literal_eval(n.test.comparators[0])==('route','teach','hoenn-only')]
 assert len(nodes)==1
 n=nodes[0];lines=src.splitlines(keepends=True)
 lo=sum(map(len,lines[:n.body[0].lineno-1]))
 hi=sum(map(len,lines[:n.body[-1].end_lineno]))
 replacement="""   assert e.u8(syms['gPlayerAvatar'])&SURF
   a_dive();reach(U,9,6,UW)
   native_save_reopen(e,source_pc);reach(U,9,6,UW)
   menu_dive();reach(R,31,54,SURF)
   native_save_reopen(e,source_pc);reach(R,31,54,SURF)
   a_dive();reach(U,9,6,UW)
   menu_dive();reach(R,31,54,SURF)
   report['native_sootopolis_roundtrip']=True
"""
 src=src[:lo]+replacement+src[hi:]
 src=src.replace("mode='native-dive-'+a.case","mode='native-sootopolis-dive-'+a.case")
 ast.parse(src)
 return src
if __name__=='__main__':
 src=adapt(Path('tools/qa/native_dive_qa.py').read_text())
 exec(compile(src,'tools/qa/native_sootopolis_dive_qa.py','exec'),
      {'__name__':'__main__','__file__':'tools/qa/native_sootopolis_dive_qa.py'})
