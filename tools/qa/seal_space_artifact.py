#!/usr/bin/env python3
"""Encrypt a runner-only build bundle for its local reviewer, never publish a raw ROM."""
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import zipfile

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SCHEMA = 'TY_SPACE_SEALED_BUILD_V1'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--public-key', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.input.is_dir() and not args.input.is_symlink()
    root = args.input.resolve()
    assert not args.output.exists() and not args.output.is_symlink()
    assert not args.output.resolve().is_relative_to(root)
    public_bytes = args.public_key.read_bytes()
    public_key = serialization.load_pem_public_key(public_bytes)
    assert isinstance(public_key, rsa.RSAPublicKey) and public_key.key_size >= 3072
    entries = sorted(root.rglob('*'))
    files = []
    total = 0
    for path in entries:
        assert not path.is_symlink(), 'No symlinks in a build bundle'
        if path.is_dir():
            continue
        assert path.is_file()
        name = path.relative_to(root).as_posix()
        assert path.resolve().is_relative_to(root)
        assert path.suffix.lower() not in {'.sav', '.srm', '.pem', '.key', '.p12'}
        size = path.stat().st_size
        assert size < 256_000_000
        total += size
        assert total < 1_000_000_000
        files.append((name, path))
    assert files and (root / 'provenance.json').is_file()
    # Only a freshly assembled build/evidence directory is accepted by the caller.
    # Existing user files and credential directories are never build inputs.
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, path in files:
            archive.write(path, name)
    plain = data.getvalue()
    key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    header = {
        'schema': SCHEMA,
        'public_key_sha256': hashlib.sha256(public_bytes).hexdigest(),
        'plaintext_sha256': hashlib.sha256(plain).hexdigest(),
        'plaintext_bytes': len(plain),
        'files': len(files),
        'nonce': base64.b64encode(nonce).decode('ascii'),
        'wrapped_key': base64.b64encode(public_key.encrypt(key, padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=SCHEMA.encode()))).decode('ascii'),
    }
    aad = json.dumps(header, sort_keys=True, separators=(',', ':')).encode('ascii')
    encrypted = AESGCM(key).encrypt(nonce, plain, aad)
    with args.output.open('xb') as stream:
        stream.write(b'TYSPACE1\n')
        stream.write(len(aad).to_bytes(4, 'big'))
        stream.write(aad)
        stream.write(encrypted)
    print(json.dumps({'status': 'SEALED_BUILD_ONLY', 'files': len(files),
                      'ciphertext_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      'ciphertext_bytes': args.output.stat().st_size,
                      'public_key_sha256': header['public_key_sha256']}))


if __name__ == '__main__':
    main()
