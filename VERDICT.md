Fix review: merge 19ffbcbfbd43b36492bc594fb86df307eb34f6b7

bus-nonce: e75ff14d08b9a349eb2375b377c491b9

# Fix review — #2112 `bus.sh orphans` (R9-ORPHAN-HANDOFF)

Measured head: **19ffbcbfbd43b36492bc594fb86df307eb34f6b7** (`git ls-remote origin
refs/heads/fix/r9-orphans` re-read at post time, unchanged). The authored code
head is `1965925bbea7d959e20b249fabff509786f06cc4`; this review measures the
row-head, which is a superset. Detached worktree at the head; I pushed nothing
to GitHub but this verdict.

This is round 1 for this PR (the first fixes-round against it).

## RESULT — it runs, and prints a real answer

    RESULT orphans-live: 8 stranded, 1 superseded; skipped no-body=152
           named=10 ancestor=51 young=1; origin main c729bb3  (rc 1)
    RESULT orphans-total: 8+1+152+10+51+1 = 223 == my own
           git ls-remote origin 'refs/heads/handoff/*' = 223   (reconciled)

`bus.sh orphans` fetches the three families over the git protocol, token-free,
and returns one line per state with rc 1 for STRANDED only. The stdout is the
detector working, not an error and not an empty set.

## RESULT — the predicate is content-aware, on my own fixture

I built an independent local bare remote and drove the predicate (no ref pushed
to `origin`; evidence `fixture.txt`):

    RESULT ancestor:  a handoff ref whose tip is an ancestor of main is NOT
           reported (ancestor=1); --no-ancestry reports it -> the ancestry
           juncture is load-bearing and correct.
    RESULT superseded: a ref whose added file main carries under a moved path
           (tools/x1.py -> dev/x1.py) is SUPERSEDED, not STRANDED; --no-content
           reads it stranded -> the content arm is load-bearing.
    RESULT orphan:    a ref whose work is absent from main is STRANDED
           repair=opener.
    RESULT named:     a ref with a pull request at fix/<t> is not reported.
    RESULT null:      a handoff ref with no handoff-body ref is never owed.

The body's two named cases both hold: "not an ancestor" does not by itself
produce STRANDED, and "carried by another path" is separated from "absent".

## RESULT — the mutation proof reproduces

Deleting the `&& content_superseded "$tip"` condition (bus.sh:448) turns exactly
two arms red, as the body says:

    FAIL a ref whose file main already carries under a moved path is SUPERSEDED
    FAIL green: with the pull requests pushed nothing is stranded and the run is 0
    bus self-test: 53 checks, 2 failed

Restored, `--self-test` is `53 checks, 0 failed`, and the added arms are the
orphans arms (opener/update/review, two null controls, the content arm, the
repaired-remote green arm). The proof is not vacuous.

## RESULT — the red check is answered

The head's own check-runs: the only red gate check is **`budget-raise-gate`**
(failure, both heads); `coverage` and `Analyze (python)` are in-flight `null`,
not red, and the `cancelled` runs are not red. The body names
`budget-raise-gate` and answers it ("red by design", the raise is owner-gated
under 0013, cheaper detector none). Trigger answered.

## RESULT — the budget raise is to the measured value (verified)

`policy_lint --budgets` at the head: measured == cap for every moved cap
(`corpus ~60449 = cap 60449`; `role record ~7405 = cap 7405`; the two per-file
caps exactly). I removed the mechanism (reverted the four changed
policy-prose files to the merge base): corpus falls to 59898 and record to 7226,
so the prose accounts for 551 and 179 of the movement; the remainder is
pre-existing drift already inside the old band, absorbed by a re-record that the
policy requires be taken to the head measurement. Cap == measurement, not a
padded raise. Still owner-gated; my verdict is not that approval.

## RESULT — forward-carry is present, versions untouched, merge is clean

- `dev/governance/roles/orchestrator.md` section 5b and
  `dev/governance/rules/delivery-status-tracking.md` both carry the finding as a
  precondition with its control. Both are policy and await the owner, as the
  body says.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched; no claim file is
  in the diff; `env_drift --all` reports no drift.
- `git merge-tree --write-tree origin/main <head>` exits 0, no conflict, no
  driver verdict. The body's disclosed `bus.sh` conflict is with a sibling ref,
  not `main`.
- Body figures corroborate: `check-wave-script.mjs` 172/0, `fold_ledger check`
  the identical string, `rules_sync --check` ok, `structure.py` PASSED.

## Recorded limitation (not a block)

The content arm's `A`/`R` cases match a **basename anywhere on main**. I
reproduced a false supersede: a ref adding `dev/unique/state.json`, with content
nowhere on main, reads SUPERSEDED because `dev/other/state.json` shares the
basename (fixture `lane-d`). The rule's breadth is nevertheless load-bearing —
the one real SUPERSEDED ref (`r9-eg-coordinator-seams`) adds
`tools/audit/harnesses/eg_b7_seam_hubs.py` and main's copy at
`dev/audit/harnesses/` has a **different** blob, so a content-hash rule could
not catch it. The failure still prints the ref's own line (mislabelled repair,
rc 0), and no live ref is currently affected: with ancestry on, exactly one
non-ancestral ref is content-carried and it is the genuine case, so the
false-supersede count on the live remote is 0. Worth a follow-up tightening
(suffix-aware, or a size/similarity arm) via `finding-propagation.md`; it does
not block a detector that repairs nothing and surfaces every ref it judges.

## Figures I could not re-derive

The body's live counts were taken at `origin/main` `7cd5a588c`; the remote moved
several times during this review (I saw `c729bb3`, `d3dbf2c`). The body says so
itself ("the counts are a function of that tip and the clock"). I re-derived the
mechanism, not the digits: at the current tip the run totals reconcile exactly
with my own enumeration (223 = 223), and `--no-ancestry` still removes the large
ancestral set. The body's specific digits (10 stranded, no-body=161, delta 45)
are true of that tip and are not reproducible now, by the body's own statement.

## Evidence

`/Users/timmalmstrom/hpo-seats/r9rev-2112/evidence/` — `head-19ffbcb.txt`,
`orphans-live.txt`, `self-test.txt`, `mutation-self-test.txt`, `fixture.txt`,
`independent-count.txt`, `budget-earned.txt`, `checks.txt`, `structure.txt`.
