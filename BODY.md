# R10-FLOW-MQ-PROBE: blocked, live probe not run

Result body (no code head: `handoff/r10-flow-mq-probe` was not pushed). Base `dfcd8d9be1dab28cfe52f684764befd1e19291de` (origin/main at 2026-10-25T18:13:18+01:00).

## Verdict

**Blocked: this seat cannot run the probe the brief asks for.** No merge-queue measurement was taken, so this body records no reports-on-`merge_group` result for any context in either arm. The adopt-or-decline recommendations owed by carry [2] for R10-FLOW-RECORD-PITCH, R10-FLY-ROW-HEAD-CARRY, R10-FLY-CARRY-DOC-CONTEXT, R10-TRAIN-OVERLAP-GRADE and part (a) of R10-FLOW-BODY-ONLY are **not given**: each depends on the measurement. The held groups stay held.

## Why it is blocked

Two separate reasons. Either one would be enough to stop the probe:

1. **No means.** The probe needs three things: a ruleset with a `merge_queue` rule on a probe branch, a PR into that branch, and an enqueue. Creating the ruleset takes repository-admin REST access (`POST /repos/tvofi/heatpump_optimizer/rulesets`). This seat's `GH_TOKEN` fails `gh auth status` ("The token in GH_TOKEN is invalid"). The GitHub MCP tools available to the seat have no rulesets endpoint. HANDOVER also records that the old admin token returns 401.
2. **Out of seat scope.** The seat prompt says: "Never write to any branch except your return refs" and "open no pull request". The probe needs a throwaway branch, a PR and a ruleset, so all three are writes the prompt forbids. Following "never work around a refusal", I stopped here and did not look for a route around it.

The only write this seat made besides this body was its pool claim, `claim/s6/r10-flow-mq-probe`.

## What the live probe must check (static reading, not measured)

These notes come from reading the tree at the base above. They are for whoever runs the probe with admin means, and none of them stands in for the measurement.

- The live required set of `main-protect-checks` (23698884), as recorded in `tools/policy/fixtures/required-contexts.json`, is `gate` alone. `ci.yml` triggers on `merge_group: [checks_requested]` and has no branch filter. Its `gate` job is `if: !cancelled()`, so statically `gate` should report on a queue commit for any branch with a `merge_queue` rule. The probe must confirm this in both arms: a passing PR, and a PR made red on purpose. HANDOVER's trap applies: a required context that never reports blocks every merge.
- On `merge_group`, `prelude.derive` returns `kind=code`, the PR number parsed from `gh-readonly-queue/<branch>/pr-N-<sha>`, and the base with `refs/heads/` stripped. `workset("code", pr)` is all eight units (CODE_UNITS + BODY_UNITS). `gate.py` then requires event class `pr`, or `pr-cc` when the three-dot diff reaches `custom_components/`. So the probe has to read all 22 `gate_required` names on the queue run, not only `gate`.
- `ci.yml`'s `run-name` writes `pr=- base=-` on `merge_group`. `gate.py` matches other runs by title (pr, base), so a queue run can only count its own jobs as sources. That is intended (one run per queue head), but if the queue re-runs a group, the re-run starts a new run, and the probe should check that it does not defer or fail on "no run at this head judged base".
- `tests.yml`'s guard refuses a queue commit with no second parent. The probe ruleset's `merge_queue` rule must set `merge_method: MERGE` (decision 0010). A probe with SQUASH or REBASE would read red for that reason, not because the queue fails.
- `main-protect-checks` was not touched, per the brief.

## What unblocks it

Pick one, the owner's call:

- (a) The owner, or a seat given a working admin token and explicit permission to write a probe branch, a probe ruleset and a probe PR, runs the probe as briefed and deletes the ruleset afterwards (one DELETE, #1300).
- (b) The orchestrator re-dispatches this group to a seat with those means.

Either way, the after-edges on the held groups (carry [2]) stay as they are until the measurement exists.

## Figures

- `gh auth status` at this seat: `X Failed to log in to github.com using token (GH_TOKEN)`. A null control is not applicable, since the command prints a success line when the token is valid.
- Required contexts: read from the recorded fixture `tools/policy/fixtures/required-contexts.json` at the base, not from the live ruleset, which this seat could not read. `contexts` = `["gate"]`.
