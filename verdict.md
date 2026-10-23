Fix review: blocked e542446e725f703f2cfd51a35fbc987ed0d54584 cutover-unsound: main's push gate requires tests / ci-ratchet, which is red on main (critical_path_minutes 57.8 > 54.825 at a6620c30a), so step 5's --verify cannot pass and rollback trigger 2 fires by construction; reds-at-head also passes a head whose required units are skipped or absent, and tests / closures is red at this head (UNDER-SCOPED harness_headers.py) and unanswered

bus-nonce: 7dc3cd8e950fece88ea43c6226e0b789

Round 1 of this review (first fix review of #2662). I measured head `e542446e725f703f2cfd51a35fbc987ed0d54584` (`ev/HEAD.txt`) from a detached worktree. The role contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Block

1. **The cut-over rolls itself back.** After the merge, main's push `gate` runs this head's `tools/ci/gate.py`. A push sets no `PINNED`, so main's own copy runs, and its `REQUIRED["push"]` includes `tests / ci-ratchet` (B3, and the self-test check "B3: push owes the Tests push run's ratchets"). main's `ci-ratchet` is red today. The five newest push Tests runs on main are all `failure`, and the newest, run 39938675967 at a6620c30a (this PR's base), fails only on `ci-ratchet`. Its log, job 120380010176, reads `GROW critical_path_minutes: 57.80833333333334 (budget 54.825)`. See `ev/main-push-tests-a6620c30a.txt`.
   - The metric is the median of the newest 8 completed push runs. `tests/ci_ratchet.py` at this head keeps the window continuous across the cut-over (`PUSH_RUNS = ("ci.yml", "tests.yml")`, and an old Tests run "reads the same").
   - So the first push run after the merge medians 8 pre-merge runs. Its `tests / ci-ratchet` is red, its `gate` is red, and the body's step 5 (`--verify --head <main sha>`) fails.
   - That is rollback trigger 2 ("main's push `gate` is not green within 75 min"). It fires by construction, not by accident.
   - The body never mentions ci-ratchet or critical path. The roster carry on this group (diagnosis 2026-10-21: "must get main's ci-ratchet green by paying; a budget raise is refused while this payment exists") is not answered with a measurement.
   - U5b's `arch-instrument` split may be the payment. But no figure shows the path under 54.825, and even a sound payment needs 4 or more new push runs before the 8-run median moves.
   - Owed: either the window plan names how main's push gate goes green, or the payment is measured and the expected first-green push stated, with the rollback trigger adjusted accordingly.

2. **`reds-at-head` is weaker than the gate it stands in for.** During the window, `--disable` turns the whole ruleset off, and `reds-at-head` is the only check on the merge. It treats `GREEN = ("success", "skipped", "neutral")` and never checks that the required names are present. So it PASSes when an entire unit is skipped or absent. This is exactly the 4.2 hazard that `gate` exists to refuse ("Never skippable: a skipped required check passes").
   - My offline plants (`ev/reds_plant.py`, `ev/reds-at-head-plants.txt`):
     - the `tests` caller skipped with no `tests / *` jobs: PASS;
     - `tests / closures` skipped: PASS;
     - only the three base-pinned jobs and `gate` exist: PASS;
     - `codeql / Analyze (python)` neutral: PASS;
     - control, `tests / closures` cancelled: FAIL.
   - The self-test carries no skipped or absent plant: the mutant `GREEN` without `skipped` survives, 72/0.
   - The body's own reading of Arm B is "a FAIL that names only the three". The instrument does not implement that.
   - Cheap fix: require every name in `gate.REQUIRED[pr or pr-cc]`, less `BASE_PINNED`, to be present at H with `success`, and plant the absent and skipped cases.

3. **carry-missing: the body's four `## Forward-carry` items are not in the tree.**
   - They are: delete `pre_cutover`, delete gate.py's 17-renamed self-check, delete merge_train's A5 layouts pair, and measure `same_sha_dup_heads`.
   - Each says `Carry: R10-CI-LAYOUT-P2`, and `carry_audit.py check` routes all four (`ev/carry-audit.txt`).
   - But `finding-propagation.md` (Enforcement) requires the carry in the tree, with the body naming the file and the roster branch SHA. The body names neither.
   - `origin/handoff/audit-r10-roster` at d9b29967f holds 9 carries for R10-CI-LAYOUT-P2, none of them these; `pre_cutover` appears 0 times (`ev/roster-carry-count.txt`).
   - Roster carry 1 (`same_sha_dup_heads` before and after) is likewise still open at this head: the body defers it to Arm B.

4. **Hygiene: a head commit carries Claude trailers.** cc51e6626, "ci: record runs only at main; pin every write-holding governance job (U4 resume)", cherry-picked from 767a06f7f, ends `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` and a `Claude-Session:` claude.ai session link (`ev/cc51e6626-trailers.txt`, link redacted).
   - main merges by merge commit, so it would land on main.
   - It is the only one of the 57 commits with such trailers (`ev/footers.txt`).

5. **Unanswered reds at this head (step 11).** The head's code run 39949789023 concluded at 12:32Z. Its `pr-contract` started at 12:31, after the last red unit concluded (12:30:58), so the trigger stands. See `ev/ci-final.txt` and `ev/new-reds-logs.txt`.
   - **`tests / closures` is red, and it is this PR's red.** It reads `UNDER-SCOPED: tests/harness_headers.py really reads 2 file(s) the committed closure does not list: dev/audit/harnesses/r10_ci_layout_u5/run_part.py, .../unitcheck.py`. Those are the two files 9f7f443cc took out of INERT.
     - `closures-autofix` then printed `skip-classifier-disagrees -- THE REPAIR DID NOT HAPPEN`, so no bot commit is coming.
     - The body lists `tests / closures` and `closures-autofix` only as ancestry reds "fixed by 9f7f443cc and 4a83592e3". At this head they are red again, and `## Red checks` does not answer them.
     - The fix: `./tests/derive_closures.sh --single tests/harness_headers.py` on Linux, then commit `tests/closures.json`.
     - Cheaper detector: `closure.py check` over CI's own recordings of a probe head that includes 9f7f443cc.
   - **`pr-contract / pr-contract` is red** on main's pinned policy_lint: `ERROR [pr-body] check pr-contract / pr-contract is red and ## Red checks does not name it`. It is in the range's red history through #2658's runs, which the body discusses under "How to read it" but not under `## Red checks`. P2b's own policy_lint excludes that name; main's does not.
     - This makes a fourth base-pinned-style red, and `ruleset_cutover.BASE_PINNED` lists only the three governance jobs. So even with closures fixed, `reds-at-head` refuses H until the body names it, which a body edit settles.
   - `gate` at this run reads `FAIL run(s) [39949790607, 39949942238] at this head are still being judged`: the label and edit runs' preludes were still waiting at 12:33Z. Expected, and not judged here.

## Findings

- `--rollback` does not bind the copy it restores to the staged hash. It checks only an absolute path and exactly 17 contexts. A copy edited between `--disable` and `--rollback` (for example, enforcement or the `pull_request` rule) is PUT as is. The mutant deleting even the 17-count check survives the self-test (72/0, `ev/ruleset-mutants.txt`). Fix: store the six-key digest beside the copy at `--disable`, refuse a mismatch at `--rollback` and `--enable`, and plant both. Carry: R10-CI-LAYOUT-P2
- The integration id is pinned by nothing. The mutant `NEW_CHECKS = [{"context": "gate"}]` survives (72/0), because the self-test compares the PUT with `NEW_CHECKS` itself. The head's value is correct (15368), but a literal `15368` assertion is owed. Carry: R10-CI-LAYOUT-P2
- `--enable --merged M` accepts any commit on main (`compare M...main` ahead or identical). It does not check that M is #2662's merge, that is, a merge whose parents include H. Carry: R10-CI-LAYOUT-P2
- The window disables more than the required checks. `--disable` PUTs the whole ruleset 23698884 with `enforcement: disabled`, and that ruleset also carries the `pull_request` rule (code-owner review). For the window, main has only `main-protect` 22628467 (deletion and non-fast-forward), so a fast-forward push or an unreviewed merge by any writer is unguarded. The body says "enforcement: disabled" but not that review lapses too. Alternative for the operator: PUT the copy with only the `required_status_checks` rule removed and enforcement kept active. tvofi's ruling covers a ruleset-off window, so this is not a block. Carry: R10-CI-LAYOUT-P2
- P2a's `gate.py` self-test (lines unchanged here) does not kill the mutants "cancelled is success" or "PENDING ignored" (28/0). The design replay kills the cancelled one (`GATE-REPLAY2 rc 1`, output DIFFERS), so the predicate is pinned, just not by the fast self-test. Carry: dismissed: the design replay pins it, and the self-test's job is narrower

## Evidence

**RESULT lines**
- `RESULT perturb: 243 cases, 0 holes; pr=18 pr-cc=19 push=18`. This is my own harness (`ev/gate_perturb.py`), not the finder's. Every name `gate` owes, set to failure, skipped, cancelled, timed_out, absent or pending, FAILs and names itself. The nulls (all green) PASS for pr, pr-cc and push (`ev/gate-perturb-head.txt`).
- `gate self-test: 28 checks, 0 failed`. The design replay `r10_ci_gate_core.py replay` is rc 0, IDENTICAL to 1371a0a6. b3 parity is GREEN, and `--plant` reads RED (`ev/gate-core-head.txt`).
- Gate mutants (`ev/gate-mutants.txt`):
  - skipped-is-success: killed (1 failed, 37 holes);
  - absent-ignored: killed;
  - drop-browser: killed;
  - drop-governance-wave: killed;
  - cancelled-is-success: killed by the replay only;
  - pending-ok: killed by my harness only.
- `ruleset_cutover self-test: 72 checks, 0 failed`. The body's three mutants are killed (reds-any-red 2 failed, merged-always 1, disable-no-staged 1), and so are mine, disable-touches-rules and enable-keeps-disabled. Three survive, as listed above.

**(1) The gate.** `ci.yml` `gate` needs `[prelude, tests, codeql, governance, hassfest, validate, kernel-points, arch-score, budget-raise-gate, pr-contract]`, with `if: !cancelled()`. It restores `tools/ci/*.py` from the base and judges from the jobs API, not from `needs`. Every unit the predicate requires (`UNITS`) is wired. `kernel-points` is waited on but not required, as before: label-gated, and never in the 17. The non-unit jobs `refresh` and `cancel-superseded` are rightly not gated. The forgery pin refuses `statuses: write`, with planted fixtures (`tests/entities.py:19351-19417`), which closes the #2622 review carry.

**(2) Coverage parity.** The 17 old contexts map to `gate`'s 18 pr names, 7+3+3+1+1+1+1 plus `tests / arch-instrument`:
- `fast (3.14)`, `browser`, `briefs`, `typing`, `mutation`, `closures`, `closure-scope` → `tests / *`;
- `Analyze (actions|javascript-typescript|python)` → `codeql / *`;
- `policy-docs`, `wave-script`, `env-matrix` → `governance / *`;
- `hassfest` → `hassfest / hassfest`;
- `validate-hacs` → `validate / validate-hacs`;
- `budget-raise-gate` → `budget-raise-gate / budget-raise-gate`;
- `pr-contract` → `pr-contract / pr-contract`.

None is missing. The gate self-test asserts the equality against `pre_cutover`. None is weaker: the old contexts never refused a skipped job, and `gate` does. The extras are `arch-score` on pr-cc (D-2) and the push ratchets (B3).

**(3) ruleset_cutover.py.** I read it in full and wrote nothing to the network.
- `--disable` PUTs `{**six(copy), enforcement: disabled}` and reads all six keys back.
- `--enable` PUTs `payload(copy)`: the copy with `[{"context":"gate","integration_id":15368}]` and the copy's own enforcement, `active`. It requires the live state to be the disabled copy, and reads back both halves.
- `--verify` takes the newest `gate` of every check suite, which must be success, app 15368, at head.
- `--rollback` PUTs the copy's six keys and reads all six back. It is not hash-checked (see Findings).

**(4) Unit refs** (`ev/unit-cherry.txt`, `ev/unit-recut.txt`). `git cherry` against the head:
- u0c 3/3 `-`;
- u1u2u7 8/8;
- u3 1/1;
- u5, u6, u8, u9a, u9d and u10: every commit `-` except exactly the body's re-cut ones.

Each re-cut counterpart (b0bd2d25e and c9d647e64→20382dd99, 0c04d5da4→8f339b0fa, 4f3d54e14→2d5378a20, 1877542fd→ea38b17fe, c2143e8e8→e3b6c8730) is an ancestor of the head with an identical subject and file set. The dropped probe commits (65f112ec5, d4506f37e, 536fdb4b9, c758cb770, 14b8d768a, d924db603, 4cf31cc50, 89a4a44e7, 69a9279a5) are not ancestors, and no patch-id in a6620c30a..head matches any of them.

**(5) Red checks.** One bulk check-runs read at the head (38 runs at 12:00Z), then a jobs poll of the code run until `gate` concluded, at 12:33Z (`ev/ci-final.txt`). The final reds are:
- governance env-matrix, policy-docs and wave-script (base-pinned, below);
- `tests / closures` and `closures-autofix` (this PR's, Block 5);
- `pr-contract / pr-contract` (body, Block 5);
- `gate`.

Everything else required is green: `tests / fast (3.14)`, `arch-instrument`, `browser`, `briefs`, `typing`, `mutation`, `closure-scope`, the three codeql `Analyze`, `hassfest`, `validate-hacs`, `arch-score`, `budget-raise-gate` and `instrument-self-tests`. That makes `tests / fast (3.14)`, which runs `tests/entities.py`, green at this head. The three base-pinned reds are base-pinned in both the workflow source and the logs:
- `governance.yml`'s three jobs restore with `PINNED = pull_request.base.sha` (`ev/base-pinned-source.txt`);
- wave-script, job 120401311490: `PINNED: a6620c30a`, then main's `agreement_py` raises `FileNotFoundError: '.github/workflows/budget-raise-gate-rerun.yml'`, a file this PR deletes;
- policy-docs, job 120401311410: main's policy_lint, `TOTAL: 37 error(s)`, `[required-contexts]`;
- env-matrix, 120401311248: failure. I did not read its log; the restore source is the same.

The ancestry reds on a0f525900 are each answered in the body with a cause, a fixing commit (ff7244ac0, 1cce735c3, 9f7f443cc and 4a83592e3, all ancestors, `ev/ancestry-fixes.txt`) and a cheaper detector. At this head, `tmp_paths --check` reads 0 refused, `tests/layout.py` reads ok, and `brief_lint` reads ok. #2658's pr-contract reds are answered as root-cause-detectable (`carry_audit.py check`).

**(6) Hygiene.**
- The three-dot diff is 107 files (`ev/files.txt`), equal to the PR's `changed_files` 107. The body has no file list to compare beyond the Approval list, and those paths are all in the diff.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (0 diff lines).
- `git merge-tree --write-tree origin/main HEAD`: rc 0, tree 42b0b14ec, clean (`ev/merge-tree.txt`).
- `closure.orphan_files()` reads 0. `tests/entities.py` could not run locally: homeassistant is not installed in this container (`ev/entities.txt`), so its result is CI's `tests / fast (3.14)` at this head (`ev/ci-final.txt`).
- Scoped gate: `MODE: FULL -- every test script runs, nothing is scoped out.` (`ev/scope-mode.txt`). The diff touches workflows and tests.

**Body figures re-derived** (`ev/figures.txt`):
- `selftest_wiring: 91 self-testing, 91 wired, 0 unwired`;
- policy_lint against the live ruleset: TOTAL 0, with the PRE-CUT-OVER note;
- `ruleset_cutover` 72/0;
- `gate` 28/0;
- `ghapi` 19/0.

**Harnesses.** The group names no finder harness for the gate beyond the design's oracles (`r10_ci_gate_core.py`, at 1371a0a6), which I ran. `gate_perturb.py` and `reds_plant.py` are mine, disclosed here and kept in `ev/`.
