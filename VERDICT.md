Fix review: blocked ba5d3b2527fb40fe1a15b2fe8dc832f8aeb8406a class-open: blind_classify_readers is not total: a busy with no free name still reads as a read under Call-with-argument, BoolOp, IfExp, Subscript and two argument-less builtins, and a starred or rebound classify call is never counted

bus-nonce: 770f248f6cc3cca248dbba0cbbc972e9

## Block

This is round 4 by the verdict history (round 1 at 940705766041, round 2 at 1aec0e574b42 on probe/rev-3499-0ae1cd85, round 3 at 44e0b74b5508 on probe/rev-3499-b19d3a70); the dispatch counts it the third cloud review. The delta since round 3 is the merge of origin/main and one predicate, `reads()` in `blind_classify_readers` (authored head 9f8def4ae6). Everything round 3 read cured stays cured (Evidence). The one open item is still open, as a class and not as three spellings.

The question asked was whether the classifier is total over its input space. It is not. The body's claim is "only an expression that can carry runtime state is a read ... every other spelling is blind". `reads()` decides by the top node's type and does not look inside it, so an expression with no free name anywhere (nothing in it can carry runtime state) is a read whenever its top node is on the allow-list. `classify` reads `busy` by truthiness alone (merge_train.py:508), so each such falsy expression is the same blind read as `()`.

Measured with my instrument ev/reviewer_totality.py (the reviewer's, not the finder's) at this head, ev/totality_head.txt: of 255 distinct closed busy expressions, each evaluated falsy, the census reads 23 blind and 232 as a read (464 LEAK lines: positional and `busy=`). End to end, planted in review_packet.py and run through `_gate_reader_barrier_self_test` (ev/plants.txt; NULL SURVIVED, and the controls `None` and `frozenset()` KILLED):

The unguarded domain, all of it that I found, by the branch of the predicate that admits it:

1. `ast.Call` that is not an argument-less listed constructor. SURVIVED: `tuple(())`, `busy=bool(0)`, `(lambda: ())()`. Same branch in the enumeration: `list(())`, `set(())`, `frozenset(())`, `dict({})`, `str('')`, `int(0)`, `sorted(())`, `len(())`, `any(())`, `sum(())`, `[].copy()`, `''.join(())`, `{}.keys()`, `dict.fromkeys(())`, `type(())()`.
2. Argument-less builtin constructors absent from `_EMPTY_CTORS`, the body's own stated category. SURVIVED: `bytearray()`. Same: `complex()`. The enumeration derives the list from `builtins` instead of carrying one: every type that constructs falsy with no argument.
3. `ast.BoolOp`. SURVIVED: `None or ()`. Every pair of the eight falsy atoms under `or` and `and` leaks.
4. `ast.IfExp`. SURVIVED: `() if True else ()`.
5. `ast.Subscript`. SURVIVED: `()[0:0]`. Same: `[()][0]`, `{0: ()}[0]`, `''[:]`.
6. A starred positional makes any call a read (`blind()` returns False on any `ast.Starred`). SURVIVED: `classify(*(l, r))`, a two-argument blind call, and `classify(l, r, *())`. The opposite side fails closed already: `**{}` and `**k` are counted.
7. The call is found by the callee's spelling. SURVIVED: `c = merge_train.classify; return c(l, r)` and `getattr(merge_train, 'classify')(l, r)`. Same in the enumeration: import-as, `functools.partial(classify, l, r)()`, `(c := classify)(l, r)`, `classify.__call__(l, r)`.
8. The exemption is a substring. SURVIVED: a production function named `_reviewer_self_test_free_reader` calling `classify(l, r)`; any function or class whose name contains `self_test` is skipped.
9. The module list is four literals. SURVIVED: a new `tools/audit/seat/reviewer_new_reader.py` calling `merge_train.classify(l, r)`. The bugclasses record says "a structural self-test refuses another" blind read; it refuses one only inside those four files.

Why this keeps recurring: each round widened a list (deny-list, then a list of top node types), and the pins restate the list. Three allow-list entries are pinned by nothing and used by nothing: dropping `ast.Subscript`, `ast.IfExp` or `ast.BoolOp` from `reads()` SURVIVES the barrier self-test, and so does dropping `bytes`, `bool`, `int` or `float` from `_EMPTY_CTORS` (ev/plants.txt, seven survivors; the body's proof names the other six constructors only). The census of real call sites (ev/busy_sites.txt) shows what the allow-list has to admit: the only non-absent busy arguments outside self-tests are the bare Name `busy`, twice (merge_train.py:2151, 2204).

A rule that closes items 1 to 5 as one predicate, measured in the same instrument: a busy is a read only if its subtree holds a free name (a Name or Attribute that is not a builtin used as a callee, nor bound inside the expression by a comprehension, lambda or walrus). On the 255 closed expressions it reads 0 as a read; on the body's seven runtime reads plus `self._gate_busy(h, runs)`, `busy or ()` and `b if c else ()` it calls 0 blind (ev/totality_head.txt, last RESULT line). The narrower rule the call sites support is also total: a read is a bare Name or Attribute, everything else is blind and must be registered. Items 6 to 9 close by failing closed the same way: a starred positional with no `busy=` keyword counts; any Name or Attribute `classify` that is not the callee of a Call counts (that covers rebinding, partial, walrus and `__call__`); the exemption keys on the registered self-test functions, not a substring; the modules are derived (every `tools/audit/seat/*.py` that imports merge_train) or the body states why four is the population.

What no syntactic census decides, and so what the body may disposition rather than fix: a Name bound elsewhere to an empty constant (`EMPTY = ()` then `classify(l, r, EMPTY)`) and a callee reached through a string (`getattr(mt, 'classify')`, half of item 7). The contract accepts a seam "dispositioned in the body"; today the body dispositions none and claims the opposite. Closure for the next round is: items 1 to 6, 8, 9 and the rebinding half of 7 refused by the predicate, with the enumeration (not a spelling list) as the pin, and the data-flow remainder named in the body as the barrier's stated limit. Carry: dismissed: this block, repaired in this pull request before merge

## Findings

none

## Evidence

- Head measured: ba5d3b2527fb40fe1a15b2fe8dc832f8aeb8406a (ev/HEAD.txt), still `refs/pull/3499/head` at 18:06Z and the SHA the body's `## Head` names. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main ba5d3b2527fb40fe1a15b2fe8dc832f8aeb8406a` exits 0 against origin/main 43e95474559c (ev/merge_tree.txt).
- CI at this head: `merge_train.py classify ba5d3b2527fb40fe1a15b2fe8dc832f8aeb8406a --pr 3499` read WAIT (rc 3, `pending: gate red: none`) at the start of this session, as the packet's required-wait advisory records, and `GREEN ... pending: none red: none` (rc 0) at 18:06:13Z (ev/classify_polls.txt). No owed red at this head; `tests / nightly-status` is not in `owed-reds` (ev/owed_reds.txt). The block is on the tree, not on CI.
- Self-tests at the head, unmutated: merge_train 676 checks, 0 failed; orchestrator_tick 317, 0 failed; merge_pr 26, 0 failed (ev/mt_selftest.txt, ev/ot_selftest.txt, ev/mp_selftest.txt). They match the body.
- Finder's harness `dev/audit/harnesses/r10_gate_defer_barrier.py`: head rc 0, no DEFECT, `policy_wait=True`, `policy_B_wait=False policy_C_wait=False policy_C_names_fast=True policy_A_wait=True`, `under_started=[] under_queued_null=['TIMEOUT']` (ev/harness_head.txt). Merge base 8c10361eb1fe: rc 1, `DEFECT policy`, `DEFECT under`, null arms holding (ev/harness_base.txt). Both ends match the body's Figures.
- The body's predicate mutants I re-ran: `frozenset` dropped from `_EMPTY_CTORS` KILLED; `reads()` True for any dict literal KILLED (ev/plants.txt). Not re-run: OLD_DENYLIST and the tuple/list/set-literal mutant.
- The body's enumeration (20 spellings, 13 blind and 7 reads) does not contradict mine: each of its 7 reads holds a free name. It enumerates empty-container literals and argument-less constructors, which is the list the predicate was written from.
- Untouched: VERSION, RELEASE_NOTES.md, the manifest, both claim files and every `*_budgets.json` are absent from the three-dot diff (ev/untouched.txt is empty).
- Not re-derived: the round-2 and round-3 mutants on `wait_ci`, `policy_refusal`, `_classify_reading` and merge_pr.sh (round 3 read each KILLED at 44e0b74b5508; that code is unchanged in the delta, and CI's mutation lane is green at this head), the body's 89-mutant diff census, and the live instances (#3479, #3454, #3442, #3465).
- Instruments: ev/reviewer_totality.py and ev/reviewer_barrier_driver.py are the reviewer's. The driver runs `_gate_reader_barrier_self_test` alone (5 checks), as the body's own proof does, not the full 676.
