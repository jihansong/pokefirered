MauvilleCity_Gym_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, MauvilleCity_Gym_OnLoad
	.byte 0

MauvilleCity_Gym_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_SHAWN, MauvilleCity_Gym_Text_H0_0, MauvilleCity_Gym_Text_H0_1
	msgbox MauvilleCity_Gym_Text_H0_2, MSGBOX_AUTOCLOSE
	end

MauvilleCity_Gym_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_VIVIAN, MauvilleCity_Gym_Text_H1_0, MauvilleCity_Gym_Text_H1_1
	msgbox MauvilleCity_Gym_Text_H1_2, MSGBOX_AUTOCLOSE
	end

MauvilleCity_Gym_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_BEN, MauvilleCity_Gym_Text_H2_0, MauvilleCity_Gym_Text_H2_1
	msgbox MauvilleCity_Gym_Text_H2_2, MSGBOX_AUTOCLOSE
	end

MauvilleCity_Gym_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_KIRK, MauvilleCity_Gym_Text_H3_0, MauvilleCity_Gym_Text_H3_1
	msgbox MauvilleCity_Gym_Text_H3_2, MSGBOX_AUTOCLOSE
	end

MauvilleCity_Gym_EventScript_H4::
	msgbox MauvilleCity_Gym_Text_H4, MSGBOX_NPC
	end

MauvilleCity_Gym_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_ANGELO, MauvilleCity_Gym_Text_H5_0, MauvilleCity_Gym_Text_H5_1
	msgbox MauvilleCity_Gym_Text_H5_2, MSGBOX_AUTOCLOSE
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Event 3: WATTSON's gym. The electric barriers are Emerald's own puzzle: the
@ imported map keeps its tilesets and blocks byte for byte, so the metatile ids
@ (constants/metatile_labels_hoenn.h) and the three ported specials work as they
@ do there. Only the leader's words, the BADGE and the reward are ours.
MauvilleCity_Gym_OnLoad::
	goto_if_set FLAG_HOENN_DEFEATED_MAUVILLE_GYM, MauvilleCity_Gym_EventScript_DeactivatePuzzle
	switch VAR_HOENN_MAUVILLE_GYM_STATE
	case 0, MauvilleCity_Gym_EventScript_UpdateBarriers
	case 1, MauvilleCity_Gym_EventScript_Switch1Pressed
	case 2, MauvilleCity_Gym_EventScript_Switch2Pressed
	case 3, MauvilleCity_Gym_EventScript_Switch3Pressed
	case 4, MauvilleCity_Gym_EventScript_Switch4Pressed
	end

MauvilleCity_Gym_EventScript_UpdateBarriers::
	goto_if_set FLAG_HOENN_MAUVILLE_BARRIERS, MauvilleCity_Gym_EventScript_SetAltBarriers
	end

MauvilleCity_Gym_EventScript_SetAltBarriers::
	setmetatile 3, 11, METATILE_MauvilleGym_RedBeamV1_On, TRUE
	setmetatile 3, 12, METATILE_MauvilleGym_RedBeamV2_On, TRUE
	setmetatile 3, 13, METATILE_MauvilleGym_PoleTop_On, TRUE
	setmetatile 4, 10, METATILE_MauvilleGym_RedBeamH1_On, FALSE
	setmetatile 5, 10, METATILE_MauvilleGym_RedBeamH2_On, FALSE
	setmetatile 4, 11, METATILE_MauvilleGym_RedBeamH3_On, TRUE
	setmetatile 5, 11, METATILE_MauvilleGym_RedBeamH4_On, TRUE
	setmetatile 7, 10, METATILE_MauvilleGym_RedBeamH1_On, FALSE
	setmetatile 8, 10, METATILE_MauvilleGym_RedBeamH2_On, FALSE
	setmetatile 7, 11, METATILE_MauvilleGym_RedBeamH3_On, TRUE
	setmetatile 8, 11, METATILE_MauvilleGym_RedBeamH4_On, TRUE
	setmetatile 4, 13, METATILE_MauvilleGym_GreenBeamH1_Off, FALSE
	setmetatile 5, 13, METATILE_MauvilleGym_GreenBeamH2_Off, FALSE
	setmetatile 4, 14, METATILE_MauvilleGym_GreenBeamH3_Off, FALSE
	setmetatile 5, 14, METATILE_MauvilleGym_GreenBeamH4_Off, FALSE
	setmetatile 1, 10, METATILE_MauvilleGym_GreenBeamH1_Off, FALSE
	setmetatile 2, 10, METATILE_MauvilleGym_GreenBeamH2_Off, FALSE
	setmetatile 1, 11, METATILE_MauvilleGym_GreenBeamH3_Off, FALSE
	setmetatile 2, 11, METATILE_MauvilleGym_GreenBeamH4_Off, FALSE
	setmetatile 6, 8, METATILE_MauvilleGym_PoleBottom_On, TRUE
	setmetatile 6, 9, METATILE_MauvilleGym_FloorTile, FALSE
	setmetatile 6, 10, METATILE_MauvilleGym_PoleTop_Off, FALSE
	setmetatile 4, 6, METATILE_MauvilleGym_GreenBeamH1_Off, FALSE
	setmetatile 5, 6, METATILE_MauvilleGym_GreenBeamH2_Off, FALSE
	setmetatile 4, 7, METATILE_MauvilleGym_GreenBeamH3_Off, FALSE
	setmetatile 5, 7, METATILE_MauvilleGym_GreenBeamH4_Off, FALSE
	end

MauvilleCity_Gym_EventScript_Switch1Pressed::
	setvar VAR_0x8004, 0
	special MauvilleGymPressSwitch
	goto MauvilleCity_Gym_EventScript_UpdateBarriers
	end

MauvilleCity_Gym_EventScript_Switch2Pressed::
	setvar VAR_0x8004, 1
	special MauvilleGymPressSwitch
	goto MauvilleCity_Gym_EventScript_UpdateBarriers
	end

MauvilleCity_Gym_EventScript_Switch3Pressed::
	setvar VAR_0x8004, 2
	special MauvilleGymPressSwitch
	goto MauvilleCity_Gym_EventScript_UpdateBarriers
	end

MauvilleCity_Gym_EventScript_Switch4Pressed::
	setvar VAR_0x8004, 3
	special MauvilleGymPressSwitch
	goto MauvilleCity_Gym_EventScript_UpdateBarriers
	end

MauvilleCity_Gym_EventScript_DeactivatePuzzle::
	special MauvilleGymDeactivatePuzzle
	end

@ Stepping on a floor switch swaps which set of barriers is live
MauvilleCity_Gym_EventScript_Switch1::
	lockall
	goto_if_set FLAG_HOENN_DEFEATED_MAUVILLE_GYM, MauvilleCity_Gym_EventScript_SwitchDoNothing
	goto_if_eq VAR_HOENN_MAUVILLE_GYM_STATE, 1, MauvilleCity_Gym_EventScript_SwitchDoNothing
	setvar VAR_HOENN_MAUVILLE_GYM_STATE, 1
	setvar VAR_0x8004, 0
	goto MauvilleCity_Gym_EventScript_PressFloorSwitch
	end

MauvilleCity_Gym_EventScript_Switch2::
	lockall
	goto_if_set FLAG_HOENN_DEFEATED_MAUVILLE_GYM, MauvilleCity_Gym_EventScript_SwitchDoNothing
	goto_if_eq VAR_HOENN_MAUVILLE_GYM_STATE, 2, MauvilleCity_Gym_EventScript_SwitchDoNothing
	setvar VAR_HOENN_MAUVILLE_GYM_STATE, 2
	setvar VAR_0x8004, 1
	goto MauvilleCity_Gym_EventScript_PressFloorSwitch
	end

MauvilleCity_Gym_EventScript_Switch3::
	lockall
	goto_if_set FLAG_HOENN_DEFEATED_MAUVILLE_GYM, MauvilleCity_Gym_EventScript_SwitchDoNothing
	goto_if_eq VAR_HOENN_MAUVILLE_GYM_STATE, 3, MauvilleCity_Gym_EventScript_SwitchDoNothing
	setvar VAR_HOENN_MAUVILLE_GYM_STATE, 3
	setvar VAR_0x8004, 2
	goto MauvilleCity_Gym_EventScript_PressFloorSwitch
	end

MauvilleCity_Gym_EventScript_Switch4::
	lockall
	goto_if_set FLAG_HOENN_DEFEATED_MAUVILLE_GYM, MauvilleCity_Gym_EventScript_SwitchDoNothing
	goto_if_eq VAR_HOENN_MAUVILLE_GYM_STATE, 4, MauvilleCity_Gym_EventScript_SwitchDoNothing
	setvar VAR_HOENN_MAUVILLE_GYM_STATE, 4
	setvar VAR_0x8004, 3
	goto MauvilleCity_Gym_EventScript_PressFloorSwitch
	end

MauvilleCity_Gym_EventScript_PressFloorSwitch::
	special MauvilleGymSetDefaultBarriers
	special MauvilleGymPressSwitch
	special DrawWholeMapView
	playse SE_UNLOCK
	goto_if_set FLAG_HOENN_MAUVILLE_BARRIERS, MauvilleCity_Gym_EventScript_ClearBarriersAltState
	goto_if_unset FLAG_HOENN_MAUVILLE_BARRIERS, MauvilleCity_Gym_EventScript_SetBarriersAltState
	releaseall
	end

MauvilleCity_Gym_EventScript_SwitchDoNothing::
	releaseall
	end

MauvilleCity_Gym_EventScript_SetBarriersAltState::
	setflag FLAG_HOENN_MAUVILLE_BARRIERS
	releaseall
	end

MauvilleCity_Gym_EventScript_ClearBarriersAltState::
	clearflag FLAG_HOENN_MAUVILLE_BARRIERS
	releaseall
	end

@ WATTSON himself: HOENN's second BADGE for a champion starting over
MauvilleCity_Gym_EventScript_Wattson::
	trainerbattle_single TRAINER_HOENN_WATTSON_1, MauvilleCity_Gym_Text_WattsonIntro, MauvilleCity_Gym_Text_WattsonDefeat, MauvilleCity_Gym_EventScript_DefeatedWattson, NO_MUSIC
	goto_if_unset FLAG_HOENN_GOT_TM34_FROM_WATTSON, MauvilleCity_Gym_EventScript_GiveTM34
	goto MauvilleCity_Gym_EventScript_WattsonPostBattle
	end

MauvilleCity_Gym_EventScript_DefeatedWattson::
	setflag FLAG_HOENN_BADGE03_GET
	setflag FLAG_HOENN_DEFEATED_MAUVILLE_GYM
	special MauvilleGymDeactivatePuzzle
	special DrawWholeMapView
	goto_if_ge VAR_HOENN_STAGE1_PROGRESS, 6, MauvilleCity_Gym_EventScript_BadgeText
	setvar VAR_HOENN_STAGE1_PROGRESS, 6
MauvilleCity_Gym_EventScript_BadgeText::
	msgbox MauvilleCity_Gym_Text_WattsonBadge
	goto MauvilleCity_Gym_EventScript_GiveTM34
	end

MauvilleCity_Gym_EventScript_GiveTM34::
	msgbox MauvilleCity_Gym_Text_TakeThisTM
	checkitemspace ITEM_TM34
	goto_if_eq VAR_RESULT, FALSE, MauvilleCity_Gym_EventScript_NoRoomForTM34
	giveitem_msg MauvilleCity_Gym_Text_ReceivedTM34, ITEM_TM34
	setflag FLAG_HOENN_GOT_TM34_FROM_WATTSON
	msgbox MauvilleCity_Gym_Text_ExplainTM34
	release
	end

MauvilleCity_Gym_EventScript_NoRoomForTM34::
	msgbox MauvilleCity_Gym_Text_NoRoomForTM34
	release
	end

@ Event 4: after the BADGE, WATTSON hands over the BASEMENT KEY and asks the
@ champion to find where NEW MAUVILLE is leaking power. Shutting the generator
@ off brings TM24 back here.
MauvilleCity_Gym_EventScript_WattsonPostBattle::
	goto_if_unset FLAG_HOENN_WATTSON_ERRAND, MauvilleCity_Gym_EventScript_WattsonGiveErrand
	goto_if_set FLAG_HOENN_NEW_MAUVILLE_DONE, MauvilleCity_Gym_EventScript_WattsonDone
	goto_if_eq VAR_HOENN_NEW_MAUVILLE_STATE, 2, MauvilleCity_Gym_EventScript_WattsonReward
	msgbox MauvilleCity_Gym_Text_WattsonErrandWaiting
	release
	end

MauvilleCity_Gym_EventScript_WattsonGiveErrand::
	msgbox MauvilleCity_Gym_Text_WattsonErrand
	checkitemspace ITEM_BASEMENT_KEY
	goto_if_eq VAR_RESULT, FALSE, MauvilleCity_Gym_EventScript_NoRoomForKey
	giveitem_msg MauvilleCity_Gym_Text_ReceivedBasementKey, ITEM_BASEMENT_KEY
	setflag FLAG_HOENN_WATTSON_ERRAND
	setflag FLAG_HOENN_GOT_BASEMENT_KEY
	msgbox MauvilleCity_Gym_Text_WattsonErrandWaiting
	release
	end

MauvilleCity_Gym_EventScript_NoRoomForKey::
	msgbox MauvilleCity_Gym_Text_NoRoomForTM34
	release
	end

MauvilleCity_Gym_EventScript_WattsonReward::
	msgbox MauvilleCity_Gym_Text_WattsonThanks
	checkitemspace ITEM_TM24
	goto_if_eq VAR_RESULT, FALSE, MauvilleCity_Gym_EventScript_NoRoomForKey
	giveitem_msg MauvilleCity_Gym_Text_ReceivedTM24, ITEM_TM24
	setflag FLAG_HOENN_NEW_MAUVILLE_DONE
	goto_if_ge VAR_HOENN_STAGE1_PROGRESS, 7, MauvilleCity_Gym_EventScript_WattsonDone
	setvar VAR_HOENN_STAGE1_PROGRESS, 7
MauvilleCity_Gym_EventScript_WattsonDone::
	msgbox MauvilleCity_Gym_Text_WattsonPostBattle
	release
	end

MauvilleCity_Gym_EventScript_LeftGymStatue::
	msgbox MauvilleCity_Gym_Text_GymStatue, MSGBOX_SIGN
	end

MauvilleCity_Gym_EventScript_RightGymStatue::
	msgbox MauvilleCity_Gym_Text_GymStatue, MSGBOX_SIGN
	end
@ END PATCH
