record_row.py wrote the record body's `## Red checks` with the short names, but `review_packet.py` gate_digest passes each red check-run's full name (`tests / nightly-status`, `governance / delivery-status`, `governance / record`) to `policy_lint.mjs --pr-body`, which refused #2966 as red-unanswered. The section now names each reporter by full name with the short name beside it, from one definition (`RED_CHECKS`) that the body text and the self-test both read. Triage: dev/programme/triage/s6-batch63.md#P292.

## Head

e316cdb9526e6cc81995d57a575dbf9497f0941e, on origin/main 7539d1675d7f (unmoved since the base, so no second prepr run).

## Mutation proof

Mutant: the Red checks lead-in and the record bullet revert to the short names only (`_red_names_line` emits `` `record`, `nightly-status` and `delivery-status` ``).
Command: `PYTHONPATH=tests/hastub python3 tools/audit/seat/record_row.py --self-test`
Red at the mutant: `1 self-test check(s) failed: body check passes the generated body over the reporter reds (rc 1: PR-BODY: 1 error(s) ...)`. Only that arm fails. Restored; the same command prints `record_row self-test: all checks passed`.

## Null control

The existing stripped-names arm (`the nightly lane`, `the delivery reporter`), run with `--red` set to the full `tests / nightly-status`, still exits 1 with "does not name it": `a body that does not name nightly-status is refused (null control)` passes at the head. Its absence from the failing list at the mutant shows the mutation did not disable the check.

## Figures

- `bash tools/pr/prepr.sh` at the head: `PRE-PR: e316cdb9526e6cc81995d57a575dbf9497f0941e ... rc=0`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED`, one changed file, `tools/audit/seat/record_row.py`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/entities.py`: all checks passed.

## Red checks

none

## Forward-carry

none

## Friction

none
