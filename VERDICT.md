Fix review: blocked 4f0bde1653627ab3c52f2325986119f80370e7bb root-cause-unanswered: fast (3.14) went red, unanswered

bus-nonce: 228d3b27b07b87836c7c16cd6402ff14

Delta review (round 2) of #2114. The prior verdict blocked f19851987
`carry-missing: not carried to D0`. That block is resolved; a new one replaces
it: the head turned `fast (3.14)` red and the body's `## Red checks: none on
this head` does not answer it.

## The red (the block)

`fast (3.14)` concluded `failure` on this head (check-run 114249368012, run
38064506824, "Run the suite" step, completed 2026-10-10T15:48:00Z). The
failing script is `tests/layout.py`, which is `run_always`, so no scope skips
it. Reproduced locally at the head, rc=1:

    layout: GUARD: 5 refusal(s) against d3dbf2c3fc42
    new-reference: dev/programme/carries/carry-201.json cites retired path
      .claude/workflows/brief_lint.mjs
    new-reference: ... docs/decisions/
    new-reference: ... tools/audit/briefs/D11.md
    new-reference: ... tools/audit/briefs/D13.md
    new-reference: ... tools/audit/round5/

All five are on the two lines of `dev/programme/carries/carry-201.json` this
branch edited: the `_comment` line naming `.claude/workflows/brief_lint.mjs`
(gained a trailing comma) and the `stage` line (D0 clause appended), each of
which already cited retired paths on main; editing the line makes its
citations new references against the merge base, and layout.py's guard refuses
new references to retired paths. Main at the merge base d3dbf2c3f is green on
tests.yml (run 38059574126, success), and the guard self-tests all pass, so
this red is the branch's own and not the instrument's. It is not one of the
three autofix classes (`UNDER-SCOPED`, `INHERITED CLAIMS`, killed unpinned
mutants), so no bot commit repairs it. The fix itself is sound; the body owes
the answer the second trigger demands (name the detector and its standing
cost, or the finding that none exists) — plus, on the merits, either the two
edited lines' retired citations moved to current paths, or the guard's answer.

## RESULT lines (all at 4f0bde1653627ab3c52f2325986119f80370e7bb, this box Apple M1 / python 3.11.5 / numpy 2.4.6, BLAS=accelerate)

RESULT head_unchanged=1 4f0bde1653627ab3c52f2325986119f80370e7bb
RESULT features_two_zone j_plain=110.436632 j_continuation_off=111.267093 continuation_gain=+0.830461 j_seeded_half_price=110.129674
RESULT features_null_single_zone j_plain=67.730056 j_continuation_off=67.730056 continuation_gain=+0.000000 j_seeded_half_price=67.729557
RESULT features_summary=ALL 3986 FEATURE CHECKS PASSED
RESULT layout_guard_refusals=5 rc=1 (all on carry-201.json)
RESULT brief_lint=rc=0 carry-201.json linted clean, no live roster group covers #201
RESULT ci_fast_3_14=fast (3.14) FAILURE (tests/layout.py, run_always)
RESULT ci_features_fast_lane=ok python3 tests/features.py (255s) -- the re-keyed check is GREEN at CI's kernel class
RESULT delta_code_unchanged=1 (custom_components, tests/features.py, tests/harness_headers.py, tests/closures.json, dev/audit/harnesses/r9_rc_blas_kernel_red_f21_p3.py all byte-identical f19851987 -> 4f0bde165)

## The delta f19851987 -> 4f0bde165

`f19851987` is an ancestor of the head. The delta is 22 files, all of them
main's own newer commits merged in (#2072, #2075, #2083: tools/audit/seat,
tools/pr, mutation_ledger rows, delivery rows, CLAUDE.md, fixer.md) plus the
branch's own ONE carry commit: one entry appended to
`dev/programme/carries/carry-201.json` with its `stage` and `_comment`
extended to name D0. Every file the reviewed behaviour lives in is
byte-identical across the delta (blob ids compared): `custom_components`,
`tests/features.py`, `tests/harness_headers.py`, `tests/closures.json`,
`dev/audit/harnesses/r9_rc_blas_kernel_red_f21_p3.py`. No VERSION, manifest,
notes heading or budget file in the branch's own diff. merge-tree against
origin/main exits 0, no conflict.

## The carry destination — judged legitimate, not re-blocked

`finding-propagation.md`'s "Where it goes" names three destinations: the
stage's brief (a live group's `brief` string plus any out-of-tree copy), the
role contract, and — "**The stage has no live roster group** → its own
`dev/programme/carries/carry-<N>.json`, N the destination issue, and
**creating it is part of the finding**". It does not name a dimension-method
document as a destination; `dev/governance/dimensions/D0.md` is the D0
method, policy, and the rule routes a no-live-group stage to the carry file,
which `brief_lint.mjs` lints as "the brief of a stage that has no roster
group". I verified: the only roster in the tree
(`.claude/workflows/wave-3l-groups.json`) covers issues 400/401/404/405/408/
457/460/463/465, none D0 or #201; `node tools/policy/brief_lint.mjs` exits 0
with carry-201.json linted clean (the linter itself "refuses a carry at an
issue a live group covers" — it did not refuse). The tree's own precedent is
directly on point: a75bf1662 landed a D0 finding as carry-1295.json "rather
than as an edit to ... D0.md because both D0.md and D9.md are one-sided policy
caps ... raising a cap needs the owner's confirmation obtained before the
push". The prior round's `carry-missing` is therefore resolved: the entry
(carry[10]) is real, names #2114, `effect: invalidates` (one of the rule's
three), carries the control with the voiding perturbation ("a second kernel
class where production's multi-start lands in the half-price plan's basin"),
a re-measurement instruction naming the check's own printed line, and a brief
that states preconditions, not opportunities. The finder's harness
(`dev/audit/harnesses/k1725_blas_kernel_gap.py`) is still unrunnable verbatim
on this box — its `score()` calls `m.simulate_trajectory(st, pw, ot, wi, ra,
so, DT)` with 7 positional arguments against a 3-positional keyword-only
signature, stale at the merge base, unchanged by the delta; the prior round's
disclosed one-line patch and its -0.2070 stand unchallenged.

## Arms not run here

The Linux/cross-kernel arm: this box is Accelerate, `OPENBLAS_CORETYPE`
selects nothing; the container lane was retired 2026-10-04 and
`gate-scoping.md` forbids re-deriving closures off Linux. The body deferred
the CI-kernel-class arm to the check-run; that run exists and is green
(`ok python3 tests/features.py (255s)` in the failing fast job), so the
re-keyed check's verdict holds at CI's kernel class too. `closures` and
`coverage` were still in progress when this verdict was taken.

## Evidence

`/Users/timmalmstrom/hpo-seats/r9rev-2114b/ev/` — HEAD names
4f0bde1653627ab3c52f2325986119f80370e7bb; features_head.log (local head arm),
layout_head.log (local layout rc=1), fast314.log (the failing CI job log),
brief_lint.out.
