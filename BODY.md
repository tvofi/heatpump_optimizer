R10-TRAIN-OVERLAP-GRADE part 3 (#2725), parts (1) and (2) of the brief: carries 1, 2, 3, 11b, 15 (refusal handling) and 13, 18 (record-PR sweep) in `tools/audit/seat/merge_train.py`. Part (3), carries 7 and 10, is the remainder (`## Forward-carry`).

What the train does differently:

- **Policy refusal (carries 1, 2, 3; #2577, P4 s4).** On "the base branch policy prohibits the merge", `Train.policy_refusal` reads `gh pr view --json mergeStateStatus,reviewDecision,statusCheckRollup` against the head's required contexts. The whole refusal and the read reason are logged. A required context still pending, or a state it cannot read, retries as before. A red required context, a missing review, or BLOCKED with every required context green **parks** the car with `[BRANCH-POLICY]` and that reason after that attempt. The text starts `not merged after <k> attempt(s)`, so `at_head`'s #2290 recovery still recarries one whose head main has moved past.
- **Approval carry widened (carry 2, step 2).** A refusal an approval can answer (REVIEW_REQUIRED, or BLOCKED with every required context green) is offered, once, to `_carry_owner_approval`. Its conditions are unchanged: `--approval-carry`, a clean recarry, no branch-own file in h0..h, a prior owner APPROVED review citing one mandate, the mandate re-read in force at the merge, and a byte-identical read-back. Each refusal now leaves its reason in `item["carry_refused"]`, and the park names it.
- **P34 (carry 3).** The head wait reads the required set with `pr_head=True` inside `Train.serial`, the one path every serial head wait goes through (`one`, `one_overlap`, the batch's serial entries). The `req` parameter of `one` and `one_overlap` is gone, so no caller can hand a head wait main's set. This replaced a first cut that passed a second variable from `_batch`. That cut's mutant survived (`## Mutation proof`, M11), and the seam is the better fix (fixer.md step 17). At the merge base `PR_ONLY` is `()` (9262e6f43, the umbrella `gate`), and `gate.py` `REQUIRED["pr"]` holds `pr-contract`. So on today's ruleset a red pr-contract already reads as a red `gate`. This change makes the head wait independent of what `PR_ONLY` holds.
- **P231 (carry 15).** `sweep_bots` keeps `gh pr merge`'s output. A refused record PR now logs `BOT #<n> not merged at <h8> (<state>) refused: <gh's last non-empty line, up to 200 chars>`. `sweep_bots` returns the merged PR's number, else None.
- **P191 (carry 18).** After a refused attempt that is not BASE_MOVED, under `--bot-prs`, `land` sweeps once per landing. A record PR merged there raises `MainMoved('merge', 'the record PR #N merged under the batch')`, which the existing recovery recarries. No sweep runs on beats, and `add` still refuses the record branch.
- **P289 (carry 13).** A critical-path entry skips the sweep before its recarry, and `serial` sweeps after its merge (or when it stops). A batch holding one skips the sweep before reading its base and sweeps after its merges, before its serial entries. Critical path = `roster_lib.group_for_branch` on the entry's branch, checked against `roster_lib.critical_path_groups` at `roster_lib.reader_ref`, read once per run. Anything unread is nothing critical, which is today's order. `Train(critical=...)` takes a fixture reader, and both self-test drivers default it to "nothing critical", so no fixture reads the live roster.
- **P184 (b) (carry 11b).** `freeable` frees a clean holder whose HEAD is origin/<branch> or an ancestor of it (`git -C <holder> merge-base --is-ancestor`). A HEAD with commits origin lacks refuses with `has commits origin does not have`. HEAD or origin unreadable refuses as before. Keyed on commits, never a path.
- **P184's second caller, `queue_pre_flight` (round 2).** `PreFlight.worktree_holder` calls `Train.freeable` under the train's `--free-holders`. Its self-test stub answered every `merge-base` argv rc 0, so the new ancestor probe read the unpushed holder (HEAD 1.., origin 2..) as behind origin and passed it. The stub now answers `--is-ancestor` rc 1 unless the world says `behind`. A twin arm pins that a clean holder behind origin/<branch> passes, mirroring merge_train's P184 pair. The module docstring's `worktree` line now says `or an ancestor of it`.
- **Three policy survivors pinned (round 2).** The fix review's new survivors each get an arm in `merge_train`'s self-test. (a) A second approval-class refusal after a carried approval parks after attempt 2 with exactly one `approved (carry)` line. (b) A required context reading SKIPPED, or NEUTRAL, with a missing review parks at once as green rather than pending. (c) `--ignore`'d `nightly-status`, required and red, parks nothing: the running `fast` waits and the next attempt merges.

Alternatives not taken: a separate approval path for the policy class. It lost because carry 2 says to widen the existing carry under the same conditions, and a second path would be a second writer of the concept (fixer.md step 17). Parking on every policy refusal lost too: the pending-check case is the review-run race `review_settle` exists for (P86), and parking there would stop entries that merge one attempt later.

Closes nothing: #2725 stays open for part (3).

## Head

Measured at ee438e5d173eac96f8ded452b1fa80fcc1f6bcad, pushed to `handoff/r10-train-overlap-grade-p3`. It is one commit on the round-1 live head e456ff01323580d4390f964483a17dbdb6cff5bf. The merge base is 507a9ec264eb373b132248d752259254d8a9fa4d. origin/main was e77418f9b48f89421bd72b0ab511c057341c7fa4 at 2026-10-30 13:56Z, and `git merge-tree --write-tree origin/main HEAD` exits 0 there, so main was not merged (fixer.md step 6).

## Mutation proof

Each mutant is applied to a copy of the head's `merge_train.py` beside it, by an exact single-occurrence string replace, then `python3 <copy> --self-test` is run (driver: `$SCRATCH/mut.py`, a one-off probe, not in the tree). Every arm's mutant is the base's behaviour at that site.

- M1, policy park off (`if BRANCH_POLICY_SAID.search(said):` -> `if False:`, the base's loop): 7 failed. These are `policy refusal with a required context red ...`, `... still running waits ...`, `... missing review, no --approval-carry ...`, `carry 2: a policy refusal ... answered by the approval carry ...`, and the three `carry 2 null (...)` arms.
- M2, carry delta check dropped (`if own:` -> `if False:`): 2 failed, `approval-carry MUTATION (the diff-empty check)` and `carry 2 null (names branch-own)`.
- M3, live mandate read dropped (`if not live:` -> `if False:`): 2 failed, `approval-carry MUTATION (the mandate in-force check)` and `carry 2 null (is not in force at the merge)`.
- M4, park's carry off (`if approval and not carried:` -> `if False:`): 5 failed, the four `carry 2` arms and `... missing review, no --approval-carry ...`.
- M5, P231 text dropped from the BOT line: 1 failed, `P231: a record PR GitHub refuses logs ...`.
- M6, P191 sweep dropped (`bot = self.sweep_bots()` -> `bot = None`): 3 failed, `P191: a refused attempt with a record PR now green ...` and both `P191 null (...)` arms (they count the sweep).
- M7, P289 skip off (`if self.bot_prs and self.critical(item):` -> `if False:`): 2 failed, `P289 serial: a critical-path #7 merges, then the record PR, then #8` and `P289 serial, a critical-path entry alone ...`.
- M7b, the brief's mutation, skipping the sweep for every entry (`-> if self.bot_prs:`): 4 failed, among them `P289 serial: null, nothing critical: the record PR merges FIRST, as today` and the existing `--bot-prs: the open record PR ... merges FIRST`.
- M8, P289 batch (`cp = ...` -> `cp = False`): 1 failed, `P289 batch: with a critical-path entry the proof is built without the record PR ...`.
- M9, P34 (`req = self.required(pr_head=True)` in `serial` -> `self.required()`): 1 failed, `P34: pr-contract failure at the head (stops at ci naming it, no merge attempt)`.
- M10, P184 ancestor (`if here != there and not self.ok(... --is-ancestor ...):` -> `if here != there:`): 1 failed, `P184 --free-holders: a clean holder whose HEAD is an ancestor of origin/<branch> is freed ...`.
- M12, P289 post-merge sweep dropped: 1 failed, `P289 serial, a critical-path entry alone: the record PR still merges, after it`. With two entries, the next entry's recarry sweep masks this mutant, which is why the single-entry arm exists.
- S1, round 2 (`if approval and not carried:` -> `if approval:`): 1 failed, `carry 2: a second policy refusal after a carried approval parks without a second carry`.
- S2, round 2 (the green set `("SUCCESS", "SKIPPED", "NEUTRAL")` -> `("SUCCESS",)`): 2 failed, `policy refusal with the required context SKIPPED ...` and `... NEUTRAL ...`.
- S3, round 2 (`n not in self.ignore and ` dropped from `red`): 1 failed, `policy refusal null (--ignore): an ignored red required context parks nothing; ...`.
- Q1, round 2: queue_pre_flight's `--is-ancestor` stub is removed, which restores the round-1 fixture. Run with `python3 tools/audit/seat/queue_pre_flight.py --self-test`: `44 checks, 1 failed`, `... and one whose HEAD is not origin/<branch> still PARKs (unpushed work)`. This is the CI red, reproduced.
- Q2, round 2: M10 is applied to `merge_train.py`, then queue_pre_flight's self-test is run: `44 checks, 1 failed`, `... and one whose HEAD is an ancestor of origin/<branch> passes (P184: nothing origin lacks)`. The new twin arm reads `freeable`'s ancestor probe through the second caller.
- M11, from the first cut (`head_req = self.required(pr_head=True)` in `_batch` -> `head_req = req`): **survived**, 0 failed. Answered by removing the variable: the head set is now read in `serial` itself, where M9 kills it for the batch's serial entries too.

Baseline for every mutant: the unmutated head. It prints `merge_train self-test: 380 checks, 0 failed` and `queue_pre_flight self-test: 44 checks, 0 failed`. M1-M12 were run in round 1 against the 376-check head, and the fix reviewer re-ran them at e456ff01. Round 2 re-ran M10 at this head: 380 checks, 1 failed.

## Null control

- Policy: an unreadable merge state retries three times and stops `[BRANCH-POLICY] not merged after 3 attempts`, as today (`policy refusal null: ...`). The pre-existing `every refused merge attempt is logged ...`, `#2290 shape` and `... while the same refusals on a head that still contains main stop as before` arms pass unchanged.
- Carry: the three null worlds (a conflict-resolution delta, a prior review by the `hpo-approver` App, a mandate past its window) each park after one attempt naming their reason, with no `approved (carry)` line.
- P34: the same car with pr-contract green merges.
- P231: the existing `--bot-prs ... merges FIRST` arm still logs `BOT #9 MERGED`.
- P191: no open record PR (lookup 0), and a record PR still pending, each run three refused attempts with no MAIN-MOVED. Pending logs `BOT #9 pending` twice. Without `--bot-prs` nothing is looked up.
- P289: nothing critical merges the record PR first, serial and batch (the existing batch arm `batch --bot-prs: the record PR merges before the base is read` passes unchanged).
- P184: a holder at origin's tip is freed as today. A holder ahead of origin refuses. Without `--free-holders` nothing is detached. In queue_pre_flight the same three worlds hold: at origin's tip it passes, ahead of origin it PARKs, and without `--free-holders` the holder PARKs.
- S3's arm is itself a null control. Nothing red at the head parks, and the arm fails exactly when the ignore filter is dropped.

## Figures

- Self-test, merge_train: `python3 tools/audit/seat/merge_train.py --self-test` prints `merge_train self-test: 380 checks, 0 failed` at the head. In a worktree at the merge base 507a9ec2 the same command prints `merge_train self-test: 355 checks, 0 failed`. At round 1's head e456ff01 it prints `376 checks, 0 failed`. The difference is checks executed, not call sites. `git diff 507a9ec2... HEAD -- tools/audit/seat/merge_train.py | grep -c '^+.*check('` prints 19 call sites, and some of them sit in loops.
- Self-test, queue_pre_flight: `python3 tools/audit/seat/queue_pre_flight.py --self-test` prints `queue_pre_flight self-test: 44 checks, 0 failed` at the head. At e456ff01 it prints `43 checks, 1 failed`, the CI red. At the merge base 507a9ec2 it prints `43 checks, 0 failed`. The same diff command on this file prints 1 added call site.
- Gate scope: `python3 tests/closure.py select --diff 507a9ec264eb373b132248d752259254d8a9fa4d --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. It names `tests/entities.py`, and the 4 changed files are listed. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2484 ENTITY CHECKS PASSED`.
- `run_always` lines: `python3 tests/env_drift.py --claims-only 507a9ec2...` exits 0, `python3 tests/closure.py selftest` exits 0 and `python3 tests/layout.py` exits 0. `python3 tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. Every metric is within budget and none was re-recorded.
- `python3 tools/audit/archscore/score.py --diff 507a9ec264eb373b132248d752259254d8a9fa4d` prints `Architecture score: dS +0.0000 NULL`. The diff reaches no file the score reads, so no gain is claimed.
- Class rule, step 8. The instances are train logs on the orchestrator's host, not in the tree, so there is no finder harness to re-run, and the self-test fixtures model each instance. Let E be the line of `def _self_test` in merge_train.py.
  - Merge sites: `awk 'NR<E && /"gh", "pr", "merge"/' tools/audit/seat/merge_train.py` lists every production site that merges a pull request, and returns 2. `land`'s loop is closed in this diff (carries 1-3, 18). `sweep_bots` is closed (carry 15).
  - Head-set reads: `awk 'NR<E && /\.required\(/'` returns 3 sites. `serial` reads pr_head=True, closed here. `policy_refusal` reads pr_head=True, new. `_batch` reads main's set for `main_green`, `admit` and `settle`. `admit` is the distinct seam carried below. The CLI's `t.required(pr_head=not a.main)` in `main` is already right.
  - Sweeps: `awk 'NR<E && /self\.sweep_bots\(\)/'` returns 6 sites. `recarry` and `_batch`'s pre-base sweep are closed (P289 skip). Four are new: `serial` after the merge, `serial` on a stop, `_batch` after the merges, and `land` on refusal (P191).
  - P184, every caller of `Train.freeable`: `git grep -n '\.freeable(' -- tools tests dev` returns 2 sites. `Train.free_holder` in merge_train.py is closed in round 1, with the P184 pair. `PreFlight.worktree_holder` in queue_pre_flight.py is closed in round 2: its fixture answers the probe, and the twin arm pins the ancestor pass (Q2 kills it). This is the round-2 block's class. Its null control is the round-1 body: the same rule there would have returned the queue_pre_flight site undispositioned.

## Red checks

- `governance / instrument-self-tests` was red at e456ff01, job 124070275423: `queue_pre_flight self-test: 43 checks, 1 failed`. This diff caused it. Round 1 added the `--is-ancestor` probe to `Train.freeable`. queue_pre_flight, its second caller, has a fixture that answered every `merge-base` argv rc 0, so the unpushed-holder arm passed instead of parking.
  - Answer: the fixture now answers the probe, and a twin arm was added. At this head the self-test prints `44 checks, 0 failed`.
  - The cheaper detector exists: `python3 tools/audit/seat/queue_pre_flight.py --self-test`, which takes seconds locally. Round 1 ran only merge_train's self-test, and the class rule listed no caller of `freeable`. Its standing cost is one more self-test per edit to a shared `Train` method.
  - The P184 line in `## Figures` now enumerates every caller (`git grep -n '\.freeable('`), so a third caller is listed by the rule rather than found by CI. The analysis is `root-cause.md`'s seat, not this one.

## Forward-carry

- Part (3) of the brief, carries 7 (`add --front` / `add --remove` under `QUEUE_LOCK`, P112) and 10 (`stats`, and `--cap auto` only past 0.5 h/day lost, P164), is not built here. Reason: carry 10's `--cap auto` decision needs the train logs, and no train log is in the tree or reachable from this container (`git ls-files | grep -iE 'train[^/]*\.log|queue-add|skipped\.json'` prints nothing). The fixer.md rotation bound also applies. The two carries stay in the group's roster entry on `handoff/audit-r10-roster` as written. Carry: R10-TRAIN-OVERLAP-GRADE
- `_batch` admission reads a PR head's CI with main's required set (`self.required()`, no `pr_head`). It is the P34 class's sibling seam, latent while `PR_ONLY` is `()`. A future non-empty `PR_ONLY` would admit a head whose PR-only context is red. Control: the M9 arm's world (`PR_ONLY=("pr-contract",)`, pr-contract red) driven through `batch` instead of the serial train. Carry: R10-TRAIN-OVERLAP-GRADE
- Round-2 survivors. All three new survivors (S1-S3) are pinned here, so none is carried. The round-1 survivors R3, R5, R8 and R9 remain in carry 21 at `handoff/audit-r10-roster` 78c0bb77, as the fix review confirmed. Carry: R10-TRAIN-OVERLAP-GRADE
- Carry 2's last sentence, "pass --approval-carry in the live launch", is the orchestrator's launch line, not this file. Without the flag every approval-class policy refusal parks naming `--approval-carry or --mandate is not given`. Carry: R10-TRAIN-OVERLAP-GRADE

## Friction

- fixer.md-step-3: unclear: the carries' instances (train17, train27, s41, s44, #2665 run3) are train logs on the orchestrator's host, so "re-execute the finder's harness" has no harness to run. The self-test fixtures model each instance instead. Carry: dismissed: no finder harness exists for instrument carries; the fixtures are the measurement
