Owner ruling (tvofi, 2026-11-07, waste-study decision cards, card 2, ruled NARROW): a fix reviewer that returns `blocked` with class `mutation-vacuous` or `class-open` lists, in that one verdict, every survivor or open seam it found at that head. It no longer names one per round. The repair fixer then answers the whole list in one repair.

This is **policy**. It changes what a reviewer seat must do (`dev/governance/roles/fix-review.md` steps 1 and 6), so it merges only on tvofi's approving review.

What changes:
- `fix-review.md` step 1: `blocked <sha> mutation-vacuous: <mutants>` names every survivor the reviewer's driver run reports at that head. The driver output goes in the evidence directory, and `push-verdict` reads it there (`survivor_list.py`).
- `fix-review.md` step 6: `blocked <sha> class-open: <seams>` names every seam the review found, not one per round. No hunt past what the review already ran is owed. A listed item whose harness does not move under its own perturbation is void (`judge.md`), so padding the list buys nothing.
- `tools/audit/seat/survivor_list.py` is the mechanical half. `bus.sh push-verdict` runs `survivor_list.py check <verdict> <evidence dir>` and refuses a `mutation-vacuous` verdict that omits a survivor `<file>:<line>` (or a spec name) that the evidence's driver output reports. Both verdict paths go through this: a local seat's push, and `cloud_relay.sh`, which calls push-verdict. It reads the survivor lines of `mutant_run.py` (`--diff`, `--spec`) and `tests/mutation_table.py` (`LIVES`, and `--pin-killed` through its owner `mutation_table.survivor_sites`). It drops a site that the table marks `[triaged equivalent]`. Any other verdict class passes unread.
- `class-open` has no mechanical check. There is no driver output to count a seam against: the enumeration rule a body names is free-form, so the obligation stays in the reviewer contract. The body says so here, as the brief asked.
- The rule text is paid for inside `fix-review.md` by trimming spent prose in steps 2, 4, 8, 9, 11 and 13, with no meaning dropped. The file stays inside its `policy_lint.mjs --budgets` caps (133 of 140 lines, ~2449 of 2451 tokens). No budget was raised.

In-flight edits to `fix-review.md`: R10-PROCESS-SLIM (`handoff/r10-process-slim`), R10-HOTFIX-NONREQUIRED-REDS (`handoff/r10-hotfix-nonrequired-reds`) and R10-DISPATCH-AT-HANDOFF (`handoff/r10-dispatch-at-handoff`, `-p2`). This diff edits steps 1, 2, 4, 6, 8, 9, the GREEN-mutation paragraph of step 11 and step 13. `git merge-tree --write-tree` against each sibling head is in Figures: one sibling, `-p2`, now conflicts in `fix-review.md`.

## Repair

Round 1 repair of the blocked verdict `Fix review: blocked 81741e448f32052efde42f2c0fe2605c8083e19f mutation-vacuous: tools/audit/seat/survivor_list.py:77 left-boundary lookbehind unpinned`. The verdict lists two items, and this repair answers both.

- Survivor `tools/audit/seat/survivor_list.py:77`, the left-boundary lookbehind `(?<![\w./-])` of the whole-token rule in `unlisted`. Fixed in `c7b72252c`. This commit adds the self-test arm `a key is a whole token: tools/setup.py:3 does not list setup.py:3`, which is the reviewer's own example: a verdict that names only `tools/setup.py:3` must leave survivor `setup.py:3` unlisted. The mutant `token_lookbehind_off` survives at `81741e448` and is killed at this head (Mutation proof). No production line changed. Carry: R10-REVIEW-ENUMERATE
- Stale scope figure. The previous body's `--files` scope line was taken before `tests/closures.json` entered the diff. Re-taken under Figures at this head with both commands. Carry: R10-REVIEW-ENUMERATE

The reviewer's `class_anchor` survivor (`^` and the trailing `:` dropped from `CLASS`) was judged equivalent in the verdict and was not blocked on. It is left alone. Carry: dismissed: the verdict judged it equivalent (`re.match` anchors at the start, and no verdict class extends `mutation-vacuous`)

## Head

`32fbd8338c86f6e66730eb5be9bc880edbe9273c`. The chain to it from the reviewed head `81741e448f32052efde42f2c0fe2605c8083e19f` is:
- `c7b72252cef4ddd58b22af131c1a4990be016695`: the repair commit, on top of `81741e448`.
- `ebbc08bfb1d23deea548a6f0c901329d170b4933`: merges `origin/main` `51cd5ec8a42a`. The only resolution was the ledger driver's set merge of `tests/closures.json`.
- `32fbd8338c86`: merges `origin/main` `daf8b349fd30cc60786eeca333a426b693aa4c5f` (#3346). That moved range touches none of this diff's files.

Every figure below was taken at `32fbd8338c86`, with merge base and `origin/main` `daf8b349fd30` (2026-11-08T21:06Z). `tools/pr/prepr.sh` ran clean at this head against that base. A `PREPR_SKIP_CLOSURES=1` run also passed at `ebbc08bfb` against `51cd5ec8a42a`, before main moved.

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
- `node tools/policy/policy_lint.mjs --budgets`: `fix-review.md` 133 lines (cap 140), ~2449 tokens (cap 2451). The rule is `Math.round(bytes / 4)`. This repair does not touch that file.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `125 self-testing, 125 wired, 0 unwired`, `0 index gap(s)`.
- `node tools/policy/agreement.mjs`: `RESULT divergent=0 unregistered=0`. The 6 `REFUSED` lines ask for `--py-json`, which this bare run did not pass.
- Sibling conflicts, `git merge-tree --write-tree HEAD <sibling handoff head>`:
  - `r10-process-slim`: rc 0.
  - `r10-hotfix-nonrequired-reds`: rc 0.
  - `r10-dispatch-at-handoff`: rc 0.
  - `r10-dispatch-at-handoff-p2` (`089f1da01`): rc 1, on `dev/governance/roles/fix-review.md`. Against `origin/main` it gives rc 0, so this diff causes the conflict. The two hunks are adjacent: `-p2` drops `(a script routes on it)` from the preamble's first-line sentence and rewrites step 7. This diff rewrites steps 6 and 8, which sit on either side of step 7. Whichever lands second merges `origin/main` and resolves by keeping both texts. That merge is the orchestrator's under `fixer.md` step 6, not a re-cut.
- The brief's motivating counts come from `python3 -I tools/audit/seat/review_strength.py --by class`. It reads live verdict refs, so it is named here and not quoted (`fixer.md` step 3).

## Red checks

none. CI has not run on this head. The reviewed head `81741e448` classified `GREEN ... red: none` (`merge_train.py classify`, in the verdict). The local reds the previous body named (`tests/entities.py` 4 of 2666, and `bus.sh`'s `ordinary append` check) are gone at this head: entities and bus.sh both pass above.

## Forward-carry

none

## Friction

none

## Unpinned sites

`tools/audit/seat/survivor_list.py`'s predicates, both sides of the whole-token rule included, are pinned by the six spec mutants above. All six are killed by its self-test. `bus.sh`'s added call is pinned by the bus.sh self-test arm named under Mutation proof.

## Approval

Policy: merges only on tvofi's approving review (`CLAUDE.md`, "Where the policy is").
