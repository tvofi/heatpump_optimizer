# P2b unit U9a (opus). Topic r10-ci-layout-p2-u9a

Handoff refs: code `refs/heads/handoff/r10-ci-layout-p2-u9a`, body `refs/heads/handoff-body/r10-ci-layout-p2-u9a` (via body_push.sh).

## Your unit's scope, verbatim from the plan's section 1 row (1011d6b2f:plans/ci-layout/EXECUTION.md)

| unit | files | prod / test lines (est.) | depends on | runs as | lands in |
|---|---|---|---|---|---|
| **U9a** seat readers | `merge_train.py` (`DISPATCH`, `PR_ONLY=()`, `tests / nightly-status`, A5 both directions with the platform cross-check, `RATE-LIMITED` never a pass); `orchestrator_tick.py` (`PR_ONLY`, req = `gate_required` ∪ {gate}); `proof_watch.py`; `ci-watch.sh` fixtures; `autofix_statuses.sh`; `merge_main_bot.py` PIN_CHAIN; `stamp.py` push-`gate` reader (B3); `ci_ratchet.py:177,185` re-key, with (c)'s exclusion kept | 400 / 250 | U0a names | cloud, opus (A5 is adversarial) | P2b |

## Unit specifics: U9a, the seat readers (adversarial)

Read DESIGN-P2 §9 (every reader's change), PLAN.md A5 and B3, and DESIGN-REVIEW's U9 rows. Build against the design's names: the umbrella's check names are `<stem> / <job>` plus `gate`, as in `tools/ci/gate.py` `REQUIRED` on main. Read them from that file, never from memory. If U0c's published names differ when you finish (`git ls-remote origin refs/heads/handoff/r10-ci-layout-p2-u0c`), re-key to them and say so.

Musts:
- **A5 in both directions**, with the platform cross-check: a reader that sees an old-layout head and one that sees a new-layout head. `RATE-LIMITED` is never read as a pass. Plant one of each.
- `stamp.py`'s push-`gate` reader (B3). The fallback that reads the `Tests` push run is the three-round fallback, so keep it isolated in its own function.
- The `ci_ratchet.py:177,185` re-key keeps the (c) exclusion. The `script_runs_per_push` rows of the arch pair must still count (carry 3; U5b moves the pair into `tests / arch-instrument`). Null: `script_runs_per_push == 54` on a replayed push run.
- `merge_train.py` / `orchestrator_tick.py`: req = `gate_required` ∪ {gate}, read from `tools/policy/fixtures/required-contexts.json`, never restated.
- `tests / nightly-status` keeps its reading (carry 9: do not touch the NEW/ABSENT window).
- Each changed self-test gets a perturbation; mutants go per-file in the mutants harness.

Seat-side readers live in `tools/audit/seat/` and `tools/pr/`, so they classify under existing closures. Run their self-tests and `selftest_wiring.py --check`.

## Common to every P2b unit seat (R10-CI-LAYOUT-P2, sub-PR P2b "cut-over"; Part of #2495)

You build ONE unit of P2b offline and return it on your handoff refs. You do NOT open a pull request, write a delivery row, push any `ci-probe/*` ref, dispatch any workflow, or post anything to GitHub. The local P2b coordinator seat cherry-picks every unit onto `ci-probe/all`, runs the live probes and opens P2b. Every GitHub write is the orchestrator's (decisions 0011 and 0013).

Binding sources. Read them from the refs, never from memory:
- Execution plan: `git fetch origin plan/ci-layout` (tip 1011d6b2f), then `git show 1011d6b2f:plans/ci-layout/EXECUTION.md`. Read §0 (approved decisions), §1 (your unit's row, quoted below), §3/§3.1 (the P2a interface contract, now merged) and §4.
- Approved design: tag `archive/probe/design-ci-rev4` = `1371a0a6`. Read `git show 1371a0a6:DESIGN-P2.md` §2 (umbrella layout, ci.yml sketch, prelude), §4 (gate semantics, events), §5 (permissions), §9 (readers), §10 (your unit's row and its null control), plus the `measure/rev/` tree. `measure/rev/unitcheck2.py` is the per-unit static null control. The round-5 review is tag `archive/probe/design-ci-review5` = `afc00bfe`.
- Plan addendum and its design review, at 1011d6b2f: `plans/ci-layout/PLAN.md` (A1-A6) and `plans/ci-layout/DESIGN-REVIEW.md` (B1-B9, §6 unit list). tvofi's 2026-10-19 ruling sets a 60 s floor on every GitHub poll, overriding any 30 s or 15 s figure.
- Roster group R10-CI-LAYOUT-P2 and all 9 carries: `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json | jq '.groups[]|select(.group=="R10-CI-LAYOUT-P2")'`.
- P2a as merged (a1633381a, #2622): `tools/ci/{ghapi,prelude,gate,sweep,alert_list,ruleset_cutover}.py`, `tools/audit/seat/{sweep_driver,ci_probe}.py`. Read #2622's "## Forward-carry" section from `git show 7d0570a70:BODY.md` (ref `handoff-body/r10-ci-layout-p2a`). Build against P2a's real interface. If you find a defect in P2a's merged code, fix it in your unit with a failing test first (fixer.md) and say so under "## P2a defect". Do not open a separate PR.
- Policy: CLAUDE.md, `dev/governance/roles/fixer.md`, `.claude/rules/*`.

Input refs:
- Base: fresh `origin/main`, which must contain P2a's merge `a1633381adadcf9e94c477bf651dfe94ba229c5c`. Check with `git merge-base --is-ancestor a1633381a origin/main`. Work in your own worktree under an ABSOLUTE scratch directory.
- Stack only on the extra refs your unit section names.

Rules:
- Follow fixer.md: failing test first, mutation proof, a null control for every quantified claim, and `python3 tests/structure.py` before the push.
- Set `PREPR_SKIP_CLOSURES=1` for any prepr or gate run (tvofi 2026-10-21). CI owns the closures. Run the scoped gate `PREPR_SKIP_CLOSURES=1 GATE_SCOPE=auto PYTHONPATH=tests/hastub ./tests/run.sh` under the gate lease (`gate-scoping.md`). Key on the MODE line, never the count.
- Spare the GitHub API. Your unit is offline: static maps, `unitcheck2.py static`, self-tests over fakes or saved JSON. Prefer git. Make at most a handful of reads, and only when unavoidable. Stop on any 403 or 429 and report it; do not retry.
- No Claude Code footers, no Co-Authored-By or Claude-Session trailers, and no claude.ai session links in any commit message, body or file.
- Workflow files: edit ONLY the ones your unit owns. Do not add `instrument-self-tests` steps to `governance.yml` unless you own `governance.yml`. List any wiring line you need under "## Wiring" and the coordinator adds it. Edit `tests/entities.py` only where your unit row names entities pins.
- Classify each new file you add in `tests/closure.py`, one line each (a measured closure, or `INERT`). Otherwise `tests/entities.py` fails with "these force the FULL suite when touched".
- Self-test hygiene (carry 6):
  - Mutants go in `dev/audit/harnesses/r10_seat_selftests_mutants.py` with per-file ids, placed inside the instrument's own block.
  - Git repositories are built only through `tests/throwaway_git.py`; run `python3 tests/throwaway_git.py --check`.
  - Register any new push site in `PUSHERS` (`tools/audit/seat/ref_privacy.py`).
  - Run `python3 -I tools/audit/seat/tmp_paths.py --check`.
- After any merge of origin/main, run `python3 -I tools/audit/seat/selftest_wiring.py --check` and expect `N self-testing, N wired, 0 unwired`, rc 0 (carry 2). An unwired self-test you add goes under "## Wiring".
- Do not change `nightly.yml`'s schedule (carry 9).
- Never touch VERSION, the manifest version or the RELEASE_NOTES heading. Never re-record a value-bearing golden fixture.
- Run `harness_headers` in the run.sh form (`PYTHONPATH=tests/hastub`), not under `-I`, which cannot import the stub.
- Bound: about 400 production lines. A unit that cannot be sound within it stops and says so in its body (fixer.md step 17); it does not grow.

Return signal:
- Before the push, `git log origin/main..HEAD` must hold only your commits, with no merge of a roster branch.
- Push the code head to `refs/heads/handoff/<topic>` (topic below) with `git push origin HEAD:refs/heads/handoff/<topic>`.
- Push the body with `bash tools/audit/seat/body_push.sh <topic> <body.md>`.
- That handoff push is the return signal; the coordinator watches for it. Your final message is RESULT / CHECKS-RUN / UNCERTAINTIES / ESCALATE.

Body headings, all required:
- "## Unit": which unit, its files, and line counts from `git diff --stat origin/main...HEAD`.
- "## Interface": what you export or consume, with exact names: check names, inputs, outputs.
- "## Static map": your `unitcheck2.py static` map and its rc against current main.
- "## Controls": each plant, null and mutant, with the command and its output.
- "## Live checks owed": the live half the coordinator must run (design §10), exactly.
- "## Wiring": workflow or entities lines you need someone else to add, or "none".
- "## Red checks": one line for each check red on main's ancestry. pr-contract refuses a body that leaves one out.
