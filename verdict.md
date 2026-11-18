Fix review: merge 212e79760d8427b1a16ce33f3074b71a94886824

bus-nonce: a7a6ba627e146e91460efee5f2569f30
pending-ci: gate

Round: first verdict at a code head after the round-1 block at 007e7be48d (mutation-vacuous); the packet's `## Review scope` reads `full` (no verdict names dbc6569df2), so the whole three-dot diff was reviewed.

## Evidence

- Head measured: 212e79760d8427b1a16ce33f3074b71a94886824, merge base 9fe63d00b59f100aea67267ddddc95522e164aa1; the body's `## Head` names the same head (step 7).
- Merge with main: `git merge-tree --write-tree origin/main 212e79760d` exit 0, tree 62f813fd68 (ev/merge_tree.txt): no conflict; re-run at origin/main 107988b792 at 20:27Z, exit 0. Head re-read then: still 212e79760d (step 12).
- Block A at the head (`features_block.py`, prelude by `--emit-prelude`, ev/blockA.sh): `ALL 33 FEATURES BLOCK PASSED` (ev/blockA_head.txt), matching the body.
- Mutation proof (step 1), my own driver ev/mutant_driver.py over block A, one mutant at a time, file restored after each; 20 of 20 killed, worktree clean after (ev/mutants.log, per-mutant output ev/mut_*.txt):
  - the body's named mutants: `owed_scale(..., True)` (1 of 33 fail); `keep=True`, `keep=not distorted`, `keep=not frozen` (1 each), confirming the body's counts;
  - `judge_floor`'s `if experiment` off (6 fail); the coordinator's `experiment = False` (5); `commit_runs` space filter dropped (2); defrost no longer a stop (1); settle window zero (5); `SEGMENT_MAX_MIN` close off (1); per-minute dedupe off (1); `pass_origin` probe kind ignored (1) and feedback-start origin off (2); `_note_pass` call removed from `_arbitrate` (1); the coordinator's `draw=self._accuracy.draw` dropped (1); `"kind": self._sysid.kind` dropped (1); map rows not written by `to_dict` (KeyError in the round-trip check); `from_dict` ignoring `_stored_map` (4); non-finite cell accepted (1); unequal-length columns kept (1).
- Harness `dev/audit/harnesses/draw_map_rows.py` sha1 057455db8d886d3b112e0c43a2b422d3de37e220 (the fixer's/design's, in the tree; the finding has no separate finder's harness, the packet's `Finder's harness: none named`), `--synthetic` at the head: `RESULT store rows=672 ... added_bytes=58058`, `RESULT open_loop rows=25 distinct_c=18 gain_kw_per_k=0.300 offset_kw=0.400`, null `RESULT shuffled ... gain_kw_per_k=0.023`: every figure the body quotes re-derived (ev/harness_head.txt). At the base's production code the harness stops `AttributeError: 'DrawRange' object has no attribute 'map'` (ev/harness_base.txt), as the body says.
- Claims (step 4): `env_drift.py --all` at the head: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56` (ev/env_drift_all.txt); the diff touches neither claim file.
- Step 5: `VERSION`, `RELEASE_NOTES.md` and `manifest.json` absent from the three-dot diff.
- Ratchet (step 14): `tests/structure.py` at the head passes, `seam_cut_total 413 <= 413` (ev/structure_head.txt). Earned: with only the base's `coordinator.py` and `tests/seam_map.json` restored, the same tree reads `seam_cut_total 415 > 413 (+2)` (ev/structure_head_with_base_coordinator.txt), so the whole -2 is the `_dhw_current_hour` move out of the class, a helper that reads no `self`; a sound move, not a re-spelling.
- Architecture score: `score.py --diff 9fe63d00b5` -> `dS -0.0006 WORSENS (inadmissible: coord_footprint 2507->2508)` (ev/archscore.txt), the body's figure; the body's `## Architecture score` explains the one statement; the required `arch-score / arch-score` check at this head decides (see CI below).
- Step 6/class: the body names rules `git grep -n "judge_floor(" -- custom_components` and `git grep -n "owed_scale(" -- custom_components`; the dispositioned seams (`_fold_measured_cop`, the heat-counter span close) cover the callers I read in the diff. No seam outside the body's list surfaced.
- Step 10: every `Carry:` names R11-CARRY-DRAWMAP, parts B and F of the approved note design/R11-CARRY-DRAWMAP a1688d8d6a: `fixer.md`'s split-part exception (lines 295-297); `carry_audit` resolves each on origin/handoff/audit-r10-roster (packet).
- Step 16: no new refusal before an actuator write; `_note_pass` runs after `_command` and only records. Its new reads (`_map_inputs` on non-heating passes) go through None-tolerant helpers (`_step_kw`, `modulation_floor_flow_c`, `_band_kw`), and `_pass_record` returns None before them wherever `_flow_command` is None.
- Store growth: `added_bytes=58058` at 672 rows is the figure the approved design note (C7/C11) carries to part F for its budget, not a defect here.
- Reds in the range (step 11): CI at 007e7be48d failed `arch-score / arch-score`, `tests / mutation`, `pr-contract / pr-contract`, `gate` (and `tests / mutation-autofix`, `tests / nightly-status`, outside the owed-reds set, ev/owed_reds.txt). The body answers `tests / mutation` and `arch-score`; `gate` is the aggregate of the others.
- CI at this head: `merge_train.py classify 212e79760d --pr 3737` polled every ~72 s from 19:57Z to 20:27Z, every run `WAIT 212e79760d8427b1a16ce33f3074b71a94886824 pending: gate red: none` (rc 3); no required red at this head while polled. Hence `pending-ci: gate`: the relay posts this verdict only once CI is green here. The `arch-score / arch-score` result at this head (the body's explanation of `coord_footprint 2507->2508`) is inside that pending gate.

## Findings

- Note: root-cause-unanswered: `pr-contract / pr-contract` went red at 007e7be48d ("Check the body against the contract") and the body's `## Red checks` does not name it; paperwork, not a block (C5). Carry: dismissed: a body note for the orchestrator to resolve at merge (C5), no code defect
