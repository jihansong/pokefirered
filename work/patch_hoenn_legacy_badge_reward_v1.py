#!/usr/bin/env python3
"""Resume Brawly/Wattson badges after old trainer wins; dry run first."""
import argparse,datetime,hashlib,json,re,subprocess
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--apply',action='store_true');a=P.parse_args()
R=Path.cwd();sha=lambda b:hashlib.sha256(b).hexdigest()
ROWS=[{"map":"DewfordTown_Gym","sha":"e34a0fdcb715ee807f385a9da043dd1660136bc5260b94b367f6dd0df3ac74c5","edits":[["\ttrainerbattle_single TRAINER_HOENN_BRAWLY_1, DewfordTown_Gym_Text_BrawlyIntro, DewfordTown_Gym_Text_BrawlyDefeat, DewfordTown_Gym_EventScript_DefeatedBrawly, NO_MUSIC\n\tgoto_if_unset FLAG_HOENN_GOT_TM08_FROM_BRAWLY, DewfordTown_Gym_EventScript_GiveTM08\n\tmsgbox DewfordTown_Gym_Text_BrawlyPostBattle","\ttrainerbattle_single TRAINER_HOENN_BRAWLY_1, DewfordTown_Gym_Text_BrawlyIntro, DewfordTown_Gym_Text_BrawlyDefeat, DewfordTown_Gym_EventScript_DefeatedBrawly, NO_MUSIC\n\tgoto_if_unset FLAG_HOENN_BADGE02_GET, DewfordTown_Gym_EventScript_DefeatedBrawly\n\tgoto_if_unset FLAG_HOENN_GOT_TM08_FROM_BRAWLY, DewfordTown_Gym_EventScript_GiveTM08\nDewfordTown_Gym_EventScript_LegacyPostBattle::\n\tmsgbox DewfordTown_Gym_Text_BrawlyPostBattle"],["DewfordTown_Gym_EventScript_GiveTM08::\n\tmsgbox DewfordTown_Gym_Text_TakeThisTM","DewfordTown_Gym_EventScript_GiveTM08::\n\tgoto_if_set FLAG_HOENN_GOT_TM08_FROM_BRAWLY, DewfordTown_Gym_EventScript_LegacyPostBattle\n\tmsgbox DewfordTown_Gym_Text_TakeThisTM"]]},{"map":"MauvilleCity_Gym","sha":"a210782c723e0c5df84b0afc7cb5359465e1f06a4b74e190014be5f797a3b095","edits":[["\ttrainerbattle_single TRAINER_HOENN_WATTSON_1, MauvilleCity_Gym_Text_WattsonIntro, MauvilleCity_Gym_Text_WattsonDefeat, MauvilleCity_Gym_EventScript_DefeatedWattson, NO_MUSIC\n\tgoto_if_unset FLAG_HOENN_GOT_TM34_FROM_WATTSON, MauvilleCity_Gym_EventScript_GiveTM34","\ttrainerbattle_single TRAINER_HOENN_WATTSON_1, MauvilleCity_Gym_Text_WattsonIntro, MauvilleCity_Gym_Text_WattsonDefeat, MauvilleCity_Gym_EventScript_DefeatedWattson, NO_MUSIC\n\tgoto_if_unset FLAG_HOENN_BADGE03_GET, MauvilleCity_Gym_EventScript_DefeatedWattson\n\tgoto_if_unset FLAG_HOENN_GOT_TM34_FROM_WATTSON, MauvilleCity_Gym_EventScript_GiveTM34"],["MauvilleCity_Gym_EventScript_GiveTM34::\n\tmsgbox MauvilleCity_Gym_Text_TakeThisTM","MauvilleCity_Gym_EventScript_GiveTM34::\n\tgoto_if_set FLAG_HOENN_GOT_TM34_FROM_WATTSON, MauvilleCity_Gym_EventScript_WattsonPostBattle\n\tmsgbox MauvilleCity_Gym_Text_TakeThisTM"]]}]
assert subprocess.check_output(['git','branch','--show-current'],text=True).strip()=='hoenn-z3'
before={};after={}
for row in ROWS:
 canon='data/maps/'+row['map']+'/scripts.inc'
 mirror='tools/hoenn_import/patches/'+row['map']+'.scripts.inc'
 for rel in [canon,mirror]:
  f=R/rel;assert f.is_file(),('native/mirror source missing',rel)
  before[rel]=f.read_bytes();t=before[rel].decode()
  for old,new in row['edits']:
   if new in t:assert t.count(new)==1,('duplicate fixed block',rel)
   else:
    assert t.count(old)==1,('current source anchor changed',rel,old[:80])
    t=t.replace(old,new,1)
  after[rel]=t.encode()
  if rel==canon and before[rel]!=after[rel]:
   assert sha(before[rel])==row['sha'],('canonical preimage changed',rel)
  for flag in ['FLAG_HOENN_GOT_TM08_FROM_BRAWLY' if row['map']=='DewfordTown_Gym' else 'FLAG_HOENN_GOT_TM34_FROM_WATTSON']:
   assert t.count('setflag '+flag)==1,('reward receipt writer changed',rel)
  assert ('setflag FLAG_HOENN_BADGE02_GET' if row['map']=='DewfordTown_Gym' else 'setflag FLAG_HOENN_BADGE03_GET') in t
changed={p:b for p,b in after.items() if b!=before[p]}
saves={str(p):sha(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}
receipt={'apply':a.apply,'changed':list(changed),'native_legacy_cases':'NOT_RUN',
 'save_layout_changed':False,'trainer_ids_or_parties_changed':False,
 'existing_map_objects_warps_terrain_changed':False,
 'scope':'Only existing win bits recover missing Hoenn badge; successfully received TM is never given twice',
 'files':{p:{'before':sha(before[p]),'after':sha(after[p])} for p in before},
 'original_save_sha256':saves}
if a.apply and changed:
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 dest=R/'work/backups'/('hoenn-legacy-badge-reward-v1-'+stamp)
 for p,b in before.items():assert (R/p).read_bytes()==b,('concurrent source edit',p)
 for p in changed:
  q=dest/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[p])
 for p,b in changed.items():(R/p).write_bytes(b)
 receipt['backup']=str(dest.relative_to(R))
assert {str(p):sha(p.read_bytes()) for p in (R/'saves').rglob('*.sav')}==saves
print(json.dumps(receipt,indent=2))
