Owner ruling (tvofi, 2026-11-07, waste-study decision cards, card 2, ruled NARROW): a fix reviewer that returns `blocked` with class `mutation-vacuous` or `class-open` lists, in that one verdict, every survivor or open seam it found at that head. It no longer names one per round. The repair fixer then answers the whole list in one repair.

This is **policy**. It changes what a reviewer seat must do (`dev/governance/roles/fix-review.md` steps 1 and 6), so it merges only on tvofi's approving review.

What changes:
- `fix-review.md` step 1: `blocked <sha> mutation-vacuous: <mutants>` names every survivor the reviewer's driver run reports at that head. The driver output goes in the evidence directory, and `push-verdict` reads it there (`survivor_list.py`).
- `fix-review.md` step 6: `blocked <sha> class-open: <seams>` names every seam the review found, not one per round. No hunt past what the review already ran is owed. A listed item whose harness does not move under its own perturbation is void (`judge.md`), so padding the list buys nothing.
- `tools/audit/seat/survivor_list.py` is the mechanical half. `bus.sh push-verdict` runs `survivor_list.py check <verdict> <evidence dir>` and refuses a `mutation-vacuous` verdict that omits a survivor `<file>:<line>` (or a spec name) that the evidence's driver output reports. Both verdict paths go through this: a local seat's push, and `cloud_relay.sh`, which calls push-verdict. It reads the survivor lines of `mutant_run.py` (`--diff`, `--spec`) and `tests/mutation_table.py` (`LIVES`, and `--pin-killed` through its owner `mutation_table.survivor_sites`). It drops a site that the table marks `[triaged equivalent]`. Any other verdict class passes unread.
- `class-open` has no mechanical check. There is no driver output to count a seam against: the enumeration rule a body names is free-form, so the obligation stays in the reviewer contract. The body says so here, as the brief asked.
- The rule text is paid for inside `fix-review.md` by trimming spent prose in steps 2, 4, 8, 9, 11 and 13, with no meaning dropped. The file stays inside its `policy_lint.mjs --budgets` caps (133 of 140 lines, ~2449 of 2451 tokens). No budget was raised.

In-flight edits to `fix-review.md`: R10-PROCESS-SLIM (`handoff/r10-process-slim`), R10-HOTFIX-NONREQUIRED-REDS (`handoff/r10-hotfix-nonrequired-reds`) and R10-DISPATCH-AT-HANDOFF (`handoff/r10-dispatch-at-handoff`, `-p2`). This diff edits steps 1, 2, 4, 6, 8, 9, the GREEN-mutation paragraph of step 11 and step 13. `git merge-tree --write-tree` against each sibling head is in Figures (taken at the previous head): one sibling, `-p2`, now conflicts in `fix-review.md`.

## Repair

Round 2 repair. `governance / instrument-self-tests` was red at `c9ba955f30fc` because the step this PR adds to `.github/workflows/governance.yml` (`Show the survivor-list check ...`) had no `id:` and an unconditional `if: ${{ !cancelled() }}`.
- Failing check first, at `c9ba955f30fc`: `python3 tools/ci/selftest_scope.py static` printed `UNGATED step 'Show the survivor-list check (tools/audit/seat/survivor_list.py) refusing its own fixtures': its if: does not read steps.scope.outputs.<its own id>` and `107 gated step(s), 1 problem(s)`.
- Fix, as its neighbours are gated: `id: survivor-list` and `if: ${{ !cancelled() && steps.scope.outputs.survivor-list == 'true' }}`. The scope table `tools/ci/selftest_closures.json` is measured, not hand-written, so the entry came from `python3 tools/ci/selftest_scope.py record --step survivor-list` (strace, Linux): it reads `tests/closures.json`, `tests/mutation_table.py`, `tools/audit/seat/mutant_run.py` and `tools/audit/seat/survivor_list.py`. `selftest_scope.py` is unchanged.
- Null control, same command at the fix `419fa71b56bd`: `selftest_scope static: 108 gated step(s), 0 problem(s)`, and `python3 tools/ci/selftest_scope.py --self-test` prints `selftest_scope self-test: 90 checks, 0 failed`. Before the table entry was recorded, `static` printed `STALE tools/ci/selftest_closures.json: its steps differ from the workflow's: missing ['survivor-list']`, so the table check is live too.
- The round-1 repair below stands; no production file changed in round 2. Carry: R10-REVIEW-ENUMERATE

### Round 1

Round 1 repair of the blocked verdict `Fix review: blocked 81741e448f32052efde42f2c0fe2605c8083e19f mutation-vacuous: tools/audit/seat/survivor_list.py:77 left-boundary lookbehind unpinned`. The verdict lists two items, and this repair answers both.

- Survivor `tools/audit/seat/survivor_list.py:77`, the left-boundary lookbehind `(?<![\w./-])` of the whole-token rule in `unlisted`. Fixed in `c7b72252c`. This commit adds the self-test arm `a key is a whole token: tools/setup.py:3 does not list setup.py:3`, which is the reviewer's own example: a verdict that names only `tools/setup.py:3` must leave survivor `setup.py:3` unlisted. The mutant `token_lookbehind_off` survives at `81741e448` and is killed at this head (Mutation proof). No production line changed. Carry: R10-REVIEW-ENUMERATE
- Stale scope figure. The previous body's `--files` scope line was taken before `tests/closures.json` entered the diff. Re-taken under Figures at this head with both commands. Carry: R10-REVIEW-ENUMERATE

The reviewer's `class_anchor` survivor (`^` and the trailing `:` dropped from `CLASS`) was judged equivalent in the verdict and was not blocked on. It is left alone. Carry: dismissed: the verdict judged it equivalent (`re.match` anchors at the start, and no verdict class extends `mutation-vacuous`)

## Head

Code head `419fa71b56bdd45556ce2ea8eafe99405c948481`: the reviewed-and-merged `c9ba955f30fc8f64b2e0c3865dcfe9dd609ef822` plus one commit changing `.github/workflows/governance.yml` and `tools/ci/selftest_closures.json` only. Figures other than those under Repair describe `c9ba955f30fc` and its predecessors; no file they read moved.

## Mutation proof

Run at `32fbd8338c86`: `python3 tools/audit/seat/mutant_run.py --spec <6 mutants> --cmd 'python3 -I tools/audit/seat/survivor_list.py --self-test'` (copy-tree). Output: `SURVIVED NULL`, then six kills:
- `KILLED class_gate_off`: the class predicate is forced to `if True: return []`.
- `KILLED listed_always`: the listed test is forced false.
- `KILLED triaged_not_dropped`: `found - triaged` becomes `found`.
- `KILLED check_rc_zero`: `if missing:` becomes `if False:`.
- `KILLED token_lookbehind_off`: the reviewer's survivor, with `(?<![\w./-])` deleted.
- `KILLED token_lookahead_off`: `(?![\w])` deleted.

Control at the reviewed head `81741e448`, with the same `token_lookbehind_off` spec run in place: `SURVIVED token_lookbehind_off`. This reproduces the verdict.

`bus.sh`'s pin is unchanged by this repair. The arm `push-verdict refuses a mutation-vacuous verdict naming one of two survivors, and review/7 does not move` was re-run by the reviewer at `81741e448` and goes red when the call is deleted.

## Null control

- `survivor_list.py --self-test` at this head prints all three of `ok null control: another blocked class with the same evidence passes`, `ok null control: a merge verdict passes` and `ok evidence with no driver output counts nothing`.
- The new arm has a null twin: the existing arm `a key is a whole token: :12 does not list :120` pins the right boundary. `token_lookahead_off` is killed and `token_lookbehind_off` is killed by the new arm, so each side of the token rule has its own killing arm.
- `bus.sh --self-test`: `ok null control: another blocked class over the same evidence proposes`.

## Figures

- `python3 -I tools/audit/seat/survivor_list.py --self-test`: `survivor_list self-test: 20 checks, 0 failed`. That is 19 at `81741e448` plus the one new arm.
- `bash tools/audit/seat/bus.sh --self-test`: `bus self-test: 162 checks, 0 failed`.
- Scope at this head, by `fixer.md` step 5's command: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 3 script(s) run, 30 scoped out` over 8 changed files, `tests/closures.json` among them, running doc_claims, entities and harness_headers. The reviewer's command, `python3 tests/closure.py select --files $(git diff --name-only $(git merge-base origin/main HEAD)...HEAD)`, prints `MODE: FULL` at the same head. The `tests/closures.json` edit adds one `INERT` entry. The `--diff` selector scopes past it and `--files` does not. The scoped gate in `tests/run.sh` calls `closure.py select --diff`. I have not traced why the two differ, so no cause is claimed. The previous body's `--files ... SCOPED -- 3` was taken before that file entered the diff, and it is withdrawn.
- `PYTHONPATH=tests/hastub` scoped scripts at this head: `tests/doc_claims.py` printed `ALL 296 checks PASSED`, `tests/entities.py` printed `ALL 2668 ENTITY CHECKS PASSED` and `tests/harness_headers.py` printed `ALL 112 HARNESS HEADER CHECKS PASSED`, each rc 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs --budgets`: `dev/governance/roles/fix-review.md` 133 lines (printed by `--budgets` under the path `tools/audit/briefs/fix-review.md`) (cap 140), ~2450 tokens (cap 2451), re-taken at this head. The rule is `Math.round(bytes / 4)`. This repair does not touch that file.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `125 self-testing, 125 wired, 0 unwired`, `0 index gap(s)`.
- `node tools/policy/agreement.mjs`: `RESULT divergent=0 unregistered=0`. The 6 `REFUSED` lines ask for `--py-json`, which this bare run did not pass.
- Sibling conflicts, `git merge-tree --write-tree HEAD <sibling handoff head>`:
  - `r10-process-slim`: rc 0.
  - `r10-hotfix-nonrequired-reds`: rc 0.
  - `r10-dispatch-at-handoff`: rc 0.
  - `r10-dispatch-at-handoff-p2` (`089f1da01`): rc 1, on `dev/governance/roles/fix-review.md`. Against `origin/main` it gives rc 0, so this diff causes the conflict. The two hunks are adjacent: `-p2` drops `(a script routes on it)` from the preamble's first-line sentence and rewrites step 7. This diff rewrites steps 6 and 8, which sit on either side of step 7. Whichever lands second merges `origin/main` and resolves by keeping both texts. That merge is the orchestrator's under `fixer.md` step 6, not a re-cut.
- The brief's motivating counts come from `python3 -I tools/audit/seat/review_strength.py --by class`. It reads live verdict refs, so it is named here and not quoted (`fixer.md` step 3).

## Red checks

`governance / instrument-self-tests`: red at `c9ba955f30fc`, and this PR's own. Cause: the step this PR adds was UNGATED (see Repair). Cheaper detector: `python3 tools/ci/selftest_scope.py static`, a workflow-and-table read, about 0.1 s (the `record` run for one step took 0.2 s). It existed and ran only in CI's `instrument-self-tests`; run it in prepr for any diff touching `.github/workflows/governance.yml` or `tools/ci/selftest_closures.json`. I ran it at this head: `0 problem(s)`. Standing cost: that fraction of a second per prepr; a prepr.sh edit is a separate change and is not in this diff.

`tests / fast (3.14)`: red, inherited from main at `2f6d699e` (de.json keys and D6 claim C112) and fixed by #3378. Not this PR's: this diff touches neither `de.json` nor any D6 claim.

`governance / delivery-status` (check-run 128955414223, job 128955414223, 2026-11-09T03:01Z, head `06a3478fdbf3`): red, and it is main's, not this diff's.
- What it graded: `python -I -S tests/delivery_status.py --check` printed `DELIVERY STATUS OVERDUE -- 0 rowed, 12 pending, 1 overdue (overdue at 12 commits)`, naming `#3318 R10-BODY-CONTRACT` as overdue and `#3316` as pending. Those are main's own record rows held for the stamp. The check's own text says it grades main and blocks no merge.
- Not this diff: the `governance.yml` hunk adds one step to the self-test job (`survivor_list.py --self-test`). It does not touch the `delivery-status` job, `tests/delivery_status.py`, the plan, `HANDOVER.md` or any row. The graded count is a function of main's commit count since each held row, which this diff does not move.
- Evidence, same failure line on PRs whose diff touches none of its inputs: #3358 (code files only), check-run 128949628159, `DELIVERY STATUS OVERDUE -- 0 rowed, 12 pending, 1 overdue`, and #3360 (code and blueprint only), check-run 128988774945, `... 3 overdue`. #3364 (check-run 128931369503) prints the identical line with `#3318` overdue. The count grows with main's commits (1 overdue at 03:01, 3 at 05:09). The `delivery-status` job is skipped on main's push runs (check-runs 128972499737, 128924112970), so main prints no line of its own; the rows pending for the stamp are what each PR run reads.
- Cheaper detector and standing cost: `tests/delivery_status.py --check` is itself the detector and is already the cheapest (a local file and git-log read, a few seconds in the governance job). `prepr.sh` deliberately does not copy the exemption (its comment: a second copy would drift) and `policy_lint.mjs --pr-body` already carries it. No cheaper detector exists for a red whose cause is a stamp that has not run; the fix is draining the rows (`web-stamp`), the orchestrator's on main (`defect-root-cause.md`).
- Other checks at this head: `pr-contract` failed only on this unanswered line.

## Forward-carry

none

## Friction

none

## Unpinned sites

`tools/audit/seat/survivor_list.py`'s predicates, both sides of the whole-token rule included, are pinned by the six spec mutants above. All six are killed by its self-test. `bus.sh`'s added call is pinned by the bus.sh self-test arm named under Mutation proof.

## Approval

Policy: merges only on tvofi's approving review (`CLAUDE.md`, "Where the policy is").
