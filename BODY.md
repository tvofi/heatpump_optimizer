The orchestrator tick (`tools/audit/seat/orchestrator_tick.py`, `Tick.main`, the MAIN section) judged every non-green latest lane at main's tip red and wrote a `main-red <lane>` fixer brief for each. `pr-contract-rerun.yml` runs on `workflow_run`, so its `rerun-stale-contract` follower attaches to main's tip, and its concurrency group `pr-contract-rerun-<head_sha>` with `cancel-in-progress: true` (R10-FOLLOWER-DEBOUNCE, f210e78b) cancels an older follower for a newer one by design. Job 119215715286 at f58b14c1 was such a cancel (annotation "Canceling since a higher priority waiting request for pr-contract-rerun-c0700aa7797cfa34bea8a85df64e959c2dcaf72f exists"), and the tick reported "main-red rerun-stale-contract" for a run that never had a runner.

The fix: `Tick.superseded(cr)` reads a check run's annotations only when its conclusion is `cancelled`, and returns true only when a list entry's message matches `SUPERSEDED` (GitHub's own concurrency-cancel text). `Tick.main` drops such a lane from `red` after `judge()`, prints it on an unflagged "superseded, not red" line, and so writes no brief for it. It fails closed in four ways: any other cancel text stays red; an annotation read that fails, or a body that is not a list (null, an error object), stays red; a `failure` carrying the same text is never superseded and its annotations are never read; and a **required** context is never asked, because a required context cancelled at the tip leaves the tip with no verdict for it (REQUIRED not green stays, the stricter reading; no current required context is produced by a workflow whose group can cancel a main run, see the seams below).

This head continues the prior local fixer's `69f93a268` (never prepr'd, no body): it merges origin/main `3688cf259` (no conflict) and adds `677c8f9dc`, which (a) excludes required contexts from the superseded filter, and (b) checks the annotations body is a list before iterating it (a `null` body raised `TypeError`), each pinned by a new self-test arm.

Alternatives rejected: matching on the conclusion alone (`cancelled` -> not red) also hides a manual or timeout cancel; keying on the lane name (`rerun-stale-contract`) is an allow-list keyed on a field that does not carry *why* the run ended, so it would equally silence a genuinely broken follower (fixer.md step 14); dropping cancel-in-progress in `pr-contract-rerun.yml` reverses R10-FOLLOWER-DEBOUNCE's debounce. GitHub's annotation is the one field that records the reason, so the classifier reads it.

Root cause: process state (d). The MAIN classifier's precondition, that a non-green latest run at main's tip is a defect, held while no workflow could cancel a run attached to main's tip; f210e78b (R10-FOLLOWER-DEBOUNCE) made a concurrency cancel a normal outcome there, and the classifier was not revisited with it. `defect-root-cause.md`'s triggers do not fire: the false brief reached no release (the tick is a seat instrument, not shipped code), and it turned no pull request red, so no cause seat is owed; this paragraph records the cause for the reviewer.

## Head

`677c8f9dcb221047a0e943048187507596c98151`, measured against origin/main `3688cf25977ca71b4406be942df9592577d9b42e` at 2026-10-21T13:05Z (merge base = that tip).

## Mutation proof

Each mutant applied to `tools/audit/seat/orchestrator_tick.py` at the head, then `python3 tools/audit/seat/orchestrator_tick.py --self-test` (166 checks), then restored (`cmp` against the saved head copy: identical):

- M1 filter removed in `Tick.main` (`sup` empty): 2 failed, `MAIN cancelled lane: concurrency-superseded: brief absent`, `... superseded line iff superseded`.
- M2 conclusion test removed from `superseded()` (`if not cr.get("id")` only): 2 failed, `MAIN failed lane is never superseded: failure: not superseded`, `... and no annotation read`.
- M3 `SUPERSEDED = re.compile(r"")`: 2 failed, `MAIN cancelled lane: cancelled otherwise (null control): brief present`, `... superseded line iff superseded`.
- M4 an unreadable annotation list read as superseded: 2 failed, `MAIN cancelled lane: annotations unreadable (fails closed): brief present`, `... superseded line iff superseded`.
- M5 required-context exclusion removed: 3 failed, `MAIN superseded required context stays red: REQUIRED not green`, `... no superseded line`, `... annotations not read`.
- M6 `isinstance(notes, list)` guard removed: 1 failed, `MAIN annotations body null: not superseded`.

Failing-first: origin/main's production code with this head's self-test (and a `superseded()` that returns False, origin/main's behaviour, so the direct arms can call it): 166 checks, 2 failed, `MAIN cancelled lane: concurrency-superseded: brief absent` and `... superseded line iff superseded`; the other new arms pass there because origin/main already reads those cases red.

## Null control

- origin/main's tick: `python3 tools/audit/seat/orchestrator_tick.py --self-test` prints 150 checks, 0 failed; this head prints 166 checks, 0 failed (16 new checks: 9 in the three cancelled-lane arms, 3 required-context, 2 failed-lane, 2 non-list-body).
- The "cancelled otherwise" arm (message "The operation was canceled.") is the null control for the pattern: it keeps the brief at this head, and M3 shows the arm goes red when the pattern matches everything.
- Live replay of the MAIN section with main's tip pinned to the incident commit f58b14c1, through the real API (one-off probe, source below): origin/main's tick prints `FLAG main-red rerun-stale-contract: job 119218797523 ...` beside `main f58b14c19321 green (37 context(s) concluded green)`; this head's tick prints `main f58b14c19321: superseded, not red (...): rerun-stale-contract` and the same green line, with no flag. The latest `rerun-stale-contract` there is now 119218797523, a later follower cancelled the same way (annotation names `pr-contract-rerun-eabf604b...`), not 119215715286; both carry the concurrency text.
- Census at f58b14c1 through this head's own `Tick.check_runs` and `Tick.superseded`: 75 runs, 16 cancelled, 16 superseded, all named `rerun-stale-contract`; 0 failures, so 0 failures superseded. The census found no real cancel without the text there, so the "not superseded" side is shown by the self-test arm and M3, not by live data.
- The same replay at the current tip 3688cf259 prints `UNREADABLE: check runs at main 3688cf25977c` under both ticks: this container's proxy refuses the numeric-ID page URLs `gh api --paginate` follows (HTTP 403, "Numeric-ID repository paths ... are not supported through this proxy"), an environment limit identical at both ends.

```python
# replay.py <tick.py> <pinned tip> <checkout>: Tick.main with commits/main answered by <pinned tip>
import importlib.util, sys
spec = importlib.util.spec_from_file_location("tick", sys.argv[1]); m = importlib.util.module_from_spec(spec)
sys.modules["tick"] = m; spec.loader.exec_module(m)
t = m.Tick("tvofi/heatpump_optimizer", sys.argv[3]); real = t.gh
t.gh = lambda argv: (0, sys.argv[2]) if any(str(a).endswith("/commits/main") for a in argv) else real(argv)
t.mandate = t.pins = t.policy_drift = lambda S: None
t.main()
for l in t.sections["MAIN"]: print(("FLAG " if l["flag"] else "     ") + l["text"][:200])
```

## Figures

- self-test counts (150 at origin/main, 166 at the head, 0 failed at each): `python3 tools/audit/seat/orchestrator_tick.py --self-test`, at each tree.
- incident annotation: `gh api repos/tvofi/heatpump_optimizer/check-runs/119215715286/annotations --jq '.[].message'`.
- lanes at f58b14c1 (16 cancelled `rerun-stale-contract` of 30 such runs): `gh api --paginate --jq '.check_runs[] | select(.name=="rerun-stale-contract") | [.id,.conclusion,.started_at] | @tsv' 'repos/tvofi/heatpump_optimizer/commits/f58b14c19321af380613abeb479b9395d35df364/check-runs?per_page=100'`.
- gate scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` The run_always scripts: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`: `tests/layout.py` passes; `tests/harness_headers.py` fails 14 of 109 on this container's Python 3.11 (f-string syntax in round harnesses CI runs on 3.14), and `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at origin/main prints identical check lines (cpu times stripped, `diff` empty) under the same interpreter, so it is the environment, not this diff.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.

Class seams. Rule: `git grep -nE "check-runs|check_runs|statusCheckRollup" -- 'tools/**' '.github/**' '.claude/**' ':!*.md'`, each hit read for the sha it judges and the conclusions it counts. The property: a reader that judges main's tip red from a cancelled latest run.

- `orchestrator_tick.py` `Tick.main` (main's tip, any non-green): closed in this diff.
- `orchestrator_tick.py` PRS, WORKERS and the throughput-stall reads (`check_runs(head)`, `check_runs(cur)`, `check_runs(h)`): pull-request heads; a `workflow_run` follower attaches to the default branch's commit, never a PR head; not this class.
- `merge_train.py` `main_green` (main's tip): reads only the required contexts (`only=req`, and under `--overlap` `n in req`); `pr-contract-rerun.yml` states nothing of it is re-reported as a required context, and this diff likewise never excuses a required context; already consistent.
- `merge_train.py` `wait_ci` on entries, `merge_pr.sh`, `proof_watch.py`, `ci-watch.sh`, `record_row.py`, `ci_predict_replay.sh`, `tools/audit/round4/D11/d11lib.py` and `tools/audit/round4/D11/governance_cost.py`, `.github/workflows/pr-contract.yml`, `tools/pr/push.sh`: a pull request's head or commits; not main's tip.
- `tools/pr/prepr.sh` `ancestry_reds` and `policy_lint.mjs` `redsOverCommits`: the branch's own `merge-base..head` commits, which exclude main's tip, and they count `conclusion == "failure"` only, never `cancelled`.
- `failure_logs.sh`, `codeql-triage-poll.sh`: `failure` only.
- `tools/plan/replan.py`: the `closures` lane's timings, not a red judgement.
- `.claude/workflows/web-*.js`, `cloud_dispatch.py`, `preflight.sh`: prompt or comment text naming the API, not readers.
- `tools/policy/fixtures/red-ancestry/*.json`, `tools/plan/durations.json`: recorded data.

Only the tick's MAIN section judges main's tip red from a non-required lane, so the class has one member and this diff closes it. Workflows whose concurrency can cancel: `grep -l "cancel-in-progress" .github/workflows/*.yml`: the per-PR groups (`codeql`, `governance`, `hassfest`, `kernel-points`, `tests`, `validate`) cancel only on `pull_request` events; `governance.yml`'s `delivery-status-publish` job group can cancel a main-push run, which would then read superseded, not red, a run whose successor in the same group carries the result.

## Unpinned sites

none

## Red checks

none: no check on this branch has run yet (it carries no pull request). The incident's `rerun-stale-contract` cancel at f58b14c1 is the defect this diff stops the tick reporting, not a red this branch turned.

## Forward-carry

none: the change binds no later stage's work; the tick's MAIN line it adds is self-describing.

## Friction

none
