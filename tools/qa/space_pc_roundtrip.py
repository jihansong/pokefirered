"""Normal-key PC main-menu/ON-OFF check. No host launch or memory writes.

This bounded first check deliberately does not claim BOX/storage coverage.
VMap ABI is checked against the exact current C declaration and ARM pointer ABI.
"""
import re
import struct


def pc_roundtrip(guest, tour, case):
    assert case['script'] == 'SpaceFacility_PC'
    assert tour.name() == case['map'], 'Caller must use ordinary doors to reach room'
    assert guest.schema['abi']['pointer_bytes'] == 4
    for name in ('VMap', 'gStringVar4', 'Text_BootedUpPC', 'Text_AccessWhichPC'):
        assert name in guest.sym, ('Missing fresh PC symbol', name)
    declaration = (tour.source/'include/global.fieldmap.h').read_text(encoding='utf8')
    assert re.search(r'struct\s+BackupMapLayout\s*\{\s*s32\s+Xsize;\s*s32\s+Ysize;\s*u16\s*\*\s*map;\s*\};', declaration), 'Unsupported VMap declaration; derive ABI before proceeding'
    v = guest.values
    room = tour.maps[case['map']]
    stand = tuple(case['stand'])
    assert stand == (6, 2) and case['direction'] == 'N'
    target = (6, 1)

    def tile():
        width, height, pointer = struct.unpack('<iiI', guest.read(guest.sym['VMap'], 12))
        assert width == room['w']+v['constant.MAP_OFFSET_W']
        assert height == room['h']+v['constant.MAP_OFFSET_H']
        assert 0x02000000 <= pointer < 0x02040000
        x, y = target[0]+v['constant.MAP_OFFSET'], target[1]+v['constant.MAP_OFFSET']
        offset = (y*width+x)*2
        assert 0 <= offset < width*height*2 and pointer+offset+2 <= 0x02040000
        return int.from_bytes(guest.read(pointer+offset, 2), 'little') & 1023

    def text_seen(label):
        # PLAYER placeholders expand in gStringVar4; compare the longest
        # literal ROM span rather than assuming a particular trainer name.
        raw = guest.read(guest.sym[label], 128).split(b'\xff', 1)[0]
        chunks, current, index = [], bytearray(), 0
        while index < len(raw):
            if raw[index] == 0xfd:
                chunks.append(bytes(current)); current.clear(); index += 2
            else:
                current.append(raw[index]); index += 1
        chunks.append(bytes(current))
        needle = max(chunks, key=len)[:32]
        assert len(needle) >= 8
        return needle in guest.read(guest.sym['gStringVar4'], 128)

    tour.walk(case['map'], stand)
    before = guest.snapshot()
    assert guest.field(before) and not before['script_locked'] and tile() == 1005

    def stable():
        snap = guest.snapshot()
        assert snap['map'] == before['map'] and snap['xy'] == before['xy']
        return snap

    def wait_text(label):
        for _ in range(30):
            stable()
            if text_seen(label):
                return
            guest.step(0, 24)
        raise AssertionError(('PC text not reached', label))

    guest.step(64, 1); guest.step(0, 12); stable()
    guest.picture('pc-approach-off')
    guest.tap('A', settle=24)
    wait_text('Text_BootedUpPC')
    guest.step(0, 180)
    assert tile() == 1006 and stable()['script_locked'], 'PC ON tile/locked dialogue not observed'
    guest.picture('pc-booted-on')
    guest.tap('A', settle=24)
    wait_text('Text_AccessWhichPC')
    guest.step(0, 180)
    assert tile() == 1006 and stable()['script_locked']
    guest.picture('pc-actual-main-menu-on')
    guest.tap('B', settle=24)
    for _ in range(30):
        snap = stable()
        if guest.field(snap) and not snap['script_locked'] and tile() == 1005:
            break
        guest.step(0, 24)
    else:
        raise AssertionError('Normal PC menu cancel did not restore OFF tile and field controls')
    guest.picture('pc-cancelled-off-field')
    return {'status': 'PASS_ACTUAL_PC_MAIN_AND_ON_OFF_ONLY', 'before': before,
            'after': guest.snapshot(), 'live_backup_map_tile_sequence': [1005, 1006, 1005],
            'text_labels_observed': ['Text_BootedUpPC', 'Text_AccessWhichPC'],
            'runtime_memory_writes': 0, 'storage_or_BOX_verified': False,
            'pending': 'Someone/Bill -> Storage menu -> Move Pokemon BOX -> cancel to PC menu requires separate actual observation'}
