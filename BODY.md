Triage batch 60 rules the orchestrator's 2026-10-29T10:24Z roster-push proposal as P278. It is the next rolling batch under V182, after batch 59 (#2945, merged as `66974d473`).
- **P278 (retry a roster push refused as non-fast-forward): ACCEPT, narrowed, to R10-ORCH-ROSTER-SCHEMA; the retry is REJECTED.**
  - The two refusals (09:15Z and 09:26Z, `append-group R10-FLY-OWED-LEVELS`) were rc 3. That is `roster_edit.py`'s lint-gate refusal (`:657-660`), which returns before any push. A lost race takes its own path (`:682`), retries up to `PUSH_ATTEMPTS = 3` (`:137`), and refuses with rc 2. `roster_queue.py` retries again on a stale lint checkout or a race (`:122`, `:137`).
  - Reproduced without `--push` and with no rival: brief_lint gives `TOTAL: 2 error(s)`, both in the group's own brief. One sentence cited `orchestrator_tick.py:690` and `owed_unactioned.py:50`, and the linter's clause window (`brief_lint.mjs` `clauseWindow`, `:391`) searched each file for the other's name. A retry would have refused every time.
  - The cause was invisible because the roster loop keeps only the last line matching `pushed|REFUSED|error`, which is "... nothing pushed". Both re-queue notes recorded a race.
  - Carried: the lint-gate refusal's last line names cause, count and outcome together. rc stays 3. The carry adds a self-test arm, a mutant of the old two-line form and a clean-fixture null control.
  - The authoring defect is this seat's (P277's brief, batch 59). The group JSON is corrected out of tree, and the same dry run now gives `TOTAL: 0 error(s)` with nothing pushed. This seat now dry-runs every group and carry op it queues.
  - One held roster op (`append-carry R10-ORCH-ROSTER-SCHEMA`), released once this file is on main.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`54082f025acbbd4c685d095ad9fff392b9dbf25c`; the file is the whole diff against `66974d47312caa46e9817b9aeae7186e9764e560`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P278 as `ACCEPT`, and `triage_refusal` passes the P278 carry text (returns None).
- With P278's `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same carry is refused: `dev/programme/triage/s6-batch60.md#P278 is not an ACCEPT ruling (REJECT)`. The first draft led its verdict line with "REJECT the retry" and would have been refused the same way. It was reordered before commit.

## Null control

- With the file absent, the carry returns `the triage ruling dev/programme/triage/s6-batch60.md is not on the roster branch or origin/main`. That is also what the real dry run of the held op printed before this push.
- For the ruling's measurement: the roster at tip `68406609a`, without the new group, lints `TOTAL: 0 error(s)`. With the original group it gives 2 errors, and with the clause-split group 0. So the errors belong to the brief alone.

## Figures

- Dry run: `roster_edit.py append-group R10-FLY-OWED-LEVELS <json> --roster-ref handoff/audit-r10-roster --lint-cwd <origin/main 66974d473 checkout>` without `--push`, on a scratch worktree that was then removed. Original brief: `LINT GATE REFUSED`, `TOTAL: 2 error(s)`. Corrected brief: `lint gate: TOTAL: 0 error(s)`, `ready: ... (no --push)`.
- The carry text was linted by appending it to a copy of the roster at `68406609a` (group R10-ORCH-ROSTER-SCHEMA): `TOTAL: 0 error(s)`.
- Roster tip: R10-FLY-ABORT-OWN-MERGE and both batch-59 carries landed at 09:15Z (`79542c319`, `539b4b5e2`, `13aa34d67`). R10-FLY-OWED-LEVELS is absent.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
