Part of #201.

**Policy change: tvofi approves it before merging** (an approving review at the head; `ci-autofix.md` is policy under `CLAUDE.md`).

This pull request makes two corrections to `dev/governance/rules/ci-autofix.md`, plus the instrument prose that makes the second claim.

### 1. The seat's route for a predicted INERT READS

The rule named only the bot's route for an INERT READS, which is to wait for `closures-autofix`, while `prepr.sh` step 6d refuses the push that route needs. #2376 added `python3 tools/pr/ci_predict.py --apply-inert` as the seat's pre-push repair and drafted the rule sentence in `dev/audit/rca/R10-RCA-INERT-PREDICT.md` section 5 ("Not landed, because it is policy and needs tvofi's approval"). This lands that sentence verbatim, where the RCA puts it (after "the bot merges INERT READS from CI recordings too (#1886, R9-CI-1)"):

> One 6d predicts is not the wait: `prepr.sh` refuses it before the push, and `python3 tools/pr/ci_predict.py --apply-inert` writes the entry the Linux recording would — that commit is not a `--single`.

**RCA process state addressed: (d), its preconditions changed underneath it** (`R10-RCA-INERT-PREDICT.md` section 2). #2376 fixed (d) in the instrument; this fixes it in the rule, so the rule's "wait" covers only an INERT READS that CI finds and 6d did not predict.

The sentence matches the instrument's wording: `ci_predict.py`'s route line prints `python3 tools/pr/ci_predict.py --apply-inert`, and 6d's step line says "`--apply-inert` repairs them". The command sits on one line of the rule, so a grep finds it.

### 2. A GITHUB_TOKEN push's `pull_request` runs are held, not absent

The rule said a `GITHUB_TOKEN` (bot) push "creates no `pull_request` run (measured 2026-10-09)". That is stale. Re-measured over the REST API:

- Every bot-pushed head from 2026-10-15T10:23Z has `pull_request` runs: 28 of 28. They are created with actor `github-actions[bot]` and held `action_required`, and `hpo-runs[bot]` approves them as attempt 2 at all 28 heads. tvofi also re-ran Hassfest at `417ec84622`. At read time, 2 of the 8 runs at `6f6aa4e48d` (Hassfest, Architecture score) were still held at attempt 1.
- Cited run: Tests **38781421410** at `720d3636`, subject `ci: pin killed mutants`. Attempt 1 is `action_required`, actor github-actions[bot]; attempt 2 was triggered by `hpo-runs[bot]`.
- Null control: two 2026-10-09 bot heads, `3c9fe53f` and `63084989`, still read 0 `pull_request` runs; two 2026-10-10 bot heads, `18a04ed6` and `72cfb1d0`, read 8 each. So the old measurement was true at its date.

Corrected sites:

- `ci-autofix.md` and its two generated copies.
- `tools/audit/seat/merge_train.py`: the docstring, `BOT_HEAD`'s comment, the `bot_tip` block comment (it keeps the 2026-10-09 measurement as history), the batch comment, the self-test comment, and the `bot_refusal` message, which printed the same false claim at run time.
- The same claim, found by a tree-wide grep: `tools/audit/seat/ci-watch.sh`'s header, `tools/audit/seat/queue_pre_flight.py`'s docstring, and `tools/audit/seat/INSTRUMENTS.md`'s `ci-watch.sh` entry.

All of these are prose; no behaviour changes. The train still refuses a bot tip, because it does not read whether the held runs were approved.

**The ABSENT consequences, re-read after the correction.** "Absent is not green (`orchestrator.md` section 11)" is still true. What changed is when ABSENT ends. The contexts only `pull_request` writes are ABSENT at a bot head while its runs are held. The three jobs approve those runs, fail-soft while their secrets are absent, and that approval is now the usual cure. An App push or a body edit is the cure when it fails. "All three approve any held run" was already in the paragraph and stays true, and it is now load-bearing rather than insurance. That paragraph is the rule's only ABSENT claim. The `--single`, DIRTY and phantom statements do not depend on it.

**Paid for, not raised** (`ratchet-budgets.md` step 1). The file sat 1 token under its `files_tokens` cap. Both changes are paid for with cuts in the same file:

- "(Linux `strace` recordings are the ones to merge)": the next sentence says the same.
- "— the status a clean run also reports —": the "What green means" paragraph already lists `skip-clean`.
- "Closing it needs a dry-run classification and a ruling on the guard's contract.": a design note that tells a seat nothing to do.
- "; none is closed here" (a rule file closes nothing), plus ", so no bot commit comes" and ", the job is green,": both restate the heading "Three paths still end green unrepaired".
- "in place" (prune edits the table where it is).
- The held-runs paragraph is tighter than the one it replaces.

No `*_budgets.json` is touched.

## Head

4f25f6fdf4c4038759bb96fa8da0f1bf883c6bed

## Mutation proof

n/a: the prose changes have no production line, and `merge_train.py`'s change is comments plus a message string. The checks they can redden are mechanical:

- Reverting the generated copies alone makes `node tools/policy/rules_sync.mjs --check` refuse the drift.
- Without the cuts, a plain `node tools/policy/policy_lint.mjs` refuses `ci-autofix.md` on `files_tokens` (see Null control).
- `merge_train.py --self-test`'s BOT-HEAD check keys on `GITHUB_TOKEN`, the subject and `App push` in the refusal line. The new message keeps all three, and the self-test stays green.

## Null control

On a detached `origin/main` worktree, with only the INERT READS sentence added and nothing cut, a plain `node tools/policy/policy_lint.mjs` refuses with `ERROR [budgets] .claude/rules/ci-autofix.md: ... exceeds its cap ... (files_tokens)`. At this head it exits 0. `--budgets` alone only prints the rows. For the API figures, the 2026-10-09 bot heads reading 0 `pull_request` runs are the control.

## Figures

- `node tools/policy/policy_lint.mjs --budgets`: the `ci-autofix.md` row at the head, against its cap, compared exactly.
- `node tools/policy/rules_sync.mjs --check`: RULES-SYNC ok.
- `gh api 'repos/tvofi/heatpump_optimizer/actions/runs?event=workflow_dispatch&created=2026-10-15&per_page=100'`, and the same for each date to 2026-10-18: the bot heads. These are runs whose `head_commit.author.email` starts `41898282`, created from 2026-10-15T10:23Z. The autofix jobs dispatch four runs at every bot head they push, so this lists those heads. Querying `pull_request` runs directly hits the API's 1000-result cap, since the window holds several thousand runs.
- `gh api 'repos/tvofi/heatpump_optimizer/actions/runs?head_sha=<sha>&event=pull_request&per_page=100'` for each such head: 28 of 28 have `pull_request` runs, and 0 have none.
- `gh api repos/tvofi/heatpump_optimizer/actions/runs/38781421410/attempts/1`: `action_required`, actor github-actions[bot]. `gh api repos/tvofi/heatpump_optimizer/actions/runs/38781421410`: run_attempt 2, triggering actor hpo-runs[bot].
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: the mode line is `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, and the script it names is `tests/entities.py`.
- `python3 tools/audit/seat/merge_train.py --self-test`, `bash tools/audit/seat/ci-watch.sh --self-test`, `python3 tools/audit/seat/queue_pre_flight.py --self-test`: each ends with 0 failed.
`PYTHONPATH=tests/hastub python3 tests/entities.py`, with `BASH_ENV` unset, ends `ALL 2346 ENTITY CHECKS PASSED`. The `run_always` lines (`tests/env_drift.py --claims-only <merge-base>`, `tests/closure.py selftest`, `tests/harness_headers.py`, `tests/layout.py`) and `python3 tests/structure.py` (STRUCTURE RATCHET PASSED) all exit 0.
- This container still sets `BASH_ENV=/etc/profile.d/hpo-toolchain.sh`. That is the environment's, and the orchestrator is removing it. Under it, `tests/entities.py` ends `1 of 2346 ENTITY CHECKS FAILED` on `graders-head-copy's delivery_status step ...`, identically on `origin/main`: the profile re-prepends its venv ahead of that test's stub `python`. Nothing in the tree works around it.
- `bash tools/pr/prepr.sh <this body>` at the head: rc=0 under `env -u BASH_ENV`. With the environment's `BASH_ENV` set it is rc=1, its only REFUSE being `closures`: `failed while being recorded: tests/entities.py (exit 1)`, for the cause in the line above.

## Red checks

none

## Forward-carry

none

## Friction

ci-autofix-draft: unclear: the drafted sentence opens "One 6d predicts", whose antecedent is "an INERT READS" in the sentence before; it was landed verbatim as the RCA drafted it, not reworded on this seat's judgement.
ci-autofix-held-runs: stale: the same "a GITHUB_TOKEN push creates no pull_request run" claim stands in five `.github/workflows/tests.yml` comments (above `mutation-autofix`'s dispatch, and at each job's push and approve steps). They are not edited here: a workflow edit is a gate file and forces the FULL suite, and that is the orchestrator's call.
merge-train-bot-tip: cost: the train still refuses every bot tip, while `hpo-runs[bot]` approved held runs at all 28 bot heads in the window (2 runs at `6f6aa4e48d` were still held at read time). The refusal may now be over-conservative; reading the held runs' approval state could replace it, but that changes behaviour, which this pull request does not do.

## Approval

Policy: `dev/governance/rules/ci-autofix.md` and its two generated copies; the instrument edits are prose. tvofi approves before merging, by an approving GitHub review at the head. Nothing is merged on this seat's word.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_018qAxaCuvKU3aVvNn8asGdA
