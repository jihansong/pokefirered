#!/usr/bin/env python3
"""Replace Steven's duplicate HM08 with a one-time TM; preserve old receipts."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys
r=Path.cwd();m='MossdeepCity_SpaceCenter_2F';p=r/'tools/hoenn_import/patches'
sp=p/(m+'.scripts.inc');tp=p/(m+'.text.inc')
s=sp.read_text(encoding='utf-8');t=tp.read_text(encoding='utf-8')
start=m+'_EventScript_StevenAfter::\n'
end=m+'_EventScript_Scientist::\n'
assert s.count(start)==1 and s.count(end)==1
lo=s.index(start);hi=s.index(end,lo)
old=s[lo:hi]
assert 'checkitem ITEM_HM08' in old and 'ITEM_TM49' not in old
block=r'''
@M@_EventScript_StevenAfter::
 @ Old receipt flags remain final, whether the player still carries HM08 or not.
 goto_if_set FLAG_HOENN_GOT_HM08_FROM_STEVEN, @M@_EventScript_DiveReport
 checkitem ITEM_HM08
 goto_if_eq VAR_RESULT, TRUE, @M@_EventScript_DiveAlternate
 checkpcitem ITEM_HM08
 goto_if_eq VAR_RESULT, TRUE, @M@_EventScript_DiveAlternate
 msgbox @M@_Text_DiveOffer
 giveitem ITEM_HM08
 goto_if_eq VAR_RESULT, FALSE, @M@_EventScript_DiveNoRoom
 setflag FLAG_HOENN_GOT_HM08_FROM_STEVEN
 goto @M@_EventScript_DiveReport
@M@_EventScript_DiveAlternate::
 msgbox @M@_Text_DiveAlternate
 giveitem ITEM_TM49
 goto_if_eq VAR_RESULT, FALSE, @M@_EventScript_DiveAlternateNoRoom
 @ This existing flag records the regional reward; no new save field is needed.
 setflag FLAG_HOENN_GOT_HM08_FROM_STEVEN
 msgbox @M@_Text_DiveAlternateUse
 goto @M@_EventScript_DiveReport
@M@_EventScript_DiveReport::
 checkitem ITEM_HM08
 goto_if_eq VAR_RESULT, TRUE, @M@_EventScript_DiveCarried
 checkpcitem ITEM_HM08
 goto_if_eq VAR_RESULT, TRUE, @M@_EventScript_DiveStored
@M@_EventScript_DiveCarried::
 msgbox @M@_Text_StevenAfter
 release
 end
@M@_EventScript_DiveStored::
 msgbox @M@_Text_DiveStored
 release
 end
@M@_EventScript_DiveNoRoom::
 msgbox @M@_Text_DiveNoRoom
 release
 end
@M@_EventScript_DiveAlternateNoRoom::
 msgbox @M@_Text_DiveAlternateNoRoom
 release
 end
'''.lstrip().replace('@M@',m)
s=s[:lo]+block+s[hi:]
texts={
 'DiveAlternate':r''' .string "STEVEN: You already have HM08.\n"
 .string "Another copy would not help.\p"
 .string "Take this rare TM instead.\n"
 .string "It contains SNATCH.$"
''',
 'DiveAlternateUse':r''' .string "STEVEN: SNATCH takes the foe's\n"
 .string "healing or support move.\p"
 .string "The thieves sought our supplies.\n"
 .string "Now you can turn the tables.$"
''',
 'DiveAlternateNoRoom':r''' .string "Make room for TM49 in your\n"
 .string "TM CASE, then speak to me again.\p"
 .string "I will keep your reward here.$"
''',
 'DiveStored':r''' .string "STEVEN: Your HM08 is in the\n"
 .string "PC item storage.\p"
 .string "Withdraw it to your TM CASE,\n"
 .string "then teach DIVE to a partner.\p"
 .string "Search the dark water on\n"
 .string "ROUTE 128 for AQUA's trail.$"
'''}
for k,v in texts.items():
 label=m+'_Text_'+k+'::'
 assert label not in t,label
 t+='\n'+label+'\n'+v
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
b=r/'work/hoenn-hm08-alternate-backups'/stamp
paths=[sp,tp]+[r/'data/maps'/m/x for x in ['scripts.inc','text.inc','map.json']]
for f in paths:
 d=b/f.relative_to(r);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,d)
sp.write_text(s,encoding='utf-8');tp.write_text(t,encoding='utf-8')
subprocess.run([sys.executable,'tools/hoenn_import/apply_patches.py',m],check=True)
(b/'receipt.json').write_text(json.dumps({'save_layout_changed':False,'runtime_validated':False,
 'duplicate_detection':['bag HM08','PC item HM08'],'alternate':'TM49 SNATCH',
 'old_reward_flags_preserved':True,'failed_gift_flag_unchanged':True,
 'files':{str(f.relative_to(r)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [sp,tp]}},indent=2)+'\n')
print(b)
