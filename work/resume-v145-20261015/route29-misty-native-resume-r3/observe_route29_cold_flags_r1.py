import json,hashlib
from pathlib import Path
source=Path("work/resume-v145-20261015/route29-misty-native-resume-r3/native_misty_walk_qa_r10.py").read_text()
assert hashlib.sha256(source.encode()).hexdigest()=="4fe78a90ea3a8a88603200be92a69b2660d63d61fa345d4a3e36c5c9ffe3b7bc"
marker="try:"+chr(10)+"    for direction in"
assert source.count(marker)==1
exec(compile(source.split(marker)[0],"<verified-r10-readonly-prefix>","exec"))
q=root/"work/resume-v145-20261015/native-Route29-independent-r6/Route29-road-save-cold-native-QA-only.sav"
qh=qa_hash_bytes(q.read_bytes()); original=SaveFile(str(q)); lo=off("sb2.hoennFlags"); hi=off("sb2.hoennVars"); before=bytes(original.sb2[lo:hi])
e=ReadOnlyEmu(str(rom),str(q),sym=""); e.syms=syms
try:
    e.boot_continue(); settle(e); e.run(40); safe(e); after=bytes(blocks(e).sb2[lo:hi]); changes=[dict(offset=i,before=x,after=y,xor=x^y,changed_bits=[i*8+k for k in range(8) if (x^y)&(1<<k)]) for i,(x,y) in enumerate(zip(before,after)) if x!=y]; e.shot(str(out/"cold-field.png"),scale=4)
finally:
    e.close()
assert qa_hash_bytes(q.read_bytes())==qh and all(qa_hash_bytes(f.read_bytes())==h for f,h in inputs.items())
answer=dict(qa_saved_file=str(q),qa_saved_sha256=qh,location=e.location() if e.h else "closed",offset=lo,length=len(before),before_hex=before.hex(),after_hex=after.hex(),changes=changes,source_qa_and_original_inputs_unchanged=True,RAM_writes=0,direct_engine_calls=0,state_loads=0)
(out/"cold-flag-diff.json").write_text(json.dumps(answer,indent=2)); print(json.dumps(answer,indent=2))
