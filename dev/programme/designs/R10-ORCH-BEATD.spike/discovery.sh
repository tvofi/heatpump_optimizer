#!/bin/bash
# The shim's real-git discovery under the PATH spellings of design-verdict 1d5cdad0f
# (evidence/shim_discovery.sh), plus a poisoned HPO_REAL_GIT and no real git.
# Each case runs `git --version` under a 5 s bound; rc 124 would be an exec loop.
# Usage: discovery.sh [shim]   (default: shims/git beside this file). Runs under bash 3.2.
set -u
SHIM=${1:-$(cd "$(dirname "$0")/beatd_shims" && pwd)/git}
W=$(mktemp -d); mkdir -p "$W/a/tools/audit/seat/beatd_shims" "$W/b" "$W/empty"
cp "$SHIM" "$W/a/tools/audit/seat/beatd_shims/git"; cp "$SHIM" "$W/b/git"; cd "$W/a"
bound() { "$@" & p=$!; ( /bin/sleep 5; kill -9 $p 2>/dev/null ) & k=$!; wait $p; r=$?; kill $k 2>/dev/null; wait $k 2>/dev/null; [ $r = 137 ] && r=124; return $r; }
run() { out=$(PATH="$2" HPO_REAL_GIT="${3:-}" bound git --version 2>&1); echo "$1: rc=$? ${out%%$'\n'*}"; }
S=$W/a/tools/audit/seat/beatd_shims; B=/usr/bin:/bin
run "absolute, one copy"           "$S:$B"
run "relative entry"               "tools/audit/seat/beatd_shims:$B"
run "trailing slash"               "$S/:$B"
run "two shim copies"              "$S:$W/b:$B"
run "duplicate entry"              "$S:$S:$B"
run "HPO_REAL_GIT is a shim copy"  "$S:$B" "$W/b/git"
run "no real git on PATH"          "$S:$W/b:$W/empty"
cd /; rm -rf "$W"
