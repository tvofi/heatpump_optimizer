#!/bin/bash
# Minimal repro of the self-test's line-119 trap plus line-217 ZPID loop.
W=$(mktemp -d); mkdir -p "$W/bin"; : > "$W/bin/stub"; LOG=$(mktemp)
trap 'echo "trap ran in pid $BASHPID (main $$)" >> '"$LOG"'; [ -n "${ZPID:-}" ] && kill "$ZPID" 2>/dev/null; rm -rf "$W"' EXIT
n=0; while :; do sleep 600 & ZPID=$!; n=$((n+1)); case $ZPID in *0*) break ;; esac; kill "$ZPID" 2>/dev/null; done
sleep 0.5
echo "iterations=$n subshell-trap-runs=$(grep -vc "pid $$ " "$LOG") fixture-present=$([ -e "$W/bin/stub" ] && echo yes || echo NO)"
kill "$ZPID" 2>/dev/null; trap - EXIT; rm -rf "$W" "$LOG"
