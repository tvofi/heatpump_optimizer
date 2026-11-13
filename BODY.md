Hotfix R10-HOTFIX-TRAIN-CONTEXT-PAGES: the merge train read only the first 100 rollup contexts, so a required context on a later page was never seen and a green approved head was refused as unread. `rollup_walk` follows `endCursor` and merges every page into one payload for `platform_gate`. This repair answers the second mutation-survivor block (at 853c9f47ccb8): it changes self-test code in `tools/audit/seat/merge_train.py` only, and closes the class by a full diff-mutant pass over the whole delta, not the three mutants the verdict names.

## Head

f52985b40053ef00cb8b741d02bcfe6df9f4719f

## Mutation proof

The class's enumerator is `python3 tools/audit/seat/mutant_run.py --diff f44e761c19dc07fff222bbd6a323bdc847ea9f04...HEAD --cmd 'python3 tools/audit/seat/merge_train.py --self-test' --report-only` (git-archive copy, no mutant cap, every added Python line of the delta); every `SURVIVED` line it prints is dispositioned below.

The verdict's three survivors, and every other named mutant of both rounds, re-run through `mutant_run.py --spec` at fa1e82e816, whose `merge_train.py` is byte-identical to this head's (its NULL mutant survives, so the command is live):
- M5, `have["nodes"] = list(ctx["nodes"])` in `rollup_walk`: KILLED by the new row "A5 platform: page 1's contexts stay in the merge", which puts a red required gate run, then another required context, on page 1 beside a green gate rerun on page 2.
- M8, `contexts(first:100)` with no `after:$after` in `ROLLUP_Q`, and M9, `pageInfo{hasNextPage}` with no `endCursor`: KILLED. The train's paged fake now answers the query it is sent, as GitHub does: the page after `after=` only where the query declares `$after` and passes it to `contexts`, an `endCursor` only where the query asks for one. Under either mutant "A5 serial: the train passes each page's endCursor on the next read" no longer reads page 2's red gate.
- M8b (mine), `$after` used and not declared: KILLED by the same row.
- M2 (per-page oid guard off), M4 (cursor not sent), M6 (the no-rollup `except` returns `merged`), M11 (`if merged is None and commit.get("oid") != head`): KILLED. M2 and M11 each turn one check red, "A5 platform: a later page whose oid differs from the first page's is unread"; the previous body's "2 checks" for M2 and "NameError" for M11 were wrong.
- M10, the page cap returning `payload` in place of `merged`: SURVIVED, equivalent. At the cap the last page still carries `hasNextPage` true, so `platform_gate` answers `unread` with the same reason, "more than 100 contexts: not read whole", for either object; no caller reads anything else of it.

The full diff pass at this head prints nine survivors, all equivalent:
- `tools/audit/seat/merge_train.py:7601 CONST_SWAP`, the faked `gh` exit code `1` made `2` in the failed-read fixture: any nonzero exit is the same failed read to the Train, which tests `if code:`.
- `STMT_DEL` at lines 7561, 7568, 7573, 7580, 7602, 7612, 7628 and 7634, each the `check(...)` statement of one row the delta adds: a self-test with one assertion deleted has nothing left to fail on it. The only kill is a pinned check count, which pins nothing about the walk.

The same pass at e7e5ecdfc0, before the last repair commit, printed sixteen. Ten are gone; its other six were the `check(...)` deletions of the rows that existed then:
- `rollup_walk`'s `return payload` under `except` deleted, and its final `return merged` deleted: killed by the new row "A5 platform: an answer carrying no rollup is handed back as it came", which asserts the no-rollup answer is returned by identity from the first page and from a later one, and that the page-cap walk's reason is "not read whole".
- the Train's `if code:` guard off, `raise OSError(...)` deleted, and `[-160:]` made `[-161:]`: killed by the new row "A5 serial: a failed rollup read is unread, its reason gh's own last 160 characters".
- five fixture literals no row read (the filler count, the other head's length twice, the endless listing's page count, the page index in the train's paged fake): removed, the fixtures now state the property (`[nonreq]`, another head derived from `H0`, a listing that answers page 1 forever, `cursor is None`).

No `tests/mutation_ledger/survivor_triage/` record is written: the delta's survivors are self-test lines of a `tools/` instrument, and the dispositions above are the whole of their triage.

## Null control

The unmodified tree's self-test passes whole (`python3 tools/audit/seat/merge_train.py --self-test`, 0 failed), and `mutant_run.py`'s automatic NULL mutant prints `SURVIVED NULL` in both passes. Each new row carries its own null: page 2 alone reads green; the same two pages answered whole read green; the readable rollup merges; the query as shipped reads page 2's red gate. The three rows that send a broken query also assert `sent != ROLLUP_Q`, so a replacement that matched nothing fails the row instead of passing it.

## Figures

- named mutants killed, and the one equivalent survivor (M10): `python3 tools/audit/seat/mutant_run.py --spec <spec.json> --cmd 'python3 tools/audit/seat/merge_train.py --self-test'`, the spec being the nine edits quoted under `## Mutation proof`
- survivors of the delta: `python3 tools/audit/seat/mutant_run.py --diff f44e761c19dc07fff222bbd6a323bdc847ea9f04...HEAD --cmd 'python3 tools/audit/seat/merge_train.py --self-test' --report-only`
- failed-check count under M2 and under M11: `python3 tools/audit/seat/merge_train.py --self-test` in a `git archive` copy carrying the one edit, taken at f509f6d5d4, whose `merge_train.py` is byte-identical to this head's (`git diff --quiet f509f6d5d4 HEAD -- tools/audit/seat/merge_train.py`)
- gate scope (`MODE: SCOPED`, `tests/doc_claims.py` and `tests/entities.py`, both green): `python3 tests/closure.py select --diff f44e761c19dc07fff222bbd6a323bdc847ea9f04 --workdir <dir>`
- structure ratchet passes: `python3 tests/structure.py`

## Red checks

none. `tests / nightly-status` is red on #3516 and is outside the set `python3 tools/audit/seat/merge_train.py owed-reds` prints.

## Forward-carry

none

## Friction

none
