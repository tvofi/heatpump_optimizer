## 7. The scorecard

Nine lines, report-only, recorded once a day. The reference script is
`scorecard.py` (this directory); it makes no GitHub call.
`$RW` is that directory, `$W` the study's `study/work`, `$R` the orchestrator's read checkout.

| Line | What it is | Rule | Null control (what it must print when the claim is false) | Baseline 2026-11-11 |
|---|---|---|---|---|
| A_gate | the product's release status | share of the last 20 concluded CI push runs on main whose job named `gate` concluded success; unread runs are reported, not guessed | a run whose only failed job is `governance / instrument-self-tests` counts green | 3 of 6 read (14 unread); 16 of 26 over the reds since 2026-11-09 |
| A_run | the machinery-inclusive status | share of the same runs whose run conclusion is success | the same run counts red | 0 of 20 |
| Y_rev | review first pass | over the last 50 pull requests by first verdict, verdicts de-duplicated on (pull request, head, kind, class word): share whose first verdict is `merge` | a bus of merge verdicts only prints 100% | 25 of 50 |
| M_first | bookkeeping at first review | same 50: share whose first verdict is a block in a machinery family (carry, body, CI state, merge state, root-cause form, ruling or roster) | the same bus prints 0% | 3 of 50 |
| Y_train | train first pass | over the last 50 merged pull requests the train named: share never on a `SKIP` or `PARK` line | a log with no such line prints 100%; a pull request the train never named is not counted | 25 of 50 |
| H | hotfix load | hotfix-named merges among the last 50 code merges, with the production merges among those 50 beside it | none: it is a naming measure and is read with that caveat | 18 of 50; 10 production |
| S | size | `tools/audit/machinery_ratchet.py --measure --head origin/main` (non-production merges per 580, churn per 1 000 product lines), and machinery lines over product lines from `git grep -c ''` over `tools .github .claude dev/governance` against `custom_components blueprints` | a frozen machinery gives a flat or falling ratio | 498 of 580 (cap 521); 12 299 (cap 14 797); 180 193 / 99 739 = 1.81 |
| E | escapes | roster groups whose source is an outside report, and hotfix or bug groups whose files include the product; the number still open | a round with no escape adds none | 24 and 13; 19 open |
| C, K | detection delay and seat cost | C: longest row of consecutive cancelled main runs in the last 50; K: recycle lines of the standing dispatch and triage seats in the day's sweep record | C is 0 when no main run is cancelled; K is 0 with no recycle | C 6 (8 over the window); K 16 in session 14 |

Daily refresh, in order (about one GitHub read per new concluded main run, plus one listing):

```
gh api "repos/tvofi/heatpump_optimizer/actions/workflows/389816862/runs?branch=main&event=push&per_page=100" > page.json
python3 $RW/runs_refresh.py $W/main_ci_runs.json runs.json page.json        # prints the job reads owed
gh api "repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs?per_page=100&filter=latest" > $RW/jobs_<id>.json   # one per id printed
python3 $W/verdicts_dump.py $R verdicts.json
python3 $W/merges.py $R v7.0.0..origin/main merges.tsv
git -C $R show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json > roster.json
python3 $RW/scorecard.py --runs runs.json --jobs $RW --verdicts verdicts.json --merges merges.tsv \
        --train <state>/merge_train/train.log --roster roster.json
```

Do not issue the job reads while GitHub Actions is degraded; a missing read prints `unread`, which
is the honest value.

What the scorecard is for. It is the baseline from which tvofi can later set thresholds. It is not
yet a control: no line sets an exit code or holds a merge. The one loop that is executed by a
machine today is the machinery ratchet in CI, and carry A6 makes it bind.

---

