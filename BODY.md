Root cause fix for the roster drain's "stale-worktree trap" and its "HEAD ... is on no origin ref" cascade (round 10 root-cause seat, 2026-11-08). The sweep runner drain refused roster ops because the lint clone stayed at an older main; each refusal then stranded a local commit in wt-run and refused the next op for that op's fault.

Cause, in tools/audit/seat/roster_queue.py `_run_op`: (1) the lint refresh (fetch, detach) ignored return codes and read the lint clone's own origin/main, a different ref from the edit checkout's origin/main that roster_edit.lint_gate compares; four attempts in a row stayed stale (main-lint's origin/main reflog: no update 11:40 to 14:34 +0100 while the edit checkout saw 4a9d2d5 and bb7dfb9). (2) A refusal other than "not origin/main" left its edit as a local commit in the worktree. Why the clone's fetch did not move is not established; the fix does not depend on it.

Process state (defect-root-cause.md): (c). The check existed (the lint gate, the retry on "not origin/main") but the refresh feeding it was unchecked and read another ref.

Fix: `refresh_lint` detaches the lint clone at the edit checkout's origin/main SHA after a fetch there, verifies HEAD equals it, and refuses by name ("lint clone not refreshed") otherwise; a final refusal removes the worktree.

Repair round 1 (fix review blocked `mutation-vacuous` at d0db3e30b8, ref verdict/3337): only the detach SHA was pinned; M4, M5 and M6 survived the harness and the self-test, M3 and M7 survived as minor. This round adds no production line; it adds checks that each mutant fails:
- the harness now runs three scenarios: `stale` (the finder's: the lint clone's fetch fails, both ops push), `cascade` (the reviewer's variant: the stub refuses op1 once for an unrelated reason and op2 must push, which needs the refused op's worktree removed: pins M4), `follow` (another clone pushes main, and `refresh_lint` alone must detach a clone with its own object store, no alternates, at origin's new main: pins M3, the edit checkout's fetch, and M7, the clone's fallback fetch).
- the self-test gains two checks on an empty lint clone (a directory with no objects and no origin): `refresh_lint` must refuse it naming the wanted SHA (pins M5), and `_run_op` must report "lint clone not refreshed" and never run the editor, read from the stub's calls file (pins M6).

Cost test: defect about 5 min hand-landing plus about 20 min pass delay per stale refusal, 172 of 1327 drain report lines (13%) were cascade refusals, 3+ instances on 2026-11-08; countermeasure a one-time diff of about 40 production lines and about 50 ms per op, no extra network call. cost(countermeasure) < cost(defect) x P(recurrence).

## Head

d21308c547e09cd298c9f62a6ff52cd436597a8a

Measured at that head: the repair commit 516f48443 plus a merge of origin/main at 17e621f08c (fetched 2026-11-08 19:38 UTC; main touched no file this PR reads: `git diff --stat 8a4974d15 17e621f08 -- tools/audit/seat/roster_queue.py tests/throwaway_git.py` is empty). The merge re-ran steps 2-8: harness, self-test, mutation table, `tests/entities.py`, `tests/structure.py`.

## Mutation proof

Mutants are the reviewer's seven (verdict/3337 evidence/mutants_src), re-applied as the same one-line edits to this head's roster_queue.py. Harness: `python3 -I dev/audit/harnesses/roster_queue_stale_lint.py <mutant>`; self-test: the mutant copied over tools/audit/seat/roster_queue.py, `python3 -I tools/audit/seat/roster_queue.py --self-test`, the file restored by copy (cmp-checked).

| mutant | edit | harness | self-test (56 checks) | verdict |
|---|---|---|---|---|
| M1 | `return ""` at the top of refresh_lint | stale, cascade, follow FAIL | 3 failed: missing clone refused; checkout-fails clone refused; unrefreshed lint clone reported | killed |
| M2 | detach at `origin/main` (the clone's own ref) | stale, cascade, follow FAIL | 0 failed | killed (harness) |
| M3 | edit checkout's `fetch origin main` -> `status` | follow FAIL | 0 failed | killed (harness) |
| M4 | drop the `worktree remove` before the final `return False` | cascade FAIL | 0 failed | killed (harness) |
| M5 | `if c.returncode != 0 or head != sha:` -> `if False:` | PASS | 2 failed: "refresh_lint: a clone whose checkout fails is refused, not passed"; "run: an unrefreshed lint clone is reported by name and the editor never runs" | killed (self-test) |
| M6 | `if err:` in _run_op -> `if False:` | PASS | 1 failed: "run: an unrefreshed lint clone is reported by name and the editor never runs" (got a pushed line) | killed (self-test) |
| M7 | drop the lint clone's fallback `fetch origin main` | follow FAIL | 0 failed | killed (harness) |

Harness at base (the merge base 8a4974d15's pre-fix roster_queue.py) and at head:

```
== base
stale: roster: set-stage G refused rc=3 LINT GATE REFUSED the push | --lint-cwd is at 1a0b5e98908e, not origin/main (ffb2bf55d622): the stale-worktree trap
stale: roster: set-stage G refused rc=2 REFUSED: /tmp/tmp38auqz8m/wt HEAD 1277575df3b1 is on no origin ref
stale: RESULT: FAIL
cascade: roster: set-stage G refused rc=4 REFUSED: unrelated
cascade: roster: set-stage G refused rc=2 REFUSED: /tmp/tmpakdn9ony/wt HEAD 759e43435cf7 is on no origin ref
cascade: RESULT: FAIL
follow: no refresh_lint
follow: RESULT: FAIL
RESULT: FAIL
== head
stale: roster: set-stage G pushed 1c60b7dba
stale: roster: set-stage G pushed e748630b6
stale: RESULT: PASS
cascade: roster: set-stage G refused rc=4 REFUSED: unrelated
cascade: roster: set-stage G pushed e748630b6
cascade: RESULT: PASS
follow: refresh_lint='' head=cae73fe8aa58 origin main=cae73fe8aa58
follow: RESULT: PASS
RESULT: PASS
```

## Null control

- The reviewer's null variant (verdict/3337 evidence/variants_src/null_fresh.py: the lint clone's fetch works and is fresh, no refusal) prints `RESULT: PASS` against the base roster_queue.py and against this head's: a healthy drain was never refused, so the checks read the defect, not the setup.
- Every new check passes on the unmutated file: `python3 -I tools/audit/seat/roster_queue.py --self-test` prints `roster_queue self-test: 56 checks, 0 failed`; the harness prints `RESULT: PASS` on all three scenarios (above).
- In `cascade`, op1's refusal is still reported (`refused rc=4`) at head: the fix removes the stranded worktree, it does not hide the refusal.

## Figures

- 56 self-test checks, 0 failed (54 before this round, plus the two `lc_empty` checks): `python3 -I tools/audit/seat/roster_queue.py --self-test`.
- Mutation table, 7 of 7 killed (rule: a mutant is killed when the harness prints `RESULT: FAIL` or the self-test reports at least one failed check): the commands in `## Mutation proof`, mutants from verdict/3337 evidence/mutants_src.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`; it runs `tests/entities.py`, which passed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `tools/pr/prepr.sh` ran clean at this head with `PREPR_SKIP_CLOSURES=1` (cloud seat; closures-autofix repairs that step on the PR). Null control against main: `git diff 17e621f08 HEAD -- tests/closures.json` is the one inert entry for the harness, which the previous round already recorded, and this round's commit (`git diff --stat d0db3e30b 516f48443`) touches only the harness and roster_queue.py, both already classified, so the skipped step has nothing new to read.
- 1327 report lines, 786 pushed, 172 no-origin-ref cascade, 2 stale-worktree, 30 lint TOTAL refusals: counted from the sweep runner's roster-rep.txt (outside the tree); `python3 -I dev/audit/harnesses/roster_queue_stale_lint.py` reproduces the two mechanisms, not the counts.

## Red checks

- `gate` in run 42499187718 (job 128788451757), concluded red at d0db3e30b8: a deferral, superseded by run 42499185929's green `gate` at the same head. No defect in this diff; no cheaper detector is owed. (Separately, `merge_train.py classify` reports a deferral red as RED even when its deciding run is green: an instrument observation the reviewer recorded on verdict/3337 for the orchestrator, not filed here.)
- No red at the new head is known at handoff: it has not run CI yet.

## Forward-carry

none

## Friction

none
