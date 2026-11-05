#!/bin/bash
# Reviewer's own plants against the production reuse_verdict at the reviewed head.
# usage: plant.sh <worktree of the head>
set -u
SRC=$1; SELF=$SRC/tools/pr/app_push.sh
eval "$(sed -n '/^reuse_verdict() {/,/^}/p' "$SELF")"
U=$(mktemp -d); export GIT_AUTHOR_NAME=r GIT_AUTHOR_EMAIL=r@x GIT_COMMITTER_NAME=r GIT_COMMITTER_EMAIL=r@x
g() { git -C "$U/wt" "$@" >/dev/null 2>&1; }
git init -q --bare -b main "$U/o.git"; git clone -q "$U/o.git" "$U/wt" 2>/dev/null
cd "$U/wt"; echo a > a; g add a; g commit -qm base; g tag B0; g push -q origin HEAD:main
g checkout -q -b fix/t; echo code > c; g add c; g commit -qm code; g tag C
g checkout -q main; echo m > m; g add m; g commit -qm main2; g push -q origin main
g checkout -q fix/t; g merge -q --no-edit origin/main; g tag GOOD
uc=$(git rev-parse C); ut=$(git rev-parse 'C^{tree}')
body() { g push -q -f origin "$(git commit-tree "$(git mktree </dev/null)" -m "$(printf 'body: t\n\nCode: %s\n%s' "$uc" "$1")"):refs/heads/handoff-body/t"; }
v() { reuse_verdict "$U/wt" "[]" fix/t; echo "rc=$?"; }
res() { printf 'RESULT %-55s %s\n' "$1" "$(v | paste -sd' ' -)"; }
body "Prepr: $uc $ut"; g reset -q --hard GOOD
res "null control: genuine receipt at clean merge"
# P1 trailer naming another head: an unrelated commit X (own tree), HEAD unchanged
g checkout -q -b other B0; echo o > o; g add o; g commit -qm other; X=$(git rev-parse HEAD); g checkout -q fix/t; g reset -q --hard GOOD
body "Prepr: $X $(git rev-parse "$X^{tree}")"; res "P1 trailer names another head (not in HEAD)"
# P1b another head that IS in HEAD: main's commit, own tree matches
M=$(git rev-parse origin/main); body "Prepr: $M $(git rev-parse "$M^{tree}")"; res "P1b trailer names main's tip (in HEAD)"
# P2 head moved after the receipt: one more code commit on top of the receipted code
body "Prepr: $uc $ut"; g reset -q --hard C; echo more >> c; g commit -qam more; g merge -q --no-edit origin/main
res "P2 code commit after receipt, then merge main"
# P2b head moved: amend of C (C not in HEAD)
g reset -q --hard C; echo amend >> c; g commit -q --amend -am code2; g merge -q --no-edit origin/main
res "P2b receipted code amended (C not in HEAD)"
# P3 receipt from a different base: same diff rebased onto new main (C not in HEAD)
g reset -q --hard origin/main; echo code > c; g add c; g commit -qm code-rebased
res "P3 same change rebased on new base (C not in HEAD)"
# P3b different base: HEAD contains C but merged with a main commit that is NOT on main (fork of main)
g checkout -q -b fork origin/main; echo f > fk; g add fk; g commit -qm fork; g checkout -q fix/t; g reset -q --hard C; g merge -q --no-edit fork
res "P3b HEAD merged with a non-main base"
# P4 forged tree: right sha, tree of base
g reset -q --hard GOOD; body "Prepr: $uc $(git rev-parse 'B0^{tree}')"; res "P4 trailer tree forged"
# P5 malformed trailer (short sha)
body "Prepr: ${uc:0:12} $ut"; res "P5 short sha trailer"
# P6 merge with -s ours style evil merge: tree differs from clean merge
body "Prepr: $uc $ut"; g reset -q --hard C; g merge -q --no-edit --no-commit origin/main; echo evil > c; g add c; g commit -qm evilmerge
res "P6 evil merge (resolution edits code)"
g reset -q --hard GOOD; res "null control again: genuine receipt at clean merge"
rm -rf "$U"
