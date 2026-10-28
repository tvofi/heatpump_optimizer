## Head

d4b017368d585900b2705a39821cc78681fb4217

## Red checks

`governance / wave-script` was red at fbbd3e61, the round-1 head. `check-wave-script.mjs` refused the brief because it now numbered a step `M5` that `rotation.json` did not carry. This head fixes it by adding `D11.M5` to `rotation.json` and `scopes.json`. Cheaper detector: run `node tools/policy/check-wave-script.mjs` locally whenever a diff touches `dev/governance/dimensions/`; standing cost is one local run per such diff. `tools/pr/prepr.sh` does not run it for a brief-only diff, which is how the red got through. Wiring it into prepr for dimension-brief diffs is a mechanisation proposal for `proposal-triage.md`. Carry: proposal-triage

## Forward-carry

`none`

## Friction

`none`
