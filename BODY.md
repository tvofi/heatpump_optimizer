R10-TRAIN-OVERLAP-GRADE part 3 (#2725), parts (1) and (2) of the brief: carries 1, 2, 3, 11b, 15 (refusal handling) and 13, 18 (record-PR sweep) in `tools/audit/seat/merge_train.py`. Part (3), carries 7 and 10, is the remainder (`## Forward-carry`).

What the train does differently:

- **Policy refusal (carries 1, 2, 3; #2577, P4 s4).** On "the base branch policy prohibits the merge", `Train.policy_refusal` reads `gh pr view --json mergeStateStatus,reviewDecision,statusCheckRollup` against the head's required contexts. The whole refusal and the read reason are logged. A required context still pending, or a state it cannot read, retries as before. A red required context, a missing review, or BLOCKED with every required context green **parks** the car with `[BRANCH-POLICY]` and that reason after that attempt. The text starts `not merged after <k> attempt(s)`, so `at_head`'s #2290 recovery still recarries one whose head main has moved past.
- **Approval carry widened (carry 2, step 2).** A refusal an approval can answer (REVIEW_REQUIRED, or BLOCKED with every required context green) is offered, once, to `_carry_owner_approval`. Its conditions are unchanged: `--approval-carry`, a clean recarry, no branch-own file in h0..h, a prior owner APPROVED review citing one mandate, the mandate re-read in force at the merge, and a byte-identical read-back. Each refusal now leaves its reason in `item["carry_refused"]`, and the park names it.
- **P34 (carry 3).** The head wait reads the required set with `pr_head=True` inside `Train.serial`, the one path every serial head wait goes through (`one`, `one_overlap`, the batch's serial entries). The `req` parameter of `one` and `one_overlap` is gone, so no caller can hand a head wait main's set. This replaced a first cut that passed a second variable from `_batch`. That cut's mutant survived (`## Mutation proof`, M11), and the seam is the better fix (fixer.md step 17). At the merge base `PR_ONLY` is `()` (9262e6f43, the umbrella `gate`), and `gate.py` `REQUIRED["pr"]` holds `pr-contract`. So on today's ruleset a red pr-contract already reads as a red `gate`. This change makes the head wait independent of what `PR_ONLY` holds.
- **P231 (carry 15).** `sweep_bots` keeps `gh pr merge`'s output. A refused record PR now logs `BOT #<n> not merged at <h8> (<state>) refused: <gh's last non-empty line, up to 200 chars>`. `sweep_bots` returns the merged PR's number, else None.
- **P191 (carry 18).** After a refused attempt that is not BASE_MOVED, under `--bot-prs`, `land` sweeps once per landing. A record PR merged there raises `MainMoved('merge', 'the record PR #N merged under the batch')`, which the existing recovery recarries. No sweep runs on beats, and `add` still refuses the record branch.
- **P289 (carry 13).** A critical-path entry skips the sweep before its recarry, and `serial` sweeps after its merge (or when it stops). A batch holding one skips the sweep before reading its base and sweeps after its merges, before its serial entries. Critical path = `roster_lib.group_for_branch` on the entry's branch, checked against `roster_lib.critical_path_groups` at `roster_lib.reader_ref`, read once per run. Anything unread is nothing critical, which is today's order. `Train(critical=...)` takes a fixture reader, and both self-test drivers default it to "nothing critical", so no fixture reads the live roster.
- **P184 (b) (carry 11b).** `freeable` frees a clean holder whose HEAD is origin/<branch> or an ancestor of it (`git -C <holder> merge-base --is-ancestor`). A HEAD with commits origin lacks refuses with `has commits origin does not have`. HEAD or origin unreadable refuses as before. Keyed on commits, never a path.

Alternatives not taken: a separate approval path for the policy class. It lost because carry 2 says to widen the existing carry under the same conditions, and a second path would be a second writer of the concept (fixer.md step 17). Parking on every policy refusal lost too: the pending-check case is the review-run race `review_settle` exists for (P86), and parking there would stop entries that merge one attempt later.

Closes nothing: #2725 stays open for part (3).

## Head

Measured at the head pushed to `handoff/r10-train-overlap-grade-p3` (44409798071ec5a9ecade15d72106a572a502614), cut from origin/main 89ccf73266a8dcfc0e8d4f45ad6583b0cb622db6 (merge base 89ccf73266a8dcfc0e8d4f45ad6583b0cb622db6).

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
- M11, from the first cut (`head_req = self.required(pr_head=True)` in `_batch` -> `head_req = req`): **survived**, 0 failed. Answered by removing the variable: the head set is now read in `serial` itself, where M9 kills it for the batch's serial entries too.

Baseline for every mutant: the unmutated head, `merge_train self-test: 376 checks, 0 failed`.

## Null control

- Policy: an unreadable merge state retries three times and stops `[BRANCH-POLICY] not merged after 3 attempts`, as today (`policy refusal null: ...`). The pre-existing `every refused merge attempt is logged ...`, `#2290 shape` and `... while the same refusals on a head that still contains main stop as before` arms pass unchanged.
- Carry: the three null worlds (a conflict-resolution delta, a prior review by the `hpo-approver` App, a mandate past its window) each park after one attempt naming their reason, with no `approved (carry)` line.
- P34: the same car with pr-contract green merges.
- P231: the existing `--bot-prs ... merges FIRST` arm still logs `BOT #9 MERGED`.
- P191: no open record PR (lookup 0), and a record PR still pending, each run three refused attempts with no MAIN-MOVED. Pending logs `BOT #9 pending` twice. Without `--bot-prs` nothing is looked up.
- P289: nothing critical merges the record PR first, serial and batch (the existing batch arm `batch --bot-prs: the record PR merges before the base is read` passes unchanged).
- P184: a holder at origin's tip is freed as today. A holder ahead of origin refuses. Without `--free-holders` nothing is detached.

## Figures

- Self-test: `python3 tools/audit/seat/merge_train.py --self-test` prints `merge_train self-test: 376 checks, 0 failed` at the head. The same command on the base's file prints `merge_train self-test: 355 checks, 0 failed` (`git show 89ccf732...:tools/audit/seat/merge_train.py > tools/audit/seat/_base_merge_train.py`, run, removed). The difference is checks executed, not call sites: `git diff 89ccf732... HEAD -- tools/audit/seat/merge_train.py | grep -c '^+.*check('` prints 16 call sites, and the loops among them run more than once.
- Gate scope: `python3 tests/closure.py select --diff 89ccf73266a8dcfc0e8d4f45ad6583b0cb622db6 --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run`, naming `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2484 ENTITY CHECKS PASSED`, rc 0.
- `run_always` lines: `python3 tests/env_drift.py --claims-only 89ccf732...`, `python3 tests/closure.py selftest` and `python3 tests/layout.py` each exit 0. `python3 tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED`, rc 0.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; every metric is within budget, none re-recorded.
- `python3 tools/audit/archscore/score.py --diff 89ccf73266a8dcfc0e8d4f45ad6583b0cb622db6` prints `Architecture score: dS +0.0000 NULL`. The diff reaches no file the score reads, so a gain is not claimed.
- Class rule, step 8 (the instances are train logs on the orchestrator's host, not in the tree, so no finder harness exists to re-run; the self-test fixtures model each instance). Every production site that merges a pull request is listed by `awk 'NR<E && /"gh", "pr", "merge"/' tools/audit/seat/merge_train.py`, with E the line of `def _self_test`. It returns two sites: `land`'s loop (closed in this diff, carries 1-3, 18) and `sweep_bots` (closed, carry 15). Every head-set read is listed by `awk 'NR<E && /\.required\(/'`, which returns three sites. In `serial`: pr_head=True, closed here. In `policy_refusal`: pr_head=True, new. In `_batch`: main's set, for `main_green`, `admit` and `settle`. Main and a proof never carry PR-only contexts, but `admit` judges a PR head with main's set. That is a distinct seam of P34's class, latent while `PR_ONLY` is `()`, carried below. The CLI's `t.required(pr_head=not a.main)` in `main` is already right. Every sweep is listed by `awk 'NR<E && /self\.sweep_bots\(\)/'`, which returns six sites. `recarry` (P289 skip) and `_batch`'s pre-base sweep (P289 skip) are closed. `serial` after the merge, `serial` on a stop, `_batch` after the merges, and `land` on refusal (P191) are new.

## Red checks

none at the head before the PR exists; the scoped gate above is green locally.

## Forward-carry

- Part (3) of the brief, carries 7 (`add --front` / `add --remove` under `QUEUE_LOCK`, P112) and 10 (`stats`, and `--cap auto` only past 0.5 h/day lost, P164), is not built here. Reason: carry 10's `--cap auto` decision needs the train logs, and no train log is in the tree or reachable from this container (`git ls-files | grep -iE 'train[^/]*\.log|queue-add|skipped\.json'` prints nothing). The fixer.md rotation bound also applies. The two carries stay in the group's roster entry on `handoff/audit-r10-roster` as written. Carry: R10-TRAIN-OVERLAP-GRADE
- `_batch` admission reads a PR head's CI with main's required set (`self.required()`, no `pr_head`). It is the P34 class's sibling seam, latent while `PR_ONLY` is `()`. A future non-empty `PR_ONLY` would admit a head whose PR-only context is red. Control: the M9 arm's world (`PR_ONLY=("pr-contract",)`, pr-contract red) driven through `batch` instead of the serial train. Carry: R10-TRAIN-OVERLAP-GRADE
- Carry 2's last sentence, "pass --approval-carry in the live launch", is the orchestrator's launch line, not this file. Without the flag every approval-class policy refusal parks naming `--approval-carry or --mandate is not given`. Carry: R10-TRAIN-OVERLAP-GRADE

## Friction

- fixer.md-step-3: unclear: the carries' instances (train17, train27, s41, s44, #2665 run3) are train logs on the orchestrator's host, so "re-execute the finder's harness" has no harness to run. The self-test fixtures model each instance instead. Carry: dismissed: no finder harness exists for instrument carries; the fixtures are the measurement
