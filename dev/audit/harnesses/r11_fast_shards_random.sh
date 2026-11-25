#!/bin/bash
# The fast shards' independence proof (R11-CI-CASE-SELECT P2, #3885), run once.
#
#   bash dev/audit/harnesses/r11_fast_shards_random.sh SEED OUTDIR [N]
#
# Draws a RANDOM assignment of every script run.sh names to N shards (default 3; the
# PRODUCERS groups -- the plan payload's writer and its readers -- drawn as one unit, the one
# dependency the planner keeps), then runs tests/run.sh once per shard, one after another, each
# exactly as CI's fast job runs it (GOLDEN_MODE=drift, RUN_PART=fast, GATE_SCOPE=full, the
# shard's HPO_FAST_SHARD and HPO_FAST_PLAN). Each shard's log lands in OUTDIR.
# EXPECTED RESULT: every shard exits 0 and the union of the scripts the shards ran is every
# script one unsharded run runs (the RAN line), with no script run twice (the TWICE line empty):
# no script depends on another having run in the same job, beyond the group drawn together.
# Null: a draw that splits plan_view.py from card.mjs (SPLIT_PRODUCERS=1) fails card.mjs.
set -u
SEED="$1"; OUT="$2"; N="${3:-3}"
cd "$(dirname "$0")/../../.." || exit 9
mkdir -p "$OUT"
HPO_FAST_PLAN=$(SEED="$SEED" N="$N" python3 - <<'PY'
import json, os, random, sys
sys.path.insert(0, "tools/ci")
sys.path.insert(0, "tests")
import closure, shards
scripts, _ = shards.suite_scripts(open("tests/run.sh").read())
rng, n = random.Random(int(os.environ["SEED"])), int(os.environ["N"])
group = {s: s for s in scripts}
if os.environ.get("SPLIT_PRODUCERS") != "1":
    for a, b in closure.lane_edges(scripts):
        group[b] = group[a]
draw = {g: rng.randint(1, n) for g in sorted(set(group.values()))}
plan = {"n": n, "s": {s: draw[group[s]] for s in scripts}}
assert shards.check(plan), "a draw left a shard empty: pick another seed"
print(json.dumps(plan, sort_keys=True))
PY
) || exit 2
export HPO_FAST_PLAN GOLDEN_MODE=drift GOLDEN_REF="${GOLDEN_REF:-origin/main}" RUN_PART=fast GATE_SCOPE=full
printf '%s\n' "$HPO_FAST_PLAN" > "$OUT/plan.json"
for k in $(seq 1 "$N"); do
  HPO_FAST_SHARD="$k/$N" ./tests/run.sh > "$OUT/shard$k.log" 2>&1
  echo "shard $k/$N rc=$?" | tee -a "$OUT/summary.txt"
done
# Every `ok`/`FAILED` progress line names a script that ran; count each script once per shard.
grep -hoE '\] (ok|FAILED) +[^ ]+ (tests/[^ ]+)' "$OUT"/shard*.log | awk '{print $NF}' | sort | uniq -c \
  | awk '$1 > 1 {print "TWICE " $2} {print "RAN " $2}' >> "$OUT/summary.txt"
cat "$OUT/summary.txt"
