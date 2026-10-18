`roster_edit.py` could add an issue to a group (`wire-issue`) but not remove one from `issues` or `fixes`, so a stale `fixes` entry (#2228, #2253, #2317) had no safe edit. Adds `unwire-issue <group> <N> [--field fixes|issues]` (default `issues`): same JSON load, modify, dump and brief_lint gate on push; refuses an N the group does not hold in that field, a non-integer N, an unknown group, and `--field` on any op but `set-resume`, `wire-issue` and `unwire-issue`. Also `wire-issue --field fixes|issues` (default `issues`), because no op could write `fixes` (R10-ARCHSCORE-COVERAGE needed [2259]). INSTRUMENTS.md lists both. Part of #201.

## Head

7f096fa75c814872b66e4d7321fe0b7a4b5eaae9

## Mutation proof

Self-test written first: 5 new checks failed before the op existed, 0 failed after. Four mutants, each run alone against the restored file, each caught:
- absent-refusal removed: FAIL `unwire-issue absent refused`, `unwire-issue default field is issues, not fixes`, `unwire-issue --field fixes absent refused`
- op always acts on `issues`: FAIL `unwire-issue --field fixes removes only that field's entry`, `unwire-issue --field fixes absent refused`
- CLI drops `--field`: FAIL `unwire-issue default field is issues, not fixes`, `unwire-issue --field fixes rc`, `unwire-issue --field fixes removes only that field's entry`
- wire-issue ignores `--field` (CLI call hard-wired to issues): FAIL `wire-issue --field fixes writes fixes only`, `wire-issue --field issues still defaults and sorts`, `unwire-issue cleans the wire-issue arm`
- op removes nothing: FAIL `unwire-issue round-trip`, `absent refused`, `default field`, `--field fixes removes only`, `--field fixes absent refused`

## Null control

`wire-issue` and every other op are unchanged: the self-test's existing checks (round-trip bytes, wire-issue, append-group, set-resume) pass unmodified at this head, 64 checks, 0 failed.

## Figures

- `roster_edit self-test: 64 checks, 0 failed`: `python3 tools/audit/seat/roster_edit.py --self-test` (the script's own count line adds failures to the total)
- `STRUCTURE RATCHET PASSED`: `python3 tests/structure.py`

## Red checks

none

## Forward-carry

none

## Friction

none
