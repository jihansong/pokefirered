"""Guard and apply the sixteen Devon dialogue paths, never run the live importer.

Actual repository importer runs twice in a new work tree with current map JSON,
sidecars and candidate canonical scripts/text. Every resulting byte must match
the intended candidates and the original maps. Default performs preflight only.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, shutil, subprocess, sys, uuid

def check(value, message):
    if not value:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def safe_path(root, relative):
    path = (root / relative).resolve()
    check(path.is_relative_to(root), 'Path outside expected root: ' + relative)
    return path

def run(repo, package, apply=False):
    repo, package = repo.resolve(strict=True), package.resolve(strict=True)
    manifest = json.loads((package / 'manifest.json').read_text(encoding='utf-8'))
    check(manifest['status'] == 'CONFIRMED_SOURCE_DRAFT_STATIC_PASS_NATIVE_PENDING', 'Unconfirmed source bundle')
    check(manifest['static']['pass'] and not manifest['product_changes_applied'], 'Unapproved candidate bundle')
    rows = manifest['files']
    maps = ['Route116', 'RusturfTunnel', 'RustboroCity_DevonCorp_1F', 'RustboroCity_DevonCorp_3F']
    expected = {f'data/maps/{m}/{k}' for m in maps for k in ['scripts.inc','text.inc']}
    check(len(rows) == 8 and {r['path'] for r in rows} == expected, 'Candidate scope must be exactly four maps/eight data files')
    changes = {}
    guards = {}
    for row in rows:
        canonical_expected = 'tools/hoenn_import/patches/' + row['path'].split('/')[2] + '.' + row['path'].split('/')[-1]
        check(row['canonical_path'] == canonical_expected, 'Unexpected canonical path')
        for relative, old, new in [(row['path'], row['baseline_sha256'], row['candidate_sha256']),
                                    (row['canonical_path'], None if row['canonical_baseline_must_be_absent'] else row['canonical_baseline_sha256'], row['canonical_sha256'])]:
            path = safe_path(repo, relative)
            candidate = safe_path(package, 'candidate/' + relative)
            check(sha(path) == old, 'Changed product source: ' + relative)
            check(sha(candidate) == new, 'Changed candidate: ' + relative)
            check(path not in changes, 'Duplicate target path')
            guards[path] = old
            changes[path] = (candidate, new)
    check(len(changes) == 16, 'Expected exactly sixteen target files')
    importer = safe_path(repo, 'tools/hoenn_import/apply_patches.py')
    check(importer.is_file(), 'Missing actual repository importer')
    guards[importer] = sha(importer)
    # Protect everything the importer could touch/read for the selected maps.
    for m in maps:
        for relative in [f'data/maps/{m}/map.json', f'tools/hoenn_import/patches/{m}.json', f'tools/hoenn_import/patches/{m}.mapscripts']:
            path = safe_path(repo, relative)
            guards[path] = sha(path)
    # ROM and every current original SAV are read-only inputs to this operation.
    for path in [repo/'pokemonthyl.gba', repo/'pokemonthyl.elf', *sorted((repo/'saves').rglob('*.sav'))]:
        if path.exists():
            check(path.resolve().is_relative_to(repo), 'Save resolves outside repository')
            guards[path.resolve()] = sha(path)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    out = safe_path(repo, 'work/devon-story-r2-' + stamp)
    out.mkdir(parents=True, exist_ok=False)
    isolated = out / 'isolated-roundtrip'
    copied_importer = isolated / 'tools/hoenn_import/apply_patches.py'
    copied_importer.parent.mkdir(parents=True)
    shutil.copy2(importer, copied_importer)
    for path, before_sha in guards.items():
        relative = path.relative_to(repo)
        if relative.parts[:2] == ('data','maps') or (relative.parts[:3] == ('tools','hoenn_import','patches') and relative.suffix in ['.json','.mapscripts']):
            if path.exists():
                dest = isolated / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)
    for path, (candidate, wanted) in changes.items():
        relative = path.relative_to(repo)
        dest = isolated / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path if relative.parts[:2] == ('data','maps') else candidate, dest)
    report = {'revision': 2, 'applied': False, 'source_guard_pass': False,
              'live_importer_executed': False, 'native_game_QA_performed': False,
              'exact_product_target_count': 16, 'work_output': str(out),
              'importer_sha256': sha(importer), 'manifest_sha256': sha(package/'manifest.json'),
              'canonical_regeneration_passes': 0}
    def unchanged(except_changes=False):
        for path, wanted in guards.items():
            if except_changes and path in changes:
                wanted = changes[path][1]
            check(sha(path) == wanted, 'Protected path changed: ' + str(path.relative_to(repo)))
    try:
        for attempt in [1,2]:
            result = subprocess.run([sys.executable, str(copied_importer), *maps], cwd=isolated,
                                    text=True, capture_output=True, timeout=30)
            (out/f'roundtrip-{attempt}.log').write_text(result.stdout + result.stderr, encoding='utf-8')
            check(result.returncode == 0, 'Isolated importer failed')
            for path, (candidate, wanted) in changes.items():
                check(sha(isolated/path.relative_to(repo)) == wanted, 'Isolated generated candidate mismatch: ' + str(path.relative_to(repo)))
            for m in maps:
                path = safe_path(repo, f'data/maps/{m}/map.json')
                check(sha(isolated/path.relative_to(repo)) == guards[path], 'Importer would change map/warp JSON: ' + m)
            report['canonical_regeneration_passes'] += 1
        unchanged()
        report['source_guard_pass'] = True
        if apply:
            backup = out / 'original-backup'
            backup.mkdir()
            for path in changes:
                if path.exists():
                    target = backup / path.relative_to(repo)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, target)
            (backup/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
            written = []
            try:
                unchanged()
                for path, (candidate, wanted) in changes.items():
                    check(sha(path) == guards[path], 'Concurrent target edit: ' + str(path))
                    path.parent.mkdir(parents=True, exist_ok=True)
                    staged = path.with_name(path.name + '.devon-r2-' + stamp + '.tmp')
                    check(not staged.exists(), 'Temporary path already occupied')
                    shutil.copy2(candidate, staged)
                    check(sha(staged) == wanted, 'Staged bytes differ from candidate')
                    os.replace(staged, path)
                    written.append(path)
                unchanged(except_changes=True)
            except Exception:
                for path in reversed(written):
                    # Do not overwrite a concurrent third-party edit during rollback.
                    check(sha(path) == changes[path][1], 'Rollback stopped: concurrent target edit, use original-backup')
                    original = backup/path.relative_to(repo)
                    if original.exists():
                        shutil.copy2(original, path)
                    else:
                        check(guards[path] is None and path in written, 'Cannot remove a pre-existing file')
                        path.unlink()  # Only a new canonical file created by this run.
                raise
            report.update({'applied': True, 'original_backup': str(backup),
                           'map_json_unchanged': True, 'ROM_ELF_all_original_SAV_unchanged': True})
        else:
            report.update({'map_json_unchanged': True, 'ROM_ELF_all_original_SAV_unchanged': True})
    except Exception as error:
        report['error'] = repr(error)
        raise
    finally:
        (out/'apply-result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent/'story-bundle')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(args.repo, args.package, args.apply)))
