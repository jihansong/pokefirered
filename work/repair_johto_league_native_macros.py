#!/usr/bin/env python3
"""Validate existing native held-item party macros from their actual battle header."""
from pathlib import Path
import ast,hashlib,json,re,sys
p=Path('tools/johto/build_johto_league.py');old=p.read_bytes()
assert hashlib.sha256(old).hexdigest()=='93f9b8a83b4627200091d5eea6f99ae1fa9f4d45b878d086ea4208582a3af747'
t=old.decode()
a=" headers='\\n'.join(final.text('include/constants/'+n) for n in ['species.h','items.h','moves.h','songs.h','event_objects.h','event_object_movement.h','global.h','trainers.h'])\n";b=" headers='\\n'.join(final.text('include/constants/'+n) for n in ['species.h','items.h','moves.h','songs.h','event_objects.h','event_object_movement.h','global.h','trainers.h'])\n party_macros=final.text('include/battle.h')\n for macro in ('ITEM_CUSTOM_MOVES','ITEM_DEFAULT_MOVES'):\n  definitions=re.findall(r'^#define\\s+'+re.escape(macro)+r'\\([^)]*\\)[^\\n]*$',party_macros,re.M)\n  assert len(definitions)==1,('native trainer party macro missing',macro)\n  headers+='\\n'+definitions[0]\n"
assert t.count(a)==1;t=t.replace(a,b);new=t.encode();ast.parse(new)
assert hashlib.sha256(new).hexdigest()=='cb9ba7049d9dc0fb66a5e4079626f7742f849509c9cff006e2986a71246d70be'
print(json.dumps({'path':str(p),'bytes':len(new),'sha256':hashlib.sha256(new).hexdigest(),
 'native_header':'include/battle.h','exact_native_party_macros':['ITEM_CUSTOM_MOVES','ITEM_DEFAULT_MOVES'],
 'unknown_real_constant_check_unchanged':True}))
if '--apply' in sys.argv:
 backup=p.with_name(p.name+'.before-party-macro-header');assert not backup.exists();backup.write_bytes(old);p.write_bytes(new)
