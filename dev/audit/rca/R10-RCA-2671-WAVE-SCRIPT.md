# R10-RCA-2671-WAVE-SCRIPT: two reds on #2671 that every local path predicted green

The root-cause seat for #2671 (R10-ORCH-LEDGER) at head `338c9ba49`, run
2026-10-23 against `origin/main` `f046076ad`. It follows
`dev/governance/roles/root-cause.md` and `dev/governance/rules/defect-root-cause.md`.
The seat did not edit #2671's branch and filed no issue.

Trigger: the second one. Governance run 39996377402 (on `refs/pull/2671/merge`
= `9c5110c27`, PINNED `fd7e289d0`) went red on `wave-script` and
`instrument-self-tests`. The fixer's body reports `prepr.sh` and
`ci_predict.py` green on the same head.

## 1. Reproduction

Commands ran in a shared clone with `refs/remotes/origin/main` set to the PR's
base. The clone is needed because `agreement.mjs`'s merge-subject guard walks
to `merge-base HEAD origin/main`. A live `origin/main` that has already merged
the PR under test moves that walk onto the branch's own merges. It printed
`refused=3` on #2669's tree, and CI printed `refused=0` there.

**wave-script.** The arm builds CI's tree, then runs the lane. Steps: a merge
commit of head into base, base as first parent. The restore pathspecs that
`governance.yml`'s wave-script job uses, checked out from the base. Then
`agreement_py.py --out` and `agreement.mjs --py-json`.

| tree | `agreement.mjs` copy | RESULT line | rc |
|---|---|---|---|
| `338c9ba49` | branch (what prepr step 3f4 runs) | `divergent=0 unregistered=0 dead=0 refused=0` | 0 |
| `338c9ba49` merged into `fd7e289d0` | base, full wave-script restore (what CI runs) | `divergent=0 unregistered=3 dead=0 refused=0` | 1 |
| `fd7e289d0` (no `ledger.py`, no harness) | branch | `divergent=0 unregistered=0 dead=3 refused=0` | 1 |
| null: #2669 `0506a55b2` merged into `e6dd46277` | base, full restore | `divergent=0 unregistered=0 dead=0 refused=0` | 0 |

The three UNREGISTERED lines are CI's own: `[0-9a-f]{40}`,
`\bledger_open ([a-z-]+) ` and `\blevel_line ([a-z-]+) `. #2669 is the null
control because its diff also edits `tools/policy/agreement.mjs`, and CI's
wave-script was green on it (job 120594524199, `AGREEMENT ok`).

**instrument-self-tests.** `python3 -I tools/audit/seat/ref_privacy.py --check`
at `338c9ba49` prints `REFUSE tools/audit/seat/ledger.py:726` and `1 refused`.
That matches CI job 120560854278. At `origin/main` it prints `0 refused`.

**The fixer's account, corrected.** `ci_predict.py` does not run the agreement
lane under either copy. Its predictions are `closures`, `fast` and
`mutation` (`predict()` → `no_recording`, `under_scoped`, `unpinned`). Only
`prepr.sh` step 3f4 runs the lane, from the branch's copy. The fixer's
standing-cost figure, 0.2–0.4 s, is the `seconds=` of the node half alone.
`agreement_py.py` measured 6.4 s wall-clock here. The full base-pinned arm,
fresh checkout included, took 13 s on the null control and 18 s on the defect.

## 2. Cause

Three causes. The third is wider than the one reported.

1. **wave-script, predictor side.** `prepr.sh` steps 3e–3g ("the graders CI
   pins to the base, run on THIS head's copy") port only one direction of a
   pinned job: the push to main, which grades with the head's copy. The pull
   request's own run grades the head's tree with the base's copy. No local
   path runs that direction for any pinned grader. The two verdicts differ
   only when the diff touches a pinned path. #2671's diff touches
   `tools/policy/agreement.mjs`.
2. **instrument-self-tests.** `ref_privacy.py --check` has no local path.
   `grep -c ref_privacy tools/pr/prepr.sh` prints 0 at `origin/main`. It reads
   the branch's own copy, so no copy question arises. It is simply not run.
   The same is true of `selftest_wiring.py --check`, the other tree-reading
   `--check` in that job (0.14 s, no measured instance).
3. **The lane has no passing tree for a new shared grammar.** wave-script is
   a required context: it is in `rules/branches/main`'s
   `required_status_checks`. A pull request that adds a second writer of a
   grammar and registers it in `SHARED_GRAMMARS` is UNREGISTERED under the
   base's copy. A pull request that registers first is DEAD (table row 3). So
   a correct local predictor turns the CI red into a local red, and the
   pull request is still unmergeable without a bypass. The precedent is #2423:
   it edited the lane's readers, its final head `58dbe46a0` has
   `wave-script=failure`, and it merged anyway. Since the lane landed in #1847
   (`948671af1`, 2026-10-02), #2671 is the first pull request to add a
   `SHARED_GRAMMARS` entry. The enumerator is `git log origin/main
   --first-parent -m -p` over the lane's two paths, counting added registry
   lines per merge. It shows only #1847's initial 27.

## 3. Process state

**(c) for all three.** Causes 1 and 2 are the shape `root-cause.md` §2 names:
a check that exists in CI but in no local path, or is half-ported, is (c).
Step 3f4 ran and passed. Its unit read the head's copy, the opposite direction
from the pull-request run. #2073 (`R9-RCA-stale-pins.md`) is the same shape:
step 6d passed while reading one of `mutation`'s two directions. Cause 3 is
also (c): base-pinning the lane was followed as designed, and for a
registration it produces a required check that no tree can pass. None of the
three is (b). No instruction was disobeyed.

## 4. Reach

Over `origin/main` merges 2026-10-09..10-23, 25 merges touched one of
`agreement.mjs`, `field_coverage.mjs`, `policy_lint.mjs`,
`check-wave-script.mjs` or `brief_lint.mjs`. Every commit of those 25 pull
requests was read for a red `wave-script` or `policy-docs`:

- Same shape (head copy edited, red under the base's copy): #2423 (2 heads,
  `divergent=2`, the fix to the readers themselves), #2671. #2636 is probable
  but unverified: 2 heads were red on `policy-docs` `FIELD COVERAGE REFUSED`,
  and its diff edits `field_coverage.mjs`, `policy_lint.mjs` and
  `.claude/settings.json`.
- Not this shape: #2390, #2406, #2408, #2415 and #2421 were red on
  `divergent=2` at base `07a09406a`. That was main's own merge-subject
  divergence, which #2423 fixed.

Over the same window, 147 of 440 merges touched some path in the wave-script
restore list. That figure is the trigger rate if the arm keys on the whole
list.

## 5. Cost test

Unit: wall-clock seconds per pull request.

- cost(defect) is at least one Governance run from push to a visible red.
  Run 39996377402 took 9 min 47 s (created 17:35:53Z, updated 17:45:40Z), so
  the floor is about 600 s. A fixer round comes on top; estimated 30 min,
  from #2671's round 3. For cause 3 there is no bounded cost: the head is
  red until a bypass. It has been red since 17:36Z.
- P(recurrence), measured: 3 pull requests in 440 merges for causes 1 and 3
  (#2423, #2636 probable, #2671), which is 0.68 %. For cause 2: 2 known
  instances, #2447 (roster carry) and #2671, which is at least 0.45 %.

| countermeasure | standing cost per PR | cost(defect) × P, CI floor only | with a fixer round | verdict |
|---|---|---|---|---|
| A: base-pinned arm, keyed on the lane's reader closure being touched | 25/440 × 15 s = 0.85 s | 0.0068 × 600 = 4.1 s | 0.0068 × 2400 = 16 s | build |
| A': same arm, keyed on any wave-script pin being touched | 147/440 × 15 s = 5.0 s | 4.1 s | 16 s | do not build; key narrowly |
| B: `ref_privacy.py --check` on every run | 1.46 s (measured at `338c9ba49`) | 0.0045 × 600 = 2.7 s | 11 s | build |
| `selftest_wiring.py --check` | 0.14 s | P unmeasured (0 instances) | — | not costed; no instance |
| C: give the lane a passing route for a registration | design change, once | unbounded per instance (no green tree) | — | owed: an owner decision, not a seat's |

## 6. Countermeasures

- **A** (cause 1): run each base-pinned grader under CI's restore when the
  diff touches a pinned file in that grader's own load closure. For the
  agreement lane that closure is what `agreement_py.py --restore` derives,
  plus `agreement.mjs`. CI's restore means a merge commit of head into base,
  base as first parent, with the job's restore pathspecs checked out from the
  base. The demonstration is in section 1: it fires on `338c9ba49`
  (`unregistered=3`, rc 1), and the #2669 null control passes (rc 0). It
  must not run with a live `origin/main` that is past the PR (section 1's
  `refused=3` artifact). It does not go green by skipping, because the
  trigger is a diff fact. Carried to R10-FLY-CIPREDICT-LAYOUT.
- **B** (cause 2): add `ref_privacy.py --check` to the local path. It fires
  at `338c9ba49` (`1 refused`) and passes at `origin/main` (`0 refused`).
  Carried to R10-FLY-CIPREDICT-LAYOUT.
- **C** (cause 3): the lane needs an admissible route for a new shared
  grammar. Two candidates. (i) DEAD does not refuse an entry marked as
  pending its second writer, so a registration can land first. (ii) The
  registry moves out of the pinned program into a code-owned data file that
  is read from the head. Either one changes a required check's semantics, so
  it is the owner's call. Carried to R10-MERGE-SUBJECT-HARDEN, the live group
  that owns `tools/policy/agreement.mjs`, for the orchestrator to confirm or
  re-route. Until C lands, #2671's wave-script red is passable only by the
  route #2423 took, or by not sharing the grammar.

The roster at `handoff/audit-r10-roster` `a29c7ebfb` already carries #2671's
note to R10-FLY-CIPREDICT-LAYOUT. That note says "run tools/policy/ as it is
at origin/main", which is not CI's restore: it omits the other restored
paths, the merge tree and the base-pinned `origin/main`. It also leaves cause
3 to that group, which owns only `tools/pr/ci_predict.py`. The corrections
are queued to the roster seat.
