RusturfTunnel_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, RusturfTunnel_OnTransition
	.byte 0

RusturfTunnel_EventScript_HItem88::
	finditem ITEM_POKE_BALL
	end

RusturfTunnel_EventScript_HItem89::
	finditem ITEM_MAX_ETHER
	end

RusturfTunnel_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_MIKE_2, RusturfTunnel_Text_H0_0, RusturfTunnel_Text_H0_1
	msgbox RusturfTunnel_Text_H0_2, MSGBOX_AUTOCLOSE
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Z3 E8: the tunnel stays open. The grunt and PEEKO occupy one side of the
@ passage only during the theft, including on CONTINUE from an older save.
.equ LOCALID_RUSTURF_DEVON_GRUNT, 4
.equ LOCALID_RUSTURF_PEEKO, 5

RusturfTunnel_OnTransition::
	special HoennZ3_SetupObjects
	end

RusturfTunnel_EventScript_DevonGrunt::
	goto_if_ne VAR_HOENN_SCENE_DEVON, 2, RusturfTunnel_EventScript_DevonSceneDone
	trainerbattle_single TRAINER_HOENN_GRUNT_RUSTURF_TUNNEL, RusturfTunnel_Text_DevonGruntIntro, RusturfTunnel_Text_DevonGruntDefeat, RusturfTunnel_EventScript_DevonGruntDefeated, NO_MUSIC
	goto RusturfTunnel_EventScript_DevonGruntDefeated
	end

@ A pre-existing trainer win or a full BAG reaches the same reward path.
@ Check the bag itself to recover an interrupted older quest without adding
@ a second key item. A failed add leaves the scene and both objects waiting.
RusturfTunnel_EventScript_DevonGruntDefeated::
	lockall
	checkitem ITEM_DEVON_GOODS
	goto_if_eq VAR_RESULT, TRUE, RusturfTunnel_EventScript_DevonGoodsRecovered
	additem ITEM_DEVON_GOODS
	goto_if_eq VAR_RESULT, FALSE, RusturfTunnel_EventScript_DevonGoodsNoRoom
	msgreceiveditem RusturfTunnel_Text_ReceivedDevonGoods, ITEM_DEVON_GOODS, 1, MUS_OBTAIN_KEY_ITEM
RusturfTunnel_EventScript_DevonGoodsRecovered::
	setflag FLAG_HOENN_GOT_DEVON_GOODS
	goto_if_set FLAG_HOENN_PEEKO_RESCUED, RusturfTunnel_EventScript_KeepBoatPosition
	setvar VAR_HOENN_BRINEY_STATE, BRINEY_AT_ROUTE104
RusturfTunnel_EventScript_KeepBoatPosition::
	setflag FLAG_HOENN_PEEKO_RESCUED
	setvar VAR_HOENN_SCENE_DEVON, 3
	msgbox RusturfTunnel_Text_DevonGruntLeaves
	closemessage
	applymovement LOCALID_RUSTURF_DEVON_GRUNT, RusturfTunnel_Movement_GruntLeaves
	waitmovement 0
	setflag FLAG_HIDE_HOENN_RUSTURF_GRUNT
	removeobject LOCALID_RUSTURF_DEVON_GRUNT
	goto_if_set FLAG_HIDE_HOENN_RUSTURF_PEEKO, RusturfTunnel_EventScript_PeekoSafe
	playmoncry SPECIES_WINGULL, CRY_MODE_NORMAL
	waitmoncry
	applymovement LOCALID_RUSTURF_PEEKO, RusturfTunnel_Movement_PeekoFliesHome
	waitmovement 0
	setflag FLAG_HIDE_HOENN_RUSTURF_PEEKO
	removeobject LOCALID_RUSTURF_PEEKO
RusturfTunnel_EventScript_PeekoSafe::
	msgbox RusturfTunnel_Text_PeekoSafe
	releaseall
	end

RusturfTunnel_EventScript_DevonGoodsNoRoom::
	msgbox RusturfTunnel_Text_DevonGoodsNoRoom
	releaseall
	end

RusturfTunnel_EventScript_Peeko::
	lock
	faceplayer
	playmoncry SPECIES_WINGULL, CRY_MODE_NORMAL
	msgbox RusturfTunnel_Text_Peeko
	waitmoncry
	release
	end

RusturfTunnel_EventScript_DevonSceneDone::
	end

RusturfTunnel_Movement_GruntLeaves:
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

RusturfTunnel_Movement_PeekoFliesHome:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	step_end
@ END PATCH
