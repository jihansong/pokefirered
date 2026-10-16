SkyPillar_4F_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SkyPillar_4F_TY_ClearLooseStones
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Thunder Yellow Sky Pillar safe ascent v1
SkyPillar_4F_TY_ClearLooseStones::
	goto_if_set FLAG_HOENN_SEAFLOOR_CLEARED, SkyPillar_4F_TY_OpenStairs
	goto_if_set FLAG_HOENN_BADGE08_GET, SkyPillar_4F_TY_OpenStairs
	end

SkyPillar_4F_TY_OpenStairs::
	setmetatile 8, 2, 0x235, FALSE
	end
@ END PATCH
