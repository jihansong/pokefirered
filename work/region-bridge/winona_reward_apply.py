from pathlib import Path
import json,re,hashlib,datetime,tempfile,importlib.util,subprocess
R=Path('/workspaces/pokefirered')
NAME='FortreeCity_Gym'
SCRIPT=r'''@ Z5 reward bridge: a pre-Z5 save may already record WINONA's defeat.
@ The post-battle fallthrough and the new-victory callback use the same path.
@ Owning TM40 does not record whether WINONA gave it.
FortreeCity_Gym_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_WINONA_1, FortreeCity_Gym_Text_H0_0, FortreeCity_Gym_Text_H0_1, FortreeCity_Gym_EventScript_DefeatedWinona, NO_MUSIC
	goto FortreeCity_Gym_EventScript_DefeatedWinona
	end

FortreeCity_Gym_EventScript_DefeatedWinona::
	goto_if_set FLAG_HOENN_BADGE06_GET, FortreeCity_Gym_EventScript_CheckTM40
	setflag FLAG_HOENN_BADGE06_GET
	msgbox FortreeCity_Gym_Text_ReceivedFeatherBadge

FortreeCity_Gym_EventScript_CheckTM40::
	goto_if_set FLAG_HOENN_GOT_TM40_FROM_WINONA, FortreeCity_Gym_EventScript_PostBattle
	msgbox FortreeCity_Gym_Text_TakeTM40
	additem ITEM_TM40
	goto_if_eq VAR_RESULT, FALSE, FortreeCity_Gym_EventScript_NoRoomForTM40
	@ Commit the receipt only after the item was successfully added.
	setflag FLAG_HOENN_GOT_TM40_FROM_WINONA
	msgreceiveditem FortreeCity_Gym_Text_ReceivedTM40, ITEM_TM40
	msgbox FortreeCity_Gym_Text_ExplainTM40
	release
	end

FortreeCity_Gym_EventScript_NoRoomForTM40::
	msgbox FortreeCity_Gym_Text_NoRoomForTM40
	release
	end

FortreeCity_Gym_EventScript_PostBattle::
	msgbox FortreeCity_Gym_Text_H0_2
	release
	end
'''
TEXT=r'''FortreeCity_Gym_Text_H0_0::
    .string "WINONA: A champion from KANTO!\n"
    .string "Your journey has brought you far.\p"
    .string "Let our partners show us how high\n"
    .string "they can soar!$"

FortreeCity_Gym_Text_H0_1::
    .string "Your team moved as one.\n"
    .string "A beautiful battle!$"

FortreeCity_Gym_Text_H0_2::
    .string "The sky is vast, and there is\n"
    .string "always more to learn.\p"
    .string "I will keep training with my\n"
    .string "partners among these treetops.$"

FortreeCity_Gym_Text_ReceivedFeatherBadge::
    .string "{PLAYER} received\n"
    .string "the FEATHER BADGE!$"

FortreeCity_Gym_Text_TakeTM40::
    .string "Take this TM as well.\n"
    .string "Let your partners try it.$"

FortreeCity_Gym_Text_ReceivedTM40::
    .string "{PLAYER} received TM40\n"
    .string "from WINONA.$"

FortreeCity_Gym_Text_ExplainTM40::
    .string "AERIAL ACE strikes with speed\n"
    .string "and precision.\p"
    .string "A well-timed move can turn\n"
    .string "the whole battle around!$"

FortreeCity_Gym_Text_NoRoomForTM40::
    .string "Your TM CASE can't hold another.\n"
    .string "Make room for TM40 and come back.$"
'''
B='FLAG_HOENN_BADGE06_GET';F='FLAG_HOENN_GOT_TM40_FROM_WINONA';T='TRAINER_HOENN_WINONA_1'
cases=[]
def case(name,edits,steps,xfail=False):
 c={'name':'z5_winona_'+name,'edit':['warp FortreeCity_Gym 15 3','noquestlog','trainer '+T+' 1','flag '+B+' 0','flag '+F+' 0','item ITEM_TM40 0','money 10000']+edits,'steps':steps}
 if xfail:c['xfail']=True
 cases.append(c)
talk=['UP','A','mash 180','expect overworld']
paid=['expect trainer '+T+' = 1','expect flag '+B+' = 1','expect flag '+F+' = 1']
case('new_victory',['trainer '+T+' 0','strong 4 100','lead 4','fastbattle'],['UP','A','mashbattle','expect battle','expect flag '+B+' = 0','expect flag '+F+' = 0','expect item ITEM_TM40 = 0','mash 600','expect overworld']+paid+['expect item ITEM_TM40 = 1','shot reward','A','mash 180','expect item ITEM_TM40 = 1'])
case('old_victory_recovers',[],['UP','watch FortreeCity_Gym_Text_ReceivedFeatherBadge','A','mash 180','expect overworld']+paid+['expect saw FortreeCity_Gym_Text_ReceivedFeatherBadge = 1','expect item ITEM_TM40 = 1','expect money = 10000','shot recovered','A','mash 180','expect item ITEM_TM40 = 1','expect money = 10000'])
case('other_source_tm_kept',['item ITEM_TM40 1'],talk+paid+['expect item ITEM_TM40 = 2','A','mash 180','expect item ITEM_TM40 = 2'])
case('full_stack_pending',['item ITEM_TM40 999'],['UP','watch FortreeCity_Gym_Text_NoRoomForTM40','A','mash 180','expect overworld','expect flag '+B+' = 1','expect flag '+F+' = 0','expect saw FortreeCity_Gym_Text_NoRoomForTM40 = 1','expect item ITEM_TM40 = 999','expect money = 10000','shot full','A','mash 180','expect flag '+F+' = 0','expect item ITEM_TM40 = 999'])
case('retry_after_room',['flag '+B+' 1','item ITEM_TM40 998'],talk+paid+['expect item ITEM_TM40 = 999','A','mash 180','expect item ITEM_TM40 = 999'])
case('already_received_kept',['flag '+B+' 1','flag '+F+' 1','item ITEM_TM40 1'],talk+paid+['expect item ITEM_TM40 = 1','A','mash 180','expect item ITEM_TM40 = 1'])
case('already_received_used',['flag '+B+' 1','flag '+F+' 1'],talk+paid+['expect item ITEM_TM40 = 0','A','mash 180','expect item ITEM_TM40 = 0'])
case('paid_missing_badge_recovered',['flag '+F+' 1'],talk+paid+['expect item ITEM_TM40 = 0'])
case('badge_not_reannounced',['flag '+B+' 1'],['UP','watch FortreeCity_Gym_Text_ReceivedFeatherBadge','A','mash 180','expect overworld']+paid+['expect saw FortreeCity_Gym_Text_ReceivedFeatherBadge = 0','expect item ITEM_TM40 = 1'])
case('no_reward_before_win',['trainer '+T+' 0','fastbattle'],['UP','A','mashbattle','expect battle','expect trainer '+T+' = 0','expect flag '+B+' = 0','expect flag '+F+' = 0','expect item ITEM_TM40 = 0'])
case('loss_no_reward',['trainer '+T+' 0','mon 0 MAGIKARP 1','party 1','held 0 ITEM_NONE','hp 0 1','fastbattle'],['UP','A','mashbattle','expect battle','mash 600','expect overworld','expect trainer '+T+' = 0','expect flag '+B+' = 0','expect flag '+F+' = 0','expect item ITEM_TM40 = 0'])
others={'FLAG_BADGE01_GET':0,'FLAG_BADGE02_GET':1,'FLAG_HOENN_BADGE01_GET':0,'FLAG_HOENN_BADGE02_GET':1,'FLAG_HOENN_BADGE03_GET':1,'FLAG_HOENN_BADGE05_GET':0,'FLAG_HOENN_BADGE04_GET':1,'FLAG_HOENN_BADGE07_GET':0,'FLAG_HOENN_BADGE08_GET':1}
case('other_badges_unchanged',['flag '+k+' '+str(v) for k,v in others.items()],talk+paid+['expect flag '+k+' = '+str(v) for k,v in others.items()])
case('duplicate_negative_control',['flag '+B+' 1','flag '+F+' 1'],talk+['expect item ITEM_TM40 = 1'],True)
case('full_stack_negative_control',['item ITEM_TM40 999'],talk+['expect flag '+F+' = 1'],True)
DATA={'script':SCRIPT,'text':TEXT,'cases':'# Winona reward cases; original saves are unchanged.\n'+''.join(json.dumps(c)+'\n' for c in cases)}
def sha(b):return hashlib.sha256(b).hexdigest()
def rb(rel):return (R/rel).read_bytes() if (R/rel).exists() else None
def rt(rel):
 b=rb(rel);return b.decode() if b is not None else ''
assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='hoenn-z3','Unexpected branch'
expected={
 'data/maps/FortreeCity_Gym/scripts.inc':'6752c49f19958db4d18778ea22395e7c79d0aa8e5492df11db5cfd1159724263',
 'data/maps/FortreeCity_Gym/map.json':'c4d65419bf7fd215f1c3b6671a7dfa497466b4d2f36a60dac4c3920754fce0ca',
 'data/maps/FortreeCity_Gym/text.inc':'e291d288d3e3c6f5efcfe92399395a24a5a6b6664b61924f8bf0b22cd3ddb04c',
 'data/layouts/HoennFortreeCity_Gym/map.bin':'650a69e942297e0bb4f35256f819a51cbb75778299368c684340167a49d2b7fb'}
for rel,h in expected.items():assert sha(rb(rel))==h,'Fresh source differs: '+rel
prefix='tools/hoenn_import/patches/'+NAME
assert not rb(prefix+'.scripts.inc'),'Canonical Winona script exists; merge it explicitly'
assert not rb(prefix+'.text.inc'),'Canonical Winona dialogue exists; merge it explicitly'
# Reserve a single unused bit inside the already-existing hoennFlags array.
flagrel='include/constants/flags_hoenn_story.h';flags=rt(flagrel)
flag='FLAG_HOENN_GOT_TM40_FROM_WINONA'
assert flag not in flags,'Reward flag exists; inspect previous work'
for hp in (R/'include').rglob('*.h'):
 h=hp.read_text()
 assert flag not in h,'Reward flag already referenced: '+str(hp)
 assert not re.search(r'HOENN_STORY_FLAGS_START\s*\+\s*(?:100|0[xX]0*64)\b',h),'Story +100 already referenced: '+str(hp)
 assert not re.search(r'HOENN_FLAGS_START\s*\+\s*(?:612|0[xX]0*264)\b',h),'Equivalent Hoenn +0x264 already referenced: '+str(hp)
used=re.search(r'^#define HOENN_STORY_FLAGS_USED\s+(\d+)\s*$',flags,re.M)
assert used and int(used.group(1))==100,'Story flag reservation changed'
allocated=[int(x) for x in re.findall(r'\(HOENN_STORY_FLAGS_START\s*\+\s*(\d+)\)',flags)]
assert allocated and max(allocated)==99 and len(allocated)==len(set(allocated)),'Flag allocation needs review'
assert re.search(r'#define\s+FLAG_HOENN_BADGE06_GET\s+\(HOENN_STORY_FLAGS_START\s*\+\s*5\)',flags)
addition=('@ Stage 5 reward bridge. One unused bit in the existing Hoenn flag array.\n'
          '@ No save fields, offsets, map IDs, object IDs or trainer IDs change.\n').replace('@','//')
addition+='#define '+flag+'    (HOENN_STORY_FLAGS_START + 100)\n\n#define HOENN_STORY_FLAGS_USED 101'
newflags=flags[:used.start()]+addition+flags[used.end():]
casepath='tools/qa/cases/z5_winona.jsonl'
docpath='docs/team/qa/codex-z5-winona-20261004/README.md'
assert not (R/casepath).exists() and not (R/docpath).exists(),'Existing QA artifacts must not be overwritten'
for p in (R/'tools/hoenn_import/patches').glob('*'):
 if p.is_file() and p.suffix in ('.inc','.json','.mapscripts'):
  assert flag not in p.read_text(), 'Existing reward reference in '+str(p)
original={p:rb(p) for p in expected}
for p in [flagrel,casepath,docpath]+[prefix+'.'+x for x in ('scripts.inc','text.inc','json','mapscripts')]:original[p]=rb(p)
changes={
 flagrel:newflags.encode(),
 prefix+'.scripts.inc':DATA['script'].encode(),
 prefix+'.text.inc':DATA['text'].encode(),
 casepath:DATA['cases'].encode(),
 docpath:('''# Winona reward bridge — implementation awaiting runtime QA

The imported gym previously recorded a trainer victory but never awarded the
FEATHER BADGE or TM40. The victory callback and post-victory conversation now
share one recovery path. TM40 is committed only after AddBagItem succeeds;
a full stack leaves its receipt flag clear, and revisiting retries the gift.
Owning a TM40 from another source does not consume this reward.

Changed: canonical gym script/text, generated script/text, one existing-array
flag bit at HOENN_STORY_FLAGS_START+100, and fourteen event cases.
Unchanged: save structures/offsets, map/object/trainer IDs, maps and tiles,
trainer parties/levels, other gym badges, global bag code, user save files.
This is a reward fix; it does not complete Hoenn Z5 or its league.

Checks performed by apply script: source SHA guards, flag allocation guards,
canonical regeneration twice, duplicate labels, map unchanged, concurrent
source guards and exact before-file backup.

Runtime status: NOT RUN. Build/syms and these commands are still required:
- python3 tools/qa/eventcheck.py tools/qa/cases/z5_winona.jsonl --shots docs/team/qa/codex-z5-winona-20261004/shots
- python3 tools/qa/eventcheck.py tools/qa/cases/z4_flannery.jsonl
- python3 tools/qa/eventcheck.py tools/qa/cases/z3_roxanne.jsonl
- python3 tools/qa/textwidth.py tools/hoenn_import/patches/FortreeCity_Gym.text.inc
- Existing save-compatibility and map-smoke checks.

The fourteen cases cover a new victory, a pre-Z5 victory, another TM40 source,
full-stack failure, retry after space is made, duplicate/used rewards, badge
recovery, no repeated badge text, before-victory and loss paths, unrelated
badges, and two negative controls. They work on copies of saves/hoenn.sav.
Save/reload persistence and a real Delta device check remain separate runtime
checks; no local/in-memory preparation is reported as those checks passing.
''').encode()}
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
stage=Path(tempfile.mkdtemp(prefix='.qa-winona-stage-',dir=R))
for rel,b in original.items():
 if b is not None:
  p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
for rel,b in changes.items():
 p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
spec=importlib.util.spec_from_file_location('winona_apply',R/'tools/hoenn_import/apply_patches.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.R=str(stage);m.P=str(stage/'tools/hoenn_import/patches')
m.apply(NAME)
generated={}
for kind in ('scripts.inc','text.inc'):
 rel='data/maps/'+NAME+'/'+kind;generated[rel]=(stage/rel).read_bytes()
 # A canonical override must leave one definition of each label.
 labels=re.findall(r'^(\w+)::?',generated[rel].decode(),re.M)
 assert len(labels)==len(set(labels)),'Duplicate generated labels in '+rel
assert (stage/('data/maps/'+NAME+'/map.json')).read_bytes()==original['data/maps/'+NAME+'/map.json'],'Map changed'
m.apply(NAME)
assert all((stage/p).read_bytes()==b for p,b in generated.items()),'Canonical generator not idempotent'
changes.update(generated)
# Require every original byte to remain unchanged since planning this transaction.
for rel,b in original.items():assert rb(rel)==b,'Concurrent modification: '+rel
backup=R/('.qa-winona-before-'+stamp);backup.mkdir(exist_ok=False)
for rel,b in original.items():
 if b is not None:
  p=backup/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
manifest={'utc':stamp,'branch':'hoenn-z3','head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
 'before':{p:sha(b) if b is not None else None for p,b in original.items()},
 'after':{p:sha(b) for p,b in changes.items()},
 'new_flag':flag,'new_flag_id':'0x1264','save_layout_changed':False,
 'canonical_idempotent':True,'runtime_qa':'NOT_RUN'}
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for rel,b in changes.items():
 p=R/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
print(json.dumps({'applied':list(changes),'backup':str(backup),'stage':str(stage),'runtime_qa':'NOT_RUN'},indent=2))
