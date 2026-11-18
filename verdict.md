Fix review: blocked af0616cbe8dbd95e9a0ccb1e8822949f579a7cba mutation-vacuous: five non-equivalent swaps on lines this repair added to loop_ledger.py survive its self-test: the summary column's product and machinery counts, its unread count, and the column's event test

bus-nonce: 1ffe4e576682e7e1f4e90f29000724e2

Round 2, scope `delta` over the reviewed head 3fe03e1480a1149d529b46373a7ba275ac47681b. Reviewed from a detached worktree at af0616cbe8dbd95e9a0ccb1e8822949f579a7cba. The delta's two first-parent commits are merges. The branch's own authored change is caa40bb294, ebc8bca74b and ad36eefec0, which touch only `tools/audit/seat/loop_ledger.py` and `instruments/loop_ledger.py.md`. The rest arrives from origin/main (c8976e5397 and 8e76c192d2). No production (`custom_components/`) code is authored in the delta, so the scope is not widened. The mutant driver is the reviewer's own (`ev/mut.py`). No finder harness is named.

## Block

1. **Five swaps on lines the repair added survive** `python3 -I tools/audit/seat/loop_ledger.py --self-test --no-mutants`: each ends `0 failed`, while the unmutated control also ends `0 failed` and 8 other reviewer swaps on the same new code are killed (`ev/reviewer_mutants.txt`, `ev/reviewer_mutants_2.txt`). The body's `## Unpinned sites` says the enumerator's survivors on the read's lines are five, all equivalent. None of these five is on that list, and none is equivalent:
   - `red_lines` summary, `sum(a == _gate().RED for a, _ in pairs)` changed to `sum(b == _gate().RED for _, b in pairs)` (the product count reads the machinery verdict): survives. The only push fixture with a summary check (`both`, run 60) is symmetric: product red 1 and machinery red 1. A push red whose product is red and machinery green prints `product red 1` at the head and `product red 0` under the swap.
   - Same line, `a == _gate().RED` changed to `a != _gate().GREEN`: survives. An `unread` product is then counted as red. Runs 61/62 hold exactly that input (`product unread`), but only their row text is checked, never the summary.
   - The machinery twin, `b == _gate().RED` changed to `b != _gate().GREEN`: survives for the same reason (run 62, `machinery unread`).
   - `on {len(reds) - len(pairs)}` changed to `on {len(rows) - len(pairs)}`: survives. `rows` also holds a blind run's unread row, so a directory with one run that has no listing and one non-push red prints `unread on 1` at the head and `unread on 2` under the swap. No fixture combines a blind run with the column.
   - The column's event test, `if r.get("event") == "push" else None` changed to `if r.get("event") != "pull_request" else None`: survives. `tests.yml`'s own header names `merge_group` and dispatch runs. Under the swap such a run gets a `push`-class verdict, which the body's own departure says must read `unread`. The table's `column class from the event` row (`if True`) is killed only by the `pull_request` fixture. No fixture lists a third event, although the `no push on main` fixture already builds such a run.
   Each needs a fixture that tells it apart and a `MUTANTS` row, as round 1's item 1 required of the read's predicates.

## Previous verdict's block, at this head

- Item 1 (four survivors): resolved. Rows `gate job by name`, `failed jobs failed`, `prelude and gate owed` and `main row's own spell` have fixtures and are killed. The full self-test ends `loop_ledger self-test: 0 failed` with 90 `ok` lines, 30 of them `ok    mutant killed`, and no `FAIL` (`ev/loop_ledger_selftest_full.txt`).
- Item 2 (false column reason): resolved. The column is `gate.status(..., "push")` over the red attempt's own jobs on a push run. On any other run it is `unread` with the reason `NO_CLASS`, which names `status`. `gate.py:308` `status` and `:303` `MACHINERY_JOBS` exist at this head. The two departures are raised in the body.
- Item 3 (spell open at the left edge): resolved. The `EDGE` sentinel returns `unread` on main and head rows until the first green main run. The reviewer's swaps `edge return deleted`, `EDGE falsy` and `edge on head rows only` are each killed by the two edge checks. The instrument page names the limit.

## Evidence

- CI: `merge_train.py classify af0616cbe8dbd95e9a0ccb1e8822949f579a7cba --pr 3696` printed `GREEN af0616cbe8dbd95e9a0ccb1e8822949f579a7cba pending: none red: none` (rc 0) on its first run (`ev/classify_last.txt`). No red is owed a `## Red checks` answer.
- Merge: `git merge-tree --write-tree origin/main af0616cbe8` exits 0. The merge base is 8e76c192d2, which is origin/main's head at review.
- The branch's own diff is unchanged by the main merges except the authored files. Per file, the `+`/`-` lines of `git diff <merge-base> <head>` match between 3fe03e1480 and af0616cbe8 for every branch file except `loop_ledger.py`, its instrument page and `tools/ci/selftest_closures.json`. The last one differs only through main's side (c8976e5397's resolution keeps both sides' entries).
- Reviewer swaps killed (`ev/reviewer_mutants.txt`, `ev/reviewer_mutants_2.txt`): edge return deleted, EDGE made falsy, edge on head rows only, row pair order swapped, status class `pr` in place of `push`, status over every attempt's jobs, every member passed as `in_progress`. The worktree was restored after the swaps (`git status --short` empty).
- `python3 -I tools/audit/seat/loop_ledger.py --repo .` ends `gate_reds unread (no --runs directory)`, as the body says.
- Body figures re-derived at the head (`ev/figures_rederived.txt`): `STRUCTURE RATCHET PASSED`. The `git grep` at 38bf516bdd prints `gate.py:303:MACHINERY_JOBS` and `gate.py:308:def status`. `selftest_scope.py select --change M:tools/ci/gate.py` names `loop-ledger`. `git diff --name-only 3fe03e1480 ad36eefec0` prints the two files the body names. Not re-derived: `ALL 2725 ENTITY CHECKS PASSED`, because `tests/entities.py` was stopped at its 220 s limit before the summary line. The archscore line and the [d-hotfile-enumerator] list were also not re-derived.
