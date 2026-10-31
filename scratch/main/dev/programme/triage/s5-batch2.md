# Proposal triage, session s5, batch 2 (P34-P41)

The s5 orchestrator's eight proposals of 2026-10-23 (items A-H of its
out-of-tree `proposals-s5-batch2.md`), ruled in order as P34-P41 from
`dev/governance/roles/proposal-triage.md`. Two are defects in an instrument,
not proposals (P34, P37): each is ruled only to confirm or set its route, and
P37 was ruled already as `s5-batch1.md#P23`.

Base: origin/main `d7cb63508`; roster origin/handoff/audit-r10-roster
`222cd5278`, read with
`git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json | jq -r '.groups[] | select(.group=="<G>") | .carry[]'`.
"carry N" below is that list's 0-based index at `222cd5278`. Logs cited by
file name are in the s5 orchestrator's scratch directory (out of tree).
GitHub calls: 0.

A roster op citing an ACCEPT below resolves only once this file is on the
roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P34: the train reads `ci red=[]` while a required context is red
Verdict: ACCEPT -> R10-TRAIN-OVERLAP-GRADE (new carry; not a proposal: defect, route set here)
Source: s5 item A; `merge-report.txt` 18:32:27Z line; `train/run3/train.log`.
Instances: 1 -- run3 logged `#2665 b859929d ci red=[]` and then spent merge
attempts 1/8 to 8/8 on "the base branch policy prohibits the merge" while
`pr-contract` was red at that head (job 120583698954, named in
`merge-report.txt` 18:32:27Z). The mechanism is in the tree:
`Train.one` and `Train.batch` call `self.required()` with its default
`pr_head=False` (`rg -n 'self\.required\(\)' tools/audit/seat/merge_train.py`),
which drops `PR_ONLY` -- `closure-scope`, `pr-contract`, `budget-raise-gate` --
so `at_head`'s wait never judges those three at a pull request's head; only the
CLI's `classify` passes `pr_head` (`rg -n 'pr_head=' tools/audit/seat/*.py`).
The comment above `PR_ONLY` asserts each is "green at every head the batch
admits", which nothing checks at the recarried head.
Cost: S -- `pr_head=True` on the head waits, one fixture row (a red
`pr-contract` at the head stops the car at `ci`, naming it) with its null
control (the same row green merges), one mutant, in `merge_train.py`, which
this group already edits for carries 1 and 2.
Binding: a train that reads a red head green spends its retries blind (8 x the
30 s sleep, then a SKIP naming no cause) and the run's rc 1; the defect is owed
under policy, and carries 1 and 2 (park on "base branch policy prohibits" with
the reason read from `statusCheckRollup`) are its diagnostic half, so one fixer
takes both.

## P35: a fetch's transient `cannot lock ref` kills the state beat and refuses roster ops
Verdict: ACCEPT -> R10-ORCH-ROSTER-SCHEMA (new carry)
Source: s5 item B.
Instances: 3 in one afternoon, each `error: cannot lock ref
'refs/remotes/origin/train-hold'` from a fetch in the shared orchestrator
checkout while a train refreshed that ref: `state-beat.log` line 149 (the
beat's traceback through `roster_sync.sync` -> `roster_edit.fetch_origin`;
the beat's last push before it was `aca3086a5`, 17:32:37Z, and it ran again
only as pid 31011 at 18:01:04Z, the 17:57:14Z restart refused on its own
argument); `roster-report.txt` line 15 (17:10Z, an `append-carry` for
R10-PARAMS-OWNER refused); `wt-sync.log` line 22277 (the wt_sync loop, which
survives it). Count: `rg -c 'cannot lock ref'` over the three files.
Cost: S -- one bounded retry (2 attempts, about 2 s apart) in
`roster_edit.fetch_origin`, keyed on git's `cannot lock ref` text only, which
every caller (roster ops, `roster_sync`, `state_docs.py beat`) inherits; one
self-test row with its null control (any other fetch failure still refuses at
once) and one mutant. No API call, no standing CPU.
Binding: the race recurs whenever a train runs (`merge_train.py` refreshes the
train-hold ref on every wait, at most `HEARTBEAT_SECONDS` apart) and each hit
costs a dead beat with its records missed until a hand restart, or a refused
roster op; the retry is a few lines in a file this group already edits (carries
3 and 5). The beat surviving a failed pass is R10-ORCH-BEATD's supervisor
(carry 0, item 0), not this carry.

## P36: `--free-holders` does not free a clean holder whose HEAD is an ancestor of the branch tip
Verdict: DEFER -> owned at the source by R10-FLY-OPENPR-ATOMIC (carry 1) and R10-UPDATE-PR-SIGNALS (carry 2)
Source: s5 item C.
Instances: 1 of the proposed shape -- run3 parked #2669 on the opener worktree
`~/.local/state/hpo/pr/r10-policy-lint-family/wt`, clean at `48dbc2c8`, an
ancestor of origin `8734cdd1` after the bot's `ci: merge main`
(`merge-report.txt` 17:51:06Z; `train/run3/skipped.json`). `freeable` requires
HEAD exactly `origin/<br>` (`rg -n 'def freeable' -A14 tools/audit/seat/merge_train.py`).
The second case is not this shape: run5's holder `train/run4/wt/2664` sat at
the origin tip with 42 tracked deletions (`merge-report.txt` 18:45:43Z;
`train/run5/skipped.json`), a dirty worktree `freeable` must refuse; it was left
by a train stopped by hand mid-run.
Cost: about 3 lines in `freeable` and a fixture row, in a hot file.
Binding: the holder exists only because an opener leaves its worktree on the
branch, which carry 1 of R10-FLY-OPENPR-ATOMIC and carry 2 of
R10-UPDATE-PR-SIGNALS remove at the source; once they land there is no holder
to widen the rule for. What would change it: a second ancestor-holder park
after those groups land, or a holder of this shape left by a train itself.

## P37: replan.py crashes on roster size XS
Verdict: DEFER -> owned by R10-FLOW-TOOLKIT-MODEL (carry 6) -- not a proposal: defect, ruled as `s5-batch1.md#P23`
Source: s5 item D.
Instances: still live at the base: `jq -c .sizes_hours tools/plan/durations.json`
holds L, M, S, XL; `tools/plan/replan.py` line 325 indexes it with no fallback;
`jq '[.groups[] | select(.size=="XS" and .resume.stage!="done")] | length'` over
the roster counts the open XS groups. `tools/audit/seat/roster_edit.py` has no
size check (`rg -n -i size tools/audit/seat/roster_edit.py`).
Cost: owned there.
Binding: carry 6 already requires a measured XS value and a loud line or
refusal for any size outside the table, which covers what an edit-time size
check in `roster_edit.py` would add; no unattended path runs replan
(`rg -n replan tools/audit/seat/state_docs.py tools/audit/seat/tick_loop.sh`
is empty), so carry 6's fly-in trigger has not fired.

## P38: replan.py schedules merge-verdicted, queued groups as fixer work
Verdict: REJECT
Source: s5 item E.
Instances: 1 plan -- `plan.json` (generated 2026-10-23 about 18:58Z) puts
R10-FLY-RELAY-REVIEW-FF and R10-POLICY-LINT-FAMILY in its final batch
(`jq -c '.batches[-1]' plan.json`), whose finish is the plan's closure
(`jq -c .summary.closure plan.json`), against the batch before it at 11:10Z
(`jq -c '.batches[-2]' plan.json`). The cause: both were `in-progress`, the
slot cap admits only the six highest live groups at the replan instant
(`replan.py` step 1, `live_pending`), and the rest queue by height, so a leaf
goes last. Both merged within the hour (`merge-report.txt` 19:13:25Z and
19:39:36Z).
Cost: a "merge-queued" stage in the classified stage set (every
`DONE_STAGES`/`LIVE_STAGES` reader, R10-ORCH-ROSTER-SCHEMA's carry 3), or a
verdict-ref read in replan.py.
Binding: the error is about 2.4 h on one plan's closure figure, gone at the
next replan after the merge, and no dispatch decision was taken on it; a stage
change touching every stage reader is not clearly cheaper than that. Reopen if
a dispatch or hold is shown taken on a misplaced merge-queued group.

## P39: warn when a diff voids the main-state exemption and the body does not name the reporter
Verdict: REJECT
Source: s5 item F.
Instances: 1 -- #2665's body said `none` and `pr-contract` refused it at
`b859929d` (job 120583698954) because its diff touches
`.github/workflows/tests.yml`, a `REPORTER_INPUTS` path
(`rg -n 'REPORTER_INPUTS' tools/policy/policy_lint.mjs`). The diff property
the warning would key on is common: 28 of the 283 first-parent merges on
origin/main since 2026-10-16 touched a reporter input
(`for m in $(git log origin/main --first-parent --merges --since=2026-10-16 --format=%H); do git diff --name-only $m^1 $m | rg -q -x 'tests/(delivery|nightly)_status.py|\.github/workflows/(tests|governance|nightly)\.yml|dev/programme/(HANDOVER|plan-2026-09-open-issues)\.md' && echo $m; done | wc -l`).
Cost: a warning line in `policy_lint.mjs --pr-body` plus a fixture row, read
and answered on every such diff.
Binding: the red depends on main's state at CI time, so a diff-only warning
fires on about one pull request in ten for one known red. The exact detector
exists: `policy_lint.mjs --pr-body` with `--red`, fed by prepr step 7c and by
`body_patch.sh`, refuses the body once the red exists. #2665's red was first
met by the train at a recarried head, where P34's fix stops the car at `ci`
naming `pr-contract`.

## P40: `bus.sh push-verdict` runs the carry audit over the verdict
Verdict: ACCEPT -> R10-FLY-CARRY-DISPOSITION (new carry)
Source: s5 item G.
Instances: 1 direct, costing two parks -- #2670's merge verdict, review
comment 6371729358, held 2 finding items with no valid `Carry:` marker; run4
parked it at pre-flight (`merge-report.txt` 18:34:32Z) and run6 again after
the verdict was re-taken (19:15:31Z), cured only by an owner-approved approver
PATCH (`patch-6371729358/`). The class precedes it: this group's brief counts
four markers-only re-reads (#2547, #2580, #2578, #2569). `push_verdict` in
`tools/audit/seat/bus.sh` checks grammar, nonce, evidence and dispatch binding
and never calls `carry_audit.py` (`rg -n carry_audit tools/audit/seat/bus.sh`
is empty).
Cost: S -- about 10 lines in `push_verdict` (write the verdict as a one-comment
`--comments` file and run `carry_audit.py --roster-ref
origin/handoff/audit-r10-roster check`, refusing on rc 1 with the unrouted
item ids), one self-test arm with its null control (the same verdict with its
markers pushes), one mutant; local git only, about 1 s per verdict push, no
API call.
Binding: an unrouted verdict item is caught today only at the train's
pre-flight or by `pr-contract`, after the reviewer seat has ended, and each
costs a park, a verdict re-take or a hand PATCH; the check that would refuse it
already exists and runs offline. This group already edits `bus.sh` (carry 0)
and `carry_audit.py` (carry 3).

## P41: `carry_audit pr` audits superseded verdicts; no tool edits an approver comment
Verdict: DEFER -> owned by R10-FLY-CARRY-DISPOSITION (brief)
Source: s5 item H.
Instances: 1 -- after #2670's verdict was re-taken as comment 6372641454,
`carry_audit.py pr 2670` still reported the superseded comment 6371729358's 2
items unrouted, which parked run6 (`merge-report.txt` 19:15:31Z).
`finding_rows` reads every comment matching `VERDICT`
(`rg -n 'def finding_rows' -A10 tools/audit/carry_audit.py`). The cure was a
one-off approver-token PATCH, its before and after in `patch-6371729358/`
(`wc -c orig.md new.md`).
Cost: owned there.
Binding: the brief of R10-FLY-CARRY-DISPOSITION already lets the orchestrator
add `Carry: dismissed: <reason>` or `Carry: <group>` under its own identity,
keyed to the verdict's head and read back, which routes an old verdict's item
without editing that verdict. The proposal's other arm, skipping a superseded
verdict, is refused: finding-propagation.md requires every finding a verdict
records to name its destination, and a re-take that drops an item would lose
it silently, the lost-ask class this group's carry 1 records. P40 removes the
source.
