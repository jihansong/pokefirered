"""Compile read-only PC/Summary observations against guarded current ARM sources.

Run in the actual build checkout. Does not link or change the product.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, subprocess

ap = argparse.ArgumentParser()
for n in ('root', 'rom', 'elf', 'guard-manifest', 'elf-helper', 'out'):
    ap.add_argument('--' + n, type=Path, required=True)
c = ap.parse_args()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(c.rom) == 'af2677993a75979fb36f0768c390d1bad7424e61f2d569b5054d40702250d2e8'
assert sha(c.elf) == '2549852a48935c680e06e81719b54663b9c0efa7fdaccd31d1f4683886c5d64e'
assert sha(c.elf_helper) == '5389bc06c82abb229865c29651063e03c999709b1a290e486941a2f9f99affac'
root, out = c.root.resolve(), c.out.resolve()
assert out.is_relative_to(root / 'work') and not out.exists()
guard = json.loads(c.guard_manifest.read_text())
if isinstance(guard, dict):
    guard = guard.get('files', guard)
if isinstance(guard, list):
    guard = {r['path']: r for r in guard}
rels = ['src/pokemon_summary_screen.c', 'src/pokemon_storage_system_data.c',
        'src/pokemon_storage_system_tasks.c', 'src/pokemon_storage_system_menu.c',
        'src/menu.c', 'include/pokemon_storage_system_internal.h',
        'include/pokemon_storage_system.h', 'include/pokemon.h', 'include/constants/items.h']
source_hashes = {}
for rel in rels:
    row = guard[rel]
    h = row['sha256'] if isinstance(row, dict) else row
    assert sha(root / rel) == h, ('Missing/stale PC UI dependency', rel)
    source_hashes[rel] = h

def decl(rel, typ):
    rows = re.findall(r'^struct ' + re.escape(typ) + r'\s*\{[\s\S]*?^\};', (root/rel).read_text(), re.M)
    assert len(rows) == 1, ('Private declaration changed', rel, typ)
    return rows[0]

lines = ['#include "global.h"', '#include "gflib.h"', '#include "pokemon.h"',
         '#include "pokemon_storage_system_internal.h"', '#include "task.h"',
         '#include "constants/items.h"',
         decl('src/menu.c', 'Menu'), decl('src/pokemon_summary_screen.c', 'PokemonSummaryScreenData')]
fields = {}
for typ, names in {
    'PokemonStorageSystemData': ('state', 'boxOption', 'menuItems', 'menuItemsCount',
          'displayMonPersonality', 'displayMonSpecies', 'displayMonIsEgg',
          'displayMonLevel', 'displayMonNickname', 'summaryCursorPos'),
    'StorageMenu': ('textId',),
    'PokemonSummaryScreenData': ('isEgg', 'isBadEgg', 'isBoxMon', 'summarySetupStep',
          'currentMon', 'summary.nicknameStrBuf', 'summary.speciesNameStrBuf'),
    'Menu': ('cursorPos', 'minCursorPos', 'maxCursorPos'),
    'Task': ('func', 'isActive', 'data'),
}.items():
    fields[typ + '.size'] = (typ, None)
    for name in names:
        fields[typ + '.' + name] = (typ, name)
constants = ('OPTION_MOVE_MONS', 'MENU_TEXT_SUMMARY', 'CURSOR_AREA_IN_BOX',
             'CURSOR_AREA_BOX_TITLE', 'IN_BOX_COLUMNS', 'IN_BOX_COUNT',
             'TOTAL_BOXES_COUNT', 'ITEM_ESCAPE_ROPE', 'NUM_TASKS')
lookup = {}
for i, (key, (typ, member)) in enumerate(fields.items()):
    sym = 'qo_' + str(i)
    exp = f'sizeof(struct {typ})' if member is None else f'offsetof(struct {typ}, {member})'
    lines.append(f'char {sym}[{exp}+1];'); lookup[sym] = ('offsets', key)
for i, key in enumerate(constants):
    sym = 'qc_' + str(i)
    lines.append(f'char {sym}[{key}+1];'); lookup[sym] = ('constants', key)
out.mkdir(parents=True)
src, obj, dep = [out/n for n in ('PC-summary-layout.c', 'PC-summary-layout.o', 'PC-summary-layout.d')]
src.write_text('\n'.join(lines)+'\n')
dka = Path(os.environ.get('DEVKITARM', '/opt/devkitpro/devkitARM'))
cmd = [str(dka/'bin/arm-none-eabi-gcc'), '-c', '-w', '-mthumb', '-mabi=apcs-gnu',
       '-march=armv4t', '-fcommon', '-iquote', 'include', '-DLEAFGREEN', '-DREVISION=0',
       '-DENGLISH', '-DMODERN=1', '-MMD', '-MF', str(dep), str(src), '-o', str(obj)]
cp = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=60)
(out/'compile.json').write_text(json.dumps({'exit_code': cp.returncode, 'stderr': cp.stderr}, indent=2))
assert cp.returncode == 0, cp.stderr
report = {'ROM_sha256': sha(c.rom), 'ELF_sha256': sha(c.elf), 'source_sha256': source_hashes,
          'probe_sha256': sha(__file__), 'offsets': {}, 'constants': {}, 'symbols': {},
          'native_executed': False, 'product_changed': False}
listing = subprocess.check_output([str(dka/'bin/arm-none-eabi-nm'), '-S', str(obj)], text=True)
for line in listing.splitlines():
    r = line.split()
    if len(r)==4 and r[3] in lookup:
        group, key = lookup[r[3]]; report[group][key] = int(r[1],16)-1
assert set(report['offsets']) == set(fields) and set(report['constants']) == set(constants)
deps = dep.read_text().replace('\\\n', ' ').split(':',1)[1].split()
report['compiler_dependency_sha256'] = {}
for p in deps:
    p = Path(p); p = p if p.is_absolute() else root/p
    p = p.resolve()
    if p.is_relative_to(root) and not p.is_relative_to(out):
        report['compiler_dependency_sha256'][str(p.relative_to(root))] = sha(p)
spec = importlib.util.spec_from_file_location('verified_elf', c.elf_helper)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
linked = mod.Elf32(c.elf)
owners = {'sCursorArea':'pokemon_storage_system_data.o', 'sCursorPosition':'pokemon_storage_system_data.o',
          'sIsMonBeingMoved':'pokemon_storage_system_data.o', 'sMenu':'menu.o',
          'sInMultiMoveMode':'pokemon_storage_system_data.o',
          'sMonSummaryScreen':'pokemon_summary_screen.o',
          'Task_PCMainMenu':'pokemon_storage_system_menu.o',
          'Task_PokeStorageMain':'pokemon_storage_system_tasks.o',
          'Task_OnSelectedMon':'pokemon_storage_system_tasks.o',
          'Task_ShowMonSummary':'pokemon_storage_system_tasks.o',
          'CB2_PokeStorage':'pokemon_storage_system_tasks.o',
          'CB2_RunPokemonSummaryScreen':'pokemon_summary_screen.o'}
for name in (*owners, 'gStorage', 'gTasks'):
    report['symbols'][name] = linked.bind(name, owners.get(name))
assert report['symbols']['gStorage']['size'] == 4
assert report['symbols']['gTasks']['size'] == report['offsets']['Task.size'] * report['constants']['NUM_TASKS']
(out/'PC-summary-abi.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'status':'CURRENT_ARM_PC_SUMMARY_ABI_READY', 'native_executed':False,
                  'ABI':str(out/'PC-summary-abi.json')}))
