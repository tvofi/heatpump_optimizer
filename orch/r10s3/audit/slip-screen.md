# Slip screen — recorded asks with no delivery, last 500 merged PRs

Read-only seat. Window, method, null control, verdicts, then the confirmed slips.

## Window covered

The 500 most recent first-parent merges on `main` at #2489 (`990e90af9`): **PR #2489 merged
2026-10-20T15:28Z down to #1719 merged 2026-09-27T11:16Z**. Of that span, 496 are `Merge pull
request #N` commits whose bodies were screened in full (4.36 M characters); the rest of the
first-parent history in the span is record/squash commits that carry no PR body.

## Null control (mandatory) — 6 of 6 found as LANDED-ELSEWHERE

| ask | delivered by | proof |
|---|---|---|
| #1955 folds (a)–(d) | #2006 | body enumerates them; `project_planned_levels`, `CONF_FLOW_HEAT_C`/`mixing_valve.flow_setpoint` (optimizer.py:5302), `learner_unmetered` (coordinator.py:2601), `planned_draw_runs` all in tree |
| #2016 items 1–3 | #2024 | `flow_meter.py`, `const.py:1111 CONF_FLOW_METER_ENTITY`, options field, `measured_heat_output_kw` |
| #2016 item 4 | #2118 | `thermal_model.py:2632,2728 measured_heat_kw`; `dev/audit/harnesses/ux10_flow_into_model.py` |
| #2116 stale harness path | #2072 (`71f7a612a`) | CLAUDE.md:156 now says `dev/audit/harnesses/` |
| #2421 merge_pr self-test unwired | `ebc770b80` | governance.yml:550 runs `merge_pr.sh --self-test` |
| #2396 stale GITHUB_TOKEN sentence | `c084cc242` | ci-autofix.md:78 now says `pull_request` runs are held `action_required` |

The method finds a delivery when one exists; the exemplar's fold (e) is excluded from the counts.

## Counts per verdict

Hand-verified candidates: 12. **CONFIRMED-SLIP 5**, LANDED-ELSEWHERE 6 (the controls),
SUPERSEDED 0, UNPROVEN 1.

## CONFIRMED-SLIPs, in order of what they cost if left

### 1. #2393 — the no-indoor-sensor learner finding never reached D1/D2
Ask (verbatim, `pull/2393` Forward-carry): the heat-loss learner replays against
`ThermalState.room_temperature`'s 21.0 °C default on installs with no indoor entity, because
`_learning_frozen` deliberately does not freeze an unconfigured slot; "belongs to the D1 / D2
brief … named here for the orchestrator to route."
Search that would have found delivery: `grep -ni 'indoor|room_temperature|learner'` in
`dev/governance/dimensions/D1.md` and `D2.md`; the round-10 D1/D2 findings.
Returned: nothing — neither brief carries it, round-10 did not reproduce it, and the code is
unchanged (`coordinator.py:6385-6388` still says an unconfigured slot must not freeze).
Routing: carry into the not-started **R10-INPUT-STALENESS** group, or a new D1 group.

### 2. #1930 fold (e) — mutation-driver skipping, deferred and lost
Ask (`issues/1930`): "Option (e), skipping a driver on a mutant line it never executes, is
recorded as deferred: high risk, needs a 595-row replay."
Search: `tests/mutation_table.py` for any such skip; later PRs/issues naming a 595-row replay.
Returned: #1975 closed the issue with (a)–(d) and the two carried items only; the text survives
only in the **done** group R9-F10.16's brief (`wave-r9-groups.json:6684`) and PLAN-TABLE:167.
Routing: new roster group (one 595-row replay + mutation proof).

### 3. #1763 — the P2/I5 catch-all split deferred to round 10, which has no group for it
Ask (`pull/1763`): deferred to round 10 "with a detector-first pre-study".
Search: all 91 round-10 roster groups, round-10 pre-study/judge artifacts, `dev/` for
`catch-all|P2/I5|detector-first`.
Returned: only the round-9 plan row (`plan-2026-09-open-issues.md:99`) and record row 1762; no
group, no pre-study. Routing: new group, or an owner decision recorded as "not built".

### 4. #2114 — `tests/README.md:272` still cites the retired harness path
Ask: the kernel-gap instrument is cited at `tools/audit/harnesses/...`; the file is under
`dev/audit/harnesses/`; "flagged to the orchestrator for whoever owns the doc."
Search: read line 272 and `ls tools/audit/harnesses`; check the sibling fixes.
Returned: still stale; the directory does not exist; the CLAUDE.md/fixer.md siblings were fixed
by #2072. Routing: trivial — carry into **R10-I5-DOCS**.

### 5. #2408 — no fixture drives `policy_lint.mjs --record-known-bad`
Ask: "A pin belongs in `policy_lint_mutants.mjs`'s fixture drive … owed and stays open: that
file is outside this group, so the orchestrator dispatches it."
Search: `grep -rn 'record-known-bad' tools/policy/policy_lint_mutants.mjs tools/policy/fixtures`.
Returned: no match; the mutants file drives the loop/corpus lanes only. Routing: carry into
**R10-POLICY-LINT-FAMILY** (not-started).

## Depth and cost

Screened every window body for the seven deferral section names, `Carry:` markers and deferral
phrases (421 carry items from 246 PRs); 197 closing-keyword references resolved, 71 real issues
with bodies and comments read; 33 issues carry owner comments (owner comments added new asks only
in the #1955/#2016 pattern — #2016 landed); review threads fetched for the 5 candidates and 2
controls (0 reviewer asks); 798 delivery rows and all 91 roster `carry` arrays compared. Twelve
candidates were then verified against the tree at `#2489`; one was left UNPROVEN. Verification
depth therefore reached every CONFIRMED-SLIP through a tree or record check, not a keyword.

API honesty: `core.remaining` at start **4529/5000**; an early per-issue loop was stopped on the
orchestrator's instruction after about 150 calls, after which every fetch was batched (≤10 calls)
and all screening ran from the disk cache.

## Extractor

Not landed. It is a one-off body/carry screener whose value is this report; landing it would add a
tracked file that needs a closure/INERT classification and a PR, and the screen is the deliverable.
