Fix review: blocked bd7eb6b2cd0336a66c5f96751565c92357385cf2 class-open: roster-library dirs misses dev/governance/dimensions; merged, main keeps 1 drift refusal
bus-nonce: 4bfc1aa85837065119377ad3ad58596c

Delta review, round 2 (prior verdict: merge 00d07210bd41a89c38f477f60490b3be091d4f72).

RESULT delta: `review_carry.py 00d07210 bd7eb6b2` prints FRESH-REVIEW only because #3801 landed the four `survivor_triage/currency.py` entries on main; the own diff at bd7eb6b2 is the 00d07210 diff less those four lines, and `tools/ci/selftest_closures.json` is the same blob (6ac03a263c) at both heads. Both main merges (dc00fe13, bd7eb6b2) have an empty remerge-diff. The reviewed change itself is unchanged and still correct for what it covers.

RESULT base red: `governance / instrument-self-tests` is failure at merge base e893cd3d (job 135716032632) and at main 698eeeb2 (job 136092952034), both on step "Refuse a self-test read set the committed table misses", both `selftest_scope check: 127 gated step(s), 4 refusal(s)`: policy-lint-mutants, dependency-graph-census, prepr (round11 dirs) and roster-library (`dirs misses ['dev/governance/dimensions']`).

RESULT head green is vacuous: `merge_train.py introduced bd7eb6b2` prints `introduced: 0 ... head governance / instrument-self-tests: success`, but at the head (job 135729405064) the drift step is `skipped` (`if: env.SELFTEST_TRACE != ''`; a pull request runs only `static_check`). The head's success does not measure the drift check.

RESULT drift emulation (evidence `drift_emulate.py`, `selftest_scope.drift(table, steps-of-artifact, workflow_steps)` against main 698eeeb2's `selftest-closures` artifact, run 44677469341): main's table gives 4 refusals, the same four lines CI printed (null control: the emulation reproduces CI exactly). This head's table gives 1 refusal: `UNDER-SCOPED step roster-library: dirs misses ['dev/governance/dimensions']`.

Block: the PR's purpose is to turn main's `instrument-self-tests` green, and merged it leaves the step red. The roster-library miss entered with #3739 (6b230c6dd0 adds `dev/governance/dimensions/DX0.md`; merged at e893cd3d, this PR's merge base), after the 7ae05284d5 artifact the table was taken from. Remedy: re-take the table from main's latest `selftest-closures` artifact (run 44677469341 or newer), which adds `dev/governance/dimensions` to roster-library's `dirs`, and re-run the emulation to 0 refusals. Carry: dismissed: this PR's own remedy, owed at its next head

Note: body-stale: `## Mutation proof` and `## Figures` state 0 refusals at this head; against main 698eeeb2's measurement it is 1. Carry: dismissed: the fixer re-takes the body with the next head
Note: instrument: a pull request touching only `tools/ci/selftest_closures.json` cannot show its drift check green before merge (drift step is main-only), so a table re-record's only pre-merge evidence is an emulation like this one. Carry: dismissed: by design per `static_check`'s docstring ("the drift check is main's"); an emulation against main's newest artifact is the control
