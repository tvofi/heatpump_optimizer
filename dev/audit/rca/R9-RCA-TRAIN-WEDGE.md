# R9-RCA-TRAIN-WEDGE: the merge train's pre-admission wait demanded runs no push event owed it

The root-cause seat ran beside the fixes (**#2170** merged, **#2171** open at `5499a38a`) and
not inside them (`dev/governance/roles/root-cause.md`,
`dev/governance/rules/defect-root-cause.md`).

**Trigger.** 2026-10-13: five or more consecutive `merge_train.py batch --overlap`
invocations produced zero output and zero merges, each killed at its 2-hour wait budget. The
faulthandler stack (orchestrator census) sits at `batch` → `main_green` → `wait_ci`
sleeping — the pre-admission `main_green(base, req, "before admission")`, the first act of
`batch` (`tools/audit/seat/merge_train.py:941`), so nothing after it ever ran or logged.
`batch2b` (01:55Z) merged normally: main's tip then had all required runs concluded.

## 1. Named cause (reproduced at the production clock)

`wait_ci(h, only=req)` returns only once **every** required context has a *completed* run at
`h` — `all(last.get(n, {}).get("status") == "completed" for n in only)` — so a required name
with **no run at all** reads as "not yet" and the loop sleeps on. Pre-#2171 `main_green`
called `wait_ci(tip, only=req)` **before** its `--overlap` branch: the owner's P7 decision
"do not wait on main's CI" was implemented as "do not *Stop*", and the blocking wait ran
anyway. `polls=24 × POLL_SECONDS=300 = 2 h`, then `TIMEOUT`.

Why a main tip legitimately lacks completed runs — the trigger matrix, read from the tree
and measured from the day's own runs:

| context | produced on push by | measured 2026-10-13 |
|---|---|---|
| `fast (3.14)` | `tests.yml` job `fast`, `if: !cancelled() && (push || pull_request || merge_group …)` | ran 13:30:41→14:22:49Z at the 13:30:33Z tip (52 min) |
| `closures` | `tests.yml` job `closures`, bare `!cancelled()` over `needs: [closure-scope, coverage]` | check run **created** 14:40:29Z at the #2170 merge tip — 58 min after the 13:42:22Z push, queued behind the day's saturation (34 `PR contract re-run` workflow_run runs fired at that tip, 13:44–14:48Z) |
| `Analyze (actions\|javascript-typescript\|python)` | `codeql.yml` matrix, `on: push: branches: [main]` | `Analyze (python)` 13:30:41→13:55:04Z (25 min) |

On a quiet day all five conclude well inside 2 h (why `batch2b` worked). During the day's
runner saturation the incomplete window at a fresh merge tip exceeded the budget, and the
orchestrator's required-set diff at tip `96901a0d9` found exactly those five with no runs at
census time. `wait_ci(only=req)` cannot conclude at such a tip; the invocation died
silently.

**Reproduced diagnostic** (this seat; `Train` subclass, stubbed `gh`, sleep *counted* not
slept, `polls=24` — the production clock; required set = the 17 ruleset-23698884 contexts
minus nothing, the five heavy lanes absent, the light lanes completed):

- current main `cb7cb25c7`: **24 check-run reads, 24 sleeps = 2.0 h**, then `TIMEOUT`;
- #2171 head `5499a38a`: **1 read, 0 sleeps**, returns immediately.

## 2. Process state: (c) — followed, and it pinned the wrong thing

The process existed and was followed arms-first. The batch self-test's world factory
hard-wires the precondition the defect violates — `ci()`'s base branch carries the comment
*"main's own push run writes every required context"* and marks every required context at
the base `completed`. The un-concludable tip was therefore unreachable in any arm's world,
and the `--overlap` arm asserted its log line over a *completed-red* base (`main_moved`),
pinning **no-Stopping** rather than **no-waiting**. Not (b): no step was skipped. Not (d):
`fast`'s ~50-minute push run predates the flag; the fixture's assumption was false at merge
hours from birth. What the day changed is frequency (saturation plus the R9-CI-SKIP churn of
#2159/#2160), turning the latent hole into five dead trains.

## 3. Cost test

- `cost(defect)`, counted for 2026-10-13: 5+ dead invocations × 2 h = **10+ wall-clock
  hours** with zero train merges; 3 misdiagnosed "wedges" (legitimate required-only waits)
  cost investigation turns; 2 healthy trains were killed on that misdiagnosis; the day's
  merges fell back to hand-merges.
- `cost(countermeasure, recurring)`: 6 new self-test arms; the whole
  `merge_train.py --self-test` measured **41.7 s** locally (111 checks pre-#2171, 113 post),
  so the arms' share is ≈ 1 s per CI run.
- `P(recurrence)`, measured same-day: 3 of 3 wait sites carried the class; ~5 of ~6 batch
  invocations wedged (the quiet-hours one did not).
- 1 s per run < 10 h × ~0.8: passes by roughly four orders of magnitude. The audit-class
  bound (3+ instances in one round) also triggers, and the barrier is the fix itself.

## 4. Countermeasure and verification

- **#2170** (merged at `96901a0d9`): `admit` and `at_head` wait the ruleset's required
  contexts only, with four new arms (admission-time `TIMEOUT`, a red non-required context
  not holding, a stuck non-required lane not holding, a red required context still stopping).
- **#2171** (open, checks green, head `5499a38a`): `main_green` under `--overlap` performs
  one non-blocking read (`_check_runs` + `_by_name`) and logs; the non-overlap completion
  wait — D's bound — is unchanged, with a control arm asserting it still waits.
- **No fourth blocking wait site**: every `wait_ci` call at the #2171 head classified —
  `at_head`/`admit` (pull-request heads, whose runs the train knows fire; bot heads are
  refused first by `bot_refusal`), `settle` and its subsets (proof branches the train itself
  launched; a `TIMEOUT` there is a *named* `Stop`, never silence), and `main_green` — one
  method, **three call sites** in `batch`: before admission (`merge_train.py:941`, the one
  that wedged), right before each entry's merge (`:992`), and the D-merge revert guard
  (`:1016`) — all three behind the same one-pass-under-overlap fix. Class search beyond the
  train: `ci-watch.sh` already judges ABSENT only at a settled head (its W3 arm is the same
  lesson learned earlier); `merge_pr.sh` waits all runs but bounded at 60 min on the
  single-PR path; `codeql-triage-poll.sh` polls specific runs, not a required set.

## 5. The check demonstration — and what it found in the countermeasure

`defect-root-cause.md` demands a check-shaped countermeasure be shown failing on the defect
and passing once fixed. Both runs, measured:

- the standalone diagnostic in §1 discriminates: **24 sleeps (red) pre-fix, 0 sleeps (green)
  at the #2171 head**;
- the full self-test at the #2171 head: 113 checks, 0 failed (null control — it does not
  fire on the healthy tree).

**But the arm on #2171's branch head (`5499a38a`) does not redden the defect.** Measured:
with only the pre-fix `main_green` planted back into #2171's file (its fix hunks reverted,
every test hunk kept), the suite still reports **113 checks, 0 failed** — the stubbed clock
makes a blocking wait free, and the landed arm asserts outcomes (`rc`, merges, the log
line), not the one-pass property. That is the exact "check that passes while the bug is
present" shape the rule names, inside the countermeasure itself.

**The arm that does detect it is the invocation-counting form the fixer's instruction now
pins**: a self-test where the `wait_ci` call is counted — main_green must drive it **zero
times under `--overlap`** and **exactly once on the non-overlap path** (counting the calls
whose `h` is main's base tip; admit/settle legitimately call it at their own heads).
Demonstrated by this seat on the #2171 wiring, both runs measured:

- current #2171 wiring + the counting arm: **113 checks, 0 failed** (count 0 under
  overlap; the non-overlap control's count is exactly 1);
- the same build with the pre-fix `main_green` planted (the blocking `wait_ci` before the
  overlap branch): **113 checks, 1 failed** — the overlap arm goes red on the nonzero
  count, while the non-overlap control still passes.

An in-suite `cr_reads == 1` ceiling is wrong — measured `cr_reads[base] == 2` on the fixed
tree, because `main_green` legitimately re-reads the tip at "right before #N's merge". The
counting arm is **not yet on #2171's branch** as of `5499a38a`; it must land in #2171
before that pull request merges. This RCA reports it to the orchestrator rather than
editing the fixer's branch.

## 6. Record

Named cause, state (c), cost test and countermeasure verification: this file. The defect
class is mechanism-akin to P6 (a consumer waits on a fact no producer writes at that
moment, with a silent fallback); `bugclasses.json` carries no class for instrument waits —
folding it in is the owner's call, not this seat's.
