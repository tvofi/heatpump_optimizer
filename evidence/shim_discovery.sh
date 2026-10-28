#!/bin/bash
# The spike shim's real-git discovery ("the first git on PATH outside its own
# directory", note §3) under four PATH spellings. Each case runs `git --version`
# under a 5 s timeout; rc 124 is an endless exec loop (the shim finds itself, or
# two shim copies find each other).
# Usage: shim_discovery.sh <path to R10-ORCH-BEATD.spike/shims/git>
SHIM=${1:?shim path}
W=$(mktemp -d); mkdir -p "$W/a/tools/audit/seat/shims" "$W/b"
cp "$SHIM" "$W/a/tools/audit/seat/shims/git"; cp "$SHIM" "$W/b/git"; cd "$W/a"
run() { PATH="$2:$PATH" timeout 5 git --version >/dev/null 2>&1; echo "$1: rc=$?"; }
run "absolute, one copy (the spike's case)"                "$W/a/tools/audit/seat/shims"
run "relative entry (sweep_template.md:51's wording)"     "tools/audit/seat/shims"
run "two shim copies (beatd's + roster_queue.py:95-97's)" "$W/a/tools/audit/seat/shims:$W/b"
run "trailing slash"                                       "$W/a/tools/audit/seat/shims/"
rm -rf "$W"
