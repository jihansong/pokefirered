from pathlib import Path
import argparse,hashlib
p=argparse.ArgumentParser();p.add_argument('--expect-source',required=True);a=p.parse_args()
source=Path("tools/qa/rocket96_intro_check.py")
dest=Path("tools/qa/rocket96_finish_check.py")
original=source.read_bytes()
assert hashlib.sha256(original).hexdigest()==a.expect_source,"Intro QA changed since review"
assert not dest.exists(),"Existing finish check preserved"
s=original.decode()
def replace_once(old,new):
    global s
    assert s.count(old)==1,old
    s=s.replace(old,new,1)
replace_once('p.add_argument("--out",type=Path,required=True)\n','p.add_argument("--out",type=Path,required=True);p.add_argument("--finish",action="store_true")\n')
replace_once("results=[]\n",'if a.finish:names+=("r01_viridian_pc_lose_continues",)\nresults=[]\n')
addition='''
                if a.finish:
                    departed=False;outro=False
                    for frame in range(30000):
                        e.hold(*(("A",) if frame%16<2 else ()));e.run(1)
                        assert not e.reset_seen(),"Game reset during trainer battle"
                        tags=struct.unpack("<64H",e.sym_read("sSpriteTileRangeTags",128)).count(0xD7A0)
                        banks=struct.unpack("<16H",e.sym_read("sSpritePaletteTags",32)).count(0xD7A0)
                        if tags==banks==0:departed=True
                        if departed and not outro and tags==banks==1:
                            positions=list(e.sym_read("gBattlerPositions",e.u8(e.sym("gBattlersCount"))))
                            oi=e.u8(e.sym("gBattlerSpriteIds")+positions.index(1));op=e.sym("gSprites")+oi*0x44
                            if oi<64 and e.u32(op+0x14)==e.sym("sRocketTemplate") and struct.unpack("<4h",e.read(op+0x20,8))==(192,56,0,0):
                                oa=e.u16(op+4);ot=oa&1023;ob=oa>>12
                                assert e.read(0x06010000+ot*32,4608)==raw
                                assert e.read(e.sym("gPlttBufferUnfaded")+512+ob*32,32)==pal
                                e.hold();e.run(2)
                                want=[(144,8,0,3,ot,ob),(208,8,2,3,ot+64,ob),(144,72,1,3,ot+96,ob),(208,72,0,2,ot+128,ob)];got=[]
                                for index in range(128):
                                    x,y,z=struct.unpack("<3H",e.read(0x07000000+index*8,6))
                                    item=(y&511,x&255,x>>14,y>>14,z&1023,z>>12)
                                    if ((x>>8)&3)!=2 and item in want:got.append(item)
                                assert sorted(got)==sorted(want),"Defeat portrait OAM clipped or missing"
                                e.shot(str(a.out/(name+"-defeat.png")),scale=4);outro=True
                        if e.field_idle():
                            e.hold();e.run(30)
                            if e.field_idle():break
                    else:raise AssertionError("Battle did not return to the field")
                    assert departed,"Intro resources never released"
                    assert struct.unpack("<64H",e.sym_read("sSpriteTileRangeTags",128)).count(0xD7A0)==0
                    assert struct.unpack("<16H",e.sym_read("sSpritePaletteTags",32)).count(0xD7A0)==0
                    assert not any((e.u8(e.sym("gSprites")+i*0x44+0x3e)&1) and e.u32(e.sym("gSprites")+i*0x44+0x14)==e.sym("sRocketTemplate") for i in range(64))
                    assert outro or "lose" in name,"Win did not exercise the defeat portrait"
                    e.shot(str(a.out/(name+"-returned.png")),scale=4)
                    row.update(intro_resources_released=True,battle_returned_to_field=True,defeat_portrait_verified=outro,final_resources_released=True)
'''
anchor='                row["pass"]=row.pop("pass_")\n'
replace_once(anchor,anchor+addition)
replace_once('"battle_completion_resource_release_verified":False','"battle_completion_resource_release_verified":a.finish and all(r["pass"] for r in results)')
compile(s,str(dest),"exec")
assert source.read_bytes()==original
with dest.open("x",encoding="utf-8",newline="\n") as f:f.write(s)
print(dest,hashlib.sha256(s.encode()).hexdigest())
