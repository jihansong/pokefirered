"""Resume verification after the reviewed build-warning stop; never apply/build products.

The original failed output and its backups remain immutable. Only a new work
directory, compiler probe outputs, and dedicated native QA clones are written.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, struct, subprocess, sys, traceback

ap = argparse.ArgumentParser(description=__doc__)
for key in ('root', 'prior-out', 'bundle', 'sav', 'out'):
    ap.add_argument('--' + key, type=Path, required=True)
ap.add_argument('--native', action='store_true')
a = ap.parse_args()
root = a.root.resolve(strict=True)
prior = a.prior_out.resolve(strict=True)
pkg = a.bundle.resolve(strict=True)
sav = a.sav.resolve(strict=True)
out = a.out.resolve()
assert prior.is_relative_to(root / 'work')
assert out.is_relative_to(root / 'work') and not out.exists()
assert not out.is_relative_to(prior) and not prior.is_relative_to(out)
assert not out.is_relative_to(pkg)
H = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
NEW_ROM = 'fdd021066ee7ce6fa775407c6be6699ba41583f34d92264e65020bd98950b0f4'
NEW_ELF = '7c831da7d91eba1f4132e67a6ce804434003b2249e6abe0af5e19e69d622a53b'
SAV = '0949ebf04557a76e2175602e967eefadb7ffb722f2746be8a40ddb1fd66550a9'
assert H(pkg / 'apply_build_route29_misty_r1.py') == '530a144e358e2d2425af59ce5a59a59a8d88eaddc5531839f05fa748b97f1a11'
assert H(pkg / 'bundle-files.json') == 'ca207e24cd976b2b9a30b879067bd2afe2e0f4ea82fd8e5bcf4e1ce4a24181a4'
for rel, want in json.loads((pkg / 'bundle-files.json').read_text()).items():
    assert H(pkg / rel) == want, ('Existing bundle changed', rel)
plan = json.loads((pkg / 'payload-manifest.json').read_text())
assert set(plan['product_inputs']) == {
    'data/layouts/JohtoRoute29/map.bin', 'tools/johto/build_entry.py',
    'tools/johto/route29_landscape_boundaries.py',
    'graphics/object_events/pics/people/misty_companion_season1.png'}
for rel, row in plan['product_inputs'].items():
    assert H(root / rel) == row['after_sha256'], ('Applied input changed', rel)
for rel, want in plan['guarded_sources'].items():
    assert H(root / rel) == want, ('Preserved source changed', rel)
for rel, want in plan['protected_user_saves_expected'].items():
    assert H(root / rel) == want, ('User SAV changed; do not overwrite it', rel)
ROM, ELF = root / 'pokemonthyl.gba', root / 'pokemonthyl.elf'
assert H(ROM) == NEW_ROM and H(ELF) == NEW_ELF and H(sav) == SAV
previous = json.loads((prior / 'validation.json').read_text())
assert previous['pass'] is False
assert previous['status'] == 'FAILED_REVIEW_RETAINED_ARTIFACTS_NO_AUTOMATIC_ROLLBACK'
assert previous['user_SAV_changed'] is False
assert previous['all_original_user_SAV_headers_helpers_and_unrelated_dirty_sources_unchanged'] is True
assert set(previous['product_inputs_applied']) == set(plan['product_inputs'])
assert previous['baseline_ROM_sha256'] == plan['baseline_ROM_sha256']
assert previous['baseline_ELF_sha256'] == plan['baseline_ELF_sha256']
assert 'Build emitted warnings; review retained logs' in previous.get('error', '')
commands = previous['build_commands']
assert len(commands) == 2 and all(row['returncode'] == 0 for row in commands)
assert commands[0]['command'] == ['make', 'leafgreen', '-j2']
assert commands[1]['command'] == ['make', 'GAME_VERSION=LEAFGREEN', 'syms']
warnings = []
for row, name in zip(commands, ('make-leafgreen.log', 'make-syms.log')):
    log = prior / name
    assert Path(row['log']).resolve() == log.resolve() and H(log) == row['log_sha256']
    warnings.extend(line for line in log.read_text(errors='replace').splitlines()
                    if re.search(r'\bwarning\s*:', line, re.I))
assert warnings == previous['build_warnings']
jobserver = re.compile(r"^make\[1\]: warning: jobserver unavailable: using -j1\.\s+Add '\+' to parent make rule\.$")
rwx = re.compile(r'^/opt/devkitpro/devkitARM/bin/arm-none-eabi-ld: warning: ../../pokemonthyl\.elf has a LOAD segment with RWX permissions$')
assert len(warnings) == 3 and sum(bool(jobserver.fullmatch(x)) for x in warnings) == 2
assert sum(bool(rwx.fullmatch(x)) for x in warnings) == 1, ('Unexpected warning; review required', warnings)
backup = prior / 'backup'
originals = json.loads((prior / 'backup-manifest.json').read_text())
assert originals['pokemonthyl.gba'] == plan['baseline_ROM_sha256']
assert originals['pokemonthyl.elf'] == plan['baseline_ELF_sha256']
for rel, want in originals.items():
    assert H(backup / rel) == want, ('Original backup changed', rel)
for rel, row in plan['product_inputs'].items():
    if row['before_sha256'] is not None:
        assert originals[rel] == row['before_sha256']
helpers = {
    'tools/qa/native_misty_basic_qa.py': '5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6',
    'tools/qa/johto_violet_native_bootstrap_v1.py': '83c4557b96c344b241fc6f79e9b17722acfc0b0e81e0f9e6d649ff5d8b1c84bb',
    'tools/qa/emu.py': 'c8d3ba672d7ecc84dcefab513d84223f410e9d8cb43081cee4b37555e1378e69',
    'tools/qa/savefile.py': 'e6cc1acb8569dbdca6d1b7b095835a5271c9e16de9d2fa3f976d15b50b9b7daa',
    'tools/qa/gamedata.py': 'acaa4654ed889dc4f98f6c20dc26a85ea8d35963a771967c159ca4edc26a7ab3',
    'tools/qa/hoenn_gauntlet_save_qa.py': 'b22478d2eac54849a6f5e8effdbb8ad67f5a3a34cc3da02dd63db39f0ad1941b'}
for rel, want in helpers.items():
    assert H(root / rel) == want, ('Existing safety helper changed', rel)
verify = pkg / 'verify_build.py'
vspec = importlib.util.spec_from_file_location('resume_readonly_rom_elf_verifier', verify)
v = importlib.util.module_from_spec(vspec)
sys.modules[vspec.name] = v
vspec.loader.exec_module(v)
expected_native, palette = v.encode_png(
    root / 'graphics/object_events/pics/people/misty_companion_season1.png',
    root / 'graphics/object_events/palettes/player.pal')
assert hashlib.sha256(expected_native).hexdigest() == plan['compiled_misty_sha256']
out.mkdir(parents=True)
os.chdir(root)
protected = {p.resolve(): H(p) for p in (root / 'saves').rglob('*.sav')}
protected[sav] = H(sav)
for rel in (*plan['guarded_sources'], *helpers, *plan['product_inputs']):
    protected[(root / rel).resolve()] = H(root / rel)
protected.update({p.resolve(): H(p) for p in (root / 'include').rglob('*.h')})
protected.update({p.resolve(): H(p) for p in prior.rglob('*') if p.is_file()})
protected.update({p.resolve(): H(p) for p in pkg.rglob('*') if p.is_file()})
for name in ('pokemonthyl.gba', 'pokemonthyl.elf', 'pokemonthyl.sym', 'pokemonthyl.map',
             'graphics/object_events/pics/people/misty_companion_season1.4bpp'):
    path = root / name
    if path.is_file(): protected[path.resolve()] = H(path)
dirty = subprocess.check_output(['git', 'diff', '--name-only', '-z'], cwd=root).decode().split('\0')
for rel in filter(None, dirty):
    path = (root / rel).resolve()
    if path.is_file(): protected[path] = H(path)
(out / 'retained-input-hashes.json').write_text(json.dumps({str(p): h for p, h in protected.items()}, indent=2) + '\n')
report = {
    'status': 'VERIFICATION_ONLY_RUNNING', 'pass': False,
    'prior_failed_report': str(prior / 'validation.json'),
    'prior_failed_report_sha256': H(prior / 'validation.json'),
    'baseline_backup': str(backup), 'product_inputs_reapplied': False,
    'ROM_rebuilt': False, 'build_commands_executed': [], 'build_warnings_retained': warnings,
    'warning_free': False, 'warnings_suppressed': False,
    'native_tests': [], 'user_SAV_changed': False, 'automatic_rollback': False,
    'files_deleted': 0, 'natural_story_completion_proved': False,
    'full_Johto_Hoenn_completed': False, 'input_SAV_sha256': SAV,
    'compiled_ROM_sha256': NEW_ROM, 'compiled_ELF_sha256': NEW_ELF}
def emit():
    (out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
def run(command, name):
    log = out / (name + '.log')
    with log.open('wb') as stream:
        process = subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT)
    row = {'command': list(map(str, command)), 'returncode': process.returncode,
           'log': str(log), 'log_sha256': H(log)}
    assert process.returncode == 0, ('Verification command failed; retained artifacts', row)
    return row
try:
    sys.path.insert(0, str(root / 'tools/qa'))
    import gamedata as gd
    gd.CACHE = str(out / 'compiler-cache')
    gd._OFFSETS = None
    gd.FIELDS.update({'qa.layout.map': ('MapLayout', 'map'),
                      'qa.layout.width': ('MapLayout', 'width'),
                      'qa.layout.height': ('MapLayout', 'height')})
    offsets = {k: gd.off(k) for k in ('qa.layout.map', 'qa.layout.width', 'qa.layout.height',
                                    'sb1', 'sb2', 'storage', 'pokemon', 'boxmon')}
    assert [offsets[k] for k in ('sb1', 'sb2', 'storage', 'pokemon', 'boxmon')] == [15720, 3876, 33744, 100, 80]
    assert offsets == json.loads((prior / 'current-compiler-offsets.json').read_text())
    (out / 'current-compiler-offsets.json').write_text(json.dumps(offsets, indent=2) + '\n')
    built = root / 'graphics/object_events/pics/people/misty_companion_season1.4bpp'
    assert H(built) == plan['compiled_misty_sha256'] and built.stat().st_size == 2304
    regenerated = out / 'misty-independent-regenerated.4bpp'
    report['graphics_regeneration_command'] = run([
        str(root / 'tools/gbagfx/gbagfx'),
        str(root / 'graphics/object_events/pics/people/misty_companion_season1.png'),
        str(regenerated), '-mwidth', '2', '-mheight', '4'], 'gbagfx-independent')
    assert regenerated.read_bytes() == built.read_bytes() == expected_native
    before, after = v.Elf(backup / 'pokemonthyl.elf'), v.Elf(ELF)
    oldrom, newrom = (backup / 'pokemonthyl.gba').read_bytes(), ROM.read_bytes()
    checks = {'ram': v.compare_ram(before, after),
              'baseline_rom_elf': v.segment_match(before, oldrom),
              'candidate_rom_elf': v.segment_match(after, newrom)}
    assert all(row['pass'] for row in checks.values())
    def load_segments(elf):
        names = ('type', 'file_offset', 'virtual_address', 'physical_address',
                 'file_size', 'memory_size', 'flags', 'alignment')
        return [dict(zip(names, row)) for row in elf.segments if row[0] == 1]
    oldloads, newloads = load_segments(before), load_segments(after)
    oldrwx = [row for row in oldloads if row['flags'] & 7 == 7]
    newrwx = [row for row in newloads if row['flags'] & 7 == 7]
    loadcheck = {'baseline_PT_LOAD_headers': oldloads, 'candidate_PT_LOAD_headers': newloads,
                 'all_PT_LOAD_headers_identical': oldloads == newloads,
                 'baseline_RWX_headers': oldrwx, 'candidate_RWX_headers': newrwx,
                 'no_new_RWX_segment': oldrwx == newrwx,
                 'warning_free': False, 'linker_or_permission_changes_performed': False}
    checks['LOAD_segment_permission_review'] = loadcheck
    (out / 'LOAD-segment-review.json').write_text(json.dumps(loadcheck, indent=2) + '\n')
    assert oldloads and oldloads == newloads and oldrwx and oldrwx == newrwx, 'LOAD headers differ or RWX was not already present; independent review required'
    sprite, data = v.symbol_rom(after, newrom, 'gObjectEventPic_MistyCompanion')
    old_sprite, olddata = v.symbol_rom(before, oldrom, 'gObjectEventPic_MistyCompanion')
    assert data == expected_native and sprite.addr == old_sprite.addr and sprite.size == old_sprite.size == 2304
    assert all(olddata[i*256:(i+1)*256] == data[i*256:(i+1)*256] for i in (2, 7, 8))
    _, nativepal = v.symbol_rom(after, newrom, 'gObjectEventPal_Player')
    _, oldpal = v.symbol_rom(before, oldrom, 'gObjectEventPal_Player')
    assert nativepal == oldpal == palette
    _, old_misty = v.symbol_rom(before, oldrom, 'gObjectEventPic_Misty')
    _, new_misty = v.symbol_rom(after, newrom, 'gObjectEventPic_Misty')
    assert old_misty == new_misty
    def route_bytes(elf, data):
        layout = elf.unique('JohtoRoute29_Layout')
        start = layout.addr - 0x08000000
        width = struct.unpack_from('<I', data, start + offsets['qa.layout.width'])[0]
        height = struct.unpack_from('<I', data, start + offsets['qa.layout.height'])[0]
        assert (width, height) == (40, 24)
        address = struct.unpack_from('<I', data, start + offsets['qa.layout.map'])[0]
        assert 0x08000000 <= address < 0x0a000000
        raw = data[address-0x08000000:address-0x08000000+1920]
        assert len(raw) == 1920
        return address, raw
    oldmap, oldbytes = route_bytes(before, oldrom)
    newmap, newbytes = route_bytes(after, newrom)
    assert oldmap == newmap and hashlib.sha256(oldbytes).hexdigest() == plan['product_inputs']['data/layouts/JohtoRoute29/map.bin']['before_sha256']
    assert newbytes == (pkg / 'payload/data/layouts/JohtoRoute29/map.bin').read_bytes()
    allowed = [(sprite.addr-0x08000000, sprite.addr-0x08000000+2304),
               (newmap-0x08000000, newmap-0x08000000+1920)]
    assert len(oldrom) == len(newrom) == 33554432
    differences = [i for i, (x, y) in enumerate(zip(oldrom, newrom)) if x != y]
    assert differences and all(any(lo <= i < hi for lo, hi in allowed) for i in differences), 'ROM differs outside existing sprite/map allocations'
    checks.update(pass_all=True, ROM_changed_byte_count=len(differences), allowed_ROM_ranges=allowed,
                  all_other_ROM_bytes_identical=True, compiled_Misty_sha256=H(built),
                  Misty_2304B_allocation_preserved=True, Route29_1920B_allocation_preserved=True,
                  native_player_palette_preserved=True,
                  approved_side_native_frames_2_7_8_byte_identical=True,
                  original_Misty_overworld_asset_preserved=True,
                  new_ROM_sha256=NEW_ROM, new_ELF_sha256=NEW_ELF)
    (out / 'build-verification.json').write_text(json.dumps(checks, indent=2) + '\n')
    report.update(status='EXISTING_BUILD_AND_ABI_PASS_NATIVE_PENDING', build_and_ABI_pass=True,
                  baseline_RWX_already_present=True, unchanged_LOAD_headers=True)
    emit()
    if a.native:
        args = ['--root', str(root), '--rom', str(ROM), '--elf', str(ELF), '--sav', str(sav),
                '--expect-rom-sha', NEW_ROM, '--expect-elf-sha', NEW_ELF, '--expect-sav-sha', SAV,
                '--verifier', str(verify), '--guard-manifest', str(pkg / 'payload-manifest.json')]
        for script, folder, extra in [
            ('native_misty_walk_qa_r5.py', 'native-Misty-eight-cases', []),
            ('native_route29_geometry_r1.py', 'native-Route29-ten-cases',
             ['--walk-runner', str(pkg / 'native_misty_walk_qa_r5.py')])]:
            report['native_tests'].append(run([
                sys.executable, str(pkg / script), *args, '--out', str(out / folder), *extra], folder))
            emit()
        report.update(status='EXISTING_BUILD_NATIVE_FIXTURE_QA_PASS_RENDER_REVIEW_REQUIRED',
                      actual_native_executed=True, rendered_frames_require_visual_review=True,
                      expected_native_fixture_cases=18)
    else:
        report['status'] = 'EXISTING_BUILD_AND_ABI_PASS_NATIVE_NOT_EXECUTED'
    report['pass'] = True
except Exception as error:
    report.update(status='VERIFICATION_FAILED_ARTIFACTS_RETAINED', **{'pass': False},
                  error=repr(error), traceback=traceback.format_exc())
finally:
    changes = [str(path) for path, want in protected.items() if not path.is_file() or H(path) != want]
    report['protected_files_changed'] = changes
    report['all_protected_files_unchanged'] = not changes
    report['prior_failed_artifacts_and_backup_unchanged'] = not any(Path(p).is_relative_to(prior) for p in changes)
    report['user_SAV_changed'] = any(Path(p).suffix.lower() == '.sav' for p in changes)
    if changes:
        report['pass'] = False
        report['status'] = 'PROTECTED_INPUT_CHANGED_REVIEW_REQUIRED'
    emit()
print(json.dumps({k: report.get(k) for k in ('pass', 'status', 'error', 'compiled_ROM_sha256', 'compiled_ELF_sha256')}), flush=True)
sys.exit(0 if report['pass'] else 1)
