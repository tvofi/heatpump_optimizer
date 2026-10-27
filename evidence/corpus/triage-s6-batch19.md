Adds `dev/programme/triage/s6-batch19.md`: five rulings, P88-P92 (S6-V23 to S6-V27), under `dev/governance/roles/proposal-triage.md`, batched under tvofi's 4-5-per-PR rule of 2026-10-24. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the route the earlier batches took. (The title says P89-P92, but the file covers P88-P92. Retitling is the orchestrator's call.)

**Critical path:** P89 unblocks critical-path work. The R10-GATE-DEFER opener lost about 2 h to a carry check that reads only main's roster, and P89's carry asks R10-FLOW-ROSTER-FREEZE to cut that fix first.

Verdicts:
- **P88 (V23) ACCEPT -> R10-FLOW-RECORD-PITCH.** Record PRs open on a push only at 4 or more rowless merges, or once the oldest is 8 first-parent commits old (under `STALE_AFTER_COMMITS = 12`). Schedule and dispatch runs flush at any count, and the stamp dispatches first. The carry now states how this combines with the group's existing pitch bound: the count and age gate governs opening, the pitch governs automerge, and the 8-commit arm overrides the pitch. The orchestrator judged it compatible with trap 15 and queued it after the drain.
- **P89 (V24) ACCEPT -> R10-FLOW-ROSTER-FREEZE arm (b), cut first.** `carry_audit.py` also resolves destinations on the round's roster ref (`roster_lib.round_ref`), as `finding-propagation.md` already counts them. Candidate (a) is rejected.
- **P90 (V25) ACCEPT NARROWED -> R10-ORCH-LEDGER.** `ledger.review_owed` prints CARRY for a head that is a dispatched or verdicted head plus only main merges or only its own row, and FILTERED for record/autofix PRs. It does not filter by `triage/*` branch name.
- **P91 (V26) REJECT** of a new helper: `merge_train.latest_runs` and `failure_logs.sh` already reduce check-runs to the latest per name. The slips were hand reads, so the fix is a brief line, with no code.
- **P92 (V27) ACCEPT -> R10-FLOW-POSTMERGE.** The set-stage owed line resolves its group through `roster_lib.group_for_branch` or `resume.pr`, else `no-group`.

## Head

`3eb3223977b257f3c0dcf2940299c28eff967102`, on merge base `0810d5b8f30a81adbbc074640c6d95a1b358c5f6`. It is one commit on the reviewed head `b28cb6ac52dfc81b0c639a6429344a1b4bc00d30` and touches only `dev/programme/triage/s6-batch19.md`'s P88 entry. No merge of origin/main was taken, and every figure below is measured at the fixed merge base over fixed UTC windows, so none moves with main.

Repair of round-2 block `Fix review: blocked b28cb6ac5 figure-wrong` (refs/heads/review/2767):
- The block was that P88 quoted 37 record PRs (24 merged) and 12 merges since 12:00Z. The fix replaces the fuzzy PR search with a first-parent git rule, giving 19 and 9 in Instances. Binding is re-derived (about 10 to 12 saved a day, not 28), and both places in the carry text now read 19 instead of 37.
- The finding was that the pitch and the count gate had no stated relation. The carry text now states it, and it adds a harness case for the override.

## Mutation proof

n/a: no code or check changes, because the file is a ruling record. Its consumer is the triage gate. `roster_edit.ruling_verdict` at this head reads P88 ACCEPT, P89 ACCEPT, P90 ACCEPT, P91 REJECT and P92 ACCEPT.

## Null control

- `roster_edit.ruling_verdict` on a pid the file lacks (`P99`) returns None.
- Record-merge rule: the same `git log` with grep string `from tvofi/record/autofixZZ` returns 0.
- Chain claim: the record PR four back is rowed by 0 of 19 record merges, against 19 of 19 for the previous one.
- Carry lint: the new P88 carry text, set as the brief and the carry of R10-FLOW-RECORD-PITCH in a scratch copy of the roster, gives `node tools/policy/brief_lint.mjs`: 0 errors. The same copy with `tests/delivery_status.py` made `tests/delivery_statusX.py` gives 1 error, so the linter does read the text.
- The P89, P90 and P92 carries are unchanged from the reviewed head, where they linted at 0 errors.

## Figures

Every figure is at merge base `0810d5b8f`. Define `R(from,to) = git log --first-parent 0810d5b8f --since=<from> --until=<to> --grep='from tvofi/record/autofix' --format=%h`.
- `R(2026-10-24T00:00:00Z, 2026-10-25T00:00:00Z) | wc -l`: 19 record merges. The same window with `--merges` and no grep gives 46 first-parent merges, so 27 are non-record.
- `R(2026-10-24T12:00:00Z, 2026-10-25T00:00:00Z) | wc -l`: 9 record merges.
- Rows per record merge are `git diff --name-only --diff-filter=AM <c>^1 <c> -- dev/programme/delivery/ | wc -l` over `R(day)`. Sorted, they are 2 2 2 2 2 2 2 3 3 3 3 3 3 3 4 4 4 5 10 (range 2 to 10, median 3), and the 12:00Z-onward subset is 2 2 3 3 3 4 4 5 10.
- Chain: for each c in `R(day)`, `git diff --quiet <c>^1 <c> -- dev/programme/delivery/<N>.md` fails, where N is the PR number of the record merge before c on first parent. It fails for 19 of 19, so each record merge rows the previous record PR. The null run uses the record merge four back and fails for 0 of 19.
- Binding: the rule is non-record merges divided by real merges per batch. With the record chain standing, each batch of 4 holds 3 real merges plus the previous record merge, so 27 / 3 = 9. With P49's chain fix, each batch holds 4 real merges, so 27 / 4 is about 7. Against 19 record merges a day, that saves about 10 to 12. The age arm only opens a PR sooner, so this is an upper bound on the saving.
- Entries and verdicts: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' -r '$1' dev/programme/triage/s6-batch19.md | sort | uniq -c` gives 4 ACCEPT and 1 REJECT.
- Scope: `python3 tests/closure.py select --diff 0810d5b8f` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

- At the reviewed head b28cb6ac5, all 52 check runs concluded success or skipped (review/2767, evidence/check-runs.txt). This head has not run CI yet.
- `tests / ci-ratchet` on main's push run, if it is red, is not this PR's. GitHub's repo-wide artifacts listing returns 0 bytes, a hotfix is in flight, and this diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

n/a: once this file is on main, the orchestrator routes each carry through `roster_edit.py`, citing this file.

## Friction

none
