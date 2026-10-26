"""Small read-only ELF32/ARM linker evidence reader (Python standard library)."""
from pathlib import Path
import hashlib
import re
import struct


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Elf:
    def __init__(self, path):
        self.path = Path(path)
        self.raw = self.path.read_bytes()
        assert self.raw[:7] == b'\x7fELF\x01\x01\x01', 'ELF32 little endian required'
        h = struct.unpack_from('<16sHHIIIIIHHHHHH', self.raw)
        assert h[2] == 40, 'ARM ELF required'
        self.kind = h[1]
        self.sections = []
        values = [struct.unpack_from('<10I', self.raw, h[6] + i*h[11]) for i in range(h[12])]
        strings = self.raw[values[h[13]][4]:sum(values[h[13]][4:6])]
        for i, row in enumerate(values):
            keys = ('name_offset', 'type', 'flags', 'address', 'offset', 'size', 'link', 'info', 'align', 'entsize')
            s = dict(zip(keys, row)); s['index'] = i
            s['name'] = strings[row[0]:strings.index(0, row[0])].decode('ascii')
            self.sections.append(s)
        self.symbols = []; self.tables = {}; self.by_name = {}
        for s in self.sections:
            if s['type'] != 2:
                continue
            st = self.sections[s['link']]; names = self.content(st); table = []
            table_bytes = self.content(s)
            for off in range(0, s['size'], s['entsize']):
                n, v, z, info, other, ndx = struct.unpack_from('<IIIBBH', table_bytes, off)
                name = names[n:names.index(0, n)].decode('utf8', 'replace')
                x = dict(name=name, value=v, size=z, bind=info>>4, type=info&15, ndx=ndx)
                table.append(x); self.symbols.append(x)
                if name and ndx:
                    self.by_name.setdefault(name, []).append(x)
            self.tables[s['index']] = table

    def content(self, section):
        return self.raw[section['offset']:section['offset'] + section['size']]

    def at(self, address, size):
        for s in self.sections:
            if s['type'] == 1 and s['address'] <= address and address+size <= s['address']+s['size']:
                p = address-s['address']; return self.content(s)[p:p+size]
        raise AssertionError(('ELF address has no stored bytes', hex(address), size))

    def one(self, name):
        rows = self.by_name.get(name, [])
        assert len(rows) == 1, ('Non-unique or missing symbol', name, len(rows))
        return rows[0]

    def named_bytes(self, name, size=None):
        s = self.one(name)
        if self.kind == 1:
            raw = self.content(self.sections[s['ndx']])
            return raw[s['value']:s['value'] + (s['size'] if size is None else size)]
        address = s['value'] & ~1 if s['type'] == 2 else s['value']
        return self.at(address, s['size'] if size is None else size)


def lz77(raw):
    assert raw[0] == 0x10
    size = int.from_bytes(raw[1:4], 'little'); out = bytearray(); i = 4
    while len(out) < size:
        flags = raw[i]; i += 1
        for bit in range(7, -1, -1):
            if len(out) == size:
                break
            if flags & (1 << bit):
                a, b = raw[i:i+2]; i += 2; count = (a >> 4)+3; delta = ((a&15)<<8 | b)+1
                assert delta <= len(out)
                for _ in range(count):
                    if len(out) == size: break
                    out.append(out[-delta])
            else:
                out.append(raw[i]); i += 1
    return bytes(out)


def map_sections(text, unit):
    """Read one input object's map entries, including wrapped section names."""
    normalized = re.sub(r'(?m)^\s*([.\w]+)\s*\n\s*(0x[0-9a-fA-F]+)', r' \1 \2', text)
    expression = (r'(?m)^\s*([.\w]+)\s+(0x[0-9a-fA-F]+)\s+'
                  r'(0x[0-9a-fA-F]+)\s+(?:\./)?' + re.escape(unit) + r'\s*$')
    rows = {}
    for name, address, size in re.findall(expression, normalized):
        address, size = int(address, 16), int(size, 16)
        if size:
            assert name not in rows, ('Duplicate object section placement', unit, name)
            rows[name] = (address, size)
    assert rows, ('Object has no linker-map placements', unit)
    return rows


def audit_object(path, unit, final, rom, maptext):
    """Resolve actual candidate relocations, then compare every allocated ROM byte.

    The method follows the project's earlier independent relocation audit. Only
    immutable files beneath the selected artifact directory are used. No cached
    Windows objects or previous ROMs are substituted.
    """
    obj = Elf(path); assert obj.kind == 1
    placements = map_sections(maptext, unit); sections = []; counts = {}

    def value(sym):
        if sym['ndx'] == 0xfff1:
            return sym['value']
        if 0 < sym['ndx'] < len(obj.sections):
            section = obj.sections[sym['ndx']]
            if section['name'] in placements and placements[section['name']][0]:
                return placements[section['name']][0] + sym['value']
        matches = final.by_name.get(sym['name'], [])
        exported = [x for x in matches if x['bind']]
        if exported: matches = exported
        assert len(matches) == 1, ('Unresolved relocation', unit, sym['name'])
        return matches[0]['value']

    for section in obj.sections:
        if not section['flags'] & 2 or not section['size']:
            continue
        assert section['name'] in placements, (unit, section['name'])
        address, size = placements[section['name']]
        assert size == section['size']
        if section['type'] == 8 or not 0x08000000 <= address < 0x0a000000:
            sections.append(dict(name=section['name'], bytes=size, address=hex(address), scope='RAM/non-ROM; separate symbol ABI gate'))
            continue
        raw = obj.content(section); want = bytearray(raw); actual = final.at(address, size); relocations = []
        for rel in obj.sections:
            if rel['type'] != 9 or rel['info'] != section['index']:
                continue
            assert rel['entsize'] == 8
            for offset in range(0, rel['size'], 8):
                p, info = struct.unpack_from('<II', obj.content(rel), offset)
                typ = info & 255; sym = obj.tables[rel['link']][info >> 8]
                word = struct.unpack_from('<I', raw, p)[0]; place = address+p
                detail = dict(offset=p, type=typ, symbol=sym['name'])
                if typ == 2:  # R_ARM_ABS32
                    struct.pack_into('<I', want, p, (value(sym)+word)&0xffffffff)
                elif typ == 3:  # R_ARM_REL32
                    struct.pack_into('<I', want, p, (value(sym)+word-place)&0xffffffff)
                elif typ == 40:  # R_ARM_V4BX, unchanged ARM7TDMI BX
                    assert word & 0x0ffffff0 == 0x012fff10
                elif typ in (10, 30):  # Thumb BL / legacy THM_PC22
                    a, b = struct.unpack_from('<HH', raw, p)
                    assert a&0xf800 == 0xf000 and b&0xf800 == 0xf800
                    add = (a&2047)<<12 | (b&2047)<<1
                    if add & (1<<22): add -= 1<<23
                    symbol_value = value(sym); target = symbol_value&~1; delta = target+add-place
                    if not -(1<<22) <= delta < (1<<22):
                        a2, b2 = struct.unpack_from('<HH', actual, p)
                        assert a2&0xf800 == 0xf000 and b2&0xf800 == 0xf800
                        encoded = (a2&2047)<<12 | (b2&2047)<<1
                        if encoded & (1<<22): encoded -= 1<<23
                        stub_address = place+4+encoded; stub = final.at(stub_address, 16)
                        assert add == -4 and stub[:12] == bytes.fromhex('7847fde700c09fe51cff2fe1')
                        assert struct.unpack_from('<I', stub, 12)[0] == symbol_value
                        named = final.one('__'+sym['name']+'_veneer')
                        assert named['value'] == stub_address|1 and named['size'] == 16
                        assert rom[stub_address-0x08000000:stub_address-0x08000000+16] == stub
                        detail['validated_veneer'] = dict(name=named['name'], address=hex(stub_address), sha256=sha(stub))
                        target = stub_address; delta = target+add-place
                    assert -(1<<22) <= delta < (1<<22) and delta%2 == 0
                    struct.pack_into('<HH', want, p, 0xf000|((delta>>12)&2047), 0xf800|((delta>>1)&2047))
                else:
                    raise AssertionError(('Unsupported actual relocation; no fallback', unit, section['name'], typ, p))
                assert want[p:p+4] == actual[p:p+4], (unit, section['name'], detail)
                counts[str(typ)] = counts.get(str(typ), 0)+1; relocations.append(detail)
        assert bytes(want) == actual, ('Object payload mismatch', unit, section['name'])
        assert rom[address-0x08000000:address-0x08000000+size] == actual
        sections.append(dict(name=section['name'], address=hex(address), bytes=size, sha256=sha(actual), relocations=relocations, ROM_exact=True))
    assert any(x.get('ROM_exact') for x in sections), ('No ROM contribution', unit)
    return dict(unit=unit, object_sha256=sha(obj.raw), sections=sections, relocation_counts=counts, all_allocated_ROM_bytes_exact=True)
