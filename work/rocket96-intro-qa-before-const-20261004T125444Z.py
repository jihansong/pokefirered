#!/usr/bin/env python3
"""First native Rocket96 game-render check; battle completion remains separate."""
from pathlib import Path
import argparse,contextlib,hashlib,json,os,struct,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"tools/qa"))
from emu import Emu
import savedit
from gamedata import const
def sha(b):return hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument("--rom",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
a=p.parse_args();a.rom=a.rom.resolve();assert not a.out.exists(),"Fresh QA output required"
raw=(ROOT/"graphics/trainers/front_pics/jessie_james_hires.4bpp").read_bytes()
pal=(ROOT/"graphics/trainers/palettes/jessie_james_hires.gbapal").read_bytes()
assert sha(raw)=="99f3ff74b5438521ba48e4d7fc403acca7df233f003878ddd525bdba8ab14add"
assert sha(pal)=="02951ab3bc6bd04dbce501258a13e92e3ba934728bb8249514b41238f835b792"
rom_sha=sha(a.rom.read_bytes());a.out.mkdir(parents=True)
cases=[json.loads(x) for x in (ROOT/"tools/qa/cases/rocket.jsonl").read_text().splitlines() if x.strip() and not x.lstrip().startswith("#")]
names=("r01_viridian_pc_win","r02_mtmoon_double","r02_mtmoon_single_fallback_same_money")
results=[]
for name in names:
    case=next(c for c in cases if c["name"]==name);base=ROOT/case.get("base","saves/hoenn.sav");before=sha(base.read_bytes())
    row={"case":name,"source_save_sha256_before":before,"pass":False}
    try:
        with tempfile.TemporaryDirectory(prefix="rocket96-intro-") as temp:
            save=Path(temp)/"case.sav";args=[str(base),"-o",str(save)]
            for edit in case["edit"]:args+=edit.split()
            with open(os.devnull,"w") as quiet,contextlib.redirect_stdout(quiet):assert savedit.run(args)==0
            with Emu(str(a.rom),str(save)) as e:
                assert e.u8(e.sym("gRocketTrainerHiresEnabled"))==1,"Review build did not enable Rocket96"
                e.boot_continue();e.run(30);e.walk("UP")
                for n in range(6000):
                    if e.in_battle() and (e.ptr("gBattleMainFunc")&~1)==e.sym("BattleIntroPrintTrainerWantsToBattle"):
                        positions=list(e.sym_read("gBattlerPositions",e.u8(e.sym("gBattlersCount"))))
                        sid=e.u8(e.sym("gBattlerSpriteIds")+positions.index(1));s=e.sym("gSprites")+sid*0x44
                        if sid<64 and struct.unpack("<4h",e.read(s+0x20,8))==(168,56,0,0):break
                    e.hold(*(() if e.in_battle() or n%24>=3 else ("A",)));e.run(1)
                else:raise AssertionError("Settled trainer introduction not reached")
                e.hold();e.run(2)
                assert e.u32(s+0x14)==e.sym("sRocketTemplate") and not(e.u8(s+0x3e)&4)
                flags=e.u32(e.sym("gBattleTypeFlags"));assert bool(flags&const("BATTLE_TYPE_DOUBLE"))==(name=="r02_mtmoon_double")
                attr=e.u16(s+4);tile=attr&1023;bank=attr>>12
                assert e.read(0x06010000+tile*32,4608)==raw,"VRAM differs from reviewed portrait"
                assert e.read(e.sym("gPlttBufferUnfaded")+512+bank*32,32)==pal,"Palette differs from reviewed portrait"
                pieces=[(120,8,0,3,tile,bank),(184,8,2,3,tile+64,bank),(120,72,1,3,tile+96,bank),(184,72,0,2,tile+128,bank)]
                found=[]
                for i in range(128):
                    aa,bb,cc=struct.unpack("<3H",e.read(0x07000000+i*8,6))
                    if ((aa>>8)&3)==2:continue
                    entry=(bb&511,aa&255,aa>>14,bb>>14,cc&1023,cc>>12)
                    if entry in pieces:found.append(entry)
                assert sorted(found)==sorted(pieces),("Missing native 96px OAM pieces",found)
                tiles=struct.unpack("<64H",e.sym_read("sSpriteTileRangeTags",128))
                pals=struct.unpack("<16H",e.sym_read("sSpritePaletteTags",32))
                assert tiles.count(0xD7A0)==pals.count(0xD7A0)==1
                e.shot(str(a.out/(name+".png")),scale=4)
                row.update(pass_=True,frame=e.frame(),sprite_id=sid,oam_pieces=found,native_size=96)
                row["pass"]=row.pop("pass_")
    except Exception as ex:row.update({"pass":False,"error":repr(ex)})
    row["source_save_sha256_after"]=sha(base.read_bytes())
    row["source_save_preserved"]=row["source_save_sha256_after"]==before
    row["pass"]=row["pass"] and row["source_save_preserved"]
    results.append(row);print(json.dumps(row),flush=True)
report={"pass":all(r["pass"] for r in results),"cases":results,"rom_sha256":rom_sha,
        "rom_preserved":sha(a.rom.read_bytes())==rom_sha,"visual_review":"pending",
        "battle_completion_resource_release_verified":False,"new_original_art_created":False}
report["pass"]=report["pass"] and report["rom_preserved"]
(a.out/"result.json").write_text(json.dumps(report,indent=2))
raise SystemExit(0 if report["pass"] else 1)
