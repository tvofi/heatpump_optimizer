Question: the hotfix is an atomic grader+data change, so prepr.sh's ci predict refuses it as BOOTSTRAP; how do you want it routed?

Head 87eb346e089b1fae7f98028a417e22beb5dd620e (code on this ref's parent) passes every other prepr step.
Measured (three arms, scratch worktrees):
- head lints clean: `node tools/policy/brief_lint.mjs` exit 0; merged with refs/pull/3481/head exit 0; with 10 lines inserted in optimizer.py exit 0.
- the BASE grader (caacd43b4e brief_lint.mjs) over the head's tree exits 1: `LEGACY-CONTROL VACUOUS: carry-1412.json` (the re-anchored data lints clean, the base list still holds it). CI restores the grader from base, so the briefs job is red by construction.
- the head grader over the base's data would fail the old control, so no split works: p1 grader-only reddens main, p2 data-only is refused by the base grader. The change cannot be made green in two steps; it needs the serial merge route (decision 0013) with the briefs job acknowledged.
Not run: body_push.sh (it refuses a head ci_predict predicts red on).
