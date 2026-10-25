Fix review: merge 8a29702db07ec8fd3e760f7e73fe7cd7b9cd5b80

bus-nonce: 01be551ceca7cdd1cf4b7eea62269bee

This is a re-post of the round-2 merge verdict (review/2770 at 592c247f9, published as comment 6391986616), at the same live head and with the same evidence. The only change is dismissal markers on the three `## Evidence` bullets tools/audit/carry_audit.py read as deferrals: the harness and mutant bullets here end in one, and an added bullet names the three published items by id. This is review round 2. It follows the blocked round-1 verdict on `review/2770` (b5de86332), which was measured at ce6f6511e.

I measured head `8a29702db07ec8fd3e760f7e73fe7cd7b9cd5b80`. It was still `refs/pull/2770/head` when I pushed this verdict. That head merges the code head b2ff00056 and then origin/main 662a3809c, which is the PR's current base. Every file this PR changes is byte-identical between b2ff00056 and the head. The round-2 code delta from ce6f6511e is `tools/ci/sweep.py` (one predicate plus its docstring), `tools/ci/sweep_selftest.py` (two fixtures), the race harness, and a header comment in `gate-sweep.yml`. `gate.py`, `prelude.py` and `ci.yml` are unchanged since round 1.

`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract I read is current.

## Round-1 findings, each confirmed paid at this head

- **Block (class-open, `sweep.py:115` swept lower ids only): paid.**
  - `sweep.py:117` now walks `r["id"] != v["id"]`.
  - The race harness was run at both ends and against the round-1 null, with `--edit-s 760` and `--edit-s 900` (ev/race_all.txt):
    - `editcode` at ce6f6511e: `re-runs 0 RESIDUAL-RED 1`.
    - `editcode` at the head: `re-runs 1 RESIDUAL-RED 0`, and the expired code gate is re-judged to PASS by the edit run's sweep.
    - `editcode` at the merge base 5c0ee1093: `RESIDUAL-RED 0`, because the red sits on the lower id there.
  - My mutant M7 (sweep reverted to `<`) brings back `RESIDUAL-RED 1` and fails both new sweep fixtures.
  - Failing test first: the head's `sweep_selftest.py` run against ce6f6511e's `sweep.py` prints `23 checks, 2 failed`, with the two HIGHER-id fixture names (ev/failing_test_first.txt).
- **Finding 1 (who built the harness): paid.** The body's "Who built the harness" paragraph now states plainly that the fixer seat built it.
- **Finding 2 (no UNCERTAINTIES): paid.** The body now states one uncertainty, answered below.

## Findings

- `tools/ci/ghapi.py:226`'s comment still says "the sweep re-runs only older reds". This PR's `sweep.py:117` change makes that comment false. It is only a comment, and code-owned. Carry: R10-ORCH-LEDGER
- The fixer's stated uncertainty: `.github/workflows/gate-sweep.yml`'s step is still named "Re-judge the older gates at this head", now that the sweep re-judges either id. I confirmed the reason given: `dev/audit/harnesses/r10_ci_layout_u0c/sweep_map.json` records that step name as a measurement, so a rename would break the measurement. The answer is to leave the name now and do the rename together with the map re-record. The body carries this to R10-ORCH-LEDGER, but I found no roster entry for it on `handoff/audit-r10-roster`, so it is carried here. Carry: R10-ORCH-LEDGER

## Evidence

- ev/HEAD.txt: the head reviewed, `8a29702db07ec8fd3e760f7e73fe7cd7b9cd5b80`.
- **Finder-shape harness** `dev/audit/harnesses/r10_gate_defer_race.py`. It is fixer-built, and the body discloses that. I ran it over the head, over an export of the merge base 5c0ee1093, and over the round-1 head ce6f6511e, each with edit-s 518, 760 and 900, across all scenarios (ev/race_all.txt). Every figure under the body's Null control and Figures re-derives:
  - **Head:**
    - At 518: every scenario shows UNDECIDED-RED 0, DEADLOCK no and RESIDUAL-RED 0. Gate-wait is 660 s on `2754`, 120 s on `pair` and `cascade`, 540 s on `editcode` and 0 s on `single`.
    - At 760 and 900: `2754` and `editcode` show UNDECIDED-RED 1 (the bound's residual) with RESIDUAL-RED 0.
  - **Base 5c0ee1093:**
    - `2754`: UNDECIDED-RED 2.
    - `pair`: UNDECIDED-RED 2, DEADLOCK yes, RESIDUAL-RED 2.
    - `cascade`: 1.
    - `editcode`: 1.
    - `single`: 0. Carry: dismissed: evidence record, not a finding
- **Null control, a real red is never masked.** `2754-red` shows MASKED 0 at all three trees and at every edit-s. At the head with edit-s 900, the review and edit gates publish `FAIL tests / closures: failure (run 40119473870)`. The code gate, which expired while deferring, stays red, and no sweep turns any verdict green.
- **No-defect null.** `single` shows gate-wait 0 s and no red at all three trees.
- **Mutants.** The driver and output are ev/mutants_driver.py and ev/mutants.txt. Each mutant was applied to the head alone and then restored; `git status` read clean afterwards. All 7 were killed:
  - M7, sweep reverted to `<`: sweep self-test 2 failed, and the harness shows `editcode` RESIDUAL-RED 1.
  - M7b, sweep only `>`: sweep self-test 2 failed.
  - M5, the M1 prelude reverted to id order: the prelude fixture "M1: waits for a LATER code run ..." fails, and the harness `2754` gate-wait rises from 660 s to 780 s.
  - M5b, the prelude waits on every run: 1 prelude fixture fails.
  - M6, the prelude waits until finished: 2 prelude fixtures fail, and the harness shows `2754` UNDECIDED-RED 2.
  - M1, judge never waits: 6 gate fixtures fail, and the harness shows `pair` DEADLOCK yes, RESIDUAL-RED 2.
  - M4, deferral published as PASS: the gate fixture "past the bound ..." fails.
  - The body's M1 to M7 name the same failing fixtures. Carry: dismissed: evidence record, not a finding
- **Self-tests at the head** (ev/selftests.txt), each with 0 failed:
  - `gate`: 37 checks.
  - `prelude`: 29.
  - `sweep`: 23.
  - `codescan_wait`: 17.
  - `ruleset_cutover`: 101.
  - `ghapi`: 19.
- **`r10_ci_gate_core.py` at the head** (ev/gate_core_head.txt):
  - `replay`: `output IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt`.
  - `mutants`: `RESULT mutants=16 survivors=0`.
- **720 s against `ci.yml`'s `gate` `timeout-minutes: 15`.** `GATE_WAIT_MAX_S = 720` and the gate block are unchanged since round 1. The step times are round 1's 31 real gate jobs (ev/gate_job_steps_round1.tsv). I recomputed them myself (ev/timeout_arith.txt):
  - Job start to judge: max 19 s.
  - Judge read: max 8 s.
  - Post steps: max 3 s.
  - Worst case: 19 + 720 + 8 + 3 = 750 s, under 900 s with 150 s spare.
  - The jobs I could list on 2026-10-25 were cancelled ones, so I took no fresh sample.
- **Sweep re-run safety, which I checked myself.** The new walk can re-run a higher-id gate only when V's own gate is green and covers the newest event. Each run is re-run at most once, and a green gate is never re-run. A re-run that turns green triggers its own sweep, and that sweep skips V because V is green, so nothing ping-pongs. A higher-id gate still waiting when V's sweep runs has nothing left to wait for, since V's PASS means no run was still being judged. It therefore decides on its next 60 s poll, inside the sweep's 600 s bound. The harness's `2754` at 900 shows exactly this.
- **Class enumeration.** I re-ran the body's rule (ev/class_enum.txt). Its hits match the body's dispositions: `prelude.py:193` and `sweep.py:117` are in the diff; `gate.py:146`, `codescan_wait.py:79` and `ruleset_cutover.py:347/368/884` are dispositioned; the rest are usage strings. `gate.py` `refresh` also walks the head's runs, but has no id order (it skips only its own id).
- **Claim and version files.** `VERSION`, `RELEASE_NOTES.md`, both claim files and the manifest are untouched, three-dot from the merge base and from 5c0ee1093 (ev/static.txt).
- **Merge with origin/main.** `git merge-tree --write-tree origin/main 8a29702db` exits 0 with tree 2677fae89, and prints no MERGE-CLAIM line (ev/merge_tree.txt). origin/main is 662a3809c, the PR's base.
- **Forward-carries.** Both are on `handoff/audit-r10-roster`: 61446b002 (P82's tick names `GATE_WAIT_MAX_S`, with removal keyed on this merge, "once it lands") and 216e090fe (M3 still owed under R10-RCA-CODESCAN-WAIT, M1 and M4 landing here). Both commits are ancestors of the roster tip.
- **CI on this head**, from the check-runs API at review time:
  - Two `ci.yml` runs (40149731315 and 40149732613) are at `prelude` queued or `refresh`.
  - `dependabot.yml` passed, and `arm` was skipped.
  - Nothing has concluded red, so no red check is owed an answer yet. The heavy lanes have not reported, and I re-ran none of them.
  - On a PR, the gate job restores `tools/ci/*.py` from the base, so this PR's own gate runs main's program.
- **Earlier evidence records.** carry_audit read three evidence bullets of the earlier verdicts as unrouted: the round-1 mutant record and this verdict's harness and mutant records, as first published. None of them is a finding. Carry: dismissed: evidence record, not a finding (item 966bc31f) Carry: dismissed: evidence record, not a finding (item 80cd9485) Carry: dismissed: evidence record, not a finding (item e516ff36)
- **Not re-derived.** The body's `entities.py` count (2429) and its `BASH_ENV` explanation. This seat did not run the full suite; that is CI's job.
