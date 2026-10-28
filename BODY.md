R10-FLY-SWEEP-DEFAULTS (fly-in, size S). Owner ruling (tvofi, 2026-10-28): what the round-10 orchestrator added to its session sweep becomes the default in `tools/audit/seat/sweep_template.md`. Each addition cites its rule file or instrument by tree path.

- (0) The OWED arm now also says the sweep is not clean while `policy_reread_check.py` exits 1, until `--write-stamp` runs after the newest compaction.
- (4b) A record beat runs every sweep, not only after a merge: `state_docs.py --push --mirror`, then `tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}}`, then `tools/audit/seat/plan_page.py --plan {{plan_json}} --html {{plan_page}}`. Four new placeholders replace `plan_generator` and `plan_artifact`, which no step uses any more (the renderer refuses an unused one). The defaults (slots 10, seats 99) are in the table text, because the renderer has no default mechanism and refuses an unfilled value.
- (5) The tick board is read unfiltered: every `OWED`, `REVIEW OWED`, `DISPATCH:`, `OWNER FLAG:` and `DESIGN-BUILD:` line, none truncated, and each one gets an action that sweep.
- (4c) Every open PR is put in one bucket each sweep: in train, review out, fixer out, CI wait or owner-held.
- (4d) Queue priority. A group's critical-path standing comes from the roster's `critical` list (`roster_lib.py` `critical_path`), and the gate order from `tools/pr/gate_priority.py`. No `ci_priority.json` is tracked.
- (4e) Superseded-run cancel. The R10-FLY-CANCEL-SWEEP instrument is not on main at the base, so the step describes the `gh run list` / `gh run cancel` read instead, and points to `tools/pr/cancel_superseded.py` as the per-run in-workflow counterpart.
- (1) Seat caps replace `local_seat_cap`/`cloud_above_cap`. Reviewer model routing (record PR -> sonnet; design, code or architecture -> opus) goes in the same step.
- (3) The train flags `--overlap --approval-carry --skip-bad --free-holders --bot-prs --pre-flight --mandate {{mandate}}` are now the recommended default (`standing-merge.md`).

**Two points for the orchestrator to judge** (neither is fixed here):
1. Item 7's gate ("fewer than 3 handoffs without a PR and 6 to 10 open PRs") is not implemented by `pr_cap.py dispatch-gate`. That gate counts only roster `in-progress` groups against `HPO_WIP_CAP` (default 6) (`pr_cap.py` `dispatch_gate`). No rule file states the handoff or open-PR arms either. The template therefore attributes those numbers to the owner ruling of 2026-10-28 and says that `dispatch-gate` measures only the WIP arm. As a result, this usage guide carries a number that no rule file or instrument owns yet. The owner may want it in `orchestrator.md` section 5 and in `pr_cap.py`.
2. `standing-merge.md`'s instrument line lists `--overlap --bot-prs --approval-carry --skip-bad --free-holders`, without `--pre-flight` or `--mandate`. The template's default is a superset of it. The two do not contradict each other, but standing-merge.md is policy, so I left it unchanged.

Policy status: `printf '%s\n' tools/audit/seat/sweep_template.md tools/audit/seat/sweep_render.py | node tools/policy/policy_lint.mjs --corpus-filter` prints nothing (rc 0), so neither file is a policy path.

## Head

Measured at `d8b6a3a8df343a0c4dd512a340ad3594e8e52012`, cut from origin/main `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa` (the base given). The head has two commits: the change itself, then `tests/closures.json` from `python3 tools/pr/ci_predict.py --apply-inert`. That repaired the one red prepr step 6d predicted on the first commit: `INERT READS tests/entities.py: tools/audit/seat/sweep_render.py`. The scoped gate says `MODE: SCOPED -- 1 script(s) run, 32 scoped out` and names `tests/entities.py`, from `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`.

Environment: `tools/audit/seat/seat_venv.sh` failed with rc 2 in this container (`No download found for request: cpython-3.14.7-linux-x86_64-gnu`), and the ambient 3.11 cannot parse `tests/entities.py`. I therefore ran the scoped script in a scratch 3.13 venv built from `tests/requirements-ci.txt`. CI's 3.14 runner is still the authority.

## Mutation proof

The failing test came first. A new self-test arm, `the tracked template's sweep carries every round-10 default`, checks the sweep body against `sweep_render.DEFAULTS`: one fragment each for the replan beat, the plan-page beat, `REVIEW OWED`, `OWNER FLAG:`, `DESIGN-BUILD:` and the train flags. That covers items 2, 3 and 8.

- On the base template, with the new renderer, `python3 -I tools/audit/seat/sweep_render.py --self-test` exits 1 and fails `the tracked template's sweep carries every round-10 default`. It reports `missing: record beat: the replan, record beat: the plan page, tick board read unfiltered, tick board: owner flags, tick board: design builds, train flags`. It also fails the render null control, because the full overlay now carries `plan_slots`, which the base template does not declare.
- On the head, the self-test reports `24 checks, 0 failed` and exits 0.
- I mutated the head template one fragment at a time, ran the self-test after each, and restored the template:
  - The train flags reverted to `--bot-prs --approval-carry --pre-flight` failed the defaults arm with `missing: train flags`.
  - `replan.py --out` reduced to `replan.py` failed it with `missing: record beat: the replan`.
  - With `` `REVIEW OWED`, `` deleted, it failed with `missing: tick board read unfiltered`.
  - With `` `DESIGN-BUILD:` `` deleted, it failed with `missing: tick board: design builds`.

## Null control

- `a sweep carrying every default fragment misses none (null control)`: `defaults_missing` over the six fragments joined returns `[]`. The same text without the train flags returns exactly `["train flags"]`. Both are ok on the head.
- Every refusal arm that already existed still fires on the head: unfilled (omitted, empty, boolean, null, `{{`, newline), unknown (overlay key, sweep placeholder), unused, structure (repeated row, missing marker, non-object), host-path (literal, straddle) and citation. The head's self-test output lists them all as `ok`, together with their null controls (minimal render, overlay-supplied home, existing citation). The citation check also resolves every path the new steps cite: `tools/plan/replan.py`, `tools/audit/seat/plan_page.py`, `tools/audit/seat/pr_cap.py`, `tools/audit/seat/roster_lib.py`, `tools/pr/gate_priority.py`, `tools/pr/cancel_superseded.py`, `dev/governance/roles/standing-merge.md` and `dev/governance/roles/standing-tick.md`. It reports `the tracked template cites only paths that exist` ok.

## Figures

| figure | command | result |
|---|---|---|
| self-test, head | `python3 -I tools/audit/seat/sweep_render.py --self-test` | `24 checks, 0 failed`, rc 0 |
| self-test, base template + new renderer | same, with `sweep_template.md` stashed | `22 checks, 2 failed`, rc 1 |
| structure ratchet | `python3 tests/structure.py` | `STRUCTURE RATCHET PASSED`, rc 0 |
| scope | `tests/closure.py select` (above) | `MODE: SCOPED -- 1 script(s) run` (`tests/entities.py`) |
| scoped script | `PYTHONPATH=tests/hastub <py3.13 venv from tests/requirements-ci.txt> tests/entities.py` | `ALL 2467 ENTITY CHECKS PASSED`, rc 0 |
| prepr, first commit | `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` | rc 1: `REFUSE ci predict` (1 predicted closures red), repaired by `--apply-inert` |
| prepr, head | same | rc 0, `PRE-PR: d8b6a3a8df343a0c4dd512a340ad3594e8e52012 000000000000000000000` |

## Red checks

Locally, prepr step 6d predicted one red on `tests / closures` (`INERT READS`) on the first commit. Following `ci-autofix.md`, it was repaired before the handoff with `ci_predict.py --apply-inert` and is no longer predicted at the head. CI has not run.

## Forward-carry

n/a: no later stage's brief changes. The dispatch-gate gap, point 1 above, needs a ruling on where the 3-handoff and open-PR arms live (`orchestrator.md` section 5, `pr_cap.py`). That routing is the orchestrator's, and this seat writes only its return refs.

## Friction

none
