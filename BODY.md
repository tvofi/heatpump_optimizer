Beat-only dispatch (P404) and one window for rules 4 and 5 (P403), from triage batch 132 (dev/programme/triage/s6-batch132.md), repaired for the blocked fix review at 01e9c612 (verdict/3296, class-open). The record flush dispatched nightly.yml with no input, so every nightly lane ran to reach the one-minute record-autofix job. Rule 5 read tag..origin/main while rule 4 read tag..HEAD, so a merge past HEAD after a flush timeout refused rows (v7.1.5 run 1, #3271).

Round 1 changes (unchanged): nightly.yml gains `workflow_dispatch.inputs.lanes` (choice all|beat, default all); mutation-nightly, mutation-ledger, mutation-ledger-push, slow and nightly-ha append `&& inputs.lanes != 'beat'`; record-autofix's `if` is unchanged. stamp.py `RECORD_BEAT_PAYLOAD` posts `lanes=beat`. `tests/delivery_status.py --head REV` (default origin/main) ends its window; `disposition_gate` passes the stamp head.

This round, the review's block: a lanes=beat dispatch skips every REQUIRED_LANES job, and `tests/nightly_status.py` graded it as the newest concluded main dispatch, reading ABSENT (EXIT_RED) after every stamp flush and hiding the last real nightly's jobs. The cure is the reviewer's, in the same files:
- nightly.yml gets `run-name: ${{ inputs.lanes == 'beat' && 'Nightly record beat' || 'Nightly' }}`.
- `nightly_status.BEAT_TITLE` / `is_beat(run)`: `_discover` drops a run whose `display_title` is the beat title before `pick_runs`, and `collect(--run-id)` refuses one as `Unreadable` (a beat verifies nothing).
- tests/entities.py evaluates nightly.yml's own `run-name:` against `BEAT_TITLE` (beat gives it; lanes=all and the schedule do not), and drives `collect` over a listing holding a newer dispatch and an older scheduled nightly. A beat dispatch is never graded, by discovery or by `--run-id`. The null control is a lanes=all dispatch, which still is.
- stamp.py: the `FLUSH_MAX_DISPATCHES` comment and the rule-"flush" docstring named the old every-lane dispatch; both now name the lanes=beat run. The stamp self-test's rows-gate and record-beat pins now also read the return values, which kills the three diff-mutant survivors (below).

`verdict()` is unchanged by design: a beat run that were graded would still read ABSENT, which is right. The fix is that one is never selected. Alternative considered: grading a beat as "no nightly here" inside `verdict`. Rejected: a title is the run's own declaration, and dropping it at discovery keeps the age window and the corroboration loop working on real nightlies only.

Closes: none.

## Head

b4446e5cb97958de79c1c9d38d25e7679624de68

## Mutation proof

Each mutant was applied in place to the committed tree at 9dce60e3, followed by `PYTHONPATH=tests/hastub python3 tests/entities.py`, then `git checkout --`. `git status --short` was clean after each. In this container the baseline fails 3 of 2652 (the three workflow-run probes the reviewer also saw: coverage reuse, release ZIP, Pages). Each mutant adds only its own failures to that set:
- `_discover` without `not is_beat(r) and`: 4 of 2652, adds FAIL "a lanes=beat dispatch is never the graded nightly, by discovery or by --run-id; a newer lanes=all dispatch still is (null control)" [beat: graded (82, 'refused'), want (81, 'refused')].
- `collect`'s `if is_beat(run):` changed to `if False:`: 4 of 2652, adds the same check [beat: graded (81, 'read'), want (81, 'refused')].
- nightly.yml's run-name with `'Nightly record beat'` changed to `'Nightly'`: 5 of 2652, adds FAIL "nightly.yml titles a lanes=beat run nightly_status.BEAT_TITLE, and no other run" and the graded-nightly check [beat: graded (82, 'read')].
- Round 1's mutants (stamp `--head`, payload, nightly.yml `if:`s) were re-run by the reviewer at 01e9c612 (verdict/3296 evidence/); this round does not change those lines.

## Null control

A newer lanes=all dispatch on main is still the graded run (entities check above, `(82, 'read')`), and so is the scheduled nightly when no dispatch exists. nightly.yml titles a schedule run and a lanes=all dispatch `Nightly`, never the beat title (the run-name check evaluates all three inputs). `verdict()` is untouched: the reviewer's harness still reads lanes=all PASSED and lanes=beat ABSENT at this head (Figures).

The companion harness named under Figures, for re-running:

<details><summary>companion harness source (beat_graded.py)</summary>

```python
"""Fixer's companion to the reviewer's beat_nightly_status.py: drives the
reporter's own selection (nightly_status.collect -> _discover -> pick_runs)
over a listing holding a newer dispatch and an older scheduled nightly, the
dispatch titled by evaluating the given nightly.yml's run-name (absent at the
base: the default title). Prints which run is graded and its verdict."""
import sys, re, datetime as dt
sys.path.insert(0, sys.argv[2]); sys.path.insert(0, "tests")
from fns import _workflow_job, _gh_if, _gh_eval
import nightly_status as ns
yml = open(sys.argv[1]).read()
body = yml.split("\njobs:", 1)[1]
ids = re.findall(r"^  ([A-Za-z][\w-]*):$", body, re.M)
m = re.search(r"^run-name: \$\{\{ (.*) \}\}$", yml, re.M)
def title(lanes):
    if not m: return "Nightly"
    return eval(m.group(1).replace("inputs.lanes", repr(lanes)).replace("&&", " and ").replace("||", " or "), {"__builtins__": {}})
def jobs_for(ev, lanes):
    ctx = {"github.event_name": ev, "github.ref": "refs/heads/main", "inputs.lanes": lanes,
           **{f"needs.{x}.result": "success" for x in ids}}
    return [{"name": n, "conclusion": "success" if _gh_eval(_gh_if(_workflow_job(body, n)), ctx) else "skipped"} for n in ids]
now = dt.datetime(2026, 11, 8, 12, 0, tzinfo=dt.timezone.utc)
for lanes in ("beat", "all"):
    runs = {1: {"id": 1, "event": "schedule", "head_branch": "main", "status": "completed", "conclusion": "success",
                "created_at": "2026-11-08T00:40:00Z", "display_title": title("")},
            2: {"id": 2, "event": "workflow_dispatch", "head_branch": "main", "status": "completed", "conclusion": "success",
                "created_at": "2026-11-08T09:00:00Z", "display_title": title(lanes)}}
    jobs = {1: jobs_for("schedule", ""), 2: jobs_for("workflow_dispatch", lanes)}
    def get(url, _t):
        if "/jobs" in url:
            rid = int(url.split("/runs/")[1].split("/")[0]); return {"total_count": len(jobs[rid]), "jobs": jobs[rid]}
        ev = url.split("event=")[1].split("&")[0]
        return {"workflow_runs": [r for r in runs.values() if r["event"] == ev]}
    ns._get, ns._sleep = get, lambda s: None
    c, f, j, rec = ns.collect("o/r", "nightly.yml", None, None, now=now)
    state, rc, _ = ns.verdict(c, f, j, now)
    print(f"RESULT dispatch lanes={lanes} title={title(lanes)!r} graded_run={c['id']} ({c['event']}) nightly_status={state} rc={rc}")
```

</details>

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py` at b4446e5c: 3 of 2652 ENTITY CHECKS FAILED (rc=1). The failing checks are the three workflow-run probes named above, the same set the reviewer recorded at 01e9c612 (verdict/3296 evidence/entities-head-fails.txt). The two new checks pass.
- `python3 tests/structure.py` at b4446e5c: STRUCTURE RATCHET PASSED (rc=0).
- `python3 tools/release/stamp.py --self-test` at b4446e5c: RESULT stamp_self_test=pass.
- `MUTANT_CMD="python3 tools/release/stamp.py --self-test" bash tools/pr/prepr.sh` at 278609d6: rc=0, `diff mutants` WARN 3 survivors, all in the self-test's own fixture lines (stamp.py `_Proc(0→1, "ok")` in the rows-gate forward pin; `_BeatResp.status = 204→205`; the urlopen lambda's `[1]→[2]`). The cure is b4446e5c, where the pins read `disposition_gate`'s and `dispatch_record_beat`'s returns. Re-run: `python3 -I tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --cmd "python3 tools/release/stamp.py --self-test" --max-mutants 40 --report-only` at b4446e5c: 7 mutants (`--list`), 0 SURVIVED, rc=0, wall 9.1 s. mutant_run's diff mode mutates only stamp.py here. The nightly_status.py and nightly.yml lines are pinned by the in-place mutants under `## Mutation proof`.
- `MUTANT_CMD="python3 tools/release/stamp.py --self-test" bash tools/pr/prepr.sh <this body>` at b4446e5c: rc=0 (the PRE-PR line names b4446e5c). origin/main has moved past the merge base (15e34edb at handoff), and `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main was not merged (owner ruling 2026-11-07).
- Reviewer's harness beat_nightly_status.py from the verdict/3296 evidence (`git show aa2d255e8f0db7fd9f682b2885af88869feeb260:evidence/beat_nightly_status.py`, sha1 4869f3965a186a26fe7a28eda76ca9d4e0a8f758), run with a `fns.py` holding entities.py's own `_workflow_job`/`_gh_if`/`_gh_eval` text (sha1 d650249cf5c26d64bc51d3b2411afdeafbdec64c):
  - base aaaec212 nightly.yml: `lanes=beat nightly_status=PASSED rc=0` (every lane runs) and `lanes=all PASSED rc=0`.
  - 01e9c612 and b4446e5c nightly.yml: `lanes=beat nightly_status=ABSENT rc=1 ran=['record-autofix']` and `lanes=all PASSED rc=0`. It feeds the beat's jobs straight to `verdict()`, which this fix rightly leaves alone, so it reads flat between 01e9c612 and this head.
- Companion harness (the fixer's own, sha1 ee112c070bfafac5ac74b3c2ad707b33add25349, source under Null control). It drives `nightly_status.collect` → `_discover` → `pick_runs` over a newer main dispatch and an older schedule run, with the dispatch titled by evaluating that tree's nightly.yml `run-name:`:
  - base aaaec212: beat → graded run 2 (workflow_dispatch) PASSED rc=0; all → graded run 2 PASSED rc=0.
  - 01e9c612: beat → graded run 2 (workflow_dispatch) **ABSENT rc=1**; all → graded run 2 PASSED rc=0 (the defect).
  - b4446e5c: beat (title 'Nightly record beat') → graded run 1 (schedule) PASSED rc=0; all → graded run 2 (workflow_dispatch) PASSED rc=0 (null control).
- Class seams (fixer step 8). Rule: `git grep -l -E "actions/(workflows/[^ ]*/)?runs" -- tests tools .github | xargs grep -l -E "nightly"` returns 8 files. Disposition per site that reads the runs API:
  - tests/nightly_status.py `_discover` / `collect`: closed in this diff.
  - .github/workflows/tests.yml `nightly-status` job: runs nightly_status.py, closed with it. Its run-approver steps query `status=action_required` on a PR branch, so a beat cannot match.
  - tests/entities.py: fixtures only.
  - tools/audit/seat/replay_draws.py `fetch`: lists nightly.yml runs, but harvests only `slow` / `tests / replay` job logs, so already guarded. A beat's `slow` is skipped and gives no draw. It takes a newest-N slot, so a window yields fewer draws; no false draw is possible.
  - tools/ci/gate.py: `workflows/ci.yml/runs` only. Not reachable.
  - tools/pr/merge_main_bot.py `pins_running`: runs at the PR head SHA, jobs `tests / mutation*`. Not reachable.
  - tools/audit/seat/merge_train.py `review_runs`: `event=pull_request_review`. Not reachable.
  - tools/release/stamp.py `gate_runs`: `event=push`, Tests/ci.yml. Not reachable. `dispatch_record_beat` posts the beat, and `record_flush` waits on git, not the runs API.


## Red checks

none at b4446e5c: CI has not yet run on this head. At the previous head 01e9c612 the concluded reds (filter=all, every page, reviewer's evidence/check-runs.tsv) were:
- `tests / nightly-status` (128480692664, 128501222702). Class: inherited main red. It graded run 42369836867 (08fd676, cancelled lanes), which predates this branch. The round-1 body answered it. Not required (owner ruling 2026-11-07).
- `pr-contract / pr-contract` (128492906044, 128501198033). Class: body contract. It refused an earlier body; a later pr-contract run, 128500799416, is green.
- `gate` (128481833681, 128487511325, 128493108261). Class: aggregate of its siblings above. It cleared with them.
- `gate` (128481461227) and `arch-score / arch-score` (128480844487) were cancelled at 17:55 and superseded by green runs.

## Forward-carry

- Carry 1: stays carried to the first stamp after merge, because this seat has no workflow-dispatch right. The code under measurement is in tools/release/stamp.py (`dispatch_record_beat`, posting `lanes=beat`) and .github/workflows/nightly.yml (`on.workflow_dispatch.inputs.lanes`, `run-name:`) at b4446e5c. Post-merge measurement owed at the first stamp after merge, for one beat-only dispatch: its jobs and runner-minutes by the runs jobs API (`python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py runs <id>`). The job list should show record-autofix alone running. The same measurement must also confirm nightly-status's reading of that run: the run's `display_title` is `Nightly record beat`, and the next PR's `tests / nightly-status` grades the last schedule or lanes=all run, not the beat. This seat has no workflow-dispatch right. Carry: R10-FLY-STAMP-FLUSH-COST

## Friction

- Carry 2: stays carried as a process note, with no code to deliver at b4446e5c. fixer-step-push: stale: refs/heads/handoff-wip/r10-fly-stamp-flush-cost held a previous seat's BLOCKED commit (e4b03333) not on the PR head's line, so a fast-forward step push was refused. I did not force it, and no step was pushed before the handoff. Carry: R10-FLY-STAMP-FLUSH-COST
