#!/usr/bin/env python3
"""Keep the Weather/Space generator consistent with the canonical HM reward."""
from pathlib import Path
import ast,datetime,hashlib,json,shutil,sys
g=Path(sys.argv[1]).resolve()
src=g.read_text(encoding='utf-8')
m='MossdeepCity_SpaceCenter_2F'
canonical=Path('tools/hoenn_import/patches')/(m+'.scripts.inc')
actual=canonical.read_text(encoding='utf-8')
start=m+'_EventScript_StevenAfter::\n';end=m+'_EventScript_Scientist::\n'
lo=actual.index(start);hi=actual.index(end,lo)
block=actual[lo:hi].replace(m,'@M@')
assert 'giveitem ITEM_TM49' in block and 'checkpcitem ITEM_HM08' in block
a=start.replace(m,'@M@');b=end.replace(m,'@M@')
assert src.count(a)==1 and src.count(b)==1
lo=src.index(a);hi=src.index(b,lo)
src=src[:lo]+block+src[hi:]
nodes=[n for n in ast.walk(ast.parse(src)) if isinstance(n,ast.Call)
 and isinstance(n.func,ast.Name) and n.func.id=='text_file' and len(n.args)==2
 and isinstance(n.args[0],ast.Name) and n.args[0].id=='S2']
assert len(nodes)==1
n=nodes[0];d=ast.literal_eval(n.args[1])
d.update({
 'DiveAlternate':['STEVEN: You already have HM08.|Another copy would not help.',
                  'Take this rare TM instead.|It contains SNATCH.'],
 'DiveAlternateUse':["STEVEN: SNATCH takes the foe's|healing or support move.",
                     'The thieves sought our supplies.|Now you can turn the tables.'],
 'DiveAlternateNoRoom':['Make room for TM49 in your|TM CASE, then speak to me again.',
                       'I will keep your reward here.'],
 'DiveStored':['STEVEN: Your HM08 is in the|PC item storage.',
               'Withdraw it to your TM CASE,|then teach DIVE to a partner.',
               "Search the dark water on|ROUTE 128 for AQUA's trail."]})
lines=src.splitlines(keepends=True)
lo=sum(map(len,lines[:n.lineno-1]))+n.col_offset
hi=sum(map(len,lines[:n.end_lineno-1]))+n.end_col_offset
src=src[:lo]+'text_file(S2, '+repr(d)+')'+src[hi:]
ast.parse(src)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=Path('work/hoenn-hm08-generator-backups')/stamp
backup.mkdir(parents=True,exist_ok=True);shutil.copy2(g,backup/g.name)
g.write_text(src,encoding='utf-8')
receipt={'generator':str(g),'sha256':hashlib.sha256(g.read_bytes()).hexdigest(),
 'canonical_reward_sha256':hashlib.sha256(block.encode()).hexdigest(),
 'generator_executed':False,'save_layout_changed':False}
(backup/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
