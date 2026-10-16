#!/usr/bin/env python3
"""Wallace's post-storm Waterfall reward and League directions; save ABI unchanged."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess
r=Path.cwd();p=r/'tools/hoenn_import/patches';city='SootopolisCity'
flag='FLAG_HOENN_GOT_WALLACE_WATERFALL_REWARD'
ff=r/'include/constants/flags_hoenn_story.h'
source=ff.read_text()
assert re.search(r'^#define\s+HOENN_STORY_FLAGS_USED\s+112\s*$',source,re.M)
assert not re.search(r'HOENN_STORY_FLAGS_START\s*\+\s*112\b',source)
assert flag not in source
source=source.replace('#define HOENN_STORY_FLAGS_USED 112',
 '// Wallace rewards one shared HM or one rare TM after the sea-sky chapter.\n#define '+flag+' (HOENN_STORY_FLAGS_START + 112)\n#define HOENN_STORY_FLAGS_USED 113',1)
f=p/(city+'.scripts.inc');script=f.read_text()
pending={ff:source}
for suffix in ['Calm','Legacy']:
 old=city+'_TY_Wallace'+suffix+'::\n\tmsgbox '+city+'_Text_TY_Wallace'+suffix+', MSGBOX_NPC\n\tend'
 new=city+'_TY_Wallace'+suffix+'::\n\tlock\n\tfaceplayer\n\tmsgbox '+city+'_Text_TY_Wallace'+suffix+', MSGBOX_DEFAULT\n\tgoto '+city+'_TY_WaterfallReward'
 assert script.count(old)==1,(suffix,'current Wallace anchor changed')
 script=script.replace(old,new,1)
assert '@ Thunder Yellow Waterfall league bridge v1' not in script
script+="""
@ Thunder Yellow Waterfall league bridge v1
SootopolisCity_TY_WaterfallReward::
	goto_if_set FLAG_HOENN_GOT_WALLACE_WATERFALL_REWARD, SootopolisCity_TY_WaterfallDirections
	goto_if_set FLAG_HIDE_FOUR_ISLAND_ICEFALL_CAVE_1F_HM07, SootopolisCity_TY_WaterfallAlternate
	checkitem ITEM_HM07, 1
	goto_if_eq VAR_RESULT, TRUE, SootopolisCity_TY_WaterfallAlternate
	checkpcitem ITEM_HM07, 1
	goto_if_eq VAR_RESULT, TRUE, SootopolisCity_TY_WaterfallAlternate
	msgbox SootopolisCity_Text_TY_WaterfallFirst
	checkitemspace ITEM_HM07, 1
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_TY_WaterfallFull
	giveitem ITEM_HM07, 1
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_TY_WaterfallFull
	setflag FLAG_HOENN_GOT_WALLACE_WATERFALL_REWARD
	goto SootopolisCity_TY_WaterfallDirections

SootopolisCity_TY_WaterfallAlternate::
	msgbox SootopolisCity_Text_TY_WaterfallAlternate
	checkitemspace ITEM_TM26, 1
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_TY_WaterfallFull
	giveitem ITEM_TM26, 1
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_TY_WaterfallFull
	setflag FLAG_HOENN_GOT_WALLACE_WATERFALL_REWARD

SootopolisCity_TY_WaterfallDirections::
	msgbox SootopolisCity_Text_TY_WaterfallDirections
	release
	end

SootopolisCity_TY_WaterfallFull::
	msgbox SootopolisCity_Text_TY_WaterfallFull
	release
	end
"""
pending[f]=script
tf=p/(city+'.text.inc');text=tf.read_text() if tf.exists() else ''
assert 'SootopolisCity_Text_TY_WaterfallFirst::' not in text
text+="""
@ Thunder Yellow Waterfall league bridge v1
SootopolisCity_Text_TY_WaterfallFirst::
	.string "WALLACE: Take this HM for\\n"
	.string "WATERFALL. The sea is calm again.\\p"
	.string "JUAN's RAIN BADGE will let you\\n"
	.string "climb HOENN's waterfalls.$"

SootopolisCity_Text_TY_WaterfallAlternate::
	.string "WALLACE: You already received\\n"
	.string "WATERFALL on your earlier journey.\\p"
	.string "One HM works in every region.\\n"
	.string "Take TM26, EARTHQUAKE, instead.$"

SootopolisCity_Text_TY_WaterfallDirections::
	.string "After earning the RAIN BADGE,\\n"
	.string "sail east from ROUTE 128.\\p"
	.string "Climb EVER GRANDE's waterfall\\n"
	.string "and cross VICTORY ROAD.\\p"
	.string "The LEAGUE will check all eight\\n"
	.string "of your HOENN BADGES.$"

SootopolisCity_Text_TY_WaterfallFull::
	.string "Your TM CASE has no room.\\n"
	.string "Make space, then come back.$"
"""
pending[tf]=text
m=r/'data/maps'/city/'map.json'
mj=json.loads(m.read_text());layout=next(z for z in json.loads((r/'data/layouts/layouts.json').read_text())['layouts'] if z.get('id')==mj['layout'])
terrain=r/layout['blockdata_filepath']
unchanged={x:hashlib.sha256(x.read_bytes()).hexdigest() for x in (m,terrain)}
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=r/'work'/('wallace-waterfall-backup-'+stamp);backup.mkdir(parents=True,exist_ok=False)
targets=set(pending)|set(x for x in (r/'data/maps'/city).iterdir() if x.is_file())
for target in sorted(targets):
 if target.exists():
  dest=backup/target.relative_to(r);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,dest)
for target,content in pending.items():target.write_text(content)
subprocess.run(['python3','tools/hoenn_import/apply_patches.py',city],check=True)
assert unchanged=={x:hashlib.sha256(x.read_bytes()).hexdigest() for x in unchanged}
print(json.dumps({'changed':[str(x.relative_to(r)) for x in pending],
 'backup':str(backup.relative_to(r)),'flag_slot':112,'duplicate_hm_tm':'TM26 EARTHQUAKE',
 'terrain_and_map_events_unchanged':True,'save_layout_unchanged':True,
 'native_reward_and_waterfall_qa_pending':True,
 'canonical_sha256':{str(x.relative_to(r)):hashlib.sha256(x.read_bytes()).hexdigest() for x in pending}}))
