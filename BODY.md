Mechanises the two design steps of decision 0014 (R10-FLOW-DESIGN-STAGES, #2718, #2800): roster stages `design` and `design-review` (derivable, not live claims: no pull request exists at either step, so no read rewrites them and the planner's LIVE view stays its own four words); `bus.sh push-design` and `push-design-verdict` writing `design/<group>` (design.md) and `design-verdict/<group>` (verdict.md), the verdict refused unless it names the current design tip; cloud roles `designer` (may push only `design/<group>`, opens no pull request) and `design-reviewer` (only `design-verdict/<group>`), each saying so in its own text, pinned to the base SHA and, for the reviewer, the design tip; a fixer dispatch for an L/XL group refused unless the verdict approves the current design tip or `--design-exempt <reason>` is given; a `DESIGN OWED:` tick line. Roster issues: #2718, #2800 (not closed by this body; the preflight lists none as intended).

Design choices: eligibility is `roster_lib.needs_design` (size L/XL), shared by dispatch and tick; the roster has no "design on record" marker, so the exemption is an explicit dispatch flag with a stated reason, not a new roster field. The topic is the roster group id, the spelling the existing `design/<group>` refs and `design_builds` already use.

## Head

1322fcf5e71850044dda6fcd7fdcc8b2186867cc

## Mutation proof

Predicate mutants, each restored after: `if not design_approved(...)` -> `if False` in cloud_dispatch.py: FAIL "a fixer for an L group with no design ref is refused", "a fixer is still refused with a design and no verdict", "a fixer is refused on a `revise` verdict", "a fixer is refused on an approval of a design that has since moved". bus.sh `[ "$tip" = "$sha" ] || die` -> `true || die`: FAIL "a verdict naming a sha other than the design tip is refused". orchestrator_tick.py dropping `not rl.needs_design(g)`: FAIL "DESIGN OWED: an L group ...", "DESIGN OWED: null controls ...". Run with each instrument's `--self-test`; no unpinned `custom_components/` site is added.

## Null control

At the base, `cloud_dispatch.py --role designer` is refused ("role must be one of"), `roster_edit.py set-stage <g> design` is refused as unclassified, and the tick prints no `DESIGN OWED` line. In the self-tests the null controls are an S group, a group with a design ref, an undispatched predecessor, and a fixer dispatched once the verdict approves the current tip.

## Figures

- `python3 tools/audit/seat/bus.sh --self-test` (bash): 110 checks, 0 failed at 1322fcf5e71850044dda6fcd7fdcc8b2186867cc
- `python3 tools/audit/seat/cloud_dispatch.py --self-test`: 100 checks, 0 failed
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 218 checks, 0 failed
- `python3 tools/audit/seat/roster_edit.py --self-test`: 125 checks, 0 failed
- `python3 tests/entities.py`: ALL 2484 ENTITY CHECKS PASSED; `python3 tests/structure.py`: STRUCTURE RATCHET PASSED; `bash tools/pr/prepr.sh`: no refusal in the steps run

## Red checks

none attributable to this diff. One pre-existing break, found not fixed: `dev/audit/harnesses/r10_flow_dispatch_mutants.py` aborts with "wait-line-dropped's pattern occurs 0 times" at the base too (its pattern `"and no timeout. " + WAIT_LINE)` needs a quote that cloud_dispatch.py's multi-line string does not have); this diff keeps its other patterns (`cli-nonce-dropped`, `cli-overlay-dropped`) matching.

## Forward-carry

Per-carry disposition, by roster number:

- Carry 1: build beside R10-FLOW-DESIGN-POLICY, which is done; the templates name its contracts by path. Done. Carry: dismissed: done in this pull request, evidenced above.
- Carry 2: pre-study K19 read as the brief's source; no change owed. Done. Carry: dismissed: done in this pull request, evidenced above.
- Carry 3: self-test hygiene held: no new S-number mutant, no hand-built git init (\`tests/throwaway_git.py --check\` 0 refused), no new push site, Red checks answered. Done. Carry: dismissed: done in this pull request, evidenced above.
- Carry 4: cloud-payload stub (P-A) is not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 5: payload-echo stub pinning the pushed commit, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 6: handoff-wip step pushes, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 7: the fixer prompt's handoff-wip last step, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 8: the model-per-role table in cloud_dispatch.py, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 9: the stub first, ahead of the design stages: this diff is the design stages only; the stub stays owed. Carry: R10-FLOW-DESIGN-STAGES
- Carry 10: cloud-setup --check stop behaviour in the rendered setup line, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 11: the cloud seat pool (R10-FLY-POOL-INSTRUMENT), another group. Carry: R10-FLOW-DESIGN-STAGES
- Carry 12: the reviewer pool arm, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 13: verify the handoff over the current main, a fixer-prompt change not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 14: one ending CI waiter in the reviewer prompt, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 15: the DESIGN OWED line prints no age and no CP mark yet; it is a level line every pass until a design ref exists. Carry: R10-FLOW-DESIGN-STAGES
- Carry 16: rendering a group's carries in its dispatch, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 17: the fire-wait mode, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 18: pinning the seat git identity in the setup line, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 19: pool stale-claim predicate, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 20: pool drop verb, not in this diff. Carry: R10-FLOW-DESIGN-STAGES
- Carry 21: done. The (word, kind) rows `design` and `design-review` are in STAGE_KIND as derivable; the close rule is derive()'s existing derivable rule (a merge closes to done), pinned by a new roster_sync arm; roster_lib and roster_edit carry an arm each. The unclassified-word null control is the registry self-test's own. Carry: dismissed: done in this pull request, evidenced above.
- Carry 22: the same as carry 21, done. Carry: dismissed: done in this pull request, evidenced above.

The orchestrator's by-hand runs: the stages and refs now exist, so the contracts can name `bus.sh push-design` and `push-design-verdict`. Also found, not fixed: `dev/audit/harnesses/r10_flow_dispatch_mutants.py`'s `wait-line-dropped` pattern matches nothing at the base. Carry: R10-FLOW-DESIGN-STAGES

## Friction

none
