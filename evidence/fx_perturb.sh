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

# Step 7a's whole body, so `--self-test` drives the code the step runs rather

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
# the targets outside `docs/` that its C108/C110 arms `exists()`-test. A
# renamed entry makes `git archive` refuse the whole pathspec, so a short copy
# fails the step loudly: it never grades a tree the generator did not read.
# THIS LIST IS NOT THE GENERATOR'S WHOLE READ SET, and treating it as one was
# #2853's review: C108 resolves every relative link in the docs against the
# copy root, and that set is data -- whatever path a documentation edit names.
# `claims_reg_line` therefore also copies the link targets the generator
# itself reports (`--print-link-targets`), so a link to an in-tree file this
# list does not name still resolves in the copy. Keep this list to the
# generator's own imports and parses; the link targets are derived.
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
  # THE COPY HOLDS EVERY TARGET THE DOCS LINK TO, not only the generator's
  # enumerated inputs. C108 resolves each relative link with `.exists()`
  # against the copy root, so a documentation edit that links an in-tree file
  # the enumeration does not name was graded broken in the copy though the
  # repository held it -- and the refusal's own remedy re-records the tree,
  # which changes nothing (#2853's review). The target list comes from the
  # generator's own extractor (`--print-link-targets`, run before its heavy
  # imports), so the copy step cannot drift from what C108 resolves; each
  # missing target is taken from HEAD, so the copy resolves exactly as a
  # whole-tree `git archive HEAD` copy does, and a target the repository lacks
  # is still graded broken. Today's targets are all in CLAIMS_INPUTS, so an
  # ordinary docs diff adds no archive here. The normalisation is done in the
  # shell, not by spawning an interpreter per target: a `python3 -I -c` here
  # cost this check 2.84-3.12 s of CPU across the 84 targets and put it over the
  # owner's 5 s cap (#2853's round-2 review). A leading `..` still escapes the
  # copy the way `os.path.normpath` refused it; a `docs/../x` form is left as
  # written, which `test -e` and git both resolve.
  local repo=$PWD t rel
  if [ -f "$repo/$CLAIMS_GEN" ] && grep -q -e '--print-link-targets' "$2/$CLAIMS_GEN" 2>/dev/null; then
    while IFS= read -r t; do
      [ -n "$t" ] || continue
      rel=""; continue
      [ -n "$rel" ] || continue
      [ -e "$2/$rel" ] && continue
      [ -n "$(git -C "$repo" ls-tree --name-only HEAD -- "$rel" 2>/dev/null)" ] || continue
      { git -C "$repo" archive HEAD -- "$rel" 2>/dev/null | tar -x -C "$2" 2>/dev/null; } || true
    done < <(cd "$2" && python3 -I "$CLAIMS_GEN" --print-link-targets 2>/dev/null)
  fi
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
