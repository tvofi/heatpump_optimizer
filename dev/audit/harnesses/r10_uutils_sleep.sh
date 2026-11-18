#!/usr/bin/env bash
# r10-hotfix-uutils-sleep: pr_args.sh's self-test on a host whose sleep is a
# uutils-style multicall binary (ubuntu-26.04's /bin/sleep), which refuses to
# run when argv[0]'s basename is not `sleep`. Linux only: a private mount
# namespace binds an emulating script over /usr/bin/sleep (and so /bin/sleep);
# macOS has no uutils and no namespace, so no cheaper host reproduces it.
#
#   bash dev/audit/harnesses/r10_uutils_sleep.sh <rev> [emu|gnu] [symlink]
#
# Runs `pr_args.sh --self-test` in a fresh detached worktree at <rev>, under the
# emulation (emu, the default) or the host's own sleep (gnu, the null control).
# `symlink` first restores the bystander fixture's renamed link to /bin/sleep
# (the mutant). Prints the self-test's tally line and rc=<its exit status>.
set -uo pipefail
rev=${1:?usage: r10_uutils_sleep.sh <rev> [emu|gnu] [symlink]}; mode=${2:-emu}; mut=${3:-}
top=$(git rev-parse --show-toplevel) || exit 2
d=$(mktemp -d); wt=$d/wt
trap 'git -C "$top" worktree remove --force "$wt" 2>/dev/null; rm -rf "$d"' EXIT
git -C "$top" worktree add -q --detach "$wt" "$rev" || exit 2
if [ "$mut" = symlink ]; then
  python3 - "$wt/tools/audit/seat/pr_args.sh" <<'PY' || exit 2
import sys
p = sys.argv[1]; s = open(p).read()
old = """  printf '#!/bin/sh\\nexec sleep "$1"\\n' > "$REAP_DIR/unrelated-sleep"; chmod +x "$REAP_DIR/unrelated-sleep"\n"""
if s.count(old) != 1:
    sys.exit("mutant anchor not found exactly once")
open(p, "w").write(s.replace(old, '  ln -s /bin/sleep "$REAP_DIR/unrelated-sleep"\n'))
PY
fi
mkdir "$d/real"; cp "$(readlink -f /usr/bin/sleep)" "$d/real/sleep"  # basename kept: a multicall host sleep runs too
printf '%s\n' '#!/bin/sh' \
  "case \${0##*/} in sleep) exec $d/real/sleep \"\$@\" ;; esac" \
  "printf 'Security violation: Requested utility \`%s\` does not match executable name \`sleep\`\\n' \"\${0##*/}\" >&2; exit 1" > "$d/sleep"
chmod +x "$d/sleep"
run='cd "$0" && bash tools/audit/seat/pr_args.sh --self-test > "$1/out" 2>&1; echo "rc=$?" >> "$1/out"'
if [ "$mode" = emu ]; then
  ns=(unshare -m); [ "$(id -u)" = 0 ] || ns=(unshare -rm)
  "${ns[@]}" bash -c "mount --bind '$d/sleep' /usr/bin/sleep && $run" "$wt" "$d" || exit 2
else
  bash -c "$run" "$wt" "$d"
fi
grep -E '^ *FAIL|^pr_args self-test:|^rc=' "$d/out"
