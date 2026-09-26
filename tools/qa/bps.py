#!/usr/bin/env python3
"""Apply a BPS patch: bps.py SOURCE.gba PATCH.bps OUT.gba (uses the decoder in
tools/make_bps_patch.py, which checks the patch's CRCs)."""

import os
import sys

sys.dont_write_bytecode = True   # tools/__pycache__ is tracked; leave it alone
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from make_bps_patch import apply_patch  # noqa: E402

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    with open(sys.argv[1], 'rb') as f:
        src = f.read()
    with open(sys.argv[2], 'rb') as f:
        patch = f.read()
    with open(sys.argv[3], 'wb') as f:
        f.write(apply_patch(src, patch))
