Roster set-stage for round 10: the merged groups' `resume.stage` becomes the canonical `done`.

## Head

`fcf2648e0c537750033500dcc1ec3cc15887bc90` — handoff/audit-r10-roster: eighteen `roster_edit.py set-stage <group> done --at-sha <merge sha>` commits.

## Mutation proof

N/A — roster state; no production code.

## Null control

N/A — roster state.

## Figures

`tools/audit/seat/roster_lib.py` counts a group done only when `resume.stage` is in `DONE_STAGES` (`done`, `rca-done`). At `origin/main` `633f37487` the merged groups read `done: merged #N` and similar, so `orchestrator_tick.py`'s PLAN section printed `56 open group(s) of 56` and every after-edge to a merged group read blocked (enumerator: `seat-python tools/audit/seat/orchestrator_tick.py --repo tvofi/heatpump_optimizer`, PLAN section). Each set-stage below was gated by `git merge-base --is-ancestor <merge sha> origin/main` before the edit, the merge sha read from `gh pr view <N> --json mergeCommit`:

R10-FAHRENHEIT #2285, R10-FEEDS #2336, R10-RATIO-SITES #2347, R10-TARIFF #2282, R10-DEEPLINK #2283, R10-UX-SETUP #2346, R10-REGISTRY-LEAK #2329, R10-SERVICES-GUARD #2290, R10-I1 #2284, R10-PRE-EDIT-HOOK #2323, R10-POLICY-LINT-STATS #2294, R10-GATE-YIELD #2275, R10-STALE-PATHS #2289, R10-STRUCTURE-BLIND #2340, R10-TICK-TRAIN #2305, R10-PREPR-CAP #2341, R10-REPLAY-LOOPNORM #2339, R10-STALE-PATHS-2 #2344.

Left open on purpose: R10-ARCHSCORE-COVERAGE (p4/p5 owed), R10-TICK-ORCH (arms a, c owed), R10-REF-PRIVACY (the tracked-file scrub and the bus evidence-path arm owed; #2310 reopened for them), R10-PUMP-MODEL (primary PR unopened, D2-s2-01 held), R10-DEEPLINK-CENSUS (#2345 open).

## Red checks

none.

## Forward-carry

n/a: roster state — the set-stage edits carry no finding that changes how a later stage must work.

## Friction

N/A: roster state — no production code, no seams.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
