#!/usr/bin/env python3
"""Guarded staged Rocket96 integration; normal-game 64px fallback stays enabled."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil
def sha(b):return hashlib.sha256(b).hexdigest()
def once(text,old,new):
    if text.count(old)!=1:raise ValueError("Patch anchor must occur once: "+old[:80])
    return text.replace(old,new,1)
def in_function(text,name,old,new):
    m=re.search(r"static void "+re.escape(name)+r"\([^;]*?\)\s*\n\{",text)
    if not m:raise ValueError("Function definition missing: "+name)
    end=text.index("\n}",m.end())+2
    return text[:m.start()]+once(text[m.start():end],old,new)+text[end:]
def patch_controller(before):
    if "rocket_trainer_portrait.h" in before or "TryCreateRocketTrainerPortrait" in before:
        raise ValueError("Controller already contains a Rocket portrait patch; inspect it instead of applying again")
    after=once(before,'#include "battle_gfx_sfx_util.h"','#include "battle_gfx_sfx_util.h"\n#include "rocket_trainer_portrait.h"')
    anchor="    DecompressTrainerFrontPic(trainerPicId, gActiveBattler);"
    for name,x,x2,speed,priority,done in (
        ("OpponentHandleDrawTrainerPic",176,"-DISPLAY_WIDTH",2,"GetBattlerSpriteSubpriority(gActiveBattler)","CompleteOnBattlerSpriteCallbackDummy"),
        ("OpponentHandleTrainerSlide",200,"96",-2,"30","CompleteOnBattlerSpriteCallbackDummy2")):
        added=f"    if (TryCreateRocketTrainerPortrait(trainerPicId, {x}, {x2}, {speed},\n"
        added+=f"                                       {priority}, &gBattlerSpriteIds[gActiveBattler]))\n"
        added+="    {\n"+f"        gBattlerControllerFuncs[gActiveBattler] = {done};\n"+"        return;\n    }\n"
        after=in_function(after,name,anchor,added+anchor)
    block="""        FreeTrainerFrontPicPaletteAndTile(gSprites[gBattlerSpriteIds[gActiveBattler]].oam.affineParam);
        gSprites[gBattlerSpriteIds[gActiveBattler]].oam.tileNum = gSprites[gBattlerSpriteIds[gActiveBattler]].data[5];
        FreeSpriteOamMatrix(&gSprites[gBattlerSpriteIds[gActiveBattler]]);
        DestroySprite(&gSprites[gBattlerSpriteIds[gActiveBattler]]);"""
    new="        if (!TryDestroyRocketTrainerPortrait(&gSprites[gBattlerSpriteIds[gActiveBattler]]))\n        {\n"
    new+="".join("    "+line+"\n" for line in block.splitlines())+"        }"
    after=in_function(after,"FreeTrainerSpriteAfterSlide",block,new)
    block="""    FreeTrainerFrontPicPaletteAndTile(sprite->oam.affineParam);
    sprite->oam.tileNum = sprite->data[5];
    FreeSpriteOamMatrix(sprite);
    DestroySprite(sprite);"""
    new="    if (!TryDestroyRocketTrainerPortrait(sprite))\n    {\n"
    new+="".join("    "+line+"\n" for line in block.splitlines())+"    }"
    after=in_function(after,"SpriteCB_FreeOpponentSprite",block,new)
    for name in ("OpponentHandleTrainerSlideBack","OpponentHandleIntroTrainerBallThrow"):
        after=in_function(after,name,"    gSprites[gBattlerSpriteIds[gActiveBattler]].data[2] = 280;",
            "    gSprites[gBattlerSpriteIds[gActiveBattler]].data[2] = GetTrainerPortraitExitX(&gSprites[gBattlerSpriteIds[gActiveBattler]]);")
    for name in ("TryCreateRocketTrainerPortrait","TryDestroyRocketTrainerPortrait","GetTrainerPortraitExitX"):
        assert after.count(name+"(")==2,name
    assert after.count(anchor)==before.count(anchor)==2
    return after

p=argparse.ArgumentParser();p.add_argument("--repo",type=Path,default=Path.cwd())
p.add_argument("--stage",type=Path,required=True);p.add_argument("--expect");p.add_argument("--expect-stage")
p.add_argument("--write",action="store_true");a=p.parse_args();root=a.repo.resolve();stage=a.stage.resolve()
assert stage!=root and stage.is_relative_to(root),"Stage must be an independent directory inside this repository"
names=("include/rocket_trainer_portrait.h","src/rocket_trainer_portrait.c","tools/qa/rocket96_host_check.py")
payload={}
for name in names:
    source=(stage/name).resolve();target=(root/name).resolve()
    assert source.is_relative_to(stage) and target.is_relative_to(root),"Path escaped its root"
    assert source.is_file() and not target.exists() and target.parent.is_dir(),name
    payload[name]=source.read_bytes()
    if name.endswith(".py"):compile(payload[name].decode(),name,"exec")
assert re.search(r"^#define ROCKET_TRAINER_HIRES_ENABLED 0$",payload[names[0]].decode(),re.M),"Default must stay 64px"
target=root/"src/battle_controller_opponent.c";original=target.read_bytes()
patched=patch_controller(original.decode()).encode()
manifest={name:sha(data) for name,data in payload.items()}
stage_sha=sha(json.dumps(manifest,sort_keys=True,separators=(",",":")).encode())
report={"state":"PREFLIGHT_ONLY","before_sha256":sha(original),"after_sha256":sha(patched),
        "stage_manifest_sha256":stage_sha,"core_files":manifest,"native_96_enabled":False,"save_layout_changed":False}
if a.write:
    assert a.expect==sha(original) and a.expect_stage==stage_sha,"Fresh controller and stage SHA are required"
    backup=root/"work/rocket96-apply-v1";assert not backup.exists(),"Prior run preserved"
    assert target.read_bytes()==original
    for name,data in payload.items():assert (stage/name).read_bytes()==data
    backup.mkdir(parents=True)
    (backup/"original-battle_controller_opponent.c").write_bytes(original)
    (backup/"planned-battle_controller_opponent.c").write_bytes(patched)
    (backup/"manifest.json").write_text(json.dumps(report,indent=2))
    for name,data in payload.items():
        with (root/name).open("xb") as f:f.write(data)
    assert target.read_bytes()==original,"Controller changed; original live controller retained"
    temp=backup/"controller-next.c";temp.write_bytes(patched);os.chmod(temp,target.stat().st_mode);os.replace(temp,target)
    assert target.read_bytes()==patched
    report["state"]="APPLIED_WITH_64PX_FALLBACK"
    (backup/"manifest.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
