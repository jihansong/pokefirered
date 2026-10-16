#!/usr/bin/env python3
"""Encode reviewed native Rocket96 PNG in its four-OAM tile order; never resize."""
from pathlib import Path
import argparse, hashlib, io, os, struct, tempfile
from PIL import Image
SOURCE_SHA = "210bd8b8c196cb83ce25fb35bc8affc0869743bd4a760b4be9fc90047a9ea438"
EXPECTED = {
    "tiles": "99f3ff74b5438521ba48e4d7fc403acca7df233f003878ddd525bdba8ab14add",
    "palette": "02951ab3bc6bd04dbce501258a13e92e3ba934728bb8249514b41238f835b792",
}
PIECES = [(0,0,64,64,0),(64,0,32,64,64),(0,64,64,32,96),(64,64,32,32,128)]
def encode(source):
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA:
        raise ValueError("Rocket96 source changed; review artwork and update pinned hashes together")
    im = Image.open(io.BytesIO(source))
    if im.mode != "P" or im.size != (96,96) or im.info.get("transparency") != 0:
        raise ValueError("Native 96x96 indexed PNG with transparent index zero required")
    pixels = list(im.get_flattened_data() if hasattr(im,"get_flattened_data") else im.getdata())
    if any(index < 0 or index > 15 for index in pixels):
        raise ValueError("More than 16 palette indices")
    pal = im.getpalette()
    if not pal or len(pal) < 48:
        raise ValueError("16 palette entries required")
    packed = bytearray()
    restored = [None] * 9216
    for x,y,w,h,offset in PIECES:
        if len(packed) != offset * 32:
            raise ValueError("OAM tile offset mismatch")
        for ty in range(y,y+h,8):
            for tx in range(x,x+w,8):
                for row in range(8):
                    for col in range(0,8,2):
                        pos = (ty+row)*96+tx+col
                        value = pixels[pos] | (pixels[pos+1] << 4)
                        packed.append(value)
                        restored[pos:pos+2] = [value & 15, value >> 4]
    if restored != pixels or len(packed) != 4608:
        raise ValueError("Native pixel roundtrip failed")
    palette = b"".join(struct.pack("<H", (pal[i]>>3)|((pal[i+1]>>3)<<5)|((pal[i+2]>>3)<<10)) for i in range(0,48,3))
    result = {"tiles": bytes(packed), "palette": palette}
    for kind,blob in result.items():
        if hashlib.sha256(blob).hexdigest() != EXPECTED[kind]:
            raise ValueError(kind + " differs from reviewed encoded output")
    return result
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("--kind", choices=EXPECTED, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    suffix = ".4bpp" if args.kind == "tiles" else ".gbapal"
    if args.output.suffix != suffix or args.source.resolve() == args.output.resolve():
        raise ValueError("Invalid generated output path")
    before = args.source.read_bytes()
    blob = encode(before)[args.kind]
    if args.source.read_bytes() != before:
        raise RuntimeError("Source changed during encoding")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=args.output.parent, prefix=".rocket96-", delete=False) as f:
        temp = Path(f.name)
        f.write(blob)
    os.replace(temp,args.output)
    print(args.output, len(blob), hashlib.sha256(blob).hexdigest())
if __name__ == "__main__":
    main()
