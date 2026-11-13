Question: tests/entities.py's #2227 arm now reads the re-homed carries from the tree's roster, but roster entry R11-INTAKE-R10-RESIDUE carry[56] ("carry-201 entry 6 (file removed)") was folded without carry-201 entry 6's `remeasure`, the one command naming dev/audit/rounds/round6/D11/fix/codeowners_gap.py; will the orchestrator amend that roster entry to carry the remeasure text verbatim (the roster is not this seat's to write), or rule otherwise?

# BLOCKED: r10-closeout-prep-p2 repair round 3

## Measured at c57b58f5f6 (fe2e12051d removes the round-2 note; c57b58f5f6 merges origin/main e28a310d7d)

- The arm change (in the WIP commit above this note): roster_lib's `roster_path(".")` names dev/programme/rosters/wave-r10-groups.json; the arm appends each group's `carry` string that matches `carry-<N> entry <K> (file removed)` to `_SP_REMEASURES`, labelled `<roster>#<group>[<i>]`, and the carry-cited floor counts those labels. Floors are unchanged.
- Why only the re-homed entries: read the whole roster and the arm crashes (FileNotFoundError on dev/audit/rounds/round10/D7/arch2-s2/event_hub_writes.py, cited by R10-LIVESTATE[1]). Measured over every roster `carry` string: 274 distinct executable paths cited, 54 not in the tree. Round harnesses stay out of the tree by rule (fixer.md step 3). The filtered read yields 31 entries.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: 3 of 2711 fail.
  1. #2227: cited 2 < floor 3. The carry-cited floor now holds: dora_keys.py is cited by R11-INTAKE-R10-RESIDUE[53] and [54]. codeowners_gap.py is cited by nothing.
  2. The cited-program null-control arm: it requires `_sp_cog in _SP_CITED`. Same cause.
  3. #2312 F2: `closure.select(["dev/programme/rosters/wave-r10-groups.json"])` returns scoped, 1 script, not tests/entities.py, and the file is not INERT. This one is a closures-table repair (ci_predict); this seat can make it once the block clears.
- The cause: on main (e28a310d7d), dev/programme/carries/carry-201.json carries[6].remeasure tells a seat to run `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`. The roster's delivered text for entry 6 (R11-INTAKE-R10-RESIDUE carry[56]) keeps the effect and brief and drops that command. Nothing else in the tree cites the program. A floor re-scope is refused by ruling (a). Re-adding entry 6 to carry-201.json would give one carry two destinations.

## Also done this round, verified
- carry-1645 control 0 now cites `doc_claims.check_simulate_plan_fields` by symbol and no longer cites tests/doc_claims.py:612. brief_lint was run with the file temporarily taken off the legacy list, at three heads:
  - main's copy: "'_mutated_span' not found near tests/doc_claims.py:612; found at line 616 instead"
  - this head: no carry-0 error
  - a misspelled symbol (control): "'check_simulate_plan_fieldz' not found in tests/doc_claims.py"
  - Carry 1's no-path error remains, so the file stays listed.
