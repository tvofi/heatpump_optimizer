Fix review: merge 34f4afac0852fa09091263a05a36c50b624caec5

bus-nonce: 8e498178108f67022b3c1438f54a5b44

## Round

This is the third fix review of #3245 (R10-PROCESS-SLIM); the brief calls it ROUND 3. It is measured at head 34f4afac0852fa09091263a05a36c50b624caec5. That head merges the code head e6a4a7dd3374b97b44dcb5ea1bb52d23d984f628, which is `handoff/r10-process-slim` per ls-remote. Earlier verdicts:
- 481c7750: blocked, ci-red (the handoff_push delivery_row grep);
- 6289321a: blocked, ci-red (ref_privacy author guard masked by head-stale).

Both causes are repaired at this head (Evidence). This round's own-diff delta against 6289321a's own diff is:
- nightly.yml back to the base (the record-autofix beat is kept);
- its pins restored in tests/entities.py, merge_train.py and orchestrator_tick.py;
- the record-text corrections;
- the release_worktrees fix and its self-tests;
- the roster_edit.py docstring and the sweep_template.md text for C6;
- main's R10-HOTFIX-SELFTEST-TIMEOUT taken in the merge.

This is not the fourth round, so no re-cut is owed.

## CI state at this head

`merge_train.py classify` exits 1: `RED 34f4afac... pending: none red: gate`. The final `gate` (128695594031) prints exactly one failure: `FAIL codeql / Analyze (python): cancelled (run 42464275029)`.
- `codeql / Analyze (python)` (128693917445) ran from 08:46:10Z to 09:31:13Z and was cancelled at codeql.yml's `timeout-minutes: 45`. Its last step reached was "Waiting for processing to finish". This diff leaves codeql.yml byte-identical to the merge base.
- **Null control:** main's current head 2a3c05644 cancels the same job the same way (08:21:13Z to 09:06:19Z). Main f9a963203 took 36 min, so the job is near its timeout on main itself. The cancel is main-wide CodeQL headroom, not this diff. It is carried below to the existing R10-HOTFIX-CODEQL-HEADROOM.
- This merge verdict judges the code, tests and harness. It does not declare the head green. `codeql / Analyze (python)` is a required context (`tools/ci/fixtures/ruleset/ruleset_23698884.json`). The train must see it re-run to success at this head before merging, and its own classify enforces that. Run 42464275029's later attempts (12 to 17) re-ran only the gate, never the cancelled CodeQL job.
- The only other red is `budget-raise-gate / budget-raise-gate`, the expected approval-owed red for the two proposal-triage.md caps. The body's `## Raise justification` carries the mandate line (comment 6624093439, scope all) and `Architecture score: dS +0.0000 NULL`. I re-derived the score here: `dS +0.0000 NULL`.

## Owner constraint

The diff writes 0 files under `custom_components/`, and `tools/ci/`, `ci.yml`, `codeql.yml` and `nightly.yml` are byte-identical to the merge base (ev/untouched.txt). So the gate's workset rules for production-only, machinery-only and mixed diffs are main's, unchanged. Per change, the production path touched and the check that still guards it:
- **C4** (bus.sh derives `--reviewed-head` from the last merge verdict; fix-review.md step 12): no production path. Mutation, goldens, features and CodeQL still run on every head, and a red never carries.
- **C5** (paperwork becomes a note; no seat writes a delivery row; the `governance / delivery-status` and `delivery-status-publish` jobs and tests.yml's PR copy of the delivery_status grader are deleted; record's refusal step is report-only):
  - no production path, and a note on `custom_components/` still blocks (fix-review.md at the head);
  - `governance / delivery-status` is not in the required set;
  - **this round keeps Nightly's record-autofix beat**, so the stamp's flush and `--require-rows` still read real rows. This is narrower than earlier rounds.
- **C8** (bus.sh dispatch waits on `CHEAP_CHECKS`, and post refuses `merge` at RED): no production path. A production review waits at most for checks that themselves gate production.
- **C6 (a)** (proposal-triage.md deleted, with its two caps and its phantom closure entry): no production path.
- **Train fixes** (postmerge docs step removed, app_approve carry() ancestry, merge_train release_worktrees): no production path.
- **Planted production defect, with a null control** (ev/plant/): `grid_fee.fee_bound` made to return -1.0 (grid_fee.py:81).
  - `tests/config_flow_steps.py` refuses it with **rc 1, `2 of 539 checks FAILED`**, at this head and at origin/main 2a3c05644 alike.
  - `tests/closure.py select --files custom_components/heatpump_optimizer/grid_fee.py` gives `MODE: SCOPED -- 22 script(s) run, 11 scoped out` at both ends. The set of selected scripts is identical. The only differences are scoped-out closure sizes from main's newer recording (ev/plant/select.diff).
- The body states per card why the risk is acceptable and names the remaining guard. No cut goes beyond cards C4, C5, C8 and C6 (a) as written. I found no large unforeseen risk with a measurement behind it.

## Policy text changed (for the coordinator to surface to tvofi)

The round-2 list in verdict 1cddf8fd0 still holds, except that the sentences saying the beat is deleted are gone. New this round (ev/policy-delta-r2-to-r3.txt):
- **delivery-status-tracking.md item 1:** "There is no per-PR ... row and no record pull request ... rows already merged ... read by nothing that gates" becomes "No seat writes a per-PR `dev/programme/delivery/<N>.md` row (card C5 ...). Nightly's `record-autofix` beat still rows each merge from API facts, because `tools/release/stamp.py`'s flush and `--require-rows` read those rows (orchestrator ruling 2026-11-08, until R10-FLY-STAMP-FLUSH-COST retires them)."
- **CLAUDE.md's delivery-status-tracking row:** "no per-PR row" becomes "no seat writes a per-PR row".
- **orchestrator.md section 9:** "no per-PR row (card C5)" becomes "no per-PR row from you (card C5)".
- **orchestrator.md record item:** "no per-PR row is written" becomes "No seat writes a per-PR row; `tools/audit/seat/record_row.py` drives the record-autofix job that rows each merge, which the stamp reads".
- **fix-review.md:**
  - main's "Evidence names differ beyond case." is unioned in;
  - "(card C5, tvofi 2026-11-05)" becomes "(card C5)";
  - "(card C4, tvofi 2026-11-05; #1667, 2026-10-27)" becomes "(card C4; #1667)".
- **tools/audit/seat/roster_edit.py docstring and sweep_template.md (7):** a proposal now goes to the orchestrator, who rules it directly (card C6), instead of to proposal-triage.md.

The body says `Content approved by tvofi in chat 2026-11-05`.

## Findings

- `codeql / Analyze (python)`, a required context, is cancelled at its 45-minute timeout at this head (128693917445). It is cancelled identically at main 2a3c05644, and main f9a963203 needed 36 min. That is main-wide CodeQL headroom, not this diff (codeql.yml is unchanged). The train owes a re-run of that job to success at this head before the merge, and the cure is the headroom group's. Carry: R10-HOTFIX-CODEQL-HEADROOM
- `dev/programme/delivery/3245.md` is in the diff, written by the orchestrator at 481c77507 under the pre-C5 rule. It reads `**open**`. The kept record-autofix beat's plan upgrades an open row of a merged PR, so the stamp's `--require-rows` is still satisfied, and this needs no change here. Carry: dismissed: a pre-C5 row the kept beat reconciles after the merge; nothing to change in this diff

## Evidence

- **Head measured:** 34f4afac0852fa09091263a05a36c50b624caec5 (ev/HEAD.txt). It is the PR head and `refs/pull/3245/head` per ls-remote at 09:55Z, and the body's `## Head` names it. The merge base is 17e1157925908bd69addb58ed824c1ac22bfa82f.
- **review_packet.py render:** REFUSE required-red `gate`. That was an early edit-run deferral ("FAIL run(s) [42464275029] at this head are still being judged; their gate decides", ev/gate-128680432033.log). I waited, then re-read all check-runs across pages (ev/checkruns-1.tsv, ev/checkruns-final.tsv, ev/checkruns-final2.tsv).
- **Concluded success at this head:** `tests / fast (3.14)`, `tests / mutation`, `tests / closures`, `tests / coverage`, `tests / arch-instrument`, `tests / typing`, `tests / browser`, `tests / briefs`, `tests / closure-scope`, `governance / instrument-self-tests` (08:58:35Z, step success, no timeout), `governance / env-matrix`, `governance / policy-docs`, `hassfest / hassfest`, `validate / validate-hacs`, `codeql / Analyze (actions)` and `codeql / Analyze (javascript-typescript)`.
- **pr-contract:** `pr-contract / pr-contract` 128693918847 succeeded. It started at 09:31:16Z, after the last red concluded (CodeQL cancel, 09:31:13Z), so it is the root-cause-answer evidence under fix-review.md step 11.
- **classify:** ev/classify-log.txt; final `RED ... red: gate`, rc 1.
- **Round-1 and round-2 causes:** both repaired.
  - `handoff_push.sh --self-test`: 6 checks, 0 failed. instrument-self-tests is green in CI.
  - `ref_privacy.py --self-test` at this head: 113 checks, 1 failed, the machine-email arm only. The same arm fails identically at origin/main 2a3c05644 in this container (ev/ref_privacy-main.log), and CI's instrument-self-tests passed. The runner-default arm round 2 blocked on now passes.
- **Self-tests at the head** (ev/checks-head/summary.txt):
  - `stamp.py --self-test`: `RESULT stamp_self_test=pass`;
  - `orchestrator_tick.py --self-test`: 283 checks, 0 failed;
  - `merge_train.py --self-test`: 475 checks, 0 failed;
  - `body_push.sh --self-test`: 35 checks, 0 failed;
  - `postmerge.py --self-test`: 15 checks, 0 failed;
  - `ci_predict.py --self-test`: 0 failed (after `mkdir /opt/hpo/runner-temp`, as the body says);
  - `app_approve.sh --self-test`: 324 checks, 0 failed;
  - `tests/structure.py`: STRUCTURE RATCHET PASSED;
  - `selftest_wiring.py --check`: 0 index gaps;
  - `rules_sync.mjs --check` rc 0, `policy_lint.mjs` `0 error(s) across 49 policy file(s)`, and `--budgets` rc 0.
- **bus.sh --self-test:** 166 checks, 1 failed (`an ordinary append with no intervening fetch is the same commit object as before`). The body names this as the container's at origin/main; I did not re-run it at main.
- **entities.py:** `2 of 2648 ENTITY CHECKS FAILED` at the head and `2 of 2656` at the base 17e11579 (ev/entities-base.summary). It is the same two at both ends (the coverage-cache reuse and the release ZIP), which matches the body's figure exactly.
- **Mutants**, my own, in a detached worktree at the head (ev/mutants/summary.txt). All were KILLED:
  - M1: release_worktrees never skips a collected worktree. merge_train: 1 failed, "already collected ... not removed again".
  - M2: skip without the registered check. merge_train: 4 failed.
  - M3: nightly.yml HOLD_MAX_AGE_S renamed. `stamp_self_test=fail`.
  - M4: body_push head-stale moved before the identity guard. ref_privacy: 2 failed, the runner-default arm among them.
  - M5b: head-stale never fires. body_push: 2 failed.
  - M5, my first attempt, was a malformed mutant that broke the script's syntax. It is disclosed and superseded by M5b.
- **merge-tree:** `git merge-tree --write-tree origin/main 34f4afac0`: rc 0, `LEDGER-MERGE: resolved tests/closures.json` (set merge), no conflict, no MERGE-CLAIM line (ev/mergetree.*). That is origin/main 2a3c05644.
- **Untouched files:** VERSION, the manifest, RELEASE_NOTES.md, tests/golden/claimed_drift.txt, card_claimed_drift.txt, nightly.yml, ci.yml and codeql.yml are byte-identical to the merge base. The `*_budgets.json` diff is only the two proposal-triage.md keys (36, 489). Diffstat: 39 files, +557/-743, as the body says.
- **Forward-carry:** the beat-deletion carry is on `handoff/audit-r10-roster` under R10-FLY-STAMP-FLUSH-COST ("From r10-process-slim, body item ada60feb ..."), and carry_audit at the head reads it resolved.
- **Role currency:** `git diff 17e11579...origin/main -- dev/governance/roles/ .claude/rules/` is empty, so the role text is current.
- **Finder's harness:** none named, because this is a process group with no finding harness. The planted production defect and the mutants above are this seat's own controls.
- **Not re-derived:**
  - the card savings figures, which the body cites from earlier rounds;
  - main's merge_train figure of 472 checks;
  - `orchestrator_tick`'s mutant counts at d70186a59.
- **Not pushed:** handoff-wip was not pushed for liveness, because the payload says to push nothing but the probe ref.
