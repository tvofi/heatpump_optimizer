# fixer-r11-ci-3885-queue-rest: two of four levers handed off; L4 and L3 not started

Question: re-dispatch L4 (record-branch stand-down, with carry 2) and L3 (W1 + W2) to a fresh fixer context? This seat's context passed fixer.md's rotation bound (~150 k for S/M) after L7 and L5. Second question for the same dispatch: may a cloud seat run `gh api` for `dev/audit/harnesses/ci3885_queue.py fetch` and `ci3885_light.py`? This container's harness rule allows `gh` for search only, so both handed-off bodies report their harness arms by applying the arm's rule to GitHub MCP `list_workflow_jobs` listings rather than by running the harness.

## Handed off (each branched from origin/main fd93aa3e9b)

- L7 failed-only re-runs: `handoff/r11-ci-3885-queue-l7` 030d07524c, body on `handoff-body/r11-ci-3885-queue-l7`. The body also re-checks L2 at the base: `sweep.py` `fresh` still dispatches when a code unit at the head is running or cancelled (`code_red` counts only completed `failure`). That is unmeasured here, and its instruction is already in `dev/programme/carries/carry-3885.json` carry 1.
- L5 refresh folded into cancel-superseded: `handoff/r11-ci-3885-queue-l5` 4f0c7af26b, body on `handoff-body/r11-ci-3885-queue-l5`.
- Both prepr runs: `PRE-PR: ... rc=0` (PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1). The bodies quote their `diff mutants` lines.

## L4: what the next seat starts from (read, not built)

- A record PR (`record/autofix`, #3903) changes only `dev/programme/delivery/<n>.md` rows of other PRs. That list is already `light` (`prelude.light`), so `stand_down` already drops LIGHT_LANES. What it still pays is the machinery lanes. CI run 45907701622 (2026-11-26, attempt 1) spent 57.1 runner-min over its jobs: governance / instrument-self-tests 19.0, governance / env-matrix 7.4, tests / fast 4.6 + 2.1, tests / closures 3.8, policy-docs 2.8, briefs 2.4, arch-instrument 1.9, mutation 1.4, and the rest under 1.5 each.
- `prelude.machinery` is False only for an all-product list, and a delivery row is not product. `lane_reads_delivery.recording.json` records that closures, env-matrix and instrument-self-tests READ delivery rows (policy_lint's tree-wide grep). Only arch-instrument is row-blind, and `machinery_rowblind` drops only the PR's own row, never other PRs' rows. So "every lane whose closure it cannot reach" is a per-lane question, and the design's "the fixer reads tests/closures.json" has to be answered against that recording, not assumed.
- L4 and L3 both touch `tools/ci/prelude.py`. L3 goes after L4 and merges L4's ref if L4 is not on main yet.
