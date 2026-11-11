The root-cause document owed by `pr-contract`'s red on PR 3424 at `f9c7952b` (run 42953123178, job 130312858296): `dev/audit/rca/r10-rca-restore-base-skew.md`. Cause: every check-source restore pins `github.event.pull_request.base.sha` while the job checks out the merge commit, so restored files (`roster_lib.py` at `d08ed31049`) and unrestored callers (`carry_audit.py` at `c620ebba96`) come from two mains. Process state (c): the `tests/entities.py` base-restore census (`e55be57447`) asserted the expression's value, the payload base, not the tree it yields, and covered `governance.yml` and `tests.yml` only. The countermeasure, that census's pull_request arm reading the merge commit's first parent over every workflow, is built by R10-HOTFIX-RESTORE-BASE-SKEW; this branch changes no workflow and no test.

Repair round 1 answers the `class-open` block on `49462e86f3`: section 3 now names and dispositions all eleven `base.sha` reads its own rule returns, and places `tests.yml`'s `mutation-pins` `PR_BASE` in the class.

## Head

`30b143922cdc5ed869fe32150ecb20cc8202727b`, continued from `49462e86f3`. Measured at origin/main `a7628041dc`, 2026-11-11 07:18Z (`date -u`). `git merge-tree --write-tree origin/main HEAD` exits 0, so no merge was owed.

## Mutation proof

n/a: the diff is one analysis document and one delivery row. It changes no check, production, test or workflow line. The detector's failing and passing pair is in document section 5, run here with the arm extracted from the hotfix WIP.

## Null control

- Rule output: the literal occurs on 32 lines (`grep -h 'github.event.pull_request.base.sha' .github/workflows/*.yml | wc -l`), 21 of them `PINNED` lines (the same piped to `grep -c` of the PINNED pattern; the 22nd site, `ci.yml:117`, has no literal), so 32 = 21 + 11 and the class rule returns the complement, not a re-count.
- Restore source: restoring `roster_lib.py` from the first parent `c620ebba96` reads `carry_receivable` present (`True`).
- Census arm: `defects=29` on `49462e86f3`'s workflows and `defects=0` on `5ab1c861c8`'s. The same timer around an empty arm reads 0.000 s.
- Window: the window count over `tools/none.py`, a path in no commit, prints 0.

## Figures

Class rule (`fixer.md` step 8), at `49462e86f3`. The output is pasted verbatim in document section 3, with indentation collapsed:
`grep -n 'github.event.pull_request.base.sha' .github/workflows/*.yml | grep -v 'PINNED:.*base.sha\|PINNED=.*base'` returns 11 lines. Each seam is listed with its disposition. "Diff key" means ruling P572, "Do not change the diff bases" (`dev/programme/triage/s6-batch160.md` at roster `b91ac890cf`). Each consumer was read to confirm it.

| seam | consumer | disposition |
|---|---|---|
| `arch-score.yml:63` `EVENT_BASE` | step output `base`; both trees read whole from git | not this class |
| `budget-raise-gate.yml:96` `PR_BASE` | `budget_raise_gate.py --base`: `git show` of budget JSON, `merge-base`, the scorer run in a detached worktree of the base | diff key, P572 |
| `ci.yml:130` `BASE_SHA` | `codeql_scope.py changed --base`, `git diff` | diff key, P572 |
| `dependabot-automerge.yml:69` `ref` | a whole checkout of the base | not this class |
| `governance.yml:213` `MACHINERY_BASE` | `machinery_ratchet.py --check-event`, history reads only | diff key, P572 |
| `governance.yml:246` `SINCE` | `git diff --quiet "$SINCE" HEAD` | diff key, P572 |
| `pr-contract.yml:159` `PAYLOAD_BASE` | output `base` → `PR_BASE`: path list `git diff`, `raises_between` | diff key, P572 |
| `tests.yml:1180` `PR_BASE` | `git show "$PR_BASE":tests/mutation_table.py > tests/_mutation_table_base.py`, run in the merge checkout | **in the class**; open seam, carried to R10-HOTFIX-RESTORE-BASE-SKEW |
| `tests.yml:1501` `BASE` | `closure.py changed --base`, `git diff "$BASE"...` | diff key, P572 |
| `tests.yml:1896` `BASE` | the same | diff key, P572 |
| `tests.yml:2104` `BASE` | `closure.py changed --base` | diff key, P572 |

`tests.yml:1180` is in the class because the base program drives the checkout's own scripts. `tests/mutation_table.py` resolves `ROOT = Path(__file__).resolve().parent.parent` and runs `tests/closure.py`, `tests/stress.py` and the mutated scripts from `ROOT`. The step's `grep -q -- '--pin-killed'`, `'--budget-minutes'` and `'--shard'` guard only the workflow-to-program interface. `_rbs_defects` keys on `_RBS_RESTORE = re.compile(r'git checkout "\$PINNED"|"\$PINNED:')` at `5ab1c861c8`, so it does not read this site.

Other quantified sentences in the document were re-run at `49462e86f3` unless stated:

- 22 restore sites: `grep -c 'PINNED:.*base.sha\|PINNED=.*base' .github/workflows/*.yml` gives budget-raise-gate 1, ci 6, codeql 2, governance 6, pr-contract 1, tests 6.
- The one batch arm: `grep -n 'merge-base FETCH_HEAD HEAD' .github/workflows/*.yml` returns only `ci.yml:117`.
- Census units "only" two files: `grep -n '^_BP_UNITS = ' tests/entities.py` prints `{"governance.yml": "governance", "tests.yml": "tests"}` (line 28736).
- "Both pass": `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ok   and on a pull_request and a push every such restore reads the event's own commit` and ``ok   `policy-docs` restores its graders from the base commit before it grades``. The run's other `FAIL` lines are `a3:*`/`a4:*` HA-stub arms, in no closure of this diff.
- 53 commits, 19 merges: `git rev-list --count d08ed31049..c620ebba96`, with `--merges`. `git merge-base --is-ancestor e08425e904 d08ed31049` gives rc 1; against `c620ebba96`, rc 0.
- Reproduction at `c620ebba96`: `427c4ca874` is no longer fetchable. `roster_lib` from `d08ed31049` gives `False`; from `c620ebba96`, `True`. `git show c620ebba96:tools/audit/carry_audit.py | grep -c 'roster_lib.carry_receivable'` gives 2. The head touches neither file: `git diff --name-only $(git merge-base c620ebba96 f9c7952b) f9c7952b -- tools/audit/seat/roster_lib.py tools/audit/carry_audit.py | wc -l` gives 0.
- Window, at fixed `dbd1ab5b07` with `W="--first-parent --since=2026-11-04T00:00Z dbd1ab5b07"`:
  - `git rev-list --count $W` gives 231 commits; 211 with `--merges`.
  - 58 touch the 22 pathspec patterns of `pr-contract.yml` at `c620ebba96`; 9 touch `roster_lib.py`. Rule: `git log --format=%H -m $W -- <paths> | sort -u | wc -l`.
- Resolver: `time` over 100 `git rev-parse HEAD^1` plus `git merge-base --is-ancestor` pairs took 0.675 s here (7 ms a pair). The reviewer measured 1.609 s.
- Census arm runtime: a one-off probe, not in the tree. It holds `_bp_value` and the `_RBS_` block extracted verbatim from `5ab1c861c8:tests/entities.py`, run 20 times. Median 1.98 s, max 2.47 s on 4 CPUs. With `yaml.safe_load` cached by text, the first run takes 0.222 s, still `defects=29`.
- Run rate: `ci.yml` run 6266 at 2026-11-09T00:20:41Z and run 7265 at 2026-11-11T07:12:02Z (`list_workflow_runs ci.yml`, `perPage=1`, pages 1000 and 1). That is 999 runs in 54.9 h, about 3060 a week. The number of `tests/entities.py` runs a week is not measured.
- Break-even: 3876 s / 1.98 s = 1957 and 3876 s / 0.222 s = 17459 runs a week, against the measured 64.6 min. Against the 1227 PR-minute upper bound: 37181 and 331621.
- 64.6 min: run 42953123178, `created_at` 03:29:46Z to `updated_at` 04:34:20Z (from the reviewer's `actions_get`, which reproduced it).

Not re-derived, so removed from the document: the 05:05Z census "17 of 23 open PRs" and the four-PR `base.sha` sample. The open set has moved, and no conclusion rests on either since the cost test uses the measured occurrence.

Disclosed self-correction: the message of commit `6d65d663a1` says nine reads are settled by P572; it is eight, as the next commit's message records.

## Red checks

None owed. `tests / nightly-status`: red at `49462e86f3`, not in the set `merge_train.py owed-reds` prints; it grades `main`'s nightly lanes, not this diff (`defect-root-cause.md`, tvofi 2026-11-07), so no answer is owed. At `49462e86f3`, `gate` concluded success (job 130378290444).

## Forward-carry

- Open seam `tests.yml:1180` (`mutation-pins`). The payload base's `tests/mutation_table.py` is written into the merge checkout and drives that checkout's scripts. `_rbs_defects` keys on `$PINNED` only and does not read it. The census must also match a payload-base blob written into the checkout (`git show "<event base>":<path> >`), and that source must resolve to the merge commit's first parent like the 22 restore sites. Control: plant `git show "$PR_BASE":x > y` under an env reading `github.event.pull_request.base.sha`; the census must refuse it. Carry: R10-HOTFIX-RESTORE-BASE-SKEW
- Census arm cost. `_rbs_defects` as written spends a median 1.98 s per `tests/entities.py` run, mostly re-parsing every workflow five times. With the parse cached by text it is 0.222 s and returns the same 29 defects. As written it breaks even with the measured occurrence below 1957 runs a week, and `ci.yml` alone runs about 3060. Count `tests/entities.py` runs a week, then cache the parse or justify the cost. Re-measure at the hotfix head. Carry: R10-HOTFIX-RESTORE-BASE-SKEW
- Finding 1 of the review (the cost test misquoted P572's 19 of 23 as reddened): fixed at this head. 19 x 64.6 = 1227 is now labelled an upper bound, and the verdict rests on the measured 64.6 min. Carry: dismissed: fixed at this head in document section 4, own group (fixer.md: a finding in its own seam is built, not carried)
- Finding 2 of the review (no standing cost for the census arm): fixed at this head. The arm is measured at 1.98 s a run (0.222 s cached), and its unmeasured run count is stated as a break-even. Carry: dismissed: fixed at this head in document section 4, own group (fixer.md: a finding in its own seam is built, not carried)

## Friction

none
