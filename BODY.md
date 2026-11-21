Lands the round-11 audit box D3-top6 result on main. The box pushed one result commit, `handoff/audit-r11-find-D3-top6` (`fdd9e2d827`), with no history shared with main, so it could not be opened as a pull request.

The box ran the D3-s1 seat's D3.M3 slice (T1-T3: full net and full gate over the prescreen survivors). Its report is `dev/audit/rounds/round11/D3/s1/REPORT-D3-top6.md` with `reports-D3-top6.json`: universe 35 survivors, 30 examined, 5 not reached. It carries one new finding, D3-s1-02 (low): no suite check pins the `k <= 0` guard of `tariff._smooth_topk_sum`, and the scalar and batch top-k disagree at `k = 0`. Its `CHECK.txt` reads `ok D3-s1`.

Every file the result commit adds under `dev/audit/rounds/round11/` is copied, 265 files, except `D3/s1/CHECK.txt`; the tree held no `__pycache__/`. None was on main and none overwrites a main file. No production code changes. Every new file sits under `dev/audit/`, which `tests/closure.py` lists as INERT by prefix. This PR does not fold, judge or register anything; D3-s1-02 still goes through the round's verify and judge steps.

The box shares `D3/s1/` with box D3-m5, which #3810 lands. 119 of the shared paths carry the same bytes on both branches, so either merge order adds them once. `D3/s1/finalize.py` takes #3810's blob, which has the canonical `repo_root`. Eight paths differ between the two boxes and land here with a `-D3-top6` suffix, so neither PR conflicts with the other or overwrites its copy: `REPORT.md`, `REPORT.json`, `m5_solves.py`, `prescreen.py`, `state/baselines.json`, `state/null.json`, `state/prescreen.log` and `state/results/c3c6/6e6026d857732e96.json`. The `report_path` in `reports-D3-top6.json` and `REPORT-D3-top6.json`, and the box's own scripts that call or write those files (`box_report.py`, `top6_compose.py`, `t3_drive.sh`, `phase_a.sh`, and the two renamed scripts), name the suffixed paths. Log and JSON evidence text still names the unsuffixed paths, as the box wrote it.

Twelve box harnesses walked a fixed parent count to the root (`parents[6]`, or `HERE.parents[5]`), which `tests/harness_headers.py`'s depth-seam scan refuses. Each now inlines `tools/audit/repo_root.py`'s `repo_root`, and the inline scan is rc 0. The evidence carried this host's home paths; `ref_privacy.py scrub` rewrote them to `~`. The cloud-box paths under `/home/user/` stay, as in 62 round-11 files already on main.

Issues: none drafted or closed.

## Head

`0213be8e42ae2c0ecf7ebf47de13444cab1991ce` merges main `a8efe1d` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`fef69b4db38b10c4a9c0ae578018496ebf1deadd`: the code tip, which the live head `e1559416b6d2735b084b890e6cc19a358f1d7be9` holds. The authored commit was `d325ee730d8e755b0fa402cb9f2517d29de6e086` on origin/main `7ae05284d5`, one commit: the copy, the renames, the repo_root fix and the scrub.

## Mutation proof

n/a: a record PR carries no fix to break.

## Null control

n/a: no behavioural claim.

## Figures

none

## Red checks

Three checks failed on earlier heads of this branch and are green at `0213be8e` (run 44922848472: `governance / policy-docs`, `governance / wave-script` and `tests / closures` all `success`). Each answer names the head it was red on and the log read.

- `governance / policy-docs`: red at `b6443317` (job 135515161080) on the machinery ratchet, `FAIL churn_per_kilo_product_lines 49943 <= 34898 + band 3636`: the box's raw full-gate logs under `D3/s1/state/gates/`, about 16k lines each, put 343194 lines into the copy. Cause: this PR's own files, now fixed. `fef69b4db3` trims those logs to head and tail, and the PR carries it. The cheaper detector exists and is standing: `python3 tools/audit/machinery_ratchet.py --check --base origin/main --head HEAD`, seconds, run before the push. It was not run before the first push, so the red reached CI once.
- `governance / wave-script`: red at `5becddba` (job 135737025354, a `workflow_dispatch` run), on `FAIL ownerOnlyRecord reads every declared owner-only brief's id, seat and dimension` with `owner-only declared [none]`. Cause: inherited, a stale base, not this PR's files; the PR touches no workflow, no policy script and no brief. CI pins the base's check script over the branch tree, and that branch tree predated main's `dev/governance/dimensions/DX0.md` (landed by #3739 at e893cd3d), so the check found no owner-only brief. The same check run from `5becddba`'s own tree is clean, so the tree is not at fault. Main's wave-script at e893cd3d is `success`. Merging main (`818d5df371` onward) supplied the brief, and the check is green at `0213be8e`. The cheaper detector is `base_fresh.py` before a dispatch or push, one merge of cost; no new detector is owed.
- `tests / closures`: red at `0151b17020` (job 135526428948), `INERT READS UNDER-APPROXIMATED`: 24 of the box's harnesses under `dev/audit/rounds/round11/D3/s1/` open INERT files that the committed `inert_reads` for `tests/harness_headers.py` did not list. Cause: this PR's files, correctly repaired by the closures-autofix job, which pushed `5becddba58` (`ci: re-record closures`, `tests/closures.json` +34 lines). No bot commit is pending and `tests / closures-autofix` is `skipping` at the head. The detector is `tests/closure.py check --partial` after `derive_closures.sh --single`, which `ci-autofix.md` assigns to that job; a local re-derivation is off Linux and not run.

## Forward-carry

none

## Friction

none


