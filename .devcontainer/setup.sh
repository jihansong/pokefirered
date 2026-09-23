#!/bin/bash
# Everything the container needs beyond the devkitARM image, so a rebuilt
# container comes back with the same tools. Run by postCreateCommand; safe to
# run again by hand (each step skips what is already there).
#
#   bash .devcontainer/setup.sh
#
# What lives where:
#   apt packages                system (lost on rebuild, reinstalled here)
#   tools/agbcc                 built from pret/agbcc at AGBCC_REV
#   /root/src/pokeemerald       pret/pokeemerald at EMERALD_REV (Hoenn import
#                               scripts and tools/qa/textaudit.py read it)
#   tools/qa/libqa.so           the headless emulator wrapper (libmgba)
#   qa-base/, saves/            in the workspace, so they survive a rebuild;
#                               qa-base is rebuilt by tools/qa/refroms.sh
set -euo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
AGBCC_REV=da598c1d918402c42c0c0d7128ba14567f3175e9      # pret/agbcc, 2026-01-20
EMERALD_REV=5eff78649                                   # pret/pokeemerald, the Hoenn import base
SUDO=""
[ "$(id -u)" -eq 0 ] || SUDO=sudo

echo "== apt packages"
PKGS=(
    build-essential libpng-dev git-lfs        # the build, and the repo's LFS push hook
    gh                                        # releases
    python3 python3-pil python3-numpy python3-docx   # tools/*.py, tools/qa, walkthrough .docx
    libmgba-dev                               # mGBA core for tools/qa (headless)
    libreoffice-writer-nogui fonts-noto-cjk poppler-utils   # render the .docx to PDF/PNG to check it
)
missing=()
for p in "${PKGS[@]}"; do
    dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p")
done
if [ ${#missing[@]} -gt 0 ]; then
    $SUDO apt-get update -q
    DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y -q --no-install-recommends "${missing[@]}"
fi

# Workspace clones are owned by another uid than the container user.
git config --global --add safe.directory '*'

echo "== agbcc"
if [ ! -x "$REPO/tools/agbcc/bin/agbcc" ]; then
    src=$(dirname "$REPO")/agbcc
    [ -d "$src/.git" ] || git clone -q https://github.com/pret/agbcc "$src"
    git -C "$src" fetch -q origin "$AGBCC_REV"
    git -C "$src" checkout -q "$AGBCC_REV"
    (cd "$src" && ./build.sh && ./install.sh "$REPO")
fi

echo "== pokeemerald $EMERALD_REV"
EM=/root/src/pokeemerald
if [ "$(git -C "$EM" rev-parse --short=9 HEAD 2>/dev/null)" != "$EMERALD_REV" ]; then
    $SUDO mkdir -p "$(dirname "$EM")"
    [ -d "$EM/.git" ] || $SUDO git clone -q https://github.com/pret/pokeemerald "$EM"
    $SUDO git -C "$EM" checkout -q "$EMERALD_REV"
fi

echo "== tools/qa"
"$REPO/tools/qa/build.sh"

echo "== done"
[ -f "$REPO/baserom_leafgreen.gba" ] || echo "note: put your LeafGreen ROM at baserom_leafgreen.gba (see docs/INSTALL.md)"
[ -d "$REPO/qa-base/v0.7.0" ] || echo "note: run tools/qa/refroms.sh once to build the reference ROMs for the save tests"
