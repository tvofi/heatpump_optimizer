Fix review: blocked f19851987a55fb6ac53d1b40935f2c13838f49ab carry-missing: not carried to D0

bus-nonce: 6c3a5eccd88e5d78d6b96e6086ee281f

# Fix review — PR #2114 (R9-RC-BLAS-KERNEL-RED), head f19851987a55fb6ac53d1b40935f2c13838f49ab

Measured at the head named above, from a detached worktree at it, against merge
base `7cd5a588c`. Merge base checked first: `git diff
$(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is
empty, so the contract I read is current. The fix itself measures clean at every
arm I could reach; the block is the forward-carry alone.

## The re-key is real, and the check is not vacuous

RESULT lines (my own runs; logs cited at the end):

    RESULT block_head_two_zone=1 j_plain=110.436632 j_continuation_off=111.267093 continuation_gain=+0.830461 j_seeded_half_price=110.129674   -> ok, ALL 14 FEATURES BLOCK PASSED, rc=0
    RESULT block_head_single_zone_null: j_plain=67.730056 j_continuation_off=67.730056 continuation_gain=+0.000000   -> ok (exact: schedules array-equal)
    RESULT block_base_two_zone=1: FAIL R9-F2.1 P3 [shipped 110.4366, seeded 110.1297], 1 of 14 FAILED, rc=1
    RESULT mutation_two_zone=1 j_plain=111.267093 j_continuation_off=111.267093 continuation_gain=+0.000000: FAIL, 1 of 14 FAILED, rc=1

**Both ends, on this box.** At the merge base `7cd5a588c` the OLD check is RED
on Accelerate (`FAIL ... [shipped 110.4366, seeded 110.1297]`); at the head it is
green. The defect this PR claims to fix is reproduced at the base and fixed at
the head, by the same block command the body names.

**Mutation (step 1), reproduced exactly.** I planted `return cands  # MUTATION`
at the head of `_optimize_space_only`'s `move_starts` (`optimizer.py`) — the
continuation removed, the `934dcb1fc^` route. The check goes red at the exact
arm: `FAIL R9-F2.1 P3: the half-price continuation buys a strictly better storage
plan...`, `1 of 14 FEATURES BLOCK FAILED`, with `j_plain=111.267093`
`j_continuation_off=111.267093` `continuation_gain=+0.000000`. Restored with
`git checkout --`; tree clean. The single-zone null arm stays green under the
same mutation (its `j_plain == j_off`), which is the body's own claim about that
arm. So the new predicate is not vacuous — removing the mechanism it exists for
moves the acceptance.

**The old arm under the same mutation**, as the body states: `110.129674 + 0.1 -
111.267093 = -1.037`. Reproduced.

**Addressing my dispatch's question 2.** The seeded race is still MEASURED and
PRINTED and non-gating: every run emits `RESULT f21_p3_two_zone=1 j_plain=...
j_continuation_off=... continuation_gain=... j_seeded_half_price=...`, and the
check reads only `j_plain < j_off`. Removing the gate did not remove the
observation. The `j_seeded_half_price` figure is the old race's other side, kept.

**Attention the check's `move_starts` replacement deserves.** `_f21_ms_no_continuation`
forces `move_starts` to `lambda cands, maxiter: cands` — the parameter's own
default in `_multi_start_minimize`, so the no-continuation arm is the
pre-continuation route reached by one parameter, not a second copy of the
multi-start. Correct, and the null-arm exactness (`move_starts` returns its
candidates untouched unless `two_zone_enabled`) is real: the single-zone arm
asserts `j_plain == j_off` AND `np.array_equal(pw, pw_off)`, with no tolerance.

## Question 1 — the key does not move across BLAS builds: VERIFIED IN PART

The claim is that `continuation_gain` is stable where `+0.1000` vs `-0.2070` was
not. What I could reproduce: on this box (Apple M1, Accelerate) the new arm reads
`continuation_gain=+0.830461`, and the fixer's harness ladder — which I re-ran —
reads `0.25 -> +0.840025`, `0.50 -> +0.830461`, `0.75 -> +0.000000`,
`1.00 -> +0.000000`: the gain is a CLIFF, so a kernel change toggles between 0
and ~0.83 and cannot land a verdict on a thin margin. That is the structural
reason the re-key should hold across kernels, and it is measured.

What I could NOT reproduce, and so treat as UNVERIFIED rather than green: the
Linux-side values of the NEW arm. `OPENBLAS_CORETYPE` selects nothing on an
Accelerate numpy (the harness's own env line: `core=(unset) -- no OpenBLAS Core:
line`), the container lane is retired, and `gate-scoping.md` forbids re-deriving
closures off Linux. So the Sandybridge/Haswell/Nehalem rows for the new arm are
taken from the body, and the Haswell (CI) row in particular is owed as a
check-run, not established here. The old arm's `-0.2070` on this box IS verified
(below).

**The finder's harness, and why I could not run it verbatim.** The body names
`dev/audit/harnesses/k1725_blas_kernel_gap.py` as #1726's instrument. It does
NOT run at this head: `score()` calls `m.simulate_trajectory(st, pw, ot, wi, ra,
so, DT)` while the live signature is
`simulate_trajectory(initial_state, power_schedule, weather, *, dt_hours=)`.
This is pre-existing and not this PR's — the file is byte-identical to the merge
base, untouched by the diff, and its stale call is present at `7cd5a588c` too.
I patched that ONE line in a working copy (marked `# REVIEWER PATCH: stale API`,
then restored; whole-tree `git status` clean) to run its P3 arms:

    RESULT f21_p3_two_zone_margin=-0.2070 (j_plain=110.4366, j_seeded=110.1297)
    RESULT f21_p3_single_zone_margin=+0.0995

which are precisely the body's Figures and #1726's null control. So the finder's
P3 arm is reproduced, by the finder's own instrument (one disclosed line
patched) and independently by the check's own printed `j_seeded_half_price` and
`j_plain`. The fixer's harness at head reproduces the body's whole Figures table,
including `threads_identical=1` (threads are not the mover).

## Question 3 — the closure repair is the table only

Confirmed. Commit `be7dc8be1` touches `tests/closures.json` ALONE, adding one
line, `dev/audit/harnesses/r9_rc_blas_kernel_red_f21_p3.py`, to
`inert_reads['tests/harness_headers.py']` (541 entries, still sorted). The
recorded `closed`/`recorded` maps are unchanged, and the diff reaches no other
data file. No FULL re-derive is claimed: the body states that at `be7dc8be1` the
diff reaches `tests/closures.json` itself so `closure.py affected` answers
`CASE: FULL` and step 6b SKIPS, leaving every closure to CI's own derivation —
exactly what the head must do. `python3 tools/pr/ci_predict.py --base 7cd5a588c`
at the head prints `no closures or fast red predicted ... (a data-file read is
not seen)`; the recording is earned by `harness_headers.py` reading every harness
header, not gamed.

## Other contract steps

- **Red checks (step 11).** None on the head. `be7dc8be1` shows 9 `cancelled`
  runs at `14:41:3xZ` — superseded by the head push at `14:37:48Z`/`14:41`, not
  `failure`. `fast (3.14)`, `mutation`, `pr-contract`, `delivery-status`,
  `briefs`, `typing`, `closure-scope` all `success`; `closures`/`coverage`/the
  python `Analyze` were still running at my read. No red → no answer owed.
- **Conflict (step 13).** `git merge-tree --write-tree origin/main HEAD` exits 0,
  no driver marker. Not blocked on that.
- **Versions (step 5).** `VERSION`, the manifest and `RELEASE_NOTES.md` are
  untouched by the three-dot diff.
- **Class (step 6).** #1725 states two seams — `optimality.py`'s ftol check and
  this P3 storage comparison. The first was fixed by #1726 (already on main); the
  body dispositions the second, which is this diff. Both arms are accounted for;
  the rule the body cites ("measure each arm per kernel and key the verdict on
  what does not move") is verbatim `tests/README.md:267`. No third seam was
  demonstrated, so the class reads as those two, both closed.
- **Head SHA (step 7).** The head I measured is the head in the body and on the
  remote; `git ls-remote` still reads `f19851987...`.

## Why blocked

The body carries a `## Forward-carry` section naming `dev/governance/dimensions/D0.md`
for the optimality finding — "on Accelerate this platform's multi-start ships
110.436632 where a warm start from the half-price plan reaches 110.129674, i.e.
0.307 left on the table" — and `tests/features.py` at this head asserts in-tree
that "the optimality question itself is carried to D0's brief". Under
`finding-propagation.md` the producing PR does not merge until that carry is in
the tree, and a body or code comment records a finding without delivering it.

It is not delivered:

- `dev/governance/dimensions/D0.md` is byte-identical to `origin/main`
  (`git diff --quiet origin/main HEAD -- dev/governance/dimensions/D0.md`).
- no `dev/programme/carries/carry-*.json` is added by the diff (the four files
  are `tests/features.py`, `tests/closures.json`, the new harness, and the
  delivery row).
- `grep -rn "110.129674\|left on the table"` over the tree returns the authored
  `features.py` only.

So the finding exists only in this PR. The body's own words ("Named for the
destination rather than filed") are the disclosure; the in-tree comment is the
overclaim, and both point the same way: D0 must receive this, and has not.

I am not judging whether the optimality gap is the right size or whether D0 is
the right owner — I am reporting that a destination this PR names does not hold
what it claims. Per `finding-propagation.md` the destination for a stage with no
live roster group is its own `dev/programme/carries/carry-<N>.json`, which this
diff can create; that is the repair. If instead the fixer's judgement is that the
gap lacks its null control (there is no flat-price arm for it here) and is not
yet established, then it is "measured first or dropped": drop the item from
`## Forward-carry`, drop the "carried to D0's brief" claim from the comment, and
say so. Either repair resolves this; leaving it named-but-absent does not.

I flag as non-blocking friction, matching the body's own second bullet: the
kernel rule's instrument is cited at `tools/audit/harnesses/k1725_blas_kernel_gap.py`
in both `tests/README.md:271` and `dev/audit/README.md:235`, but the file lives
under `dev/audit/harnesses/`; and that same file no longer runs (above).

Evidence: `/Users/timmalmstrom/hpo-seats/r9rev-2114/ev/` — `EVIDENCE.md` and the
run logs (`features_block_{head,mutant,base}.log`,
`k1725_finder_{head,patched_head}.log`, `fixer_harness_head.log`).
