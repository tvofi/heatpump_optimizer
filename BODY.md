R10-GATE-DEFER-BARRIER, part 1 of 2 (carries 0-4): every reader of the required `gate` conclusion treats an at-once deferral red as provisional. Carries 5-8 are part 2 and are not answered here.

Alternatives that lost: a new re-dispatch job (the sweep is one); copying gate.py's `busy` into each reader (`classify_at` is the one reading); a spelling list of forbidden comparisons (the census below is keyed on the call, `classify` without its `busy` argument, so a new spelling of the same blind read is still a call). `policy_refusal` reads same-named contexts together (the predecessor's commit 1eb3bd2c4, kept) rather than collapsing by name. A second, broader reading of "deferral" in `policy_refusal` (any unfinished workflow run at the head) lost to the one reading: `_gate_busy`, gate.py's `busy` over the ci.yml runs, which `classify_at` uses.

What changed, by carry number (item N.M is carry N, part M; Carry 0, Carry 1, Carry 2, Carry 3 and Carry 4 land here; the brief's Carry 5, Carry 6, Carry 7 and Carry 8 are part 2):
Item 4.2 -- `policy_refusal`: a failing `gate` beside a passing one, or while `_gate_busy` names a ci.yml run (not any unfinished workflow), is the gate's own deferral: it is dropped from the red set and counted pending, and every other required context is still read after it, so a red beside a deferral gate is named and does not wait (round 2 items 4 and 7, cases B, B', C). The old `gate_deferred` wrapper had one caller and is deleted; under `reviewDecision` APPROVED the remaining case is worded as an approval of the last push at the moved head (never "a review").
Item 4.1 -- `wait_ci`: when the deferral is read and a sibling ci.yml run at the head is in_progress and inside `CODE_RUN_DEADLINE_SECONDS` (one named constant, the longest job ceiling in ci.yml) of its `run_started_at`, the wait is bounded by that deadline, not by `polls`; a queued run, one past the deadline, or one with no readable start keeps the polls bound (TIMEOUT). The existing "never finishes ends in TIMEOUT within polls" check is kept.
Items 2 and 3, readers: `orchestrator_tick.py` `one_pr` and `main` read through `_classify_reading` (`Train.classify_at`; its fallback is the raw `classify`, so an unread classify stays red), and the gate-race line no longer cites the deleted `GATE_WAIT_MAX_S` wait; `merge_pr.sh` waits out a `classify` WAIT up to `HPO_MERGE_CLASSIFY_POLLS` polls and, when classify still answers WAIT after the last, prints `WAIT-EXHAUSTED` and exits 3 (the train's WAIT), never `RED` (round 2 item 2; pinned by a merge_pr self-test with a classify stub that never leaves WAIT); `review_packet.py` `gate_digest`, `proof_watch.py` and `bus.sh` already read through `classify` (`required_reading`, `classify_at`, `merge_train.py classify`) and are unchanged. A structural self-test (`_gate_reader_barrier_self_test`, registry `BLIND_CLASSIFY_READERS`) fails on another `classify` call in a reader module whose `busy` is absent or reads nothing: any literal or argument-less builtin constructor (None, False, 0, '', (), [], {}, set(), frozenset(), dict(), positional or `busy=`; round 2 item 3, round 3), and on `merge_pr.sh` losing its wait.
Item 3, record: class `N-provisional-gate-red-read-final` in `bugclasses.json` as barriered, citing `dev/audit/rca/r10-gate-defer-read-final.md`, with the id in `finding.schema.json` and its generated copy (`fold_ledger.py sync`). `dev/governance/roles/nudge.md` step 15 reads a gate failure through `classify` (policy: needs the owner's approving review before merge); the sentence was tightened elsewhere in the step to stay under the `files_tokens` cap, no cap raised.
Item 1: `dev/audit/harnesses/r10_gate_defer_barrier.py`, the committed finder harness for the policy and under-run arms; its `under` stub now answers the paged JSON-lines read that `gate_deferred_runs` uses, and it gains the real-red arms `policy-real-red` and `policy-hidden-red` (round 2 item 6).
Item 0: `dev/audit/rca/r10-gate-busy-defer-2.md` section 1's "waits one poll, then passes" is marked superseded; section 5.2's fresh dispatch stays needed (below).

## Re-cut

Round 4. Review 44e0b74b5508 found one class-open item: `blind_classify_readers` decided "reads nothing" with a deny-list (`None`/falsy constant, empty tuple/list/set literal, `tuple()`/`list()`/`set()`), so `busy=frozenset()`, `dict()` and `{}` survived. The minimal change is one predicate: the deny-list is replaced by `reads(b)`, an allow-list in which only an expression that can carry runtime state is a read (a Name, Attribute, Subscript, IfExp, BoolOp, a call that is not an argument-less builtin constructor, or a container literal holding such an element); every other spelling is blind. Nothing else changed since 44e0b74b besides the merge of origin/main. Earlier rounds missed the class because each added the spellings the reviewer had just named (a list, not a predicate) and the self-test pinned that list, so the pins and the predicate agreed with each other and with nothing else. This round enumerates the spellings first, from the other side: every empty-container form a reader can be handed.

Enumeration, re-runnable (prints each spelling, positional and `busy=`, with the registry verdict; a blind spelling reads `{'f': 1}`, a read reads `{}`):

    cd tools/audit/seat && python3 - <<'X'
    import merge_train as m
    for a in ["None","()","[]","{}","set()","frozenset()","dict()","tuple()","list()","str()","''","0","False","b","self.b","x[0]","h(r)","frozenset(r)","[b]","{'a': b}"]:
        for f in ("{}","busy={}"):
            print(f.format(a), m.blind_classify_readers("def f():\n    return classify(l, r, %s)\n" % f.format(a)))
    X

Result: the first 13 spellings (through `False`, both forms) are blind; the last 7 (`b`, `self.b`, `x[0]`, `h(r)`, `frozenset(r)`, `[b]`, `{'a': b}`) read. The self-test arm pins `None`, `()`, `[]`, `{}`, `set()`, `tuple()`, `list()`, `frozenset()`, `dict()`, `str()`, `''`, `0`, `False` and `busy=` `None`, `()`, `[]`, `{}`, `set()`, `frozenset()`, `dict()`; a call returning a container (`h(r)`) is a read by the allow-list, and a builtin constructor with an argument (`frozenset(r)`) is a read.

Mutation proof (`mutant_run.py --spec --in-place`, cmd `_gate_reader_barrier_self_test` driven alone, NULL SURVIVED as required): OLD_DENYLIST (the previous deny-list form restored) KILLED; each of `tuple`, `list`, `set`, `frozenset`, `dict`, `str` dropped from `_EMPTY_CTORS` KILLED; `reads` returning True for any dict literal, and for any tuple/list/set literal, KILLED.

## Head

9f8def4ae679513923e1031954dd93a90fe9b685. Round 4 repair: the predicate change above, on top of the merge of origin/main into 487225c07f (the handoff PR head 44e0b74b55080d829f199410c2e4861850cd7d99 merged it). Previous head: 487225c07f6262053ecf0b8a25e5fbf42a916703, on top of the reviewed head 1aec0e574b424af409b8bed502e3424b336986a4 (repair of both verdicts: round 1 940705766041a8316ba976d33a3b16b7ca281668 and round 2 aa1418625c5245fe8f00906e6a5ee8308b504320). An earlier step push (4b40911278) on the wip ref is superseded by a merge that keeps this tree. Measured against origin/main 5365b18437, 2026-11-12T13:45:19Z. Live instances cited, not re-measured: `gate` red at the heads of #3479, #3454 and #3442 while sibling jobs were queued or running, and four merge attempts on #3465 against a base-policy refusal while its gate check-run sat QUEUED. #3473 (R10-HOTFIX-GATE-REDISPATCH-LOOP) is still open and is not duplicated; once it lands, re-check that the `classify` WAIT window still spans the gate re-run it adds.

## Mutation proof

Each production line deleted, the named self-test run, line restored:
- `wait_ci` deadline extension (`or self._sibling_in_deadline(deferring)`) removed: `_gate_race_self_test` fails "carry 4 (1): a STARTED sibling run inside its deadline is waited on past `polls`" and "a started sibling that never finishes ends at its deadline".
- `policy_refusal` same-name deferral predicate forced false: `_review_settle_self_test` fails both "P590 a rollup holding a success gate and a deferral failure gate" orders.
- `orchestrator_tick._classify_reading` returning raw `classify`: `orchestrator_tick.py --self-test` fails "carry 9 one_pr: WAIT clears the red", "P436 one_pr reads classify_at: WAIT" and the OWED-buckets carry-9 check.
- `merge_pr.sh` wait (`[ "$crc" = 3 ] || break` made `break`): `merge_pr.sh --self-test` fails "a gate red that classify reads WAIT, then GREEN, is waited out and merges".
- Round 2, `mutant_run.py --spec ... --in-place` with `merge_train.py --self-test` (NULL SURVIVED as required): M8 (delete `or self._gate_busy(h, self._check_runs(h))` from the deferral predicate) KILLED by "P436 A"; M9 (the `not (deferral and n == GATE)` filter removed from `red`) KILLED; M6 (`classify(l, r, None)` and `classify(l, r, ())` planted in review_packet.py) and the 2-argument plant KILLED by the barrier check.
- Diff-arm survivors fixed: `CODE_RUN_DEADLINE_SECONDS = 151 * 60` (now pinned to ci.yml's longest `timeout-minutes`), `rollup_red_after_pass` guard-off and `>=` (direct unit checks, incl. an equal stamp and another name's entries), and `_sibling_in_deadline`'s `0 <=` edges (direct edge check). Each killed by its new check, run by the spec arm.

## Null control

The unmodified tree (origin/main's `tools/audit/seat` and `tools/ci`) read by the finder's harness: `policy` arm reads DEFECT (the passing-plus-failing rollup is not a wait) and `under` arm reads DEFECT (TIMEOUT where the code run concluded success). Controls kept in the self-tests: a rollup of the passing gate alone parks as before; REVIEW_REQUIRED keeps the review wording; a queued sibling, and a started one past its deadline, end in TIMEOUT; a red gate with no unfinished run is red at once; `merge_pr.sh` with a RED `classify` still refuses RED and with no red never asks `classify`; a new function calling `classify(latest, req)` is a blind reader the registry does not hold; a lone gate FAILURE with no unfinished ci.yml run is red (A null); a real gate red beside an unrelated unfinished workflow is red (B, B'); another required context's red beside a deferral gate is named (C), and the same red beside a green gate is named (C null).

## Figures

- `python3 -I dev/audit/harnesses/r10_gate_defer_barrier.py` at this head: exit 0, no DEFECT line; `policy_null_ok=True`, `under_queued_null=['TIMEOUT']`.
- `D=$(mktemp -d); git archive origin/main tools/audit/seat tools/ci | tar -x -C "$D"; python3 -I dev/audit/harnesses/r10_gate_defer_barrier.py --tree "$D"`: exit 1, DEFECT policy and DEFECT under (the baseline control); its null arms hold at both ends (`policy_null_ok=True`, `under_queued_null=['TIMEOUT']`).
- The round-2 finder instrument (the reviewer plant script in the evidence directory of probe/rev-3499-0ae1cd85, plus one added stub for the ci.yml runs path, which `policy_refusal` now reads) at this head: A wait=True; NULL, B, B', C, C' wait=False with the red named (C names `tests / fast (3.14)` only). At origin/main's tree: every case wait=False.
- `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test`, `python3 tools/audit/seat/orchestrator_tick.py --self-test`, `bash tools/audit/seat/merge_pr.sh --self-test`: 0 failed each (676, 317 and 26 checks).
- `python3 tools/pr/ci_predict.py --apply-inert` repaired the one predicted closures red (the new harness, a classification in `tests/closures.json`).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED; no budget touched. `env -u BASH_ENV ./tests/derive_closures.sh --single tests/entities.py` run; `tests/closures.json` re-derived in this PR.
- `mutant_run.py --diff $(git merge-base origin/main HEAD)...HEAD --in-place` with cmd `merge_train.py --self-test && orchestrator_tick.py --self-test`, over the whole diff (89 mutants listed): every SURVIVED line other than the fixed ones above is self-test data or an equivalent mutant: `_sibling_in_deadline`'s trailing `return False` (a `None` return is falsy), `sib = [r[1] ...]` (read only as truthiness and in a log line), the `last_def + 2` settle count (a one-poll grace, unpinned), the `_gate_reader_barrier_self_test(check)` call itself (a deleted call is unpinned by construction), and constants and stubs inside the added self-test code. None is a production predicate. Carry: dismissed: test-data constants and equivalent mutants
- Enumerator for the barrier registry: `blind_classify_readers` over merge_train.py, orchestrator_tick.py, review_packet.py and proof_watch.py, compared with `BLIND_CLASSIFY_READERS` by `_gate_reader_barrier_self_test`.

## Red checks

- `arch-score / arch-score` at head 44e0b74b55080d829f199410c2e4861850cd7d99: its first run (job 131268051080) failed in the PR-lookup step on `gh: HTTP 503`; nothing was scored (no dS or WORSENS line in its log). The cause is outside this repository (GitHub API, owner GitHub). Its re-run (job 131294433348, run 43242714081) concluded success. At the new head the check has not run yet from this seat; a fresh run scores it, and no score is claimed here. Cheaper detector: none exists.

## Forward-carry

- Section 5.2 of `dev/audit/rca/r10-gate-busy-defer-2.md` (a fresh dispatch where a re-run would replay a stale pinned program) stays needed under the at-once program; re-measure with that document's `census` arm after #3473 lands. Carry: dismissed: the seam is #3473 (R10-HOTFIX-GATE-REDISPATCH-LOOP), whose roster row is carries-open and not receivable; the relay folds this re-measure instruction when #3473 lands
- The fixer step 8 extension to a writer change (enumerate the readers of a conclusion whose meaning changes), proposed in `dev/audit/rca/r10-gate-defer-read-final.md` section 6, is policy and is not edited here. Carry: dismissed: owner-only policy, already recorded in that document's section 7

## Friction

none

## Approval

Policy file changed: `dev/governance/roles/nudge.md` step 15 (the only nudge.md in the tree; there is no generated copy). Not approved yet: this seat holds no approval and asserts none. Merge waits on `@tvofi`'s approving review of the head, per `CLAUDE.md`.
