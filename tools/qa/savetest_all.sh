#!/bin/sh
# The save compatibility check the plans call savetest_all.sh: build any
# missing reference ROMs, then compare every save in saves/ (tools/qa/savetest.py).
set -e
cd "$(dirname "$0")"
./refroms.sh >/dev/null
exec python3 savetest.py "$@"
