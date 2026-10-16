"""Canonical, deterministic Route29 landscape adjustment; no file I/O."""
import hashlib
import struct

INPUT_SHA = 'aedcb49f54b0d6fae8d5f2c625a73199181d9d18d9f4c5af1c08f80773418ed8'
OUTPUT_SHA = '5627de7b6074aded401ea881930c2e19e2c25463196011d13d673ea5ccdef762'
GROVES = [(5, 3, 8, 4), (22, 4, 10, 4), (8, 17, 8, 4), (27, 17, 8, 4)]


def improve_route29(original):
    assert len(original) == 24 and all(len(row) == 40 for row in original)
    data = struct.pack('<960H', *(v for row in original for v in row))
    current = hashlib.sha256(data).hexdigest()
    if current == OUTPUT_SHA:
        return [row[:] for row in original]
    assert current == INPUT_SHA, 'Route29 source changed; do not redraw a different map'
    result = [row[:] for row in original]
    # Pair each grove from its own origin. Global x/y parity cut half a tree
    # at the odd-origin rectangles (5,3), (8,17) and (27,17).
    for x0, y0, width, height in GROVES:
        assert width % 2 == height % 2 == 0
        for dy in range(height):
            for dx in range(width):
                if dy == 0:
                    mid = (0x00e, 0x00f)[dx % 2]
                elif dy == height - 1:
                    mid = (0x016, 0x017)[dx % 2]
                else:
                    mid = ((0x01c, 0x01d) if dy % 2 == 0 else (0x014, 0x015))[dx % 2]
                old = original[y0+dy][x0+dx]
                assert (old >> 10) & 3 == 1
                result[y0+dy][x0+dx] = (old & 0xfc00) | mid
    # The three-row passage is already clear and already connects both maps.
    # Keep the two-column seam buffers byte-identical to the old map.
    for y in range(11, 14):
        for x in range(2, 38):
            old = original[y][x]
            assert not old & 0x0c00 and old >> 12 == 3
            result[y][x] = (old & 0xfc00) | 0x296
    # Small passable flower groups give the clearings scale without moving
    # an NPC, altering the 12 tall-grass cells, or blocking an old save spot.
    for x, y in [(17,4),(18,4),(17,5),(19,5),(14,7),(15,7),
                 (19,17),(20,17),(19,18),(22,19),(23,19),(24,20),
                 (4,19),(5,19),(3,20),(36,3),(36,4)]:
        old = original[y][x]
        assert old == 0x3001
        result[y][x] = 0x3004
    return result
