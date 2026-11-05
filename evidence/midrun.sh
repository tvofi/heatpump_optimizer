#!/bin/bash
# Reviewer's harness: does prepr.sh's receipt name the HEAD the run measured, when HEAD moves mid-run?
SRC=${1:?prepr.sh}
eval "$(sed -n '/^receipt_file() {/,/^}/p;/^receipt_skips() {/,/^}/p;/^receipt_write() {/,/^}/p' "$SRC")"
say() { echo "$1 $2: $3"; }
export GIT_AUTHOR_NAME=r GIT_AUTHOR_EMAIL=r@x GIT_COMMITTER_NAME=r GIT_COMMITTER_EMAIL=r@x GIT_CONFIG_GLOBAL=/dev/null
U=$(mktemp -d); cd "$U"; git init -q -b main; echo a > a; git add a; git commit -qm base
H0=$(git rev-parse HEAD)                                   # the HEAD a run starts measuring
echo 'unmeasured code' > b; git add b; git commit -qm 'committed while prepr ran'   # HEAD moves mid-run, tree clean
receipt_write 0 body.md                                    # the main flow's last step, as called: rc and body only
read -r s t < "$(receipt_file)"
echo "measured=$H0 receipt=$s"; [ "$s" = "$H0" ] && echo "RESULT: receipt names the measured HEAD" || echo "RESULT: receipt names a HEAD the run did not start on"
rm -rf "$U"
