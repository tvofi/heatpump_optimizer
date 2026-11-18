# R10-N-vocabulary-drift: a record's writer accepts a word no read can close

**Instances (three in round 10).** `459ef684a` — `roster_edit.py append-group`
inserted a group whose `resume.stage` read `in-review`; CI job `119785082787`
failed because `roster_sync.py` had no rule for that word. `94ece3d08` —
`roster_edit.py set-stage` wrote `in-review` on `R10-HOUSE-GRADE` again; CI job
`122016117273` step 59 failed (the finding is registered in the r10 roster as
this group's carry index 3). `d6308d77c` — eight `R10-FLY-*` groups were
appended with `"size": "XS"` while `tools/plan/durations.json`'s `sizes_hours`
carries only `L`, `M`, `S`, `XL`; `replan.build_plan` line 325's
`size_hours[G[n].get("size") or "M"]` raised `KeyError: 'XS'` for every
planning run, and `tools/plan/` is `INERT` at `tests/closure.py:336`, so no
gate read it. Reproduced at the fix head against main's roster, which still
carries `XS`:

    python3 -I - <<'EOF'
    import json, subprocess, sys, datetime as dt
    sys.path.insert(0, "tools/plan")
    import replan
    roster = json.loads(subprocess.run(
        ["git", "show", "origin/main:dev/programme/rosters/wave-r10-groups.json"],
        capture_output=True, text=True).stdout)
    caps = {"slots": 4, "seats": 4, "coordinator_cap": 1, "stamp_every": 20}
    replan.build_plan(roster, json.load(open("tools/plan/durations.json")),
                      caps, dt.datetime(2026, 10, 27), "t")
    EOF
    # -> KeyError: 'XS'

**Named cause.** The roster's vocabulary was declared on each side of a write
and nowhere between them. `roster_edit.py` validated a stage only as
"a non-empty string" (`op_set_stage`) and a size not at all (`op_append_group`
copied the entry's `size` through), while `roster_sync.py` held its own
`DERIVABLE_STAGES`/`PROTECTED_STAGES` and `replan.py` its own `LIVE_STAGES` and
the duration model. So the writer could record a state that no reader could
close — and `roster_edit.py:883`'s own self-test round-tripped `in-review`,
asserting the unclassified word as the contract. The size half had no writer
check at all, so `XS` was written the same way.

**Process state: (a) — the process did not exist.** No check anywhere in the
tree tested that a stage or size word written to a roster was one a read could
consume: the writer's self-test asserted the drift (`roster_edit.py:883`), the
reconciler's self-test listed its own stages but never read the writer's, and
the planner had no test that its model keys every size the roster carries. This
is not (b): nothing was bypassed. It is not (c): no check existed in CI or
locally to be obeyed and prove insufficient.

**How far the class reaches** (searched, not assumed: `grep -rn` for stage and
size writers and for declared vocabularies under `tools/`). Found:
`replan.py:94`'s `LIVE_STAGES` is a second copy of a stage subset (it is
exactly the registry's `LIVE`; `roster_lib`'s self-test pins the equality, and
R10-PLAN-PRIO owns adopting the view); `orchestrator_tick.py:206`'s
`DEFERRED_STAGES = ("deferred", "refused")` is a third, narrower subset of
`roster_lib.DISPOSITION` (it omits `refuted`, `absorbed`, `carries-open`), so a
group in one of those three can be reported as owed; and
`state_docs.py:830`'s self-test fixture writes `refused-then-landed`, a word the
writer now refuses. None is fixed here: each is another seat's file, and the
first two change what a report says rather than what a roster holds.

One gap is named and left to its own carry: a size can still be changed by
hand-editing the roster JSON, because `roster_edit.py` has no `set-size` op
(this group's carry 20, triage `s6-batch26.md#P139`, asks for `set-size` and
`set-files`). The new read-side scan is what covers that route: a hand-edited
size the model does not key is red in `roster_sync.py --self-test`, which
`governance.yml` runs on every pull request, so the drift can no longer reach
main silently — but the write route is a refusal only once that carry lands.

**Cost test.** cost(countermeasure) = the registry and the refusals already
written here, run inside the two self-tests `governance.yml` already executes
(`python3 -I tools/audit/seat/{roster_edit,roster_lib,roster_sync}.py
--self-test`) — no new job, no standing minutes. cost(defect) = two CI reds in
one round, each costing a lane a re-push, a reviewer re-verdict and a
`steward` pass (jobs `119785082787`, `122016117273` step 59), plus a planner
that died on every run with `KeyError: 'XS'` and no gate to see it. P(recurrence)
= 3 in round 10 (measured: three instances above). The countermeasure pays on
the first avoided red.

**Countermeasure and demonstration.** `roster_lib.py` now holds one registry:
`STAGE_KIND`, a tuple of `(word, kind)` with `kind` one of `derivable`,
`live-claim`, `done`, `disposition`, and `DERIVABLE`, `LIVE_CLAIM`,
`DONE_STAGES`, `DISPOSITION`, `LIVE` derived from it (never re-declared);
`sizes(durations)` returns the model's `sizes_hours` keys, so the measured model
*is* the size vocabulary. `roster_sync.py` imports the views and closes a live
claim to `done` on its merge, so a merged group cannot be stranded open.
`roster_edit.py` refuses an unclassified stage at `set-stage`,
`set-resume --field stage` and `append-group`, and an unmodelled size at
`append-group`, naming the roster path, the group id and the offending value.

Demonstrated both ways, in this pull request: at the red head `21b1ed140`
`roster_edit.py --self-test` reads `124 checks, 4 failed` (the three writer
refusals and the size) and `roster_sync.py --self-test` reads `61 checks, 4
failed` (a live claim lost under an open pull request, a merged live claim
never closed, a `done` group rewritten, and `{'XS': 'wave-r10-groups.json'}`
from the size scan); at the fix head both read `0 failed`. Each refusal arm
carries a null control (a classified stage and a modelled size still land), and
each is mutation-proven: `r10_roster_ops_mutants.py` plants S1–S7 (each op's
check, both registry guards, and the vocabulary dropped from `apply_op`, so a
legal size is refused) and `r10_roster_sync_mutants.py` plants M21–M24 (a live
claim rewritten, a live claim stranded, a `done` group rewritten, the size scan
blind); every plant turns its own arm red and the null runs read `rc=0 fails=0`.

**Data repair.** The eight `XS` groups are relabelled `S`, the smallest
modelled bucket, because adding `XS` to the model without a measurement would
put a guessed number in the plan. The measurement is carried to
`R10-FLOW-TOOLKIT-MODEL`, whose brief owns the duration model.

**Class citation.** Registered as `N-vocabulary-drift` in
`dev/audit/config/bugclasses.json` with `"rca": ["R10-N-vocabulary-drift"]`
(kind `instrument`, nearest existing `I4`).
