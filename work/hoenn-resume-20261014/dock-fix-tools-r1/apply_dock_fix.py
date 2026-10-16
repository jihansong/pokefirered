"""Apply only the five reviewed dock-script changes; never build or edit saves."""
from pathlib import Path
import argparse,hashlib,json,shutil
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--package',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();root=a.root.resolve(strict=True);package=a.package.resolve(strict=True);out=a.out.resolve()
 assert out.is_relative_to(root/'work') and not out.exists(),'Use a fresh backed-up result directory'
 m=json.loads((package/'patch-manifest.json').read_text());assert m['status']=='REVIEWED_CANDIDATE_NOT_APPLIED' and len(m['files'])==5
 rp=root/m['confirmed_native_trap_report']['path'];assert sha(rp)==m['confirmed_native_trap_report']['sha256'];r=json.loads(rp.read_text())
 assert r['status']=='confirmed_gameplay_blocker' and r['native_four_direction_dock_trap_confirmed'] and r['protected_original_inputs_unchanged']
 assert all(r[k]==0 for k in ['RAM_writes','direct_script_calls','forced_battle_outcomes'])
 assert len(r['dock_direction_probes'])==4 and {v['key']for v in r['dock_direction_probes']}=={'UP','DOWN','LEFT','RIGHT'}
 assert all(v['blocked']and v['actual_keys']and v['start']==[43,11,13,9]and v['finish']==v['start']and v['field_idle']for v in r['dock_direction_probes'])
 assert sha(root/'pokemonthyl.gba')==r['ROM_sha256'] and sha(root/'pokemonthyl.elf')==r['ELF_sha256'],'Build changed since the genuine blocker report; review first'
 sp=root/m['original_natural_SAVE']['path'];assert sha(sp)==m['original_natural_SAVE']['sha256']
 targets={}
 for rel,h in m['files'].items():
  dst=(root/rel).resolve(strict=True);src=(package/rel).resolve(strict=True)
  assert dst.is_relative_to(root) and src.is_relative_to(package)
  assert sha(dst)==h['before_sha256']and sha(src)==h['after_sha256'],('Source/payload changed',rel)
  targets[dst]=(src,h)
 protected=set((root/'saves').rglob('*.sav'))|{root/'pokemonthyl.gba',root/'pokemonthyl.elf',rp,sp}
 protected|={f for sub in ['data/maps','data/layouts']for f in (root/sub).rglob('*')if f.is_file()and f.resolve()not in targets}
 frozen={f:sha(f)for f in protected};out.mkdir(parents=True)
 for dst in targets:
  backup=out/'before'/dst.relative_to(root);backup.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(dst,backup)
 result={'status':'applying','source_files':m['files'],'protected_save_count':len(list((root/'saves').rglob('*.sav'))),'product_maps_and_original_saves_changed':False,'built':False,'native_postfix_verified':False}
 (out/'application.json').write_text(json.dumps(result,indent=2)+'\n')
 for dst,(src,h)in targets.items():shutil.copyfile(src,dst);assert sha(dst)==h['after_sha256']
 assert all(f.exists()and sha(f)==h for f,h in frozen.items()),'Protected map/layout/ROM/ELF/SAV changed during source application'
 result.update(status='applied_not_built',protected_input_count=len(frozen),all_original_and_synced_saves_preserved=True)
 (out/'application.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
