#!/bin/bash
# Minimal repro of the self-test's line-119 trap plus line-217 ZPID loop.
W=$(mktemp -d); mkdir -p "$W/bin"; : > "$W/bin/stub"; LOG=$(mktemp)
trap 'echo "trap ran in pid $BASHPID (main $$)" >> '"$LOG"'; [ -n "${ZPID:-}" ] && kill "$ZPID" 2>/dev/null; rm -rf "$W"' EXIT
n=0; while :; do sh -c 'case $$ in *0*) exec sleep 600 ;; esac' & ZPID=$!; n=$((n+1)); case $ZPID in *0*) break ;; esac; wait "$ZPID"; done
sleep 0.5
echo "zpid-comm=$(cat /proc/$ZPID/comm 2>/dev/null) iterations=$n subshell-trap-runs=$(grep -vc "pid $$ " "$LOG") fixture-present=$([ -e "$W/bin/stub" ] && echo yes || echo NO)"
kill "$ZPID" 2>/dev/null; trap - EXIT; rm -rf "$W" "$LOG"
