R10-GATE-DEFER-BARRIER, part 1 of 2 (carries 0-4): every reader of the required `gate` conclusion treats an at-once deferral red as provisional. Carries 5-9 are part 2 and are not answered here, and so is Carry 10 (`tools/audit/seat/tick_loop.sh --self-test` moves the HEAD of the checkout it runs in), appended to the roster entry on `handoff/audit-r10-roster` while this re-cut ran: `tick_loop.sh` is not among this group's files and the orchestrator's ruling scopes this pass to the classifier. This seat ran no `tick_loop.sh` self-test, so no figure below was taken on a moved HEAD (`git rev-parse HEAD` in the worktree equals `## Head` after every step).

Alternatives that lost: a new re-dispatch job (the sweep is one); copying gate.py's `busy` into each reader (`classify_at` is the one reading); a spelling list of forbidden comparisons (the census below is keyed on the call and accepts only a closed grammar of readers, so a new spelling of a blind read is counted). `policy_refusal` reads same-named contexts together (the predecessor's commit 1eb3bd2c4, kept) rather than collapsing by name. A second, broader reading of "deferral" in `policy_refusal` (any unfinished workflow run at the head) lost to the one reading: `_gate_busy`, gate.py's `busy` over the ci.yml runs, which `classify_at` uses.

What changed, by carry number (item N.M is carry N, part M; Carry 0, Carry 1, Carry 2, Carry 3 and Carry 4 land here; the brief's Carry 5, Carry 6, Carry 7 and Carry 8 are part 2, and so is Carry 9, the `_post_agent_approval` wording under a bare `--mandate` id, which the roster gained at c2d0d268096e99b64af99082cc66bb696c91eb64 while this round ran and which this round does not touch):
Item 4.2 -- `policy_refusal`: a failing `gate` beside a passing one, or while `_gate_busy` names a ci.yml run (not any unfinished workflow), is the gate's own deferral: it is dropped from the red set and counted pending, and every other required context is still read after it, so a red beside a deferral gate is named and does not wait (round 2 items 4 and 7, cases B, B', C). The old `gate_deferred` wrapper had one caller and is deleted; under `reviewDecision` APPROVED the remaining case is worded as an approval of the last push at the moved head (never "a review").
Item 4.1 -- `wait_ci`: when the deferral is read and a sibling ci.yml run at the head is in_progress and inside `CODE_RUN_DEADLINE_SECONDS` (one named constant, the longest job ceiling in ci.yml) of its `run_started_at`, the wait is bounded by that deadline, not by `polls`; a queued run, one past the deadline, or one with no readable start keeps the polls bound (TIMEOUT). The existing "never finishes ends in TIMEOUT within polls" check is kept.
Items 2 and 3, readers: `orchestrator_tick.py` `one_pr` and `main` read through `_classify_reading` (`Train.classify_at`; its fallback is the raw `classify`, so an unread classify stays red), and the gate-race line no longer cites the deleted `GATE_WAIT_MAX_S` wait; `merge_pr.sh` waits out a `classify` WAIT up to `HPO_MERGE_CLASSIFY_POLLS` polls and, when classify still answers WAIT after the last, prints `WAIT-EXHAUSTED` and exits 3 (the train's WAIT), never `RED` (round 2 item 2; pinned by a merge_pr self-test with a classify stub that never leaves WAIT); `review_packet.py` `gate_digest`, `proof_watch.py` and `bus.sh` already read through `classify` (`required_reading`, `classify_at`, `merge_train.py classify`) and are unchanged. A structural self-test (`_gate_reader_barrier_self_test`, registry `BLIND_CLASSIFY_READERS`) fails on another `classify` call in a reader module that has no `busy` candidate, or any candidate outside `busy_reads`'s closed grammar (round 2 item 3; the `## Re-cut` section's subject), and on `merge_pr.sh` losing its wait.
Item 3, record: class `N-provisional-gate-red-read-final` in `bugclasses.json` as barriered, citing `dev/audit/rca/r10-gate-defer-read-final.md`, with the id in `finding.schema.json` and its generated copy (`fold_ledger.py sync`). `dev/governance/roles/nudge.md` step 15 reads a gate failure through `classify` (policy: needs the owner's approving review before merge); the sentence was tightened elsewhere in the step to stay under the `files_tokens` cap, no cap raised.
Item 1: `dev/audit/harnesses/r10_gate_defer_barrier.py`, the committed finder harness for the policy and under-run arms; its `under` stub now answers the paged JSON-lines read that `gate_deferred_runs` uses, and it gains the real-red arms `policy-real-red` and `policy-hidden-red` (round 2 item 6).
Item 0: `dev/audit/rca/r10-gate-busy-defer-2.md` section 1's "waits one poll, then passes" is marked superseded; section 5.2's fresh dispatch stays needed (below).

## Re-cut

Re-cut by orchestrator ruling after the fifth blocked review (class-open on the gate-deferral classifier). Round history is deleted; every figure below was taken in this pass at the head `## Head` names. The re-cut is on the resume head a6076a0f0c4c254efe94f30c4cb5bf22797daa16; its delta is `tools/audit/seat/merge_train.py` and `dev/audit/harnesses/r10_gate_defer_barrier_mutants.py` (89 insertions, 241 deletions by `git diff --stat a6076a0f HEAD`), with no merge of origin/main (`git merge-tree --write-tree origin/main HEAD`: no conflict).

What was dropped, and why: the per-node-class table `BUSY_ARMS`, its enumerator `unclassified_expr_nodes`, the fold table `_static_truth`, the BLIND verdict, the literal-splat flattening in `_busy_candidates`, the 140-row `BUSY_CORPUS` and the in-block arm-mutant loop. Each block found the next spelling the folds missed one node away (a constant comprehension filter, `(not 1) and b`, `f''` as a test); a decision procedure over Python's expression grammar has an open seam wherever a fold is incomplete, so the ruling replaces it with a grammar that is closed by construction.

- Steering and values: `busy_reads(n) -> bool` is true only for a Name that is not a builtin, an Attribute chain rooted at one, or a Call whose func is either (`b`, `self.b`, `h(r)`, `self._gate_busy(h, runs)`). Everything else is refused: literals, displays, every operator, `and`/`or`/`if`/`not`, comprehensions (filters included), subscripts, f-strings, builtin calls, walrus, lambda, and any node class a later interpreter adds. No expression is folded, so no fold can be incomplete.
- Binding: every candidate must read. `_busy_candidates` returns each positional from the third on, each `*` splat's operand wherever it stands, and the value of each `busy=` keyword and `**` splat, reading no splat through; `blind_classify_readers` counts a call with no candidate or with any refused candidate. `classify(l, r, None, **kw)` and its nine siblings in the verdict are counted; `classify(l, r, b, **kw)`, `classify(l, r, busy=b, **kw)`, `classify(*a)`, `classify(l, r, **kw)` and `classify(l, r, *rest, **kw)` still pass.
- What the closed grammar now refuses that a6076a0f read, by design: a literal splat read through (`classify(*(l, r, b))`, `classify(l, r, **{'busy': b})`, `classify(l, r, *(b,))`), a builtin call over a reader (`frozenset(r)`), and a reader spelled as a comprehension, operator or subscript (`{r.id for r in runs}`, `a | b`, `x[0]`). Such a reader is rewritten into the grammar or registered.
- Registry: the tree needs nothing beyond the grammar. Its two busy-passing calls, `classify(last, required, busy)` in `Train.classify_at` and `classify(last, only, busy)` in `Train.wait_ci`, pass a Name; `BLIND_CLASSIFY_READERS` is unchanged (five entries, all no-busy reads), and the barrier check comparing it with `blind_classify_readers` over the four reader modules passes.
- Known limit: a Name or call in the grammar that evaluates to an empty value (`NO_BUSY` bound to `()`, a function returning one) reads; deciding it needs name resolution or evaluation. Carry: dismissed: undecidable for a per-call syntactic predicate; the alias form was dismissed on that ground in the round-4 verdict and named outside the class by the round-5 verdict
- Alternative that lost: the verdict's decision procedure (each steer's own verdict, fold where `_static_truth` answers, REFUSED where it cannot) keeps a fold table and its recursion; the ruling chose the closed grammar, which is smaller and refuses more.

## Head

3785b0d097bc22410f42eae7ba3129c5fece1c61, one commit on a6076a0f0c4c254efe94f30c4cb5bf22797daa16. Measured against origin/main 4145f2852642fd0b5ccb8b7af60d41e896a5eea3, 2026-11-12T20:10:15Z. No CI run exists at this head before the pull request moves to it, and none is claimed.

## Mutation proof

- `python3 -I dev/audit/harnesses/r10_gate_defer_barrier_mutants.py`: 13 source mutants of `busy_reads`, `_busy_candidates` and `blind_classify_readers` (Call not unwrapped, Attribute chain not walked, builtin Name reads, the open fold-shaped grammar, Subscript walked as Attribute, `all` to `any` (the a6076a0f regression), no-candidate passes, `*` splat dropped, only the third positional, `**` dropped, `busy=` dropped, Starred read as its node, self-test functions counted), each compiled in memory with `_gate_reader_barrier_self_test` run: `RESULT mutants=13 survived=0 stale=0 baseline_failed=0`, exit 0. Null: `--tree` at an export of a6076a0f (`git archive a6076a0f tools/audit/seat`) prints `RESULT mutants=13 survived=0 stale=12 baseline_failed=0`: twelve fragments do not exist there, so the harness cannot pass against the removed classifier.
- Diff-mutant pass: `tools/pr/prepr.sh` at this head, `MUTANT_IN_PLACE=1`, `MUTANT_CMD="env PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test"`: rc 0. Its draw is the first 40 mutants of the branch's added lines in file order (`mutant_run.py --diff <merge-base>...HEAD --max-mutants 40`), which end before this round's lines (those are the harness's, above). Full output of that step, each line showing the mutated text:

```
SURVIVED tools/audit/seat/merge_train.py:2184 CONST_SWAP  while k < self.polls or (last_def and not deferring and k <= last_def + 3) or self._sibling_in_deadline(deferring):
SURVIVED tools/audit/seat/merge_train.py:2209 CONST_SWAP  sib = [r[1] for r in rows]
SURVIVED tools/audit/seat/merge_train.py:5918 CALL_DEL  pass
SURVIVED tools/audit/seat/merge_train.py:6715 CONST_SWAP  t = Train("o/r", Path(d), None, "", (), 2, run=run, sleep=lambda s: None, log=lambda s: None, polls=polls,
SURVIVED tools/audit/seat/merge_train.py:6728 CONST_SWAP  started = lambda st, ago: _jl([{"id": 42237558474, "status": st, "run_started_at": iso(ago)}])
SURVIVED tools/audit/seat/merge_train.py:6730 CONST_SWAP  [started("in_progress", 5001)] * 7 + [done], polls=3)
SURVIVED tools/audit/seat/merge_train.py:6733 CONST_SWAP  red, _ = wait([[edit_gate]], [started("queued", 5001)], polls=3)
SURVIVED tools/audit/seat/merge_train.py:6734 CALL_DEL  pass
SURVIVED tools/audit/seat/merge_train.py:6735 CONST_SWAP  red, sb = wait([[edit_gate]], [started("in_progress", CODE_RUN_DEADLINE_SECONDS + 61)], polls=3)
SURVIVED tools/audit/seat/merge_train.py:6742 CONST_SWAP  tb = Train("o/r", Path(d), None, "", (), 2, run=lambda *a, **k: (0, ""), sleep=lambda s: None,
SURVIVED tools/audit/seat/merge_train.py:6743 CONST_SWAP  log=lambda s: None, polls=4, wall=lambda: NOW)
SURVIVED tools/audit/seat/merge_train.py:6744 CONST_SWAP  edge = lambda st, ago: tb._sibling_in_deadline([(2, st, iso(ago))])  # noqa: E731
SURVIVED tools/audit/seat/merge_train.py:6747 CONST_SWAP  edge("in_progress", 1) is True and edge("in_progress", CODE_RUN_DEADLINE_SECONDS) is True
SURVIVED tools/audit/seat/merge_train.py:6748 CONST_SWAP  and edge("in_progress", CODE_RUN_DEADLINE_SECONDS + 2) is False and edge("queued", 5) is False
SURVIVED tools/audit/seat/merge_train.py:6749 CONST_SWAP  and tb._sibling_in_deadline([(2, "in_progress", "")]) is False)
SURVIVED tools/audit/seat/merge_train.py:6750 CONST_SWAP  tick = iter(range(11 ** 6))
SURVIVED tools/audit/seat/merge_train.py:6751 CONST_SWAP  red, sb = wait([[edit_gate]], [started("in_progress", 5001)], polls=3, wall=lambda: NOW + 600 * next(tick))
WARN     diff mutants           17 survivor(s) on the diff's added lines -- each owes a killing check or a line under ## Unpinned sites (fixer.md step 2)
```

Disposition: every survivor is on a line unchanged since 9f8def4ae679513923e1031954dd93a90fe9b685 (`git diff a6076a0f HEAD` touches none of them): the `last_def + 2` settle count and `sib = [r[0] for r in rows]` (read as truthiness and in a log line) in `Train.wait_ci`, the deleted `_gate_reader_barrier_self_test(check)` call and the deleted QUEUED-sibling `check(...)` call inside self-test code, and 13 constant swaps in `_gate_race_self_test`'s fixtures (stub ids, ages, poll counts). None is a production predicate of this round. The kernel killed one process for memory while the draw ran; a kill can only turn a survivor into a false kill, so this list is a floor. Carry: dismissed: self-test fixture constants and equivalent mutants on lines the round-4 review already read

## Null control

- Plants: the verdict's ten binding spellings, and its eighteen steering spellings each as third positional and as `busy=` (36 calls), driven through `blind_classify_readers` at an export of a6076a0f and at this head, with the verdict's five reading binding forms as the control. a6076a0f: `binding_uncounted=10/10 steering_uncounted=36/36 reading_counted=0/5`; this head: `binding_uncounted=0/10 steering_uncounted=0/36 reading_counted=0/5`. Driver: a scratch probe loading each tree's `merge_train.py`, the reviewer's lists inline; the binding rows are also in the self-test's "P436 barrier binding" check.
- `python3 -I dev/audit/harnesses/r10_gate_defer_barrier.py` at this head: exit 0, `policy_null_ok=True`, `under_queued_null=['TIMEOUT']`, `policy_A_wait=True`, `policy_B_wait=False`, `policy_C_wait=False`. Its baseline end was not re-taken: no production line of its arms is in this pass's delta.

## Figures

- `python3 -I dev/audit/harnesses/r10_gate_defer_barrier_mutants.py --corpus-under "$D"`, `$D` the a6076a0f export: `RESULT corpus other calls=108 wrong=64 not_reading_passed=64 reading_counted_blind=0` and `RESULT corpus tree calls=108 wrong=0 not_reading_passed=0 reading_counted_blind=0`. Rule: each `BUSY_CORPUS` expression as third positional, as `busy=`, and as `busy=` beside `**kw`; wrong is a call whose counted-or-not disagrees with its recorded reads flag.
- Corpus size is `len(BUSY_CORPUS)`, printed in the self-test's "P436 closed grammar" check name; the call count is in the "P436 barrier over the corpus" check name (six binding forms per expression, three of them beside a reading splat).
- `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test`: 680 checks, 0 failed. `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 317 checks, 0 failed. `bash tools/audit/seat/merge_pr.sh --self-test`: 26 checks, 0 failed.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run`, naming `tests/doc_claims.py` (ALL 343 checks PASSED) and `tests/entities.py` (ALL 2709 ENTITY CHECKS PASSED, run with `env -u BASH_ENV`); of `run_always`, `tests/env_drift.py --claims-only origin/main` (claims hygiene ok), `tests/closure.py selftest` (ALL 118 closure shrink pins PASSED), `tests/layout.py` (ok) and `tests/harness_headers.py` (ALL 115 HARNESS HEADER CHECKS PASSED) were run. `tests/stress.py` and the rest are CI's.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched. `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0081 IMPROVES`, over the whole branch.
- Enumerator for the class's seams: the binding seam is `_busy_candidates` over every argument shape an `ast.Call` carries (positional, Starred, keyword, `**`), closed in this diff by "every candidate must read"; the value and steering seams are `busy_reads`, closed in this diff by a three-shape allow-list refusing every other `ast.expr` (the "P436 closed grammar null" check drives a node class this interpreter lacks at the root, as an attribute base and as a call func); the name-resolution seam is the limit above.

## Red checks

None owed at this head: no CI run exists here before the pull request moves to it.

## Forward-carry

- Section 5.2 of `dev/audit/rca/r10-gate-busy-defer-2.md` (a fresh dispatch where a re-run would replay a stale pinned program) stays needed under the at-once program; re-measure with that document's `census` arm after #3473 lands. Carry: dismissed: the seam is #3473 (R10-HOTFIX-GATE-REDISPATCH-LOOP), whose roster row is carries-open and not receivable; the relay folds this re-measure instruction when #3473 lands
- The fixer step 8 extension to a writer change (enumerate the readers of a conclusion whose meaning changes), proposed in `dev/audit/rca/r10-gate-defer-read-final.md` section 6, is policy and is not edited here. Carry: dismissed: owner-only policy, already recorded in that document's section 7

## Friction

none

## Approval

Policy file changed: `dev/governance/roles/nudge.md` step 15 (the only nudge.md in the tree; there is no generated copy). Not approved yet: this seat holds no approval and asserts none. Merge waits on `@tvofi`'s approving review of the head, per `CLAUDE.md`.
