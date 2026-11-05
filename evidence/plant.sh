#!/bin/bash
# Reviewer's own harness: planted receipts against app_push.sh's production reuse_verdict.
SRC=${1:?app_push.sh}; set -u
eval "$(sed -n '/^reuse_verdict() {/,/^}/p' "$SRC")"
export GIT_AUTHOR_NAME=r GIT_AUTHOR_EMAIL=r@x GIT_COMMITTER_NAME=r GIT_COMMITTER_EMAIL=r@x GIT_CONFIG_GLOBAL=/dev/null
U=$(mktemp -d); g() { git -C "$U/wt" "$@" >/dev/null 2>&1; }
git init -q --bare -b main "$U/o.git"; git clone -q "$U/o.git" "$U/wt" 2>/dev/null
cd "$U/wt"; echo a > a; g add a; g commit -qm base; g push -q origin HEAD:main
g checkout -q -b fix/t; echo code > c; g add c; g commit -qm code; C=$(git rev-parse HEAD); CT=$(git rev-parse HEAD^{tree})
g checkout -q -b sib main; echo other > s; g add s; g commit -qm sibling; S=$(git rev-parse HEAD); ST=$(git rev-parse HEAD^{tree})
g checkout -q main; echo m > m; g add m; g commit -qm main2; g push -q origin main
g checkout -q fix/t; g merge -q --no-edit origin/main
body() { local m; m=$(printf 'body: t\n\nCode: %s' "$C"); for l in "$@"; do m=$(printf '%s\n%s' "$m" "$l"); done
  g push -q -f origin "$(git commit-tree "$(git mktree </dev/null)" -m "$m"):refs/heads/handoff-body/t"; }
v() { local name=$1 want=$2 out rc; out=$(reuse_verdict "$U/wt" "[]" fix/t); rc=$?; local got=$([ $rc = 0 ] && echo REUSE || echo FULL)
  printf '%s %-28s want=%-5s got=%-5s | %s\n' "$([ $got = $want ] && echo PASS || echo FAIL)" "$name" "$want" "$got" "$out"; }
body "Prepr: $C $CT";              v "null: genuine receipt" REUSE
body "Prepr: $S $ST";              v "R1 sibling head named" FULL
body "Prepr: $C $(git rev-parse HEAD^{tree})"; v "R4 forged tree (HEAD's)" FULL
body "Prepr: $C $CT" "Prepr: $C $CT"; v "R7 two trailers" FULL
# R2: head moved after the receipt (new code on top, then main merged)
body "Prepr: $C $CT"; echo more > c2; g add c2; g commit -qm moved; v "R2 head moved after receipt" FULL; g reset -q --hard HEAD~1
# R5: evil merge -- extra content inside the merge commit itself
M=$(git rev-parse HEAD); echo evil > e; g add e; g commit -q --amend --no-edit; v "R5 evil merge" FULL; g reset -q --hard "$M"
# R3: receipt from a different base -- code rebased onto new main as C'; receipt still names old C
g checkout -q -B fix/t origin/main; echo code > c; g add c; g commit -qm code-rebased; v "R3 rebased, old-base receipt" FULL
# R6: HEAD holds a main commit that is not on main's first-parent chain
g checkout -q -B fix/t "$C"; g checkout -q -b side main~1 2>/dev/null; g checkout -q -b side2 origin/main~1; echo sd > sd; g add sd; g commit -qm side; SD=$(git rev-parse HEAD)
g checkout -q main; g reset -q --hard origin/main; g merge -q --no-ff --no-edit side2; g push -q origin main
g checkout -q fix/t; g merge -q --no-edit "$SD"; v "R6 off-first-parent main" FULL
# R8: a hand-written trailer with the right sha and tree but no prepr run at all
g checkout -q -B fix/t "$C"; g merge -q --no-edit origin/main; body "Prepr: $C $CT"; v "R8 unbacked hand trailer" REUSE
rm -rf "$U"
