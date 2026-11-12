Fix review: blocked 44e0b74b55080d829f199410c2e4861850cd7d99 class-open: blind_classify_readers misses busy=frozenset(), dict() and {}, each a no-deferral read that classify treats like ()

bus-nonce: b19d3a701f4f02f8a0a2e6246eb9fa2b

## Block

This is round 3. Round 1 was verdicted at 940705766041, round 2 blocked at 1aec0e574b42 (probe/rev-3499-0ae1cd85, aa1418625c). This head is the merge 44e0b74b55 of repair handoff 487225c07f. Round 2's items are cured except one spelling family of item 3, which stays open:

- class-open, census of blind `classify` readers: `blind_classify_readers` (merge_train.py:6790-6795) decides "reads nothing" with a deny-list. It covers a falsy `ast.Constant`, an empty Tuple, List or Set literal, and a no-argument call to `tuple`, `list` or `set`. `classify` reads `busy` only by truthiness (merge_train.py:508, `deferred = {GATE} if busy else set()`), so every empty container is a blind read. I planted `return merge_train.classify(l, r, <arg>)` in a new review_packet.py function and ran `merge_train.py --self-test` (ev/mutant_M6_family.txt, ev/mutant_M6*.diff/.log):
  - Killed (1 failed): `None`, `busy=()`, `""`, `[]`, `busy=False`, `set()`, `tuple()`, `list()`, `busy=set()`, `0`.
  - Survived (676 checks, 0 failed): `frozenset()`, `dict()`, `{}`.

  The body says a spelling list lost because "a new spelling of the same blind read is still a call". Here the census of the busy argument is itself a spelling list, and it leaks. The bugclasses record says "a structural self-test refuses another" blind read, so the barrier claim is wider than what the check enforces.

  Fix: invert the predicate. Treat as blind any busy whose AST is a literal or a call to a builtin constructor and that `ast.literal_eval` / constructor-with-no-args evaluates falsy. The sounder form is to accept only a non-literal expression (a Name, an Attribute, or a call to a non-builtin). Pin `frozenset()`, `dict()` and `{}` in the null list at merge_train.py:6826-6827. Carry: dismissed: this block, repaired in this pull request before merge

Round-2 items at this head:
1. merge: `git merge-tree --write-tree origin/main 44e0b74b55080d829f199410c2e4861850cd7d99` exits 0, and LEDGER-MERGE resolved tests/closures.json (ev/merge_tree.txt).
2. merge_pr.sh under-run: CURED. When the WAIT is exhausted, it prints `WAIT-EXHAUSTED` and exits 3. Mutant MPx (that branch prints RED and exits 1) is KILLED, 1 of 26 failed. MPy (`break` for `[ "$crc" = 3 ] || break`) is KILLED, 3 of 26 failed.
3. Census on argument count: CURED for None and empty tuple, list and set (M6a-d, M6f KILLED). OPEN for frozenset(), dict() and {} (above).
4. M8 (delete `or self._gate_busy(h, self._check_runs(h))` from policy_refusal's deferral): KILLED, "P436 A", 2 of 676 failed.
5. Approval body: CURED. It names `dev/governance/roles/nudge.md`, the only nudge.md in the tree. `tools/audit/briefs/nudge.md` is absent (ev/nudge_path.txt).
6. Finder harness stale: CURED. At the head: rc 0, no DEFECT, `under_started=[] under_queued_null=['TIMEOUT']`, `policy_null_ok=True` (ev/harness_head.txt). At origin/main 19baca7618: rc 1, `DEFECT policy`, `DEFECT under`, with null arms holding (ev/harness_base.txt).
7. policy_refusal reading real reds as a deferral: CURED. The committed harness's real-red arms at the head read `policy_B_wait=False policy_C_wait=False policy_C_names_fast=True policy_A_wait=True`. At main they read A wait=False. M9 (drop `not (deferral and n == GATE)`) is KILLED, 3 of 676 failed. I did not re-run my round-2 plant: it needs `--tree` and the body says it gained a ci.yml stub (ev/plant_head.txt is the rc 2 usage error). The committed harness's B and C arms stand in for it.

## Findings

none

## Evidence

- Head measured: 44e0b74b55080d829f199410c2e4861850cd7d99 (ev/HEAD.txt), the PR head per pull_request_read at about 15:05Z, matching the body's `## Head`. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Self-tests at the head, unmutated: merge_train 676 checks, 0 failed; orchestrator_tick 317, 0 failed; merge_pr 26, 0 failed. These match the body's figures (ev/mt_selftest.txt, ev/ot_selftest.txt, ev/mp_selftest.txt).
- Mutants on the body's named lines, all KILLED: WD (delete `or self._sibling_in_deadline(deferring)`), 2 of 676 failed, and the finder harness prints `DEFECT under` (ev/mutant_WD*). OT1 (`_classify_reading` returns raw classify), 3 of 317 failed (ev/mutant_OT1*). M8, M9, MPx, MPy as above.
- Untouched: VERSION, RELEASE_NOTES.md, the manifest and both claim files are absent from the three-dot diff (ev/untouched.txt is empty).
- CI at this head: `merge_train.py classify 44e0b74b55080d829f199410c2e4861850cd7d99 --pr 3499` printed `WAIT ... pending: gate red: none` (rc 3) at every poll from 15:08Z to 15:25Z (ev/classify_polls.txt). The verdict is blocked on the tree, so no pending-ci line follows.
- Red checks: `arch-score / arch-score` (job 131268051080) is in `owed-reds` (ev/owed_reds.txt) and failed at 15:00:56Z on `gh: HTTP 503` from `gh api repos/.../pulls/3499` in its body-read step (ev/arch-score.log, tail). That is a cause outside this repository, owned by GitHub, not this diff. The body's `## Red checks: none` was written before it. Once the head's workflows conclude, it is owed a re-run or a one-line answer naming that cause. I do not block on it here (fix-review.md step 11's posting condition is unmet: workflows are still in progress). `tests / nightly-status` failure is not in owed-reds and blocks nothing.
- Not re-derived: the live instances (#3479, #3454, #3442, #3465), the body's mutant_run --diff 89-mutant census, and the round-2 plant readings at this head (above).
- Instruments: the M6 family plant and the subagent-run mutants are the reviewer's, not the finder's. ev/reviewer_plant_policy_round2.py is the round-2 plant copied for reference.
