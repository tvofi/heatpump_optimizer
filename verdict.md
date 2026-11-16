Design review: approve a21ad55901b20369a6540abdd4793f29e3eae8bb

Round 3, delta review: `git diff 22fdbabafb..a21ad55901 -- design.md`, from a detached worktree at a21ad55901, code read at 030a4d377f (the brief's base). The note's own base 4ce615b5e6 is an ancestor of 030a4d377f, 81 commits behind; of the files the note names, only `tools/audit/seat/orchestrator_tick.py` (+514/-65, #3635, #3651, #3661) and `.github/workflows/governance.yml` changed in that range, and every anchor the note cites in them still holds at 030a4d377f (`judge` :437 calling `mt.run_state` :442; `governance.yml` :310 and :313). Token count: the harness reports none. The shape is unchanged from the approved round 2; the switch remains unapproved, and nothing here dispatches it.

## Checked at 030a4d377f

- o1, o2, o3: the rulings the note quotes are in the group's `resume.note` in dev/programme/rosters/wave-r10-groups.json at 4ce615b5e6, verbatim. Carry: dismissed: rulings verified as quoted (item v1)
- n-a: `inputs.recheck` is read at tests.yml :1628 and :1764 and `closure-recordings-tree-` is written at :2251 and read at :2120, as the note says; passing both `recheck=true` and the new input keeps lane proofs and lane identification unchanged, which settles my round-2 point without a tests.yml condition change. Carry: dismissed: resolved as asked (item v2)
- Carry 1 is not moot: `Train.admit` returns a serial entry at its `serial:` log line before the P86 approval at admission, so only serial entries reach `land` unapproved; applying (i)-(vi) to them is the right reading. Carry: dismissed: verified at base (item v3)
- Carries 4, 5, 6, 7 and 11's draft half: 02f0c1d097, eb1081cf08, 868f8a726b, 95a12bf027, dbe75142ac and 6c4c5addcf are ancestors of 030a4d377f; `_sweep_busy` :2347, `prelude.py` `judging` :274, the `mandate comment` wording :2983-2984, `rollup_walk` :497 and `is_draft` / `gh pr ready` :1616-1631 are present. Carry: dismissed: fixes verified at base (item v4)
- Carry 3 open as stated: `review_settle` adds every grain to `waited` (:3570-3571) and `runs or ()` empty returns at once (:3573-3575). Carry: dismissed: verified open at base (item v5)
- Carry 9's narrowing to structure budgets with no cap up matches the owner-accepted text and keeps every serial class it names. Carry: dismissed: matches the accepted carry (item v6)
- Carry 13: `MACHINERY_JOBS` is absent from `tools/ci/gate.py` at 030a4d377f, so the after-edge on R11-PRE-TOOLCHAIN-PIN part 2 stands. Carry: dismissed: verified at base (item v7)
- Sibling designs: R11-INTAKE-R10-RESIDUE's note is a stop that marks carries 2 and 3 moved here, so no double claim; R11-PRE-STANDING-SCRIPTS leaves `merge_train.py` unedited by its own L5. Carry: dismissed: no overlapping claim found (item v8)

## Decisions routed, no revise point

- R11-PRE-TOOLCHAIN-PIN's design (design/R11-PRE-TOOLCHAIN-PIN, its table at lines 77 and 82) edits `pr_args.sh` (`pr_tools_fresh`), `remerge_main.sh:29` and `train.sh:475`, which NO-ABSORB (`pr_args.sh`, `remerge_main.sh`) and TRAIN-WAITS (`train.sh`'s per-repository lock) also edit. The concerns differ (a freshness refusal against an absorb predicate and a pidfile lock), so no seam is claimed twice, but the note gives an after-edge only for carry 13; the merge order of these parts against TOOLCHAIN-PIN part 1 is the orchestrator's. decision: orchestrator. Carry: R11-PRE-PARALLEL-PIPELINE (item d1)
- TRAIN-WAITS is cut as S over three files with seven arms (carry 2's three residuals, carry 3, carry 11's three open items), each with its own self-test, null and mutant, in a 5000-line `merge_train.py`; M fits that better. Its size is a roster entry, not the design's shape. decision: orchestrator. Carry: R11-PRE-PARALLEL-PIPELINE (item d2)
- Carry 12: the harness is at tag archive/design-wip/r11-pre-parallel-pipeline, not on the design ref, because `bus.sh push-design` writes one file; the carry's text asks for the design ref. Whether the tag satisfies it is the orchestrator's. decision: orchestrator. Carry: R11-PRE-PARALLEL-PIPELINE (item c12)

## Notes for the fixer

- G1 was measured at 4ce615b5e6; 81 commits have merged since, so the machinery ratchet's headroom at dispatch is not G1's. Each part's fixer reruns `python3 tools/audit/machinery_ratchet.py --check` at its own merge base before the handoff, as the note says. Carry: R11-PRE-PARALLEL-PIPELINE (item n-d)

## Could not verify

Rerun nothing, per the brief: no harness, replay or ratchet was run, and no GitHub read was made. I did not re-read `orchestrator_tick.py`'s new owed-watch code for a fourth gate reader that bypasses `classify`; TRAIN-WAITS' fixer greps for `run_state` callers in the tick at its own base. Carry: R11-PRE-PARALLEL-PIPELINE (item c2)
