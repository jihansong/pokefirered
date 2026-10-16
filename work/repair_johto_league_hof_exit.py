#!/usr/bin/env python3
"""Repair the new HOF exit behavior and preserve explicit regional continue branches."""
from pathlib import Path
import ast,hashlib,json,sys
p=Path('tools/johto/build_johto_league.py');old=p.read_bytes();oldsha=hashlib.sha256(old).hexdigest()
assert oldsha in ('810e90ee1d11c147bd5970507bfb2c52e4ed5851bdf0212f02b4bf5f7e2ff210','d53b66e6fef052489c8d8ccdeb8426d527f3d18c9caeec97bca714f097f8aee7')
t=old.decode()
a=" p='src/post_battle_event_funcs.c';t=s.text(p)\n anchor='    SetContinueGameWarpToHealLocation(HEAL_LOCATION_PALLET_TOWN);'\n gate='''    // JOHTO_HOF_CONTINUE_DESTINATION_V1\n    if (IsJohtoHallOfFameContext())\n        SetContinueGameWarpToHealLocation(HEAL_LOCATION_JOHTO_INDIGO_PLATEAU);\n    else\n        SetContinueGameWarpToHealLocation(HEAL_LOCATION_PALLET_TOWN);'''\n if '// JOHTO_HOF_CONTINUE_DESTINATION_V1' not in t:t=C.once(t,anchor,gate,'Johto HOF continue destination')\n else:assert gate in t\n out[p]=t.encode()\n";b=" p='src/post_battle_event_funcs.c';t=s.text(p)\n anchor='    else\\n        SetContinueGameWarpToHealLocation(HEAL_LOCATION_PALLET_TOWN);'\n gate='''    else if (IsJohtoHallOfFameContext())\n        SetContinueGameWarpToHealLocation(HEAL_LOCATION_JOHTO_INDIGO_PLATEAU);\n    else\n        SetContinueGameWarpToHealLocation(HEAL_LOCATION_PALLET_TOWN); // JOHTO_HOF_CONTINUE_DESTINATION_V1'''\n if '// JOHTO_HOF_CONTINUE_DESTINATION_V1' not in t:t=C.once(t,anchor,gate,'Johto HOF continue destination')\n else:assert gate in t\n out[p]=t.encode()\n"
if oldsha=='810e90ee1d11c147bd5970507bfb2c52e4ed5851bdf0212f02b4bf5f7e2ff210':
 assert t.count(a)==1;t=t.replace(a,b)
a=" hof=V.layout_array(s,'LAYOUT_POKEMON_LEAGUE_HALL_OF_FAME')\n return {'JohtoRoute27':route27";b=" hof=V.layout_array(s,'LAYOUT_POKEMON_LEAGUE_HALL_OF_FAME')\n assert len(hof)==13 and len(hof[0])==11 and hof[12][5]==0x32b0,'native Hall-of-Fame layout preimage changed'\n hof[12][5]=0x3013  # Building primary MB_SOUTH_ARROW_WARP, collision0/elevation3.\n return {'JohtoRoute27':route27"
assert t.count(a)==1;t=t.replace(a,b);new=t.encode();ast.parse(new)
assert hashlib.sha256(new).hexdigest()=='93f9b8a83b4627200091d5eea6f99ae1fa9f4d45b878d086ea4208582a3af747'
print(json.dumps({'path':str(p),'bytes':len(new),'sha256':hashlib.sha256(new).hexdigest(),
 'new_hof_exit':[5,12,'0x3013','MB_SOUTH_ARROW_WARP'],'native_terrain_guard_unchanged':True,'canonical_generated_writes':0}))
if '--apply' in sys.argv:
 backup=p.with_name(p.name+'.before-hof-exit-fix');assert not backup.exists();backup.write_bytes(old);p.write_bytes(new)
