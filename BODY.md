R10-996-RUNNER-CLAIMS. Some golden drift moves the same way on every host but lands on a different set of fixtures on each host. No list of fixture names can claim it, so `tests/env_drift.py` gains a claim keyed on the move: `shape: <leaf paths> <from> -> <to>`. A fixture whose moved leaves all match a shape reads `SHAPED`. A shape that matches nothing on a host reads stale. A malformed line, or one whose from-set and to-set overlap, refuses the run. Issue #996's claim-grammar decision closes here.

`dev/audit/harnesses/r10_shape_grammar_mutants.py`, this diff's mutation instrument, runs each child bytecode-free (`-B`, empty `PYTHONPYCACHEPREFIX`), so no child imports a previous mutant's cached `.pyc`.

## Approval

Owed: the owner's approving review at the head. `dev/governance/rules/claim-files.md` and its generated copies `.claude/rules/claim-files.md` and `.cursor/rules/claim-files.mdc` are code-owned policy (decision 0009, step 6). No budget is raised.

## Head

`9f62bb70d711dee2ca178892ac935fd231365fde`, a merge of origin/main `11b7a9d739db46a5a62e9f9cf01a8f527a974137` into `41c0cdc362d8cce4d790eecbda1cdc47dda31cf2`; merge base `11b7a9d739db46a5a62e9f9cf01a8f527a974137`. Every figure below was taken at this head between 2026-10-26T06:11Z and 06:24Z (`date -u`), on Linux x86_64.

## Mutation proof

`python3 dev/audit/harnesses/r10_shape_grammar_mutants.py` (in this diff) rewrites one production line of `tests/env_drift.py`, runs `tests/entities.py`'s shape-claim block in a child against it, then restores the file. At this head: `M0 RESULT pins=16 fails=0`, R1 to R17 each KILLED except R10, `RESULT mutants=17 killed=16`, exit 0. R10 drops the `path.startswith(prefix)` guard in `shaped_leaves` and is an equivalent mutant: `_diff_leaves` always prefixes the path with `<fixture>.`. The fix review dismissed it.

The delta's own mutation is the parent `a2a7b9ef`'s harness, without `-B` and the prefix: R11 reads SURVIVED (`## Figures`).

## Null control

The harness at `a2a7b9ef`, run 10 times as `R10 R11`, reads R11 SURVIVED on 8 of 10 runs and exits 1 on those 8. This head's harness reads R11 KILLED on 10 of 10. Had the change been inert, the two columns would match.

## Figures

- **Before.** `git show a2a7b9ef:dev/audit/harnesses/r10_shape_grammar_mutants.py` copied beside the harness, then `for i in $(seq 10); do python3 <copy> R10 R11 | grep -E "^R11"; echo "exit=${PIPESTATUS[0]}"; done | sort | uniq -c`: `8 R11: RESULT pins=16 fails=0 SURVIVED`, `2 R11: RESULT pins=16 fails=1 KILLED`, `8 exit=1`, `2 exit=0`.
- **After.** The same loop over `dev/audit/harnesses/r10_shape_grammar_mutants.py`: `10 R11: RESULT pins=16 fails=1 KILLED`, `10 exit=0`.
- **Whole run.** `python3 dev/audit/harnesses/r10_shape_grammar_mutants.py`: `RESULT mutants=17 killed=16`, exit 0, 10.5 s wall (`time`).
- **Scoped gate.** `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh`, 06:12Z to 06:24Z: `MODE: SCOPED -- 6 script(s) run, 27 scoped out`. `env_drift.py --all`, `env_drift.py --claims-only`, `card.mjs`, `plan_view.py`, `harness_headers.py`, `layout.py` and `closure.py selftest` ok; `tests/entities.py` reads `2 of 2461 ENTITY CHECKS FAILED`. Control: `PYTHONPATH=tests/hastub python3 tests/entities.py` in a detached worktree at `11b7a9d73`, 06:15Z to 06:24Z, reads `2 of 2449`, and the FAIL names of the two runs are identical (the `gate-sweep.yml` U0c check and the `graders-head-copy` delivery_status check, plus the same self-test arms). The branch's 12 added checks all pass, among them `one shape claim holds on every recorded host reading of the parked classifier arm`.
- **Structure.** `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- **Architecture.** `python3 tools/audit/archscore/score.py --diff 11b7a9d73 HEAD`: `Architecture score: dS +0.0000 NULL`.
- **Policy caps.** `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
- **Rule sync.** `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- **Claim files and version.** `git diff --quiet $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json && echo CLAIMS-VERSION-UNTOUCHED`: `CLAIMS-VERSION-UNTOUCHED`.
- **CI prediction.** `python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 11b7a9d739db`.
- **Temp paths.** `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused`.

## Red checks

Read from the check-runs API for #2843 at the PR head `a2a7b9ef` and for main at `11b7a9d73`, 2026-10-26T06:15Z. No run exists yet for `9f62bb70`. Every red below stopped on the installation's GitHub API rate limit (HTTP 403, `reset_epoch=1792991224`, 04:52Z to 05:01Z) before any test body ran. That is infrastructure, not this PR's defect, so no cheaper detector is owed under `defect-root-cause.md`. A rerun is the answer.

- `arch-score / arch-score`: red in `CI code` run 40271999135 (`API rate limit exceeded for installation`). Its rerun in `CI edit` run 40271998592, attempt 2, passed at 05:36Z.
- `refresh`: red in run 40271999135, exit 3, `reset_epoch=1792991224`. Its rerun in run 40271998592, attempt 2, passed at 05:09Z.
- `validate / validate-hacs`: red in run 40271999135 (`GitHubRatelimitException: API rate limit exceeded for installation`). Not rerun; the push of this head re-runs it.
- `governance / env-matrix`: red in run 40271999135 on one outcome, `FAIL pr / nothing skipped in a full clone -- skip required-contexts the GitHub API is unreachable`; 15 other outcomes held. The push of this head re-runs it.
- `governance / delivery-status`: green on the PR head (run 40271999135, success at 05:01:45Z). The opener's prepr listed it from a commit in main's ancestry, not from this PR; main's `CI code` run 40273778098 at `11b7a9d73`, this head's base, concluded success.
- `tests / nightly-status`: `NIGHTLY UNREADABLE ... HTTP 403 ... (rate limit exhausted)` in run 40271999135. Not a required context. The nightly it reads is main's, red on `Nightly` / record-autofix (`batch=$?` under `bash -e`, exit 4 `BATCH WAIT`); hotfix PR #2848 owns that, not this PR.

## Forward-carry

- The `tests/golden/claimed_drift.txt` header does not name the shape line, and a branch that claims nothing leaves that file byte-identical. The first branch that claims by shape restates the header with its claim. Carry: R10-ARCH-SHAPES-CLASSIFIER
- R10-ARCH-SHAPES-CLASSIFIER claims by `shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'`; `bash dev/audit/harnesses/r10_shape_claim_controls.sh <its head> <its base>` re-runs the real-capture controls there. Carry: R10-ARCH-SHAPES-CLASSIFIER

## Friction

none
