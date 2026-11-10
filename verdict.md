Fix review: merge 9f9780c8f686cd94c08b0c1b9e913e946e4fa9f7

bus-nonce: a8b8e941023da41a0bd5474924c8244d

Round 3 on #3402: the third `Fix review:`, after round 1's `blocked b10beaad55c9 config-attack` and round 2's `merge b163dc32376e`. Scope follows the owner's 2026-11-09 ruling. I reviewed the delta `git diff b163dc32376e1f448ea408c4de4c53645850a392 9f9780c8f686cd94c08b0c1b9e913e946e4fa9f7`, round 2's findings and the live required checks. The measured head is `9f9780c8f686cd94c08b0c1b9e913e946e4fa9f7`.

## Findings

None open. Round 2 recorded no open finding at `b163dc32376e`. Round 1's block (the unbounded adopted baseline) and its budget-1 residual were settled there, and this round re-checks both below.

## Evidence

- The delta is main merged in plus one claim resolution. The commits since `b163dc32376e` are two merges of origin/main (`1b564238e`, `9f9780c8f`) and the resolution commit `3e31f5c1c`. I replayed the PR at round 2's head onto the new merge base: `git merge-tree --write-tree cd36e797 b163dc32` gives a tree that differs from this head's in one file only, `tests/golden/claimed_drift.txt` (`ev/delta_vs_replay.diff`). That replay conflicted only in that file. So no line of production code, test or instrument differs from a mechanical merge of round 2's reviewed head with main.
- Production overlap. Main's delta (chiefly #3297, R10-HOTFIX-COP-UNMEASURED) touched six of the PR's production files: `config_flow.py`, `const.py`, `strings.json` and the de/en/sv translations. All six auto-merged without conflict. `heat_curve.py` and `off_restore.py`, where the reviewed logic lives, are untouched by main. The overlap is additive keys and option pages on different flow pages, and the config_flow golden and `tests/config_flow_steps.py` in CI cover it. I found no non-obvious risk to the reviewed code, so I did not extend the review.
- Claim resolution (`3e31f5c1c`). Main's `config_flow` claim (#3297) and the branch's both rewrote one scenario, and the claimnotes driver refused, as `claim-files.md` says it must. The resolution keeps main's five `coord_*` lines and restates `config_flow` as this branch's own move, the `persistent` option (two options leaves). Main's replaced line is inert against origin/main, because those leaves are already in main's fixture. `GOLDEN_MODE=drift tests/env_drift.py --all origin/main` at this head prints `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`, rc=0 (`ev/env_drift.log`). `claims-for: 7.1.9` equals `VERSION` 7.1.9.
- Focus re-check, round 1's block. The clamp still stands at this head: `write_persistent` adopts `_within_range(reading.value - (state["written"] - baseline), reading)`. The stated departure from P6 (bound at adoption, rather than refuse or bound at restore) is unchanged from round 2, which judged it sound. I re-ran round 2's runner (`ev/mcmd.sh`, `ev/mut.py`) at this head. Unmutated it prints `ALL 106 FEATURES BLOCK PASSED`, rc=0 (`ev/block_head.log`), the same count as at `b163dc32376e`. All 7 mutants are killed (`ev/mutants.log`): M21 (adoption bound removed), M22/M23 (one side of the helper deleted), M24 (adoption bounded on the floor only), M25 (plan target unbounded), M26 (reserve +2 -> +1, the budget-1 residual) and M27.
- Versions (step 5): the delta does not touch `VERSION`, `manifest.json` or `RELEASE_NOTES.md` beyond what main brings in.
- Merge (step 13): `git merge-tree --write-tree origin/main 9f9780c8f686cd94c08b0c1b9e913e946e4fa9f7` exits 0 against origin/main `fc022fd193dd` (`ev/merge_tree.txt`).
- CI (step 11): `merge_train.py classify 9f9780c8f686cd94c08b0c1b9e913e946e4fa9f7 --pr 3402` read WAIT (`pending: gate`) from 11:47Z, then exited 0 at 12:31:45Z with `GREEN 9f9780c8f686cd94c08b0c1b9e913e946e4fa9f7 pending: none red: none` (`ev/ci_classify.log`). The first `gate` run, id 129807253058, concluded failure at 11:42:25Z, before the other jobs finished. Classify reads the latest runs and reports no red, so no context in `merge_train.py owed-reds` (`ev/owed_reds.txt`, 23 required contexts) is owed a `## Red checks` answer.
- Head re-read before return (step 12): `git ls-remote origin refs/pull/3402/head` is `9f9780c8f686cd94c08b0c1b9e913e946e4fa9f7`, unchanged.

## Friction

- `merge_train.py owed-reds` takes no head or PR argument; it lists the ruleset's required contexts. The brief's "for the head you review" reads as if it filtered by head. I ran it bare.
