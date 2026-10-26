"""Read-only live collision positions for a paused host protocol.

Call player_obstacles(guest, collision_constants(source)) before each path
replan. Subtract its blocked cells from the raw blockdata floor, rather than
from a floor which has already permanently removed map.json spawn cells.
No step, input, RAM write, reset, or callable guest-function API is used.

Engine binding: event_object_movement.c DoesObjectCollideWithObjectAt checks
both currentCoords and previousCoords for every active other object, with
compatible elevation. follower_pikachu.c ignores Pikachu and Misty for the
player. Map numbers are deliberately not used to filter active objects;
the engine collision loop does not apply such a filter either.
"""
from pathlib import Path
import re
import struct


def collision_constants(source):
    """Read source constants; do not assume an object count or follower ID."""
    source = Path(source)
    fields = {
        'object_count': ('include/constants/global.h', 'OBJECT_EVENTS_COUNT'),
        'pikachu_id': ('include/constants/event_objects.h', 'LOCALID_FOLLOWER'),
        'misty_id': ('include/companion_misty.h', 'LOCALID_MISTY_COMPANION'),
    }
    result = {}
    for key, (relative, name) in fields.items():
        match = re.search(r'^#define\s+' + re.escape(name) +
                          r'\s+(0[xX][0-9a-fA-F]+|\d+)\b',
                          (source / relative).read_text(), re.M)
        if match is None:
            raise ValueError('Missing literal source constant ' + name)
        result[key] = int(match.group(1), 0)
    if not 1 <= result['object_count'] <= 256:
        raise ValueError('Invalid object count')
    return result


def _bitfield(record, schema, name):
    spec = schema['bitfields'][name]
    offset, size = spec['offset'], spec['size']
    if offset < 0 or size < 1 or offset + size > len(record):
        raise ValueError('Bitfield outside target ABI record: ' + name)
    return ((int.from_bytes(record[offset:offset + size], 'little') &
             spec['mask']) >> spec['shift'])


def player_obstacles(guest, constants):
    """Return live object records and a set of occupied local map cells.

    guest supplies .read(address, length), .sym, and the fresh ARM .schema.
    One array read contains all current/previous records at one paused host
    frame; reads do not advance emulation. Replan after every normal step.
    """
    schema, values = guest.schema, guest.schema['values']
    count, stride = constants['object_count'], values['sizes.ObjectEvent']
    avatar = guest.read(guest.sym['gPlayerAvatar'], values['sizes.PlayerAvatar'])
    player = avatar[values['offset.PlayerAvatar.objectEventId']]
    if not 0 <= player < count:
        raise ValueError('Player object is unavailable outside field state')
    raw = guest.read(guest.sym['gObjectEvents'], count * stride)
    if len(raw) != count * stride:
        raise ValueError('Truncated object array')
    records = []
    for index in range(count):
        record = raw[index * stride:(index + 1) * stride]
        if not _bitfield(record, schema, 'ObjectEvent.active'):
            continue
        item = {'index': index,
                'local_id': record[values['offset.ObjectEvent.localId']],
                'elevation': _bitfield(record, schema, 'ObjectEvent.currentElevation')}
        for field in ('currentCoords', 'previousCoords'):
            offset = values['offset.ObjectEvent.' + field]
            if values['size.ObjectEvent.' + field] != 4 or offset + 4 > stride:
                raise ValueError('Unexpected target coordinate ABI')
            point = struct.unpack_from('<hh', record, offset)
            item[field] = tuple(x - values['constant.MAP_OFFSET'] for x in point)
        records.append(item)
    player_record = next((r for r in records if r['index'] == player), None)
    if player_record is None:
        raise ValueError('Inactive player object')
    ignored = {constants['pikachu_id'], constants['misty_id']}
    blocked = set()
    for item in records:
        if item['index'] == player or item['local_id'] in ignored:
            continue
        a, b = player_record['elevation'], item['elevation']
        if a != 0 and b != 0 and a != b:
            continue
        blocked.add(item['currentCoords'])
        blocked.add(item['previousCoords'])
    return {'blocked': blocked, 'records': records, 'player_index': player,
            'player_xy': player_record['currentCoords']}
