Roster for round 10, batch 21, at the roster tip `94d14569ea32889e228c54fc082c62d968f254e0`: the 166 roster commits on `handoff/audit-r10-roster` after `c8d51c464e84d36732855f21f962287d9b1405f7` (the roster head of batch 20, #2861), counted by kind under Figures. They are 163 `roster_edit.py` ops and 3 `roster_sync.py` commits: 153 `drop-carry` (151 provenance drops from 68 done groups, plus 2 from R10-RCA-ORCH-CONTINUITY), 7 `append-carry`, 3 `set-resume`. Part of #201. It closes nothing by keyword and leaves #201 open.

**Merge order: after #2861 (batch 20), which has merged** as `ca877f55951351a783c52180b8d1ffb6fdad5efe`. Batch 20's roster head `c8d51c464e84d36732855f21f962287d9b1405f7` is the merge base of main and this head, so the three-dot diff carries only this batch's commits; no merge of main into the roster branch was needed. The three triage batch 34 ops (R10-FLOW-BODY-ONLY and R10-996-RUNNER-CLAIMS carries, R10-RECORD-HOLD-APPROVE group) are held until `dev/programme/triage/s6-batch34.md` is on main and are not in this batch.

### The 151 provenance drops

Each commit is `roster: drop brief carry of <GROUP> (brief carry consumed by #<PR>)`, one `drop-carry --match` op per carry. The rule that confirmed each drop (orchestrator class A, 2026-10-26, re-checked for this body over all 151 commits): the dropped text, whitespace-normalised, is one of the carries the group held at the first roster revision that contains the group, so it is the brief's own carry and not a later forward-carry; the group is at `resume.stage` `done` at the drop commit; and `Merge pull request #<PR>` is on origin/main. Exactly one carry left the group in each commit. The check printed `drops 151 groups 68 bad 0`. The other 221 carries the done groups still hold (the classes this rule does not cover) stay for a per-carry audit and are not touched here.

By group (PR, drops): R10-ADVISOR (#2572, 2); R10-ARCH-DOCS-FIRST (#2609, 2); R10-ARCHSCORE-COVERAGE (#2293, 2); R10-BRIEFS-FOLD (#2631, 2); R10-CURRENCY (#2620, 1); R10-DEAD-RATE-LIMIT (#2448, 2); R10-DEEPLINK (#2452, 1); R10-DIAG-REPLAY (#2399, 3); R10-FAHRENHEIT (#2285, 3); R10-FEEDS (#2336, 3); R10-FLOW-ANDON (#2582, 5); R10-FLOW-ARCH-PLANNER (#2633, 3); R10-FLOW-AUTOTRAIN (#2780, 4); R10-FLOW-BODY-PATCH (#2578, 5); R10-FLOW-DESIGN-POLICY (#2586, 2); R10-FLOW-DISPATCH (#2577, 5); R10-FLOW-MAIN-GATE (#2584, 4); R10-FLOW-PULL (#2628, 2); R10-FLOW-RECHAIN (#2576, 3); R10-FLOW-RECORD-PITCH (#2836, 4); R10-FLOW-RELAY-HOLD (#2580, 3); R10-FLOW-TOOLKIT-MEASURE (#2645, 5); R10-FLOW-YIELD-PROBE (#2579, 2); R10-FLY-CIPREDICT-LAYOUT (#2707, 1); R10-FLY-CLOUD-SETUP-TOOLCHAIN (#2709, 3); R10-FLY-ENVMATRIX-NOREMOTE (#2708, 1); R10-FLY-NO-FOOTERS-EMITTERS (#2652, 1); R10-FLY-YIELD-GUARD (#2765, 2); R10-FREQ-DEFROST (#2527, 1); R10-GATE-YIELD (#2275, 1); R10-I1 (#2284, 2); R10-I5-DOCS (#2521, 1); R10-INPUT-STALENESS (#2683, 2); R10-LEAF-IMPORTS (#2371, 2); R10-LEARNER-ETA (#2775, 1); R10-LIVESTATE (#2675, 5); R10-LOOP-CPU (#2632, 2); R10-MERGE-SUBJECT-HARDEN (#2697, 2); R10-MUTATION-ANCHOR (#2766, 1); R10-NIGHT-FOLDS (#2563, 3); R10-PARAMS-OWNER (#2817, 3); R10-POLICY-LINT-FAMILY (#2669, 2); R10-POLICY-LINT-STATS (#2294, 1); R10-PRE-EDIT-HOOK (#2323, 1); R10-PREPR-CAP (#2528, 1); R10-RATIO-ANCHOR (#2698, 3); R10-RATIO-SITES (#2347, 3); R10-REGISTRY-LEAK (#2329, 1); R10-REPLAY-LANE (#2514, 2); R10-REPLAY-LOOPNORM (#2339, 1); R10-REPLAY-SCOPED (#2692, 1); R10-SAV-BASELINE (#2411, 2); R10-SAV-REASONS (#2511, 2); R10-SCORES (#2647, 3); R10-SENSOR-PAYLOAD (#2379, 2); R10-SERVICES-GUARD (#2290, 1); R10-SOLVER (#2612, 3); R10-STALE-PATHS (#2344, 2); R10-STAMP (#2485, 1); R10-STORE (#2375, 2); R10-STRUCTURE-ALIAS (#2711, 1); R10-STRUCTURE-BLIND (#2340, 2); R10-TARIFF (#2282, 2); R10-TICK-DRIVERS (#2390, 2); R10-TICK-ORCH (#2360, 1); R10-TRUST-RELATIVE (#2435, 2); R10-UX-SETUP (#2346, 3); R10-VENT-DETECTOR (#2391, 2). The command under Figures enumerates every commit and its carry.

### The other twelve ops, oldest first

- `f082177a4d888fecfde3647390efe681bc34b67a` append-carry R10-ORCH-BEATD and `503685300ee40303855e72f0e02f871990ee3c1b` drop-carry R10-RCA-ORCH-CONTINUITY carry 0: the same text rerouted from the done group to the live one, appended first.
- `7a56d6b3f15d7d59d591936e1b3490deec77083d` drop-carry R10-RCA-ORCH-CONTINUITY carry 1 (from #2586): decision 0012 was revoked by decision 0014 on 2026-10-21 and the group is done, so no live brief carries the line. R10-RCA-ORCH-CONTINUITY now holds zero carries.
- `7ba5f3b3d0cae51e072cdbf1379494abc1a28b27` set-resume R10-FLOW-JIDOKA note and `f236106e3c3fbce0ceadf0e2fa0c22b3d931aed7` set-resume R10-FLY-ROW-HEAD-CARRY note, both to "Decision 0012 (moratorium) was revoked by decision 0014 on 2026-10-21; the brief's 0012 reference binds nothing." Each replaced the previous note (R10-FLOW-JIDOKA's was `rca: topic r10-rca-body-check-parity`; R10-FLY-ROW-HEAD-CARRY's named its fly-in registration under mandate 6319294694).
- `630146b9a696ebc836734bbb536c2e12a82e1e3a` append-carry R10-FLY-GH-READ-RETRY: the orchestrator's finding from triage's #2859 diagnosis, that `tools/ci/ghapi.py` `get()` retries a 5xx status but not a transport `IncompleteRead`.
- `dd415af568d7b4833222c499079f2f0e46f69e1b` set-resume R10-996-RUNNER-CLAIMS note: "#2843 merged bb8addd8; next PR = P196 per-scenario claimnotes arm (carry held for triage batch 34)".
- `32d783569a2a423786eea34b12cde5f47ce08bd7` and `c39e46bc6e47dc2784f57a5f0650e9b4d5796031` append-carry R10-ARCH-SHAPES-CLASSIFIER: two findings from #2843 (R10-996-RUNNER-CLAIMS, merged `bb8addd8`) on the `tests/golden/claimed_drift.txt` header and the shape claim form.
- `d040c3da9f2a01f67ca4e6d00e4e530c0c0dca79` append-carry R10-ORCH-BEATD: recurrence evidence of 2026-10-26 (two orchestrator record loops died unnoticed), routed by the orchestrator after triage deferred P197 to this group.
- `cb64633fb5e8bc410aa0c4a3568bc00e16c870e4` append-carry R10-FLOW-DESIGN-STAGES: triage batch 33's P194 ruling, applied once `dev/programme/triage/s6-batch33.md` reached main with #2859 (`10f459f185ba204c1af2bb67cc93e729e545b8d7`).
- `94d14569ea32889e228c54fc082c62d968f254e0` append-carry R10-ERREXIT-COUNTERMEASURES: a finding from #2849's round-2 fix review (at `ae74761359af1a7864eb4795e13ddb4694337a12`), not proposal-sourced.

Every append was read back with `roster_queue.py readback` as an exact single match at the last index, at its full length.

### The three `roster_sync.py` commits

These were derived from pull requests by the tool, not authored by a seat op. `666bf5d9dd9997f95f59c30d232ecde9d5553bbd` set `resume` stage, pr or commit on R10-HEAT-METER, R10-MERGE-SUBJECT-HARDEN (to done), R10-FLOW-JIDOKA, R10-FLY-OPENPR-ATOMIC, R10-FLY-DEPGRAPH-STALE (to done), R10-ADVISOR-RESIDUE, R10-996-RUNNER-CLAIMS and R10-RCA-RATELIMIT-RECUR, and added four carries to R10-MERGE-SUBJECT-CASEARM (3 to 7). `1ec8c7259144db1c77a27a1f7bfa025f61fdbd1a` set R10-996-RUNNER-CLAIMS to done and added two carries to R10-ARCH-SHAPES-CLASSIFIER. `57efa020ed0be1d9f9f3d711a8f4d6d92033e435` set R10-RCA-RATELIMIT-RECUR to done and added three carries to R10-RECORD-API-O1 (3 to 6).

## Head

The authored head is `94d14569ea32889e228c54fc082c62d968f254e0`, the tip of `handoff/audit-r10-roster`. Its merge base with origin/main (`ca877f55951351a783c52180b8d1ffb6fdad5efe` at this reading) is `c8d51c464e84d36732855f21f962287d9b1405f7`. `git merge-tree --write-tree ca877f55951351a783c52180b8d1ffb6fdad5efe 94d14569ea32889e228c54fc082c62d968f254e0` prints the tree `5241e1a66a9cda31ce995effed0405505c546848` and no conflict. The only file these ops touch is `dev/programme/rosters/wave-r10-groups.json`, the pull request's own delivery row apart. `git diff --stat ca877f55951351a783c52180b8d1ffb6fdad5efe...94d14569ea32889e228c54fc082c62d968f254e0` prints:

```
 dev/programme/rosters/wave-r10-groups.json | 324 ++++++++---------------------
 1 file changed, 81 insertions(+), 243 deletions(-)
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

The blob hashes come from `git show <ref>:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin`: origin/main (which now holds batch 20) prints `fb90f3cffe328f5c7ab765ab1d10b22dc0b9202a`, the same blob as batch 20's head, and this head prints `53414799bdd5549578172f1c101f0ecd4807aed4`. A script that loads both files as JSON and keys groups by `group` printed `groups 199 199 added [] removed []` and `changed 84`. The 84 are exactly the groups the 166 commits name: the 68 provenance groups (each `carry` only, except R10-MERGE-SUBJECT-HARDEN, whose `resume` stage and commit `roster_sync.py` also moved), R10-RCA-ORCH-CONTINUITY (2 to 0), the five append targets (R10-ORCH-BEATD 26 to 28, R10-FLY-GH-READ-RETRY 6 to 7, R10-ARCH-SHAPES-CLASSIFIER 0 to 4, R10-FLOW-DESIGN-STAGES 19 to 20, R10-ERREXIT-COUNTERMEASURES 4 to 5), the three set-resume targets, and the seven groups only `roster_sync.py` moved (R10-HEAT-METER, R10-FLY-OPENPR-ATOMIC, R10-FLY-DEPGRAPH-STALE, R10-ADVISOR-RESIDUE, R10-MERGE-SUBJECT-CASEARM, R10-RCA-RATELIMIT-RECUR, R10-RECORD-API-O1). No other group moved.

`node tools/policy/brief_lint.mjs` from a fresh origin/main checkout (`10f459f185ba204c1af2bb67cc93e729e545b8d7`) with this head's roster file as its argument, as `roster_edit.py`'s lint gate runs it, exited 0 with `TOTAL: 0 error(s) across 1 file(s)` and no `ERROR` line. On `git archive` extracts of origin/main and of the merged tree, each given `git init`, `git add -A` and one commit: with the roster file as argument both exit 0 with `TOTAL: 0 error(s) across 1 file(s)`; with no argument both exit 1 with `TOTAL: 10 error(s) across 48 file(s)` and an identical error set (the extract lacks files under `dev/governance/config/` and `dev/audit/config/` that the carry files cite), so the delta is zero. The no-argument run does not read `dev/programme/rosters/`.

## Figures

`git log --no-merges --format=%s c8d51c464e84d36732855f21f962287d9b1405f7..94d14569ea32889e228c54fc082c62d968f254e0 -- dev/programme/rosters/` prints the 166 commit subjects; piping it through `grep -c 'brief carry consumed by'` prints 151, through `grep -c '^roster_sync'` prints 3, through `grep -c 'append-carry'` prints 7, through `grep -c 'set-resume'` prints 3, and through `grep -c '^roster: drop carry'` prints 2.

`git log --no-merges --reverse --format='%h %s' c8d51c464e84d36732855f21f962287d9b1405f7..94d14569ea32889e228c54fc082c62d968f254e0 -- dev/programme/rosters/` enumerates every commit with its short SHA; `git show <sha>` on a provenance drop shows the one carry it removed.

The per-group counts and the 84 changed groups come from the script named under Null control.

## Red checks

Not read by this seat for this body; this pull request changes only the roster JSON and its delivery row. The orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
