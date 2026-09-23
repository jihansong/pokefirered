#!/bin/sh
# Build the release ROMs the save tests compare against, one per tag, into
# qa-base/<tag>/ (gitignored, inside the workspace so it survives a container
# rebuild). A tag that is already built is skipped. Each build is checked
# against the GitHub release's pokemonthyl.bps when gh is logged in.
#
#   tools/qa/refroms.sh                 # the tags savetest.py needs
#   tools/qa/refroms.sh v0.6.0 v0.8.0   # or any tags
set -e
REPO=$(cd "$(dirname "$0")/../.." && pwd)
BASE="$REPO/qa-base"
TAGS=${*:-"v0.1.0 v0.2.1 v0.3.0 v0.5.1 v0.7.0"}
JOBS=$(nproc)
mkdir -p "$BASE"
cd "$REPO"
for tag in $TAGS; do
    out="$BASE/$tag"
    if [ -f "$out/pokemonthyl.gba" ] && [ -f "$out/pokemonthyl.sym" ]; then
        echo "$tag: already built"
        continue
    fi
    src="$BASE/.src-$tag"
    rm -rf "$src"
    git worktree prune
    git worktree add --detach "$src" "$tag" >/dev/null
    ln -sfn "$REPO/tools/agbcc" "$src/tools/agbcc"
    echo "$tag: building"
    make -C "$src" leafgreen -j"$JOBS" >"$BASE/$tag.log" 2>&1
    make -C "$src" GAME_VERSION=LEAFGREEN syms >>"$BASE/$tag.log" 2>&1
    mkdir -p "$out"
    cp "$src/pokemonthyl.gba" "$src/pokemonthyl.sym" "$out/"
    git worktree remove --force "$src"
    if command -v gh >/dev/null && gh auth status >/dev/null 2>&1 && [ -f "$REPO/baserom_leafgreen.gba" ]; then
        tmp=$(mktemp -d)
        if gh release download "$tag" -p pokemonthyl.bps -D "$tmp" >/dev/null 2>&1; then
            python3 "$REPO/tools/qa/bps.py" "$REPO/baserom_leafgreen.gba" "$tmp/pokemonthyl.bps" "$tmp/rel.gba"
            if cmp -s "$tmp/rel.gba" "$out/pokemonthyl.gba"; then
                echo "$tag: matches the release patch"
            else
                echo "$tag: WARNING build differs from the release patch; using the release ROM"
                cp "$tmp/rel.gba" "$out/pokemonthyl.gba"
            fi
        fi
        rm -rf "$tmp"
    fi
done
