Fix review: merge ce21b136c649d60e3f00d52a458c0abafb6b73a4

bus-nonce: e44c6bff3fa9b2a5f87111e784d6a800

## Round

First round (review scope full, packet: no `--reviewed-head`).

## Evidence

- RESULT: head ce21b136c649d60e3f00d52a458c0abafb6b73a4 reviewed from a detached worktree; `git merge-tree --write-tree origin/main <head>` rc 0 (tree 54dab14fa4), so no conflict with main. `dev/governance/roles/` is unchanged between merge base and origin/main.
- RESULT: the three-dot diff touches `.github/workflows/tests.yml`, `tests/replay.py` and `dev/programme/delivery/3912.md` only. `VERSION`, the manifest, the notes heading, both claim files and every `*_budgets.json` are untouched, and no production code (`custom_components/`) is changed.
- RESULT: `controls()` at head reads 41 controls, 0 failing, and all four `headroom` controls are ok (`ev/mutants.txt` driver `ctl.py`). The cap reads `60 60` (regex reader and PyYAML agree). `budget_wall_s()` = 2768.08 s at `cpu_ratio` budget 589.6842, which matches the body's 2768.1.
- RESULT: the null-control table re-derived at base cap 30 and head cap 60 (`ev/null_control.txt`). 772.0 and 836.1 are ok at both caps. 1518.1, 1476.4, 1798.0 and 1751.8 are red at 30 (limit 1424.0 s) and ok at 60. The slow-runner draw 2505.3 and the budget wall 2768.1 are ok at 60, under the 2864.0 s limit. This matches the body.
- RESULT: reviewer hand mutants, each restored, driver `controls()` exit 1 on any failing control (`ev/mutants.txt`). 8 of 10 were killed: predicate `if True:` and `limit*2`, the None-cap branch disabled, the job-reader regex loosened, `REPLAY_HEADROOM_SHARE` 1.0, `budget_wall_s` unscaled, `rest_s` 0, and cap 60 -> 58. Two survived; both are listed under Findings.
- RESULT: CI `tests / replay` job 140208054638 at this head printed `replay lane wall time 1766.1 s`, `ok   lane wall time within the pull-request replay job's headroom` and `ALL 203 replay checks PASSED` (`ev/replay_ci_tail.txt`), finishing in 29m49s. That is the new check wired end to end in `main()` on CI's runner, under the 60-minute cap.
- RESULT: the class is one seam, the pull-request `replay` job's cap read by `replay_timeout_minutes`. The nightly `slow` job runs the same lane under its own cap, and the body dispositions it (the check fires there first by design). No other quantified set is claimed.
- RESULT: the mutation driver draws no mutant on `tests/` (`SKIP_PREFIXES`), so CI's green `tests / mutation` evaluated nothing for this diff. The reviewer's hand mutants above are the measured proof.
- CI state: `merge_train.py classify ce21b136c649d60e3f00d52a458c0abafb6b73a4 --pr 3912` exited 0 with `GREEN ce21b136c649d60e3f00d52a458c0abafb6b73a4 pending: none red: none` at 23:50:57Z (`ev/classify.log`). The two earlier `gate` runs at this head (jobs 140208391442 and 140208877194, 22:55-22:57Z) concluded failure about a minute in, while the suite was still running. Classify read them as pending and then as superseded, with no red. `tests / nightly-status` is red, but it reports main's last nightly run and is not in the `owed-reds` set (`ev/owed_reds.txt`), so no answer is owed.
- Figures carried, not re-run (cite CI's heavy runs): gate scope `MODE: FULL` and the governance self-test results, which are host-specific per the body. CI's runs at this head are the authority for both.

## Findings

- Surviving hand mutant: `REPLAY_JOB_SETUP_S` 20.0 -> 0.0 leaves every control green, because no control sits within the 16 s that the setup term moves the limit. It is a calibration constant whose only effect is a 16 s shift in a 0.8-share limit, and it is not a behaviour the body claims to pin. Carry: dismissed: calibration constant, inside every control's margin by design, no claimed behaviour unpinned
- Surviving hand mutant: cap 60 -> 600 in tests.yml leaves every control green. The check is one-sided by design (it guards against a cap too small for the lane), and the body claims no upper bound. Carry: dismissed: one-sided guard by design, no upper-bound claim made

## Notes

- Note: stale-body: `dev/programme/delivery/3912.md`'s row still titles the PR "raise the replay job timeout to 45 min", while the PR title and diff say 60.
- Note: stale-body: the body's `## Null control` list is labelled "ok at 45" and "At 45 it fires on none". The head's cap is 60, the reviewer re-derived the table at 60 with the same verdicts, and the body's following paragraph covers 60.

## Friction

none
