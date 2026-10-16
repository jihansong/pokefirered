@ Z3 E8: DEVON's delivery is stolen only after the woods and the STONE BADGE.
@ Append objects so old object IDs and saved maps keep their meaning.
.equ LOCALID_RUSTBORO_DEVON_THIEF, 13
.equ LOCALID_RUSTBORO_DEVON_WORKER, 14

RustboroCity_OnTransition::
	setflag FLAG_HOENN_WORLD_MAP_RUSTBORO_CITY
	special HoennZ3_SetupObjects
	end

RustboroCity_EventScript_DevonTheft::
	goto_if_ne VAR_HOENN_SCENE_DEVON, 1, RustboroCity_EventScript_DevonSceneDone
	goto_if_unset FLAG_HOENN_BADGE01_GET, RustboroCity_EventScript_DevonSceneDone
	lockall
	applymovement LOCALID_RUSTBORO_DEVON_WORKER, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox RustboroCity_Text_DevonStopThief
	closemessage
	playbgm MUS_ENCOUNTER_AQUA, FALSE
	applymovement LOCALID_RUSTBORO_DEVON_WORKER, RustboroCity_Movement_WorkerPushed
	waitmovement 0
	msgbox RustboroCity_Text_DevonThief
	closemessage
	applymovement LOCALID_RUSTBORO_DEVON_THIEF, RustboroCity_Movement_ThiefRunsNorth
	waitmovement 0
	setvar VAR_HOENN_SCENE_DEVON, 2
	setflag FLAG_HIDE_HOENN_RUSTBORO_THIEF
	removeobject LOCALID_RUSTBORO_DEVON_THIEF
	applymovement LOCALID_RUSTBORO_DEVON_WORKER, RustboroCity_Movement_WorkerRecovers
	waitmovement 0
	fadedefaultbgm
	msgbox RustboroCity_Text_DevonChase
	releaseall
	end

RustboroCity_EventScript_DevonSceneDone::
	end

RustboroCity_EventScript_DevonWorker::
	lock
	faceplayer
	goto_if_eq VAR_HOENN_SCENE_DEVON, 2, RustboroCity_EventScript_DevonWaiting
	goto_if_ge VAR_HOENN_SCENE_DEVON, 3, RustboroCity_EventScript_DevonRecovered
	msgbox RustboroCity_Text_DevonDelivery
	release
	end

RustboroCity_EventScript_DevonWaiting::
	msgbox RustboroCity_Text_DevonChase
	release
	end

@ E12: the second GREAT BALL is the RUSTBORO employee's own reward.
RustboroCity_EventScript_DevonRecovered::
	goto_if_set FLAG_HOENN_GOT_RUSTBORO_GREAT_BALL, RustboroCity_EventScript_DevonAfterReward
	msgbox RustboroCity_Text_DevonRecovered
	giveitem ITEM_GREAT_BALL
	goto_if_eq VAR_RESULT, FALSE, RustboroCity_EventScript_DevonBagFull
	setflag FLAG_HOENN_GOT_RUSTBORO_GREAT_BALL
RustboroCity_EventScript_DevonAfterReward::
	msgbox RustboroCity_Text_DevonAfterReward
	release
	end

RustboroCity_EventScript_DevonBagFull::
	msgbox RustboroCity_Text_DevonBagFull
	release
	end

RustboroCity_Movement_WorkerPushed:
	walk_fast_down
	walk_in_place_faster_up
	step_end

RustboroCity_Movement_WorkerRecovers:
	walk_up
	walk_in_place_faster_right
	step_end

RustboroCity_Movement_ThiefRunsNorth:
	walk_fast_left
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end
