#!/usr/bin/env python3
"""Connect existing Dive assets/warps to field UI; no save-layout changes."""
from pathlib import Path
import datetime, hashlib, json, shutil, subprocess, sys
ROOT=Path.cwd().resolve();pending={}
def source(p):return pending.get(p,(ROOT/p).read_text(encoding='utf-8'))
def replace(p,old,new):
 s=source(p)
 if new in s:
  return
 assert s.count(old)==1,(p,'anchor count',s.count(old),old[:80])
 pending[p]=s.replace(old,new,1)
def before(p,anchor,new):
 s=source(p)
 if new.strip() in s:return
 assert s.count(anchor)==1,(p,anchor)
 pending[p]=s.replace(anchor,new+anchor,1)
replace('include/constants/party_menu.h',
 '#define FIELD_MOVE_END          12',
 '#define FIELD_MOVE_DIVE         12\n#define FIELD_MOVE_END          13')
p='src/data/party_menu.h'
before(p,'static const u8 *const sFieldMoveDescriptionTable[] =',
 'static const u8 sText_DiveBelowSurface[] = _("Explore underwater.");\n\n')
replace(p,'    [FIELD_MOVE_SWEET_SCENT] = gText_LureWildPokemon,',
 '    [FIELD_MOVE_SWEET_SCENT] = gText_LureWildPokemon,\n    [FIELD_MOVE_DIVE]        = sText_DiveBelowSurface,')
replace(p,'    [CURSOR_OPTION_FIELD_MOVES + FIELD_MOVE_SWEET_SCENT] = {gMoveNames[MOVE_SWEET_SCENT], CursorCB_FieldMove},',
 '    [CURSOR_OPTION_FIELD_MOVES + FIELD_MOVE_SWEET_SCENT] = {gMoveNames[MOVE_SWEET_SCENT], CursorCB_FieldMove},\n    [CURSOR_OPTION_FIELD_MOVES + FIELD_MOVE_DIVE]        = {gMoveNames[MOVE_DIVE],        CursorCB_FieldMove},')
replace(p,'MOVE_DIG, MOVE_MILK_DRINK, MOVE_SOFT_BOILED, MOVE_SWEET_SCENT, FIELD_MOVE_END',
 'MOVE_DIG, MOVE_MILK_DRINK, MOVE_SOFT_BOILED, MOVE_SWEET_SCENT, MOVE_DIVE, FIELD_MOVE_END')
replace(p,'    [FIELD_MOVE_SWEET_SCENT]  = {SetUpFieldMove_SweetScent,  PARTY_MSG_CANT_USE_HERE},',
 '    [FIELD_MOVE_SWEET_SCENT]  = {SetUpFieldMove_SweetScent,  PARTY_MSG_CANT_USE_HERE},\n    [FIELD_MOVE_DIVE]         = {SetUpFieldMove_Dive,        PARTY_MSG_CANT_USE_HERE},')
p='src/party_menu.c'
before(p,'#include "field_effect.h"','#include "field_control_avatar.h"\n')
replace(p,'static bool8 SetUpFieldMove_Surf(void);',
 'static bool8 SetUpFieldMove_Surf(void);\nstatic bool8 SetUpFieldMove_Dive(void);')
replace(p,'if (fieldMove <= FIELD_MOVE_WATERFALL && FlagGet(FLAG_BADGE01_GET + fieldMove) != TRUE)',
 '''if ((fieldMove <= FIELD_MOVE_WATERFALL && FlagGet(FLAG_BADGE01_GET + fieldMove) != TRUE)
         || (fieldMove == FIELD_MOVE_DIVE && gMapHeader.mapType != MAP_TYPE_UNDERWATER
          && !FlagGet(FLAG_HOENN_BADGE07_GET)))''')
before(p,'static void DisplayCantUseSurfMessage(void)\n{',r'''static void FieldCallback_Dive(void)
{
    gFieldEffectArguments[0] = GetCursorSelectionMonId();
    gFieldEffectArguments[1] = 0;
    FieldEffectStart(FLDEFF_USE_DIVE);
}

static bool8 SetUpFieldMove_Dive(void)
{
    // Surfacing remains available for legacy saves already underwater.
    if (gMapHeader.mapType != MAP_TYPE_UNDERWATER
     && !FlagGet(FLAG_HOENN_BADGE07_GET))
        return FALSE;
    if (TrySetDiveWarp() == 0)
        return FALSE;
    gFieldCallback2 = FieldCallback_PrepareFadeInFromMenu;
    gPostMenuFieldCallback = FieldCallback_Dive;
    return TRUE;
}

''')
replace(p,'for (i = 0; i < NUM_HIDDEN_MACHINES - 1; ++i) // no dive',
 'for (i = 0; i < NUM_HIDDEN_MACHINES; ++i)')
before('include/field_control_avatar.h',
 'bool8 dive_warp(struct MapPosition * pos, u16 behavior);',
 'u8 TrySetDiveWarp(void);\n')
before('include/event_scripts.h',
 'extern const u8 EventScript_UseSurf[];',
 'extern const u8 EventScript_DeepWater[];\nextern const u8 EventScript_CantDive[];\nextern const u8 EventScript_TrySurface[];\nextern const u8 EventScript_ObstacleCantSurface[];\n')
p='src/field_control_avatar.c'
replace(p,'static u8 TrySetDiveWarp(void)\n{','u8 TrySetDiveWarp(void)\n{')
# Gate the actual warp too, so direct script use cannot bypass entry requirements.
replace(p,'''    else if (MetatileBehavior_IsDiveable(metatileBehavior) == TRUE)
    {
        if (SetDiveWarpDive(position->x - MAP_OFFSET, position->y - MAP_OFFSET))''',
 '''    else if (TestPlayerAvatarFlags(PLAYER_AVATAR_FLAG_SURFING)
          && FlagGet(FLAG_HOENN_BADGE07_GET)
          && MetatileBehavior_IsDiveable(metatileBehavior) == TRUE)
    {
        if (SetDiveWarpDive(position->x - MAP_OFFSET, position->y - MAP_OFFSET))''')
replace(p,'''    else if (MetatileBehavior_IsDiveable(metatileBehavior) == TRUE)
    {
        if (SetDiveWarpDive(x - MAP_OFFSET, y - MAP_OFFSET) == TRUE)''',
 '''    else if (TestPlayerAvatarFlags(PLAYER_AVATAR_FLAG_SURFING)
          && MetatileBehavior_IsDiveable(metatileBehavior) == TRUE)
    {
        if (SetDiveWarpDive(x - MAP_OFFSET, y - MAP_OFFSET) == TRUE)''')
replace(p,'''        else
            return EventScript_CantUseWaterfall;
    }
    return NULL;
}''', '''        else
            return EventScript_CantUseWaterfall;
    }
    if (gMapHeader.mapType == MAP_TYPE_UNDERWATER)
    {
        if (TrySetDiveWarp() == 1)
            return EventScript_TrySurface;
        return EventScript_ObstacleCantSurface;
    }
    if (TestPlayerAvatarFlags(PLAYER_AVATAR_FLAG_SURFING) && TrySetDiveWarp() == 2)
    {
        if (FlagGet(FLAG_HOENN_BADGE07_GET))
            return EventScript_DeepWater;
        return EventScript_CantDive;
    }
    return NULL;
}''')
replace('data/scripts/field_moves.inc',
 '''EventScript_DeepWater::
\tlockall
\tcheckpartymove MOVE_DIVE''',
 '''EventScript_DeepWater::
\tlockall
\tgoto_if_unset FLAG_HOENN_BADGE07_GET, EventScript_MayGoUnderwater
\tcheckpartymove MOVE_DIVE''')
p='src/field_effect.c'
replace(p,'''        dive_warp(&pos, gObjectEvents[gPlayerAvatar.objectEventId].currentMetatileBehavior);
        DestroyTask(FindTaskIdByFunc(Task_UseDive));''',
 '''        if (!dive_warp(&pos, gObjectEvents[gPlayerAvatar.objectEventId].currentMetatileBehavior))
        {
            gPlayerAvatar.preventStep = FALSE;
            UnlockPlayerFieldControls();
        }
        DestroyTask(FindTaskIdByFunc(Task_UseDive));''')
p='src/overworld.c'
replace(p,'''    s32 i;
    s32 count = gMapHeader.connections->count;
    const struct MapConnection *connection = gMapHeader.connections->connections;

    if (connection == NULL)''',
 '''    s32 i;
    s32 count;
    const struct MapConnection *connection;

    if (gMapHeader.connections == NULL)
        return NULL;
    count = gMapHeader.connections->count;
    connection = gMapHeader.connections->connections;
    if (connection == NULL)''')
p='src/field_player_avatar.c'
replace(p,'''static void PlayerAvatarTransition_Underwater(struct ObjectEvent * playerObjEvent)
{

}''', '''static void PlayerAvatarTransition_Underwater(struct ObjectEvent * playerObjEvent)
{
    // Reuse the player's approved native riding graphics without a surface wake.
    ObjectEventSetGraphicsId(playerObjEvent, GetPlayerAvatarGraphicsIdByStateId(PLAYER_AVATAR_GFX_RIDE));
    ObjectEventTurn(playerObjEvent, playerObjEvent->movementDirection);
    SetPlayerAvatarStateMask(PLAYER_AVATAR_FLAG_UNDERWATER);
}''')
replace(p,'''    if (gPlayerAvatar.flags & PLAYER_AVATAR_FLAG_SURFING)
    {
        // Same speed as running''',
 '''    if (gPlayerAvatar.flags & (PLAYER_AVATAR_FLAG_SURFING | PLAYER_AVATAR_FLAG_UNDERWATER))
    {
        // Same speed as running''')
replace(p,'''    u8 flags = gPlayerAvatar.flags;

    for (i = 0; i < NELEMS(*sPlayerAvatarGfxToStateFlag); i++)''',
 '''    u8 flags = gPlayerAvatar.flags;

    if (flags & PLAYER_AVATAR_FLAG_UNDERWATER)
        return GetPlayerAvatarGraphicsIdByStateId(PLAYER_AVATAR_GFX_RIDE);
    for (i = 0; i < NELEMS(*sPlayerAvatarGfxToStateFlag); i++)''')
replace(p,'''    u8 unk = GetPlayerAvatarStateTransitionByGraphicsId(graphicsId, gPlayerAvatar.gender);

    gPlayerAvatar.transitionFlags |= unk | extras;''',
 '''    u8 unk = GetPlayerAvatarStateTransitionByGraphicsId(graphicsId, gPlayerAvatar.gender);

    if (gMapHeader.mapType == MAP_TYPE_UNDERWATER)
        unk = PLAYER_AVATAR_FLAG_UNDERWATER;
    gPlayerAvatar.transitionFlags |= unk | extras;''')
replace('src/bike.c',
 'else if (gPlayerAvatar.flags & (PLAYER_AVATAR_FLAG_SURFING | PLAYER_AVATAR_FLAG_DASH))',
 'else if (gPlayerAvatar.flags & (PLAYER_AVATAR_FLAG_SURFING | PLAYER_AVATAR_FLAG_UNDERWATER | PLAYER_AVATAR_FLAG_DASH))')
p='src/quest_log_events.c'
before(p,'static const u8 *const sUsedFieldMoveTexts[] =',
 'static const u8 sText_QuestLogUsedDive[] = _("{STR_VAR_1} used DIVE to\\nexplore the sea.\\p");\n\n')
replace(p,'    [FIELD_MOVE_SWEET_SCENT] = gText_QuestLog_UsedSweetScent\n',
 '    [FIELD_MOVE_SWEET_SCENT] = gText_QuestLog_UsedSweetScent,\n    [FIELD_MOVE_DIVE]        = sText_QuestLogUsedDive\n')

# These two differently sized cave maps cannot use an offset-0 connection.
# Preserve the imported door warps; only native Dive/emerge gets fixed coordinates.
dive_maps=[
 ('Underwater_SeafloorCavern','MAP_SEAFLOOR_CAVERN_ENTRANCE',10,16),
 ('SeafloorCavern_Entrance','MAP_UNDERWATER_SEAFLOOR_CAVERN',6,6)]
marker='@ Thunder Yellow native Dive v1'
for name,dest,x,y in dive_maps:
 values={
  'mapscripts':marker+'\n\tmap_script MAP_SCRIPT_ON_DIVE_WARP, '+name+'_NativeDiveWarp\n',
  'scripts.inc':marker+'\n'+name+'_NativeDiveWarp::\n\tsetdivewarp '+dest+', '+str(x)+', '+str(y)+'\n\tend\n'}
 for suffix,text in values.items():
  p='tools/hoenn_import/patches/'+name+'.'+suffix
  if (ROOT/p).exists():
   assert (ROOT/p).read_text(encoding='utf-8')==text,('Existing unrelated canonical Dive patch',p)
  pending[p]=text

# Commit only after every source anchor has matched.
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=ROOT/'work/native-dive-v1-backups'/stamp
originals=set(pending)
for name,_,_,_ in dive_maps:
 originals.update('data/maps/'+name+'/'+f for f in ['map.json','scripts.inc','text.inc'])
for p in originals:
 if (ROOT/p).exists():
  dest=backup/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/p,dest)
for p,s in pending.items():
 target=ROOT/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(s,encoding='utf-8')
subprocess.run([sys.executable,'tools/hoenn_import/apply_patches.py']+[m[0] for m in dive_maps],check=True)
receipt={'source_only':True,'save_layout_changed':False,'fixed_ewram_added':0,
 'runtime_validated':False,'files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in pending}}
(backup/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'changed_files':len(pending),'backup':str(backup),'runtime_validated':False}))

