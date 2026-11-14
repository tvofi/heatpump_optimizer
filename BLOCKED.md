# BLOCKED: r10-docs-strings-residue part 1, repair round (prepr refuses on a calendar red at the base)

Question: `tools/pr/prepr.sh` at the repaired head 5604d6eba51e19b5375c1e12d7ef29b3690ac3d9 refuses only its `closures` step, because `tests/features.py` exits 1 on one check that fails on weekends at the merge base too. Should this part hand off with that refusal answered in the body, or wait for a fix to the check (another group's, not text) or for a weekday prepr run? The repair delta must stay text only, so I did not touch tests/features.py.

The repair itself is done and on this ref (5604d6eba5, before this file): the sv `space_setpoint_unit` text now says "från entiteten" (the block item), plus the same key's "framledningsentitet" and its three labels' "börvärdesentiteten"; the how-it-works Hold-verified bullet now opens with the option and the heading is kept (the advisory item). The draft body is on refs/heads/handoff-wip/r10-docs-strings-residue-body. handoff/ and handoff-body/ have not moved.

prepr.sh summary (rc=1, 2026-11-14):
```
REFUSE   closures               failed while being recorded: tests/features.py (exit 1) -- fix the script first; a re-derive would record the same truncation; left to CI: tests/harness_headers.py
PRE-PR: 5604d6eba51e19b5375c1e12d7ef29b3690ac3d9 00000000000000000100000000000 rc=1
```
Every other step was ok or skip, including pr-body (0 errors), figures, figure blocks and carry.

The failing check is `a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked` (section `R8-P8 round 3: mutation survivors on lines this diff's files carry`). `_chg_seq` starts its non-Saturday traces at `dt_util.now()` and moves only the `saturday=True` trace onto a Saturday, so on a Saturday or Sunday the weekday traces book the weekend day type ([0, 1] where [1, 0] is expected). Measured with `tools/audit/seat/features_block.py` over that section in a detached worktree of the merge base e23124ff6e45bac1d48b4a775dad555a37965355, with `homeassistant.util.dt.now` pinned in the prelude: 2026-11-13 (Friday) `ok`, 2026-11-14 (Saturday) `FAIL`. With the real clock, the base and this head both FAIL on 2026-11-14. The reviewed head passed it on 2026-11-13. Today any head's features.py, main's included, is red until Monday. The likely fix is in the test: move the non-Saturday start off a weekend, for example `start -= timedelta(days=max(0, start.weekday() - 4))`.

The scoped gate's other red, `tests/env_drift.py --all origin/main` `DRIFT config_flow` (the hysteresis entity keys), comes from main's #3531 after this branch's merge base and is not in the branch diff. `git merge-tree --write-tree origin/main HEAD` exits 0.
