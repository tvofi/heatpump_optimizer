Fix review: blocked 9f8def4ae679513923e1031954dd93a90fe9b685 class-open: blind_classify_readers still reads a builtin constructor holding only an empty literal (frozenset(()), set([]), dict({}), tuple([]), list(()), frozenset(set())) and an IfExp or BoolOp of blind operands (None or (), () if c else None) as a read

bus-nonce: c03cc45661d3a0de9bb1680d2ac4eae8

## Block

Round 4 of this topic (a later round over 44e0b74b55080d829f199410c2e4861850cd7d99, scope: the delta, plus round 3's one class-open finding). The repair swaps the deny-list for an allow-list, `reads(b)`, but the allow-list is not recursive where it has to be, so the same class (a `busy` that reads nothing, which the barrier must call blind) stays open one level of nesting down:

- `ast.Call` on a name in `_EMPTY_CTORS` counts as a read whenever it has any argument. It ignores whether that argument reads anything. So `frozenset(())`, `set([])`, `dict({})`, `dict(())`, `tuple([])`, `list(())`, `frozenset([])` and `frozenset(set())` all count as reads, both positional and as `busy=`. The body's own example, "a builtin constructor with an argument (`frozenset(r)`) is a read", is true only because `r` reads. The predicate should be: a ctor call reads iff any of its args or keyword values reads.
- `ast.IfExp` and `ast.BoolOp` are reads unconditionally. So `None or ()`, `() and x` and `() if c else None` count as reads. They should read iff an operand that can be the value reads (IfExp: body or orelse; BoolOp: any value).

I measured this two ways. First, my enumeration of 34 blind spellings, each positional and `busy=` (ev/enum_reviewer.txt): the 13 the body names and 8 more are blind; the 26 forms above (13 spellings × 2) read. Second, plants at the head: `def _planted_reader(l, r): return classify(l, r, <spelling>)` was appended to tools/audit/seat/review_packet.py, a registered reader module, and `merge_train.py --self-test` was run with the plant in place. With `frozenset(())`, `busy=set([])` or `None or ()` it prints 676 checks, 0 failed. With the control `frozenset()` it prints 676 checks, 1 failed (ev/plants.txt). So the barrier lets through a planted blind reader whose spelling is one nesting away from the case round 3 named.

The predicate's other side is unsound too (no false negative, but it changes the same function): a comprehension (`{r.id for r in runs}`, `[r for r in runs]`) and a BinOp (`a | b`) read runtime state, yet `reads` returns False for them, so a legitimate reader spelled that way would be refused as blind (ev/enum_reviewer.txt, SHOULD-READ group). The repair should cover both directions with one structural recursion over the expression. The enumeration should then be re-run from both sides, and pinned in the self-test with the nested forms, not only the flat ones.

## Findings

- Out of scope: a `busy` passed through an alias of an empty constant (`NO_BUSY = frozenset()`; `classify(l, r, NO_BUSY)`), or through a method or attribute call on one (`dict.fromkeys([])`, `frozenset().union()`, `type(None)()`), reads as a read (ev/enum_reviewer.txt). A per-call syntactic predicate cannot decide these without name or type resolution. Carry: dismissed: beyond a per-call syntactic predicate; the barrier's registry comparison over the four reader modules shows no current reader using one, and a repair that resolves module-level constant aliases would close the first form if the designer wants it

## Evidence

- Head reviewed: 9f8def4ae679513923e1031954dd93a90fe9b685 (ev/HEAD.txt). It matches the head named in the body's `## Head`. The handoff body is at refs/heads/handoff-body/r10-gate-defer-barrier; no pull request exists yet.
- No review packet and no CI exist for this head before the PR opens, so no live required check was read and no `## Red checks` answer was judged at this head. `merge_train.py owed-reds` was run (tail in transcript only).
- The delta 44e0b74b..9f8def4a is one merge of origin/main (23c9af9b1e) plus 9f8def4ae6, which touches only tools/audit/seat/merge_train.py. The merge resolution is a clean merge: `git merge-tree --write-tree` of its parents gives tree 1d26fc4b1d, identical to the commit's tree (ev/merge-resolution.txt). No custom_components/ delta, so the scope is not widened.
- `git merge-tree --write-tree origin/main 9f8def4a`: rc=0, no conflict (ev/merge-tree.txt).
- `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test` at the head: 676 checks, 0 failed (ev/merge_train_selftest.txt). This matches the body's figure.
- Finder harness `python3 -I dev/audit/harnesses/r10_gate_defer_barrier.py` at the head: rc 0, `policy_null_ok=True`, `under_queued_null=['TIMEOUT']`, `policy_A_wait=True`, `policy_B_wait=False`, `policy_C_wait=False` (ev/harness_head.txt). This matches the body. I did not re-take the baseline end, the body's mutant_run figures, or orchestrator_tick / merge_pr.sh, because the block does not turn on them.
- The body's own enumeration, re-run, reproduces its stated split for its 20 spellings. The split is correct for those; the class-open is in spellings it did not enumerate.

## Friction

none
