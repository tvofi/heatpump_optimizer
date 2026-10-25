# Proposal triage, session s6, batch 29 (P158-P167)

Proposals from the s6 `proposals.md`. Numbering continues after `s6-batch28.md` (P150-P157). This batch holds 8-10 entries and merges only through the train queue (tvofi, 2026-10-25). V79-V103 are 25 tvofi-accepted ideas (throughput T, first-pass yield F, quality Q); they are ruled across batches 29-31, ordered by round-10 closure time saved, and round-11 items are recorded in R10-ROUND-PLAYBOOK as batch 28 did. Facts read at origin/main dfcd8d9be and roster 63d8938eb.

Most of the dispatch-side carries below (P159-P161, with P140, P144, P146 and P149 of batch 27) land on R10-FLOW-DESIGN-STAGES, the owner of `cloud_dispatch.py`, the dispatch templates and the absorbed pool instrument (its carry 10). This group's fixer cuts them as one release-and-pool sub-PR, separate from the design-stage work, and the orchestrator resizes the group M -> L once the `set-size` op (P139) exists.

Round-1 re-cut (verdict 6402371947, 2026-10-25): an unmeasured benefit is DEFER, never ACCEPT. P158 and P163 are ACCEPT as trials, each with a measurement and a removal criterion. P164 is ACCEPT measure-first. P159-P162 and P165-P167 are DEFER.

A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P158: CodeQL on the train's batch proofs is the measured bottleneck (orchestrator measurement, folded into S6-V79 and V81)
Verdict: ACCEPT as a trial -> new group R10-PROOF-CODEQL (S, no after-edges; files `tools/pr/codeql_scope.py`, `tools/ci/prelude.py`). A train batch proof stops waiting on a CodeQL leg that every entry's own PR head already judged. The trial is measured, with a removal criterion: proof wall time over the next three batches, against the orchestrator's measured s41 instance. The skip is reverted if CodeQL's tail beyond the other checks was under 5 min.
- Running CodeQL only nightly on main would break the rule that main keeps a full analysis of every merged tree (`codeql_scope.py:29-31`).
- Caching by closure is what PR-head scoping already does: its docstring records that 76 of the 144 pull requests merged in round 10 skipped (`codeql_scope.py:19`). The general cache is round-11 P153.

No open group owns `codeql_scope.py` or `prelude.py`. The CI-layout groups are done, and R10-FLY-ROW-HEAD-CARRY holds only `codeql.yml`, behind three after-groups. So this is a new group.
Source: the orchestrator's measurement relayed for V79/V81/V74 (2026-10-25).
- `codeql / Analyze (python)` runs about 28-30 min and gates `gate` on every batch proof.
- It held s41's batch-1 proof at 2ac575d0, every other check green by about 18:55Z, and #2811's head earlier.

Instances: read at origin/main dfcd8d9be.
- A batch proof is a push to `batch/<tag>-<n>` (`merge_train.py:5435`).
- The prelude gives every push full scope (`prelude.py:226`) and the full CodeQL workset (self-test `prelude.py:343-344`).
- `codeql_scope.py`'s rule is that only `pull_request` may skip, and a push always analyzes (`:29-31`).
- `gate` needs `[prelude, pr-contract]` (`ci.yml:301-302`), and `pr-contract` needs `codeql` (`ci.yml:254`), so the gate waits on CodeQL transitively.

So each proof re-analyzes in full a tree whose entries were each analyzed at their own heads.
Cost: S.
- In `codeql_scope.decide`, a push to a ref under `batch/` skips a leg when every entry head the proof merges has a successful (or legitimately skipped) analysis of that leg at that head. It uploads the stand-in category exactly as a skipped PR leg does.
- The train names the entry heads in the proof commit, or the decision reads them from the proof's parents.
- Any doubt analyzes: an unreadable head list, an entry with no analysis, or a file under `.github/`. Pushes to main are unchanged and always analyze in full.
- This revises an owner design rule (DESIGN-P2 D-5's push arm) for proof refs only. It is approved under mandate 6329234399 and stated in the body.

Binding: the proof exists to show the combined tree passes the gate. A CodeQL alert that only the combination can create is a cross-entry dataflow, which is rare. Main's full push analysis catches it one merge later, as it already does for every PR leg skipped today.
Closure saving: about 1.5 h if the trial confirms the s41 tail; not claimed before. Basis: about 7 critical-path merges, each behind one batch proof, x CodeQL's tail beyond the other checks. Taken as about 12 min from the s41 instance: the proof went green on everything else by about 18:55Z while a 28-30 min analysis ran on. Throughput gains on the other merges come on top. Re-measure the proof's wall time before and after.

New group (for `roster_edit.py append-group`, citing `triage: dev/programme/triage/s6-batch29.md#P158`): R10-PROOF-CODEQL, lane IN, kind instrument, class instrument, severity medium, size S, files `tools/pr/codeql_scope.py` and `tools/ci/prelude.py`, after none, fixer and reviewer opus at medium effort. Brief: "GROUP R10-PROOF-CODEQL (new, size S, triage: dev/programme/triage/s6-batch29.md#P158). A train batch proof (a push to `batch/<tag>-<n>`, `merge_train.py`) analyzes every CodeQL leg in full (`prelude.py` gives a push full scope; `codeql_scope.py` lets only `pull_request` skip; `gate` waits on it through `pr-contract`), and the python leg's 28-30 min held the 2026-10-25 s41 batch-1 proof after every other check was green. Change: `codeql_scope.decide` lets a push to a `batch/` ref skip a leg when every entry head the proof merges has a successful or legitimately skipped analysis of that leg at that head, uploading the stand-in category as a skipped PR leg does. Fail closed: an unreadable entry list, an entry with no analysis at its head, or any changed file under `.github/` analyzes. Pushes to main and every other event keep analyzing in full (the rule that main keeps a full analysis of every merged tree is unchanged). This revises DESIGN-P2 D-5's push arm for proof refs only, under mandate 6329234399; say so in the body. Controls: a proof whose entries all analyzed python at their heads skips the python leg and uploads its category; one entry without an analysis analyzes it; a push to main analyzes every leg (null); a `.github/` change analyzes every leg; a mutant that skips on any push fails the main arm. Measure the proof's wall time before and after over at least three batches."

## P159: an expedite review lane with a measured time to claim (S6-V83)
Verdict: DEFER -> the pool module R10-FLOW-DESIGN-STAGES carries (its carries 10 and 11) owns the claim order. What would change the answer is the claim latency of critical-path reviewer lines against the others: dispatch-ref commit time to the matching fire line, split by critical path. In the P144 sample, 2 of the 5 long waits were on critical-path #2819, but nothing in the logs says whether queue order caused them. (Round-1 re-cut: the earlier ACCEPT asserted 4 min of queue position.)
Source: s6 `proposals.md` `## V83` (orchestrator, 2026-10-25, tvofi-accepted T7).
Instances: the pool module is not on main yet (`git ls-tree origin/main tools/audit/seat/` has no `pool.py`). The claim refs (`claim/s6/<topic>`) and dispatch refs (`dispatch/reviewer-<pr>-<sha8>`) carry the two timestamps that time-to-claim needs.
Cost: XS on top of the pool module. A `cp` flag on the POOL line comes from the plan's critical path, and claims take CP lines first. A `claim-age` report gives the dispatch-ref commit time to the claim-ref commit time, per line.
Binding: a reviewer that claims a non-critical line while a critical-path line waits costs the closure the whole wait.
Closure saving: not claimed (DEFER).


## P160: pace releases to the bottleneck stage (S6-V79)
Verdict: DEFER. What would change the answer is the depth over time of the two queues (handoffs owed an open, from the relay's `handoff-no-pr` level lines, and PRs owed a reviewer, from the ledger's REVIEW OWED), against the critical-path waits they caused. (Round-1 re-cut: the earlier ACCEPT asserted 0.5 h.)
- Narrowed because the queues are already measured. The relay folds every handoff with no PR into `handoff-no-pr` lines (`cloud_relay.sh:101-105`), and the ledger keeps reviewer-fire and dispatch events (`ledger.py:90-98`).
- The hourly bottleneck report becomes the release step's own reading of those queues, so no separate report is built.

Source: s6 `proposals.md` `## V79` (orchestrator, 2026-10-25, tvofi-accepted T1). Owner rules that bound it: critical-path groups start regardless of any cap (2026-10-22), and new groups wait for the open PRs to drain to about 5-6 (2026-10-21).
Instances: on 2026-10-25 fixers outran the openers and review, and handoffs waited up to 1 h (filing; plan-opt handoff-to-open median 0.99 h).
Cost: XS inside the release step. Before releasing a non-critical group, count the handoffs owed an open and the PRs owed a reviewer. Above a buffer (default 3 each), hold the release and print `HELD <group>: <stage> queue <n>`.
Binding: work released into a full queue only waits there and spends seat tokens. Critical-path releases are never held.
Closure saving: not claimed (DEFER).


## P161: Definition of Ready before a fixer dispatch (S6-V87)
Verdict: DEFER. What would change the answer is the count of blocked verdicts on groups whose brief named no controls or no files, by verdict id. (Round-1 re-cut, verdict 6402371947: the earlier ACCEPT's benefit was asserted, and its carried predicate did not re-derive.)
Source: s6 `proposals.md` `## V87` (orchestrator, 2026-10-25, tvofi-accepted F1).
Instances, measured on roster 63d8938eb, re-derived in round 1: of 54 groups not-started or queued, 4 have no whole word `\bcontrols?\b` (case-insensitive) in brief or carries. A substring rule (`controls`, or `control:`) refuses 14, because it misses wording such as 'Null control owed' (verdict 6402371947). The 4 are: R10-RCA-HEADMOVED, R10-FLOW-MQ-PROBE, R10-BRIEFS-FOLD-D0 and R10-REPLAY-REAL-DAY. 3 have an empty `files` list: R10-RCA-HEADMOVED, R10-CARD-VOICE and R10-LEARNER-DEFAULT. Carry rendering is P140.
Cost: XS. A `ready` check in the fixer dispatch: refuse when (a) `files` is empty, (b) no `Controls` appear in brief or carries, or (c) the render dropped a carry (P140's count check). A root-cause group (kind `rca`) would be exempt from (a) and (b). R10-RCA-HEADMOVED's kind is `study`, so it would not be exempt.
Binding: a fixer dispatched without controls or files invents them, and the reviewer then blocks on them.
Closure saving: none claimed. 4 of 54 groups match, all off the critical path, and no block has yet been attributed to the missing word.

Carry text (for `roster_edit.py append-carry R10-FLOW-DESIGN-STAGES`, citing `triage: dev/programme/triage/s6-batch29.md#P161`): "Definition of Ready (tvofi-accepted V87). Beside the brief item (3) refusal (no approved design verdict), the fixer dispatch refuses a group whose `files` list is empty, or whose brief and carries contain no `Controls` (case-insensitive, or `control:`), or whose rendered PROMPT.md holds fewer carries than the roster entry (P140). Groups of kind `rca` are exempt from the first two. Print `NOT READY <group>: <reason>`. On roster 63d8938eb this refuses R10-RCA-HEADMOVED (exempt if rca), R10-FLOW-MQ-PROBE, R10-BRIEFS-FOLD-D0, R10-REPLAY-REAL-DAY, R10-CARD-VOICE and R10-LEARNER-DEFAULT until fixed. Controls: one fixture per reason refuses; a ready fixture renders unchanged (null); a mutant that skips the carry count fails its arm."

## P162: a handoff that conflicts with main is refused before the PR exists (S6-V93)
Verdict: DEFER -> already enforced, and owned where it is not. A conflicting handoff never becomes a PR today: `open_pr.sh` runs under `pr_trap` (`open_pr.sh:15`; `pr_args.sh:32-35`, `set -Eeo pipefail` with an ERR report), so a conflicting `git merge -q --no-edit origin/main` (`open_pr.sh:48`) stops the script before `app_push.sh` creates the PR (`open_pr.sh:54-58`). The earlier carry's control was vacuous: line 48 stops that mutant too. #2817's DIRTY state came from main moving after the open (its head took main merges at 18:02 and 20:17 +0100, `refs/pull/2817/head`). The tick already flags that (`orchestrator_tick.py:844-848`, with `merge_train.dirty_repair`). (Round-1 re-cut, verdict 6402371947.)
- A fresh base at open is already enforced: `open_pr.sh` always merges origin/main (`open_pr.sh:6`, `:48`).
- DIRTY on an open PR is already flagged by the tick, with a repair suggestion (`orchestrator_tick.py:844-848`, `merge_train.dirty_repair`).
- The "within N minutes" freshness is narrowed to the conflict test, which is the real criterion: a clean merge-tree at open needs no time bound.
- What is left is that a conflicting handoff must never become a PR. This is the atomic-open seam.

Source: s6 `proposals.md` `## V93` (orchestrator, 2026-10-25, tvofi-accepted F9).
Instances: #2817 (R10-PARAMS-OWNER) arrived DIRTY (filing). Its mergeable state reads BLOCKED now, after a repair.
Cost: XS. Before `gh pr create`, run `git merge-tree --write-tree origin/main <handoff tip>`. On a conflict, refuse with the conflicted paths, write `handoff-conflict <topic> <sha>` for the relay, and create no PR. The cloud fixer prompt already tells the seat to merge main before its handoff.
Binding: a PR opened DIRTY spends a CI run and a reviewer on a head that must move.
Closure saving: none; the refusal is already enforced.


## P163: an andon on a stuck push run (S6-V84)
Verdict: ACCEPT as a trial -> R10-UPDATE-PR-SIGNALS (in-progress; its follow-on fixer `dispatch/fixer-r10-pusher-reap` owns stuck push runs). The line is report-only and is its own measurement. It is removed if it fires zero times over 48 h, because one filed instance (#2819, 20 min or more) is not a measured rate. The general SLO is already other groups' work:
- seat liveness: `pulse.py --seat-alive`, R10-ORCH-BEATD carries 15 and 21;
- the handoff-ahead and dead-relay alarms: BEATD carry 17;
- event ages: the ledger's aging, BEATD carry 8.

The instance the filing names is a push run that held its branch lock for 20 min or more. Nothing reports the lock's age.
Source: s6 `proposals.md` `## V84` (orchestrator, 2026-10-25, tvofi-accepted T8).
Instances: #2819's `update_pr.sh` was stuck for 20 min or more in a push check (filing). The per-branch lock is `pr_branch_lock` (`pr_args.sh:66`), held for the whole run (`update_pr.sh:35`, `open_pr.sh:34`).
Cost: XS. The lock records its start time. A run older than a bound (default 15 min) prints `STUCK <branch> <pid> <age>` on the relay's level, so the tick shows it. Nothing kills the run automatically; the reap path stays this group's.
Binding: a stuck pusher holds its branch and every update behind it, and today only a person notices.
Closure saving: not claimed until the trial counts STUCK lines.

Carry text (for `roster_edit.py append-carry R10-UPDATE-PR-SIGNALS`, citing `triage: dev/programme/triage/s6-batch29.md#P163`): "Lock-age andon (tvofi-accepted V84, narrowed to the push run). `pr_branch_lock` (`pr_args.sh:66`) writes its start epoch beside the pid. `cloud_relay.sh` reports any lock older than `HPO_PUSH_STUCK_SECS` (default 900) as `STUCK <branch> <pid> <age>s` on its level, where the tick reads it. It reports only, and the reap stays this group's. Seat and beat SLOs are R10-ORCH-BEATD's carries 8, 15, 17 and 21. Controls: a fixture lock aged 901 s is reported and one aged 899 s is not; a released lock is never reported; a mutant that reads the lock file's mtime instead of the recorded start fails a fixture whose file was touched later."

## P164: size train batches from the measured red rate (S6-V82)
Verdict: ACCEPT narrowed -> R10-TRAIN-OVERLAP-GRADE (queued, M; owns admission in `merge_train.py`, with P129). Narrowed to measure first. The batch proof already drops a red entry rather than stopping the batch (the drop is asserted at `merge_train.py:4655` and `:4659`; `:4876-4890` assert only no drop on a red main). A sizing rule is built only if the measured skip-and-retry cost justifies it.
Source: s6 `proposals.md` `## V82` (orchestrator, 2026-10-25, tvofi-accepted T6).
Instances: no per-batch red rate is recorded in the tree today. The filing gives none.
Cost: XS to measure: from the train logs, p(red) per entry and per batch, and the time lost to drop-and-retry. S to build, conditionally: a batch cap from p(red), the largest n with (1-p)^n of at least 0.5.
Binding: with no measurement, any cap is a guess. With it, the cap is arithmetic.
Closure saving: about 0.3 h, estimated until measured.

Carry text (for `roster_edit.py append-carry R10-TRAIN-OVERLAP-GRADE`, citing `triage: dev/programme/triage/s6-batch29.md#P164`): "Batch size from the red rate (tvofi-accepted V82, measure first). Add a `merge_train.py stats` reading of the train logs: entries and batches, p(red) per entry, dropped entries, and wall time lost to drop-and-retry, over a window. Only if the lost time exceeds 0.5 h per day, add `--cap auto`: the largest n with (1-p)^n >= 0.5, bounded by the existing cap. Controls: a fixture log with 2 red entries in 10 prints p=0.2; `--cap auto` at p=0.2 gives 3 ((0.8)^3 = 0.51); a mutant that inverts p fails."

## P165: D15 bundles as a replay corpus (S6-V97)
Verdict: DEFER -> owned by R10-REPLAY-REAL-DAY, which builds the one-real-day fixture from the round's only D15 bundle. A corpus needs a second bundle and a measured catch from the first. What would change the answer is the count of bundles held and the defects the one-day fixture catches. (Round-1 re-cut: the earlier ACCEPT's benefit was unmeasured.)
Source: s6 `proposals.md` `## V97` (orchestrator, 2026-10-25, tvofi-accepted Q3, "design seat").
Instances: the group's brief states that #2272's headline item, a real recorded day as a nightly-gated replay fixture, never landed. Round 10 holds one D15 bundle (the owner install, leads L1-L9).
Cost: XS on top of the group: the fixture loader takes a directory of redacted bundles. The design-seat marking applies to the opt-in half, which is not built here.
Binding: each real bundle is a regression fixture the synthetic suites cannot write.
Closure saving: 0 h (quality, off the critical path).


## P166: safety invariants and fault injection (S6-V102)
Verdict: DEFER -> owned by R10-LEGIONELLA-COMPLETION (queued), whose brief point (3) establishes that an overdue cycle is loud. The rest is landed (stale sensors: R10-INPUT-STALENESS, #2683; DST: `tests/dst_checks.py`) or unmeasured. (Round-1 re-cut, verdict 6402371947: an item an existing group owns is DEFER naming it, as `s5-batch1.md` does.)
- Stale sensors: R10-INPUT-STALENESS, #2683.
- DST and clock handling: `tests/dst_checks.py`.
- The comfort-floor alert and API-outage injection: round-11, D1 robustness and D8 sensors.

Source: s6 `proposals.md` `## V102` (orchestrator, 2026-10-25, tvofi-accepted Q9).
Instances: legionella last completion about 66 days before export against a 7-day interval (D15 lead L8, in that group's brief).
Cost: none new in round 10.
Binding: the one safety instance with evidence already has an owner. A fault-injection framework without a measured failure is round-11 audit scope.
Closure saving: 0 h.

## P167: one pipeline event log with a live flow view (S6-V80)
Verdict: DEFER. What would change the answer is a measured gap between `replan.py`'s modelled stage durations and the actual waits, from the ledger and refs over a week. Building the flow log now would add a design step to R10-ORCH-LEDGER or R10-FLOW-TOOLKIT-MODEL, both on the critical path. (Round-1 re-cut: the earlier ACCEPT was a round-11 design item on an unmeasured benefit.)
- The ledger is that log in part: `ledger.py` keeps event kinds for reviewer-fire, verdict-unposted, approve-held-runs, dispatch, train-stop and postmerge-owed (`ledger.py:90-98`).
- The cumulative-flow view and `replan.py` using measured waits are new.
- Building them in round 10 would add a design step to R10-ORCH-LEDGER or R10-FLOW-TOOLKIT-MODEL, both on the critical path (plan v47), to improve the plan's accuracy rather than the closure.

Source: s6 `proposals.md` `## V80` (orchestrator, 2026-10-25, tvofi-accepted T2).
Instances: plan-opt measured the per-stage waits offline (`bin/cycle.py`) and found them; nothing in the tree derives them live.
Cost: M plus a design step.
Binding: no round-10 closure gain, and a cost on the critical path. Closure saving: 0 h in round 10.

