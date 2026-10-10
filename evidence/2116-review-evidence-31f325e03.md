# Evidence — fix review of PR #2116

Measured head: 31f325e03f05609edf55bced84b1a9acee1671c6
(branch fix/r9-bus-fetchhead; `git ls-remote origin refs/heads/fix/r9-bus-fetchhead` = 31f325e03f05609edf55bced84b1a9acee1671c6 at publish time; body `## Head` names the same sha)
Merge base: 7cd5a588cbbbef354c00148040da2d720b8a888c
Baseline copies: `git show 7cd5a588c:<path>` (cmp-empty against 23d354970 for bus.sh, the body's claim)
Reviewer worktree: /Users/timmalmstrom/hpo-seats/r9rev-2116/wt (detached at the head)
All arms run on COPIES under /Users/timmalmstrom/hpo-seats/r9rev-2116/{head,base,mut,mut2,armsfirst,export},
HPO_BUS_STATE pointed at scratch state dirs; a temp bare origin per run. Live bus state untouched
(scratch state dirs stayed empty); no ref pushed to the real origin.

## 1. What the parent is now (the code, at the head)

tools/audit/seat/bus.sh `append_commit()`:

    tip=$(git ls-remote "$REMOTE" "refs/heads/$fam/$pr" 2>/dev/null | awk 'NF { print $1; exit }')
    rc=$?
    [ $rc = 0 ] || { ... return 1; }
    if [ -n "$tip" ]; then
      [[ $tip =~ ^[0-9a-f]{40}$ ]] || { ... return 1; }
      git fetch -q "$REMOTE" "refs/heads/$fam/$pr" || { ... return 1; }
      parent="-p $tip"
    fi

The parent is `$tip`: the 40-hex sha `git ls-remote` answered for the ref, captured into a
shell local in THIS process, before the fetch. `git ls-remote` writes no per-worktree state.
The fetch is kept for the objects only (commit-tree cannot write a parent it cannot read).
`git grep -n FETCH_HEAD 31f325e03 -- .` leaves, in the instrument's production path, comments
only; the one executable read is the self-test's own precondition assertion (bus.sh:655).

## 2. RESULT lines — the defect reproduced and gone

RESULT own-arm(base, 7cd5a588c) appends=60 ok=39 refused=21 reparented=0 unreachable_built=6 parented_on_main_tip=6
RESULT own-arm(base) refusal shapes: "fatal: ambiguous argument 'FETCH_HEAD': unknown revision or path not i..." and a non-fast-forward push refusal
RESULT own-arm(head, 31f325e03) appends=60 ok=60 refused=0 reparented=0 unreachable_built=0 parented_on_main_tip=0
RESULT own-arm(base, N=25 too) appends=25 ok=16 refused=9 unreachable_built=3 parented_on_main_tip=3
RESULT own-arm(head, N=25 too) appends=25 ok=25 refused=0 unreachable_built=0 parented_on_main_tip=0

The own arm is the reviewer's instrument (disclosed as such: the finding #2092 carried no committed
harness), NOT the fixer's: no PATH shim and no in-window interposition. A real concurrent fetch of
an unrelated ref (`git fetch origin refs/heads/main`) runs in a tight loop in the SAME checkout
while the script appends to review/21 N times; the arm counts landed appends, refusals, and the
commits it built whose parent is main's tip. The race is timing-dependent — that is why the arm is
N appends and why the numbers are counts, not a single verdict — and it is not zero on the defect:
6 of 60 appends at the baseline were parented on main's tip, with 21 refusals in the two measured
shapes (push non-fast-forward, and `fatal: ambiguous argument 'FETCH_HEAD'`, the orchestrator's
second shape). At the head, 0 of 60.

    /Users/timmalmstrom/hpo-seats/r9rev-2116/myrace.sh <bus.sh> <N>

## 3. The fixer's harness, both ends (also run)

    bash tools/audit/seat/r9_rc_bus_fetchhead.sh <bus.sh> race|append|ootree
    bash tools/audit/seat/r9_rc_bus_fetchhead.sh <body_push.sh> bodypush
    bash tools/audit/seat/r9_rc_bus_fetchhead.sh <handoff_push.sh> handoffpush

RESULT race(base) push-verdict rc=1; built commit's parent c723b3b10448381139899d6a0cc729f42d43255f = main's tip != review/21's tip 012eb79c7 -> rc 1
RESULT race(head) push-verdict rc=0; built commit 9ae1b977c parent b8701f138 = review/21's tip -> rc 0
RESULT append(base) round-1 903ff5f3d round-2 ec4bbbdc9 tree c7d7c97b3
RESULT append(head) round-1 903ff5f3d round-2 ec4bbbdc9 tree c7d7c97b3
RESULT append(base) vs append(head): `diff` empty — byte-identical (the null control)
RESULT ootree(base) confirm rc=1, poster calls 0, verdict/21 AFTER confirm: exists -> HALF-APPLIED
RESULT ootree(head) confirm rc=1, poster calls 0, verdict/21 after confirm: absent -> nothing pushed, nothing posted
RESULT bodypush(base) parent 0c8080f83 (the decoy's tip) != handoff-body/A's tip 436b13d2f -> the arm's rc 1
RESULT bodypush(head) parent 436b13d2f == handoff-body/A's tip -> pass
RESULT handoffpush(base) published body "BODY MARKER B" -> NOT topic A's
RESULT handoffpush(head) published body "BODY MARKER A" -> topic A's

## 4. bus.sh --self-test, and the mutation proof (the PR's named predicate)

RESULT self-test(7cd5a588c) 45 checks, 0 failed
RESULT self-test(31f325e03) 48 checks, 0 failed
RESULT self-test(31f325e03, /bin/bash 3.2.57) 48 checks, 0 failed
RESULT self-test(5bd9385fc, arms-first) 48 checks, 2 failed — exactly the two new defect arms:
       "an intervening fetch of an unrelated ref does not reparent the appended commit" and
       "a copy outside a checkout refuses before it pushes the verdict ref" (46 of 48 pass)
RESULT M1 self-test: parent="-p $tip" reverted to parent="-p $(git rev-parse FETCH_HEAD)" -> 48 checks, 1 failed,
       the named arm, and nothing else -> the arm is attributed to that line
RESULT M2 self-test: the poster-guard line deleted -> 48 checks, 1 failed, "a copy outside a checkout refuses before it pushes the verdict ref"
RESULT handoff_push.sh --self-test 1 checks, 0 failed
The self-test is driven in CI by .github/workflows/governance.yml:332 (`bash tools/audit/seat/bus.sh --self-test`).

## 5. The poster guard's null control — a baseline export without .git is NOT refused

`git archive HEAD | tar -x -C <scratch>` (no .git), tools/pr/app_comment.sh present and 0755:
RESULT self-test from the export: 48 checks, 0 failed
RESULT race arm from the export: parent == ref's previous tip -> rc 0
So the guard refuses a copy parked outside a checkout, and does not refuse the documented
baseline-export use.

## 6. Head checks, class census, closure, budgets, drift, conflict

RESULT check-runs at 31f325e03 (commit's own API, all runs): 40 runs; 2 in_progress (Analyze (python), coverage);
       every other run success/skipped/neutral. No red.
RESULT class census `git grep -n FETCH_HEAD 7cd5a588c -- . | grep -v '^dev/audit/rounds/'`: 5 seams —
       tests.yml:3117 (comment), body_push.sh:20, bus.sh:150, handoff_push.sh:40, handover_prompt.py:94;
       each is in the diff or dispositioned in the body. No seam returned by the rule is undispositioned.
RESULT MODE: SCOPED -- 0 script(s) run, 33 scoped out; the same 5 changed files as the body names.
       tools/audit/ is on tests/closure.py's INERT list, so the new harness file is classified.
RESULT STRUCTURE RATCHET PASSED (rc 0); layout self-test: ok (rc 0)
RESULT env_drift.py --all: NO UNCLAIMED DRIFT (56 scenarios); NO STALE FIXTURE; both claim files byte-identical
RESULT VERSION / custom_components/heatpump_optimizer/manifest.json / RELEASE_NOTES.md: untouched (name-only diff empty)
RESULT `git merge-tree --write-tree origin/main HEAD` rc 0, no conflict, no MERGE-CLAIM refusal

## 7. Not re-derived here

- The body's local "harness header EXPECTED vs RESULT: 12 of 109" figure: tests/harness_headers.py
  cannot run in this reviewer's environment (tests/harness.py imports homeassistant, absent), and
  it is not a CI check at the head. Unverified by me; not a CI red.
- The body's `ci_predict` "PREDICT closures INERT READS" figure for the un-taken
  dev/audit/harnesses/ placement, and the run-specific commit shas in its arm tables (each run
  mints its own nonce, which the body states).
- tests/entities.py could not run here (same homeassistant dependency); classification is taken
  from the scoped gate returning SCOPED with all five files, and from CI's green `closures` and
  `instrument-self-tests` runs.
