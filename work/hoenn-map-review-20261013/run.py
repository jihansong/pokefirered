from pathlib import Path
import json,subprocess,hashlib,shutil,time
r=Path('/workspaces/pokefirered');o=r/'work/hoenn-map-review-20261013';o.mkdir(exist_ok=True)
rom=r/'pokemonthyl.gba';s=r/'saves/pokemonthyl_v1.25.sav';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=o/'hoenn-map-QA-only.sav';shutil.copyfile(s,base)
groups=json.loads((r/'data/maps/map_groups.json').read_text());maps=[n for k,values in groups.items() if k.startswith('gMapGroup_Hoenn') for n in values]
assert len(maps)==len(set(maps))
report={'rom':str(rom),'rom_sha256':sha(rom),'source_sav_sha256':sha(s),'maps':maps,'map_count':len(maps),'scope':'one preboot QA spawn per map; entry/walking/crash/black screen checks, not full story traversal or visual art approval','started':time.time()}
(o/'manifest.json').write_text(json.dumps(report,indent=2))
p=subprocess.run(['python3','tools/check_map_integrity.py','--no-upstream','--out',str(o/'static-integrity.txt')],cwd=r,stdout=(o/'static.log').open('w'),stderr=subprocess.STDOUT);report['static_integrity_exit']=p.returncode
args=['python3','tools/qa/mapsmoke_snapshot_fixed.py',*maps,'--rom',str(rom),'--base',str(base),'--frames','240','-j','3','--shots',str(o/'shots'),'--shots-all','--quick']
p=subprocess.run(args,cwd=r,stdout=(o/'mapsmoke.log').open('w'),stderr=subprocess.STDOUT);report['mapsmoke_exit']=p.returncode
assert sha(s)==report['source_sav_sha256'] and sha(rom)==report['rom_sha256']
report['input_sav_and_rom_unchanged']=True;report['finished']=time.time()
(o/'result.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='maps'}))
