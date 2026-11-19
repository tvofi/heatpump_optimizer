Lands three round-11 audit box results on main. Each box pushed one result commit with no history shared with main, so none could be opened as a pull request:

- `handoff/audit-r11-find-D3-m5` (`9abc45c9e2`): the D3-s1 seat's evidence under `dev/audit/rounds/round11/D3/s1/` and `reports-D3-m5.json`. That is one new finding, D3-s1-52 (low): `tests/closure.py`'s `_widen` unions `tests/plan_view.py`'s closure into `tests/card_drift.mjs`'s, though `card_drift.mjs` compares two renders over one shared payload, so no cell edit can move it. It also carries the M5 kill matrix and gate-table state under `D3/s1/state/`.
- `handoff/audit-r11-sweep-SW2` (`1a950ed6fd`): the class sweeps N-solve-recompute (2 instances, barriered), N-stale-step-actuation (1, not barriered) and N-staleness (1, barriered), under `dev/audit/rounds/round11/sweep/`, and `reports-SW2.json`.
- `handoff/audit-r11-sweep-SW4` (`f8457e044a`): the class sweeps N-table-value (0), N-unbounded-retention (2, not barriered) and N-unbudgeted-background (0), and `reports-SW4.json`.

Every file of the three trees except `__pycache__/` and each box's top-level `CHECK.txt` is copied unchanged, 317 files in all. None was on main and none overwrites a main file. Each box's `CHECK.txt` reads `ok` for each of its reports. No production code changes. Every new file sits under `dev/audit/`, which `tests/closure.py` lists as INERT by prefix, as for the round-11 record in #3723. This PR does not fold, judge or register anything. The new instances and D3-s1-52 still go through the round's verify and judge steps.

To let the record pass its own gates, three landed harnesses were changed: `D3/s1/finalize.py` walked `HERE.parents[5]`, and the two sweep `harness/enumerate.py` files walked `parents[6]`. That names `dev/`, not the root, so their `--controls` arm read no package. `tests/harness_headers.py`'s depth-seam scan refuses all three. Each now inlines `tools/audit/repo_root.py`'s `repo_root`, and both sweep `--controls` runs print `controls OK`.

The SW2 and SW4 reports name their enumerators at `dev/audit/rounds/round11/D14/sweep-N-*/`, the path inside the box. The files land at `dev/audit/rounds/round11/sweep/N-*/harness/`, as the box tree holds them. The reports are evidence as the boxes wrote them and are not rewritten.

Issues: none drafted or closed.

One more file outside `dev/audit/`: `dev/governance/config/corpus_excluded.json` gains `dev/audit/rounds/round11/D3/s1/REPORT.md`. `tools/audit/briefs/COMMON.md` names `REPORT.md` by basename, so policy_lint's `named-docs` check reads the landed report as an uncapped named document. The report is round evidence, excluded as the other round-11 seat reports are. Renaming it would break the `report_path` that `reports-D3-m5.json` and `REPORT.json` record. With the entry, `unmeasuredNamedDocs()` returns 0, against 1 without it.

## Head

`1f7a5c06b524f20824536473b82d185c48c7267e`: the authored head, on origin/main `99436a082c`. It holds three commits: the copy, the repo_root fix, and the corpus exclusion.

## Mutation proof

n/a: a record PR carries no fix to break.

## Null control

n/a: no behavioural claim. `tests/harness_headers.py`'s inline scan reads `FAIL depth seams` naming the three harnesses at the copy commit, and rc 0 after the repo_root commit.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
