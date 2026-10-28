Fix review: merge 89b04b74feaef1c0696fca1f353c9532c6792374

bus-nonce: 2de9970ab64dc3f7cac26d7e10be96af

## Round

Round 1. Reviewed head 89b04b74feaef1c0696fca1f353c9532c6792374, base b0b2d7697f8c5baaef2c082d9bf3242b57249e68 (origin/main), from a detached worktree. dev/governance/roles/ is unchanged between the merge base and origin/main, so the contract is current.

## Findings

- The template's step (1) dispatch gate ("fewer than 3 handoffs wait without a pull request and 6 to 10 pull requests are open") is a number that no rule file and no instrument owns. `pr_cap.py dispatch-gate` counts only roster `in-progress` groups against HPO_WIP_CAP (default 6). The body discloses this as point 1. The same goes for the placeholder table's "10 unless the owner set another" and "99" for `plan_slots` and `plan_seats`, while `tools/plan/replan.py` DEFAULT_CAPS is slots 6 and seats 8. The group that owns the open-PR and handoff arms of the gate is the not-started R10-FLOW-WIP, whose brief already names both arms; its fixer should take the figures from the ruling, not from this template. Carry: R10-FLOW-WIP
- `dev/governance/roles/standing-merge.md` lists the train flags without `--pre-flight` and `--mandate`, so the template's default is a superset of it (body point 2). This is not a contradiction, and standing-merge.md is policy, which a fly-in rightly leaves alone. Carry: dismissed: superset, no contradiction
- A surviving mutant: deleting steps (4c) and (4e) from the template leaves the self-test at 24 checks, 0 failed (ev/mut-M7-drop-4c-4e.txt). Likewise, steps (0)'s OWED clause, (1)'s caps and model routing, and (4d) are not pinned by DEFAULTS. The body states that DEFAULTS pins items 2, 3 and 8 only, so the scope is disclosed. Carry: dismissed: prose steps, pinned scope disclosed

## Evidence

- RESULT self-test at head: `sweep_render self-test: 24 checks, 0 failed`, rc 0 (ev/self-test-head.txt). This matches the body.
- RESULT base template with the new renderer: `22 checks, 2 failed`, rc 1. It is missing exactly the six DEFAULTS names, and the render null control fails on `plan_slots` (ev/base-template-new-renderer.txt). This matches the body's figure.
- Mutation proof, re-run by me: each production or template mutant below failed the self-test (rc 1, files ev/mut-*.txt):
  - M1: `defaults_missing` returns [].
  - M2: `--skip-bad` dropped.
  - M3: `OWNER FLAG:` dropped.
  - M4: `plan_page.py --plan` changed to `--input`.
  - M6: (4b) deleted.
- M5 disables the new self-test arm itself, which is a test mutant rather than a production one. It passes, as expected; it is recorded as evidence and is not a vacuity finding.
- Null controls: `a sweep carrying every default fragment misses none` and `a sweep without the train flags is reported missing exactly them` are both ok at the head.
- I checked by hand that every flag and argument the template cites exists in the tree at the head:
  - `replan.py` `--out`, `--slots`, `--seats`.
  - `plan_page.py` `--plan`, `--html`.
  - `pr_cap.py` `dispatch-gate`.
  - `roster_lib.py` `critical_path`.
  - `train.sh` and `merge_train.py` `--overlap`, `--approval-carry`, `--skip-bad`, `--free-holders`, `--bot-prs`, `--pre-flight`, `--mandate`.
  - `tools/pr/gate_priority.py` and `tools/pr/cancel_superseded.py` exist.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0 (ev/structure.txt).
- The `tests/closures.json` move adds one line, `sweep_render.py`, to a closure. It is earned by the change: `tests/entities.py` reads the file (INERT READS), which the body cites as the ci_predict repair. No budget file is touched.
- VERSION, the manifest version and RELEASE_NOTES.md are untouched. No claim file is touched.
- `git merge-tree --write-tree origin/main 89b04b74feaef1c0696fca1f353c9532c6792374`: rc 0, tree 903e00feff2197ed1a36436563db96f55c73910f, no conflict (ev/merge-tree.txt).
- CI at the head, read from the check-runs API after every run had concluded (22:31Z): every run is success or skipped, with none red (ev/check-runs.tsv). `pr-contract` is green on both runs. `governance / instrument-self-tests` is green; that is the step that runs the sweep_render self-test. With no red check, no root-cause trigger applies.
- The `tests / mutation` lane is green. I did not read its log to tell evaluated from inconclusive; my targeted mutants above stand instead.
- Finder's harness: none. This is an owner-ordered fly-in, not an audit finding, so steps 2, 3 and 9 have no harness to run.
- Head check: the body names 89b04b74feaef1c0696fca1f353c9532c6792374 as the head, and the branch was still at 89b04b74feaef1c0696fca1f353c9532c6792374 when I re-read it before writing.
