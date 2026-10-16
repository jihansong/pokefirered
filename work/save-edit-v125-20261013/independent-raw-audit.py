import sys,struct,json
from pathlib import Path
from hashlib import sha256
sys.path.insert(0,'/workspaces/pokefirered/tools/qa')
from savefile import SaveFile
r=Path('/workspaces/pokefirered');o=r/'work/save-edit-v125-20261013'
paths=[r/'saves/pokemonthyl_v1.25.sav',o/'pokemonthyl_v1.25-items99-iv2x.sav']
hashes=['53d923bf4668373724b19c9d3c8526b002701606ab7ac082d657ee990e23d7b3','158e50e370b290fccec6e8a09dda79001cab312c5ebe4de31ee245bb846ecef5']
for p,h in zip(paths,hashes):assert sha256(p.read_bytes()).hexdigest()==h
old,new=map(lambda p:SaveFile(str(p)),paths)
assert old.party_count()==new.party_count()==6 and old.sb2==new.sb2
assert len(old.blocks['storage'])==33744 and old.blocks['storage']==new.blocks['storage']
misc=(3,2,3,2,1,1,3,2,3,2,1,1,3,2,3,2,1,1,0,0,0,0,0,0)
u32=lambda z,o:struct.unpack_from('<I',z,o)[0]
def plain(z):return struct.pack('<12I',*(v^u32(z,0)^u32(z,4) for v in struct.unpack_from('<12I',z,32)))
checked=[]
for i in range(6):
 x,y=(s.sb1[56+100*i:156+100*i] for s in (old,new))
 if x==y:continue
 assert len(x)==len(y)==100 and u32(x,4)==2839214970
 off=36+12*misc[u32(x,0)%24];allowed=set(range(28,30))|set(range(off,off+4))|set(range(86,100))
 assert all(x[j]==y[j] for j in range(100) if j not in allowed)
 for z in (x,y):assert sum(struct.unpack('<24H',plain(z)))&65535==struct.unpack_from('<H',z,28)[0]
 v0,v1=(u32(plain(z),off-32) for z in (x,y))
 assert v1==((v0&0xc0000000)|sum(min(31,(((v0>>(5*j))&31)*2))<<(5*j) for j in range(6)))
 checked.append({'party_slot':i+1,'pid':u32(x,0),'ivs_before':[(v0>>(5*j))&31 for j in range(6)],'ivs_after':[(v1>>(5*j))&31 for j in range(6)]})
assert len(checked)==4
result={'pass':True,'checked':checked,'storage_and_sb2_unchanged':True,'independent_12_u32_xor_checksum':True,'no_Mon_subs_reuse':True}
(o/'independent-raw-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
