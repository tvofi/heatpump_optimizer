Part of #201. R10-FLOW-BODY-ONLY, V147 (the roster entry's Carry 14), built first on the orchestrator's priority note (triage P321: recurred on #3016). A handoff updates only with the body pushed for it, and a failed update records why.

The group's carries, numbered as the review packet numbers them (the roster's `carry` list, from 1):

- Carry 1 (pre-study K12): the brief's parts (a) to (c) are not built here; owed.
- Carry 2 (`app_approve.sh --carry` until this lands): still binds, as no body-only mode lands here.
- Carry 3 (the seam with R10-ORCH-MACHINERY): untouched; owed with parts (b) and (c).
- Carry 4 (self-test hygiene): (a) the mutants take per-file ids, `cloud_relay-35` to `-38` at the end of the cloud_relay block and `body_push-3` beside `body_push-1`/`-2`; (b) the new fixture rows reuse the self-test's `throwaway_git_init` repositories; (c) no new git push site; (d) `## Red checks` names nightly-status.
- Carry 5 (P22): its reason half is built here (a failed update's last REFUSE line, else last line, kept per topic and sha); exit 75 for a checked-out-elsewhere worktree and keying the failure on the body sha are owed.
- Carry 6 (the level written before the serial update loop): owed.
- Carry 7 (`--roster-ref` in body_patch.sh's contract arm): owed.
- Carry 8 (card 7, generated figure block): owed; it builds on parts (b) and (c).
- Carry 9 (hold part (a)): lifted by carry 10.
- Carry 10 (train-path branch of part (a)): owed.
- Carry 11 (V115, the lint's tracked files at the gated head): owed.
- Carry 12 (V64 not built in #2858): stands; built under carry 13.
- Carry 13 (auto-open on handoff): owed.
- Carry 14 (V147): built by this pull request, below.
- Carry 15 (ref_privacy.py's home-directory refusal on a cloud seat): owed; this diff does not touch ref_privacy.py.
- Carry 16 (V191, a body-only handoff skipped in silence): owed.

V147, as built:

- `tools/audit/seat/body_push.sh`: a PR body's commit carries a trailer line `Code: <handoff/<topic> tip>`, the sha the script has just proved equal to the checkout's HEAD. A result body (no `handoff/<topic>`) writes none.
- `tools/audit/seat/cloud_relay.sh` `handoff_arm`: after it fetches `handoff-body/<topic>` and before `update_pr.sh`, a body tip whose `Code:` names a sha other than the handoff tip runs no update, writes one `handoff-body-stale refs/heads/handoff/<topic> <hs> body names <sha12>` level line, records nothing in `cloud-handoff-failed`, and is retried on the next pass. A body with no `Code:` line (pushed before this change) updates as before. No timestamp comparison.
- A failed update's `handoff-update` level line ends in the update's last `REFUSE` line, else its last line. `cloud-handoff-failed` keeps its bare `<topic> <sha>` lines; the reason is kept beside it in `cloud-handoff-failed.why` (tab-separated), so the recorded-failed path keeps the reason on every later pass instead of losing it after one.
- `tools/audit/seat/ledger.py`: `handoff-body-stale` registered in `KINDS` as derived.

Alternative not taken: holding the reason only in the failing pass's level line. `level_set` rewrites the level every pass and the recorded-failed path writes the line again without the update's output, so the reason would be gone one pass later (the #2894 and #2900 shape).

## Head

`cde451a79b4f326211defd961ee0155ce0480b38`, a clean merge of origin/main `4822c8f9b7f7ca6201cea05a9c80f7797e5f56a6` (2026-10-31, `ci: record nightly kills`: 23 files under `tests/mutation_ledger/`, none this diff reads) into `d1cd320db1174f1f9f84dab6b3608070978bf3bd`, where the mutants and the fixture were first run. The relay self-test, structure and prepr were re-run at the merge head.

## Mutation proof

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-35 cloud_relay-36 cloud_relay-37 cloud_relay-38 body_push-3`: all five KILLED, `survivors=0`, each after its unmutated step passed (the harness's per-mutant null control).

- `cloud_relay-35`, the arm ignores `Code:` (`if false`): red on "a body whose Code: names the previous handoff head runs no update_pr" and "and owes one handoff-body-stale line".
- `cloud_relay-36`, the failed update's level line drops its `why`: red on the REFUSE-line and last-line checks.
- `cloud_relay-37`, the REFUSE line is not read: red on "a failed update's handoff-update line ends in its last REFUSE line" and the next-pass check.
- `cloud_relay-38`, the recorded-failed path does not read `cloud-handoff-failed.why`: red on "and keeps it on the next pass, which does not retry".
- `body_push-3`, the trailer condition inverted (graded by prepr's self-test, which drives body_push): red on "that body's commit names the handoff head it describes in a Code: trailer" and its result-body null control.

## Null control

- A body whose `Code:` names the current handoff head updates, and the stale line is gone (self-test check "a body whose Code: names the current handoff head updates (null control)").
- A body with no `Code:` line updates as before (self-test check "a body with no Code: line updates as before (null control)"), and every pre-existing handoff-arm check, written against bodies with no trailer, still passes.
- A result body names no `Code:` (prepr self-test check "a result body, with no handoff/<topic>, names no Code: (null control)").
- The one pre-existing check changed is "and owes handoff-update in the level file, at the topic's tip": its stub prints nothing, so its line now ends in `(no output)`, `last_line`'s value for empty output.

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test`: its last line reports 0 failed.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-35 cloud_relay-36 cloud_relay-37 cloud_relay-38 body_push-3`: `RESULT survivors=0`.
- `python3 -I tools/audit/seat/ledger.py --self-test`: 0 failed.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED`; `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` and `PYTHONPATH=tests/hastub python3 tests/entities.py`, the scripts `scope.run` names, pass.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/throwaway_git.py --check`: 0 sites refused (the new fixture rows reuse the self-test's `throwaway_git_init` repositories).

## Red checks

- `tests / nightly-status`: red on main's ancestry, graded on main; this diff touches none of what it reads, so it is the orchestrator's on main.

## Forward-carry

- The rest of the group stays owed in its own brief, `dev/programme/rosters/wave-r10-groups.json` stage R10-FLOW-BODY-ONLY: parts (a) to (c) and every carry the list above marks owed; this pull request builds the V147 carry alone. Carry: R10-FLOW-BODY-ONLY

## Friction

none
