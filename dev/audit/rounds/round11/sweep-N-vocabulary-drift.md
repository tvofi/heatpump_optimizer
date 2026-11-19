# Class sweep: N-vocabulary-drift (round 11, PLAN phase D)

Status in `bugclasses.json`: `barriered` for the roster stage/size seam (roster_lib.STAGE_KIND, both self-tests in governance.yml). This round's two findings sit outside that barrier, so the class is reported **not barriered** for the seams below.

## Enumerator
`python3 dev/audit/rounds/round11/D14/vocab_seams.py` lists every stage / verdict-class word literal held outside its registry (roster_lib.STAGE_KIND; web-fix-wave.js VERDICT_CLASSES): 7 seams, 2 carrying unregistered words. The body-vocabulary seam of D13-s2-02 is measured by its own harness `D13/s2/friction_keys.mjs`.

- Positive control: bus.sh MECHANICAL_CLASSES reports 9 words absent from VERDICT_CLASSES, the figure in D13-s2-01; friction_keys.mjs reproduces 69/174 (D13-s2-02).
- Null control: `--root $(mktemp -d)` returns registries of size 0 and 0 instances.
- Perturbation: `--perturb tools/audit/seat/sweep_gantt.py:CLOSED_STAGES:closed` moves instances 2 -> 3.

## Disposition
| seam | disposition |
|---|---|
| web-fix-wave.js KNOWN_STAGES | **instance (beyond findings)**: roster_edit writes any of 18 registered stages; the wave reader knows 7 words and throws on `fixing`, `handoff`, `queued`, ... (14 registered words). Also holds `fix`/`merge`/`blocked`, which no writer can produce. |
| bus.sh MECHANICAL_CLASSES | instance, D13-s2-01's site |
| policy_lint.mjs frictionEntries / checkPrBody | instance, D13-s2-02's site |
| replan.py LIVE_STAGES, REVIEW_STAGES | guarded: every word in roster_lib.STAGE_KIND; roster_sync self-test classifies them |
| orchestrator_tick.py DEFERRED_STAGES, UNBLOCKABLE_STAGES | guarded: every word is registered |
| sweep_gantt.py CLOSED_STAGES | not applicable to this class: its words are registered, but it narrows roster_lib.CLOSED_STAGES (omits absorbed/refused/deferred). That is two definitions disagreeing, class I4 |
| roster stage/size writer (roster_edit) | guarded: roster_lib registry + governance.yml self-tests (existing barrier) |

Proposed barrier: derive KNOWN_STAGES and VERDICT_CLASSES from one registry (or have the self-test diff roster_lib.STAGES, bus.sh MECHANICAL_CLASSES and the wave literals), and make checkPrBody resolve a friction `<rule_id>` to a policy file.
