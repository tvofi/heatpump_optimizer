# BLOCKED: r10-sav-wood-heat repair round 2 (cloud fixer seat), superseded by a concurrent handoff

Question for the orchestrator: two seats held this topic at once. Which one returns, and should this seat's evidence go into the live body?

What happened:
- This seat resumed from `622be7c53`. It built `sensor.plan_monthly_savings`'s `saving_includes_wood` (the one definition `wood_fuel.py` `saving_includes_wood`, the sensor attribute, five golden captures claimed structure-only, the README row, and the pinned RETURN_DEL), and pushed each step to `handoff-wip/r10-sav-wood-heat`.
- While it worked, the `hpo-fixer` identity pushed onto that same ref: main merges, the blueprint commit `06aa96295` and the docs commit `d5643c78e`. At 19:41Z it handed off `handoff/r10-sav-wood-heat` at `a94e4dc33` with its own body (`handoff-body` `f2c9bdb09`). The orchestrator merged that into the PR (`a25821255`).
- `a94e4dc33` contains this seat's last head `2f88732c3`, so no code of this seat is missing from the handoff.
- This seat did not push `handoff/` and did not run `body_push.sh`. Either would move a PR head that the handoff froze and replace the other seat's body (fixer.md step 6).

Evidence this seat holds at `2f88732c3` (the full body is `SEAT-ROUND2-PR-BODY.md` beside this file):
- 16 mutants, each killed, null control green (entities, features, card.mjs, card_browser.mjs). They include two blueprint mutants: B1 (guard dropped) and B2 (note line dropped), each killed by the `entities.py` blueprint check.
- Scoped gate `MODE: SCOPED -- 28 script(s) run`, rc 0, with `env_drift --all`: NO UNCLAIMED DRIFT and NO STALE FIXTURE over 56 scenarios.
- `tools/pr/prepr.sh` with that body at `2f88732c3`: `PRE-PR ... rc=0`. `carry_audit`: 4 routed, 0 unrouted.
- The class rule widened to the whole tree (52 lines; my first draft covered `custom_components/` only and missed the blueprint).
- The finder's census and the wood-plant arm print identical output at every head measured.
