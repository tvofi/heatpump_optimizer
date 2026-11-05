#!/bin/bash
# Reviewer's own planted receipts against the PRODUCTION reuse_verdict, extracted
# from tools/pr/app_push.sh of the checkout given as $1. Prints one RESULT per row.
SRC=${1:?checkout}; set -u; BASH_ARGV0="$SRC/tools/pr/app_push.sh"  # reuse_verdict sources delivery_row.sh beside $0
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_NAME=r GIT_AUTHOR_EMAIL=r@x GIT_COMMITTER_NAME=r GIT_COMMITTER_EMAIL=r@x
eval "$(sed -n '/^reuse_verdict() {/,/^}/p' "$SRC/tools/pr/app_push.sh")"
. "$SRC/tools/audit/seat/delivery_row.sh"
T=$(mktemp -d); g() { git -C "$T/wt" "$@" >/dev/null 2>&1; }
git init -q --bare -b main "$T/o.git"; git clone -q "$T/o.git" "$T/wt" 2>/dev/null
cd "$T/wt"; printf 'a\n' > a; g add a; g commit -qm base; g tag B; g push -q origin HEAD:main
g checkout -q -b fix/t; printf 'code\n' > c; g add c; g commit -qm code; g tag C
g checkout -q main; printf 'm\n' > m; g add m; g commit -qm main2; g push -q origin main; g checkout -q fix/t
C=$(git rev-parse C); CT=$(git rev-parse 'C^{tree}')
body() { local m; m=$(printf 'body: t\n\nCode: %s\n%s' "$C" "$1"); g push -q -f origin "$(git commit-tree "$(git mktree </dev/null)" -m "$m"):refs/heads/handoff-body/t"; }
row() { # label expect(0 reuse|1 refuse) listing
  local why rc; why=$(reuse_verdict "$T/wt" "${3:-[]}" fix/t 2>&1); rc=$?
  if [ "$rc" = "$2" ]; then r=PASS; else r=FAIL; fi
  echo "RESULT: $r $1 rc=$rc want=$2 :: $why"
}
reset_head() { g checkout -q fix/t; g reset -q --hard C; g merge -q --no-edit origin/main; }
reset_head; body "Prepr: $C $CT"
row "NULL valid receipt, HEAD = clean merge of C and main" 0
# F1: trailer naming another head: a sibling code commit D with its own (correct) tree, D not in HEAD
g checkout -q -b other B; printf 'other\n' > o; g add o; g commit -qm other; D=$(git rev-parse HEAD); DT=$(git rev-parse 'HEAD^{tree}'); reset_head
body "Prepr: $D $DT"; row "F1 receipt names another head D (tree correct for D, D not in HEAD)" 1
# F1b: trailer names HEAD's sha but the tree of C
body "Prepr: $(git rev-parse HEAD) $CT"; row "F1b receipt sha = HEAD but tree = C's" 1
# F2: head moved after the receipt: one more code commit on top of the receipted code
body "Prepr: $C $CT"; printf 'late\n' > late; g add late; g commit -qm late-code
row "F2 HEAD moved after the receipt (extra code commit past C+main)" 1
# F2b: moved head where the new code commit sits BELOW the merge (C -> N -> merge main)
g reset -q --hard C; printf 'n\n' > n; g add n; g commit -qm N; g merge -q --no-edit origin/main
row "F2b HEAD = (C + new code N) merged with main" 1
# F3: receipt from a different base: same patch re-cut on main's tip (C2), receipt still names C on old base
g checkout -q -B fix/t origin/main; printf 'code\n' > c; g add c; g commit -qm code-recut
row "F3 receipt from a different base (C on B; HEAD is the patch re-cut on main, C not in HEAD)" 1
# F3b: receipt names the old-base commit C, HEAD is C rebased, receipt tree forged to HEAD's tree
body "Prepr: $C $(git rev-parse 'HEAD^{tree}')"; row "F3b old-base sha with the new head's tree" 1
# F4: evil merge -- C merged with main cleanly, but the merge commit itself edits a file
body "Prepr: $C $CT"; reset_head; g reset -q --soft HEAD~0; printf 'evil\n' >> a; g add a; g commit -q --amend --no-edit
row "F4 evil merge: clean-merging parents, merge commit edits a (tree != clean merge)" 1
# F5: malformed trailer: extra field / short sha / uppercase
reset_head
body "Prepr: $C $CT extra"; row "F5a trailer with a third field" 1
body "Prepr: ${C:0:39} $CT"; row "F5b 39-hex sha" 1
body "Prepr: $(echo "$C" | tr a-f A-F) $CT"; row "F5c upper-case sha" 1
# F6: receipt only on an older handoff-body commit; tip has none
P=$(git commit-tree "$(git mktree </dev/null)" -m "$(printf 'body: t\n\nCode: %s\nPrepr: %s %s' "$C" "$C" "$CT")")
g push -q -f origin "$(git commit-tree "$(git mktree </dev/null)" -p "$P" -m "body: t"):refs/heads/handoff-body/t"
row "F6 receipt on the parent of handoff-body's tip, tip carries none" 1
# F7: live head (open PR) whose own extra commit is outside the merge HEAD made
body "Prepr: $C $CT"; reset_head; L=$(git rev-parse HEAD)
row "NULL2 update: HEAD = live head L (C+main)" 0 "[{\"number\": 9, \"title\": \"t\", \"head\": {\"sha\": \"$L\"}}]"
mkdir -p "$ROW_DIR"; printf 'r\n' > "$ROW_DIR/9.md"; printf 'x\n' > x; g add -A; g commit -qm "row plus extra"
row "F7 row commit that also adds another file" 1 "[{\"number\": 9, \"title\": \"t\", \"head\": {\"sha\": \"$L\"}}]"
g reset -q --hard HEAD~1; mkdir -p "$ROW_DIR"; printf "r\n" > "$ROW_DIR/8.md"; g add -A; g commit -qm "another PR's row"
row "F8 row commit for another PR's row (8.md, listing #9)" 1 "[{\"number\": 9, \"title\": \"t\", \"head\": {\"sha\": \"$L\"}}]"
# F9 (condition (e) alone): HEAD = clean merge of C and main, then two extra commits
# that net to no tree change -- the tree equals the clean merge, so (d) passes; only (e) refuses.
body "Prepr: $C $CT"; reset_head; printf 'x\n' > tmpx; g add tmpx; g commit -qm "unchecked subject one"; g rm -q tmpx; g commit -qm "unchecked subject two"
row "F9 two tree-neutral commits past C+main (only (e) can see them)" 1
rm -rf "$T"
