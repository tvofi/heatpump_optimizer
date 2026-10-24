`tools/pr/ci_predict.py` predicts three CI reds that no handoff check saw. The first is the layout guard `fast` runs (#2554's forward-carry, item 4ddebe42). The other two are the reds #2671 reached CI with, both carried to this group from dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md: `wave-script`'s agreement lane run with the base's copy (countermeasure A), and `instrument-self-tests`' `ref_privacy.py --check` (countermeasure B). Part of #2505 (R10-FLY-CIPREDICT-LAYOUT, carved out of R10-ORCH-MACHINERY's row G).

`body_push.sh` refuses a handoff only on what `ci_predict.py` predicts, plus the pr-body lint. Before this change:
- `prepr.sh` ran the layout guard (`moved_line`), but the predictor did not.
- `prepr.sh` step 3f4 runs the agreement lane with the head's copy. That is push-to-main's direction. CI grades a pull request with the base's copy (governance.yml's wave-script restore).
- No local path ran `ref_privacy.py --check`.

The arms:
- **LAYOUT** (`layout_preds`, `tests / fast (3.14)`) calls `tests/layout.py`'s own `guard` over the commit HEAD, against the merge base, with HEAD's `tests/layout.json`.
- **REF PRIVACY** (`privacy_preds`, `governance / instrument-self-tests`) calls `ref_privacy.py`'s own `sites`/`grep`, `registry_refusals` and `content_check` over the commit HEAD. It judges with the runner's identity, as CI's run does. Running `--check` itself on a seat would add the seat's home and name to the classes. `_leaks` matches the home as a substring, and the root account's home is inside the path of the root-cause role contract, which 28 tracked files cite; on a root seat each of them would refuse (see `## Forward-carry`).
- **AGREEMENT** (`agreement_preds`, `governance / wave-script`) runs only when the three-dot diff touches a file the lane loads (`lane_files`). That set is `agreement_py.closure`, the restore precondition's own derivation, plus the `.mjs` files `agreement.mjs` imports or `load`s/`at`s, transitively. The run builds CI's tree in a throwaway clone:
  - HEAD is merged into the base tip, base first, with GitHub's `Merge <head> into <base>` subject;
  - every pathspec of the job's restore step (`agreement_py.restore_specs`, read from the merge's `governance.yml`) is checked out from the tip;
  - `refs/remotes/origin/main` is set to the tip;
  - then `agreement_py.py --out` and `agreement.mjs --py-json` run.

  A base that does not carry the lane predicts nothing for this arm, because the job skips it. A head that does not merge is predicted `AGREEMENT UNMERGED`.

Each arm prints `PREDICT <check> <ARM> ...` and its own `CI PREDICT:` repair line, and sets rc 1. The AGREEMENT repair line says that a registration only the head's copy carries has no local repair (the RCA's cause 3, carried to R10-MERGE-SUBJECT-HARDEN).

Alternatives considered:
- An AGREEMENT key on any wave-script restore pathspec (the RCA's A'). Rejected on the cost test below: about 2.3 times the trigger rate for the same verdict.
- Running prepr step 3f4 under the base's copy. The handoff (`body_push.sh`) runs only this predictor, so step 3f4 would still not refuse a handoff. Step 3f4 itself is `prepr.sh`'s, outside this one-module group (`## Forward-carry`).
- Calling `ref_privacy.py --check` as a process. That is the seat-identity run above. Its 28-file false refusal on root seats would block those seats' handoffs.

## Head

`7ff66e5a521d5fe3c3c8e2bdea0cb05c1a0a85c3`. It continues the round-1 head `cd7dc09a8` with `origin/main` merged in (`6b5183c5e`), and its merge base is `origin/main` `e97f5749b441b282e43bd99dbcbb762e9d10a369`. Every figure below was taken at this head unless it names `6d4c233af`, `1f62fdc1a` or `9cd9b78df`, its parents on this branch; those differ from it only in `plant_self_test`, a `--no-renames` flag and a docstring. The figures were taken on 2026-10-24 from 14:20Z to 16:45Z, with `origin/main` at `e97f5749b` until about 16:30Z. It then moved to `806aa2ce8` (`git ls-remote origin main` at the handoff). That move changes one file this diff reads, `tools/audit/seat/ref_privacy.py` (`git diff --name-only e97f5749b...806aa2ce8`, #2700's `d4e766136`): `grep` gains a defaulted `root` and a portable prefilter. The head was not merged forward. As a control, a throwaway merge of this head with `806aa2ce8` prints `ci_predict self-test: 0 failed`, and its predictor prints `no closures, fast, wave-script or instrument red predicted against 806aa2ce89ae`; `git merge-tree --write-tree origin/main HEAD` exits 0. Python 3.14.7 at `/opt/hpo/venv-ci`, node 22.

## Mutation proof

The arms' red cases failed before each arm existed. Mutants A1, B1 and M1 below (an arm not called) are that state. Each mutant is one single-occurrence replacement in `tools/pr/ci_predict.py`. A one-off driver in the seat's scratch applied each replacement, ran `python3 -I tools/pr/ci_predict.py --self-test` and restored the file; `git status --short` was empty afterwards. It is not landed: the replacement column is the whole of it, and the in-tree self-test is the pin.

| mutant | replacement | rc | failing checks |
|---|---|---|---|
| NULL | none | 0 | none |
| A1 privacy arm not called | delete `preds += privacy_preds(root)` | 1 | `an unregistered push site is predicted red`, `a guarded pusher's guard dropped in HEAD and restored in the index is predicted red` |
| A2 seat identity | `rp.content_check("HEAD", root)` in place of `..., runner)` | 1 | `a line that pushes nothing and names the seat's home is predicted green (null control: ...)` and the three staged-not-committed nulls |
| A3 registry text from the worktree | `(root / p).read_text()` in place of `show(root, "HEAD", p)` | 1 | `a guarded pusher's guard dropped in HEAD and restored in the index is predicted red` |
| A4 refusals dropped | `return []` in place of the arm's return | 1 | the two privacy red cases |
| A5 repair line dropped | `if False:` for the REF PRIVACY repair | 1 | the two privacy red cases |
| B1 agreement arm not called | delete `preds += agreement_preds(...)` | 1 | `a grammar registered only in the head's copy is predicted red` |
| B2 no restore from the base | the pathspec checkout disabled | 1 | that red case, and `a head copy of the lane that exits 1 is predicted green (null control: CI runs the base's)` |
| B3 no key | `hit = sorted(lane_files(root))` | 1 | `a grammar in two files the lane does not load, the lane untouched, is not run (null control: the key; ...)` |
| B4 HEAD, not the merge | `git checkout HEAD` in place of the merge | 1 | `a grammar the base tip shares and registers, under a HEAD that only edits the lane, is predicted green (CI merges HEAD into the tip)` |
| B5 origin/main not set | delete the `update-ref ... origin/main` | 1 | `a lane edit under a branch merge, main already past it, is predicted green (null control: CI's origin/main is the base)` |
| B6 verdict dropped | `if True: return []` | 1 | `a grammar registered only in the head's copy is predicted red` |
| B7 repair line dropped | `if False:` for the AGREEMENT repair | 1 | the same case |
| M6 manifest from the worktree | `(root / layout.MANIFEST).read_text()` | 1 | `the re-added path with its entry dropped from the staged manifest is predicted red` |
| M7 UNREADABLE dropped | `return []` in place of the `LAYOUT UNREADABLE` return | 1 | `a manifest that does not parse is predicted red` |
| M8 guard from HEAD~1 | `layout.guard(root, manifest, <HEAD~1>, "HEAD")` | 1 | `the re-added path under a second commit is predicted red` |

Fix review round 1's survivors M6, M7 and M8 are killed by the three layout cases added for them. Round 1's M1–M5 are unchanged in the code and stay killed: M1 (arm not called) and M3 (the guard on the index) fail the same cases they failed in round 1's table. A3, B3, B4 and B5 survived the first run, at `6d4c233af` (rc 0, 0 failed each). `1f62fdc1a` and `9cd9b78df` added the four cases that pin them:
- the guard dropped in HEAD and restored in the index (A3);
- a lane edit under a base tip that shares and registers a grammar HEAD lacks (B4);
- an unregistered grammar in files the lane does not load (B3);
- a branch merge with a non-template subject under a `main` already past it (B5). Under B5 that case printed `merge-subject-pr c5df709e8 "Merge branch 'side' into plant"` refused, which is the RCA's refused=3 shape.

## Null control

- In the self-test, each arm's nulls run in the same throwaway clone as its plants:
  - a line that cites, pushes and registers nothing;
  - each red plant staged and not committed;
  - a line naming the seat's home (`SEAT_HOME`, set as the predictor's `HOME`);
  - a head `agreement.mjs` that runs `process.exit(1)` first;
  - the base-tip registration;
  - the non-lane grammar;
  - the branch merge under a later `main`.

  Each prints no line for its arm and exits rc 0. `python3 -I tools/pr/ci_predict.py --self-test` at this head prints `ci_predict self-test: 0 failed`.
- On this head's own diff, the predictor prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against e97f5749b441`, rc 0. AGREEMENT is not keyed: the lane-key probe below prints `key []` for this diff.
- **Both ends, against the RCA's controls.** Each run was done in a `git clone --shared` of this repository at the pull request's head, with the predictor file copied in, running `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base <PINNED>`. "Base" is `git show e97f5749b:tools/pr/ci_predict.py`; "head" is this head's file.

  | end | tree | predictor rc | wave-script / instrument lines | wall |
  |---|---|---|---|---|
  | base | #2671 `338c9ba49` against `fd7e289d0` | 0 | none | 2.8 s |
  | base | #2669 `0506a55b2` against `e6dd46277` (null) | 0 | none | 2.5 s |
  | head | #2671 `338c9ba49` against `fd7e289d0` | 1 | `AGREEMENT RESULT divergent=0 unregistered=3 dead=0 refused=0` with CI's three UNREGISTERED grammars (`[0-9a-f]{40}`, `\bledger_open ([a-z-]+) `, `\blevel_line ([a-z-]+) `); `REF PRIVACY REFUSE tools/audit/seat/ledger.py:726` | 11.9 s |
  | head | #2669 `0506a55b2` against `e6dd46277` (null) | 0 | none | 11.5 s |

  The head rows reproduce the RCA's table and CI's verdicts: run 39996377402's red `wave-script` and job 120560854278's `ledger.py:726`, and job 120594524199's `AGREEMENT ok` on #2669. The null ran the arm and did not skip it. The lane-key probe (`ci_predict.lane_files` intersected with the three-dot diff, in the same clone) prints `key ['tools/policy/agreement.mjs', 'tools/policy/agreement_py.py', 'tools/policy/budget_raise_gate.py', 'tools/policy/policy_lint.mjs']` for #2669 and `key ['tools/policy/agreement.mjs']` for #2671. The 11.5 s, against the base end's 2.5 s, is the lane's own run.
- The old local path, at #2671's tree, is green. That is the defect: the lane under the head's copy (step 3f4's run, `origin/main` set to `fd7e289d0`) prints `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`, rc 0. `ref_privacy.py --check` there prints `1 refused`; at this head it prints `0 refused`.

## Figures

- `python3 -I tools/pr/ci_predict.py --self-test` -> `ci_predict self-test: 0 failed`, with 3 carry, 7 layout (5 red, 2 null), 4 privacy (2 red, 2 null) and 7 agreement (1 red, 6 null) cases `ok`, and `every JOB value is a name gate.REQUIRED owes`. The JOB check exempts `instrument-self-tests`, which is no required context; its red is predicted because a red check is still owed an answer. Wall time 120 s at this head, against round 1's 11.8 s: the agreement cases run the lane 5 times. `governance.yml`'s "Show the CI predictor" step runs it, inside `instrument-self-tests`' 20-minute timeout.
- Standing cost per handoff on a diff the lane key misses: the head predictor took 2.9–3.3 s and the base predictor 2.3 s, over 3 alternating runs on this head's diff (`time` around each `ci_predict.py --base origin/main`). Of that, `lane_files` measured 0.58 s and `privacy_preds` 0.26 s, timed in-process.
- Trigger rate, the cost test re-measured at this merge base, by a scratch probe over `git log --first-parent --merges --since=2026-10-09T00:00 --until=2026-10-24T00:00 origin/main` (the RCA's window): `merges 456 | touching the lane's closure (20 files) 62 | touching a restore pathspec 142`.
  - Rule: a merge counts when `git diff --name-only M^1 M` meets `ci_predict.lane_files` at this tree, or meets `agreement_py.covers` over the restore specs.
  - Controls: #2669's merge `5c9828fe5` counts (`lane-touching=True`); #2650's record merge `8cea0d2cf` does not (`lane-touching=False`).
  - The key's 62 (13.6 %) is above the RCA's 25 of 440. The RCA counted 5 `.mjs` files; this key adds the 14 Python readers the restore precondition derives.
  - Cost: at the arm's measured ~11 s over the base end, the standing cost is 62/456 × 11 s = 1.5 s per PR. Keyed on any restore pathspec, it would be 142/456 × 11 s = 3.4 s. The RCA's expected defect cost is 4.1 s (0.68 % × 600 s CI floor), so the narrow key passes the cost test and the wide one passes with less margin for no added verdict.
- `python3 tests/closure.py select --diff e97f5749b441 --workdir "$D"` -> `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` The changed files are `tools/pr/ci_predict.py` and `dev/programme/delivery/2707.md` (the orchestrator's row, carried by `cd7dc09a8`).
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff e97f5749b441` -> `Architecture score: dS +0.0000 NULL`.
- `python3 -I tests/throwaway_git.py --check` -> `0 raw git init or clone site(s) refused`. Both clones go through `throwaway_git_clone`.
- `python3 -I tools/audit/seat/tmp_paths.py --check` -> `tmp_paths: 0 refused`.
- `python3 -I tools/audit/seat/ref_privacy.py --check` -> `0 refused`. The privacy plant's own push-site line is split across two source lines so that the file is not a push site; the runner identity's home is built, not spelled. The arm itself first caught the spelled home, refusing the `privacy_preds` line that spelled it in the self-test's staged-plant nulls.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> `93 self-testing, 93 wired, 0 unwired`.
- `python3 -I tests/layout.py --guard --base e97f5749b441` -> `GUARD: 0 refusal(s)`.
- `bash tools/pr/prepr.sh <this body>` -> `PRE-PR: 7ff66e5a521d5fe3c3c8e2bdea0cb05c1a0a85c3 000000000000000001000000`, rc 1. Its one refusal is the closures step, `failed while being recorded: tests/entities.py (exit 1)`, which is the seat's recorder (`## Red checks`). Every other step is `ok` or `skip`, including `self-test 352 passed, 0 failed`, `wave-script 209 passed, 0 failed`, `agreement lane` and `ci predict`.
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` -> `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`.
- **The class census (fixer step 8), widened.** The class is a CI red that the handoff (`body_push.sh` = `ci_predict.py` plus `prepr.sh --body-check`) does not predict, either because no handoff check runs CI's command, or because one runs it in the other copy's direction. Round 1's rule (`*_line` functions) missed step 3f4. There are three rules now.

  **Rule 1, every `prepr.sh` step:** `grep -nE '^# --- [0-9]+[a-z0-9]*\. ' tools/pr/prepr.sh` returns 29 steps.
  - Local preconditions with no CI check of their own (6): 0 shared root, 1 merge base, 1a transport, 1b0 gate priority, 1b heavy slot, 2 MODE line. Not in the class. 3g (`pinned_verdict`) is a local meta-check over the other steps; also not in the class.
  - 3f4 the agreement lane: **closed in this diff** (AGREEMENT).
  - 6e the layout guard: **closed** (LAYOUT, round 1).
  - 6d: this predictor.
  - 7 the body: run by `body_push.sh` through `--body-check`.
  - 6b scoped recordings: predicted statically by the closures arms, by design. A recording is not static, and `closures-autofix` repairs it after the push (`ci-autofix.md`).
  - 5 version untouched: no pull-request check reddens on it; the stamp refuses it after the merge.
  - **Open seams, carried (`## Forward-carry`)**:
    - The base-pinned graders, run locally only with the head's copy, which is 3f4's direction gap: 3 `policy_lint`, 3a corpus acceptance, 3b `rules_sync --check`, 3c fragments, 3d hooks, 3e `codeowners_gap --check`, 3f `brief_lint`, 3f3 field coverage (`policy-docs`), and 4 `check-wave-script` (`wave-script`). 3f3 is the RCA's probable #2636 instance.
    - Run by `prepr.sh` but by no handoff check: 3f5 the register check, 3f6 `tmp_paths --check`, 3h the governance self-test, 6/6a claim files and `INHERITED CLAIMS` (`claims_line`), 6c `no-copies` (`copies_line`) and 6f `throwaway_git --check`. The last three were already carried in round 1.

  **Rule 2, the tree-reading checks of `instrument-self-tests`, which `prepr.sh` may not run at all:** `awk 'NR>=243 && NR<940' .github/workflows/governance.yml | grep -nE -- 'python3 -I [^ ]+ --check\b'` returns 4 (lines 243 and 940 bound the job, from `grep -n '^  [a-z-]*:$'`).
  - `ref_privacy.py --check`: **closed in this diff** (REF PRIVACY).
  - `tmp_paths.py --check` and `throwaway_git.py --check`: prepr steps 3f6 and 6f, open seams of rule 1.
  - `selftest_wiring.py --check`: open seam. The RCA measured 0.14 s and no instance, and left it uncosted. Carried with the rest.

  **Rule 3, `fast`'s always-run scripts, which a fixer runs by hand (fixer step 5) and no handoff check runs:** `grep -nE '^\s*run_always "\$PYTHON"' tests/run.sh` returns 4.
  - `tests/layout.py`: its guard is **closed** (LAYOUT). The rest of it is the layout self-test.
  - `tests/env_drift.py --claims-only`: `claims_line`, carried in round 1.
  - `tests/closure.py selftest`: open seam. It refused this diff at `9cd9b78df` (`no rename-detecting --name-only diff under RENAME_SITES`, on the restore list's `git diff`), and `7ff66e5a5` repairs that with `--no-renames`. The fixer's step-5 run caught it before any push; no handoff check would have.
  - `tests/harness_headers.py`: open seam.

  Both open seams are carried.

## Unpinned sites

n/a: `ci_predict.py --base origin/main` prints no `ADDED UNPINNED` line for this diff (prepr step 6d). Every mutant in `## Mutation proof` is killed by the in-tree self-test.

## Red checks

- At round 1's head `cd7dc09a8` (check-runs API, read about 14:35Z): `pr-contract / pr-contract` (job 120891274769) failed at 14:02:26Z, 3 s after `tools/ci/codescan_wait.py` started, while `codeql / Analyze (python)` was still `in_progress` (it was still `in_progress` at the read). `gate` (job 120892151815) failed after it. This is the known transient: codescan_wait exits 1 while an Analyze is unfinished, so it is no body defect and no diff fault. The cheaper detector would be a wait that exits on an unfinished Analyze without failing. That is `codescan_wait.py`'s, not this group's, and its standing cost is nil. No CI run exists at this head yet. This answer is owed again only if the check is red at this head after codeql concludes, which the next reader of the check-runs API decides.
- Locally, `prepr.sh`'s closures step refused, because the strace recording of `tests/entities.py` exits 1. Null control: `tests/derive_closures.sh --single tests/entities.py --record-only --out-dir D`, run at the same time at this head and in a worktree at the merge base `e97f5749b` without this diff. Both exit 1 with `2 of 2425 ENTITY CHECKS FAILED`, and the same two checks fail at both ends: `gate-sweep.yml: on CI's completion, no concurrency, ...` and `graders-head-copy's delivery_status step is red only when ...`. The FAIL lines of the two outputs differ only in measured milliseconds and set order (`diff` of their first 80 columns: 3 lines, all `hb:positive_control` timings and one `a8:register_once` set order). Round 1's two failures were `hb:positive_control` tries under the same recorder, also at both ends. So the refusal comes from the seat's recorder environment and says nothing about this diff, as in round 1. CI's `closures` job does the recording that counts (green at `cd7dc09a8`). The cheaper detector would be the base recording itself, about 19 min (1115 s measured at `6d4c233af`), which is the same cost as the gate. None is built; the condition is under `## Friction`.
- The self-test's reds before each arm existed were the failing tests, written first.
- `main`'s possible push-CI red on `tests / ci-ratchet` is not this diff's: the diff touches no ratchet file.

## Forward-carry

- The base-pinned graders other than the agreement lane still have only a head-copy local run: prepr steps 3, 3a–3f, 3f3 and 4 (rule 1 above). A diff to one of them is graded by CI with the base's copy, as #2671's lane was. Precondition for the stage, with its control: run each grader under its job's restore (`policy-docs`' and `wave-script`'s restore steps), keyed on the diff touching that grader's load closure, as `ci_predict.agreement_preds` does for the lane. The arm must fire on a plant registered only in the head's copy and stay quiet when the head's copy alone is broken (this PR's `plant_self_test` pair). Re-measure the trigger rate at your merge base with this body's rule (`## Figures`). Carry: R10-FLOW-JIDOKA
- `fast`'s always-run `tests/closure.py selftest` and `tests/harness_headers.py` (rule 3): run by no handoff check. `closure.py selftest` refused this diff's restore-list `git diff` at `9cd9b78df` until `--no-renames` (`7ff66e5a5`). Control: the same plant/null pair as below. Carry: R10-FLOW-JIDOKA
- Run by `prepr.sh` but by no handoff check: step 3f5 (the register check), 3f6 `tmp_paths.py --check`, 3h the governance self-test and `selftest_wiring.py --check` (rules 1 and 2). Control, as for the arms here: a planted violation must make the predictor refuse, and a null plant must keep it quiet. Carry: R10-FLOW-JIDOKA
- `ref_privacy.py`'s `_leaks` matches a seat's home as a substring. On a seat running as root, any added line citing the root-cause role contract's path (under `dev/governance`) refuses as `home-directory`, because the root account's home is inside that path. Measured: `ref_privacy.content_refusals` over one added line citing that path, with `Identity.made` of the root account's home and name, returns one `home-directory` refusal; with the runner's identity it returns none. `git grep -c` of the path's basename over `origin/main -- dev tools` -> 28 files. The same match refused two docstring lines of this diff at `9cd9b78df` on this seat, and those lines were reworded. Precondition: a local `ref_privacy.py --check` on a root seat is not CI's verdict. Judge with the runner's identity, as `privacy_preds` does, or bound the home match at a path edge. No live group owns `ref_privacy.py`, so this goes to the stage that ports its local runs. Carry: R10-FLOW-JIDOKA

## Friction

- gate-scoping: cost: on this cloud seat, `prepr.sh`'s closures step refuses any diff that reaches `tests/entities.py`, because its strace recording exits 1 at the base as at the head (`## Red checks`). Each occurrence costs about 19 min of recording to show that. Round 1 carried the same. Carry: R10-POLICY-GATE-SCOPING
