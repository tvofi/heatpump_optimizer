# Appendix B: the measured baseline (R11-PRE-PARALLEL-PIPELINE)

Window: 2026-11-07T00:00Z to 2026-11-14T00:00Z, the non-record pull requests
merged on main's first-parent line. Every figure is printed by a script under
`harness/` over the files under `data/`; the recorded output of each is under
`out/`. `PD_REPO` names a checkout holding the bus refs (`review/*`,
`verdict/*`, `handoff-body/*`), `PD_STATE` the instrument state root.

## How the data was taken

| file | source | reads |
|---|---|---|
| `data/merges.json` | `harness/collect_git.py`: `git log --first-parent origin/main`, the bus refs, the roster | git only |
| `data/prs.json` | `harness/fetch_prs.py`: createdAt, reviews and timeline per pull request | GraphQL, 12 queries |
| `data/runs/*.json` | `harness/fetch_runs.sh`: `ci.yml` workflow runs per half day, 2026-11-07 to 11-14 | REST, 45 reads |
| `data/main_gate.json` | `harness/fetch_main_gate.py`: the `gate` check-run of the push run at each first-parent commit | GraphQL, 49 queries |
| job-level shares | the s12 CI throughput study (state directory `s12/ci-tput`, 2026-11-05 to 11-07), not re-taken | none |

## Figures

| id | figure | literal | enumerator (output file) |
|---|---|---|---|
| B1 | merges in the window | 215 (146 group, 56 hotfix, 13 fly-in) | `baseline.py` (`out/baseline.txt`) |
| B2 | handoff to merged, mean / p50 / p90 | 17.36 / 15.12 / 32.73 h | `baseline.py` |
| B3 | handoff to PR open, mean / p50 / p90 | 2.94 / 0.64 / 9.50 h | `baseline.py` |
| B4 | PR open to first verdict, mean | 2.48 h | `baseline.py` |
| B5 | first verdict to FIRST merge verdict, mean | 4.38 h | `segments.py` (`out/segments.txt`) |
| B6 | FIRST merge verdict to merged, mean / p50 / p90 | 7.60 / 3.90 / 19.77 h | `replay_pipeline.py`, line "today" |
| B7 | verdicts issued after a first merge verdict | 78 in 40 PRs (56 merge, 22 blocked) | `segments.py` |
| B8 | first-pass merge verdicts | 102 of 215 | `baseline.py` |
| B9 | repair rounds and their wall | 266, mean 5.92 h, p10 1.43 h | `rounds.py` |
| B10 | inside a round: blocked to repair commit / repair commit to pushed / pushed to dispatched / review | 3.93 / 1.15 / 0.52 / 1.09 h | `segments.py` (first two), `rounds.py` (last two) |
| B11 | rounds opened by a mechanical class | 69 of 266, 313 h | `segments.py` |
| B12 | `ci.yml` runs per merged change, distinct heads | 12.43, 4.38 | `baseline.py` |
| B13 | runs at a head that already had a run | 1730 of 2672 | `baseline.py` |
| B14 | merges of main into the 215 branches | 826; clean under `git merge-tree` 739 | `absorbs.py`, `absorb_need.py` |
| B15 | the 826 by actor | instruments 494 (at PR open 191, in review 124, after the final verdict 178); fixer seats 278 (195 clean); merge-main bot 41 | `absorbs.py`, `absorb_need.py` |
| B16 | PRs whose head moved after the final merge verdict | 130 of 215; 122 by a remerge of main; the train's own recarry 141 commits in 75 PRs | `who_moved.py`, `segments.py` (the train's share) |
| B17 | merged PRs in a serial class of the train | 140 of 215 (grader 120) | `replay_pipeline.py`, line "entries in a serial class" |
| B18 | main's `gate` after a merge | 215 success, 44 failure, 32 cancelled of 291 | `main_gate.py` |
| B19 | red-streak starts | 24 over 259 judged merges; among the 215: 20, of which 14 one red then green | `main_gate.py`, `replay_pipeline.py` |
| B20 | train batches, 2026-10-16 to 11-14 | 401, 249 of one entry; 358 skips of 1009 entries; 408 recarry starts | `train_stats.py` |
| B21 | serial routings by reason | grader 427, workflow 122, budget 111, claim 85, bot-head 20 | `train_stats.py` |
| B22 | FULL run wall, p50 | 43 to 46 min on 11-07 and 11-08; 74 to 104 min on 11-13 and 11-14 | `ci_load.py` |
| B23 | runner-minutes by class (s12 study) | invalidated by a merge of main 14.7 %; cancelled-superseded 10.1 %; main push runs 12.6 %; the PR code run that gated a merge 8.5 % | `cards.md` and `analysis.txt` of that study |
| B24 | job cap and its use (s12 study) | 40 concurrent jobs; at 38 to 40 for 11.2 % of the time | `EVIDENCE.txt` of that study |

Note on B5 to B7. The first cut of this baseline measured the post-verdict wait
from the LAST merge verdict (4.65 h) and booked everything before it as repair
(7.3 h). That is wrong for a pull request re-reviewed after approval because its
head moved: B7's 78 verdicts are review turns the pipeline caused. The split
from the FIRST merge verdict is the one the design uses. The first cut stays
printed by `baseline.py` and `rounds.py`; the corrected figures are printed by
`segments.py` and by `replay_pipeline.py`'s "today" line.

## Null controls

- The four segments sum to the measured total: B3 + B4 + B5 + B6 = 17.40 h
  against B2's 17.36 h (the 0.04 h is two pull requests with no handoff-body
  ref).
- `replay_pipeline.py`'s "today" line is the identity: it must print B6.
- B14's "clean" is plain `git merge-tree --write-tree` of the merge's two
  parents; a conflict the claimnotes driver would have resolved counts as a
  conflict, so 739 is a lower bound on the merges no conflict asked for.
- B19 counts a red at the push run whose head had passed its own pull
  request's required set: that is the rate at which "green on its own head"
  was "red on FULL at main" in round 10, the exposure ruling 3 accepts.

## The constraint, named

1. The largest single block is approval to main (B6, 44 % of B2), and its
   cause is head movement that no conflict asked for (B14, B15, B16), driven
   by the train's serial classes (B17, B21) and by `open_pr.sh`'s
   unconditional merge of main.
2. The repair loop to first approval (B5, 25 %) is second. A round's wall is
   5.4 times the review inside it (B9, B10); the wait is before the repair
   commit.
3. CI job-hours bind only under the closing days' load (B22, B24), and they
   set the size of block 1 through re-runs (B12, B13).
4. Conflict coupling is small beside clean absorbs: 87 of 826 merges of main
   answered a conflict (B14).
