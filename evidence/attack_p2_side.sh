#!/bin/bash
# Reviewer's own harness (review-2069): drives the PRODUCTION recarry_verdict,
# extracted from tools/pr/app_push.sh at the reviewed head, against real git.
set -u
SELF=${1:?app_push.sh}
R=$(mktemp -d "${TMPDIR:-/tmp}/rv2069.XXXXXX")
rgit() { GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git -c user.name=t -c user.email=t@example.test -c init.defaultBranch=main "$@" >/dev/null 2>&1; }
eval "$(sed -n '/^recarry_verdict() {/,/^}/p' "$SELF")"
printf 'b\n' > "$R/body.md"
listing() { python3 -c 'import json,sys; print(json.dumps([{"number":7,"head":{"sha":sys.argv[1]},"body":"b"}]))' "$1"; }
rv() { GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 recarry_verdict "$R/wt" "$(listing "$1")" "$R/body.md"; }
rgit init -q --bare "$R/origin.git"; rgit clone -q "$R/origin.git" "$R/wt"
cd "$R/wt"
printf 'x\n' > x; rgit add x; rgit commit -qm base; rgit push -q origin HEAD:main
# The PR under recarry: fix branch off base.
rgit checkout -q -b fix; printf 'f\n' > f; rgit add f; rgit commit -qm fix; rgit push -q origin fix
LIVE=$(git rev-parse HEAD)
# Another PR, merged into main with a merge commit (as the repo does): its
# intermediate commit EVIL adds evil.py, which its later commit removes.
rgit checkout -q -b other main; printf 'rm -rf\n' > evil.py; rgit add evil.py; rgit commit -qm evil
EVIL=$(git rev-parse HEAD)
rgit rm -q evil.py; printf 'o\n' > o; rgit add o; rgit commit -qm "other: final"
rgit checkout -q main; rgit merge -q --no-ff --no-edit other; rgit push -q origin main
echo "main's tree has evil.py: $(git ls-tree --name-only origin/main | grep -c evil.py)"
echo "EVIL on main's first-parent chain: $(git rev-list --first-parent origin/main | grep -c "$EVIL")"
echo "EVIL ancestor of origin/main: $(git merge-base --is-ancestor "$EVIL" origin/main && echo yes || echo no)"
# The attack: merge EVIL (not main) into the live head.
rgit checkout -q fix; rgit merge -q --no-edit "$EVIL"
echo "attack HEAD tree has evil.py: $(git ls-tree --name-only HEAD | grep -c evil.py)"
out=$(rv "$LIVE"); rc=$?
echo "RESULT attack=p2-side-branch rc=$rc verdict=$out"
# Null control: the honest recarry (merge origin/main) on the same live head.
rgit reset -q --hard "$LIVE"; rgit merge -q --no-edit origin/main
out=$(rv "$LIVE"); rc=$?
echo "RESULT control=honest-main-merge rc=$rc verdict=$out"
# Attack 2: parent 1 spoof -- merge main into a commit that is not the live head.
rgit reset -q --hard "$LIVE"; printf 'g\n' > g; rgit add g; rgit commit -qm extra; rgit merge -q --no-edit origin/main
out=$(rv "$LIVE"); rc=$?
echo "RESULT attack=extra-commit-under-p1 rc=$rc verdict=$out"
# Attack 3: octopus / swapped parents.
rgit reset -q --hard origin/main; rgit merge -q --no-edit "$LIVE"
out=$(rv "$LIVE"); rc=$?
echo "RESULT attack=swapped-parents rc=$rc verdict=$out"
# Attack 4: -s ours evil merge whose tree != merge-tree.
rgit reset -q --hard "$LIVE"; rgit merge -q -s ours --no-edit origin/main
out=$(rv "$LIVE"); rc=$?
echo "RESULT attack=strategy-ours rc=$rc verdict=$out"
# Attack 5: whitespace-only body change (trailing spaces).
rgit reset -q --hard "$LIVE"; rgit merge -q --no-edit origin/main
printf 'b \n' > "$R/body.md"; out=$(rv "$LIVE"); rc=$?
echo "RESULT attack=body-trailing-space rc=$rc verdict=$out"
printf '\nb\n' > "$R/body.md"; out=$(rv "$LIVE"); rc=$?
echo "RESULT attack=body-leading-newline rc=$rc verdict=$out"
printf 'b\r\n' > "$R/body.md"; out=$(rv "$LIVE"); rc=$?
echo "RESULT attack=body-crlf rc=$rc verdict=$out"
printf 'b\n' > "$R/body.md"
# Attack 6: API failure -- empty / malformed listing.
out=$(GIT_CONFIG_GLOBAL=/dev/null recarry_verdict "$R/wt" "" "$R/body.md"); echo "RESULT attack=listing-empty rc=$? verdict=$out"
out=$(GIT_CONFIG_GLOBAL=/dev/null recarry_verdict "$R/wt" "[]" "$R/body.md"); echo "RESULT attack=listing-none rc=$? verdict=$out"
out=$(GIT_CONFIG_GLOBAL=/dev/null recarry_verdict "$R/wt" '{"message":"API rate limit"}' "$R/body.md"); echo "RESULT attack=listing-error-json rc=$? verdict=$out"
out=$(GIT_CONFIG_GLOBAL=/dev/null recarry_verdict "$R/wt" "$(python3 -c 'import json,sys; print(json.dumps([{"head":{"sha":sys.argv[1]}}]))' "$LIVE")" "$R/body.md"); echo "RESULT attack=listing-no-body-key rc=$? verdict=$out"
# Attack 7: origin fetch fails (remote gone).
rgit remote set-url origin /nonexistent; out=$(rv "$LIVE"); echo "RESULT attack=fetch-fails rc=$? verdict=$out"
rm -rf "$R"
