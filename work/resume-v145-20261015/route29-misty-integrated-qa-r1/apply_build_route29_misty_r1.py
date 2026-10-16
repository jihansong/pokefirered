"""Guarded four-input Route29/Misty candidate apply, build and native QA.

No rollback, deletion, push, publishing, user-SAV mutation or save-state loading.
Without --apply this checks inputs and writes a review report only. Root owns execution.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,shutil,subprocess,sys,traceback

ap=argparse.ArgumentParser()
for key in ('root','sav','out'):ap.add_argument('--'+key,type=Path,required=True)
ap.add_argument('--apply',action='store_true');ap.add_argument('--native',action='store_true')
ap.add_argument('--jobs',type=int,default=2)
a=ap.parse_args();root=a.root.resolve(strict=True);out=a.out.resolve();pkg=Path(__file__).resolve().parent
assert out.is_relative_to(root/'work') and not out.exists() and 1<=a.jobs<=8
assert not a.native or a.apply
H=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
plan=json.loads((pkg/'payload-manifest.json').read_text())
package_files=json.loads((pkg/'bundle-files.json').read_text())
for rel,want in package_files.items():assert H(pkg/rel)==want,('Package changed',rel)
assert set(plan['product_inputs'])=={'data/layouts/JohtoRoute29/map.bin','tools/johto/build_entry.py','tools/johto/route29_landscape_boundaries.py','graphics/object_events/pics/people/misty_companion_season1.png'}
ROM,ELF=root/'pokemonthyl.gba',root/'pokemonthyl.elf';sav=a.sav.resolve(strict=True)
assert H(ROM)==plan['baseline_ROM_sha256'] and H(ELF)==plan['baseline_ELF_sha256']
for rel,row in plan['product_inputs'].items():
    target=(root/rel).resolve();assert target.is_relative_to(root)
    assert H(pkg/'payload'/rel)==row['after_sha256']
    if row['before_sha256'] is None:assert not target.exists(),('New helper path already exists: review before replacing',rel)
    else:assert target.is_file() and H(target)==row['before_sha256'],('Product input before SHA changed',rel)
for rel,want in plan['guarded_sources'].items():assert H(root/rel)==want,('Preserved source changed',rel)
for rel,want in plan['protected_user_saves_expected'].items():assert H(root/rel)==want,('Uploaded user SAV differs; refresh inputs instead of overwriting',rel)
# Fail before product edits if a proven native dependency has changed.
helpers={'tools/qa/native_misty_basic_qa.py':'5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6',
         'tools/qa/johto_violet_native_bootstrap_v1.py':'83c4557b96c344b241fc6f79e9b17722acfc0b0e81e0f9e6d649ff5d8b1c84bb',
         'tools/qa/emu.py':'c8d3ba672d7ecc84dcefab513d84223f410e9d8cb43081cee4b37555e1378e69',
         'tools/qa/savefile.py':'e6cc1acb8569dbdca6d1b7b095835a5271c9e16de9d2fa3f976d15b50b9b7daa',
         'tools/qa/gamedata.py':'acaa4654ed889dc4f98f6c20dc26a85ea8d35963a771967c159ca4edc26a7ab3',
         'tools/qa/hoenn_gauntlet_save_qa.py':'b22478d2eac54849a6f5e8effdbb8ad67f5a3a34cc3da02dd63db39f0ad1941b'}
for rel,want in helpers.items():assert H(root/rel)==want,('Existing safety helper changed; inspect instead of relaxing',rel)
verify=pkg/'verify_build.py';assert H(verify)=='40647f774f3e470ffc29b29f82ef2fb188c0473d983f87f72d6d7e3d1642c200'
vspec=importlib.util.spec_from_file_location('readonly_rom_elf_verifier',verify)
v=importlib.util.module_from_spec(vspec);sys.modules[vspec.name]=v;vspec.loader.exec_module(v)
expected_native,palette=v.encode_png(pkg/'payload/graphics/object_events/pics/people/misty_companion_season1.png',root/'graphics/object_events/palettes/player.pal')
assert hashlib.sha256(expected_native).hexdigest()==plan['compiled_misty_sha256']
out.mkdir(parents=True);os.chdir(root)
protected={p.resolve():H(p) for p in set((root/'saves').rglob('*.sav'))|{sav}}
protected.update({(root/rel).resolve():want for rel,want in plan['guarded_sources'].items()})
protected.update({(root/rel).resolve():want for rel,want in helpers.items()})
protected.update({p.resolve():H(p) for p in (root/'include').rglob('*.h')})
# Preserve unrelated already-dirty tracked source content across the build.
dirty=subprocess.check_output(['git','diff','--name-only','-z'],cwd=root).decode().split('\0')
for rel in filter(None,dirty):
    path=(root/rel).resolve()
    if rel not in plan['product_inputs'] and path.is_file() and path.suffix not in ('.gba','.elf','.map','.sym'):
        protected[path]=H(path)
(out/'baseline-git-status.bin').write_bytes(subprocess.check_output(['git','status','--porcelain=v1','-z'],cwd=root))
report={'status':'PREFLIGHT_RUNNING','pass':False,'product_inputs_applied':[],'build_commands':[],
        'native_tests':[],'user_SAV_changed':False,'automatic_rollback':False,'files_deleted':0,
        'natural_story_completion_proved':False,'full_Johto_Hoenn_completed':False,
        'baseline_ROM_sha256':H(ROM),'baseline_ELF_sha256':H(ELF),'input_SAV_sha256':H(sav)}
def emit():(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
def run(command,name):
    log=out/(name+'.log')
    with log.open('wb') as stream:process=subprocess.run(command,cwd=root,stdout=stream,stderr=subprocess.STDOUT)
    row={'command':list(map(str,command)),'returncode':process.returncode,'log':str(log),'log_sha256':H(log)}
    assert process.returncode==0,('Command failed; edits/backups retained, no automatic rollback',row)
    return row
try:
    sys.path.insert(0,str(root/'tools/qa'));import gamedata as gd
    gd.CACHE=str(out/'compiler-cache');gd._OFFSETS=None
    gd.FIELDS.update({'qa.layout.map':('MapLayout','map'),'qa.layout.width':('MapLayout','width'),'qa.layout.height':('MapLayout','height')})
    gd._OFFSETS=None
    offsets={k:gd.off(k) for k in ('qa.layout.map','qa.layout.width','qa.layout.height','sb1','sb2','storage','pokemon','boxmon')}
    assert [offsets[k] for k in ('sb1','sb2','storage','pokemon','boxmon')]==[15720,3876,33744,100,80]
    (out/'current-compiler-offsets.json').write_text(json.dumps(offsets,indent=2)+'\n')
    if not a.apply:
        report.update(**{'pass':True},status='FOUR_INPUT_PREFLIGHT_PASS_NO_PRODUCT_EDITS');emit()
    else:
        backup=out/'backup';backup.mkdir()
        originals={'pokemonthyl.gba':H(ROM),'pokemonthyl.elf':H(ELF)}
        for rel,row in plan['product_inputs'].items():
            if row['before_sha256'] is not None:originals[rel]=row['before_sha256']
        for rel in ('pokemonthyl.sym','pokemonthyl.map'):
            if (root/rel).is_file():originals[rel]=H(root/rel)
        for rel,want in originals.items():
            dst=backup/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,dst);assert H(dst)==want
        (out/'backup-manifest.json').write_text(json.dumps(originals,indent=2)+'\n')
        for rel,row in plan['product_inputs'].items():
            target=root/rel;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((pkg/'payload'/rel).read_bytes());assert H(target)==row['after_sha256']
            report['product_inputs_applied'].append(rel);emit()
        report['build_commands'].append(run(['make','leafgreen','-j'+str(a.jobs)],'make-leafgreen'))
        report['build_commands'].append(run(['make','GAME_VERSION=LEAFGREEN','syms'],'make-syms'))
        warnings=[line for row in report['build_commands'] for line in Path(row['log']).read_text(errors='replace').splitlines() if re.search(r'\bwarning\s*:',line,re.I)]
        report['build_warnings']=warnings;assert not warnings,'Build emitted warnings; review retained logs'
        built=root/'graphics/object_events/pics/people/misty_companion_season1.4bpp'
        assert H(built)==plan['compiled_misty_sha256'] and built.stat().st_size==2304
        regenerated=out/'misty-independent-regenerated.4bpp'
        run([str(root/'tools/gbagfx/gbagfx'),str(root/'graphics/object_events/pics/people/misty_companion_season1.png'),str(regenerated),'-mwidth','2','-mheight','4'],'gbagfx-independent')
        assert regenerated.read_bytes()==built.read_bytes()==expected_native
        before=v.Elf(backup/'pokemonthyl.elf');after=v.Elf(ELF)
        oldrom=(backup/'pokemonthyl.gba').read_bytes();newrom=ROM.read_bytes()
        checks={'ram':v.compare_ram(before,after),'baseline_rom_elf':v.segment_match(before,oldrom),'candidate_rom_elf':v.segment_match(after,newrom)}
        assert all(row['pass'] for row in checks.values())
        sprite,data=v.symbol_rom(after,newrom,'gObjectEventPic_MistyCompanion');old_sprite,olddata=v.symbol_rom(before,oldrom,'gObjectEventPic_MistyCompanion')
        assert data==expected_native and sprite.addr==old_sprite.addr and sprite.size==old_sprite.size==2304
        assert all(olddata[i*256:(i+1)*256]==data[i*256:(i+1)*256] for i in (2,7,8)), 'Approved side frames changed in actual ROM'
        _,nativepal=v.symbol_rom(after,newrom,'gObjectEventPal_Player');_,oldpal=v.symbol_rom(before,oldrom,'gObjectEventPal_Player')
        assert nativepal==oldpal==palette
        for name in ('gObjectEventPic_Misty',):
            _,oldbytes=v.symbol_rom(before,oldrom,name);_,newbytes=v.symbol_rom(after,newrom,name);assert oldbytes==newbytes
        # Read the map pointer through a compiler-derived actual MapLayout offset.
        import struct
        def route_bytes(elf,data):
            layout=elf.unique('JohtoRoute29_Layout');start=layout.addr-0x08000000
            width=struct.unpack_from('<I',data,start+offsets['qa.layout.width'])[0];height=struct.unpack_from('<I',data,start+offsets['qa.layout.height'])[0]
            assert (width,height)==(40,24)
            address=struct.unpack_from('<I',data,start+offsets['qa.layout.map'])[0]
            assert 0x08000000<=address<0x0a000000
            raw=data[address-0x08000000:address-0x08000000+1920];assert len(raw)==1920
            return address,raw
        oldmap,oldbytes=route_bytes(before,oldrom);newmap,newbytes=route_bytes(after,newrom)
        assert oldmap==newmap and hashlib.sha256(oldbytes).hexdigest()==plan['product_inputs']['data/layouts/JohtoRoute29/map.bin']['before_sha256']
        assert newbytes==(pkg/'payload/data/layouts/JohtoRoute29/map.bin').read_bytes()
        allowed=[(sprite.addr-0x08000000,sprite.addr-0x08000000+2304),(newmap-0x08000000,newmap-0x08000000+1920)]
        assert len(oldrom)==len(newrom)==33554432
        differences=[i for i,(x,y) in enumerate(zip(oldrom,newrom)) if x!=y]
        assert differences and all(any(lo<=i<hi for lo,hi in allowed) for i in differences),'ROM changed outside existing sprite/map allocations; inspect before release'
        checks.update(pass_all=True,ROM_changed_byte_count=len(differences),allowed_ROM_ranges=allowed,all_other_ROM_bytes_identical=True,
                      compiled_Misty_sha256=H(built),Misty_2304B_allocation_preserved=True,Route29_1920B_allocation_preserved=True,
                      native_player_palette_preserved=True,approved_side_native_frames_2_7_8_byte_identical=True,original_Misty_overworld_asset_preserved=True,
                      new_ROM_sha256=H(ROM),new_ELF_sha256=H(ELF))
        (out/'build-verification.json').write_text(json.dumps(checks,indent=2)+'\n')
        report.update(status='FOUR_INPUT_BUILD_AND_ABI_PASS_NATIVE_PENDING',compiled_ROM_sha256=H(ROM),compiled_ELF_sha256=H(ELF),build_and_ABI_pass=True)
        emit()
        if a.native:
            args=['--root',str(root),'--rom',str(ROM),'--elf',str(ELF),'--sav',str(sav),'--expect-rom-sha',H(ROM),'--expect-elf-sha',H(ELF),'--expect-sav-sha',H(sav),'--verifier',str(verify),'--guard-manifest',str(pkg/'payload-manifest.json')]
            for script,folder,extra in [('native_misty_walk_qa_r5.py','native-Misty-eight-cases',[]),('native_route29_geometry_r1.py','native-Route29-ten-cases',['--walk-runner',str(pkg/'native_misty_walk_qa_r5.py')])]:
                report['native_tests'].append(run([sys.executable,str(pkg/script),*args,'--out',str(out/folder),*extra],folder));emit()
            report.update(**{'pass':True},status='INTEGRATED_BUILD_NATIVE_FIXTURE_QA_PASS_RENDER_REVIEW_REQUIRED',actual_native_executed=True,rendered_frames_require_visual_review=True)
        else:report['pass']=True
except Exception as error:
    report.update(**{'pass':False},status='FAILED_REVIEW_RETAINED_ARTIFACTS_NO_AUTOMATIC_ROLLBACK',error=repr(error),traceback=traceback.format_exc())
finally:
    unchanged=all(path.is_file() and H(path)==want for path,want in protected.items())
    report['all_original_user_SAV_headers_helpers_and_unrelated_dirty_sources_unchanged']=unchanged
    if not unchanged:report['pass']=False;report['status']='PROTECTED_INPUT_CHANGED_REVIEW_REQUIRED'
    report['user_SAV_changed']=any(not path.is_file() or H(path)!=want for path,want in protected.items() if path.suffix.lower()=='.sav')
    emit()
print(json.dumps({k:report.get(k) for k in ('pass','status','error','compiled_ROM_sha256','compiled_ELF_sha256')}),flush=True)
sys.exit(0 if report['pass'] else 1)
