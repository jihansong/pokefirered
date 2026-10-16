from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re,subprocess,sys
sys.dont_write_bytecode=True
R=Path.cwd().resolve()
N="PetalburgCity_Gym"
P="tools/hoenn_import/patches/"+N
G="data/maps/"+N
PIN={
P+".scripts.inc":"1f824095d9df812b00f4c682fff342cae6c1f46e373986ca59561ddd5b8dc13b",
P+".text.inc":"a0c82d3fe9c0a9c29bbc5d22a1b1185a67e3797c5db063e961f40ec78406c0d5",
G+"/scripts.inc":"86addf2774acded7e7101992f0e7ba343c90256cb0765fdbd219dfc1d85a4750",
G+"/text.inc":"8bfed456084c606a81d3cb440022298bf2fe22756ee3207b4c53a8bdd8af89cf",
"src/data/trainer_parties_hoenn.h":"0c0baa853206a0e758efadaf423855b2c5a8656c459a78a3c3adcf16d3bf1d00",
G+"/map.json":"a09214557af8fa0064572f192764841a946be7511efbc5162e4a1b264b845a3e",
"data/layouts/HoennPetalburgCity_Gym/map.bin":"b75cd4f08b42faf760a95d2610fa8be868e47d37eb8d0c55ab6724ffc45883db",
}
ENTRY="PetalburgCity_Gym_EventScript_Norman::\n\tlock\n\tfaceplayer\n\tchecktrainerflag TRAINER_HOENN_NORMAN_1\n\tgoto_if TRUE, PetalburgCity_Gym_EventScript_DefeatedNorman\n\tgoto_if_eq VAR_HOENN_SCENE_WALLY, 0, PetalburgCity_Gym_EventScript_NormanFirst\n\tgoto_if_eq VAR_HOENN_SCENE_WALLY, 1, PetalburgCity_Gym_EventScript_NormanWallyWaiting\n\tspecialvar VAR_RESULT, CountHoennBadges\n\tgoto_if_ge VAR_RESULT, 4, PetalburgCity_Gym_EventScript_NormanBattle\n\tmsgbox PetalburgCity_Gym_Text_NormanAfter\n\tcall PetalburgCity_Gym_EventScript_NormanBadges\n\trelease\n\tend\n"
EXTRA="\nPetalburgCity_Gym_EventScript_NormanWallyWaiting::\n\tmsgbox PetalburgCity_Gym_Text_NormanWallyWaiting\n\trelease\n\tend\n\nPetalburgCity_Gym_EventScript_NormanBadgesReady::\n\tmsgbox PetalburgCity_Gym_Text_NormanBadgesReady\n\treturn\n\nPetalburgCity_Gym_EventScript_NormanBattle::\n\ttrainerbattle_single TRAINER_HOENN_NORMAN_1, PetalburgCity_Gym_Text_NormanBattleIntro, PetalburgCity_Gym_Text_NormanDefeat, PetalburgCity_Gym_EventScript_DefeatedNorman, NO_MUSIC\n\tgoto PetalburgCity_Gym_EventScript_DefeatedNorman\n\tend\n\nPetalburgCity_Gym_EventScript_DefeatedNorman::\n\tgoto_if_set FLAG_HOENN_BADGE05_GET, PetalburgCity_Gym_EventScript_NormanCheckTM42\n\tsetflag FLAG_HOENN_BADGE05_GET\n\tmsgbox PetalburgCity_Gym_Text_ReceivedBalanceBadge\nPetalburgCity_Gym_EventScript_NormanCheckTM42::\n\tgoto_if_set FLAG_HOENN_GOT_TM42_FROM_NORMAN, PetalburgCity_Gym_EventScript_NormanPostBattle\n\tmsgbox PetalburgCity_Gym_Text_NormanTakeTM42\n\tadditem ITEM_TM42\n\tgoto_if_eq VAR_RESULT, FALSE, PetalburgCity_Gym_EventScript_NormanNoRoom\n\tsetflag FLAG_HOENN_GOT_TM42_FROM_NORMAN\n\tmsgreceiveditem PetalburgCity_Gym_Text_ReceivedTM42, ITEM_TM42\n\tmsgbox PetalburgCity_Gym_Text_NormanExplainTM42\n\tgoto PetalburgCity_Gym_EventScript_NormanPostBattle\n\tend\n\nPetalburgCity_Gym_EventScript_NormanNoRoom::\n\tmsgbox PetalburgCity_Gym_Text_NormanNoRoom\n\trelease\n\tend\n\nPetalburgCity_Gym_EventScript_NormanPostBattle::\n\tmsgbox PetalburgCity_Gym_Text_NormanPostBattle\n\trelease\n\tend\n"
TEXT="\nPetalburgCity_Gym_Text_NormanWallyWaiting::\n    .string \"WALLY is waiting on ROUTE 102.\\n\"\n    .string \"Please stay with him until he\\l\"\n    .string \"has caught his first partner.$\"\n\nPetalburgCity_Gym_Text_NormanBadgesReady::\n    .string \"You've earned enough HOENN BADGES\\n\"\n    .string \"to challenge me.\\p\"\n    .string \"First, let's see WALLY safely\\n\"\n    .string \"through his first catch.$\"\n\nPetalburgCity_Gym_Text_NormanBattleIntro::\n    .string \"NORMAN: You've kept your promise!\\n\"\n    .string \"Now we can battle as equals.\\p\"\n    .string \"Every journey changes a TRAINER.\\n\"\n    .string \"Show me what yours has taught you!$\"\n\nPetalburgCity_Gym_Text_NormanDefeat::\n    .string \"You and your partners have grown\\n\"\n    .string \"strong together. I concede!$\"\n\nPetalburgCity_Gym_Text_ReceivedBalanceBadge::\n    .string \"{PLAYER} received\\n\"\n    .string \"the BALANCE BADGE!$\"\n\nPetalburgCity_Gym_Text_NormanTakeTM42::\n    .string \"Take this TM as well.\\n\"\n    .string \"It may help on the road ahead.$\"\n\nPetalburgCity_Gym_Text_ReceivedTM42::\n    .string \"{PLAYER} received TM42\\n\"\n    .string \"from NORMAN.$\"\n\nPetalburgCity_Gym_Text_NormanExplainTM42::\n    .string \"FACADE turns a status problem\\n\"\n    .string \"into extra power.\\p\"\n    .string \"Think about what your partner\\n\"\n    .string \"needs before choosing a move.$\"\n\nPetalburgCity_Gym_Text_NormanNoRoom::\n    .string \"Your TM CASE can't hold another.\\n\"\n    .string \"Make room for TM42 and come back.$\"\n\nPetalburgCity_Gym_Text_NormanPostBattle::\n    .string \"I came from JOHTO to make a new\\n\"\n    .string \"home here in HOENN.\\p\"\n    .string \"Every place has something to\\n\"\n    .string \"teach a TRAINER and their team.\\p\"\n    .string \"East of MAUVILLE, the road leads\\n\"\n    .string \"towards FORTREE's GYM.\\p\"\n    .string \"Keep learning from the people\\n\"\n    .string \"and POKéMON you meet.$\"\n"
BEGIN="@ BEGIN PATCH (tools/hoenn_import/patches)\n";END="@ END PATCH\n"
def sha(b):return hashlib.sha256(b).hexdigest()
def one(pattern,text):
 a=list(re.finditer(pattern,text,re.M))
 if len(a)!=1:raise ValueError("Source anchor changed: "+pattern)
 return a[0]
def block(text,label):
 return one(r"^"+re.escape(label)+r"::\n(?:[ \t].*\n)+\n?",text)
def merge(cur,patch):
 cur=re.sub(re.escape(BEGIN)+".*?"+re.escape(END),"",cur,flags=re.S).rstrip("\n")+"\n"
 for label in re.findall(r"^(\w+)::",patch,re.M):
  cur=re.sub(r"^"+re.escape(label)+r"::\n(?:[ \t].*\n)+\n?","",cur,flags=re.M)
 return cur.rstrip("\n")+"\n\n"+BEGIN+patch.rstrip("\n")+"\n"+END
def scripts(text):
 for new in ["NormanBattle::","DefeatedNorman::","NormanCheckTM42::","NormanBadgesReady::"]:
  if "PetalburgCity_Gym_EventScript_"+new in text:raise ValueError("Story patch already present")
 original_first=block(text,N+"_EventScript_NormanFirst").group()
 m=block(text,N+"_EventScript_Norman")
 old=m.group()
 expected=["lock","faceplayer","goto_if_eq VAR_HOENN_SCENE_WALLY, 0, PetalburgCity_Gym_EventScript_NormanFirst","msgbox PetalburgCity_Gym_Text_NormanAfter","call PetalburgCity_Gym_EventScript_NormanBadges","release","end"]
 actual=[x.strip() for x in old.splitlines()[1:] if x.strip()]
 if actual!=expected:raise ValueError("Norman entry changed")
 text=text[:m.start()]+ENTRY+"\n"+text[m.end():]
 m=block(text,N+"_EventScript_NormanBadges")
 body=m.group();anchor=one(r"^(?P<i>[ \t]+)specialvar VAR_RESULT, CountHoennBadges\n",body)
 line=anchor["i"]+"goto_if_ge VAR_RESULT, 4, "+N+"_EventScript_NormanBadgesReady\n"
 body=body[:anchor.end()]+line+body[anchor.end():]
 result=text[:m.start()]+body+text[m.end():]+EXTRA
 if block(result,N+"_EventScript_NormanFirst").group()!=original_first:raise ValueError("Wally introduction changed")
 return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--flags-sha",required=True);ap.add_argument("--write",action="store_true")
 a=ap.parse_args()
 if subprocess.check_output(["git","branch","--show-current"],cwd=R,text=True).strip()!="hoenn-z3":raise ValueError("Unexpected branch")
 pins={**PIN,"include/constants/flags_hoenn_story.h":a.flags_sha}
 before={p:(R/p).read_bytes() for p in pins}
 if any(sha(b)!=pins[p] for p,b in before.items()):raise ValueError("Fresh source hash mismatch")
 text={p:b.decode("utf-8") for p,b in before.items() if not p.endswith(".bin")}
 for ext in ["scripts.inc","text.inc"]:
  if merge(text[G+"/"+ext],text[P+"."+ext])!=text[G+"/"+ext]:
   raise ValueError("Generated/canonical baseline does not match native patch merger: "+ext)
 sys.path.insert(0,str(R/"tools/qa"))
 from gamedata import consts
 flags=text["include/constants/flags_hoenn_story.h"]
 cpp=subprocess.run(["cc","-dM","-E","-w","-iquote","include","-DLEAFGREEN","-DREVISION=0","-DENGLISH","-DMODERN=1","-x","c","-"],input='#include "global.h"\n#include "constants/flags.h"\n',text=True,capture_output=True,check=True)
 names=sorted(set(re.findall(r"^#define (FLAG_[A-Za-z0-9_]+)[ \t]+[^\n]+",cpp.stdout,re.M)))
 resolved=consts(names)
 if any(v==0x1265 for v in resolved.values()):raise ValueError("Norman receipt slot already allocated")
 used=one(r"^#define HOENN_STORY_FLAGS_USED[ \t]+(?P<n>\d+)[ \t]*$",flags)
 if int(used["n"])!=101:raise ValueError("Unexpected story flag allocation; review first")
 definition="#define FLAG_HOENN_GOT_TM42_FROM_NORMAN (HOENN_STORY_FLAGS_START + 101)\n\n#define HOENN_STORY_FLAGS_USED 102"
 newflags=flags[:used.start()]+definition+flags[used.end():]
 after={}
 after["include/constants/flags_hoenn_story.h"]=newflags.encode()
 after[P+".scripts.inc"]=scripts(text[P+".scripts.inc"]).encode()
 labels=set(re.findall(r"^(\w+)::",TEXT,re.M))
 if labels & set(re.findall(r"^(\w+)::",text[P+".text.inc"],re.M)):raise ValueError("New text label collision")
 after[P+".text.inc"]=(text[P+".text.inc"]+TEXT).encode()
 for ext in ["scripts.inc","text.inc"]:
  merged=merge(text[G+"/"+ext],after[P+"."+ext].decode())
  if merge(merged,after[P+"."+ext].decode())!=merged:raise ValueError("Non-idempotent canonical merge")
  after[G+"/"+ext]=merged.encode()
 party=text["src/data/trainer_parties_hoenn.h"]
 m=one(r"^static const struct TrainerMonItemCustomMoves sHoennParty_Norman1\[\] = \{\n[\s\S]*?^\};",party)
 body=m.group()
 if re.findall(r"\.species\s*=\s*(SPECIES_\w+)",body)!=["SPECIES_SPINDA","SPECIES_VIGOROTH","SPECIES_LINOONE","SPECIES_SLAKING"]:raise ValueError("Norman species changed")
 if [int(v) for v in re.findall(r"\.lvl\s*=\s*(\d+)",body)]!=[27,27,29,31]:raise ValueError("Norman levels changed")
 levels=iter([68,68,70,72])
 body=re.sub(r"(\.lvl\s*=\s*)\d+",lambda m:m[1]+str(next(levels)),body)
 after["src/data/trainer_parties_hoenn.h"]=(party[:m.start()]+body+party[m.end():]).encode()
 report={"changed":list(after),"before":{p:sha(b) for p,b in before.items()},"after":{p:sha(b) for p,b in after.items()},"applied":False,"save_layout_changed":False,"map_or_object_position_changed":False,"gym_doors_implemented":False,"legacy_win_before_wally_gate":True,"leader_levels":[68,68,70,72],"build_or_emulator_verified":False}
 if a.write:
  backup=R/"work/norman-reward-bridge-backup"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
  backup.mkdir(parents=True,exist_ok=False)
  for p in after:
   q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[p])
  (backup/"manifest.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
  if any((R/p).read_bytes()!=b for p,b in before.items()):raise ValueError("Concurrent source change")
  for p,b in after.items():(R/p).write_bytes(b)
  if any((R/p).read_bytes()!=b for p,b in after.items()):raise ValueError("Write verification failed")
  report.update(applied=True,backup=str(backup))
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
