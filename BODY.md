R10-996-RUNNER-CLAIMS. Some golden drift moves the same way on every host but lands on a different set of fixtures on each host. No list of fixture names can claim it, so `tests/env_drift.py` gains a claim keyed on the move: `shape: <leaf paths> <from> -> <to>`. A fixture whose moved leaves all match a shape reads `SHAPED`. A shape that matches nothing on a host reads stale. A malformed line, or one whose from-set and to-set overlap, refuses the run. Issue #996's claim-grammar decision closes here.

This delta makes `dev/audit/harnesses/r10_shape_grammar_mutants.py`, this diff's mutation instrument, run each child bytecode-free. Before, a child could import the previous mutant's cached `tests/__pycache__/env_drift` `.pyc`, so R11 run after R10 read SURVIVED and the harness exited 1.

## Approval

Owed: the owner's approving review at the head. `dev/governance/rules/claim-files.md` and its generated copies `.claude/rules/claim-files.md` and `.cursor/rules/claim-files.mdc` are code-owned policy (decision 0009, step 6). The new rule: drift with one direction and a host-dependent fixture set is claimed by its shape. It was drafted under orchestrator mandate 6329234399. No budget is raised.

## Head

`41c0cdc362d8cce4d790eecbda1cdc47dda31cf2`, merge base `df478d40be4b546a7aaad150a5d9132483534a3a`, origin/main at `11b7a9d739db46a5a62e9f9cf01a8f527a974137`. No merge was owed: `git merge-tree --write-tree origin/main HEAD` reports no conflict. Every figure below was taken at this head between 2026-10-26T05:23Z and 05:44Z (`date -u`), on Linux x86_64.

## Mutation proof

The instrument is `python3 dev/audit/harnesses/r10_shape_grammar_mutants.py` (in this diff). It rewrites one production line of `tests/env_drift.py` in place, runs `tests/entities.py`'s shape-claim block in a child against it, then restores the file's bytes. M0, the unmutated file, is the null arm. Its whole run at this head reads `M0 RESULT pins=16 fails=0`, then R1 to R17 each KILLED except R10, then `RESULT mutants=17 killed=16`, exit 0 (`## Figures`).

R10 drops the `path.startswith(prefix)` guard in `shaped_leaves`. It survives as an equivalent mutant: `_diff_leaves` always prefixes the path with `<fixture>.`, so the guard cannot be reached from `judge_drift`. The fix review dismissed it.

The delta's own mutation: delete `"-B", ` and the `PYTHONPYCACHEPREFIX` entry from `pins()`. That is the parent `a2a7b9ef`'s harness. Ten runs of `... R10 R11` there each print `R11: RESULT pins=16 fails=0 SURVIVED` and exit 1 (`## Figures`).

## Null control

At the parent `a2a7b9ef` the unmodified harness reads R11 SURVIVED on 10 of 10 `R10 R11` runs. With this delta it reads KILLED on 10 of 10. Had the change been inert, the after column would match the before column.

I also ran a separate control: `-B` alone, without the empty `PYTHONPYCACHEPREFIX`. It killed R11 on 10 of 10 runs. So `-B` is what fixes the measured failure. The prefix is a design choice and closes the read side as well: with an empty cache directory, no `.pyc` written by another process can stand in for a mutant.

## Figures

- **Before.** Harness at `a2a7b9ef` (this delta stashed), run 10 times as `for i in $(seq 10); do python3 dev/audit/harnesses/r10_shape_grammar_mutants.py R10 R11 | grep -E "^R11"; echo "exit=${PIPESTATUS[0]}"; done | sort | uniq -c`, at 2026-10-26T05:23Z: `10 R11: RESULT pins=16 fails=0 SURVIVED`, `10 exit=1`.
- **After.** The same loop at this head: `10 R11: RESULT pins=16 fails=1 KILLED`, `10 exit=0`.
- **`-B` alone.** The same loop over a scratch copy of this head's harness with the `PYTHONPYCACHEPREFIX` entry removed by `sed`: `10 R11: RESULT pins=16 fails=1 KILLED`.
- **Whole run, in tree.** `python3 dev/audit/harnesses/r10_shape_grammar_mutants.py` at this head: `M0 RESULT pins=16 fails=0`, `R10: RESULT pins=16 fails=0 SURVIVED`, each of the other sixteen `KILLED`, `RESULT mutants=17 killed=16`, exit 0. It took 7.2 s wall time (`time`).
- **Scoped gate.** `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh`: `MODE: SCOPED -- 6 script(s) run, 27 scoped out`, 2026-10-26T05:24Z to 05:36Z. `env_drift.py --all`, `env_drift.py --claims-only`, `card.mjs`, `plan_view.py`, `harness_headers.py`, `layout.py` and `closure.py selftest` ok. `tests/entities.py` reads `2 of 2461 ENTITY CHECKS FAILED`, then `1 TEST SCRIPT(S) FAILED`. The two FAILs are the `gate-sweep.yml` check (U0c) and the `graders-head-copy` delivery_status check. The control, `PYTHONPATH=tests/hastub python3 tests/entities.py` in a detached worktree at the merge base `df478d40b`, 2026-10-26T05:36Z to 05:44Z, reads `2 of 2449` with the same two FAIL names. Its other FAIL lines, the in-script self-test arms, match the head's line for line except for randomized ids and timings. The branch adds 2461 - 2449 checks and fails none of them, and `one shape claim holds on every recorded host reading of the parked classifier arm` is ok.
- **Structure.** `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- **Architecture.** `python3 tools/audit/archscore/score.py --diff df478d40b HEAD`: `Architecture score: dS +0.0000 NULL`.
- **Policy caps.** `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
- **Rule sync.** `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- **Claim files and version.** `git diff --quiet $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json && echo CLAIMS-VERSION-UNTOUCHED` printed `CLAIMS-VERSION-UNTOUCHED`.
- **CI prediction.** `python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against df478d40be4b`.
- **Temp paths.** `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused`.

## Unpinned sites

n/a: the diff adds no `custom_components/` line. Value checks pin the `tests/env_drift.py` sites, and the in-tree harness kills them (`## Mutation proof`). R10 is an equivalent mutant.

## Red checks

No check run exists yet for `41c0cdc36`. It sits on `handoff/r10-996-runner-claims` and becomes the PR head only when the orchestrator moves it, so it has no reds to answer.

At the PR head `a2a7b9ef` (check-runs API for #2843, read 2026-10-26T05:24Z) five concluded runs are red. Each one stopped on the installation's GitHub API rate limit before any test body ran. This is infrastructure, not this PR's defect, and no answer under `defect-root-cause.md` is owed for it:

- `arch-score / arch-score`: `gh: API rate limit exceeded for installation ... (HTTP 403)` while reading the pull request.
- `refresh`: `reset_epoch=1792991224`, exit 3.
- `validate / validate-hacs`: `GitHubRatelimitException: API rate limit exceeded for installation`.
- `tests / nightly-status`: `NIGHTLY UNREADABLE ... HTTP 403 ... (rate limit exhausted)`. Not a required context. The nightly it reads is main's.
- `governance / env-matrix`: `FAIL pr / nothing skipped in a full clone -- skip required-contexts the GitHub API is unreachable`. Its other 15 declared outcomes held.

## Forward-carry

- The `tests/golden/claimed_drift.txt` header does not name the shape line. A branch that claims nothing leaves that file byte-identical, so this branch cannot fix it. The first branch that claims by shape restates the header along with its claim. Carry: R10-ARCH-SHAPES-CLASSIFIER
- R10-ARCH-SHAPES-CLASSIFIER claims by one line: `shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'`. `bash dev/audit/harnesses/r10_shape_claim_controls.sh <its head> <its base>` re-runs the real-capture controls there. Carry: R10-ARCH-SHAPES-CLASSIFIER

## Friction

none
