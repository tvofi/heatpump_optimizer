pinned_touched() { # file of changed paths, pins (one per line)
  local f p
  while IFS= read -r f; do
    while IFS= read -r p; do
      [ -n "$p" ] || continue
      # shellcheck disable=SC2053 -- $p is a pattern on purpose
      if [[ $f == $p || $f == "$p"/* ]]; then return 0; fi
    done <<<"$2"
  done <"$1"
  return 1
}
# Step 6g's whole body: the D6 claims register `tests/harness_headers.py`
# executes in `fast`, rerun on a copy of the tree when the diff touches the
# documents it reads. #2609 (ff83a3d7) moved README.md's link count, ran prepr
# with PREPR_SKIP_CLOSURES=1, and reached CI with claims.json and claims.md
# stale. The generator writes into the tree it runs in, so it runs on a copy
# and the committed files are compared, never rewritten.
CLAIMS_DOCS='README.md
docs/*.md'
CLAIMS_GEN=dev/audit/rounds/round4/D6/claims.py
# What the copy must hold: `git archive` of the whole tree writes 135 MB, of
# which dev/audit's round evidence is 82 MB the generator never opens, and it
# cost 2.7-3.7 s of the step's 7.4-8.2 s of CPU (R10-FLOW-JIDOKA's review,
# 2026-10-26) where a copy of these entries costs 0.2 s. Each is a read in
# `claims.py`, not a guess: the files and docs it parses, the package it
# imports and scans, the `tests` modules it puts on `sys.path`, its own
# directory (which holds the committed register it is compared against), and
# the six targets outside `docs/` that its C108/C110 arms `exists()`-test
# (NOTICE, dev/README.md, dev/archive/README.md, dev/archive/backlog.md,
# tests/README.md, tools/audit/archscore/ABOUT.md). A renamed entry makes
# `git archive` refuse the whole pathspec, so a short copy fails the step
# loudly: it never grades a tree the generator did not read.
CLAIMS_INPUTS='README.md
DISCLAIMER.md
LICENSE
NOTICE
VERSION
hacs.json
docs
.github/workflows
custom_components
tests/README.md
tests/harness.py
tests/golden.py
tests/entities.py
tests/rolling.py
tests/profiles.py
tests/hastub
dev/README.md
dev/archive/README.md
dev/archive/backlog.md
tools/audit/archscore/ABOUT.md
dev/audit/rounds/round4/D6'
claims_reg_line() { # changed-paths file, tree copy -> one line; rc 0 current, 1 stale, 3 skipped
  local d out r f stale="" hdr
  pinned_touched "$1" "$CLAIMS_DOCS" || { echo "no change to README.md or docs/*.md"; return 3; }
  [ -f "$2/$CLAIMS_GEN" ] || { echo "no $CLAIMS_GEN in the tree"; return 3; }
  d=$(dirname "$2/$CLAIMS_GEN")
  # The verdict is the generator's output against the register committed
  # beside it. A copy holding the generator but not the register would compare
  # against nothing and read as stale, so it is named instead.
  [ -f "$d/claims.json" ] && [ -f "$d/claims.md" ] \
    || { echo "the copy has no committed $d/claims.json and claims.md beside $CLAIMS_GEN, so nothing was compared"; return 1; }
  mkdir -p "$2/.was"
  cp "$d/claims.json" "$d/claims.md" "$2/.was/"
  out=$(cd "$2" && PYTHONPATH=tests/hastub python3 "$CLAIMS_GEN" 2>&1); r=$?
  [ "$r" -eq 0 ] || { echo "$CLAIMS_GEN exited $r: $(tail -1 <<<"$out")"; return 1; }
  for f in claims.json claims.md; do cmp -s "$2/.was/$f" "$d/$f" || stale="$stale $f"; done
  hdr=$(python3 -I -c 'import contextlib, io, sys; sys.path[:0] = ["tests", "tests/hastub"]; from pathlib import Path
with contextlib.redirect_stdout(io.StringIO()): import harness_headers as h
e, g = h.expected_from(Path(sys.argv[1])), h.printed_from(sys.stdin.read())
print(" ".join(f"{k}={g.get(k)} (header {v})" for k, v in e.items() if g.get(k) != v))' "$2/$CLAIMS_GEN" <<<"$out") \
    || { echo "the header comparison did not run"; return 1; }
  if [ -n "$stale$hdr" ]; then
    echo "${stale:+committed${stale} not what $CLAIMS_GEN writes; }${hdr:+header RESULT moved: $hdr; }re-run it and commit"
    return 1
  fi
  echo "$CLAIMS_GEN rewrites claims.json and claims.md byte-identical, its header RESULTs hold"
}

# Steps 6a and 6b: the two failures CI already repairs, refused before the push.
# `claims-autofix` and `closures-autofix` fire only after `fast` or `closures`
# has gone red, so every repair they make costs a gate run, a held-run approval
# and a bot commit on a head a reviewer may already be reading. In the week to
# 2026-09-24 they were the most frequent repairable reds (the census and its
# per-job tables are /mnt/project-files/ci-autofix/). The checks are CI's own
