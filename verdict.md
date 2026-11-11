Fix review: blocked 49462e86f3dcb85a27f81517aaa358a545a12873 class-open: section 3's base.sha rule returns 11 reads outside the 22 restore sites, the document names and dispositions 2

bus-nonce: 995e15fedcb3f4d841a71d2da2876c86
pending-ci: gate

Round: first review of PR 3438 (R10-RCA-RESTORE-BASE-SKEW), head `49462e86f3dcb85a27f81517aaa358a545a12873`, which is the PR's head per the body's `## Head` and the API (`pull_request_read get`). Merge with origin/main: `git merge-tree --write-tree origin/main 49462e86f3` exits 0 (tree `895194943d`), no conflict.

## Block

Section 3 of `dev/audit/rca/r10-rca-restore-base-skew.md` says: "Other `base.sha` reads, `grep -n 'github.event.pull_request.base.sha' .github/workflows/*.yml` less the 22: `arch-score.yml:63` ... and `dependabot-automerge.yml:69` ... Neither is this class." I re-ran that rule at `dbd1ab5b07`, the commit the document says it measured at. It returns **11** reads outside the 22 `PINNED` lines, not 2 (`ev/repro.txt`):

- `arch-score.yml:63` (EVENT_BASE)
- `budget-raise-gate.yml:96` (PR_BASE)
- `ci.yml:130` (BASE_SHA)
- `dependabot-automerge.yml:69`
- `governance.yml:213` (MACHINERY_BASE)
- `governance.yml:246` (SINCE)
- `pr-contract.yml:159` (PAYLOAD_BASE)
- `tests.yml:1180` (PR_BASE)
- `tests.yml:1501`, `:1896` and `:2104` (BASE)

The document neither names nor dispositions nine of them. Under `fix-review.md` step 6 a seam the body's own rule returns that is neither in the diff nor dispositioned is `class-open`. `root-cause.md` §3 makes the class search part of the deliverable, so a false account of what the search returned is a defect in this PR's only product.

The fix is a document edit. Ruling P572 (`dev/programme/triage/s6-batch160.md` at roster `b91ac890cf`, "Do not change the diff bases") already classes BASE_SHA, SINCE, PR_BASE, MACHINERY_BASE, PAYLOAD_BASE and `tests.yml`'s BASE as diff keys, not restore sources. Citing that disposition and correcting the count settles eight. The ninth needs its own line: `tests.yml:1180`'s PR_BASE does more than key a diff. At `tests.yml:1214` it does `git show "$PR_BASE":tests/mutation_table.py > tests/_mutation_table_base.py`, and that payload-base program then runs inside the merge-ref tree. That is a program from one main executing against modules from another, which is the shape this document is about, even though P572 files PR_BASE under diff bases. The document should state whether it is in the class, or why not.

## Findings

- The cost test misquotes its source. It says "19 of 23 open PRs red at the order (the ruling's count)" and then charges 19 x 64.6 = 1227 PR-minutes. P572 counts 19 of 23 *exposed* (their `base.sha` lacks `8efacee48d`), and it says plainly "Not measured: how many of them reach `carry_receivable`". The verdict of the cost test survives: one observed occurrence (64.6 min) against under 0.3 s per PR still pays. The 1227 figure is an upper bound presented as a measurement, and should be labelled as one or replaced with the measured single occurrence. Carry: R10-RCA-RESTORE-BASE-SKEW
- The cost side costs the resolver's runtime (the hotfix's fix) but not the standing cost of the named countermeasure, the `tests/entities.py` census arm. "No new script" is not a number. Carry: R10-RCA-RESTORE-BASE-SKEW

## Evidence

Head reviewed: `49462e86f3dcb85a27f81517aaa358a545a12873` (`ev/HEAD.txt`). The diff is one document and one delivery row. It changes no production, test or workflow line, so no mutant is owed (step 1 is not applicable), and VERSION, the manifest and the notes heading are untouched.

Measurements re-run with the finder's commands:
- Run 42953123178 (`actions_get`): run_attempt 2, event pull_request, created_at 03:29:46Z, updated_at 04:34:20Z, which is 64.57 min. **Reproduces** 64.6.
- Job 130312858296 log: `carry_audit.py` line 446 `return roster_lib.carry_receivable(group)` raises `AttributeError: module 'roster_lib' has no attribute 'carry_receivable'`. **Reproduces.**
- `git log -1 --format='%P' 427c4ca8`: **not re-derivable**. GitHub's merge ref has since moved (`refs/pull/3424/merge` is now `ae8d899af0`, with parents `dbd1ab5b07` and `18785cfd01`) and `427c4ca874` is no longer fetchable. The run API's `referenced_workflows` names sha `427c4ca8748e…` on `refs/pull/3424/merge`, and P572 quotes the checkout line naming parent `c620ebba96`. Corroborated, not re-derived.
- `git rev-list --count d08ed31049..c620ebba96` = 53, and with `--merges` = 19. **Reproduces.**
- `git merge-base --is-ancestor e08425e904 d08ed31049` rc 1, and against `c620ebba96` rc 0. **Reproduces.** `e08425e904` (2026-11-10) touches both `roster_lib.py` and `carry_audit.py`.
- `c620ebba96` committer time 03:29:26Z. **Reproduces.**
- Restore pathspec (`pr-contract.yml` at `c620ebba96`, lines 111-133): it includes `tools/audit/seat/roster_lib.py`. `'tools/audit/*.py'` is absent (count 0). **Reproduces.**
- Reproduction in a detached worktree at `c620ebba96` (`427c4ca8` is unavailable, see above; the PR head does not touch either file): `roster_lib` from `d08ed31049` prints `False`, and from `c620ebba96` prints `True`. **Reproduces.** `git show c620ebba96:tools/audit/carry_audit.py | grep -c 'roster_lib.carry_receivable'` = 2. **Reproduces** (I read it at `c620ebba96`, not at `427c4ca8`).
- The 22 `PINNED` sites at `dbd1ab5b07` per file (budget-raise-gate 1, ci 6, codeql 2, governance 6, pr-contract 1, tests 6). **Reproduces.**
- First-parent commits since 2026-11-04T00:00Z to `dbd1ab5b07`: 231, of which 211 are merges. Commits touching the pr-contract restore pathspec (64 entries, `-m`): **58, not 57**. Touching `roster_lib.py`: 9. **Reproduces.** The document's "231 first-parent merges" counts commits, not merges. The off-by-one does not change any conclusion (`ev/costtest.txt`).
- Resolver timing: 100 `rev-parse` + `merge-base --is-ancestor` pairs took 1.609 s here, 16 ms a pair against the claimed 13 ms. **Same order.**
- "17 of 23 open PRs at 05:05Z" with 3 null-control PRs: **not re-derived**. It is a point-in-time census of the open set, which has moved since 05:05Z. P572's own census at roughly the same time reads 19 of 23 against `8efacee48d`, a different marker commit.
- Process state (c) citations: `e55be57447` (2026-10-23, R10-CI-LAYOUT-P2) adds 73 lines to `tests/entities.py`. The check "and on a pull_request and a push every such restore reads the event's own commit" is at `tests/entities.py:28790` at `dbd1ab5b07`. `_BP_UNITS = {"governance.yml": "governance", "tests.yml": "tests"}` is at line 28736. The `46a6ac4d68` (2026-09-22) pin text is at line 34474. **All reproduce.** State (c) is supported: the census existed, ran and passed, and its unit read the expression's value over two files.
- Countermeasure against the ruling: P572 accepts the restore from `HEAD^1` with a payload-base ancestry assertion, and REJECTS only the proposal's planted-`roster_lib.py` self-test. It leaves the cheaper-detector question to this seat. The document's countermeasure is the census unit change (`_rbs_defects`) plus the resolver's ancestry assertion. That is not the rejected self-test and is consistent with the ruling.
- Census demonstration, which the document records as owed and does not claim to have run. I ran it myself: the hotfix's `_rbs_defects` and `_bp_value`, extracted verbatim from `5ab1c861c8:tests/entities.py` (`ev/rbs_demo.py`, my instrument, built from the hotfix's WIP code). On `origin/main` `dbd1ab5b07`'s workflows it prints `RESULT rbs_defects=29`, including `pr-contract.yml:pr-contract restores from BASESHA`, so it is red on the defect. On the hotfix WIP `5ab1c861c8`'s workflows it prints `RESULT rbs_defects=0`, so it is green once the defect is fixed (`ev/census-demonstration.txt`). The hotfix branch tip is `1cb96d4430` "BLOCKED: the base-pinned graders refuse the new restore-source form", so the demonstrated state is WIP and not landed.
- Finder's harness: none named in the packet. The replay harness `dev/audit/harnesses/r10_restore_base_skew.py` exists only at the hotfix's WIP ref, and the document says so. I did not run its `--source` replay.
- figure_lint: 0 resolved, 9 not verified, 0 refused (git and inline-python commands). I re-ran those commands by hand above.
- CI: merge_train.py classify read `WAIT 49462e86f3dcb85a27f81517aaa358a545a12873 pending: gate red: none` (exit 3) on every poll from about 06:33Z to 07:01:36Z, which is past the 30-minute bound (`ev/classify-*.txt`, `ev/classify-poll.txt`). Hence the `pending-ci: gate` line. The review packet's digest at render showed `gate` id=130364149424 concluded failure, but classify decides, and it reads pending. `gate` is in `merge_train.py owed-reds`' set. If it concludes red at this head, the body's `## Red checks: none` owes it an answer. The block above stands independently of CI.
