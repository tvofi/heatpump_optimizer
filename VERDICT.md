Fix review: blocked 4cab619c132a214926ca27fb211220d1976a9f63 merge-conflict: tools/ci/sweep.py and tools/ci/sweep_selftest.py conflict with main at fdc8d21a (#3327, R10-HOTFIX-SWEEP-SETTLE-LOOP)

bus-nonce: 66f52d23addd9b64094b3d55c81584e5

Round 1 (first-round review). Head re-read at 23:35Z by `git ls-remote`: still 4cab619c, unmoved, measured at head `4cab619c132a214926ca27fb211220d1976a9f63` from a detached worktree; merge base `daf8b349fd30cc60786eeca333a426b693aa4c5f` (= origin/main when read). `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract read is current.

## Block

- `git merge-tree --write-tree origin/main 4cab619c132a214926ca27fb211220d1976a9f63`, with origin/main at fdc8d21adaa50a7feee534f08ee5edde9bda81ed (fetched 23:35Z), exits 1 with `CONFLICT (content)` in `tools/ci/sweep.py` and `tools/ci/sweep_selftest.py` (`ev/merge-tree.txt`). Neither is a claim file, so the result cannot be judged correct without a resolution.
  - Cause: #3327 (merge d4f5a413a at 2026-11-08T22:02:09Z, during this review; commits 34b98bbdb and 6158186e1). It changes `Sweep.settle`, the same method this PR's stale-pin path is called from ("a skipped job is no source, and settle re-runs a bot-started gate only past a new source").
  - At review start, origin/main was the merge base daf8b349, and merge-tree was clean (tree 63b13037).
  - Owed: merge origin/main and resolve both files. Then re-run steps 2-8 (`fixer.md`): the sweep self-test with both sides' checks, and the stale-pin arms through the new settle (the S15 scene under `## Findings` belongs there). The resolution delta is then the next review's.
  - Everything else measured below held at this head. The code is otherwise reviewable as-is.
  - Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Evidence

- RESULT replay (finder's harness, `dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay --ci <git archive of tools/ci tools/pr>`, `ev/replay-both-ends.txt`):
  - at the merge base daf8b349: `3252-nosource: MISREAD`, `FAIL pr-contract / pr-contract: failure (run 42387066581)`; `3244-triple: DECIDED`, all PASS; `defects=yes`, rc 1.
  - at afc1586a (the branch's cut point): the same as the merge base.
  - at 9cbd7dd0 (the triple's live pin), the null control for the three-gate shape: `3244-triple: DEADLOCK`, each gate `FAIL run(s) [<the other two>] ...`.
  - at the head: `3252-nosource: DECIDED`, PASS; `3244-triple: DECIDED`; `defects=no`, rc 0.
  - The harness moves under its own perturbation: M27 (the source order put back to id alone) on the head turns `3252-nosource` back to `MISREAD`, rc 1. So the finding is not void.
  - The harness is the RCA seat's (`r10-gate-busy-defer-2`). This fixer recorded the `3252-nosource` and `3244-triple` scenes with its `record --scene`, additions only. They are measured inputs, not a rebuilt instrument.
- RESULT self-tests at the head (`ev/selftests-head.txt`): gate 81 checks, 0 failed; sweep 62 checks, 0 failed; prelude 76 checks, 0 failed. These match the body.
- RESULT gate-core mutants (`python3 dev/audit/harnesses/r10_ci_gate_core.py mutants`, `ev/gate-core-mutants.txt`): `mutants=22 survivors=0`. M17, M18, M25, M27 and M28 are KILLED. This matches the body.
  - The body says M27 reads `MISREAD` with replay exit 1. That is true of the RCA replay (re-run above). It is not true of `r10_ci_gate_core.py`'s own row, which kills M27 by the self-test and prints `replay rc 0`. This is only the two harnesses being worded alike, not a defect.
- RESULT reviewer mutants, my own: 26 mutants over every changed production line of `tools/ci/gate.py`, `prelude.py` and `sweep.py` (`ev/reviewer-mutants.txt`, script `mut.py` beside this verdict). Each was applied in place, then the three self-tests and the RCA replay were run, then the file was restored (`git status` clean after). Result: `RESULT reviewer-mutants=26 survivors=5`.
  - Killed: the lag guard deleted (G1), sort ascending (G4), each `starts` plumbing step dropped (G5, G6, G7, P1), and the stale branch deleted (S1).
  - Also killed: the event, prefix, `.py`, 300-cap, fork and cache guards (S2-S7), the dispatch-event filter (S8), `>=`->`>` (S9), once per sweep (S11), the dispatch count (S12), the inputs' base (S13), `runs` in `run()` (S14), and the compare range reversed (S17).
  - S10 (`completed_at or "~"` -> `or ""`) is equivalent. `judge()` reaches `fresh()` only for a completed gate, which always carries `completed_at`.
  - The other four survivors (G2, G8, S15, S16) are under `## Findings`.
- Probe of the S15 survivor, my own instrument (`ev/probe-settle-poll.txt`, `probe_settle.py` beside this verdict). The scene is the #3261 pair through `settle`, plus a `workflow_dispatch` run created after both stale gates concluded.
  - At the head: no post, `run 5 re-judges this head`. The settle path's no-loop guard works as written.
  - Under S15: one dispatch is posted while a fresh judge already exists.
  - My poll-path scene did not reach `judge()` through the poll branch, so S16 is unprobed. I say so rather than infer it.
- Stale pin, attacked for a loop or a hidden red:
  - The stale branch only swaps a re-run for one dispatch. It never posts a verdict.
  - The dispatched run's gate is the newest `gate` check run at the head, and it judges with main's programs.
  - A dispatched run created at or after the stale gate's conclusion suppresses a second dispatch (S8, S9, S14 killed; S15 probed above).
  - A deferral is still `deferral()`'s red, and `busy()` and `deferral()` are untouched. So no deferral or stale pin can conclude green without a judgement.
- Source order (`gate.fresh`), attacked for a green over a real red:
  - Every source must still be completed and green, or it is a FAIL.
  - The order only picks which run is the source. A later-started red beats an earlier green (self-test, killed under G4, M27).
  - This run's own pending single-job unit stays the source (M28, G1 killed).
  - Where `starts` is absent (`{}`), the key falls back to id order, the base's behaviour.
  - With multi-job units, a sibling can cover this run's own partly pending unit, under G8's shape. Base id order already allowed that for a higher-id sibling, so it is not a regression. It is still unpinned (Findings).
- Class census: the body's rule at the head returns 8 lines (gate.py 122 and 124; sweep.py 92, 93, 202 and 248; prelude.py 236 and 303), each dispositioned in the body. This matches. `git grep -n rerun-gate`: 0 hits.
- Merge with main: clean at review start against daf8b349 (rc 0, tree 63b13037386172d2b3b89a12e2ced9e5383d9fe5). It conflicts against fdc8d21a at the verdict, as under `## Block`.
- Untouched files: `git diff --stat <mb>...HEAD` over VERSION, the manifest, RELEASE_NOTES.md, both claim files, every `*_budgets.json`, `tests/closures.json` and `tests/closure.py` is empty (`ev/static-checks.txt`).
  - The only new tracked file is `dev/programme/delivery/3348.md`, the delivery row, which `tests/entities.py` classifies (result below).
  - The PR body's `## Head` names `4cab619c132a214926ca27fb211220d1976a9f63`, the head I measured.
- Harness sha1s at the head equal the body's: rca 556b35c2, gate_core fcee81f4, codescan aa74f7bb. The codescan `--selftest` prints `15 checks, 0 failed`.
- Figures I did not re-derive:
  - The 7-day codescan reading (1821 runs, 5 ORDERED, 3 by the carry's rule). It needs hundreds of REST reads against the shared bucket, and its narrowing probe (`probe10.sh`) is scratch and not in the tree.
  - The null control's "19 of 19 SAME" pin check (`pincheck.sh`, scratch).
  - The diff-mutant table's 73 mutants and 6 survivors (CI's heavy run; cited, not re-run). My own 26 mutants above stand beside it. Four survivors there are of operators `mutant_run.py` does not generate.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0 (`ev/structure.txt`).
- `python3 tools/audit/archscore/score.py --diff afc1586a`: `Architecture score: dS +0.0000 NULL` (`ev/archscore.txt`).
- `tests/closure.py select --diff <mb>`: `MODE: FULL`, reason `tools/ci/gate.py changes the gate itself` (`ev/closure-select.txt`).
- `tests/entities.py` did NOT run clean here, and the cause is this environment, not the diff. Run plainly (venv-ci python3, no BASH_ENV or skip workaround), it stops at import with `ModuleNotFoundError: homeassistant` (`ev/entities.txt`). Under venv-ha it stops at `ModuleNotFoundError: paho` (`ev/entities-venv-ha.txt`). Neither venv got past imports, so I have no local entities verdict. CI's FULL suite on this head is the evidence for it.
- CI on this head. `merge_train.py classify 4cab619c --pr 3348` went from WAIT to `RED 4cab619c... pending: none red: gate` at 22:38:29Z (`ev/classify.txt`). The only red is `gate`. Its three check runs (`ev/gate-checkruns.tsv`, `ev/gate-logs.txt`):
  - 128871924664 (edit run 42526037423, 21:48:24Z) printed `FAIL run(s) [42526036839, 42526438071] at this head are still being judged; their gate decides`.
  - 128873239478 (edit run 42526438071, 21:50:45Z) printed `FAIL run(s) [42526036839] at this head are still being judged; their gate decides`.
  - 128884044704 (code run 42526036839, KIND code, 22:33:12Z), the newest `gate` check run at the head, printed `PASS`.
  - All three printed `programs restored from daf8b349fd30cc60786eeca333a426b693aa4c5f`, so main's gate made both deferrals, not this branch's.
  - Every other check at the head concluded success or skipped (66 check runs, one page, read at 22:28Z).
  - I judge the head GREEN on its gate. Both reds are deferrals and no unit failed. The code run they deferred to was judged PASS by its own gate. A deferral is never a verdict (brief).
  - Root-cause trigger: the two reds are the same class the body's `## Red checks` answers at the previous head 2b2e7a7b3 ("Cheaper detector: none exists"; a deferral is the gate as designed). I read that class answer as covering these two. The body names only the previous head's check-run ids, not these.
  - The deferral window: waited from 22:38Z for a re-judge. `gate-sweep.yml` is `disabled_manually`, with its workflow updated_at 2026-11-08T11:54:00Z and its newest run 42479944954 at 12:22:30Z. So no sweep re-runs these two gates, and `classify` stays RED until someone re-runs them by hand. See the last finding.
- Red checks were read across all check-run pages (66 check runs, `total_count` 66, one page at per_page 100). The only concluded reds are the two `gate` deferrals in the CI line above. The deferral reds the body answers by id are at the previous head 2b2e7a7b3.

## Findings

- Follow-up (non-blocking): Surviving mutant G2: `gate.fresh`'s `max(...)` over a unit's job starts replaced by `min(...)` passes every self-test and the replay. The aggregation over a multi-job unit (the `tests` unit's several required jobs), "the run whose jobs for it started LAST", is unpinned. Owed: a self-test where two runs' multi-job units interleave their starts. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up (non-blocking): Surviving mutant G8: `fresh`'s own-lag guard `any(... != "completed")` replaced by `all(...)` passes. For a multi-job unit partly pending in this run, the docstring's "never displaced" is then false: a later-started sibling's green covers this run's own pending job. Base id order allowed the same for a higher-id sibling, so this is no regression, but M28 pins only the single-job case. Owed: the multi-job arm of `source order null`. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up (non-blocking): Surviving mutant S15 (probed): `settle()`'s `self.judge(r, g, ..., runs)` with `runs` dropped passes every sweep self-test. Yet in the #3261-pair settle scene with a fresh dispatched judge already present, it posts a second dispatch (`ev/probe-settle-poll.txt`). So the no-loop guard is load-bearing on the settle path and unpinned there. The code at this head is correct. Owed: the `probe_settle.py` scene as a sweep self-test. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up (non-blocking): Surviving mutant S16 (unprobed): the poll path's `self.judge(..., list(listing.values()))` with the listing dropped passes. It is the same guard on the third call site. Carry: R10-HOTFIX-GATE-BUSY-DEFER

- Follow-up (non-blocking): `gate-sweep.yml` is disabled (`disabled_manually`, 2026-11-08T11:54Z). While it stays off, this PR's stale-pin dispatch (`sweep.stale_pin`/`fresh`) and #3287's deferral re-judging reach no PR. This head's two deferral gate reds stay red, and `merge_train classify` reads RED, until a hand re-run of check runs 128871924664 and 128873239478 or a re-enable. The orchestrator decides which. This PR's body says the manual RCA 5.3 dispatch is retired once it merges. That holds only with the sweep enabled. Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Friction

- review-frugal-guard: cost: discovery reads were capped at 5 inline searches per prompt, so I read the diff whole and ran no wide search. Carry: dismissed: a session plugin's guard, not this repository's policy
