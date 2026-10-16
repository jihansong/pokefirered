"""Compile a read-only Devon ABI probe against the current, SHA-locked source.

No game binary/source/SAV is changed. The output is a fresh work subdirectory.
Offsets are compiler-derived; PaletteFade.active is read from initialized data,
never from offsetof(bitfield). This preparation is not a native QA pass.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys

ROM_SHA = 'e1560c21cf51c7c1c2af8dd04f3f6a429eb3d6af4f3e157bc66aa187bef65c34'
ELF_SHA = '64bad582cd8e51da6fce54e74ff4e59c9626e525596b53b37de7877dc3e224e3'
SOURCE_SHA = {
    'src/party_menu.c': '93ae68d66132c036978a01fcd27f9d24a83bd94b212f8a02abbe6f566c92a7dd',
    'src/menu.c': '19158e25455ffed14afa516f0aa89c3412b3243dd11b5d7050cd41402db2a8ad',
    'src/data/party_menu.h': '9bbf14a1f421b6e4d80537ebb9dca96ba941e890c8d7ee20068bce237af5e842',
    'include/party_menu.h': '092ddbb884929cbaa0ef80ba367fbde335126c176c586b24a277d22dda098454',
    'include/task.h': '4d04e9fd43d54ef551d456da14fdf2a56d9d91fc19a4fc9582b289a06c192612',
    'include/pokemon.h': '02fbde9fcef7f684b93389c6d31f825ce8e9d43549738dbe7ac1502ebc8d7d40',
    'include/battle.h': '9b774f757d1e5aa72f3ebcf4ced3a12c165c28ff848e2bb529d228534a4b206d',
    'include/palette.h': '3f5ee66bab01538193629ffef3ff3cd6ad7555f7e294f52ae3ccfa36f94ac418',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def mask_comments_strings(text):
    # Keep every index/newline stable while making braces inside comments inert.
    token = r'/\*[\s\S]*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    return re.sub(token, lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), text)


def struct_body(text, prefix, suffix=None):
    clean = mask_comments_strings(text)
    matches = list(re.finditer(prefix, clean))
    if suffix is not None:
        matches = [m for m in matches if re.match(suffix, clean[closing_brace(clean, m.end() - 1) + 1:])]
    check(len(matches) == 1, 'Struct extraction must have one exact match: ' + prefix)
    opening = matches[0].end() - 1
    closing = closing_brace(clean, opening)
    return text[opening + 1:closing]


def closing_brace(clean, opening):
    check(clean[opening] == '{', 'Expected opening brace')
    depth = 1
    for index in range(opening + 1, len(clean)):
        if clean[index] == '{':
            depth += 1
        elif clean[index] == '}':
            depth -= 1
            if depth == 0:
                return index
    raise RuntimeError('Unbalanced source struct')


class Elf32:
    """Minimal bounds-checked ELF32 little-endian ARM reader, no dependencies."""
    def __init__(self, path):
        self.blob = Path(path).read_bytes()
        check(self.blob[:7] == b'\x7fELF\x01\x01\x01', 'Expected little-endian ELF32')
        check(len(self.blob) >= 52, 'Short ELF header')
        header = struct.unpack_from('<HHIIIIIHHHHHH', self.blob, 16)
        check(header[1] == 40, 'Expected ARM e_machine')
        section_offset, section_stride, count = header[5], header[10], header[11]
        check(section_stride >= 40 and count > 0, 'Unsupported ELF section table')
        check(section_offset + section_stride * count <= len(self.blob), 'Invalid section bounds')
        self.sections = [struct.unpack_from('<10I', self.blob, section_offset + i * section_stride) for i in range(count)]
        self.symbols = {}
        for sec in self.sections:
            if sec[1] != 2:  # SHT_SYMTAB
                continue
            check(sec[6] < count and sec[9] >= 16 and sec[5] % sec[9] == 0, 'Invalid symbol table')
            strings = self.section_data(sec[6])
            payload = self.section_data(self.sections.index(sec))
            translation_unit = None
            for index in range(0, len(payload), sec[9]):
                name, value, size, info, other, shndx = struct.unpack_from('<IIIBBH', payload, index)
                check(name < len(strings), 'Invalid symbol name offset')
                end = strings.find(b'\0', name)
                check(end >= 0, 'Unterminated symbol name')
                label = strings[name:end].decode('utf-8')
                if (info & 15) == 4:  # STT_FILE owns subsequent local symbols
                    translation_unit = label
                elif label and shndx != 0:
                    self.symbols.setdefault(label, []).append({'value': value, 'size': size, 'section': shndx, 'info': info, 'translation_unit': translation_unit, 'symbol_index': index // sec[9]})

    def section_data(self, index):
        sec = self.sections[index]
        if sec[1] == 8:  # SHT_NOBITS
            return bytes(sec[5])
        check(sec[4] + sec[5] <= len(self.blob), 'Invalid section payload bounds')
        return self.blob[sec[4]:sec[4] + sec[5]]

    def symbol(self, label, translation_unit=None):
        rows = self.symbols.get(label, [])
        if len(rows) != 1 and translation_unit is not None:
            rows = [r for r in rows if (r.get('translation_unit') or '').replace(chr(92), '/').rsplit('/', 1)[-1].removesuffix('.o').removesuffix('.c') == translation_unit.removesuffix('.o').removesuffix('.c')]
        check(len(rows) == 1, 'Missing/ambiguous ELF symbol: ' + label + '; candidates=' + repr(self.symbols.get(label, [])))
        return rows[0]

    def symbol_bytes(self, label):
        row = self.symbol(label)
        check(row['section'] < len(self.sections), 'Symbol has no file-backed section: ' + label)
        sec = self.sections[row['section']]
        offset = row['value'] - sec[3]
        raw = self.section_data(row['section'])
        check(offset >= 0 and offset + row['size'] <= len(raw), 'Invalid symbol data bounds: ' + label)
        return raw[offset:offset + row['size']]


def tool_path(explicit, basename):
    if explicit:
        path = Path(explicit).resolve()
    else:
        devkit = Path(os.environ.get('DEVKITARM', '/opt/devkitpro/devkitARM'))
        preferred = devkit / 'bin' / basename
        found = shutil.which(basename)
        path = preferred if preferred.is_file() else Path(found or '')
    check(path.is_file(), 'Compiler tool unavailable: ' + basename)
    return str(path.resolve())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='/workspaces/pokefirered')
    parser.add_argument('--rom', default='pokemonthyl.gba')
    parser.add_argument('--elf', default='pokemonthyl.elf')
    parser.add_argument('--out', default='work/hoenn-devon-native-20261013/abi-probe-v2')
    parser.add_argument('--gcc')
    parser.add_argument('--nm')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    def rooted(value):
        value = Path(value)
        return (value if value.is_absolute() else root / value).resolve()
    rom, elf, out = rooted(args.rom), rooted(args.elf), rooted(args.out)
    check(rom.is_relative_to(root) and elf.is_relative_to(root), 'ROM and ELF must be in workspace')
    check(out.is_relative_to(root / 'work') and not out.exists(), 'Use a fresh workspace/work output directory')
    protected = {rom: ROM_SHA, elf: ELF_SHA}
    protected.update({root / key: value for key, value in SOURCE_SHA.items()})
    for path, wanted in protected.items():
        check(sha(path) == wanted, 'Input SHA mismatch: ' + str(path))
    gcc, nm = tool_path(args.gcc, 'arm-none-eabi-gcc'), tool_path(args.nm, 'arm-none-eabi-nm')
    party = (root / 'src/party_menu.c').read_text()
    menu = (root / 'src/menu.c').read_text()
    cursor = (root / 'src/data/party_menu.h').read_text()
    private_party = struct_body(party, r'\bstruct\s+PartyMenuInternal\s*\{')
    private_menu = struct_body(menu, r'\bstruct\s+Menu\s*\{')
    private_cursor = struct_body(cursor, r'\bstatic\s+struct\s*\{', r'\s*const\s+sCursorOptions\s*\[\s*\]\s*=')
    expressions = {
        'PartyMenu.slotId': '__builtin_offsetof(struct PartyMenu, slotId)',
        'PartyMenu.action': '__builtin_offsetof(struct PartyMenu, action)',
        'Task.size': 'sizeof(struct Task)',
        'Task.func': '__builtin_offsetof(struct Task, func)',
        'Task.isActive': '__builtin_offsetof(struct Task, isActive)',
        'Pokemon.hp': '__builtin_offsetof(struct Pokemon, hp)',
        'PartyMenuInternal.actions': '__builtin_offsetof(struct PartyMenuInternal, actions)',
        'PartyMenuInternal.numActions': '__builtin_offsetof(struct PartyMenuInternal, numActions)',
        'Menu.cursorPos': '__builtin_offsetof(struct Menu, cursorPos)',
        'BattleStruct.playerPartyIdx': '__builtin_offsetof(struct BattleStruct, playerPartyIdx)',
        'CursorOption.size': 'sizeof(struct DevonCursorOption)',
        'CursorOption.text': '__builtin_offsetof(struct DevonCursorOption, text)',
        'CursorOption.func': '__builtin_offsetof(struct DevonCursorOption, func)',
        'PartyMenu.size': 'sizeof(struct PartyMenu)',
        'Menu.size': 'sizeof(struct Menu)',
        'Pokemon.size': 'sizeof(struct Pokemon)',
        'PaletteFade.size': 'sizeof(struct PaletteFadeControl)',
    }
    c = '\n'.join('#include "' + h + '"' for h in ['global.h', 'gflib.h', 'main.h', 'task.h', 'party_menu.h', 'pokemon.h', 'battle.h', 'palette.h'])
    c += '\nstruct PartyMenuInternal {' + private_party + '\n};\n'
    c += 'struct Menu {' + private_menu + '\n};\n'
    c += 'struct DevonCursorOption {' + private_cursor + '\n};\n'
    symbol_for = {key: 'devon_abi_' + key.replace('.', '_') for key in expressions}
    for key, expr in expressions.items():
        c += 'char ' + symbol_for[key] + '[(' + expr + ') + 1];\n'
    c += 'char devon_abi_task_count[(NUM_TASKS) + 1];\n'
    c += 'struct PaletteFadeControl devon_abi_palette_zero __attribute__((section(".abi_data"), used)) = {0};\n'
    c += 'struct PaletteFadeControl devon_abi_palette_active __attribute__((section(".abi_data"), used)) = {.active = 1};\n'
    out.mkdir(parents=True)
    probe_c, probe_o = out / 'devon-abi-probe.c', out / 'devon-abi-probe.o'
    probe_c.write_text(c)
    flags = ['-c', '-w', '-mthumb', '-mabi=apcs-gnu', '-march=armv4t', '-fcommon', '-iquote', 'include', '-DLEAFGREEN', '-DREVISION=0', '-DENGLISH', '-DMODERN=1']
    compile_cmd = [gcc] + flags + [str(probe_c), '-o', str(probe_o)]
    compiled = subprocess.run(compile_cmd, cwd=root, text=True, capture_output=True)
    (out / 'compiler.log').write_text(compiled.stdout + compiled.stderr)
    check(compiled.returncode == 0, 'ABI compilation failed; inspect ' + str(out / 'compiler.log'))
    nm_cmd = [nm, '-S', '--defined-only', str(probe_o)]
    nm_run = subprocess.run(nm_cmd, cwd=root, text=True, capture_output=True)
    (out / 'nm-symbols.txt').write_text(nm_run.stdout + nm_run.stderr)
    check(nm_run.returncode == 0, 'ABI nm failed')
    nm_sizes = {}
    for line in nm_run.stdout.splitlines():
        match = re.fullmatch(r'\s*([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([A-Za-z])\s+(\S+)\s*', line)
        if match and match[4].startswith('devon_abi_'):
            check(match[4] not in nm_sizes, 'Duplicate nm probe symbol')
            nm_sizes[match[4]] = int(match[2], 16)
    obj = Elf32(probe_o)
    for symbol in [*symbol_for.values(), 'devon_abi_task_count']:
        check(symbol in nm_sizes and nm_sizes[symbol] == obj.symbol(symbol)['size'], 'nm/ELF size mismatch: ' + symbol)
    offsets = {key: nm_sizes[symbol] - 1 for key, symbol in symbol_for.items()}
    task_count = nm_sizes['devon_abi_task_count'] - 1
    zero, active = obj.symbol_bytes('devon_abi_palette_zero'), obj.symbol_bytes('devon_abi_palette_active')
    check(len(zero) == len(active) == offsets['PaletteFade.size'] and not any(zero), 'Invalid palette initialization')
    differences = [(i, a ^ b) for i, (a, b) in enumerate(zip(zero, active)) if a != b]
    check(len(differences) == 1, 'Palette active must change exactly one byte')
    byte_offset, bit_mask = differences[0]
    check(bit_mask > 0 and bit_mask & (bit_mask - 1) == 0, 'Palette active must be a single bit')
    offsets['PaletteFade.active.byteOffset'] = byte_offset
    offsets['PaletteFade.active.mask'] = bit_mask
    check(offsets['CursorOption.size'] == 8 and offsets['CursorOption.text'] == 0 and offsets['CursorOption.func'] == 4, 'CursorOption ABI differs from v7 contract')
    check(1 <= task_count <= 32 and offsets['Pokemon.size'] == 100, 'Task/Pokemon ABI outside v7 contract')
    linked = Elf32(elf)
    owners = {'sMenu': 'menu.c', 'sPartyMenuInternal': 'party_menu.c',
              'sCursorOptions': 'party_menu.c', 'CB2_UpdatePartyMenu': 'party_menu.c',
              'Task_HandleChooseMonInput': 'party_menu.c',
              'Task_HandleSelectionMenuInput': 'party_menu.c',
              'CursorCB_SendMon': 'party_menu.c'}
    required_names = ['CB2_UpdatePartyMenu', 'Task_HandleChooseMonInput', 'Task_HandleSelectionMenuInput', 'CursorCB_SendMon', 'gPartyMenu', 'sPartyMenuInternal', 'sMenu', 'gBattlePartyCurrentOrder', 'gBattlerPartyIndexes', 'gBattlersCount', 'gBattlerInMenuId', 'gBattleStruct', 'sCursorOptions', 'gText_SendOut', 'gSelectedMonPartyId', 'gTasks', 'gBattleOutcome', 'BattleMainCB2', 'gPaletteFade']
    (out / 'linked-symbol-candidates.json').write_text(json.dumps({n: linked.symbols.get(n, []) for n in required_names}, indent=2) + '\n')
    bindings = {n: linked.symbol(n, owners.get(n)) for n in required_names}
    linked_sizes = {
        'gPartyMenu': offsets['PartyMenu.size'], 'sMenu': offsets['Menu.size'],
        'gPaletteFade': offsets['PaletteFade.size'], 'gTasks': offsets['Task.size'] * task_count,
        'gPlayerParty': offsets['Pokemon.size'] * 6,
    }
    for name, wanted in linked_sizes.items():
        check(linked.symbol(name, owners.get(name))['size'] == wanted, 'Linked ELF public ABI size mismatch: ' + name)
    cursor_size = bindings['sCursorOptions']['size']
    check(cursor_size > 0 and cursor_size % offsets['CursorOption.size'] == 0, 'Invalid linked cursor option array')
    # Capture compiler dependencies so the runner also protects transitive headers.
    dep_cmd = [gcc] + [f for f in flags if f != '-c'] + ['-MM', str(probe_c)]
    deps = subprocess.run(dep_cmd, cwd=root, text=True, capture_output=True)
    (out / 'dependencies.txt').write_text(deps.stdout + deps.stderr)
    check(deps.returncode == 0, 'Header dependency extraction failed')
    source_sha = dict(SOURCE_SHA)
    joined = deps.stdout.replace('\\\n', ' ').partition(':')[2]
    for token in joined.split():
        dep = rooted(token)
        check(dep.is_file(), 'Missing compiler dependency: ' + token)
        if dep.is_relative_to(root) and dep != probe_c:
            source_sha[dep.relative_to(root).as_posix()] = sha(dep)
    for path, wanted in protected.items():
        check(sha(path) == wanted, 'Protected input changed while probing: ' + str(path))
    manifest = {
        'rom_sha256': ROM_SHA, 'elf_sha256': ELF_SHA, 'task_count': task_count,
        'source_sha256': source_sha, 'offsets': offsets,
        'symbol_bindings': bindings, 'symbol_binding_method': 'STT_FILE-qualified local symbol ownership; unique globals',
        'method': 'ARM GCC common-symbol sizes minus one; ELF32 initialized PaletteFade active byte; linked public object sizes cross-checked',
        'compiler_command': compile_cmd, 'compiler_sha256': sha(gcc),
        'nm_command': nm_cmd, 'nm_sha256': sha(nm),
        'probe_c_sha256': sha(probe_c), 'probe_o_sha256': sha(probe_o),
        'palette_active_raw_hex': active.hex(), 'palette_zero_raw_hex': zero.hex(),
        'linked_public_sizes': linked_sizes, 'linked_cursor_array_size': cursor_size,
        'protected_inputs_unchanged': True, 'native_qa_executed': False,
    }
    destination = out / 'devon-v7-abi.json'
    destination.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'abi_json': str(destination), 'abi_sha256': sha(destination), 'task_count': task_count, 'offsets': offsets, 'native_qa_executed': False}), flush=True)


if __name__ == '__main__':
    main()
