#!/bin/bash
# reviewer-built: stamp_paths over a heading + 2 MB filler, N calls, under pipefail
set -uo pipefail
. "$1"; N=$2
FILL=$(head -c 2000000 /dev/zero | tr '\0' 'x' | fold -w 100)
NOTES=$(printf '+## v9.9.9\n%s' "$FILL"); MAN=$(printf '+  "version": "9.9.9",\n%s' "$FILL")
mn=0; mm=0; nn=0
for i in $(seq 1 $N); do
  case "$(stamp_paths "" "" "$NOTES")" in *'RELEASE_NOTES.md(heading)'*) ;; *) mn=$((mn+1));; esac
  case "$(stamp_paths "" "$MAN" "")" in *'manifest.json(version)'*) ;; *) mm=$((mm+1));; esac
done
g=$(stamp_paths "" "$FILL" "$FILL"); [ -z "$g" ] || nn=1
echo "RESULT sigpipe impl=$(basename $1) calls=$N notes_missed=$mn manifest_missed=$mm nullctl_fired=$nn"
