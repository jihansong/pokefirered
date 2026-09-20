#!/usr/bin/env python3
"""Create a BPS patch that turns the original LeafGreen ROM into Thunder Yellow.

The patch holds only the differences, so it can be shared without the
original ROM. Apply it with any BPS patcher (Flips, beat, RomPatcher.js).

Usage:
    python3 tools/make_bps_patch.py [ORIGINAL.gba] [MODIFIED.gba] [OUTPUT.bps]

ORIGINAL defaults to baserom_leafgreen.gba, MODIFIED to pokemonthyl.gba
(built with `make leafgreen`) and OUTPUT to pokemonthyl.bps. The original
must be the retail English LeafGreen (v1.0); any other source prints a
warning, because the patch would only apply to that exact file. The finished
patch is decoded again and checked against MODIFIED before the script exits.

Keep your ROM as baserom_leafgreen.gba. `make clean` deletes every poke*.gba
in the repository, so a ROM kept as pokeleafgreen.gba is thrown away with the
build output.

If it ever goes missing, the base ROM can be rebuilt from the decompilation
itself, since pret/pokefirered reproduces the retail cartridge byte for byte:

    git worktree add /tmp/base upstream/master
    ln -s "$PWD/tools/agbcc" /tmp/base/tools/agbcc
    make -C /tmp/base leafgreen -j"$(nproc)"
    (cd /tmp/base && sha1sum -c leafgreen.sha1)     # pokeleafgreen.gba: OK
    cp /tmp/base/pokeleafgreen.gba baserom_leafgreen.gba
"""

import hashlib
import os
import sys
import zlib

LEAFGREEN_SHA1 = "574fa542ffebb14be69902d1d36f1ec0a4afd71e"

SOURCE_READ, TARGET_READ, SOURCE_COPY, TARGET_COPY = range(4)

# Runs shorter than this are cheaper to store as literal bytes than as a copy.
MIN_COPY = 4


def encode_number(value):
    out = bytearray()
    while True:
        x = value & 0x7F
        value >>= 7
        if value == 0:
            out.append(0x80 | x)
            return out
        out.append(x)
        value -= 1


def decode_number(data, pos):
    value, shift = 0, 1
    while True:
        x = data[pos]
        pos += 1
        value += (x & 0x7F) * shift
        if x & 0x80:
            return value, pos
        shift <<= 7
        value += shift


def build_source_index(source):
    """Map each 4-byte sequence in the source to the offsets where it starts."""
    index = {}
    for i in range(len(source) - MIN_COPY + 1):
        key = source[i:i + MIN_COPY]
        offsets = index.get(key)
        if offsets is None:
            index[key] = [i]
        elif len(offsets) < 8:
            offsets.append(i)
    return index


def match_length(a, a_pos, b, b_pos, limit):
    n = 0
    while n < limit and a[a_pos + n] == b[b_pos + n]:
        n += 1
    return n


def create_patch(source, target):
    patch = bytearray(b"BPS1")
    patch += encode_number(len(source))
    patch += encode_number(len(target))
    patch += encode_number(0)  # no metadata

    index = build_source_index(source)
    literal = bytearray()
    source_rel = 0  # position the decoder's SourceCopy offset is relative to
    pos = 0

    def flush_literal():
        if literal:
            patch.extend(encode_number(((len(literal) - 1) << 2) | TARGET_READ))
            patch.extend(literal)
            literal.clear()

    while pos < len(target):
        remaining = len(target) - pos

        # Unchanged bytes at the same offset
        if pos < len(source):
            n = match_length(source, pos, target, pos, min(remaining, len(source) - pos))
            if n >= MIN_COPY:
                flush_literal()
                patch.extend(encode_number(((n - 1) << 2) | SOURCE_READ))
                pos += n
                continue

        # Data that moved within the ROM
        best_len, best_off = 0, 0
        if remaining >= MIN_COPY:
            for off in index.get(target[pos:pos + MIN_COPY], ()):
                n = match_length(source, off, target, pos, min(remaining, len(source) - off))
                if n > best_len:
                    best_len, best_off = n, off
        if best_len >= 16:
            flush_literal()
            patch.extend(encode_number(((best_len - 1) << 2) | SOURCE_COPY))
            delta = best_off - source_rel
            patch.extend(encode_number((abs(delta) << 1) | (delta < 0)))
            source_rel = best_off + best_len
            pos += best_len
            continue

        literal.append(target[pos])
        pos += 1

    flush_literal()
    patch += zlib.crc32(source).to_bytes(4, "little")
    patch += zlib.crc32(target).to_bytes(4, "little")
    patch += zlib.crc32(patch).to_bytes(4, "little")
    return bytes(patch)


def apply_patch(source, patch):
    if patch[:4] != b"BPS1":
        raise ValueError("not a BPS patch")
    if zlib.crc32(patch[:-4]) != int.from_bytes(patch[-4:], "little"):
        raise ValueError("patch checksum mismatch")
    pos = 4
    source_size, pos = decode_number(patch, pos)
    target_size, pos = decode_number(patch, pos)
    metadata_size, pos = decode_number(patch, pos)
    pos += metadata_size
    if len(source) != source_size or zlib.crc32(source) != int.from_bytes(patch[-12:-8], "little"):
        raise ValueError("source ROM does not match the patch")

    target = bytearray()
    source_rel = target_rel = 0
    end = len(patch) - 12
    while pos < end:
        data, pos = decode_number(patch, pos)
        command, length = data & 3, (data >> 2) + 1
        if command == SOURCE_READ:
            target += source[len(target):len(target) + length]
        elif command == TARGET_READ:
            target += patch[pos:pos + length]
            pos += length
        else:
            data, pos = decode_number(patch, pos)
            delta = -(data >> 1) if data & 1 else data >> 1
            if command == SOURCE_COPY:
                source_rel += delta
                target += source[source_rel:source_rel + length]
                source_rel += length
            else:
                target_rel += delta
                for _ in range(length):
                    target.append(target[target_rel])
                    target_rel += 1
    if len(target) != target_size or zlib.crc32(target) != int.from_bytes(patch[-8:-4], "little"):
        raise ValueError("patched ROM checksum mismatch")
    return bytes(target)


DEFAULT_SOURCES = ("baserom_leafgreen.gba", "baserom.gba")


def main(argv):
    if len(argv) > 1 and argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    if len(argv) > 1:
        source_path = argv[1]
    else:
        source_path = next((p for p in DEFAULT_SOURCES if os.path.exists(p)), None)
        if source_path is None:
            print("error: no base ROM. Put the retail LeafGreen ROM in the repository "
                  "as baserom_leafgreen.gba (not pokeleafgreen.gba: `make clean` deletes "
                  "every poke*.gba), or pass its path.", file=sys.stderr)
            return 1
    target_path = argv[2] if len(argv) > 2 else "pokemonthyl.gba"
    patch_path = argv[3] if len(argv) > 3 else "pokemonthyl.bps"

    with open(source_path, "rb") as f:
        source = f.read()
    with open(target_path, "rb") as f:
        target = f.read()

    source_sha1 = hashlib.sha1(source).hexdigest()
    if source_sha1 != LEAFGREEN_SHA1:
        print("warning: %s is not the retail pokeleafgreen.gba (sha1 %s, expected %s);\n"
              "         the patch will only apply to this exact file."
              % (source_path, source_sha1, LEAFGREEN_SHA1), file=sys.stderr)

    patch = create_patch(source, target)
    if apply_patch(source, patch) != target:
        print("error: the patch does not reproduce %s" % target_path, file=sys.stderr)
        return 1
    with open(patch_path, "wb") as f:
        f.write(patch)
    print("%s: %d bytes (source %s, target %s, verified)"
          % (patch_path, len(patch), source_path, target_path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
