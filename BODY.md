## Summary
`tools/audit/seat/roster_edit.py` gains `unwire-issue <group> <N> [--field fixes|issues]` (default `issues`), the inverse of `wire-issue`: same JSON load, modify, dump, same brief_lint gate on push. It refuses an N the group does not hold in that field, a non-integer N, an unknown group, and `--field` values other than issues/fixes (argparse still rejects resume fields; `--field fixes|issues` is refused on every op but `unwire-issue`, and the resume fields only on `set-resume`). INSTRUMENTS.md lists the op.

Part of #201.

## Evidence
- Self-test written first: 5 of the new checks failed before the op existed. After: `roster_edit self-test: 59 checks, 0 failed` (the script's count line adds the failures to the total).
- Mutants, each caught by the self-test: no absent-refusal (3 checks fail), op always acts on `issues` (2), CLI drops `--field` (3), op removes nothing (5).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- prepr.sh not run locally: box load1 was above 40 and heavy lanes go to CI per the heavy-to-ci ruling; CI check-runs are the evidence for the heavy suites.
- The op was used for its own purpose in the same task (roster ref handoff/audit-r10-roster, edits via the lint gate).

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
