from pathlib import Path
import json,hashlib,os,tempfile
r=Path('/workspaces/pokefirered')
mutations=json.loads("{\"src/companion_misty.c\":{\"sha\":\"1ab831929503dc78c88971063b88f221c69c11a6898e4a349f27d6205fe3856f\",\"edits\":[[\"void MistyCompanion_OnMapLoad(void)\\n{\\n    sMistyHiddenByScript = FALSE;\\n    MistyCompanion_Update();\\n}\",\"void MistyCompanion_OnMapLoad(void)\\n{\\n    sMistyHiddenByScript = FALSE;\\n    // Restore an old hidden static NPC before Prepare clears its hide flag.\\n    MistyCompanion_Update();\\n    // Continue can bypass OnTransition; the Pallet frame table keeps Oak first.\\n    if (!QL_IS_PLAYBACK_STATE\\n        && gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_PALLET_TOWN)\\n        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_PALLET_TOWN))\\n        MistyPreparePalletVisit();\\n}\"],[\"        // Oak's existing National-Dex scene keeps priority and its original script.\\n        if (VarGet(VAR_MAP_SCENE_PALLET_TOWN_OAK) != 2) VarSet(VAR_TEMP_7, TRUE);\",\"        // Queue behind Oak's frame-table entry instead of dropping the invitation.\\n        if (!FlagGet(FLAG_MISTY_COMPANION_DECLINED)) VarSet(VAR_TEMP_7, TRUE);\"],[\"    FlagSet(FLAG_MISTY_COMPANION_JOINED);\\n    FlagSet(FLAG_HIDE_MISTY_PALLET);\\n    ShowMistyCompanion();\",\"    FlagClear(FLAG_MISTY_COMPANION_DECLINED);\\n    FlagSet(FLAG_MISTY_COMPANION_JOINED);\\n    FlagSet(FLAG_HIDE_MISTY_PALLET);\\n    ShowMistyCompanion();\"]],\"append\":\"\\nu16 CanOfferMistyCompanionJoin(void)\\n{\\n    if (QL_IS_PLAYBACK_STATE || InUnionRoom() == TRUE\\n        || FlagGet(FLAG_MISTY_COMPANION_JOINED)\\n        || FlagGet(FLAG_MISTY_COMPANION_DECLINED))\\n        return FALSE;\\n    return CanMistyJoin();\\n}\\n\\nvoid MistyDeclineCompanionJoin(void)\\n{\\n    FlagSet(FLAG_MISTY_COMPANION_DECLINED);\\n    // VAR_TEMP_7 belongs to Pallet's frame table; other maps keep their own state.\\n    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_PALLET_TOWN)\\n        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_PALLET_TOWN))\\n        VarSet(VAR_TEMP_7, FALSE);\\n}\\n\"},\"data/scripts/companion_misty.inc\":{\"sha\":\"a1c3657a339d14535bdf1d2f67d5ee716416e69ba05ed0f6b434e1dd044eb0a9\",\"edits\":[[\"PalletTown_EventScript_MistyDeclined::\\n    msgbox MistyCompanion_Text_Declined, MSGBOX_DEFAULT\",\"PalletTown_EventScript_MistyDeclined::\\n    special MistyDeclineCompanionJoin\\n    msgbox MistyCompanion_Text_Declined, MSGBOX_DEFAULT\"]],\"append\":\"\\n@ Caller retains its existing locks. This helper returns to the airport story.\\nEventScript_MistyPostChampionBridge::\\n    specialvar VAR_RESULT, CanOfferMistyCompanionJoin\\n    goto_if_eq VAR_RESULT, FALSE, MistyCompanion_PostChampionBridgeDone\\n    msgbox MistyCompanion_Text_Join, MSGBOX_YESNO\\n    goto_if_eq VAR_RESULT, NO, MistyCompanion_PostChampionBridgeDeclined\\n    special MistyJoin\\n    msgbox MistyCompanion_Text_Joined, MSGBOX_DEFAULT\\n    return\\nMistyCompanion_PostChampionBridgeDeclined::\\n    special MistyDeclineCompanionJoin\\n    msgbox MistyCompanion_Text_Declined, MSGBOX_DEFAULT\\nMistyCompanion_PostChampionBridgeDone::\\n    return\\n\"},\"include/companion_misty.h\":{\"sha\":\"14843338736b830b5699dd02218946c1b0b93269e7bae59d236c66bf2ba5621f\",\"edits\":[[\"#endif\",\"u16 CanOfferMistyCompanionJoin(void);\\nvoid MistyDeclineCompanionJoin(void);\\n\\n#endif\"]]},\"data/specials.inc\":{\"sha\":\"55ce0afb2bd02bd70fb44c9f64d05b80bab48745125f968d1fa2312e17e1a53e\",\"edits\":[[\"gSpecialsEnd::\",\"\\tdef_special CanOfferMistyCompanionJoin\\n\\tdef_special MistyDeclineCompanionJoin\\ngSpecialsEnd::\"]]},\"include/constants/flags.h\":{\"sha\":\"79fbf69f3c3c1cd1a821eab7c5240d750d361498d17a09a16fef47effc0ccf19\",\"edits\":[[\"FLAG_0x228\",\"FLAG_MISTY_COMPANION_DECLINED\"]]},\"data/maps/KantoAirport/scripts.inc\":{\"sha\":\"36ea9dc781f56fc4c1afb6cc493019bc4f1180911746f9805b9e159a6714296c\",\"edits\":[[\"msgbox KantoAirport_Text_FlyToJohto, MSGBOX_YESNO\",\"call EventScript_MistyPostChampionBridge\\n    msgbox KantoAirport_Text_FlyToJohto, MSGBOX_YESNO\"],[\"msgbox KantoAirport_Text_FlyToHoenn, MSGBOX_YESNO\",\"call EventScript_MistyPostChampionBridge\\n    msgbox KantoAirport_Text_FlyToHoenn, MSGBOX_YESNO\"]]}}")
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((r/'data/maps/PalletTown/scripts.inc').read_bytes())=='0ec3ff71f92328730f65eea065b36f1f32824d848a78122c428b12214b4c3bb0'
prepared=[];changes=[]
for name,change in mutations.items():
 p=r/name;old=p.read_bytes();assert sha(old)==change['sha'],('SHA guard',name)
 s=old.decode()
 for a,b in change.get('edits',[]):
  assert s.count(a)==1,('anchor count',name,a,s.count(a));s=s.replace(a,b,1)
 s+=change.get('append','');new=s.encode();changes.append((p,old,new))
backup=r/'work/regression-oct12/backups';backup.mkdir(exist_ok=True,parents=True)
try:
 for p,old,new in changes:
  dest=backup/(p.name+'.pre-misty-'+sha(old)[:12])
  if dest.exists():assert dest.read_bytes()==old
  else:dest.write_bytes(old)
  assert p.read_bytes()==old
  fd,tmp=tempfile.mkstemp(prefix='.misty-repair-',dir=p.parent)
  with os.fdopen(fd,'wb') as f:f.write(new)
  prepared.append((p,Path(tmp),old))
 for p,tmp,old in prepared:os.replace(tmp,p)
except BaseException:
 for p,tmp,old in prepared:
  if tmp.exists():tmp.unlink()
  if p.read_bytes()!=old:p.write_bytes(old)
 raise
receipt={'source_applied':True,'native_executed':False,'save_abi_changed':False,'original_savs_modified':False,'flag':'0x228 was free; all active and backup SAV bits zero before assignment','changes':[{'path':str(p),'before_sha256':sha(old),'after_sha256':sha(new)} for p,old,new in changes]}
(r/'work/regression-oct12/misty-repair-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
