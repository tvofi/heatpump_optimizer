#!/usr/bin/env bash
# Reviewer's driver (the reviewer's own, not the finder's or the fixer's): head's tick_loop.sh in scratch
# copies that are no checkout. variants: asis | nopf (the `set +o pipefail` line deleted) | asis+pin | nopf+pin
# (+pin plants one row: an early match followed by 2 MB, prepr.sh's own deterministic form of the class).
set -u
wt=$1; D=$2; shift 2
mk() { # <variant>
  local v=$1 m=$D/$1; [ -d "$m" ] && return; mkdir -p "$m/tools/audit/seat" "$m/tests"
  for f in tools/audit/seat/tick_loop.sh tools/audit/seat/heartbeat.sh tools/audit/seat/ref_privacy.py tests/throwaway_git.sh; do cp "$wt/$f" "$m/$f"; done
  python3 - "$m/tools/audit/seat/tick_loop.sh" "$v" <<'PY'
import sys
p, v = sys.argv[1:]; s = open(p).read().split("\n")
if v.startswith("nopf"):
    i = [k for k, l in enumerate(s) if l.strip() == "set +o pipefail"]; assert len(i) == 1, i; s.pop(i[0])
if v.endswith("+pin"):
    i = [k for k, l in enumerate(s) if l.lstrip().startswith("ck() {")]; assert len(i) == 1, i
    s.insert(i[0] + 1, """  big=$(head -c 2000000 /dev/zero | tr '\\0' 'x' | fold -w 100); printf 'MATCH\\n%s\\n' "$big" | grep -q '^MATCH$'; ck "REVIEWER PIN: an early match followed by 2 MB is read as a match" $?; unset big""")
open(p, "w").write("\n".join(s))
PY
}
mkdir -p "$D/plain/bin"; printf '#!/bin/sh\nexit 0\n' > "$D/plain/bin/gh"; chmod +x "$D/plain/bin/gh"
v=$1; tag=$2; mk "$v"
s0=$SECONDS
env -u HPO_TICK_CODE_DIR -u HPO_TICK_HEARTBEAT -u GIT_CEILING_DIRECTORIES HPO_STATE_DIR="$D/plain" ${NESTED:+HPO_TICK_SELFTEST_NESTED=1} \
  bash "$D/$v/tools/audit/seat/tick_loop.sh" --self-test > "$D/$v.$tag.log" 2>&1; rc=$?
echo "RESULT $v $tag: $(tail -n 1 "$D/$v.$tag.log") rc=$rc $((SECONDS - s0))s load=$(cut -d' ' -f1 /proc/loadavg)"; sed -n 's/^  FAIL /    FAIL /p; s/^    nested FAIL/      nested FAIL/p' "$D/$v.$tag.log"
