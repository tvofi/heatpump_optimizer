Fix review: merge 699491f2368ddcd96c0fb14cf6040155f66f5c44

bus-nonce: 0e62cf870d0d64d1a06f202c173bc082

## Round

Fourth fix-review round of PR 3297. Earlier rounds: blocked 9cf0b6108 (mutation-vacuous), merge 2d010b091, blocked 7fe24f9f6 (merge-conflict). This round is a fourth, so `fixer.md`'s re-cut clause applies from here. This verdict is `merge`, so no re-cut is owed.

What I reviewed, from a detached worktree at 699491f2368ddcd96c0fb14cf6040155f66f5c44:
- the whole fix again;
- the merge delta, which is the authored code head 9c59a9ea9 ("Conflict resolution 3") plus an automatic merge of origin/main 19865e5a8.

`review_carry.py 9c59a9ea9 699491f23` prints `CARRY`: the two branch-only commits are both merges.

## Evidence

- RESULT head=699491f2368ddcd96c0fb14cf6040155f66f5c44 merge-base=19865e5a866ce066eaa52f7167a7d901fd1d5968=origin/main (ev/HEAD.txt). `git ls-remote` still printed this head for `fix/r10-hotfix-cop-unmeasured` when I wrote the verdict.
- `## Head` in the body names this head, and its code head is 9c59a9ea9.
- `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the role contract I followed is current.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 699491f23` rc=0, tree 0dc74eac7, no CONFLICT line (ev/merge_tree.txt).
- RESULT resolution delta, thermal_model.py: `git diff 20e83746f 9c59a9ea9 -- thermal_model.py` adds only this branch's lines and deletes 0 lines. `git diff 7fe24f9f6 9c59a9ea9` on the same file adds only main's lines: `on_off`, `declared_modulation`, `_onto_band` and `project_space_against`. The union is clean and drops nothing from either side.
- RESULT mutants. Each one ran the whole `PYTHONPATH=tests/hastub python3 tests/features.py` in its own worktree at the head (ev/mut_*.txt, driver ev/mut_driver.py, which is my own instrument):
  - CTRL (unmutated): rc=0.
  - M1, `if measured:` -> `if True:` (coordinator.py:5466): rc=1, `3 of 4987 FEATURE CHECKS FAILED`. The three failures are the no-heat null control, the Tuya check and the metered-records check.
  - G, measured_cop load ungated (coordinator.py:4637): rc=1, `1 of 4987`. The failure is "a last COP stored before measured provenance does not load as measured ...".
  - M4, `_estimated` id rule -> `return False` (thermal_model.py:1447): rc=1, `3 of 4987`. The failures are the Tuya, probe_install and cop_observability checks.
  - M7, `and (self.heat_sees_dhw or not dhw)` deleted (thermal_model.py:1305): rc=1, `1 of 4987`. The failure is the metered hot-water check.
  - All four match the body's counts and names. The 4987 check total matches the body's `ALL 4987 FEATURE CHECKS PASSED`.
  - RELEC, `and self.cop_electric()` deleted: rc=0, so it survives. See Findings.
  - Mutants M3, M5, M6 and the CUSUM/DOMAINS mutants were not re-run. coordinator.py, store.py and accuracy.py are unchanged by the merges, per the body's `git diff 7fe24f9f6 9c59a9ea9`. Round 2 killed them at 2d010b091.
- RESULT null control: M1 turns the brief's null-control check red ("inferred 2.5533587538536424 model 2.5533587538536424 ... scale samples 1"), so the control moves under its own perturbation. I did not re-take the base transplant. Rounds 1 and 2 hold it.
- RESULT figures re-derived at the head (ev/cheap.txt):
  - `option_doc_coverage.py`: `option_fields_rendered=208`, `option_schema_keys_rendered=241`, `option_fields_undocumented=0`.
  - `claims.py`: `claims_false=0`. It left the tree clean (no regenerated diff).
  - `tests/structure.py`: STRUCTURE RATCHET PASSED.
  - Class rule `git grep -n -e "_measured_cop.record(" -e "_observe_cop_health(" -- custom_components`: coordinator.py:5467-5468 and the `def` at 9516 only.
  - `git grep -n "InstallCapability("`: thermal_model.py:1385 only.
  - All of these match the body.
- RESULT archscore: `score.py --diff 19865e5a8 HEAD` printed `Architecture score: dS -0.0023 WORSENS (inadmissible: coord_footprint 2489->2493)` (ev/archscore.txt), the body's figure. Rounds 1 and 2 judged the +4 justified, with no sound in-seam payment. The merges add no production statement of this branch's, and no `*_budgets.json` is touched.
- RESULT drift: `env_drift.py --all 19865e5a8` rc=0 (ev/env_drift.txt).
  - It printed `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`.
  - Every claim moved: `CLAIMED config_flow: 7 leaves`, and `coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal`, `coord_two_zone` at 2 leaves each.
  - `git diff origin/main HEAD` on both claim files adds 11 lines and deletes 0 (ev/claim_files_vs_main.diff). Both `claims-for: 7.1.8` = VERSION 7.1.8.
- RESULT version: the three-dot diff touches no `VERSION`, `RELEASE_NOTES.md`, `manifest.json` or `*_budgets.json`.
- RESULT CI. I read the check runs at this head:
  - Code run 42539691216 is all green:
    - `gate` job 128935101531: success at 01:47:29Z.
    - `tests / fast (3.14)`: success.
    - `tests / mutation`: success.
    - `pr-contract / pr-contract` job 128934844339: success, 01:45:56Z-01:46:50Z.
    - codeql, governance, closures, coverage, browser: all success.
  - `merge_train.py classify 699491f23 --pr 3297` exits 1 with `RED 699491f2368ddcd96c0fb14cf6040155f66f5c44 pending: none red: gate` (ev/classify.txt). The red it reads is the edit run's `gate` (run 42545491668, job 128931394723, 01:35:15Z), whose whole log is `FAIL run(s) [42539691216] at this head are still being judged; their gate decides`. That is gate.py's `deferral`. The run it defers to has since concluded success.
  - classify keeps the worst latest gate per check suite (`latest_runs`, A5). It treats a deferral as a wait only while `busy` names an unfinished run, so once the code run finishes, the edit suite's deferral red stays red. I judge the head as GREEN on that basis, and say so explicitly: the only red is a deferral whose deferred-to gate is green, and it carries no defect of this diff.
  - Step 11: the `pr-contract` run at 01:45:56Z started after the last red (01:35:18Z) concluded, and it is success, so the body check stands. The earlier `tests / fast (3.14)` red at 7fe24f9f6 is answered in `## Red checks`.
- Forward-carry: the body says `none`. Its two `## Friction` items carry valid markers (packet carry_audit: 2 routed, 0 unrouted).

## Findings

- Follow-up: the edit run 42545491668's deferral `gate` (job 128931394723) keeps `merge_train.py classify` at RED (rc=1) after the code run's gate concluded success. The train will refuse this head until that edit run's gate job is re-run, which needs no code change. The instrument cause: `latest_runs` keeps a stale deferral red per suite once `busy` is empty. So any PR whose body edit lands while the code run is busy reads RED after a green code run. Carry: #201
- Follow-up: round 2's unpinned conjunct is still unpinned at this head. Deleting `and self.cop_electric()` from `InstallCapability.cop_measured` (thermal_model.py:1303) passes the whole `tests/features.py`: rc=0 over 4987 checks (ev/mut_RELEC.txt). It is reachable only through `machine_score(..., cop_measured(False))`. On an install with a heat counter and no electric counter, it would publish `cop_watch_learning` instead of `cop_unmeasurable`. The production line is correct and the grade is None either way, so it does not block a hotfix. What is owed: one fresh-install check that a heat counter with no electric counter grades `cop_unmeasurable`. Round 2 carried this to this PR's own group. The body neither paid nor dispositioned it, and the group closes with this merge. Carry: #201

## Friction

- My first CI watcher after the container restart used `pgrep -x` on the waiter script, which the brief forbids. I stopped it unused and waited on the waiter's own exit instead. Carry: dismissed: seat slip, corrected before it read anything
