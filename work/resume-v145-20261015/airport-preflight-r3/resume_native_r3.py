"""Only resume the 18 native QA cases after the recorded successful build checks.

No product reapplication, ROM build, old report replacement or user-SAV edits.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, traceback

ap = argparse.ArgumentParser(description=__doc__)
for name in ('root', 'sav', 'bundle', 'postchecks-out', 'out'):
    ap.add_argument('--' + name, type=Path, required=True)
a = ap.parse_args()
root, sav, pkg, previous = [p.resolve(strict=True) for p in (a.root, a.sav, a.bundle, a.postchecks_out)]
qa = Path(__file__).resolve().parent
out = a.out.resolve()
assert previous.is_relative_to(root / 'work') and out.is_relative_to(root / 'work')
assert not out.exists() and not out.is_relative_to(previous) and not previous.is_relative_to(out)
assert not out.is_relative_to(pkg) and not out.is_relative_to(qa)
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ROM_SHA = 'fdd021066ee7ce6fa775407c6be6699ba41583f34d92264e65020bd98950b0f4'
ELF_SHA = '7c831da7d91eba1f4132e67a6ce804434003b2249e6abe0af5e19e69d622a53b'
SAV_SHA = '0949ebf04557a76e2175602e967eefadb7ffb722f2746be8a40ddb1fd66550a9'
ROM, ELF = root / 'pokemonthyl.gba', root / 'pokemonthyl.elf'
assert H(ROM) == ROM_SHA and H(ELF) == ELF_SHA and H(sav) == SAV_SHA
for rel, want in {
    'native_misty_walk_qa_r7.py': '4fec42760e54472b5ec86b760c644a51e58df8a761939afbcba15fe42b237c2f',
    'native_route29_geometry_r3.py': 'bb3f68db251ab064b2e4867bdfec8f267c3806bf210e86a254e5478b1d68bb9e'}.items():
    assert H(qa / rel) == want, ('New QA helper changed', rel)
assert H(pkg / 'bundle-files.json') == 'ca207e24cd976b2b9a30b879067bd2afe2e0f4ea82fd8e5bcf4e1ce4a24181a4'
for rel, want in json.loads((pkg / 'bundle-files.json').read_text()).items():
    assert H(pkg / rel) == want, ('Original bundle changed', rel)
plan = json.loads((pkg / 'payload-manifest.json').read_text())
for rel, want in plan['guarded_sources'].items():assert H(root / rel) == want, rel
for rel, row in plan['product_inputs'].items():assert H(root / rel) == row['after_sha256'], rel
for rel, want in plan['protected_user_saves_expected'].items():assert H(root / rel) == want, rel
helper_hashes = {
    'tools/qa/native_misty_basic_qa.py': '5b26bfee0a30d2f446a1981429aac0dc70d9ec0c8748c218ec38b3dd33be4ec6',
    'tools/qa/johto_violet_native_bootstrap_v1.py': '83c4557b96c344b241fc6f79e9b17722acfc0b0e81e0f9e6d649ff5d8b1c84bb',
    'tools/qa/emu.py': 'c8d3ba672d7ecc84dcefab513d84223f410e9d8cb43081cee4b37555e1378e69',
    'tools/qa/savefile.py': 'e6cc1acb8569dbdca6d1b7b095835a5271c9e16de9d2fa3f976d15b50b9b7daa',
    'tools/qa/gamedata.py': 'acaa4654ed889dc4f98f6c20dc26a85ea8d35963a771967c159ca4edc26a7ab3',
    'tools/qa/hoenn_gauntlet_save_qa.py': 'b22478d2eac54849a6f5e8effdbb8ad67f5a3a34cc3da02dd63db39f0ad1941b'}
for rel, want in helper_hashes.items():assert H(root / rel) == want, rel
old = json.loads((previous / 'validation.json').read_text())
checks = json.loads((previous / 'build-verification.json').read_text())
assert old['pass'] is False and old['build_and_ABI_pass'] is True
assert old['status'] == 'VERIFICATION_FAILED_ARTIFACTS_RETAINED'
assert old['all_protected_files_unchanged'] is True and old['user_SAV_changed'] is False
assert old['compiled_ROM_sha256'] == ROM_SHA and old['compiled_ELF_sha256'] == ELF_SHA
assert checks['pass_all'] is True and checks['all_other_ROM_bytes_identical'] is True
assert checks['new_ROM_sha256'] == ROM_SHA and checks['new_ELF_sha256'] == ELF_SHA
assert checks['ram']['pass'] and checks['baseline_rom_elf']['pass'] and checks['candidate_rom_elf']['pass']
assert checks['LOAD_segment_permission_review']['all_PT_LOAD_headers_identical'] is True
assert checks['LOAD_segment_permission_review']['no_new_RWX_segment'] is True
assert "unknown constant OBJ_EVENT_GFX_MISTY_COMPANION" in (previous / 'native-Misty-eight-cases.log').read_text(errors='replace')
assert old['warning_free'] is False and len(old['build_warnings_retained']) == 3
backup = Path(old['baseline_backup']).resolve(strict=True)
assert backup.is_relative_to(root / 'work')
assert H(backup / 'pokemonthyl.gba') == plan['baseline_ROM_sha256']
assert H(backup / 'pokemonthyl.elf') == plan['baseline_ELF_sha256']
protected = {p.resolve(): H(p) for p in (root / 'saves').rglob('*.sav')}
protected.update({p.resolve(): H(p) for p in (root / 'include').rglob('*.h')})
for directory in (previous, backup.parent, pkg):
    protected.update({p.resolve(): H(p) for p in directory.rglob('*') if p.is_file()})
for rel in (*plan['guarded_sources'], *plan['product_inputs'], *helper_hashes):
    protected[(root / rel).resolve()] = H(root / rel)
for p in (ROM, ELF, sav, *qa.glob('*.py')):protected[p] = H(p)
dirty = subprocess.check_output(['git', 'diff', '--name-only', '-z'], cwd=root).decode().split('\0')
for rel in filter(None, dirty):
    p = (root / rel).resolve()
    if p.is_file():protected[p] = H(p)
out.mkdir(parents=True)
report = {'status': 'NATIVE_ONLY_RUNNING', 'pass': False,
    'ROM_sha256': ROM_SHA, 'ELF_sha256': ELF_SHA, 'input_SAV_sha256': SAV_SHA,
    'successful_build_checks_reused': str(previous / 'build-verification.json'),
    'successful_build_checks_sha256': H(previous / 'build-verification.json'),
    'prior_failed_QA_report': str(previous / 'validation.json'),
    'prior_failed_QA_report_sha256': H(previous / 'validation.json'),
    'build_warnings_retained': old['build_warnings_retained'], 'warning_free': False,
    'ROM_rebuilt': False, 'product_inputs_reapplied': False, 'automatic_rollback': False,
    'files_deleted': 0, 'RAM_writes': 0, 'engine_calls': 0,
    'natural_story_completion_proved': False, 'full_Johto_Hoenn_completed': False,
    'native_tests': [], 'actual_native_executed': False}
def emit():(out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
try:
    args = ['--root', str(root), '--rom', str(ROM), '--elf', str(ELF), '--sav', str(sav),
            '--expect-rom-sha', ROM_SHA, '--expect-elf-sha', ELF_SHA, '--expect-sav-sha', SAV_SHA,
            '--verifier', str(pkg / 'verify_build.py'), '--guard-manifest', str(pkg / 'payload-manifest.json')]
    for script, folder, result_name, count, extra in [
        ('native_misty_walk_qa_r7.py', 'native-Misty-eight-cases', 'walk-validation.json', 8, []),
        ('native_route29_geometry_r3.py', 'native-Route29-ten-cases', 'route29-validation.json', 10,
         ['--walk-runner', str(qa / 'native_misty_walk_qa_r7.py')])]:
        command = [sys.executable, str(qa / script), *args, '--out', str(out / folder), *extra]
        log = out / (folder + '.log')
        with log.open('wb') as stream:
            process = subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT)
        row = {'command': command, 'returncode': process.returncode, 'log': str(log), 'log_sha256': H(log)}
        report['native_tests'].append(row);emit()
        assert process.returncode == 0, ('Native QA failed; retained output', row)
        result_path = out / folder / result_name
        result = json.loads(result_path.read_text())
        assert result['pass'] is True and result['status'] == 'complete'
        assert len(result['cases']) == count and all(case['pass'] is True for case in result['cases'])
        assert result['original_inputs_unchanged'] is True
        assert result['native_SAVE_cold']['checksummed_sectors'] == 14
        assert result['dependency_preflight']['pass'] is True
        row.update(result_path=str(result_path), result_sha256=H(result_path), actual_native_cases=count)
        emit()
    report.update(status='NATIVE_18_FIXTURE_CASES_PASS_RENDER_REVIEW_REQUIRED', **{'pass': True},
                  actual_native_executed=True, actual_native_cases=18, rendered_frames_require_visual_review=True)
except Exception as error:
    report.update(status='NATIVE_QA_FAILED_OUTPUT_RETAINED', error=repr(error), traceback=traceback.format_exc())
finally:
    changes = [str(p) for p, want in protected.items() if not p.is_file() or H(p) != want]
    report['protected_files_changed'] = changes
    report['all_protected_files_unchanged'] = not changes
    report['user_SAV_changed'] = any(Path(p).suffix.lower() == '.sav' for p in changes)
    if changes:report.update(status='PROTECTED_INPUT_CHANGED_REVIEW_REQUIRED', **{'pass': False})
    emit()
print(json.dumps({k: report.get(k) for k in ('pass', 'status', 'actual_native_cases', 'error')}), flush=True)
sys.exit(0 if report['pass'] else 1)
