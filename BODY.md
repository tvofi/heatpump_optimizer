This changes the merge train's own instruments: `merge_train.py`, `train.sh`, `queue_pre_flight.py` and `INSTRUMENTS.md`. It covers roster item (f) and the improvements tvofi asked for on 2026-10-15: handle a moved main, and collect and merge bot pull requests. It closes the roster group's issue.

Closes #2266.

**(f), the trace.** `_carry_owner_approval` looks up the owner's latest APPROVED review and requires its `commit_id` to be h0, the head before the recarry. For #2209, review 5526967770's body names the recarried head 8a8e66e7, but the reviews API reports its `commit_id` as 8876da3b, the train's later recarry. Review 5526849236's body names 860afdbc, and the API also reports 8876da3b for it. So GitHub re-anchors an approval's `commit_id` across a clean merge of the base. After the train's recarry, the owner's approval already named the live head h, not h0. The equality failed and no carry was made. I cannot replay the API as it read at 02:00Z, so this is the reading the record supports, not a replay. Two changes fix it:

- `approve()` now checks first whether the owner's approval is already at the head. It uses budget_raise_gate's own `approval` reading and passes it the gate's own `justification` of the body, exactly as the gate's `decide` does. The one difference from the gate is when the mandate is judged: at the merge, as `policy_gate` judges it, not at the review's submission. That is stricter, never looser. When the approval is there, nothing is re-posted.
- The carry reads every head this invocation's recarries moved through (`carried_chain`), because a main-moved recovery recarries more than once. The delta is read from the head the approval names.

**Main moved.** `--main-moved-tries N` (CLI default 3; 0 keeps the old stop). A foreign merge under a settled head now raises `MainMoved`, either at step 4 or in the guard before the merge. The serial path recarries onto the new main and waits for CI again. The carry, the approval, the policy gate and `--match-head-commit` are all re-read at the new head. In a batch, a foreign merge before an entry's merge rebuilds and re-proves the remaining entries on the new main, on a fresh `batch/<tag>-m<k>-<n>` proof. The batch's own merges are not foreign: the existing check that main's tree equals the proof's tree stands above them. After a post-merge skip the batch does not recover, because that tree is the batch's own unexplained one. Past the bound, each path stops as before and names the spent bound.

**Bot pull requests.**
- `--bot-prs` merges the open record/autofix pull request in the train's own sequence: before the batch's base is read, and before each recarry. It runs behind `record_row.py`'s own guard, the same `--automerge-check --require-green` the record beat runs, at the head that guard judged, and merges with `--match-head-commit`. A refusal or a pending check never merges it and never stops the train.
- In a batch, a head whose tip is a GITHUB_TOKEN push now goes serial (`bot-head`) instead of being refused at admission. Its serial recarry, after the batch's own merges have moved main, is the App push that cures it. When main never moved, it is refused as before (`[BOT-HEAD]`). `--overlap` leaves such a head out of the up-front recarry.

**train.sh.**
- With no `--checkout`, the default path resolved to `<repo>/tools`. That is the `tools/tools/audit/seat/merge_train.py` death at 2026-10-15T19:00:41Z in `train-b5`'s log. It now resolves to the repository root.
- A second defect: `${skipbad:+--skip-bad}` over a default of `0`, which is non-empty, passed `--skip-bad --overlap` on every launch. Measured at origin/main 613b10c51 with a stub child.
- The new options now pass through.

**Other improvements.**
- `--pre-flight` runs `queue_pre_flight.py`'s reads inside the train and parks a failing entry: a `PARK #<pr>` line, an entry in `skipped.json`, rc 1. Without it, such an entry stops the train at its turn.
- `--free-holders` detaches a holder worktree only when it is clean (`status --porcelain` empty, so an untracked file also blocks) and its HEAD is exactly `origin/<branch>`. The log line names the restore command. Anything else is today's `[HOLDER]` stop, with the reason appended.

**The train-b5 finding (2026-10-15T20:24Z, #2290).** #2290 was recarried up front onto 613b10c5. When #2275's merge in the same batch moved main to 74cf47b9, eight merge attempts were refused, and nothing in the log said why: the train discarded the merge output. Afterwards the train's own `wt/2290` still held the branch, and the next pre-flight PARKed the entry on it. Three repairs:

- Every refused attempt is now logged in GitHub's words, and the stop names the last refusal.
- A refusal saying the base moved (`BASE_MOVED`) is a `MainMoved`, which the recovery recarries. So is the serial case where every attempt was refused and origin/main has moved past the head. That condition is serial only, because a batch's proved heads never contain main.
- The recarry worktrees a run created under its state dir are removed before its closing line. The removal is never forced, and a queue entry's own `worktree` is never touched.

The ruleset's `strict_required_status_checks_policy` is false, so "not up to date" was not the refusal. The real reason for #2290 cannot be recovered; the new log line is how the next one gets one.

**Out of scope, with the destination.** This PR does not make the record beat's own auto-merge yield while a train is live. The beat runs in CI (`tests.yml` `record-autofix`), and CI cannot see the train's local pidfile. A hold needs a change to `.github/workflows/tests.yml`, which is outside this group's files. It is #2302 (R10-TRAIN-HOLD). The two arms above already cover the beat: `--bot-prs` takes the record pull request at points the train chooses, and the main-moved recovery absorbs a beat merge that still lands mid-train. The pin-chain item the orchestrator added is its own pull request in this group, #2297 (`handoff/r10-tick-train-pins`).

## Head

`a46805de288b9a8bf8dd596883b52a2d0c2f1eb1`. Every figure below was taken at this head unless it names another one. It is the round-1 head `3c807ab5bb62d2d4da36003d2787437d2b012b4b` plus four commits:

- `957633266` adds the self-test arms that kill the reviewer's surviving mutants, and makes `_owner_at_head` pass the gate's justification.
- `e026bf5e0` adds `dev/audit/harnesses/r10_tick_train_mutants.sh`.
- `a6a775289` splits that harness's R9 into its two sites.
- `a46805de2` lists the harness in `tests/harness_headers.py`'s inert reads in `tests/closures.json`. `harness_headers.py` reads `dev/audit/harnesses/` by glob, and at `a6a775289` `tools/pr/ci_predict.py` predicted `INERT READS tests/harness_headers.py: dev/audit/harnesses/r10_tick_train_mutants.sh`. The entry is the one `665f903c2` added for the R10-I1 harnesses, in the same shape. At the head, `ci_predict.py` prints `no closures or fast red predicted`.

`merge_train.py` is byte-identical between `e026bf5e0` and the head (`git diff --quiet e026bf5e0e14 HEAD -- tools/audit/seat/merge_train.py` exits 0), so mutant runs taken at `e026bf5e0` hold at the head. origin/main is not merged in. The merge base is still `d4c94f9a4e96ec930e11a63b8f8ab3e4b5985892`; origin/main was `c42d7cea65ab` at 2026-10-15T22:42Z.

## Mutation proof

Written first, in round 1. At the code base, the two `#2209's shape` arms failed (`merge_train self-test: 141 checks, 2 failed`). Before its fix, `train.sh` launched without `--checkout` ran its child in `<root>/tools`.

**Round 2: the reviewer's mutants.** `bash dev/audit/harnesses/r10_tick_train_mutants.sh [names]` applies each mutant in place, runs `python3 tools/audit/seat/merge_train.py --self-test`, restores the file and prints the last line plus the FAIL lines. R1-R17 are rev-2305's mutants with the reviewer's strings. J1 is mine. The baseline M0 printed `merge_train self-test: 180 checks, 0 failed`. I ran the harness in four detached worktrees at `e026bf5e0`, with the names split between them. R9 and R9b were run at the head.

| mutant | what it removes | killed by (FAIL lines) |
|---|---|---|
| R1 | `is_sha(here)` in `freeable` | `--free-holders refuses a holder whose HEAD and origin/<branch> both fail to read` (new) |
| R2 | serial range `+1` -> `+2` | **survives: equivalent.** `n == main_moved_tries` raises before the extra iteration is reached |
| R3 | batch bound `<` -> `<=` | `the base moving between two merges stops the batch before the second` |
| R4 | `recover = True` after a post-merge skip | `--skip-bad (--main-moved-tries 3): a Stop after the merge API call is fatal for that entry only ...` (new, at the CLI default) |
| R5 | `_owner_at_head` always held | 14 arms, among them `code-owned with a budget file is not mandate-approved` and the approval-carry mutation arms |
| R6 | the `n == "0"` early return | `--bot-prs with no open record PR (the lookup answers 0) guards nothing and merges nothing but the queue` (new) |
| R7 | bot merge without `--match-head-commit` | `--bot-prs: the open record PR ... merges FIRST, pinned there` |
| R8 | pre-flight's `self.real` gate | `--pre-flight on a batch/ rehearsal reads nothing and parks nothing` (new) |
| R9 | serial `return 1 if self.skipped else 0` -> `0` | `--pre-flight: an entry the pre-flight refuses is PARKed ...; rc 1` |
| R9b | the same return in `batch` | `--skip-bad: a queue of [good, bad, good] ...` and both `--skip-bad (--main-moved-tries 0/3)` arms |
| R10 | `free_holder` detaching without `freeable` | all four `--free-holders refuses a holder ...` arms |
| R11 | carry chain -> `carried_from` only | `approval-carry from the MIDDLE of the carry chain` (new) |
| R12 | the branch-own-file delta check | `approval-carry MUTATION (the diff-empty check)` |
| R13 | `base branch was modified` dropped from `BASE_MOVED` | `a refusal saying the base moved is a MainMoved` |
| R14 | `sweep_bots`'s `self.real` gate | `batch --bot-prs on a batch/ rehearsal looks nothing up and merges no record PR` (new) |
| R15 | `first` left False after a re-proof | `--main-moved-tries: the FIRST merge on the re-proof re-reads the moved main green` (new) |
| R16 | the batch sweep before the base is read | `batch --bot-prs: the record PR merges before the base is read -- before the proof, which carries its commit` (new) |
| R17 | the re-proof on the old `prev` | `--main-moved-tries: a foreign merge before the second merge re-proves the rest ...` and the R15 arm |
| J1 | `justify=` dropped from `_owner_at_head` | `#2209's shape MUTATION (the gate's own justification)` (new) |

All 19 non-equivalent mutants are killed. Each was a single failing self-test run with rc 1. R9 as planted matched two identical lines and replaced the first, which is the serial one. The harness names each line by its context, and both are killed.

**Round 1's table** (M1-M11, Q1, Q2, T1, T2, N1-N6) was measured at `b977179a689801abecd7fcf194a60821cf3aaf90`, against the 164- and 171-check suites. I did not re-run it here. Round 2 adds arms and changes no production line those mutants touch, apart from `_owner_at_head`'s `justify`. M1 is that site's mutant, and R5 and J1 above cover it at this head.

## Null control

- M0: the unmutated head prints `180 checks, 0 failed`. R2, the equivalent mutant, prints the same, so a mutant that changes no behaviour does not show up as killed.
- Each new arm has a counterpart that holds the predicate's other side:
  - R14's rehearsal arm against R16's arm on `main`, where the record PR does merge.
  - R6's lookup of 0 against the existing lookup of 9.
  - R8's rehearsal pre-flight against the existing `main` pre-flight arm, which PARKs.
  - R1's unreadable pair against the clean-holder arm, which frees the holder.
  - R15's red foreign tip against the existing green-tip re-proof arm, which merges all three.
  - R4 runs at tries 0 and at tries 3, and both give the same result.
  - J1's missing payment line against the #2209 arms with the full justification, which land.
- `--main-moved-tries 0` (the constructor's default) still gives exactly today's stop line, after exactly one recarry. Without `--bot-prs` no record pull request is looked up, and without `--free-holders` a freeable holder still gets today's HOLDER stop.

## Figures

All at the head, with the seat venv shims first on PATH.

- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 180 checks, 0 failed`. Round 1 had 171. The base had 138.
- `bash dev/audit/harnesses/r10_tick_train_mutants.sh`: the table above. The rule is one self-test run per mutant, and a mutant counts as killed when it prints at least one FAIL line.
- `python3 tools/audit/seat/queue_pre_flight.py --self-test`: `queue_pre_flight self-test: 32 checks, 0 failed`.
- `bash tools/audit/seat/train.sh --self-test`: `train.sh self-test: ok (5 refusals shown, root and options reach the child, no unasked flag)`.
- `python3 tests/closure.py select --diff d4c94f9a4e96ec930e11a63b8f8ab3e4b5985892`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, with 7 changed files. The script it runs, `PYTHONPATH=tests/hastub python3 tests/entities.py`, prints `ALL 2319 ENTITY CHECKS PASSED` with rc 0.
- The `run_always` lines, with `PYTHONPATH=tests/hastub`:
  - `tests/env_drift.py --claims-only d4c94f9a4e96...`: `claims hygiene: ... ok`.
  - `tests/closure.py selftest`: `ALL 115 closure shrink pins PASSED`.
  - `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `tests/layout.py`: `layout self-test: ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff d4c94f9a4e96ec930e11a63b8f8ab3e4b5985892`: `Architecture score: dS +0.0000 NULL`.
- `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- From round 1, not re-taken:
  - `gh api repos/tvofi/heatpump_optimizer/rulesets/23698884`: `strict_required_status_checks_policy` false.
  - `gh api repos/tvofi/heatpump_optimizer/pulls/2209/reviews`: reviews 5526849236 and 5526967770 both report `commit_id` 8876da3b. Their bodies name 860afdbc and 8a8e66e7.

## Red checks

none

## Unpinned sites

The CI mutation lane does not reach this diff. Job 116686609830 printed `MUTATION TABLE PASSED (empty scope)`, because nothing under `tools/` is production code in its scope. `mutation-autofix` therefore pins nothing here. The sites this PR pins are the ones in the self-test mutant table under `## Mutation proof`, each named with the arm that kills it. The run command is `bash dev/audit/harnesses/r10_tick_train_mutants.sh [names]`. One site is equivalent: R2, the serial loop's range. Any other line of the diff has not been mutated, and nothing pins it.

## Forward-carry

- The record beat's yield while a train is live goes to #2302 (R10-TRAIN-HOLD). It needs `.github/workflows/tests.yml`, which is outside this group.
- The pin-chain item is #2297 (`handoff/r10-tick-train-pins`).

## Friction

- `dev/governance/roles/fixer.md`: unclear: step 2 offers "pinned by `mutation-autofix`" as a disposition for an unpinned site. The CI mutation lane's scope leaves out `tools/`, so for an instrument file that disposition pins nothing, and round 1's body relied on it. The mutant harness for this file now lives in the tree.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
