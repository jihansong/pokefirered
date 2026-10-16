"""Compiler-derived private dex/list/palette read-only UI ABI for root.

Run only on the matching current Codespaces source. No game file is changed.
--source-manifest maps actual repository paths to captured sha256 strings or
{sha256:...} entries. The temporary compiler object lives in --out exclusively.
"""
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
from pathlib import Path

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def elf_tables(raw):
    header = struct.unpack_from('<16sHHIIIIIHHHHHH', raw)
    assert header[0][:6] == b'\x7fELF\x01\x01' and header[2] == 40
    sections = [struct.unpack_from('<10I', raw, header[6] + i * header[11]) for i in range(header[12])]
    rows = []
    for section in sections:
        if section[1] != 2:
            continue
        strings_section = sections[section[6]]
        strings = raw[strings_section[4]:strings_section[4] + strings_section[5]]
        owner = None
        for offset in range(section[4], section[4] + section[5], section[9]):
            name, value, size, info, other, index = struct.unpack_from('<IIIBBH', raw, offset)
            label = strings[name:strings.find(b'\0', name)].decode()
            if info & 15 == 4:
                owner = label
            rows.append(dict(name=label, value=value, size=size, info=info, section=index,
                             local_translation_unit=owner if info >> 4 == 0 else None))
    return sections, rows

def definition(source, name):
    starts = list(re.finditer(r'\bstruct\s+' + re.escape(name) + r'\s*\{', source))
    assert len(starts) == 1
    begin = starts[0].start()
    end = source.index('{', begin) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    assert source[end] == ';'
    return source[begin:end + 1]

def main():
    parser = argparse.ArgumentParser()
    for name in ('root', 'rom', 'elf', 'out', 'source-manifest'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    root, rom, elf, out = [getattr(args, name).resolve() for name in ('root', 'rom', 'elf', 'out')]
    assert digest(rom.read_bytes()) == '0845f8cbc1afa5d957a64f76a4ae2700606175dd55bcd101184e6ba2a650b7fa'
    assert digest(elf.read_bytes()) == 'e625069ea9379ea3dc2f83e3014fb741a2e0b7383f41f6d56bc37fc0eae6f17b'
    manifest = json.loads(args.source_manifest.read_text())
    required = ('src/pokedex_screen.c', 'src/list_menu.c', 'src/main.c', 'src/bg.c', 'src/start_menu.c',
                'include/main.h', 'include/palette.h', 'include/task.h', 'include/list_menu.h',
                'include/global.h', 'include/constants/pokedex.h', 'include/pokedex_screen.h',
                'include/pokedex.h', 'include/constants/species.h', 'include/constants/vars.h')
    checked = {}
    for relative in required:
        entry = manifest[relative]
        expected = entry['sha256'] if isinstance(entry, dict) else entry
        assert digest((root / relative).read_bytes()) == expected
        checked[relative] = expected
    source = (root / 'src/pokedex_screen.c').read_text()
    structure = definition(source, 'PokedexScreenData')
    out.mkdir(parents=True, exist_ok=False)
    fields = {
        'dex.size': ('PokedexScreenData', None), 'dex.task': ('PokedexScreenData', 'taskId'),
        'dex.state': ('PokedexScreenData', 'state'), 'dex.topListTask': ('PokedexScreenData', 'modeSelectListMenuId'),
        'dex.orderedListTask': ('PokedexScreenData', 'orderedListMenuTaskId'),
        'dex.order': ('PokedexScreenData', 'dexOrderId'), 'dex.count': ('PokedexScreenData', 'orderedDexCount'),
        'dex.region': ('PokedexScreenData', 'regionalDex'), 'dex.national': ('PokedexScreenData', 'showNationalNumbers'),
        'list.size': ('ListMenu', None), 'list.offset': ('ListMenu', 'cursorPos'), 'list.row': ('ListMenu', 'itemsAbove'),
        'list.template': ('ListMenu', 'template'), 'listTemplate.size': ('ListMenuTemplate', None),
        'listTemplate.items': ('ListMenuTemplate', 'items'), 'listTemplate.count': ('ListMenuTemplate', 'totalItems'),
        'listTemplate.shown': ('ListMenuTemplate', 'maxShowed'), 'listItem.size': ('ListMenuItem', None),
        'listItem.index': ('ListMenuItem', 'index'), 'task.size': ('Task', None),
        'task.func': ('Task', 'func'), 'task.active': ('Task', 'isActive'), 'task.data': ('Task', 'data'),
        'main.size': ('Main', None), 'main.callback2': ('Main', 'callback2'),
        'main.vblankCounter2': ('Main', 'vblankCounter2'), 'main.heldKeysRaw': ('Main', 'heldKeysRaw'),
        'main.newAndRepeatedKeys': ('Main', 'newAndRepeatedKeys'), 'main.keyRepeatCounter': ('Main', 'keyRepeatCounter'),
        'palette.size': ('PaletteFadeControl', None),
    }
    lines = ['#include "global.h"', '#include "main.h"', '#include "palette.h"', '#include "task.h"',
             '#include "list_menu.h"', '#include "constants/pokedex.h"', '#include "pokedex_screen.h"', structure]
    identifiers = {}
    for index, (name, (kind, field)) in enumerate(fields.items()):
        symbol = 'qa_shape_' + str(index)
        expression = 'sizeof(struct ' + kind + ')' if field is None else 'offsetof(struct ' + kind + ', ' + field + ')'
        lines.append('char ' + symbol + '[' + expression + '+1];')
        identifiers[symbol] = name
    lines.append('char qa_numeric_menu_value[DEX_MODE(NUMERICAL_KANTO)+1];')
    identifiers['qa_numeric_menu_value'] = 'menu.numericalItem'
    lines.append('const struct PaletteFadeControl qa_palette_active_mask = {.active = 1};')
    c, obj = out / 'ui-offsets.c', out / 'ui-offsets.o'
    c.write_text('\n'.join(lines) + '\n')
    compiler = Path(os.environ.get('DEVKITARM', '/opt/devkitpro/devkitARM')) / 'bin/arm-none-eabi-gcc'
    subprocess.run([str(compiler), '-c', '-w', '-mthumb', '-mabi=apcs-gnu', '-march=armv4t', '-fcommon',
                    '-iquote', 'include', '-DLEAFGREEN', '-DREVISION=0', '-DENGLISH', '-DMODERN=1',
                    '-o', str(obj), str(c)], cwd=root, check=True)
    compiled = obj.read_bytes()
    sections, probe = elf_tables(compiled)
    offsets = {identifiers[row['name']]: row['size'] - 1 for row in probe if row['name'] in identifiers}
    assert set(offsets) == set(fields) | {'menu.numericalItem'}
    mask = [row for row in probe if row['name'] == 'qa_palette_active_mask']
    assert len(mask) == 1 and mask[0]['size'] == offsets['palette.size']
    entry = mask[0]
    section = sections[entry['section']]
    active_mask = compiled[section[4] + entry['value']:section[4] + entry['value'] + entry['size']]
    bits = [(i, value) for i, value in enumerate(active_mask) if value]
    assert len(bits) == 1 and bits[0][1] & (bits[0][1] - 1) == 0
    assert offsets['task.size'] == 40 and offsets['task.data'] == 8 and offsets['list.size'] == 32
    game_sections, game_symbols = elf_tables(elf.read_bytes())
    wanted = {'gMain': (1, None, offsets['main.size']), 'gTasks': (1, None, 16 * offsets['task.size']),
              'gPaletteFade': (1, None, offsets['palette.size']),
              'sPokedexScreenData': (1, 'pokedex_screen.o', 4), 'sDmaBusyBitfield': (1, 'bg.o', 16),
              'gKeyRepeatStartDelay': (1, None, 2), 'gKeyRepeatContinueDelay': (1, None, 2),
              'sNumStartMenuItems': (1, 'start_menu.o', 1), 'sStartMenuCursorPos': (1, 'start_menu.o', 1),
              'sStartMenuOrder': (1, 'start_menu.o', None),
              'CB2_PokedexScreen': (2, None, None), 'Task_PokedexScreen': (2, 'pokedex_screen.o', None),
              'Task_DexScreen_NumericalOrder': (2, 'pokedex_screen.o', None),
              'ListMenuDummyTask': (2, 'list_menu.o', None)}
    bound = {}
    for name, (kind, owner, size) in wanted.items():
        matches = [row for row in game_symbols if row['name'] == name and row['info'] & 15 == kind
                   and (owner is None or row['local_translation_unit'] == owner)]
        assert len(matches) == 1, (name, matches)
        row = matches[0]
        assert size is None or row['size'] == size
        assert row['section'] < len(game_sections)
        section = game_sections[row['section']]
        assert section[2] & 2 and section[3] <= (row['value'] & ~1) < section[3] + section[5]
        assert (row['value'] & ~1) + row['size'] <= section[3] + section[5]
        if kind == 1:
            assert 0x02000000 <= row['value'] < 0x02040000 or 0x03000000 <= row['value'] < 0x03008000
        else:
            assert 0x08000000 <= (row['value'] & ~1) < 0x0a000000
        bound[name] = row
    assert all(digest((root / rel).read_bytes()) == value for rel, value in checked.items())
    result = dict(schema='thunder-yellow-dex-ui-compiler-probe-v1', ROM_sha256=digest(rom.read_bytes()),
                  ELF_sha256=digest(elf.read_bytes()), source_sha256=checked, offsets=offsets,
                  palette_active_byte=bits[0][0], palette_active_mask=bits[0][1], symbols=bound,
                  private_struct_source_sha256=digest(structure.encode()), compiled_object_sha256=digest(compiled),
                  global_STT_FILE_owner_not_inferred=True, gameplay_inputs_or_ROM_RAM_changes=0)
    helper_names = {'gSaveBlock1Ptr', 'gSaveBlock2Ptr', 'gPokemonStoragePtr', 'gPlayerParty', 'gPlayerPartyCount',
                    'gQuestLogState', 'gQuestLogPlaybackState', 'sGlobalScriptContextStatus', 'sLockFieldControls',
                    'CB2_Overworld', 'BattleMainCB2', 'CB2_MainMenu', 'CB2_InitCopyrightScreenAfterBootup',
                    'CB2_InitCopyrightScreenAfterTitleScreen', 'CB2_WaitFadeBeforeSetUpIntro', 'CB2_SetUpIntro',
                    'CB2_Intro', 'CB2_CopyrightScreen'}
    helper = {}
    required_helpers = {'gSaveBlock1Ptr', 'gSaveBlock2Ptr', 'gPokemonStoragePtr', 'gPlayerParty', 'gPlayerPartyCount',
                        'gQuestLogState', 'gQuestLogPlaybackState', 'CB2_Overworld', 'CB2_MainMenu'}
    for name in helper_names:
        rows = [row for row in game_symbols if row['name'] == name and row['info'] & 15 in (1, 2)
                and row['section'] < len(game_sections) and game_sections[row['section']][2] & 2]
        assert len(rows) <= 1, ('Ambiguous Emu helper symbol', name)
        if rows:
            helper[name] = rows[0]
    assert required_helpers <= helper.keys()
    result['helper_symbols'] = helper
    (out / 'dex-ui-abi.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(dict(abi=str(out / 'dex-ui-abi.json'), offsets=offsets,
                         palette_active=[bits[0][0], bits[0][1]], source_guards=len(checked))))

if __name__ == '__main__':
    main()
