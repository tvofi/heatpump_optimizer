This changes the merge train's own instruments: `merge_train.py`, `train.sh`, `queue_pre_flight.py` and `INSTRUMENTS.md`. It covers roster item (f) and the improvements tvofi asked for on 2026-10-15: handle a moved main, and collect and merge bot pull requests. It closes the roster group's issue.

Closes #2266.

**(f), the trace.** `_carry_owner_approval` looks up the owner's latest APPROVED review and requires its `commit_id` to be h0, the head before the recarry. For #2209, review 5526967770's body names the recarried head 8a8e66e7, but the reviews API reports its `commit_id` as 8876da3b, the train's later recarry. Review 5526849236's body names 860afdbc, and the API also reports 8876da3b for it. So GitHub re-anchors an approval's `commit_id` across a clean merge of the base. After the train's recarry, the owner's approval already named the live head h, not h0. The equality failed and no carry was made. I cannot replay the API as it read at 02:00Z, so this is the reading the record supports, not a replay. Two changes fix it:

- `approve()` now checks first whether the owner's approval is already at the head. It uses budget_raise_gate's own `approval` reading, with the mandate judged at the merge as `policy_gate` judges it. When the approval is there, nothing is re-posted.
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

**Declined, with the reason.** I did not make the record beat's own auto-merge yield while a train is live. The beat runs in CI (`tests.yml` `record-autofix`), and CI cannot see the train's local pidfile. A hold would need a change to `.github/workflows/tests.yml`, which is outside this group's files. By the owner's 2026-10-15 ruling I report it to the orchestrator instead of widening this PR. The two arms above already cover the beat: `--bot-prs` takes the record pull request at points the train chooses, and the main-moved recovery absorbs a beat merge that still lands mid-train. The pin-chain item the orchestrator added is its own pull request in this group, #2297 (`handoff/r10-tick-train-pins`).

## Head

`b977179a689801abecd7fcf194a60821cf3aaf90`: code commits `c5b926762a50`, `e762f04f299f` and the docs commit, merged with origin/main `39b77a467928` (2026-10-15T21:18Z). Every figure below was taken at this head.

## Mutation proof

Written first. At the code base, the two `#2209's shape` arms failed (`merge_train self-test: 141 checks, 2 failed`). Before its fix, `train.sh` launched without `--checkout` ran its child in `<root>/tools`.

Each mutant below was applied in place, run through its tool's `--self-test`, and restored. All 21 were killed. The first 15 were run against the 164-check suite and N1-N6 against the 171-check one:

| mutant | rc | failing checks (abridged) |
|---|---|---|
| M1 `if held:` -> `if False:` (owner approval at head) | 1 | `#2209's shape (approval-carry on)`, `(approval-carry off)`, `approval-carry with no recarry ... nothing is re-posted` |
| M2 serial loop `range(self.main_moved_tries + 1)` -> `range(1)` | 1 | `main moving during CI is recovered`, `the recovery is bounded`, `main moving between the approval and the merge is recovered too`, `approval-carry across a main-moved recovery` |
| M3 batch re-prove predicate -> `False` | 1 | `--main-moved-tries: a foreign merge before the second merge re-proves the rest`, `the batch recovery is bounded` |
| M4 bot guard `if code:` -> `if False:` | 1 | `--bot-prs: a guard exit 3 never merges`, `a guard exit 1 never merges` |
| M5 bot-head route dropped | 1 | `a batch entry whose head is a GITHUB_TOKEN bot push goes serial`, `... with nothing merged before it`, `--overlap leaves a bot-routed head out`, `a skip carries its block class` |
| M6 overlap bot exclusion dropped | 1 | `--overlap leaves a bot-routed head out of the up-front recarry` |
| M7 holder clean check `code or st.strip()` -> `code` | 1 | `--free-holders refuses a holder with uncommitted or untracked` (both) |
| M8 holder pushed check `here != there` dropped | 1 | `--free-holders refuses a holder with unpushed work` |
| M9 pre-flight `status == "PASS"` -> `True` | 1 | `--pre-flight: an entry the pre-flight refuses is PARKed` |
| M10 carry chain -> last head only | 1 | `approval-carry across a main-moved recovery` |
| M11 sweep before recarry removed | 1 | `--bot-prs: the open record PR ... merges FIRST`, both guard-exit arms |
| Q1 pre-flight `bot and not self.bot_cured` -> `bot` | 1 | `the train's own pre-flight (bot_cured) passes a bot tip` |
| Q2 pre-flight free_holders condition dropped | 1 | `under the train's --free-holders a clean holder ... passes` |
| T1 train.sh root reverted to `../..` | 2 | `REFUSE: self-test: launched without --checkout the child ran in '<root>/tools'` |
| T2 train.sh `skipbad=0 overlap=0` restored | 2 | `REFUSE: self-test: a bare launch passed flags it was not given` |
| N1 base-moved refusal not raised | 1 | `a refusal saying the base moved is a MainMoved` |
| N2 exhausted-with-main-moved not recarried | 1 | `every attempt refused while main moved past the head (the #2290 shape) is recarried` |
| N3 its `contains_main` condition dropped | 1 | the same, and `... while the same refusals on a head that still contains main stop as before` |
| N4 the refusal log line removed | 1 | `every refused merge attempt is logged with GitHub's own words` |
| N5 `release_worktrees` a no-op | 1 | `a recarry worktree the train made ... is removed`, `the recarry worktrees the batch made in the real clone are gone` |
| N6 own-worktree guard dropped | 1 | `an absorbed-branch recarry lands in a real fixture repo`, `... a queue entry's own worktree is never touched` |

## Null control

- `--main-moved-tries 0` (the constructor's default) gives exactly today's stop line, after exactly one recarry.
- Without `--bot-prs`, no record pull request is looked up.
- Without `--pre-flight`, the same malformed entry stops the train.
- Without `--free-holders`, even a freeable holder gets today's HOLDER stop, with nothing detached.
- A bot head with nothing merged before it is refused as before.
- A refused merge on a head that still contains main stops as before. It does not recarry.
- A queue entry's own `worktree` is never removed.
- With no owner approval at the head, a budget entry stops as before. A re-anchored approval under an expired mandate also stops as before.
- The existing `the base moving between two merges stops the batch` arm still passes, with tries at 0.

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 171 checks, 0 failed`. The base had 138.
- `python3 tools/audit/seat/queue_pre_flight.py --self-test`: `queue_pre_flight self-test: 32 checks, 0 failed`.
- `bash tools/audit/seat/train.sh --self-test`: `train.sh self-test: ok (5 refusals shown, root and options reach the child, no unasked flag)`.
- `python3 tests/closure.py select --diff 39b77a467928`: `MODE: SCOPED -- 0 script(s) run`. `governance.yml` runs the merge_train and train.sh self-tests.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `gh api repos/tvofi/heatpump_optimizer/rulesets/23698884`: `strict_required_status_checks_policy` false.
- `gh api repos/tvofi/heatpump_optimizer/pulls/2209/reviews`: reviews 5526849236 and 5526967770 both report `commit_id` 8876da3b; their bodies name 860afdbc and 8a8e66e7.

## Red checks

none

## Unpinned sites

The 21 mutated sites above are each killed by a named arm. That covers the sites I mutated, not every line of the diff. The gate's own mutation pass and `mutation-autofix` cover the rest. `mutation-autofix` pins whatever the gate's own mutation pass reports.

## Forward-carry

none. The declined CI-side hold has been reported to the orchestrator for a group of its own (it needs `.github/workflows/tests.yml`).

## Friction

none
