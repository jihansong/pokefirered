#!/bin/sh
# Build the headless emulator wrapper used by tools/qa/*.py (needs libmgba-dev).
set -e
cd "$(dirname "$0")"
cc -O2 -shared -fPIC -o libqa.so libqa.c -lmgba
