Fix review: blocked e0238c1fe8bc36541e3ecb9fea4c1e59e71e5245 mutation-vacuous: string_compared's last-opener loop survives the self-test and the first-opener mutant passes a raw wc string compare after a leading test

bus-nonce: 21ac79dbd1a1089482c73cbae60d7c0d
pending-ci: gate

## Block

Round 2. The scope is `delta` over the reviewed head 296a0a30d4. Head reviewed: `e0238c1fe8bc36541e3ecb9fea4c1e59e71e5245`, the head the PR body names. The delta `git diff 296a0a30d4 e0238c1fe8` touches only `tools/audit/seat/shell_hazard.py`, an instrument, so nothing widens the scope.

Round 1's finding is resolved. `NUMERIC` and the line-wide `STRING_CMP` are gone, and the three repair rows the verdict asked for are in the self-test and pass. A re-added line-wide NUMERIC exemption is killed (the body's figure). The 288-line corpus misjudges 0 at this head and 48 through 296a0a30d4's `hazards()`, which reproduces the body (`ev/null_control_48.txt`).

The delta adds one predicate the body does not list among its mutants, and it survives. In `string_compared()`:

```
opener = None
for opener in TEST_OPEN.finditer(pre):
    pass
```

This loop picks the **last** `[`/`[[` opener before the substitution. If you replace it with `opener = TEST_OPEN.search(pre)` (the first opener), `--self-test` still prints `ok` with rc 0 (`ev/mutants.txt`, `ev/mutants2.txt`). The mutant is not equivalent. Under it, `[ "$a" = b ] && [ "$(wc -l <f)" = 3 ]` passes, because the first opener's `]` sits between it and the substitution. At the head that line is refused, and 296a0a30d4 refused it too (`ev/mutants2.txt` probe line, `ev/null_control_48.txt`). The corpus adds tails only after the compare, never a test before it, so no row pins the last-opener choice. The body's statement "Its replacement's predicates are each killed above" does not hold for this one.

Repair owed (fixer.md steps 2-8 re-run after it): add a self-test row with a leading test on the line, for example `[ "$a" = b ] && [ "$(wc -l <f)" = 3 ]` refused. Or add a leading-test head to the corpus (e.g. `[ -n "$x" ] && `), so that the first-opener mutant fails.

## Findings

- Follow-up (not a block, outside the delta): the `break` after `out.append((n, "wc-compare", ...))` in `hazards()` is unpinned. Deleting it leaves `--self-test` at ok, because no row has two raw wc compares on one line. Without the break, such a line yields duplicate `wc-compare` entries. That changes only the count of report lines, never the verdict on a line. Carry: dismissed: duplicate report lines on one already-refused line change no refusal; the next repair may add a two-substitution row at no cost

## Evidence

- Self-test at head: `shell_hazard self-test: ok` rc 0 (`ev/selftest.txt`).
- Targeted mutants on the delta (`ev/mutants.txt`, `ev/mutants2.txt`): one replacement on the file, then `--self-test`, then restore. The file was confirmed clean afterwards with `git status`. KILLED: STR_SUBJECT arm deleted, limited to `st`, limited to `case`; closed-bracket check dropped; opener-None check dropped; STR_OP_AFTER removed; STR_OP_BEFORE removed; `!=` dropped from each side; `==` dropped from STR_OP_AFTER; TEST_OPEN without `[[`; NORMALISE exemption removed; RAW exemption removed; `string_compared` always True. SURVIVED: first opener instead of last (the block); `break` removed (Findings). My fail-row counts use my own counter, which matches any line containing `FAIL` (the summary included). I did not reconcile them with the body's per-mutant counts.
- Probes at head (`ev/probe_at_head.txt`): refused `[ "$a" = b ] && [ "$(wc -l <f)" = 3 ]`, `if [ "$(wc -l < f)" = "3" ]; then`, `st $(wc -l <f) 0 m`. Passed: `[ "$(wc -l <f)" -eq 3 -a "$x" = y ]`, `[[ "$(wc -l <f)" -eq 3 && $x == y ]]`. `test "$(wc -l <f)" = 3` still passes; the body dispositions it under Unpinned sites as outside the stated rule.
- Corpus figure: the 288 lines and 0 misjudged at head, and the 48 misjudged at 296a0a30d4, are both re-derived (`ev/null_control_48.txt`).
- Merge with main: `git merge-tree --write-tree origin/main e0238c1fe8` rc 0, `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge_tree.txt`); no conflict.
- Head parents: 296a0a30d4 and 8d2eb5c41a. The delta is the one commit 8d2eb5c41a, as the body states.
- Role contract current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- CI at this head: `merge_train.py classify e0238c1fe8 --pr 3639` printed `WAIT e0238c1fe8bc36541e3ecb9fea4c1e59e71e5245 pending: gate red: none` on every run from 19:19 to 19:48 UTC (`ev/classify.log`). I stopped after about 30 minutes, as the brief says. The block rests on code and tests, not on CI. I did not re-run the gate or the mutation table; I cite CI for them.
- Finder's harness: none named (the packet). This is an instrument lane; round 1 reproduced the instance commits, and the delta does not touch them.
