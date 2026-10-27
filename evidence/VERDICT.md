Fix review: merge 1f077c996884c298e2d25f91e190a6fb61b78681
bus-nonce: 026ec9eb9df1c666766e154efc86cc19

# Fix review, round 1 — #2880 (head 1f077c996)

Measured from a detached worktree at the head; `git merge-base origin/main HEAD`
= `524c1896b` (origin/main's tip, so the diff measured is the branch's own).
Contract current: `git diff $(git merge-base origin/main HEAD)...origin/main --
dev/governance/roles/` is empty. Every number below was executed at this head
unless a line names another ref; the commands and logs are in the evidence
directory (`measurements.txt` indexes them).

## 1. "A writer that refuses what no read closes" — established, both ends

The refusal is `roster_edit._stage_why` / `_size_why`, called from
`op_set_stage`, `op_set_resume --field stage` and `op_append_group`. My harness
(`both_ends.py`, mine, not the fixer's) drives that op layer at both ends; the
baseline is an origin/main worktree, the head is this worktree, same op and args.

    RESULT baseline set-stage-shipped-written: ok=True detail='shipped'
    RESULT baseline set-resume-stage-shipped-written: ok=True detail='shipped'
    RESULT baseline append-group-XS-written: ok=True detail=('not-started', 'XS')
    RESULT head set-stage-shipped-written: ok=False
      detail="stage 'shipped' for R9-A is not a classified roster stage
      (classified: ...) in the/roster.json"
    RESULT head append-group-XS-written: ok=False
      detail="append-group: size 'XS' for R9-H is not in the durations model
      (L, M, S, XL) at tools/plan/durations.json in the/roster.json"

The null controls are in the same run — a writer that refuses everything is not
the claim:

    RESULT head set-stage-review-written: ok=True detail='review'
    RESULT head set-resume-stage-fixing-written: ok=True detail='fixing'
    RESULT head append-group-S-written: ok=True detail=('not-started', 'S')

The CLI path's rc=2 and stderr message are pinned by the self-test's own
`refusal()` arms; `roster_edit.py --self-test` reads `124 checks, 0 failed` at
this head.

## 2. One registry — established

Grepped `roster_edit.py`, `roster_sync.py` and `wave-r10-groups.json` for stage
and size literals (`"in-progress|not-started|carries-open|..."`,
`^\s*(SIZES|SIZE_ORDER|...)=`, `\bXS\b|\bXL\b`): no vocabulary list survives in
any of the three. `roster_sync.DERIVABLE_STAGES = roster_lib.DERIVABLE` and
`PROTECTED_STAGES = roster_lib.DISPOSITION`; the views are derived from
`STAGE_KIND`, and the size vocabulary is `sizes(durations)` over
`tools/plan/durations.json`'s `sizes_hours` keys (`('L','M','S','XL')`). The
roster's 208 groups carry only those four sizes at head; `unmodelled_sizes` = {}.
Against main's roster the same reader returns `{'XS': 'wave-r10-groups.json'}` —
a driven both-ends, so the head green is a measurement.

Two second copies survive outside the three files and both are dispositioned in
the body: `tools/plan/replan.py:108 LIVE_STAGES` (equal to `roster_lib.LIVE`,
carried to R10-FLOW-TOOLKIT-MODEL) and `orchestrator_tick.py:206
DEFERRED_STAGES`/`:207 UNBLOCKABLE_STAGES` (carried to R10-FLOW-WIP, whose
carry 9 names both). `state_docs.py:728` is a self-test fixture writing the
roster dict directly, not through the writer; its self-test passes at head.

## 3. The roster's changed lines lose nothing main carries — established

`git diff origin/main HEAD -- dev/programme/rosters/wave-r10-groups.json` is
8 changes, all `"size": "XS"` -> `"size": "S"` on the eight `R10-FLY-*` groups;
group set identical (208), and per-group stage and carry counts differ from main
on 0 groups. Against `origin/handoff/audit-r10-roster` (`eb0e5237d`) this head is
*behind*, not ahead: 7 stage movements and 8 groups' carries are other seats'
later writes on that branch, and no carry text in head is absent from it. The
roster branch still carries `XS` (the repair lives in the PR's copy); I
simulated the stamp merge with `git merge-tree` of main-plus-this-PR against the
branch and the merged roster carries 0 `XS` — the repair survives. `git
merge-tree --write-tree origin/main HEAD` exits 0 with no conflict. The body
accounts for the relabelling and for each carry it wrote, with read-backs at
`3dbef7271`/`9e7ee283d`; `carry_audit.py ... check --body` reads `6 finding
item(s): 6 routed, 0 unrouted, 0 bad destination(s)`.

## 4. The two mutant drivers — both prove their claims; one count in the body is wrong

- `r10_roster_sync_mutants.py` at head: 24 plants, every one `rc=1` with a named
  FAIL (`M1 4 ... M24 1`, matching the body line for line), driver prints
  `restored`; `--null` reads `rc=0 fails=0`. No survivors, no crash kills.
- `r10_roster_ops_mutants.py` at head: 31 plants (not 32), 30 named FAILs and
  `C6` a crash kill (`KeyError: 'carry'`, disclosed by the body), driver prints
  `plants: 31, without a FAIL line: ['C6']`; `--null` reads `rc=0 fails=0`. All
  seven new `S` plants die with named arms (`S1 1, S2 1, S3 1, S4 1, S5 3, S6 1,
  S7 2`), so the extension covers the new code.
- My own plant, by hand: deleting `op_set_stage`'s `_stage_why` call makes
  `roster_edit.py --self-test` read `124 checks, 1 failed` — `FAIL set-stage
  refuses an unclassified stage (got: (0, ''))` — and the file was restored from
  git (`git status` clean).

Figure correction (non-blocking, step 8): the body's `## Mutation proof` says
"32 plants" and its `## Figures` says "32 ops plants, 31 named FAIL and C6 a
crash kill"; the tree holds 31 plants, and the measured split is 30 named FAIL
plus the C6 crash. The driver, not the body, is what the tree answers, and the
seven new plants all die. Carry: R10-ORCH-ROSTER-SCHEMA

## 5. The RCA owes its four elements — present; one quoted output is stale

`dev/audit/rca/R10-N-vocabulary-drift.md` carries (1) a named cause — a
vocabulary declared on each side of a write and nowhere between, with the three
instances and their job ids; (2) process state **(a) the process did not exist**,
with (b) and (c) argued rather than asserted; (3) a cost test in one unit —
`cost(countermeasure)` = 0 new jobs, inside the two self-tests governance.yml
already runs; `cost(defect)` = two CI reds (`119785082787`, `122016117273` step
59) plus a planner dead on every run; `P(recurrence) = 3` measured from the
three instances; (4) a countermeasure with its red/fix demonstration, which I
re-ran: at `21b1ed140` `roster_edit` reads 124 checks/4 failed and `roster_sync`
61/4 failed; at this head 124/0, 64/0 and 31/0. The reproduction command is
given in full.

Figure correction (non-blocking, step 8): the RCA and the body quote
`KeyError: 'XS'` from that reproduction. At this head the same command prints
`replan.PlanError: R10-FLY-DAEMONIZE-ARGV: size 'XS' has no measured duration in
sizes_hours (L, M, S, XL)` — main's #2874 (`5f269ef0c`) added that refusal after
the RCA's base `6f44346080d2`. The class still reproduces (a plan over main's
roster still refuses, by name); the quoted exception text is stale at the head
this review measured. Carry: R10-ORCH-ROSTER-SCHEMA

## 6. Policy — dev/governance/roles/standing-dispatch.md

The six lines change one factual clause: "`roster_edit.py set-stage` accepts any
string and nothing verifies `branch`" becomes "`roster_edit.py set-stage`
refuses unknown stages; nothing verifies `branch`". The paragraph's instruction —
read the persisted ref, not the record — is unchanged; what changed is a
description of the writer, and it now records a real constraint (a seat can no
longer write an arbitrary stage word). It is still a role contract, so under
CLAUDE.md it merges only on @tvofi's approving review. The body says so in its
`## Approval` section and does not claim the approval there. The file is 39 lines
at its 39-line cap with `policy_lint.mjs` at 0 errors; no budget was raised.

**This verdict is not the owner's approving review.** It approves the code and
the record; the policy sentence must not merge as ordinary code. The merge seat
holds this pull request until @tvofi's approving review is on it.

## What I could not establish

- `archscore`'s `dS +0.0000 NULL` was not re-run (heavy; no budget or score file
  moves in the diff, and `tests/structure.py` passed at this head), so that one
  quoted figure is carried from the body, not verified by me.
- No check at this head is red (55 check-runs, all success/skipped; `gate`
  success twice, `pr-contract` success twice), so no red-check answer is owed
  here; the body's `## Red checks` section answers an earlier head's
  `entities.py` arm and I did not re-run that lane.
